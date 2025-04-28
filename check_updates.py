# check_updates.py
# Bu dosya, realImages klasöründeki görseller ve realImages_json içindeki JSON dosyalarında bir değişiklik olup olmadığını kontrol eder.
# Yeni görseller veya güncellenmiş JSON tespit edilirse, kullanıcıya detaylı bilgi verir ve gerekli işlemlerin yapılması için onay bekler.
# Oluşturulma: 2025-04-19
# Güncelleme: 2025-04-27 (Kullanıcı onayı eklendi)
# Güncelleme: 2025-04-28 (Web arayüzü entegrasyonu ve detaylı değişiklik raporu eklendi)
# Hazırlayan: Kafkas

import os
import time
import json
import hashlib
import subprocess
import pathlib
import shutil
from datetime import datetime
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
    models = ["pattern", "color", "texture", "color+pattern"]
    updated = False
    updated_clusters = []
    
    # Güncelleme bayrağını kontrol et
    if os.path.exists('updating_clusters.flag'):
        print("⚠️ Güncelleme işlemi devam ediyor, cluster kontrolü atlanıyor.")
        return False, []
    
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
                            updated_clusters.append((image_name, cluster_id))
        
        # Değişiklik olduysa kaydet
        if updated:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return updated, updated_clusters

# Görsel meta bilgilerini getir
def get_image_metadata(image_name):
    # Metadata dosyasını kontrol et
    metadata_path = "image_metadata_map.json"
    if not os.path.exists(metadata_path):
        return {}
        
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        return metadata.get(image_name, {})
    except Exception as e:
        print(f"Metadata okuma hatası: {e}")
        return {}

# Görsel bilgilerini al
def get_image_info(image_name):
    image_path = os.path.join(REAL_IMAGES_DIR, image_name)
    if not os.path.exists(image_path):
        return {}
    
    # Dosya boyutu ve tarihi al
    file_stats = os.stat(image_path)
    file_size = file_stats.st_size
    created_time = datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    # Görsel meta verileri
    metadata = get_image_metadata(image_name)
    
    return {
        "filename": image_name,
        "file_size": file_size,
        "file_size_formatted": format_file_size(file_size),
        "created": created_time,
        "modified": modified_time,
        "extension": pathlib.Path(image_name).suffix.lower(),
        "metadata": metadata
    }

# Dosya boyutunu formatlı şekilde döndür
def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

# Değişiklikleri tespit et ve detaylı rapor oluştur
def detect_changes():
    current_images = get_image_filenames()
    current_hashes = get_json_hashes()
    cached = load_previous_cache()
    
    # Önce cluster tutarlılığını kontrol et
    cluster_updated, updated_clusters = check_cluster_integrity()

    # Yeni ve silinen görselleri tespit et
    new_images = [img for img in current_images if img not in cached["images"]]
    removed_images = [img for img in cached["images"] if img not in current_images]
    
    # JSON değişikliklerini tespit et
    json_changes = []
    for fname, current_hash in current_hashes.items():
        if fname not in cached["json_hashes"] or cached["json_hashes"][fname] != current_hash:
            json_changes.append(fname)
    
    # Değişiklik var mı kontrol et
    has_changes = len(new_images) > 0 or len(removed_images) > 0 or len(json_changes) > 0 or cluster_updated
    
    # Detaylı görsel bilgileri topla
    new_images_details = [get_image_info(img) for img in new_images]
    removed_images_details = [
        {
            "filename": img,
            "metadata": get_image_metadata(img)
        } for img in removed_images
    ]
    
    # Gereken işlemlerin listesini hazırla
    required_actions = []
    if new_images:
        required_actions.append({
            "action": "generate_thumbnails",
            "description": "Yeni görseller için önizleme oluştur"
        })
        required_actions.append({
            "action": "extract_features",
            "description": "Özellik vektörlerini güncelle"
        })
    
    if cluster_updated:
        required_actions.append({
            "action": "update_clusters",
            "description": "Cluster bilgilerini güncelle"
        })
    
    if json_changes:
        required_actions.append({
            "action": "update_metadata",
            "description": "Metadata bilgilerini güncelle"
        })
    
    # Değişiklik raporu oluştur
    change_report = {
        "has_changes": has_changes,
        "summary": {
            "new_images_count": len(new_images),
            "removed_images_count": len(removed_images),
            "json_changes_count": len(json_changes),
            "cluster_updates_count": len(updated_clusters) if cluster_updated else 0
        },
        "details": {
            "new_images": new_images_details,
            "removed_images": removed_images_details,
            "json_changes": json_changes,
            "cluster_updates": {
                "updated": cluster_updated,
                "details": updated_clusters
            }
        },
        "required_actions": required_actions,
        "current_images": current_images,
        "current_hashes": current_hashes,
        "timestamp": datetime.now().isoformat()
    }
    
    return change_report

