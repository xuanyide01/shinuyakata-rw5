"""Generate the watch UI skin: cold steel-blue plates in the style of the PC original.

All shapes are drawn at 4x and downsampled with LANCZOS so edges stay clean.
Output: src/common/ui2/*.png (RGBA) in 432x514 design pixels.
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码\src\common\ui2')
OUT.mkdir(parents=True, exist_ok=True)
S = 4

A = (10, 20, 32, 255)        # base A #0a1420
B = (13, 27, 42, 255)        # base B #0d1b2a
INNER = (44, 66, 87, 255)    # #2c4257
MAIN = (119, 155, 188, 255)  # #779bbc
HI = (207, 224, 240, 255)    # #cfe0f0
BTN_TOP = (143, 134, 168, 255)
BTN_BOT = (106, 98, 128, 255)
BTN_EDGE = (232, 230, 240, 255)
BTN_TOP_D = (92, 84, 112, 255)
BTN_BOT_D = (63, 58, 82, 255)
BTN_EDGE_D = (169, 194, 218, 255)
GOLD = (216, 180, 106, 255)
GOLD_HI = (242, 230, 200, 255)


def canvas(w, h):
    return Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))


def vgradient(size, top, bottom):
    w, h = size
    img = Image.new('RGBA', (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        row = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(4))
        for x in range(w):
            px[x, y] = row
    return img


def rounded_mask(size, radius, radius_px=None):
    w, h = size
    mask = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    return mask


def save(img, name, w, h):
    img = img.resize((w, h), Image.LANCZOS)
    path = OUT / name
    img.save(path, 'PNG', optimize=True)
    print(f'{name}\t{w}x{h}\t{path.stat().st_size} B\t{img.mode}')
    return path


# 1) dialogue plate
w, h = 432, 228
img = canvas(w, h)
plate = vgradient((w * S, h * S), A, B)
mask = Image.new('L', (w * S, h * S), 0)
ImageDraw.Draw(mask).rectangle([0, 0, w * S - 1, h * S - 1], fill=255)
img.paste(plate, (0, 0), mask)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w * S - 1, 2 * S], fill=MAIN)
d.rectangle([2 * S, 2 * S, w * S - 2 * S - 1, h * S - 2 * S - 1], outline=INNER, width=S)
save(img, 'box.png', w, h)

# 2) name bar underline
w, h = 432, 42
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rectangle([22 * S, 34 * S, (22 + 120) * S, 36 * S - 1], fill=MAIN)
save(img, 'namebar.png', w, h)

# 3) menu panel with corner brackets
w, h = 396, 470
img = canvas(w, h)
panel = vgradient((w * S, h * S), A, B)
img.paste(panel, (0, 0))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w * S - 1, h * S - 1], outline=MAIN, width=S)
d.rectangle([4 * S, 4 * S, w * S - 4 * S - 1, h * S - 4 * S - 1], outline=INNER, width=S)
arm = 12 * S
for (cx, cy, dx, dy) in ((0, 0, 1, 1), (w * S - 1, 0, -1, 1), (0, h * S - 1, 1, -1), (w * S - 1, h * S - 1, -1, -1)):
    d.line([cx, cy, cx + dx * arm, cy], fill=HI, width=2 * S)
    d.line([cx, cy, cx, cy + dy * arm], fill=HI, width=2 * S)
save(img, 'panel.png', w, h)


def button(w, h, top, bottom, edge, radius, highlight):
    img = canvas(w, h)
    grad = vgradient((w * S, h * S), top, bottom)
    mask = rounded_mask((w * S, h * S), radius * S)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([S, S, w * S - S - 1, h * S - S - 1], radius=radius * S,
                        outline=edge, width=2 * S)
    if highlight:
        d.line([3 * S, 3 * S, w * S - 3 * S, 3 * S], fill=HI[:3] + (100,), width=S)
    return img


save(button(380, 52, BTN_TOP, BTN_BOT, BTN_EDGE, 4, True), 'btn.png', 380, 52)
save(button(380, 52, BTN_TOP_D, BTN_BOT_D, BTN_EDGE_D, 4, False), 'btn_press.png', 380, 52)
save(button(118, 46, BTN_TOP, BTN_BOT, BTN_EDGE, 3, True), 'btn_small.png', 118, 46)
save(button(118, 46, BTN_TOP_D, BTN_BOT_D, BTN_EDGE_D, 3, False), 'btn_small_press.png', 118, 46)

# 7) divider with gold diamond
w, h = 260, 16
img = canvas(w, h)
d = ImageDraw.Draw(img)
mid = h * S // 2
for x0 in range(0, w * S):
    t = abs(x0 - w * S / 2) / (w * S / 2)
    alpha = max(0, int(200 * (1 - t)))
    d.point((x0, mid), fill=MAIN[:3] + (alpha,))
cx, cy = w * S // 2, mid
r = 3 * S
d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=GOLD, outline=GOLD_HI)
save(img, 'divider.png', w, h)

# 8) cursor diamond
w = h = 14
img = canvas(w, h)
d = ImageDraw.Draw(img)
c = w * S // 2
r = 5 * S
d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=GOLD, outline=GOLD_HI)
save(img, 'cursor.png', w, h)

# 9) save slot plate
w, h = 400, 64
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w * S - 1, S - 1], fill=INNER)
d.rectangle([0, 12 * S, 3 * S - 1, 52 * S], fill=MAIN)
save(img, 'slot_plate.png', w, h)

# 10) chapter plate
w, h = 400, 64
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w * S - 1, S - 1], fill=INNER)
d.rectangle([0, 12 * S, 3 * S - 1, 52 * S], fill=GOLD)
d.line([w * S - 18 * S, 0, w * S - 1, 0], fill=MAIN, width=2 * S)
d.line([w * S - 1, 0, w * S - 1, 18 * S], fill=MAIN, width=2 * S)
save(img, 'chapter_plate.png', w, h)

# 11) full-screen menu plate
w, h = 432, 514
img = canvas(w, h)
img.paste(vgradient((w * S, h * S), A, B), (0, 0))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w * S - 1, h * S - 1], outline=MAIN, width=2 * S)
d.rectangle([6 * S, 6 * S, w * S - 6 * S - 1, h * S - 6 * S - 1], outline=INNER, width=S)
save(img, 'panel_full.png', w, h)

# 12) gallery card plate 176x150
w, h = 176, 150
img = canvas(w, h)
img.paste(vgradient((w * S, h * S), A, B), (0, 0))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w * S - 1, h * S - 1], outline=MAIN, width=S)
save(img, 'card_plate.png', w, h)

print('done')
