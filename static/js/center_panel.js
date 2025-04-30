// Karşılaştırma listesine görsel ekle
function addToCompareList(filename, resultData) {
    // Halihazırda listede mi kontrol et
    const existingIndex = compareList.findIndex(item => item.filename === filename);
    if (existingIndex !== -1) {
        // Listede varsa uyarı ver
        alert(`"${filename}" zaten karşılaştırma listesinde!`);
        return;
    }
    
    // Maksimum 4 görsel karşılaştırılabilir
    if (compareList.length >= 4) {
        alert("En fazla 4 görsel karşılaştırabilirsiniz. Lütfen önce listeden görsel çıkarın.");
        return;
    }
    
    // Listeye ekle
    compareList.push({
        filename: filename,
        metadata: resultData ? resultData : { filename: filename }
    });
    
    // Karşılaştırma barını göster veya güncelle
    updateCompareBar();
    
    // Console'a bilgi ver
    console.log(`Karşılaştırma listesine eklendi: ${filename}`);
}

// Karşılaştırma listesinden görsel çıkar
function removeFromCompareList(filename) {
    const index = compareList.findIndex(item => item.filename === filename);
    if (index !== -1) {
        compareList.splice(index, 1);
        updateCompareBar();
        console.log(`Karşılaştırma listesinden çıkarıldı: ${filename}`);
    }
}

// Karşılaştırma barını güncelle
function updateCompareBar() {
    // Karşılaştırma barını kontrol et, yoksa oluştur
    let compareBar = document.getElementById("compare-bar");
    if (!compareBar) {
        compareBar = document.createElement("div");
        compareBar.id = "compare-bar";
        compareBar.style.position = "fixed";
        compareBar.style.bottom = "0";
        compareBar.style.left = "0";
        compareBar.style.right = "0";
        compareBar.style.backgroundColor = "rgba(155, 89, 182, 0.9)"; // Mor renk, hafif transparan
        compareBar.style.color = "white";
        compareBar.style.padding = "10px";
        compareBar.style.boxShadow = "0 -2px 10px rgba(0,0,0,0.2)";
        compareBar.style.zIndex = "999";
        compareBar.style.display = "flex";
        compareBar.style.alignItems = "center";
        compareBar.style.justifyContent = "space-between";
        document.body.appendChild(compareBar);
    }
    
    // Boşsa görünürden kaldır
    if (compareList.length === 0) {
        compareBar.style.display = "none";
        // Karşılaştırma modundan çık
        if (isCompareMode) {
            exitCompareMode();
        }
        return;
    }
    
    // Barı göster
    compareBar.style.display = "flex";
    
    // İçeriğini güncelle
    let leftContent = document.createElement("div");
    leftContent.style.display = "flex";
    leftContent.style.alignItems = "center";
    leftContent.style.flex = "1";
    leftContent.style.marginRight = "10px";
    leftContent.style.overflowX = "auto";
    leftContent.style.paddingBottom = "5px"; // Scroll bar için fazladan boşluk
    
    // Görsel önizlemelerini ve çıkarma butonlarını ekle
    compareList.forEach(item => {
        const previewContainer = document.createElement("div");
        previewContainer.style.display = "flex";
        previewContainer.style.flexDirection = "column";
        previewContainer.style.alignItems = "center";
        previewContainer.style.margin = "0 10px";
        previewContainer.style.position = "relative";
        
        const previewImg = document.createElement("img");
        previewImg.src = `/thumbnails/${item.filename}`;
        previewImg.alt = item.filename;
        previewImg.style.width = "60px";
        previewImg.style.height = "60px";
        previewImg.style.objectFit = "cover";
        previewImg.style.borderRadius = "4px";
        previewImg.style.border = "2px solid white";
        
        const removeBtn = document.createElement("button");
        removeBtn.innerHTML = "&times;";
        removeBtn.style.position = "absolute";
        removeBtn.style.top = "-8px";
        removeBtn.style.right = "-8px";
        removeBtn.style.backgroundColor = "#e74c3c";
        removeBtn.style.color = "white";
        removeBtn.style.border = "none";
        removeBtn.style.borderRadius = "50%";
        removeBtn.style.width = "20px";
        removeBtn.style.height = "20px";
        removeBtn.style.fontSize = "14px";
        removeBtn.style.cursor = "pointer";
        removeBtn.style.display = "flex";
        removeBtn.style.justifyContent = "center";
        removeBtn.style.alignItems = "center";
        removeBtn.style.lineHeight = "1";
        removeBtn.addEventListener("click", () => removeFromCompareList(item.filename));
        
        const filename = document.createElement("div");
        filename.textContent = item.filename.length > 15 ? item.filename.substring(0, 12) + "..." : item.filename;
        filename.style.fontSize = "10px";
        filename.style.marginTop = "4px";
        filename.style.color = "white";
        filename.style.maxWidth = "60px";
        filename.style.overflow = "hidden";
        filename.style.textOverflow = "ellipsis";
        filename.style.whiteSpace = "nowrap";
        
        previewContainer.appendChild(previewImg);
        previewContainer.appendChild(removeBtn);
        previewContainer.appendChild(filename);
        leftContent.appendChild(previewContainer);
    });
    
    // Sağ taraf (butonlar)
    let rightContent = document.createElement("div");
    rightContent.style.display = "flex";
    rightContent.style.alignItems = "center";
    rightContent.style.gap = "10px";
    
    // Karşılaştırma butonları
    const compareBtn = document.createElement("button");
    compareBtn.textContent = "Karşılaştır";
    compareBtn.style.backgroundColor = "#8e44ad";
    compareBtn.style.color = "white";
    compareBtn.style.border = "none";
    compareBtn.style.borderRadius = "4px";
    compareBtn.style.padding = "8px 15px";
    compareBtn.style.cursor = "pointer";
    compareBtn.addEventListener("click", showCompareView);
    
    const clearBtn = document.createElement("button");
    clearBtn.textContent = "Temizle";
    clearBtn.style.backgroundColor = "rgba(255,255,255,0.3)";
    clearBtn.style.color = "white";
    clearBtn.style.border = "none";
    clearBtn.style.borderRadius = "4px";
    clearBtn.style.padding = "8px 15px";
    clearBtn.style.cursor = "pointer";
    clearBtn.addEventListener("click", clearCompareList);
    
    rightContent.appendChild(compareBtn);
    rightContent.appendChild(clearBtn);
    
    // Barın içeriğini güncelle
    compareBar.innerHTML = '';
    compareBar.appendChild(leftContent);
    compareBar.appendChild(rightContent);
}

// Karşılaştırma listesini temizle
function clearCompareList() {
    compareList = [];
    updateCompareBar();
    console.log("Karşılaştırma listesi temizlendi");
}

