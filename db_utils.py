import os
import json
import sqlite3
import numpy as np
import time
import faiss
from datetime import datetime
from pathlib import Path

# SQLite bağlantısı oluşturma
def create_connection():
    """SQLite veritabanı bağlantısı oluşturur"""
    conn = None
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'benzer_desen.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Sonuçları dict olarak almak için
        return conn
    except sqlite3.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
    
    return conn

# --------------- Fabric/Kumaş İşlemleri ---------------

def get_all_fabrics():
    """Tüm kumaşları döndürür"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, design, season, quality, creation_date, last_modified
            FROM fabrics
            ORDER BY filename
        """)
        
        fabrics = [dict(row) for row in cursor.fetchall()]
        return fabrics
    except sqlite3.Error as e:
        print(f"Kumaşları getirme hatası: {e}")
        return []
    finally:
        conn.close()

def get_fabric_by_filename(filename):
    """Dosya adına göre kumaş bilgilerini döndürür"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, design, season, quality, creation_date, last_modified
            FROM fabrics
            WHERE filename = ?
        """, (filename,))
        
        fabric = cursor.fetchone()
        if fabric:
            # Özellikleri getir
            cursor.execute("""
                SELECT feature_name, feature_value
                FROM fabric_features
                WHERE fabric_id = ?
            """, (fabric['id'],))
            
            features = []
            for feature in cursor.fetchall():
                features.append([feature['feature_name'], feature['feature_value']])
            
            result = dict(fabric)
            result['features'] = features
            return result
        
        return None
    except sqlite3.Error as e:
        print(f"Kumaş getirme hatası: {e}")
        return None
    finally:
        conn.close()

def get_fabrics_by_filter(filters):
    """Filtrelere göre kumaşları döndürür"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Temel sorgu
        query = """
            SELECT id, filename, design, season, quality, creation_date, last_modified
            FROM fabrics
            WHERE 1=1
        """
        params = []
        
        # Filtre parametreleri
        if filters:
            if 'design' in filters and filters['design']:
                query += " AND design = ?"
                params.append(filters['design'])
            
            if 'season' in filters and filters['season']:
                query += " AND season = ?"
                params.append(filters['season'])
            
            if 'quality' in filters and filters['quality']:
                query += " AND quality = ?"
                params.append(filters['quality'])
            
            if 'features' in filters and filters['features']:
                for feature in filters['features']:
                    # Her özellik için bir alt sorgu ekliyoruz
                    query += """ 
                        AND id IN (
                            SELECT fabric_id FROM fabric_features 
                            WHERE feature_name = ? AND feature_value = ?
                        )
                    """
                    params.extend([feature[0], feature[1]])
        
        # Sorguyu çalıştır
        cursor.execute(query, params)
        fabrics = [dict(row) for row in cursor.fetchall()]
        
        return fabrics
    except sqlite3.Error as e:
        print(f"Filtrelenmiş kumaşları getirme hatası: {e}")
        return []
    finally:
        conn.close()

def get_distinct_values(field):
    """Belirli bir alandan farklı değerleri getirir (design, season, quality)"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT {field} FROM fabrics WHERE {field} IS NOT NULL")
        values = [row[0] for row in cursor.fetchall()]
        return values
    except sqlite3.Error as e:
        print(f"Farklı değerleri getirme hatası: {e}")
        return []
    finally:
        conn.close()

# --------------- Model Versiyonları İşlemleri ---------------

