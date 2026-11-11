#!/usr/bin/env python3
"""Place Wada's colours in PCCS, and list the system's own colours and tones, into pccs.json.

    uv run -q --python 3.12 --with colour-science --with scipy python scripts/pccs.py

It places Wada's colours from their Munsell notation as scripts/munsell.py finds it (unrounded: this runs
its conversion again). It needs colour-science (and scipy) for that and for the Munsell renotation's colours,
as munsell.py does; uv fetches them for the run. Takes a few minutes.

PCCS (the Practical Color Co-ordinate System, the Japan Color Research Institute's, 1964) is defined
through Munsell's notation: its lightness l is Munsell's value; its 24 hues h are points on Munsell's hue
circle; its saturation s is a scale of Munsell chroma per hue and value, from 0 (grey) to 9, the most
vivid pigment colours of each hue. The conversion here is Kobayasi and Yosiki's precise one (Mituo
Kobayasi and Kayoko Yosiki, "Mathematical Relation among PCCS Tones, PCCS Color Attributes and Munsell
Color Attributes", Journal of the Color Science Association of Japan 25(4), 2001, 249-261), fitted to
the institute's reference Munsell values for the PCCS grid (Matsuie's, 2,844 points):

- l = V (their equations 10 and 12);
- hue: between the 24 hues' Munsell hues (their table 4, from the institute's 201-L chart), linearly;
- saturation: C = (a3 s^3 + a2 s^2 + a1 s) (1 - exp(-g(h) l)) (equation 14), with (a1, a2, a3) per even
  hue (table 2) linear between them, and g(h) = 0.81 - 0.24 sin((h - 2.6) pi / 12) (equation 2); and back,
  that cubic solved for s by Newton's method from the quadratic of their simple algorithm (equations 13
  and 15).

Its tones: each is defined by a representative colour per hue (their table 1, from 201-L: the even hues;
vivid and bright have all 24, whose odd ones aren't in the paper). The odd hues' representatives are
from the tone coordinates (equation 20 and table 8): l = t + m(h) s, rounded to 0.5 as 201-L's are; they
give the even hues' table 1 values back but for a few, half a step off. A colour's tone is the nearest
representative's in those coordinates (s and t = l - m(h) s, which make the representatives the same for
every hue), as the paper suggests; pale+ and light+ (201-L's) are pale and light. Under s 1 (where the
paper's figure 13 draws the edge of the greys), a colour's tone is a grey's: W, ltGy, mGy, dkGy or Bk, by
its lightness rounded to 0.5 (W 9.5; ltGy 7.5 to 9; mGy 4 to 7; dkGy 2 to 3.5; Bk 1.5: 201-L's greys,
and those between them with the middle ones). A colour's tone is from its own values, its cell from
them rounded (h and s whole, l to 0.5): a colour just under s 1 is in a cell of s 1, with a grey's tone.

pccs.json holds:

- `colours`: per colour of colors.json, in its order, its PCCS hue h (1 to 25, 25 being 1 again; null
  for a grey), lightness l and saturation s, to 0.0001; its tone.
- `chips`: the system's own colours: the PCCS grid (h 1 to 24, l in steps of 0.5, s whole) as far as
  the Munsell renotation's real colours go (within the MacAdam limits of what a surface can reflect:
  its chroma under the real chips' most at its hue and value, between the pages and values round it,
  none at value 10, the ideal white; and where the renotation's data, which colour-science interpolates,
  has that chroma at the values round it), as [h, l, s, tone] and OKLCH, in our space (relative to the paper, D65) as munsell.json's chips are.
  colour-science gives a notation's Y against the ideal white (ASTM D1535's), so a chip is the Munsell
  chip of the same notation.
- `greys`: n-1.5 to n-9.5, as [l, its tone, OKLCH lightness].
- `tones`: per tone, its code and name, its coordinates (s, t) and its representative's l per hue.
"""
import json
import math
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*Matplotlib.*")

import numpy as np
import colour
from colour.notation.datasets.munsell import MUNSELL_COLOURS_REAL

sys.dont_write_bytecode = True  # (no __pycache__ beside the scripts)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import munsell as ms  # noqa: E402
from munsell import OBSERVER, to_d65  # noqa: E402
from oklab import oklch_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pccs.json"

