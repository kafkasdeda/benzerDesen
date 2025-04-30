# Benzer Desen Projesi - Session 13: Hammadde Karışımı Slider Problemi ve Veri Yapısı Sorunları

## Genel Durum

Bu oturumda, Benzer Desen projesindeki Hammadde Karışımı filtresine odaklandık. Filtreleme Parametreleri panelinde bulunan Hammadde Karışımı (Opsiyonel) bölümünde, kullanıcıların hammadde tipi seçip, belirli yüzde aralıklarında filtreleme yapmasını sağlayan bölümde iki önemli sorun tespit edildi:

1. **Combobox İçeriği Sorunu**: Hammadde seçim combobox'ı içerisine hammadde değerleri yüklenmiyordu.
2. **Tek Başlı Slider Sorunu**: Eskiden çift başlı olan slider (min-max değer belirlemek için), yeni sistemde tek başlı slider'a dönüşmüştü.

## Tespit Edilen Sorunlar

### 1. Combobox İçeriği Sorunu

`image_metadata_map.json` dosyasındaki features yapısında değişiklik olduğunu tespit ettik:

**Eski Veri Yapısı:**
```json
"features": [
  ["WV", 60],  // %60 Yün (Wool/WV)
  ["PES", 40]  // %40 Polyester (PES)
]
```

**Yeni Veri Yapısı:**
```json
"features": []  // Boş dizi
```

Bu değişiklik nedeniyle, `left_panel.js` içinde veri yükleme sırasında oluşturulan `window.blendSet` değişkeni boş kalıyordu, bu da combobox'ın boş görünmesine neden oluyordu.

### 2. Slider Yapısı Sorunu

`center_panel.js` dosyasının `addMaterial` fonksiyonunda, slider oluşturulurken tek değer kullanılıyordu:

```javascript
const slider = noUiSlider.create(rangeContainer, {
    start: [0],           // Tek değer
    connect: [true, false], // Tek noktalı slider bağlantısı
    step: 1,
    range: {
        'min': 0,
        'max': 100
    }
});
```

## Yaptığımız Değişiklikler

### 1. Veri Yapısı Sorunu İçin

Bu sorunu çözmek için, eski `image_metadata_map.json` dosyasını kullanmayı ve `windows.blendSet` değişkeninin düzgün doldurulmasını sağlamayı tercih ettik.

### 2. Slider Yapısı İçin

Slider'ı çift başlı yapmak için `addMaterial` fonksiyonunu şu şekilde güncelledik:

```javascript
const slider = noUiSlider.create(rangeContainer, {
    start: [0, 100],      // Min ve max değerleri
    connect: true,        // Aralığı bağla
    step: 1,
    range: {
        'min': 0,
        'max': 100
    }
});

// Slider değişimini dinle
slider.on('update', function(values, handle) {
    const minValue = parseInt(values[0]);
    const maxValue = parseInt(values[1]);
    valueDisplay.textContent = `${minValue}-${maxValue}%`;
    updateTotalPercentage();
    updateMixFilters();
});
```

Ayrıca `updateMixFilters` fonksiyonunu da güncelledik:

```javascript
function updateMixFilters() {
    currentMixFilters = [];
    
    const materialRows = document.querySelectorAll(".material-row");
    materialRows.forEach(row => {
        const type = row.dataset.type;
        const valueText = row.querySelector(".material-value").textContent;
        
        // Değer formatı "min-max%" şeklinde
        const valueParts = valueText.split('-');
        if (valueParts.length === 2) {
            const minValue = parseInt(valueParts[0]);
            const maxValue = parseInt(valueParts[1].replace('%', ''));
            
            if (!isNaN(minValue) && !isNaN(maxValue)) {
                currentMixFilters.push({
                    type: type,
                    min: minValue,
                    max: maxValue
                });
            }
        }
    });
}
```

## Yeni Tespit Edilen Sorun

Değişiklikleri yaptıktan ve uygulamayı yeniden başlattıktan sonra, `image_metadata_map.json` dosyasındaki "features" alanlarının yeniden boşaldığını gözlemledik. Bu, uygulama başlatıldığında bir işlemin bu dosyayı yeniden oluşturuyor veya güncelliyor olabileceğine işaret ediyor.

## Nerede Kaldık

Şu an önemli soru, `image_metadata_map.json` dosyasını hangi sürecin boşalttığını belirlemek. Muhtemelen `generate_metadata_map.py` scriptinin uygulama başlatılırken çalıştırılması veya başka bir güncelleme mekanizması bu soruna neden oluyor olabilir. Bu durumda, `app.py` veya başlangıç kodlarında bu mekanizmayı tespit etmemiz gerekiyor.

## Sonraki Adımlar

1. **Metadata Yeniden Oluşturma Mekanizmasını Tespit Etme**:
   - `app.py` dosyasını inceleyerek, başlangıçta `image_metadata_map.json` dosyasını yeniden oluşturan/güncelleyen kod parçasını bulma.
   - Otomatik güncelleme veya çalıştırma mekanizmalarını kontrol etme.

2. **Kalıcı Çözüm Uygulaması**:
   - Tespit edilen mekanizmayı devre dışı bırakma veya değiştirme.
   - Ya da `generate_metadata_map.py` scriptini güncelleyerek, features alanını doğru şekilde doldurmasını sağlama.

3. **Geçici Çözüm**:
   - Uygulama başlatıldıktan sonra, manuel olarak doğru veri yapısına sahip `image_metadata_map.json` dosyasını geri yükleme.
   - Ya da `window.blendSet` değişkenini JavaScript kodunda sabit değerlerle doldurma.

Bu oturumun sonunda, hammadde combo box'ının içeriğinin boşalması sorununu çözmek için odaklanmamız gereken asıl alanın, metadata yeniden oluşturma mekanizması olduğunu belirledik.
