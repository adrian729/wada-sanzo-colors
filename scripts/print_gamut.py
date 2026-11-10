#!/usr/bin/env python3
"""Measure what the press can print, from its ICC profile, and store it in print-gamut.json.

    python3 scripts/print_gamut.py

Wada's CMYK is read through Japan Color 2011 Coated (cmyk_to_oklch.py). This finds the edge of
everything that printing condition can make, its gamut, in two forms the site uses:

1. `chroma`: the most chroma it can print at each lightness and hue of OKLCH, for the Colors ›
   OKLCH view's Print choice (its slices' edge, and its solid's walls). Per half degree of hue, and
   at the hue of each corner of the inks' cube (pure yellow, yellow and magenta, ...), where the
   edge comes to a point: the edge as lightness goes from the darkest the press prints at that hue
   to white, as a line through [lightness, chroma] points, stored to 0.00001, never more than 0.0002
   off it in √chroma: the view's distance from the axis, so the edge is as smooth near the axis, at the
   darkest and lightest levels, as at the rim.
   Between two hues the page blends their lines, at each lightness, by hue; and where that would be
   more than 0.001 off the edge halfway between them (round the corners, where the edge turns
   sharply with hue), there are more hues, down to 1/128 of a degree apart.
2. `ostwald`: the full colours and the tint edge Ostwald's system is measured against (see
   notes/ostwald.md), per 1° of chromaticity angle round the white (CIE 1931 xy, D65; 0° towards
   +x, anticlockwise), and at the angle of each ink alone and of each two at 100% (`angles`): the
   purest colour the press prints there, with no black and only two inks
   (its full colour: its distance from the white in xy, X + Y + Z, and its OKLCH hue), and the
   brightest it prints at each share of that full colour against white (the tint edge: Y at a share
   of 0, 1/32, ..., 1).

How: CMYK is printable within 0 to 100% per ink and at most 350% in all (the profile's own limit:
its inverse table B2A1 prints its darkest colour with exactly that). The edge of what four inks can
make is where at least two of them are at a limit (0 or 100%, or the total), so it lies on the
surfaces where two inks vary and the other two are each at 0 or 100% (24 of them), or where the
total is 350% with one ink at 100% (4). Each is sampled every 1% through the A2B1 table, as
cmyk_to_oklch.py reads it, and cut into triangles. The edge at a lightness and hue is the furthest
point out from the grey axis where any of those triangles meets them, found per 0.002 of lightness.
Where the surfaces meet in a ridge (one ink varying, the other three at a limit: pure yellow, for
one), sampled every 0.25%, the ridge's own points are added, so that the line keeps its peaks.

The tint edge and the full colours come from the three surfaces of two inks with no black and the
third ink at 0, sampled every 0.5%: no other ink makes a colour brighter at the same chromaticity,
or purer at the same chromaticity angle.

Standard library only. Takes a few minutes.
"""
import bisect
import json
import math
from pathlib import Path

import cmyk_to_oklch as cx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "print-gamut.json"
TAC = 350  # % of ink in all, at most: see check_limit()
L_STEP, H_STEP = 0.002, 0.5  # the edge's search: lightness, hue (degrees)
TOLERANCE = 0.0002  # √chroma, as the OKLCH view draws it: how far the stored line may be from the edge found
SCALE = 100000  # the edge's points are stored as whole numbers: lightness and chroma times this
BLEND_TOLERANCE = 0.001  # chroma: how far blending two neighbouring hues may be from the edge between
R_STEPS = 32  # the tint edge, per 1/32 of share of full colour

# CIE 1931 XYZ (D65) of linear sRGB, CSS Color 4's: its white, (1, 1, 1), is the white measured against
# (Y = 1, the paper's white, as Lab is media-relative). It is only the white: no colour goes through sRGB.
SRGB_TO_XYZ = [[0.41239079926595934, 0.357584339383878, 0.1804807884018343],
               [0.21263900587151027, 0.715168678767756, 0.07219231536073371],
               [0.01933081871559182, 0.11919477979462598, 0.9505321522496607]]
WHITE = [sum(row) for row in SRGB_TO_XYZ]
XW, YW = WHITE[0] / sum(WHITE), WHITE[1] / sum(WHITE)


def lab_to_xyz_d65(lab):
    return cx.mul(cx.D50_TO_D65, cx.lab_to_xyz_d50(*lab))


