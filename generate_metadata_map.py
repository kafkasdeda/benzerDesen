# generate_metadata_map.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas ❤️ Luna
# Açıklama:
# Bu script, realImages klasöründeki görsellerin metadata bilgilerini
# (yunportalclaude.json + yunportalclaudedetail.json) ve varsa cluster bilgisini birleştirir.
# Çıktı olarak image_metadata_map.json dosyasına yazar.

import os
import json
from glob import glob

# Dosya yolları
REAL_DIR = "realImages"
JSON_DIR = "realImages_json"
OUT_PATH = "image_metadata_map.json"

# JSON kaynaklarını oku
with open(os.path.join(JSON_DIR, "yunportalclaude.json"), encoding="utf-8") as f:
    claude_data = json.load(f)

with open(os.path.join(JSON_DIR, "yunportalclaudedetail.json"), encoding="utf-8") as f:
    detail_data = json.load(f)

# BlendId → [HTYPE, PERCENTAGE] eşlemesi
blend_lookup = {}
for blend in detail_data:
    blend_id = str(blend.get("BlendID"))
    if blend_id not in blend_lookup:
        blend_lookup[blend_id] = []
    blend_lookup[blend_id].append((blend["HTYPE"], blend["PERCENTAGE"]))

# Cluster eşleşmesi → filename: cluster_adi
cluster_lookup = {}
CLUSTER_BASE = "exported_clusters/pattern"
if os.path.exists(CLUSTER_BASE):
    for cluster_name in os.listdir(CLUSTER_BASE):
        cluster_path = os.path.join(CLUSTER_BASE, cluster_name)
        if not os.path.isdir(cluster_path):
            continue
        for fname in os.listdir(cluster_path):
            cluster_lookup[fname] = cluster_name

# Görselleri tara ve metadata ile eşleştir
result = {}
real_images = glob(os.path.join(REAL_DIR, "*.jpg"))
for img_path in real_images:
    fname = os.path.basename(img_path)
    entry = next((item for item in claude_data if item["FULLPATH"] == fname), None)

    if not entry:
        continue

    blend_id = str(entry.get("BlendId"))
    if blend_id not in blend_lookup:
        print(f"⚠️ BlendId eşleşmedi: {fname}, BlendId: {blend_id}")

    result[fname] = {
        "design": entry.get("DESIGN"),
        "season": entry.get("SEASON"),
        "quality": entry.get("QUALITY"),
        "features": blend_lookup.get(blend_id, []),
        "cluster": cluster_lookup.get(fname)  # olmayabilir
    }

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✅ {len(result)} görsel için metadata + cluster eşleşmesi tamamlandı → {OUT_PATH}")
