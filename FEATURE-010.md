# FEATURE-010-3d-fabric-visualization

## 📋 Görev Tanımı ve Kapsam

### Hedefler

Bu görev, Benzer Desen projesinde tekstil desenlerini 3D giysi modelleri üzerinde görselleştirme özelliğini geliştirmeyi amaçlamaktadır. Kullanıcılar, seçtikleri kumaş desenlerini gerçek zamanlı olarak 3D giysi modelleri üzerinde görebilecek ve modeli farklı açılardan inceleyebileceklerdir.

### Teknik Gereksinimler

- Three.js kütüphanesi ile 3D model görüntüleme
- GLTF formatındaki modelleri yükleme ve işleme
- Kumaş desenlerini model üzerine texture olarak uygulama
- 3D modeli döndürme, yakınlaştırma ve uzaklaştırma kontrolleri
- Kumaş deseninin modele doğru şekilde map'lenmesi
- Farklı cinsiyetlere göre (KM: erkek, KW: kadın) model seçimi
- Basit, kullanıcı dostu bir arayüz

### Kabul Kriterleri

1. Kullanıcı bir kumaş deseni seçtiğinde, desene uygun 3D model otomatik olarak yüklenmelidir
2. 3D model, kumaş deseni uygulanmış şekilde kaliteli görüntülenmelidir
3. Kullanıcı modeli fare ile döndürebilmeli, yakınlaştırabilmeli ve uzaklaştırabilmelidir
4. Farklı kumaş desenleri arasında geçiş yapılabilmelidir
5. Yükleme süreleri 3 saniyeden az olmalıdır
6. Düşük donanımlı bilgisayarlarda bile düzgün çalışmalıdır
7. Mobil cihazlarda responsive olarak çalışmalıdır
8. Kumaş desenlerinin endüstriyel görünümü doğru şekilde yansıtılmalıdır

## 📊 Alt Görevler ve İlerleme Takibi

### FEATURE-010-A: Proje Altyapısı ve Three.js Entegrasyonu
- **Öncelik**: P0
- **Tahmini Süre**: 3 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: Three.js kütüphanesinin projeye entegrasyonu ve temel 3D görüntüleme altyapısının oluşturulması
- **Yapılacaklar**:
  - [ ] Three.js ve gerekli bağımlılıkların yüklenmesi
  - [ ] 3D görüntüleme için temel HTML/JS yapısının oluşturulması
  - [ ] 3D canvas element'inin oluşturulması ve boyutlandırılması
  - [ ] Sahne, kamera ve renderer ayarlarının yapılması
  - [ ] Temel ışıklandırma ve ortam ayarlarının yapılması
  - [ ] Browser uyumluluğunun test edilmesi

### FEATURE-010-B: 3D Model Yükleme ve Klasör Yapısı
- **Öncelik**: P0
- **Tahmini Süre**: 4 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: 3D model klasör yapısının oluşturulması ve GLTF modellerinin yüklenmesi
- **Yapılacaklar**:
  - [ ] `3d-models/` klasör yapısının oluşturulması
  - [ ] Erkek ve kadın model klasörlerinin oluşturulması
  - [ ] GLTF modellerin yüklenme mekanizmasının geliştirilmesi
  - [ ] Model yüklenirken progress bar gösterimi
  - [ ] Hata durumlarının yönetilmesi
  - [ ] Model metadata bilgilerinin saklanması
  - [ ] Modeli ön belleğe alma mekanizması

### FEATURE-010-C: Kumaş Deseni Uygulama
- **Öncelik**: P0
- **Tahmini Süre**: 5 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: Seçilen kumaş deseninin 3D model üzerine uygulanması
- **Yapılacaklar**:
  - [ ] Kumaş deseninin texture olarak yüklenmesi
  - [ ] Model malzemelerinin (materials) incelenmesi ve değiştirilmesi
  - [ ] Diffuse map olarak kumaş deseninin uygulanması
  - [ ] UV mapping ayarlarının yapılması
  - [ ] Texture tekrarlama (repeat) ve döndürme ayarları
  - [ ] Kumaş türüne göre normal ve metallic/roughness ayarları
  - [ ] Kumaş desen önizlemesinin oluşturulması