def xyz_to_oklab(xyz):
    lms = cx.mul(cx.XYZ_TO_LMS, xyz)
    return cx.mul(cx.LMS_TO_OKLAB, [math.copysign(abs(v) ** (1 / 3), v) for v in lms])


class Press:
    """CMYK (percent) -> XYZ (D65) and OKLab, each sample computed once."""

    def __init__(self):
        self.a2b = cx.load_a2b1(cx.PROFILE)
        self.cache = {}

    def __call__(self, cmyk):
        key = tuple(round(v, 6) for v in cmyk)
        if key not in self.cache:
            xyz = lab_to_xyz_d65(cx.cmyk_to_lab(self.a2b, key))
            self.cache[key] = (xyz, xyz_to_oklab(xyz))
        return self.cache[key]


def check_limit():
    """The profile's total ink limit: what its inverse table (B2A1) prints black with."""
    total = sum(cx.lab_to_cmyk(cx.load_b2a1(), (0, 0, 0)))
    assert abs(total - TAC) < 0.5, f"the profile prints black with {total:.1f}% of ink, not {TAC}%"


def ok(v):
    return v is not None and sum(v) <= TAC + 1e-9 and all(-1e-9 <= x <= 100 + 1e-9 for x in v)


def surfaces(step):
    """The gamut's surfaces, each as a grid of CMYK (None where not printable): two inks free over 0..100
    (the grid's axes), the other two at 0 or 100; and the total limit's (one ink at 100%, two free, the
    third making up the 350%)."""
    n = round(100 / step)
    grid = [step * i for i in range(n + 1)]
    for i in range(4):
        for j in range(i + 1, 4):
            rest = [k for k in range(4) if k not in (i, j)]
            for a in (0, 100):
                for b in (0, 100):
                    def at(x, y, i=i, j=j, rest=rest, a=a, b=b):
                        v = [0.0] * 4
                        v[i], v[j], v[rest[0]], v[rest[1]] = x, y, a, b
                        return v if ok(v) else None
                    yield [[at(x, y) for y in grid] for x in grid]
    for full in range(4):
        i, j, k = [q for q in range(4) if q != full]
        def at(x, y, i=i, j=j, k=k, full=full):
            v = [0.0] * 4
            v[full], v[i], v[j], v[k] = 100, x, y, TAC - 100 - x - y
            return v if ok(v) else None
        yield [[at(x, y) for y in grid] for x in grid]


def ridges(step):
    """The ridges where surfaces meet, each as a line of CMYK: one ink varying, the other three at 0 or
    100%; and along the total limit, one ink at 100%, one at 0 or 100%, the other two sharing the rest."""
    n = round(100 / step)
    for i in range(4):
        rest = [k for k in range(4) if k != i]
        for bits in range(8):
            line = []
            for t in range(n + 1):
                v = [0.0] * 4
                v[i] = step * t
                for q, k in enumerate(rest):
                    v[k] = 100.0 * ((bits >> q) & 1)
                line.append(v if ok(v) else None)
            yield line
    for full in range(4):
        for second in range(4):
            if second == full:
                continue
            i, j = [q for q in range(4) if q not in (full, second)]
            for s in (0, 100):
                line = []
                for t in range(n + 1):
                    v = [0.0] * 4
                    v[full], v[second], v[i] = 100, s, step * t
                    v[j] = TAC - 100 - s - v[i]
                    line.append(v if ok(v) else None)
                yield line


def triangles(grid):
    """A grid's squares, each cut along its x + y diagonal (so that the total limit, x + y constant, runs
    along triangle edges); only triangles whose corners are all printable."""
    n = len(grid) - 1
    for x in range(n):
        for y in range(n):
            a, b, c, d = grid[x][y], grid[x + 1][y], grid[x][y + 1], grid[x + 1][y + 1]
            for tri in ((a, b, c), (b, d, c)):
                if all(tri):
                    yield tri


def between(hues, h0, h1):
    """The indices of `hues` (sorted, 0 to 360) between h0 and h1, the shorter way round, with each one's
    hue as seen from h0 (so that h0 + span covers it, across 0 too)."""
    span = (h1 - h0 + 180) % 360 - 180
    lo, hi = (h0, h0 + span) if span >= 0 else (h0 + span, h0)
    out = []
    for turn in (-360, 0, 360):
        a, b = bisect.bisect_left(hues, lo - turn - 1e-9), bisect.bisect_right(hues, hi - turn + 1e-9)
        out += [(k, hues[k] + turn) for k in range(a, b)]
    return out


