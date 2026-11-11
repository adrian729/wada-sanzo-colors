# Wada's colours in PCCS

PCCS, the Practical Color Co-ordinate System (日本色研配色体系), was made in 1964 by the Japan Color Research Institute, which grew out of the association Wada founded in 1927. It was made for colour harmony: besides hue, lightness and saturation, it groups colours into tones, and describes combinations by hue and tone. Nothing here is Wada's: he wrote colours in Ostwald's notation (see [ostwald.md](ostwald.md)), and PCCS came after him. The site's Colors › PCCS view shows it. [scripts/pccs.py](../scripts/pccs.py) computes it into `pccs.json`, from `munsell.json` (see [munsell.md](munsell.md)); the counts below are from the page.

## Why it's built on Munsell's notation

- **PCCS is defined in Munsell's terms.** Its lightness is Munsell's value. The institute's reference values (Matsuie's) give each of the PCCS grid's 2,844 points as a Munsell hue, value and chroma, read off charts drawn on Munsell's pages. Its 201-L chart gives each chip's Munsell notation. PCCS has no colorimetric definition of its own, so a PCCS colour is a Munsell colour, named another way.
- **So nothing is given up.** Wada's colours are placed from their Munsell notation, converted. PCCS's own colours are its grid points converted to Munsell notation, then given the renotation's colour, as the Munsell view's chips are. What PCCS adds to Munsell's notation is here: its hue circle, its saturation scale and its tones.
- **The conversion** is Kobayasi and Yosiki's (2001; see the README's sources), fitted to the reference values:
  - their precise algorithm is within 0.23 chroma and 0.2 saturation of them (rms 0.08 and 0.06);
  - hue is exact at the 24 hues, from a table of 201-L's Munsell hues;
  - against 201-L's own chroma, for the seven colours the paper lists as the hardest, it's within 0.43.
- **What isn't available:** Matsuie's table itself, which isn't published that we found. The conversion stands in for it.

## The system

- **Hue:** 24 hues, from the four psychological primaries (2:R, 8:Y, 12:G, 18:B) and their afterimages, so that opposite hues (h and h + 12) are complementary. A hue is written by its number and symbol, e.g. 2:R, 13:bG. On Munsell's circle they're unevenly spaced: 2:R is 4R, 8:Y 5Y, 20:V 9PB.
- **Lightness l:** Munsell's value, in steps of 0.5, from 1.5 (black) to 9.5 (white).
- **Saturation s:** per hue, from 0 (grey) to 9, the most vivid pigment colour of that hue (in 1964). A step is about one of Munsell's chroma, more in dark colours: the same chroma is more saturated in a darker colour.
- **A colour's notation:** hue, lightness, saturation, e.g. 2:R-4.5-9s; a grey, n and its lightness, e.g. n-5.5.
- **Tones:** colours of like lightness and saturation across the hues.
  - The 12: pale p, light lt, bright b, vivid v, strong s, deep dp, light grayish ltg, soft sf, dull d, grayish g, dark dk, dark grayish dkg.
  - The greys': W, ltGy, mGy, dkGy, Bk.
  - A tone is defined by a representative colour per hue (201-L's), and written with the hue's number: v2, lt8.

## Placing Wada's colours

- **From their Munsell notation** (munsell.json: against the ideal white, under Illuminant C), by the precise algorithm:
  - l = V;
  - h from Munsell's hue, between the 24 hues' (linearly);
  - s from a cubic in s per hue, its coefficients the paper's for the even hues, linear between, solved by Newton's method.
- **A colour's cell:** h and s rounded to whole numbers, l to 0.5. If s rounds to 0, it's a grey: n and its lightness. The cell's code is what the view calls it, e.g. PCCS ≈ 2:R-3.5-8s; the exact notation is given too, e.g. 1.6:R-3.5-7.7s for Red.
- **A colour's tone:** from its own values, not its cell's.
  - In Kobayasi and Yosiki's tone coordinates: s, and a relative lightness t = l − m(h) s, which makes each tone's representatives about the same for every hue. The tone is the nearest representative's. 201-L's pale+ and light+ count as pale and light.
  - Under s 1, where the paper's figure draws the edge of the greys, the tone is a grey's, by lightness rounded to 0.5: W 9.5; ltGy 7.5 to 9; mGy 4 to 7; dkGy 2 to 3.5; Bk 1.5. These are 201-L's greys, with those between them going to the middle ones.
  - PCCS defines tones only by their representatives; the paper leaves the regions between them to be drawn as one sees fit. Nearest representative is our choice.
  - So near an edge a colour's tone and its cell can disagree: Wada's near-greys (Munsell chroma under 1) are in cells of s 1, but have a grey's tone.

## The system's own colours

- **The grid:** h 1 to 24, l 1.5 to 9.5 in steps of 0.5, s from 1 up. Each point is converted to Munsell notation and given the renotation's colour (colour-science's interpolation), in our space as munsell.json's chips are: 4,086 colours.
- **As far as the renotation's real colours go:**
  - its chroma is within the real chips' most at its hue and value, interpolated between the pages and values round it, and none at value 10 (the ideal white);
  - the renotation has the data to interpolate it.
