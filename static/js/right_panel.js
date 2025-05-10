// right_panel.js
// Model ve versiyon seçim comboları eklendi

const rightPanel = document.getElementById("right-panel");

// Global değişkenler - varsayılan değerler
window.currentModel = window.currentModel || "pattern";
window.currentVersion = window.currentVersion || "v1";

// Panel başlatma fonksiyonu
function initRightPanel() {
  // Panel içeriğini temizle
  rightPanel.innerHTML = "";

  // Modeli Eğit butonu ekle
const trainButtonContainer = document.createElement("div");
trainButtonContainer.className = "train-button-container";
trainButtonContainer.style.padding = "10px";
trainButtonContainer.style.backgroundColor = "#f5f5f5";
trainButtonContainer.style.border = "1px solid #ddd";
trainButtonContainer.style.borderRadius = "5px";
trainButtonContainer.style.marginBottom = "15px";
trainButtonContainer.style.textAlign = "center";

const trainButton = document.createElement("button");
trainButton.textContent = "🧠 MODELİ EĞİT";
trainButton.style.padding = "10px 15px";
trainButton.style.backgroundColor = "#9c27b0";
trainButton.style.color = "white";
trainButton.style.border = "none";
trainButton.style.borderRadius = "4px";
trainButton.style.fontSize = "16px";
trainButton.style.cursor = "pointer";
trainButton.style.width = "100%";

trainButton.addEventListener("click", () => {
  // Eğitim arayüzünü göstermek için train_interface.js'deki fonksiyonu çağır
  showTrainingInterface(window.currentModel, window.currentVersion);
});

trainButtonContainer.appendChild(trainButton);
rightPanel.appendChild(trainButtonContainer);
  
  // Model ve Versiyon seçim alanını oluştur
  const selectionArea = document.createElement("div");
  selectionArea.className = "model-version-selector";
  selectionArea.style.padding = "10px";
  selectionArea.style.backgroundColor = "#f5f5f5";
  selectionArea.style.border = "1px solid #ddd";
  selectionArea.style.borderRadius = "5px";
  selectionArea.style.marginBottom = "15px";
  
  // Modeller için resimli kutucuk-combo
  const modelSelector = document.createElement("div");
  modelSelector.innerHTML = `
    <label><strong>🔍 Aktif Model:</strong></label>
    <div class="model-buttons" style="display: flex; gap: 10px; margin-top: 8px;">
      <button class="model-button" data-model="pattern" style="padding: 8px; border-radius: 4px; border: 2px solid #ddd; cursor: pointer; display: flex; flex-direction: column; align-items: center;">
        <span style="font-size: 24px;">🧩</span>
        <span>Desen</span>
      </button>
      <button class="model-button" data-model="color" style="padding: 8px; border-radius: 4px; border: 2px solid #ddd; cursor: pointer; display: flex; flex-direction: column; align-items: center;">
        <span style="font-size: 24px;">🎨</span>
        <span>Renk</span>
      </button>
      <button class="model-button" data-model="texture" style="padding: 8px; border-radius: 4px; border: 2px solid #ddd; cursor: pointer; display: flex; flex-direction: column; align-items: center;">
        <span style="font-size: 24px;">🧵</span>
        <span>Doku</span>
      </button>
      <button class="model-button" data-model="color+pattern" style="padding: 8px; border-radius: 4px; border: 2px solid #ddd; cursor: pointer; display: flex; flex-direction: column; align-items: center;">
        <span style="font-size: 24px;">✨</span>
        <span>Renk+Desen</span>
      </button>
    </div>
  `;
  
  // Versiyonlar için açılır menü
  const versionSelector = document.createElement("div");
  versionSelector.innerHTML = `
    <label style="display: block; margin-top: 15px;"><strong>📝 Aktif Versiyon:</strong></label>
    <select id="version-combo" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px;">
      <option value="v1">Versiyon 1</option>
    </select>
  `;
  
  // Ekrana ekle
  selectionArea.appendChild(modelSelector);
  selectionArea.appendChild(versionSelector);
  
  // Yeni Versiyon Oluştur butonu ekle
  const newVersionButton = document.createElement("button");
  newVersionButton.textContent = "🚀 Yeni Versiyon Oluştur";
  newVersionButton.style.width = "100%";
  newVersionButton.style.padding = "10px";
  newVersionButton.style.backgroundColor = "#3498db";
  newVersionButton.style.color = "white";
  newVersionButton.style.border = "none";
  newVersionButton.style.borderRadius = "4px";
  newVersionButton.style.marginTop = "15px";
  newVersionButton.style.cursor = "pointer";
  
  newVersionButton.onclick = showNewVersionModal;
  selectionArea.appendChild(newVersionButton);
  
  rightPanel.appendChild(selectionArea);
  
  // Mevcut model seçimini göster
  highlightCurrentModel();
  setCurrentVersion();
  
  // Orta paneldeki aktif model göstergesini güncelle
  if (document.getElementById("active-model-name")) {
    document.getElementById("active-model-name").textContent = window.currentModel;
  }
  if (document.getElementById("active-version-name")) {
    document.getElementById("active-version-name").textContent = window.currentVersion;
  }
  
  // Olay dinleyicileri ekle
  const modelButtons = document.querySelectorAll(".model-button");
  modelButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      window.currentModel = btn.dataset.model;
      highlightCurrentModel();
      loadAvailableVersions(window.currentModel);
      loadClusterRepresentatives(window.currentModel, window.currentVersion);
      
      // Orta paneldeki aktif model göstergesini güncelle
      if (document.getElementById("active-model-name")) {
        document.getElementById("active-model-name").textContent = window.currentModel;
      }
      
      // Orta panele model değişikliğini bildir (özel event)
      const event = new CustomEvent('modelChanged', {
        detail: {
          model: window.currentModel,
          source: 'rightPanel'
        }
      });
      document.dispatchEvent(event);
    });
  });
  
  document.getElementById("version-combo").addEventListener("change", (e) => {
    window.currentVersion = e.target.value;
    loadClusterRepresentatives(window.currentModel, window.currentVersion);
    
    // Orta paneldeki aktif versiyon göstergesini güncelle
    if (document.getElementById("active-version-name")) {
      document.getElementById("active-version-name").textContent = window.currentVersion;
    }
    
    // Orta panele versiyon değişikliğini bildir (oözel event)
    const event = new CustomEvent('versionChanged', {
      detail: {
        model: window.currentModel,
        version: window.currentVersion,
        source: 'rightPanel'
      }
    });
    document.dispatchEvent(event);
  });
  
  // Başlangıçta cluster'ları yükle
  loadAvailableVersions(window.currentModel);
  loadClusterRepresentatives(window.currentModel, window.currentVersion);
}

// Mevcut modeli vurgula
function highlightCurrentModel() {
  document.querySelectorAll(".model-button").forEach(btn => {
    if (btn.dataset.model === window.currentModel) {
      btn.style.borderColor = "#4CAF50";
      btn.style.backgroundColor = "#e8f5e9";
    } else {
      btn.style.borderColor = "#ddd";
      btn.style.backgroundColor = "";
    }
  });
}

// Mevcut versiyonu ayarla
function setCurrentVersion() {
  const versionCombo = document.getElementById("version-combo");
  if (versionCombo) {
    versionCombo.value = window.currentVersion;
  }
}

// Modele göre kullanılabilir versiyonları yükle
function loadAvailableVersions(model) {
  // Burada bir API çağrısı yapılabilir
  fetch(`/available-versions?model=${model}`)
    .then(res => res.json())
    .then(versions => {
      const versionCombo = document.getElementById("version-combo");
      versionCombo.innerHTML = "";
      
      versions.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v.id;
        opt.textContent = v.name;
        versionCombo.appendChild(opt);
      });
      
      // Eğer mevcut versiyon listede yoksa, ilk versiyonu seç
      if (!versions.some(v => v.id === window.currentVersion)) {
        window.currentVersion = versions[0]?.id || "v1";
      }
      
      setCurrentVersion();
    })
    .catch(err => {
      console.error("Versiyon listesi yüklenirken hata:", err);
      // Gerçek API olmadığında varsayılan versiyonları göster
      const versionCombo = document.getElementById("version-combo");
      versionCombo.innerHTML = `
        <option value="v1">Versiyon 1</option>
      `;
      setCurrentVersion();
    });
}

