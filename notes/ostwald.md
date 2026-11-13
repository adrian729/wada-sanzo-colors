# Wada's colours in Ostwald's system

Wada wrote colours in Ostwald's notation, and his colour-name books give every colour in it (see [guidelines.md](guidelines.md#reading-a-colour)). The NDL has scans of those books, but they aren't public, so the codes here are computed from our colour values, not taken from him. They follow the system as his 1935 supplement draws it, as closely as his own data allows, measured against what the press that printed his colours can print. The site's Colors › Ostwald view shows them. [ostwald.py](ostwald.py) prints every number below, except the one-off checks marked as such.

## The system, as Wada drew it

- **Mixing:** every colour is full colour, white and black, adding up to 1. Ostwald measured them on a spinning disc, so the mixture is additive.
- **Hue:** a circle of 100 steps:
  - yellow 0, orange 12.5, red 25, violet 37.5, ultramarine 50, ice blue 62.5, sea green 75, leaf green 87.5;
  - the view names them as Wada's Figure 1 does, his German translated literally: Gelb (yellow), Kress (cress, Ostwald's orange), Rot (red), Veil (violet), Ublau (ultramarine), Eisblau (ice blue), Seegrün (sea green), Laubgrün (leaf green). English books on Ostwald often say purple and turquoise instead. Wada's Japanese names under them are plainer: 黃, 橙, 赤, 紫, 靑紫, 靑, 綠, 黃綠;
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

