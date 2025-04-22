# generate_representatives.py
# Oluşturulma: 2025-04-20
# Hazırlayan: Kafkas
# Açıklama:
# Bu script, exported_clusters/pattern klasöründeki her cluster klasöründen bir temsilci görsel (ilk jpg) seçer.
# Bunları exported_clusters/pattern/v1/representatives.json dosyasına yazar.
# Dosya, versiyon açıklaması (version_comment) ile birlikte tüm cluster temsilcilerini içerir.

import os
import json
from glob import glob

CLUSTER_ROOT = "exported_clusters/pattern"
VERSION = "v1"
OUT_DIR = os.path.join(CLUSTER_ROOT, VERSION)
OUT_FILE = os.path.join(OUT_DIR, "representatives.json")

# ✅ Temsilci klasörü oluştur
os.makedirs(OUT_DIR, exist_ok=True)

representatives = {
    "version_comment": "Otomatik oluşturulan ilk versiyon. Temsilciler klasörlerin ilk görselidir.",
    "clusters": []
}

# 🔄 Her klasörü tara ve ilk jpg'yi temsilci olarak seç
for cluster_name in os.listdir(CLUSTER_ROOT):
    cluster_path = os.path.join(CLUSTER_ROOT, cluster_name)
    if not os.path.isdir(cluster_path) or cluster_name == VERSION:
        continue

    images = sorted(glob(os.path.join(cluster_path, "*.jpg")))
    if not images:
        continue

    representative_filename = os.path.basename(images[0])

    representatives["clusters"].append({
        "filename": representative_filename,
        "cluster": cluster_name,
        "comment": ""
    })

# 💾 JSON dosyasına yaz
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(representatives, f, indent=2, ensure_ascii=False)

print(f"✅ {len(representatives['clusters'])} cluster temsilcisi yazıldı → {OUT_FILE}")