function loadClusterRepresentatives(model, version) {
  // Seçici alanının altına yükleniyor mesajı
  const existingContent = document.querySelector(".model-version-selector");
  if (existingContent && existingContent.nextSibling) {
    while (existingContent.nextSibling) {
      rightPanel.removeChild(existingContent.nextSibling);
    }
  }
  
  const loadingMsg = document.createElement("div");
  loadingMsg.innerHTML = "\u{1F50D} Cluster verisi yükleniyor...";
  rightPanel.appendChild(loadingMsg);

  // Yeni cluster verisi için API çağrısı yap
  fetch(`/clusters/${model}/${version}/data`)
    .then(res => {
      // Status kodu kontrol et
      if (!res.ok) {
        throw new Error(`Sunucu yanıtı hatalı: ${res.status} ${res.statusText}`);
      }
      return res.json();
    })
    .then(response => {
      // Veri format kontrolü
      if (!response.data || !response.data.clusters) {
        loadingMsg.innerHTML = "❌ Cluster verisi bulunamadı.";
        
        // Yeni cluster oluştur butonunu yine de göster
        const createButton = document.createElement("button");
        createButton.textContent = "➕ Seçilenlerle İlk Cluster'ı Oluştur";
        createButton.style.marginTop = "15px";
        createButton.style.padding = "10px";
        createButton.style.backgroundColor = "#4CAF50";
        createButton.style.color = "white";
        createButton.style.border = "none";
        createButton.style.borderRadius = "4px";
        createButton.style.width = "100%";
        createButton.style.cursor = "pointer";
        
        createButton.onclick = () => createNewCluster(model, version);
        rightPanel.appendChild(createButton);
        return;
      }
      
      const data = response.data;

      // Loading mesajını temizle
      if (loadingMsg.parentNode === rightPanel) {
        rightPanel.removeChild(loadingMsg);
      }

      // Versiyon yorumu
      const versionHeader = document.createElement("div");
      versionHeader.innerHTML = `
        <h3>${model} - ${version}</h3>
        <p><strong>Versiyon Yorumu:</strong> <span id="version-comment-text">${data.comment || "(Yorum yok)"}</span>
        <button id="edit-comment-btn">🖊️</button></p>
        <div id="comment-edit-box" style="display:none; margin-top:8px;">
          <textarea id="version-comment-input" rows="3" style="width:100%;"></textarea>
          <button id="save-comment-btn">Kaydet</button>
          <button id="cancel-comment-btn">İptal</button>
        </div>
      `;
      rightPanel.appendChild(versionHeader);

      document.getElementById("edit-comment-btn").addEventListener("click", () => {
        document.getElementById("version-comment-input").value = data.comment || "";
        document.getElementById("comment-edit-box").style.display = "block";
      });

      document.getElementById("cancel-comment-btn").addEventListener("click", () => {
        document.getElementById("comment-edit-box").style.display = "none";
      });

      document.getElementById("save-comment-btn").addEventListener("click", () => {
        const newComment = document.getElementById("version-comment-input").value.trim();
        fetch("/update-version-comment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ model, version, version_comment: newComment })
        })
        .then(res => res.json())
        .then(result => {
          if (result.status === "ok") {
            document.getElementById("version-comment-text").textContent = newComment;
            document.getElementById("comment-edit-box").style.display = "none";
          } else {
            alert("❌ Güncellenemedi: " + result.message);
          }
        });
      });

      // Cluster sayısı ve istatistik ekle
      const statsBox = document.createElement("div");
      statsBox.style.backgroundColor = "#f9f9f9";
      statsBox.style.padding = "10px";
      statsBox.style.borderRadius = "5px";
      statsBox.style.marginBottom = "15px";

      // Cluster sayısını ve istatistiklerini bul
      const clusters = data.clusters || {};
      const uniqueClusters = Object.keys(clusters).length;
      
      // Görsel sayısını bul (tüm cluster'lardaki görselleri topla)
      let totalImages = 0;
      Object.values(clusters).forEach(cluster => {
        if (cluster.images && Array.isArray(cluster.images)) {
          totalImages += cluster.images.length;
        }
      });
      
      statsBox.innerHTML = `
        <div style="display: flex; justify-content: space-between;">
          <div>
            <strong>Toplam Cluster:</strong> ${uniqueClusters}
          </div>
          <div>
            <strong>Toplam Görsel:</strong> ${totalImages}
          </div>
        </div>
      `;
      rightPanel.appendChild(statsBox);

      const container = document.createElement("div");
      container.className = "image-grid";

      // Cluster'ları göster
      Object.entries(clusters).forEach(([clusterName, clusterData]) => {
        const box = document.createElement("div");
        box.className = "cluster-box";
        
        // Temsil eden görsel
        const filename = clusterData.representative;
        
        // Cluster içindeki görsel sayısını hesapla
        const clusterImages = clusterData.images || [];
        
        const img = document.createElement("img");
        img.src = `thumbnails/${filename}`;
        img.alt = filename;
        img.loading = "lazy";

        box.appendChild(img);
        
        // Tooltip için hover olayı
        box.addEventListener('mouseenter', function(event) {
            console.log("DEBUG: Sağ panel - Kafkas diyor ki: Sağ panelde bir görsele geldin, elimle koyduğum gibi!");
            // Button hover'ları için tooltip'i atla
            if (event.target.closest('.move-button')) {
              console.log("DEBUG: Sağ panel - Kafkas diyor ki: Bu bir buton, elini sürunce tooltip olmaz!");
              return;
            }
            
            // Önce varsa eski tooltip'leri temizle
            if (this._currentTooltip) {
                console.log("DEBUG: Sağ panel - Kafkas diyor ki: Eski tooltip'i temizliyorum, elimin hakkıyla!");
                this._currentTooltip.remove();
                this._currentTooltip = null;
            }
            
            const tooltip = document.createElement("div");
            tooltip.className = "tooltip";
            tooltip.style.position = "fixed";
            tooltip.style.backgroundColor = "#fff";
            tooltip.style.border = "2px solid red"; // Debug amaçlı kırmızı çerçeve
            tooltip.style.padding = "8px";
            tooltip.style.zIndex = "9999";
            tooltip.style.width = "300px";
            tooltip.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
            tooltip.style.borderRadius = "4px";
            tooltip.style.display = 'block';
            tooltip.style.visibility = 'visible';
            tooltip.style.pointerEvents = 'none';
            
            tooltip.innerHTML = `
              <img src='thumbnails/${filename}' style="width: 300px; max-height: 300px; object-fit: contain;" />
              <strong>${clusterName}</strong><br>
              Bu cluster'da ${clusterImages.length} görsel var
            `;
            
            // Tooltip'i document.body'e ekleyelim
            document.body.appendChild(tooltip);
            console.log("DEBUG: Sağ panel - Kafkas diyor ki: Tooltip yaptım, elinizden kaydı gitti!");
            
            // Tooltip konumunu görsel kutusuna göre ayarla
            const boxRect = this.getBoundingClientRect();
            tooltip.style.top = boxRect.top + "px";
            tooltip.style.left = (boxRect.left - 310) + "px"; // Sağ panelde sol tarafta göster
            console.log("DEBUG: Sağ panel - Kafkas diyor ki: Görsel kutusunun pozisyonu:", boxRect);
            console.log("DEBUG: Sağ panel - Kafkas diyor ki: Tooltip yerini ayarladım, elin kaymasın!", tooltip.style.top, tooltip.style.left);
            
            // Viewport sınırlarını kontrol et ve gerekirse konumu ayarla
            setTimeout(() => {
              const rect = tooltip.getBoundingClientRect();
              console.log("DEBUG: Sağ panel - Kafkas diyor ki: Tooltip'in boyutları ne?", rect);
              if (rect.left < 0) {
                tooltip.style.left = (boxRect.right + 10) + "px";
                console.log("DEBUG: Sağ panel - Kafkas diyor ki: Sola sığmadı, sağa kaydırdım elimiçabuk!");
              }
              if (rect.bottom > window.innerHeight) {
                tooltip.style.top = (window.innerHeight - rect.height - 10) + "px";
                console.log("DEBUG: Sağ panel - Kafkas diyor ki: Aşağıya taşıyordu, yukarı çektim elimden geldiğince!");
              }
            }, 0);
            
            // Tooltip'i mouseleave olayında kaldırmak için kaydedelim
            this._currentTooltip = tooltip;
        });
        
        // Tooltip'i mouseleave olayında kaldırmak için
        box.addEventListener('mouseleave', function() {
            console.log("DEBUG: Sağ panel - Kafkas diyor ki: Mouse kaçtı, elim sana kurban olsun!");
            if (this._currentTooltip) {
                console.log("DEBUG: Sağ panel - Kafkas diyor ki: Tooltip'i süpirdim, türel temizlik yapayım!");
                this._currentTooltip.remove();
                this._currentTooltip = null;
            }
        });
        
        // Cluster adını göster
        const nameLabel = document.createElement("div");
        nameLabel.textContent = `${clusterName} (${clusterImages.length})`;
        nameLabel.style.marginTop = "5px";
        nameLabel.style.fontSize = "14px";
        nameLabel.style.textAlign = "center";
        box.appendChild(nameLabel);
        
        const moveButton = document.createElement("button");
        moveButton.textContent = "Seçilenleri Taşı";
        moveButton.className = "move-button";
        moveButton.style.marginTop = "6px";
        moveButton.style.display = "block";
        moveButton.style.width = "100%";

        moveButton.onclick = () => {
          const selected = window.selectedImages || [];
          if (!selected.length) {
            alert("Lütfen önce orta panelden görsel(ler) seçin.");
            return;
          }

          fetch("/move-to-cluster", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              model: model,  // Model parametresi eklendi
              version: version,  // Versiyon parametresi eklendi
              cluster: clusterName,
              images: selected
            })
          })
          .then(res => res.json())
          .then(result => {
            if (result.status === "ok") {
              console.log("✅ Taşıma başarılı:", result);
              alert(`Seçilen görseller '${clusterName}' cluster'a taşındı.`);
              
              // Seçimleri temizle
              window.selectedImages.clear();
              document.querySelectorAll("#center-results .image-box input[type='checkbox']").forEach(cb => {
                cb.checked = false;
              });
              document.querySelectorAll("#center-results .image-box").forEach(box => {
                box.classList.remove('selected');
              });
              
              // Sayfayı yenile
              loadClusterRepresentatives(model, version);
            } else {
              alert("❌ Hata: " + result.message);
            }
          })
          .catch(err => {
            console.error("🚫 Taşıma hatası:", err);
            alert("Bir hata oluştu.");
          });
        };

        box.appendChild(moveButton);
        container.appendChild(box);
      });

      rightPanel.appendChild(container);

      // ✅ Yeni Cluster Oluştur Butonu
      const createButton = document.createElement("button");
      createButton.textContent = "➕ Seçilenlerle Yeni Cluster Oluştur";
      createButton.style.marginTop = "15px";
      createButton.style.padding = "10px";
      createButton.style.backgroundColor = "#4CAF50";
      createButton.style.color = "white";
      createButton.style.border = "none";
      createButton.style.borderRadius = "4px";
      createButton.style.width = "100%";
      createButton.style.cursor = "pointer";
      
      createButton.onclick = () => createNewCluster(model, version);

      rightPanel.appendChild(createButton);
    })
    .catch(err => {
      console.error("Yükleme hatası:", err);
      loadingMsg.innerHTML = `❌ Cluster verisi yüklenemedi. <br><small>${err.message}</small>`;
      
      // Hata durumunda boş representatives.json oluştur butonunu göster
      const initButton = document.createElement("button");
      initButton.textContent = "🚀 Bu Model & Versiyon İçin Hazırlık Yap";
      initButton.style.marginTop = "15px";
      initButton.style.padding = "10px";
      initButton.style.backgroundColor = "#3498db";
      initButton.style.color = "white";
      initButton.style.border = "none";
      initButton.style.borderRadius = "4px";
      initButton.style.width = "100%";
      initButton.style.cursor = "pointer";
      
      initButton.onclick = () => initModelVersion(model, version);
      rightPanel.appendChild(initButton);
      
      // Yeni cluster oluştur butonunu da ekle
      const createButton = document.createElement("button");
      createButton.textContent = "➕ Seçilenlerle İlk Cluster'ı Oluştur";
      createButton.style.marginTop = "15px";
      createButton.style.padding = "10px";
      createButton.style.backgroundColor = "#4CAF50";
      createButton.style.color = "white";
      createButton.style.border = "none";
      createButton.style.borderRadius = "4px";
      createButton.style.width = "100%";
      createButton.style.cursor = "pointer";
      
      createButton.onclick = () => createNewCluster(model, version);
      rightPanel.appendChild(createButton);
    });
}

