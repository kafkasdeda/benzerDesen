"""
Görev Yönetim Aracı
Bu araç, Benzer Desen projesi için komut satırı tabanlı görev yönetim sistemi sağlar.
"""
import sqlite3
import argparse
import os
import sys
from datetime import datetime
from tabulate import tabulate

DB_PATH = "project_management.db"

def get_connection():
    """Veritabanı bağlantısı oluştur"""
    if not os.path.exists(DB_PATH):
        print(f"Hata: {DB_PATH} bulunamadı. Önce db_setup.py dosyasını çalıştırın.")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Dict-like erişim için
    return conn

def list_tasks(args):
    """Görevleri listele"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Filtreleme koşulları
    conditions = []
    params = []
    
    if args.status:
        conditions.append("status = ?")
        params.append(args.status)
    
    if args.priority:
        conditions.append("priority = ?")
        params.append(args.priority)
    
    if args.category:
        conditions.append("category = ?")
        params.append(args.category)
    
    # SQL sorgusunu oluştur
    sql = "SELECT id, title, status, priority, category FROM tasks"
    
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    
    if args.sort:
        sql += f" ORDER BY {args.sort}"
    else:
        sql += " ORDER BY priority, status"
    
    # Sorguyu çalıştır
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    # Sonuçları tablo olarak göster
    headers = ["ID", "Başlık", "Durum", "Öncelik", "Kategori"]
    table_data = [[row["id"], row["title"], row["status"], row["priority"], row["category"]] for row in rows]
    
    print("\nGörev Listesi:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\nToplam: {len(rows)} görev")
    
    conn.close()

def show_task(args):
    """Görev detaylarını göster"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Görevi bul
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (args.id,))
    task = cursor.fetchone()
    
    if not task:
        print(f"Hata: {args.id} ID'li görev bulunamadı.")
        conn.close()
        return
    
    # Görevi tablo olarak göster
    print(f"\n{task['id']} - {task['title']} ({task['status']})")
    print("-" * 80)
    
    details = [
        ["Kategori", task["category"]],
        ["Öncelik", task["priority"]],
        ["Durum", task["status"]],
        ["Açıklama", task["description"] or "N/A"],
        ["Tahmini Süre", f"{task['estimated_hours']} saat" if task["estimated_hours"] else "N/A"],
        ["Gerçek Süre", f"{task['actual_hours']} saat" if task["actual_hours"] else "N/A"],
        ["Başlangıç", task["start_date"] or "N/A"],
        ["Tamamlanma", task["completion_date"] or "N/A"],
        ["Bağımlılıklar", task["dependencies"] or "N/A"],
        ["Notlar", task["notes"] or "N/A"],
        ["Oluşturulma", task["created_at"]],
        ["Son Güncelleme", task["updated_at"]]
    ]
    
    print(tabulate(details, tablefmt="plain"))
    print()
    
    conn.close()

