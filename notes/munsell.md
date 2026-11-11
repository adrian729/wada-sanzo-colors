# Wada's colours in Munsell's system

Munsell's notation is how Japan's colour standards write a colour (JIS Z 8721), and PCCS is defined in its terms (see [pccs.md](pccs.md); PCCS was made by the Japan Color Research Institute, which grew out of the association Wada founded in 1927). Wada himself wrote colours in Ostwald's notation (see [ostwald.md](ostwald.md)), so nothing here is his: the notation is computed from our colour values, as a chip would be measured. The site's Colors › Munsell view shows it. [scripts/munsell.py](../scripts/munsell.py) computes it into `munsell.json`; the counts below are from the page.

## The system

- **Hue:** a circle of 10 families, R, YR, Y, GY, G, BG, B, PB, P and RP, each numbered 0 to 10, so 5R is the middle of red and 10R is 0YR. ASTM D1535 numbers the whole circle 0 to 100 (5R is 5, 5YR 15, ... 10RP 100).
- **Value:** lightness, 0 (ideal black) to 10 (ideal white), spaced to look even. The greys are N1 to N9.
- **Chroma:** distance from the grey of the same value, open-ended: as far as colours go.
- **A colour's notation:** hue, value/chroma, e.g. 5R 4/12; a grey is N and its value, e.g. N5.
- **The chips:** the 1943 renotation (Newhall, Nickerson and Judd) measured the system's colours under Illuminant C: 40 hue pages, 2.5 apart (2.5R, 5R, 7.5R, 10R, ...), values 1 to 9, chroma in steps of 2. Its 2,734 "real" colours are those a surface can reflect (within the MacAdam limits). Its Y is against magnesium oxide, the white standard of the time.

## Placing Wada's colours

- **Against the ideal white:** a chip's notation is measured against the perfect white, and Wada's colours are printed on paper, which reflects less. Our values (colors.json) are relative to the paper, as the CMYK was printed on it, so each colour's Y is multiplied by the paper's own: 0.8561, the media white point of the Japan Color 2011 Coated profile. Wada's white paper comes out N9.4.
- **Under Illuminant C:** each colour is adapted from D65 (CSS's white, our values') to C with Bradford's transform.
- **The conversion:** colour-science's (Centore's method, from the renotation data), with the value scale of ASTM D1535. Each colour's notation, converted back, is within 0.00012 of it in OKLab.
- **A colour's cell:** its nearest hue page, its value rounded (1 to 9), and its chroma rounded to the nearest even step, its ring. Under chroma 1 it is a grey: N and its value. The cell's code is what the view calls it, e.g. Munsell ≈ 5R 5/10; the exact notation is given too, e.g. 5.8R 5.4/10.2 for Eugenia Red - A.

## The system's own colours

- **Each empty cell** shows the renotation's colour for it, in our space: its Y scaled by 0.975 (magnesium oxide against the ideal white, as ASTM D1535 does), adapted from C to D65, and made relative to the paper. The greys N1 to N9 come from ASTM D1535's value scale.
- **Ranges,** as in the OKLCH view:
  - Screen: the chips Rec. 2020 holds, 2,096 of the 2,734;
  - Print: the chips the press prints (Japan Color 2011 Coated, at most 350% ink), 955;
  - all 9 greys in both.
- **A page's rings** at a value go out to its last chip in the range, or to one of Wada's colours, if that's further. A cell between the two has the renotation's colour, beyond the range, and says so: 2 cells in Screen, 33 in Print. Every cell has a chip in the renotation.
- **Their CMYK** is estimated through the print profile, as the OKLCH view's own colours are.

## The view

