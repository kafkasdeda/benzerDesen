/**
 * Fabric3D Init - 3D Kumaş Görselleştirici Başlatma Kodu
 * 
 * Benzer Desen projesi için 3D kumaş görselleştirme özelliğini
 * başlatmak ve test etmek için kullanılır.
 * 
 * @author Benzer Desen Ekibi
 * @version 1.0.0
 * @date 2025-05-10
 */

document.addEventListener('DOMContentLoaded', function() {
    // Demo container var mı kontrol et
    const container = document.getElementById('fabric3d-container');
    if (!container) {
        console.log('Fabric3D: Demo container bulunamadı, atlıyorum.');
        return;
    }
    
    console.log('Fabric3D: Demo başlatılıyor...');
    
    // Fabric3D sınıfını başlat
    const fabric3d = new Fabric3DVisualizer('fabric3d-container');
    fabric3d.setDebugMode(true);
    
    // Three.js ortamını başlat
    if (!fabric3d.init()) {
        console.error('Fabric3D: Three.js ortamı başlatılamadı.');
        return;
    }
    
    console.log('Fabric3D: Three.js ortamı başarıyla başlatıldı.');
    
    // Model listesini yükle
    fabric3d.loadModelList()
    .then(modelList => {
    console.log('Fabric3D: Model listesi başarıyla yüklendi.');
        
        // Model listesi hakkında bilgi göster
    if (modelList && modelList.models && modelList.models.length > 0) {
            console.log(`Fabric3D: ${modelList.models.length} model bulundu.`);
                
                // Navigasyon butonlarını göster/gizle
                const prevButton = document.querySelector('.fabric3d-nav-button.prev');
                const nextButton = document.querySelector('.fabric3d-nav-button.next');
                
                if (prevButton && nextButton) {
                    prevButton.style.display = 'flex';
                    nextButton.style.display = 'flex';
                }
            }
        })
        .catch(error => {
            console.error('Fabric3D: Model listesi yüklenemedi:', error);
            updateStatus(`Hata: Model listesi yüklenemedi: ${error.message}`, statusDiv);
            
            // 3 saniye sonra tekrar deneme mesajı göster
            setTimeout(() => {
                updateStatus('Model listesi yüklenemedi. Sayfayı yenileyip tekrar deneyin.', statusDiv);
            }, 3000);
        });
    
    // Ortam hazır mesajı
    const statusDiv = document.createElement('div');
    statusDiv.className = 'fabric3d-status';
    statusDiv.innerHTML = 'Three.js ortamı hazır!<br>Model ve kumaş bekleniyor...';
    container.appendChild(statusDiv);
    
    // Gezinme butonları oluştur
    createNavigationButtons(container, fabric3d, statusDiv);
    
    // Kontrol panel oluştur
    createControlPanel(container, fabric3d);
    
    // Global erişim (test için)
    window.fabric3d = fabric3d;
    
    // Varsayılan modelini test etmek için
    setTimeout(() => {
        // Yükleme durumunu göster
        updateStatus('Varsayılan model yükleniyor...', statusDiv);
        
        fabric3d.loadDefaultModel('men')
            .then(result => {
                console.log('Fabric3D: Varsayılan model yüklendi', result);
                updateStatus('Varsayılan model yüklendi: ' + result.info.name, statusDiv);
                
                // Örnek olarak bir kumaş deseni de uygula
                return fabric3d.applyFabricTexture('/thumbnails/fabric001.jpg');
            })
            .then(() => {
                console.log('Fabric3D: Örnek kumaş uygulandı');
            })
            .catch(error => {
                console.error('Fabric3D: Varsayılan model yüklenemedi:', error);
                updateStatus('Hata: Varsayılan model yüklenemedi: ' + error.message, statusDiv);
            });
    }, 2000); // 2 saniye sonra
});

/**
 * Kontrol paneli oluştur
 * @param {HTMLElement} container Panel konteyneri
 * @param {Fabric3DVisualizer} fabric3d Fabric3D nesnesi
 */
/**
 * Durum mesajını güncelle
 * @param {string} message Durum mesajı
 * @param {HTMLElement} statusDiv Durum mesajı div'i
 */
function updateStatus(message, statusDiv) {
    if (!statusDiv) return;
    statusDiv.innerHTML = message;
}

/**
 * Model gezinme butonlarını oluştur
 * @param {HTMLElement} container Panel konteyneri
 * @param {Fabric3DVisualizer} fabric3d Fabric3D nesnesi
 * @param {HTMLElement} statusDiv Durum mesajı div'i
 */