def column_hues(press):
    """The edge's hues: every half degree, and the hue of each corner of the inks' cube (each ink at 0
    or 100%, within the total) that has colour, where the edge comes to a point."""
    hues = {round(j * H_STEP, 6) for j in range(round(360 / H_STEP))}
    for corner in range(16):
        v = [100.0 * ((corner >> k) & 1) for k in range(4)]
        if ok(v):
            _, a, b = press(v)[1]
            if math.hypot(a, b) > 0.02:
                hues.add(round(math.degrees(math.atan2(b, a)) % 360, 6))
    return sorted(hues)


def chroma_columns(press, hues):
    """Per hue (`hues`, sorted): the edge, as [lightness, chroma] points from the darkest to white."""
    rows, cols = round(1 / L_STEP), len(hues)
    found = [[0.0] * cols for _ in range(rows + 1)]
    for grid in surfaces(1):
        for tri in triangles(grid):
            P = [press(v)[1] for v in tri]  # OKLab
            Ls = [p[0] for p in P]
            for k in range(math.ceil(min(Ls) / L_STEP - 1e-9), math.floor(max(Ls) / L_STEP + 1e-9) + 1):
                L = k * L_STEP
                cut = []  # where the plane of lightness L cuts the triangle: a segment in (a, b)
                for s in range(3):
                    p, q = P[s], P[(s + 1) % 3]
                    if p[0] == L:
                        cut.append((p[1], p[2]))
                    elif (p[0] - L) * (q[0] - L) < 0:
                        t = (L - p[0]) / (q[0] - p[0])
                        cut.append((p[1] + t * (q[1] - p[1]), p[2] + t * (q[2] - p[2])))
                if len(cut) < 2:
                    continue
                (a0, b0), (a1, b1) = cut[0], cut[-1]
                da, db = a1 - a0, b1 - b0
                for j, hue in between(hues, math.degrees(math.atan2(b0, a0)), math.degrees(math.atan2(b1, a1))):
                    ca, sa = math.cos(math.radians(hue)), math.sin(math.radians(hue))
                    den = da * sa - db * ca
                    if abs(den) < 1e-15:
                        continue
                    t = -(a0 * sa - b0 * ca) / den
                    if -1e-9 <= t <= 1 + 1e-9:
                        r = (a0 + t * da) * ca + (b0 + t * db) * sa
                        if r > found[k][j]:
                            found[k][j] = r
    # The ridges' points, at each column's hue.
    extra = [[] for _ in range(cols)]
    for line in ridges(0.25):
        pts = [None if v is None else press(v)[1] for v in line]
        for p, q in zip(pts, pts[1:]):
            if p is None or q is None:
                continue
            hp, hq = (math.degrees(math.atan2(v[2], v[1])) for v in (p, q))
            Cp, Cq = math.hypot(p[1], p[2]), math.hypot(q[1], q[2])
            if min(Cp, Cq) < 1e-4:
                continue
            for j, hue in between(hues, hp, hq):
                d = (hq - hp + 180) % 360 - 180
                t = 0.0 if abs(d) < 1e-12 else (hue - hp) / d
                if -1e-9 <= t <= 1 + 1e-9:
                    extra[j].append((p[0] + t * (q[0] - p[0]), Cp + t * (Cq - Cp)))
    columns = []
    for j in range(cols):
        line = [(k * L_STEP, found[k][j]) for k in range(rows + 1)]
        first = next((k for k, (_, c) in enumerate(line) if c > 0), None)
        line = line[max(0, first - 1):] if first is not None else [(1.0, 0.0)]
        line[-1] = (1.0, 0.0)  # white
        ridge = sorted(extra[j])
        if ridge and ridge[0][0] < line[0][0]:  # darker than the darkest row found: the line starts there
            line.insert(0, (ridge[0][0], 0.0))
        for L, C in ridge:  # a ridge point where it's further out than the line
            Ls = [p[0] for p in line]
            k = bisect.bisect_right(Ls, L)
            (L0, C0), (L1, C1) = line[max(0, k - 1)], line[min(k, len(line) - 1)]
            if C > (C0 if L1 == L0 else C0 + (C1 - C0) * (L - L0) / (L1 - L0)) + 1e-6:
                line.insert(k, (L, C))
        columns.append(line)
    return columns


