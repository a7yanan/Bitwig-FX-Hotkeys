"""Generates assets/icon.png and assets/icon.ico (purple->blue lightning bolt)."""
from PIL import Image, ImageDraw

S = 1024
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
grad = Image.new("RGBA", (S, S))
px = grad.load()
a, b = (124, 58, 237), (59, 130, 246)
for y in range(S):
    for x in range(S):
        t = (x + y) / (2 * S - 2)
        px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle((24, 24, S - 24, S - 24), radius=230, fill=255)
img.paste(grad, (0, 0), mask)
bolt = [(580, 140), (270, 560), (470, 560), (410, 890), (760, 440), (545, 440), (640, 140)]
ImageDraw.Draw(img).polygon(bolt, fill=(255, 255, 255, 255))
img.resize((256, 256), Image.LANCZOS).save("assets/icon.png")
img.save("assets/icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
