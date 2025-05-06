# Benzer Desen Proje Talimatları

## 🎯 Proje Felsefesi
"Tekstil sektöründe görsel benzerlik analizi - Desen, renk ve doku özelliklerine göre benzer görselleri gruplandıran ve yöneten sistem"

## 🚨 ÖNEMLİ: Claude Masaüstü Kontrolü
**Herhangi bir dosya değişikliği yapmadan önce, her zaman şu soruyu sormalıyım:**
"Claude masaüstü uygulamasında mısınız? (Browser'da değil)"

Tarayıcıdaysanız, dosyaları doğrudan değiştiremem.
Masaüstü uygulamasındaysanız, dosya işlemlerini sizin için halledebilirim.

## 🤖 Yapabileceklerim vs Sizin Yapmanız Gerekenler

### Claude Masaüstü Uygulamasındayken:
- ✅ Tüm proje dosyalarını okuyabilirim
- ✅ Yeni dosya ve klasörler oluşturabilirim
- ✅ Mevcut dosyaları düzenleyebilirim
- ✅ Dosyaları silebilirim
- ✅ Dosyaları taşıyabilir/yeniden adlandırabilirim
- ✅ Dizin içeriklerini listeleyebilirim
- ✅ Tüm markdown dosyalarını güncelleyebilirim

### Sizin Yapmanız Gerekenler (Masaüstü Uygulamasında Olsanız Bile):
**BUNU SİZİN YAPMANIZ GEREKİYOR:**
1. **Git İşlemleri**
   - `git add .`
   - `git commit -m "message"`
   - `git push`
   - Branch işlemleri
   - Merge işlemleri

2. **Terminal Komutları**
   - `python app.py`
   - `pip install -r requirements.txt`
   - Uygulamayı çalıştırma
   - Testleri çalıştırma

3. **Manuel Testler**
   - Tarayıcıda test etme
   - İşlevselliği doğrulama
   - Farklı tarayıcılarda test etme

## 🧪 SIKI TEST POLİTİKASI

### TEST KURALLARI 🔒
1. **KODSUZ TEST OLMAZ** - Test yoksa kod yoktur!
2. **TEST KAPSAMASI MİNİMUM %80** - Altı kabul edilmez!
3. **TESTLER GEÇMEDEN PR KABUL EDİLMEZ** - Kırmızı = Durdur!
4. **DEBUG LOGLAR ZORUNLU** - Her kritik noktada log olmalı!

### Test İş Akışı

#### Claude'un Sorumlulukları:
1. Tüm test dosyalarını hazırlar
2. Test senaryolarını yazar
3. Mock data ve test utility'lerini oluşturur
4. Debug log stratejisini belirler
5. Test konfigürasyonunu hazırlar

#### Kullanıcının Yapacakları:
```bash
# 1. Test bağımlılıklarını yükle
pip install pytest pytest-cov

# 2. Testleri çalıştır
python -m pytest

# 3. Test coverage raporu
python -m pytest --cov

# 4. Belirli testleri çalıştır
python -m pytest tests/test_extract_features.py
```

### Debug Log Standartları 📝

#### Zorunlu Debug Logları:
```python
# Fonksiyon girişi
logging.debug(f"[{function_name}] START - Params: {params}")

# Kritik noktalar
logging.debug(f"[{function_name}] {checkpoint} - State: {state}")

# Hata durumları
logging.error(f"[{function_name}] ERROR - {error}, Context: {context}")

# Performans
import time
start_time = time.time()
# ... kod ...
logging.debug(f"[{function_name}] Execution time: {time.time() - start_time:.2f}s")

# Fonksiyon çıkışı
logging.debug(f"[{function_name}] END - Result: {result}")
```

#### Log Seviyeleri:
- `logging.debug()` - Sadece geliştirme ortamında
- `logging.info()` - Önemli bilgiler
- `logging.warning()` - Potansiyel sorunlar
- `logging.error()` - Sadece hatalar

### Test Kategorileri

1. **Unit Testler**
   - Her utility fonksiyonu
   - Her servis metodu
   - Her yardımcı fonksiyon
   - Her model ve algoritma

2. **Integration Testler**
   - Modül etkileşimleri
   - Veri akışı doğrulaması
   - API entegrasyonu

3. **E2E Testler**
   - Kritik kullanıcı akışları
   - Form gönderimi
   - Hata senaryoları

### Test Coverage Gereksinimleri