// Yeni versiyon modalını göster
function showNewVersionModal() {
  // Önce eski modal varsa kaldır
  const oldModal = document.getElementById("new-version-modal");
  if (oldModal) document.body.removeChild(oldModal);
  
  // Seçili model tipini al
  const selectedModel = window.currentModel;
  console.log("Seçili model:", selectedModel);
  
  // Yeni modal oluştur
  const modal = document.createElement("div");
  modal.id = "new-version-modal";
  modal.style.position = "fixed";
  modal.style.top = "0";
  modal.style.left = "0";
  modal.style.width = "100%";
  modal.style.height = "100%";
  modal.style.backgroundColor = "rgba(0,0,0,0.5)";
  modal.style.display = "flex";
  modal.style.justifyContent = "center";
  modal.style.alignItems = "center";
  modal.style.zIndex = "1000";
  
  // Modal içeriği
  const content = document.createElement("div");
  content.style.backgroundColor = "white";
  content.style.padding = "20px";
  content.style.borderRadius = "5px";
  content.style.maxWidth = "500px";
  content.style.width = "90%";
  
  // Başlık
  const title = document.createElement("h2");
  title.textContent = `Yeni ${selectedModel} Versiyonu Oluştur`;
  content.appendChild(title);
  
  // Eğer seçilen model "color" ise farklı form göster
  if (selectedModel === "color") {
    console.log("Renk modeli için özel form gösteriliyor...");
    // Renk modeli için özel form
    content.innerHTML += `
      <div class="color-model-params">
        <p>Renk modeli için kümeleme yerine HSV renk uzayında spektrum organizasyonu kullanılacak.</p>
        
        <div class="form-group">
          <label for="version-name">Versiyon Adı:</label>
          <input type="text" id="version-name" value="v1" class="form-control" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
        </div>
        
        <div class="form-group">
          <label for="divisions" title="Renk çemberindeki bölüm sayısı. Daha yüksek değer daha detaylı ton ayrımı sağlar.">
            Ton (Hue) Bölümleri:
          </label>
          <select id="divisions" class="form-control" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
            <option value="6">6 bölüm (60° aralıklar)</option>
            <option value="12" selected>12 bölüm (30° aralıklar)</option>
            <option value="18">18 bölüm (20° aralıklar)</option>
            <option value="24">24 bölüm (15° aralıklar)</option>
            <option value="36">36 bölüm (10° aralıklar)</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="saturation-levels" title="Doygunluk seviyelerinin sayısı. Daha yüksek değer daha detaylı doygunluk ayrımı sağlar.">
            Doygunluk (Saturation) Seviyeleri:
          </label>
          <select id="saturation-levels" class="form-control" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
            <option value="2">2 seviye (Düşük, Yüksek)</option>
            <option value="3" selected>3 seviye (Düşük, Orta, Yüksek)</option>
            <option value="4">4 seviye (Çok detaylı)</option>
            <option value="5">5 seviye (En detaylı)</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="value-levels" title="Parlaklık seviyelerinin sayısı. Daha yüksek değer daha detaylı parlaklık ayrımı sağlar.">
            Parlaklık (Value) Seviyeleri:
          </label>
          <select id="value-levels" class="form-control" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
            <option value="2">2 seviye (Koyu, Açık)</option>
            <option value="3" selected>3 seviye (Koyu, Orta, Açık)</option>
            <option value="4">4 seviye (Çok detaylı)</option>
            <option value="5">5 seviye (En detaylı)</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="dominant-color-method" title="Görselden dominant renk çıkarma yöntemi. Histogram daha hızlı, K-means daha doğru sonuç verir.">
            Dominant Renk Metodu:
          </label>
          <select id="dominant-color-method" class="form-control" style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
            <option value="histogram" selected>Histogram (Hızlı)</option>
            <option value="kmeans">K-Means (Doğru)</option>
            <option value="average">Ortalama (En hızlı)</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="color-wheel-container" title="Renk çarkı üzerinden renk seçebilirsiniz.">Renk Çarkı:</label>
          <div id="color-wheel-container" style="display: flex; justify-content: center; margin-top: 15px; margin-bottom: 15px;">
            <div class="color-wheel" style="position: relative; width: 200px; height: 200px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 8px rgba(0,0,0,0.2);">
              <!-- Renk çarkı bölümleri -->
              <div class="color-section" data-hue="0" style="position: absolute; width: 50%; height: 50%; background: #f00; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(0deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="30" style="position: absolute; width: 50%; height: 50%; background: #ff8000; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(30deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="60" style="position: absolute; width: 50%; height: 50%; background: #ff0; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(60deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="90" style="position: absolute; width: 50%; height: 50%; background: #80ff00; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(90deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="120" style="position: absolute; width: 50%; height: 50%; background: #0f0; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(120deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="150" style="position: absolute; width: 50%; height: 50%; background: #00ff80; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(150deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="180" style="position: absolute; width: 50%; height: 50%; background: #0ff; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(180deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="210" style="position: absolute; width: 50%; height: 50%; background: #0080ff; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(210deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="240" style="position: absolute; width: 50%; height: 50%; background: #00f; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(240deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="270" style="position: absolute; width: 50%; height: 50%; background: #8000ff; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(270deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="300" style="position: absolute; width: 50%; height: 50%; background: #f0f; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(300deg) skewY(60deg);"></div>
              <div class="color-section" data-hue="330" style="position: absolute; width: 50%; height: 50%; background: #ff0080; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(330deg) skewY(60deg);"></div>
              <!-- Orta beyaz daire -->
              <div class="center-circle" style="position: absolute; width: 40px; height: 40px; background: white; border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 5px rgba(0,0,0,0.2); border: 1px solid #ddd;"></div>
              <!-- Marker (seçilen rengi gösterecek) -->
              <div id="color-marker" style="position: absolute; width: 12px; height: 12px; background: black; border-radius: 50%; top: 30px; left: 100px; transform: translate(-50%, -50%); box-shadow: 0 0 5px rgba(0,0,0,0.5); display: none;"></div>
            </div>
          </div>
          <div id="selected-hue-info" style="text-align: center; margin-bottom: 10px;">Seçilen Ton (Hue): Yok</div>
        </div>

        <div class="form-group">
          <label for="color-group-filter" title="Belirli renk gruplarını filtreleme veya vurgulama için kullanılır.">Renk Grubu Hızlı Seçim:</label>
          <div id="color-group-buttons" style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px;">
            <button type="button" class="color-group-btn" data-color="red" style="width: 30px; height: 30px; background-color: #e74c3c; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="orange" style="width: 30px; height: 30px; background-color: #e67e22; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="yellow" style="width: 30px; height: 30px; background-color: #f1c40f; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="green" style="width: 30px; height: 30px; background-color: #2ecc71; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="blue" style="width: 30px; height: 30px; background-color: #3498db; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="purple" style="width: 30px; height: 30px; background-color: #9b59b6; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="pink" style="width: 30px; height: 30px; background-color: #fd79a8; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="brown" style="width: 30px; height: 30px; background-color: #795548; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="gray" style="width: 30px; height: 30px; background-color: #95a5a6; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="black" style="width: 30px; height: 30px; background-color: #34495e; border: 2px solid #ddd; border-radius: 4px;"></button>
            <button type="button" class="color-group-btn" data-color="white" style="width: 30px; height: 30px; background-color: #ecf0f1; border: 2px solid #ddd; border-radius: 4px;"></button>
          </div>
          <div id="selected-color-info" style="margin-top: 8px; font-size: 14px;">Seçilen Renk: Yok</div>
        </div>

        <div class="form-group">
          <label for="version-comment">Açıklama (opsiyonel):</label>
          <input type="text" id="version-comment" class="form-control" placeholder="Bu versiyon hakkında bir açıklama..." style="width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
        </div>
      </div>
    `;
  } else {
    // Diğer modeller için standart form
    content.innerHTML += `
      <div style="margin-bottom: 15px;">
        <label style="display: block; margin-bottom: 5px;"><strong>Algoritma:</strong></label>
        <select id="algorithm-select" style="width: 100%; padding: 8px; border-radius: 4px;">
          <option value="kmeans">K-Means</option>
          <option value="dbscan">DBSCAN</option>
          <option value="hierarchical">Hierarchical</option>
        </select>
      </div>
      
      <!-- Algoritma-özel parametreler -->
      <div id="algorithm-params">
        <!-- K-Means için -->
        <div id="kmeans-params" class="algo-params">
          <label style="display: block; margin-bottom: 5px;">
            <strong>k - Cluster Sayısı:</strong> <span id="k-value">5</span>
          </label>
          <input type="range" id="k-slider" min="2" max="100" value="5" style="width: 100%;">
        </div>
        
        <!-- DBSCAN için (başlangıçta gizli) -->
        <div id="dbscan-params" class="algo-params" style="display: none;">
          <label style="display: block; margin-bottom: 5px;">
            <strong>eps - Threshold:</strong> <span id="eps-value">0.5</span>
          </label>
          <input type="range" id="eps-slider" min="0.1" max="2" step="0.1" value="0.5" style="width: 100%;">
          
          <label style="display: block; margin-top: 10px; margin-bottom: 5px;">
            <strong>min_samples:</strong> <span id="min-samples-value">5</span>
          </label>
          <input type="range" id="min-samples-slider" min="2" max="15" value="5" style="width: 100%;">
        </div>
        
        <!-- Hierarchical için (başlangıçta gizli) -->
        <div id="hierarchical-params" class="algo-params" style="display: none;">
          <label style="display: block; margin-bottom: 5px;">
            <strong>Linkage Type:</strong>
          </label>
          <select id="linkage-select" style="width: 100%; padding: 8px; border-radius: 4px;">
            <option value="ward">Ward (varsayılan)</option>
            <option value="complete">Complete</option>
            <option value="average">Average</option>
            <option value="single">Single</option>
          </select>
          
          <label style="display: block; margin-top: 10px; margin-bottom: 5px;">
            <strong>Cluster Sayısı:</strong> <span id="h-k-value">5</span>
          </label>
          <input type="range" id="h-k-slider" min="2" max="20" value="5" style="width: 100%;">
        </div>
      </div>
      
      <!-- Versiyon Açıklaması -->
      <div style="margin-top: 15px;">
        <label style="display: block; margin-bottom: 5px;"><strong>Versiyon Açıklaması:</strong></label>
        <textarea id="version-comment" style="width: 100%; padding: 8px; border-radius: 4px; height: 80px;" 
          placeholder="Bu versiyonun özelliklerini yazın..."></textarea>
      </div>
    `;
  }
  
  // Butonlar
  const buttonContainer = document.createElement("div");
  buttonContainer.style.marginTop = "20px";
  buttonContainer.style.display = "flex";
  buttonContainer.style.justifyContent = "space-between";
  
  const cancelBtn = document.createElement("button");
  cancelBtn.id = "cancel-version";
  cancelBtn.textContent = "İptal";
  cancelBtn.style.padding = "10px 15px";
  cancelBtn.style.backgroundColor = "#ccc";
  cancelBtn.style.border = "none";
  cancelBtn.style.borderRadius = "4px";
  cancelBtn.style.cursor = "pointer";
  
  const createBtn = document.createElement("button");
  createBtn.id = "create-version";
  createBtn.textContent = "Oluştur";
  createBtn.style.padding = "10px 15px";
  createBtn.style.backgroundColor = "#4CAF50";
  createBtn.style.color = "white";
  createBtn.style.border = "none";
  createBtn.style.borderRadius = "4px";
  createBtn.style.cursor = "pointer";
  
  buttonContainer.appendChild(cancelBtn);
  buttonContainer.appendChild(createBtn);
  content.appendChild(buttonContainer);
  
  modal.appendChild(content);
  document.body.appendChild(modal);
  
  // Event listeners
  if (selectedModel !== "color") {
    // Sadece diğer modeller için algoritma seçim olayları ekle
    document.getElementById("algorithm-select").addEventListener("change", updateAlgorithmParams);
    document.getElementById("k-slider").addEventListener("input", e => {
      document.getElementById("k-value").textContent = e.target.value;
    });
    document.getElementById("eps-slider").addEventListener("input", e => {
      document.getElementById("eps-value").textContent = e.target.value;
    });
    document.getElementById("min-samples-slider").addEventListener("input", e => {
      document.getElementById("min-samples-value").textContent = e.target.value;
    });
    document.getElementById("h-k-slider").addEventListener("input", e => {
      document.getElementById("h-k-value").textContent = e.target.value;
    });
    
    // İlk görünümü ayarla
    updateAlgorithmParams();
  } else {
    // Renk çarkı etkileşimini ekle
    const colorWheel = document.querySelector('.color-wheel');
    const colorMarker = document.getElementById('color-marker');
    
    if (colorWheel) {
      // Renk çarkı bölümlerine tıklama olayı ekle
      const colorSections = colorWheel.querySelectorAll('.color-section');
      colorSections.forEach(section => {
        section.addEventListener('click', function(e) {
          // Tıklanan konumu al
          const rect = colorWheel.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          
          // Merkeze göre konumu hesapla
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          const dx = x - centerX;
          const dy = y - centerY;
          
          // Merkeze olan uzaklık (radius içinde olup olmadığını kontrol etmek için)
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          // Eğer orta dairede tıkladıysa işlem yapma
          if (distance < 20) return;
          
          // Ton (Hue) değerini hesapla (0-360 derece)
          const angle = Math.atan2(dy, dx) * 180 / Math.PI;
          const hue = (angle + 90) % 360; // +90 döndürüyor renk çemberi için
          
          // Marker'i göster ve konumlandır
          colorMarker.style.display = 'block';
          colorMarker.style.left = x + 'px';
          colorMarker.style.top = y + 'px';
          
          // Seçilen Ton bilgisini güncelle
          document.getElementById('selected-hue-info').textContent = `Seçilen Ton (Hue): ${Math.round(hue)}°`;
          
          // Seçilen tonu form parametrelerine ekle
          let hueInput = document.getElementById('hue-filter-value');
          if (!hueInput) {
            hueInput = document.createElement('input');
            hueInput.type = 'hidden';
            hueInput.id = 'hue-filter-value';
            document.querySelector('.color-model-params').appendChild(hueInput);
          }
          hueInput.value = Math.round(hue);
          
          // Seçilen ton ile uyumlu renk butonunu da vurgula
          if (hue >= 330 || hue < 30) highlightColorButton('red');
          else if (hue >= 30 && hue < 60) highlightColorButton('orange');
          else if (hue >= 60 && hue < 90) highlightColorButton('yellow');
          else if (hue >= 90 && hue < 150) highlightColorButton('green');
          else if (hue >= 150 && hue < 210) highlightColorButton('blue');
          else if (hue >= 210 && hue < 270) highlightColorButton('blue');
          else if (hue >= 270 && hue < 330) highlightColorButton('purple');
        });
      });
    }
    
    // Renk butonlarına tıklama olaylarını ekle
    const colorButtons = document.querySelectorAll('.color-group-btn');
    colorButtons.forEach(btn => {
      btn.addEventListener('click', function() {
        // Tüm butonların seçim durumunu temizle
        colorButtons.forEach(b => {
          b.style.borderColor = '#ddd';
          b.style.borderWidth = '2px';
        });
        
        // Bu butonu seçili olarak işaretle
        this.style.borderColor = '#3498db';
        this.style.borderWidth = '3px';
        
        // Seçilen renk bilgisini güncelle
        const colorName = this.dataset.color;
        document.getElementById('selected-color-info').textContent = `Seçilen Renk: ${colorName.charAt(0).toUpperCase() + colorName.slice(1)}`;
        
        // Renk grubunu form parametrelerine ekle için hidden input güncelle veya ekle
        let colorFilterInput = document.getElementById('color-filter-value');
        if (!colorFilterInput) {
          colorFilterInput = document.createElement('input');
          colorFilterInput.type = 'hidden';
          colorFilterInput.id = 'color-filter-value';
          document.querySelector('.color-model-params').appendChild(colorFilterInput);
        }
        colorFilterInput.value = colorName;
      });
    });
  }
  
  // Renk butonunu vurgulama yardımcı fonksiyonu
  function highlightColorButton(colorName) {
    const colorButtons = document.querySelectorAll('.color-group-btn');
    colorButtons.forEach(btn => {
      if (btn.dataset.color === colorName) {
        btn.style.borderColor = '#3498db';
        btn.style.borderWidth = '3px';
      } else {
        btn.style.borderColor = '#ddd';
        btn.style.borderWidth = '2px';
      }
    });
  }
  
  document.getElementById("cancel-version").addEventListener("click", () => {
    document.body.removeChild(modal);
  });
  
  document.getElementById("create-version").addEventListener("click", () => {
    const versionName = document.getElementById("version-name").value;
    const versionComment = document.getElementById("version-comment").value;
    
    let clusterParams = {};
    
    if (selectedModel === "color") {
      // Renk modeli için spektrum parametreleri
      const divisions = parseInt(document.getElementById("divisions").value);
      const saturationLevels = parseInt(document.getElementById("saturation-levels").value);
      const valueLevels = parseInt(document.getElementById("value-levels").value);
      const dominantColorMethod = document.getElementById("dominant-color-method").value;
      
      // Seçilen renk grubu filtresi (varsa)
      const colorFilter = document.getElementById('color-filter-value')?.value;
      
      clusterParams = {
        model_type: selectedModel,
        version: versionName,
        algorithm: "color_spectrum",
        divisions: divisions,
        saturation_levels: saturationLevels,
        value_levels: valueLevels,
        dominant_color_method: dominantColorMethod
      };
      
      // Renk filtresi varsa ekle
      if (colorFilter) {
        clusterParams.color_filter = colorFilter;
      }
      
      // Ton (Hue) değeri seçilmişse ekle
      const hueValue = document.getElementById('hue-filter-value')?.value;
      if (hueValue) {
        clusterParams.hue_filter = parseInt(hueValue);
      }
    } else {
      // Diğer modeller için kümeleme parametreleri
      const algorithm = document.getElementById("algorithm-select").value;
      
      clusterParams = {
        model_type: selectedModel,
        version: versionName,
        algorithm: algorithm
      };
      
      if (algorithm === "kmeans") {
        clusterParams.k = parseInt(document.getElementById("k-slider").value);
      } else if (algorithm === "dbscan") {
        clusterParams.eps = parseFloat(document.getElementById("eps-slider").value);
        clusterParams.min_samples = parseInt(document.getElementById("min-samples-slider").value);
      } else if (algorithm === "hierarchical") {
        clusterParams.distance_threshold = parseFloat(document.getElementById("linkage-select").value);
        clusterParams.linkage = document.getElementById("linkage-select").value;
      }
    }
    
    if (versionComment) {
      clusterParams.comment = versionComment;
    }
    
    // API'ye istek gönder
    createClusterVersion(clusterParams);
    
    // Modal kapat
    document.body.removeChild(modal);
  });
}

