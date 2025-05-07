# Faiss indekslerini temizleme ve hafızayı boşaltma için zamanlama
def clean_faiss_indexes_periodically():
    """Düzenli aralıklarla Faiss indekslerini sıfırla ve hafızayı temizle"""
    global faiss_indexes, cached_features, cached_filenames, cached_metadata
    
    # Belirli bir süre geçtikten sonra temizlik yap
    print("🕓 Planlı Faiss indeks temizliği başlatılıyor")
    
    # Faiss indekslerini sıfırla
    faiss_indexes = {}
    
    # Öncelikle özellik vektörleri dışındaki önbellekleri sıfırla
    cached_filenames = {}
    cached_metadata = None
    
    # Bellek toplama işlemini manuel olarak başlat
    gc.collect()
    
    # Bir sonraki planlı temizliği zamanla (4 saat sonra)
    timer = threading.Timer(4 * 60 * 60, clean_faiss_indexes_periodically)  # 4 saat
    timer.daemon = True  # Program kapanırken thread'in kapanmasını sağla
    timer.start()# app.py
# Oluşturulma: 2025-04-19
# Güncelleme: 2025-04-29 (SQLite Veritabanı Entegrasyonu)
# Açıklama:
# Bu Flask uygulaması, Power User (PU) arayüzüyle etkileşime girer.
# Kullanıcılara metadata güncelleme, model eğitimi ve feedback sistemlerini yönetme imkânı sağlar.
# Şu an aktif olan endpointler:
# - "/"              → Ana yönlendirme (ileride dashboard'a bağlanabilir)
# - "/train"         → Eğitim arayüzü (train.html)
# - "/train-model"   → POST ile eğitim başlatma
# - "/check-updates" → JSON & görsel güncellemelerini kontrol eder
# - "/find-similar"  → Benzer desen görsellerini getirir
# - "/realImages/<path:filename>" → Gerçek görselleri sunar
# - "/create-cluster" → Seçilen görsellerle yeni cluster oluşturur

from flask import Flask, render_template, request, jsonify, send_from_directory
from train_handlers import setup_training_routes
import json
import subprocess
import sys
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import shutil
from datetime import datetime
import random
import traceback
import faiss  # Faiss kütüphanesini ekledik
import colorsys  # Renk dönüşümleri için eklendi
import cv2
import threading
import gc
import time  # time modülünü eksikti
import sqlite3
import db_utils  # SQLite işlemleri için yardımcı modül
from color_utils import (
    extract_dominant_color_improved, 
    analyze_image_colors, 
    find_harmonious_colors, 
    calculate_color_similarity,
    identify_color_group,
    rgb_to_hsv
)

import color_utils
import color_spectrum

# Sürüm bilgisi
APP_VERSION = "1.2.0"
APP_LAST_UPDATED = "2025-04-28"

app = Flask(__name__)

# Faiss indekslerini saklamak için global değişken
faiss_indexes = {}

# Özellik vektörlerini ve dosya isimlerini saklamak için global değişkenler
cached_features = {}
cached_filenames = {}
cached_metadata = None




# Faiss indeksi oluşturma ve alım için yardımcı fonksiyon
def get_faiss_index(model_type):
    """Belirtilen model tipi için Faiss indeksi oluşturur veya önbellekten alır"""
    # Önbellekte varsa döndür
    if model_type in faiss_indexes:
        return faiss_indexes[model_type]
    
    # Önbellekte yoksa yükle
    feature_path = f"image_features/{model_type}_features.npy"
    if not os.path.exists(feature_path):
        return None
    
    # Özellik vektörlerini yükle (önbellekte yoksa)
    if model_type not in cached_features:
        features = np.load(feature_path)
        cached_features[model_type] = features.astype(np.float32)
    else:
        features = cached_features[model_type]
    
    # Faiss indeksi oluştur
    d = features.shape[1]  # Vektör boyutu
    
    # GPU kontrolü
    use_gpu = faiss.get_num_gpus() > 0
    
    if model_type in ["pattern", "color+pattern"] or model_type.startswith("pattern"):
        # Kosinüs benzerliği için L2 normalleştirme
        normalized_features = features.copy()
        faiss.normalize_L2(normalized_features)
        
        if use_gpu:
            # GPU ile IP (Inner Product) indeksi
            print(f"🚀 {model_type} için GPU ile Faiss IP indeksi oluşturuluyor")
            flat_config = faiss.GpuIndexFlatConfig()
            flat_config.device = 0
            res = faiss.StandardGpuResources()
            index = faiss.GpuIndexFlatIP(res, d, flat_config)
        else:
            # CPU ile IP indeksi
            print(f"📊 {model_type} için CPU ile Faiss IP indeksi oluşturuluyor")
            index = faiss.IndexFlatIP(d)
        
        # Normalize edilmiş vektörleri ekle
        index.add(normalized_features)
    else:
        # Öklid mesafesi için L2 indeksi
        if use_gpu:
            print(f"🚀 {model_type} için GPU ile Faiss L2 indeksi oluşturuluyor")
            flat_config = faiss.GpuIndexFlatConfig()
            flat_config.device = 0
            res = faiss.StandardGpuResources()
            index = faiss.GpuIndexFlatL2(res, d, flat_config)
        else:
            print(f"📊 {model_type} için CPU ile Faiss L2 indeksi oluşturuluyor")
            index = faiss.IndexFlatL2(d)
        
        # Vektörleri ekle
        index.add(features)
    
    # İndeksi önbelleğe al
    faiss_indexes[model_type] = index
    
    return index

# Renk benzerliği hesaplayan fonksiyon
def calculate_color_similarity(color1, color2):
    """İki RGB rengi arasındaki benzerliği hesaplar (0-1 arası)"""
    # Euclidean mesafe tabanlı basit benzerlik
    color1 = np.array(color1)
    color2 = np.array(color2)
    
    # 3D renk uzayında mesafe hesapla
    distance = np.sqrt(np.sum((color1 - color2)**2))
    
    # Maksimum mesafe 441.67 (255, 255, 255 ile 0, 0, 0 arası)
    max_distance = np.sqrt(3 * 255**2)
    
    # Mesafeyi benzerliğe dönüştür (0-1 arası)
    similarity = 1.0 - (distance / max_distance)
    
    return similarity

# Uyumlu renkleri bulan fonksiyon
def find_harmonious_colors(reference_color, harmony_type="complementary"):
    """Bir referans renge uyumlu renkleri bulan fonksiyon
    
    Args:
        reference_color: RGB formatında referans renk [r, g, b]
        harmony_type: Uyum tipi ('complementary', 'analogous', 'triadic', 'split_complementary', 'monochromatic')
    
    Returns:
        Uyumlu renklerin listesi
    """
    # RGB'yi HSV'ye dönüştür (renk teorisi işlemleri HSV'de daha kolay)
    hsv_color = colorsys.rgb_to_hsv(reference_color[0]/255, reference_color[1]/255, reference_color[2]/255)
    h, s, v = hsv_color
    
    harmonious_colors = []
    
    if harmony_type == "complementary":
        # Tamamlayıcı renk (renk çemberinde 180 derece karşı)
        complementary_h = (h + 0.5) % 1.0
        complementary_rgb = colorsys.hsv_to_rgb(complementary_h, s, v)
        harmonious_colors.append([int(c * 255) for c in complementary_rgb])
    
    elif harmony_type == "analogous":
        # Analog renkler (renk çemberinde +/- 30 derece)
        for angle in [-30, 30]:
            analog_h = (h + angle/360) % 1.0
            analog_rgb = colorsys.hsv_to_rgb(analog_h, s, v)
            harmonious_colors.append([int(c * 255) for c in analog_rgb])
    
    elif harmony_type == "triadic":
        # Triadik renkler (renk çemberinde +/- 120 derece)
        for angle in [120, 240]:
            triad_h = (h + angle/360) % 1.0
            triad_rgb = colorsys.hsv_to_rgb(triad_h, s, v)
            harmonious_colors.append([int(c * 255) for c in triad_rgb])
    
    elif harmony_type == "split_complementary":
        # Split complementary (tamamlayıcı rengin her iki yanından 30'ar derece)
        comp_h = (h + 0.5) % 1.0
        for angle in [-30, 30]:
            split_h = (comp_h + angle/360) % 1.0
            split_rgb = colorsys.hsv_to_rgb(split_h, s, v)
            harmonious_colors.append([int(c * 255) for c in split_rgb])
    
    elif harmony_type == "monochromatic":
        # Monokromatik renkler (aynı rengin farklı ton ve doygunlukları)
        # Daha açık ve daha koyu versiyonlar
        for value_mod in [-0.3, -0.15, 0.15, 0.3]:  # V değeri değişimleri
            new_v = max(0.1, min(0.9, v + value_mod))  # Sınırlar içinde tut
            mono_rgb = colorsys.hsv_to_rgb(h, s, new_v)
            harmonious_colors.append([int(c * 255) for c in mono_rgb])
    
    return harmonious_colors

