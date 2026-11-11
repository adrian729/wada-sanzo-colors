"""Place Wada's colours in Ostwald's colour system, and check the placement against Wada's own data.

The same computation as the site's Ostwald view (index.html, ostwaldSystem). Prints the checks quoted in
notes/ostwald.md. Run from anywhere:

    python3 notes/ostwald.py

Standard library only. Reads colors.json and print-gamut.json (scripts/print_gamut.py): every colour is
measured against what the press prints, Japan Color 2011 Coated, as Wada's colours were printed.
"""
import bisect
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
# OKLCH <-> CIE XYZ (D65), CSS Color 4's maths and white, as the scripts and the page have them.
from oklab import WHITE, oklab_of, oklch_of, xyz_of  # noqa: E402
colors = json.loads((ROOT / "colors.json").read_text())
index = {c["name"]: i for i, c in enumerate(colors)}
PRESS = json.loads((ROOT / "print-gamut.json").read_text())["ostwald"]
RAYS, ANGLES, STEPS = PRESS["rays"], PRESS["angles"], PRESS["steps"]

# Wada's grey scale (1935 supplement, Figure 2): 16 letters, A to P with J, from Ostwald's white (0.891
# white content) to his black (0.0355), evenly spaced on a log scale. Ostwald's own scale skips J.
# A grey's black content is 1 minus its white.
LETTERS = "abcdefghijklmnop"
GREYS = [0.891 * (0.0355 / 0.891) ** (k / 15) for k in range(16)]

# The white is CSS's D65 (Y = 1), the white print-gamut.json measures the press against.
SW = sum(WHITE)
XW, YW = WHITE[0] / SW, WHITE[1] / SW


def between(theta):
    """The two rays either side of chromaticity angle theta (degrees round the white in xy), and how far
    theta is from the first to the second (print-gamut.json's rays: one per degree, and one at each ink
    alone and each two at 100%, where the full colours turn a corner)."""
    x = theta % 360
    k = bisect.bisect_right(ANGLES, x)
    j0, j1 = (k - 1) % len(ANGLES), k % len(ANGLES)
    a0, a1 = ANGLES[j0], ANGLES[j1] + (360 if k == len(ANGLES) else 0)
    return RAYS[j0], RAYS[j1], (x - a0) / (a1 - a0)


def ray(theta):
    """The press's full colour and tint edge at theta, between the rays: the full colour's distance from
    the white and its X + Y + Z, and the tint edge (Y at each share of full colour)."""
    a, b, t = between(theta)
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), [p + t * (q - p) for p, q in zip(a[3], b[3])])


def full_hue(theta):
    """The OKLCH hue of the press's full colour at theta, between the rays (the shorter way round)."""
    a, b, t = between(theta)
    return a[2] + t * ((b[2] - a[2] + 180) % 360 - 180)


def tint_edge(edge, r):
    """The brightest the press prints (Y) at share r of full colour, between the table's 1/32 steps."""
    x = min(max(r, 0), 1) * STEPS
    k = min(int(x), STEPS - 1)
    return edge[k] + (x - k) * (edge[k + 1] - edge[k])


def hue_number(theta):
    """Ostwald's 100-step hue at chromaticity angle theta, before calibration. Ostwald spaced his circle
    evenly to the eye, with complements opposite. Complements, mixed, give grey, so they are at opposite
    chromaticity angles. The full colour's OKLCH hue is even to the eye, but the press's full colours aren't
    symmetrical in it: a full colour and its complement are up to 37 degrees from opposite. So the number
    takes the mean of the two, the complement's turned half round, and complements stay exactly 50 steps
    apart. The circle runs the other way round from OKLCH's, a quarter of it (25 steps) per 90 degrees."""
    h1, h2 = full_hue(theta), full_hue(theta + 180)
    mean = h1 + ((h2 - h1) % 360 - 180) / 2
    return (-mean / 3.6) % 100