// Karşılaştırma görünümünü göster
function showCompareView() {
    if (compareList.length < 2) {
        alert("Karşılaştırma için en az 2 görsel seçmelisiniz.");
        return;
    }
    
    // Karşılaştırma moduna geç
    isCompareMode = true;
    
    // Orta panel içeriğini karşılaştırma görünümüyle değiştir
    const container = document.getElementById("center-results");
    
    // Başlık ve kontroller
    let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
            <h3 style="margin: 0;">Görsel Karşılaştırma (${compareList.length} görsel)</h3>
            <button id="exit-compare-btn" style="padding: 5px 10px; background-color: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;">Çıkış</button>
        </div>
    `;
    
    // Karşılaştırma tablosu
    html += `<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">`;
    
    // Başlık satırı
    html += `<tr style="background-color: #f8f9fa;">
        <th style="padding: 10px; border: 1px solid #ddd; min-width: 100px;">Bilgi</th>
    `;
    
    // Her görsel için bir sütun ekle
    compareList.forEach(item => {
        html += `<th style="padding: 10px; border: 1px solid #ddd; min-width: 200px;">${item.filename}</th>`;
    });
    
    html += `</tr>`;
    
    // Görsel satırı
    html += `<tr>
        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Görsel</td>
    `;
    
    compareList.forEach(item => {
        html += `
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">
                <img src="/realImages/${item.filename}" style="max-width: 100%; max-height: 200px; object-fit: contain;">
            </td>
        `;
    });
    
    html += `</tr>`;
    
    // Benzerlik skoru satırı (ilk görsel referans alarak)
    if (compareList.length > 1 && compareList[0].metadata && compareList[0].metadata.similarity !== undefined) {
        html += `<tr>
            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Benzerlik</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">Referans</td>
        `;
        
        // İlk görselden sonraki görseller için benzerlik skorları
        for (let i = 1; i < compareList.length; i++) {
            const item = compareList[i];
            let similarityDisplay = "Bilinmiyor";
            
            if (item.metadata && item.metadata.similarity !== undefined) {
                const similarity = item.metadata.similarity * 100;
                let color = "#2ecc71"; // Yeşil
                
                if (similarity < 50) {
                    color = "#e74c3c"; // Kırmızı
                } else if (similarity < 75) {
                    color = "#f39c12"; // Turuncu
                }
                
                similarityDisplay = `<span style="color: ${color}; font-weight: bold;">${similarity.toFixed(1)}%</span>`;
            }
            
            html += `<td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${similarityDisplay}</td>`;
        }
        
        html += `</tr>`;
    }
    
    // Diğer özellikler
    const properties = ["design", "season", "quality", "cluster"];
    const propertyLabels = {
        "design": "Desen",
        "season": "Sezon",
        "quality": "Kalite",
        "cluster": "Cluster"
    };
    
    properties.forEach(prop => {
        let hasProperty = false;
        
        // En az bir görselde bu özellik var mı kontrol et
        for (const item of compareList) {
            if (item.metadata && item.metadata[prop]) {
                hasProperty = true;
                break;
            }
        }
        
        if (hasProperty) {
            html += `<tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">${propertyLabels[prop]}</td>
            `;
            
            compareList.forEach(item => {
                const value = (item.metadata && item.metadata[prop]) ? item.metadata[prop] : "-";
                html += `<td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${value}</td>`;
            });
            
            html += `</tr>`;
        }
    });
    
    // Ham madde karışımı için özel satır
    let hasFeatures = false;
    for (const item of compareList) {
        if (item.metadata && Array.isArray(item.metadata.features) && item.metadata.features.length > 0) {
            hasFeatures = true;
            break;
        }
    }
    
    if (hasFeatures) {
        html += `<tr>
            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Ham Madde</td>
        `;
        
        compareList.forEach(item => {
            let featuresHtml = "-";
            
            if (item.metadata && Array.isArray(item.metadata.features) && item.metadata.features.length > 0) {
                featuresHtml = `<div style="display: flex; flex-direction: column; gap: 5px;">`;
                
                item.metadata.features.forEach(feature => {
                    featuresHtml += `
                        <div style="display: flex; justify-content: space-between; font-size: 12px;">
                            <span>${feature[0]}:</span>
                            <span style="font-weight: bold;">${feature[1]}%</span>
                        </div>
                    `;
                });
                
                featuresHtml += `</div>`;
            }
            
            html += `<td style="padding: 10px; border: 1px solid #ddd;">${featuresHtml}</td>`;
        });
        
        html += `</tr>`;
    }
    
    html += `</table></div>`;
    
    // Renk karşılaştırması için bölüm
    html += `
        <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
            <h3>Renk Karşılaştırması</h3>
            <p>Bu bölümde dominant renklerin karşılaştırması gösterilecektir.</p>
            <div id="color-comparison" style="display: flex; justify-content: space-around; margin-top: 20px;">
                <div class="color-loading">Renk analizi yapılıyor...</div>
            </div>
        </div>
    `;
    
    // HTML içeriğini güncelle
    container.innerHTML = html;
    
    // Çıkış butonuna event listener ekle
    document.getElementById("exit-compare-btn").addEventListener("click", exitCompareMode);
    
    // Renk analizi için API çağrısı eklenebilir (Backend'de renk çıkarma fonksiyonu varsa)
    analyzeDominantColors();
}

// Karşılaştırma modundan çık
function exitCompareMode() {
    isCompareMode = false;
    
    // Ana aramaya geri dön
    if (currentFilename) {
        fetchSimilarImages(currentFilename);
    } else {
        document.getElementById("center-results").innerHTML = "Lütfen sol panelden bir görsel seçin.";
    }
}

// Renk karşılaştırması için renk analizi
async function analyzeDominantColors() {
    if (!isCompareMode) return;
    
    const colorContainer = document.getElementById("color-comparison");
    if (!colorContainer) return;
    
    // Dummy renk analizi (Gerçek API yoksa)
    // Not: Gerçek bir uygulamada server'dan renk analizi yapmak daha doğru olur
    const dummyColors = [
        [125, 60, 152],   // Mor
        [45, 125, 210],   // Mavi
        [220, 60, 30],    // Kırmızı
        [30, 150, 90]     // Yeşil
    ];
    
    // HTML oluştur
    let html = '';
    
    compareList.forEach((item, index) => {
        // Döngüsel olarak dummy renkler kullan
        const color = dummyColors[index % dummyColors.length];
        const colorHex = `#${color[0].toString(16).padStart(2, '0')}${color[1].toString(16).padStart(2, '0')}${color[2].toString(16).padStart(2, '0')}`;
        
        html += `
            <div style="text-align: center;">
                <div style="width: 60px; height: 60px; background-color: ${colorHex}; border-radius: 50%; margin: 0 auto; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"></div>
                <div style="margin-top: 8px; font-size: 12px;">${item.filename}</div>
                <div style="margin-top: 4px; font-size: 10px; color: #666;">RGB: ${color.join(', ')}</div>
                <div style="margin-top: 2px; font-size: 10px; color: #666;">HEX: ${colorHex}</div>
            </div>
        `;
    });
    
    colorContainer.innerHTML = html;
}/**
 * center_panel.js
 * Oluşturulma: 2025-04-19
 * Güncelleme: 2025-04-28 (Uyumlu renkleri bulma özelliği eklendi)
 * Güncelleme: 2025-04-29 (Tooltip bilgi balonları eklendi)
 * Hazırlayan: Kafkas
 * 
 * Açıklama:
 * Bu dosya, Power User arayüzünün orta panelini yönetir. Benzer görsel
 * sonuçlarını gösterir ve filtreleme seçenekleri sunar.
 */