# Yardımcı fonksiyon: Filtre uygulamaları için izin verilen indeksleri oluştur
def get_allowed_indices(filters, filenames, metadata, model_type, version):
    """Filtre parametrelerine göre izin verilen indeksleri döndürür"""
    allowed_indices = []
    
    if not filters:
        # Filtre yoksa ve versiyon v1 değilse, versiyon bazlı filtreleme yap
        if version != "v1":
            model_data = get_model_data(model_type)
            version_data = model_data.get("versions", {}).get(version, {})
            version_clusters = version_data.get("clusters", {})
            
            # Tüm clusterlar'daki görselleri topla
            version_images = set()
            for cluster_data in version_clusters.values():
                version_images.update(cluster_data.get("images", []))
            
            # Sadece bu versiyondaki görselleri dahil et
            allowed_indices = [i for i, fname in enumerate(filenames) if fname in version_images]
            print(f"ℹ️ Versiyon filtreleme: {version} versiyonunda {len(allowed_indices)} görsel bulundu.")
        else:
            allowed_indices = list(range(len(filenames)))
        return allowed_indices

    # Filtreleri işle
    mix_filters = filters.get("mixFilters", [])
    feature_filters = filters.get("features", [])
    cluster_status = filters.get("cluster", "")
    
    # Model verilerini yükle (versiyon bilgisi için)
    model_data = get_model_data(model_type)

    for i, fname in enumerate(filenames):
        meta = metadata.get(fname, {})
        feature_map = {f[0]: f[1] for f in meta.get("features", [])}
        cluster = meta.get("cluster")

        match_mix = all(
            mix["min"] <= feature_map.get(mix["type"], 0) <= mix["max"]
            for mix in mix_filters
        )

        match_feature = all(f in feature_map for f in feature_filters)

        # Versiyon bazlı cluster kontrolü
        match_cluster = True
        if cluster_status == "clustered" and not cluster:
            match_cluster = False
        elif cluster_status == "unclustered" and cluster:
            match_cluster = False
            
        # Versiyon kontrolü: Eğer metadata'da cluster bilgisi varsa
        # ve bu cluster belirtilen model ve versiyonda yer alıyorsa, kullan
        if version != "v1" and cluster:  # v1 tüm görseller için varsayılan
            # Model verisinde bu cluster var mı kontrol et
            version_data = model_data.get("versions", {}).get(version, {})
            version_clusters = version_data.get("clusters", {})
            
            cluster_exists = False
            for cluster_name, cluster_data in version_clusters.items():
                if fname in cluster_data.get("images", []):
                    cluster_exists = True
                    break
            
            # Bu görsel belirtilen versiyonda değilse ve clustered filtresi varsa, filtreleme yap
            if cluster_status == "clustered" and not cluster_exists:
                match_cluster = False

        if match_mix and match_feature and match_cluster:
            allowed_indices.append(i)
            
    return allowed_indices
setup_training_routes(app)

# Model JSON yönetimi için yardımcı fonksiyonlar
def get_model_data(model):
    """Model JSON verisini okur"""
    model_path = os.path.join("exported_clusters", model, "versions.json")
    
    if not os.path.exists(model_path):
        # Yeni model dosyası oluştur
        data = {
            "current_version": "v1",
            "versions": {}
        }
        # Model klasörünü oluştur
        os.makedirs(os.path.join("exported_clusters", model), exist_ok=True)
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

def save_model_data(model, data):
    """Model JSON verisini kaydeder"""
    model_path = os.path.join("exported_clusters", model, "versions.json")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True

def get_next_version(model):
    """Bir sonraki versiyon adını döndürür (v1, v2, ...)"""
    data = get_model_data(model)
    versions = data["versions"].keys()
    
    if not versions:
        return "v1"
        
    # v1, v2, ... formatındaki versiyonları bul
    v_numbers = [int(v[1:]) for v in versions if v.startswith("v") and v[1:].isdigit()]
    
    if not v_numbers:
        return "v1"
        
    return f"v{max(v_numbers) + 1}"

# Metadata güncelleme yardımcı fonksiyonu
def update_metadata(filename, updates):
    """Görsel metadatasını günceller"""
    metadata_path = "image_metadata_map.json"
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        if filename in metadata:
            metadata[filename].update(updates)
        else:
            metadata[filename] = updates
            
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Metadata güncelleme hatası: {str(e)}")
        return False

@app.route("/")
def home():
    return "<h2>PU Ana Panel </h2><p>/train ile model eğit, /check-updates ile güncelle kontrol et.</p>"


@app.route("/train")
def train():
    return render_template("train.html")

@app.route("/pu")
def pu_screen():
    return render_template("pu.html")

@app.route("/train-model", methods=["POST"])
def train_model_route():
    data = request.get_json()
    with open("train_config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Eğitim klasörü yoksa oluştur
    cluster_path = os.path.join("exported_clusters", data["model_type"])
    os.makedirs(cluster_path, exist_ok=True)

    python_exe = sys.executable
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run([python_exe, "train_model.py"], capture_output=True, text=True, check=True, env=env)
        print(result.stdout)

        # Eğitim sonrası özet satırı bul (✅ Eğitim Özeti: ...)
        summary_line = ""
        for line in result.stdout.splitlines():
            if line.startswith("✅ Eğitim Özeti"):
                summary_line = line
                break

        status_msg = summary_line if summary_line else "✅ Eğitim başarıyla tamamlandı."
        return jsonify({"status": status_msg})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": f"❌ Eğitim sırasında hata: {e.stderr}"})

@app.route('/image_metadata_map.json')
def serve_metadata_map():
    return send_from_directory('.', 'image_metadata_map.json')

@app.route('/realImages/<path:filename>')
def serve_real_image(filename):
    return send_from_directory('realImages', filename)

@app.route("/check-updates")
def check_updates():
    # Manuel çalıştırma parametresi ekleyerek kontrol sağlıyoruz
    force_check = request.args.get('force', 'false').lower() == 'true'
    
    # Eğer manuel olarak çalıştırılmadıysa, sadece mevcut durumu döndür
    if not force_check:
        return jsonify({
            "status": "check_disabled",
            "message": "Otomatik güncelleme kontrolü devre dışı bırakıldı. Manuel kontrol için ?force=true parametresini ekleyin."
        })
    
    # Manuel çalıştırılması durumunda orijinal işlevi gerçekleştir
    try:
        from check_updates import check_for_updates
        changes = check_for_updates()
        
        if changes.get("has_changes", False):
            print(f"🔍 Değişiklik algılandı: {changes.get('summary', {})}")
            return jsonify({
                "status": "changes_detected",
                "changes": changes,
                "message": changes.get("notification", {}).get("message", "Değişiklikler algılandı.")
            })
        else:
            return jsonify({
                "status": "up_to_date",
                "message": changes.get("message", "✅ Değişiklik yok, metadata güncel.")
            })
    except Exception as ex:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"❌ Hata oluştu: {str(ex)}"
        })
    
@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    return send_from_directory('thumbnails', filename)

@app.route("/clusters/<model>/<version>/data")
def serve_cluster_data(model, version):
    """Model versiyon bilgilerini döndürür"""
    model_data = get_model_data(model)
    
    # Eğer versiyon yoksa hata döndür
    if version not in model_data.get("versions", {}):
        return jsonify({"error": "Versiyon bulunamadı"}), 404
    
    # Versiyon içeriklerini kontrol et
    version_data = model_data["versions"][version]
    clusters = version_data.get("clusters", {})
    cluster_count = len(clusters)
    total_images = 0
    
    # Her cluster'daki görsel sayısını topla
    for cluster_name, cluster_data in clusters.items():
        total_images += len(cluster_data.get("images", []))
    
    print(f"\n[DEBUG] Model: {model}, Version: {version}")
    print(f"[DEBUG] Cluster count: {cluster_count}")
    print(f"[DEBUG] Total images: {total_images}")
    print(f"[DEBUG] Clusters: {list(clusters.keys())}\n")
    
    # Sadece istenen versiyonun verisini döndür
    return jsonify({
        "version": version,
        "data": model_data["versions"][version],
        "stats": {
            "cluster_count": cluster_count,
            "total_images": total_images
        }
    })

