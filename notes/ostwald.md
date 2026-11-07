# Wada's colours in Ostwald's system

Wada wrote colours in Ostwald's notation, and his colour-name books give every colour in it (see [guidelines.md](guidelines.md#reading-a-colour)). The NDL has scans of those books, but they aren't public, so the codes here are computed from our colour values, not taken from him. They follow the system as his 1935 supplement draws it, as closely as his own data allows. The site's Colors › Ostwald view shows them. [ostwald.py](ostwald.py) prints every number below, except the one-off checks marked as such.

## The system, as Wada drew it

- **Mixing:** every colour is full colour, white and black, adding up to 1. Ostwald measured them on a spinning disc, so the mixture is additive.
- **Hue:** a circle of 100 steps:
  - yellow 0, orange 12.5, red 25, purple 37.5, ultramarine 50, turquoise 62.5, sea green 75, leaf green 87.5;
  - complementary hues are 50 steps apart;
  - Wada's Figure 1 (1935, p. 9) draws it as 24 hues numbered on the 100-step scale (00, 04, 08, 13, ...), with Gelb (yellow) at the top, Rot (red) at the right, Ublau (ultramarine) at the bottom and Seegrün (sea green) at the left, clockwise.
- **Greys:** Wada's Figure 2 (p. 10) letters them A to P, 16 letters including J. Ostwald's own scale has 15 and skips j.
  - Wada doesn't list the letters' values. He gives the ends: his white reflects about 90% of the light and his black 3.5% (p. 6), which are Ostwald's a (0.891) and p (0.0355).
  - Here the 16 letters are spaced evenly on a log scale between those ends, as Ostwald spaced his, so that they look evenly spaced. Each is about 0.81 times the white of the one before: A 0.891, B 0.719, C 0.580, D 0.468, E 0.377, F 0.304, G 0.245, H 0.198, I 0.160, J 0.129, K 0.104, L 0.0838, M 0.0676, N 0.0546, O 0.0440, P 0.0355.
  - A grey's black content is 1 minus its white.
  - The 16 letters fit Wada's count of "120 variations" per hue, 12,000 over the 100 hues (p. 13): a hue's triangle with 16 greys holds 16 × 15 / 2 = 120 colours off the axis. With 15 letters it would hold 105.
- **A colour's code:** the hue number, then two letters. The first letter gives the white content; the second gives the black, as 1 minus that grey's white.
  - Wada's orange, 16PA, is hue 16 with white 0.0355 (P) and black 0.109 (1 − A). He reads a second letter A as no black (p. 14), since his white already holds about 10% black (p. 6).
  - His scorched brown, 17PK, has white 0.0355 and black 0.896.
- **The solid:** a double cone, with the greys on its axis, white at the top. Each hue is a triangle from the axis out to its full colour. A code's two letters fix the colour's row and its distance from the axis.

## Placing Wada's colours

- **White, black and colour:** convert OKLCH to linear sRGB, clipped to the gamut. White is the smallest channel, black is 1 minus the largest, and colour is the rest.
- **Hue:** the hexagonal (HSV) hue of the linear RGB. It puts additive complements exactly opposite, as Ostwald's circle does. His circle runs the other way round, at 25 steps per 90°.
- **Calibration:** the hue is shifted so that Wada's Orange is 16 (+2.77 steps). Only this zero point is fitted.
- **Letters:** white content, and 1 minus black, each go to the nearest of the 16 greys on the log scale. When both land on the same grey, the colour is that grey.
- **Code:** the hue rounded to a whole step, then the two letters, e.g. 16PA. Greys get one letter.

## Choices tested against Wada's data

