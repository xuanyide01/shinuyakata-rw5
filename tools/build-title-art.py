"""Render the title menu wordmarks as PNG using the game's embedded font (Cedar, thin strokes).

Vela cannot synthesise bold for a bundled TTF and its text metrics differ from the PC
renderer, so the labels are rasterised once at build time with a hairline stroke and a
soft shadow, matching the original 222x46 title buttons.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = Path(r'D:\codex\移植项目\shinuyakata-rw5\源码')
FONT = R.parent / '可调用资源/files/data/sysscn/MTLc3m.ttf'
OUT = R / 'src/common/ui2'
OUT.mkdir(parents=True, exist_ok=True)

ITEMS = [('start', 'NEW GAME'), ('load', 'LOAD GAME'), ('gallery', 'GALLERY'),
         ('settings', 'CONFIG'), ('end', 'END GAME')]

SIZE = 44
W, H = 260, 52
for key, text in ITEMS:
    font = ImageFont.truetype(str(FONT), SIZE)
    probe = Image.new('L', (W, H))
    box = ImageDraw.Draw(probe).textbbox((0, 0), text, font=font, stroke_width=1)
    th = box[3] - box[1]

    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((8 - box[0] + 1, (H - th) / 2 - box[1] + 2), text, font=font,
                                fill=(0, 0, 0, 160), stroke_width=1, stroke_fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.6))

    core = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(core).text((8 - box[0], (H - th) / 2 - box[1]), text, font=font,
                              fill=(242, 247, 252, 255), stroke_width=1, stroke_fill=(242, 247, 252, 255))

    out = Image.alpha_composite(shadow, core)
    path = OUT / f'title-{key}.png'
    out.save(path, 'PNG', optimize=True)
    print(f'{path.name}\t{W}x{H}\t{path.stat().st_size} B')
print('wordmarks done')