// Seçilen algoritmaya göre parametre alanını güncelle
function updateAlgorithmParams() {
  const algorithm = document.getElementById("algorithm-select").value;
  
  document.querySelectorAll(".algo-params").forEach(elem => {
    elem.style.display = "none";
  });
  
  document.getElementById(`${algorithm}-params`).style.display = "block";
}

// Yeni versiyon oluştur
function createNewVersion() {
  // Mevcut seçili model ve algoritma bilgilerini al
  const selectedModel = window.currentModel;
  const selectedAlgorithm = document.getElementById("algorithm-select").value;
  
  // Modal içeriğini oluştur
  const modalContent = document.createElement("div");
  modalContent.className = "modal-content";
  
  // Başlık ve açıklama
  const header = document.createElement("div");
  header.className = "modal-header";
  header.innerHTML = `
      <h2>Yeni Versiyon Oluştur</h2>
      <p>Seçilen model tipi: <strong>${selectedModel}</strong></p>
  `;
  modalContent.appendChild(header);
  
  // Form alanları
  const form = document.createElement("div");
  form.className = "modal-form";
  
  // Farklı model tipleri için farklı içerik göster
  if (selectedModel === "color") {
      // Renk modeli için özel form
      form.innerHTML = `
          <div class="color-model-params">
              <h3>Renk Spektrumu Parametreleri</h3>
              <p>Renk modeli için kümeleme yerine HSV renk uzayında spektrum organizasyonu kullanılacak.</p>
              
              <div class="form-group">
                  <label for="version-name">Versiyon Adı:</label>
                  <input type="text" id="version-name" value="v1" class="form-control">
              </div>
              
              <div class="form-group">
                  <label for="divisions" title="Renk çemberindeki bölüm sayısı. Daha yüksek değer daha detaylı ton ayrımı sağlar.">
                      Ton (Hue) Bölümleri:
                      <i class="fas fa-info-circle"></i>
                  </label>
                  <select id="divisions" class="form-control">
                      <option value="6">6 bölüm (60° aralıklar)</option>
                      <option value="12" selected>12 bölüm (30° aralıklar)</option>
                      <option value="18">18 bölüm (20° aralıklar)</option>
                      <option value="24">24 bölüm (15° aralıklar)</option>
                      <option value="36">36 bölüm (10° aralıklar)</option>
                  </select>
              </div>
              
              <div class="form-group">
                  <label for="saturation-levels" title="Doygunluk seviyelerinin sayısı. Daha yüksek değer daha detaylı doygunluk ayrımı sağlar.">
                      Doygunluk (Saturation) Seviyeleri:
                      <i class="fas fa-info-circle"></i>
                  </label>
                  <select id="saturation-levels" class="form-control">
                      <option value="2">2 seviye (Düşük, Yüksek)</option>
                      <option value="3" selected>3 seviye (Düşük, Orta, Yüksek)</option>
                      <option value="4">4 seviye (Çok detaylı)</option>
                      <option value="5">5 seviye (En detaylı)</option>
                  </select>
              </div>
              
              <div class="form-group">
                  <label for="value-levels" title="Parlaklık seviyelerinin sayısı. Daha yüksek değer daha detaylı parlaklık ayrımı sağlar.">
                      Parlaklık (Value) Seviyeleri:
                      <i class="fas fa-info-circle"></i>
                  </label>
                  <select id="value-levels" class="form-control">
                      <option value="2">2 seviye (Koyu, Açık)</option>
                      <option value="3" selected>3 seviye (Koyu, Orta, Açık)</option>
                      <option value="4">4 seviye (Çok detaylı)</option>
                      <option value="5">5 seviye (En detaylı)</option>
                  </select>
              </div>
              
              <div class="form-group">
                  <label for="dominant-color-method" title="Görselden dominant renk çıkarma yöntemi. Histogram daha hızlı, K-means daha doğru sonuç verir.">
                      Dominant Renk Metodu:
                      <i class="fas fa-info-circle"></i>
                  </label>
                  <select id="dominant-color-method" class="form-control">
                      <option value="histogram" selected>Histogram (Hızlı)</option>
                      <option value="kmeans">K-Means (Doğru)</option>
                      <option value="average">Ortalama (En hızlı)</option>
                  </select>
              </div>
              
              <div class="form-group">
                  <label for="color-wheel-container" title="Renk çarkı üzerinden renk seçebilirsiniz.">Renk Çarkı:</label>
                  <div id="color-wheel-container" style="display: flex; justify-content: center; margin-top: 15px; margin-bottom: 15px;">
                      <div class="color-wheel" style="position: relative; width: 200px; height: 200px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 8px rgba(0,0,0,0.2);">
                          <!-- Renk çarkı bölümleri -->
                          <div class="color-section" data-hue="0" style="position: absolute; width: 50%; height: 50%; background: #f00; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(0deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="30" style="position: absolute; width: 50%; height: 50%; background: #ff8000; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(30deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="60" style="position: absolute; width: 50%; height: 50%; background: #ff0; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(60deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="90" style="position: absolute; width: 50%; height: 50%; background: #80ff00; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(90deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="120" style="position: absolute; width: 50%; height: 50%; background: #0f0; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(120deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="150" style="position: absolute; width: 50%; height: 50%; background: #00ff80; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(150deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="180" style="position: absolute; width: 50%; height: 50%; background: #0ff; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(180deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="210" style="position: absolute; width: 50%; height: 50%; background: #0080ff; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(210deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="240" style="position: absolute; width: 50%; height: 50%; background: #00f; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(240deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="270" style="position: absolute; width: 50%; height: 50%; background: #8000ff; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(270deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="300" style="position: absolute; width: 50%; height: 50%; background: #f0f; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(300deg) skewY(60deg);"></div>
                          <div class="color-section" data-hue="330" style="position: absolute; width: 50%; height: 50%; background: #ff0080; left: 50%; top: 0; transform-origin: bottom left; transform: rotate(330deg) skewY(60deg);"></div>
                          <!-- Orta beyaz daire -->
                          <div class="center-circle" style="position: absolute; width: 40px; height: 40px; background: white; border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 5px rgba(0,0,0,0.2); border: 1px solid #ddd;"></div>
                          <!-- Marker (seçilen rengi gösterecek) -->
                          <div id="color-marker" style="position: absolute; width: 12px; height: 12px; background: black; border-radius: 50%; top: 30px; left: 100px; transform: translate(-50%, -50%); box-shadow: 0 0 5px rgba(0,0,0,0.5); display: none;"></div>
                      </div>
                  </div>
                  <div id="selected-hue-info" style="text-align: center; margin-bottom: 10px;">Seçilen Ton (Hue): Yok</div>
              </div>

              <div class="form-group">
                  <label for="color-group-filter" title="Belirli renk gruplarını filtreleme veya vurgulama için kullanılır.">Renk Grubu Hızlı Seçim:</label>
                  <div id="color-group-buttons" style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px;">
                      <button type="button" class="color-group-btn" data-color="red" style="width: 30px; height: 30px; background-color: #e74c3c; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="orange" style="width: 30px; height: 30px; background-color: #e67e22; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="yellow" style="width: 30px; height: 30px; background-color: #f1c40f; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="green" style="width: 30px; height: 30px; background-color: #2ecc71; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="blue" style="width: 30px; height: 30px; background-color: #3498db; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="purple" style="width: 30px; height: 30px; background-color: #9b59b6; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="pink" style="width: 30px; height: 30px; background-color: #fd79a8; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="brown" style="width: 30px; height: 30px; background-color: #795548; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="gray" style="width: 30px; height: 30px; background-color: #95a5a6; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="black" style="width: 30px; height: 30px; background-color: #34495e; border: 2px solid #ddd; border-radius: 4px;"></button>
                      <button type="button" class="color-group-btn" data-color="white" style="width: 30px; height: 30px; background-color: #ecf0f1; border: 2px solid #ddd; border-radius: 4px;"></button>
                  </div>
                  <div id="selected-color-info" style="margin-top: 8px; font-size: 14px;">Seçilen Renk: Yok</div>
              </div>

              <div class="form-group">
                  <label for="version-comment">Açıklama (opsiyonel):</label>
                  <input type="text" id="version-comment" class="form-control" placeholder="Bu versiyon hakkında bir açıklama...">
              </div>
          </div>
      `;
  } else {
      // Diğer modeller için standart kümeleme form
      form.innerHTML = `
          <div class="form-group">
              <label for="version-name">Versiyon Adı:</label>
              <input type="text" id="version-name" value="v1" class="form-control">
          </div>
          
          <div class="form-group">
              <label for="algorithm">Algoritma:</label>
              <select id="algorithm" class="form-control">
                  <option value="kmeans" ${selectedAlgorithm === "kmeans" ? "selected" : ""}>K-Means</option>
                  <option value="dbscan" ${selectedAlgorithm === "dbscan" ? "selected" : ""}>DBSCAN</option>
                  <option value="hierarchical" ${selectedAlgorithm === "hierarchical" ? "selected" : ""}>Hierarchical</option>
              </select>
          </div>
          
          <div class="form-group" id="kmeans-params" style="display: ${selectedAlgorithm === 'kmeans' ? 'block' : 'none'}">
              <label for="k">Küme Sayısı (k):</label>
              <input type="number" id="k" min="2" max="100" value="20" class="form-control">
          </div>
          
          <div class="form-group" id="dbscan-params" style="display: ${selectedAlgorithm === 'dbscan' ? 'block' : 'none'}">
              <label for="eps">Epsilon (komşuluk mesafesi):</label>
              <input type="number" id="eps" min="0.01" max="10" step="0.01" value="0.5" class="form-control">
              <label for="min-samples">Min Samples:</label>
              <input type="number" id="min-samples" min="2" max="100" value="5" class="form-control">
          </div>
          
          <div class="form-group" id="hierarchical-params" style="display: ${selectedAlgorithm === 'hierarchical' ? 'block' : 'none'}">
              <label for="distance-threshold">Mesafe Eşiği:</label>
              <input type="number" id="distance-threshold" min="0.1" max="10" step="0.1" value="1.5" class="form-control">
              <label for="linkage">Bağlantı Tipi:</label>
              <select id="linkage" class="form-control">
                  <option value="ward">Ward</option>
                  <option value="complete">Complete</option>
                  <option value="average">Average</option>
                  <option value="single">Single</option>
              </select>
          </div>
          
          <div class="form-group">
              <label for="version-comment">Açıklama (opsiyonel):</label>
              <input type="text" id="version-comment" class="form-control" placeholder="Bu versiyon hakkında bir açıklama...">
          </div>
      `;
  }
  
  modalContent.appendChild(form);
  
  // Butonlar
  const buttons = document.createElement("div");
  buttons.className = "modal-buttons";
  buttons.innerHTML = `
      <button id="cancel-version" class="btn btn-secondary">İptal</button>
      <button id="create-version" class="btn btn-primary">Oluştur</button>
  `;
  modalContent.appendChild(buttons);
  
  // Modal göster
  showModal(modalContent);
  
  // Algoritma değiştiğinde parametre panellerini güncelle
  if (selectedModel !== "color") {
      document.getElementById("algorithm").addEventListener("change", function() {
          const algorithm = this.value;
          document.getElementById("kmeans-params").style.display = algorithm === "kmeans" ? "block" : "none";
          document.getElementById("dbscan-params").style.display = algorithm === "dbscan" ? "block" : "none";
          document.getElementById("hierarchical-params").style.display = algorithm === "hierarchical" ? "block" : "none";
      });
  }
  
  // İptal butonu
  document.getElementById("cancel-version").addEventListener("click", function() {
      closeModal();
  });
  
  // Renk çarkı etkileşimini ekle
  const colorWheel = document.querySelector('.color-wheel');
  const colorMarker = document.getElementById('color-marker');
  
  if (colorWheel) {
      // Renk çarkı bölümlerine tıklama olayı ekle
      const colorSections = colorWheel.querySelectorAll('.color-section');
      colorSections.forEach(section => {
          section.addEventListener('click', function(e) {
              // Tıklanan konumu al
              const rect = colorWheel.getBoundingClientRect();
              const x = e.clientX - rect.left;
              const y = e.clientY - rect.top;
              
              // Merkeze göre konumu hesapla
              const centerX = rect.width / 2;
              const centerY = rect.height / 2;
              const dx = x - centerX;
              const dy = y - centerY;
              
              // Merkeze olan uzaklık (radius içinde olup olmadığını kontrol etmek için)
              const distance = Math.sqrt(dx * dx + dy * dy);
              
              // Eğer orta dairede tıkladıysa işlem yapma
              if (distance < 20) return;
              
              // Ton (Hue) değerini hesapla (0-360 derece)
              const angle = Math.atan2(dy, dx) * 180 / Math.PI;
              const hue = (angle + 90) % 360; // +90 döndürüyor renk çemberi için
              
              // Marker'i göster ve konumlandır
              colorMarker.style.display = 'block';
              colorMarker.style.left = x + 'px';
              colorMarker.style.top = y + 'px';
              
              // Seçilen Ton bilgisini güncelle
              document.getElementById('selected-hue-info').textContent = `Seçilen Ton (Hue): ${Math.round(hue)}°`;
              
              // Seçilen tonu form parametrelerine ekle
              let hueInput = document.getElementById('hue-filter-value');
              if (!hueInput) {
                  hueInput = document.createElement('input');
                  hueInput.type = 'hidden';
                  hueInput.id = 'hue-filter-value';
                  document.querySelector('.color-model-params').appendChild(hueInput);
              }
              hueInput.value = Math.round(hue);
              
              // Seçilen ton ile uyumlu renk butonunu da vurgula
              if (hue >= 330 || hue < 30) highlightColorButton('red');
              else if (hue >= 30 && hue < 60) highlightColorButton('orange');
              else if (hue >= 60 && hue < 90) highlightColorButton('yellow');
              else if (hue >= 90 && hue < 150) highlightColorButton('green');
              else if (hue >= 150 && hue < 210) highlightColorButton('blue');
              else if (hue >= 210 && hue < 270) highlightColorButton('blue');
              else if (hue >= 270 && hue < 330) highlightColorButton('purple');
          });
      });
  }
  
  // Renk butonunu vurgulama yardımcı fonksiyonu
  function highlightColorButton(colorName) {
      const colorButtons = document.querySelectorAll('.color-group-btn');
      colorButtons.forEach(btn => {
          if (btn.dataset.color === colorName) {
              btn.style.borderColor = '#3498db';
              btn.style.borderWidth = '3px';
          } else {
              btn.style.borderColor = '#ddd';
              btn.style.borderWidth = '2px';
          }
      });
  }
  
  // Renk butonlarına tıklama olaylarını ekle
  const colorButtons = document.querySelectorAll('.color-group-btn');
  colorButtons.forEach(btn => {
      btn.addEventListener('click', function() {
          // Tüm butonların seçim durumunu temizle
          colorButtons.forEach(b => b.style.borderColor = '#ddd');
          
          // Bu butonu seçili olarak işaretle
          this.style.borderColor = '#3498db';
          this.style.borderWidth = '3px';
          
          // Seçilen renk bilgisini güncelle
          const colorName = this.dataset.color;
          document.getElementById('selected-color-info').textContent = `Seçilen Renk: ${colorName.charAt(0).toUpperCase() + colorName.slice(1)}`;
          
          // Renk grubunu form parametrelerine ekle için hidden input güncelle veya ekle
          let colorFilterInput = document.getElementById('color-filter-value');
          if (!colorFilterInput) {
              colorFilterInput = document.createElement('input');
              colorFilterInput.type = 'hidden';
              colorFilterInput.id = 'color-filter-value';
              document.querySelector('.color-model-params').appendChild(colorFilterInput);
          }
          colorFilterInput.value = colorName;
      });
  });

  // Oluştur butonu
  document.getElementById("create-version").addEventListener("click", function() {
      const versionName = document.getElementById("version-name").value;
      const versionComment = document.getElementById("version-comment").value;
      
      let clusterParams = {};
      
      if (selectedModel === "color") {
          // Renk modeli için spektrum parametreleri
          const divisions = parseInt(document.getElementById("divisions").value);
          const saturationLevels = parseInt(document.getElementById("saturation-levels").value);
          const valueLevels = parseInt(document.getElementById("value-levels").value);
          const dominantColorMethod = document.getElementById("dominant-color-method").value;
          
          // Seçilen renk grubu filtresi (varsa)
          const colorFilter = document.getElementById('color-filter-value')?.value;
          
          clusterParams = {
              model_type: selectedModel,
              version: versionName,
              algorithm: "color_spectrum",
              divisions: divisions,
              saturation_levels: saturationLevels,
              value_levels: valueLevels,
              dominant_color_method: dominantColorMethod
          };
          
          // Renk filtresi varsa ekle
          if (colorFilter) {
              clusterParams.color_filter = colorFilter;
          }
          
          // Ton (Hue) değeri seçilmişse ekle
          const hueValue = document.getElementById('hue-filter-value')?.value;
          if (hueValue) {
              clusterParams.hue_filter = parseInt(hueValue);
          }
      } else {
          // Diğer modeller için kümeleme parametreleri
          const algorithm = document.getElementById("algorithm").value;
          
          clusterParams = {
              model_type: selectedModel,
              version: versionName,
              algorithm: algorithm
          };
          
          if (algorithm === "kmeans") {
              clusterParams.k = parseInt(document.getElementById("k").value);
          } else if (algorithm === "dbscan") {
              clusterParams.eps = parseFloat(document.getElementById("eps").value);
              clusterParams.min_samples = parseInt(document.getElementById("min-samples").value);
          } else if (algorithm === "hierarchical") {
              clusterParams.distance_threshold = parseFloat(document.getElementById("distance-threshold").value);
              clusterParams.linkage = document.getElementById("linkage").value;
          }
      }
      
      if (versionComment) {
          clusterParams.comment = versionComment;
      }
      
      // API'ye istek gönder
      createClusterVersion(clusterParams);
      
      // Modal kapat
      closeModal();
  });
}