### FEATURE-010-D: Kullanıcı Kontrolleri
- **Öncelik**: P1
- **Tahmini Süre**: 3 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: 3D model etkileşimi için kullanıcı kontrollerinin geliştirilmesi
- **Yapılacaklar**:
  - [ ] OrbitControls ile model döndürme
  - [ ] Yakınlaştırma/uzaklaştırma kontrolleri
  - [ ] Kamera açısı sınırlamalarının ayarlanması
  - [ ] Mobil dokunma desteği
  - [ ] Otomatik döndürme seçeneği
  - [ ] Kamera pozisyonunu sıfırlama butonu
  - [ ] Kullanıcı kontrollerinin özelleştirilebilmesi

### FEATURE-010-E: Kumaş Kodu Analizi ve Otomatik Model Seçimi
- **Öncelik**: P1
- **Tahmini Süre**: 3 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: Kumaş koduna göre (KM, KW, KP) uygun 3D modelin otomatik seçilmesi
- **Yapılacaklar**:
  - [ ] Kumaş kodlarını analiz etme fonksiyonu
  - [ ] Cinsiyete göre model seçim mantığı
  - [ ] Premium kumaşlar için özel işleme
  - [ ] Model bulunamadığında varsayılan modele yönlendirme
  - [ ] Kullanıcıya manuel model değiştirme seçeneği
  - [ ] Model seçim geçmişinin saklanması

### FEATURE-010-F: UI Entegrasyonu
- **Öncelik**: P1
- **Tahmini Süre**: 4 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: 3D görüntüleyiciyi mevcut UI'a entegre etme
- **Yapılacaklar**:
  - [ ] Sağ panele 3D görüntüleyici eklenmesi
  - [ ] Center panel ile entegrasyon
  - [ ] Seçilen kumaşın 3D modele yansıtılması
  - [ ] Responsive tasarım ayarları
  - [ ] Tam ekran modu
  - [ ] 3D görüntüleyiciyi açma/kapama seçeneği
  - [ ] Performance optimizasyonları

### FEATURE-010-G: Performans İyileştirmeleri
- **Öncelik**: P2
- **Tahmini Süre**: 3 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: 3D görüntüleme performansının iyileştirilmesi
- **Yapılacaklar**:
  - [ ] Model seviyesi detay (Level of Detail) ayarları
  - [ ] Texture boyutlarının optimize edilmesi
  - [ ] Gereksiz geometri ve malzemelerin temizlenmesi
  - [ ] Bellek yönetimi ve temizliği
  - [ ] İşlem yükünü azaltma stratejileri
  - [ ] Yükleme zamanlarını optimize etme
  - [ ] Düşük donanım için fallback seçenekleri

### FEATURE-010-H: Test ve Dokümantasyon
- **Öncelik**: P2
- **Tahmini Süre**: 2 saat
- **Durum**: Planlandı 🗓️
- **Gerçek Süre**: -
- **Açıklama**: 3D görüntüleme özelliğinin test edilmesi ve belgelendirilmesi
- **Yapılacaklar**:
  - [ ] Farklı tarayıcılarda test edilmesi
  - [ ] Farklı cihazlarda test edilmesi
  - [ ] Farklı kumaş desenleriyle test edilmesi
  - [ ] Kullanım kılavuzunun hazırlanması
  - [ ] Kod dokümantasyonunun tamamlanması
  - [ ] Performans ölçümlerinin yapılması
  - [ ] Bilinen sınırlamaların belgelenmesi

## 📝 Teknik Notlar ve Talimatlar