def get_model_versions(model_type):
    """Belirli bir model türü için tüm versiyonları döndürür"""
    conn = create_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, model_type, version_name, creation_date, parameters
            FROM model_versions
            WHERE model_type = ?
            ORDER BY version_name
        """, (model_type,))
        
        versions = {}
        for row in cursor.fetchall():
            version_name = row['version_name']
            versions[version_name] = {
                'created_at': row['creation_date'],
                'parameters': json.loads(row['parameters']) if row['parameters'] else {}
            }
            
            # Cluster bilgilerini getir
            cursor.execute("""
                SELECT c.id, c.cluster_number, c.representative_id, f.filename as representative
                FROM clusters c
                JOIN fabrics f ON c.representative_id = f.id
                WHERE c.version_id = ?
            """, (row['id'],))
            
            clusters = {}
            for cluster in cursor.fetchall():
                cluster_num = f"cluster-{cluster['cluster_number']}"
                
                # Küme üyelerini getir
                cursor.execute("""
                    SELECT f.filename
                    FROM fabric_clusters fc
                    JOIN fabrics f ON fc.fabric_id = f.id
                    WHERE fc.cluster_id = ?
                """, (cluster['id'],))
                
                members = [member['filename'] for member in cursor.fetchall()]
                
                clusters[cluster_num] = {
                    'representative': cluster['representative'],
                    'images': members,
                    'comment': ""
                }
            
            versions[version_name]['clusters'] = clusters
        
        return {
            'current_version': list(versions.keys())[0] if versions else None,
            'versions': versions
        }
    except sqlite3.Error as e:
        print(f"Model versiyonlarını getirme hatası: {e}")
        return {}
    finally:
        conn.close()

def get_model_version_by_name(model_type, version_name):
    """Model türü ve versiyon adına göre versiyon bilgilerini döndürür"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, model_type, version_name, creation_date, parameters
            FROM model_versions
            WHERE model_type = ? AND version_name = ?
        """, (model_type, version_name))
        
        version = cursor.fetchone()
        if not version:
            return None
        
        version_data = {
            'id': version['id'],
            'created_at': version['creation_date'],
            'parameters': json.loads(version['parameters']) if version['parameters'] else {}
        }
        
        # Cluster bilgilerini getir
        cursor.execute("""
            SELECT c.id, c.cluster_number, c.representative_id, f.filename as representative
            FROM clusters c
            JOIN fabrics f ON c.representative_id = f.id
            WHERE c.version_id = ?
        """, (version['id'],))
        
        clusters = {}
        for cluster in cursor.fetchall():
            cluster_num = f"cluster-{cluster['cluster_number']}"
            
            # Küme üyelerini getir
            cursor.execute("""
                SELECT f.filename
                FROM fabric_clusters fc
                JOIN fabrics f ON fc.fabric_id = f.id
                WHERE fc.cluster_id = ?
            """, (cluster['id'],))
            
            members = [member['filename'] for member in cursor.fetchall()]
            
            clusters[cluster_num] = {
                'representative': cluster['representative'],
                'images': members,
                'comment': ""
            }
        
        version_data['clusters'] = clusters
        return version_data
    except sqlite3.Error as e:
        print(f"Versiyon getirme hatası: {e}")
        return None
    finally:
        conn.close()

def create_model_version(model_type, version_name, parameters, clusters_data):
    """Yeni bir model versiyonu oluşturur"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Model versiyonu ekle
        cursor.execute("""
            INSERT INTO model_versions (model_type, version_name, creation_date, parameters)
            VALUES (?, ?, ?, ?)
        """, (
            model_type,
            version_name,
            datetime.now().isoformat(),
            json.dumps(parameters)
        ))
        
        version_id = cursor.lastrowid
        
        # Cluster'ları ekle
        for cluster_num, cluster_data in clusters_data.items():
            # Temsilci kumaşı bul
            rep_filename = cluster_data.get('representative')
            if not rep_filename:
                continue
                
            cursor.execute("SELECT id FROM fabrics WHERE filename = ?", (rep_filename,))
            rep_result = cursor.fetchone()
            if not rep_result:
                continue
                
            rep_id = rep_result[0]
            
            # Cluster numarası olarak sayısal değer al
            if cluster_num.startswith('cluster-'):
                cluster_number = int(cluster_num[8:])
            else:
                try:
                    cluster_number = int(cluster_num)
                except:
                    continue
            
            # Cluster'ı ekle
            cursor.execute("""
                INSERT INTO clusters (version_id, cluster_number, representative_id)
                VALUES (?, ?, ?)
            """, (version_id, cluster_number, rep_id))
            
            cluster_id = cursor.lastrowid
            
            # Küme üyelerini ekle
            members = cluster_data.get('images', [])
            if not members:
                members = cluster_data.get('members', [])
                
            for member_filename in members:
                cursor.execute("SELECT id FROM fabrics WHERE filename = ?", (member_filename,))
                fabric_result = cursor.fetchone()
                if fabric_result:
                    cursor.execute("""
                        INSERT OR IGNORE INTO fabric_clusters (fabric_id, cluster_id)
                        VALUES (?, ?)
                    """, (fabric_result[0], cluster_id))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Model versiyonu oluşturma hatası: {e}")
        return False
    finally:
        conn.close()

