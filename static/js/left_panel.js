// left_panel.js
// Oluşturulma: 2025-04-19
// Hazırlayan: Kafkas
// Açıklama:
// Sol panelde tüm görseller listelenir. Hover'da metadata ve büyük görsel görünür.
// Bir görsele tıklanınca seçilen modele göre benzerleri orta panelde yüklenir.
// Ek olarak: Karışım, özellik ve cluster filtrelerine göre dinamik filtreleme yapılır.

window.onload = function () {
  console.log("✅ left_panel.js window.onload tetiklendi");

  fetch('image_metadata_map.json')
    .then(res => res.json())
    .then(metadataMap => {
      console.log("📦 Metadata başarıyla alındı. Toplam:", Object.keys(metadataMap).length);

      const container = document.getElementById("image-container");
      const filenames = Object.keys(metadataMap);
      let allBoxes = []; // 🎯 Filtrelemeye yardımcı olmak için tüm box'ları saklıyoruz
      const blendSet = new Set();
      
      
      const featureSet = new Set([
        "MONOSTRETCH", "BISTRETCH", "POWERSTRETCH", "NATURALSTRETCH",
        "LIGHTWEIGHT", "COMFORT", "WASHABLE", "BREATHABLE",
        "ANTIBACTERIAL", "EASYIRONING", "MOISTUREMANAGMENT", "UVPROTECTION",
        "WRINKLERESISTANCE", "WATERREPELLENT", "THERMALCOMFORT", "QUICKDRY",
        "RWS", "RCSGRS"
      ]);
      window.featureSet = featureSet;

      filenames.forEach((name) => {
        const data = metadataMap[name];
        const box = document.createElement("div");
        box.className = "image-box";
        box.style.cursor = "pointer";

        const blendKeys = data.features.map(f => f[0]);
        const blendMap = Object.fromEntries(data.features);

        box.dataset.blend = blendKeys.join(",");
        box.dataset.features = data.features.filter(f => featureSet.has(f[0])).map(f => f[0]).join(",");
        box.dataset.cluster = data.cluster || "";
        box.dataset.blendMap = JSON.stringify(blendMap);

        blendKeys.forEach(k => blendSet.add(k));

        box.addEventListener("click", () => {
          console.log("🔁 Benzer görseller yükleniyor:", name);

          window.currentSelectedImage = name;
          const model = document.getElementById("model-selector")?.value || "pattern";
          const topN = parseInt(document.getElementById("topn-input")?.value || "10");
          const metric = document.getElementById("metric-selector")?.value || "cosine";

          if (document.getElementById("model-selector")) document.getElementById("model-selector").value = model;
          if (document.getElementById("topn-input")) document.getElementById("topn-input").value = topN;
          if (document.getElementById("metric-selector")) document.getElementById("metric-selector").value = metric;

          let filters = null;
          if (document.getElementById("center-pre-filter")?.checked && window.getFilterParams) {
            filters = window.getFilterParams();
          }

          function waitForLoadSimilarImages(callback) {
            if (typeof window.loadSimilarImages === "function") {
              callback();
            } else {
              console.warn("⏳ loadSimilarImages henüz hazır değil. 100ms sonra tekrar denenecek.");
              setTimeout(() => waitForLoadSimilarImages(callback), 100);
            }
          }

          waitForLoadSimilarImages(() => {
            loadSimilarImages(name, model, topN, metric, filters);
          });
        });

        if (data.cluster) box.classList.add("clustered");

        const img = document.createElement("img");
        img.loading = "lazy";
        img.src = `thumbnails/${name}`;
        img.alt = name;

        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        tooltip.style.pointerEvents = "none";

        const htypeStr = data.features.map(f => `${f[0]} (${f[1]}%)`).join(", ");
        tooltip.innerHTML = `
          <img src='realImages/${name}' />
          <strong>${data.design}</strong><br>
          Season: ${data.season}<br>
          Quality: ${data.quality}<br>
          Blend: ${htypeStr}<br>
          Cluster: ${data.cluster || 'Yok'}
        `;

        box.appendChild(img);
        box.appendChild(tooltip);
        container.appendChild(box);
        allBoxes.push(box);
      });

      const blendSelect = document.getElementById("blend-filter");
blendSet.forEach(b => {
const opt = document.createElement("option");
opt.value = b;
opt.textContent = b;
blendSelect?.appendChild(opt);
});

window.blendSet = blendSet;
if (window.populateMaterialDropdown) {
console.log("🎯 blendSet içeriği:", Array.from(blendSet));
window.populateMaterialDropdown();
}



      const featureSelect = document.getElementById("feature-filter");
      featureSet.forEach(f => {
        const opt = document.createElement("option");
        opt.value = f;
        opt.textContent = f;
        featureSelect?.appendChild(opt);
      });

      window.addKarisimFilter = function () {
        const wrapper = document.createElement("div");
        wrapper.className = "karisim-wrapper";
        wrapper.style.margin = "10px 0";
        wrapper.style.padding = "10px";
        wrapper.style.border = "1px solid #eee";
        wrapper.style.borderRadius = "5px";
        
        // Karışım tipi seçimi
        const selectContainer = document.createElement("div");
        selectContainer.style.marginBottom = "10px";
        
        const select = document.createElement("select");
        select.className = "karisim-select";
        select.style.width = "100%";
        select.style.padding = "5px";
        
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Tümü";
        select.appendChild(defaultOption);
        
        blendSet.forEach(b => {
          const opt = document.createElement("option");
          opt.value = b;
          opt.textContent = b;
          select.appendChild(opt);
        });
        
        selectContainer.appendChild(select);
        
        // Görünmeyen input'lar (değerleri saklamak için)
        const minInput = document.createElement("input");
        minInput.type = "hidden";
        minInput.className = "min-input";
        minInput.value = "0";
        
        const maxInput = document.createElement("input");
        maxInput.type = "hidden";
        maxInput.className = "max-input";
        maxInput.value = "100";
        
        // Range slider container
        const rangeContainer = document.createElement("div");
        rangeContainer.style.margin = "15px 0";
        
        // Range slider için div
        const sliderDiv = document.createElement("div");
        sliderDiv.className = "range-slider";
        
        // Değer gösterimi için div
        const valueDisplay = document.createElement("div");
        valueDisplay.className = "range-value-display";
        valueDisplay.style.display = "flex";
        valueDisplay.style.justifyContent = "space-between";
        valueDisplay.style.marginTop = "5px";
        valueDisplay.style.fontSize = "14px";
        valueDisplay.style.color = "#666";
        valueDisplay.innerHTML = '<span>0%</span><span>100%</span>';
        
        // noUiSlider oluştur
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
              to: function (value) {
                return Math.round(value);
              },
              from: function (value) {
                return Number(value);
              }
            }
          });
          
          // Değer değiştiğinde input ve gösterimi güncelle
          sliderDiv.noUiSlider.on('update', function (values, handle) {
            const minVal = parseInt(values[0]);
            const maxVal = parseInt(values[1]);
            
            minInput.value = minVal;
            maxInput.value = maxVal;
            
            valueDisplay.innerHTML = `<span>${minVal}%</span><span>${maxVal}%</span>`;
          });
        } else {
          // noUiSlider yüklenmediyse uyarı ver ve normal range input'lar kullan
          console.warn("noUiSlider kütüphanesi bulunamadı, normal range input'lar kullanılıyor.");
          
          const rangeInputsContainer = document.createElement("div");
          rangeInputsContainer.style.display = "flex";
          rangeInputsContainer.style.alignItems = "center";
          rangeInputsContainer.style.gap = "10px";
          
          const minLabel = document.createElement("span");
          minLabel.textContent = "Min:";
          minLabel.style.width = "40px";
          
          const minRange = document.createElement("input");
          minRange.type = "range";
          minRange.min = "0";
          minRange.max = "100";
          minRange.value = "0";
          minRange.style.flex = "1";
          minRange.addEventListener("input", function() {
            minInput.value = this.value;
            valueDisplay.innerHTML = `<span>${this.value}%</span><span>${maxInput.value}%</span>`;
            
            if (parseInt(minInput.value) > parseInt(maxInput.value)) {
              maxInput.value = minInput.value;
              valueDisplay.innerHTML = `<span>${minInput.value}%</span><span>${maxInput.value}%</span>`;
            }
          });
          
          const maxLabel = document.createElement("span");
          maxLabel.textContent = "Max:";
          maxLabel.style.width = "40px";
          
          const maxRange = document.createElement("input");
          maxRange.type = "range";
          maxRange.min = "0";
          maxRange.max = "100";
          maxRange.value = "100";
          maxRange.style.flex = "1";
          maxRange.addEventListener("input", function() {
            maxInput.value = this.value;
            valueDisplay.innerHTML = `<span>${minInput.value}%</span><span>${this.value}%</span>`;
            
            if (parseInt(maxInput.value) < parseInt(minInput.value)) {
              minInput.value = maxInput.value;
              valueDisplay.innerHTML = `<span>${minInput.value}%</span><span>${maxInput.value}%</span>`;
            }
          });
          
          rangeInputsContainer.appendChild(minLabel);
          rangeInputsContainer.appendChild(minRange);
          rangeInputsContainer.appendChild(maxLabel);
          rangeInputsContainer.appendChild(maxRange);
          
          sliderDiv.appendChild(rangeInputsContainer);
        }
        
        // Kaldırma butonu
        const removeButton = document.createElement("button");
        removeButton.textContent = "Kaldır";
        removeButton.style.marginTop = "10px";
        removeButton.style.padding = "5px 10px";
        removeButton.style.backgroundColor = "#f44336";
        removeButton.style.color = "white";
        removeButton.style.border = "none";
        removeButton.style.borderRadius = "4px";
        removeButton.style.cursor = "pointer";
        
        removeButton.addEventListener("click", function() {
          wrapper.remove();
          window.applyFilters(); // Filtreleri yeniden uygula
        });
        
        // Tüm elemanları container'a ekle
        rangeContainer.appendChild(sliderDiv);
        rangeContainer.appendChild(valueDisplay);
        
        wrapper.appendChild(selectContainer);
        wrapper.appendChild(rangeContainer);
        wrapper.appendChild(minInput);
        wrapper.appendChild(maxInput);
        wrapper.appendChild(removeButton);
        
        document.getElementById("karisim-panel")?.appendChild(wrapper);
      };

      window.addKarisimFilter();

      function getMixFilterValues() {
        const wrappers = document.querySelectorAll(".karisim-wrapper");
        return Array.from(wrappers).map(wrapper => {
          return {
            htype: wrapper.querySelector("select")?.value,
            min: parseInt(wrapper.querySelector(".min-input")?.value || "0"),
            max: parseInt(wrapper.querySelector(".max-input")?.value || "100")
          };
        }).filter(entry => entry.htype && entry.htype !== "Tümü");
      }

      window.applyFilters = function () {
        const blendValue = document.getElementById("blend-filter")?.value?.trim().toLowerCase();
        const featureValue = document.getElementById("feature-filter")?.value?.trim().toLowerCase();
        const clusterValue = document.getElementById("cluster-filter")?.value?.trim().toLowerCase();
        const mixFilters = getMixFilterValues();

        allBoxes.forEach(box => {
          const matchBlend = !blendValue || box.dataset.blend.toLowerCase().includes(blendValue);
          const matchFeature = !featureValue || box.dataset.features.toLowerCase().includes(featureValue);

          const matchCluster = !clusterValue ||
            (clusterValue === "clustered" && box.dataset.cluster) ||
            (clusterValue === "unclustered" && !box.dataset.cluster);

          const blendMap = JSON.parse(box.dataset.blendMap || "{}");
          const matchMix = mixFilters.every(filter => {
            const val = blendMap[filter.htype] || 0;
            return val >= filter.min && val <= filter.max;
          });

          box.style.display = (matchBlend && matchFeature && matchCluster && matchMix) ? "block" : "none";
        });
      };

      document.getElementById("blend-filter")?.addEventListener("change", applyFilters);
      document.getElementById("feature-filter")?.addEventListener("change", applyFilters);
      document.getElementById("cluster-filter")?.addEventListener("change", applyFilters);
    })
    .catch(err => {
      document.getElementById("image-container").innerText = "❌ Metadata yüklenemedi: " + err;
      console.error("❌ Metadata yüklenemedi:", err);
    });
};