- **Hue from wavelength (tested, not used):** Wada's Figure 3 (p. 11) sets his 100-step circle against the wavelengths of the spectrum.
  - Read off the scan (one-off, November 2026; its hue scale is regular to about 0.15 steps): 420 nm 45.0, 430 nm 48.0, 440 nm 50.0, 450 nm 51.9, 460 nm 53.1, 470 nm 55.8, 480 nm 62.1, 490 nm 77.9, 500 nm 82.9, 510 nm 85.2, 520 nm 86.9, 530 nm 87.9, 540 nm 88.8, 550 nm 90.9, 560 nm 93.2, 570 nm 98.6, 580 nm 6.0, 590 nm 12.0, 600 nm 14.1, 610 nm 16.0, 620 nm 17.8, 630 nm 19.1, 640 nm 20.8, 650 nm 22.2, 660 nm 23.8, and 25.0 at the red end of the spectrum. The purples, 25 to 45, have no wavelength.
  - The test (one-off): take each colour's dominant wavelength (CIE 1931, D65 white; for a purple, the complementary wavelength, 50 steps round) and read its hue off that scale.
  - Orange comes out 12.3, not 16.
  - Wada's complementary pairs (p. 22) come out 8.0 steps from opposite on average, and none within 3. The hexagonal hue puts 7 of the 10 within 3 (see below).
  - On p. 22, Wada notes that the true complement of Red Orange is a colour "a little greener" (今少シ緑ガカツタモノ) than his Green Blue. Here it lands 10 steps bluer; with the hexagonal hue it lands 2.1 steps greener.
  - Illuminant C, a daylight white of the 1930s, gives much the same: Orange 12.2, the pairs 8.8 steps off.
  - So the figure doesn't describe his chips as our values measure them, and the hue here stays additive.
- **Measuring against paper white (tested, not used):** his white reflects about 90%, so a white of 0.891 could stand for sRGB's 1. Scaling our values that way makes Orange 16PB, not 16PA, so they are measured as they are.

## The view

- **The disc:** one level of the solid, seen from above.
  - Angle is hue, in Wada's 24 sectors, with yellow at the top and red at the right.
  - Distance from the centre is colour content, in his steps.
- **Levels:**
  - The level is the sum of the two letters' positions: 0 is white, 30 black.
  - The ring is their difference: 0 is the axis, 15 the full colour.
  - Even levels have a grey at the centre. Odd levels fall between two greys, and level 15, between H and I, has the full colours at its rim.
  - Levels shrink towards the tips, as the cone does.
- **Cells:** each of Wada's colours fills the cell of its code, so it stands for a range of white and black. The info panel gives its exact values. Colours sharing a cell split it in hue order. An empty cell shows a dot of the system's own colour there, in sRGB. Hovering it gives that colour's code and values; clicking or tapping it opens its card, as a colour's, with the same values, its white and black content, and its CSS colour to copy; it has no name, so the panel calls it "Ostwald" and its code, e.g. Ostwald 67JG, and gives the code as exact (Ostwald = 67JG) where Wada's colours have an approximate one (Ostwald ≈ 16PA). Its CMYK is estimated, so it has ≈ too (see [CMYK for the empty cells](#cmyk-for-the-empty-cells)).
- **The control:** the 16 greys and the cone's outline, with the current slice. The cone runs from the middle of A to the middle of P, as the levels do. The slice's ellipse holds its level's disc, in the system's own colours, seen from the front with yellow at the back and red on the right, as on the disc. The axis goes behind the disc's near half, so that it reads as passing through it. Drag, click, scroll, or use the arrow keys (Page Up and Down move a whole grey). Hovering over it previews a level on the disc without choosing it; a dashed slice, with its own disc, marks the level previewed.
- **Empty cells:** a second switch, beside the 2D/3D one, shows them as cells with a dot (the default), as the dots alone, filled with the system's own colour, so the disc or solid is complete, or hidden, leaving only Wada's colours. Its four diamonds draw a cell each way, dashed where the cell isn't drawn; their tooltips, or a label on touch screens, say which is which. It works in both views, and the page remembers the choice. With the dots alone, hovering a dot still outlines its cell on the disc.
- **3D:** the 2D/3D switch under the control shows the whole solid instead, drawn with WebGL.
  - 24 pages, one per hue sector, stand round a pole of the 16 greys. Each page is Wada's Figure 2 triangle stood upright: white at the top, black at the bottom, the full colour at the outer tip. Its cells are diamonds, and it is equilateral, as in his figure.
  - The pages are wedges, 40% of their sector, so that the gaps between them show their faces.
  - Wada's colours fill their cells. Empty cells are pale card with a dot of the system's colour on each side of the page, as on the disc, and on the page's outer edge, so the solid's surface shows its colours too: from the top, pale near the pole to the full colour at the rim. On the pole, an empty grey has a band of its grey.
  - With the empty cells hidden, only Wada's colours are left, each in its place, closed by walls where its neighbours were. Filled, the empty cells have their own colour on every face, and the solid is whole.
  - With the dots alone, Wada's colours stand as when the empty cells are hidden, and each empty cell is a sphere of its colour at its middle, smaller near the pole, where the cells crowd. The spheres are faked: discs facing the camera, shaded as if lit from the upper left, in front, so each has its exact colour where the light falls square and darker toward its rim. Hovering one draws it bigger, on top, with a thin ring round it, in place of the cell's outline, which among the dots is hard to place.
  - The control cuts the solid through the middle of its level: what's above is hidden. A third switch, in 3D only, cuts from the bottom instead: what's below is hidden, and the view turns to look up at the cut face, so the pale upper half can be opened too. Its two choices are drawn as the solid's outline with the part that stays filled. Seen from straight above, the cut face is the disc; from straight below, the disc mirrored. The control's figure runs from the middle of A to the middle of P, but the solid's end cells reach half a level further, to its tips. So at the end the cut comes from (A from the top, P from the bottom) nothing is cut, as on the figure: a cut through the middle of A would take the white tip off while the black one stays.
  - The control's figure then fills in what the cut leaves, so it shows which side is gone. The fill is the solid's section through its axis, in the system's own colours: a page of Wada's Figure 2 on each side of the greys, facing as the view does, with the hue on the solid's right on the right. The slice's ellipse holds the cut face, the disc of the level, seen from above, or from below when cut from the bottom. It turns with the solid, follows a previewed level too, and is a wash, so the outlines show through.
  - Faces keep their exact colour, with no lighting; only the pages' edges are shaded. The canvas is sRGB, so the 16 colours outside it are clipped (see [Limits](#limits)); the disc shows them as the browser does.
  - Drag, or use the arrow keys, to turn it. Hovering and clicking work as on the disc.
  - Round the solid, each of the 24 pages has a button that hides or shows it, to see inside: the hue's name where it has one, a dot of its full colour for the other 16. A hidden page's name is struck through, and its dot hollow. The names show through the solid, faint; a dot hides behind it (behind its outline, less what the cut hides).