| Kategori | Minimum Kapsama |
|----------|-----------------|
| Utilities | 95% |
| Services | 90% |
| Feature Extraction | 85% |
| API | 80% |
| Overall | 85% |

### Test Dosyası Adlandırma
- Unit testler: `test_[filename].py`
- Integration testler: `test_integration_[feature].py`
- E2E testler: `test_e2e_[flow].py`

## 📋 Görev Yönetim Sistemi

### Temel Prensipler

1. **Atomik Görevler**
   - Her görev tek bir sorumluluk taşımalı
   - Görev büyüklüğü maksimum 4 saat olmalı
   - Birbirinden bağımsız tamamlanabilir olmalı

2. **Görev Tanımlama**
   - Format: `[Category]-[Number]-[short-description]`
   - Kategoriler: FEATURE, UI, PERF, REFAC, FIX, TEST, DOC, INFRA, TASK
   - Örnek: `FEATURE-001-feedback-training-integration`

3. **Görev Bağımlılıkları**
   - Açıkça belirtilmeli
   - Bağımlı görev başlamadan önce bağımlılık çözülmeli
   - Döngüsel bağımlılıklar yasak

4. **Görev Durumları**
   - `Not Started` → `In Progress` → `Testing` → `Completed`
   - Beklemede: `Waiting`
   - Engelleyici varsa: `Blocked` (sebep açıklanmalı)
   - İptal edilirse: `Cancelled` (sebep açıklanmalı)

5. **Öncelik Seviyeleri**
   - `P0`: Kritik, hemen yapılması gereken
   - `P1`: Yüksek öncelikli, mevcut sprint için
   - `P2`: Orta öncelikli, planlı
   - `P3`: Düşük öncelikli, zaman kalırsa




### Oturum İş Akışı

1. **Oturum Başlangıcı**
   ```
   1. "Claude masaüstü uygulamasında mısınız?" diye sor
   2. tasks.md dosyasını gözden geçir
   3. PROJECT_STATUS.md'yi kontrol et
   4. Mevcut sprint görevlerini belirle
   5. Engelleyici olmadığını doğrula
   ```

2. **Görev Seçimi**
   - Öncelik sırasına göre (P0 → P1 → P2 → P3)
   - Bağımlılıkları çözülmüş olanlardan
   - Mevcut sprint'ten
   - Görev başlamadan önce uygun branch oluştur
   - İlk commit'i yap (`git commit --allow-empty -m "Start [TASK-ID] - description"`)

3. **Oturum Süreçleri**
   - Analiz: Gerekli belgeleri incele, problemi anla
   - Planlama: Yaklaşımı belirle, işi küçük adımlara böl
   - Uygulama: Kod yazma ve test
   - Değerlendirme: Kabul kriterlerini karşılıyor mu?

4. **Oturum Tamamlama**
   - Değişiklikleri gözden geçir
   - Test senaryolarını çalıştır
   - Dokümantasyonu güncelle
   - İşi tamamla veya bir sonraki oturuma devret

### Görev Tamamlama İş Akışı

1. **Kabul kriterlerini kontrol et**
2. **Test senaryolarını çalıştır**
3. **Dokümantasyon güncellemeleri yap:**
   - **tasks.md**: Görev durumunu güncelle (Completed ✅), gerçek süreyi ve tamamlanma tarihini ekle
   - **PROJECT_STATUS.md**: Yeni özellikleri "Tamamlanan İşlemler" bölümüne ekle, proje yapısını güncelle
   - **README.md**: Kullanıcıya görünür bir özellik eklendiyse
   - **CHANGELOG.md**: Değişiklikleri logla

#### Görev Tamamlama Kontrol Listesi
```
✅ GÖREV TAMAMLAMA KONTROL LİSTESİ:
   
1. [ ] tasks.md güncellemesi:
   - Status: Completed ✅
   - Actual time eklendi
   - Completion date eklendi
   
2. [ ] PROJECT_STATUS.md güncellemesi:
   - "Tamamlanan İşlemler" bölümüne yeni özellik eklendi
   - Proje yapısı güncellendi (yeni dosyalar varsa)
   - "Bir Sonraki Oturumda Yapılacaklar" listesi güncellendi
   
3. [ ] Diğer gerekli dokümanlar:
   - README.md (kullanıcı-görünür özellikler için)
   - CHANGELOG.md
```

**Görev tamamlandığında Claude şunu desin:**
```
🎉 [TASK-ID] tamamlandı!

📄 Güncellenmesi gereken dosyalar:
1. tasks.md - Görev durumunu Completed yap ✅
2. PROJECT_STATUS.md - Yeni özelliği ekle
3. [Diğer gerekli dosyalar]

Bu güncellemeleri yapayım mı? (Claude Desktop'ta iseniz)
```

