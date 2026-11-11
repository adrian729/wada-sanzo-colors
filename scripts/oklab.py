"""OKLCH <-> CIE XYZ (D65), for every script here and notes/ostwald.py: one copy of the maths, so that they agree
with each other and with the page (index.html's xyzOf and oklchOfXYZ, the same numbers).

CSS Color 4's matrices (https://www.w3.org/TR/css-color-4/#color-conversion-code), XYZ to OKLab and, inverted,
back; its white, D65 with Y = 1. Nothing is clipped. Standard library only.
"""
import math

XYZ_TO_LMS = [[0.8190224379967030, 0.3619062600528904, -0.1288737815209879],
              [0.0329836539323885, 0.9292868615863434, 0.0361446663506424],
              [0.0481771893596242, 0.2642395317527308, 0.6335478284694309]]
LMS_TO_OKLAB = [[0.2104542683093140, 0.7936177747023054, -0.0040720430116193],
                [1.9779985324311684, -2.4285922420485799, 0.4505937096174110],
                [0.0259040424655478, 0.7827717124575296, -0.8086757660377118]]
OKLAB_TO_LMS = [[1.00000000239858, 0.39633777716154006, 0.21580375421218242],
                [0.999999999290284, -0.1055613457521502, -0.06385417190922567],
                [0.9999999856456103, -0.08948417624532107, -1.2914855294809227]]
LMS_TO_XYZ = [[1.226879875845924, -0.557814994460217, 0.2813910456659646],
              [-0.040575745214800875, 1.1122868032803173, -0.07171105806551642],
              [-0.07637293667466001, -0.4214933324022431, 1.5869240198367816]]
WHITE = [0.9504559270516716, 1.0, 1.0890577507598784]  # D65 (x 0.3127, y 0.3290), CSS's


def mul(m, v):
    return [sum(a * b for a, b in zip(row, v)) for row in m]


def xyz_of(L, C, h):
    """OKLCH -> XYZ (D65)."""
    lms = mul(OKLAB_TO_LMS, [L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))])
    return mul(LMS_TO_XYZ, [v ** 3 for v in lms])


def oklab_of(xyz):
    return mul(LMS_TO_OKLAB, [math.copysign(abs(v) ** (1 / 3), v) for v in mul(XYZ_TO_LMS, xyz)])


def oklch_of(xyz):
    """XYZ (D65) -> OKLCH, rounded as colors.json is (and as the page's oklchOfXYZ)."""
    L, a, b = oklab_of(xyz)
    C = round(math.hypot(a, b), 4)
    h = round(math.degrees(math.atan2(b, a)) % 360, 2)
    return [round(L, 4), C, 0 if C == 0 or h == 360 else h]
