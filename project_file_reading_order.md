# Benzer Desen Projesi - Dosya Okunma Sırası Kılavuzu

Bu belge, Benzer Desen projesinin çalışma mantığını anlamak için hangi dosyaların hangi sırada okunması gerektiğini açıklamaktadır. Bu sayede projenin akışını ve dosyalar arası ilişkileri daha iyi kavrayabilirsiniz.

## 1. Temel Proje Yapısı

İlk olarak projenin genel yapısını anlamak için ana dokümantasyon dosyalarını incelemelisiniz:

1. **benzer-desen-dokumantasyon.md**: Projenin genel amacını, yapısını ve bileşenlerini tanıtan ana dokümantasyon dosyası
2. **project_summary.md**: Projenin mevcut durumunu ve geliştirme aşamalarını özetleyen rapor
3. **session*.md** dosyaları: Her bir geliştirme oturumunda yapılan değişiklikleri anlatan oturum notları

## 2. Backend Yapısı

Backend akışını anlamak için şu sırada dosyaları incelemeniz önerilir:

1. **app.py**: 
   - Tüm sistemi başlatan Flask web uygulaması
   - Endpoint tanımları ve API rotaları burada bulunur
   - Diğer tüm modülleri çağıran ana giriş noktasıdır

2. **check_updates.py**:
   - Sistem ilk başlatıldığında çalışır
   - Görsel ve metadata değişikliklerini kontrol eder
   - Gerekli güncellemeleri belirler ve uygular

3. **extract_features.py**:
   - Görsellerden özellik vektörlerini çıkarır
   - Farklı model türleri için özellik çıkarma stratejilerini içerir
   - Benzerlik aramasında kullanılacak vektörleri oluşturur

4. **auto_cluster.py**:
   - Özellik vektörlerini kullanarak otomatik kümeleme yapar
   - KMeans, DBSCAN, Hierarchical gibi kümeleme algoritmalarını içerir
   - Yeni versiyonlar oluşturulduğunda çalışır

5. **train_model.py**:
   - Öznitelik çıkarıcı modelleri eğitir
   - Transfer learning ile modelleri oluşturur
   - Farklı model türleri için dönüşümleri tanımlar

6. **train_handlers.py**:
   - Eğitim arayüzü API endpoint'lerini sağlar
   - Eğitim sürecini yönetir ve izler

7. **merge_metadata.py**:
   - Farklı kaynaklardan gelen metadata bilgilerini birleştirir
   - JSON dosyalarını ve görsel özelliklerini işler

8. **generate_thumbnails.py**:
   - Görsel önizlemeleri oluşturur
   - Performans için küçük boyutlu görseller hazırlar

## 3. Frontend Yapısı

Frontend akışını anlamak için şu sırada dosyaları incelemeniz önerilir:

1. **templates/pu.html**:
   - Tüm kullanıcı arayüzünün HTML yapısını tanımlar
   - Üç panelli tasarımı oluşturur
   - JavaScript ve CSS dosyalarını dahil eder

2. **static/js/init.js**:
   - Sayfa ilk yüklendiğinde çalışır
   - Başlangıç kontrolleri ve ayarlarını yapar
   - Diğer JavaScript modüllerinin doğru sırayla yüklenmesini sağlar

3. **static/js/performance-fix.js**:
   - Performans iyileştirmelerini içerir
   - Bellek yönetimi ve otomatik temizleme işlevleri sağlar

4. **static/js/left_panel.js**:
   - Sol panelin (tüm görseller) davranışını tanımlar
   - Görsel yükleme, filtreleme ve tıklama olaylarını yönetir
   - Görsel seçimini center_panel.js'e iletir

5. **static/js/center_panel.js**:
   - Orta panelin (benzerlik sonuçları) davranışını tanımlar
   - Benzer görselleri görüntüleme ve filtreleme yapar
   - Uyumlu renkleri arama işlevlerini içerir

6. **static/js/right_panel.js**:
   - Sağ panelin (model/versiyon) davranışını tanımlar
   - Cluster temsilcilerini gösterir
   - Model ve versiyon seçimi sağlar
   - Yeni versiyon oluşturma ve cluster yönetimi yapar

7. **static/js/train_interface.js**:
   - Eğitim arayüzünün davranışını tanımlar
   - Eğitim parametrelerini toplayan formları oluşturur
   - Eğitim sürecini izler ve görselleştirir