// right_panel.js'de değiştirilecek fonksiyon - muhtemelen satır 1421 civarında
function createClusterVersion(params) {
  // Gönderilen parametreleri debug etmek için konsola yazdır
  console.log("Gönderilen versiyon parametreleri:", JSON.stringify(params, null, 2));
  
  // model ve version parametrelerini garanti edelim
  if (!params.model) {
    // model_type kullanılmışsa, model alanına kopyalayalım
    if (params.model_type) {
      params.model = params.model_type;
    } else {
      // Yoksa mevcut modeli kullan
      params.model = window.currentModel;
    }
  }
  
  if (!params.version) {
    params.version = params.version_name || "v1";
  }
  
  console.log("Düzeltilmiş parametreler:", JSON.stringify(params, null, 2));
  
  // Yükleniyor göster
  const loadingMsg = document.createElement("div");
  loadingMsg.id = "loading-message";
  loadingMsg.style.position = "fixed";
  loadingMsg.style.top = "50%";
  loadingMsg.style.left = "50%";
  loadingMsg.style.transform = "translate(-50%, -50%)";
  loadingMsg.style.backgroundColor = "rgba(0,0,0,0.8)";
  loadingMsg.style.color = "white";
  loadingMsg.style.padding = "20px";
  loadingMsg.style.borderRadius = "5px";
  loadingMsg.style.zIndex = "1001";
  loadingMsg.innerHTML = `
    <div style="text-align: center;">
      <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
      <div>Versiyon oluşturuluyor...</div>
    </div>
  `;
  document.body.appendChild(loadingMsg);
  
  // API'ye istek gönder
  fetch("/create-cluster-version", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params)
  })
  .then(res => res.json())
  .then(result => {
    // Yükleniyor mesajını kaldır
    if (document.getElementById("loading-message")) {
      document.body.removeChild(document.getElementById("loading-message"));
    }
    
    if (result.status === "ok") {
      // Başarılı mesajı göster
      alert(`✅ Yeni versiyon oluşturuldu: ${params.version}`);
      
      // Versiyonları güncelle
      window.currentVersion = params.version;
      loadAvailableVersions(params.model);
      
      // Kullanıcı tercihlerini güncelle
      saveUserPreferences();
      
      // Sağ paneli güncelle
      loadClusterRepresentatives(params.model, params.version);
      
      // Orta panele versiyon değişimini bildir (özel event)
      const event = new CustomEvent('versionChanged', {
        detail: {
          model: params.model,
          version: params.version,
          source: 'rightPanel'
        }
      });
      document.dispatchEvent(event);
    } else {
      // Hata mesajı göster
      alert(`❌ Versiyon oluşturulamadı: ${result.message || 'Bilinmeyen hata'}`);
    }
  })
  .catch(err => {
    // Yükleniyor mesajını kaldır
    if (document.getElementById("loading-message")) {
      document.body.removeChild(document.getElementById("loading-message"));
    }
    
    console.error("Versiyon oluşturma hatası:", err);
    alert("❌ Versiyon oluşturulurken bir hata oluştu.");
  });
}

