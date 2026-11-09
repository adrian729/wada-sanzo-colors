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
- **Hue:** one scale decides which hue a colour has, another how far apart the hues are.
  - The hexagonal (HSV) hue of the linear RGB gives the colour's full colour, the one it is mixed from. It puts additive complements exactly opposite, as Ostwald's circle does.
  - Ostwald also spaced his circle evenly to the eye. The full colour's OKLCH hue is even to the eye, but sRGB's full colours aren't symmetrical in it: a full colour and its complement are up to 29° from opposite. So the hue is the mean of the two, the complement's turned half round, and complements stay exactly 50 steps apart.
  - His circle runs the other way round from OKLCH's, at 25 steps per 90°.
- **Calibration:** the hue is turned so that Wada's Orange is 16, which puts hue 0 (yellow) at a mean OKLCH hue of 97.8°. Only this zero point is fitted.
- **Letters:** white content, and 1 minus black, each go to the nearest of the 16 greys on the log scale. When both land on the same grey, the colour is that grey.
- **Code:** the hue rounded to a whole step, then the two letters, e.g. 16PA. Greys get one letter.

## Choices tested against Wada's data

- **Even steps of the hexagonal hue (tested, not used):** the hexagonal hue alone, 3.6° per step, calibrated on Orange in the same way.
  - Its steps aren't even to the eye: a sector spans from 6.4° to 30.9° of OKLCH hue. The purples crowd together, and orange to red is stretched.
  - Wada's Yellow comes out 4.7 and his Red 21.4, and hue 25, Ostwald's red, is a pink: #ff009c at its full colour. With the mean OKLCH hue, his Yellow is 1.2 and his Red 24.3 (see [Checks](#checks)).
  - It puts more of his complementary pairs within 3 steps, 7 of the 10 against 5, but they are further off on average, 4.5 steps against 4.0. The pairs are the same additive complements on both scales; only the count of steps between them differs.
