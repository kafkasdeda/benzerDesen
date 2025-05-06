"""
TASK-001 için alt görevleri veritabanına ekleyen script.
"""
import sqlite3
import re
import os
from datetime import datetime

def add_subtasks_to_db():
    """TASK-001 için alt görevleri veritabanına ekle"""
    # Veritabanı bağlantısı
    db_path = "project_management.db"
    
    if not os.path.exists(db_path):
        print(f"Hata: {db_path} bulunamadı.")
        return False
    
    # Alt görev dosyası
    subtasks_file = "TASK-001-subtasks.md"
    
    if not os.path.exists(subtasks_file):
        print(f"Hata: {subtasks_file} bulunamadı.")
        return False
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Ana görevi kontrol et
        parent_id = "TASK-001"
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (parent_id,))
        parent_task = cursor.fetchone()
        
        if not parent_task:
            print(f"Hata: {parent_id} ID'li görev bulunamadı.")
            conn.close()
            return False
        
        # Gerekli tabloları oluştur
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_task_id TEXT NOT NULL,
            subtask_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            estimated_hours FLOAT,
            actual_hours FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS acceptance_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtask_id TEXT NOT NULL,
            criteria TEXT NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dependent_task TEXT NOT NULL,
            dependency TEXT NOT NULL
        )
        """)
        
        # Has_subtasks alanını ekle (eğer yoksa)
        try:
            cursor.execute("SELECT has_subtasks FROM tasks LIMIT 1")
        except sqlite3.OperationalError:
            # Sütun mevcut değil, ekle
            cursor.execute("ALTER TABLE tasks ADD COLUMN has_subtasks BOOLEAN DEFAULT 0")
            
        # Dosyayı oku ve alt görevleri ekle
        with open(subtasks_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Alt görev bloklarını regex ile bul
        subtask_pattern = r"### ([A-Z]+-\d+\.\d+-[\w-]+)(.*?)(?=### |\Z)"
        subtask_blocks = re.findall(subtask_pattern, content, re.DOTALL)
        
        # Ana görevi alt görevlere sahip olarak işaretle
        cursor.execute("UPDATE tasks SET has_subtasks = 1 WHERE id = ?", (parent_id,))
        
        subtask_count = 0
        
        for subtask_id, subtask_content in subtask_blocks:
            # Başlık çıkar
            title_match = re.search(r"- \*\*Açıklama\*\*: (.+?)[\n\r]", subtask_content)
            if not title_match:
                title_match = re.search(r"\*\*Açıklama\*\*: (.+?)[\n\r]", subtask_content)
            title = title_match.group(1) if title_match else subtask_id
            
            # Durum bilgisini çıkar
            status_match = re.search(r"- \*\*Durum\*\*: (.+?)[\n\r]", subtask_content)
            if not status_match:
                status_match = re.search(r"\*\*Durum\*\*: (.+?)[\n\r]", subtask_content)
            status = "Not Started"
            if status_match:
                status_text = status_match.group(1)
                if "Tamamlandı" in status_text:
                    status = "Completed"
                elif "Devam Ediyor" in status_text:
                    status = "In Progress"
                elif "Beklemede" in status_text:
                    status = "Waiting"
            
            # Öncelik çıkar
            priority_match = re.search(r"- \*\*Öncelik\*\*: (.+?)[\n\r]", subtask_content)
            if not priority_match:
                priority_match = re.search(r"\*\*Öncelik\*\*: (.+?)[\n\r]", subtask_content)
            priority = priority_match.group(1) if priority_match else "P1"
            
            # Tahmini süre
            estimated_match = re.search(r"- \*\*Tahmini\*\*: (\d+\.?\d*)s", subtask_content)
            if not estimated_match:
                estimated_match = re.search(r"\*\*Tahmini\*\*: (\d+\.?\d*)s", subtask_content)
            estimated_hours = float(estimated_match.group(1)) if estimated_match else None
            
            # Alt görevi ekle veya güncelle
            cursor.execute("SELECT COUNT(*) FROM subtasks WHERE subtask_id = ?", (subtask_id,))
            subtask_exists = cursor.fetchone()[0] > 0
            
            if subtask_exists:
                # Alt görevi güncelle
                cursor.execute("""
                UPDATE subtasks SET
                    title = ?, description = ?, status = ?, priority = ?,
                    estimated_hours = ?, updated_at = CURRENT_TIMESTAMP
                WHERE subtask_id = ?
                """, (title, title, status, priority, estimated_hours, subtask_id))
            else:
                # Yeni alt görev ekle
                cursor.execute("""
                INSERT INTO subtasks (
                    parent_task_id, subtask_id, title, description,
                    status, priority, estimated_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (parent_id, subtask_id, title, title, status, priority, estimated_hours))
            
            # Kabul kriterlerini çıkar ve ekle
            criteria_match = re.search(r"- \*\*Kabul Kriterleri\*\*:(.*?)(?:- \*\*Bağımlılıklar|\Z)", subtask_content, re.DOTALL)
            if not criteria_match:
                criteria_match = re.search(r"\*\*Kabul Kriterleri\*\*:(.*?)(?:\*\*Bağımlılıklar|\Z)", subtask_content, re.DOTALL)
                
            if criteria_match:
                # Önceki kriterleri temizle
                cursor.execute("DELETE FROM acceptance_criteria WHERE subtask_id = ?", (subtask_id,))
                
                criteria_text = criteria_match.group(1).strip()
                criteria_items = re.findall(r"  - (.+?)$", criteria_text, re.MULTILINE)
                if not criteria_items:
                    criteria_items = re.findall(r"- (.+?)$", criteria_text, re.MULTILINE)
                
                for criteria in criteria_items:
                    cursor.execute("""
                    INSERT INTO acceptance_criteria (subtask_id, criteria)
                    VALUES (?, ?)
                    """, (subtask_id, criteria))
            
            # Bağımlılıkları çıkar ve ekle
            dependencies_match = re.search(r"- \*\*Bağımlılıklar\*\*: (.+?)(?:[\n\r]|$)", subtask_content)
            if not dependencies_match:
                dependencies_match = re.search(r"\*\*Bağımlılıklar\*\*: (.+?)(?:[\n\r]|$)", subtask_content)
                
            if dependencies_match:
                # Önceki bağımlılıkları temizle
                cursor.execute("DELETE FROM dependencies WHERE dependent_task = ?", (subtask_id,))
                
                dependencies_text = dependencies_match.group(1).strip()
                if dependencies_text and dependencies_text != "Yok":
                    dependencies = [dep.strip() for dep in dependencies_text.split(",")]
                    
                    for dependency in dependencies:
                        cursor.execute("""
                        INSERT INTO dependencies (dependent_task, dependency)
                        VALUES (?, ?)
                        """, (subtask_id, dependency))
            
            subtask_count += 1
        
        # Değişiklikleri kaydet
        conn.commit()
        
        print(f"✅ {subtask_count} alt görev {parent_id} görevine eklendi.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Alt görev ekleme hatası: {str(e)}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    add_subtasks_to_db()
