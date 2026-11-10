#!/usr/bin/env python3
"""Estimate CMYK for every cell of the Ostwald view and store it in ostwald-cmyk.json.

    python3 scripts/ostwald_cmyk.py

The view's empty cells show the Ostwald system's own colour (see notes/ostwald.md), which has no
CMYK of its own. This estimates one the way a printer would: colour -> CIE Lab (D50) -> CMYK through
the same Japan Color 2011 Coated profile that turns the book's CMYK into OKLCH (cmyk_to_oklch.py),
using its colorimetric table B2A1, the inverse of the A2B1 table used there. The profile's table also
fixes how much black replaces cyan, magenta and yellow.

The cells are measured against what that press prints (notes/ostwald.py, print-gamut.json), so every
one is printable: the estimate, printed, should come back as the cell's colour.

Re-run it after changing colors.json (Wada's Orange fixes the hue's zero point), the Ostwald
computation (notes/ostwald.py, which it imports) or print-gamut.json. It also prints how well the
estimate does on Wada's own colours, whose CMYK we know.
Standard library only.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "notes"))
import cmyk_to_oklch as cx  # noqa: E402  the profile's tables and the Lab <-> OKLab maths
import ostwald  # noqa: E402  the Ostwald system: its greys, letters and calibration

OUT = ROOT / "ostwald-cmyk.json"


# --- OKLab / XYZ (D65) -> Lab (D50), the inverse of cmyk_to_oklch.py's maths --------------------

def inverse(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]


OKLAB_TO_LMS, LMS_TO_XYZ, D65_TO_D50 = inverse(cx.LMS_TO_OKLAB), inverse(cx.XYZ_TO_LMS), inverse(cx.D50_TO_D65)


def xyz_to_lab(xyz):
    X, Y, Z = (v / w for v, w in zip(cx.mul(D65_TO_D50, xyz), cx.D50))
    f = lambda t: t ** (1 / 3) if t > cx.EPSILON else (cx.KAPPA * t + 16) / 116  # noqa: E731
    return [116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))]


def oklab_to_lab(oklab):
    return xyz_to_lab(cx.mul(LMS_TO_XYZ, [v ** 3 for v in cx.mul(OKLAB_TO_LMS, oklab)]))


def oklch_to_lab(L, C, h):
    return oklab_to_lab([L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))])


def delta_e_2000(lab1, lab2):
    (L1, a1, b1), (L2, a2, b2) = lab1, lab2
    Cm = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    G = 0.5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1, a2 = a1 * (1 + G), a2 * (1 + G)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    h1 = math.degrees(math.atan2(b1, a1)) % 360 if C1 else 0.0
    h2 = math.degrees(math.atan2(b2, a2)) % 360 if C2 else 0.0
    dh = 0.0 if C1 * C2 == 0 else (h2 - h1 + 180) % 360 - 180
    dH = 2 * math.sqrt(C1 * C2) * math.sin(math.radians(dh / 2))
    Lm, Cm = (L1 + L2) / 2, (C1 + C2) / 2
    hm = h1 + h2 if C1 * C2 == 0 else ((h1 + h2) / 2 if abs(h1 - h2) <= 180 else (h1 + h2 + 360) / 2 % 360)
    T = (1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm))
         + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63)))
    SL = 1 + 0.015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2)
    SC, SH = 1 + 0.045 * Cm, 1 + 0.015 * Cm * T
    RT = -2 * math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hm - 275) / 25) ** 2)))
    return math.sqrt(((L2 - L1) / SL) ** 2 + ((C2 - C1) / SC) ** 2 + (dH / SH) ** 2 + RT * ((C2 - C1) / SC) * (dH / SH))


# --- The cells, as index.html's ostwaldSystem computes them --------------------------------------

def cells():
    """(code, XYZ) of every cell: its own colour, as notes/ostwald.py's cell_xyz makes it (white GREYS[a],
    black 1 - GREYS[b], at the sector's chromaticity angle, measured against the press)."""
    G, letters = ostwald.GREYS, ostwald.LETTERS.upper()
    for a in range(len(G)):
        for b in range(a + 1):
            if a == b:
                yield letters[a], ostwald.cell_xyz(None, a, b)
                continue
            for sector in range(24):
                number = int(sector * 100 / 24 + 0.5) % 100  # rounding half up, as Math.round
                yield f"{number}{letters[a]}{letters[b]}", ostwald.cell_xyz(sector, a, b)


def main():
    a2b, b2a = cx.load_a2b1(cx.PROFILE), cx.load_b2a1()

    # How well the estimate does where the answer is known: Wada's colours, from their OKLCH.
    colors = json.loads(cx.COLORS.read_text())
    worst, close5, close10, far, trips = [], 0, 0, 0, []
    for c in colors:
        lab = oklch_to_lab(*c["oklch"])
        est = [round(v) for v in cx.lab_to_cmyk(b2a, lab)]
        d = max(abs(e - k) for e, k in zip(est, c["cmyk"]))
        close5, close10, far = close5 + (d <= 5), close10 + (d <= 10), far + (d > 20)
        worst.append((d, c["name"], c["cmyk"], est))
        trips.append(delta_e_2000(lab, cx.cmyk_to_lab(a2b, est)))
    trips.sort()
    print(f"Wada's {len(colors)} colours, estimated from their OKLCH:")
    print(f"  every ink within 5 points of the book's: {close5}; within 10: {close10}; some ink over 20 off: {far}")
    print("  furthest: " + "; ".join(f"{n} book {k} estimate {e}" for _, n, k, e in sorted(worst)[-3:]))
    print(f"  the estimate printed (A2B1) against the colour, ΔE2000: median {trips[len(trips) // 2]:.2f}, largest {trips[-1]:.2f}")

    # The cells.
    out, trips, outside = {}, [], []
    for code, xyz in cells():
        lab = xyz_to_lab(xyz)
        est = [round(v) for v in cx.lab_to_cmyk(b2a, lab)]
        out[code] = est
        trips.append(delta_e_2000(lab, cx.cmyk_to_lab(a2b, est)))
        if trips[-1] > 3:
            outside.append(code)
    trips.sort()
    print(f"\nCells: {len(out)}; the estimate printed against the cell's colour, ΔE2000: median {trips[len(trips) // 2]:.2f}, largest {trips[-1]:.2f}")
    print(f"  more than 3 off: {len(outside)}" + (f", e.g. {', '.join(outside[::max(1, len(outside) // 8)][:8])}" if outside else ""))

    # The calibration it was made for (the page ignores the file if its own differs), then code -> CMYK.
    lines = ",\n".join(f'"{code}":{json.dumps(v, separators=(",", ":"))}' for code, v in out.items())
    OUT.write_text(f'{{"offset":{ostwald.OFFSET:.6f},"cmyk":{{\n{lines}\n}}}}\n')
    print(f"\nwrote {len(out)} estimates to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