- **Flat:** the whole solid seen from above, every colour at once by hue and chroma, its value left out, as the OKLCH view's flat wheel. A page's rings go as far as at its widest value. Each of Wada's colours fills its page and ring (the greys the centre); an empty cell shows the chip of its hue and chroma at the page's widest value, or at the nearest value that has it: the most vivid colour of that chroma.
- **The disc:** one value of the solid, seen from above.
  - Angle is hue, the 40 pages anticlockwise as the hue numbers rise, as the OKLCH view's hues go: 5R near the right, 5Y at the top, 5PB at the bottom. The 10 families' 5s are named round it.
  - Distance from the centre is chroma, a ring per 2. The grey of the value is the centre, wider than a ring (0.12 of the radius, 1.9 rings) so that the first ring's cells, 9° each, aren't slivers.
  - The scale is Screen's: 14 rings (chroma 28) to the dashed rim, in both ranges, so that Print's smaller solid shows as smaller.
- **Cells:** as in the Ostwald view. Each of Wada's colours fills the cell of its code; the info panel gives the code (Munsell ≈ 5R 5/10) and the exact notation ("Measured"). Colours sharing a cell split it in hue order. An empty cell shows a dot of the system's colour; hovering gives its code (Munsell = 10GY 5/12) and values, clicking opens its card. Picked in Create, it is saved as its OKLCH values and named by its code again when read back.
- **The control:** the greys N9 to N1 and the solid's outline beside them, at each value as wide as its widest page in the range, with the slice. Drag, click, scroll or use the arrow keys; Page Up and Down move 2 values, Home and End go to N9 and N1.
- **Switches:** Flat, 2D or 3D; Screen or Print; the cells (every cell a dot, the empty cells as cells with a dot, dots alone, filled, or hidden, as in the other views); the slice (2D); the cut (3D). The page remembers each.
- **Pages:** the slice through the axis shows a hue's page on the right and the opposite one, 20 pages round, on the left (5BG and 5R first), the greys between, N9 at the top.
  - The cells are squares, a ring across and a value up, as Munsell meant them: about as far apart to the eye.
  - Wada's colours sharing a cell split it side by side, out from the axis by chroma; greys sharing one, the lightest on the left.
  - The dial shows each page at its widest value, labelled with the 5s' codes (5R, 5YR, ...). Drag or click to the hue for the right, or scroll, or use the arrow keys (clockwise: right and down; Page Up and Down move 4 pages, to the next 5; Home goes to 5R). Buttons each side of the caption turn the pages.
- **3D:** the solid, drawn as the OKLCH view's: its 40 pages as walls round a column of the greys, a cell a ring wide and a value tall, cut at the value chosen, from the top or the bottom. Each page has a button round it that hides or shows it. Hovering and clicking work as on the disc.
- **Create:** Munsell is a source in the picker, flat or in 2D, as Ostwald is.

## How Wada's colours spread

- **Values 2 to 9:** none at value 1. Per value, 2 to 9: 7, 22, 29, 40, 18, 28, 17, 10.
- **Chroma:** up to 15.5 (8 rings).
- **Cells:** the 171 colours fill 159 cells; 11 are shared, by at most 3.
- **Greys** (under chroma 1), with their exact notation:
  - N9: White (N9.4), Pale King's Blue - B (5.8GY 9.1/0.7);
  - N7: Neutral Gray (3.2B 7.4/0.6), Mineral Gray (4BG 6.9/0.8), Pale Ecru-Drab (5.6YR 7.3/1.0);
  - N6: Warm Gray (4.4GY 6.5/0.6);
  - N3: Dull Purplish Black (3Y 2.6/0.6);
  - N2: Black (3.9Y 1.6/0.3).
- **Beyond the range:** one of Wada's colours is in a cell whose chip Rec. 2020 doesn't hold, and 25 in cells whose chip the press can't print. The colours themselves are within both; the chips, at the cell's rounded chroma, are further out.

## Limits

- **Our values are computed, not measured:** from the book's CMYK through the press's profile (see the README). The notation is as good as that.
- **The paper's white** is the profile's, not the book's paper, which isn't measured.
- **Illuminant C** is the renotation's: the adaptation from D65 is Bradford's, one of several, and changes the notation a little.
- **The renotation** is smoothed and partly extrapolated data, the standard for the notation, not a physical book of chips: real Munsell books hold fewer colours, and their chips vary.
