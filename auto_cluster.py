# auto_cluster.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas
# Açıklama:
# Bu dosya, Power User arayüzünden gelen parametrelere göre otomatik görsel kümeleri oluşturur.
# Desteklenen algoritmalar: KMeans, DBSCAN, Hierarchical
# Giriş verileri: image_features/{model_type}_features.npy ve corresponding image list
# Çıktı: exported_clusters/{model_type}/{version}/cluster-{id}/image.jpg

import os
import json
import numpy as np
import shutil
from datetime import datetime
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import StandardScaler

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

# 4. Sonuçları klasörlere ayır
output_dir = os.path.join("exported_clusters", model_type, version)  # Versiyon eklendi
os.makedirs(output_dir, exist_ok=True)  # Versiyon klasörünü oluştur

# Önceki cluster'ları temizle
for item in os.listdir(output_dir):
    if item.startswith("cluster-"):
        shutil.rmtree(os.path.join(output_dir, item), ignore_errors=True)

# representatives.json için temel yapı oluştur
rep_data = {
    "representatives": [],
    "clusters": [],
    "version_comment": f"{model_type} modeli {version} versiyonu - {algorithm} ile oluşturuldu",
    "last_updated": datetime.now().isoformat()
}

for idx, label in enumerate(labels):
    if label == -1:
        continue  # DBSCAN outlier
    cluster_name = f"cluster-{label}"
    cluster_folder = os.path.join(output_dir, cluster_name)
    os.makedirs(cluster_folder, exist_ok=True)
    
    # Kaynak ve hedef dosya yollarını oluştur
    source_path = image_paths[idx]  # Tam yol zaten image_paths içinde var
    filename = os.path.basename(source_path)
    target_path = os.path.join(cluster_folder, filename)
    
    # Dosyayı kopyala
    if os.path.exists(source_path):
        shutil.copy2(source_path, target_path)
        
        # representatives.json için veri ekle
        rep_data["clusters"].append({
            "cluster": cluster_name,
            "filename": filename,
            "comment": ""
        })
        
        # Her cluster'ın ilk görselini temsilci olarak ekle
        if cluster_name not in [r["cluster"] for r in rep_data["representatives"]]:
            rep_data["representatives"].append({
                "cluster": cluster_name,
                "filename": filename
            })

# representatives.json dosyasını kaydet
rep_path = os.path.join(output_dir, "representatives.json")
with open(rep_path, "w", encoding="utf-8") as f:
    json.dump(rep_data, f, indent=2, ensure_ascii=False)

print(f"✅ Otomatik clusterlama tamamlandı. {len(set(labels)) - (1 if -1 in labels else 0)} küme oluşturuldu.")
