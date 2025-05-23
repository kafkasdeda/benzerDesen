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

@app.route('/clusters/<model>/<version>/representatives.json')
def serve_representatives(model, version):
    folder = os.path.join("exported_clusters", model, version)
    return send_from_directory(folder, "representatives.json")

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

    path = os.path.join("exported_clusters", model, version, "representatives.json")

    if not os.path.exists(path):
        return jsonify({"status": "error", "message": "Dosya bulunamadı."})

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)

        content["version_comment"] = comment

        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

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

    # Ana klasörü oluştur
    cluster_base = os.path.join("exported_clusters", model, version)
    os.makedirs(cluster_base, exist_ok=True)
    
    reps_path = os.path.join(cluster_base, "representatives.json")

    # representatives.json dosyası yoksa oluştur
    if not os.path.exists(reps_path):
        rep_data = {
            "representatives": [],
            "clusters": [],
            "version_comment": f"{model} modeli {version} versiyonu",
            "last_updated": datetime.now().isoformat()
        }
    else:
        try:
            with open(reps_path, "r", encoding="utf-8") as f:
                rep_data = json.load(f)
        except json.JSONDecodeError:
            # Dosya bozuk ise yeniden oluştur
            rep_data = {
                "representatives": [],
                "clusters": [],
                "version_comment": f"{model} modeli {version} versiyonu",
                "last_updated": datetime.now().isoformat()
            }

    try:
        clusters = rep_data.get("clusters", [])

        # Eski cluster'lardan çıkar (aynı görseller varsa)
        clusters = [c for c in clusters if c["filename"] not in filenames]

        # Yeni cluster adı
        cluster_ids = [c["cluster"] for c in clusters]
        existing_ids = [int(c.split("-")[-1]) for c in cluster_ids if c.startswith("cluster-")] 
        next_id = max(existing_ids + [0]) + 1
        new_cluster_name = f"cluster-{next_id}"

        # Yeni klasör oluştur
        new_folder = os.path.join(cluster_base, new_cluster_name)
        os.makedirs(new_folder, exist_ok=True)

        # Görselleri kopyala ve representative listesine ekle
        for i, fname in enumerate(filenames):
            src = os.path.join("realImages", fname)
            dst = os.path.join(new_folder, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                # Metadatada güncelle
                update_metadata(fname, {"cluster": new_cluster_name})
                # Cluster listesine ekle
                clusters.append({
                    "cluster": new_cluster_name,
                    "filename": fname,
                    "comment": ""
                })

        # ✅ Temsilci olarak ilk görseli representatives listesine ekle
        rep_data.setdefault("representatives", [])
        existing = [r["cluster"] for r in rep_data["representatives"]]
        if new_cluster_name not in existing and filenames:
            rep_data["representatives"].append({
                "cluster": new_cluster_name,
                "filename": filenames[0]
            })

        rep_data["clusters"] = clusters
        rep_data.setdefault("version_comment", f"{model} modeli {version} versiyonu")
        rep_data["last_updated"] = datetime.now().isoformat()

        with open(reps_path, "w", encoding="utf-8") as f:
            json.dump(rep_data, f, indent=2, ensure_ascii=False)

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
    model = data.get("model", "pattern")  # Model parametresi eklendi
    version = data.get("version", "v1")    # Versiyon parametresi eklendi
    cluster_name = data.get("cluster")
    images = data.get("images", [])

    if not cluster_name or not images:
        return jsonify({"status": "error", "message": "Eksik bilgi"}), 400

    # Dosya yolları
    metadata_path = "image_metadata_map.json"
    cluster_dir = os.path.join("exported_clusters", model, version, cluster_name)  # Doğru klasör yapısı

    # Klasörü oluştur
    os.makedirs(cluster_dir, exist_ok=True)

    # Metadata dosyasını yükle
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    moved = []

    # Representatives dosyasını kontrol et
    rep_path = os.path.join("exported_clusters", model, version, "representatives.json")
    if os.path.exists(rep_path):
        try:
            with open(rep_path, "r", encoding="utf-8") as f:
                rep_data = json.load(f)
        except json.JSONDecodeError:
            rep_data = {"representatives": [], "clusters": []}
    else:
        rep_data = {"representatives": [], "clusters": [], "version_comment": "", "last_updated": datetime.now().isoformat()}

    # Eski cluster'lardan görselleri çıkar
    rep_data["clusters"] = [c for c in rep_data.get("clusters", []) if c["filename"] not in images]

    for img in images:
        src_path = os.path.join("realImages", img)
        dst_path = os.path.join(cluster_dir, img)

        # Eğer kaynak varsa kopyala
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            moved.append(img)
            
            # Cluster listesine ekle
            rep_data["clusters"].append({
                "cluster": cluster_name,
                "filename": img,
                "comment": ""
            })
        else:
            print(f"⚠️ {img} bulunamadı")

        # Metadata'da cluster güncelle
        if img in metadata:
            metadata[img]["cluster"] = cluster_name
        else:
            print(f"📛 Metadata'da {img} bulunamadı")

    # Metadata'yı kaydet
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    # Representatives dosyasını güncelle
    rep_data["last_updated"] = datetime.now().isoformat()
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(rep_data, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "ok", "moved": moved, "cluster": cluster_name})

@app.route("/available-versions")
def available_versions():
    """Bir model için mevcut tüm versiyonları listeler"""
    model = request.args.get("model", "pattern")
    
    base_path = os.path.join("exported_clusters", model)
    versions = []
    
    try:
        if os.path.exists(base_path):
            for item in os.listdir(base_path):
                full_path = os.path.join(base_path, item)
                if os.path.isdir(full_path):
                    # Versiyon adını oluştur
                    version_name = f"Versiyon {item[1:]}" if item.startswith("v") else item
                    versions.append({"id": item, "name": version_name})
    except Exception as e:
        print(f"Versiyon listesi alınırken hata: {str(e)}")
        
    # Eğer liste boşsa varsayılan ekle
    if not versions:
        versions.append({"id": "v1", "name": "Versiyon 1"})
        
    return jsonify(versions)

if __name__ == "__main__":
    app.run(debug=True)