def line_at(line, L, Ls=None):
    """A column's chroma at lightness L (none outside it; at a step straight up, the top of it)."""
    Ls = Ls or [p[0] for p in line]
    if L < Ls[0] or L > Ls[-1]:
        return 0.0
    k = bisect.bisect_right(Ls, L)
    if k >= len(line):
        return line[-1][1]
    (L0, C0), (L1, C1) = line[k - 1], line[k]
    return C0 if L1 == L0 else C0 + (C1 - C0) * (L - L0) / (L1 - L0)


def edge_columns(press):
    """The edge's hues and their columns: those of column_hues, and more between two neighbours wherever
    blending them (at each lightness, by hue) would be more than BLEND_TOLERANCE off the edge halfway."""
    hues = column_hues(press)
    lines = dict(zip(hues, chroma_columns(press, hues)))
    todo = None  # the neighbours to check: all of them, then those either side of a hue added
    for _ in range(7):
        hs = sorted(lines)
        pairs = [(hs[i], hs[(i + 1) % len(hs)]) for i in range(len(hs))]
        pairs = [q for q in pairs if todo is None or q in todo]
        mids = sorted({round(((a + ((b - a) % 360) / 2)) % 360, 9): (a, b) for a, b in pairs}.items())
        if not mids:
            break
        found = chroma_columns(press, [m for m, _ in mids])
        todo = set()
        grid = [0.2 + 0.001 * k for k in range(801)]
        for (m, (a, b)), line in zip(mids, found):
            La, Lb, Lm = ([q[0] for q in x] for x in (lines[a], lines[b], line))
            off = max(abs(line_at(line, L, Lm) - (line_at(lines[a], L, La) + line_at(lines[b], L, Lb)) / 2) for L in grid)
            if off > BLEND_TOLERANCE:
                lines[m] = line
                todo |= {(a, m), (m, b)}
    hues = sorted(lines)
    return hues, [simplify(lines[h]) for h in hues]


def simplify(line):
    """Fewer points: each kept segment within TOLERANCE of every point it skips (in √chroma, at its lightness)."""
    kept, i = [line[0]], 0
    while i < len(line) - 1:
        j = i + 1
        while j + 1 < len(line):
            (L0, C0), (L1, C1) = line[i], line[j + 1]
            if L1 <= L0 or any(abs(math.sqrt(max(0.0, C0 + (C1 - C0) * (L - L0) / (L1 - L0))) - math.sqrt(C)) > TOLERANCE
                                for L, C in line[i + 1:j + 1]):
                break  # (a step straight up, at the darkest: kept)
            j += 1
        kept.append(line[j])
        i = j
    return kept


def chromaticity(xyz):
    s = sum(xyz)
    return xyz[0] / s - XW, xyz[1] / s - YW


