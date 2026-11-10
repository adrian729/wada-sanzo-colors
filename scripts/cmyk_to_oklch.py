#!/usr/bin/env python3
"""Compute each colour's OKLCH from its CMYK and store it in colors.json.

    python3 scripts/cmyk_to_oklch.py

Sets the `oklch` field of every colour to [L, C, h], usable in CSS as oklch(L C h).
Re-run it after changing any CMYK value.

Pipeline (standard library only):

1. CMYK -> CIE Lab (D50), via the ICC profile of the printing condition.
   CMYK is device-dependent: it only describes a colour together with the press, paper and inks
   it was printed with. An ICC output profile encodes that relationship as a measured lookup
   table, so this step is a table interpolation, not a formula. We use Japan Color 2011 Coated
   (the Japanese offset standard, ISO 12647-2) and its colorimetric table A2B1, which is the
   media-relative colorimetric intent: the paper white maps to white, nothing else is altered.
   No black point compensation: that is a rendering decision for a specific output device and
   belongs at display time, not in the data.

2. Lab (D50) -> XYZ (D50) -> XYZ (D65) -> OKLab -> OKLCH.
   Exact maths, using the constants and matrices from CSS Color 4
   (https://www.w3.org/TR/css-color-4/#color-conversion-code), so the result matches what a
   browser computes for the same colour given as lab().

No RGB step: sRGB would clip the print colours outside its gamut and quantise to 8 bits.
"""
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "profiles" / "JapanColor2011Coated.icc"
COLORS = ROOT / "colors.json"


# --- 1. CMYK -> Lab (D50) through the ICC profile's A2B1 lookup table ------------------------

class Lut:
    """An ICC v2 lut8Type ('mft1') or lut16Type ('mft2') tag."""

    def __init__(self, data):
        kind = data[:4]
        if kind not in (b"mft1", b"mft2"):
            raise ValueError(f"unsupported LUT type {kind!r} (only ICC v2 mft1/mft2)")
        self.n_in, self.n_out, self.grid = data[8], data[9], data[10]
        self.is16 = kind == b"mft2"
        if self.is16:
            in_entries, out_entries = struct.unpack(">HH", data[48:52])
            fmt, scale, pos = "H", 65535.0, 52
        else:
            in_entries = out_entries = 256
            fmt, scale, pos = "B", 255.0, 48

        def read(count):
            nonlocal pos
            size = struct.calcsize(fmt)
            values = struct.unpack(f">{count}{fmt}", data[pos:pos + count * size])
            pos += count * size
            return [v / scale for v in values]

        self.in_curves = [read(in_entries) for _ in range(self.n_in)]
        self.clut = read(self.grid ** self.n_in * self.n_out)
        self.out_curves = [read(out_entries) for _ in range(self.n_out)]

    @staticmethod
    def curve(table, x):
        """Piecewise-linear 1D table lookup, x in [0, 1]."""
        p = min(max(x, 0.0), 1.0) * (len(table) - 1)
        i = min(int(p), len(table) - 2)
        return table[i] + (table[i + 1] - table[i]) * (p - i)

    def node(self, idx):
        """CLUT output vector at integer grid coordinates (first input varies slowest)."""
        flat = 0
        for i in idx:
            flat = flat * self.grid + i
        return self.clut[flat * self.n_out:(flat + 1) * self.n_out]

    def eval4(self, x):
        """4-input CLUT interpolation as LittleCMS does it: linear along the first input,
        tetrahedral over the other three."""
        g = self.grid - 1
        lo, frac = [], []
        for v in x:
            p = min(max(v, 0.0), 1.0) * g
            i = min(int(p), g - 1)
            lo.append(i)
            frac.append(p - i)

        def tetra(first):
            # Walk from the cube's low corner towards the high corner, one axis at a time,
            # in order of decreasing fractional position (Kasson et al. 1995).
            axes = sorted(range(1, 4), key=lambda a: -frac[a])
            corner = [first] + lo[1:]
            out = [w * (1 - frac[axes[0]]) for w in self.node(corner)]
            for k, a in enumerate(axes):
                corner[a] += 1
                weight = frac[a] - (frac[axes[k + 1]] if k < 2 else 0.0)
                out = [o + w * weight for o, w in zip(out, self.node(corner))]
            return out

        a, b = tetra(lo[0]), tetra(lo[0] + 1)
        return [va + (vb - va) * frac[0] for va, vb in zip(a, b)]

    def __call__(self, device):
        x = [self.curve(t, v) for t, v in zip(self.in_curves, device)]
        y = self.eval4(x)
        return [self.curve(t, v) for t, v in zip(self.out_curves, y)]


