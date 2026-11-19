"""Prépare les photos 2021 pour le web : redimensionne, convertit en WebP, ne garde aucune métadonnée."""
import sys
from pathlib import Path
from PIL import Image, ImageOps

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
# nom de sortie : (préfixe du fichier reçu, tailles)
PHOTOS = {
    "hero-1": ("3bb793fb", (1920, 1080)),   # enfants et cartables, bras levés
    "hero-2": ("f090017c", (1920, 1080)),   # femmes qui dansent avec des branches
    "hero-3": ("ab560363", (1920, 1080)),   # élèves en uniforme devant la végétation
    "hero-4": ("805530d6", (1920, 1080)),   # marché : avocats et oranges
    "meres": ("22b6cf23", (1920, 1080)),    # femmes attentives au pupitre
    "groupe": ("3e1c9b0d", (1920, 1080)),   # grand groupe avec les cartables
    "fournitures": ("f2225820", (1600, 800)),
    "sourires": ("697770e1", (1600, 800)),
    "pupitres": ("551db777", (1600, 800)),
    "pupitres-2": ("69fd1bf5", (1600, 800)),
    "uniformes": ("b73965d5", (1600, 800)),
    "danse": ("14165a90", (1600, 800)),
    "jeunes": ("c951ce95", (1600, 800)),
    "terre-rouge": ("ddc10358", (1600, 800)),
}
for name, (key, sizes) in PHOTOS.items():
    src = next(SRC.glob(f"{key}-image.jpg"))
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    for w in sizes:
        h = round(im.height * w / im.width)
        out = OUT / f"{name}-{w}.webp"
        im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=74 if w > 1200 else 72, method=6)
        print(out.name, f"{out.stat().st_size // 1024} KB")
# Image de partage (aperçu WhatsApp, Facebook) : 1200 x 630
im = ImageOps.exif_transpose(Image.open(next(SRC.glob("3bb793fb-image.jpg")))).convert("RGB")
W, H = im.size
crop_h = round(W * 630 / 1200)
top = max(0, round(H * 0.08))
og = im.crop((0, top, W, top + crop_h)).resize((1200, 630), Image.LANCZOS)
og.save(OUT / "partage.jpg", "JPEG", quality=82, optimize=True, progressive=True)
print("partage.jpg", (OUT / "partage.jpg").stat().st_size // 1024, "KB")
