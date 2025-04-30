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
    """SQLite veritabanı kullanan benzerlik arama endpoint'i"""
    start_time = datetime.now()  # Performans ölçümü için başlangıç zamanı
    
    filters = request.get_json() if request.method == "POST" else None
    filename = request.args.get("filename")
    model = request.args.get("model", "pattern")
    version = request.args.get("version", "v1")
    topN = int(request.args.get("topN", 100))
    metric = request.args.get("metric", "cosine")
    
    print(f"📊 Benzer görsel arama: model={model}, version={version}, metric={metric}")

    # db_utils modülü aracılığıyla SQLite tabanlı arama yap
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

    # Benzer görselleri bul
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


@app.route("/create-cluster", methods=["POST"])
def create_cluster():
    """SQLite entegrasyonlu küme oluşturma endpoint'i"""
    data = request.get_json()
    model = data.get("model")
    version = data.get("version")
    filenames = data.get("filenames", [])

    if not model or not version or not filenames:
        return jsonify({"status": "error", "message": "Model, versiyon ve görsel listesi gerekli."})

    try:
        # Versiyon kontrolü - SQLite kullanarak
        conn = db_utils.create_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Veritabanına bağlanılamadı."})
        
        cursor = conn.cursor()
        
        # Versiyon ID'sini bul
        cursor.execute("""
            SELECT id FROM model_versions
            WHERE model_type = ? AND version_name = ?
        """, (model, version))
        
        version_row = cursor.fetchone()
        version_id = None
        
        # Eğer versiyon yoksa oluştur
        if not version_row:
            print(f"✅ Yeni versiyon oluşturuluyor: {model}/{version}")
            # Versiyon yoksa oluştur
            cursor.execute("""
                INSERT INTO model_versions (model_type, version_name, creation_date, parameters)
                VALUES (?, ?, ?, ?)
            """, (
                model,
                version,
                datetime.now().isoformat(),
                json.dumps({"algorithm": "manual"})
            ))
            version_id = cursor.lastrowid
        else:
            version_id = version_row['id']
        
        # Görsel ID'lerini al
        placeholders = ','.join(['?' for _ in filenames])
        cursor.execute(f"""
            SELECT id, filename FROM fabrics 
            WHERE filename IN ({placeholders})
        """, filenames)
        
        fabric_ids = {row['filename']: row['id'] for row in cursor.fetchall()}
        
        # Eğer bazı görseller bulunamadıysa uyar
        missing_files = [f for f in filenames if f not in fabric_ids]
        if missing_files:
            print(f"⚠️ Bu dosyalar veritabanında bulunamadı: {missing_files}")
        
        # Bu görsellerin mevcut kümelerden çıkarılması
        # Önce bu versiyondaki tüm kümeleri bul
        cursor.execute("""
            SELECT c.id, c.cluster_number, c.representative_id 
            FROM clusters c WHERE c.version_id = ?
        """, (version_id,))
        
        clusters = cursor.fetchall()
        
        for cluster in clusters:
            # Bu kümede bulunan görselleri bul
            cursor.execute("""
                SELECT fabric_id FROM fabric_clusters 
                WHERE cluster_id = ? AND fabric_id IN ({})
            """.format(','.join(['?' for _ in fabric_ids.values()])), 
                [cluster['id']] + list(fabric_ids.values()))
            
            to_remove = cursor.fetchall()
            
            # Bu görselleri kümeden çıkar
            for row in to_remove:
                cursor.execute("""
                    DELETE FROM fabric_clusters 
                    WHERE cluster_id = ? AND fabric_id = ?
                """, (cluster['id'], row['fabric_id']))
            
            # Eğer temsil eden görsel çıkarıldıysa
            if cluster['representative_id'] in fabric_ids.values():
                # Geriye kalan herhangi bir üye var mı?
                cursor.execute("""
                    SELECT fabric_id FROM fabric_clusters 
                    WHERE cluster_id = ? LIMIT 1
                """, (cluster['id'],))
                
                remaining = cursor.fetchone()
                
                if remaining:
                    # Yeni temsil eden görsel seç
                    cursor.execute("""
                        UPDATE clusters SET representative_id = ? 
                        WHERE id = ?
                    """, (remaining['fabric_id'], cluster['id']))
                else:
                    # Küme tamamen boşaldı, sil
                    cursor.execute("""
                        DELETE FROM clusters 
                        WHERE id = ?
                    """, (cluster['id'],))
        
        # Yeni küme numarası için mevcut en yüksek numarayı bul
        cursor.execute("""
            SELECT MAX(cluster_number) as max_num FROM clusters 
            WHERE version_id = ?
        """, (version_id,))
        
        max_num = cursor.fetchone()
        next_id = 1
        if max_num and max_num['max_num'] is not None:
            next_id = max_num['max_num'] + 1
        
        # Temsil eden görseli seç (ilk görsel)
        representative = filenames[0]
        if representative in fabric_ids:
            # Yeni küme oluştur
            cursor.execute("""
                INSERT INTO clusters (version_id, cluster_number, representative_id)
                VALUES (?, ?, ?)
            """, (version_id, next_id, fabric_ids[representative]))
            
            cluster_id = cursor.lastrowid
            
            # Kümeye görselleri ekle
            for filename in filenames:
                if filename in fabric_ids:
                    cursor.execute("""
                        INSERT INTO fabric_clusters (fabric_id, cluster_id)
                        VALUES (?, ?)
                    """, (fabric_ids[filename], cluster_id))
            
            # Değişiklikleri kaydet
            conn.commit()
            
            new_cluster_name = f"cluster-{next_id}"
            
            # ESKİ YÖNTEM (UYUMLULUK İÇİN): JSON dosyalarını da güncelle
            try:
                # Model verisini al
                model_data = get_model_data(model)
                
                # Versiyon kontrolü
                if version not in model_data["versions"]:
                    model_data["versions"][version] = {
                        "created_at": datetime.now().isoformat(),
                        "comment": f"{model} modeli {version} versiyonu",
                        "algorithm": "manual",
                        "parameters": {},
                        "clusters": {}
                    }
                
                # Eski cluster'lardan seçili görselleri çıkar
                version_data = model_data["versions"][version]
                for cluster_name, cluster_data in list(version_data["clusters"].items()):
                    cluster_data["images"] = [img for img in cluster_data["images"] if img not in filenames]
                    
                    if not cluster_data["images"] or cluster_data["representative"] in filenames:
                        if cluster_data["images"]:
                            cluster_data["representative"] = cluster_data["images"][0]
                        else:
                            del version_data["clusters"][cluster_name]
                
                # Thumbnail klasörünü oluştur (eğer yoksa)
                thumbnail_path = os.path.join("exported_clusters", model, version, "thumbnails")
                os.makedirs(thumbnail_path, exist_ok=True)
                
                # Görsellerin thumbnail'larını kopyala
                for fname in filenames:
                    src_thumb = os.path.join("thumbnails", fname)
                    dst_thumb = os.path.join(thumbnail_path, fname)
                    
                    if os.path.exists(src_thumb):
                        shutil.copy2(src_thumb, dst_thumb)
                        
                    # Metadatada güncelle (eski yöntem)
                    update_metadata(fname, {"cluster": new_cluster_name})
                
                # Yeni cluster'a görselleri ekle
                version_data["clusters"][new_cluster_name] = {
                    "representative": representative,
                    "images": filenames,
                    "comment": ""
                }
                
                # Model verisini kaydet
                save_model_data(model, model_data)
            except Exception as e:
                print(f"⚠️ JSON dosya güncellemesi başarısız: {str(e)}")
            
            return jsonify({"status": "ok", "new_cluster": new_cluster_name})
        else:
            # Temsil eden görsel bulunamadı
            conn.rollback()
            return jsonify({"status": "error", "message": "Temsil eden görsel bulunamadı."})

    except Exception as e:
        import traceback
        print(f"Cluster oluşturma hatası: {str(e)}")
        print(traceback.format_exc())
        
        # Hata durumunda işlemi geri al
        if 'conn' in locals():
            conn.rollback()
        
        return jsonify({"status": "error", "message": str(e)})
    finally:
        # Bağlantıyı kapat
        if 'conn' in locals() and conn:
            conn.close()

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