# --------------- Faiss İşlemleri ---------------

def get_faiss_index(model_type, force_rebuild=False):
    """Model türüne göre Faiss indeksi döndürür. 
    Eğer indeks yoksa veya force_rebuild True ise yeniden oluşturur."""
    
    conn = create_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Faiss indeks kaydını kontrol et
        cursor.execute("""
            SELECT binary_path, dimension, last_updated
            FROM faiss_indexes
            WHERE model_type = ?
        """, (model_type,))
        
        index_info = cursor.fetchone()
        binary_path = None
        
        if index_info and not force_rebuild:
            binary_path = index_info['binary_path']
            
            # İndeks dosyası var mı kontrol et
            if os.path.exists(binary_path):
                try:
                    # İndeksi yükle
                    index = faiss.read_index(binary_path)
                    print(f"✅ {model_type} Faiss indeksi yüklendi.")
                    return index
                except Exception as e:
                    print(f"⚠️ Faiss indeksi yüklenirken hata: {e}")
                    # Hata oluştuğunda yeniden oluştur
        
        # İndeksi yeniden oluştur
        print(f"⚠️ {model_type} için Faiss indeksi yeniden oluşturuluyor...")
        
        # Özellik vektörlerini yükle
        feature_path = f"image_features/{model_type}_features.npy"
        if not os.path.exists(feature_path):
            print(f"❌ {feature_path} dosyası bulunamadı!")
            return None
        
        # Vektörleri yükle
        features = np.load(feature_path).astype(np.float32)
        
        # İndeks oluştur
        d = features.shape[1]
        
        # Model tipine göre benzerlik türü seç
        if model_type in ["pattern", "color+pattern"]:
            # Kosinüs benzerliği için L2 normalleştirme
            faiss.normalize_L2(features)
            index = faiss.IndexFlatIP(d)  # İç çarpım için
        else:
            # Öklid mesafesi için
            index = faiss.IndexFlatL2(d)
        
        # Vektörleri indekse ekle
        index.add(features)
        
        # Faiss indekslerini saklayacak klasörü oluştur
        faiss_dir = "faiss_indexes"
        if not os.path.exists(faiss_dir):
            os.makedirs(faiss_dir)
        
        # İndeksi kaydet
        if not binary_path:
            binary_path = os.path.join(faiss_dir, f"{model_type}_index.bin")
        
        faiss.write_index(index, binary_path)
        
        # Veritabanını güncelle
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO faiss_indexes 
            (model_type, binary_path, dimension, last_updated)
            VALUES (?, ?, ?, ?)
        """, (model_type, binary_path, d, now))
        
        conn.commit()
        print(f"✅ {model_type} Faiss indeksi oluşturuldu ve kaydedildi.")
        
        return index
    except Exception as e:
        print(f"❌ Faiss indeksi işleminde hata: {e}")
        return None
    finally:
        if conn:
            conn.close()

def reset_faiss_indexes():
    """Tüm Faiss indekslerini sıfırlar"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tüm model türlerini al
        cursor.execute("SELECT model_type FROM faiss_indexes")
        model_types = [row['model_type'] for row in cursor.fetchall()]
        
        for model_type in model_types:
            # Faiss indeksini yeniden oluştur
            get_faiss_index(model_type, force_rebuild=True)
        
        return True
    except sqlite3.Error as e:
        print(f"Faiss indekslerini sıfırlama hatası: {e}")
        return False
    finally:
        conn.close()

# --------------- Benzerlik Arama İşlemleri ---------------

