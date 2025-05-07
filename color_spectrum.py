# Global önbellek temizleme fonksiyonu
def clear_color_cache():
    """Renk önbelleklerini temizler"""
    global _cached_color_index, _cached_color_mapping, _cached_spectrum
    _cached_color_index = None
    _cached_color_mapping = None
    _cached_spectrum = None
    print("DEBUG: Renk önbellekleri temizlendi")
    return True

"""
Renk spektrumu yönetimi için modül.

Bu modül, HSV renk uzayında ton (hue), doygunluk (saturation) ve parlaklık (value)
bölümleri ile doğal bir renk organizasyonu sağlar. Renk modeli için kümeleme
algoritmaları yerine daha doğal bir renk aralığı organizasyonu sunar.
"""

import os
import json
import time
import numpy as np
from typing import Tuple, List, Dict, Union, Optional, Any


# color_spectrum.py dosyasına eklenecek

# Global önbellek değişkenleri
_cached_color_index = None
_cached_color_mapping = None
_cached_spectrum = None

def get_cached_spectrum():
    """Önbellekten renk spektrumunu döndürür, yoksa yükler"""
    global _cached_spectrum
    
    if _cached_spectrum is not None:
        return _cached_spectrum
    
    spectrum_file = "color_spectrum.json"
    if os.path.exists(spectrum_file):
        try:
            with open(spectrum_file, "r", encoding="utf-8") as f:
                _cached_spectrum = json.load(f)
            print(f"✅ Renk spektrumu yüklendi: {len(_cached_spectrum.get('hue_divisions', []))} bölüm")
            return _cached_spectrum
        except Exception as e:
            print(f"❌ Renk spektrumu yükleme hatası: {str(e)}")
    
    return build_color_spectrum()  # Varsayılan boş spektrum

def get_cached_faiss_index():
    """Önbellekten Faiss indeksini döndürür, yoksa oluşturur"""
    global _cached_color_index, _cached_color_mapping
    
    if _cached_color_index is not None and _cached_color_mapping is not None:
        return _cached_color_index, _cached_color_mapping
    
    # Spektrumu al
    spectrum = get_cached_spectrum()
    
    # Faiss indeksini oluştur
    try:
        # Faiss'i import et
        import faiss
        print("✅ Faiss kütüphanesi import edildi")
        
        print("⚡ Renk spektrumu Faiss indeksi oluşturuluyor...")
        _cached_color_index, _cached_color_mapping = create_faiss_index_for_colors(spectrum)
        print(f"✅ Renk spektrumu indeksi oluşturuldu: {len(_cached_color_mapping['id_to_filename'])} görsel")
    except ImportError:
        print("❌ Faiss kütüphanesi bulunamadı! Basit benzerlik hesaplaması kullanılacak.")
        return None, None
    except Exception as e:
        print(f"❌ Renk spektrumu indeksi oluşturma hatası: {str(e)}")
        return None, None
    
    return _cached_color_index, _cached_color_mapping




# color_utils modülünden gerekli fonksiyonları import et
from color_utils import (
    rgb_to_hsv, hsv_to_rgb, 
    calculate_hsv_distance, calculate_hue_distance,
    extract_dominant_color_improved,
    identify_color_group
)


def build_color_spectrum(
    divisions: int = 12, 
    saturation_levels: int = 3, 
    value_levels: int = 3
) -> Dict:
    """
    Renk spektrumu yapısını oluşturur.
    
    Args:
        divisions: Ton (hue) bölünme sayısı (varsayılan: 12 - 30 derecelik dilimler)
        saturation_levels: Doygunluk (saturation) seviye sayısı (varsayılan: 3)
        value_levels: Parlaklık (value) seviye sayısı (varsayılan: 3)
        
    Returns:
        Renk spektrumu yapısını içeren sözlük
    """
    # Renk spektrumu yapısı
    spectrum = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "divisions": divisions,
        "saturation_levels": saturation_levels,
        "value_levels": value_levels,
        "hue_divisions": [],
        "total_images": 0
    }
    
    # Renk isimleri (12 bölüm için - her biri 30 derecelik dilimler)
    hue_names = [
        "Kırmızı", "Kırmızı-Turuncu", "Turuncu", "Sarı-Turuncu", 
        "Sarı", "Sarı-Yeşil", "Yeşil", "Turkuaz", 
        "Cyan", "Mavi", "Mor", "Magenta"
    ]
    
    # Doygunluk isimleri
    saturation_names = ["Soluk", "Orta", "Canlı"]
    
    # Parlaklık isimleri
    value_names = ["Koyu", "Orta", "Açık"]
    
    # Bölümleri oluştur
    for i in range(divisions):
        # Ton bölümü
        hue_start = i / divisions
        hue_end = (i + 1) / divisions
        
        if i < len(hue_names):
            hue_name = hue_names[i]
        else:
            hue_name = f"Ton-{i+1}"
        
        hue_division = {
            "index": i,
            "name": hue_name,
            "hue_range": (hue_start, hue_end),
            "center_hue": (hue_start + hue_end) / 2,
            "saturation_groups": []
        }
        
        # Doygunluk seviyeleri
        for s in range(saturation_levels):
            sat_start = s / saturation_levels
            sat_end = (s + 1) / saturation_levels
            
            if s < len(saturation_names):
                sat_name = saturation_names[s]
            else:
                sat_name = f"S-{s+1}"
            
            saturation_group = {
                "index": s,
                "name": sat_name,
                "saturation_range": (sat_start, sat_end),
                "center_saturation": (sat_start + sat_end) / 2,
                "value_groups": []
            }
            
            # Parlaklık seviyeleri
            for v in range(value_levels):
                val_start = v / value_levels
                val_end = (v + 1) / value_levels
                
                if v < len(value_names):
                    val_name = value_names[v]
                else:
                    val_name = f"V-{v+1}"
                
                value_group = {
                    "index": v,
                    "name": val_name,
                    "value_range": (val_start, val_end),
                    "center_value": (val_start + val_end) / 2,
                    "members": []  # Görseller burada saklanacak
                }
                
                saturation_group["value_groups"].append(value_group)
            
            hue_division["saturation_groups"].append(saturation_group)
        
        spectrum["hue_divisions"].append(hue_division)
    
    return spectrum