### Proje Bilgileri
- Proje yolu: `C:\projeler\benzerDesen`
- Claude, dosya yazma izni vardır (her session'da sorma)
- Her dosya güncelleme veya oluşturma işleminden önce mutlaka onay alınmalıdır
- Önemli dosya değişikliklerinden önce "burada git commit etseniz iyi olur" uyarısı verilmelidir
- Her session'da en fazla 2 task bitirilebilir
- Session sonunda bu FEATURE-010.md dosyası güncellenir, bitirilen ve yarım kalan tasklar belirlenir

### 3D Model Klasör Yapısı
```
3d-models/
  ├── men/
  │   ├── jacket/
  │   │   └── default/
  │   │       ├── men-jacket_gltf_thin.gltf
  │   │       ├── men-jacket_gltf_thin.bin
  │   │       └── ... (texture dosyaları)
  │   └── shirt/
  │       └── ...
  └── women/
      ├── dress/
      │   └── ...
      └── ...
```

### Kumaş Kodu Algılama Mantığı
- "KM" içeren kumaşlar → Erkek modelleri (`men/` klasörü)
- "KW" içeren kumaşlar → Kadın modelleri (`women/` klasörü)
- "KP" içeren kumaşlar → 
  - Eğer aynı zamanda "KM" içeriyorsa → Erkek modelleri
  - Eğer aynı zamanda "KW" içeriyorsa → Kadın modelleri
  - Hiçbiri yoksa → Varsayılan olarak erkek modelleri (`men/` klasörü)

### Three.js Entegrasyonu
Three.js modeli yüklemek için temel kod:

```javascript
// Three.js kütüphanelerini yükle
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Sahne, kamera ve renderer oluştur
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

// Sahneye ışık ekle
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

// GLTF modeli yükle
const loader = new GLTFLoader();
loader.load(
  'path/to/model.gltf',
  (gltf) => {
    scene.add(gltf.scene);
    
    // Model texture'ını değiştir
    gltf.scene.traverse((child) => {
      if (child.isMesh && child.material) {
        // Yeni bir texture yükle
        const textureLoader = new THREE.TextureLoader();
        const fabricTexture = textureLoader.load('path/to/fabric/texture.jpg');
        
        // Texture tekrarlama ayarları
        fabricTexture.wrapS = THREE.RepeatWrapping;
        fabricTexture.wrapT = THREE.RepeatWrapping;
        fabricTexture.repeat.set(4, 4);
        
        // Texture'ı uygula
        child.material.map = fabricTexture;
        child.material.needsUpdate = true;
      }
    });
  },
  (xhr) => {
    // Yükleme progress
    console.log(`${(xhr.loaded / xhr.total) * 100}% loaded`);
  },
  (error) => {
    console.error('Error loading model:', error);
  }
);

// OrbitControls ekle
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Animasyon döngüsü
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

### Potansiyel Zorluklar ve Çözümleri

1. **Model Yükleme Performansı**
   - Sorun: GLTF modelleri büyük olabilir ve yükleme süresi uzayabilir
   - Çözüm: Modelleri optimize etme, progressive loading, düşük çözünürlüklü önizlemeler

2. **Texture Mapping**
   - Sorun: Kumaş deseninin modele düzgün şekilde uygulanması
   - Çözüm: UV mapping kontrolü, texture tekrarlama ayarları, doku yönlendirmesi

3. **Mobil Performans**
   - Sorun: Düşük performanslı mobil cihazlarda yavaş çalışma
   - Çözüm: LOD (Level of Detail) implementasyonu, mobil için optimize edilmiş render ayarları

4. **Browser Uyumluluğu**
   - Sorun: Farklı tarayıcılarda WebGL desteği ve performansı
   - Çözüm: Feature detection, fallback options, cross-browser test

## 🚀 İlerleme Günlüğü

### 10 Mayıs 2025
- Proje planlaması yapıldı
- FEATURE-010.md dosyası oluşturuldu
- 3D model klasör yapısı ve implementasyon stratejisi belirlendi
- Temel klasör yapısı tasarlandı:
  - `3d-models/` ana klasörü
  - `men/` ve `women/` alt klasörleri
  - Kumaş kodu algılama mantığı (KM, KW, KP)

**Sonraki Adımlar:**
- FEATURE-010-A: Three.js entegrasyonu
- Model klasör yapısının oluşturulması
- İlk prototip geliştirme