@app.route("/find-similar", methods=["GET", "POST"])
def find_similar():
    """SQLite veritabanı kullanan ve renk spektrumu desteği içeren benzerlik arama endpoint'i"""
    start_time = datetime.now()  # Performans ölçümü için başlangıç zamanı
    
    filters = request.get_json() if request.method == "POST" else None
    filename = request.args.get("filename")
    model = request.args.get("model", "pattern")
    version = request.args.get("version", "v1")
    topN = int(request.args.get("topN", 100))
    metric = request.args.get("metric", "cosine")
    
    # Renk spektrumu için yeni parametreler
    use_color_spectrum = request.args.get("use_color_spectrum", "false").lower() == "true"
    # Eğer renk modeli ve HSV ile başlayan bir versiyon seçilmişse, otomatik olarak renk spektrumunu kullan
    if model == "color" and version and version.startswith("HSV"):
        use_color_spectrum = True
        print(f"DEBUG: HSV versiyonu tespit edildi, use_color_spectrum şimdi {use_color_spectrum}")
    hue_range = request.args.get("hue_range", "0-360")  # Ton aralığı (derece)
    min_saturation = float(request.args.get("min_saturation", "0"))  # Min doygunluk (0-1)
    min_value = float(request.args.get("min_value", "0"))  # Min parlaklık (0-1)
    color_group = request.args.get("color_group", None)  # Renk grubu (ör: "Kırmızı", "Mavi", vb.)
    
    print(f"📊 Benzer görsel arama: model={model}, version={version}, metric={metric}")
    if use_color_spectrum and model == "color":
        print(f"🎨 Renk spektrumu kullanılıyor: hue_range={hue_range}, min_saturation={min_saturation}, min_value={min_value}")
        if color_group:
            print(f"🎨 Renk grubu: {color_group}")

    # Fabric bilgilerini kontrol et
    fabric = db_utils.get_fabric_by_filename(filename)
    if not fabric:
        print(f"⚠️ Kumaş bulunamadı: {filename}")
        # Eski yönteme geri dön (uyumluluk için)
        try:
            # Metadata dosyasını kontrol et
            metadata_path = "image_metadata_map.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                if filename not in metadata:
                    return jsonify([])
        except:
            return jsonify([])

    # Eğer renk modeli seçiliyse ve renk spektrumu kullanımı isteniyorsa
    if model == "color" and use_color_spectrum:
        print(f"DEBUG: Renk spektrumu araması başlıyor - HSV version kontrolü: {version} start with HSV = {version.startswith('HSV') if version else False}")
        try:
            # Import color_utils burada
            from color_utils import (
                extract_dominant_color_improved, rgb_to_hsv, 
                identify_color_group
            )

            # Görselin dominant rengini çıkar
            img_path = os.path.join("realImages", filename)
            print(f"DEBUG: Dominant renk çıkarılıyor - {img_path}")
            dominant_color = extract_dominant_color_improved(img_path, method='histogram')

            # RGB'den HSV'ye dönüştür
            hsv_color = rgb_to_hsv(dominant_color)
            print(f"DEBUG: Dominant renk tespit edildi - RGB={dominant_color}, HSV={hsv_color}")

            # Eğer renk grubu belirtilmişse, filtre bilgisini kaydedelim
            if color_group:
                # Görselin renk grubunu belirle
                img_color_group = identify_color_group(hsv_color)
                if img_color_group != color_group:
                    print(f"⚠️ Görsel renk grubu ({img_color_group}) filtre ile eşleşmiyor ({color_group})")

            # Doğrudan modülden color_spectrum fonksiyonlarını kullan
            print(f"DEBUG: find_similar_colors_optimized çağrılıyor - hsv={hsv_color}, limit={topN}")
            spectrum_results = color_spectrum.find_similar_colors_optimized(
                hsv_color=hsv_color,
                limit=topN
            )
            
            print(f"DEBUG: {len(spectrum_results)} adet sonuç bulundu")
            
            # Sonuçları formatla
            results = []
            for item in spectrum_results:
                filename_result = item.get("filename")
                if not filename_result:
                    print(f"WARNING: filename boş - {item}")
                    continue
                    
                fabric_info = db_utils.get_fabric_by_filename(filename_result)
                if fabric_info:
                    results.append({
                        "filename": filename_result,
                        "design": fabric_info.get("design"),
                        "season": fabric_info.get("season"),
                        "quality": fabric_info.get("quality"),
                        "features": fabric_info.get("features", []),
                        "cluster": None,  # Renk spektrumunda cluster kavramı yok
                        "version": version,
                        "similarity": item["similarity"],
                        "color_info": {
                            "dominant_color": item.get("dominant_color"),
                            "color_group": item.get("color_group"),
                            "hsv": item.get("hsv")
                        }
                    })
                else:
                    print(f"WARNING: İşlenecek fabric_info bulunamadı - {filename_result}")
            
            print(f"🎨 Renk spektrumu ile {len(results)} sonuç bulundu")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Renk spektrumu hatası: {str(e)}")
            print(f"Hata detayları: {error_details}")
            # Hata durumunda standart arama yöntemine geç
            use_color_spectrum = False
    
    # Eğer renk spektrumu kullanılmıyorsa veya bir hata oluştuysa
    if model != "color" or not use_color_spectrum:
        # Benzer görselleri bul (standart yöntem)
        results = db_utils.find_similar_images(
            filename=filename,
            model_type=model,
            version=version,
            topN=topN,
            metric=metric,
            filters=filters
        )
        
        # Sonuç yoksa ve hala eski JSON yapısı varsa, uyumluluk modu için eski yöntemi dene
        if not results:
            feature_path = f"image_features/{model}_features.npy"
            index_path = f"image_features/{model}_filenames.json"
            
            if os.path.exists(feature_path) and os.path.exists(index_path) and cached_metadata is not None:
                print(f"⚠️ SQLite sonuç yok, eski yöntem deneniyor: {filename}")
                
                # Eskiden kullanılan JSON-tabanlı arama fonksiyonuna yönlendir
                try:
                    # Önbellekte yoksa dosya isimlerini yükle
                    if model not in cached_filenames:
                        with open(index_path, "r", encoding="utf-8") as f:
                            cached_filenames[model] = json.load(f)
                    filenames = cached_filenames[model]
                    
                    # Faiss indeksini al
                    index = get_faiss_index(model)
                    if index and filename in filenames:
                        # Burada eski find_similar işlevi çağrılabilir
                        # Ancak bu geçiş aşamasında kullanılacak geçici bir çözüm
                        print(f"⚠️ Eski arama yöntemi kullanılıyor")
                except Exception as e:
                    print(f"❌ Eski yöntem hatası: {str(e)}")
    
    # Sonuçların ilk elemanı, aranılan görsel olmalı (tam eşleşme)
    # Eğer yoksa ekle
    self_exists = any(r["filename"] == filename for r in results)
    
    if not self_exists:
        # db_utils ile fabric bilgilerini al
        reference_fabric = db_utils.get_fabric_by_filename(filename)
        
        if reference_fabric:
            # En başa kendisini ekle
            results.insert(0, {
                "filename": filename,
                "design": reference_fabric.get("design"),
                "season": reference_fabric.get("season"),
                "quality": reference_fabric.get("quality"),
                "features": reference_fabric.get("features", []),
                "cluster": None,  # Cluster bilgisi sonra eklenecek
                "version": version,
                "similarity": 1.0  # Tam eşleşme her zaman 1.0
            })
    
    # Performans ölçümü
    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    print(f"⏱️ Benzerlik araması {duration_ms:.1f} ms'de tamamlandı ({len(results)} sonuç)")
    
    return jsonify(results)

@app.route("/update-version-comment", methods=["POST"])
def update_version_comment():
    data = request.get_json()
    model = data.get("model")
    version = data.get("version")
    comment = data.get("version_comment", "")

    if not model or not version:
        return jsonify({"status": "error", "message": "Model ve versiyon belirtilmelidir."})

    try:
        model_data = get_model_data(model)
        
        if version not in model_data.get("versions", {}):
            return jsonify({"status": "error", "message": "Belirtilen versiyon bulunamadı."})
        
        model_data["versions"][version]["comment"] = comment
        save_model_data(model, model_data)

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})








