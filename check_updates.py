# check_updates.py
# Bu dosya, realImages klasöründeki görseller ve realImages_json içindeki JSON dosyalarında bir değişiklik olup olmadığını kontrol eder.
# Yeni görseller veya güncellenmiş JSON tespit edilirse, merge_metadata.py, generate_thumbnails.py ve generate_representatives.py çalıştırılır.
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas

import os
import time
import json
import hashlib
import subprocess
from merge_metadata import load_json

REAL_IMAGES_DIR = "realImages"
JSON_DIR = "realImages_json"
MERGE_CACHE_FILE = "metadata_cache.json"

# Klasördeki dosyaların hash'ini alalım
def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def get_image_filenames():
    return sorted([f for f in os.listdir(REAL_IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

def get_json_hashes():
    hashes = {}
    for fname in ["yunportalclaude.json", "yunportalclaudedetail.json"]:
        path = os.path.join(JSON_DIR, fname)
        if os.path.exists(path):
            hashes[fname] = get_file_hash(path)
    return hashes

# Kaydedilmiş cache dosyasını yükle
def load_previous_cache():
    if not os.path.exists(MERGE_CACHE_FILE):
        return {"images": [], "json_hashes": {}}
    with open(MERGE_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Güncel durumu kaydet
def save_current_cache(image_list, json_hashes):
    with open(MERGE_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"images": image_list, "json_hashes": json_hashes}, f, indent=2)

# Model dosyasını al
def get_model_data(model_type):
    model_path = os.path.join("exported_clusters", model_type, "versions.json")
    if not os.path.exists(model_path):
        return None
        
    try:
        with open(model_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# Mevcut clusterları ve versiyonları kontrol et
def check_cluster_integrity():
    # Kullanılabilir modelleri kontrol et
    models = ["pattern", "color", "texture"]
    updated = False
    
    for model in models:
        model_data = get_model_data(model)
        if not model_data:
            continue
        
        current_version = model_data.get("current_version")
        if not current_version:
            continue
            
        versions = model_data.get("versions", {})
        if not versions:
            continue
            
        # Metadata dosyasını yükle
        metadata_path = "image_metadata_map.json"
        if not os.path.exists(metadata_path):
            continue
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Versiyon tutarlılığını kontrol et
        for version_id, version_data in versions.items():
            clusters = version_data.get("clusters", {})
            for cluster_id, cluster_data in clusters.items():
                # Bu cluster'daki tüm görsellerin metadata'daki cluster bilgisini güncelle
                images = cluster_data.get("images", [])
                
                for image_name in images:
                    if image_name in metadata:
                        # Metadata bilgisini kontrol et ve güncelle
                        if metadata[image_name].get("cluster") != cluster_id:
                            metadata[image_name]["cluster"] = cluster_id
                            updated = True
                            print(f"🔄 Görsel {image_name} için cluster bilgisi güncellendi: {cluster_id}")
        
        # Değişiklik olduysa kaydet
        if updated:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"✅ Metadata tutarlılığı sağlandı.")
    
    return updated

# Asıl kontrol fonksiyonu
def check_for_updates():
    current_images = get_image_filenames()
    current_hashes = get_json_hashes()
    cached = load_previous_cache()
    
    # Önce cluster tutarlılığını kontrol et
    cluster_updated = check_cluster_integrity()

    if cached["images"] != current_images or cached["json_hashes"] != current_hashes or cluster_updated:
        print("🔄 Değişiklik algılandı: metadata yeniden oluşturuluyor...")
        import merge_metadata  # yeniden çalıştır

        # Thumbnail'ları da güncelle
        try:
            subprocess.run(["python", "generate_thumbnails.py"], check=True)
        except Exception as e:
            print(f"❌ Thumbnail oluşturma sırasında hata: {e}")

        # ✅ GÜNCELLEME: Cluster temsilcilerini de yeniden oluştur
        try:
            subprocess.run(["python", "generate_representatives.py"], check=True)
        except Exception as e:
            print(f"❌ Cluster temsilcileri güncellenemedi: {e}")

        save_current_cache(current_images, current_hashes)
        return True
    else:
        print("✅ Değişiklik yok, metadata güncel.")
        return False

if __name__ == "__main__":
    update_result = check_for_updates()
    print(f"💼 Güncelleme durumu: {'Güncellendi' if update_result else 'Güncel'}")