# Table 4: each PCCS hue's Munsell hue, in ASTM's numbers (5R is 5, ... 10RP 100); 25 is 1 again.
HUES = [None, 0, 4, 7, 10, 14, 18, 22, 25, 28, 33, 38, 43, 49, 55, 60, 65, 70, 73, 76, 79, 83, 87, 91, 96, 100]
# Table 2: (a1, a2, a3) for the even hues.
COEFFS = {
    2: (1.042805, 0.046437, 0.001607), 4: (1.079160, 0.025470, 0.003052), 6: (1.039472, 0.054749, -0.000511),
    8: (0.925185, 0.050245, 0.000953), 10: (0.968557, 0.012537, 0.003375), 12: (1.070433, -0.047359, 0.007385),
    14: (1.087030, -0.051075, 0.006526), 16: (1.089652, -0.050206, 0.006056), 18: (0.880861, 0.060300, -0.001280),
    20: (0.897326, 0.053912, -0.000860), 22: (0.887834, 0.055086, -0.000847), 24: (0.853642, 0.084379, -0.002798),
}
# Table 1: each tone's representative per even hue (2, 4, ... 24): its s, and its l per hue. Table 8: the
# tone's coordinates (s, t). pale+ and light+ are 201-L's, between pale and light and the next tones.
TONES = [  # code, name, s, t, l for h = 2, 4, ... 24
    ("p", "pale", 2, 8.6, [8.5, 8.5, 9.0, 9.0, 9.0, 8.5, 8.5, 8.5, 8.0, 8.0, 8.0, 8.5]),
    ("p+", "pale", 3, 8.2, [8.0, 8.0, 8.5, 9.0, 8.5, 8.0, 8.0, 8.0, 7.5, 7.5, 7.5, 8.0]),
    ("ltg", "light grayish", 2, 7.1, [7.0, 7.0, 7.5, 7.5, 7.5, 7.0, 7.0, 7.0, 6.5, 6.5, 6.5, 7.0]),
    ("g", "grayish", 2, 4.1, [4.0, 4.0, 4.5, 4.5, 4.5, 4.0, 4.0, 4.0, 3.5, 3.5, 3.5, 4.0]),
    ("dkg", "dark grayish", 2, 2.1, [2.0, 2.0, 2.5, 2.5, 2.5, 2.0, 2.0, 2.0, 1.5, 1.5, 1.5, 2.0]),
    ("lt", "light", 5, 7.8, [7.5, 8.0, 8.5, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.5, 6.5, 7.0]),
    ("lt+", "light", 6, 7.3, [7.0, 7.5, 8.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 6.0, 6.0, 6.5]),
    ("sf", "soft", 5, 6.3, [6.0, 6.5, 7.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 5.0, 5.0, 5.5]),
    ("d", "dull", 5, 4.8, [4.5, 5.0, 5.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.5, 3.5, 4.0]),
    ("dk", "dark", 5, 3.0, [2.5, 3.0, 3.5, 4.0, 3.5, 3.0, 2.5, 2.5, 2.0, 2.0, 2.0, 2.5]),
    ("b", "bright", 8, 6.6, [6.0, 6.5, 7.5, 8.5, 7.5, 6.5, 6.0, 5.5, 5.0, 5.0, 5.0, 5.5]),
    ("s", "strong", 8, 5.2, [4.5, 5.0, 6.5, 7.5, 6.5, 5.0, 4.5, 4.0, 3.5, 3.5, 3.5, 4.0]),
    ("dp", "deep", 8, 4.1, [3.5, 4.0, 5.0, 6.0, 5.0, 4.0, 3.5, 3.0, 2.5, 2.5, 2.5, 3.0]),
    ("v", "vivid", 9, 5.5, [4.5, 5.5, 7.0, 8.0, 7.0, 5.5, 4.5, 4.0, 3.5, 3.5, 3.5, 4.0]),
]
FOLD = {"p+": "p", "lt+": "lt"}  # 201-L's extra representatives, of these tones
GREY_TONES = [(9.5, "W"), (7.5, "ltGy"), (4.0, "mGy"), (2.0, "dkGy"), (0, "Bk")]  # each from this l up


def gamma(h):
    """Equation 2."""
    return 0.81 - 0.24 * math.sin((h - 2.6) * math.pi / 12)


def coeffs(h):
    """(a1, a2, a3) at hue h: table 2's, linear between the even hues round it."""
    e0 = 2 * math.floor(h / 2)
    f = (h - e0) / 2
    a, b = COEFFS[(e0 - 1) % 24 + 1], COEFFS[(e0 + 1) % 24 + 1]
    return [x + f * (y - x) for x, y in zip(a, b)]


def hue_of(h):
    """PCCS hue (1 to 25) to ASTM's Munsell hue number (0 to 100): table 4, linear between."""
    i = min(24, math.floor(h))
    return HUES[i] + (h - i) * (HUES[i + 1] - HUES[i])


