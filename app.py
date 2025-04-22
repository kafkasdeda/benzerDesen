# app.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas
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
import json
import subprocess
import sys
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import shutil
from datetime import datetime
import json
import os
import random
import traceback

app = Flask(__name__)

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
        updated = check_for_updates()
        if updated:
            return jsonify({"status": "🔄 Değişiklik algılandı: metadata yeniden oluşturuluyor..."})
        else:
            return jsonify({"status": "✅ Değişiklik yok, metadata güncel."})
    except Exception as ex:
        return jsonify({"status": f"❌ Hata oluştu: {str(ex)}"})
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
    
    # Sadece istenen versiyonun verisini döndür
    return jsonify({
        "version": version,
        "data": model_data["versions"][version]
    })

@app.route("/find-similar", methods=["GET", "POST"])
def find_similar():
    filters = request.get_json() if request.method == "POST" else None
    filename = request.args.get("filename")
    model = request.args.get("model", "pattern")
    topN = int(request.args.get("topN", 100))
    metric = request.args.get("metric", "cosine")

    feature_path = f"image_features/{model}_features.npy"
    index_path = f"image_features/{model}_filenames.json"
    metadata_path = "image_metadata_map.json"

    if not os.path.exists(feature_path) or not os.path.exists(index_path):
        return jsonify([])

    features = np.load(feature_path)
    with open(index_path, "r", encoding="utf-8") as f:
        filenames = json.load(f)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    if filename not in filenames:
        return jsonify([])

    idx = filenames.index(filename)
    query_vector = features[idx].reshape(1, -1)

    # 🎯 Eğer filtre varsa, sadece filtreyi geçen indeksleri topla
    allowed_indices = []
    if filters:
        mix_filters = filters.get("mixFilters", [])
        feature_filters = filters.get("features", [])
        cluster_status = filters.get("cluster", "")

        for i, fname in enumerate(filenames):
            meta = metadata.get(fname, {})
            feature_map = {f[0]: f[1] for f in meta.get("features", [])}
            cluster = meta.get("cluster")

            match_mix = all(
                mix["min"] <= feature_map.get(mix["type"], 0) <= mix["max"]
                for mix in mix_filters
            )

            match_feature = all(f in feature_map for f in feature_filters)

            match_cluster = True
            if cluster_status == "clustered" and not cluster:
                match_cluster = False
            elif cluster_status == "unclustered" and cluster:
                match_cluster = False

            if match_mix and match_feature and match_cluster:
                allowed_indices.append(i)
    else:
        allowed_indices = list(range(len(filenames)))

    if not allowed_indices:
        return jsonify([])

    # 🔍 Sadece filtreyi geçenler ile similarity hesapla
    filtered_features = features[allowed_indices]
    if metric == "cosine":
        sims = cosine_similarity(query_vector, filtered_features)[0]
    elif metric == "euclidean":
        dists = euclidean_distances(query_vector, filtered_features)[0]
        sims = 1 / (1 + dists)
    else:
        return jsonify([])

    sorted_local_idx = np.argsort(-sims)
    final_results = []
    for local_idx in sorted_local_idx[:topN]:
        global_idx = allowed_indices[local_idx]
        fname = filenames[global_idx]
        meta = metadata.get(fname, {})
        final_results.append({
            "filename": fname,
            "design": meta.get("design"),
            "season": meta.get("season"),
            "quality": meta.get("quality"),
            "features": meta.get("features", []),
            "cluster": meta.get("cluster"),
            "similarity": float(sims[local_idx])
        })

    return jsonify(final_results)


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
    data = request.get_json()
    model = data.get("model")
    version = data.get("version")
    filenames = data.get("filenames", [])

    if not model or not version or not filenames:
        return jsonify({"status": "error", "message": "Model, versiyon ve görsel listesi gerekli."})

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
            
            # Eğer cluster boşalmışsa ve temsil eden görsel de çıkarıldıysa, cluster'ı sil
            if not cluster_data["images"] or cluster_data["representative"] in filenames:
                if cluster_data["images"]:
                    # Boş değilse ama temsil eden görsel çıkarıldıysa, yeni temsil eden görsel seç
                    cluster_data["representative"] = cluster_data["images"][0]
                else:
                    # Tamamen boşsa cluster'ı sil
                    del version_data["clusters"][cluster_name]
        
        # Yeni cluster adı
        existing_clusters = list(version_data["clusters"].keys())
        cluster_numbers = [int(c.split("-")[-1]) for c in existing_clusters if c.startswith("cluster-") and c.split("-")[-1].isdigit()]
        next_id = max(cluster_numbers + [0]) + 1
        new_cluster_name = f"cluster-{next_id}"
        
        # Thumbnail klasörünü oluştur (eğer yoksa)
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
        
        # Yeni cluster'a görselleri ekle
        version_data["clusters"][new_cluster_name] = {
            "representative": filenames[0],
            "images": filenames,
            "comment": ""
        }
        
        # Model verisini kaydet
        save_model_data(model, model_data)

        return jsonify({"status": "ok", "new_cluster": new_cluster_name})

    except Exception as e:
        import traceback
        print(f"Cluster oluşturma hatası: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)})

# --- YENİ: Feedback kaydı alma endpointi ---
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    feedback = request.get_json()
    print("📩 Feedback alındı:", feedback)

    feedback_file = "feedback_log.json"
    feedback_list = []

    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            try:
                feedback_list = json.load(f)
            except json.JSONDecodeError:
                feedback_list = []

    # Aynı anchor-output-model-version varsa güncelle / iptal et
    anchor = feedback.get("anchor")
    output = feedback.get("output")
    model = feedback.get("model")
    version = feedback.get("version")

    feedback_list = [f for f in feedback_list if not (
        f.get("anchor") == anchor and
        f.get("output") == output and
        f.get("model") == model and
        f.get("version") == version
    )]

    if feedback.get("feedback") is not None:
        feedback_list.append(feedback)

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(feedback_list, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "ok"})

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
        
        # Auto cluster sonucunu versions.json'a aktar
        # (auto_cluster.py'ye de değişiklikler gerekecek)
        model_data["current_version"] = new_version
        if new_version not in model_data["versions"]:
            model_data["versions"][new_version] = {
                "created_at": datetime.now().isoformat(),
                "comment": comment,
                "algorithm": algorithm,
                "parameters": parameters,
                "clusters": {}  # Bunu auto_cluster.py dolduracak
            }
        
        # Veriyi kaydet
        save_model_data(model, model_data)
        
        return jsonify({
            "status": "ok", 
            "version": new_version,
            "cluster_count": cluster_count,
            "message": f"{model} modeli için {new_version} versiyonu oluşturuldu."
        })
    
    except Exception as e:
        import traceback
        print(f"Versiyon oluşturma hatası: {str(e)}")
        print(traceback.format_exc())
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

if __name__ == "__main__":
    app.run(debug=True)
