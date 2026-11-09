# Wada Sanzo: A Dictionary of Color Combinations

A static site for browsing Sanzo Wada's *A Dictionary of Color Combinations*: its 159 colours in the book's six families, its 348 combinations of 2, 3 and 4 colours, the 72 seasonal combinations of Volume 2 (with its 11 extra colours), a colour wheel, and a page to compose your own combinations.

Live: https://adrian729.github.io/wada-sanzo-colors/

## Run locally

It's a single `index.html` that loads the JSON files, so it has to be served over HTTP:

```sh
python3 -m http.server
```

Then open http://localhost:8000.

## Data

- `colors.json`: the 170 colours (159 from Volume 1, and 11 only in Volume 2, marked `"volume": 2`), each with its name as printed in the book, its CMYK as given in the book, and OKLCH.
- `combinations.json`: Volume 1's 348 combinations, as indices into `colors.json`, the colours in the book's order (a row left to right; a cross top, left, right, bottom).
- `seasons.json`: Volume 2's 72 seasonal combinations (six a month, January first), the colours top to bottom.
- `families.json`: the book's six colour families, in the order of its colour index.
- `ostwald-cmyk.json`: CMYK estimated for every cell of the Colors › Ostwald view, by its Ostwald code, for the cells none of Wada's colours fill (`scripts/ostwald_cmyk.py`).

OKLCH is computed from CMYK through the Japan Color 2011 Coated profile (`scripts/cmyk_to_oklch.py`). The Ostwald view's estimated CMYK goes the other way, through the same profile (`scripts/ostwald_cmyk.py`); re-run it after changing `colors.json` or the Ostwald computation (`notes/ostwald.py`).

## Sources

- Volume 1: the dataset from [mattdesl/dictionary-of-colour-combinations](https://github.com/mattdesl/dictionary-of-colour-combinations) (MIT, see `DATA-LICENSE.txt`), itself based on [dblodorn/sanzo-wada](https://github.com/dblodorn/sanzo-wada), checked against the book: names corrected to the printed spelling and a few CMYK values fixed.
- Volume 2: its seasonal combinations reprint Wada's 配色総鑑 B篇 (1934–35), which the National Diet Library has scanned and marked public domain. They were read from those scans and checked against the printed book; see `vol2/README.md`.
- The Japan Color 2011 Coated ICC profile, from the ICC Profile Registry, shared unaltered under its licence (`profiles/`).
- The DM Mono font, under the SIL Open Font License (`fonts/OFL.txt`).
