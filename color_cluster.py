"""
Renk modeli için özel sınıflandırma modülü.

Bu modül, renk modeli için kümeleme yaklaşımı yerine renk spektrumuna dayalı bir 
sınıflandırma sistemi sunar. HSV renk uzayı kullanarak daha doğal renk grupları oluşturur.
"""

import os
import json
import numpy as np
import shutil
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Renk işleme için yardımcı modüller
from color_utils import (
    rgb_to_hsv, hsv_to_rgb, 
    calculate_hsv_distance,
    identify_color_group, 
    extract_dominant_color_improved
)

# Renk spektrumu modülünden fonksiyonları import et
from color_spectrum import (
    build_color_spectrum,
    classify_color_in_spectrum,
    get_color_group_name,
    build_spectrum_from_directory
)

def get_model_data(model_type: str) -> Dict:
    """
    Model JSON verisini okur.
    
    Args:
        model_type: Model tipi ("color", "pattern", vb.)
        
    Returns:
        Model verisi
    """
    model_path = os.path.join("exported_clusters", model_type, "versions.json")
    
    if not os.path.exists(model_path):
        # Yeni model dosyası oluştur
        data = {
            "current_version": "v1",
            "versions": {}
        }
        # Model klasörünü oluştur
        os.makedirs(os.path.join("exported_clusters", model_type), exist_ok=True)
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data
        
    try:
        with open(model_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Bozuksa yeniden oluştur
        return {
            "current_version": "v1",
            "versions": {}
        }

def save_model_data(model_type: str, data: Dict) -> bool:
    """
    Model JSON verisini kaydeder.
    
    Args:
        model_type: Model tipi ("color", "pattern", vb.)
        data: Kaydedilecek veri
        
    Returns:
        Başarı durumu
    """
    model_path = os.path.join("exported_clusters", model_type, "versions.json")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True

def create_color_clusters(
    model_type: str,
    version: str,
    divisions: int = 12,
    saturation_levels: int = 3,
    value_levels: int = 3,
    dominant_color_method: str = 'histogram',
    output_dir: Optional[str] = None
) -> Dict:
    """
    Renk modeli için özel sınıflandırma yapar.
    
    Args:
        model_type: Model tipi ("color")
        version: Oluşturulacak versiyon adı
        divisions: Ton (hue) bölünme sayısı
        saturation_levels: Doygunluk seviye sayısı
        value_levels: Parlaklık seviye sayısı
        dominant_color_method: Dominant renk çıkarma yöntemi
        output_dir: Çıktı klasörü (belirtilmezse otomatik oluşturulur)
        
    Returns:
        Oluşturulan küme verisi
    """
    # Başlangıç zamanı
    start_time = time.time()
    
    # Çıktı klasörünü ayarla
    if output_dir is None:
        output_dir = os.path.join("exported_clusters", model_type, version)
    
    # Çıktı klasörlerini oluştur
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    # Görsel dosyalarını bul
    image_folder = "realImages"
    if not os.path.exists(image_folder):
        raise FileNotFoundError(f"Görsel klasörü bulunamadı: {image_folder}")
    
    # Renk spektrumu oluştur
    print(f"🔍 Renk spektrumu oluşturuluyor: {divisions} bölüm, {saturation_levels}x{value_levels} seviye")
    spectrum = build_spectrum_from_directory(
        image_folder, 
        divisions=divisions, 
        saturation_levels=saturation_levels, 
        value_levels=value_levels,
        method=dominant_color_method
    )
    
    # Spektrum istatistiklerini hesapla
    from color_spectrum import get_color_spectrum_statistics
    stats = get_color_spectrum_statistics(spectrum)
    
    # Model verisini al
    model_data = get_model_data(model_type)
    
    # Mevcut versiyon verisi veya yeni versiyon oluştur
    if version not in model_data["versions"]:
        model_data["versions"][version] = {
            "created_at": datetime.now().isoformat(),
            "comment": f"{model_type} modeli renk spektrumu sınıflandırması",
            "algorithm": "color_spectrum",
            "parameters": {
                "divisions": divisions,
                "saturation_levels": saturation_levels,
                "value_levels": value_levels,
                "dominant_color_method": dominant_color_method
            },
            "clusters": {}
        }
    
    # Mevcut version verisi
    version_data = model_data["versions"][version]
    
    # Önceki cluster'ları temizle (eğer varsa)
    version_data["clusters"] = {}
    
    # Her ton bölümü bir küme olacak
    for h_idx, hue_div in enumerate(spectrum["hue_divisions"]):
        # Ton adı
        hue_name = hue_div["name"]
        
        # Küme üyelerini topla
        members = []
        for sat_group in hue_div["saturation_groups"]:
            for val_group in sat_group["value_groups"]:
                members.extend(val_group["members"])
        
        # Boş kümeleri atla
        if not members:
            continue
        
        # Bir temsilci seç (ilk üye)
        representative = members[0] if members else None
        
        # Kümeyi oluştur
        cluster_name = f"cluster-{h_idx}"
        
        version_data["clusters"][cluster_name] = {
            "representative": representative,
            "images": members,
            "comment": f"{hue_name} ton grubu"
        }
    
    # Nadir renkler (düşük doygunluk) için özel bir küme
    rare_colors = []
    for h_idx, hue_div in enumerate(spectrum["hue_divisions"]):
        # En düşük doygunluk
        lowest_sat_group = hue_div["saturation_groups"][0]
        for val_group in lowest_sat_group["value_groups"]:
            rare_colors.extend(val_group["members"])
    
    # Nadir renkler kümesi (boş değilse)
    if rare_colors:
        representative = rare_colors[0] if rare_colors else None
        version_data["clusters"]["rare_colors"] = {
            "representative": representative,
            "images": rare_colors,
            "comment": "Düşük doygunluklu renkler (griler, beyazlar, siyahlar)"
        }
    
    # Thumbnail'leri kopyala
    start_copy_time = time.time()
    copied_count = 0
    
    for cluster_name, cluster_data in version_data["clusters"].items():
        for filename in cluster_data["images"]:
            src_thumb = os.path.join("thumbnails", filename)
            dst_thumb = os.path.join(thumbnail_dir, filename)
            
            if os.path.exists(src_thumb):
                shutil.copy2(src_thumb, dst_thumb)
                copied_count += 1
    
    copy_duration = time.time() - start_copy_time
    
    # Detaylı bir log dosyası oluştur
    log_path = os.path.join(output_dir, "color_cluster_log.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Algoritma: color_spectrum\n")
        log_file.write(f"Toplam küme sayısı: {len(version_data['clusters'])}\n")
        log_file.write(f"Ton bölüm sayısı: {divisions}\n")
        log_file.write(f"Doygunluk seviye sayısı: {saturation_levels}\n")
        log_file.write(f"Parlaklık seviye sayısı: {value_levels}\n")
        log_file.write(f"Dominant renk çıkarma yöntemi: {dominant_color_method}\n")
        
        # Küme boyutları analizi
        log_file.write("\nKüme boyutları:\n")
        for cluster_name, cluster_data in sorted(
            version_data["clusters"].items(), 
            key=lambda x: len(x[1]["images"]), 
            reverse=True
        ):
            log_file.write(f"  {cluster_name}: {len(cluster_data['images'])} görsel\n")
        
        # Renk spektrumu istatistikleri
        log_file.write("\nRenk spektrumu istatistikleri:\n")
        log_file.write(f"  Toplam görsel: {stats['total_images']}\n")
        log_file.write(f"  Dolu gruplar: {stats['filled_groups']}\n")
        log_file.write(f"  Boş gruplar: {stats['empty_groups']}\n")
        log_file.write(f"  En büyük grup: {stats['largest_group']['name']} ({stats['largest_group']['count']} görsel)\n")
        
        # Ton dağılımı
        log_file.write("\nTon (Hue) Dağılımı:\n")
        for key, value in stats["hue_distribution"].items():
            log_file.write(f"  {key}: %{value}\n")
        
        # Doygunluk dağılımı
        log_file.write("\nDoygunluk (Saturation) Dağılımı:\n")
        for key, value in stats["saturation_distribution"].items():
            log_file.write(f"  {key}: %{value}\n")
        
        # Parlaklık dağılımı
        log_file.write("\nParlaklık (Value) Dağılımı:\n")
        for key, value in stats["value_distribution"].items():
            log_file.write(f"  {key}: %{value}\n")
    
    # Renk spektrumunu kaydet
    spectrum_path = os.path.join(output_dir, "color_spectrum.json")
    with open(spectrum_path, "w", encoding="utf-8") as f:
        json.dump(spectrum, f, ensure_ascii=False, indent=2)
    
    # Metadata update - kısa yoldan
    if os.path.exists("image_metadata_map.json"):
        try:
            with open("image_metadata_map.json", "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # Her clusterdaki görsellerin metadata'sını güncelle
            for cluster_name, cluster_data in version_data["clusters"].items():
                for img in cluster_data["images"]:
                    if img in metadata:
                        metadata[img]["cluster"] = cluster_name
            
            # Metadata'yı kaydet
            with open("image_metadata_map.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Metadata güncelleme hatası: {str(e)}")
    
    # Güncel versiyonu ayarla
    model_data["current_version"] = version
    
    # Model verisini kaydet
    save_model_data(model_type, model_data)
    
    # İşlem süresi
    total_duration = time.time() - start_time
    
    # Özet bilgileri
    total_clusters = len(version_data['clusters'])
    total_images = sum(len(cluster['images']) for cluster in version_data['clusters'].values())
    
    print(f"✅ Renk spektrumu sınıflandırması tamamlandı.")
    print(f"   - {total_clusters} küme oluşturuldu")
    print(f"   - {total_images} görsel kümelere atandı")
    print(f"   - Klasör: {output_dir}")
    print(f"   - Toplam süre: {total_duration:.2f} saniye")
    
    return version_data

def cluster_images(
    config: Dict
) -> Dict:
    """
    Kümeleme işlemi için ana giriş noktası.
    auto_cluster.py ile uyumlu olması için bu fonksiyon oluşturuldu.
    
    Args:
        config: Konfigürasyon parametreleri
        
    Returns:
        Oluşturulan versiyon verisi
    """
    model_type = config.get("model_type")
    version = config.get("version", "v1")
    
    # Renk modeli için özel parametre kontrolü
    if model_type == "color":
        # Renk modeli için spektrum bazlı sınıflandırma
        divisions = int(config.get("divisions", 12))
        saturation_levels = int(config.get("saturation_levels", 3))
        value_levels = int(config.get("value_levels", 3))
        
        return create_color_clusters(
            model_type=model_type,
            version=version,
            divisions=divisions,
            saturation_levels=saturation_levels,
            value_levels=value_levels
        )
    else:
        # Diğer modeller için standart kümeleme
        from auto_cluster import main as auto_cluster_main
        return auto_cluster_main(config)

def main(config_path: str = "cluster_config.json") -> Dict:
    """
    Konfigürasyon dosyasını okuyarak kümeleme işlemini başlatır.
    
    Args:
        config_path: Konfigürasyon dosyasının yolu
        
    Returns:
        Oluşturulan versiyon verisi
    """
    # Konfigürasyon dosyasını oku
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return cluster_images(config)

if __name__ == "__main__":
    # Örnek konfigürasyon
    config = {
        "model_type": "color",
        "version": "spectrum_v1",
        "divisions": 12,
        "saturation_levels": 3,
        "value_levels": 3
    }
    
    # Konfigürasyon dosyasını kaydet
    with open("color_cluster_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Renk sınıflandırmasını çalıştır
    main("color_cluster_config.json")