- **Hue from wavelength (tested, not used):** Wada's Figure 3 (p. 11) sets his 100-step circle against the wavelengths of the spectrum.
  - Read off the scan (one-off, November 2026; its hue scale is regular to about 0.15 steps): 420 nm 45.0, 430 nm 48.0, 440 nm 50.0, 450 nm 51.9, 460 nm 53.1, 470 nm 55.8, 480 nm 62.1, 490 nm 77.9, 500 nm 82.9, 510 nm 85.2, 520 nm 86.9, 530 nm 87.9, 540 nm 88.8, 550 nm 90.9, 560 nm 93.2, 570 nm 98.6, 580 nm 6.0, 590 nm 12.0, 600 nm 14.1, 610 nm 16.0, 620 nm 17.8, 630 nm 19.1, 640 nm 20.8, 650 nm 22.2, 660 nm 23.8, and 25.0 at the red end of the spectrum. The purples, 25 to 45, have no wavelength.
  - The test (one-off): take each colour's dominant wavelength (CIE 1931, D65 white; for a purple, the complementary wavelength, 50 steps round) and read its hue off that scale.
  - Orange comes out 12.3, not 16.
  - Wada's complementary pairs (p. 22) come out 8.0 steps from opposite on average, and none within 3. The scale here puts 5 of the 10 within 3, and 4.0 steps off on average (see below).
  - On p. 22, Wada notes that the true complement of Red Orange is a colour "a little greener" (今少シ緑ガカツタモノ) than his Green Blue. Here it lands 10 steps bluer; with the scale here, 3.1 steps greener.
  - Illuminant C, a daylight white of the 1930s, gives much the same: Orange 12.2, the pairs 8.8 steps off.
  - Its spacing is closer to the scale here than to even steps of the hexagonal hue: over the 137 colours three or more steps from the axis, each scale's hue minus the figure's spreads by 4.2 steps (standard deviation), against 5.2.
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
- **The cells switch:** a second switch, beside the 2D/3D one, shows every cell as a dot, or shows the empty cells as cells with a dot (the default), as the dots alone, filled with the system's own colour, so the disc or solid is complete, or hidden, leaving only Wada's colours. Its first choice is drawn as a dot with smaller ones where a cell's corners would be; the other four are diamonds, a cell drawn each way, dashed where the cell isn't drawn. Their tooltips, or a label on touch screens, say which is which. It works in both views, and the page remembers the choice. With the dots alone, hovering a dot still outlines its cell on the disc.
- **Every cell a dot:** Wada's colours become dots too, so the view is a lattice of the system's colours with his standing out. His dots are 1.6 times the empty cells' dots, as far as they fit in their cell. Where the cells narrow, they come out smaller: 1.42 to 1.48 times within five rings of the disc's centre, and 1.45 times within two rings of the pole in 3D.
  - Colours sharing a cell (13 cells: 12 pairs and one of three) are all one size, as big as fits in the cell. On the disc they sit in a row round the circle in hue order, or in a row along the radius, or, for the three, in two rows, one dot inside and two outside: whichever gives the biggest dots. Along the radius each sits as far out as it would in the solid: the less white for its colour, the further out. The pages and the 3D view set them side by side the same way, out from the axis; greys sharing a cell go one above another, the lightest at the top (White above Pale King's Blue - B, in A).
  - The shared dots come out between an empty cell's dot and a lone colour's: 1.09 to 1.33 times an empty dot on the disc, where the cells are shallow for their dots (1.09 for the two greys in A); on the pages, full size, but 1.26 times for the three and 1.35 for the two greys in A; in 3D, full size, but 1.28 times for the pair near the pole, 1.32 for the two greys on it in A, and 1.24 times for the three.
  - Hovering a dot outlines its piece of the cell: on the disc, the cell split halfway between its dots; on the pages, split into equal shares, side by side, as the other choices split it. In 3D, it draws the dot bigger, with a ring, as for the empty cells' dots.
- **Pages:** a third switch, in 2D only, slices the solid through its axis instead of across it, so the view shows two pages back to back: a hue's on the right, its complement's on the left (Sea green and Red, Ultramarine and Yellow, ...), the greys between, white at the top.
  - Each page is Wada's Figure 2 triangle, equilateral, its cells diamonds, as in the solid, so the two make a rhombus. The hues are named at its tips (on phones, only in the caption, left then right, each with a square of its full colour).
  - Cells work as on the disc, and the cells switch too. Wada's colours sharing a cell split it side by side in hue order; greys sharing one, one above another, the lightest at the top.
  - In the control's place, a dial: the solid's middle level seen from above, as the disc shows it, the two pages bright, the slice across it, and a pointer at the hue on the right. The named hues are round it, as round the disc, the two pages' darker, where there is room for them beside the pages; on smaller screens, and on phones, the dial is alone. Drag or click to the hue for the right, or click its name, scroll, or use the arrow keys (clockwise: right and down; Page Up and Down move three pages, to the next named hue; Home goes to yellow). Hovering previews a pair of pages, marked by a dashed slice. Buttons each side of the caption turn to the previous or next pages. There are 24 positions, so each pair shows twice, mirrored.
  - The 3D view keeps step: switching to it faces the pages chosen, the hue on the right on the solid's right, and turning it then switching back shows the pages it faced. The 3D view has no cut through the axis of its own: the cut would have to follow the camera, so the solid would change shape while it turns.
  - The page remembers the slice and the pages.
- **3D:** the 2D/3D switch under the control shows the whole solid instead, drawn with WebGL.
  - 24 pages, one per hue sector, stand round a pole of the 16 greys. Each page is Wada's Figure 2 triangle stood upright: white at the top, black at the bottom, the full colour at the outer tip. Its cells are diamonds, and it is equilateral, as in his figure.
  - The pages are wedges, 40% of their sector, so that the gaps between them show their faces.
  - Wada's colours fill their cells. Empty cells are pale card with a dot of the system's colour on each side of the page, as on the disc, and on the page's outer edge, so the solid's surface shows its colours too: from the top, pale near the pole to the full colour at the rim. On the pole, an empty grey has a band of its grey.
  - With the empty cells hidden, only Wada's colours are left, each in its place, closed by walls where its neighbours were. Filled, the empty cells have their own colour on every face, and the solid is whole.
  - With the dots alone, Wada's colours stand as when the empty cells are hidden, and each empty cell is a sphere of its colour at its middle, smaller near the pole, where the cells crowd. The spheres are faked: discs facing the camera, shaded as if lit from the upper left, in front, so each has its exact colour where the light falls square and darker toward its rim. Hovering one draws it bigger, on top, with a thin ring round it, in place of the cell's outline, which among the dots is hard to place.
  - With every cell a dot, Wada's colours are spheres too, bigger, and the solid is a lattice of spheres. Hovering any of them draws it bigger, with its ring.
  - The control cuts the solid through the middle of its level: what's above is hidden. A third switch, in 3D only, cuts from the bottom instead: what's below is hidden, and the view turns to look up at the cut face, so the pale upper half can be opened too. Its two choices are drawn as the solid's outline with the part that stays filled. Seen from straight above, the cut face is the disc; from straight below, the disc mirrored. The control's figure runs from the middle of A to the middle of P, but the solid's end cells reach half a level further, to its tips. So at the end the cut comes from (A from the top, P from the bottom) nothing is cut, as on the figure: a cut through the middle of A would take the white tip off while the black one stays.
  - The control's figure then fills in what the cut leaves, so it shows which side is gone. The fill is the solid's section through its axis, in the system's own colours: a page of Wada's Figure 2 on each side of the greys, facing as the view does, with the hue on the solid's right on the right. The slice's ellipse holds the cut face, the disc of the level, seen from above, or from below when cut from the bottom. It turns with the solid, follows a previewed level too, and is a wash, so the outlines show through.
  - Faces keep their exact colour, with no lighting; only the pages' edges are shaded. The canvas is sRGB, so the 16 colours outside it are clipped (see [Limits](#limits)); the disc shows them as the browser does.
  - Drag, or use the arrow keys, to turn it. Hovering and clicking work as on the disc.
  - Round the solid, each of the 24 pages has a button that hides or shows it, to see inside: the hue's name where it has one, a dot of its full colour for the other 16. A hidden page's name is struck through, and its dot hollow. The names show through the solid, faint; a dot hides behind it (behind its outline, less what the cut hides).

## Checks

- **Orange comes out as 16PA.** Its exact values are white 0.014 and black 0.127, against the letters' 0.0355 and 0.109. The letters weren't fitted, so this match doesn't follow from the calibration.
- **Yellow and Red come out near Ostwald's.** Only Orange is fitted, but Wada's Yellow comes out 1.2 (1PA) and his Red 24.3 (24PE), by Ostwald's yellow (0) and red (25), and his Sea Green 76.2, by sea green (75).
- **Wada's complementary pairs (1935, p. 22)** should be 50 steps apart. How far each is from that:

| Pair | Hues | Off by |
|---|---|---|
| Spectrum Red, Sea Green | 21.7, 76.2 | 4.4 |
| Red Orange, Green Blue | 19.9, 66.8 | 3.1 |
| Orange, Peacock Blue | 16.0, 64.5 | 1.5 |
| Yellow Orange, Antwerp Blue | 10.8, 58.8 | 2.0 |
| Apricot Yellow, Blue | 3.2, 54.4 | 1.2 |
| Yellow, Deep Lyons Blue | 1.2, 52.9 | 1.8 |
| Lemon Yellow, Violet Ultramarine | 1.1, 43.4 | 7.6 |
| Light Green Yellow, Violet | 97.5, 46.1 | 1.4 |
| Yellow Green, Red Violet | 92.4, 38.6 | 3.8 |
| Night Green, Rosolane Purple | 90.8, 27.8 | 13.0 |

- **5 of the 10 pairs are within 3 steps,** and they are 4.0 steps off on average. With each colour's own OKLCH hue, whose opposite hues aren't additive complements, only 2 are; with the wavelength scale of Figure 3, none.
- **Night Green and Rosolane Purple don't fit:** they are 13.0 steps off, about an eighth of the circle.
- **Perceptual check:** for each colour, the nearest of the system's cell colours in OKLab:
  - is its own cell for 84 colours, and a neighbouring cell for 80;
  - is a cell further off for 7, but closer than its own by at most 0.018;
  - is at a median distance of 0.019 from the colour's own cell colour, and at most 0.071.
- **A second implementation (one-off check, November 2026):** written separately. It converts through XYZ, takes the hexagonal hue from Python's `colorsys` and the mean hue as a circular mean, and finds each sector's full colour in a table rather than by halving.
  - It places 168 of the 170 colours it was run on as the site does (Pale King's Blue - B came later; it is A by a clear margin, white content 0.84 against A and B's boundary at 0.80).
  - The other 2 sit on a rounding boundary:
    - Apricot Orange's white content is on the K/L boundary (15KA or 15LA);
    - Pistachio Green's sector is 19.498 against 19.504 (81JF either way, in the sector of 79 or of 83).
- **Chrome's own conversion (one-off):** each colour in 8-bit sRGB is within one level of ours, for all 170 it was run on (before Pale King's Blue - B).
- **The drawing (one-off, every level, read from the page):**
  - each colour is drawn once, at its level, in its own value;
  - every point of its outline lies inside its own cell;
  - points sampled across all 2,896 cells are covered by exactly that cell's colours, one each;
  - the dots in the 2,739 empty cells have the system's colour, within one 8-bit level;
  - with every cell a dot, each of Wada's dots lies in its own piece of its cell and no other, and no two dots overlap, at every level and at all 24 positions of the pages;
  - the only exceptions are the 2 boundary colours above, which the second implementation puts in the next cell.

