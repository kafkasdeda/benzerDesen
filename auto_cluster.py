# auto_cluster.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas
# Açıklama:
# Bu dosya, Power User arayüzünden gelen parametrelere göre otomatik görsel kümeleri oluşturur.
# Desteklenen algoritmalar: KMeans, DBSCAN, Hierarchical
# Giriş verileri: image_features/{model_type}_features.npy ve corresponding image list
# Çıktı: exported_clusters/{model_type}/{version}/thumbnails/{image.jpg}
# versions.json güncellenir

import os
import json
import numpy as np
import shutil
from datetime import datetime
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import StandardScaler

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

# 1. Ayarları oku
with open("cluster_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

model_type = config.get("model_type")
version = config.get("version", "v1")  # Versiyon parametresi eklendi
algorithm = config.get("algorithm")

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
if algorithm == "kmeans":
    clustering = KMeans(n_clusters=k, random_state=42)
    labels = clustering.fit_predict(X)
elif algorithm == "dbscan":
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric=distance_metric)
    labels = clustering.fit_predict(X)
elif algorithm == "hierarchical":
    clustering = AgglomerativeClustering(n_clusters=k, linkage=linkage)
    labels = clustering.fit_predict(X)
else:
    raise ValueError(f"Bilinmeyen algoritma: {algorithm}")

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

# Görselleri işle ve cluster'lara ekle
for idx, label in enumerate(labels):
    if label == -1:
        continue  # DBSCAN outlier
        
    # Cluster adı
    cluster_name = f"cluster-{label}"
    
    # Kaynak dosya bilgileri
    source_path = image_paths[idx]  # Tam yol
    filename = os.path.basename(source_path)
    
    # Eğer cluster yoksa oluştur
    if cluster_name not in version_data["clusters"]:
        version_data["clusters"][cluster_name] = {
            "representative": filename,
            "images": [],
            "comment": ""
        }
    
    # Görseli cluster'a ekle
    if filename not in version_data["clusters"][cluster_name]["images"]:
        version_data["clusters"][cluster_name]["images"].append(filename)
    
    # Thumbnail'i kopyala
    src_thumb = os.path.join("thumbnails", filename)
    dst_thumb = os.path.join(thumbnail_dir, filename)
    
    if os.path.exists(src_thumb):
        shutil.copy2(src_thumb, dst_thumb)
    else:
        print(f"[UYARI] {filename} için thumbnail bulunamadı")

# Güncel versiyonu ayarla
model_data["current_version"] = version

# Model verisini kaydet
save_model_data(model_type, model_data)

print(f"✅ Otomatik clusterlama tamamlandı. {len(version_data['clusters'])} küme oluşturuldu.")
