"""Place Wada's colours in Ostwald's colour system, and check the placement against Wada's own data.

The same computation as the site's Ostwald view (index.html, ostwaldSystem). Prints the checks quoted in
notes/ostwald.md. Run from anywhere:

    python3 notes/ostwald.py

Standard library only.
"""
import colorsys
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
colors = json.loads((ROOT / "colors.json").read_text())
index = {c["name"]: i for i, c in enumerate(colors)}

# Wada's grey scale (1935 supplement, Figure 2): 16 letters, A to P with J, from Ostwald's white (0.891
# white content) to his black (0.0355), evenly spaced on a log scale. Ostwald's own scale skips J.
# A grey's black content is 1 minus its white.
LETTERS = "abcdefghijklmnop"
GREYS = [0.891 * (0.0355 / 0.891) ** (k / 15) for k in range(16)]


def linear_srgb(L, C, h):
    """OKLCH -> linear sRGB, clipped to 0..1 (Ottosson's matrices)."""
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return [min(1, max(0, v)) for v in rgb]


def hexagonal_hue(r, g, b):
    """The hue of an additive mixture, in degrees (red 0, yellow 60, green 120, ...): complements are 180 apart."""
    hi, lo = max(r, g, b), min(r, g, b)
    d = hi - lo
    if d == 0:
        return None
    if hi == r:
        return 60 * (((g - b) / d) % 6)
    if hi == g:
        return 60 * ((b - r) / d + 2)
    return 60 * ((r - g) / d + 4)


def oklab(rgb):
    """Linear sRGB -> OKLab (Ottosson's matrices)."""
    r, g, b = rgb
    lms = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b, 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b, 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in lms)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def full_colour(h):
    """The full colour of hexagonal hue h (degrees), in linear sRGB: HSV with saturation and value 1."""
    return list(colorsys.hsv_to_rgb((h % 360) / 360, 1, 1))


def hue_number(h):
    """Ostwald's 100-step hue of hexagonal hue h, before calibration. Ostwald spaced his circle evenly
    to the eye, with complements opposite. The full colour's OKLCH hue is even to the eye, and the
    hexagonal hue puts complements opposite, but sRGB's full colours aren't symmetrical in OKLCH: a
    full colour and its complement are up to 29 degrees from opposite. So the number takes the mean of
    the two, the complement's turned half round, and complements stay exactly 50 steps apart. The circle
    runs the other way round from OKLCH's, a quarter of it (25 steps) per 90 degrees."""
    def ok_hue(rgb):
        _, a, b = oklab(rgb)
        return math.degrees(math.atan2(b, a))
    h1, h2 = ok_hue(full_colour(h)), ok_hue(full_colour(h + 180))
    mean = h1 + ((h2 - h1) % 360 - 180) / 2
    return (-mean / 3.6) % 100


def raw(i):
    """White, black and colour content, and the hue on Ostwald's 100-step circle before calibration."""
    r, g, b = linear_srgb(*colors[i]["oklch"])
    w, k = min(r, g, b), 1 - max(r, g, b)
    h = hexagonal_hue(r, g, b)
    return None if h is None else hue_number(h), w, k, 1 - w - k


# Calibration: Wada's orange (橙色) is 16PA in his colour-name books (1935 supplement, p. 14).
OFFSET = (16 - raw(index["Orange"])[0]) % 100


def sector_colour(sector):
    """The full colour of one of the 24 hues (sector 0 is yellow), in linear sRGB: the hexagonal hue
    whose number is the sector's, found by halving (the number falls as the hexagonal hue rises)."""
    def diff(h):
        return (hue_number(h) + OFFSET - sector * 100 / 24 + 50) % 100 - 50
    lo = next(x for x in range(360) if diff(x) >= 0 and diff(x + 1) < 0)
    hi = lo + 1
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if diff(mid) >= 0 else (lo, mid)
    return full_colour((lo + hi) / 2)


SECTOR_COLOURS = [sector_colour(s) for s in range(24)]


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
    print("The 24 hues' full colours: " + " ".join("#" + "".join(f"{round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)):02x}" for v in c) for c in SECTOR_COLOURS) + "\n")
    o = ostwald(index["Orange"])
    print(f"Orange: {o['code']} (white {o['white']:.3f}, black {o['black']:.3f}); Wada: 16PA (white 0.036, black 0.109)\n")

    pairs = [("Spectrum Red", "Sea Green"), ("Red Orange", "Green Blue"), ("Orange", "Peacock Blue"),
             ("Yellow Orange", "Antwerp Blue"), ("Apricot Yellow", "Blue"), ("Yellow", "Deep Lyons Blue"),
             ("Lemon Yellow", "Violet Ultramarine"), ("Light Green Yellow", "Violet"),
             ("Yellow Green", "Red Violet"), ("Night Green", "Rosolane Purple")]
    print("Wada's complementary pairs (1935, p. 22): hue numbers, and how far from opposite (50 steps apart)")
    for a, b in pairs:
        na, nb = ostwald(index[a])["n"], ostwald(index[b])["n"]
        gap = abs(na - nb) % 100
        print(f"  {a:18s} {na:5.1f}   {b:18s} {nb:5.1f}   off by {abs(50 - min(gap, 100 - gap)):4.1f}")

    placed = [ostwald(i) for i in range(len(colors))]
    levels = Counter(p["level"] for p in placed)
    rings = Counter(p["ring"] for p in placed)
    cells = Counter((p["sector"], p["ring"], p["level"]) for p in placed)
    top = 2 * (len(GREYS) - 1)
    print(f"\nColours per level (0 = white ... {top} = black):", [levels[s] for s in range(top + 1)])
    print(f"Colours per ring (0 = greys on the axis ... {len(GREYS) - 1} = pure colour):", [rings[r] for r in range(len(GREYS))])
    print(f"Cells used: {len(cells)}; with 2 or more colours: {sum(1 for v in cells.values() if v > 1)}; most in one: {max(cells.values())}")

    # Colours outside sRGB, clipped before they are measured.
    def unclipped(i):
        L, C, h = colors[i]["oklch"]
        a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
        l, m, s = ((L + x * a + y * b) ** 3 for x, y in ((0.3963377774, 0.2158037573), (-0.1055613458, -0.0638541728), (-0.0894841775, -1.2914855480)))
        return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    out = sorted(((min(min(v), 0) - max(max(v) - 1, 0), c["name"]) for c, v in ((c, unclipped(i)) for i, c in enumerate(colors)) if min(v) < -1e-3 or max(v) > 1 + 1e-3))
    print(f"\nOutside sRGB (clipped): {len(out)}; furthest: " + ", ".join(f"{n} ({d:+.3f})" for d, n in out[:3]))

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
                ideal[(2 * a, 0, None)] = oklab([GREYS[a]] * 3)
                continue
            for sector in range(24):
                ideal[(a + b, a - b, sector)] = oklab([GREYS[a] + (GREYS[b] - GREYS[a]) * v for v in SECTOR_COLOURS[sector]])
    own = neighbour = further = 0
    gaps, dists = [], []
    for i in range(len(colors)):
        o = ostwald(i)
        cell = (o["level"], o["ring"], o["sector"])
        lab = oklab(linear_srgb(*colors[i]["oklch"]))
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
    print(f"Nearest cell colour (OKLab) is its own: {own}; a neighbouring cell: {neighbour}; further off: {further}, closer by at most {max(gaps):.3f}")
    print(f"Distance to its own cell's colour: median {dists[len(dists) // 2]:.3f}, largest {dists[-1]:.3f}")