## Checks

- **Orange comes out as 16PA.** Its exact values are white 0.014 and black 0.127, against the letters' 0.0355 and 0.109. The letters weren't fitted, so this match doesn't follow from the calibration.
- **Wada's complementary pairs (1935, p. 22)** should be 50 steps apart. How far each is from that:

| Pair | Hues | Off by |
|---|---|---|
| Spectrum Red, Sea Green | 19.8, 72.7 | 2.9 |
| Red Orange, Green Blue | 18.6, 66.5 | 2.1 |
| Orange, Peacock Blue | 16.0, 65.0 | 1.0 |
| Yellow Orange, Antwerp Blue | 12.8, 61.5 | 1.3 |
| Apricot Yellow, Blue | 7.0, 58.1 | 1.1 |
| Yellow, Deep Lyons Blue | 4.7, 56.8 | 2.1 |
| Lemon Yellow, Violet Ultramarine | 4.5, 47.4 | 7.2 |
| Light Green Yellow, Violet | 1.1, 50.1 | 1.1 |
| Yellow Green, Red Violet | 96.1, 40.0 | 6.1 |
| Night Green, Rosolane Purple | 93.8, 24.2 | 19.7 |

- **7 of the 10 pairs are within 3 steps.** With OKLCH hue in place of the hexagonal hue, only 2 are; with the wavelength scale of Figure 3, none. The hexagonal hue is the best scale tried for Wada's circle.
- **Night Green and Rosolane Purple don't fit:** they are 19.7 steps off, about a fifth of the circle.
- **Perceptual check:** for each colour, the nearest of the system's cell colours in OKLab:
  - is its own cell for 86 colours, and a neighbouring cell for 83;
  - is a cell further off for 1, but closer than its own by only 0.010;
  - is at a median distance of 0.019 from the colour's own cell colour, and at most 0.077.
- **A second implementation (one-off check, November 2026):** written separately, converting through XYZ and taking the hue from Python's `colorsys`.
  - It places 166 of the 170 colours as the site does.
  - The other 4 sit on a rounding boundary:
    - Fresh Color's hue is 17.500 against 17.496 (18GA or 17GA);
    - Apricot Orange's white content is on the K/L boundary (15KA or 15LA);
    - Deep Slate Green's sector is 16.496 against 16.502;
    - Grayish Lavender B's hue, a near-grey, is 26.53 against 26.46 (27DC or 26DC).