def pccs_hue(H):
    """ASTM's Munsell hue number to PCCS hue (1 to 25): table 4, linear between."""
    H %= 100
    i = max(i for i in range(1, 25) if HUES[i] <= H)
    return i + (H - HUES[i]) / (HUES[i + 1] - HUES[i])


def to_munsell(h, l, s):
    """PCCS (h, l, s) to Munsell (H, V, C): the precise algorithm (equations 10, 14 and table 4)."""
    a1, a2, a3 = coeffs(h)
    return hue_of(h), l, (a3 * s**3 + a2 * s**2 + a1 * s) * (1 - math.exp(-gamma(h) * l))


def to_pccs(H, V, C):
    """Munsell (H, V, C) to PCCS (h, l, s): the precise algorithm (equations 12, 15 and table 4)."""
    h = pccs_hue(H)
    target = C / (1 - math.exp(-gamma(h) * V))
    big = 12 + 1.7 * math.sin((h + 2.2) * math.pi / 12)  # equation 4, for the start (equation 13)
    s = (-0.077 + math.sqrt(0.077**2 + 4 * 0.0040 * target / big)) / (2 * 0.0040)
    a1, a2, a3 = coeffs(h)
    if a3 < 0:  # the cubic has a top: a chroma past it has no saturation (and Newton's method would run off)
        top = (-a2 - math.sqrt(a2 * a2 - 3 * a1 * a3)) / (3 * a3)
        if target > a3 * top**3 + a2 * top**2 + a1 * top:
            raise ValueError(f"Munsell {H} {V}/{C}: beyond the conversion's most saturation at its hue, s {top:.1f}")
    for _ in range(50):
        step = (a3 * s**3 + a2 * s**2 + a1 * s - target) / (3 * a3 * s**2 + 2 * a2 * s + a1)
        s -= step
        if abs(step) < 1e-12:
            break
    return h, V, s


def cell(h, l, s):
    """The cell the page puts a colour in (index.html's pccsSystem, rounding halves up as Math.round does): its
    page (None for a grey), level (0 is l 9.5) and ring."""
    j = 0 if h is None else math.floor(s + 0.5)
    return ((math.floor(h + 0.5) - 2) % 24 if j else None), min(16, max(0, 19 - math.floor(2 * l + 0.5))), j


def m_of(h):
    """Equation 19: the tone coordinates' shear at hue h."""
    return 0.25 - 0.34 * math.sqrt(max(0.0, 1 - math.sin((h - 2) * math.pi / 12)))


def tone_of(h, l, s):
    """The nearest tone representative's in the tone coordinates (s, t), table 8; pale+ is pale, light+ light."""
    t = l - m_of(h) * s
    code = min(TONES, key=lambda T: (T[2] - s) ** 2 + (T[3] - t) ** 2)[0]
    return FOLD.get(code, code)


def grey_tone(l):
    """A grey's tone, by its lightness rounded to 0.5 (halves up, as cell() rounds them)."""
    l = math.floor(2 * l + 0.5) / 2
    return next(name for top, name in GREY_TONES if l >= top)