// Global değişkenler
let currentFilename = null;
let currentModel = "pattern";
let currentVersion = "v1";
let currentMetric = "cosine";
let currentTopN = 50;
let currentFeatures = [];
let currentMixFilters = [];
let clusterStatus = "";
let filterApplied = false;
let selectedImages = new Set();

// Karşılaştırma için global değişkenler
let compareList = [];
let isCompareMode = false;

// DOM yüklendikten sonra çalış
document.addEventListener("DOMContentLoaded", async () => {
    // Aktif Model Bilgisi Gösterge Paneli
    const modelInfoPanel = document.createElement("div");
    modelInfoPanel.id = "active-model-info";
    modelInfoPanel.style.backgroundColor = "#f8f9fa";
    modelInfoPanel.style.border = "1px solid #ddd";
    modelInfoPanel.style.borderRadius = "5px";
    modelInfoPanel.style.padding = "10px";
    modelInfoPanel.style.margin = "10px 0 20px 0";
    modelInfoPanel.style.display = "flex";
    modelInfoPanel.style.justifyContent = "space-between";
    modelInfoPanel.style.alignItems = "center";
    modelInfoPanel.style.fontSize = "14px";
    modelInfoPanel.innerHTML = `
        <div>
            <span style="font-weight: bold;">Aktif Model:</span> <span id="active-model-name">${currentModel || 'pattern'}</span>
            <span style="margin-left: 15px; font-weight: bold;">Versiyon:</span> <span id="active-version-name">${currentVersion || 'v1'}</span>
        </div>
        <div>
            <span style="font-weight: bold;">Metrik:</span> <span id="active-metric-name">${currentMetric || 'cosine'}</span>
            <span style="margin-left: 15px; font-weight: bold;">Top N:</span> <span id="active-topn-name">${currentTopN || '50'}</span>
        </div>
    `;
    
    // Arama parametreleri panelinin altına yerleştir
    document.getElementById("search-panel-content").parentNode.insertBefore(modelInfoPanel, document.getElementById("center-results"));
    initializeUI();
    initializeEventListeners();
});

// Arayüz elemanlarını hazırla
function initializeUI() {
    // Filtreleme paneli açma/kapama
    const toggleButton = document.getElementById("toggle-search-panel");
    const panelContent = document.getElementById("search-panel-content");

    toggleButton.addEventListener("click", () => {
        const isVisible = panelContent.style.display === "block";
        panelContent.style.display = isVisible ? "none" : "block";
        toggleButton.textContent = isVisible ? "▼" : "▲";
    });
    
    // Başlangıçta filtreleme panelini gizli göster
    panelContent.style.display = "none";
    toggleButton.textContent = "▼";

    // Parametreleri sıfırlama düğmesi
    const resetButton = document.getElementById("reset-filters");
    resetButton.addEventListener("click", resetFilters);

    // Arama yapma düğmesi
    const applyButton = document.getElementById("apply-filters");
    applyButton.addEventListener("click", () => {
        filterApplied = true;
        if (currentFilename) {
            fetchSimilarImages(currentFilename);
        }
    });

    // Model değiştiğinde versiyon listesini güncelle
    const modelSelector = document.getElementById("model-selector");
    modelSelector.addEventListener("change", updateVersions);

    // Versiyon değiştiğinde küme listesini güncelle (eğer uygulanabilirse)
    const versionSelector = document.getElementById("version-selector");
    versionSelector.addEventListener("change", () => {
        currentVersion = versionSelector.value;
    });

    document.getElementById("model-selector").addEventListener("change", () => {
      currentModel = document.getElementById("model-selector").value;
      document.getElementById("active-model-name").textContent = currentModel;
    });
    
      document.getElementById("version-selector").addEventListener("change", () => {
      currentVersion = document.getElementById("version-selector").value;
      document.getElementById("active-version-name").textContent = currentVersion;
    });
    
    document.getElementById("metric-selector").addEventListener("change", () => {
    currentMetric = document.getElementById("metric-selector").value;
    document.getElementById("active-metric-name").textContent = currentMetric;
    });
    
    document.getElementById("topn-input").addEventListener("change", () => {
        currentTopN = document.getElementById("topn-input").value;
        document.getElementById("active-topn-name").textContent = currentTopN;
      });

    // Feature checkboxlarını dinle
    const featureCheckboxes = document.querySelectorAll(".feature-checkbox");
    featureCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", () => {
            updateSelectedFeatures();
        });
    });

    // Karışım ekle butonunu dinle
    const addMaterialButton = document.getElementById("add-material");
    addMaterialButton.addEventListener("click", addMaterial);

    // Cluster radio butonlarını dinle
    const clusterRadios = document.querySelectorAll('input[name="center-cluster"]');
    clusterRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            clusterStatus = radio.value;
        });
    });

    // Hammadde dropdown'unu doldur
    populateMaterialDropdown();
}

// Hammadde dropdown'unu doldur
function populateMaterialDropdown() {
    // Bu fonksiyon daha sonra implementlerınııe edilecek
    // Şimdilik window.blendSet üzerinden çağırılıyor
    if (window.blendSet) {
        const selector = document.getElementById("material-selector");
        selector.innerHTML = '<option value="">Hammadde Seçin</option>';
        window.blendSet.forEach(htype => {
            const opt = document.createElement("option");
            opt.value = htype;
            opt.textContent = htype;
            selector.appendChild(opt);
        });
    }
}

// Olay dinleyicilerini ekle
function initializeEventListeners() {
    // Görsel kutusu tıklama olayı için delegasyon
    document.getElementById("center-results").addEventListener("click", handleImageClick);
}

// Filtreleri sıfırla
function resetFilters() {
    // Model ve versiyon hariç tüm filtreleri sıfırla
    currentMetric = "cosine";
    currentTopN = 50;
    currentFeatures = [];
    currentMixFilters = [];
    clusterStatus = "";
    filterApplied = false;

    // UI elemanlarını güncelle
    document.getElementById("metric-selector").value = "cosine";
    document.getElementById("topn-input").value = "50";
    
    // Özellik checkboxlarını temizle
    document.querySelectorAll(".feature-checkbox").forEach(cb => cb.checked = false);
    
    // Karışım satırlarını temizle
    document.getElementById("material-rows").innerHTML = "";
    document.getElementById("total-percentage").textContent = "0";
    document.getElementById("total-progress").style.width = "0%";
    
    // Cluster radio butonlarını sıfırla
    document.querySelector('input[name="center-cluster"][value=""]').checked = true;
    
    console.log("Filtreler sıfırlandı.");
    
    // Eğer bir görsel seçiliyse, sıfırlanmış filtrelerle yeniden sonuçları getir
    if (currentFilename) {
        fetchSimilarImages(currentFilename);
    }
}

// Seçili özellikleri güncelle
function updateSelectedFeatures() {
    const checkboxes = document.querySelectorAll(".feature-checkbox:checked");
    currentFeatures = Array.from(checkboxes).map(cb => cb.value);
}

