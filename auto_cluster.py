# auto_cluster.py
# Oluşturulma: 2025-04-19
# Güncelleme: 2025-05-06 (Renk modeli için özel sınıflandırma eklendi - FEATURE-009-D)
# Hazırlayan: Kafkas
# Açıklama:
# Bu dosya, Power User arayüzünden gelen parametrelere göre otomatik görsel kümeleri oluşturur.
# Desteklenen algoritmalar: KMeans, DBSCAN, Hierarchical
# Renk modeli için özel spektrum-bazlı sınıflandırma eklendi (color_cluster.py)
# Giriş verileri: image_features/{model_type}_features.npy ve corresponding image list
# Çıktı: exported_clusters/{model_type}/{version}/thumbnails/{image.jpg}
# versions.json güncellenir
# Faiss kullanarak hızlandırılmış kümeleme işlemleri

import os
import json
import numpy as np
import shutil
import time
from datetime import datetime
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import StandardScaler
import faiss

# Renk modeli için özel sınıflandırma modülü
from color_cluster import cluster_images as color_cluster_method

# Yardımcı fonksiyonlar
def get_model_data(model_type):
    """Model JSON verisini okur"""
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

def save_model_data(model_type, data):
    """Model JSON verisini kaydeder"""
    model_path = os.path.join("exported_clusters", model_type, "versions.json")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True