@app.route('/create-cluster', methods=["POST"])
def create_cluster():
    """
    Küme oluşturma endpoint'i.
    Model türüne göre farklı kümeleme yaklaşımları kullanır:
    - Model tipi "color" ise renk spektrumu tabanlı sınıflandırma kullanır
    - Diğer modeller için standart kümeleme algoritması kullanır
    """
    data = request.get_json()
    model = data.get("model")
    version = data.get("version")
    filenames = data.get("filenames", [])

    if not model or not version or not filenames:
        return jsonify({"status": "error", "message": "Model, versiyon ve görsel listesi gerekli."})

    try:
        # Model ve versiyon kontrolü
        # Renk modeli için özel sınıflandırma
        if model == "color":
            print(f"🎨 Renk modeli için renk spektrumu tabanlı sınıflandırma kullanılıyor: {version}")
            
            # color_cluster.py'den işlevleri kullan
            import color_cluster
            
            # Konfigürasyon
            config = {
                "model_type": model,
                "version": version,
                "divisions": 12,  # varsayılan değerler 
                "saturation_levels": 3,
                "value_levels": 3
            }
            
            # Custom parametreler varsa ekle
            if "parameters" in data:
                config.update(data.get("parameters", {}))
            
            # Renk tabanlı kümeleme yap
            version_data = color_cluster.cluster_images(config)
            
            # JSON olarak metadata güncelle (eski yöntemle uyumluluk için)
            for fname in filenames:
                # İlk kümeyi bul
                assigned_cluster = None
                for cluster_name, cluster_data in version_data.get("clusters", {}).items():
                    if fname in cluster_data.get("images", []):
                        assigned_cluster = cluster_name
                        break
                
                if assigned_cluster:
                    update_metadata(fname, {"cluster": assigned_cluster})
            
            return jsonify({"status": "ok", "message": "Renk spektrumu tabanlı sınıflandırma tamamlandı."})
        
        else:
            # Standart kümeleme yöntemi (auto_cluster.py kullanımı)
            print(f"🔍 Standart kümeleme algoritması kullanılıyor: {model}/{version}")
            
            # Model verilerini oku
            model_path = os.path.join("exported_clusters", model, "versions.json")
            
            if not os.path.exists(model_path):
                # Model klasörünü ve versiyon dosyasını oluştur
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                # Yeni model dosyası oluştur
                model_data = {
                    "current_version": "v1",
                    "versions": {}
                }
                with open(model_path, "w", encoding="utf-8") as f:
                    json.dump(model_data, f, indent=2, ensure_ascii=False)
            else:
                with open(model_path, "r", encoding="utf-8") as f:
                    model_data = json.load(f)
            
            # Versiyon kontrolü
            if version not in model_data["versions"]:
                model_data["versions"][version] = {
                    "created_at": datetime.now().isoformat(),
                    "comment": f"{model} modeli {version} versiyonu",
                    "algorithm": "manual",
                    "parameters": {},
                    "clusters": {}
                }
            
            version_data = model_data["versions"][version]
            
            # Mevcut kümelerde bu görseller varsa çıkar
            for cluster_name, cluster_data in list(version_data["clusters"].items()):
                cluster_data["images"] = [img for img in cluster_data["images"] if img not in filenames]
                
                if not cluster_data["images"] or cluster_data["representative"] in filenames:
                    if cluster_data["images"]:
                        cluster_data["representative"] = cluster_data["images"][0]
                    else:
                        del version_data["clusters"][cluster_name]
            
            # Yeni küme ismi
            new_cluster_name = "cluster-" + str(len(version_data["clusters"]) + 1)
            
            # thumbnail klasörünü kontrol et
            thumbnail_path = os.path.join("exported_clusters", model, version, "thumbnails")
            os.makedirs(thumbnail_path, exist_ok=True)
            
            # Görsellerin thumbnail'larını kopyala
            for fname in filenames:
                src_thumb = os.path.join("thumbnails", fname)
                dst_thumb = os.path.join(thumbnail_path, fname)
                
                if os.path.exists(src_thumb):
                    shutil.copy2(src_thumb, dst_thumb)
                    
                # Metadatada güncelle
                update_metadata(fname, {"cluster": new_cluster_name})
            
            # Temsil görselini seç (ilk görsel)
            representative = filenames[0]
            
            # Yeni kümeyi oluştur
            version_data["clusters"][new_cluster_name] = {
                "representative": representative,
                "images": filenames,
                "comment": ""
            }
            
            # Model verisini güncelle
            model_data["current_version"] = version
            
            # Değişiklikleri kaydet
            with open(model_path, "w", encoding="utf-8") as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)
            
            return jsonify({"status": "ok", "new_cluster": new_cluster_name})
            
    except Exception as e:
        import traceback
        print(f"Cluster oluşturma hatası: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)})


# --- Feedback kaydı alma endpointi (SQLite) ---
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    feedback_data = request.get_json()
    print("📩 Feedback alındı:", feedback_data)

    # Gerekli verileri al
    anchor = feedback_data.get("anchor")
    output = feedback_data.get("output")
    model = feedback_data.get("model")
    version = feedback_data.get("version")
    rating = feedback_data.get("feedback")

    # Eğer rating yoksa, bu bir iptal işlemidir
    if rating is None:
        # Eski yöntem: JSON dosyasını güncelle (uyumluluk için)
        feedback_file = "feedback_log.json"
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, "r", encoding="utf-8") as f:
                    feedback_list = json.load(f)
                
                # İlgili feedback'i çıkar
                feedback_list = [f for f in feedback_list if not (
                    f.get("anchor") == anchor and
                    f.get("output") == output and
                    f.get("model") == model and
                    f.get("version") == version
                )]
                
                # Güncellenmiş listeyi kaydet
                with open(feedback_file, "w", encoding="utf-8") as f:
                    json.dump(feedback_list, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Feedback JSON güncellemesi hatası: {str(e)}")

        # Veritabanından da sil (ileride eklenecek)
        # db_utils.delete_feedback(anchor, output, model, version)
        return jsonify({"status": "ok", "message": "Feedback silindi"})

    # SQLite veritabanına ekle
    success = db_utils.add_feedback(
        anchor_filename=anchor,
        output_filename=output,
        model_type=model,
        version=version,
        rating=rating
    )

    # Eski yöntem: JSON dosyasına da ekle (uyumluluk için)
    feedback_file = "feedback_log.json"
    feedback_list = []

    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            try:
                feedback_list = json.load(f)
            except json.JSONDecodeError:
                feedback_list = []

    # Aynı anchor-output-model-version varsa çıkar
    feedback_list = [f for f in feedback_list if not (
        f.get("anchor") == anchor and
        f.get("output") == output and
        f.get("model") == model and
        f.get("version") == version
    )]

    # Yeni feedback'i ekle
    feedback_list.append(feedback_data)

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(feedback_list, f, indent=2, ensure_ascii=False)

    if success:
        return jsonify({"status": "ok", "message": "Feedback kaydedildi"})
    else:
        return jsonify({"status": "error", "message": "Feedback kaydedilirken bir hata oluştu"})

@app.route("/init-model-version", methods=["POST"])
def init_model_version():
    """Yeni bir model ve versiyon kombinasyonu için gereken başlangıç yapısını oluşturur"""
    data = request.get_json()
    model = data.get("model")
    version = data.get("version")
    
    if not model or not version:
        return jsonify({"status": "error", "message": "Model ve versiyon belirtilmeli."})
    
    # Model ve versiyon klasörlerini oluştur
    version_path = os.path.join("exported_clusters", model, version)
    os.makedirs(version_path, exist_ok=True)
    
    # Boş representatives.json dosyası oluştur
    rep_data = {
        "representatives": [],
        "clusters": [],
        "version_comment": f"{model} modeli {version} versiyonu",
        "last_updated": datetime.now().isoformat()
    }
    
    rep_path = os.path.join(version_path, "representatives.json")
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(rep_data, f, indent=2, ensure_ascii=False)
    
    return jsonify({"status": "ok", "message": f"{model} modeli {version} versiyonu hazırlandı."})

@app.route("/move-to-cluster", methods=["POST"])
def move_to_cluster():
    data = request.get_json()
    model = data.get("model", "pattern") 
    version = data.get("version", "v1")   
    cluster_name = data.get("cluster")
    images = data.get("images", [])

    if not cluster_name or not images:
        return jsonify({"status": "error", "message": "Eksik bilgi"}), 400

    try:
        # Model verisini al
        model_data = get_model_data(model)
        
        # Versiyon kontrolü
        if version not in model_data["versions"]:
            return jsonify({"status": "error", "message": "Versiyon bulunamadı"}), 404
            
        version_data = model_data["versions"][version]
        
        # Cluster kontrolü
        if cluster_name not in version_data["clusters"]:
            return jsonify({"status": "error", "message": "Cluster bulunamadı"}), 404
        
        # Metadata dosyasını yükle
        metadata_path = "image_metadata_map.json"
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        moved = []
        
        # Görselleri diğer clusterlardan çıkar
        for existing_cluster, cluster_data in list(version_data["clusters"].items()):
            if existing_cluster == cluster_name:
                continue
                
            # Görselleri filtrele
            cluster_data["images"] = [img for img in cluster_data["images"] if img not in images]
            
            # Temsil eden görsel taşındıysa, yeni temsil eden seç
            if cluster_data["representative"] in images and cluster_data["images"]:
                cluster_data["representative"] = cluster_data["images"][0]
            
            # Eğer cluster boşalmışsa ve temsil eden görsel de taşındıysa, cluster'ı sil
            if not cluster_data["images"]:
                del version_data["clusters"][existing_cluster]
        
        # Görselleri thumbnail olarak kopyala
        thumbnail_path = os.path.join("exported_clusters", model, version, "thumbnails")
        os.makedirs(thumbnail_path, exist_ok=True)
        
        for img in images:
            src_thumb = os.path.join("thumbnails", img)
            dst_thumb = os.path.join(thumbnail_path, img)
            
            if os.path.exists(src_thumb):
                shutil.copy2(src_thumb, dst_thumb)
                moved.append(img)
            else:
                print(f"⚠️ Thumbnail bulunamadı: {img}")
            
            # Hedef cluster'a ekle
            if img not in version_data["clusters"][cluster_name]["images"]:
                version_data["clusters"][cluster_name]["images"].append(img)

            # Metadata'da cluster güncelle
            if img in metadata:
                metadata[img]["cluster"] = cluster_name
            else:
                print(f"📛 Metadata'da {img} bulunamadı")

        # Metadata'yı kaydet
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        # Model verisini kaydet
        save_model_data(model, model_data)

        return jsonify({"status": "ok", "moved": moved, "cluster": cluster_name})
        
    except Exception as e:
        import traceback
        print(f"Görsel taşıma hatası: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/create-new-version", methods=["POST"])
def create_new_version():
    """Yeni bir model versiyonu oluşturur ve clustering yapar"""
    data = request.get_json()
    
    model = data.get("model", "pattern")
    algorithm = data.get("algorithm", "kmeans")
    parameters = data.get("parameters", {})
    comment = data.get("comment", "")
    
    # Yeni versiyon adını belirle
    new_version = get_next_version(model)
    
    # Model datasını al
    model_data = get_model_data(model)
    
    # Cluster config oluştur
    cluster_config = {
        "model_type": model,
        "version": new_version,
        "algorithm": algorithm,
        **parameters
    }
    
    # Config'i kaydet
    with open("cluster_config.json", "w", encoding="utf-8") as f:
        json.dump(cluster_config, f, indent=2, ensure_ascii=False)
    
    try:
        # Versiyon klasörünü oluştur
        version_path = os.path.join("exported_clusters", model, new_version)
        thumbnail_path = os.path.join(version_path, "thumbnails")
        os.makedirs(thumbnail_path, exist_ok=True)
        
        # Auto cluster'ı çalıştır
        python_exe = sys.executable
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            [python_exe, "auto_cluster.py"], 
            capture_output=True, 
            text=True, 
            check=True, 
            env=env
        )
        
        # Çıktıdan cluster bilgilerini al
        cluster_count = 0
        for line in result.stdout.splitlines():
            if "küme oluşturuldu" in line:
                parts = line.split()
                try:
                    cluster_count = int(parts[parts.index("küme") - 1])
                except (ValueError, IndexError):
                    pass
        
        # Güncel verileri al
        updated_model_data = get_model_data(model)
        updated_version_data = updated_model_data["versions"].get(new_version, {})
        actual_clusters = updated_version_data.get("clusters", {})
        actual_cluster_count = len(actual_clusters)
        
        return jsonify({
            "status": "ok", 
            "version": new_version,
            "cluster_count": actual_cluster_count or cluster_count,
            "message": f"{model} modeli için {new_version} versiyonu oluşturuldu."
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/available-versions")
def available_versions():
    """Bir model için mevcut tüm versiyonları listeler"""
    model = request.args.get("model", "pattern")
    
    try:
        model_data = get_model_data(model)
        versions = []
        
        for version_id in model_data["versions"].keys():
            version_data = model_data["versions"][version_id]
            version_name = f"Versiyon {version_id[1:]}" if version_id.startswith("v") else version_id
            
            # İsteğe bağlı olarak versiyon hakkında daha fazla bilgi eklenebilir
            versions.append({
                "id": version_id,
                "name": version_name,
                "algorithm": version_data.get("algorithm", "unknown"),
                "created_at": version_data.get("created_at", ""),
                "comment": version_data.get("comment", "")
            })
        
        # Eğer liste boşsa varsayılan ekle
        if not versions:
            versions.append({"id": "v1", "name": "Versiyon 1"})
            
        return jsonify(versions)
    except Exception as e:
        print(f"Versiyon listesi alınırken hata: {str(e)}")
        return jsonify([{"id": "v1", "name": "Versiyon 1"}])

# Yeni: Değişiklikleri uygulama endpoint'i
@app.route("/apply-updates", methods=["POST"])
def apply_updates():
    try:
        from check_updates import apply_updates, check_for_updates
        
        # İlk önce değişiklikleri kontrol et
        changes = check_for_updates()
        
        if not changes.get("has_changes", False):
            return jsonify({
                "status": "no_changes", 
                "message": "Uygulanacak değişiklik bulunamadı."
            })
        
        # İşlem zaten devam ediyorsa bildir
        if os.path.exists('updating_clusters.flag'):
            flag_age = time.time() - os.path.getmtime('updating_clusters.flag')
            return jsonify({
                "status": "in_progress",
                "message": f"⏳ Başka bir güncelleme işlemi {flag_age/60:.1f} dakikadır devam ediyor, lütfen bekleyin."
            })
            
        # Değişiklikleri uygula
        results = apply_updates(changes)
        
        # Faiss indekslerini temizle
        global faiss_indexes, cached_features, cached_filenames, cached_metadata
        faiss_indexes = {}
        cached_features = {}
        cached_filenames = {}
        cached_metadata = None
        
        return jsonify({
            "status": results.get("status", "success"),
            "message": "✅ Değişiklikler başarıyla uygulandı" if results.get("status") == "success" else "⚠️ Bazı değişiklikler uygulanamadı",
            "results": results
        })
    except Exception as ex:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"❌ Hata oluştu: {str(ex)}"
        })