// Karışım ekle
function addMaterial() {
    const materialSelector = document.getElementById("material-selector");
    const materialType = materialSelector.value;
    
    if (!materialType) return;
    
    // Zaten eklenmiş mi kontrol et
    const existingRows = document.querySelectorAll(".material-row");
    for (const row of existingRows) {
        if (row.dataset.type === materialType) {
            alert(`${materialType} zaten eklenmiş!`);
            return;
        }
    }
    
    // Karışım satırı oluştur
    const materialRows = document.getElementById("material-rows");
    const rowId = `material-${Date.now()}`;
    
    const rowHtml = `
        <div id="${rowId}" class="material-row" data-type="${materialType}" style="display: grid; grid-template-columns: 100px 1fr 60px 30px; gap: 5px; margin-bottom: 10px; align-items: center;">
            <span class="material-name">${materialType}</span>
            <div class="material-range-container" style="position: relative; height: 30px;">
                <div class="material-range" style="position: absolute; top: 50%; transform: translateY(-50%); width: 100%;"></div>
            </div>
            <span class="material-value" id="${rowId}-value">0%</span>
            <button class="material-remove" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 16px;">&times;</button>
        </div>
    `;
    
    materialRows.insertAdjacentHTML('beforeend', rowHtml);
    
    // Slider oluştur
    const rangeContainer = document.querySelector(`#${rowId} .material-range`);
    const valueDisplay = document.getElementById(`${rowId}-value`);
    
    const slider = noUiSlider.create(rangeContainer, {
        start: [0],
        connect: [true, false],
        step: 1,
        range: {
            'min': 0,
            'max': 100
        }
    });
    
    // Slider değişimini dinle
    slider.on('update', function(values, handle) {
        const value = parseInt(values[handle]);
        valueDisplay.textContent = `${value}%`;
        updateTotalPercentage();
        updateMixFilters();
    });
    
    // Kaldırma düğmesini dinle
    const removeButton = document.querySelector(`#${rowId} .material-remove`);
    removeButton.addEventListener('click', () => {
        document.getElementById(rowId).remove();
        updateTotalPercentage();
        updateMixFilters();
    });
    
    updateTotalPercentage();
    updateMixFilters();
}

// Toplam yüzdeyi güncelle
function updateTotalPercentage() {
    const materialRows = document.querySelectorAll(".material-row");
    let total = 0;
    
    materialRows.forEach(row => {
        const valueText = row.querySelector(".material-value").textContent;
        const value = parseInt(valueText);
        if (!isNaN(value)) {
            total += value;
        }
    });
    
    document.getElementById("total-percentage").textContent = total;
    
    // İlerleme çubuğunu güncelle
    const progressBar = document.getElementById("total-progress");
    progressBar.style.width = `${Math.min(100, total)}%`;
    
    // 100'ü aşarsa uyarı rengi
    if (total > 100) {
        progressBar.style.backgroundColor = "#e74c3c";
    } else {
        progressBar.style.backgroundColor = "#3366cc";
    }
}

// Karışım filtrelerini güncelle
function updateMixFilters() {
    currentMixFilters = [];
    
    const materialRows = document.querySelectorAll(".material-row");
    materialRows.forEach(row => {
        const type = row.dataset.type;
        const valueText = row.querySelector(".material-value").textContent;
        const value = parseInt(valueText);
        
        if (!isNaN(value)) {
            currentMixFilters.push({
                type: type,
                min: 0,
                max: value
            });
        }
    });
}

// Model değiştiğinde versiyonları güncelle
async function updateVersions() {
    const modelSelector = document.getElementById("model-selector");
    const versionSelector = document.getElementById("version-selector");
    currentModel = modelSelector.value;
    
    // Aktif model göstergesini güncelle
    document.getElementById("active-model-name").textContent = currentModel;
    
    try {
        const response = await fetch(`/available-versions?model=${currentModel}`);
        if (response.ok) {
            const versions = await response.json();
            
            // Versiyon selector'ı temizle ve doldur
            versionSelector.innerHTML = '';
            versions.forEach(version => {
                const option = document.createElement("option");
                option.value = version.id;
                option.textContent = version.name + (version.comment ? ` (${version.comment})` : '');
                versionSelector.appendChild(option);
            });
            
            currentVersion = versionSelector.value;
        }
    } catch (error) {
        console.error("Versiyon listesi alınırken hata:", error);
    }
}

