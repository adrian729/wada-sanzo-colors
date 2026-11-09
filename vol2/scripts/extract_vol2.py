"""Extract the 72 seasonal combinations (配色総鑑 B篇, NDL scans) and match them to Volume 1's colours.

python extract_vol2.py <cards dir> <ocr_en.jsonl> <corrections.json> <colors.json> <out.json>

Each card: a vertical strip, one large colour on top then N-1 equal smaller bands; the English name of
each colour to the right, in the same top-to-bottom order (labels are not always level with their band),
and the Japanese name (kana over kanji) to the left. Japanese names are not extracted: OCR cannot read
them reliably (widely spaced characters).

Names: OCR text, fixed by corrections.json (visually verified), then matched to colors.json by name.
Colours sampled from the scan (90-year-old paper chips, uncalibrated) only check matches; between
same-name colours (Grayish Lavender A/B, Eugenia Red A/B) the book decides (corrections.json "variant"),
except on a card that has both (card 16), where the scan does; without a "variant" (Pale King's Blue, Volume 1's
瓶覗 and Volume 2's 藍白), the scan decides too.
"""
import sys, json, re, difflib, math
from pathlib import Path
from PIL import Image

cards_dir, en_path, corrections_path, colors_path, out_path = sys.argv[1:6]
colors = json.load(open(colors_path))
fixes = json.load(open(corrections_path))


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def base(name):  # "Eugenia Red | A" -> "Eugenia Red"
    return re.sub(r"\s*[|\-]\s*[AB]$", "", name).strip()


by_base = {}
for i, c in enumerate(colors):
    by_base.setdefault(norm(base(c["name"])), []).append(i)


# --- colour maths: sRGB (scan) and OKLCH (our data) both to OKLab ---
def oklab(rgb):
    lin = [((v / 255 + 0.055) / 1.055) ** 2.4 if v / 255 > 0.04045 else v / 255 / 12.92 for v in rgb]
    r, g, b = lin
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklch_to_oklab(lch):
    L, C, h = lch
    return (L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h)))