def measure(xyz):
    """Where a colour falls against the press: its chromaticity angle (None for a grey), its share of full
    colour against white r (Ostwald's discs: the colour is a W + b F, white and the full colour, so r =
    b / (a + b)), and its white, black and colour content. Black is how far it is below the tint edge,
    1 - Y / Ymax(r): a tint has none, and its shadow series, the same chromaticity darker, more. Beyond
    what the press prints, purer than its full colour or brighter than its tint edge, it is measured at
    the edge (`outside` says by how much: the share past 1, and the black below 0)."""
    s = sum(xyz)
    if s < 1e-9:  # black: no chromaticity, all black
        return dict(theta=None, r=0.0, white=0.0, black=1.0, colour=0.0, outside=(0.0, 0.0))
    dx, dy = xyz[0] / s - XW, xyz[1] / s - YW
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return dict(theta=None, r=0.0, white=xyz[1], black=1 - xyz[1], colour=0.0, outside=(0.0, 0.0))
    theta = math.degrees(math.atan2(dy, dx)) % 360
    dF, sF, edge = ray(theta)
    u = d / dF
    r_raw = SW * u / (SW * u + sF * (1 - u)) if u < 1 else 1 + (u - 1)  # (past the full colour: by its purity)
    r = min(r_raw, 1.0)
    black_raw = 1 - xyz[1] / tint_edge(edge, r)
    black = max(black_raw, 0.0)
    return dict(theta=theta, r=r, white=(1 - r) * (1 - black), black=black, colour=r * (1 - black),
                outside=(max(r_raw - 1, 0.0), max(-black_raw, 0.0)))


def raw(i):
    """White, black and colour content, and the hue on Ostwald's 100-step circle before calibration."""
    m = measure(xyz_of(*colors[i]["oklch"]))
    return None if m["theta"] is None else hue_number(m["theta"]), m["white"], m["black"], m["colour"]


# Calibration: Wada's orange (橙色) is 16PA in his colour-name books (1935 supplement, p. 14).
OFFSET = (16 - raw(index["Orange"])[0]) % 100


def sector_angle(sector):
    """The chromaticity angle of one of the 24 hues (sector 0 is yellow): where the number is the sector's,
    found by halving (the number falls as the angle rises)."""
    def diff(theta):
        return (hue_number(theta) + OFFSET - sector * 100 / 24 + 50) % 100 - 50
    lo = next(x for x in range(360) if diff(x) >= 0 and diff(x + 1) < 0)
    hi = lo + 1
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if diff(mid) >= 0 else (lo, mid)
    return (lo + hi) / 2


SECTOR_ANGLES = [sector_angle(s) for s in range(24)]


def cell_xyz(sector, a, b):
    """A cell's own colour: white GREYS[a], 1 - black GREYS[b], so colour GREYS[b] - GREYS[a]. Its share of
    full colour is r = colour / (white + colour), at the sector's chromaticity angle, and it is as far below
    the press's tint edge as its black says: Y = (1 - black) Ymax(r). A grey (a == b) is GREYS[a] white."""
    if a == b or sector is None:
        return [GREYS[a] * v for v in WHITE]
    theta = SECTOR_ANGLES[sector]
    dF, sF, edge = ray(theta)
    r = (GREYS[b] - GREYS[a]) / GREYS[b]
    u = r * sF / (SW * (1 - r) + r * sF)  # the purity of share r: the inverse of measure()'s
    Y = GREYS[b] * tint_edge(edge, r)
    x, y = XW + u * dF * math.cos(math.radians(theta)), YW + u * dF * math.sin(math.radians(theta))
    return [x * Y / y, Y, (1 - x - y) * Y / y]


def step(v):
    """The nearest grey, on a log scale (the greys are evenly spaced to the eye)."""
    return min(range(len(GREYS)), key=lambda k: abs(math.log(max(v, 1e-3)) - math.log(GREYS[k])))


def ostwald(i):
    n, w, k, c = raw(i)
    a, b = step(w), step(1 - k)  # first letter: white content; second: black content
    if a <= b or n is None:  # no colour content left at this precision: a grey, on the axis
        a = b = int((a + b) / 2 + 0.5)  # rounding half up, as the site's Math.round
    n = None if a == b else (n + OFFSET) % 100
    sector = None if n is None else round(n * 24 / 100) % 24  # the 24 hues of Wada's Figure 1: 0 is yellow
    return dict(n=n, sector=sector, white=w, black=k, colour=c,
                code=LETTERS[a].upper() if a == b else f"{round(n) % 100}{LETTERS[a]}{LETTERS[b]}".upper(),
                level=a + b, ring=a - b)


