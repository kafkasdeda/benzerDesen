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

  // Doğru URL ile versiyonlu cluster verilerini yükle
  fetch(`/clusters/${model}/${version}/representatives.json`)
    .then(res => {
      // Status kodu kontrol et
      if (!res.ok) {
        throw new Error(`Sunucu yanıtı hatalı: ${res.status} ${res.statusText}`);
      }
      return res.json();
    })
    .then(data => {
      if (!data.clusters || !Array.isArray(data.clusters)) {
        loadingMsg.innerHTML = "❌ Cluster verisi beklenen formatta değil veya boş.";
        
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

      // Loading mesajını temizle
      if (loadingMsg && loadingMsg.parentNode === rightPanel) {
        rightPanel.removeChild(loadingMsg);
      }

      // Versiyon yorumu
      const versionHeader = document.createElement("div");
      versionHeader.innerHTML = `
        <h3>${model} - ${version}</h3>
        <p><strong>Versiyon Yorumu:</strong> <span id="version-comment-text">${data.version_comment || "(Yorum yok)"}</span>
        <button id="edit-comment-btn">🖊️</button></p>
        <div id="comment-edit-box" style="display:none; margin-top:8px;">
          <textarea id="version-comment-input" rows="3" style="width:100%;"></textarea>
          <button id="save-comment-btn">Kaydet</button>
          <button id="cancel-comment-btn">İptal</button>
        </div>
      `;
      rightPanel.appendChild(versionHeader);

      // EVENT: Yorumu düzenle
      document.getElementById("edit-comment-btn").addEventListener("click", () => {
        document.getElementById("version-comment-input").value = data.version_comment || "";
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

      // Cluster sayacı ve istatistik ekle
      const statsBox = document.createElement("div");
      statsBox.style.backgroundColor = "#f9f9f9";
      statsBox.style.padding = "10px";
      statsBox.style.borderRadius = "5px";
      statsBox.style.marginBottom = "15px";
      
      // Benzersiz cluster say
      const uniqueClusters = new Set(data.clusters.map(c => c.cluster)).size;
      
      statsBox.innerHTML = `
        <div style="display: flex; justify-content: space-between;">
          <div>
            <strong>Toplam Cluster:</strong> ${uniqueClusters}
          </div>
          <div>
            <strong>Toplam Görsel:</strong> ${data.clusters.length}
          </div>
        </div>
      `;
      rightPanel.appendChild(statsBox);

      const container = document.createElement("div");
      container.className = "image-grid";

      // Sadece benzersiz cluster'ları göster (temsil eden görseller)
      const clusterMap = {};
      data.representatives.forEach(rep => {
        clusterMap[rep.cluster] = rep.filename;
      });
      
      // Her cluster için bir kutu oluştur
      Object.entries(clusterMap).forEach(([clusterName, filename]) => {
        const box = document.createElement("div");
        box.className = "cluster-box";
        
        // Cluster içindeki görsel sayısını hesapla
        const clusterImages = data.clusters.filter(c => c.cluster === clusterName);
        
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
          .then(data => {
            console.log("✅ Taşıma başarılı:", data);
            alert("Seçilen görseller ilgili cluster'a taşındı.");
            document.querySelectorAll("#center-results .image-box input[type='checkbox']").forEach(cb => {
              cb.checked = false;
            });
            // Sayfayı yenile
            loadClusterRepresentatives(model, version);
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

// Sayfa yüklendiğinde paneli başlat
window.addEventListener("DOMContentLoaded", () => {
  initRightPanel();
});