## CMYK for the empty cells

- **How:** the cell's colour goes to CIE Lab, then to CMYK through the colorimetric table (B2A1) of the Japan Color 2011 Coated profile. That is the inverse of the table that turns the book's CMYK into our values (`scripts/cmyk_to_oklch.py`). The profile also decides how much black stands in for cyan, magenta and yellow.
- **Where it comes from:** `scripts/ostwald_cmyk.py` writes the estimates to `ostwald-cmyk.json` and prints the checks below. The page ignores the file if it was made for another calibration, so re-run the script after changing `colors.json`.
- **Tested on Wada's 171 colours,** whose CMYK the book gives:
  - every ink is within 5 points of the book's for 102 colours, and within 10 for 126;
  - printed back through the profile, the estimate is the colour itself: within ΔE2000 2.5, median 0.33;
  - the 16 furthest off, by more than 20 points on some ink, are dark colours. The same dark colour can be printed with more black or with more of the other three inks, and the book chose differently from the profile. Black, for example, is C 20 M 10 Y 15 K 100 in the book and C 85 M 83 Y 84 K 76 estimated.
- **What the press can't print:** 419 of the 2,896 cells are more vivid than Japan Color 2011 Coated allows; their estimate prints more than ΔE2000 3 away. Most are purples (121), ultramarines (94), sea greens (87) and leaf greens (83), towards the full colours. Their CMYK is the nearest colour the press can print, so for them the ≈ is looser.