# Yeni: Sistem bilgilerini döndür
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
    
    # Parametreleri kontrol et
    if not fabric_id:
        return jsonify({"status": "error", "message": "fabricId parametresi gerekli."})
        
    if harmony_type not in ["complementary", "analogous", "triadic", "split_complementary", "monochromatic"]:
        harmony_type = "complementary"  # Varsayılan olarak tamamlayıcı renk kullan
    
    # Seçilen kumaşın dosya yolu
    img_path = os.path.join("realImages", fabric_id)
    if not os.path.exists(img_path):
        return jsonify({"status": "error", "message": f"Görsel dosyası bulunamadı: {fabric_id}"})
    
    # Metadata dosyasını kontrol et
    if not os.path.exists("image_metadata_map.json"):
        return jsonify({"status": "error", "message": "Metadata dosyası bulunamadı."})
    
    # Metadata yükle
    with open("image_metadata_map.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # Kumaşın 1x1 indirgenerek dominant renk bilgisini al
    img = cv2.imread(img_path)
    if img is None:
        return jsonify({"status": "error", "message": "Görsel dosyası okunamadı."})
    
    # RGB dominant rengi al (BGR'den RGB'ye dönüştür)
    dominant_color = cv2.resize(img, (1, 1))[0, 0].tolist()  # [B, G, R] formatında
    dominant_color = dominant_color[::-1]  # [R, G, B] formatına dönüştür
    
    # Uyumlu renkleri bul
    harmonious_colors = find_harmonious_colors(dominant_color, harmony_type)
    
    # Referans kumaşın metadata bilgisini al (filtreleme için)
    reference_metadata = metadata.get(fabric_id, {})
    reference_season = reference_metadata.get("season")
    reference_quality = reference_metadata.get("quality")
    
    # Döndürülecek sonuçları hazırla
    results = []
    found_count = 0
    
    # Tüm realImages klasöründeki kumaşları tara
    all_fabrics = [f for f in os.listdir("realImages") if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for fabric_name in all_fabrics:
        if fabric_name == fabric_id:
            continue  # Kendisini dışarıda bırak
        
        # Bu kumaşın metadata bilgisini al (eğer varsa)
        fabric_metadata = metadata.get(fabric_name, {})
        
        # Filtreleme seçenekleri kontrol
        if current_season_only and reference_season and fabric_metadata.get("season") != reference_season:
            continue  # Mevsim eşleşmezse atla
            
        if current_quality_only and reference_quality and fabric_metadata.get("quality") != reference_quality:
            continue  # Kalite eşleşmezse atla
        
        fabric_img_path = os.path.join("realImages", fabric_name)
        fabric_img = cv2.imread(fabric_img_path)
        if fabric_img is None:
            continue
        
        # Kumaşın dominant rengini al (BGR'den RGB'ye dönüştür)
        fabric_dominant_color = cv2.resize(fabric_img, (1, 1))[0, 0].tolist()[::-1]  # [R, G, B]
        
        # Bu kumaşın rengi, uyumlu renklerden herhangi birine ne kadar benzer?
        best_similarity = 0
        best_harmony_color = None
        
        for harmonious_color in harmonious_colors:
            similarity = calculate_color_similarity(harmonious_color, fabric_dominant_color)
            if similarity > best_similarity:
                best_similarity = similarity
                best_harmony_color = harmonious_color
        
        # Benzerlik belirli bir eşiğin üzerindeyse, sonuçlara ekle
        if best_similarity > threshold:
            results.append({
                "filename": fabric_name,
                "similarity": round(float(best_similarity), 3),
                "harmony_type": harmony_type,
                "harmony_color": best_harmony_color,
                "dominant_color": fabric_dominant_color,
                "design": fabric_metadata.get("design"),
                "season": fabric_metadata.get("season"),
                "features": fabric_metadata.get("features", []),
                "quality": fabric_metadata.get("quality")
            })
            found_count += 1
            
            # Sonuç sayısı limiti aşıldıysa döngüyü sonlandır
            if found_count >= result_count:
                break
    
    # Benzerliğe göre sırala (en benzerden başlayarak)
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    
    # Sonuçları döndür
    return jsonify({
        "status": "success",
        "reference_fabric": fabric_id,
        "reference_color": dominant_color,
        "harmony_type": harmony_type,
        "harmony_colors": harmonious_colors,
        "found_count": found_count,
        "results": results
    })

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

# Uygulamayı başlatırken flag kontrolü
check_faiss_reset_flag()

if __name__ == "__main__":
    # Uygulama başlarken bir temizlik zamanlaması başlat
    clean_timer = threading.Timer(4 * 60 * 60, clean_faiss_indexes_periodically)  # 4 saat
    clean_timer.daemon = True
    clean_timer.start()
    
    app.run(debug=True, use_reloader=False)