// Benzer görselleri getir
async function fetchSimilarImages(filename) {
    try {
        // Yükleniyor mesajını göster
        document.getElementById("center-results").innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                          border-top: 4px solid #3498db; border-radius: 50%; animation: spin 2s linear infinite;"></div>
                <p style="margin-top: 10px;">Benzer görseller aranıyor...</p>
            </div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }}</style>
        `;

        // Filtre parametrelerini hazırla
        const filterParams = filterApplied ? {
            features: currentFeatures,
            mixFilters: currentMixFilters,
            cluster: clusterStatus
        } : null;
        
        // Yüklenme süresini kayıt altına al
        const startTime = performance.now();

        // API isteği gönder
        const response = await fetch(`/find-similar?filename=${encodeURIComponent(filename)}&model=${currentModel}&version=${currentVersion}&topN=${currentTopN}&metric=${currentMetric}`, {
            method: filterApplied ? 'POST' : 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            body: filterApplied ? JSON.stringify(filterParams) : undefined
        });

        const endTime = performance.now();
        const loadTime = Math.round(endTime - startTime);
        console.log(`Benzerlik araması ${loadTime}ms sürde tamamlandı`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const results = await response.json();
        
        // Eğer sonuçlar yüklendikten sonra 2 saniyeden daha az süre geçmişse,
        // sunucu yükünü azaltmak için kısa bir gecikme ekle
        const totalTime = performance.now() - startTime;
        if (totalTime < 500) {
            await new Promise(resolve => setTimeout(resolve, 500 - totalTime));
        }
        
        displaySimilarImages(results);

    } catch (error) {
        console.error("Benzer görsel getirme hatası:", error);
        document.getElementById("center-results").innerHTML = `
            <div style="text-align: center; padding: 20px; color: #e74c3c;">
                <p>Hata oluştu: ${error.message}</p>
                <button id="reset-cache" style="margin-top: 10px; padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">♻️ Önbelleği Temizle</button>
            </div>
        `;
        
        // Önbellek temizleme butonu olayı
        document.getElementById("reset-cache")?.addEventListener("click", async () => {
            try {
                // Faiss indekslerini sıfırla
                await fetch('/reset-faiss-indexes');
                
                // Sayfayı yenile
                window.location.reload();
            } catch (resetError) {
                console.error('❌ Önbellek temizleme hatası:', resetError);
            }
        });
    }
}

// Benzer görselleri göster
function displaySimilarImages(results) {
    const container = document.getElementById("center-results");
    
    // Aktif model ve versiyon bilgisini güncelle
    document.getElementById("active-model-name").textContent = currentModel;
    document.getElementById("active-version-name").textContent = currentVersion;
    document.getElementById("active-metric-name").textContent = currentMetric;
    document.getElementById("active-topn-name").textContent = currentTopN;
    
    if (!results || results.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #7f8c8d;">
                <p>Benzer görsel bulunamadı veya filtre kriterlerine uygun sonuç yok.</p>
            </div>
        `;
        return;
    }
    
    // Sonuçları HTML'e dönüştür
    let html = '';
    
    results.forEach(result => {
        const isSelected = selectedImages.has(result.filename);
        const selectedClass = isSelected ? 'selected' : '';
        const clustered = result.cluster ? 'clustered' : '';
        
        html += `
            <div class="image-box ${clustered} ${selectedClass}" data-filename="${result.filename}">
                <img src="/thumbnails/${result.filename}" alt="${result.filename}" />
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Seçilen görsel üstüne "Uyumluyu Ara" butonu ekle ve tooltip fonksiyonalitesi ekle
    document.querySelectorAll('.image-box').forEach(box => {
        const filename = box.dataset.filename;
        // Tooltip olayları ekle
        box.addEventListener('mouseenter', function(event) {
            // Button hover'ları için tooltip'i atla
            if (event.target.closest('.image-buttons')) {
              return;
            }
            
            // Önce varsa eski tooltip'leri temizle
            if (this._currentTooltip) {
                this._currentTooltip.remove();
                this._currentTooltip = null;
            }
            
            // İlgili görsele ait sonucu bul
            const result = results.find(r => r.filename === filename);
            if (!result) {
                return;
            }
            
            // Tooltip görsel boyutları
            const imgWidth = 300;
            const imgHeight = 300;
            
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
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
                <img src="/realImages/${result.filename}" alt="${result.filename}" style="width: ${imgWidth}px; max-height: ${imgHeight}px; object-fit: contain;" />
                <p>${result.filename}</p>
                <p>Benzerlik: ${(result.similarity * 100).toFixed(1)}%</p>
                ${result.design ? `<p>Desen: ${result.design}</p>` : ''}
                ${result.cluster ? `<p>Cluster: ${result.cluster}</p>` : ''}
                ${result.season ? `<p>Sezon: ${result.season}</p>` : ''}
                <div class="features">
                    ${Array.isArray(result.features) ? result.features.map(f => 
                        `<span class="feature-tag">${f[0]}: ${f[1]}%</span>`
                    ).join('') : ''}
                </div>
                <div class="feedback-stars" data-anchor="${currentFilename}" data-output="${result.filename}" data-model="${currentModel}" data-version="${currentVersion}">
                    <span class="star" data-rating="1">★</span>
                    <span class="star" data-rating="2">★</span>
                    <span class="star" data-rating="3">★</span>
                    <span class="star" data-rating="4">★</span>
                    <span class="star" data-rating="5">★</span>
                </div>
            `;
            
            // Tooltip'i document.body'e ekleyelim
            document.body.appendChild(tooltip);
            
            // Tooltip konumunu görsel kutusuna göre ayarla
            const boxRect = this.getBoundingClientRect();
            tooltip.style.top = boxRect.top + "px";
            tooltip.style.left = (boxRect.left - 310) + "px"; // Orta panelde sol tarafta göster
            
            // Viewport sınırlarını kontrol et ve gerekirse konumu ayarla
            setTimeout(() => {
              const rect = tooltip.getBoundingClientRect();
              if (rect.left < 0) {
                tooltip.style.left = (boxRect.right + 10) + "px";
              }
              if (rect.bottom > window.innerHeight) {
                tooltip.style.top = (window.innerHeight - rect.height - 10) + "px";
              }
            }, 0);
            
            // Tooltip'i mouseleave olayında kaldırmak için kaydedelim
            this._currentTooltip = tooltip;
            
            // Derecelendirme işlemlerini ayarla
            setupFeedbackListenersForElement(tooltip);
        });
        
        box.addEventListener('mouseleave', function() {
            if (this._currentTooltip) {
                this._currentTooltip.remove();
                this._currentTooltip = null;
            }
        });
        
        // Alt kısma buton eklemek için container oluştur
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'image-buttons';
        
        // Uyumluyu Ara butonu ekle
        const findHarmoniousButton = document.createElement('button');
        findHarmoniousButton.textContent = 'Uyumluyu Ara';
        findHarmoniousButton.className = 'find-harmonious-btn';
        
        findHarmoniousButton.addEventListener('click', (e) => {
            e.stopPropagation();
            showHarmoniousSearchModal(filename);
        });
        
        // Karşılaştırma butonu ekle
        const compareButton = document.createElement('button');
        compareButton.textContent = 'Karşılaştır';
        compareButton.className = 'compare-btn';
        
        compareButton.addEventListener('click', (e) => {
            e.stopPropagation();
            addToCompareList(filename, result);
        });
        
        buttonContainer.appendChild(findHarmoniousButton);
        buttonContainer.appendChild(compareButton);
        box.appendChild(buttonContainer);
    });
    
    // Derecelendirme olaylarını ekle
    setupFeedbackListeners();
}

// Derecelendirme olay dinleyicilerini ekle - tüm tooltip elementleri için
function setupFeedbackListeners() {
    // Tüm tooltipleri bul
    document.querySelectorAll('.tooltip').forEach(tooltip => {
        setupFeedbackListenersForElement(tooltip);
    });
}