def ostwald_rays(press):
    """Per ray, every 1° of chromaticity angle and at each of the six corners (an ink at 100%, or two):
    the full colour (its distance from the white in xy, its X + Y + Z, its OKLCH hue) and the tint edge,
    the brightest Y at each share r of full colour against white, r = k/32."""
    n = 200
    corners = []
    for cmyk in ((100, 0, 0, 0), (0, 100, 0, 0), (0, 0, 100, 0), (0, 100, 100, 0), (100, 0, 100, 0), (100, 100, 0, 0)):
        dx, dy = chromaticity(press(cmyk)[0])
        corners.append(round(math.degrees(math.atan2(dy, dx)) % 360, 6))
    angles = sorted(set(range(360)) | set(corners))
    curves = [[] for _ in angles]  # per ray, the points of the tint edge on it: XYZ
    for i, j in ((0, 1), (0, 2), (1, 2)):  # cyan and magenta, cyan and yellow, magenta and yellow
        grid = []
        for x in range(n + 1):
            row = []
            for y in range(n + 1):
                v = [0.0] * 4
                v[i], v[j] = 100 * x / n, 100 * y / n
                row.append(press(v)[0])
            grid.append(row)
        for tri in triangles(grid):
            # A ray's colours: XYZ whose chromaticity is on the ray from the white at angle θ, a plane
            # through the origin (and the white), so it cuts the triangle in a segment.
            ang = []
            for p in tri:
                dx, dy = chromaticity(p)
                ang.append(None if math.hypot(dx, dy) < 1e-7 else math.degrees(math.atan2(dy, dx)))
            known = [a for a in ang if a is not None]
            if not known:
                continue
            base = known[0]
            rel = [(a - base + 180) % 360 - 180 for a in known]
            for m, deg in between(angles, base + min(rel), base + max(rel)):
                ct, st = math.cos(math.radians(deg)), math.sin(math.radians(deg))
                f = [(p[0] - XW * sum(p)) * st - (p[1] - YW * sum(p)) * ct for p in tri]
                for s in range(3):
                    p, q, fp, fq = tri[s], tri[(s + 1) % 3], f[s], f[(s + 1) % 3]
                    if fp == 0:
                        point = p
                    elif fp * fq < 0:
                        t = fp / (fp - fq)
                        point = [a + t * (b - a) for a, b in zip(p, q)]
                    else:
                        continue
                    dx, dy = chromaticity(point)
                    if dx * ct + dy * st >= -1e-9:  # on the ray, not the opposite one
                        curves[m].append(point)
    rays, sW = [], sum(WHITE)
    for points in curves:
        d = lambda p: math.hypot(*chromaticity(p))  # noqa: E731
        F = max(points, key=d)
        dF, sF = d(F), sum(F)
        _, A, B = xyz_to_oklab(F)
        # Each point's share of full colour against white, as on Ostwald's discs: P = aW + bF, r = b / (a + b).
        share = lambda u: sW * u / (sW * u + sF * (1 - u))  # noqa: E731
        pts = sorted((share(d(p) / dF), p[1]) for p in points)
        pts = [(0.0, 1.0)] + [p for p in pts if p[0] > 1e-6]
        rs = [p[0] for p in pts]
        edge = []
        for k in range(R_STEPS + 1):
            m = min(max(1, bisect.bisect_left(rs, k / R_STEPS - 1e-12)), len(pts) - 1)
            (r0, y0), (r1, y1) = pts[m - 1], pts[m]
            edge.append(y0 + (y1 - y0) * (k / R_STEPS - r0) / (r1 - r0) if r1 > r0 else max(y0, y1))
        rays.append({"dF": dF, "sF": sF, "hF": math.degrees(math.atan2(B, A)) % 360, "edge": edge,
                     "rise": max(b[1] - a[1] for a, b in zip(pts, pts[1:]))})
    return angles, rays


def main():
    check_limit()
    press = Press()
    hues, columns = edge_columns(press)
    darkest = min(p[1][0] for p in press.cache.values())
    angles, rays = ostwald_rays(press)
    inks = {name: math.degrees(math.atan2(lab[2], lab[1])) % 360 for name, cmyk in
            (("C", (100, 0, 0, 0)), ("M", (0, 100, 0, 0)), ("Y", (0, 0, 100, 0)), ("R", (0, 100, 100, 0)),
             ("G", (100, 0, 100, 0)), ("B", (100, 100, 0, 0))) for lab in [press(cmyk)[1]]}
    col_rows = ",\n".join("[" + ",".join(f"{round(L * SCALE)},{round(C * SCALE)}" for L, C in col) + "]" for col in columns)
    ray_rows = ",\n".join(json.dumps([round(r["dF"], 6), round(r["sF"], 6), round(r["hF"], 3), [round(v, 5) for v in r["edge"]]], separators=(",", ":")) for r in rays)
    OUT.write_text(
        '{"profile":"Japan Color 2011 Coated, A2B1 (media-relative)","limit":%d,"darkest":%.4f,\n' % (TAC, darkest)
        + '"inks":%s,\n' % json.dumps({k: round(v, 2) for k, v in inks.items()}, separators=(",", ":"))
        + '"chroma":{"scale":%d,"hues":%s,"columns":[\n' % (SCALE, json.dumps(hues, separators=(",", ":"))) + col_rows + "]},\n"
        + '"ostwald":{"steps":%d,"angles":%s,"rays":[\n' % (R_STEPS, json.dumps(angles, separators=(",", ":"))) + ray_rows + "]}}\n")
    print(f"{len(press.cache)} CMYK samples; darkest lightness {darkest:.4f}")
    print(f"edge: {sum(len(c) for c in columns)} points over {len(columns)} hues; most chroma "
          f"{max(C for col in columns for _, C in col):.4f}")
    print(f"tint edge: the largest rise in brightness as the share grows (none expected): {max(r['rise'] for r in rays):.5f}")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
