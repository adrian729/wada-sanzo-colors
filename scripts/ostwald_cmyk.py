#!/usr/bin/env python3
"""Estimate CMYK for every cell of the Ostwald view and store it in ostwald-cmyk.json.

    python3 scripts/ostwald_cmyk.py

The view's empty cells show the Ostwald system's own colour (see notes/ostwald.md), which has no
CMYK of its own. This estimates one the way a printer would: colour -> CIE Lab (D50) -> CMYK through
the same Japan Color 2011 Coated profile that turns the book's CMYK into OKLCH (cmyk_to_oklch.py),
using its colorimetric table B2A1, the inverse of the A2B1 table used there. The profile's table also
fixes how much black replaces cyan, magenta and yellow.

Re-run it after changing colors.json (Wada's Orange fixes the hue's zero point) or the Ostwald
computation (notes/ostwald.py, which it imports). It also prints how well the estimate does on
Wada's own colours, whose CMYK we know.
Standard library only.
"""
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "notes"))
import cmyk_to_oklch as cx  # noqa: E402  the profile's tables and the Lab <-> OKLab maths
import ostwald  # noqa: E402  the Ostwald system: its greys, letters and calibration

OUT = ROOT / "ostwald-cmyk.json"


# --- Lab (D50) -> CMYK through the profile's B2A1 table -----------------------------------------

class Lut3(cx.Lut):
    """A 3-input table (Lab in), interpolated trilinearly, as LittleCMS does for Lab input."""

    def __call__(self, device):  # here the encoded Lab
        x = [self.curve(t, v) for t, v in zip(self.in_curves, device)]
        g = self.grid - 1
        lo, frac = [], []
        for v in x:
            p = min(max(v, 0.0), 1.0) * g
            i = min(int(p), g - 1)
            lo.append(i)
            frac.append(p - i)
        y = [0.0] * self.n_out
        for corner in range(8):
            d = [(corner >> k) & 1 for k in range(3)]
            w = math.prod(f if dk else 1 - f for f, dk in zip(frac, d))
            if w:
                y = [o + w * n for o, n in zip(y, self.node([i + dk for i, dk in zip(lo, d)]))]
        return [self.curve(t, v) for t, v in zip(self.out_curves, y)]


def load_tag(sig):
    data = cx.PROFILE.read_bytes()
    (count,) = struct.unpack(">I", data[128:132])
    for i in range(count):
        s, offset, size = struct.unpack(">4sII", data[132 + 12 * i:144 + 12 * i])
        if s == sig:
            return data[offset:offset + size]
    raise ValueError(f"profile has no {sig.decode()} table")


def lab_to_cmyk(lut, lab):
    """Media-relative CIE Lab (D50) -> CMYK in percent."""
    L, a, b = lab
    if not lut.is16:
        raise ValueError("expected a 16-bit B2A1 table")
    # ICC v2 legacy 16-bit Lab: L 0..100 <-> 0x0000..0xFF00, a/b 0 <-> 0x8000
    return [100 * v for v in lut([L * 652.80 / 65535, (a + 128) * 256 / 65535, (b + 128) * 256 / 65535])]


# --- OKLab / linear sRGB -> Lab (D50), the inverse of cmyk_to_oklch.py's maths ------------------

def inverse(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]


OKLAB_TO_LMS, LMS_TO_XYZ, D65_TO_D50 = inverse(cx.LMS_TO_OKLAB), inverse(cx.XYZ_TO_LMS), inverse(cx.D50_TO_D65)


def oklab_to_lab(oklab):
    lms = [v ** 3 for v in cx.mul(OKLAB_TO_LMS, oklab)]
    X, Y, Z = (v / w for v, w in zip(cx.mul(D65_TO_D50, cx.mul(LMS_TO_XYZ, lms)), cx.D50))
    f = lambda t: t ** (1 / 3) if t > cx.EPSILON else (cx.KAPPA * t + 16) / 116  # noqa: E731
    return [116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))]


def oklch_to_lab(L, C, h):
    return oklab_to_lab([L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))])


def linear_srgb_to_lab(rgb):
    r, g, b = rgb
    lms = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
           0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
           0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in lms)
    return oklab_to_lab([0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                         1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                         0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s])


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
    """(code, linear sRGB) of every cell: white GREYS[a] plus colour (GREYS[b] - GREYS[a]) times the
    full colour of the sector's hue."""
    G, letters = ostwald.GREYS, ostwald.LETTERS.upper()
    for a in range(len(G)):
        for b in range(a + 1):
            if a == b:
                yield letters[a], [G[a]] * 3
                continue
            for sector in range(24):
                full = ostwald.SECTOR_COLOURS[sector]
                number = int(sector * 100 / 24 + 0.5) % 100  # rounding half up, as Math.round
                yield f"{number}{letters[a]}{letters[b]}", [G[a] + (G[b] - G[a]) * v for v in full]


def main():
    a2b, b2a = cx.load_a2b1(cx.PROFILE), Lut3(load_tag(b"B2A1"))

    # How well the estimate does where the answer is known: Wada's colours, from their OKLCH.
    colors = json.loads(cx.COLORS.read_text())
    worst, close5, close10, far, trips = [], 0, 0, 0, []
    for c in colors:
        lab = oklch_to_lab(*c["oklch"])
        est = [round(v) for v in lab_to_cmyk(b2a, lab)]
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
    for code, rgb in cells():
        lab = linear_srgb_to_lab(rgb)
        est = [round(v) for v in lab_to_cmyk(b2a, lab)]
        out[code] = est
        trips.append(delta_e_2000(lab, cx.cmyk_to_lab(a2b, est)))
        if trips[-1] > 3:
            outside.append(code)
    trips.sort()
    print(f"\nCells: {len(out)}; the estimate printed against the cell's colour, ΔE2000: median {trips[len(trips) // 2]:.2f}, largest {trips[-1]:.2f}")
    print(f"  more than 3 off (outside what the press can print): {len(outside)}, e.g. {', '.join(outside[::max(1, len(outside) // 8)][:8])}")

    # The calibration it was made for (the page ignores the file if its own differs), then code -> CMYK.
    lines = ",\n".join(f'"{code}":{json.dumps(v, separators=(",", ":"))}' for code, v in out.items())
    OUT.write_text(f'{{"offset":{ostwald.OFFSET:.6f},"cmyk":{{\n{lines}\n}}}}\n')
    print(f"\nwrote {len(out)} estimates to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
