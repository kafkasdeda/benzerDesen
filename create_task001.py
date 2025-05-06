"""
TASK-001 görevini ve alt görevlerini veritabanına ekleyen script.
"""
import sqlite3
import os
import re
from datetime import datetime

def create_task001_and_subtasks():
    """TASK-001 görevini ve alt görevlerini oluştur"""
    # Veritabanı bağlantısı
    db_path = "project_management.db"
    
    if not os.path.exists(db_path):
        print(f"Hata: {db_path} bulunamadı.")
        return False
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Ana görevi oluştur
        task_id = "TASK-001"
        title = "complete-sqlite-integration"
        
        # Görev zaten var mı kontrol et
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            print(f"Görev {task_id} zaten mevcut.")
        else:
            # Ana görevi ekle
            cursor.execute("""
            INSERT INTO tasks (
                id, title, description, category, priority, status,
                estimated_hours, dependencies, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                title,
                "SQLite veritabanı entegrasyonunu tamamlama",
                "TASK",
                "P1",
                "In Progress",
                6.0,
                "INFRA-001",
                "Session 11 ve 12'de başlandı, tamamlanması gerekiyor"
            ))
            
            print(f"✅ {task_id} görevi oluşturuldu.")
        
        # Subtasks tablosunu oluştur (eğer yoksa)
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
        
        # Acceptance criteria tablosunu oluştur (eğer yoksa)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS acceptance_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtask_id TEXT NOT NULL,
            criteria TEXT NOT NULL
        )
        """)
        
        # Dependencies tablosunu oluştur (eğer yoksa)
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
        
        # Alt görev dosyasını oku
        subtasks_file = "TASK-001-subtasks.md"
        
        if not os.path.exists(subtasks_file):
            print(f"Hata: {subtasks_file} bulunamadı.")
            return False
            
        with open(subtasks_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Alt görev bloklarını regex ile bul
        subtask_pattern = r"### ([A-Z]+-\d+\.\d+-[\w-]+)(.*?)(?=### |\Z)"
        subtask_blocks = re.findall(subtask_pattern, content, re.DOTALL)
        
        # Ana görevi alt görevlere sahip olarak işaretle
        cursor.execute("UPDATE tasks SET has_subtasks = 1 WHERE id = ?", (task_id,))
        
        subtask_count = 0
        
        for subtask_id, subtask_content in subtask_blocks:
            # Başlık çıkar (- **Açıklama**: ile başlıyor, ancak düzenli ifadede sorun olabilir)
            description = ""
            description_pattern = r"\*\*Açıklama\*\*: (.+?)[\r\n]"
            description_match = re.search(description_pattern, subtask_content)
            if description_match:
                description = description_match.group(1).strip()
            
            # Alt görevi tanımla
            subtask_data = {
                "parent_task_id": task_id,
                "subtask_id": subtask_id,
                "title": f"{subtask_id.split('-')[2]}",  # ID'den başlık çıkar
                "description": description if description else f"{subtask_id.split('-')[2]}",
                "status": "Not Started",
                "priority": "P1"
            }
            
            # Tahmini süre
            estimated_pattern = r"\*\*Tahmini\*\*: (\d+\.?\d*)s"
            estimated_match = re.search(estimated_pattern, subtask_content)
            if estimated_match:
                subtask_data["estimated_hours"] = float(estimated_match.group(1))
            
            # Alt görevi ekle veya güncelle
            cursor.execute("SELECT COUNT(*) as count FROM subtasks WHERE subtask_id = ?", (subtask_id,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                print(f"Alt görev {subtask_id} zaten mevcut.")
            else:
                # Alt görevi ekle
                cursor.execute("""
                INSERT INTO subtasks (
                    parent_task_id, subtask_id, title, description, status, 
                    priority, estimated_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    subtask_data["parent_task_id"],
                    subtask_data["subtask_id"],
                    subtask_data["title"],
                    subtask_data["description"],
                    subtask_data["status"],
                    subtask_data["priority"],
                    subtask_data.get("estimated_hours")
                ))
                
                # Kabul kriterlerini çıkar ve ekle
                criteria_pattern = r"\*\*Kabul Kriterleri\*\*:(.*?)(?:\*\*Bağımlılıklar|\Z)"
                criteria_match = re.search(criteria_pattern, subtask_content, re.DOTALL)
                
                if criteria_match:
                    criteria_text = criteria_match.group(1).strip()
                    criteria_items = re.findall(r"  - (.+?)$", criteria_text, re.MULTILINE)
                    
                    if not criteria_items:
                        # Alternatif format dene
                        criteria_items = re.findall(r"- (.+?)$", criteria_text, re.MULTILINE)
                    
                    for criteria in criteria_items:
                        cursor.execute("""
                        INSERT INTO acceptance_criteria (subtask_id, criteria)
                        VALUES (?, ?)
                        """, (subtask_id, criteria))
                
                # Bağımlılıkları çıkar ve ekle
                dependencies_pattern = r"\*\*Bağımlılıklar\*\*: (.+?)(?:[\r\n]|$)"
                dependencies_match = re.search(dependencies_pattern, subtask_content)
                
                if dependencies_match:
                    dependencies_text = dependencies_match.group(1).strip()
                    
                    if dependencies_text and dependencies_text != "Yok":
                        dependencies = [dep.strip() for dep in dependencies_text.split(",")]
                        
                        for dependency in dependencies:
                            cursor.execute("""
                            INSERT INTO dependencies (dependent_task, dependency)
                            VALUES (?, ?)
                            """, (subtask_id, dependency))
                
                subtask_count += 1
                print(f"✅ Alt görev {subtask_id} eklendi.")
        
        # Değişiklikleri kaydet
        conn.commit()
        
        print(f"✅ Toplam {subtask_count} alt görev eklendi.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_task001_and_subtasks()
