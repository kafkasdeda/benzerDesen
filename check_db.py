"""
Veritabanındaki görevleri listeleyen script.
"""
import sqlite3
import os

def check_database():
    """Veritabanını kontrol et"""
    # Veritabanı bağlantısı
    db_path = "project_management.db"
    
    if not os.path.exists(db_path):
        print(f"Hata: {db_path} bulunamadı.")
        return False
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Tabloları listele
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Veritabanındaki tablolar:")
        for table in tables:
            print(f"- {table['name']}")
        
        print("\n")
        
        # Görevleri listele
        cursor.execute("SELECT id, title, status, priority FROM tasks")
        tasks = cursor.fetchall()
        
        print("Görevler:")
        if not tasks:
            print("Hiç görev bulunamadı.")
        else:
            for task in tasks:
                print(f"ID: {task['id']}, Başlık: {task['title']}, Durum: {task['status']}, Öncelik: {task['priority']}")
        
        print("\n")
        
        # Alt görevleri listele (tablo varsa)
        try:
            cursor.execute("SELECT subtask_id, title, status FROM subtasks")
            subtasks = cursor.fetchall()
            
            print("Alt Görevler:")
            if not subtasks:
                print("Hiç alt görev bulunamadı.")
            else:
                for subtask in subtasks:
                    print(f"ID: {subtask['subtask_id']}, Başlık: {subtask['title']}, Durum: {subtask['status']}")
        except sqlite3.OperationalError:
            print("Alt görev tablosu bulunamadı veya henüz oluşturulmadı.")
            
    except Exception as e:
        print(f"Veritabanı kontrol hatası: {str(e)}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
