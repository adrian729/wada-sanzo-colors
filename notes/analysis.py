"""Compare the book's combinations with random regroupings of the same colours.

Prints every number quoted in notes/data-analysis.md. Run from anywhere:

    python3 notes/analysis.py

Standard library only; the seed is fixed, so the output is the same on every run.
"""
import json
import math
import random
import statistics as st
from itertools import combinations as pairs
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
colors = json.loads((ROOT / "colors.json").read_text())
combos = json.loads((ROOT / "combinations.json").read_text())
seasons = json.loads((ROOT / "seasons.json").read_text())
cards = json.loads((ROOT / "vol2/extracted.json").read_text())
RUNS = 1000
rng = random.Random(1)

# Colour measures, from OKLCH.
L = lambda i: colors[i]["oklch"][0]
C = lambda i: colors[i]["oklch"][1]
H = lambda i: colors[i]["oklch"][2]


def lab(i):
    l, c, h = colors[i]["oklch"]
    return l, c * math.cos(math.radians(h)), c * math.sin(math.radians(h))


def dE(a, b):
    return math.dist(lab(a), lab(b))


def hdiff(a, b):
    d = abs(H(a) - H(b)) % 360
    return min(d, 360 - d)


NEUTRAL = 0.04  # below this chroma a colour has no meaningful hue


def temp(i):
    if C(i) < NEUTRAL:
        return "neutral"
    h = H(i)
    if h < 115 or h >= 340:
        return "warm"
    if 150 <= h < 300:
        return "cool"
    return "between"


muted = lambda i: C(i) < 0.06
vivid = lambda i: C(i) >= 0.12
pale = lambda i: L(i) >= 0.80 and C(i) < 0.10
deep = lambda i: C(i) >= 0.10 and L(i) < 0.75
dark = lambda i: L(i) < 0.50
light = lambda i: L(i) >= 0.70


def chromatic(cb):
    return [i for i in cb if C(i) >= NEUTRAL]


def tier(i):
    return "dark" if L(i) < 0.55 else "light" if L(i) > 0.75 else "mid"


# Each measure maps a combination to a number or a yes/no; a group's value is the mean.
MEASURES = {
    "Closest pair, ΔE": lambda cb: min(dE(a, b) for a, b in pairs(cb, 2)),
    "Two colours with ΔE < 0.08": lambda cb: min(dE(a, b) for a, b in pairs(cb, 2)) < 0.08,
    "Lightness range, ΔL": lambda cb: max(map(L, cb)) - min(map(L, cb)),
    "Two colours within 0.05 in lightness": lambda cb: min(abs(L(a) - L(b)) for a, b in pairs(cb, 2)) < 0.05,
    "All chromatic hues within 40°": lambda cb: len(chromatic(cb)) >= 2 and max(hdiff(a, b) for a, b in pairs(chromatic(cb), 2)) <= 40,
    "Two hues at least 150° apart": lambda cb: any(hdiff(a, b) >= 150 for a, b in pairs(chromatic(cb), 2)),
    "Both warm and cool": lambda cb: {"warm", "cool"} <= {temp(i) for i in cb},
    "A muted and a vivid colour": lambda cb: any(map(muted, cb)) and any(map(vivid, cb)),
    "A dark, a mid and a light colour": lambda cb: {tier(i) for i in cb} == {"dark", "mid", "light"},
}

# Wada's "seasoning" advice (1935, p. 29), as condition -> what it asks for.
RULES = {
    "Two or more vivid: a muted one among them": (lambda cb: sum(map(vivid, cb)) >= 2, lambda cb: any(map(muted, cb))),
    "Two or more pale: a deep one among them": (lambda cb: sum(map(pale, cb)) >= 2, lambda cb: any(map(deep, cb))),
    "Two or more dark: a light one among them": (lambda cb: sum(map(dark, cb)) >= 2, lambda cb: any(map(light, cb))),
}

# His complementary pairs (1935, p. 22). Violet Ultramarine is only in Vol 2.
COMPLEMENTS = [
    ("Spectrum Red", "Sea Green"), ("Red Orange", "Green Blue"), ("Orange", "Peacock Blue"),
    ("Yellow Orange", "Antwerp Blue"), ("Apricot Yellow", "Blue"), ("Yellow", "Deep Lyons Blue"),
    ("Lemon Yellow", "Violet Ultramarine"), ("Light Green Yellow", "Violet"),
    ("Yellow Green", "Red Violet"), ("Night Green", "Rosolane Purple"),
]


def shuffled(group):
    """The same colours, each used as often as in the book, regrouped at random (no colour twice in one combination)."""
    pool = [i for cb in group for i in cb]
    n = len(group[0])
    while True:
        rng.shuffle(pool)
        out = [pool[k:k + n] for k in range(0, len(pool), n)]
        if all(len(set(cb)) == n for cb in out):
            return out


def p_two_sided(book, random_values):
    m = st.mean(random_values)
    hits = sum(1 for x in random_values if abs(x - m) >= abs(book - m))
    return (hits + 1) / (len(random_values) + 1)


