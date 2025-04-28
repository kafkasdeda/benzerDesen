# train_handlers.py - Eğitim ile ilgili endpointler ve işlevler

from flask import jsonify, request
import os
import json
import subprocess
import sys
import torch
from datetime import datetime
import threading

# Devam eden eğitim işleri için global değişken
active_trainings = {}

def setup_training_routes(app):
    """app.py'a eğitim ile ilgili route'ları ekler"""
    
    @app.route("/check-model-exists")
    def check_model_exists():
        model = request.args.get("model", "pattern")
        version = request.args.get("version", "v1")
        
        model_path = os.path.join("models", f"{model}_{version}.pt")
        exists = os.path.exists(model_path)
        
        # Eğer model dosyası varsa, son değişiklik tarihini al
        last_trained = None
        if exists:
            timestamp = os.path.getmtime(model_path)
            last_trained = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")
        
        return jsonify({
            "exists": exists,
            "last_trained": last_trained
        })

    @app.route("/check-gpu-status")
    def check_gpu_status():
        # GPU durumunu kontrol et
        gpu_available = torch.cuda.is_available()
        gpu_name = None
        speedup = None
        
        if gpu_available:
            # GPU bilgilerini al
            try:
                gpu_name = torch.cuda.get_device_name(0)
                # GPU tipine göre hızlanma tahminini belirle
                if "3090" in gpu_name or "A100" in gpu_name:
                    speedup = "20-30x"
                elif "3080" in gpu_name or "2080" in gpu_name:
                    speedup = "15-20x"
                elif "3070" in gpu_name or "2070" in gpu_name:
                    speedup = "10-15x"
                else:
                    speedup = "5-10x"
            except:
                pass
        
        return jsonify({
            "gpu_available": gpu_available,
            "gpu_name": gpu_name,
            "speedup": speedup
        })

    @app.route("/start-training", methods=["POST"])
    def start_training():
        data = request.get_json()
        
        # Eğitim ID'si oluştur
        training_id = f"train_{int(datetime.now().timestamp())}"
        
        # Eğitim konfigürasyonunu kaydet
        with open("train_config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        # Eğitim klasörü yoksa oluştur
        model_type = data["model_type"]
        cluster_path = os.path.join("exported_clusters", model_type)
        os.makedirs(cluster_path, exist_ok=True)
        
        # Eğitimi başlat (arka planda)
        try:
            python_exe = sys.executable
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            # Eğitim sürecini başlat
            process = subprocess.Popen(
                [python_exe, "train_model.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Aktif eğitim bilgilerini kaydet
            active_trainings[training_id] = {
                "process": process,
                "start_time": datetime.now(),
                "config": data,
                "current_epoch": 0,
                "total_epochs": data["epochs"],
                "progress_percent": 0,
                "current_loss": 0,
                "loss_history": [],
                "last_log": "Eğitim başlıyor...",
                "status": "running"
            }
            
            # Eğitim çıktısını dinlemek için ayrı bir thread başlat
            thread = threading.Thread(target=monitor_training_output, args=(training_id, process))
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "status": "started",
                "training_id": training_id
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            })

    @app.route("/training-status")
    def training_status():
        training_id = request.args.get("id")
        
        if training_id not in active_trainings:
            return jsonify({
                "status": "not_found",
                "message": "Eğitim bulunamadı"
            })
        
        training_info = active_trainings[training_id]
        
        # Geçen süreyi hesapla
        elapsed_time = datetime.now() - training_info["start_time"]
        elapsed_seconds = elapsed_time.total_seconds()
        elapsed_str = f"{int(elapsed_seconds // 60)}:{int(elapsed_seconds % 60):02d}"
        
        # Kalan süreyi tahmin et
        remaining_str = "--:--"
        if training_info["current_epoch"] > 0:
            seconds_per_epoch = elapsed_seconds / training_info["current_epoch"]
            remaining_epochs = training_info["total_epochs"] - training_info["current_epoch"]
            remaining_seconds = seconds_per_epoch * remaining_epochs
            remaining_str = f"{int(remaining_seconds // 60)}:{int(remaining_seconds % 60):02d}"
        
        return jsonify({
            "status": training_info["status"],
            "current_epoch": training_info["current_epoch"],
            "total_epochs": training_info["total_epochs"],
            "progress_percent": training_info["progress_percent"],
            "current_loss": training_info["current_loss"],
            "loss_history": training_info["loss_history"],
            "loss_trend": training_info.get("loss_trend", "stable"),
            "last_log": training_info["last_log"],
            "elapsed_time": elapsed_str,
            "remaining_time": remaining_str,
            "error_message": training_info.get("error_message", "")
        })

    @app.route("/stop-training", methods=["POST"])
    def stop_training_route():
        # Aktif eğitimleri durdur
        for training_id, training_info in active_trainings.items():
            if training_info["status"] == "running":
                try:
                    training_info["process"].terminate()
                    training_info["status"] = "stopped"
                except:
                    pass
        
        return jsonify({
            "status": "stopped"
        })

def monitor_training_output(training_id, process):
    """Eğitim sürecinin çıktısını izler ve durum bilgilerini günceller"""
    training_info = active_trainings[training_id]
    
    for line in iter(process.stdout.readline, ''):
        # Çıktıyı işle
        line = line.strip()
        if not line:
            continue
        
        # Epoch bilgisini güncelle
        if line.startswith("Epoch"):
            try:
                parts = line.split(',')
                epoch_info = parts[0].split('/')
                current_epoch = int(epoch_info[0].split()[1])
                total_epochs = int(epoch_info[1])
                
                loss_value = float(parts[1].split(":")[1].strip())
                
                training_info["current_epoch"] = current_epoch
                training_info["total_epochs"] = total_epochs
                training_info["progress_percent"] = (current_epoch / total_epochs) * 100
                training_info["current_loss"] = loss_value
                training_info["loss_history"].append(loss_value)
                training_info["last_log"] = line
                
                # Loss trendini belirle
                if len(training_info["loss_history"]) > 1:
                    prev_loss = training_info["loss_history"][-2]
                    if loss_value < prev_loss:
                        training_info["loss_trend"] = "decreasing"
                    elif loss_value > prev_loss:
                        training_info["loss_trend"] = "increasing"
                    else:
                        training_info["loss_trend"] = "stable"
            except:
                pass
        
        # Diğer önemli mesajlar
        elif "Model kaydedildi" in line:
            training_info["status"] = "completed"
            break
    
    # Süreç tamamlandığında
    return_code = process.wait()
    
    # Eğitim başarısız olduysa
    if return_code != 0:
        training_info["status"] = "failed"
        training_info["error_message"] = process.stderr.read()
    elif training_info["status"] != "stopped":
        training_info["status"] = "completed"