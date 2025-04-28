# Benzer Desen Projesi - Session 4: Performans İyileştirmeleri ve Faiss Entegrasyonu

## Genel Durum ve İlerleyiş

Benzer Desen projemiz şu ana kadar aşağıdaki aşamaları başarıyla tamamlamıştır:

1. **Session 1-2**: Proje yapısını inceleme, eksiklikleri tespit etme, eğitim arayüzü ekleme
2. **Session 3**: Feedback sistemini analiz etme ve eğitime entegrasyon planı
3. **Session 4 (Şu an)**: Performans iyileştirmeleri, özellikle benzerlik arama hızını artırma

Mevcut durumda, color ve color+pattern modelleri için özellik vektörleri oluşturuldu ve model versiyonları oluşturuldu. Ancak, sol paneldeki bir görsele tıklandığında benzerlik sonuçlarının yüklenmesi oldukça yavaş (6-7 saniye). Bu session'da bu probleme odaklanıyoruz.

## Performans Sorunları ve Nedenleri

Sol panelde bir görsele tıklama sonrası arama sonuçlarını yükleme işleminin yavaş olmasının nedenleri şöyle tespit edildi:

1. **Verimsiz Veri Yükleme**:
   - Her arama işleminde `np.load(feature_path)` ile tüm özellik vektörleri her seferinde disk'ten yükleniyor
   - Tüm metadata `image_metadata_map.json` dosyasından her istekte tekrar okunuyor

2. **Optimize Edilmemiş Benzerlik Hesaplamaları**:
   - Sklearn'in `cosine_similarity` ve `euclidean_distances` fonksiyonları büyük veri setleri için verimli değil
   - Filtreler uygulandığında, önce tüm indeksler toplanıp sonra filtreleme yapılıyor

3. **Tekrarlanan Model Veri Yüklemeleri**:
   - Versiyon kontrolü için model verileri her aramada tekrar yükleniyor

## Çözüm: Faiss Entegrasyonu

Facebook AI Similarity Search (Faiss) kütüphanesi, büyük vektör veri setlerinde benzerlik aramaları için optimize edilmiş bir kütüphanedir. Projemiz için faiss-gpu entegrasyonu öneriyoruz.

### Faiss'in Avantajları

- **Yüksek Hızlı Arama**: CPU ile 10x, GPU ile 100x'e kadar hızlanma sağlayabilir
- **Verimli Bellek Kullanımı**: Vektörleri optimize edilmiş yapılarda saklar
- **GPU Desteği**: GPU ile daha hızlı benzerlik aramaları
- **Ölçeklenebilirlik**: Milyonlarca vektörle bile etkili çalışır

### İnceleme Sonuçları

Proje dosyalarını incelediğimizde, Faiss entegrasyonu için gereken altyapının büyük ölçüde hazır olduğunu gördük:

1. **requirements.txt** içinde `faiss-gpu` zaten mevcut
2. **extract_features.py** ve **train_model.py** dosyalarında GPU kontrolü ve kullanımı var
3. Mevcut verilerin Faiss formatına dönüştürülmesi kolay

### Yapılacak Değişiklikler

#### 1. app.py Dosyasında Değişiklikler

`/find-similar` endpoint'ini Faiss kullanacak şekilde güncellemeliyiz:

```python
import faiss
import numpy as np

# Faiss indekslerini saklamak için global değişken
faiss_indexes = {}

# Özellik vektörlerini ve dosya isimlerini saklamak için global değişkenler
cached_features = {}
cached_filenames = {}
cached_metadata = None

def get_faiss_index(model_type):
    # Önbellekte varsa döndür
    if model_type in faiss_indexes:
        return faiss_indexes[model_type]
    
    # Önbellekte yoksa yükle
    feature_path = f"image_features/{model_type}_features.npy"
    if not os.path.exists(feature_path):
        return None
    
    # Özellik vektörlerini yükle (önbellekte yoksa)
    if model_type not in cached_features:
        features = np.load(feature_path)
        cached_features[model_type] = features.astype(np.float32)
    else:
        features = cached_features[model_type]
    
    # Faiss indeksi oluştur
    d = features.shape[1]
    
    # GPU kontrolü
    use_gpu = faiss.get_num_gpus() > 0
    
    if model_type in ["pattern", "color+pattern"]:
        # Kosinüs benzerliği için L2 normalleştirme
        faiss.normalize_L2(features)
        
        if use_gpu:
            # GPU indeksi
            flat_config = faiss.GpuIndexFlatConfig()
            flat_config.device = 0
            res = faiss.StandardGpuResources()
            index = faiss.GpuIndexFlatIP(res, d, flat_config)
        else:
            # CPU indeksi
            index = faiss.IndexFlatIP(d)
    else:
        # Öklid mesafesi indeksi
        if use_gpu:
            flat_config = faiss.GpuIndexFlatConfig()
            flat_config.device = 0
            res = faiss.StandardGpuResources()
            index = faiss.GpuIndexFlatL2(res, d, flat_config)
        else:
            index = faiss.IndexFlatL2(d)
    
    # Vektörleri indekse ekle
    index.add(features)
    
    # İndeksi önbelleğe al
    faiss_indexes[model_type] = index
    
    return index

@app.route("/find-similar", methods=["GET", "POST"])
def find_similar():
    global cached_metadata
    
    filters = request.get_json() if request.method == "POST" else None
    filename = request.args.get("filename")
    model = request.args.get("model", "pattern")
    version = request.args.get("version", "v1")
    topN = int(request.args.get("topN", 100))
    metric = request.args.get("metric", "cosine")
    
    print(f"📊 Benzer görsel arama: model={model}, version={version}, metric={metric}")

    # Gerekli dosya yolları
    feature_path = f"image_features/{model}_features.npy"
    index_path = f"image_features/{model}_filenames.json"
    metadata_path = "image_metadata_map.json"

    if not os.path.exists(feature_path) or not os.path.exists(index_path):
        return jsonify([])

    # Faiss indeksini al
    index = get_faiss_index(model)
    if index is None:
        return jsonify([])
    
    # Önbellekte yoksa dosya isimlerini yükle
    if model not in cached_filenames:
        with open(index_path, "r", encoding="utf-8") as f:
            cached_filenames[model] = json.load(f)
    filenames = cached_filenames[model]
    
    # Önbellekte yoksa metadata yükle
    if cached_metadata is None:
        with open(metadata_path, "r", encoding="utf-8") as f:
            cached_metadata = json.load(f)
    metadata = cached_metadata

    if filename not in filenames:
        return jsonify([])

    # Vektör indeksini bul
    idx = filenames.index(filename)
    
    # Sorgu vektörünü al
    features = cached_features[model]
    query_vector = features[idx].reshape(1, -1).copy()
    
    # Kosinüs benzerliği için L2 normalizasyon
    if model in ["pattern", "color+pattern"] or metric == "cosine":
        faiss.normalize_L2(query_vector)
    
    # Filtreleri uygula
    allowed_indices = get_allowed_indices(filters, filenames, metadata, model, version)
    
    if not allowed_indices:
        return jsonify([])
    
    # Filtrelenmiş indeksler için arama
    filtered_features = features[allowed_indices]
    
    # Geçici indeks oluştur
    if model in ["pattern", "color+pattern"] or metric == "cosine":
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
        fname = filenames[global_idx]
        meta = metadata.get(fname, {})
        
        # Benzerlik skoru
        if model in ["pattern", "color+pattern"] or metric == "cosine":
            # İç çarpım için [0,2] aralığını [0,1] aralığına dönüştür
            similarity = float(1.0 - distances[0][i] / 2)
        else:
            # L2 mesafesi için
            similarity = float(1.0 / (1.0 + distances[0][i]))
        
        # Cluster bilgisi
        cluster_info = get_cluster_info(meta, model, version)
        
        results.append({
            "filename": fname,
            "design": meta.get("design"),
            "season": meta.get("season"),
            "quality": meta.get("quality"),
            "features": meta.get("features", []),
            "cluster": cluster_info,
            "version": version,
            "similarity": similarity
        })
    
    return jsonify(results)
```