### Kod Standartları

1. **Dosya Organizasyonu**
   ```
   benzerDesen/
   ├── app.py                  # Flask web uygulaması
   ├── extract_features.py     # Özellik çıkarma
   ├── auto_cluster.py         # Kümeleme algoritmaları
   ├── train_model.py          # Model eğitimi
   ├── check_updates.py        # Güncelleme kontrolleri
   ├── db_utils.py             # Veritabanı yardımcıları
   ├── db_init.py              # Veritabanı şeması oluşturma
   ├── migrate_data.py         # Veri migrasyon aracı
   ├── static/                 # Statik dosyalar (JS, CSS)
   ├── templates/              # HTML şablonları
   ├── tests/                  # Test dosyaları
   │   ├── test_extract_features.py
   │   ├── test_auto_cluster.py
   │   └── ...
   ├── image_features/         # Özellik vektörleri
   ├── exported_clusters/      # Kümeleme sonuçları
   └── realImages/             # Orijinal görseller
   ```

2. **Python Kod Standartları**
   - PEP 8 uyumlu
   - Type hints kullanımı
   - Docstrings (Google formatı)
   - İsimlendirme: snake_case fonksiyonlar, PascalCase sınıflar
   - Max satır uzunluğu: 88 karakter (Black formatter)

3. **JS Kod Standartları**
   - Fonksiyonel komponentler
   - Açıklayıcı değişken isimleri 
   - Modüler organizasyon
   - ESLint uyumlu kod

### Dokümantasyon Gereksinimleri

1. **Kod Yorumları**
   - Docstring tüm fonksiyonlar için
   - Karmaşık mantık açıklamaları
   - İşlenen algoritmaların referansları

2. **README Güncellemeleri**
   - Özellik eklemeleri
   - Konfigürasyon değişiklikleri
   - Kullanım örnekleri

3. **Görev Dokümantasyonu**
   - Net kabul kriterleri
   - Test senaryoları
   - Bağımlılıklar

### Versiyon Kontrol

1. **Görev Bazlı Commitler**
   - Her görev başlamadan önce commit yapılmalı
   - Commit mesajı görev ID'sini içermeli
   - Küçük, atomik commitler tercih edilmeli
   
   ```bash
   # Görev başlangıcı
   git commit -m "Start [TASK-ID] - brief description"
   
   # Görev ilerlemesi
   git commit -m "WIP: [TASK-ID] implement feature X"
   git commit -m "Fix: [TASK-ID] resolve issue Y"
   
   # Görev tamamlanması
   git commit -m "Complete [TASK-ID] - final implementation"
   ```

2. **Commit Mesajları**
   ```
   <type>: [TASK-ID] <description>

   [optional body]
   [optional footer]
   ```
   Types: feature, fix, docs, style, refactor, test, chore, infra, task

