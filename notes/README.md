# How Wada Sanzo combined colours

Research notes on how Wada built the combinations in *A Dictionary of Color Combinations*, and on what he advised about using them. They draw on:

- his own texts;
- the original editions, scanned by the National Diet Library (NDL);
- our data.

The translations from the Japanese were made for these notes. Before quoting one in public, check it against the scan; page numbers are given.

## In short

- **Wada left guidelines, not formulas.** He wrote that combining colours "is not something to be taught in words, as we learn mathematics". Then he gave concrete advice anyway, in a 1935 supplement that the reprint leaves out. See [guidelines.md](guidelines.md).
- **His main rules:**
  - balance lightness and saturation, not just hue: a vivid set needs a muted colour, a pale set a measured amount of a deep one, and a dark set some lighter ones;
  - when every colour is equally strong, the result is safe but "ordinary";
  - start from one hue in its light and dark tones, and contrast different hues only with care;
  - equal areas need colours of equal strength, so give weak tones the large areas and strong tones the small ones;
  - the largest colour unifies the rest, but the focal point can be a small accent;
  - large areas look paler than the chips.
- **The original has 360 combinations.** The reprint follows the first edition (1933–34), which has 348. The card edition (1934–35) has 12 more four-colour plates. They are listed in [haishoku-sokan.md](haishoku-sokan.md), and every colour in them is in our palette.
- **The plates themselves show little pattern.** Compared with random regroupings of the same colours, they mainly avoid near-duplicate colours, and lean slightly towards contrast. His rules don't show beyond chance: they are advice for using a combination, and the plates show every colour at the same size. See [data-analysis.md](data-analysis.md).

## Files

- [guidelines.md](guidelines.md): Wada's own advice on making a combination and on using one.
- [haishoku-sokan.md](haishoku-sokan.md): the original work: Wada and why he made it, the editions, the 12 extra plates and the cards.
- [data-analysis.md](data-analysis.md): what the combinations show statistically.
- [analysis.py](analysis.py): the script behind data-analysis.md. Run `python3 notes/analysis.py`; it takes about 40 seconds.
- [ostwald.md](ostwald.md): Wada's colours placed in Ostwald's colour system as his 1935 supplement draws it, as in the site's Ostwald view, and how well that fits his own data.
- [ostwald.py](ostwald.py): the script behind ostwald.md. Run `python3 notes/ostwald.py`.

## Sources

- **Wada's 1935 supplement:** 『配色總鑑附說』 ("Supplement to the Haishoku Sōkan"). It was compiled by Wada and published by Hakubisha (博美社) on 20 November 1935, not for sale. NDL scan: https://dl.ndl.go.jp/pid/1903674.
  - Its chapters: introduction (p. 1); reading and handling colours (p. 4); notation (p. 8); the strength of colours (p. 14); colour harmony (p. 16); notes on using the Haishoku Sōkan (p. 32).
  - Page numbers in these notes are its own unless marked 1934.
- **Wada's 1934 booklet:** 『配色總鑑概説と其活用』 ("General remarks on the Haishoku Sōkan and how to use it"). Published by Hakubisha on 25 February 1934, not for sale. NDL scan: https://dl.ndl.go.jp/pid/1911912. The reprint includes an abridged version (pp. 16–23).
- **The reprint:** *A Dictionary of Color Combinations* Vol 1 (Seigensha, 2010; Japanese title 配色事典), read from the PDF. Its Japanese-only texts are:
  - the notes on the edition (凡例);
  - the foreword (はじめに);
  - the essay 「和田三造と『配色總鑑』」 by Ōmi Gentarō (近江源太郎) of the Japan Color Research Institute (pp. 7–15), cited as "essay";
  - the abridged 1934 booklet.
- **The original plates at the NDL:** listed in [haishoku-sokan.md](haishoku-sokan.md#editions). The B篇 cards are listed in `vol2/README.md`.
- **Our data:** `colors.json` (OKLCH), `combinations.json`, `seasons.json` and `vol2/extracted.json`.

## Ideas for the site

- **Add the 12 extra four-colour plates** as #349–#360, marked as missing from the reprint. Plate 116's Grayish Lavender needs checking: A or B.
- **A page on how Wada worked:**
  - the rules above;
  - the four kinds of harmony;
  - his reading of the two January cards.
- **In Create:**
  - suggest his complementary pairs;
  - an option to put white, grey or black between colours, with Chevreul's advice on which to use;
  - layouts that give strong colours less area;
  - a "large area" preview.