- **Against the press:** Ostwald's full colours were the purest colours his pigments made, and Wada's colours were printed. So each colour is measured against what the press prints: Japan Color 2011 Coated, the profile that turns the book's CMYK into our values (see the main README), with its ink limit of 350%. `scripts/print_gamut.py` measures it once, into `print-gamut.json`. Nothing is clipped to a screen's colours.
- **Hue plane:** a colour's direction from the white in CIE xy (D65), its chromaticity angle. Complements, mixed additively, give grey, so they lie in opposite directions, as Ostwald's circle has them.
- **Full colour:** in each direction, the press's purest colour: two inks and no black, one of them at 100% and the third at 0 (magenta and yellow for an orange). `print-gamut.json` has it for every degree, and at each ink alone and each two at 100%, where the full colours turn a corner; between those, it is interpolated.
- **White, black and colour:** as on Ostwald's discs, a colour is white and its full colour mixed, then darkened with black.
  - Its share of full colour against white, r, comes from its purity, its distance from the white towards the full colour, weighted by the two's X + Y + Z, as an additive mixture of the two is.
  - Its black is how far it is below the press's tint edge: the brightest the press prints in that direction at that share (Y). black = 1 − Y / Ymax(r). A tint has none, and its shadow series, the same chromaticity darker, has more.
  - White is (1 − r)(1 − black), and colour r (1 − black).
  - The tint edge is why it fits: the press prints a light tint as separate dots of its inks on white paper, much brighter than its full colour mixed with white. Measured against that straight line instead, light tints come out with less than no black (see [Choices tested](#choices-tested-against-wadas-data)).
- **Hue number:** one scale decides which hue plane a colour is in, another how far apart the hues are.
  - The chromaticity angle gives the plane, with complements exactly opposite.
  - Ostwald also spaced his circle evenly to the eye. The full colour's OKLCH hue is even to the eye, but the press's full colours aren't symmetrical in it: a full colour and its complement are up to 37° from opposite. So the number is the mean of the two, the complement's turned half round, and complements stay exactly 50 steps apart.
  - His circle runs the other way round from OKLCH's, at 25 steps per 90°.
- **Calibration:** the hue is turned so that Wada's Orange is 16, which puts hue 0 (yellow) at a mean OKLCH hue of 95.4°. Only this zero point is fitted.
- **Letters:** white content, and 1 minus black, each go to the nearest of the 16 greys on the log scale. When both land on the same grey, the colour is that grey.
- **Code:** the hue rounded to a whole step, then the two letters, e.g. 16PA. Greys get one letter.
- **A cell's own colour:** the same, backwards. Its white is its first letter's grey and its black 1 minus its second's, at the chromaticity angle of its sector's hue number: its share of full colour gives its purity, and it lies as far below the tint edge as its black says. A grey is its letter's share of the white. Every cell is something the press prints (see [CMYK for the empty cells](#cmyk-for-the-empty-cells)).

## Choices tested against Wada's data

- **Measuring against sRGB (the placement here until November 2026; tested, not used):** sRGB's own full colours: white the smallest of a colour's linear RGB channels, black 1 minus the largest, and the hue from the hexagonal (HSV) hue.
  - Its solid is exactly Ostwald's shape, at each hue the triangle of white, black and full colour, but its full colours are a screen's, not print's. Plate 8's full colours came out far from the rim: 3 of the 12 PA, Violet Ultramarine 43PG, Blue 54PD; and in 7 of the 12 hues the tint had more colour than the full colour (see [Checks](#checks)).
  - 16 of Wada's colours lie outside sRGB and were clipped before they were measured, by up to 0.105 (Peacock Blue, Benzol Green).
  - Measuring against the press changes 126 of the 171 codes, mostly in the letters (106 codes). The hue numbers move little: 0.52 steps on average, 20 by more than a step and 2 by more than two, at most 2.25.
- **Measuring against Rec. 2020 (tested, not used):** the widest standard screen gamut, which holds all of Wada's colours and everything the press prints. Its full colours are far purer than print's, so none of Plate 8's 12 full colours comes out PA, and no colour reaches the outer 3 rings.
- **The press's full colours in sRGB's shape (tested, not used; one-off, November 2026):** the step before this model, prompted by Plate 8. Each hue's full colour was the press's, as here, but white, black and colour were read off the triangle of white, black and that full colour, as with sRGB.
  - It fixed Plate 8's full colours: 6 of the 12 PA, against 3.
  - It put 26 colours outside the triangle, with less than no black: 12 by 0.07 to 0.57, mostly light violets, blues and blue-greens. Grayish Lavender - A came out at −0.57 black, and Blue Violet had 1.21 colour content.
  - Why: the press's light tints are much brighter than its full colour mixed with white. Measuring black against the press's own tint edge, as here, fixes it: 16 colours fall beyond what the press prints at all, and only by a hair (see [Limits](#limits)).
- **Even steps of the chromaticity angle (tested, not used):** 3.6° per step, calibrated on Orange in the same way.
  - Its steps aren't even to the eye: a sector spans from 7.0° to 43.4° of OKLCH hue, against 8.1° to 21.9° here.
  - Wada's Yellow comes out 6.1 and his Red 24.1, against 0.8 and 23.8 here.
  - His complementary pairs: 5 of the 10 within 3 steps either way, 3.8 steps off on average, against 3.6 here. The pairs are the same additive complements on both scales; only the count of steps between them differs.
- **Hue from wavelength (tested, not used):** Wada's Figure 3 (p. 11) sets his 100-step circle against the wavelengths of the spectrum.
  - Read off the scan (one-off, November 2026; its hue scale is regular to about 0.15 steps): 420 nm 45.0, 430 nm 48.0, 440 nm 50.0, 450 nm 51.9, 460 nm 53.1, 470 nm 55.8, 480 nm 62.1, 490 nm 77.9, 500 nm 82.9, 510 nm 85.2, 520 nm 86.9, 530 nm 87.9, 540 nm 88.8, 550 nm 90.9, 560 nm 93.2, 570 nm 98.6, 580 nm 6.0, 590 nm 12.0, 600 nm 14.1, 610 nm 16.0, 620 nm 17.8, 630 nm 19.1, 640 nm 20.8, 650 nm 22.2, 660 nm 23.8, and 25.0 at the red end of the spectrum. The purples, 25 to 45, have no wavelength.
  - The test (one-off, November 2026): take each colour's dominant wavelength (CIE 1931, D65 white; for a purple, the complementary wavelength, 50 steps round) and read its hue off that scale.
  - Orange comes out 12.3, not 16.
  - Wada's complementary pairs (p. 22) come out 8.5 steps from opposite on average, and none within 3. The scale here puts 5 of the 10 within 3, and 3.6 steps off on average (see below).
  - On p. 22, Wada notes that the true complement of Red Orange is a colour "a little greener" (今少シ緑ガカツタモノ) than his Green Blue. Here it lands 10 steps bluer; with the scale here, 3.0 steps greener.
  - Illuminant C, a daylight white of the 1930s, gives much the same: Orange 12.2, the pairs 9.1 steps off.
  - Its spacing fits the scale here and even steps of the angle equally: over the 150 colours three or more rings from the axis, each scale's hue minus the figure's spreads by 4.4 steps (standard deviation).
  - So the figure doesn't describe his chips as our values measure them, and the hue here stays additive.
- **Measuring against paper white (tested, not used; one-off, November 2026):** his white reflects about 90%, so the paper, our white, could stand for Ostwald's a (0.891), every colour's Y scaled by 0.891.
  - Orange still comes out 16PA, now with black 0.109, A's own value.
  - But it changes 102 of the codes, and fewer of Plate 8's tints come out with no black: 7 of the 12, against 10. So the values are measured as they are.

## The view

- **The disc:** one level of the solid, seen from above.
  - Angle is hue, in Wada's 24 sectors, with yellow at the top and red at the right.
  - Distance from the centre is colour content, in his steps.
- **Levels:**
  - The level is the sum of the two letters' positions: 0 is white, 30 black.
  - The ring is their difference: 0 is the axis, 15 the full colour.
  - Even levels have a grey at the centre. Odd levels fall between two greys, and level 15, between H and I, has the full colours at its rim.
  - Levels shrink towards the tips, as the cone does.
- **Cells:** each of Wada's colours fills the cell of its code, so it stands for a range of white and black. The info panel gives its exact values. Colours sharing a cell split it in hue order. An empty cell shows a dot of the system's own colour there (see [Placing](#placing-wadas-colours)). Hovering it gives that colour's code and values; clicking or tapping it opens its card, as a colour's, with the same values, its white and black content, and its CSS colour to copy; it has no name, so the panel calls it "Ostwald" and its code, e.g. Ostwald 67JG, and gives the code as exact (Ostwald = 67JG) where Wada's colours have an approximate one (Ostwald ≈ 16PA). Its CMYK is estimated, so it has ≈ too (see [CMYK for the empty cells](#cmyk-for-the-empty-cells)). Picked in Create, it is saved as its OKLCH values, like any new colour, and named by its code again when read back.
- **The control:** the 16 greys and the cone's outline, with the current slice. The cone runs from the middle of A to the middle of P, as the levels do. The slice's ellipse holds its level's disc, in the system's own colours, seen from the front with yellow at the back and red on the right, as on the disc. The axis goes behind the disc's near half, so that it reads as passing through it. Drag, click, scroll, or use the arrow keys (Page Up and Down move a whole grey). Hovering over it previews a level on the disc without choosing it; a dashed slice, with its own disc, marks the level previewed.
- **The cells switch:** a second switch, beside the 2D/3D one, shows every cell as a dot, or shows the empty cells as cells with a dot (the default), as the dots alone, filled with the system's own colour, so the disc or solid is complete, or hidden, leaving only Wada's colours. Its first choice is drawn as a dot with smaller ones where a cell's corners would be; the other four are diamonds, a cell drawn each way, dashed where the cell isn't drawn. Their tooltips, or a label on touch screens, say which is which. It works in both views, and the page remembers the choice. With the dots alone, hovering a dot still outlines its cell on the disc.
- **Every cell a dot:** Wada's colours become dots too, so the view is a lattice of the system's colours with his standing out. His dots are 1.6 times the empty cells' dots, as far as they fit in their cell. Where the cells narrow, they come out smaller: 1.42 to 1.48 times within five rings of the disc's centre, and 1.45 times within two rings of the pole in 3D.
  - Colours sharing a cell (15 cells: 13 pairs and two of three) are all one size, as big as fits in the cell. On the disc they sit in a row round the circle in hue order, or in a row along the radius, or, for the threes, in two rows, one dot inside and two outside: whichever gives the biggest dots. Along the radius each sits as far out as it would in the solid: the less white for its colour, the further out. The pages and the 3D view set them side by side the same way, out from the axis; greys sharing a cell go one above another, the lightest at the top (White above Pale King's Blue - B, in A).
  - The shared dots come out between an empty cell's dot and a lone colour's, or as big as a lone colour's where the cells are big: on the disc, 1.09 to 1.48 times an empty dot in 10 of the 15 cells, where the cells are shallow for their dots (1.09 for the two greys in A), and full size in the other 5; on the pages, full size, but 1.26 times for the threes and 1.35 for the two greys in A; in 3D, full size, but 1.28 times for the pair near the pole, 1.32 for the two greys on it in A, and 1.24 times for the threes.
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
  - Faces keep their exact colour, with no lighting; only the pages' edges are shaded. The canvas holds any colour (16-bit floating point where the browser has it, else Display P3, else sRGB), so the screen shows each colour as it shows the page's other colours, clipping only what it can't show itself.
  - Drag, or use the arrow keys, to turn it. Hovering and clicking work as on the disc.
  - Round the solid, each of the 24 pages has a button that hides or shows it, to see inside: the hue's name where it has one, a dot of its full colour for the other 16. A hidden page's name is struck through, and its dot hollow. The names show through the solid, faint; a dot hides behind it (behind its outline, less what the cut hides).

## Checks

- **Orange comes out as 16PA.** Wada printed it with magenta and yellow alone (C 0 M 68 Y 100 K 0), so it is the press's own full colour: white 0 and black 0, against the letters' 0.0355 and 0.109. The letters weren't fitted, so this match doesn't follow from the calibration, but any of the press's full colours would come out PA.
- **Yellow and Red come out near Ostwald's.** Only Orange is fitted, but Wada's Yellow comes out 0.8 (1PA) and his Red 23.8 (24PD), by Ostwald's yellow (0) and red (25), and his Sea Green 75.4 (75KA), by sea green (75).
- **Wada's complementary pairs (1935, p. 22)** should be 50 steps apart. Their hue numbers here, and how far each pair is from that:
  - Spectrum Red 21.4 and Sea Green 75.4: off by 4.0;
  - Red Orange 19.8 and Green Blue 66.8: off by 3.1;
  - Orange 16.0 and Peacock Blue 66.1: off by 0.1;
  - Yellow Orange 11.1 and Antwerp Blue 61.1: off by 0.1;
  - Apricot Yellow 3.2 and Blue 55.1: off by 1.9;
  - Yellow 0.8 and Deep Lyons Blue 52.4: off by 1.5;
  - Lemon Yellow 99.7 and Violet Ultramarine 42.8: off by 6.9;
  - Light Green Yellow 96.1 and Violet 45.1: off by 1.0;
  - Yellow Green 91.8 and Red Violet 38.0: off by 3.8;
  - Night Green 90.3 and Rosolane Purple 27.2: off by 13.1.
- **5 of the 10 pairs are within 3 steps,** and they are 3.6 steps off on average. With each colour's own OKLCH hue, whose opposite hues aren't additive complements, only 2 are; with the wavelength scale of Figure 3, none.
- **Night Green and Rosolane Purple don't fit:** they are 13.1 steps off, about an eighth of the circle.
- **Plate 8 of the 1935 atlas** (Hama and Wada, with the names of Wada's books; `atlas` in `colors.json`, see the main README): 12 hues, each as a tint, a full colour "as saturated as possible" and a shade, all 36 our colours. The purple-blue shade, Coolie Blue (花色) on the plate, has no colour of that name. It is matched to Violet Blue (50PF), which Wada's own chips call 花色: it has the other shades' make-up (black 0.35 to 0.76, little white) and lies between the blue and purple shades, while the other bluish violets are lighter than the full colour (Dull Blue Violet, 43KB), have no black (Blue Violet, 44OA) or have too little (Dark Soft Violet, 47MB).
  - Yellow to orange fit: 2DA, 1PA, 1PE for yellow; 9IA, 11PA, 12PC for orange-yellow; 11HB, 16PA, 16KD for orange.
  - 5 of the 12 full colours come out PA: Yellow, Yellow Orange, Orange, Violet Ultramarine (43PA) and Blue (55PA). They are the ones the book prints as the press's full colours: no black, one ink at or near 100% and the third at 0. The other 7 have some of the third ink or black (Red, C 30 M 100 Y 70 K 10, is 24PD; Green 82KB; Violet 45PB), or no ink at full strength (Yellow Green, C 35 Y 72, is 92IA).
  - 10 of the 12 tints have no black (second letter A), as a tint should; orange's and blue's have a step of it (11HB, 55FB). In 5 of the 12 hues the tint has more colour content than the full colour.
  - Hue is a looser check: the three come within 4 steps of each other in 4 of the 12 hues, and up to 10.3 apart (purple). The commentary itself says the tints and shades were averaged into one step each, so names and colours don't always fit.
  - The plate puts violet (紫) before purple-blue (紫靑), while here Violet comes out 45.1 and Violet Ultramarine 42.8. That order is in the book's CMYK (C 85 M 90 Y 18 against C 85 M 100), not in the placement.
- **Perceptual check:** for each colour, the nearest of the system's cell colours in OKLab:
  - is its own cell for 96 colours, and a neighbouring cell for 60;
  - is a cell further off for 15, but closer than its own by at most 0.037;
  - is at a median distance of 0.019 from the colour's own cell colour, and at most 0.095.
- **The page and ostwald.py (one-off check, November 2026):** the page's own code, lifted out of `index.html` and run on the same data, gives every colour the same code, hue number, white and black (to within 10⁻¹³), and every one of the 2,896 cells the same OKLCH values.
- **The drawing (one-off checks, read from the page):**
  - each colour is drawn once, at its level, with its own code (all 171, level by level, November 2026);
  - every point of its outline lies inside its own cell, and points sampled across all 2,896 cells are covered by exactly that cell's colours, one each (checked on the earlier, sRGB placement; the drawing is the same);
  - with every cell a dot, each of Wada's dots lies in its own piece of its cell and no other, and no two dots overlap, at every level and at all 24 positions of the pages (November 2026).

## CMYK for the empty cells

- **How:** the cell's colour goes to CIE Lab, then to CMYK through the colorimetric table (B2A1) of the Japan Color 2011 Coated profile. That is the inverse of the table that turns the book's CMYK into our values (`scripts/cmyk_to_oklch.py`). The profile also decides how much black stands in for cyan, magenta and yellow.
- **Where it comes from:** `scripts/ostwald_cmyk.py` writes the estimates to `ostwald-cmyk.json` and prints the checks below. The page ignores the file if it was made for another calibration, so re-run the script after changing `colors.json` or `print-gamut.json`.
- **Tested on Wada's 171 colours,** whose CMYK the book gives:
  - every ink is within 5 points of the book's for 102 colours, and within 10 for 126;
  - printed back through the profile, the estimate is the colour itself: within ΔE2000 2.5, median 0.33;
  - the 16 furthest off, by more than 20 points on some ink, are dark colours. The same dark colour can be printed with more black or with more of the other three inks, and the book chose differently from the profile. Black, for example, is C 20 M 10 Y 15 K 100 in the book and C 85 M 83 Y 84 K 76 estimated.
- **Every cell prints:** the cells are measured against the press, so each estimate, printed back through the profile, is the cell's own colour: within ΔE2000 1.6, median 0.30, none more than 3 away. (Measured against sRGB, 419 of the 2,896 cells were more vivid than the press allows.)

## How the colours spread

- **Per level,** white to black: 2, 1, 6, 5, 5, 9, 11, 4, 5, 4, 8, 7, 3, 8, 11, 16, 13, 9, 11, 3, 11, 7, 2, 3, 0, 3, 1, 2, 0, 0, 1.
- **Per ring,** axis to full colour: 3, 4, 14, 13, 13, 15, 14, 9, 8, 10, 18, 9, 11, 9, 9, 12.
  - Half the palette is muted: 85 colours lie in the inner half of the rings.
  - 12 are full colours: Yellow, Apricot Yellow, Orange Yellow, Yellow Orange, Orange, Jasper Red, Peach Red, Red Orange and Spectrum Red, hues 1 to 21; Violet Ultramarine (43), Blue (55) and Night Green (90).
  - Only 3 are greys: White and Pale King's Blue - B (A), and Black (P). The other near-greys keep a step of colour at this scale (Warm Gray is 94ED).
- **Cells:**
  - the 171 colours fill 154 cells;
  - 15 cells hold two or more;
  - the most in one cell is 3.
- **Letters:** all 16 are used. J, the letter Ostwald's scale lacks, is in 8 codes.

## Limits

- **One calibration point.** Orange fixes the hue's zero point. The spacing is OKLCH's, made symmetrical, not measured from Ostwald's own colours.
- **The steps can't be even everywhere.** Where the press's full colours crowd together in OKLCH and their complements spread out, a step is the mean of the two. So a sector spans from 8.1° of OKLCH hue, between yellow-green and yellow, to 21.9°, between violet and ultramarine (7.0° to 43.4° with even steps of the chromaticity angle).
- **The letters' values are inferred.** Wada gives the 16 letters and the two ends, not the values in between; even spacing on a log scale is Ostwald's rule, carried over.
- **Our values aren't his.** They come from the reprint's CMYK, converted to OKLCH (see the main README), not from his colour cards. Expect a step's difference here and there.
- **The press isn't Ostwald's full colour.**
  - His full colours were pigments, not a modern press's inks. The press is the closest stand-in, since Wada's colours were printed, but it is the reprint's (Japan Color 2011), not his.
  - Orange shows this: white 0 and black 0 here, against the 0.0355 and 0.109 of its letters, as his white holds about 10% black (p. 6).
  - Plate 8's full colours that the book prints with a third ink or black come out short of the rim (see [Checks](#checks)).
- **Beyond the press, by a hair.** 16 colours come out just beyond what the press prints, and are measured at its edge: 15 a little brighter than its tint edge, by at most 0.0011 of black (Grayish Lavender - A), and 2 a little purer than its full colour, by under 0.0001 of share (Apricot Yellow, and Orange, which is both). Such amounts are the measurement's own precision: with the tint edge stored in steps of 1/256 of share instead of 1/32, the most is halved, to 0.0005 (one-off, November 2026).
- **The 24 sectors and the letters are rounded.** 44 colours are within 0.05 of a step from a neighbouring cell, and 73 within 0.1, so a small change in their values moves them. Values spread evenly across their cells would put about 37 and 68 there. Those within 0.05 are spread across white (16), black (13) and hue (15), so no one scale causes it.