def find_similar_images(filename, model_type, version, topN=100, metric="cosine", filters=None, use_cache=True):
    """Belirli bir görsele benzer görselleri bulur"""
    
    # Önce indeksi al
    index = get_faiss_index(model_type)
    if not index:
        return []
    
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Filename'leri al
        cursor.execute("SELECT id, filename FROM fabrics ORDER BY id")
        filenames_map = {row['id']: row['filename'] for row in cursor.fetchall()}
        filenames = list(filenames_map.values())
        
        # Özellik vektörlerini yükle
        feature_path = f"image_features/{model_type}_features.npy"
        filename_path = f"image_features/{model_type}_filenames.json"
        
        if not os.path.exists(feature_path) or not os.path.exists(filename_path):
            return []
        
        # Filename indekslerini al
        with open(filename_path, 'r', encoding='utf-8') as f:
            file_indices = json.load(f)
        
        if filename not in file_indices:
            return []
        
        # Sorgu vektörünü yükle
        features = np.load(feature_path).astype(np.float32)
        query_idx = file_indices.index(filename)
        query_vector = features[query_idx].reshape(1, -1).copy()
        
        # Kosinüs benzerliği için L2 normalizasyon
        if model_type in ["pattern", "color+pattern"] or metric == "cosine":
            faiss.normalize_L2(query_vector)
        
        # Filtreleme için izin verilen indeksleri belirle
        allowed_indices = get_allowed_indices(filters, file_indices, model_type, version, conn)
        
        if not allowed_indices:
            return []
        
        # Filtrelenmiş indeksler için arama
        filtered_features = features[allowed_indices]
        
        # Geçici indeks oluştur
        if model_type in ["pattern", "color+pattern"] or metric == "cosine":
            faiss.normalize_L2(filtered_features)
            temp_index = faiss.IndexFlatIP(filtered_features.shape[1])
        else:
            temp_index = faiss.IndexFlatL2(filtered_features.shape[1])
        
        temp_index.add(filtered_features)
        
        # Benzerlik araması yap
        k = min(topN, len(allowed_indices))
        distances, indices = temp_index.search(query_vector, k)
        
        # Sonuçları hazırla
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= len(allowed_indices):
                continue
            
            global_idx = allowed_indices[idx]
            search_filename = file_indices[global_idx]
            
            # Fabric bilgilerini al
            cursor.execute("""
                SELECT id, filename, design, season, quality
                FROM fabrics
                WHERE filename = ?
            """, (search_filename,))
            
            fabric = cursor.fetchone()
            if not fabric:
                continue
            
            # Özellikler
            cursor.execute("""
                SELECT feature_name, feature_value
                FROM fabric_features
                WHERE fabric_id = ?
            """, (fabric['id'],))
            
            features_list = []
            for feature_row in cursor.fetchall():
                features_list.append([feature_row['feature_name'], feature_row['feature_value']])
            
            # Benzerlik skoru
            if model_type in ["pattern", "color+pattern"] or metric == "cosine":
                # İç çarpım için [0,2] aralığını [0,1] aralığına dönüştür
                similarity = float(1.0 - distances[0][i] / 2)
            else:
                # L2 mesafesi için
                similarity = float(1.0 / (1.0 + distances[0][i]))
            
            # Cluster bilgisi
            cluster_info = get_cluster_info(fabric['id'], model_type, version, conn)
            
            results.append({
                "filename": search_filename,
                "design": fabric['design'],
                "season": fabric['season'],
                "quality": fabric['quality'],
                "features": features_list,
                "cluster": cluster_info,
                "version": version,
                "similarity": similarity
            })
        
        return results
    except Exception as e:
        print(f"Benzerlik arama hatası: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_allowed_indices(filters, filenames, model_type, version, conn):
    """Filtreler ve versiyon bilgisine göre izin verilen indeksleri döndürür"""
    
    # Filtre yoksa tüm indeksleri döndür
    if not filters:
        return list(range(len(filenames)))
    
    # Her dosya adı için fabric ID'leri al
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in filenames])
    query = f"SELECT id, filename FROM fabrics WHERE filename IN ({placeholders})"
    cursor.execute(query, filenames)
    
    # filename -> fabric_id eşlemesi oluştur
    filename_to_id = {row['filename']: row['id'] for row in cursor.fetchall()}
    
    # Filtreleri uygula
    allowed_filenames = set(filenames)
    
    # Temel filtreleri uygula (design, season, quality)
    if 'design' in filters and filters['design']:
        cursor.execute("""
            SELECT filename FROM fabrics 
            WHERE design = ? AND filename IN ({})
        """.format(placeholders), [filters['design']] + filenames)
        allowed_filenames &= {row['filename'] for row in cursor.fetchall()}
    
    if 'season' in filters and filters['season']:
        cursor.execute("""
            SELECT filename FROM fabrics 
            WHERE season = ? AND filename IN ({})
        """.format(placeholders), [filters['season']] + filenames)
        allowed_filenames &= {row['filename'] for row in cursor.fetchall()}
    
    if 'quality' in filters and filters['quality']:
        cursor.execute("""
            SELECT filename FROM fabrics 
            WHERE quality = ? AND filename IN ({})
        """.format(placeholders), [filters['quality']] + filenames)
        allowed_filenames &= {row['filename'] for row in cursor.fetchall()}
    
    # features filtresi
    if 'features' in filters and filters['features']:
        for feature in filters['features']:
            feature_name, feature_value = feature
            
            cursor.execute("""
                SELECT f.filename FROM fabrics f
                JOIN fabric_features ff ON f.id = ff.fabric_id
                WHERE ff.feature_name = ? AND ff.feature_value = ? AND f.filename IN ({})
            """.format(placeholders), [feature_name, feature_value] + filenames)
            
            allowed_filenames &= {row['filename'] for row in cursor.fetchall()}
    
    # Versiyon filtresi
    if 'cluster' in filters and filters['cluster'] and version:
        # Model versiyonunu bul
        cursor.execute("""
            SELECT id FROM model_versions
            WHERE model_type = ? AND version_name = ?
        """, (model_type, version))
        
        version_row = cursor.fetchone()
        if version_row:
            version_id = version_row['id']
            
            # Cluster numarası alınacak
            cluster_num = filters['cluster']
            if cluster_num.startswith('cluster-'):
                cluster_num = cluster_num[8:]
            
            # Cluster'ı bul
            cursor.execute("""
                SELECT id FROM clusters
                WHERE version_id = ? AND cluster_number = ?
            """, (version_id, cluster_num))
            
            cluster_row = cursor.fetchone()
            if cluster_row:
                cluster_id = cluster_row['id']
                
                # Bu cluster'a ait fabric'leri bul
                cursor.execute("""
                    SELECT f.filename FROM fabrics f
                    JOIN fabric_clusters fc ON f.id = fc.fabric_id
                    WHERE fc.cluster_id = ? AND f.filename IN ({})
                """.format(placeholders), [cluster_id] + filenames)
                
                allowed_filenames &= {row['filename'] for row in cursor.fetchall()}
    
    # İzin verilen indeksleri döndür
    allowed_indices = [i for i, fname in enumerate(filenames) if fname in allowed_filenames]
    return allowed_indices

