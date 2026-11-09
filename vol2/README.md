# Volume 2: seasonal combinations (work in progress)

How Volume 2's 72 seasonal combinations were extracted and checked, and the scripts that feed them to the site: the site's `seasons.json` is built from `extracted.json` by `scripts/build_seasons.py`; the 12 colours not in Volume 1 were added to the site's `colors.json` (marked `"volume": 2`, CMYK from `book.json`) and placed in `families.json` where Volume 2's colour index puts them (Volume 2 has the same six families).

## Source

Volume 2's seasonal section reprints Sanzo Wada's 配色総鑑 B篇 (博美社, 1934–35): 12 monthly volumes, 6 cards each. The National Diet Library holds colour scans of all 12, marked public domain (PDM): https://dl.ndl.go.jp/pid/1903615 and the IDs below.

| Month | NDL ID |
|---|---|
| 1 | 1903615 |
| 2 | 1903616 |
| 3 | 1903619 |
| 4 | 1903620 |
| 5 | 1903621 |
| 6 | 1903623 |
| 7 | 1903626 |
| 8 | 1903627 |
| 9 | 1903629 |
| 10 | 1903632 |
| 11 | 1903634 |
| 12 | 1903635 |

Each volume has 15 pages: cover, colophon, then each card followed by its blank back, and a colour calibration chart last. Each card is a vertical strip: one large colour on top, then smaller bands, with the English name to the right of each band and the Japanese name (kana above kanji) to the left.

## Files

- `ndl-manifests/`: the IIIF manifests of the 12 volumes.
- `scans/thumbs/`: every page at 200 px wide, `m<month>_r<page>.jpg`.
- `scans/cards/`: the card pages at full resolution (about 2500 × 3500 px). Not in Git (100 MB): download them again with `python scripts/ndl_fetch.py scans/cards full 3,5,7,9,11,13,15 <the 12 IDs>`.
- `ocr/ocr_en.jsonl`: Apple Vision OCR output of the English names, with positions. Japanese names are not extracted: OCR can't read them reliably (the characters are widely spaced).
- `extracted.json`: per card: number (1–72), month, and its colours top to bottom, each with the printed name, the raw OCR text, the matched Volume 1 colour (`match`, an index into `colors.json`, or null for a new colour), the band's position and the colour sampled from the scan.
- `scripts/ndl_fetch.py`: downloads pages one at a time (NDL rate-limits bursts with HTTP 503).
- `scripts/ocr.swift`: OCR with Apple Vision (`swiftc -O ocr.swift -o ocr`).
- `scripts/extract_vol2.py`: reads the OCR, samples the bands and matches the names to Volume 1's colours.
- `scripts/build_seasons.py`: writes the site's `seasons.json` (`python scripts/build_seasons.py extracted.json ../colors.json ../seasons.json`).
- `scripts/review.py`: renders `review/sheet1–6.jpg`, each card's scan beside the extracted colours (red: corrected by hand, renamed, or an A/B pair; blue: new colour).
- `corrections.json`: OCR misreads fixed by reading the scans (`review/labels.jpg`), card names that are Volume 1 colours under another name (`alias`), and which A/B colour the book uses (`variant`).
- `book.json`: what was checked in the printed book: the renames, the A/B choice, and the CMYK of the 12 new colours.

The scanned colours are 90-year-old paper chips under the scanner's light, so they are only used to check matches, not as colour values.

## Findings (checked against the book)

- 72 cards, 330 colours in all: 3 colours on 12 cards, 4 on 22, 5 on 25, 6 on 10, 7 on 3. The book keeps the cards' numbers and colour order (first and last of each month checked) but prints the colours at equal size; the cards show the first one large.
- 312 of the 330 are Volume 1 colours: 133 of our 159 appear. 59 cards use only Volume 1 colours.
- Volume 1 colours keep their CMYK in the book (checked on No. 1).
- Renamed: three card names are Volume 1 colours under another name; the book uses ours. Cerulean Blue is our Cerulian Blue (same CMYK), Light Green (card 34) is Night Green, Tawny Olive (card 32) is Khaki. Recorded in `corrections.json` (`alias`) and `book.json` (`renamed`).
- Same-name pairs: the book's colour index lists only A, so Grayish Lavender and Eugenia Red are A everywhere (`corrections.json` `variant`). The scans had suggested B for some Grayish Lavender chips; the book disagrees (No. 1). Except No. 16, which has two different Grayish Lavender chips: there the scan decides (4th B, 6th A), and the book agrees: it prints both as Grayish Lavender, 25 33 20 0 then 28 28 0 0. Pale King's Blue names two colours in Volume 2's colour index: Volume 1's 瓶覗 (33 4 7 0) and 藍白 (5 1 9 0), our Pale King's Blue - B. It has no `variant`: the scan decides. Nos. 46 (2nd) and 69 (3rd) have near-white chips, 藍白, and the book agrees (5 1 9 0 on both); Nos. 31, 32, 63 and 71 have 瓶覗's light blue.
- 12 colours are not in Volume 1, used 18 times on 13 cards; their CMYK from the book is in `book.json` (`new`): Dark Perilla Purple, Dull Citrine, Dull Purplish Black, Grape Green, Pale Cinnamon-Pink, Pale Ecru-Drab, Pale King's Blue - B (藍白; the book prints Pale King's Blue, as for Volume 1's 瓶覗; found in the photos of Volume 2's colour index, as the cards name both alike), Pale Methyl Blue (the book prints "Methy"), Pale Purplish Vinaceous, Pale Turtle Green, Sea-foam Yellow, Violet Ultramarine.
- 5 Volume 1 combinations have all their colours on a single Volume 2 card: 69 (card 5), 72 (63), 84 (14), 93 (7), 113 (34).
- Spelling: four names are misspelled in the books (Volume 1 and 2) and fixed in our `colors.json` to Ridgway's (*Color Standards and Color Nomenclature*, 1912), which they come from; the printed spelling is kept as `bookName`: Vandar Poel's Blue (Vanderpoel's Blue; the cards print both Vander Poel's and Vandar Poel's), Cerulian Blue (Cerulean Blue), Antwarp Blue (Antwerp Blue), Rosolanc Purple (Rosolane Purple; card 45 prints Rosolanc too). The book prints "Pale Methy Blue"; we use Methyl. Card 51 misprints Dark Greenish Glaucous as "Grecnish".
