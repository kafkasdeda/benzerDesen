"""
Proje yönetim veritabanı kurulum betiği.
Bu betik, Benzer Desen projesi için SQLite tabanlı proje yönetim veritabanı oluşturur.
"""
import sqlite3
import os
import json
from datetime import datetime

def create_db():
    """Proje yönetim veritabanını oluştur"""
    # Veritabanı dosya yolu
    db_path = "project_management.db"
    
    # Veritabanı mevcut mu kontrol et
    db_exists = os.path.exists(db_path)
    
    # Veritabanı bağlantısı oluştur
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabloları oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        estimated_hours FLOAT,
        actual_hours FLOAT,
        start_date TEXT,
        completion_date TEXT,
        dependencies TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Proje durumu tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_progress INTEGER NOT NULL,
        current_focus TEXT,
        next_milestones TEXT,
        blockers TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Oturumlar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_number INTEGER NOT NULL,
        session_date TEXT NOT NULL,
        completed_tasks TEXT,
        progress_notes TEXT,
        next_steps TEXT
    )
    ''')
    
    # Proje durumu tablosunda veri var mı kontrol et
    cursor.execute("SELECT COUNT(*) FROM project_status")
    status_count = cursor.fetchone()[0]
    
    # Eğer proje durumu yoksa ekle
    if status_count == 0:
        cursor.execute('''
        INSERT INTO project_status (total_progress, current_focus, next_milestones, blockers)
        VALUES (?, ?, ?, ?)
        ''', (70, 'Proje yönetimi geçişi ve SQLite entegrasyonu', 'MVP sürümü (Mayıs sonu)', ''))
    
    # Değişiklikleri kaydet
    conn.commit()
    
    print(f"Veritabanı {'oluşturuldu' if not db_exists else 'güncellendi'}: {db_path}")
    
    return conn, cursor

def import_tasks(conn, cursor, tasks_file):
    """tasks.md dosyasından görevleri içe aktar"""
    import re
    
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Görev blokları regex ile bul
        task_pattern = r"#### ([A-Z]+-\d+-[\w-]+)\n(.*?)(?=#### |$)"
        task_blocks = re.findall(task_pattern, content, re.DOTALL)
        
        task_count = 0
        
        for task_id, task_content in task_blocks:
            # Durum bilgisini çıkar
            status_match = re.search(r"\*\*Durum\*\*: (.+?)[\n\r]", task_content)
            status = "Not Started"
            if status_match:
                status_text = status_match.group(1)
                if "Tamamlandı" in status_text:
                    status = "Completed"
                elif "Devam Ediyor" in status_text:
                    status = "In Progress"
                elif "Beklemede" in status_text:
                    status = "Waiting"
            
            # Kategori ve başlığı ayır
            category, number, title = task_id.split("-", 2)
            
            # Açıklama çıkar
            description_match = re.search(r"\*\*Açıklama\*\*: (.+?)[\n\r]", task_content)
            description = description_match.group(1) if description_match else ""
            
            # Öncelik çıkar
            priority_match = re.search(r"\*\*Öncelik\*\*: (.+?)[\n\r]", task_content)
            priority = priority_match.group(1) if priority_match else "P2"
            
            # Tahmini süre
            estimated_match = re.search(r"\*\*Tahmini\*\*: (\d+)s", task_content)
            estimated_hours = float(estimated_match.group(1)) if estimated_match else None
            
            # Gerçek süre
            actual_match = re.search(r"\*\*Gerçek\*\*: (\d+)s", task_content)
            actual_hours = float(actual_match.group(1)) if actual_match else None
            
            # Başlangıç tarihi
            start_match = re.search(r"\*\*Başlangıç\*\*: (.+?)[\n\r]", task_content)
            start_date = start_match.group(1) if start_match else None
            
            # Tamamlanma tarihi
            completion_match = re.search(r"\*\*Tamamlanma\*\*: (.+?)[\n\r]", task_content)
            completion_date = completion_match.group(1) if completion_match else None
            
            # Bağımlılıklar
            dependencies_match = re.search(r"\*\*Bağımlılıklar\*\*: (.+?)[\n\r]", task_content)
            dependencies = dependencies_match.group(1) if dependencies_match else ""
            
            # Notlar
            notes_match = re.search(r"\*\*Notlar\*\*: (.+?)(?:[\n\r]|$)", task_content)
            notes = notes_match.group(1) if notes_match else ""
            
            # Veritabanına ekle veya güncelle
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE id = ?", (task_id,))
            task_exists = cursor.fetchone()[0] > 0
            
            if task_exists:
                # Görevi güncelle
                cursor.execute('''
                UPDATE tasks SET
                    title = ?, description = ?, category = ?, priority = ?,
                    status = ?, estimated_hours = ?, actual_hours = ?,
                    start_date = ?, completion_date = ?, dependencies = ?,
                    notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (
                    title, description, category, priority, status,
                    estimated_hours, actual_hours, start_date, completion_date,
                    dependencies, notes, task_id
                ))
            else:
                # Yeni görev ekle
                cursor.execute('''
                INSERT INTO tasks (
                    id, title, description, category, priority, status,
                    estimated_hours, actual_hours, start_date, completion_date,
                    dependencies, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_id, title, description, category, priority, status,
                    estimated_hours, actual_hours, start_date, completion_date,
                    dependencies, notes
                ))
            
            task_count += 1
        
        # Değişiklikleri kaydet
        conn.commit()
        
        print(f"{task_count} görev içe aktarıldı.")
        
    except Exception as e:
        print(f"Görev içe aktarma hatası: {str(e)}")

def import_project_status(conn, cursor, status_file):
    """PROJECT_STATUS.md dosyasından proje durumunu içe aktar"""
    try:
        with open(status_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Toplam ilerleme yüzdesini çıkar
        progress_match = re.search(r"\*\*Toplam İlerleme\*\*: (\d+)%", content)
        total_progress = int(progress_match.group(1)) if progress_match else 0
        
        # Mevcut odak
        focus_match = re.search(r"## 💡 Yapılacaklar Listesi(.*?)###", content, re.DOTALL)
        current_focus = "Proje yönetimi ve SQLite entegrasyonu"
        if focus_match:
            focus_text = focus_match.group(1).strip()
            current_focus = focus_text[:200] + "..." if len(focus_text) > 200 else focus_text
        
        # Bir sonraki adımlar
        next_steps_match = re.search(r"## 📋 Bir Sonraki Oturumda Yapılacaklar(.*?)##", content, re.DOTALL)
        next_milestones = ""
        if next_steps_match:
            next_text = next_steps_match.group(1).strip()
            next_milestones = next_text[:200] + "..." if len(next_text) > 200 else next_text
        
        # Proje durumunu güncelle
        cursor.execute('''
        UPDATE project_status SET
            total_progress = ?,
            current_focus = ?,
            next_milestones = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = 1
        ''', (total_progress, current_focus, next_milestones))
        
        # Değişiklikleri kaydet
        conn.commit()
        
        print("Proje durumu güncellendi.")
        
    except Exception as e:
        print(f"Proje durumu içe aktarma hatası: {str(e)}")

def add_session(conn, cursor, session_number, progress_notes="", completed_tasks="", next_steps=""):
    """Yeni bir oturum ekle"""
    cursor.execute('''
    INSERT INTO sessions (session_number, session_date, completed_tasks, progress_notes, next_steps)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        session_number,
        datetime.now().strftime("%Y-%m-%d"),
        completed_tasks,
        progress_notes,
        next_steps
    ))
    
    # Değişiklikleri kaydet
    conn.commit()
    
    print(f"Oturum {session_number} kaydedildi.")