def get_cluster_info(fabric_id, model_type, version, conn):
    """Belirli bir fabric için cluster bilgisini döndürür"""
    cursor = conn.cursor()
    
    # Versiyon ID'sini bul
    cursor.execute("""
        SELECT id FROM model_versions
        WHERE model_type = ? AND version_name = ?
    """, (model_type, version))
    
    version_row = cursor.fetchone()
    if not version_row:
        return None
    
    version_id = version_row['id']
    
    # Fabric'in bulunduğu cluster'ı bul
    cursor.execute("""
        SELECT c.cluster_number, c.id
        FROM clusters c
        JOIN fabric_clusters fc ON c.id = fc.cluster_id
        WHERE fc.fabric_id = ? AND c.version_id = ?
    """, (fabric_id, version_id))
    
    cluster_row = cursor.fetchone()
    if not cluster_row:
        return None
    
    # Cluster'ın temsilcisini bul
    cursor.execute("""
        SELECT f.filename
        FROM fabrics f
        JOIN clusters c ON f.id = c.representative_id
        WHERE c.id = ?
    """, (cluster_row['id'],))
    
    rep_row = cursor.fetchone()
    if not rep_row:
        return None
    
    return {
        'number': f"cluster-{cluster_row['cluster_number']}",
        'representative': rep_row['filename']
    }