- **Chrome's own conversion (one-off):** each colour in 8-bit sRGB is within one level of ours, for all 170.
- **The drawing (one-off, every level, read from the page):**
  - each colour is drawn once, at its level, in its own value;
  - every point of its outline lies inside its own cell;
  - points sampled across all 2,896 cells are covered by exactly that cell's colours, one each;
  - the dots in the 2,746 empty cells have the system's colour, within one 8-bit level;
  - the only exceptions are the 4 boundary colours above, which the second implementation puts in the next cell.

## CMYK for the empty cells

- **How:** the cell's colour goes to CIE Lab, then to CMYK through the colorimetric table (B2A1) of the Japan Color 2011 Coated profile. That is the inverse of the table that turns the book's CMYK into our values (`scripts/cmyk_to_oklch.py`). The profile also decides how much black stands in for cyan, magenta and yellow.
- **Where it comes from:** `scripts/ostwald_cmyk.py` writes the estimates to `ostwald-cmyk.json` and prints the checks below. The page ignores the file if it was made for another calibration, so re-run the script after changing `colors.json`.
- **Tested on Wada's 170 colours,** whose CMYK the book gives:
  - every ink is within 5 points of the book's for 101 colours, and within 10 for 125;
  - printed back through the profile, the estimate is the colour itself: within ΔE2000 2.5, median 0.33;
  - the 16 furthest off, by more than 20 points on some ink, are dark colours. The same dark colour can be printed with more black or with more of the other three inks, and the book chose differently from the profile. Black, for example, is C 20 M 10 Y 15 K 100 in the book and C 85 M 83 Y 84 K 76 estimated.
- **What the press can't print:** 508 of the 2,896 cells are more vivid than Japan Color 2011 Coated allows; their estimate prints more than ΔE2000 3 away. Most are purples (133), ultramarines (120), sea greens (91) and leaf greens (87), towards the full colours. Their CMYK is the nearest colour the press can print, so for them the ≈ is looser.

## How the colours spread

- **Per level,** white to black: 1, 1, 6, 3, 8, 8, 8, 6, 3, 5, 4, 2, 9, 6, 10, 11, 7, 13, 7, 9, 10, 14, 2, 2, 3, 6, 2, 0, 3, 0, 1.
- **Per ring,** axis to full colour: 3, 8, 22, 13, 15, 17, 16, 9, 7, 15, 11, 7, 7, 10, 3, 7.
  - Most of the palette is muted: 103 colours lie in the inner half of the rings, and only 7 are full colours, all between yellow and red-orange, hues 5 to 18 (Yellow, Apricot Yellow, Orange Yellow, Yellow Orange, Orange, Jasper Red and Peach Red).
  - Only 3 are greys: White (A), Warm Gray (E) and Black (P). The other near-greys keep a step of colour at this scale.
- **Cells:**
  - the 170 colours fill 150 cells;
  - 17 cells hold two or more;
  - the most in one cell is 3.
- **Letters:** all 16 are used. J, the letter Ostwald's scale lacks, is in 12 codes.

## Limits

- **One calibration point.** Orange fixes the hue's zero point. Between the pairs, the spacing of the hue scale is HSV's, not Ostwald's, which he meant to look even.
- **The letters' values are inferred.** Wada gives the 16 letters and the two ends, not the values in between; even spacing on a log scale is Ostwald's rule, carried over.
- **Our values aren't his.** They come from the reprint's CMYK, converted to OKLCH (see the main README), not from his colour cards. Expect a step's difference here and there.
- **sRGB isn't Ostwald's full colour.**
  - His full colours were pigments, not sRGB's primaries, so the same colour measures differently against them.
  - Orange shows this: white 0.014 and black 0.127 here, against 0.0355 and 0.109.
  - 16 colours lie outside sRGB and are clipped before they are measured, by up to 0.105 (Peacock Blue, Benzol Green).
- **The 24 sectors and the letters are rounded.**
  - 50 colours are within 0.05 of a step from a neighbouring cell, and 73 within 0.1, so a small change in their values moves them. Values spread evenly across their cells would put about 38 and 71 there. Within 0.1 that matches; within 0.05 there are 12 more, spread across white, black and hue, so no one scale causes it.
  - Rounding our values to 8-bit sRGB alone moves 9 of them (one-off).