## How the colours spread

- **Per level,** white to black: 2, 1, 6, 3, 8, 8, 8, 6, 3, 5, 4, 2, 9, 6, 10, 11, 7, 13, 7, 9, 10, 14, 2, 2, 3, 6, 2, 0, 3, 0, 1.
- **Per ring,** axis to full colour: 4, 8, 22, 13, 15, 17, 16, 9, 7, 15, 11, 7, 7, 10, 3, 7.
  - Most of the palette is muted: 104 colours lie in the inner half of the rings, and only 7 are full colours, all between yellow and red-orange, hues 1 to 19 (Yellow, Apricot Yellow, Orange Yellow, Yellow Orange, Orange, Jasper Red and Peach Red).
  - Only 4 are greys: White and Pale King's Blue - B (A), Warm Gray (E) and Black (P). The other near-greys keep a step of colour at this scale.
- **Cells:**
  - the 171 colours fill 157 cells;
  - 13 cells hold two or more;
  - the most in one cell is 3.
- **Letters:** all 16 are used. J, the letter Ostwald's scale lacks, is in 12 codes.

## Limits

- **One calibration point.** Orange fixes the hue's zero point. The spacing is OKLCH's, made symmetrical, not measured from Ostwald's own colours.
- **The steps can't be even everywhere.** Where sRGB's full colours crowd together in OKLCH and their complements spread out, a step is the mean of the two. So a sector spans from 5.6° of OKLCH hue, between yellow-green and yellow, to 24.4°, between violet and ultramarine (6.4° to 30.9° with even steps of the hexagonal hue).
- **The letters' values are inferred.** Wada gives the 16 letters and the two ends, not the values in between; even spacing on a log scale is Ostwald's rule, carried over.
- **Our values aren't his.** They come from the reprint's CMYK, converted to OKLCH (see the main README), not from his colour cards. Expect a step's difference here and there.
- **sRGB isn't Ostwald's full colour.**
  - His full colours were pigments, not sRGB's primaries, so the same colour measures differently against them.
  - Orange shows this: white 0.014 and black 0.127 here, against 0.0355 and 0.109.
  - 16 colours lie outside sRGB and are clipped before they are measured, by up to 0.105 (Peacock Blue, Benzol Green).
- **The 24 sectors and the letters are rounded.**
  - 58 colours are within 0.05 of a step from a neighbouring cell, and 80 within 0.1, so a small change in their values moves them. Values spread evenly across their cells would put about 38 and 71 there. That is 20 more within 0.05 and 9 more within 0.1; those within 0.05 are spread across white (14), black (21) and hue (23), so no one scale causes it.
  - Rounding our values to 8-bit sRGB alone moves 17 of them (one-off): 7 to another letter, 10 to another sector.