function createNavigationButtons(container, fabric3d, statusDiv) {
    // Sol gezinme butonu (önceki model)
    const prevButton = document.createElement('button');
    prevButton.className = 'fabric3d-nav-button prev';
    prevButton.innerHTML = '&lt;'; // HTML sayfasında "<" olarak görünecek
    prevButton.style.cssText = `
        position: absolute;
        top: 50%;
        left: 10px;
        width: 40px;
        height: 40px;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 20px;
        display: none; /* Başlangıçta gizli, model listesi yüklendiğinde gösterilecek */
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 100;
        transform: translateY(-50%);
        opacity: 0.7;
        transition: opacity 0.2s, background-color 0.2s;
    `;
    
    prevButton.addEventListener('mouseover', function() {
        this.style.opacity = '1';
    });
    
    prevButton.addEventListener('mouseout', function() {
        this.style.opacity = '0.7';
    });
    
    prevButton.addEventListener('click', function() {
        // Buton devre dışı görünümü
        this.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
        this.style.cursor = 'wait';
        
        if (!fabric3d.isModelLoaded || !fabric3d.currentModelId) {
            updateStatus('Henüz bir model yüklenmedi.', statusDiv);
            // Butonu normal hale getir
            setTimeout(() => {
                this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                this.style.cursor = 'pointer';
            }, 500);
            return;
        }
        
        updateStatus('Önceki model yükleniyor...', statusDiv);
        
        fabric3d.prevModel()
            .then(result => {
                updateStatus(`Model yüklendi: ${result.info.name}`, statusDiv);
                // Butonu normal hale getir
                this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                this.style.cursor = 'pointer';
                
                // Güncel kumaş deseni varsa, yeni modele uygula
                if (fabric3d.currentFabricTexture) {
                    fabric3d.applyFabricTexture(fabric3d.currentFabricTexture);
                }
            })
            .catch(error => {
                updateStatus(`Hata: ${error.message}`, statusDiv);
                console.error('Önceki model yükleme hatası:', error);
                
                // Butonu normal hale getir, ama hata rengi ile
                this.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                this.style.cursor = 'pointer';
                
                // 2 saniye sonra normal renge dön
                setTimeout(() => {
                    this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                }, 2000);
            });
    });
    
    // Sağ gezinme butonu (sonraki model)
    const nextButton = document.createElement('button');
    nextButton.className = 'fabric3d-nav-button next';
    nextButton.innerHTML = '&gt;'; // HTML sayfasında ">" olarak görünecek
    nextButton.style.cssText = `
        position: absolute;
        top: 50%;
        right: 10px;
        width: 40px;
        height: 40px;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 20px;
        display: none; /* Başlangıçta gizli, model listesi yüklendiğinde gösterilecek */
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 100;
        transform: translateY(-50%);
        opacity: 0.7;
        transition: opacity 0.2s, background-color 0.2s;
    `;
    
    nextButton.addEventListener('mouseover', function() {
        this.style.opacity = '1';
    });
    
    nextButton.addEventListener('mouseout', function() {
        this.style.opacity = '0.7';
    });
    
    nextButton.addEventListener('click', function() {
        // Buton devre dışı görünümü
        this.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
        this.style.cursor = 'wait';
        
        if (!fabric3d.isModelLoaded || !fabric3d.currentModelId) {
            updateStatus('Henüz bir model yüklenmedi.', statusDiv);
            // Butonu normal hale getir
            setTimeout(() => {
                this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                this.style.cursor = 'pointer';
            }, 500);
            return;
        }
        
        updateStatus('Sonraki model yükleniyor...', statusDiv);
        
        fabric3d.nextModel()
            .then(result => {
                updateStatus(`Model yüklendi: ${result.info.name}`, statusDiv);
                // Butonu normal hale getir
                this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                this.style.cursor = 'pointer';
                
                // Güncel kumaş deseni varsa, yeni modele uygula
                if (fabric3d.currentFabricTexture) {
                    fabric3d.applyFabricTexture(fabric3d.currentFabricTexture);
                }
            })
            .catch(error => {
                updateStatus(`Hata: ${error.message}`, statusDiv);
                console.error('Sonraki model yükleme hatası:', error);
                
                // Butonu normal hale getir, ama hata rengi ile
                this.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                this.style.cursor = 'pointer';
                
                // 2 saniye sonra normal renge dön
                setTimeout(() => {
                    this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                }, 2000);
            });
    });
    
    // Butonları konteynere ekle
    container.appendChild(prevButton);
    container.appendChild(nextButton);
}