- **The greys** n-1.5 to n-9.5, from ASTM D1535's value scale.
- **Each tone's representative per hue:** 201-L's for the even hues; for the odd ones, from the tone coordinates, rounded to 0.5 as 201-L's are. All are in the grid.
- **Ranges,** as in the OKLCH and Munsell views:
  - Screen: 3,573 of the 4,086, out to s 18;
  - Print: 2,147, out to s 11 (PCCS's 9 was the pigments of 1964);
  - all 17 greys in both.
- **Beyond the range:** as in the Munsell view, a page's rings go out to one of Wada's colours if it's further than the range. In Screen, none; in Print, 23 cells, which hold 21 of Wada's colours. Every cell has its colour in the grid.
- **Their CMYK** is estimated through the print profile, as the other views' own colours are.

## The view

- **As the Munsell view:**
  - **The disc:** one lightness. The 24 hues anticlockwise, 15° each, 2:R on the right, 8:Y at the top, named by their codes; a ring per step of saturation, 18 to the rim (Screen's most).
  - **Pages:** a hue and its complement, back to back. The cells are squares, a step of saturation across and 0.5 of lightness up: about as far apart to the eye, since a step of s is about one of Munsell's chroma, half a step of value.
  - **3D:** the solid, its 24 pages as walls.
  - **The control:** its 17 lightnesses, 9.5 at the top.
  - **Create:** PCCS is a source in the picker, flat or in 2D (its tone map too), as Munsell is.
- **Flat:** the whole solid seen from above, every colour at once by hue and saturation, its lightness left out, as the Munsell and OKLCH views' flat ones. Saturation is measured against each hue's most vivid pigment colour, so a ring is as far towards full colour on every hue: yellow and blue at s 9 are both vivid, though their Munsell chromas differ. An empty cell shows the system's colour of its hue and saturation at the page's widest lightness, or at the nearest that has it.
- **Tones (2D only):** the tone map, PCCS's own overview, with every colour at once.
  - Each chromatic tone is a ring of the 24 hues round its code, the hues placed as on the disc.
  - Tones are placed as the institute's tone diagram has them: across by saturation (a column each for 2, 5 and 8, and vivid's 9), up by the tone coordinates' relative lightness, pushed apart where two would touch. The greys' five are in a column on the left, W at the top.
  - Each of Wada's colours fills its tone's sector at its hue, or its grey tone's disc. An empty sector shows the tone's representative colour at that hue; an empty grey tone, its middle grey.
  - **One tone, large:** clicking a tone's code (the ring's hole, or the code beside a grey tone's disc) shows it large. A chromatic tone's ring fills the disc, its hues where the disc has them and named round it; a grey tone's disc is drawn large. The arrows under it, and the arrow keys, go to the previous or next tone, the greys' after the 12. Its code again, the All tones button or Escape go back to the map. The page remembers the tone.
- **The info panel** gives the cell's code (PCCS ≈ 2:R-3.5-8s), the tone (Tone: deep, dp2) and the exact notation ("Measured").

## How Wada's colours spread

- **Lightness 1.5 to 9.5:** per lightness, 9.5 to 1.5: 1, 4, 8, 6, 15, 16, 12, 9, 16, 19, 16, 12, 12, 11, 11, 1, 2.
- **Saturation:** up to 9.8, just over vivid's 9.
- **Cells:** the 171 colours fill 162 cells; 8 are shared, by at most 3.
- **Tones:** lt 19, d 19, s 18, p 17, g 17, dp 15, v 13, dk 13, sf 10, b 9, ltg 8, dkg 5; the greys' 8. On the tone map they fill 121 sectors, 32 of them shared, by at most 3.
- **Greys:** only White is grey in its cell (n-9.5). Wada's other near-greys have s just under 1, in cells of s 1, with a grey's tone:
  - ltGy: Neutral Gray (15.6:gB-7.4-0.6s), Pale Ecru-Drab (5.4:O-7.3-0.9s), Pale King's Blue - B (10.6:yG-9.1-0.7s);
  - mGy: Mineral Gray (13.8:BG-6.9-0.8s), Warm Gray (10.3:YG-6.5-0.6s);
  - dkGy: Dull Purplish Black (7.3:rY-2.6-0.7s);
  - Bk: Black (7.6:Y-1.6-0.6s).

## Limits

- **Everything in munsell.md's limits holds here too:** our values are computed, not measured; the paper's white is the profile's; Illuminant C is reached by Bradford's adaptation; the renotation is smoothed data.
- **The conversion is a fit** to the reference values, within 0.23 chroma of them. Beyond s 9 its cubic is extrapolated: it was fitted up to 9.
- **The tones' regions are our choice** (the nearest representative), and so is their placing on the tone map. The odd hues' representatives are computed: 201-L has vivid's and bright's, but the paper doesn't list them, and the other tones have none there.
- **The steps are the system's:** like Munsell's, PCCS is a grid, so its solid is drawn in steps, cell by cell.