@app.route("/get-user-feedbacks")
def get_user_feedbacks():
    """Kullanıcının önceki feedback'lerini döndürür"""
    model = request.args.get("model")
    version = request.args.get("version")
    anchor = request.args.get("anchor")
    
    if not model or not version or not anchor:
        return jsonify([]), 400
    
    try:
        # Feedback dosyasını kontrol et (eski yöntem)
        feedback_file = "feedback_log.json"
        feedback_list = []
        
        if os.path.exists(feedback_file):
            with open(feedback_file, "r", encoding="utf-8") as f:
                try:
                    feedback_list = json.load(f)
                except json.JSONDecodeError:
                    feedback_list = []
        
        # Filtrele: anchor, model ve version'a göre
        filtered_feedbacks = [{
            "output": item["output"],
            "rating": item["feedback"]
        } for item in feedback_list if 
            item["anchor"] == anchor and 
            item["model"] == model and 
            item["version"] == version and
            item["feedback"] is not None]
        
        print(f"[DEBUG] {len(filtered_feedbacks)} adet feedback bulundu")
        return jsonify(filtered_feedbacks)
    except Exception as e:
        print(f"[ERROR] Feedback'leri alma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

# Yeni: Değişiklikleri yoksay endpoint'i
@app.route("/ignore-updates", methods=["POST"])
def ignore_updates():
    try:
        data = request.get_json()
        previous_cache = data.get("previous_cache", {})
        
        # Önceki cache durumunu kaydet (değişiklikleri yoksaymak için)
        if previous_cache:
            from check_updates import save_current_cache
            save_current_cache(
                previous_cache.get("images", []), 
                previous_cache.get("json_hashes", {})
            )
            return jsonify({"status": "ok", "message": "Değişiklikler yoksayıldı."})
        else:
            return jsonify({"status": "error", "message": "Önceki cache bilgisi bulunamadı."})
    except Exception as ex:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"❌ Hata oluştu: {str(ex)}"})