## 4. Veri Akışı

Benzer Desen projesindeki veri akışını anlamak için şu dosyaları incelemelisiniz:

1. **exported_clusters/*/versions.json**:
   - Her model türü için kümeleme versiyonlarını ve küme bilgilerini saklar
   - Model ve versiyon hiyerarşisini tanımlar

2. **image_features/*.npy ve *.json**:
   - Görsellerden çıkarılan özellik vektörlerini saklar
   - Benzerlik aramalarında kullanılır

3. **image_metadata_map.json**:
   - Tüm görsellerin metadata bilgilerini içerir
   - Tasarım, sezon, kalite ve özellik bilgilerini saklar

4. **feedback_log.json**:
   - Kullanıcı geri bildirimlerini kaydeder
   - Benzerlik derecelendirmelerini içerir

## 5. Sistem Başlatma Akışı

Sistem başlatıldığında şu sırada işlemler gerçekleşir:

1. `app.py` çalıştırılır ve Flask uygulaması başlatılır
2. `check_updates.py` içinde `check_for_updates()` fonksiyonu çağrılır
   - Görsel ve metadata değişiklikleri kontrol edilir
   - Değişiklik varsa kullanıcıya bildirilir
3. Kullanıcı onaylarsa `apply_updates()` fonksiyonu çağrılır
   - Metadata güncellenir
   - Gerekirse yeni thumbnail'lar oluşturulur
   - Özellik vektörleri güncellenir
4. `get_faiss_index()` ile Faiss indeksleri oluşturulur (ilk benzerlik aramada)
5. Web arayüzü tarayıcıda görüntülenir ve kullanıcı etkileşime başlar

## 6. Benzerlik Arama Akışı

Kullanıcı bir görsele tıkladığında şu işlemler gerçekleşir:

1. `left_panel.js` içinde tıklama olayı yakalanır
2. `center_panel.js` içindeki `showSimilarImages()` fonksiyonu çağrılır
3. `fetchSimilarImages()` fonksiyonu ile backend'e istek gönderilir
4. `app.py` içindeki `/find-similar` endpoint'i çağrılır
5. Faiss indeksi kullanılarak benzerlik araması yapılır
6. Sonuçlar JSON olarak döndürülür
7. `displaySimilarImages()` fonksiyonu ile sonuçlar görüntülenir

## 7. Uyumlu Renk Arama Akışı

Kullanıcı "Uyumluyu Ara" butonuna tıkladığında şu işlemler gerçekleşir:

1. `center_panel.js` içinde `findHarmoniousColors()` fonksiyonu çağrılır
2. Backend'e istek gönderilir ve `/find-harmonious` endpoint'i çağrılır
3. `app.py` içinde seçilen kumaşın dominant rengi bulunur
4. Seçilen uyum tipine göre uyumlu renkler hesaplanır
5. Tüm görseller taranarak uyumlu renklere sahip olanlar bulunur
6. Sonuçlar JSON olarak döndürülür
7. `displayHarmoniousResults()` fonksiyonu ile sonuçlar görüntülenir

## 8. Model Eğitim Akışı

Kullanıcı eğitim işlemi başlattığında şu işlemler gerçekleşir:

1. `train_interface.js` içinde eğitim parametreleri toplanır
2. `/train-model` endpoint'ine istek gönderilir
3. `app.py` içinde `train_model_route()` fonksiyonu çalıştırılır
4. `train_model.py` betiği subprocess olarak çalıştırılır
5. Eğitim tamamlandığında sonuçlar kullanıcıya gösterilir

## Dosya İnceleme Stratejisi

Benzer Desen projesini incelemek için en etkili strateji:

1. Önce dokümantasyon ve oturum notlarını okuyarak genel bir anlayış oluşturmak
2. `app.py` dosyasını inceleyerek tüm endpoint'leri ve işlevleri anlamak
3. Frontend dosyalarını inceleyerek kullanıcı arayüzü akışını kavramak
4. Belirli bir özellik veya işlevi anlamak için ilgili endpoint'ten başlayıp, çağrılan diğer fonksiyonları takip etmek

Bu yaklaşım, projenin genel yapısını ve işleyişini daha iyi anlamanıza yardımcı olacaktır.