def load_a2b1(path):
    data = Path(path).read_bytes()
    if data[16:20] != b"CMYK" or data[20:24] != b"Lab ":
        raise ValueError("expected a CMYK output profile with a Lab connection space")
    (count,) = struct.unpack(">I", data[128:132])
    for i in range(count):
        sig, offset, size = struct.unpack(">4sII", data[132 + 12 * i:144 + 12 * i])
        if sig == b"A2B1":
            return Lut(data[offset:offset + size])
    raise ValueError("profile has no A2B1 (colorimetric) table")


def cmyk_to_lab(lut, cmyk):
    """CMYK in percent -> media-relative CIE Lab (D50)."""
    v = lut([c / 100.0 for c in cmyk])
    if lut.is16:  # ICC v2 legacy 16-bit Lab: L 0..100 <-> 0x0000..0xFF00, a/b 0 <-> 0x8000
        return [v[0] * 65535 / 652.80, v[1] * 65535 / 256 - 128, v[2] * 65535 / 256 - 128]
    return [v[0] * 100, v[1] * 255 - 128, v[2] * 255 - 128]  # 8-bit Lab encoding


# --- 2. Lab (D50) -> OKLCH, per CSS Color 4 --------------------------------------------------

D50 = [0.3457 / 0.3585, 1.0, (1.0 - 0.3457 - 0.3585) / 0.3585]
KAPPA, EPSILON = 24389 / 27, 216 / 24389

D50_TO_D65 = [  # Bradford chromatic adaptation
    [0.955473421488075, -0.02309845494876471, 0.06325924320057072],
    [-0.0283697093338637, 1.0099953980813041, 0.021041441191917323],
    [0.012314014864481998, -0.020507649298898964, 1.330365926242124],
]
XYZ_TO_LMS = [
    [0.8190224379967030, 0.3619062600528904, -0.1288737815209879],
    [0.0329836539323885, 0.9292868615863434, 0.0361446663506424],
    [0.0481771893596242, 0.2642395317527308, 0.6335478284694309],
]
LMS_TO_OKLAB = [
    [0.2104542683093140, 0.7936177747023054, -0.0040720430116193],
    [1.9779985324311684, -2.4285922420485799, 0.4505937096174110],
    [0.0259040424655478, 0.7827717124575296, -0.8086757660377118],
]


def mul(m, v):
    return [sum(a * b for a, b in zip(row, v)) for row in m]


def lab_to_xyz_d50(L, a, b):
    f1 = (L + 16) / 116
    f0, f2 = a / 500 + f1, f1 - b / 200
    xyz = [
        f0 ** 3 if f0 ** 3 > EPSILON else (116 * f0 - 16) / KAPPA,
        ((L + 16) / 116) ** 3 if L > KAPPA * EPSILON else L / KAPPA,
        f2 ** 3 if f2 ** 3 > EPSILON else (116 * f2 - 16) / KAPPA,
    ]
    return [x * w for x, w in zip(xyz, D50)]


def lab_to_oklch(lab):
    lms = mul(XYZ_TO_LMS, mul(D50_TO_D65, lab_to_xyz_d50(*lab)))
    L, a, b = mul(LMS_TO_OKLAB, [math.copysign(abs(c) ** (1 / 3), c) for c in lms])
    C = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360 if C > 1e-4 else 0.0  # hue is meaningless for neutrals
    return [round(L, 4), round(C, 4), round(h, 2)]


# --- Lab (D50) -> CMYK through the profile's B2A1 table, the inverse of A2B1 (for ostwald_cmyk.py) --

class Lut3(Lut):
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
    data = PROFILE.read_bytes()
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


def load_b2a1():
    return Lut3(load_tag(b"B2A1"))


def main():
    lut = load_a2b1(PROFILE)
    colors = json.loads(COLORS.read_text())
    for c in colors:
        c["oklch"] = lab_to_oklch(cmyk_to_lab(lut, c["cmyk"]))
    COLORS.write_text(json.dumps(colors, indent=2, ensure_ascii=False) + "\n")
    print(f"updated oklch for {len(colors)} colours in {COLORS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