@app.route("/system-info")
def system_info():
    # Faiss GPU desteği kontrolü
    gpu_count = faiss.get_num_gpus()
    uses_gpu = gpu_count > 0
    
    # Mevcut model tipleri ve versiyonları
    models = []
    for model_type in ["pattern", "color", "texture", "color+pattern"]:
        model_path = os.path.join("exported_clusters", model_type, "versions.json")
        if os.path.exists(model_path):
            try:
                with open(model_path, "r", encoding="utf-8") as f:
                    model_data = json.load(f)
                
                model_info = {
                    "model_type": model_type,
                    "current_version": model_data.get("current_version", "v1"),
                    "versions": list(model_data.get("versions", {}).keys())
                }
                models.append(model_info)
            except:
                pass
    
    # Model özellikleri
    features_info = []
    for model_type in ["pattern", "color", "texture", "color+pattern"]:
        feature_path = f"image_features/{model_type}_features.npy"
        if os.path.exists(feature_path):
            try:
                features = np.load(feature_path)
                features_info.append({
                    "model_type": model_type,
                    "shape": list(features.shape),
                    "size_mb": round(os.path.getsize(feature_path) / (1024 * 1024), 2)
                })
            except:
                pass
    
    # Görsel sayısı
    image_count = len([f for f in os.listdir("realImages") if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    return jsonify({
        "app_version": APP_VERSION,
        "last_updated": APP_LAST_UPDATED,
        "faiss": {
            "gpu_count": gpu_count,
            "uses_gpu": uses_gpu
        },
        "models": models,
        "features": features_info,
        "image_count": image_count,
        "environment": {
            "python_version": sys.version.split()[0]
        }
    })

# Yeni: Uyumlu renklere sahip kumaşları bulma endpoint'i
@app.route("/find-harmonious")
def find_harmonious():
    fabric_id = request.args.get("fabricId")
    harmony_type = request.args.get("harmonyType", "complementary")
    threshold = float(request.args.get("threshold", "80")) / 100  # Yüzdeyi ondalikli sayıya çevir
    result_count = int(request.args.get("resultCount", "20"))
    current_season_only = request.args.get("currentSeasonOnly", "false").lower() == "true"
    current_quality_only = request.args.get("currentQualityOnly", "false").lower() == "true"
    
    # Görsel dosya yolu
    img_path = os.path.join("realImages", fabric_id)
    if not os.path.exists(img_path):
        return jsonify({"error": "Görsel bulunamadı"})
    
    # Geliştirilmiş renk analizi kullanarak görselin dominant rengini ve diğer özelliklerini bul
    try:
        # Tam renk analizi (daha yavaş ama daha doğru)
        color_analysis = analyze_image_colors(img_path)
        dominant_color = color_analysis["dominant_color"]
        color_name = color_analysis["color_name"]
        dominant_hsv = color_analysis["dominant_color_hsv"]
        secondary_colors = color_analysis["secondary_colors"]
    except Exception as e:
        print(f"Renk analizi hatası: {str(e)}")
        # Sorun durumunda daha basit yönteme dön
        dominant_color = extract_dominant_color_improved(img_path, "histogram")
        dominant_hsv = rgb_to_hsv(dominant_color)
        color_name = identify_color_group(dominant_hsv)
        secondary_colors = []
    
    # Uyumlu renkleri bul
    harmonious_colors = find_harmonious_colors(dominant_color, harmony_type)
    
    # İkincil renkler için de uyumlu renkler bul (maksimum 1 ikincil renk)
    all_harmonious_colors = harmonious_colors.copy()
    if secondary_colors and len(secondary_colors) > 0:
        secondary_harmonious = find_harmonious_colors(secondary_colors[0], harmony_type)
        all_harmonious_colors.extend(secondary_harmonious)
    
    # Tüm görsellerle renk benzerliği karşılaştırması
    with open("image_metadata_map.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    results = []
    for filename, meta in metadata.items():
        if filename == fabric_id:
            continue  # Kendisini atla
            
        # Filtreleri kontrol et
        if current_season_only and meta.get("season") != metadata.get(fabric_id, {}).get("season"):
            continue
            
        if current_quality_only and meta.get("quality") != metadata.get(fabric_id, {}).get("quality"):
            continue
        
        img_path = os.path.join("realImages", filename)
        if not os.path.exists(img_path):
            continue
        
        # İlgili görselin dominant rengini bul (hızlı yöntem)
        try:
            img_color = extract_dominant_color_improved(img_path, "histogram")
        except Exception:
            continue
        
        # En yüksek renk benzerliğini bul
        max_similarity = 0
        for harm_color in all_harmonious_colors:
            similarity = calculate_color_similarity(harm_color, img_color)
            max_similarity = max(max_similarity, similarity)
        
        if max_similarity > threshold:  # Benzerlik eşiği
            results.append({
                "filename": filename,
                "harmony": max_similarity,
                "design": meta.get("design"),
                "season": meta.get("season"),
                "quality": meta.get("quality"),
                "features": meta.get("features", []),
                "dominant_color": img_color,
                "color_name": identify_color_group(rgb_to_hsv(img_color))
            })
    
    # Benzerliğe göre sırala
    results.sort(key=lambda x: x["harmony"], reverse=True)
    
    # Sonuçları sınırla
    results = results[:result_count]
    
    # Renk analizi sonuçlarını da ekle
    result_with_info = {
        "results": results,
        "source_info": {
            "fabric_id": fabric_id,
            "dominant_color": dominant_color,
            "color_name": color_name,
            "harmony_type": harmony_type,
            "hsv": [round(dominant_hsv[0] * 360), round(dominant_hsv[1] * 100), round(dominant_hsv[2] * 100)],
            "harmonious_colors": [{"rgb": color, "name": identify_color_group(rgb_to_hsv(color))} for color in harmonious_colors]
        }
    }
    
    return jsonify(result_with_info)
# Yeni: Faiss indekslerini sıfırlama endpoint'i
@app.route("/reset-faiss-indexes")
def reset_faiss_indexes():
    global faiss_indexes, cached_features, cached_filenames, cached_metadata
    faiss_indexes = {}
    cached_features = {}
    cached_filenames = {}
    cached_metadata = None
    return jsonify({"status": "ok", "message": "Faiss indeksleri sıfırlandı."})

# app.py başlatılırken Faiss indekslerinin durumunu kontrol et
def check_faiss_reset_flag():
    flag_file = "reset_faiss_indexes.flag"
    if os.path.exists(flag_file):
        # Dosyayı sil
        os.remove(flag_file)
        # Faiss indekslerini sıfırla
        global faiss_indexes, cached_features, cached_filenames, cached_metadata
        faiss_indexes = {}
        cached_features = {}
        cached_filenames = {}
        cached_metadata = None
        print("🔄 Faiss indeksleri sıfırlandı (reset flag algılandı)")




@app.route("/color-spectrum")
def get_color_spectrum():
    """
    Renk spektrumu yapısını oluşturur ve döndürür.
    
    URL parametreleri:
    - model: Spektrum model tipi (default: 'color')
    - divisions: Ton (hue) bölünme sayısı (default: 12)
    - saturation_levels: Doygunluk seviye sayısı (default: 3)
    - value_levels: Parlaklık seviye sayısı (default: 3)
    - rebuild: Spektrumu yeniden oluşturur (default: False)
    - save_version: Spektrumu versiyon olarak kaydeder (default: False)
    - version_name: Versiyon adı (default: 'spectrum-v1')
    - comment: Versiyon açıklaması (default: '')
    
    Returns:
        Renk spektrumu yapısını içeren JSON
    """
    # URL parametrelerini al
    model_type = request.args.get("model", "color")
    divisions = int(request.args.get("divisions", 12))
    saturation_levels = int(request.args.get("saturation_levels", 3))
    value_levels = int(request.args.get("value_levels", 3))
    rebuild = request.args.get("rebuild", "false").lower() == "true"
    save_version = request.args.get("save_version", "false").lower() == "true"
    version_name = request.args.get("version_name", "spectrum-v1")
    comment = request.args.get("comment", "Renk spektrumu tabanlı organizasyon")
    
    # Spektrum dosya yolları
    spectrum_path = f"exported_clusters/{model_type}/spectrum.json"
    
    # Eğer yeniden oluşturma istenmediyse ve spektrum zaten varsa, mevcut spektrumu kullan
    if not rebuild and os.path.exists(spectrum_path):
        try:
            with open(spectrum_path, "r", encoding="utf-8") as f:
                spectrum = json.load(f)
                
            print(f"📊 Mevcut renk spektrumu yüklendi: {spectrum_path}")
            
            # İstatistikleri hesapla
            stats = color_spectrum.get_color_spectrum_statistics(spectrum)
            
            return jsonify({
                "spectrum": spectrum,
                "statistics": stats,
                "message": "Mevcut renk spektrumu yüklendi."
            })
        except Exception as e:
            print(f"❌ Spektrum yükleme hatası: {str(e)}")
    
    # Spektrumu yeniden oluştur
    print(f"🔄 Renk spektrumu oluşturuluyor: {divisions} bölüm, {saturation_levels} doygunluk seviyesi, {value_levels} parlaklık seviyesi")
    
    try:
        # Görseller klasörünü kontrol et
        if os.path.exists("realImages"):
            # Spektrumu oluştur
            spectrum = color_spectrum.build_spectrum_from_directory(
                "realImages", 
                divisions=divisions,
                saturation_levels=saturation_levels,
                value_levels=value_levels
            )
            
            # Spektrumu kaydet
            os.makedirs(os.path.dirname(spectrum_path), exist_ok=True)
            with open(spectrum_path, "w", encoding="utf-8") as f:
                json.dump(spectrum, f, ensure_ascii=False, indent=2)
            
            # İstatistikleri hesapla
            stats = color_spectrum.get_color_spectrum_statistics(spectrum)
            
            # Eğer istenirse, spektrumu versiyon olarak kaydet
            if save_version:
                version_info = color_spectrum.export_spectrum_version(
                    spectrum, version_name=version_name, model_type=model_type, comment=comment
                )
                
                return jsonify({
                    "spectrum": spectrum,
                    "statistics": stats,
                    "version": version_info,
                    "message": f"Renk spektrumu oluşturuldu ve '{version_name}' versiyonu olarak kaydedildi."
                })
            
            return jsonify({
                "spectrum": spectrum,
                "statistics": stats,
                "message": "Renk spektrumu oluşturuldu."
            })
        else:
            return jsonify({
                "error": "realImages klasörü bulunamadı."
            }), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Spektrum oluşturma hatası: {str(e)}"
        }), 500


@app.route("/dominant-colors")
def get_dominant_colors():
    """
    Bir görselin dominant renklerini analiz eder ve döndürür.
    
    URL parametreleri:
    - filename: Analiz edilecek görselin dosya adı
    - method: Dominant renk çıkarma yöntemi (default: 'histogram', options: 'histogram', 'kmeans', 'average', 'resize')
    - count: Çıkarılacak renk sayısı (default: 5)
    
    Returns:
        Dominant renk analiz sonuçlarını içeren JSON
    """
    # URL parametrelerini al
    filename = request.args.get("filename")
    method = request.args.get("method", "histogram")
    count = int(request.args.get("count", 5))
    
    # Filename kontrolü
    if not filename:
        return jsonify({
            "error": "filename parametresi gerekli."
        }), 400
    
    # Görsel dosya yolu
    image_path = f"realImages/{filename}"
    
    # Dosya varlığını kontrol et
    if not os.path.exists(image_path):
        return jsonify({
            "error": f"Görsel bulunamadı: {filename}"
        }), 404
    
    try:
        # Dominant renkleri çıkar
        if count > 1:
            dominant_colors = color_utils.extract_dominant_colors(
                image_path, method=method, k=count
            )
            
            # Renk bilgilerini hazırla
            colors_info = []
            for i, rgb in enumerate(dominant_colors):
                hsv = color_utils.rgb_to_hsv(rgb)
                color_name = color_utils.identify_color_group(hsv)
                
                colors_info.append({
                    "index": i,
                    "rgb": rgb,
                    "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                    "hsv": [
                        round(hsv[0] * 360, 1),  # 0-360 derece
                        round(hsv[1] * 100, 1),  # 0-100%
                        round(hsv[2] * 100, 1)   # 0-100%
                    ],
                    "color_name": color_name
                })
        else:
            # Tek dominant renk
            rgb = color_utils.extract_dominant_color_improved(image_path, method=method)
            hsv = color_utils.rgb_to_hsv(rgb)
            color_name = color_utils.identify_color_group(hsv)
            
            colors_info = [{
                "index": 0,
                "rgb": rgb,
                "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                "hsv": [
                    round(hsv[0] * 360, 1),  # 0-360 derece
                    round(hsv[1] * 100, 1),  # 0-100%
                    round(hsv[2] * 100, 1)   # 0-100%
                ],
                "color_name": color_name
            }]
        
        # Daha detaylı renk analizi
        detailed_analysis = color_utils.analyze_image_colors(image_path)
        
        # Harmonious colors
        harmonious_colors = []
        for harmony_type in ["complementary", "analogous", "triadic", "split-complementary", "monochromatic"]:
            # İlk dominant renk için uyumlu renkleri bul
            rgb = dominant_colors[0] if count > 1 else rgb
            harm_colors = color_utils.find_harmonious_colors(rgb, harmony_type)
            
            harm_info = []
            for i, harm_rgb in enumerate(harm_colors):
                harm_hsv = color_utils.rgb_to_hsv(harm_rgb)
                harm_color_name = color_utils.identify_color_group(harm_hsv)
                
                harm_info.append({
                    "index": i,
                    "rgb": harm_rgb,
                    "hex": f"#{harm_rgb[0]:02x}{harm_rgb[1]:02x}{harm_rgb[2]:02x}",
                    "hsv": [
                        round(harm_hsv[0] * 360, 1),
                        round(harm_hsv[1] * 100, 1),
                        round(harm_hsv[2] * 100, 1)
                    ],
                    "color_name": harm_color_name
                })
            
            harmonious_colors.append({
                "type": harmony_type,
                "colors": harm_info
            })
        
        # Spektrumda sınıflandırma
        try:
            # Spektrum dosyasını yükle
            spectrum_path = "exported_clusters/color/spectrum.json"
            if os.path.exists(spectrum_path):
                with open(spectrum_path, "r", encoding="utf-8") as f:
                    spectrum = json.load(f)
                
                # İlk dominant renk için spektrum sınıflandırması
                hsv = color_utils.rgb_to_hsv(dominant_colors[0] if count > 1 else rgb)
                indices = color_spectrum.classify_color_in_spectrum(hsv, spectrum)
                group_name = color_spectrum.get_color_group_name(indices, spectrum)
                
                spectrum_info = {
                    "indices": indices,
                    "group_name": group_name
                }
            else:
                spectrum_info = None
        except Exception as e:
            print(f"Spektrum sınıflandırma hatası: {str(e)}")
            spectrum_info = None
        
        return jsonify({
            "filename": filename,
            "dominant_colors": colors_info,
            "harmonious_colors": harmonious_colors,
            "spectrum_classification": spectrum_info,
            "detailed_analysis": {
                "color_distribution": detailed_analysis["color_distribution"],
                "dominant_color_name": detailed_analysis["color_name"]
            },
            "method": method
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Renk analizi hatası: {str(e)}"
        }), 500