# Gerekli güncellemeleri yap
def apply_updates(change_report):
    # İşlemin başladığını gösteren bir flag dosyası oluştur
    with open('updating_clusters.flag', 'w') as f:
        f.write(datetime.now().isoformat())
        
    results = {
        "status": "success",
        "actions": [],
        "errors": []
    }
    
    # Metadata güncelleme
    try:
        import merge_metadata
        metadata_result = merge_metadata.merge_all_metadata()
        results["actions"].append({
            "action": "update_metadata",
            "status": "success",
            "message": "Metadata başarıyla güncellendi"
        })
    except Exception as e:
        results["errors"].append({
            "action": "update_metadata",
            "error": str(e)
        })
        print(f"\n❌ Metadata güncellenirken hata: {e}")

    # Yeni görseller için thumbnail'ları oluştur
    try:
        if len(change_report["details"]["new_images"]) > 0:
            subprocess.run(["python", "generate_thumbnails.py"], check=True)
            results["actions"].append({
                "action": "generate_thumbnails",
                "status": "success",
                "message": f"{len(change_report['details']['new_images'])} yeni görsel için önizleme oluşturuldu"
            })
            print(f"\n✅ {len(change_report['details']['new_images'])} yeni görsel için önizleme oluşturuldu")
    except Exception as e:
        results["errors"].append({
            "action": "generate_thumbnails",
            "error": str(e)
        })
        print(f"\n❌ Thumbnail oluşturma sırasında hata: {e}")

    # Özellik vektörlerini güncelle (tüm model tipleri için)
    try:
        for model_type in ["pattern", "color", "texture", "color+pattern"]:
            subprocess.run(["python", "extract_features.py", "--model_type", model_type], check=True)
            results["actions"].append({
                "action": f"extract_features_{model_type}",
                "status": "success",
                "message": f"{model_type} modeli için özellik vektörleri güncellendi"
            })
        print("\n✅ Tüm modeller için özellik vektörleri başarıyla güncellendi")
    except Exception as e:
        results["errors"].append({
            "action": "extract_features",
            "error": str(e)
        })
        print(f"\n❌ Özellik vektörleri güncellenirken hata: {e}")

    # Cluster temsilcilerini de yeniden oluştur
    try:
        subprocess.run(["python", "generate_representatives.py"], check=True)
        results["actions"].append({
            "action": "generate_representatives",
            "status": "success",
            "message": "Cluster temsilcileri güncellendi"
        })
        print("\n✅ Cluster temsilcileri güncellendi")
    except Exception as e:
        results["errors"].append({
            "action": "generate_representatives",
            "error": str(e)
        })
        print(f"\n❌ Cluster temsilcileri güncellenemedi: {e}")

    # Faiss indekslerini temizle (güncelleme sonrası yeniden oluşturmak için)
    try:
        # app.py'de tanımlanan global faiss_indexes değişkenini sıfırlamak için bir dosya oluştur
        with open("reset_faiss_indexes.flag", "w") as f:
            f.write(datetime.now().isoformat())
        results["actions"].append({
            "action": "reset_faiss_indexes",
            "status": "success",
            "message": "Faiss indeksleri sıfırlandı"
        })
    except Exception as e:
        results["errors"].append({
            "action": "reset_faiss_indexes",
            "error": str(e)
        })

    # Güncel durumu kaydet
    save_current_cache(change_report["current_images"], change_report["current_hashes"])
    
    # Güncelleme tamamlandığını kaydeden dosya oluştur
    with open("updates_done.json", "w", encoding="utf-8") as f:
        update_record = {
            "timestamp": datetime.now().isoformat(),
            "status": results["status"],
            "summary": change_report.get("summary", {}),
            "actions": results["actions"]
        }
        json.dump(update_record, f, indent=2, ensure_ascii=False)
    
    # Flag dosyasını sil
    if os.path.exists('updating_clusters.flag'):
        os.remove('updating_clusters.flag')
    
    # Başarı durumunu kontrol et
    if results["errors"]:
        results["status"] = "partial_success" if results["actions"] else "error"
    
    # Log dosyası oluştur
    update_log_path = f"update_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(update_log_path, "w", encoding="utf-8") as f:
        update_log = {
            "timestamp": datetime.now().isoformat(),
            "changes": change_report,
            "results": results
        }
        json.dump(update_log, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'✅ Güncellemeler başarıyla tamamlandı!' if results['status'] == 'success' else '⚠️ Bazı güncellemeler tamamlanamadı.'}")
    return results