// Belirli bir tooltip elementi için feedback dinleyicileri ekle
function setupFeedbackListenersForElement(tooltipElement) {
    // Tooltip içindeki yıldızları seç
    const stars = tooltipElement.querySelectorAll('.feedback-stars .star');
    
    // Her yıldıza tıklama olayı ekle
    stars.forEach(star => {
        // Eğer zaten bir event listener eklenmiş mi kontrol et
        if (star.getAttribute('data-has-click-listener') === 'true') return;
        
        star.addEventListener('click', async (e) => {
            e.stopPropagation();
            
            const rating = parseInt(star.dataset.rating);
            const starsContainer = star.parentElement;
            const anchor = starsContainer.dataset.anchor;
            const output = starsContainer.dataset.output;
            const model = starsContainer.dataset.model;
            const version = starsContainer.dataset.version;
            
            // Tüm yıldızları temizle
            starsContainer.querySelectorAll('.star').forEach(s => {
                s.classList.remove('active');
            });
            
            // Seçilen yıldıza kadar tümünü aktifleştir
            for (let i = 1; i <= rating; i++) {
                starsContainer.querySelector(`.star[data-rating="${i}"]`).classList.add('active');
            }
            
            // Feedback'i sunucuya gönder
            try {
                const response = await fetch('/submit-feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        anchor,
                        output,
                        model,
                        version,
                        feedback: rating
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                console.log(`Feedback kaydedildi: ${anchor} → ${output} = ${rating} yıldız`);
            } catch (error) {
                console.error('Feedback gönderirken hata:', error);
            }
        });
        
        // Event listener eklendiğini işaretle
        star.setAttribute('data-has-click-listener', 'true');
        
        // Hover olayları
        star.addEventListener('mouseenter', () => {
            const rating = parseInt(star.dataset.rating);
            const starsContainer = star.parentElement;
            
            // Hover'da olan yıldıza kadar tümünü aktifleştir
            starsContainer.querySelectorAll('.star').forEach(s => {
                if (parseInt(s.dataset.rating) <= rating) {
                    s.classList.add('hover');
                } else {
                    s.classList.remove('hover');
                }
            });
        });
    });
    
    // Stars container için mouseleave olayı
    const starsContainer = tooltipElement.querySelector('.feedback-stars');
    if (starsContainer && !starsContainer.getAttribute('data-has-mouseleave')) {
        starsContainer.addEventListener('mouseleave', () => {
            // Hover'dan çıkınca tüm hover sınıfını kaldır
            starsContainer.querySelectorAll('.star').forEach(s => {
                s.classList.remove('hover');
            });
        });
        starsContainer.setAttribute('data-has-mouseleave', 'true');
    }
}

// Görsel tıklama olayını işle
function handleImageClick(event) {
    // En yakın görsel kutusunu bul
    const imageBox = event.target.closest('.image-box');
    if (!imageBox) return;
    
    // Görsel dosya adını al
    const filename = imageBox.dataset.filename;
    
    // Bu görsele tıklanmış mı kontrol et
    if (imageBox.classList.contains('selected')) {
        // Seçimi kaldır
        imageBox.classList.remove('selected');
        selectedImages.delete(filename);
        
        // Görsel tıklama olayını yetkilendirilen fonksiyona ilet
        if (typeof window.handleCenterPanelImageDeselect === "function") {
            window.handleCenterPanelImageDeselect(filename);
        }
    } else {
        // Seçim ekle
        imageBox.classList.add('selected');
        selectedImages.add(filename);
        
        // Görsel tıklama olayını yetkilendirilen fonksiyona ilet
        if (typeof window.handleCenterPanelImageSelect === "function") {
            window.handleCenterPanelImageSelect(filename);
        }
    }
}

// Sol paneldeki görsel tıklandığında (global çağrı için)
function showSimilarImages(filename) {
    if (filename) {
        currentFilename = filename;
        fetchSimilarImages(filename);
    }
}

// Seçili görselleri döndür
function getSelectedImages() {
    return Array.from(selectedImages);
}

// Seçili görselleri temizle
function clearSelectedImages() {
    selectedImages.clear();
    document.querySelectorAll('.image-box.selected').forEach(box => {
        box.classList.remove('selected');
    });
}

// Global fonksiyonları dışa aktar
window.showSimilarImages = showSimilarImages;
window.getSelectedImages = getSelectedImages;
window.clearSelectedImages = clearSelectedImages;
window.findHarmoniousColors = findHarmoniousColors;
window.showHarmoniousSearchModal = showHarmoniousSearchModal;
window.addToCompareList = addToCompareList;

// Uyumlu renk arama modal arayüzünü göster
function showHarmoniousSearchModal(fabricId) {
    // Varsa önceki modalı kaldır
    const existingModal = document.getElementById('harmonious-search-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Modal overlay oluştur
    const modalOverlay = document.createElement('div');
    modalOverlay.id = 'harmonious-search-modal';
    modalOverlay.style.position = 'fixed';
    modalOverlay.style.top = '0';
    modalOverlay.style.left = '0';
    modalOverlay.style.width = '100%';
    modalOverlay.style.height = '100%';
    modalOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modalOverlay.style.display = 'flex';
    modalOverlay.style.justifyContent = 'center';
    modalOverlay.style.alignItems = 'center';
    modalOverlay.style.zIndex = '9999';
    
    // Modal içerik
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.borderRadius = '8px';
    modalContent.style.padding = '20px';
    modalContent.style.width = '500px';
    modalContent.style.maxWidth = '90%';
    modalContent.style.maxHeight = '90%';
    modalContent.style.overflowY = 'auto';
    modalContent.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
    
    // Görsel bilgisini al
    let imgSrc = '';
    
    try {
        // Önce thumbnail'i kontrol et
        imgSrc = `/thumbnails/${fabricId}`;
    } catch (error) {
        console.error('Görsel bilgisi alınamadı:', error);
    }
    
    // Modal başlık ve içerik
    modalContent.innerHTML = `
        <div style="border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px;">
            <h3 style="margin-top: 0; color: #2c3e50; display: flex; justify-content: space-between; align-items: center;">
                <span>Uyumlu Renk Arama Parametreleri</span>
                <button id="close-harmony-modal" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #7f8c8d;">&times;</button>
            </h3>
        </div>
        
        <div style="display: flex; margin-bottom: 20px;">
            <div style="flex: 0 0 100px; margin-right: 15px;">
                <img src="${imgSrc}" alt="${fabricId}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;">
            </div>
            <div style="flex: 1;">
                <p style="margin-top: 0; color: #34495e; font-weight: bold;">${fabricId}</p>
                <p style="margin-bottom: 5px; font-size: 14px; color: #7f8c8d;">Seçilen kumaşın dominant rengine göre uyumlu renklere sahip diğer kumaşları bulur.</p>
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #2c3e50;">Uyum Tipi</label>
            <select id="harmony-type-select" style="width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #ddd;">
                <option value="complementary" selected>Tamamlayıcı (Complementary)</option>
                <option value="analogous">Analog (Analogous)</option>
                <option value="triadic">Triadik (Triadic)</option>
                <option value="split_complementary">Ayrık Tamamlayıcı (Split Complementary)</option>
                <option value="monochromatic">Monokromatik (Monochromatic)</option>
            </select>
            <p style="margin-top: 5px; font-size: 12px; color: #7f8c8d;" id="harmony-description">Tamamlayıcı: Renk çemberinde 180° karşı olan renkler</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #2c3e50;">Benzerlik Eşiği (%)</label>
            <div style="display: flex; align-items: center;">
                <input type="range" id="similarity-threshold" min="50" max="100" value="80" style="flex: 1; margin-right: 10px;">
                <span id="threshold-value" style="font-weight: bold; min-width: 40px;">80%</span>
            </div>
            <p style="margin-top: 5px; font-size: 12px; color: #7f8c8d;">Daha yüksek değer daha kesin eşleşmeler sağlar</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #2c3e50;">Sonuç Sayısı</label>
            <input type="number" id="result-count" min="5" max="100" value="20" style="width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #ddd;">
            <p style="margin-top: 5px; font-size: 12px; color: #7f8c8d;">Gösterilecek maksimum sonuç sayısı</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #2c3e50;">Filtreleme Seçenekleri</label>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <label style="display: flex; align-items: center; font-size: 14px; color: #34495e;">
                    <input type="checkbox" id="current-season-only" style="margin-right: 5px;">
                    Sadece aynı sezon
                </label>
                <label style="display: flex; align-items: center; font-size: 14px; color: #34495e;">
                    <input type="checkbox" id="current-quality-only" style="margin-right: 5px;">
                    Sadece aynı kalite
                </label>
            </div>
        </div>
        
        <div style="text-align: right; border-top: 1px solid #eee; padding-top: 15px; margin-top: 15px;">
            <button id="cancel-harmony-search" style="padding: 10px 15px; background-color: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">İptal</button>
            <button id="start-harmony-search" style="padding: 10px 15px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">Aramayı Başlat</button>
        </div>
    `;
    
    modalOverlay.appendChild(modalContent);
    document.body.appendChild(modalOverlay);
    
    // Uyum tipi açıklamasını güncelle
    const harmonyTypeSelect = document.getElementById('harmony-type-select');
    const harmonyDescription = document.getElementById('harmony-description');
    
    harmonyTypeSelect.addEventListener('change', () => {
        switch (harmonyTypeSelect.value) {
            case 'complementary':
                harmonyDescription.textContent = 'Tamamlayıcı: Renk çemberinde 180° karşı olan renkler';
                break;
            case 'analogous':
                harmonyDescription.textContent = 'Analog: Renk çemberinde yan yana olan renkler (±30°)';
                break;
            case 'triadic':
                harmonyDescription.textContent = 'Triadik: Renk çemberinde eşit aralıklı üç renk (120° aralıklarla)';
                break;
            case 'split_complementary':
                harmonyDescription.textContent = 'Ayrık Tamamlayıcı: Tamamlayıcı rengin her iki yanından 30° uzaktaki renkler';
                break;
            case 'monochromatic':
                harmonyDescription.textContent = 'Monokromatik: Aynı rengin farklı ton ve değerleri';
                break;
        }
    });
    
    // Eşik değeri gösterimini güncelle
    const thresholdSlider = document.getElementById('similarity-threshold');
    const thresholdValue = document.getElementById('threshold-value');
    
    thresholdSlider.addEventListener('input', () => {
        thresholdValue.textContent = `${thresholdSlider.value}%`;
    });
    
    // Modal kapatma fonksiyonu
    const closeModal = () => {
        modalOverlay.remove();
        document.removeEventListener('keydown', handleEscKey);
    };
    
    document.getElementById('close-harmony-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-harmony-search').addEventListener('click', closeModal);
    
    // ESC tuşu ile kapatma
    const handleEscKey = function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('harmonious-search-modal');
            if (modal) {
                modal.remove();
                document.removeEventListener('keydown', handleEscKey);
            }
        }
    };
    document.addEventListener('keydown', handleEscKey);
    
    // Aramayı başlat
    document.getElementById('start-harmony-search').addEventListener('click', () => {
        const harmonyType = document.getElementById('harmony-type-select').value;
        const threshold = document.getElementById('similarity-threshold').value;
        const resultCount = document.getElementById('result-count').value;
        const currentSeasonOnly = document.getElementById('current-season-only').checked;
        const currentQualityOnly = document.getElementById('current-quality-only').checked;
        
        // Modalı kapat
        closeModal();
        
        // Aramayı başlat
        findHarmoniousColors(fabricId, {
            harmonyType,
            threshold,
            resultCount,
            currentSeasonOnly,
            currentQualityOnly
        });
    });
}