if __name__ == "__main__":
    print(f"Calibration: Orange -> 16, so hue 0 (yellow) is where the mean OKLCH hue is {OFFSET * 3.6 % 360:.1f} degrees, 3.6 degrees less per step\n")
    print("The 24 hues' full colours (OKLCH): " + "; ".join(" ".join(f"{v:g}" for v in oklch_of(cell_xyz(s, 15, 0))) for s in range(24)) + "\n")
    o = ostwald(index["Orange"])
    print(f"Orange: {o['code']} (white {o['white']:.3f}, black {o['black']:.3f}); Wada: 16PA (white 0.036, black 0.109)\n")
    print("Yellow, Red, Sea Green: " + ", ".join(f"{ostwald(index[n])['n']:.1f} ({ostwald(index[n])['code']})" for n in ("Yellow", "Red", "Sea Green")) + "\n")

    # How far a full colour and its complement are from opposite in OKLCH hue.
    skew = max(abs(((full_hue(t + 180) - full_hue(t)) % 360) - 180) for t in range(360))
    print(f"A full colour and its complement: up to {skew:.0f} degrees of OKLCH hue from opposite")
    spans = sorted(((full_hue(SECTOR_ANGLES[s]) - full_hue(SECTOR_ANGLES[(s + 1) % 24])) % 360, s) for s in range(24))
    print(f"From one sector's full colour to the next: {spans[0][0]:.1f} to {spans[-1][0]:.1f} degrees of OKLCH hue: "
          f"narrowest from sector {spans[0][1]} to {(spans[0][1] + 1) % 24}, widest from {spans[-1][1]} to {(spans[-1][1] + 1) % 24}\n")

    pairs = [("Spectrum Red", "Sea Green"), ("Red Orange", "Green Blue"), ("Orange", "Peacock Blue"),
             ("Yellow Orange", "Antwerp Blue"), ("Apricot Yellow", "Blue"), ("Yellow", "Deep Lyons Blue"),
             ("Lemon Yellow", "Violet Ultramarine"), ("Light Green Yellow", "Violet"),
             ("Yellow Green", "Red Violet"), ("Night Green", "Rosolane Purple")]
    print("Wada's complementary pairs (1935, p. 22): hue numbers, and how far from opposite (50 steps apart)")
    offs = []
    for a, b in pairs:
        na, nb = ostwald(index[a])["n"], ostwald(index[b])["n"]
        gap = abs(na - nb) % 100
        offs.append(abs(50 - min(gap, 100 - gap)))
        print(f"  {a:18s} {na:5.1f}   {b:18s} {nb:5.1f}   off by {offs[-1]:4.1f}")
    print(f"  within 3 steps: {sum(o <= 3 for o in offs)} of {len(offs)}; on average {sum(offs) / len(offs):.1f} off")

    # Plate 8 of the 1935 atlas (Hama and Wada): 12 hues, each as tint, full colour ("as saturated as
    # possible") and shade, with the names of Wada's books (colors.json's "atlas").
    plate = {h: {} for h in ("yellow", "orange-yellow", "orange", "red", "purple-red", "red-purple", "purple",
                             "purple-blue", "blue", "blue-green", "green", "yellow-green")}  # the plate's order
    for i, c in enumerate(colors):
        if "atlas" in c:
            plate[c["atlas"]["hue"]][c["atlas"]["tone"]] = ostwald(i)
    print("\nPlate 8 of the 1935 atlas: tint, full colour and shade per hue (codes, then hue numbers)")
    at_rim = tint_fuller = close = tint_a = 0
    for hue, tones in plate.items():
        row = [tones.get(t) for t in ("tint", "full colour", "shade")]
        here = [o for o in row if o]
        ns = [o["n"] for o in here]
        spread = max((b - a) % 100 for a in ns for b in ns if (b - a) % 100 <= 50)
        tint, full = tones["tint"], tones["full colour"]  # every hue has both; purple-blue has no shade
        at_rim += full["code"].endswith("PA")
        tint_fuller += tint["colour"] > full["colour"]
        tint_a += tint["code"].endswith("A")
        close += spread <= 4
        print(f"  {hue:13s} " + " ".join(f"{o['code'] if o else '-':5s}" for o in row) + "   " + " ".join(f"{o['n']:5.1f}" if o else "    -" for o in row) + f"   spread {spread:4.1f}")
    print(f"Full colours at the rim (PA): {at_rim} of {len(plate)}; tints with no black (second letter A): {tint_a}; "
          f"tint with more colour than its full colour: {tint_fuller}; tint, full colour and shade within 4 steps of hue: {close}")

    placed = [ostwald(i) for i in range(len(colors))]
    levels = Counter(p["level"] for p in placed)
    rings = Counter(p["ring"] for p in placed)
    cells = Counter((p["sector"], p["ring"], p["level"]) for p in placed)
    top = 2 * (len(GREYS) - 1)
    print(f"\nColours per level (0 = white ... {top} = black):", [levels[s] for s in range(top + 1)])
    print(f"Colours per ring (0 = greys on the axis ... {len(GREYS) - 1} = pure colour):", [rings[r] for r in range(len(GREYS))])
    print(f"Cells used: {len(cells)}; with 2 or more colours: {sum(1 for v in cells.values() if v > 1)}; most in one: {max(cells.values())}")
    full = sorted((p["n"], colors[i]["name"]) for i, p in enumerate(placed) if p["ring"] == 15)
    print(f"Full colours (ring 15): {len(full)}: " + ", ".join(f"{n} ({h:.1f})" for h, n in full))
    print("Greys: " + ", ".join(f"{colors[i]['name']} ({p['code']})" for i, p in enumerate(placed) if p["n"] is None))
    print(f"Codes using J: {sum('J' in p['code'] for p in placed)}")

    # Beyond the press: purer than its full colour, or brighter than its tint edge (measured at the edge).
    out = sorted(((max(m["outside"]), colors[i]["name"], m["outside"]) for i, m in ((i, measure(xyz_of(*c["oklch"]))) for i, c in enumerate(colors)) if max(m["outside"]) > 0), reverse=True)
    print(f"\nBeyond the press's tint edge or full colour: {len(out)}; furthest: " + ", ".join(f"{n} (share {o[0]:+.4f}, black {-o[1]:+.4f})" for _, n, o in out[:4]))

    # How close each colour is to a neighbouring cell: the distance to the nearest boundary, in steps
    # (log steps for the letters, sectors for the hue).
    bounds = [math.sqrt(GREYS[k] * GREYS[k + 1]) for k in range(len(GREYS) - 1)]
    log_step = math.log(GREYS[0] / GREYS[1])
    def margin(i):
        o = ostwald(i)
        m = min(abs(math.log(max(v, 1e-4) / bd)) / log_step for v in (o["white"], 1 - o["black"]) for bd in bounds)
        return m if o["n"] is None else min(m, abs((o["n"] * 24 / 100) % 1 - 0.5))
    margins = [margin(i) for i in range(len(colors))]
    print(f"Within 0.05 of a step from a neighbouring cell: {sum(m < 0.05 for m in margins)}; within 0.1: {sum(m < 0.1 for m in margins)}")

    # What chance would give: each value anywhere in its own cell, evenly. A value beyond the scale's
    # ends (whiter than A, darker than P) keeps its margin; the end cells have a boundary on one side only.
    def near_by_chance(i, t):
        o = ostwald(i)
        far = 1
        for v in (o["white"], 1 - o["black"]):
            x = math.log(GREYS[0] / max(v, 1e-4)) / log_step  # in steps, A = 0
            if x < 0 or x > len(GREYS) - 1:
                p = float(min(abs(x - (k + 0.5)) for k in range(len(GREYS) - 1)) < t)
            else:
                p = t if round(x) in (0, len(GREYS) - 1) else 2 * t
            far *= 1 - p
        if o["n"] is not None:
            far *= 1 - 2 * t
        return 1 - far
    print("By chance: " + "; ".join(f"within {t}: {sum(near_by_chance(i, t) for i in range(len(colors))):.0f}" for t in (0.05, 0.1)))

    # Perceptual check: is the nearest of the system's cell colours (in OKLab) the colour's own cell?
    ideal = {}
    for a in range(len(GREYS)):
        for b in range(a + 1):
            if a == b:
                ideal[(2 * a, 0, None)] = oklab_of(cell_xyz(None, a, b))
                continue
            for sector in range(24):
                ideal[(a + b, a - b, sector)] = oklab_of(cell_xyz(sector, a, b))
    own = neighbour = further = 0
    gaps, dists = [], []
    for i in range(len(colors)):
        o = ostwald(i)
        cell = (o["level"], o["ring"], o["sector"])
        lab = oklab_of(xyz_of(*colors[i]["oklch"]))
        d = {k: math.dist(lab, v) for k, v in ideal.items()}
        best = min(d, key=d.get)
        dists.append(d[cell])
        if best == cell:
            own += 1
            continue
        steps = (abs(best[0] - cell[0]), abs(best[1] - cell[1]), 0 if None in (best[2], cell[2]) else min((best[2] - cell[2]) % 24, (cell[2] - best[2]) % 24))
        if max(steps) <= 1 or steps == (2, 0, 0):  # next to it in the solid
            neighbour += 1
        else:
            further += 1
            gaps.append(d[cell] - d[best])
    dists.sort()
    print(f"Nearest cell colour (OKLab) is its own: {own}; a neighbouring cell: {neighbour}; further off: {further}" + (f", closer by at most {max(gaps):.3f}" if gaps else ""))
    print(f"Distance to its own cell's colour: median {dists[len(dists) // 2]:.3f}, largest {dists[-1]:.3f}")
