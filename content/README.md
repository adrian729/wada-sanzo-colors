# The site's reading pages

The text of the three reading pages, the source of truth for them: [about.md](about.md) (Wada Sanzō), [guidance.md](guidance.md) (Guidance) and [theory.md](theory.md) (Colour theory). Edit the text here; index.html's About, Guidance and Colour theory sections are made from it.

## Conventions

Plain Markdown, except for what the pages show that Markdown can't:

- **A colour of Wada's:** its name in double brackets, `[[Spectrum Red]]`. On the page it's the name with its square after it, and opens the colour's dialog. The name must be one of colors.json's, exactly.
- **A section's id:** after its heading, `## Hama's advice {#hama}`, so `#guidance/hama` links to it. A page's contents list ("On this page") is made from its headings that have one.
- **A link to a page or section:** the site's address, `[his pairs](#guidance/pairs)`, `[022](#combination/22)`. A link to one of the Colors views is written `#colors/ostwald` (or `oklch`, `munsell`, `pccs`): it opens Colors on that view.
- **Notes on today's colour science:** a quote that starts with `**Today:**`.
- **Blocks:** `::: name` on a line, the block's text, then `:::`.
  - `::: aside`: a note set apart (Hama's part of Guidance).
  - `::: pairs`: a list of colour pairs, one pair per line.
  - `::: card season=1`: one of Wada's seasonal cards (its number in seasons.json), shown beside the text in the block.
- **Made on the page, not written here:** the lead (the first paragraph after the title), the contents list, and the marks that tell browsers which text is Japanese.

Lines aren't wrapped: one paragraph or list item per line.
