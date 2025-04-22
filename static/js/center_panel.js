// center_panel.js
// Oluşturulma: 2025-04-19
// Hazırlayan: Kafkas

// Açıklama:
// Orta panelde, seçilen görsele göre benzer desenleri gösteren dinamik yapı.
// Filtre sırası seçimine göre (önce filtre mi, önce benzerlik mi) davranış ayarlanabilir.

let centerContainer;
const materialRows = new Map();

window.populateMaterialDropdown = function () {
  const selector = document.getElementById("material-selector");
  if (!selector || !window.blendSet) return;

  selector.innerHTML = "";

  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Hammadde Seçin";
  selector.appendChild(defaultOption);

  window.blendSet.forEach(htype => {
    const opt = document.createElement("option");
    opt.value = htype;
    opt.textContent = htype;
    selector.appendChild(opt);
  });
};

function createStarRating(outputFilename, anchorFilename, model, version) {
  const container = document.createElement("div");
  container.className = "star-rating";
  container.style.display = "flex";
  container.style.justifyContent = "center";
  container.style.marginTop = "8px";
  container.style.position = "absolute";
  container.style.bottom = "5px";
  container.style.left = "50%";
  container.style.transform = "translateX(-50%)";
  container.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
  container.style.padding = "2px 5px";
  container.style.borderRadius = "4px";
  container.style.zIndex = "5";
  container.classList.add("no-tooltip");
  container.style.pointerEvents = "auto";

  let currentRating = 0;

  function sendFeedback(rating) {
    const feedback = {
      anchor: anchorFilename,
      output: outputFilename,
      model: model,
      version: version,
      feedback: rating,
      user_id: "",
      user_role: ""
    };

    fetch("/submit-feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedback)
    })
      .then(res => res.json())
      .then(data => {
        console.log("✅ Feedback gönderildi:", data);
      })
      .catch(err => {
        console.error("❌ Feedback gönderilemedi:", err);
      });
  }

  for (let i = 1; i <= 5; i++) {
    const star = document.createElement("span");
    star.textContent = "☆";
    star.style.cursor = "pointer";
    star.style.fontSize = "20px";
    star.style.margin = "0 2px";
    star.style.pointerEvents = "auto";

    star.addEventListener("click", (e) => {
      e.stopPropagation();
      if (currentRating === i) {
        currentRating = 0;
        container.querySelectorAll("span").forEach(s => s.textContent = "☆");
        sendFeedback(null);
      } else {
        currentRating = i;
        container.querySelectorAll("span").forEach((s, idx) => {
          s.textContent = idx < i ? "★" : "☆";
        });
        sendFeedback(i);
      }
    });

    container.appendChild(star);
  }

  return container;
}


