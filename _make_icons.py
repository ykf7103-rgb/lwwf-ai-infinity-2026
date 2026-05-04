"""
Generate 4 missing subject icons (科學 / 音樂 / 體育 / 視藝)
using PIL only — no external dependencies.

Style matches existing Gemini icons:
- 1024x1024 square
- soft warm cream paper background (#fff8f0) with subtle noise
- rounded inner panel
- centered minimalist geometric subject element
- accent colour radial glow (blur)
- soft drop shadow
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024
BG = (255, 248, 240, 255)         # cream
PANEL = (255, 252, 245, 255)      # inner panel
INK = (61, 58, 53, 255)           # ink-2
INK_SOFT = (107, 103, 95, 255)    # ink-3

# Subject palettes (matches CSS vars in HTML)
PALETTES = {
    "science":  {"main": (4, 120, 87),    "soft": (52, 211, 153),  "label": "emerald"},
    "music":    {"main": (234, 88, 12),   "soft": (251, 146, 60),  "label": "orange"},
    "pe":       {"main": (109, 40, 217),  "soft": (167, 139, 250), "label": "violet"},
    "va":       {"main": (204, 120, 92),  "soft": (244, 178, 138), "label": "coral"},
}

def add_noise(img, strength=6):
    """Add subtle paper noise."""
    px = img.load()
    w, h = img.size
    rng = random.Random(42)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            n = rng.randint(-strength, strength)
            px[x, y] = (max(0, min(255, r + n)),
                        max(0, min(255, g + n)),
                        max(0, min(255, b + n)), a)
    return img

def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def make_glow(size, colour, intensity=140, blur=120):
    """Radial glow as soft blob behind shape."""
    g = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    cx, cy = size[0] // 2, size[1] // 2
    r = min(size) // 2 - 60
    gd.ellipse((cx - r, cy - r, cx + r, cy + r),
               fill=(*colour, intensity))
    g = g.filter(ImageFilter.GaussianBlur(blur))
    return g

def base_canvas():
    """Cream paper canvas with subtle texture + rounded inner panel."""
    img = Image.new("RGBA", (SIZE, SIZE), BG)
    img = add_noise(img, strength=4)

    # rounded inner panel slightly inset
    panel = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    inset = 28
    rounded_rect(pd, (inset, inset, SIZE - inset, SIZE - inset),
                 radius=120, fill=PANEL, outline=None)

    # add a faint warm overlay + edge shadow
    edge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    rounded_rect(ed, (inset, inset, SIZE - inset, SIZE - inset),
                 radius=120, outline=(180, 140, 100, 35), width=2)

    img = Image.alpha_composite(img, panel)
    img = Image.alpha_composite(img, edge)
    return img

def soft_shadow(shape_img, offset=(6, 14), blur=18, alpha=80):
    """Drop-shadow generator from an alpha shape."""
    shadow = Image.new("RGBA", shape_img.size, (0, 0, 0, 0))
    s_alpha = shape_img.split()[-1].point(lambda v: min(alpha, v))
    shadow.putalpha(s_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas = Image.new("RGBA", shape_img.size, (0, 0, 0, 0))
    canvas.paste(shadow, offset, shadow)
    return canvas

# ---------- Subject illustrations ----------

def draw_science(canvas, palette):
    """Stylised leaf with DNA-helix dots."""
    img = canvas.copy()
    glow = make_glow((SIZE, SIZE), palette["soft"], intensity=120, blur=140)
    img = Image.alpha_composite(img, glow)

    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = SIZE // 2, SIZE // 2
    # leaf: rotated ellipse
    leaf = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leaf)
    leaf_w, leaf_h = 360, 580
    box = (cx - leaf_w // 2, cy - leaf_h // 2,
           cx + leaf_w // 2, cy + leaf_h // 2)
    ld.ellipse(box, fill=(*palette["main"], 235))
    # rotate 25 deg
    leaf = leaf.rotate(-22, resample=Image.BICUBIC, center=(cx, cy))

    # leaf vein (lighter line down centre, also rotated)
    vein = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vein)
    vd.line([(cx, cy - 240), (cx, cy + 240)], fill=(255, 255, 255, 200), width=10)
    # side veins
    for dy in (-160, -60, 40, 140):
        vd.line([(cx, cy + dy), (cx + 110, cy + dy + 50)],
                fill=(255, 255, 255, 130), width=6)
        vd.line([(cx, cy + dy), (cx - 110, cy + dy + 50)],
                fill=(255, 255, 255, 130), width=6)
    vein = vein.rotate(-22, resample=Image.BICUBIC, center=(cx, cy))

    # composite shadow
    shadow = soft_shadow(leaf, offset=(8, 18), blur=22, alpha=70)
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, leaf)
    img = Image.alpha_composite(img, vein)

    # DNA helix: series of dots arcing up/down on right side
    helix = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(helix)
    for i in range(7):
        t = i / 6
        dx = 240
        x = cx + dx
        y = cy - 240 + int(t * 480)
        offset = int(35 * math.sin(t * math.pi * 2.4))
        # left strand dot
        hd.ellipse((x - offset - 18, y - 18, x - offset + 18, y + 18),
                   fill=(*palette["main"], 235))
        # right strand dot
        hd.ellipse((x + offset - 18, y - 18, x + offset + 18, y + 18),
                   fill=(*palette["soft"], 235))
        # connecting line
        hd.line([(x - offset, y), (x + offset, y)],
                fill=(*palette["main"], 130), width=4)
    img = Image.alpha_composite(img, helix)
    return img

def draw_music(canvas, palette):
    """Single musical note + sound waves curving into sparkle."""
    img = canvas.copy()
    glow = make_glow((SIZE, SIZE), palette["soft"], intensity=140, blur=140)
    img = Image.alpha_composite(img, glow)

    cx, cy = SIZE // 2, SIZE // 2

    # note stem + head
    note = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    nd = ImageDraw.Draw(note)
    head_w, head_h = 220, 160
    head_x, head_y = cx - 120, cy + 110
    nd.ellipse((head_x - head_w // 2, head_y - head_h // 2,
                head_x + head_w // 2, head_y + head_h // 2),
               fill=(*palette["main"], 240))
    # rotate head slightly
    head_layer = note.copy()
    head_layer = head_layer.rotate(-18, resample=Image.BICUBIC, center=(head_x, head_y))

    # stem
    stem = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stem)
    sd.rectangle((cx - 25, cy - 280, cx + 25, cy + 130),
                 fill=(*palette["main"], 240))
    # flag
    sd.polygon([(cx + 25, cy - 280),
                (cx + 220, cy - 200),
                (cx + 220, cy - 80),
                (cx + 25, cy - 160)],
               fill=(*palette["main"], 240))

    shadow = soft_shadow(head_layer, offset=(8, 18), blur=22, alpha=70)
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, stem)
    img = Image.alpha_composite(img, head_layer)

    # sound waves arching to the right
    waves = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)
    base_x = cx + 230
    base_y = cy + 80
    for i, r in enumerate([90, 170, 250]):
        alpha = 220 - i * 50
        wd.arc((base_x - r, base_y - r, base_x + r, base_y + r),
               start=270, end=90, fill=(*palette["main"], alpha), width=14)
    # AI sparkle (4-point star) at the end
    sx, sy = cx + 360, cy - 220
    star = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd2 = ImageDraw.Draw(star)
    pts = []
    for k in range(8):
        ang = k * math.pi / 4
        radius = 70 if k % 2 == 0 else 26
        pts.append((sx + radius * math.cos(ang),
                    sy + radius * math.sin(ang)))
    sd2.polygon(pts, fill=(*palette["soft"], 240))
    star_blur = star.filter(ImageFilter.GaussianBlur(2))

    img = Image.alpha_composite(img, waves)
    img = Image.alpha_composite(img, star_blur)
    return img

def draw_pe(canvas, palette):
    """Stylised running figure with motion lines transforming into data stream."""
    img = canvas.copy()
    glow = make_glow((SIZE, SIZE), palette["soft"], intensity=130, blur=140)
    img = Image.alpha_composite(img, glow)

    cx, cy = SIZE // 2, SIZE // 2 + 30
    main = (*palette["main"], 240)
    soft = (*palette["soft"], 240)

    fig = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fig)
    # head
    fd.ellipse((cx - 60, cy - 320, cx + 60, cy - 200), fill=main)
    # body (torso) — slanted forward
    fd.polygon([(cx - 30, cy - 200),
                (cx + 90, cy - 180),
                (cx + 70, cy - 30),
                (cx - 50, cy - 50)], fill=main)
    # back arm bent
    fd.polygon([(cx - 50, cy - 170),
                (cx - 200, cy - 90),
                (cx - 200, cy - 50),
                (cx - 60, cy - 130)], fill=main)
    # front arm forward
    fd.polygon([(cx + 70, cy - 170),
                (cx + 220, cy - 100),
                (cx + 240, cy - 60),
                (cx + 90, cy - 130)], fill=main)
    # front leg lifted
    fd.polygon([(cx + 50, cy - 30),
                (cx + 220, cy + 60),
                (cx + 240, cy + 110),
                (cx + 70, cy + 30)], fill=main)
    # back leg bent down
    fd.polygon([(cx - 30, cy - 30),
                (cx - 80, cy + 200),
                (cx - 30, cy + 220),
                (cx + 20, cy + 30)], fill=main)
    # foot extensions
    fd.ellipse((cx - 110, cy + 190, cx - 30, cy + 240), fill=main)
    fd.ellipse((cx + 220, cy + 90, cx + 300, cy + 140), fill=main)

    shadow = soft_shadow(fig, offset=(8, 18), blur=22, alpha=70)
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, fig)

    # motion lines morphing into data dots on the left
    motion = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    md = ImageDraw.Draw(motion)
    for i, y_off in enumerate([-150, -80, 0, 70, 140]):
        x_start = cx - 360 - i * 10
        x_end = cx - 200 + i * 5
        md.line([(x_start, cy + y_off), (x_end, cy + y_off)],
                fill=(*palette["main"], 180 - i * 20), width=10)
    # data dots further left
    for i in range(5):
        x = cx - 380 - i * 18
        y = cy + (-120 + i * 60)
        r = 16 - i * 2
        md.ellipse((x - r, y - r, x + r, y + r),
                   fill=(*palette["soft"], 220 - i * 25))
    img = Image.alpha_composite(img, motion)
    return img

def draw_va(canvas, palette):
    """Paint brush diagonal with glowing colour palette dot."""
    img = canvas.copy()
    glow = make_glow((SIZE, SIZE), palette["soft"], intensity=140, blur=130)
    img = Image.alpha_composite(img, glow)

    cx, cy = SIZE // 2, SIZE // 2
    main = (*palette["main"], 245)
    handle_col = (90, 60, 40, 245)   # warm dark wood
    ferrule_col = (170, 170, 175, 245)  # silver

    brush = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(brush)

    # diagonal brush from top-left to bottom-right around centre
    # we draw vertical and rotate at end
    top_y = cy - 380
    bottom_y = cy + 380

    # handle (long taper)
    bd.polygon([(cx - 35, top_y),
                (cx + 35, top_y),
                (cx + 50, top_y + 380),
                (cx - 50, top_y + 380)], fill=handle_col)

    # ferrule (metal band)
    bd.rectangle((cx - 60, top_y + 380, cx + 60, top_y + 460),
                 fill=ferrule_col)
    bd.rectangle((cx - 60, top_y + 390, cx + 60, top_y + 405),
                 fill=(220, 220, 225, 255))
    bd.rectangle((cx - 60, top_y + 440, cx + 60, top_y + 455),
                 fill=(140, 140, 145, 255))

    # bristles (paint colour)
    bd.polygon([(cx - 60, top_y + 460),
                (cx + 60, top_y + 460),
                (cx + 90, bottom_y - 30),
                (cx - 90, bottom_y - 30)], fill=main)
    # paint drip swoop at tip
    bd.ellipse((cx - 95, bottom_y - 45, cx + 95, bottom_y + 35), fill=main)
    bd.ellipse((cx + 30, bottom_y + 30, cx + 110, bottom_y + 110), fill=main)

    # rotate -32 deg for diagonal feel
    brush = brush.rotate(-32, resample=Image.BICUBIC, center=(cx, cy))
    shadow = soft_shadow(brush, offset=(10, 18), blur=22, alpha=80)
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, brush)

    # palette colour dots glowing
    dots = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    palette_colours = [
        (*palette["soft"], 240),
        (220, 90, 70, 240),
        (245, 200, 95, 240),
        (95, 165, 210, 240),
    ]
    centres = [(cx - 280, cy - 220),
               (cx - 380, cy - 100),
               (cx - 380, cy + 60),
               (cx - 280, cy + 180)]
    for (x, y), col in zip(centres, palette_colours):
        dd.ellipse((x - 50, y - 50, x + 50, y + 50), fill=col)
    dots_glow = dots.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, dots_glow)
    img = Image.alpha_composite(img, dots)
    return img


# ---------- Main ----------

def main():
    base = base_canvas()
    jobs = [
        ("icon_science.png", draw_science, "science"),
        ("icon_music.png",   draw_music,   "music"),
        ("icon_pe.png",      draw_pe,      "pe"),
        ("icon_va.png",      draw_va,      "va"),
    ]
    for fname, fn, key in jobs:
        out = fn(base, PALETTES[key])
        # final flatten to RGB (PNG can keep alpha; we keep alpha for crisp edges)
        out_path = os.path.join(OUT, fname)
        out.save(out_path, "PNG", optimize=True)
        print(f"[ok] {fname}  ({out_path})")

if __name__ == "__main__":
    main()