def fmt(x, share):
    return f"{x:.0%}" if share else f"{x:.2f}"


by_size = {n: [cb for cb in combos if len(cb) == n] for n in (2, 3, 4)}
regroupings = {n: [shuffled(g) for _ in range(RUNS)] for n, g in by_size.items()}
tests = 0

print(f"Book vs {RUNS} random regroupings (book / random mean, two-sided p)\n")
for name, f in MEASURES.items():
    print(name)
    for n, g in by_size.items():
        if name == "A dark, a mid and a light colour" and n == 2:
            continue
        book = st.mean(map(f, g))
        rand = [st.mean(map(f, r)) for r in regroupings[n]]
        share = isinstance(f(g[0]), bool)
        extra = f"  ({sum(map(f, g))} of {len(g)} vs {st.mean(rand) * len(g):.1f})" if share else ""
        print(f"  {n} colours: {fmt(book, share)} / {fmt(st.mean(rand), share)}, p≈{p_two_sided(book, rand):.3f}{extra}")
        tests += 1

print("\nWada's seasoning rules, on combinations that meet the condition (book / random)")
for name, (cond, ok) in RULES.items():
    print(name)
    for n in (3, 4):
        def rate(group):
            sub = [cb for cb in group if cond(cb)]
            return sum(map(ok, sub)) / len(sub) if sub else None, len(sub)
        book, count = rate(by_size[n])
        rand = [x for x in (rate(r)[0] for r in regroupings[n]) if x is not None]
        print(f"  {n} colours: {book:.0%} / {st.mean(rand):.0%} (n={count}), p≈{p_two_sided(book, rand):.2f}")
        tests += 1

index = {c["name"]: i for i, c in enumerate(colors)}
comp = [(index[a], index[b]) for a, b in COMPLEMENTS]


def comp_count(groups):
    return sum(1 for g in groups for cb in g for a, b in comp if a in cb and b in cb)


book = comp_count(by_size.values())
rand = [comp_count(regroupings[n][k] for n in by_size) for k in range(RUNS)]
print(f"\nWada's complementary pairs found together: book {book}, random mean {st.mean(rand):.1f}, p≈{p_two_sided(book, rand):.2f}")
tests += 1

print("\nCrosses (top, left, right, bottom): opposite pairs (top-bottom, left-right) minus neighbouring pairs")
cross = by_size[4]


def axis_diff(group, f):
    opposite = st.mean(f(a, b) for t, l, r, b_ in group for a, b in ((t, b_), (l, r)))
    neighbour = st.mean(f(a, b) for t, l, r, b_ in group for a, b in ((t, l), (t, r), (b_, l), (b_, r)))
    return opposite - neighbour


for name, f in [("ΔE", dE), ("ΔL", lambda a, b: abs(L(a) - L(b)))]:
    book = axis_diff(cross, f)
    rand = [axis_diff([rng.sample(cb, 4) for cb in cross], f) for _ in range(RUNS)]
    print(f"  {name}: {book:+.3f}, random positions {st.mean(rand):+.3f}, p≈{p_two_sided(book, rand):.2f}")
    tests += 1

print("\nPosition of the lightest, darkest and most chromatic colour (counts per position)")
for n, names in [(2, "left, right"), (3, "left, middle, right"), (4, "top, left, right, bottom")]:
    counts = {"lightest": [0] * n, "darkest": [0] * n, "most chromatic": [0] * n}
    for cb in by_size[n]:
        ls, cs = [L(i) for i in cb], [C(i) for i in cb]
        counts["lightest"][ls.index(max(ls))] += 1
        counts["darkest"][ls.index(min(ls))] += 1
        counts["most chromatic"][cs.index(max(cs))] += 1
    print(f"  {n} colours ({names}): " + "; ".join(f"{k} {v}" for k, v in counts.items()))
    tests += 3 * n
k = sum(1 for cb in by_size[3] if L(cb[2]) == max(map(L, cb)))
p = sum(math.comb(120, j) * (1 / 3) ** j * (2 / 3) ** (120 - j) for j in range(k, 121))
print(f"  Lightest on the right in triads: {k} of 120, chance 40, one-sided binomial p≈{p:.3f}")

print("\nVol 2 cards")
shares, largest = [], 0
for card in cards:
    widths = [c["band"][1] - c["band"][0] for c in card["colors"]]
    shares.append(widths[0] / sum(widths))
    largest += widths[0] == max(widths)
print(f"  Top band's share of the strip: median {st.median(shares):.0%}, from {min(shares):.0%} to {max(shares):.0%}")
print(f"  Top band is the largest on {largest} of {len(cards)} cards")
chance = sum(1 / len(s) for s in seasons)
for name, f in [("chroma", C), ("lightness", L)]:
    low = sum(1 for s in seasons if f(s[0]) == min(map(f, s)))
    high = sum(1 for s in seasons if f(s[0]) == max(map(f, s)))
    print(f"  Top colour has the lowest {name} on {low} cards and the highest on {high} (chance {chance:.1f} each)")
    tests += 2

print(f"\nTests run: {tests}")
