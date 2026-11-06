"""Review sheets: each card's scan beside the extracted names and the matched Volume 1 colours.

python review.py <cards dir> <extracted.json> <colors.json> <font.ttf> <out prefix>

Each tile: the card (strip + printed names), then for each band, at its height, a chip of the matched
colour from our data and its name; in red when OCR needed a correction, the card's name differs from
ours (renamed), or the name is shared by two colours (A/B), and "new" when it is not among our colours.
"""
import sys, json, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

cards_dir, extracted_path, colors_path, font_path, prefix = sys.argv[1:6]
cards = json.load(open(extracted_path))
colors = json.load(open(colors_path))
font = ImageFont.truetype(font_path, 15)
small = ImageFont.truetype(font_path, 13)


def oklch_to_srgb(lch):
    L, C, h = lch
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
           -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
           -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
    enc = lambda v: 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return tuple(round(255 * min(max(enc(max(v, 0)), 0), 1)) for v in rgb)


Y0, Y1 = 0.10, 0.93  # card crop, vertically
TW, TH = 330, 520  # card part of a tile
INFO = 300  # chips + names column
for start in range(0, len(cards), 12):
    batch = cards[start:start + 12]
    sheet = Image.new("RGB", (4 * (TW + INFO + 10), 3 * (TH + 40)), "white")
    d = ImageDraw.Draw(sheet)
    for k, card in enumerate(batch):
        img = Image.open(Path(cards_dir) / card["file"]).convert("RGB")
        W, H = img.size
        crop = img.crop((int(0.08 * W), int(Y0 * H), int(0.98 * W), int(Y1 * H))).resize((TW, TH))
        ox, oy = (k % 4) * (TW + INFO + 10), (k // 4) * (TH + 40)
        sheet.paste(crop, (ox, oy + 30))
        d.text((ox, oy + 6), f"{card['file']}  month {card['month']}  No.{card['number']}", fill="black", font=font)
        for e in card["colors"]:
            y = oy + 30 + ((e["band"][0] + e["band"][1]) / 2 - Y0) / (Y1 - Y0) * TH
            d.line((ox + int(0.54 / 0.9 * TW) - 30, y, ox + TW + 2, y), fill=(255, 0, 255), width=2)
            if e["match"] is not None:
                c = colors[e["match"]]
                d.rectangle((ox + TW + 4, y - 9, ox + TW + 40, y + 9), fill=oklch_to_srgb(c["oklch"]))
                letters = lambda t: re.sub(r"[^a-z]", "", re.sub(r"\s*[|\-]\s*[AB]$", "", t).lower())
                bad = e["ocr"] != e["printed"] or "same_name" in e or letters(c["name"]) != letters(e["printed"])
                d.text((ox + TW + 46, y - 8), c["name"], fill="red" if bad else "black", font=small)
            else:
                d.text((ox + TW + 46, y - 8), f"new: {e['printed']}", fill="blue", font=small)
    out = f"{prefix}{start // 12 + 1}.jpg"
    sheet.save(out, quality=88)
    print(out, sheet.size)
