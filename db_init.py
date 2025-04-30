import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Veritabanı bağlantısı oluşturma fonksiyonu
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

def setup_database():
    """Veritabanı tablolarını oluşturur"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Fabric tablosu - kumaş ve metadata bilgileri
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fabrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                design TEXT,
                season TEXT,
                quality TEXT,
                creation_date TEXT,
                last_modified TEXT
            )
            ''')
            
            # Fabric özellikleri için tablo (her özellik ayrı bir satır)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fabric_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fabric_id INTEGER,
                feature_name TEXT,
                feature_value TEXT,
                FOREIGN KEY (fabric_id) REFERENCES fabrics (id)
            )
            ''')
            
            # Model versiyonları tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_type TEXT NOT NULL,
                version_name TEXT NOT NULL,
                creation_date TEXT,
                parameters TEXT,
                UNIQUE(model_type, version_name)
            )
            ''')
            
            # Cluster tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id INTEGER,
                cluster_number INTEGER,
                representative_id INTEGER,
                FOREIGN KEY (version_id) REFERENCES model_versions (id),
                FOREIGN KEY (representative_id) REFERENCES fabrics (id)
            )
            ''')
            
            # Fabric-cluster ilişkileri
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fabric_clusters (
                fabric_id INTEGER,
                cluster_id INTEGER,
                PRIMARY KEY (fabric_id, cluster_id),
                FOREIGN KEY (fabric_id) REFERENCES fabrics (id),
                FOREIGN KEY (cluster_id) REFERENCES clusters (id)
            )
            ''')
            
            # Faiss indekslerinin metadata bilgisi
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS faiss_indexes (
                model_type TEXT PRIMARY KEY,
                binary_path TEXT NOT NULL,
                dimension INTEGER,
                last_updated TEXT
            )
            ''')
            
            # Feedback tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anchor_id INTEGER,
                output_id INTEGER,
                model_type TEXT,
                version TEXT,
                rating INTEGER,
                feedback_date TEXT,
                FOREIGN KEY (anchor_id) REFERENCES fabrics (id),
                FOREIGN KEY (output_id) REFERENCES fabrics (id)
            )
            ''')
            
            conn.commit()
            print("✅ Veritabanı tabloları başarıyla oluşturuldu.")
            
        except sqlite3.Error as e:
            print(f"Tablo oluşturma hatası: {e}")
        finally:
            conn.close()
    else:
        print("❌ Veritabanı bağlantısı kurulamadı.")

if __name__ == "__main__":
    setup_database()
    print("SQLite veritabanı kurulumu tamamlandı.")
