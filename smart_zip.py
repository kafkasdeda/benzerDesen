# smart_zip.py
# Oluşturulma: 2025-04-20
# Hazırlayan: Kafkas
# Açıklama: .zipignore dosyasına göre proje klasörünü zip'ler

import os
import zipfile

ZIPIGNORE_FILE = ".zipignore"
ZIP_NAME = "benzerDesen_clean.zip"
ROOT_DIR = "."  # Proje klasörü

# 1. Ignore listesi
ignore_patterns = []
if os.path.exists(ZIPIGNORE_FILE):
    with open(ZIPIGNORE_FILE, "r", encoding="utf-8") as f:
        ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]

def is_ignored(path):
    return any(pattern in path for pattern in ignore_patterns)

# 2. Zip oluştur
with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
    for foldername, subfolders, filenames in os.walk(ROOT_DIR):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            relpath = os.path.relpath(filepath, ROOT_DIR)

            if is_ignored(relpath):
                continue

            zipf.write(filepath, relpath)

print(f"🎉 Zip dosyası oluşturuldu: {ZIP_NAME}")