# Ana kontrol fonksiyonu
def check_for_updates():
    # İşlem zaten çalışıyorsa kontrolü geç
    if os.path.exists('updating_clusters.flag'):
        print("⚠️ Güncelleme işlemi zaten devam ediyor.")
        
        # Dosyanın 10 dakikadan daha eski olup olmadığını kontrol et
        flag_age = time.time() - os.path.getmtime('updating_clusters.flag')
        if flag_age > 600:  # 10 dakika (saniye cinsinden)
            print(f"🕑 Güncelleme bayrağı {flag_age/60:.1f} dakika eskide kalmış, temizleniyor.")
            os.remove('updating_clusters.flag')
        else:
            # İşlem devam ediyorsa boş sonuç döndür
            return {
                "has_changes": False, 
                "message": "⏳ Güncelleme işlemi halen devam ediyor, lütfen bekleyin.",
                "timestamp": datetime.now().isoformat()
            }
    
    # Uygulanmış güncellemelerin kaydını içeren dosya var mı?
    updates_done_file = "updates_done.json"
    if os.path.exists(updates_done_file):
        try:
            with open(updates_done_file, "r", encoding="utf-8") as f:
                updates_done = json.load(f)
                last_update_time = datetime.fromisoformat(updates_done.get("timestamp", "2000-01-01T00:00:00"))
                current_time = datetime.now()
                
                # Son güncellemeden bu yana 2 saatten az zaman geçtiyse ve zorla kontrol istenmemişse
                time_diff = (current_time - last_update_time).total_seconds()
                if time_diff < 7200:  # 2 saat
                    print(f"✅ Son güncellemeden sadece {time_diff/60:.1f} dakika geçti.") 
                    return {
                        "has_changes": False, 
                        "message": f"✅ Sistem güncel. Son güncelleme: {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}",
                        "timestamp": current_time.isoformat()
                    }
        except Exception as e:
            print(f"Uyarı: Güncelleme kaydı okunamadı: {e}")
            # Devam et ve güncellemeleri kontrol et
    
    # Değişiklikleri tespit et
    change_report = detect_changes()
    
    if change_report["has_changes"]:
        # Değişiklik raporu oluştur
        # Kullanıcı arayüzü için friendly mesajlar
        notification_message = ""
        if change_report["summary"]["new_images_count"] > 0:
            notification_message += f"📷 {change_report['summary']['new_images_count']} yeni görsel eklendi. "  
        if change_report["summary"]["removed_images_count"] > 0:
            notification_message += f"🚫 {change_report['summary']['removed_images_count']} görsel silindi. "
        if change_report["summary"]["json_changes_count"] > 0:
            notification_message += f"📝 {change_report['summary']['json_changes_count']} JSON dosyası değişti. "  
        if change_report["summary"]["cluster_updates_count"] > 0:
            notification_message += f"🧹 {change_report['summary']['cluster_updates_count']} cluster güncellendi. "
            
        change_report["notification"] = {
            "title": "Görsel veya Metadata Değişikliği Tespit Edildi",
            "message": notification_message,
            "actions": [
                {
                    "action": "apply_updates",
                    "label": "Güncelle",
                    "description": "Tüm değişiklikleri uygula (thumbnail, özellik vektörleri, cluster bilgileri)"
                },
                {
                    "action": "ignore",
                    "label": "Yoksay",
                    "description": "Değişiklikleri yoksay (daha sonra tekrar hatırlatılacak)"
                },
                {
                    "action": "details",
                    "label": "Detayları Göster",
                    "description": "Değişikliklerin tam listesini göster"
                }
            ]
        }
        
        # Cache'i güncellememek için önceki dosyaları ve hashları de ekle (eğer ignore olursa)
        change_report["previous_cache"] = {
            "images": load_previous_cache()["images"],
            "json_hashes": load_previous_cache()["json_hashes"]
        }
        
        return change_report
    else:
        return {
            "has_changes": False, 
            "message": "✅ Değişiklik yok, görsel ve metadata güncel.",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    report = check_for_updates()
    if report["has_changes"]:
        print("\n🔔 Görsel veya metadata değişiklikleri algılandı!")
        
        if report["new_images"]:
            print(f"\n📷 {len(report['new_images'])} yeni görsel eklendi:")
            for img in report["new_images"][:5]:
                print(f"  - {img}")
            if len(report["new_images"]) > 5:
                print(f"  - ... ve {len(report['new_images']) - 5} görsel daha")
                
        if report["removed_images"]:
            print(f"\n🚫 {len(report['removed_images'])} görsel silindi veya taşındı:")
            for img in report["removed_images"][:5]:
                print(f"  - {img}")
            if len(report["removed_images"]) > 5:
                print(f"  - ... ve {len(report['removed_images']) - 5} görsel daha")
        
        if report["json_changes"]:
            print(f"\n📝 {len(report['json_changes'])} metadata dosyası değiştirildi:")
            for json_file in report["json_changes"]:
                print(f"  - {json_file}")
        
        if report["cluster_updates"]["updated"]:
            print(f"\n🧹 Cluster bilgileri güncellendi")
            for img, cluster in report["cluster_updates"]["details"][:5]:
                print(f"  - {img} → {cluster}")
            if len(report["cluster_updates"]["details"]) > 5:
                print(f"  - ... ve {len(report['cluster_updates']['details']) - 5} görsel daha")
        
        choice = input("\n👩‍💻 Bu değişikliklere dayalı olarak gerekli güncellemeleri yapmak istiyor musunuz? (E/H): ")
        if choice.lower() == "e":
            print("\n🔄 Güncellemeler yapılıyor...")
            apply_updates(report)
        else:
            print("\nℹ️ Güncelleme işlemi iptal edildi. Değişiklikler kaydedilmedi.")
    else:
        print(report["message"])