window.addMaterialFilter = function (materialType) {
  if (!materialType || materialRows.has(materialType)) return;

  const container = document.createElement("div");
  container.className = "material-filter-row";
  container.style.display = "grid";
  container.style.gridTemplateColumns = "100px 1fr 60px 30px";
  container.style.alignItems = "center";
  container.style.marginBottom = "10px";
  container.style.padding = "5px";
  container.style.backgroundColor = "#f9f9f9";
  container.style.borderRadius = "4px";

  const name = document.createElement("span");
  name.textContent = materialType;
  name.style.fontWeight = "bold";

  const sliderContainer = document.createElement("div");
  sliderContainer.style.margin = "0 10px";

  const sliderDiv = document.createElement("div");
  sliderDiv.className = "nouislider-container";

  const valueDisplay = document.createElement("div");
  valueDisplay.className = "range-value-display";
  valueDisplay.style.display = "flex";
  valueDisplay.style.justifyContent = "space-between";
  valueDisplay.style.fontSize = "12px";
  valueDisplay.style.color = "#666";
  valueDisplay.style.marginTop = "2px";
  valueDisplay.innerHTML = '<span>0%</span><span>100%</span>';

  const minInput = document.createElement("input");
  minInput.type = "hidden";
  minInput.className = "karisim-min";
  minInput.value = "0";

  const maxInput = document.createElement("input");
  maxInput.type = "hidden";
  maxInput.className = "karisim-max";
  maxInput.value = "100";

  const valueText = document.createElement("span");
  valueText.textContent = "0-100%";
  valueText.style.textAlign = "center";

  const removeBtn = document.createElement("button");
  removeBtn.textContent = "×";
  removeBtn.style.cursor = "pointer";
  removeBtn.style.border = "none";
  removeBtn.style.background = "none";
  removeBtn.style.fontSize = "18px";
  removeBtn.style.color = "#f44336";
  removeBtn.title = "Kaldır";
  removeBtn.onclick = () => {
    materialRows.delete(materialType);
    container.remove();
  };

  sliderContainer.appendChild(sliderDiv);
  sliderContainer.appendChild(valueDisplay);

  container.appendChild(name);
  container.appendChild(sliderContainer);
  container.appendChild(valueText);
  container.appendChild(removeBtn);
  container.appendChild(minInput);
  container.appendChild(maxInput);

  document.getElementById("material-rows").appendChild(container);

  if (window.noUiSlider) {
    noUiSlider.create(sliderDiv, {
      start: [0, 100],
      connect: true,
      range: {
        'min': 0,
        'max': 100
      },
      step: 1,
      format: {
        to: value => Math.round(value),
        from: value => Number(value)
      }
    });

    sliderDiv.noUiSlider.on("update", (values) => {
      const min = parseInt(values[0]);
      const max = parseInt(values[1]);
      minInput.value = min;
      maxInput.value = max;
      valueText.textContent = `${min}-${max}%`;
      valueDisplay.innerHTML = `<span>${min}%</span><span>${max}%</span>`;
    });
  } else {
    console.warn("noUiSlider kütüphanesi bulunamadı!");
    // Fallback to basic inputs if noUiSlider is not available
    const rangeInputs = document.createElement("div");
    rangeInputs.style.display = "flex";
    rangeInputs.style.gap = "10px";
    
    const minRange = document.createElement("input");
    minRange.type = "range";
    minRange.min = "0";
    minRange.max = "100";
    minRange.value = "0";
    minRange.style.flex = "1";
    
    const maxRange = document.createElement("input");
    maxRange.type = "range";
    maxRange.min = "0";
    maxRange.max = "100";
    maxRange.value = "100";
    maxRange.style.flex = "1";
    
    minRange.addEventListener("input", () => {
      const min = parseInt(minRange.value);
      const max = parseInt(maxRange.value);
      if (min > max) maxRange.value = min;
      minInput.value = min;
      valueText.textContent = `${min}-${parseInt(maxRange.value)}%`;
    });
    
    maxRange.addEventListener("input", () => {
      const min = parseInt(minRange.value);
      const max = parseInt(maxRange.value);
      if (max < min) minRange.value = max;
      maxInput.value = max;
      valueText.textContent = `${parseInt(minRange.value)}-${max}%`;
    });
    
    sliderContainer.innerHTML = "";
    sliderContainer.appendChild(rangeInputs);
  }

  materialRows.set(materialType, { minInput, maxInput });
};

window.loadSimilarImages = function loadSimilarImages(selectedFilename, model = "pattern", topN = 10, metric = "cosine", customFilters = null) {
  if (!centerContainer) {
    console.warn("❌ centerContainer tanımlı değil.");
    return;
  }

  centerContainer.innerHTML = "🔁 Benzer görseller yükleniyor...";
  window.currentSelectedImage = selectedFilename;
  const version = document.getElementById("version-selector")?.value || "v1";
  const preFilterEnabled = document.getElementById("center-pre-filter")?.checked;
  const filters = customFilters || (preFilterEnabled && typeof window.getFilterParams === "function" ? getFilterParams() : null);

  fetch(`/find-similar?filename=${encodeURIComponent(selectedFilename)}&model=${model}&topN=${topN}&metric=${metric}`, {
    method: filters ? "POST" : "GET",
    headers: filters ? { "Content-Type": "application/json" } : {},
    body: filters ? JSON.stringify(filters) : null
  })
    .then(res => res.json())
    .then(results => {
      centerContainer.innerHTML = "";

      if (!Array.isArray(results) || results.length === 0) {
        centerContainer.innerHTML = "Sonuç bulunamadı.";
        return;
      }

      results.forEach(result => {
        const featureMap = Object.fromEntries(result.features || []);
        const box = document.createElement("div");
        box.className = "image-box";
        box.style.position = "relative";
        box.dataset.featureMap = JSON.stringify(featureMap);
        box.dataset.cluster = result.cluster || "";

        const img = document.createElement("img");
        img.src = `thumbnails/${result.filename}`;
        img.loading = "lazy";
        img.alt = result.filename;

        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        const blendText = result.features?.map(f => `${f[0]} (${f[1]}%)`).join(", ") || "Yok";
        tooltip.innerHTML = `
          <img src='realImages/${result.filename}' />
          <strong>${result.design}</strong><br>
          Season: ${result.season}<br>
          Quality: ${result.quality}<br>
          Blend: ${blendText}<br>
          Cluster: ${result.cluster || 'Yok'}<br>
          Similarity: ${result.similarity?.toFixed(3) || '—'}
        `;

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.style.position = "absolute";
        checkbox.style.top = "5px";
        checkbox.style.right = "5px";
        checkbox.checked = window.selectedImages.includes(result.filename);

        checkbox.addEventListener("change", () => {
          if (checkbox.checked) {
            if (!window.selectedImages.includes(result.filename)) {
              window.selectedImages.push(result.filename);
            }
          } else {
            window.selectedImages = window.selectedImages.filter(f => f !== result.filename);
          }
        });

        const starRating = createStarRating(result.filename, selectedFilename, model, version);

        box.appendChild(img);
        box.appendChild(tooltip);
        box.appendChild(checkbox);
        box.appendChild(starRating);
        centerContainer.appendChild(box);
      });
    })
    .catch(err => {
      centerContainer.innerText = `❌ Benzer görseller yüklenemedi: ${err}`;
      console.error(err);
    });
};