// Uyumlu renkleri bulan fonksiyon
async function findHarmoniousColors(fabricId, options = {}) {
    try {
        // Yükleniyor mesajını göster
        document.getElementById("center-results").innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                          border-top: 4px solid #3498db; border-radius: 50%; animation: spin 2s linear infinite;"></div>
                <p style="margin-top: 10px;">Uyumlu renkler aranıyor...</p>
            </div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }}</style>
        `;

        // Parametreleri al veya varsayılanları kullan
        const harmonyType = options.harmonyType || "complementary";
        const threshold = options.threshold || "80";
        const resultCount = options.resultCount || "20";
        const currentSeasonOnly = options.currentSeasonOnly || false;
        const currentQualityOnly = options.currentQualityOnly || false;

        // API isteği gönder - URL parametreleri oluştur
        let url = `/find-harmonious?fabricId=${encodeURIComponent(fabricId)}&harmonyType=${harmonyType}`;
        
        // Ek parametreleri ekle
        url += `&threshold=${threshold}&resultCount=${resultCount}`;
        if (currentSeasonOnly) url += '&currentSeasonOnly=true';
        if (currentQualityOnly) url += '&currentQualityOnly=true';
        
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === "success") {
            displayHarmoniousResults(result, fabricId);
        } else {
            throw new Error(result.message || "Uyumlu renkler bulunamadı");
        }

    } catch (error) {
        console.error("Uyumlu renk arama hatası:", error);
        document.getElementById("center-results").innerHTML = `
            <div style="text-align: center; padding: 20px; color: #e74c3c;">
                <p>Hata oluştu: ${error.message}</p>
            </div>
        `;
    }
}

// Uyumlu renk sonuçlarını gösterme
function displayHarmoniousResults(result, referenceId) {
    const container = document.getElementById("center-results");
    
    if (!result.results || result.results.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #7f8c8d;">
                <p>Uyumlu renkli görsel bulunamadı.</p>
                <button id="back-to-similar" style="margin-top: 10px; padding: 8px 15px;">⬅️ Benzer Görsellere Dön</button>
            </div>
        `;
        
        document.getElementById("back-to-similar").addEventListener("click", () => {
            fetchSimilarImages(currentFilename);
        });
        
        return;
    }
    
    // Referans renk ve uyumlu renkleri göster
    const referenceColor = result.reference_color;
    const harmonyColors = result.harmony_colors;
    const harmonyType = result.harmony_type;
    
    let headerHtml = `
        <div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #2c3e50;">Uyumlu Renk Sonuçları</h3>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="font-weight: bold; margin-right: 10px;">Referans Görsel:</div>
                <img src="/thumbnails/${referenceId}" alt="${referenceId}" 
                     style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; margin-right: 15px;">
                <div style="display: flex; align-items: center;">
                    <div style="font-weight: bold; margin-right: 10px;">Dominant Renk:</div>
                    <div class="color-box" style="width: 30px; height: 30px; background-color: rgb(${referenceColor[0]}, ${referenceColor[1]}, ${referenceColor[2]}); 
                          border-radius: 50%; border: 2px solid #ddd; cursor: help;" 
                          title="Referans Renk - RGB: ${referenceColor[0]}, ${referenceColor[1]}, ${referenceColor[2]}"></div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="font-weight: bold; margin-right: 10px;">Uyum Tipi:</div>
                <div style="background-color: #e7f4ff; padding: 4px 8px; border-radius: 4px; font-size: 14px;">
                    ${harmonyType === "complementary" ? "Tamamlayıcı" : 
                      harmonyType === "analogous" ? "Analog" : 
                      harmonyType === "triadic" ? "Triadik" : 
                      harmonyType === "split_complementary" ? "Ayrık Tamamlayıcı" : harmonyType}
                </div>
            </div>
            
            <div style="display: flex; align-items: center;">
                <div style="font-weight: bold; margin-right: 10px;">Uyumlu Renkler:</div>
                <div style="display: flex; gap: 10px;">
                    ${harmonyColors.map(color => `
                        <div class="color-box" style="width: 30px; height: 30px; background-color: rgb(${color[0]}, ${color[1]}, ${color[2]}); 
                              border-radius: 50%; border: 2px solid #ddd; cursor: help;" 
                              title="Uyumlu Renk - RGB: ${color[0]}, ${color[1]}, ${color[2]}"></div>
                    `).join('')}
                </div>
            </div>
            
            <div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                <button id="back-to-similar" style="padding: 8px 15px; background-color: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;">⬅️ Benzer Görsellere Dön</button>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <div class="tooltip-container" style="position: relative; display: inline-block;">
                        <span style="font-size: 14px; color: #555; margin-right: 5px;">Uyum Tipi:</span>
                        <select id="harmony-type-selector" style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                            <option value="complementary" ${harmonyType === "complementary" ? "selected" : ""} title="Renk çemberinde birbirine 180 derece karşı olan renkler">Tamamlayıcı</option>
                            <option value="analogous" ${harmonyType === "analogous" ? "selected" : ""} title="Renk çemberinde yan yana (30 derece aralıkla) bulunan renkler">Analog</option>
                            <option value="triadic" ${harmonyType === "triadic" ? "selected" : ""} title="Renk çemberinde eşit aralıklarla (120 derece) yerleştirilmiş üç renk">Triadik</option>
                            <option value="split_complementary" ${harmonyType === "split_complementary" ? "selected" : ""} title="Tamamlayıcı rengin her iki yanından 30 derece uzaklıktaki renkler">Ayrık Tamamlayıcı</option>
                        </select>
                        <div class="tooltip-info" style="position: absolute; top: -90px; left: 50%; transform: translateX(-50%); background-color: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; width: 250px; z-index: 100; display: none;">
                            <p style="margin: 0; font-size: 12px;">Seçilen kumaşın rengiyle uyumlu renkleri bulmak için kullanılan yöntemi belirler:</p>
                            <ul style="margin: 5px 0 0 15px; padding: 0; font-size: 11px;">
                                <li><strong>Tamamlayıcı:</strong> Renk çemberinde 180° karşı olan renkler</li>
                                <li><strong>Analog:</strong> Renk çemberinde yan yana olan renkler (30° aralıklarla)</li>
                                <li><strong>Triadik:</strong> Renk çemberinde 120° aralıklarla yerleşen renkler</li>
                                <li><strong>Ayrık Tamamlayıcı:</strong> Tamamlayıcı rengin her iki yanından 30° uzaktaki renkler</li>
                            </ul>
                        </div>
                    </div>
                    <button id="update-harmony" style="padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">🔄 Yenile</button>
                </div>
            </div>
        </div>
    `;
    
    // Sonuçları HTML'e dönüştür
    let resultsHtml = '<div class="image-grid" style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center;">';
    
    result.results.forEach(item => {
        const dominantColor = item.dominant_color;
        const harmonyColor = item.harmony_color;
        const similarity = item.similarity;
        
        resultsHtml += `
            <div class="harmony-result" style="width: 180px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                  border: 1px solid #eee; transition: transform 0.2s; cursor: pointer;"
                 data-filename="${item.filename}" 
                 onmouseover="this.style.transform='scale(1.03)'" 
                 onmouseout="this.style.transform='scale(1)'">
                <img src="/thumbnails/${item.filename}" alt="${item.filename}" 
                     style="width: 100%; height: 150px; object-fit: cover;">
                <div style="padding: 10px;">
                    <div style="font-size: 12px; color: #555; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" 
                         title="${item.filename}">${item.filename}</div>
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div class="color-box" style="width: 16px; height: 16px; background-color: rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]}); 
                              border-radius: 50%; margin-right: 8px; border: 1px solid #ddd; cursor: help;" 
                              title="Dominant Renk - RGB: ${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]}"></div>
                        <div style="font-size: 12px;">→</div>
                        <div class="color-box" style="width: 16px; height: 16px; background-color: rgb(${harmonyColor[0]}, ${harmonyColor[1]}, ${harmonyColor[2]}); 
                              border-radius: 50%; margin-left: 8px; border: 1px solid #ddd; cursor: help;"
                              title="Uyumlu Renk - RGB: ${harmonyColor[0]}, ${harmonyColor[1]}, ${harmonyColor[2]}"></div>
                    </div>
                    <div style="font-size: 12px; color: #555;">
                        <span style="color: ${similarity > 0.9 ? '#27ae60' : similarity > 0.85 ? '#2980b9' : '#e67e22'}; font-weight: bold;">
                            ${Math.round(similarity * 100)}%
                        </span> benzerlik
                    </div>
                    ${item.design ? `<div style="font-size: 11px; color: #777; margin-top: 5px;">Desen: ${item.design}</div>` : ''}
                </div>
            </div>
        `;
    });
    
    resultsHtml += '</div>';
    
    // Tam HTML'i oluştur
    container.innerHTML = headerHtml + resultsHtml;
    
    document.getElementById("back-to-similar").addEventListener("click", () => {
        fetchSimilarImages(currentFilename);
    });
    
    // Yenile butonu olayı
    document.getElementById("update-harmony").addEventListener("click", () => {
        const selectedHarmonyType = document.getElementById("harmony-type-selector").value;
        findHarmoniousColorsWithType(referenceId, selectedHarmonyType);
    });
    
    // Sonuç görseli tıklama olayı
    document.querySelectorAll(".harmony-result").forEach(result => {
        result.addEventListener("click", () => {
            const filename = result.dataset.filename;
            window.open(`/realImages/${filename}`, '_blank');
        });
    });
    
    // Tooltip üzerinde fare gezdirme işlevleri
    document.querySelectorAll('.tooltip-container').forEach(container => {
        container.addEventListener('mouseenter', function() {
            this.querySelector('.tooltip-info').style.display = 'block';
        });
        
        container.addEventListener('mouseleave', function() {
            this.querySelector('.tooltip-info').style.display = 'none';
        });
    });
    
    // Renk örnekleri için bilgi balonları
    document.querySelectorAll('.harmony-result').forEach(result => {
        const colorBoxes = result.querySelectorAll('div[style*="background-color"]');
        
        colorBoxes.forEach(box => {
            // RGB değerini al
            const style = box.getAttribute('style');
            const rgbMatch = style.match(/background-color: rgb\((\d+), (\d+), (\d+)\)/);
            
            if (rgbMatch) {
                const r = rgbMatch[1];
                const g = rgbMatch[2];
                const b = rgbMatch[3];
                
                // Hex renk kodunu hesapla
                const toHex = (c) => {
                    const hex = parseInt(c).toString(16);
                    return hex.length === 1 ? '0' + hex : hex;
                };
                
                const hexColor = `#${toHex(r)}${toHex(g)}${toHex(b)}`;
                
                // Title ekleyerek bilgi göster
                box.setAttribute('title', `RGB: ${r}, ${g}, ${b} | HEX: ${hexColor.toUpperCase()}`);
            }
        });
    });
}