3. **Branch Stratejisi**
   - main: Production ready
   - develop: Integration branch
   - feature/*: Yeni özellikler (feature/TASK-ID-description)
   - fix/*: Hata düzeltmeleri (fix/TASK-ID-description)
   - infra/*: Altyapı çalışmaları (infra/TASK-ID-description)
   - refactor/*: Yeniden yapılandırma (refactor/TASK-ID-description)


### Veritabanı Tabanlı Görev Yönetimi
- SQLite veritabanı kullanarak görevleri, proje durumunu ve oturumları yönetin
- Markdown dosyaları yerine veritabanı sorgularıyla daha verimli proje durumu takibi yapın

#### Veritabanı Kurulumu ve Kullanımı
1. `python db_setup.py` komutu ile veritabanını oluşturun
2. `python task_manager.py [komut]` ile görev yönetimi yapın

Örnek Komutlar:
```bash
# Proje durumunu görüntüle
python task_manager.py status

# Tüm görevleri listele
python task_manager.py list

# Aktif sprint görevlerini göster
python task_manager.py list --status "In Progress"

# Görev ekleme
python task_manager.py add "Yeni özellik" FEATURE P1


## 🔍 Geliştirme Kılavuzu

### Temel Flask Yapısı
```python
# app.py
from flask import Flask, render_template, request, jsonify
import logging

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/similarity', methods=['POST'])
def find_similar():
    try:
        filename = request.json.get('filename')
        model_type = request.json.get('model_type', 'pattern')
        count = int(request.json.get('count', 10))
        
        # İşlem gerçekleştir...
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        logging.error(f"Error in similarity API: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Veritabanı Yapısı (SQLite)

```python
# db_init.py
import sqlite3

def init_db():
    conn = sqlite3.connect('benzer_desen.db')
    cursor = conn.cursor()
    
    # Fabrics (Kumaşlar) tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fabrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE NOT NULL,
        design TEXT,
        season TEXT,
        quality TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Features (Özellikler) tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fabric_id INTEGER,
        type TEXT NOT NULL,  -- WV, PES, PA, vb.
        percentage INTEGER NOT NULL,
        FOREIGN KEY (fabric_id) REFERENCES fabrics(id)
    )
    ''')
    
    # Models (Modeller) tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,  -- pattern, color, texture, color+pattern
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Versions (Versiyonlar) tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id INTEGER,
        name TEXT NOT NULL,  -- v1, v2, vb.
        comment TEXT,
        algorithm TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (model_id) REFERENCES models(id)
    )
    ''')
    
    # Clusters (Kümeler) tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clusters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version_id INTEGER,
        cluster_number INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (version_id) REFERENCES versions(id)
    )
    ''')
    
    # Cluster üyeleri tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cluster_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id INTEGER,
        fabric_id INTEGER,
        is_representative BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cluster_id) REFERENCES clusters(id),
        FOREIGN KEY (fabric_id) REFERENCES fabrics(id)
    )
    ''')
    
    # Feedback tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anchor_fabric_id INTEGER,
        output_fabric_id INTEGER,
        model_id INTEGER,
        version_id INTEGER,
        rating INTEGER,  -- 1-5 arası derecelendirme
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (anchor_fabric_id) REFERENCES fabrics(id),
        FOREIGN KEY (output_fabric_id) REFERENCES fabrics(id),
        FOREIGN KEY (model_id) REFERENCES models(id),
        FOREIGN KEY (version_id) REFERENCES versions(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Veritabanı şeması başarıyla oluşturuldu!")
```

### Geliştirme/Test İş Akışı

1. **Geliştirme**
   ```bash
   # Virtual Environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Bağımlılıkları Yükle
   pip install -r requirements.txt
   
   # Uygulamayı Çalıştır
   python app.py
   ```

2. **Test**
   ```bash
   # Unit Testleri Çalıştır
   python -m pytest
   
   # Coverage Test
   python -m pytest --cov
   ```

3. **Hata Ayıklama**
   - Debug modunda çalıştır
   - Logging ifadelerini kullan
   - Browser devtools ile frontend hata ayıklama

## 🔄 Görev Güncelleme Komutları

Konuşma içinde şu komutları kullanabilirsiniz:

- `task status` - Mevcut görev durumunu görüntüle
- `task update [TASK-ID]` - Belirli bir görevi güncelle
- `task next` - Önerilen sonraki görevi al
- `task block [TASK-ID] [reason]` - Görevi engellendi olarak işaretle
- `task complete [TASK-ID]` - Görevi tamamlandı olarak işaretle
- `task start [TASK-ID]` - Görevi başlat

## 🎯 Proje Hedefleri

1. **MVP (Minimum Viable Product) Hedefleri**
   - Temel benzerlik analizi fonksiyonları
   - Kümeleme ve versiyon yönetimi
   - Verimli performans ve bellek kullanımı
   - SQLite entegrasyonu
   - Kullanıcı dostu arayüz

2. **Teknik Mükemmellik**
   - Temiz kod yapısı
   - Kapsamlı test coverage (%80+)
   - Detaylı dokümantasyon
   - Performans optimizasyonu

3. **ML Yetenekleri**
   - Yüksek doğrulukta benzerlik tespiti
   - Çoklu model desteği (desen, renk, doku, kombinasyon)
   - Uyumlu renk analizi
   - Feedback öğrenme sistemi (MVP sonrası)

## 📝 Notlar

- Masaüstüne karşı tarayıcı durumunu her zaman kontrol edin
- Görev tamamlandıktan sonra tasks.md'yi güncelleyin
- PROJECT_STATUS.md'yi büyük değişikliklerle güncel tutun
- Oturum başlangıcında bu talimatları gözden geçirin
- Gereksinimler net değilse açıklama isteyin
- MVP için geliştirme hızı veri doğruluğundan daha önemli

---
*Son Güncelleme: 2025-05-06* (SQLite Veritabanı Şeması ve Proje Yönetimi Görev Kategorileri güncellendi)