#!/usr/bin/env python3
"""Place Wada's colours in Munsell's system, and list the system's own colours, into munsell.json.

    uv run -q --python 3.12 --with colour-science --with scipy python scripts/munsell.py

It needs colour-science, which has the Munsell renotation data and Centore's conversion, and scipy, which
that conversion uses; uv fetches them (and numpy) for the run. Takes about a minute.

Munsell notation is measured as a chip is: against the ideal white (the perfect reflecting diffuser), under
Illuminant C. Our values (colors.json) are relative to the paper, as the book's CMYK was printed on it, so
each colour's Y is scaled by the paper's own, from the profile's media white point (Japan Color 2011
Coated, about 0.856), and its colour adapted from D65 (CSS's white, our values') to C with Bradford's
transform. Wada's white paper comes out N9.4.

munsell.json holds:

- `paper`: the paper's Y against the ideal white.
- `colours`: per colour of colors.json, in its order, its Munsell hue (ASTM's hue number: 5R is 5, 5YR
  15, ... 10RP 100), value and chroma, to 0.01.
- `chips`: the system's own colours: the 1943 renotation's real colours (Newhall, Nickerson and Judd,
  2,734 of them, within the MacAdam limits of what a surface can reflect), as [hue, value, chroma] and
  OKLCH, in our space (relative to the paper, D65), rounded as colors.json is. Their Y is the
  renotation's, relative to magnesium oxide, so it is scaled by 0.975, magnesium oxide's reflectance
  against the ideal white (as ASTM D1535 does).
- `greys`: the greys N1 to N9 (ASTM D1535's value scale), as OKLCH lightness.
"""
import json
import math
import struct
import warnings
from pathlib import Path

# colour-science checks each colour against its table of the MacAdam limits (the most a surface can
# reflect), which is coarse at the dark end: it flags dark printed colours that are real. Each colour is
# checked by converting it back instead (main). Nor is matplotlib needed (for plots): no warning that
# it's missing.
warnings.filterwarnings("ignore", message=".*MacAdam.*")
warnings.filterwarnings("ignore", message=".*Matplotlib.*")

import numpy as np
import colour
from colour.notation.datasets.munsell import MUNSELL_COLOURS_REAL
from colour.notation.munsell import hue_to_ASTM_hue

import cmyk_to_oklch as cx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "munsell.json"
MGO = 0.975  # magnesium oxide's reflectance factor against the ideal white

OBSERVER = colour.CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"]
D65, C = colour.xy_to_XYZ(OBSERVER["D65"]), colour.xy_to_XYZ(OBSERVER["C"])
# OKLab (Ottosson), from XYZ (D65); and back.
M1 = np.array([[0.8189330101, 0.3618667424, -0.1288597137], [0.0329845436, 0.9293118715, 0.0361456387],
               [0.0482003018, 0.2643662691, 0.6338517070]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
               [0.0259040371, 0.7827717662, -0.8086757660]])


def paper_y():
    """The paper's Y against the ideal white: the profile's media white point (wtpt, XYZ)."""
    data = cx.load_tag(b"wtpt")
    return struct.unpack(">i", data[12:16])[0] / 65536


def xyz_of(oklch):
    L, Cc, h = oklch
    lab = np.array([L, Cc * math.cos(math.radians(h)), Cc * math.sin(math.radians(h))])
    return np.linalg.inv(M1) @ (np.linalg.inv(M2) @ lab) ** 3


def oklch_of(xyz):
    """Rounded as colors.json is."""
    L, a, b = M2 @ np.cbrt(M1 @ xyz)
    Cc = round(math.hypot(a, b), 4)
    h = round(math.degrees(math.atan2(b, a)) % 360, 2)
    return [round(float(L), 4), Cc, 0 if Cc == 0 or h == 360 else h]


def to_c(xyz):
    return colour.adaptation.chromatic_adaptation_VonKries(xyz, D65, C, transform="Bradford")


def to_d65(xyz):
    return colour.adaptation.chromatic_adaptation_VonKries(xyz, C, D65, transform="Bradford")


def main():
    paper = paper_y()
    worst = 0.0
    colors = json.loads((ROOT / "colors.json").read_text())
    out = []
    for c in colors:
        xyY = colour.XYZ_to_xyY(to_c(xyz_of(c["oklch"]) * paper))
        spec = colour.notation.munsell.xyY_to_munsell_specification(xyY)
        hue, value, chroma, code = spec
        back = colour.notation.munsell.munsell_specification_to_xyY(spec)
        worst = max(worst, float(np.linalg.norm(M2 @ np.cbrt(M1 @ to_d65(colour.xyY_to_XYZ(back)))
                                                - M2 @ np.cbrt(M1 @ to_d65(colour.xyY_to_XYZ(xyY))))))
        if np.isnan(hue):  # exactly grey
            out.append([None, round(float(value), 2), 0])
        else:
            out.append([round(float(hue_to_ASTM_hue([hue, code])), 2), round(float(value), 2), round(float(chroma), 2)])
    chips = []
    for (name, value, chroma), (x, y, Y) in MUNSELL_COLOURS_REAL:
        hue, code = colour.notation.munsell.parse_munsell_colour(f"{name} {value}/{chroma}")[[0, 3]]
        xyz = to_d65(colour.xyY_to_XYZ([x, y, Y * MGO / 100])) / paper
        chips.append([float(hue_to_ASTM_hue([hue, code])), int(value), int(chroma), *oklch_of(xyz)])
    chips.sort()
    greys = []
    for v in range(1, 10):
        Y = colour.notation.munsell.luminance_ASTMD1535(v) / 100
        greys.append([v, oklch_of(to_d65(colour.xyY_to_XYZ([*OBSERVER["C"], Y])) / paper)[0]])
    OUT.write_text(
        '{"source":"Munsell renotation (1943), real colours, Illuminant C; colour-science %s","paper":%.4f,\n' % (colour.__version__, paper)
        + '"colours":[\n' + ",\n".join(json.dumps(v) for v in out) + "],\n"
        + '"chips":[\n' + ",\n".join(json.dumps(v, separators=(",", ":")) for v in chips) + "],\n"
        + '"greys":' + json.dumps(greys, separators=(",", ":")) + "}\n")
    print(f"paper Y {paper:.4f}; {len(out)} colours, {len(chips)} chips; wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")
    print(f"each colour's notation, converted back, is within {worst:.5f} of it in OKLab")
    for name in ("White", "Black", "Orange", "Red", "Blue"):
        h, v, cc = out[[c["name"] for c in colors].index(name)]
        print(f"  {name}: hue {h}, value {v}, chroma {cc}")


if __name__ == "__main__":
    main()