// Belirli bir uyum tipinde uyumlu renkleri arama
async function findHarmoniousColorsWithType(fabricId, harmonyType) {
    try {
        // Yükleniyor mesajını göster
        document.getElementById("center-results").innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                          border-top: 4px solid #3498db; border-radius: 50%; animation: spin 2s linear infinite;"></div>
                <p style="margin-top: 10px;">Uyumlu renkler aranıyor...</p>
            </div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }}</style>
        `;

        // API isteği gönder
        const response = await fetch(`/find-harmonious?fabricId=${encodeURIComponent(fabricId)}&harmonyType=${harmonyType}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === "success") {
            displayHarmoniousResults(result, fabricId);
        } else {
            throw new Error(result.message || "Uyumlu renkler bulunamadı");
        }

    } catch (error) {
        console.error("Uyumlu renk arama hatası:", error);
        document.getElementById("center-results").innerHTML = `
            <div style="text-align: center; padding: 20px; color: #e74c3c;">
                <p>Hata oluştu: ${error.message}</p>
                <button id="back-to-similar" style="margin-top: 10px; padding: 8px 15px;">⬅️ Benzer Görsellere Dön</button>
            </div>
        `;
        
        document.getElementById("back-to-similar").addEventListener("click", () => {
            fetchSimilarImages(currentFilename);
        });
    }
}