def get_task_summary(cursor):
    """Görev özetini göster"""
    # Durum dağılımı
    cursor.execute('''
    SELECT status, COUNT(*) FROM tasks GROUP BY status
    ''')
    status_counts = cursor.fetchall()
    
    print("\nGörev Durumu:")
    for status, count in status_counts:
        print(f"  {status}: {count}")
    
    # Öncelik dağılımı
    cursor.execute('''
    SELECT priority, COUNT(*) FROM tasks GROUP BY priority
    ''')
    priority_counts = cursor.fetchall()
    
    print("\nÖncelik Dağılımı:")
    for priority, count in priority_counts:
        print(f"  {priority}: {count}")
    
    # Son 5 güncellenen görev
    cursor.execute('''
    SELECT id, title, status, updated_at FROM tasks
    ORDER BY updated_at DESC LIMIT 5
    ''')
    recent_tasks = cursor.fetchall()
    
    print("\nSon Güncellenen Görevler:")
    for task_id, title, status, updated_at in recent_tasks:
        print(f"  {task_id} - {status} - {title} ({updated_at})")

def main():
    """Ana fonksiyon"""
    # Veritabanı oluştur
    conn, cursor = create_db()
    
    # Görevleri içe aktar
    tasks_file = "tasks.md"
    if os.path.exists(tasks_file):
        import_tasks(conn, cursor, tasks_file)
    
    # Proje durumunu içe aktar
    status_file = "PROJECT_STATUS.md"
    if os.path.exists(status_file):
        import_project_status(conn, cursor, status_file)
    
    # Bu oturumu kaydet
    add_session(
        conn, cursor, 
        session_number=17,
        progress_notes="Proje yönetim veritabanı oluşturuldu ve veri aktarımı yapıldı",
        completed_tasks="Proje yönetim sistemi için SQLite veritabanı kurulumu",
        next_steps="Görev yönetimi ve durum raporlama için CLI araçları geliştirme"
    )
    
    # Görev özetini göster
    get_task_summary(cursor)
    
    # Bağlantıyı kapat
    conn.close()
    
    print("\nİşlem tamamlandı.")

if __name__ == "__main__":
    main()