@app.route('/create-cluster-version', methods=['POST'])
def create_cluster_version():
    """
    Yeni bir küme versiyonu oluşturma endpoint'i.
    
    Model türüne göre farklı kümeleme yaklaşımları kullanır:
    - Model tipi "color" ise renk spektrumu tabanlı sınıflandırma kullanır
    - Diğer modeller için standart auto_cluster.py'yi kullanır
    """
    try:
        # İstek verilerini al
        data = request.get_json()
        model_type = data.get("model")
        version = data.get("version")
        algorithm = data.get("algorithm", "kmeans")  # Varsayılan k-means
        
        if not model_type or not version:
            return jsonify({"status": "error", "message": "Model ve versiyon gerekli."})
        
        # Model ve versiyon bilgisini logla
        print(f"💾 Versiyon oluşturuluyor: {model_type}/{version}, algoritma: {algorithm}")
        
        # Konfigürasyon parametrelerini hazırla
        config = {
            "model_type": model_type,
            "version": version,
            "algorithm": algorithm
        }
        
        # Algoritma parametrelerini ekle
        if "parameters" in data:
            config.update(data.get("parameters", {}))
        
        # Renk modeli mi kontrol et
        if model_type == "color":
            # Renk tabanlı kümeleme için color_cluster modülünü kullan
            print(f"🎨 Renk modeli için renk spektrumu tabanlı organizasyon kullanılıyor")
            import color_cluster
            version_data = color_cluster.cluster_images(config)
            
            return jsonify({
                "status": "ok", 
                "message": "Renk spektrumu tabanlı organizasyon tamamlandı.",
                "version": version,
                "cluster_count": len(version_data.get("clusters", {}))
            })
        else:
            # Standart kümeleme için auto_cluster modülünü kullan
            print(f"🔍 Standart kümeleme algoritması kullanılıyor")
            import auto_cluster
            result = auto_cluster.main(config)
            
            return jsonify({
                "status": "ok",
                "message": f"{algorithm} algoritması ile kümeleme tamamlandı.",
                "version": version,
                "outliers": result.get("outliers", [])
            })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Versiyon oluşturma hatası: {str(e)}")
        print(error_details)
        return jsonify({"status": "error", "message": str(e), "details": error_details})