// Kullanıcı tercihlerini localStorage'a kaydet
function saveUserPreferences() {
  try {
    localStorage.setItem('preferredModel', window.currentModel);
    localStorage.setItem('preferredVersion', window.currentVersion);
    console.log("Kullanıcı tercihleri kaydedildi:", {
      model: window.currentModel,
      version: window.currentVersion
    });
  } catch (e) {
    console.warn("Kullanıcı tercihleri kaydedilemedi:", e);
  }
}

// localStorage'dan kullanıcı tercihlerini yükle
function loadUserPreferences() {
  try {
    const savedModel = localStorage.getItem('preferredModel');
    const savedVersion = localStorage.getItem('preferredVersion');
    
    console.log("Kaydedilmiş tercihler:", {
      model: savedModel,
      version: savedVersion
    });
    
    // Eğer kaydedilmiş değerler varsa, bunları kullan
    if (savedModel) {
      window.currentModel = savedModel;
      highlightCurrentModel();
      
      // Model değiştiği için versiyonları güncelle
      loadAvailableVersions(window.currentModel).then(() => {
        if (savedVersion) {
          window.currentVersion = savedVersion;
          setCurrentVersion();
          loadClusterRepresentatives(window.currentModel, window.currentVersion);
        }
      });
    }
  } catch (e) {
    console.warn("Kullanıcı tercihleri yüklenemedi:", e);
  }
}

