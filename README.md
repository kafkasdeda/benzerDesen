# Benzer Desen Projesi

## 📋 Proje Tanımı

Benzer Desen, tekstil sektöründe görsel benzerlik (desen, renk, doku) analizi yaparak benzer görselleri gruplandıran ve yöneten bir sistemdir. Proje, derin öğrenme ve görüntü işleme teknolojilerini kullanarak kumaş desenlerinin benzerliklerini analiz eder, otomatik gruplandırma yapar ve kullanıcıların görsel veri setleri üzerinde daha verimli çalışmasını sağlar.

## 🚀 Temel Özellikler

- **Görsel Benzerlik Analizi**: Desen, renk ve doku özelliklerine göre benzerlik hesaplama
- **Otomatik Kümeleme**: KMeans, DBSCAN ve Hierarchical gibi algoritmaları kullanarak benzer desenli görselleri otomatik gruplama
- **Küme Versiyon Yönetimi**: Farklı kümeleme parametrelerini ve sonuçlarını versiyonlar halinde saklama
- **Renksel Uyum Arama**: Renk teorisi kullanarak bir görselle uyumlu renkli diğer görselleri bulma
- **Performans Optimizasyonu**: Faiss kütüphanesi ile hızlı benzerlik araması
- **Kullanıcı Geri Bildirimi**: Benzerlik sonuçlarını 5 yıldız üzerinden derecelendirme sistemi

## 🛠️ Kurulum

### Gereksinimler

- Python 3.9+
- pip (Python paket yöneticisi)
- CUDA destekli GPU (opsiyonel, ama performans için önerilir)

### Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

### Yüzdelik Çevrilmiş Görsel Kontrolü

Sistemin sağlıklı çalışması için gereken görsellerin türetilmesi:

```bash
python generate_thumbnails.py
```

## 💻 Kullanım

### Uygulamayı Başlatma

```bash
python app.py
```

Uygulama başlatıldıktan sonra tarayıcıda `http://localhost:5000` adresine giderek sisteme erişebilirsiniz.

### Görselleri Yükleme

Analizde kullanılacak görseller `realImages/` klasörüne yüklenmelidir. Desteklenen formatlar:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)

### Model Eğitimi

Özelleştirilmiş modeller eğitmek için:

```bash
python train_model.py --model_type pattern --epoch 20 --batch_size 32
```

### Kümeleme İşlemi

Özellik vektörlerine dayalı otomatik kümeleme yapmak için:

```bash
python auto_cluster.py --model_type pattern --algorithm kmeans --clusters 10
```

## 📊 Proje Yönetimi

Projemiz, SQLite veritabanı tabanlı bir proje yönetim sistemi kullanmaktadır. Bu sistem, görevlerin takibi, proje durumunun izlenmesi ve oturumların kaydedilmesi gibi işlevleri sağlar.

### Proje Yönetim Veritabanı Kurulumu

```bash
python db_setup.py
```

### Görev Yönetim Aracı

Projedeki görevleri komut satırından yönetmek için:

```bash
# Görevleri listeleme
python task_manager.py list

# Görev detaylarını görüntüleme
python task_manager.py show TASK-001-example-task

# Yeni görev ekleme
python task_manager.py add "Yeni özellik" FEATURE P1 --description "Bu bir açıklama" --estimated 4

# Görevi güncelleme
python task_manager.py update TASK-001-example-task --status "In Progress" --priority P0

# Proje durumunu görüntüleme
python task_manager.py status
```

## 👨‍💻 Arayüz Kullanımı

Benzer Desen projesi üç panelli bir arayüz sunar:

### Sol Panel: Görseller Listesi
- Tüm görselleri listeler
- Arama ve filtreleme özellikleri sunar
- Görsele tıklandığında orta panelde benzerlik sonuçları gösterilir

### Orta Panel: Benzerlik Sonuçları
- Seçilen görsele benzer görselleri gösterir
- Filtreleme ve sıralama özellikleri sunar
- Benzerlik derecesini görselleştirir
- Uyumluyu Ara özelliği ile renk uyumu araması yapar

### Sağ Panel: Model ve Versiyon Yönetimi
- Model türü seçimi (desen, renk, doku, renk+desen)
- Versiyon yönetimi
- Küme temsilcilerini gösterme
- Seçilen görselleri kümelere taşıma

## 🧪 Test Etme

Unit testleri çalıştırmak için:

```bash
python -m pytest
```

Belirli bir test dosyasını çalıştırmak için:

```bash
python -m pytest tests/test_extract_features.py
```

## 📓 Oturum Notları

Proje kapsamında yapılan çalışmalar ve ilerleme kayıtları için:

```bash
# Tüm oturumları listeleme
python task_manager.py sessions

# Yeni oturum ekleme
python task_manager.py add-session --completed "FEATURE-001 tamamlandı" --next "TASK-002 ile devam edilecek"
```

## 📈 Proje Durumu

Proje şu anda geliştirme aşamasında olup, MVP (Minimum Viable Product) kriterleri üzerinde çalışılmaktadır. Mevcut ilerleme %70 civarındadır.

### MVP Kriterleri
- ✅ Görsel benzerlik analizi
- ✅ Otomatik kümeleme
- ✅ Uyumlu renk arama
- ✅ Performans optimizasyonları
- ✅ Kullanıcı dostu arayüz
- ⏳ SQLite veritabanı entegrasyonu
- ⏳ Proje yönetimi standardizasyonu

## 🤝 Katkıda Bulunma

1. Bu repo'yu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inize push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje Apache 2.0 lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 📞 İletişim

Sorularınız için [email protected] adresine e-posta gönderebilirsiniz.

---

*Son güncelleme: 6 Mayıs 2025*