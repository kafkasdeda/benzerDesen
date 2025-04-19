# merge_metadata.py
# Bu dosya, realImages_json klasöründeki 'yunportalclaude.json' ve 'yunportalclaudedetail.json' dosyalarını birleştirerek
# realImages klasöründe gerçekten var olan görseller için tam metadata yapısı oluşturur.
# Her görsel için DESIGN, VARIANT, SEASON, QUALITY, BLEND ve tüm feature flag'leri içeren JSON objesi üretir.
# Çıktı dosyası: merged_metadata.json
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas 

# Ne Yapar?
# realImages_json/yunportalclaude.json + yunportalclaudedetail.json → birleştirir

# Sadece gerçekten realImages/ klasöründe bulunan görselleri işler

# Her görsel için:

# design, variant, season, quality

# blend → {htype, percentage} dizisi

# Sonuç: merged_metadata.json olarak dışa aktarılır


import os
import json
from typing import List, Dict

# Kök klasörleri ayarlıyoruz
REAL_IMAGES_DIR = "realImages"
JSON_DIR = "realImages_json"

# Dosya adları
MAIN_JSON = os.path.join(JSON_DIR, "yunportalclaude.json")
DETAIL_JSON = os.path.join(JSON_DIR, "yunportalclaudedetail.json")

# İçerikleri belleğe yükleyelim
def load_json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Ana ve detay verileri oku
main_data = load_json(MAIN_JSON)
detail_data = load_json(DETAIL_JSON)

# BlendId üzerinden detayları lookup yapabilmek için dict'e çevirelim
detail_lookup = {}
for entry in detail_data:
    blend_id = entry.get("BlendId")
    if blend_id:
        if blend_id not in detail_lookup:
            detail_lookup[blend_id] = []
        detail_lookup[blend_id].append({
            "htype": entry.get("HTYPE"),
            "percentage": entry.get("PERCENTAGE")
        })

# Sonuç verisini oluşturalım
merged_metadata = []

for item in main_data:
    fullpath = item.get("FULLPATH")
    filename = os.path.basename(fullpath)
    image_path = os.path.join(REAL_IMAGES_DIR, filename)

    # Gerçekten dosya var mı kontrol et
    if not os.path.exists(image_path):
        continue

    blend_id = item.get("BlendId")
    blend = detail_lookup.get(blend_id, [])

    merged_metadata.append({
        "filename": filename,
        "design": item.get("DESIGN"),
        "variant": item.get("VARIANT"),
        "season": item.get("SEASON"),
        "quality": item.get("QUALITY"),
        "blend": blend,
        "features": {
            "MONOSTRETCH": item.get("MONOSTRETCH", 0),
            "BISTRETCH": item.get("BISTRETCH", 0),
            "POWERSTRETCH": item.get("POWERSTRETCH", 0),
            "NATURALSTRETCH": item.get("NATURALSTRETCH", 0),
            "LIGHTWEIGHT": item.get("LIGHTWEIGHT", 0),
            "COMFORT": item.get("COMFORT", 0),
            "WASHABLE": item.get("WASHABLE", 0),
            "BREATHABLE": item.get("BREATHABLE", 0),
            "ANTIBACTERIAL": item.get("ANTIBACTERIAL", 0),
            "EASYIRONING": item.get("EASYIRONING", 0),
            "MOISTUREMANAGMENT": item.get("MOISTUREMANAGMENT", 0),
            "UVPROTECTION": item.get("UVPROTECTION", 0),
            "WRINKLERESISTANCE": item.get("WRINKLERESISTANCE", 0),
            "WATERREPELLENT": item.get("WATERREPELLENT", 0),
            "THERMALCOMFORT": item.get("THERMALCOMFORT", 0),
            "QUICKDRY": item.get("QUICKDRY", 0),
            "RWS": item.get("RWS", 0),
            "RCSGRS": item.get("RCSGRS", 0)
        }
    })

# Sonuç dosyasına kaydedelim (opsiyonel)
with open("merged_metadata.json", "w", encoding="utf-8") as f:
    json.dump(merged_metadata, f, indent=2, ensure_ascii=False)

print(f"✅ Toplam {len(merged_metadata)} görsel için metadata birleştirildi.")