// Yeni model versiyon kombinasyonu oluşturma
function initModelVersion(model, version) {
  fetch("/init-model-version", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, version })
  })
  .then(res => res.json())
  .then(result => {
    if (result.status === "ok") {
      alert(`✅ ${result.message}`);
      loadClusterRepresentatives(model, version);
    } else {
      alert("❌ Hazırlanamadı: " + result.message);
    }
  })
  .catch(err => {
    console.error("Hazırlama hatası:", err);
    alert("❌ İşlem sırasında hata oluştu.");
  });
}

// Yeni cluster oluşturma fonksiyonu
function createNewCluster(model, version) {
  const selected = window.selectedImages || []; // global array orta panelden
  if (!selected.length) {
    alert("Lütfen önce görselleri seçin.");
    return;
  }

  fetch("/create-cluster", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, version, filenames: selected })
  })
  .then(res => res.json())
  .then(result => {
    if (result.status === "ok") {
      alert(`✅ Yeni cluster oluşturuldu: ${result.new_cluster}`);
      loadClusterRepresentatives(model, version);
      window.selectedImages = []; // sıfırla
      
      // Merkez paneldeki seçimleri temizle
      window.selectedImages.clear();
      document.querySelectorAll("#center-results .image-box input[type='checkbox']").forEach(cb => {
        cb.checked = false;
      });
      document.querySelectorAll("#center-results .image-box").forEach(box => {
        box.classList.remove('selected');
      });
    } else {
      alert("❌ Oluşturulamadı: " + result.message);
    }
  })
  .catch(err => {
    console.error("Cluster oluşturma hatası:", err);
    alert("❌ Cluster oluşturulurken hata oluştu.");
  });
}