def update_task(args):
    """Görev güncelle"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Görevi bul
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (args.id,))
    task = cursor.fetchone()
    
    if not task:
        print(f"Hata: {args.id} ID'li görev bulunamadı.")
        conn.close()
        return
    
    # Güncellenecek alanları topla
    updates = []
    params = []
    
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    
    if args.priority:
        updates.append("priority = ?")
        params.append(args.priority)
    
    if args.title:
        updates.append("title = ?")
        params.append(args.title)
    
    if args.description:
        updates.append("description = ?")
        params.append(args.description)
    
    if args.estimated:
        updates.append("estimated_hours = ?")
        params.append(float(args.estimated))
    
    if args.actual:
        updates.append("actual_hours = ?")
        params.append(float(args.actual))
    
    if args.start_date:
        updates.append("start_date = ?")
        params.append(args.start_date)
    
    if args.completion_date:
        updates.append("completion_date = ?")
        params.append(args.completion_date)
    
    if args.dependencies:
        updates.append("dependencies = ?")
        params.append(args.dependencies)
    
    if args.notes:
        updates.append("notes = ?")
        params.append(args.notes)
    
    # Güncellemeleri uygula
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        params.append(args.id)
        
        cursor.execute(sql, params)
        conn.commit()
        
        print(f"{args.id} görevi güncellendi.")
    else:
        print("Değişiklik yapılmadı.")
    
    conn.close()

def add_task(args):
    """Yeni görev ekle"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kategori kontrolü
    valid_categories = ["FEATURE", "UI", "PERF", "REFAC", "FIX", "TEST", "DOC", "INFRA", "TASK"]
    if args.category not in valid_categories:
        print(f"Hata: Geçersiz kategori. Geçerli kategoriler: {', '.join(valid_categories)}")
        conn.close()
        return
    
    # Öncelik kontrolü
    valid_priorities = ["P0", "P1", "P2", "P3"]
    if args.priority not in valid_priorities:
        print(f"Hata: Geçersiz öncelik. Geçerli öncelikler: {', '.join(valid_priorities)}")
        conn.close()
        return
    
    # Son görev numarasını bul
    cursor.execute(f"SELECT id FROM tasks WHERE category = ? ORDER BY id DESC LIMIT 1", (args.category,))
    last_task = cursor.fetchone()
    
    task_number = 1
    if last_task:
        # ID formatı: CATEGORY-NUMBER-title
        parts = last_task["id"].split("-", 2)
        if len(parts) >= 2:
            try:
                task_number = int(parts[1]) + 1
            except ValueError:
                task_number = 1
    
    # Görev ID'sini oluştur
    task_id = f"{args.category}-{task_number:03d}-{args.title.lower().replace(' ', '-')}"
    
    # ID zaten var mı kontrol et
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone()[0] > 0:
        print(f"Hata: {task_id} ID'si zaten kullanılıyor.")
        conn.close()
        return
    
    # Görevi ekle
    cursor.execute("""
    INSERT INTO tasks (
        id, title, description, category, priority, status,
        estimated_hours, dependencies, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id,
        args.title,
        args.description or "",
        args.category,
        args.priority,
        "Not Started",
        float(args.estimated) if args.estimated else None,
        args.dependencies or "",
        args.notes or ""
    ))
    
    conn.commit()
    print(f"Yeni görev eklendi: {task_id}")
    
    conn.close()

def start_task(args):
    """Görevi başlat"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Görevi bul
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (args.id,))
    task = cursor.fetchone()
    
    if not task:
        print(f"Hata: {args.id} ID'li görev bulunamadı.")
        conn.close()
        return
    
    # Görevi başlat
    cursor.execute("""
    UPDATE tasks SET 
        status = 'In Progress',
        start_date = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (datetime.now().strftime("%Y-%m-%d"), args.id))
    
    conn.commit()
    print(f"{args.id} görevi başlatıldı.")
    
    conn.close()

def complete_task(args):
    """Görevi tamamla"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Görevi bul
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (args.id,))
    task = cursor.fetchone()
    
    if not task:
        print(f"Hata: {args.id} ID'li görev bulunamadı.")
        conn.close()
        return
    
    # Görevi tamamla
    cursor.execute("""
    UPDATE tasks SET 
        status = 'Completed',
        completion_date = ?,
        actual_hours = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        float(args.hours) if args.hours else task["estimated_hours"],
        args.id
    ))
    
    conn.commit()
    print(f"{args.id} görevi tamamlandı.")
    
    conn.close()

def show_project_status(args):
    """Proje durumunu göster"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Proje durumunu al
    cursor.execute("SELECT * FROM project_status ORDER BY id DESC LIMIT 1")
    status = cursor.fetchone()
    
    if not status:
        print("Hata: Proje durumu bulunamadı.")
        conn.close()
        return
    
    # Görev istatistiklerini al
    cursor.execute("""
    SELECT status, COUNT(*) as count FROM tasks GROUP BY status
    """)
    task_stats = cursor.fetchall()
    
    cursor.execute("""
    SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority
    """)
    priority_stats = cursor.fetchall()
    
    # Son oturumu al
    cursor.execute("""
    SELECT * FROM sessions ORDER BY id DESC LIMIT 1
    """)
    last_session = cursor.fetchone()
    
    # Durum bilgilerini göster
    print("\nBenzer Desen Projesi - Durum Raporu")
    print("=" * 50)
    print(f"Toplam İlerleme: %{status['total_progress']}")
    print(f"Son Güncelleme: {status['last_updated']}")
    print(f"Mevcut Odak: {status['current_focus']}")
    print(f"Bir Sonraki Dönüm Noktaları: {status['next_milestones']}")
    
    if status['blockers']:
        print(f"Engelleyiciler: {status['blockers']}")
    
    # Görev istatistiklerini göster
    print("\nGörev Durumu:")
    for stat in task_stats:
        print(f"  {stat['status']}: {stat['count']}")
    
    print("\nÖncelik Dağılımı:")
    for stat in priority_stats:
        print(f"  {stat['priority']}: {stat['count']}")
    
    # Son oturum bilgilerini göster
    if last_session:
        print("\nSon Oturum:")
        print(f"  Oturum #{last_session['session_number']} - {last_session['session_date']}")
        print(f"  Tamamlanan: {last_session['completed_tasks']}")
        print(f"  Bir Sonraki Adımlar: {last_session['next_steps']}")
    
    conn.close()

def update_project_status(args):
    """Proje durumunu güncelle"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Güncellenecek alanları topla
    updates = []
    params = []
    
    if args.progress:
        updates.append("total_progress = ?")
        params.append(int(args.progress))
    
    if args.focus:
        updates.append("current_focus = ?")
        params.append(args.focus)
    
    if args.milestones:
        updates.append("next_milestones = ?")
        params.append(args.milestones)
    
    if args.blockers:
        updates.append("blockers = ?")
        params.append(args.blockers)
    
    # Güncellemeleri uygula
    if updates:
        updates.append("last_updated = CURRENT_TIMESTAMP")
        
        sql = f"UPDATE project_status SET {', '.join(updates)} WHERE id = 1"
        
        cursor.execute(sql, params)
        conn.commit()
        
        print(f"Proje durumu güncellendi.")
    else:
        print("Değişiklik yapılmadı.")
    
    conn.close()

def add_session(args):
    """Yeni oturum ekle"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Son oturum numarasını bul
    cursor.execute("SELECT MAX(session_number) as last_num FROM sessions")
    last_num = cursor.fetchone()["last_num"] or 0
    
    # Yeni oturum numarası
    session_number = args.number if args.number else last_num + 1
    
    # Oturumu ekle
    cursor.execute("""
    INSERT INTO sessions (
        session_number, session_date, completed_tasks, progress_notes, next_steps
    ) VALUES (?, ?, ?, ?, ?)
    """, (
        session_number,
        args.date if args.date else datetime.now().strftime("%Y-%m-%d"),
        args.completed,
        args.notes,
        args.next
    ))
    
    conn.commit()
    print(f"Oturum #{session_number} eklendi.")
    
    conn.close()

def show_sessions(args):
    """Oturumları listele"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Oturumları al
    cursor.execute("""
    SELECT * FROM sessions ORDER BY session_number
    """)
    sessions = cursor.fetchall()
    
    if not sessions:
        print("Henüz hiç oturum kaydedilmemiş.")
        conn.close()
        return
    
    # Listeyi göster
    headers = ["#", "Tarih", "Tamamlanan", "Bir Sonraki Adımlar"]
    table_data = []
    
    for session in sessions:
        completed = session["completed_tasks"]
        if completed and len(completed) > 40:
            completed = completed[:37] + "..."
            
        next_steps = session["next_steps"]
        if next_steps and len(next_steps) > 40:
            next_steps = next_steps[:37] + "..."
        
        table_data.append([
            session["session_number"],
            session["session_date"],
            completed,
            next_steps
        ])
    
    print("\nOturum Listesi:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    conn.close()

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="Benzer Desen projesi görev yönetimi")
    subparsers = parser.add_subparsers(dest="command", help="Alt komutlar")
    
    # Görev listeleme komutu
    list_parser = subparsers.add_parser("list", help="Görevleri listele")
    list_parser.add_argument("--status", help="Duruma göre filtrele")
    list_parser.add_argument("--priority", help="Önceliğe göre filtrele")
    list_parser.add_argument("--category", help="Kategoriye göre filtrele")
    list_parser.add_argument("--sort", help="Sıralama alanı")
    
    # Görev detay komutu
    show_parser = subparsers.add_parser("show", help="Görev detaylarını göster")
    show_parser.add_argument("id", help="Görev ID")
    
    # Görev güncelleme komutu
    update_parser = subparsers.add_parser("update", help="Görev güncelle")
    update_parser.add_argument("id", help="Görev ID")
    update_parser.add_argument("--status", help="Yeni durum")
    update_parser.add_argument("--priority", help="Yeni öncelik")
    update_parser.add_argument("--title", help="Yeni başlık")
    update_parser.add_argument("--description", help="Yeni açıklama")
    update_parser.add_argument("--estimated", help="Tahmini süre (saat)")
    update_parser.add_argument("--actual", help="Gerçek süre (saat)")
    update_parser.add_argument("--start_date", help="Başlangıç tarihi")
    update_parser.add_argument("--completion_date", help="Tamamlanma tarihi")
    update_parser.add_argument("--dependencies", help="Bağımlılıklar")
    update_parser.add_argument("--notes", help="Notlar")
    
    # Yeni görev ekleme komutu
    add_parser = subparsers.add_parser("add", help="Yeni görev ekle")
    add_parser.add_argument("title", help="Görev başlığı")
    add_parser.add_argument("category", help="Görev kategorisi")
    add_parser.add_argument("priority", help="Görev önceliği")
    add_parser.add_argument("--description", help="Görev açıklaması")
    add_parser.add_argument("--estimated", help="Tahmini süre (saat)")
    add_parser.add_argument("--dependencies", help="Bağımlılıklar")
    add_parser.add_argument("--notes", help="Notlar")
    
    # Görev başlatma komutu
    start_parser = subparsers.add_parser("start", help="Görevi başlat")
    start_parser.add_argument("id", help="Görev ID")
    
    # Görev tamamlama komutu
    complete_parser = subparsers.add_parser("complete", help="Görevi tamamla")
    complete_parser.add_argument("id", help="Görev ID")
    complete_parser.add_argument("--hours", help="Gerçek süre (saat)")
    
    # Proje durumu komutu
    subparsers.add_parser("status", help="Proje durumunu göster")
    
    # Proje durumu güncelleme komutu
    status_update_parser = subparsers.add_parser("update-status", help="Proje durumunu güncelle")
    status_update_parser.add_argument("--progress", help="Toplam ilerleme yüzdesi")
    status_update_parser.add_argument("--focus", help="Mevcut odak")
    status_update_parser.add_argument("--milestones", help="Bir sonraki dönüm noktaları")
    status_update_parser.add_argument("--blockers", help="Engelleyiciler")
    
    # Oturum ekleme komutu
    session_parser = subparsers.add_parser("add-session", help="Yeni oturum ekle")
    session_parser.add_argument("--number", type=int, help="Oturum numarası")
    session_parser.add_argument("--date", help="Oturum tarihi (YYYY-MM-DD)")
    session_parser.add_argument("--completed", help="Tamamlanan görevler")
    session_parser.add_argument("--notes", help="İlerleme notları")
    session_parser.add_argument("--next", help="Bir sonraki adımlar")
    
    # Oturumları listeleme komutu
    subparsers.add_parser("sessions", help="Oturumları listele")
    
    # Argümanları işle
    args = parser.parse_args()
    
    # Komut seçimine göre fonksiyonu çağır
    if args.command == "list":
        list_tasks(args)
    elif args.command == "show":
        show_task(args)
    elif args.command == "update":
        update_task(args)
    elif args.command == "add":
        add_task(args)
    elif args.command == "start":
        start_task(args)
    elif args.command == "complete":
        complete_task(args)
    elif args.command == "status":
        show_project_status(args)
    elif args.command == "update-status":
        update_project_status(args)
    elif args.command == "add-session":
        add_session(args)
    elif args.command == "sessions":
        show_sessions(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
