# What the combinations show

Do the plates follow any simple pattern, or Wada's own rules? Run `python3 notes/analysis.py` to print every number here. It takes about 40 seconds, and its seed is fixed.

## Method

- **The comparison:** the book's 348 combinations against 1000 random regroupings of the same colours. Each regrouping keeps the combination sizes and uses each colour as often as the book does, without repeating a colour within a combination.
- **What it measures:** how Wada grouped his colours, not which colours he chose. The palette alone already carries much of his look.
- **Colour values:** OKLCH, converted from the book's CMYK (see the main README), not measured from the original paper.
- **Definitions** (the thresholds are mine, not Wada's):
  - ΔE is the OKLab distance and ΔL the lightness difference, both on a 0–1 scale;
  - a colour with chroma C < 0.04 is neutral, with no meaningful hue;
  - warm is a hue below 115° or from 340° up, and cool is 150–300°;
  - muted is C < 0.06, and vivid is C ≥ 0.12;
  - dark is L < 0.55, mid is 0.55–0.75, and light is above 0.75.
- **p:** two-sided; the share of random regroupings at least as far from the random mean as the book is.

## Results

Each cell is the book's value / the random mean, then p.

| | 2 colours | 3 colours | 4 colours |
|---|---|---|---|
| Closest pair, ΔE | 0.30 / 0.27, p≈0.007 | 0.17 / 0.15, p≈0.001 | 0.13 / 0.12, p≈0.001 |
| Two colours with ΔE < 0.08 | 0 / 5.6 of 120, p≈0.015 | 10 / 18.7 of 120, p≈0.03 | 13 / 25.5 of 108, p≈0.003 |
| Lightness range, ΔL | 0.24 / 0.22, p≈0.035 | 0.32 / 0.31, p≈0.12 | 0.39 / 0.38, p≈0.7 |
| Two colours within 0.05 in lightness | 8% / 14%, p≈0.08 | 32% / 40%, p≈0.09 | 59% / 64%, p≈0.36 |
| All chromatic hues within 40° | 13% / 21%, p≈0.04 | 12% / 12%, p≈0.9 | 4% / 6%, p≈0.3 |
| Two hues at least 150° apart | 14% / 13%, p≈0.65 | 38% / 30%, p≈0.03 | 42% / 41%, p≈0.8 |
| Both warm and cool | 33% / 28%, p≈0.18 | 60% / 52%, p≈0.03 | 68% / 61%, p≈0.04 |
| A muted and a vivid colour | 25% / 18%, p≈0.02 | 44% / 39%, p≈0.18 | 61% / 58%, p≈0.5 |
| A dark, a mid and a light colour | n/a | 26% / 22%, p≈0.37 | 44% / 45%, p≈0.84 |

- **Wada avoids near-duplicates.** This is the clearest signal:
  - in every size, the two closest colours are further apart than chance gives;
  - none of the 120 pairs has two colours closer than ΔE 0.08, where chance gives about 6;
  - in three and four colours, such near pairs are about half as common as chance.
- **A slight lean towards contrast:**
  - pairs have a little more lightness difference, and fewer same-hue pairs, than chance;
  - pairs combine a muted and a vivid colour more often;
  - triads more often hold two nearly opposite hues.
- **Warm with cool:** a little more often than chance in 3 and 4 colours, yet 32–40% of those combinations don't mix them at all.
- **No lightness ladder:**
  - a third of the triads and over half of the crosses have two colours of almost the same lightness;
  - a dark, a mid and a light colour together is no more common than chance.

## Wada's rules in the plates

**His seasoning advice (p. 29),** on the 3- and 4-colour combinations that meet each condition. The extra thresholds:

- pale is L ≥ 0.80 and C < 0.10;
- deep is C ≥ 0.10 and L < 0.75;
- dark is L < 0.50;
- light is L ≥ 0.70.

| Rule | 3 colours (book / random) | 4 colours (book / random) |
|---|---|---|
| Two or more vivid: is a muted one among them? | 42% / 34% (n=31, p≈0.24) | 55% / 56% (n=56, p≈0.89) |
| Two or more pale: is a deep one among them? | 46% / 39% (n=13, p≈0.62) | 76% / 64% (n=21, p≈0.29) |
| Two or more dark: is a light one among them? | 60% / 58% (n=10, p≈0.89) | 77% / 78% (n=22, p≈0.95) |

The book leans the right way on the first two rules, but within chance. The samples are small, and the rules are advice for using a combination: the plates show every colour at the same size.

**His complementary pairs (p. 22):**

- only one appears together in the book: Yellow with Deep Lyons Blue, in #22;
- random regroupings give 1.3 on average (p≈1);
- one pair can't appear at all, since Violet Ultramarine is only in Vol 2.

## Layout

- **Crosses:** Ōmi's essay reads the crosses as two relations, top–bottom and left–right. But the opposite pairs are no closer and no further apart than the neighbouring pairs, in ΔE (p≈0.75) or in lightness (p≈0.91).
- **Positions:** the script counts where the lightest, darkest and most chromatic colour sits, in 27 counts across the three sizes.
  - One stands out: the lightest colour is on the right in 54 of the 120 triads, where chance gives 40 (one-sided p≈0.005).
  - With 27 counts, one this far out is not unusual.

## Vol 2 cards

- **The top colour, Wada's "main colour":**
  - it takes a median 65% of the coloured strip, from 49% to 89%;
  - it is the largest band on all 72 cards.
- **It isn't chosen by chroma or lightness.** Chance would give each of these on 16.6 cards:
  - it has the lowest chroma on 16 cards, and the highest on 17;
  - it is the darkest on 13 cards, and the lightest on 16.
- **His own examples** show both kinds: a light main colour (card 1) and black (card 5).

## Caveats

- **Many tests:** the script runs 66, so at p < 0.05 about three would pass by luck. Only the near-duplicate results (p ≤ 0.007 in the closest-pair test, in every size) are clearly beyond that.
- **The baseline keeps Wada's palette and usage counts,** so this says nothing about how he chose his 159 colours.

## Overall

The plates differ from his own colours shuffled mainly in avoiding near-duplicates, with a slight pull towards contrast. The rest of what he says, about amount, area, the main colour and seasoning, is about how to use a combination. Plates of equal chips can't show it.
