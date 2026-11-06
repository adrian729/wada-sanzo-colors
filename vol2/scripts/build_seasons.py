"""Write the site's seasons.json: the 72 seasonal combinations, each a list of colour indices into colors.json.

python build_seasons.py <extracted.json> <colors.json> <out seasons.json>

Combination n (1-72) is entry n-1; months are six combinations each (1-6 January, ...). Colours in
the book's order, top to bottom. Every colour must be matched (run extract_vol2.py after adding new
colours to colors.json).
"""
import sys, json

extracted_path, colors_path, out_path = sys.argv[1:4]
cards = sorted(json.load(open(extracted_path)), key=lambda c: c["number"])
colors = json.load(open(colors_path))
assert [c["number"] for c in cards] == list(range(1, 73)), "expected cards 1-72"
seasons = []
for card in cards:
    ids = [e["match"] for e in card["colors"]]
    missing = [e["printed"] for e in card["colors"] if e["match"] is None]
    assert not missing, f"card {card['number']}: no colour for {missing}"
    assert len(set(ids)) == len(ids), f"card {card['number']}: a colour twice"
    seasons.append(ids)
with open(out_path, "w") as f:
    f.write("[\n" + ",\n".join("  " + json.dumps(ids) for ids in seasons) + "\n]\n")
print(f"{len(seasons)} combinations, {sum(map(len, seasons))} colours -> {out_path}")
