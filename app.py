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

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import subprocess
import sys
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>PU Ana Panel - Luna & Kafkas</h2><p>/train ile model eğit, /check-updates ile güncelle kontrol et.</p>"

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

@app.route("/find-similar")
def find_similar():
    filename = request.args.get("filename")
    model = request.args.get("model", "pattern")
    topN = int(request.args.get("topN", 10))
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

if __name__ == "__main__":
    app.run(debug=True)