def classify_color_in_spectrum(
    hsv: Tuple[float, float, float], 
    spectrum: Dict
) -> Tuple[int, int, int]:
    """
    Bir HSV renk değerini renk spektrumunda sınıflandırır.
    
    Args:
        hsv: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        spectrum: Renk spektrumu yapısı
        
    Returns:
        (hue_index, saturation_index, value_index) sınıflandırma indeksleri
    """
    h, s, v = hsv
    
    # Ton (Hue) indeksini bul
    divisions = spectrum["divisions"]
    hue_index = int(h * divisions) % divisions
    
    # Doygunluk (Saturation) indeksini bul
    saturation_levels = spectrum["saturation_levels"]
    saturation_index = min(int(s * saturation_levels), saturation_levels - 1)
    
    # Parlaklık (Value) indeksini bul
    value_levels = spectrum["value_levels"]
    value_index = min(int(v * value_levels), value_levels - 1)
    
    return (hue_index, saturation_index, value_index)


def add_image_to_spectrum(
    image_path: str, 
    spectrum: Dict, 
    method: str = 'histogram'
) -> Dict:
    """
    Bir görseli renk spektrumuna ekler.
    
    Args:
        image_path: Görsel dosyasının yolu
        spectrum: Renk spektrumu yapısı
        method: Dominant renk çıkarma yöntemi ('histogram' veya 'kmeans')
        
    Returns:
        Eklenen görselin renk bilgilerini içeren sözlük
    """
    # Dosya adını al
    filename = os.path.basename(image_path)
    
    # Dominant rengi çıkar
    dominant_rgb = extract_dominant_color_improved(image_path, method=method)
    dominant_hsv = rgb_to_hsv(dominant_rgb)
    
    # Renk grubunu belirle
    color_group = identify_color_group(dominant_hsv)
    
    # Spektrumda sınıflandır
    indices = classify_color_in_spectrum(dominant_hsv, spectrum)
    hue_idx, sat_idx, val_idx = indices
    
    # Görseli ilgili gruba ekle
    hue_div = spectrum["hue_divisions"][hue_idx]
    sat_group = hue_div["saturation_groups"][sat_idx]
    val_group = sat_group["value_groups"][val_idx]
    
    # Eğer aynı dosya zaten varsa ekleme
    if filename not in val_group["members"]:
        val_group["members"].append(filename)
        spectrum["total_images"] += 1
    
    # Renk bilgilerini döndür
    return {
        "filename": filename,
        "dominant_color": dominant_rgb,
        "hsv": dominant_hsv,
        "color_group": color_group,
        "indices": indices,
        "group_name": f"{val_group['name']} {sat_group['name']} {hue_div['name']}"
    }


