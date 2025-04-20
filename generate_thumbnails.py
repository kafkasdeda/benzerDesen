# generate_thumbnails.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas ❤️ Luna
# Açıklama:
# Bu script, realImages klasöründeki tüm .jpg/.png görsellerin
# küçük boyutlu versiyonlarını oluşturur ve thumbnails/ klasörüne kaydeder.
# Thumbnail'ler orta ve sol panelde hızlı ve kaliteli gösterim için kullanılır.

import os
from PIL import Image
from tqdm import tqdm

INPUT_DIR = "realImages"
THUMBNAIL_DIR = "thumbnails"
SIZE = (224, 224)

os.makedirs(THUMBNAIL_DIR, exist_ok=True)

print("📦 Thumbnail üretimi başladı...")
count = 0

for fname in tqdm(os.listdir(INPUT_DIR)):
    if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    try:
        input_path = os.path.join(INPUT_DIR, fname)
        output_path = os.path.join(THUMBNAIL_DIR, fname)

        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img.thumbnail(SIZE, Image.Resampling.LANCZOS)
            img.save(output_path)
            count += 1
    except Exception as e:
        print(f"⚠️ {fname} thumbnail oluşturulamadı: {e}")

print(f"✅ Toplam {count} görsel için thumbnail oluşturuldu → {THUMBNAIL_DIR}")
