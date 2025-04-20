# app.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas ❤️ Luna
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

app = Flask(__name__)

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

@app.route("/find-similar")
def find_similar():
    filename = request.args.get("filename")
    model = request.args.get("model", "pattern")
    topN = int(request.args.get("topN", 100))
    metric = request.args.get("metric", "cosine")

    # Feature dosyasını oku
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

    if metric == "cosine":
        sims = cosine_similarity(query_vector, features)[0]
        sorted_idx = np.argsort(-sims)
    elif metric == "euclidean":
        dists = euclidean_distances(query_vector, features)[0]
        sorted_idx = np.argsort(dists)
    else:
        return jsonify([])

    results = []
    for i in sorted_idx[1:topN+1]:
        fname = filenames[i]
        meta = metadata.get(fname, {})
        results.append({
            "filename": fname,
            "design": meta.get("design"),
            "season": meta.get("season"),
            "quality": meta.get("quality"),
            "features": meta.get("features", []),
            "cluster": meta.get("cluster"),
            "similarity": float(sims[i]) if metric == "cosine" else None
        })

    return jsonify(results)

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

    cluster_base = os.path.join("exported_clusters", model, version)
    reps_path = os.path.join(cluster_base, "representatives.json")

    if not os.path.exists(reps_path):
        return jsonify({"status": "error", "message": "representatives.json bulunamadı."})

    try:
        with open(reps_path, "r", encoding="utf-8") as f:
            rep_data = json.load(f)

        clusters = rep_data.get("clusters", [])

        # Eski cluster'lardan çıkar
        clusters = [c for c in clusters if c["filename"] not in filenames]

        # Yeni cluster adı
        cluster_ids = [c["cluster"] for c in clusters]
        next_id = max([int(c.split("-")[-1]) for c in cluster_ids if c.startswith("cluster-")]+[0]) + 1
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
            clusters.append({
                "cluster": new_cluster_name,
                "filename": fname,
                "comment": ""
            })

        # ✅ Temsilci olarak ilk görseli representatives listesine ekle
        rep_data.setdefault("representatives", [])
        existing = [r["cluster"] for r in rep_data["representatives"]]
        if new_cluster_name not in existing:
            rep_data["representatives"].append({
                "cluster": new_cluster_name,
                "filename": filenames[0]
            })

        rep_data["clusters"] = clusters
        rep_data.setdefault("version_comment", "")
        rep_data["last_updated"] = datetime.now().isoformat()

        with open(reps_path, "w", encoding="utf-8") as f:
            json.dump(rep_data, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "ok", "new_cluster": new_cluster_name})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)