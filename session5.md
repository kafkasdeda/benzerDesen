# Benzer Desen Projesi - Session 5: Uyumluyu Ara Özelliği Entegrasyonu

## Genel Durum

Session 5'te, Benzer Desen projemize "Uyumluyu Ara" adlı yeni bir özellik ekledik. Bu özellik, seçilen bir kumaşın dominant rengini tespit ederek, renk teorisine dayalı olarak uyumlu renklere sahip diğer kumaşları bulma imkanı sunuyor.

## Yapılan Geliştirmeler

### 1. Backend Değişiklikleri (app.py)

- **Renk Analizi Fonksiyonları**:
  - `calculate_color_similarity`: Görseller arasındaki renk benzerliğini hesaplama
  - `find_harmonious_colors`: Belirli bir renge uyumlu renkleri bulma
  - `/find-harmonious` endpoint'i: Kumaşlarda uyumlu renk aramak için API

```python
def calculate_color_similarity(color1, color2):
    """İki renk arasındaki benzerliği hesaplar"""
    # RGB renkleri HSV formatına dönüştürme
    hsv1 = colorsys.rgb_to_hsv(color1[0]/255, color1[1]/255, color1[2]/255)
    hsv2 = colorsys.rgb_to_hsv(color2[0]/255, color2[1]/255, color2[2]/255)
    
    # Ton (Hue) farkı (0-1 aralığında)
    hue_diff = min(abs(hsv1[0] - hsv2[0]), 1 - abs(hsv1[0] - hsv2[0]))
    
    # Doygunluk (Saturation) ve Değer (Value) farkları
    sat_diff = abs(hsv1[1] - hsv2[1])
    val_diff = abs(hsv1[2] - hsv2[2])
    
    # Ağırlıklı benzerlik skoru (ton daha önemli)
    similarity = 1.0 - (0.6 * hue_diff + 0.2 * sat_diff + 0.2 * val_diff)
    return similarity
```

```python
def find_harmonious_colors(rgb_color, harmony_type="complementary"):
    """Verilen renk için uyumlu renkleri bulur"""
    # RGB'den HSV'ye dönüştürme
    r, g, b = rgb_color
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    harmonious_colors = []
    
    if harmony_type == "complementary":
        # Tamamlayıcı renk (renk çemberinde karşıt)
        complementary_h = (h + 0.5) % 1.0
        comp_rgb = colorsys.hsv_to_rgb(complementary_h, s, v)
        harmonious_colors.append([int(c * 255) for c in comp_rgb])
        
    elif harmony_type == "analogous":
        # Analog renkler (renk çemberinde komşu)
        for angle in [-30, 30]:
            analog_h = (h + angle/360) % 1.0
            analog_rgb = colorsys.hsv_to_rgb(analog_h, s, v)
            harmonious_colors.append([int(c * 255) for c in analog_rgb])
            
    elif harmony_type == "triadic":
        # Triadik renkler (renk çemberinde 120° aralıklarla)
        for angle in [120, 240]:
            triadic_h = (h + angle/360) % 1.0
            triadic_rgb = colorsys.hsv_to_rgb(triadic_h, s, v)
            harmonious_colors.append([int(c * 255) for c in triadic_rgb])
            
    elif harmony_type == "split-complementary":
        # Ayrık tamamlayıcı (tamamlayıcının her iki yanı)
        comp_h = (h + 0.5) % 1.0
        for angle in [-30, 30]:
            split_h = (comp_h + angle/360) % 1.0
            split_rgb = colorsys.hsv_to_rgb(split_h, s, v)
            harmonious_colors.append([int(c * 255) for c in split_rgb])
    
    return harmonious_colors
```