def build_spectrum_from_directory(
    directory: str, 
    divisions: int = 12, 
    saturation_levels: int = 3, 
    value_levels: int = 3,
    method: str = 'histogram'
) -> Dict:
    """
    Bir klasördeki tüm görsellerden renk spektrumu oluşturur.
    
    Args:
        directory: Görsellerin bulunduğu klasör
        divisions: Ton (hue) bölünme sayısı
        saturation_levels: Doygunluk seviye sayısı
        value_levels: Parlaklık seviye sayısı
        method: Dominant renk çıkarma yöntemi
        
    Returns:
        Oluşturulan renk spektrumu yapısı
    """
    # Boş spektrum oluştur
    spectrum = build_color_spectrum(divisions, saturation_levels, value_levels)
    
    # Klasördeki tüm görselleri bul
    image_files = [f for f in os.listdir(directory) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    print(f"✅ {len(image_files)} görsel bulundu, spektrum oluşturuluyor...")
    
    # Her görseli spektruma ekle
    for i, img_file in enumerate(image_files):
        if i % 100 == 0 and i > 0:
            print(f"✅ {i}/{len(image_files)} görsel işlendi...")
        
        try:
            img_path = os.path.join(directory, img_file)
            add_image_to_spectrum(img_path, spectrum, method)
        except Exception as e:
            print(f"⚠️ Görsel işleme hatası ({img_file}): {str(e)}")
    
    print(f"✅ Renk spektrumu oluşturuldu ({spectrum['total_images']} görsel)")
    return spectrum


def export_spectrum_version(
    spectrum: Dict, 
    version_name: str = "v1", 
    model_type: str = "color",
    comment: str = ""
) -> Dict:
    """
    Renk spektrumunu bir versiyon olarak dışa aktarır.
    
    Args:
        spectrum: Renk spektrumu yapısı
        version_name: Versiyon adı
        model_type: Model tipi (ör: "color")
        comment: Versiyon açıklaması
        
    Returns:
        Versiyon bilgilerini içeren sözlük
    """
    # Versiyon klasörünü kontrol et
    export_dir = f"exported_clusters/{model_type}"
    version_dir = f"{export_dir}/{version_name}"
    
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)
    
    # Versiyon bilgilerini hazırla
    version_info = {
        "name": version_name,
        "model_type": model_type,
        "comment": comment,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "algorithm": "color_spectrum",
        "parameters": {
            "divisions": spectrum["divisions"],
            "saturation_levels": spectrum["saturation_levels"],
            "value_levels": spectrum["value_levels"]
        },
        "clusters": []
    }
    
    # Renk gruplarını cluster olarak aktar
    cluster_count = 0
    
    for h_idx, hue_div in enumerate(spectrum["hue_divisions"]):
        for s_idx, sat_group in enumerate(hue_div["saturation_groups"]):
            for v_idx, val_group in enumerate(sat_group["value_groups"]):
                members = val_group["members"]
                
                # Boş grupları atla
                if not members:
                    continue
                
                # Grup adını belirle
                group_name = f"{val_group['name']} {sat_group['name']} {hue_div['name']}"
                
                # Cluster oluştur
                cluster = {
                    "id": cluster_count,
                    "name": group_name,
                    "indices": [h_idx, s_idx, v_idx],
                    "center_color": [
                        int(hue_div["center_hue"] * 360),  # 0-360 derece
                        int(sat_group["center_saturation"] * 100),  # 0-100%
                        int(val_group["center_value"] * 100)  # 0-100%
                    ],
                    "members": members.copy()
                }
                
                # Cluster'a ekle
                version_info["clusters"].append(cluster)
                cluster_count += 1
    
    # Versiyonlar dosyasını güncelle
    versions_file = f"{export_dir}/versions.json"
    versions_data = {"versions": {}}
    
    if os.path.exists(versions_file):
        with open(versions_file, "r", encoding="utf-8") as f:
            try:
                versions_data = json.load(f)
            except:
                pass
    
    # Yeni versiyonu ekle
    versions_data["versions"][version_name] = {
        "name": version_name,
        "comment": comment,
        "created_at": version_info["created_at"],
        "algorithm": "color_spectrum",
        "parameters": version_info["parameters"],
        "cluster_count": cluster_count
    }
    
    # Versiyonlar dosyasını kaydet
    with open(versions_file, "w", encoding="utf-8") as f:
        json.dump(versions_data, f, ensure_ascii=False, indent=2)
    
    # Versiyon bilgisini kaydet
    version_file = f"{version_dir}/info.json"
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(version_info, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Renk spektrumu versiyonu dışa aktarıldı: {model_type}/{version_name}")
    return version_info


def get_color_group_name(indices: Tuple[int, int, int], spectrum: Dict) -> str:
    """
    Verilen spektrum indekslerine göre renk grubu adını döndürür.
    
    Args:
        indices: (hue_index, saturation_index, value_index) indeksleri
        spectrum: Renk spektrumu yapısı
        
    Returns:
        Renk grubu adı
    """
    h_idx, s_idx, v_idx = indices
    
    try:
        hue_div = spectrum["hue_divisions"][h_idx]
        sat_group = hue_div["saturation_groups"][s_idx]
        val_group = sat_group["value_groups"][v_idx]
        
        return f"{val_group['name']} {sat_group['name']} {hue_div['name']}"
    except:
        return "Bilinmeyen Grup"


def get_color_spectrum_statistics(spectrum: Dict) -> Dict:
    """
    Renk spektrumu istatistiklerini hesaplar.
    
    Args:
        spectrum: Renk spektrumu yapısı
        
    Returns:
        İstatistik bilgilerini içeren sözlük
    """
    stats = {
        "total_images": spectrum["total_images"],
        "filled_groups": 0,
        "empty_groups": 0,
        "largest_group": {"name": "", "count": 0},
        "hue_distribution": {},
        "saturation_distribution": {},
        "value_distribution": {}
    }
    
    # Dağılımları başlat
    for h_idx, hue_div in enumerate(spectrum["hue_divisions"]):
        stats["hue_distribution"][hue_div["name"]] = 0
    
    saturation_names = ["Soluk", "Orta", "Canlı"]
    for s_idx in range(spectrum["saturation_levels"]):
        if s_idx < len(saturation_names):
            sat_name = saturation_names[s_idx]
        else:
            sat_name = f"S-{s_idx+1}"
        stats["saturation_distribution"][sat_name] = 0
    
    value_names = ["Koyu", "Orta", "Açık"]
    for v_idx in range(spectrum["value_levels"]):
        if v_idx < len(value_names):
            val_name = value_names[v_idx]
        else:
            val_name = f"V-{v_idx+1}"
        stats["value_distribution"][val_name] = 0
    
    # İstatistikleri hesapla
    for h_idx, hue_div in enumerate(spectrum["hue_divisions"]):
        for s_idx, sat_group in enumerate(hue_div["saturation_groups"]):
            for v_idx, val_group in enumerate(sat_group["value_groups"]):
                members = val_group["members"]
                count = len(members)
                
                # Grup adı
                group_name = get_color_group_name((h_idx, s_idx, v_idx), spectrum)
                
                # Dolu/boş grup sayısı
                if count > 0:
                    stats["filled_groups"] += 1
                    
                    # Dağılımlara ekle
                    stats["hue_distribution"][hue_div["name"]] += count
                    stats["saturation_distribution"][sat_group["name"]] += count
                    stats["value_distribution"][val_group["name"]] += count
                    
                    # En büyük grup güncellemesi
                    if count > stats["largest_group"]["count"]:
                        stats["largest_group"] = {
                            "name": group_name,
                            "count": count,
                            "indices": (h_idx, s_idx, v_idx)
                        }
                else:
                    stats["empty_groups"] += 1
    
    # Dağılım yüzdeleri
    total = stats["total_images"]
    if total > 0:
        for key in stats["hue_distribution"]:
            stats["hue_distribution"][key] = round(stats["hue_distribution"][key] / total * 100, 1)
        
        for key in stats["saturation_distribution"]:
            stats["saturation_distribution"][key] = round(stats["saturation_distribution"][key] / total * 100, 1)
        
        for key in stats["value_distribution"]:
            stats["value_distribution"][key] = round(stats["value_distribution"][key] / total * 100, 1)
    
    return stats

def create_faiss_index_for_colors(
    spectrum: Dict, 
    use_hsv: bool = True, 
    normalized: bool = True
) -> Tuple[Any, Dict]:
    """
    Renk spektrumu için Faiss indeksi oluşturur.
    
    Args:
        spectrum: Renk spektrumu yapısı
        use_hsv: HSV renk uzayı kullanma (True) veya RGB kullanma (False)
        normalized: HSV değerlerini normalize etme
        
    Returns:
        (faiss_index, index_mapping) tuple'ı
    """
    import faiss
    import numpy as np
    
    # Görsel sayacı ve haritalama hazırla
    total_images = spectrum["total_images"]
    index_mapping = {"id_to_filename": {}, "filename_to_id": {}}
    
    if total_images == 0:
        print("⚠️ Spektrumda görsel yok, indeks oluşturulamıyor.")
        return None, index_mapping
    
    # Görüntü özellik vektörlerini ve ID'leri topla
    features = []
    image_ids = []
    id_counter = 0
    
    for h_idx, hue_div in enumerate(spectrum["hue_divisions"]):
        for s_idx, sat_group in enumerate(hue_div["saturation_groups"]):
            for v_idx, val_group in enumerate(sat_group["value_groups"]):
                members = val_group["members"]
                
                if not members:
                    continue
                
                # Her görsel için
                for filename in members:
                    # HSV renk uzayında grup merkez noktası
                    h = hue_div["center_hue"]
                    s = sat_group["center_saturation"]
                    v = val_group["center_value"]
                    
                    if use_hsv:
                        # HSV renk vektörü
                        if normalized:
                            # HSV [0-1] normalize edilmiş
                            feature = np.array([h, s, v], dtype=np.float32)
                        else:
                            # HSV [0-360, 0-100, 0-100] normalize edilmemiş
                            feature = np.array([h * 360, s * 100, v * 100], dtype=np.float32)
                    else:
                        # RGB renk vektörü
                        rgb = hsv_to_rgb((h, s, v))
                        feature = np.array(rgb, dtype=np.float32)
                    
                    features.append(feature)
                    image_ids.append(id_counter)
                    
                    # ID'den dosya adına ve tersine eşleme
                    index_mapping["id_to_filename"][id_counter] = filename
                    index_mapping["filename_to_id"][filename] = id_counter
                    
                    id_counter += 1
    
    # Numpy dizisine dönüştür
    features_array = np.array(features)
    
    # Vektör boyutu
    d = features_array.shape[1]  # 3 (HSV veya RGB)
    
    # Faiss indeksi oluştur
    if use_hsv and normalized:
        # HSV için kosinüs benzerliği (iç çarpım) - normalize edilmiş için
        index = faiss.IndexFlatIP(d)
    else:
        # L2 mesafesi (öklid) - hem RGB hem de normalize edilmemiş HSV için
        index = faiss.IndexFlatL2(d)
    
    # Vektörleri indekse ekle
    index.add(features_array)
    
    print(f"✅ Faiss indeksi oluşturuldu: {id_counter} görsel, {d} boyutlu vektörler")
    return index, index_mapping

def find_similar_colors_with_faiss(
    hsv: Tuple[float, float, float],
    faiss_index: Any,
    index_mapping: Dict,
    k: int = 50,
    use_hsv: bool = True,
    normalized: bool = True
) -> List[Dict]:
    """
    Faiss kullanarak benzer renklere sahip görselleri arar.
    
    Args:
        hsv: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        faiss_index: Faiss indeksi
        index_mapping: ID'den dosya adına eşleme sözlüğü
        k: Döndürülecek sonuç sayısı
        use_hsv: HSV renk uzayı kullanma (True) veya RGB kullanma (False)
        normalized: HSV değerlerini normalize etme
        
    Returns:
        Benzer renklere sahip görsellerin listesi
    """
    import numpy as np
    
    print(f"DEBUG: find_similar_colors_with_faiss çağrıldı - hsv={hsv}, k={k}")
    
    # index_mapping kontrolü
    if not index_mapping or "id_to_filename" not in index_mapping or not index_mapping["id_to_filename"]:
        print(f"HATA: index_mapping boş veya geçersiz: {index_mapping}")
        return []
    
    # Sorgu vektörü hazırla
    if use_hsv:
        if normalized:
            # HSV [0-1] normalize edilmiş
            query_vector = np.array([[hsv[0], hsv[1], hsv[2]]], dtype=np.float32)
        else:
            # HSV [0-360, 0-100, 0-100] normalize edilmemiş
            query_vector = np.array([[hsv[0] * 360, hsv[1] * 100, hsv[2] * 100]], dtype=np.float32)
    else:
        # RGB renk vektörü
        rgb = hsv_to_rgb(hsv)
        query_vector = np.array([rgb], dtype=np.float32)
    
    print(f"DEBUG: Sorgu vektörü hazırlandı: {query_vector}")
    
    # Benzerlik araması yap
    try:
        distances, indices = faiss_index.search(query_vector, k)
        print(f"DEBUG: Faiss arama sonucu: {len(indices[0])} adet indeks bulundu")
    except Exception as e:
        import traceback
        print(f"HATA: Faiss arama hatası: {str(e)}")
        print(traceback.format_exc())
        return []
    
    # Sonuçları hazırla
    results = []
    for i, idx in enumerate(indices[0]):
        # Geçersiz indeks kontrolü
        if idx < 0:
            print(f"DEBUG: Geçersiz indeks: {idx}")
            continue
        
        # Dosya adını ve benzerlik skorunu al
        try:
            # Önce doğrudan indeks erişimi dene
            if idx in index_mapping["id_to_filename"]:
                filename = index_mapping["id_to_filename"][idx]
            elif str(idx) in index_mapping["id_to_filename"]:
                # String anahtar olarak dene
                filename = index_mapping["id_to_filename"][str(idx)]
            else:
                # Geçersiz indeks - atla
                print(f"DEBUG: Anahtarlar arasında bulunamadı: {idx}")
                continue
        except Exception as e:
            print(f"HATA: Dosya adı alma hatası - {idx}: {str(e)}")
            continue
                
        distance = float(distances[0][i])
        
        # Benzerlik hesapla (mesafe tipine göre)
        if use_hsv and normalized:
            # İç çarpım mesafesi için [0,2] aralığını [0,1] benzerliğe dönüştür
            similarity = 1.0 - distance / 2.0
        else:
            # L2 mesafesi için tersine dönüştür
            max_distance = 100.0 if not normalized else 1.0
            similarity = 1.0 - min(1.0, distance / max_distance)
        
        results.append({
            "filename": filename,
            "similarity": similarity,
            "distance": distance
        })
    
    # Sonuçları benzerliğe göre sırala
    results.sort(key=lambda x: x['similarity'], reverse=True)
    print(f"DEBUG: Toplam {len(results)} sonuç döndürülüyor")
    
    return results


def find_similar_colors_optimized(
    hsv_color: Tuple[float, float, float],
    limit: int = 100
) -> List[dict]:
    """Basitleştirilmiş renk benzerliği fonksiyonu"""
    print(f"DEBUG: find_similar_colors_optimized çağrıldı - HSV={hsv_color}")
    
    if not hsv_color or len(hsv_color) != 3:
        print(f"HATA: Geçersiz HSV değeri: {hsv_color}")
        return []
        
    h, s, v = hsv_color
    if not (0 <= h <= 1 and 0 <= s <= 1 and 0 <= v <= 1):
        print(f"UYARI: HSV değerleri [0-1] aralığında değil: {hsv_color}")
        # Değerleri sınırla
        h = max(0, min(1, h))
        s = max(0, min(1, s))
        v = max(0, min(1, v))
        hsv_color = (h, s, v)
        print(f"Düzeltildi: {hsv_color}")
    
    # Önce Faiss indeksini almaya çalış
    faiss_index, index_mapping = get_cached_faiss_index()
    
    # Eğer Faiss indeksi oluşturulabilirse, onu kullan
    if faiss_index is not None and index_mapping is not None:
        try:
            # Kendisini import etmek yerine mevcut modüldeki fonksiyonu kullan
            # from color_spectrum import find_similar_colors_with_faiss
            print(f"DEBUG: find_similar_colors_with_faiss çağrılıyor - k={limit}")
            results = find_similar_colors_with_faiss(
                hsv=hsv_color,
                faiss_index=faiss_index,
                index_mapping=index_mapping,
                k=limit,
                use_hsv=True,
                normalized=True
            )
            print(f"✅ Faiss ile {len(results)} benzer renk bulundu")
            return results
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Faiss araması hatası: {str(e)}")
            print(f"Hata detayları: {error_details}")
            # Hata durumunda alternatif yönteme geç
    
    # Basit renk benzerliği hesaplama
    print("⚠️ Alternatif renk benzerliği hesaplama kullanılıyor...")
    results = []
    try:
        # realImages klasöründeki tüm görselleri tara
        image_path = "realImages"
        if os.path.exists(image_path):
            from color_utils import extract_dominant_color_improved, rgb_to_hsv, calculate_hsv_distance, identify_color_group
            import os
            
            # Performans için kısıtlı sayıda görsel işle
            file_limit = min(1000, limit * 10)  # En fazla 1000 görsel
            image_files = [f for f in os.listdir(image_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))][:file_limit]
            
            print(f"⚡ {len(image_files)} görsel işleniyor...")
            for filename in image_files:
                try:
                    img_path = os.path.join(image_path, filename)
                    dominant_rgb = extract_dominant_color_improved(img_path, method='histogram')
                    img_hsv = rgb_to_hsv(dominant_rgb)
                    
                    # Renk benzerliği hesapla
                    distance = calculate_hsv_distance(hsv_color, img_hsv)
                    similarity = 1.0 - distance
                    
                    results.append({
                        'filename': filename,
                        'dominant_color': dominant_rgb,
                        'color_group': identify_color_group(img_hsv),
                        'hsv': img_hsv,
                        'similarity': similarity,
                        'group_name': f"Benzerlik: {similarity:.2f}"
                    })
                except Exception as e:
                    print(f"⚠️ Görsel işleme hatası ({filename}): {str(e)}")
    except Exception as e:
        import traceback
        print(f"❌ Renk benzerliği hesaplama hatası: {str(e)}")
        print(traceback.format_exc())
    
    # Benzerliğe göre sırala
    results.sort(key=lambda x: x['similarity'], reverse=True)
    print(f"✅ {len(results)} benzer renk bulundu (basit hesaplama)")
    
    # Sonuç sayısını sınırla
    return results[:limit]



