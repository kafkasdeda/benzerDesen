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
    
    // Ortam hazır mesajı
    const statusDiv = document.createElement('div');
    statusDiv.className = 'fabric3d-status';
    statusDiv.innerHTML = 'Three.js ortamı hazır!<br>Model ve kumaş bekleniyor...';
    container.appendChild(statusDiv);
    
    // Kontrol panel oluştur
    createControlPanel(container, fabric3d);
    
    // Global erişim (test için)
    window.fabric3d = fabric3d;
});

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
    
    // Kontrol panelini konteynere ekle
    container.appendChild(controlPanel);
}