```python
@app.route("/find-harmonious")
def find_harmonious():
    fabric_id = request.args.get("fabricId")
    harmony_type = request.args.get("harmonyType", "complementary")
    
    # Dominant renk tespiti
    img_path = os.path.join("realImages", fabric_id)
    if not os.path.exists(img_path):
        return jsonify({"error": "Görsel bulunamadı"})
    
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (1, 1))  # 1x1 küçültme ile dominant rengi bul
    dominant_color = img[0, 0].tolist()
    
    # Uyumlu renkleri bul
    harmonious_colors = find_harmonious_colors(dominant_color, harmony_type)
    
    # Tüm görsellerle renk benzerliği karşılaştırması
    with open("image_metadata_map.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    results = []
    for filename, meta in metadata.items():
        if filename == fabric_id:
            continue  # Kendisini atla
            
        img_path = os.path.join("realImages", filename)
        if not os.path.exists(img_path):
            continue
            
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (1, 1))
        img_color = img[0, 0].tolist()
        
        # En yüksek renk benzerliğini bul
        max_similarity = 0
        for harm_color in harmonious_colors:
            similarity = calculate_color_similarity(harm_color, img_color)
            max_similarity = max(max_similarity, similarity)
        
        if max_similarity > 0.6:  # Benzerlik eşiği
            results.append({
                "filename": filename,
                "harmony": max_similarity,
                "design": meta.get("design"),
                "season": meta.get("season"),
                "quality": meta.get("quality"),
                "features": meta.get("features", [])
            })
    
    # Benzerliğe göre sırala
    results.sort(key=lambda x: x["harmony"], reverse=True)
    return jsonify(results[:20])  # En iyi 20 sonuç
```

- **Faiss İndekslerini Sıfırlama**:
  - `/reset-faiss-indexes` endpoint'i: Önbelleği temizleme özelliği

### 2. Frontend Değişiklikleri (center_panel.js)

- **Uyumluyu Ara Butonları**:
  - Görsellerin altına "Uyumluyu Ara" butonu eklendi
  - Renk uyumu tipi seçim arayüzü

```javascript
function addHarmoniousSearchButtons() {
    // Tüm görsel kartlarına buton ekle
    document.querySelectorAll('.result-item').forEach(item => {
        const fabricId = item.getAttribute('data-filename');
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'harmony-button-container';
        
        const harmonyButton = document.createElement('button');
        harmonyButton.className = 'harmony-search-btn';
        harmonyButton.innerHTML = 'Uyumluyu Ara';
        harmonyButton.onclick = () => findHarmoniousColors(fabricId);
        
        buttonContainer.appendChild(harmonyButton);
        item.appendChild(buttonContainer);
    });
}
```

- **Uyumlu Renk Arama ve Sonuç Gösterme**:
  - `findHarmoniousColors`: Backend'e istek gönderme
  - `displayHarmoniousResults`: Uyumlu renk sonuçlarını görselleştirme

```javascript
function findHarmoniousColors(fabricId) {
    const harmonyType = document.getElementById('harmonyTypeSelect').value || 'complementary';
    
    // Yükleniyor göstergesi
    document.getElementById('results-container').innerHTML = 
        '<div class="loading-indicator"><div class="spinner"></div><p>Uyumlu renkler aranıyor...</p></div>';
    
    // Backend'e istek gönder
    fetch(`/find-harmonious?fabricId=${fabricId}&harmonyType=${harmonyType}`)
        .then(response => response.json())
        .then(data => {
            displayHarmoniousResults(data, fabricId, harmonyType);
        })
        .catch(error => {
            console.error('Uyumlu renk arama hatası:', error);
            document.getElementById('results-container').innerHTML = 
                '<div class="error-message">Uyumlu renk arama sırasında bir hata oluştu.</div>';
        });
}
```