def _fallback_similar_colors_search(hsv_color: Tuple[float, float, float], limit: int = 100) -> List[dict]:
    """
    Faiss indeksi bulunamadığında kullanılacak alternatif benzerlik arama.
    
    Bu fonksiyon, tüm görsel dosyalarını tarar ve renk benzerliğini manuel hesaplar.
    """
    print("DEBUG: Alternatif renk araması başladı")
    import os
    from color_utils import extract_dominant_color_improved, rgb_to_hsv, calculate_hsv_distance, identify_color_group
    
    results = []
    
    # realImages klasöründeki tüm görselleri tara
    image_path = "realImages"
    if os.path.exists(image_path):
        count = 0
        for filename in os.listdir(image_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                count += 1
                if count > 1000:  # En fazla 1000 görsel tara (performans için)
                    break
                
                try:
                    img_path = os.path.join(image_path, filename)
                    dominant_rgb = extract_dominant_color_improved(img_path, method='histogram')
                    img_hsv = rgb_to_hsv(dominant_rgb)
                    
                    # Renk benzerliği hesapla
                    distance = calculate_hsv_distance(hsv_color, img_hsv)
                    similarity = 1.0 - distance
                    
                    results.append({
                        'filename': filename,
                        'dominant_color': dominant_rgb,
                        'color_group': identify_color_group(img_hsv),
                        'hsv': img_hsv,
                        'similarity': similarity,
                        'group_name': f"Benzerlik: {similarity:.2f}"
                    })
                except Exception as e:
                    print(f"DEBUG: Görsel işleme hatası ({filename}): {str(e)}")
    
    # Benzerliğe göre sırala
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Sonuç sayısını sınırla
    return results[:limit]


# Önbellek değişkenleri
_cached_color_index = None
_cached_color_mapping = None
_cached_spectrum = None

def clear_color_cache():
    """
    Renk spektrumu önbelleğini ve Faiss indeksini temizler.
    Bu fonksiyon, uygulama çalışırken önbellekleri sıfırlamak için kullanılır.
    """
    global _cached_color_index, _cached_color_mapping, _cached_spectrum
    _cached_color_index = None
    _cached_color_mapping = None
    _cached_spectrum = None
    
    print("\n🔄 Renk spektrumu önbelleği temizlendi")
    return True

def get_cached_spectrum():
    """Önbellekten renk spektrumunu döndürür, yoksa yükler"""
    global _cached_spectrum
    if _cached_spectrum is None:
        # Spektrum dosyasını kontrol et
        spectrum_path = "exported_clusters/color/spectrum.json"
        if os.path.exists(spectrum_path):
            try:
                with open(spectrum_path, "r", encoding="utf-8") as f:
                    _cached_spectrum = json.load(f)
                print(f"\n✅ Renk spektrumu önbellekten yüklendi")
            except Exception as e:
                print(f"\n❌ Spektrum yükleme hatası: {str(e)}")
                # Hata durumunda boş spektrum oluştur
                _cached_spectrum = build_color_spectrum()
    return _cached_spectrum

def get_cached_faiss_index():
    """Önbellekten Faiss indeksini döndürür, yoksa oluşturur"""
    global _cached_color_index, _cached_color_mapping
    if _cached_color_index is None:
        # Faiss indeks dosyasını kontrol et
        index_path = "exported_clusters/color/faiss_index.bin"
        mapping_path = "exported_clusters/color/index_mapping.json"
        
        if os.path.exists(index_path) and os.path.exists(mapping_path):
            try:
                import faiss
                _cached_color_index = faiss.read_index(index_path)
                
                with open(mapping_path, "r", encoding="utf-8") as f:
                    _cached_color_mapping = json.load(f)
                    
                print(f"\n✅ Faiss indeksi önbellekten yüklendi")
            except Exception as e:
                print(f"\n❌ Faiss indeksi yükleme hatası: {str(e)}")
                # Hata durumunda None döndür
                return None, None
    
    return _cached_color_index, _cached_color_mapping

def find_similar_colors_optimized(hsv_color, limit=100):
    """
    Basitleştirilmiş renk benzerliği fonksiyonu.
    Önce Faiss indeksini kullanmaya çalışır, olmuyorsa basit hesaplama yapar.
    
    Args:
        hsv_color: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        limit: Döndürülecek sonuç sayısı
        
    Returns:
        Benzer renkli görsellerin listesi
    """
    import time
    start_time = time.time()
    
    # Faiss kullansın mı? - şu an devre dışı bıraktık çünkü sonuçlar kötü geliyor
    use_faiss = False
    
    # Eğer Faiss kullanımı aktifse deneyebiliriz
    if use_faiss:
        try:
            import faiss
            faiss_index, index_mapping = get_cached_faiss_index()
            
            if faiss_index is not None and index_mapping is not None:
                results = find_similar_colors_with_faiss(
                    hsv_color, faiss_index, index_mapping, k=limit
                )
                print(f"\n✅ Faiss ile {len(results)} benzer renk bulundu ({time.time() - start_time:.3f}s)")
                return results
        except Exception as e:
            print(f"\n❌ Faiss kullanım hatası: {str(e)}")
    
    # Ana arama algoritması: HSV ton, doygunluk ve parlaklık değerlerine göre arama
    print(f"\n🔍 HSV bazlı renk benzerliği hesaplanıyor - Referans HSV: {hsv_color}")
    h, s, v = hsv_color
    
    # Tüm görsel bilgilerini yükle
    all_images_file = "exported_clusters/color/all_images_color_data.json"
    
    if os.path.exists(all_images_file):
        with open(all_images_file, "r", encoding="utf-8") as f:
            all_images = json.load(f)
            print(f"\n✅ {len(all_images)} görsel için renk verileri yüklendi")
    else:
        # Görsel bilgileri yoksa oluştur
        print(f"\n🔍 Renk verileri dosyası bulunamadı, görseller işleniyor...")
        all_images = {}
        image_files = [f for f in os.listdir("realImages") if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        print(f"\n✅ {len(image_files)} görsel bulundu, işleniyor...")
        
        # Tüm görsellerin dominant rengini hesapla
        for i, img_file in enumerate(image_files):
            if i % 100 == 0 and i > 0:
                print(f"\n✅ {i}/{len(image_files)} görsel işlendi...")
                
            try:
                img_path = os.path.join("realImages", img_file)
                rgb = extract_dominant_color_improved(img_path, method='histogram')
                img_hsv = rgb_to_hsv(rgb)
                img_group = identify_color_group(img_hsv)
                
                all_images[img_file] = {
                    "dominant_color": rgb,
                    "hsv": img_hsv,
                    "color_group": img_group
                }
            except Exception as e:
                print(f"Görsel işleme hatası ({img_file}): {str(e)}")
        
        # Renk verilerini kaydet (bir sonraki kullanım için)
        os.makedirs(os.path.dirname(all_images_file), exist_ok=True)
        with open(all_images_file, "w", encoding="utf-8") as f:
            json.dump(all_images, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Renk verileri {all_images_file} dosyasına kaydedildi")
    
    # Sonuçlar listesi
    results = []
    
    # Ton için özel dairesel uzaklık ağırlığı
    hue_weight = 0.65      # Ton, en önemli bileşen
    sat_weight = 0.25      # Doygunluk orta önemde
    val_weight = 0.1       # Parlaklık en az önemli
    
    # Benzerlik hesaplama - eşik değerleri HSV için optimize edildi
    hue_threshold = 0.15    # Ton için eşik (0-0.5 arası)
    saturation_threshold = 0.3  # Doygunluk için eşik (0-1 arası)
    value_threshold = 0.35      # Parlaklık için eşik (0-1 arası)
    
    # Benzerlik hesaplama
    print(f"\n🔍 Renk benzerliği hesaplanıyor...")
    count = 0
    for img_filename, img_data in all_images.items():
        img_hsv = img_data.get("hsv")
        if not img_hsv:
            continue
        
        # Renk bileşenlerini al
        img_h, img_s, img_v = img_hsv
        
        # Ton için dairesel mesafe (0-0.5 arası döner, 0.5 = tamamen zıt renkler)
        hue_distance = calculate_hue_distance(h, img_h)
        
        # Ton eşiğini kontrol et - eğer çok farklıysa hemen atla (performans için)
        if hue_distance > hue_threshold:
            continue
            
        # Doygunluk ve parlaklık için doğrusal mesafe
        saturation_distance = abs(s - img_s)
        value_distance = abs(v - img_v)
        
        # Doygunluk ve parlaklık eşiklerini kontrol et
        if saturation_distance > saturation_threshold or value_distance > value_threshold:
            continue
        
        # Tüm bileşenleri geçen görseller için ağırlıklı benzerlik skoru (0-1 arası)
        # Normalize edilmiş mesafeler: Ton 0-0.5, Doygunluk ve Parlaklık 0-1 aralıklarını 0-1 aralığına çeviriyoruz
        normalized_hue_distance = hue_distance * 2   # 0-0.5 -> 0-1
        
        # Ağırlıklı mesafe: Ağırlıklı ortalama
        weighted_distance = (
            (normalized_hue_distance * hue_weight) + 
            (saturation_distance * sat_weight) + 
            (value_distance * val_weight)
        )
        
        # Benzerlik = 1 - mesafe 
        similarity = 1.0 - weighted_distance
        
        # Sonuç ekle
        results.append({
            'filename': img_filename,
            'dominant_color': img_data.get("dominant_color"),
            'color_group': img_data.get("color_group"),
            'hsv': img_hsv,
            'similarity': similarity,
            'distances': {
                'hue': hue_distance,
                'saturation': saturation_distance,
                'value': value_distance
            }
        })
        count += 1
    
    # Benzerliğe göre sırala
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ {count} adet uygun görsel bulundu, {elapsed_time:.3f} saniyede tamamlandı")
    
    # Sonuç sayısını sınırla
    return results[:limit]

# Ana program çalıştırıldığında test et
if __name__ == "__main__":
    # Boş spektrum oluştur
    spectrum = build_color_spectrum()
    print(f"Boş spektrum oluşturuldu: {spectrum['divisions']} bölüm, {spectrum['saturation_levels']} doygunluk seviyesi, {spectrum['value_levels']} parlaklık seviyesi")
    
    # Test rengi
    test_hsv = (0.1, 0.8, 0.7)  # Canlı turuncu
    indices = classify_color_in_spectrum(test_hsv, spectrum)
    group_name = get_color_group_name(indices, spectrum)
    
    print(f"Test rengi (HSV {test_hsv}) sınıflandırması: {indices} - {group_name}")
    
    # Klasör yolu kontrolü
    if os.path.exists("realImages"):
        print("\nrealImages klasöründen spektrum oluşturuluyor...")
        spectrum = build_spectrum_from_directory("realImages")
        
        # İstatistikleri göster
        stats = get_color_spectrum_statistics(spectrum)
        print("\nRenk spektrumu istatistikleri:")
        print(f"Toplam görsel: {stats['total_images']}")
        print(f"Dolu gruplar: {stats['filled_groups']}")
        print(f"Boş gruplar: {stats['empty_groups']}")
        print(f"En büyük grup: {stats['largest_group']['name']} ({stats['largest_group']['count']} görsel)")
        
        # Ton dağılımı
        print("\nTon (Hue) Dağılımı:")
        for key, value in stats["hue_distribution"].items():
            print(f"  {key}: %{value}")
        
        # Doygunluk dağılımı
        print("\nDoygunluk (Saturation) Dağılımı:")
        for key, value in stats["saturation_distribution"].items():
            print(f"  {key}: %{value}")
        
        # Parlaklık dağılımı
        print("\nParlaklık (Value) Dağılımı:")
        for key, value in stats["value_distribution"].items():
            print(f"  {key}: %{value}")
        
        # Spektrumu kaydet
        with open("color_spectrum.json", "w", encoding="utf-8") as f:
            json.dump(spectrum, f, ensure_ascii=False, indent=2)
        
        print("\nRenk spektrumu 'color_spectrum.json' dosyasına kaydedildi.")