window.applyAllFilters = function () {
  if (!window.currentSelectedImage) {
    centerContainer.innerHTML = "Lütfen önce sol panelden bir görsel seçin.";
    return;
  }

  const model = document.getElementById("model-selector")?.value || "pattern";
  const version = document.getElementById("version-selector")?.value || "v1";
  const metric = document.getElementById("metric-selector")?.value || "cosine";
  const topN = parseInt(document.getElementById("topn-input")?.value || "10");
  const filters = typeof window.getFilterParams === "function" ? window.getFilterParams() : null;

  window.loadSimilarImages(window.currentSelectedImage, model, topN, metric, filters);
};

window.addEventListener("DOMContentLoaded", function () {
  centerContainer = document.getElementById("center-results");
  window.selectedImages = [];
  window.currentSelectedImage = null;

  const toggleButton = document.getElementById("toggle-search-panel");
  const searchPanelContent = document.getElementById("search-panel-content");

  if (toggleButton && searchPanelContent) {
    toggleButton.addEventListener("click", function () {
      const isVisible = searchPanelContent.style.display !== "none";
      searchPanelContent.style.display = isVisible ? "none" : "block";
      toggleButton.textContent = isVisible ? "▼" : "▲";
    });
  }

  const applyBtn = document.getElementById("apply-filters");
  if (applyBtn) {
    applyBtn.addEventListener("click", () => {
      if (typeof window.applyAllFilters === "function") {
        window.applyAllFilters();
      } else {
        console.warn("⛔ applyAllFilters fonksiyonu tanımlı değil.");
      }
    });
  }
  
  // Reset filters button functionality
  const resetBtn = document.getElementById("reset-filters");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      // Reset feature checkboxes
      document.querySelectorAll('.feature-checkbox').forEach(checkbox => {
        checkbox.checked = false;
      });
      
      // Reset cluster radio buttons
      const defaultClusterRadio = document.querySelector('input[name="center-cluster"][value=""]');
      if (defaultClusterRadio) defaultClusterRadio.checked = true;
      
      // Reset material filters
      document.getElementById("material-rows").innerHTML = "";
      materialRows.clear();
      
      // Reset material selector
      const materialSelector = document.getElementById("material-selector");
      if (materialSelector) materialSelector.value = "";
      
      console.log("✅ Filtreler sıfırlandı.");
    });
  }

  const addBtn = document.getElementById("add-material");
  if (addBtn) {
    addBtn.addEventListener("click", () => {
      const selector = document.getElementById("material-selector");
      const materialType = selector?.value;
      if (materialType && typeof window.addMaterialFilter === "function") {
        window.addMaterialFilter(materialType);
      }
    });
  }
  
  // Implement getFilterParams function to collect all filter parameters
  window.getFilterParams = function() {
    // Get selected features
    const selectedFeatures = [];
    document.querySelectorAll('.feature-checkbox:checked').forEach(checkbox => {
      selectedFeatures.push(checkbox.value);
    });
    
    // Get cluster status
    let clusterStatus = "";
    document.querySelectorAll('input[name="center-cluster"]').forEach(radio => {
      if (radio.checked && radio.value) {
        clusterStatus = radio.value;
      }
    });
    
    // Get material filters
    const mixFilters = [];
    materialRows.forEach((inputs, materialType) => {
      mixFilters.push({
        type: materialType,
        min: parseInt(inputs.minInput.value || 0),
        max: parseInt(inputs.maxInput.value || 100)
      });
    });
    
    return {
      features: selectedFeatures,
      cluster: clusterStatus,
      mixFilters: mixFilters
    };
  };
});
