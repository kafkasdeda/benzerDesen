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
  
  // Olay dinleyicileri ekle
  const modelButtons = document.querySelectorAll(".model-button");
  modelButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      window.currentModel = btn.dataset.model;
      highlightCurrentModel();
      loadAvailableVersions(window.currentModel);
      loadClusterRepresentatives(window.currentModel, window.currentVersion);
    });
  });
  
  document.getElementById("version-combo").addEventListener("change", (e) => {
    window.currentVersion = e.target.value;
    loadClusterRepresentatives(window.currentModel, window.currentVersion);
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
        loadingMsg.innerHTML = `❌ Cluster verisi beklenen formatta değil veya boş.<br><br>
                             <small>Detaylar: ${JSON.stringify(response)}</small>`;
        
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

        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        tooltip.innerHTML = `
          <img src='thumbnails/${filename}' />
          <strong>${clusterName}</strong><br>
          Bu cluster'da ${clusterImages.length} görsel var
        `;

        box.appendChild(img);
        box.appendChild(tooltip);
        
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
              document.querySelectorAll("#center-results .image-box input[type='checkbox']").forEach(cb => {
                cb.checked = false;
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
  
  content.innerHTML = `
    <h2>Yeni ${window.currentModel} Versiyonu Oluştur</h2>
    
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
        <input type="range" id="k-slider" min="2" max="20" value="5" style="width: 100%;">
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
    
    <!-- Butonlar -->
    <div style="margin-top: 20px; display: flex; justify-content: space-between;">
      <button id="cancel-version" style="padding: 10px 15px; background-color: #ccc; border: none; border-radius: 4px; cursor: pointer;">İptal</button>
      <button id="create-version" style="padding: 10px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Oluştur</button>
    </div>
  `;
  
  modal.appendChild(content);
  document.body.appendChild(modal);
  
  // Event listeners
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
  
  document.getElementById("cancel-version").addEventListener("click", () => {
    document.body.removeChild(modal);
  });
  
  document.getElementById("create-version").addEventListener("click", createNewVersion);
  
  // İlk görünümü ayarla
  updateAlgorithmParams();
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
  const algorithm = document.getElementById("algorithm-select").value;
  const comment = document.getElementById("version-comment").value;
  
  // Parametre değerlerini al
  let parameters = {};
  
  if (algorithm === "kmeans") {
    parameters.k = parseInt(document.getElementById("k-slider").value);
  }
  else if (algorithm === "dbscan") {
    parameters.eps = parseFloat(document.getElementById("eps-slider").value);
    parameters.min_samples = parseInt(document.getElementById("min-samples-slider").value);
  }
  else if (algorithm === "hierarchical") {
    parameters.k = parseInt(document.getElementById("h-k-slider").value);
    parameters.linkage = document.getElementById("linkage-select").value;
  }
  
  // Modal'ı bekliyor durumuna getir
  const modal = document.getElementById("new-version-modal");
  const content = modal.querySelector("div");
  content.innerHTML = `
    <h2>Yeni Versiyon Oluşturuluyor...</h2>
    <p style="text-align: center; margin: 20px 0;">
      <span style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
            border-top: 4px solid #3498db; border-radius: 50%; animation: spin 2s linear infinite;"></span>
    </p>
    <p style="text-align: center;">Bu işlem biraz zaman alabilir, lütfen bekleyin.</p>
    
    <style>
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    </style>
  `;
  
  // API çağrısı yap
  fetch("/create-new-version", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: window.currentModel,
      algorithm,
      parameters,
      comment
    })
  })
  .then(res => res.json())
  .then(result => {
    if (result.status === "ok") {
      // Modal'ı başarılı durumuna getir
      content.innerHTML = `
        <h2>✅ Yeni Versiyon Oluşturuldu</h2>
        <p style="margin: 15px 0;">
          <strong>${window.currentModel}</strong> modeli için <strong>${result.version}</strong> versiyonu başarıyla oluşturuldu.
        </p>
        <p>Toplam <strong>${result.cluster_count}</strong> cluster oluşturuldu.</p>
        
        <div style="margin-top: 20px; text-align: center;">
          <button id="close-success" style="padding: 10px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Tamam</button>
        </div>
      `;
      
      document.getElementById("close-success").addEventListener("click", () => {
        document.body.removeChild(modal);
        
        // Mevcut versiyonu güncelle ve yeniden yükle
        window.currentVersion = result.version;
        loadAvailableVersions(window.currentModel);
        loadClusterRepresentatives(window.currentModel, window.currentVersion);
      });
    }
    else {
      // Modal'ı hata durumuna getir
      content.innerHTML = `
        <h2>❌ Hata Oluştu</h2>
        <p style="margin: 15px 0; color: #e74c3c;">
          ${result.message}
        </p>
        
        <div style="margin-top: 20px; text-align: center;">
          <button id="close-error" style="padding: 10px 15px; background-color: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;">Kapat</button>
        </div>
      `;
      
      document.getElementById("close-error").addEventListener("click", () => {
        document.body.removeChild(modal);
      });
    }
  })
  .catch(err => {
    // Modal'ı hata durumuna getir
    content.innerHTML = `
      <h2>❌ Bağlantı Hatası</h2>
      <p style="margin: 15px 0; color: #e74c3c;">
        Sunucu ile iletişim kurulurken bir hata oluştu:<br>
        ${err.message}
      </p>
      
      <div style="margin-top: 20px; text-align: center;">
        <button id="close-error" style="padding: 10px 15px; background-color: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;">Kapat</button>
      </div>
    `;
    
    document.getElementById("close-error").addEventListener("click", () => {
      document.body.removeChild(modal);
    });
  });
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
      document.querySelectorAll("#center-results .image-box input[type='checkbox']").forEach(cb => {
        cb.checked = false;
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

// Sayfa yüklenirken bu komut çalıştırılır
window.addEventListener("DOMContentLoaded", () => {
  initRightPanel();
});