/**
 * Kontrol paneli oluştur
 * @param {HTMLElement} container Panel konteyneri
 * @param {Fabric3DVisualizer} fabric3d Fabric3D nesnesi
 */
function createControlPanel(container, fabric3d) {
    // Kontrol paneli
    const controlPanel = document.createElement('div');
    controlPanel.className = 'fabric3d-controls';
    controlPanel.style.cssText = `
        position: absolute;
        bottom: 10px;
        left: 10px;
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 5px;
        padding: 10px;
        z-index: 100;
        font-size: 12px;
        font-family: Arial, sans-serif;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    `;
    
    // Başlık
    const title = document.createElement('div');
    title.textContent = '3D Kumaş Görselleştirici';
    title.style.fontWeight = 'bold';
    title.style.marginBottom = '8px';
    title.style.fontSize = '14px';
    controlPanel.appendChild(title);
    
    // Model seçimi
    const modelRow = document.createElement('div');
    modelRow.className = 'control-row';
    modelRow.style.marginBottom = '8px';
    
    const modelLabel = document.createElement('label');
    modelLabel.textContent = 'Model: ';
    modelLabel.style.marginRight = '5px';
    modelRow.appendChild(modelLabel);
    
    const modelSelect = document.createElement('select');
    modelSelect.className = 'model-select';
    modelSelect.style.cssText = `
        padding: 2px;
        min-width: 120px;
    `;
    
    // Model seçenekleri
    const models = [
        { value: '', label: 'Model Seçin' },
        { value: '/3d-models/men/jacket/default/men-jacket_gltf_thin.gltf', label: 'Erkek Ceket' },
        { value: '/3d-models/men/shirt/men-shirt_gltf_thin.gltf', label: 'Erkek Gömlek' },
        { value: '/3d-models/women/dress/women-dress_gltf_thin.gltf', label: 'Kadın Elbise' }
    ];
    
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.value;
        option.textContent = model.label;
        modelSelect.appendChild(option);
    });
    
    modelSelect.addEventListener('change', function() {
        const modelPath = this.value;
        if (!modelPath) return;
        
        // Model yükleme butonunu etkinleştir
        loadModelBtn.disabled = false;
        
        // Otomatik yükleme
        if (autoLoadModel.checked) {
            loadModelBtn.click();
        }
    });
    
    modelRow.appendChild(modelSelect);
    controlPanel.appendChild(modelRow);
    
    // Kumaş seçimi
    const textureRow = document.createElement('div');
    textureRow.className = 'control-row';
    textureRow.style.marginBottom = '8px';
    
    const textureLabel = document.createElement('label');
    textureLabel.textContent = 'Kumaş: ';
    textureLabel.style.marginRight = '5px';
    textureRow.appendChild(textureLabel);
    
    const textureSelect = document.createElement('select');
    textureSelect.className = 'texture-select';
    textureSelect.style.cssText = `
        padding: 2px;
        min-width: 120px;
    `;
    
    // Kumaş seçenekleri
    const textures = [
        { value: '', label: 'Kumaş Seçin' },
        // Kullanıcının realImages klasöründeki görsellerini içeren liste
        // Demo için varsayılan desenler
        { value: '/thumbnails/fabric001.jpg', label: 'Kırmızı Desen' },
        { value: '/thumbnails/fabric002.jpg', label: 'Mavi Desen' },
        { value: '/thumbnails/fabric003.jpg', label: 'Yeşil Desen' }
    ];
    
    textures.forEach(texture => {
        const option = document.createElement('option');
        option.value = texture.value;
        option.textContent = texture.label;
        textureSelect.appendChild(option);
    });
    
    textureSelect.addEventListener('change', function() {
        const texturePath = this.value;
        if (!texturePath) return;
        
        // Kumaş uygulama butonunu etkinleştir
        applyTextureBtn.disabled = false;
        
        // Otomatik uygulama
        if (autoApplyTexture.checked) {
            applyTextureBtn.click();
        }
    });
    
    textureRow.appendChild(textureSelect);
    controlPanel.appendChild(textureRow);
    
    // Otomatik butonlar
    const autoRow = document.createElement('div');
    autoRow.className = 'auto-row';
    autoRow.style.marginBottom = '8px';
    
    // Otomatik model yükleme
    const autoLoadModelLabel = document.createElement('label');
    autoLoadModelLabel.style.marginRight = '10px';
    autoLoadModelLabel.style.display = 'inline-flex';
    autoLoadModelLabel.style.alignItems = 'center';
    
    const autoLoadModel = document.createElement('input');
    autoLoadModel.type = 'checkbox';
    autoLoadModel.checked = true;
    autoLoadModel.style.marginRight = '3px';
    
    autoLoadModelLabel.appendChild(autoLoadModel);
    autoLoadModelLabel.appendChild(document.createTextNode('Model'));
    autoRow.appendChild(autoLoadModelLabel);
    
    // Otomatik kumaş uygulama
    const autoApplyTextureLabel = document.createElement('label');
    autoApplyTextureLabel.style.display = 'inline-flex';
    autoApplyTextureLabel.style.alignItems = 'center';
    
    const autoApplyTexture = document.createElement('input');
    autoApplyTexture.type = 'checkbox';
    autoApplyTexture.checked = true;
    autoApplyTexture.style.marginRight = '3px';
    
    autoApplyTextureLabel.appendChild(autoApplyTexture);
    autoApplyTextureLabel.appendChild(document.createTextNode('Kumaş'));
    autoRow.appendChild(autoApplyTextureLabel);
    
    controlPanel.appendChild(autoRow);
    
    // Butonlar
    const buttonRow = document.createElement('div');
    buttonRow.className = 'button-row';
    buttonRow.style.display = 'flex';
    buttonRow.style.justifyContent = 'space-between';
    buttonRow.style.marginTop = '5px';
    
    // Model yükleme butonu
    const loadModelBtn = document.createElement('button');
    loadModelBtn.textContent = 'Model Yükle';
    loadModelBtn.disabled = true;
    loadModelBtn.style.cssText = `
        padding: 3px 8px;
        flex: 1;
        margin-right: 5px;
    `;
    
    loadModelBtn.addEventListener('click', function() {
        const modelPath = modelSelect.value;
        if (!modelPath) return;
        
        // Durum mesajını güncelle
        updateStatus('Model yükleniyor...');
        
        // Modeli yükle
        fabric3d.loadModel(modelPath)
            .then(() => {
                updateStatus('Model başarıyla yüklendi!');
            })
            .catch(error => {
                updateStatus(`Hata: ${error.message}`);
                console.error('Model yükleme hatası:', error);
            });
    });
    
    buttonRow.appendChild(loadModelBtn);
    
    // Kumaş uygulama butonu
    const applyTextureBtn = document.createElement('button');
    applyTextureBtn.textContent = 'Kumaş Uygula';
    applyTextureBtn.disabled = true;
    applyTextureBtn.style.cssText = `
        padding: 3px 8px;
        flex: 1;
    `;
    
    applyTextureBtn.addEventListener('click', function() {
        const texturePath = textureSelect.value;
        if (!texturePath) return;
        
        // Durum mesajını güncelle
        updateStatus('Kumaş uygulanıyor...');
        
        // Kumaşı uygula
        fabric3d.applyFabricTexture(texturePath)
            .then(() => {
                updateStatus('Kumaş başarıyla uygulandı!');
            })
            .catch(error => {
                updateStatus(`Hata: ${error.message}`);
                console.error('Kumaş uygulama hatası:', error);
            });
    });
    
    buttonRow.appendChild(applyTextureBtn);
    controlPanel.appendChild(buttonRow);
    
    // Durum mesajını güncellemek için yardımcı fonksiyon
    function updateStatus(message) {
        if (!statusDiv) return;
        statusDiv.innerHTML = message;
    }
    
    // Model yükleme butonu işlevini güncelle - artık ID ile yükleme yapacak
    loadModelBtn.addEventListener('click', function() {
        const modelPath = modelSelect.value;
        if (!modelPath) return;
        
        // Durum mesajını güncelle
        updateStatus('Model yükleniyor...');
        
        // Model ID'si ile yükleme yap
        // Not: Bu örnekte path yerine ID kullanmalısınız
        // Şimdilik basit tutmak için modelPath ile devam ediyoruz
        fabric3d.loadModel(modelPath)
            .then(() => {
                updateStatus('Model başarıyla yüklendi!');
            })
            .catch(error => {
                updateStatus(`Hata: ${error.message}`);
                console.error('Model yükleme hatası:', error);
            });
    });
    
    // Kontrol panelini konteynere ekle
    container.appendChild(controlPanel);
}
