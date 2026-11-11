# Wada Sanzo: A Dictionary of Color Combinations

A static site for browsing Sanzo Wada's *A Dictionary of Color Combinations*: its 159 colours in the book's six families, its 348 combinations of 2, 3 and 4 colours, the 72 seasonal combinations of Volume 2 (with its 12 extra colours), the colours laid out in Ostwald's colour solid (Wada's own notation), in OKLCH, in Munsell's solid and in PCCS's (with its tones), and a page to compose your own combinations and save them in your browser (they're listed first in Combinations, as yours).

Live: https://adrian729.github.io/wada-sanzo-colors/

## Run locally

It's a single `index.html` that loads the JSON files, so it has to be served over HTTP:

```sh
python3 -m http.server
```

Then open http://localhost:8000.

## Data

- `colors.json`: the 171 colours (159 from Volume 1, and 12 only in Volume 2, marked `"volume": 2`), each with its name as printed in the book, its CMYK as given in the book, and OKLCH.
  - 35 of them also have `atlas`: where Plate 8 of the 1935 colour atlas puts them (see Sources). It gives one of the plate's 12 hues (`hue`, translated), its tone there (`tone`: tint, full colour or shade), and the plate's Japanese name and its reading (`ja`, `reading`). The plate's 36th name, Coolie Blue (花色), isn't one of our colours. Its Grayish Lavender is our Grayish Lavender - A, the one whose hue fits. Where it gives a second spelling or a qualifier (鴾色 (鴇色), 萠木色 (裝束の)), only the first spelling is kept.
- `combinations.json`: Volume 1's 348 combinations, as indices into `colors.json`, the colours in the book's order (a row left to right; a cross top, left, right, bottom).
- `seasons.json`: Volume 2's 72 seasonal combinations (six a month, January first), the colours top to bottom.
- `families.json`: the book's six colour families, in the order of its colour index.
- `print-gamut.json`: what the press prints (Japan Color 2011 Coated, at most 350% ink): the most chroma at each OKLCH lightness and hue, for the Colors › OKLCH view's Print range, and the full colours and tint edge the Ostwald view measures Wada's colours against (`scripts/print_gamut.py`; see `notes/ostwald.md`).
- `ostwald-cmyk.json`: CMYK estimated for every cell of the Colors › Ostwald view, by its Ostwald code, for the cells none of Wada's colours fill (`scripts/ostwald_cmyk.py`).
- `munsell.json`: for the Colors › Munsell view, each colour's Munsell notation, and the system's own colours, the 1943 renotation's, in our space (`scripts/munsell.py`; see `notes/munsell.md`).
- `pccs.json`: for the Colors › PCCS view, each colour's PCCS notation and tone, and the system's own colours and tones, converted from Munsell's (`scripts/pccs.py`; see `notes/pccs.md`).

OKLCH is computed from CMYK through the Japan Color 2011 Coated profile (`scripts/cmyk_to_oklch.py`). The Ostwald view's estimated CMYK goes the other way, through the same profile (`scripts/ostwald_cmyk.py`); re-run it after changing `colors.json`, `print-gamut.json` or the Ostwald computation (`notes/ostwald.py`). The OKLCH view's, for any point of its slices or cell of its solid, is estimated the same way by the page itself, from the profile's table. `print-gamut.json` only changes with the profile or the ink limit; `scripts/print_gamut.py` takes a few minutes. Re-run `scripts/munsell.py` after changing `colors.json`; it needs colour-science and scipy, which uv fetches: `uv run -q --python 3.12 --with colour-science --with scipy python scripts/munsell.py` (about half a minute). Then re-run `scripts/pccs.py`, which reads `munsell.json`, the same way (about half a minute).

## Colour ranges

- **The OKLCH, Munsell and PCCS views** show one of two ranges (Create's colour picker has the same choice, kept apart; in the Munsell and PCCS views, the range is which of the system's own colours they show):
  - Screen (the default): Rec. 2020, the widest standard screen gamut, which holds all of Wada's colours and everything the press prints;
  - Print: what the press prints, as Wada's colours were printed. The press's darkest colour is at lightness 0.226, so the darker levels are empty.
- **Nothing is clipped before the screen.** The canvases and the 3D views draw in 16-bit floating point, which holds any colour, so each reaches the screen as CSS gives it, and a screen that shows fewer colours clips the rest itself. A browser without it gets Display P3, else sRGB, which clip what they don't hold.
- **Saved combinations** keep Wada's colours by their number in the book, and any other colour, an Ostwald, Munsell or PCCS cell's included, by its OKLCH values. An Ostwald cell's code is worked out again from them, so it follows the computation; a Munsell or PCCS cell's is found again by them. Combinations saved with the earlier Ostwald codes lose those colours.

## Sources

- Volume 1: the dataset from [mattdesl/dictionary-of-colour-combinations](https://github.com/mattdesl/dictionary-of-colour-combinations) (MIT, see `DATA-LICENSE.txt`), itself based on [dblodorn/sanzo-wada](https://github.com/dblodorn/sanzo-wada), checked against the book: names corrected to the printed spelling and a few CMYK values fixed.
- Volume 2: its seasonal combinations reprint Wada's 配色総鑑 B篇 (1934–35), which the National Diet Library has scanned and marked public domain. They were read from those scans and checked against the printed book; see `vol2/README.md`.
- Plate 8 ("Colour names and their hues") of 標準色彩圖集 (*Hyōjun shikisai zushū*, a standard colour atlas, 1935) by Hama Yaohiko and Wada Sanzō, read from the National Diet Library's scan. Its names are those of Wada's 色名總鑑 and 色名帖. It even shares the book's misprints, Rosolanc Purple and Antwarp Blue.
- The Munsell renotation data (Newhall, Nickerson and Judd, 1943), as colour-science has it (BSD licence), which also converts our colours to Munsell notation.
- PCCS's conversion from and to Munsell's notation, and its tones' representative colours and coordinates: Mituo Kobayasi and Kayoko Yosiki (小林光夫, 吉識香代子), "Mathematical Relation among PCCS Tones, PCCS Color Attributes and Munsell Color Attributes" (PCCSトーン, PCCS三属性値, およびマンセル三属性値間の数学的関係), *Journal of the Color Science Association of Japan* 25(4), 2001, pp. 249–261, from the National Diet Library's digital collections. PCCS is the Japan Color Research Institute's.
- The Japan Color 2011 Coated ICC profile, from the ICC Profile Registry, shared unaltered under its licence (`profiles/`).
- The DM Mono font, under the SIL Open Font License (`fonts/OFL.txt`).
