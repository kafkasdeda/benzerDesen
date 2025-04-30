import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import numpy as np
import time

from db_init import create_connection

def migrate_metadata_to_sqlite():
    """image_metadata_map.json dosyasındaki verileri SQLite'a aktarır"""
    
    print("Metadata verilerini SQLite'a aktarma işlemi başlatıldı...")
    conn = create_connection()
    
    if not conn:
        print("❌ Veritabanı bağlantısı kurulamadı.")
        return False
    
    cursor = conn.cursor()
    
    metadata_path = "image_metadata_map.json"
    if not os.path.exists(metadata_path):
        print(f"❌ {metadata_path} dosyası bulunamadı.")
        return False
    
    try:
        # Metadata dosyasını oku
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        print(f"✅ {len(metadata)} adet kumaş verisi okundu.")
        
        # Her kumaş için kayıt oluştur
        fabric_count = 0
        feature_count = 0
        
        for filename, meta in metadata.items():
            try:
                # Fabric kaydı oluştur
                cursor.execute("""
                    INSERT OR IGNORE INTO fabrics 
                    (filename, design, season, quality, creation_date, last_modified)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    filename, 
                    meta.get('design'), 
                    meta.get('season'), 
                    meta.get('quality'),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                if cursor.rowcount > 0:
                    fabric_count += 1
                
                # Fabric ID'sini al (yeni eklenen veya var olan)
                cursor.execute("SELECT id FROM fabrics WHERE filename = ?", (filename,))
                fabric_id = cursor.fetchone()[0]
                
                # Özellikler varsa ekle
                if 'features' in meta and meta['features']:
                    for feature in meta['features']:
                        if isinstance(feature, list) and len(feature) >= 2:
                            cursor.execute("""
                                INSERT OR IGNORE INTO fabric_features 
                                (fabric_id, feature_name, feature_value)
                                VALUES (?, ?, ?)
                            """, (fabric_id, feature[0], feature[1]))
                            
                            if cursor.rowcount > 0:
                                feature_count += 1
            
            except Exception as e:
                print(f"❌ {filename} kaydı oluşturulurken hata: {e}")
        
        conn.commit()
        print(f"✅ {fabric_count} adet kumaş ve {feature_count} adet özellik kaydedildi.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Metadata aktarma işleminde hata: {e}")
        return False
    finally:
        conn.close()

def migrate_clusters_to_sqlite():
    """exported_clusters klasöründeki versiyon bilgilerini SQLite'a aktarır"""
    
    print("Cluster verilerini SQLite'a aktarma işlemi başlatıldı...")
    conn = create_connection()
    
    if not conn:
        print("❌ Veritabanı bağlantısı kurulamadı.")
        return False
    
    cursor = conn.cursor()
    
    model_types = ["pattern", "color", "texture", "color+pattern"]
    clusters_dir = "exported_clusters"
    
    if not os.path.exists(clusters_dir):
        print(f"❌ {clusters_dir} klasörü bulunamadı.")
        return False
    
    try:
        version_count = 0
        cluster_count = 0
        member_count = 0
        
        for model_type in model_types:
            model_dir = os.path.join(clusters_dir, model_type)
            version_file = os.path.join(model_dir, "versions.json")
            
            if not os.path.exists(version_file):
                print(f"ℹ️ {version_file} dosyası bulunamadı, atlanıyor.")
                continue
            
            with open(version_file, "r", encoding="utf-8") as f:
                versions_data = json.load(f)
            
            # versions_data içinde "versions" anahtarını kontrol et
            if "versions" in versions_data:
                versions = versions_data["versions"]
                print(f"✅ {model_type} modeli için {len(versions)} versiyon bulundu.")
            else:
                # Eski formatı destekle
                versions = versions_data
                print(f"✅ {model_type} modeli için {len(versions) - 1 if 'current_version' in versions else len(versions)} versiyon bulundu (eski format)")
            
            # current_version anahtarını atlama
            if "current_version" in versions:
                versions = {k: v for k, v in versions.items() if k != "current_version"}
            
            for version_name, version_data in versions.items():
                # Parametreler farklı alanda olabilir
                parameters = {}
                if "params" in version_data:
                    parameters = version_data["params"]
                elif "parameters" in version_data:
                    parameters = version_data["parameters"]
                elif "algorithm" in version_data:
                    # Eski format destekle
                    parameters = {"algorithm": version_data.get("algorithm")}
                    if "parameters" in version_data:
                        parameters.update(version_data["parameters"])
                    
                cursor.execute("""
                    INSERT OR IGNORE INTO model_versions
                    (model_type, version_name, creation_date, parameters)
                    VALUES (?, ?, ?, ?)
                """, (
                    model_type,
                    version_name,
                    version_data.get("created_at", datetime.now().isoformat()),
                    json.dumps(parameters)
                ))
                
                if cursor.rowcount > 0:
                    version_count += 1
                
                # Versiyon ID'sini al
                cursor.execute(
                    "SELECT id FROM model_versions WHERE model_type = ? AND version_name = ?", 
                    (model_type, version_name)
                )
                version_id = cursor.fetchone()[0]
                
                # Cluster verilerini ekle
                clusters = version_data.get('clusters', {})
                for cluster_num, cluster_data in clusters.items():
                    rep_file = cluster_data.get('representative') if isinstance(cluster_data, dict) else None
                    if rep_file:
                        # Temsilci kumaşın ID'sini bul
                        cursor.execute(
                            "SELECT id FROM fabrics WHERE filename = ?", 
                            (rep_file,)
                        )
                        rep_result = cursor.fetchone()
                        
                        if rep_result:
                            rep_id = rep_result[0]
                            # Cluster oluştur
                            # Cluster numarasını düzgün şekilde işle
                            try:
                                if isinstance(cluster_num, str) and cluster_num.startswith('cluster-'):
                                    cluster_number = int(cluster_num.split('-')[1])
                                else:
                                    cluster_number = int(cluster_num)
                                
                                cursor.execute("""
                                    INSERT OR IGNORE INTO clusters
                                    (version_id, cluster_number, representative_id)
                                    VALUES (?, ?, ?)
                                """, (version_id, cluster_number, rep_id))
                            except (ValueError, TypeError) as e:
                                print(f"  ⚠️ Cluster numarası dönüştürme hatası: {cluster_num} - {e}")
                                continue
                            
                            if cursor.rowcount > 0:
                                cluster_count += 1
                            
                            # Cluster ID'sini al
                            cursor.execute(
                                "SELECT id FROM clusters WHERE version_id = ? AND cluster_number = ?",
                                (version_id, cluster_number)
                            )
                            cluster_id = cursor.fetchone()[0]
                            
                            # Küme üyelerini ekle
                            # JSON yapısında daha farklı isimler kullanılıyor olabilir - tüm olasılıkları kontrol edelim
                            members = []
                            if isinstance(cluster_data, dict):
                                if 'members' in cluster_data:
                                    members = cluster_data.get('members', [])
                                elif 'images' in cluster_data:
                                    members = cluster_data.get('images', [])
                            
                            for member_file in members:
                                cursor.execute(
                                    "SELECT id FROM fabrics WHERE filename = ?", 
                                    (member_file,)
                                )
                                fabric_result = cursor.fetchone()
                                
                                if fabric_result:
                                    fabric_id = fabric_result[0]
                                    cursor.execute("""
                                        INSERT OR IGNORE INTO fabric_clusters
                                        (fabric_id, cluster_id)
                                        VALUES (?, ?)
                                    """, (fabric_id, cluster_id))
                                    
                                    if cursor.rowcount > 0:
                                        member_count += 1
        
        conn.commit()
        print(f"✅ {version_count} adet versiyon, {cluster_count} adet küme ve {member_count} adet küme üyesi kaydedildi.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Cluster verilerini aktarma işleminde hata: {e}")
        return False
    finally:
        conn.close()

def migrate_feedback_to_sqlite():
    """feedback_log.json dosyasındaki verileri SQLite'a aktarır"""
    
    print("Feedback verilerini SQLite'a aktarma işlemi başlatıldı...")
    conn = create_connection()
    
    if not conn:
        print("❌ Veritabanı bağlantısı kurulamadı.")
        return False
    
    cursor = conn.cursor()
    
    feedback_path = "feedback_log.json"
    if not os.path.exists(feedback_path):
        print(f"ℹ️ {feedback_path} dosyası bulunamadı, atlanıyor.")
        return True  # Dosya yoksa başarılı sayılır
    
    try:
        # Feedback dosyasını oku
        with open(feedback_path, "r", encoding="utf-8") as f:
            feedbacks = json.load(f)
        
        print(f"✅ {len(feedbacks)} adet feedback verisi okundu.")
        
        feedback_count = 0
        for feedback in feedbacks:
            if feedback.get('feedback') is not None:  # Sadece derecelendirme yapılmış olanları al
                # Anchor ID'sini bul
                cursor.execute(
                    "SELECT id FROM fabrics WHERE filename = ?", 
                    (feedback['anchor'],)
                )
                anchor_result = cursor.fetchone()
                
                # Output ID'sini bul
                cursor.execute(
                    "SELECT id FROM fabrics WHERE filename = ?", 
                    (feedback['output'],)
                )
                output_result = cursor.fetchone()
                
                if anchor_result and output_result:
                    cursor.execute("""
                        INSERT OR IGNORE INTO feedback
                        (anchor_id, output_id, model_type, version, rating, feedback_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        anchor_result[0],
                        output_result[0],
                        feedback['model'],
                        feedback['version'],
                        feedback['feedback'],
                        datetime.now().isoformat()
                    ))
                    
                    if cursor.rowcount > 0:
                        feedback_count += 1
        
        conn.commit()
        print(f"✅ {feedback_count} adet feedback verisi kaydedildi.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Feedback verilerini aktarma işleminde hata: {e}")
        return False
    finally:
        conn.close()

def setup_faiss_index_records():
    """Faiss indekslerini kaydedecek klasörü oluştur ve veritabanında kayıtları ayarla"""
    
    print("Faiss indeks kayıtları oluşturuluyor...")
    conn = create_connection()
    
    if not conn:
        print("❌ Veritabanı bağlantısı kurulamadı.")
        return False
    
    cursor = conn.cursor()
    
    # Faiss indeksleri için klasör oluştur
    faiss_dir = "faiss_indexes"
    if not os.path.exists(faiss_dir):
        os.makedirs(faiss_dir)
        print(f"✅ {faiss_dir} klasörü oluşturuldu.")
    
    model_types = ["pattern", "color", "texture", "color+pattern"]
    
    try:
        for model_type in model_types:
            feature_path = os.path.join("image_features", f"{model_type}_features.npy")
            
            if os.path.exists(feature_path):
                # Dimensiyon bilgisini al
                try:
                    features = np.load(feature_path)
                    dimension = features.shape[1] if features.ndim > 1 else 1
                except:
                    dimension = 0
                    print(f"⚠️ {feature_path} dosyası okunamadı, boyut bilgisi alınamadı.")
                
                # Faiss indeksi için kayıt oluştur
                index_path = os.path.join(faiss_dir, f"{model_type}_index.bin")
                cursor.execute("""
                    INSERT OR IGNORE INTO faiss_indexes
                    (model_type, binary_path, dimension, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (
                    model_type,
                    index_path,
                    dimension,
                    None  # Henüz indeks oluşturulmadı
                ))
                
                print(f"✅ {model_type} için Faiss indeks kaydı oluşturuldu.")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Faiss indeks kayıtları oluşturulurken hata: {e}")
        return False
    finally:
        conn.close()

def run_complete_migration():
    """Tüm verileri JSON'dan SQLite'a aktarır"""
    start_time = time.time()
    print("Veritabanı migrasyon işlemi başlatıldı...")
    
    success = True
    
    # Sırayla veri aktarma işlemlerini yap
    if migrate_metadata_to_sqlite():
        print("✅ Metadata aktarımı başarılı.\n")
    else:
        print("❌ Metadata aktarımı başarısız!\n")
        success = False
    
    if migrate_clusters_to_sqlite():
        print("✅ Cluster verilerinin aktarımı başarılı.\n")
    else:
        print("❌ Cluster verilerinin aktarımı başarısız!\n")
        success = False
    
    if migrate_feedback_to_sqlite():
        print("✅ Feedback verilerinin aktarımı başarılı.\n")
    else:
        print("❌ Feedback verilerinin aktarımı başarısız!\n")
        success = False
    
    if setup_faiss_index_records():
        print("✅ Faiss indeks kayıtları başarıyla oluşturuldu.\n")
    else:
        print("❌ Faiss indeks kayıtları oluşturulamadı!\n")
        success = False
    
    end_time = time.time()
    duration = end_time - start_time
    
    if success:
        print(f"✅ Tüm veri aktarımı başarıyla tamamlandı. Geçen süre: {duration:.2f} saniye")
    else:
        print(f"⚠️ Veri aktarımı tamamlandı, ancak bazı hatalar oluştu. Geçen süre: {duration:.2f} saniye")

if __name__ == "__main__":
    run_complete_migration()