#### 2. auto_cluster.py Dosyasında Değişiklikler

Kümeleme algoritmalarını Faiss ile optimize edebiliriz:

```python
def kmeans_clustering(features, k):
    # Vektörleri float32 tipine dönüştür
    features = features.astype(np.float32)
    d = features.shape[1]
    
    # GPU kontrolü
    use_gpu = faiss.get_num_gpus() > 0
    
    if use_gpu:
        # GPU ile KMeans
        kmeans = faiss.Kmeans(d, k, niter=300, verbose=True, gpu=True)
    else:
        # CPU ile KMeans
        kmeans = faiss.Kmeans(d, k, niter=300, verbose=True)
    
    kmeans.train(features)
    _, labels = kmeans.index.search(features, 1)
    
    return labels.reshape(-1)
```

## Uygulama Planı

Faiss entegrasyonunu aşamalı olarak yapmalıyız:

### Aşama 1: Temel Entegrasyon (1-2 gün)

1. **app.py Güncellemesi**: Öncelikle `/find-similar` endpoint'ini Faiss kullanacak şekilde değiştirelim
2. **Önbellek Mekanizmaları**: Özellik vektörleri, dosya isimleri ve metadata için önbellek ekleyelim
3. **Temel Testler**: Performans iyileşmesini ölçelim

### Aşama 2: İleri Seviye Optimizasyonlar (2-3 gün)

1. **auto_cluster.py Güncellemesi**: Kümeleme algoritmalarını Faiss versiyonları ile değiştirelim
2. **Hibrit CPU/GPU Stratejisi**: Farklı indeks türleri için en uygun CPU/GPU stratejisini belirleyelim
3. **İleri Seviye Testler**: Büyük veri setleriyle performans testleri yapalım

### Aşama 3: Frontend İyileştirmeleri (1 gün)

1. **Yükleme İndikatörü**: Arama işlemi sırasında daha iyi kullanıcı geri bildirimi
2. **Lazy Loading**: Görsellerin gerektiğinde yüklenmesi
3. **Önbellek Kontrolleri**: Tarayıcı önbelleğinden daha iyi yararlanma

## Beklenen Performans İyileştirmeleri

| Aşama | Beklenen İyileştirme | Yaklaşık Arama Süresi |
|-------|----------------------|----------------------|
| Mevcut | Baz durum | 6-7 saniye |
| Temel Faiss (CPU) | 5-10x hızlanma | 0.7-1.4 saniye |
| Faiss GPU | 10-100x hızlanma | 0.07-0.7 saniye |
| Tam Optimizasyon | 20-200x hızlanma | 0.03-0.35 saniye |

## Sonuç

Faiss entegrasyonu, Benzer Desen projesinin performansını önemli ölçüde artıracak bir adımdır. Zaten projede `faiss-gpu` requirements.txt'de bulunduğundan, altyapı büyük ölçüde hazırdır. Yapılacak kod değişiklikleri ile bu entegrasyon hızla tamamlanabilir.

Ayrıca, Session 3'te planlanan feedback entegrasyonu ile birleştirilirse, hem hız hem de doğruluk açısından çok daha iyi sonuçlar elde edilebilir. Bu, Benzer Desen projesini tekstil sektöründe çok daha kullanışlı bir araç haline getirecektir.

## Sonraki Adımlar

1. Temel Faiss entegrasyonunu tamamla
2. Performans ölçümleri yap ve karşılaştır
3. Auto_cluster.py için Faiss entegrasyonunu planla
4. Frontend iyileştirmelerini uygula
5. Session 3'te planlanan feedback entegrasyonu ile birleştir