# --------------- Feedback İşlemleri ---------------

def add_feedback(anchor_filename, output_filename, model_type, version, rating):
    """Benzerlik sonucu için feedback ekler"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Fabric ID'lerini bul
        cursor.execute("SELECT id FROM fabrics WHERE filename = ?", (anchor_filename,))
        anchor_row = cursor.fetchone()
        
        cursor.execute("SELECT id FROM fabrics WHERE filename = ?", (output_filename,))
        output_row = cursor.fetchone()
        
        if not anchor_row or not output_row:
            return False
        
        # Feedback ekle
        cursor.execute("""
            INSERT OR REPLACE INTO feedback 
            (anchor_id, output_id, model_type, version, rating, feedback_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            anchor_row['id'],
            output_row['id'],
            model_type,
            version,
            rating,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Feedback ekleme hatası: {e}")
        return False
    finally:
        conn.close()

def get_feedback(model_type=None, version=None):
    """Belirli bir model ve versiyon için feedbackleri döndürür"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT f.id, a.filename as anchor, o.filename as output, f.model_type, f.version, f.rating, f.feedback_date
            FROM feedback f
            JOIN fabrics a ON f.anchor_id = a.id
            JOIN fabrics o ON f.output_id = o.id
            WHERE 1=1
        """
        params = []
        
        if model_type:
            query += " AND f.model_type = ?"
            params.append(model_type)
        
        if version:
            query += " AND f.version = ?"
            params.append(version)
        
        query += " ORDER BY f.feedback_date DESC"
        
        cursor.execute(query, params)
        
        feedbacks = []
        for row in cursor.fetchall():
            feedbacks.append({
                'id': row['id'],
                'anchor': row['anchor'],
                'output': row['output'],
                'model': row['model_type'],
                'version': row['version'],
                'feedback': row['rating'],
                'date': row['feedback_date']
            })
        
        return feedbacks
    except sqlite3.Error as e:
        print(f"Feedback getirme hatası: {e}")
        return []
    finally:
        conn.close()

# --------------- Yardımcı Fonksiyonlar ---------------

def export_to_json(model_type, version):
    """Belirli bir model ve versiyon için cluster verilerini JSON formatında dışa aktarır"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        # Versiyon bilgilerini al
        version_data = get_model_version_by_name(model_type, version)
        if not version_data:
            return None
        
        # Mevcut JSON formatına uygun bir yapı oluştur
        result = {
            'current_version': version,
            'versions': {
                version: {
                    'created_at': version_data['created_at'],
                    'parameters': version_data['parameters'],
                    'clusters': version_data['clusters']
                }
            }
        }
        
        return result
    except Exception as e:
        print(f"JSON dışa aktarma hatası: {e}")
        return None
    finally:
        if conn:
            conn.close()

def create_export_directory(model_type):
    """Dışa aktarma için gerekli dizin yapısını oluşturur"""
    export_dir = f"exported_clusters/{model_type}"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    return export_dir

def save_json_version(model_type, version_data):
    """Versiyon verilerini JSON dosyasına kaydeder"""
    export_dir = create_export_directory(model_type)
    filepath = f"{export_dir}/versions.json"
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"JSON kaydetme hatası: {e}")
        return False

def import_from_json(model_type, json_data):
    """JSON verilerini veritabanına aktarır"""
    if not json_data or 'versions' not in json_data:
        return False
    
    conn = create_connection()
    if not conn:
        return False
    
    try:
        for version_name, version_data in json_data['versions'].items():
            parameters = version_data.get('parameters', {})
            clusters = version_data.get('clusters', {})
            
            # Versiyon oluştur
            create_model_version(model_type, version_name, parameters, clusters)
        
        return True
    except Exception as e:
        print(f"JSON'dan içe aktarma hatası: {e}")
        return False
    finally:
        if conn:
            conn.close()