```javascript
function displayHarmoniousResults(results, fabricId, harmonyType) {
    const container = document.getElementById('results-container');
    
    // Başlık ve bilgi
    let harmonyTitle;
    switch(harmonyType) {
        case 'complementary':
            harmonyTitle = 'Tamamlayıcı (Complementary)';
            break;
        case 'analogous':
            harmonyTitle = 'Analog (Analogous)';
            break;
        case 'triadic':
            harmonyTitle = 'Triadik (Triadic)';
            break;
        case 'split-complementary':
            harmonyTitle = 'Ayrık Tamamlayıcı (Split Complementary)';
            break;
        default:
            harmonyTitle = harmonyType;
    }
    
    // Başlık ve kontrol paneli
    container.innerHTML = `
        <div class="harmony-header">
            <h3>Uyumlu Renkler: ${harmonyTitle}</h3>
            <div class="harmony-controls">
                <select id="harmonyTypeSelect" onchange="findHarmoniousColors('${fabricId}')">
                    <option value="complementary" ${harmonyType === 'complementary' ? 'selected' : ''}>Tamamlayıcı</option>
                    <option value="analogous" ${harmonyType === 'analogous' ? 'selected' : ''}>Analog</option>
                    <option value="triadic" ${harmonyType === 'triadic' ? 'selected' : ''}>Triadik</option>
                    <option value="split-complementary" ${harmonyType === 'split-complementary' ? 'selected' : ''}>Ayrık Tamamlayıcı</option>
                </select>
                <button onclick="findHarmoniousColors('${fabricId}')">Yenile</button>
            </div>
        </div>
        <div class="harmony-info">
            <p>Seçilen kumaş: <strong>${fabricId}</strong> için ${harmonyTitle} renkler</p>
        </div>
        <div class="results-grid" id="harmony-results-grid"></div>
    `;
    
    // Sonuçları göster
    const grid = document.getElementById('harmony-results-grid');
    
    if (results.length === 0) {
        grid.innerHTML = '<div class="no-results">Uyumlu renklere sahip kumaş bulunamadı.</div>';
        return;
    }
    
    results.forEach(result => {
        const resultCard = document.createElement('div');
        resultCard.className = 'result-item';
        resultCard.setAttribute('data-filename', result.filename);
        
        // Benzerlik göstergesi
        const harmonyPercent = Math.round(result.harmony * 100);
        
        resultCard.innerHTML = `
            <div class="img-container">
                <img src="/thumbnails/${result.filename}" alt="${result.filename}" loading="lazy">
                <div class="harmony-badge" style="background-color: ${getColorByPercentage(harmonyPercent)}">
                    ${harmonyPercent}%
                </div>
            </div>
            <div class="item-details">
                <div class="filename">${result.filename}</div>
                <div class="metadata">
                    ${result.design ? `<span class="tag">Desen: ${result.design}</span>` : ''}
                    ${result.season ? `<span class="tag">Sezon: ${result.season}</span>` : ''}
                    ${result.quality ? `<span class="tag">Kalite: ${result.quality}</span>` : ''}
                </div>
            </div>
        `;
        
        grid.appendChild(resultCard);
    });
}
```

### 3. Renk Uyum Tipleri

Dört farklı renk uyumu tipi eklendi:

1. **Tamamlayıcı (Complementary)**: Renk çemberinde 180° karşı olan renkler
2. **Analog (Analogous)**: Renk çemberinde yan yana olan renkler (±30°)
3. **Triadik (Triadic)**: Renk çemberinde eşit aralıklı üç renk (120° aralıklarla)
4. **Ayrık Tamamlayıcı (Split Complementary)**: Bir renk ve onun tamamlayıcısının her iki yanındaki renkler

### 4. Görsel Optimizasyonlar

- Yükleniyor göstergeleri eklendi
- Benzerlik derecesi renkli rozetlerle gösteriliyor
- Lazy loading ile performans iyileştirmeleri

## Sonuç

"Uyumluyu Ara" özelliği, tekstil sektöründe çalışan tasarımcılara çok faydalı bir araç sunuyor. Belirli bir kumaşa uygun, renk harmonisi açısından uyumlu diğer kumaşları hızlıca bularak, koleksiyon oluşturma ve ürün gruplaması yapmayı kolaylaştırıyor.

Bu özelliğin şu ana kadar temel implementasyonu tamamlandı. Sonraki aşamalarda kullanıcı arayüzünün daha da geliştirilmesi ve farklı renk uyum tiplerinin eklenmesi planlanıyor.