def find_bands(img, n, keep=10):
    """Candidate layouts of the strip's n bands, best first, each a list of (y0, y1) fractions: one large
    band on top, then n-1 equal bands. Scored by how well the band edges line up with colour edges."""
    w, h = img.size
    x0, x1 = int(0.44 * w), int(0.50 * w)
    rows = []
    for y in range(h):
        px = sorted((img.getpixel((x, y)) for x in range(x0, x1)), key=sum)
        rows.append(oklab(px[len(px) // 2]))
    edge = [0.0] * h  # colour change across each row
    for y in range(3, h - 3):
        edge[y] = math.dist(rows[y - 3], rows[y + 3])
    # The card's printed frame line, below the strip, is a strong edge too: find it beside the strip
    # (the darkest thin line there) and only look for the strip's bottom above it.
    grey = [sum(sum(img.getpixel((x, y))) for x in range(int(0.12 * w), int(0.30 * w))) for y in range(h)]
    frame = max(range(int(0.85 * h), h - 7), key=lambda y: min(grey[y - 6], grey[y + 6]) - grey[y])
    scored = []
    for bottom in range(int(0.80 * h), frame - int(0.008 * h)):
        for step in range(int(0.03 * h), int(0.16 * h)):
            top = bottom - (n - 1) * step  # bottom of the large band
            if top < 0.35 * h:
                break
            scored.append((sum(max(edge[bottom - k * step - 2: bottom - k * step + 3]) for k in range(n)), bottom, step))
    scored.sort(reverse=True)
    layouts, seen = [], []
    for _, bottom, step in scored:
        if any(abs(bottom - b) < 0.01 * h and abs(step - st) < 0.01 * h for b, st in seen):
            continue  # nearly the same layout as a better one
        seen.append((bottom, step))
        top = bottom - (n - 1) * step
        layouts.append([(0.2, top / h - 0.02)] + [((top + k * step) / h, (top + (k + 1) * step) / h) for k in range(n - 1)])
        if len(layouts) == keep:
            break
    return layouts


def sample(img, y0, y1):
    w, h = img.size
    m = (y1 - y0) * 0.25  # the middle half of the band
    box = img.crop((int(0.40 * w), int((y0 + m) * h), int(0.54 * w), int((y1 - m) * h)))
    px = sorted(box.get_flattened_data() if hasattr(box, 'get_flattened_data') else box.getdata(), key=sum)
    mid = px[len(px) // 4: 3 * len(px) // 4] or px  # middle half by brightness: drops specks and shadows
    return tuple(round(sum(p[k] for p in mid) / len(mid)) for k in range(3))


ocr = {}
for line in open(en_path):
    o = json.loads(line)
    ocr[Path(o["file"]).name] = o.get("lines", [])

cards = []
for f in sorted(Path(cards_dir).glob("m*_r*.jpg")):
    if f.name.endswith("_r15.jpg"):  # the calibration chart
        continue
    month, page = int(f.name[1:3]), int(f.name[5:7])
    number = (month - 1) * 6 + (page - 1) // 2  # cards are pages 3, 5, ..., 13 of each month
    lines = [t for t in ocr.get(f.name, []) if t["x"] > 0.6 and 0.2 < t["y"] < 0.95
             and not re.search(r"No\.?\s*\d", t["text"]) and re.search(r"[A-Za-z]{3}", t["text"])]
    lines.sort(key=lambda t: (round(t["y"] / 0.01), t["x"]))
    names = []  # merge pieces of one name read as separate lines at the same height
    for t in lines:
        if names and abs(t["y"] - names[-1]["y"]) < 0.008:
            names[-1] = {**names[-1], "text": names[-1]["text"] + " " + t["text"], "conf": min(names[-1]["conf"], t["conf"])}
        else:
            names.append(dict(t))
    img = Image.open(f).convert("RGB")
    small = img.resize((img.width // 4, img.height // 4))
    printed_names = [fixes["ocr"].get(t["text"], t["text"]) for t in names]
    known = [by_base.get(norm(base(fixes["alias"].get(p, p))), []) for p in printed_names]

    # Of the best-scoring layouts, keep the one whose bands look most like the named colours.
    def mismatch(layout):
        ds = [min(math.dist(oklab(sample(small, y0, y1)), oklch_to_oklab(colors[i]["oklch"])) for i in cands)
              for (y0, y1), cands in zip(layout, known) if cands]
        return sum(ds) / len(ds) if ds else 0
    bands = min(find_bands(small, len(names)), key=mismatch)
    entries = []
    for t, printed, cands, (y0, y1) in zip(names, printed_names, known, bands):
        rgb = sample(img, y0, y1)
        lab = oklab(rgb)
        ranked = sorted(cands, key=lambda i: math.dist(lab, oklch_to_oklab(colors[i]["oklch"])))
        chosen = fixes.get("variant", {}).get(base(fixes["alias"].get(printed, printed)))
        if chosen and len(ranked) > 1 and printed_names.count(printed) == 1:  # both on one card: the scan decides
            ranked.sort(key=lambda i: colors[i]["name"] != chosen)  # stable: the book's variant first
        entry = {"printed": printed, "ocr": t["text"], "ocr_conf": round(t["conf"], 2),
                 "match": ranked[0] if ranked else None, "band": [round(y0, 3), round(y1, 3)], "scan_rgb": rgb}
        if len(ranked) > 1:
            entry["same_name"] = [colors[i]["name"] for i in ranked]
        if ranked:
            entry["scan_distance"] = round(math.dist(lab, oklch_to_oklab(colors[ranked[0]]["oklch"])), 3)
        else:
            close = difflib.get_close_matches(norm(printed), by_base, n=1, cutoff=0.8)
            if close:
                entry["closest_name"] = colors[by_base[close[0]][0]]["name"]
        entries.append(entry)
    cards.append({"number": number, "month": month, "file": f.name, "colors": entries})

json.dump(cards, open(out_path, "w"), ensure_ascii=False, indent=1)
print(f"{len(cards)} cards, {sum(len(c['colors']) for c in cards)} colour slots")