// Modal gösterme fonksiyonu
function showModal(content) {
  // Eski modalı kaldır
  const oldModal = document.querySelector(".modal-container");
  if (oldModal) document.body.removeChild(oldModal);
  
  // Yeni modal oluştur
  const modalContainer = document.createElement("div");
  modalContainer.className = "modal-container";
  modalContainer.style.position = "fixed";
  modalContainer.style.top = "0";
  modalContainer.style.left = "0";
  modalContainer.style.width = "100%";
  modalContainer.style.height = "100%";
  modalContainer.style.backgroundColor = "rgba(0,0,0,0.5)";
  modalContainer.style.display = "flex";
  modalContainer.style.justifyContent = "center";
  modalContainer.style.alignItems = "center";
  modalContainer.style.zIndex = "1000";
  
  // Modal içeriği
  const modalBox = document.createElement("div");
  modalBox.className = "modal-box";
  modalBox.style.backgroundColor = "white";
  modalBox.style.padding = "20px";
  modalBox.style.borderRadius = "5px";
  modalBox.style.maxWidth = "500px";
  modalBox.style.width = "90%";
  modalBox.style.maxHeight = "80vh";
  modalBox.style.overflowY = "auto";
  
  modalBox.appendChild(content);
  modalContainer.appendChild(modalBox);
  document.body.appendChild(modalContainer);
  
  // Modal dışına tıklama ile kapatma
  modalContainer.addEventListener("click", (e) => {
    if (e.target === modalContainer) {
      closeModal();
    }
  });
}

// Modal kapatma fonksiyonu
function closeModal() {
  const modal = document.querySelector(".modal-container");
  if (modal) document.body.removeChild(modal);
}

// Sayfa yüklenirken bu komut çalıştırılır
window.addEventListener("DOMContentLoaded", () => {
  initRightPanel();
  
  // Kullanıcı tercihlerini yükle
  loadUserPreferences();
  
  // Orta panelden gelen model/versiyon değişikliklerini dinle
  document.addEventListener('modelChanged', handleModelChangeEvent);
  document.addEventListener('versionChanged', handleVersionChangeEvent);
});

// Orta panelden gelen model değişikliği olayını işle
function handleModelChangeEvent(e) {
  // Olay orta panelden geliyorsa ve mevcut modelden farklı ise güncelle
  if (e.detail && e.detail.source === 'centerPanel' && e.detail.model !== window.currentModel) {
    console.log('Orta panelden model değişikliği algılandı:', e.detail.model);
    window.currentModel = e.detail.model;
    
    // Model butonlarını güncelle
    highlightCurrentModel();
    
    // Versiyonları güncelle
    loadAvailableVersions(window.currentModel);
    
    // Cluster'ları güncelle
    loadClusterRepresentatives(window.currentModel, window.currentVersion);
    
    // Kullanıcı tercihlerini kaydet
    saveUserPreferences();
  }
}

// Orta panelden gelen versiyon değişikliği olayını işle
function handleVersionChangeEvent(e) {
  // Olay orta panelden geliyorsa ve mevcut versiyondan farklı ise güncelle
  if (e.detail && e.detail.source === 'centerPanel') {
    // Önce model değişikliğini kontrol et
    if (e.detail.model !== window.currentModel) {
      console.log('Orta panelden model ve versiyon değişikliği algılandı:', 
               {model: e.detail.model, version: e.detail.version});
      
      window.currentModel = e.detail.model;
      highlightCurrentModel();
      
      // Versiyonları güncelle, sonrasında versiyon ve cluster'ları güncelle
      loadAvailableVersions(window.currentModel).then(() => {
        if (e.detail.version !== window.currentVersion) {
          window.currentVersion = e.detail.version;
          setCurrentVersion();
          loadClusterRepresentatives(window.currentModel, window.currentVersion);
          
          // Kullanıcı tercihlerini kaydet
          saveUserPreferences();
        }
      });
    }
    // Sadece versiyon değişikliği varsa
    else if (e.detail.version !== window.currentVersion) {
      console.log('Orta panelden versiyon değişikliği algılandı:', e.detail.version);
      window.currentVersion = e.detail.version;
      setCurrentVersion();
      loadClusterRepresentatives(window.currentModel, window.currentVersion);
      
      // Kullanıcı tercihlerini kaydet
      saveUserPreferences();
    }
  }
}