def main(config_path="cluster_config.json"):
    """Ana çalıştırma fonksiyonu"""
    # 1. Ayarları oku
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    model_type = config.get("model_type")
    version = config.get("version", "v1")  # Versiyon parametresi eklendi
    algorithm = config.get("algorithm")
    
    # 🎨 Renk modeli için özel sınıflandırma kullan
    if model_type == "color":
        print(f"🎨 Renk modeli tespit edildi. Özel renk spektrumu sınıflandırması kullanılıyor...")
        return color_cluster_method(config)
        
    # Standart kümeleme algoritmaları için normal akışa devam et

    # Parametreler (opsiyonel olabilir)
    k = int(config.get("k", 5))
    eps = float(config.get("eps", 0.5))
    min_samples = int(config.get("min_samples", 5))
    linkage = config.get("linkage", "ward")

    # 🔍 Model türüne göre benzerlik metriğini belirle
    if model_type == "pattern":
        distance_metric = "cosine"
    elif model_type == "color":
        distance_metric = "euclidean"
    elif model_type == "texture":
        distance_metric = "manhattan"
    elif model_type == "color+pattern":
        distance_metric = "cosine"  # Renk+Desen için cosine similarity kullan
    else:
        distance_metric = "euclidean"  # varsayılan

    feature_path = f"image_features/{model_type}_features.npy"
    image_list_path = f"image_features/{model_type}_filenames.json"

    # 2. Vektörleri ve görselleri yükle
    if not os.path.exists(feature_path):
        raise FileNotFoundError(f"Feature dosyası bulunamadı: {feature_path}")

    X = np.load(feature_path)
    with open(image_list_path, "r", encoding="utf-8") as f:
        image_paths = json.load(f)

    X = StandardScaler().fit_transform(X)

    # 3. Clustering algoritmasını çalıştır
    start_time = time.time()

    # Verileri float32'ye dönüştür (Faiss için daha verimli)
    X = X.astype(np.float32)

    if algorithm == "kmeans":
        # GPU kontrolü
        use_gpu = faiss.get_num_gpus() > 0
        d = X.shape[1]  # özellik vektörü boyutu
        
        print(f"🔍 KMeans kümeleme başlatılıyor: k={k}, vektör boyutu={d}")
        
        if use_gpu:
            print("🚀 GPU kullanılıyor")
            # GPU KMeans
            kmeans = faiss.Kmeans(d, k, niter=300, verbose=True, gpu=True)
        else:
            print("💻 CPU kullanılıyor")
            # CPU KMeans
            kmeans = faiss.Kmeans(d, k, niter=300, verbose=True)
        
        kmeans.train(X)
        centroids = kmeans.centroids
        _, labels = kmeans.index.search(X, 1)
        labels = labels.reshape(-1)
        
        print(f"✅ KMeans kümeleme tamamlandı. {k} küme oluşturuldu.")
        
    elif algorithm == "dbscan":
        print(f"🔍 DBSCAN kümeleme başlatılıyor: eps={eps}, min_samples={min_samples}")
        
        # Model türüne göre metrik seçimi
        if distance_metric == "cosine":
            # Kosinüs mesafesi için vektörleri normalleştir
            faiss.normalize_L2(X)
            clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean")
        else:
            clustering = DBSCAN(eps=eps, min_samples=min_samples, metric=distance_metric)
        
        labels = clustering.fit_predict(X)
        print(f"✅ DBSCAN kümeleme tamamlandı. {len(set(labels)) - (1 if -1 in labels else 0)} küme oluşturuldu.")
        
    elif algorithm == "hierarchical":
        print(f"🔍 Hierarchical kümeleme başlatılıyor: k={k}, linkage={linkage}")
        clustering = AgglomerativeClustering(n_clusters=k, linkage=linkage)
        labels = clustering.fit_predict(X)
        print(f"✅ Hierarchical kümeleme tamamlandı. {k} küme oluşturuldu.")
    else:
        raise ValueError(f"Bilinmeyen algoritma: {algorithm}")

    # Performans ölçümü
    end_time = time.time()
    duration = end_time - start_time
    print(f"⏱️ Kümeleme süresi: {duration:.2f} saniye")

    # 4. Sonuçları model verilerine ekle
    output_dir = os.path.join("exported_clusters", model_type, version)  # Versiyon eklendi
    os.makedirs(output_dir, exist_ok=True)  # Ana klasörü oluştur

    # Thumbnail klasörünü oluştur
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)

    # Model datasını al
    model_data = get_model_data(model_type)

    # Versiyon yoksa oluştur
    if version not in model_data["versions"]:
        model_data["versions"][version] = {
            "created_at": datetime.now().isoformat(),
            "comment": f"{model_type} modeli {version} versiyonu - {algorithm} ile oluşturuldu",
            "algorithm": algorithm,
            "parameters": {
                "k": k if algorithm == "kmeans" else None,
                "eps": eps if algorithm == "dbscan" else None,
                "min_samples": min_samples if algorithm == "dbscan" else None,
                "linkage": linkage if algorithm == "hierarchical" else None
            },
            "clusters": {}
        }

    # Mevcut version verisi
    version_data = model_data["versions"][version]

    # Önceki cluster'ları temizle (eğer varsa)
    version_data["clusters"] = {}

    # Detaylı bir log dosyası oluştur
    log_path = os.path.join(output_dir, "cluster_log.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Algoritma: {algorithm}\n")
        total_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        log_file.write(f"Toplam küme sayısı: {total_clusters}\n")
        log_file.write(f"Kümeleme süresi: {duration:.2f} saniye\n")
        
        # Küme boyutları analizi
        log_file.write("\nKüme boyutları:\n")
        label_counts = {}
        for label in labels:
            if label == -1:  # DBSCAN outlier'ları
                continue
            label_counts[label] = label_counts.get(label, 0) + 1
        
        for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
            log_file.write(f"  Küme {label}: {count} görsel\n")
        
        # Outlier sayısı (sadece DBSCAN için)
        if algorithm == "dbscan":
            outlier_count = np.sum(labels == -1)
            log_file.write(f"\nOutlier sayısı: {outlier_count}\n")

    # Görselleri işle ve cluster'lara ekle
    start_process_time = time.time()
    processed_count = 0

    for idx, label in enumerate(labels):
        if label == -1:
            if algorithm == "dbscan":
                # DBSCAN outlier'ları için özel bir küme oluştur (opsiyonel)
                cluster_name = "outliers"
                # Outlier'lar için bir küme oluştur (yoksa)
                if cluster_name not in version_data["clusters"]:
                    version_data["clusters"][cluster_name] = {
                        "representative": "",  # İlk outlier görseli eklendiğinde güncellenecek
                        "images": [],
                        "comment": "DBSCAN tarafından outlier olarak işaretlenen görseller"
                    }
            else:
                continue  # Diğer algoritmalar için outlier konsepti yok, atla
        else:
            # Normal küme adı
            cluster_name = f"cluster-{label}"
        
        # Kaynak dosya bilgileri
        filename = os.path.basename(image_paths[idx])
        
        # Eğer normal küme yoksa oluştur
        if cluster_name not in version_data["clusters"]:
            version_data["clusters"][cluster_name] = {
                "representative": filename,
                "images": [],
                "comment": ""
            }
        elif cluster_name == "outliers" and not version_data["clusters"][cluster_name]["representative"]:
            # Outlier kümesi için ilk görseli temsilci olarak ayarla
            version_data["clusters"][cluster_name]["representative"] = filename
        
        # Görseli kümeye ekle
        if filename not in version_data["clusters"][cluster_name]["images"]:
            version_data["clusters"][cluster_name]["images"].append(filename)
            processed_count += 1
        
        # Thumbnail'i kopyala
        src_thumb = os.path.join("thumbnails", filename)
        dst_thumb = os.path.join(thumbnail_dir, filename)
        
        if os.path.exists(src_thumb):
            shutil.copy2(src_thumb, dst_thumb)

    process_duration = time.time() - start_process_time
    print(f"⏱️ Görsel işleme süresi: {process_duration:.2f} saniye ({processed_count} görsel işlendi)")

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
        except Exception:
            pass

    # Güncel versiyonu ayarla
    model_data["current_version"] = version

    # Model verisini kaydet
    save_model_data(model_type, model_data)

    total_clusters = len(version_data['clusters'])
    total_images = sum(len(cluster['images']) for cluster in version_data['clusters'].values())
    total_duration = time.time() - start_time

    print(f"✅ Otomatik kümeleme tamamlandı.")
    print(f"   - {total_clusters} küme oluşturuldu")
    print(f"   - {total_images} görsel kümelere atandı")
    print(f"   - Toplam süre: {total_duration:.2f} saniye")

    # Log dosyasına toplam süreyi ekle
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"\nToplam işlem süresi: {total_duration:.2f} saniye\n")
        log_file.write(f"Toplam küme sayısı: {total_clusters}\n")
        log_file.write(f"Toplam işlenen görsel: {total_images}\n")
        
    return version_data

if __name__ == "__main__":
    # Konfigürasyon dosyasından çalıştır
    main()