def representative(tone, h):
    """A tone's representative's l at hue h (1 to 24): table 1's, or from its coordinates for the odd hues."""
    code, _, s, t, ls = tone
    if h % 2 == 0:
        return ls[h // 2 - 1]
    return round(2 * (t + m_of(h) * s)) / 2


def spec_of(H, V, C):
    """colour-science's Munsell specification (hue in its family, value, chroma, family code)."""
    f = math.ceil(H / 10 - 1e-9) - 1
    n = H - 10 * f
    if n <= 1e-9:
        f, n = f - 1, 10.0
    return np.array([n, V, C, [7, 6, 5, 4, 3, 2, 1, 10, 9, 8][f % 10]], float)


def main():
    paper = ms.paper_y()
    # The real chips' most chroma at each page (ASTM hue 2.5 k) and value; nothing at value 10, the ideal white.
    most = {}
    for (name, value, chroma), _ in MUNSELL_COLOURS_REAL:
        hue, code = colour.notation.munsell.parse_munsell_colour(f"{name} {value}/{chroma}")[[0, 3]]
        k = round(float(colour.notation.munsell.hue_to_ASTM_hue([hue, code])) / 2.5) % 40
        most[k, int(value)] = max(most.get((k, int(value)), 0), chroma)

    def real(H, V, C):
        """Under the real chips' most chroma, between the pages and values round it."""
        if V > 10 or V < 1:
            return False
        k0, f = divmod(H / 2.5, 1)
        v0, g = divmod(V, 1)
        at = lambda k, v: most.get((int(k) % 40, int(v)), 0)
        top = ((1 - f) * (1 - g) * at(k0, v0) + f * (1 - g) * at(k0 + 1, v0)
               + (1 - f) * g * at(k0, v0 + 1) + f * g * at(k0 + 1, v0 + 1))
        return C <= top + 1e-9

    def colour_of(H, V, C):
        xyY = colour.notation.munsell.munsell_specification_to_xyY(spec_of(H, V, C))
        return oklch_of(to_d65(colour.xyY_to_XYZ(xyY)) / paper)

    # The paper's checks: 201-L's chroma for colours its simple algorithm had a whole step off (table 7).
    for h, l, s, c in [(18, 5.0, 8, 10.0), (18, 3.5, 8, 10.0), (18, 2.5, 8, 9.5), (18, 3.5, 9, 11.5), (19, 3.5, 9, 11.5), (23, 5.0, 8, 10.0), (23, 3.5, 9, 11.5)]:
        print(f"  check {h}:{l}-{s}s: C {to_munsell(h, l, s)[2]:.2f} (201-L {c}); back, s {to_pccs(*to_munsell(h, l, s))[2]:.4f}")
    # Wada's colours, from their Munsell notation, unrounded; stored to 0.0001, enough that rounding them
    # again, as the page does to find the cell, finds the cell of the unrounded values.
    names = [c["name"] for c in json.loads((ROOT / "colors.json").read_text())]
    colours = []
    for name, c in zip(names, json.loads((ROOT / "colors.json").read_text())):
        H, V, C, _ = ms.notation(c["oklch"], paper)
        if H is None or C == 0:
            colours.append([None, round(V, 4), 0, grey_tone(V)])
            continue
        h, l, s = to_pccs(H, V, C)
        tone = tone_of(h, l, s) if s >= 1 else grey_tone(l)
        colours.append([round(h, 4), round(l, 4), round(s, 4), tone])
        assert cell(*colours[-1][:3]) == cell(h, l, s), f"{name}: stored {colours[-1]} is in cell {cell(*colours[-1][:3])}, its values {[h, l, s]} in {cell(h, l, s)}"
    # The grid, as far as the real colours go; and each tone's representatives, which are on it.
    reps = {(h, representative(T, h), T[2]) for T in TONES for h in range(1, 25)}
    chips, unreal = [], []
    for h in range(1, 25):
        for l in np.arange(1.5, 9.51, 0.5):
            l = float(l)
            for s in range(1, 40):
                H, V, C = to_munsell(h, l, s)
                try:
                    ok, oklch = real(H, V, C), colour_of(H, V, C)
                except ValueError:  # beyond the renotation's data at a value round it: no colour for it
                    ok, oklch = False, None
                if not ok:
                    if (h, l, s) in reps:
                        unreal.append((h, l, s, oklch is not None))
                    if oklch is None or (h, l, s) not in reps:
                        break
                chips.append([h, l, s, tone_of(h, l, s), *oklch])
    greys = []
    for l in np.arange(1.5, 9.51, 0.5):
        Y = colour.notation.munsell.luminance_ASTMD1535(float(l)) / 100
        greys.append([float(l), grey_tone(float(l)), oklch_of(to_d65(colour.xyY_to_XYZ([*OBSERVER["C"], Y])) / paper)[0]])
    tones = [[code, name, s, t, [representative(T, h) for h in range(1, 25)]] for T in TONES for (code, name, s, t, _) in [T]]
    OUT.write_text(
        '{"source":"PCCS, by Kobayasi and Yosiki\'s precise conversion (2001) from the Munsell renotation (1943), Illuminant C; colour-science %s",\n' % colour.__version__
        + '"colours":[\n' + ",\n".join(json.dumps(v) for v in colours) + "],\n"
        + '"chips":[\n' + ",\n".join(json.dumps(v, separators=(",", ":")) for v in chips) + "],\n"
        + '"greys":' + json.dumps(greys, separators=(",", ":")) + ",\n"
        + '"tones":[\n' + ",\n".join(json.dumps(v, separators=(",", ":")) for v in tones) + "]}\n")
    print(f"{len(colours)} colours, {len(chips)} chips (s up to {max(c[2] for c in chips)}); wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")
    print(f"representatives beyond the real colours, kept: {unreal}")
    for name in ("White", "Black", "Orange", "Red", "Blue"):
        print(f"  {name}: {colours[names.index(name)]}")


if __name__ == "__main__":
    main()