@app.route("/find-similar-colors")
def find_similar_colors():
    """
    Faiss kullanarak benzer renklere sahip görselleri arar.
    
    URL parametreleri:
    - rgb: RGB renk değeri (örn: 255,0,0)
    - hex: HEX renk değeri (örn: #ff0000) - rgb parametresi önceliklidir
    - hsv: HSV renk değeri (örn: 0,100,100) - rgb ve hex önceliklidir
    - k: Döndürülecek sonuç sayısı (default: 50)
    - use_hsv: HSV renk uzayı kullanma (default: true)
    - model: Spektrum model tipi (default: 'color')
    
    Returns:
        Benzer renklere sahip görsellerin listesi
    """
    import time
    start_time = time.time()
    
    # URL parametrelerini al
    rgb_param = request.args.get("rgb")
    hex_param = request.args.get("hex", "")
    hsv_param = request.args.get("hsv")
    k = int(request.args.get("k", 50))
    use_hsv = request.args.get("use_hsv", "true").lower() == "true"
    model_type = request.args.get("model", "color")
    
    # Spektrum ve indeks dosya yolları
    spectrum_path = f"exported_clusters/{model_type}/spectrum.json"
    index_path = f"exported_clusters/{model_type}/faiss_index.bin"
    mapping_path = f"exported_clusters/{model_type}/index_mapping.json"
    
    # Renk değeri kontrolü
    if not rgb_param and not hex_param and not hsv_param:
        return jsonify({
            "error": "rgb, hex veya hsv parametrelerinden biri gerekli."
        }), 400
    
    # Renk değerini HSV'ye dönüştür
    try:
        if rgb_param:
            # RGB parametresi (örn: 255,0,0)
            rgb = [int(x) for x in rgb_param.split(",")]
            hsv = color_utils.rgb_to_hsv(rgb)
        elif hex_param:
            # HEX parametresi (örn: #ff0000)
            hex_color = hex_param.lstrip("#")
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            hsv = color_utils.rgb_to_hsv(rgb)
        elif hsv_param:
            # HSV parametresi (örn: 0,100,100) - 0-360, 0-100, 0-100 aralığından 0-1 aralığına dönüştür
            hsv_values = [float(x) for x in hsv_param.split(",")]
            hsv = (hsv_values[0] / 360.0, hsv_values[1] / 100.0, hsv_values[2] / 100.0)
    except Exception as e:
        return jsonify({
            "error": f"Renk dönüşüm hatası: {str(e)}"
        }), 400
    
    # Spektrumu kontrol et
    if not os.path.exists(spectrum_path):
        return jsonify({
            "error": f"Spektrum bulunamadı. Önce /color-spectrum endpoint'ini çağırın."
        }), 404
    
    # Spektrumu yükle
    with open(spectrum_path, "r", encoding="utf-8") as f:
        spectrum = json.load(f)
    
    # Faiss indeksini kontrol et ve gerekirse oluştur
    if not os.path.exists(index_path) or not os.path.exists(mapping_path):
        try:
            # Faiss indeksi oluştur
            import faiss
            faiss_index, index_mapping = color_spectrum.create_faiss_index_for_colors(
                spectrum, use_hsv=use_hsv
            )
            
            # İndeksi kaydet
            if faiss_index is not None:
                os.makedirs(os.path.dirname(index_path), exist_ok=True)
                faiss.write_index(faiss_index, index_path)
                
                # index_mapping'in id_to_filename ve filename_to_id anahtarlarını dict'e dönüştürelim
                # (JSON'da int anahtarlar string'e dönüşür)
                serialize_mapping = {
                    "id_to_filename": {str(k): v for k, v in index_mapping["id_to_filename"].items()},
                    "filename_to_id": {k: v for k, v in index_mapping["filename_to_id"].items()}
                }
                
                with open(mapping_path, "w", encoding="utf-8") as f:
                    json.dump(serialize_mapping, f, ensure_ascii=False, indent=2)
        except Exception as e:
            traceback.print_exc()
            return jsonify({
                "error": f"Faiss indeksi oluşturma hatası: {str(e)}"
            }), 500
    
    try:
        # Faiss indeksini yükle
        import faiss
        faiss_index = faiss.read_index(index_path)
        
        # Mapping'i yükle ve int anahtarları tekrar int'e dönüştür
        with open(mapping_path, "r", encoding="utf-8") as f:
            index_mapping_raw = json.load(f)
        
        # id_to_filename'de string anahtarları int'e çevir
        index_mapping = {
            "id_to_filename": {int(k): v for k, v in index_mapping_raw["id_to_filename"].items()},
            "filename_to_id": index_mapping_raw["filename_to_id"]
        }
        
        # Benzer renkleri bul
        results = color_spectrum.find_similar_colors_with_faiss(
            hsv, faiss_index, index_mapping, k=k, use_hsv=use_hsv
        )
        
        # Renk bilgilerini ekle
        for result in results:
            filename = result["filename"]
            try:
                # Dominant renk bilgisini ekle
                image_path = f"realImages/{filename}"
                rgb = color_utils.extract_dominant_color_improved(image_path, method="histogram")
                img_hsv = color_utils.rgb_to_hsv(rgb)
                color_name = color_utils.identify_color_group(img_hsv)
                
                result["dominant_color"] = {
                    "rgb": rgb,
                    "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                    "hsv": [
                        round(img_hsv[0] * 360, 1),
                        round(img_hsv[1] * 100, 1),
                        round(img_hsv[2] * 100, 1)
                    ],
                    "color_name": color_name
                }
            except Exception as e:
                # Hata durumunda sadece hata bilgisini ekle
                result["dominant_color_error"] = str(e)
        
        # İstatistik bilgileri
        rgb_value = color_utils.hsv_to_rgb(hsv)
        stats = {
            "query_color": {
                "hsv": [
                    round(hsv[0] * 360, 1),
                    round(hsv[1] * 100, 1),
                    round(hsv[2] * 100, 1)
                ],
                "rgb": rgb_value,
                "hex": f"#{rgb_value[0]:02x}{rgb_value[1]:02x}{rgb_value[2]:02x}",
                "color_name": color_utils.identify_color_group(hsv)
            },
            "results_count": len(results),
            "search_time": round(time.time() - start_time, 3)
        }
        
        return jsonify({
            "results": results,
            "stats": stats,
            "message": f"Renk araması tamamlandı. {len(results)} sonuç bulundu."
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Renk arama hatası: {str(e)}"
        }), 500
    """
    Faiss kullanarak benzer renklere sahip görselleri arar.
    
    URL parametreleri:
    - rgb: RGB renk değeri (örn: 255,0,0)
    - hex: HEX renk değeri (örn: #ff0000) - rgb parametresi önceliklidir
    - hsv: HSV renk değeri (örn: 0,100,100) - rgb ve hex önceliklidir
    - k: Döndürülecek sonuç sayısı (default: 50)
    - use_hsv: HSV renk uzayı kullanma (default: true)
    - model: Spektrum model tipi (default: 'color')
    
    Returns:
        Benzer renklere sahip görsellerin listesi
    """
    import time
    start_time = time.time()
    # URL parametrelerini al
    rgb_param = request.args.get("rgb")
    hex_param = request.args.get("hex")
    hsv_param = request.args.get("hsv")
    k = int(request.args.get("k", 50))
    use_hsv = request.args.get("use_hsv", "true").lower() == "true"
    model_type = request.args.get("model", "color")
    
    # Spektrum ve indeks dosya yolları
    spectrum_path = f"exported_clusters/{model_type}/spectrum.json"
    index_path = f"exported_clusters/{model_type}/faiss_index.bin"
    mapping_path = f"exported_clusters/{model_type}/index_mapping.json"
    
    # Renk değeri kontrolü
    if not rgb_param and not hex_param and not hsv_param:
        return jsonify({
            "error": "rgb, hex veya hsv parametrelerinden biri gerekli."
        }), 400
    
    # Renk değerini HSV'ye dönüştür
    try:
        if rgb_param:
            # RGB parametresi (örn: 255,0,0)
            rgb = [int(x) for x in rgb_param.split(",")]
            hsv = color_utils.rgb_to_hsv(rgb)
        elif hex_param:
            # HEX parametresi (örn: #ff0000)
            hex_color = hex_param.lstrip("#")

            # Geçerli hex değeri kontrolü
            if len(hex_color) != 6:
                return jsonify({
                    "error": "Geçersiz HEX renk değeri. 6 karakter olmalı (örn: ff0000)."
                }), 400
            try:
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                hsv = color_utils.rgb_to_hsv(rgb)
            except ValueError:
                return jsonify({
                    "error": "Geçersiz HEX renk değeri. Lütfen geçerli bir HEX kodu girin (örn: ff0000)."
                }), 400


        elif hsv_param:
            # HSV parametresi (örn: 0,100,100) - 0-360, 0-100, 0-100 aralığından 0-1 aralığına dönüştür
            hsv_values = [float(x) for x in hsv_param.split(",")]
            hsv = (hsv_values[0] / 360.0, hsv_values[1] / 100.0, hsv_values[2] / 100.0)
    except Exception as e:
        return jsonify({
            "error": f"Renk dönüşüm hatası: {str(e)}"
        }), 400
    
    # Spektrumu kontrol et
    if not os.path.exists(spectrum_path):
        return jsonify({
            "error": f"Spektrum bulunamadı. Önce /color-spectrum endpoint'ini çağırın."
        }), 404
    
    # Spektrumu yükle
    with open(spectrum_path, "r", encoding="utf-8") as f:
        spectrum = json.load(f)
    
    # Faiss indeksini kontrol et ve gerekirse oluştur
    if not os.path.exists(index_path) or not os.path.exists(mapping_path):
        try:
            # Faiss indeksi oluştur
            import faiss
            faiss_index, index_mapping = color_spectrum.create_faiss_index_for_colors(
                spectrum, use_hsv=use_hsv
            )
            
            # İndeksi kaydet
            if faiss_index is not None:
                os.makedirs(os.path.dirname(index_path), exist_ok=True)
                faiss.write_index(faiss_index, index_path)
                
                with open(mapping_path, "w", encoding="utf-8") as f:
                    json.dump(index_mapping, f, ensure_ascii=False, indent=2)
        except Exception as e:
            traceback.print_exc()
            return jsonify({
                "error": f"Faiss indeksi oluşturma hatası: {str(e)}"
            }), 500
    
    try:
        # Faiss indeksini yükle
        import faiss
        faiss_index = faiss.read_index(index_path)
        
        with open(mapping_path, "r", encoding="utf-8") as f:
            index_mapping = json.load(f)
        
        # Benzer renkleri bul
        results = color_spectrum.find_similar_colors_with_faiss(
            hsv, faiss_index, index_mapping, k=k, use_hsv=use_hsv
        )
        
        # Renk bilgilerini ekle
        for result in results:
            filename = result["filename"]
            try:
                # Dominant renk bilgisini ekle
                image_path = f"realImages/{filename}"
                rgb = color_utils.extract_dominant_color_improved(image_path, method="histogram")
                img_hsv = color_utils.rgb_to_hsv(rgb)
                color_name = color_utils.identify_color_group(img_hsv)
                
                result["dominant_color"] = {
                    "rgb": rgb,
                    "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                    "hsv": [
                        round(img_hsv[0] * 360, 1),
                        round(img_hsv[1] * 100, 1),
                        round(img_hsv[2] * 100, 1)
                    ],
                    "color_name": color_name
                }
            except:
                # Hata durumunda boş geç
                pass
        
        # İstatistik bilgileri
        stats = {
            "query_color": {
                "hsv": [
                    round(hsv[0] * 360, 1),
                    round(hsv[1] * 100, 1),
                    round(hsv[2] * 100, 1)
                ],
                "rgb": color_utils.hsv_to_rgb(hsv),
                "hex": f"#{color_utils.hsv_to_rgb(hsv)[0]:02x}{color_utils.hsv_to_rgb(hsv)[1]:02x}{color_utils.hsv_to_rgb(hsv)[2]:02x}",
                "color_name": color_utils.identify_color_group(hsv)
            },
            "results_count": len(results),
            "search_time": round(time.time() - start_time, 3)
        }
        
        return jsonify({
            "results": results,
            "stats": stats,
            "message": f"Renk araması tamamlandı. {len(results)} sonuç bulundu."
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Renk arama hatası: {str(e)}"
        }), 500




# Uygulamayı başlatırken flag kontrolü
check_faiss_reset_flag()




# Renk önbelleği işlemleri
@app.route("/reset-color-cache")
def reset_color_cache():
    """Renk önbelleğini temizler ve Faiss indeksini sıfırlar"""
    try:
        from color_spectrum import clear_color_cache
        clear_color_cache()
        return jsonify({
            "status": "ok",
            "message": "Renk önbelleği temizlendi"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Renk önbelleği temizlenirken hata: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Uygulama başlarken bir temizlik zamanlaması başlat
    clean_timer = threading.Timer(4 * 60 * 60, clean_faiss_indexes_periodically)  # 4 saat
    clean_timer.daemon = True
    clean_timer.start()
    
    app.run(debug=True, use_reloader=False)
