// left_panel.js
// Oluşturulma: 2025-04-19
// Güncelleme: 2025-04-29 (Performans optimizasyonları)
// Güncelleme: 2025-04-30 (Uyumluyu Ara butonu eklendi)
// Hazırlayan: Kafkas
// Açıklama:
// Sol panelde tüm görseller listelenir. Hover'da metadata ve büyük görsel görünür.
// Bir görsele tıklanınca seçilen modele göre benzerleri orta panelde yüklenir.
// Ek olarak: Karışım, özellik ve cluster filtrelerine göre dinamik filtreleme yapılır.

// Biraz daha hızlı çalışması için önbelleğe alınan veriler
const cachedMetadata = {};
const cachedElements = {};

// Teknik özellikler burada tanımlanıyor (sadece bir kez)
const featureSet = new Set([
  "MONOSTRETCH", "BISTRETCH", "POWERSTRETCH", "NATURALSTRETCH",
  "LIGHTWEIGHT", "COMFORT", "WASHABLE", "BREATHABLE",
  "ANTIBACTERIAL", "EASYIRONING", "MOISTUREMANAGMENT", "UVPROTECTION",
  "WRINKLERESISTANCE", "WATERREPELLENT", "THERMALCOMFORT", "QUICKDRY",
  "RWS", "RCSGRS"
]);

window.onload = function () {
  console.log("left_panel.js window.onload tetiklendi");
  
  // Model ve versiyon değişikliklerini dinle
  function listenForModelChanges() {
    const modelButtons = document.querySelectorAll(".model-button");
    if (modelButtons.length > 0) {
      console.log("Model butonları bulundu, dinleniyor...");
      return true;
    }
    return false;
  }
  
  function listenForVersionChanges() {
    const versionCombo = document.getElementById("version-combo");
    if (versionCombo) {
      console.log("Versiyon combo bulundu, dinleniyor...");
      versionCombo.addEventListener("change", () => {
        window.applyFilters(); // Versiyon değiştiğinde filtreleri yeniden uygula
      });
      return true;
    }
    return false;
  }
  
  // Element'ler yüklenene kadar bekle
  let checkInterval = setInterval(() => {
    const modelsReady = listenForModelChanges();
    const versionsReady = listenForVersionChanges();
    
    if (modelsReady && versionsReady) {
    clearInterval(checkInterval);
    console.log("Sağ panel elemanları başarıyla dinleniyor");
    }
  }, 500);

  fetch('image_metadata_map.json')
    .then(res => res.json())
    .then(metadataMap => {
      console.log("Metadata başarıyla alındı. Toplam:", Object.keys(metadataMap).length);

      // Global olarak featureSet tanımla
      window.featureSet = featureSet;

      // Performans iyileştirmesi: Görselleri döküman parçası kullanarak toplu ekle
      const container = document.getElementById("image-container");
      const filenames = Object.keys(metadataMap);
      let allBoxes = []; // 🎯 Filtrelemeye yardımcı olmak için tüm box'ları saklıyoruz
      const blendSet = new Set();
      
      // Hızlı render için DocumentFragment kullan
      const fragment = document.createDocumentFragment();
      
      // Her 200 görsel için bir batch oluştur (DOM performansı için)
      const BATCH_SIZE = 200;
      let currentBatch = 0;
      const totalBatches = Math.ceil(filenames.length / BATCH_SIZE);
      
      function processNextBatch() {
        if (currentBatch >= totalBatches) {
          console.log("Tüm görseller yüklendi.");
          
          // Blend set'i doldur ve select'e ekle
          const blendSelect = document.getElementById("blend-filter");
          blendSet.forEach(b => {
            const opt = document.createElement("option");
            opt.value = b;
            opt.textContent = b;
            blendSelect?.appendChild(opt);
          });

          window.blendSet = blendSet;
          if (window.populateMaterialDropdown) {
            window.populateMaterialDropdown();
          }

          return;
        }
        
        // Session 7: İlerleme bilgisini sadece ilk ve son batch için göster
        if (currentBatch === 0 || currentBatch === totalBatches - 1) {
          console.log(`Görseller yükleniyor... ${Math.round((currentBatch / totalBatches) * 100)}%`);
        }
        
        const startIdx = currentBatch * BATCH_SIZE;
        const endIdx = Math.min(startIdx + BATCH_SIZE, filenames.length);
        const batchFragment = document.createDocumentFragment();
        
        for (let i = startIdx; i < endIdx; i++) {
          const name = filenames[i];
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
          box.dataset.filename = name; // Görselin adını dataset'e ekle (daha hızlı erişim için)

          blendKeys.forEach(k => blendSet.add(k));

          box.addEventListener("click", function() {
            const filename = this.dataset.filename;
            console.log("Benzer görseller yükleniyor:", filename);

            window.currentSelectedImage = filename;
            const model = window.currentModel || "pattern";
            const version = window.currentVersion || "v1";
            const topN = parseInt(document.getElementById("topn-input")?.value || "10");
            const metric = document.getElementById("metric-selector")?.value || "cosine";

            // Eski elementler için geriye dönük uyumluluk kontrolleri
            if (document.getElementById("model-selector")) document.getElementById("model-selector").value = model;
            if (document.getElementById("topn-input")) document.getElementById("topn-input").value = topN;
            if (document.getElementById("metric-selector")) document.getElementById("metric-selector").value = metric;
            
            console.log(`Görsel seçildi: ${filename}, model=${model}, version=${version}`);

            let filters = null;
            if (document.getElementById("center-pre-filter")?.checked && window.getFilterParams) {
              filters = window.getFilterParams();
            }

            function waitForShowSimilarImages(callback) {
              if (typeof window.showSimilarImages === "function") {
                callback();
              } else {
                console.warn("⏳ showSimilarImages henüz hazır değil. 100ms sonra tekrar denenecek.");
                setTimeout(() => waitForShowSimilarImages(callback), 100);
              }
            }

            waitForShowSimilarImages(() => {
              window.showSimilarImages(filename);
            });
          });

          if (data.cluster) box.classList.add("clustered");

          // Lazy loading için src'yi data-src'ye taşı
          const img = document.createElement("img");
          img.loading = "lazy";
          img.dataset.src = `thumbnails/${name}`;
          img.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E"; // Placeholder
          img.alt = name;

          // Tooltip'leri lazy olarak ekle (hover olunca)
          box.addEventListener("mouseenter", function(event) {
            // Button hover'ları için tooltip'i atla
            if (event.target.closest('.image-buttons')) {
              return;
            }
            
            // Önce varsa eski tooltip'leri temizle
            const existingTooltip = this.querySelector('.tooltip');
            if (existingTooltip) {
              this.removeChild(existingTooltip);
            }
            
            const tooltip = document.createElement("div");
            tooltip.className = "tooltip";
            tooltip.style.position = "absolute";
            tooltip.style.top = "0";
            tooltip.style.left = "110%";
            tooltip.style.backgroundColor = "#fff";
            tooltip.style.border = "1px solid #aaa";
            tooltip.style.padding = "8px";
            tooltip.style.zIndex = "9999"; // Çok yüksek z-index kullan
            tooltip.style.width = "300px";
            tooltip.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
            tooltip.style.borderRadius = "4px";
            tooltip.style.display = "block";
            tooltip.style.pointerEvents = "none";
            tooltip.style.visibility = "visible"; // Görünürlük zorla
            
            // Debug amaçlı çerçeve
            tooltip.style.border = "2px solid red";
            
            // Kullanıcıya boyut bilgisini sor
            const imgWidth = 300;
            const imgHeight = 300;

            const htypeStr = data.features.map(f => `${f[0]} (${f[1]}%)`).join(", ");
            tooltip.innerHTML = `
              <img src='realImages/${name}' style="width: ${imgWidth}px; max-height: ${imgHeight}px; object-fit: contain;" />
              <strong>${data.design || ""}</strong><br>
              Season: ${data.season || "Belirtilmemiş"}<br>
              Quality: ${data.quality || "Belirtilmemiş"}<br>
              Blend: ${htypeStr}<br>
              Cluster: ${data.cluster || 'Yok'}
            `;
            
            // Document.body'e ekleyelim (görsel kutusuna değil)
            document.body.appendChild(tooltip);
            
            // Tooltip konumunu görsel kutusuna göre ayarla
            const boxRect = this.getBoundingClientRect();
            tooltip.style.position = "fixed";
            tooltip.style.top = boxRect.top + "px";
            tooltip.style.left = (boxRect.right + 10) + "px";
            
            // Viewport sınırlarını kontrol et ve gerekirse konumu ayarla
            setTimeout(() => {
              const rect = tooltip.getBoundingClientRect();
              if (rect.right > window.innerWidth) {
                tooltip.style.left = (boxRect.left - rect.width - 10) + "px";
              }
              if (rect.bottom > window.innerHeight) {
                tooltip.style.top = (window.innerHeight - rect.height - 10) + "px";
              }
            }, 0);
            
            // Tooltip'i mouseleave olayında kaldırmak için kaydedelim
            this._currentTooltip = tooltip;
          });
          
          // Tooltip'i temizleme işlemini ekle (mouse ayrılınca)
          box.addEventListener("mouseleave", function() {
            if (this._currentTooltip) {
              this._currentTooltip.remove();
              this._currentTooltip = null;
            }
          });

          // Uyumluyu Ara butonu ekle
          const buttonContainer = document.createElement('div');
          buttonContainer.className = 'image-buttons';
          
          const findHarmoniousButton = document.createElement('button');
          findHarmoniousButton.textContent = 'Uyumluyu Ara';
          findHarmoniousButton.className = 'find-harmonious-btn';
          
          findHarmoniousButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Görsel seçme olayının tetiklenmesini engelle
            if (window.showHarmoniousSearchModal) {
              window.showHarmoniousSearchModal(name);
            } else {
              console.warn("showHarmoniousSearchModal fonksiyonu bulunamadı");
              alert("Uyumlu renk arama modalı henüz yüklenmemiş!");
              }
          });
          
          buttonContainer.appendChild(findHarmoniousButton);
          
          // Karşılaştırma butonu ekle
          const compareButton = document.createElement('button');
          compareButton.textContent = 'Karşılaştır';
          compareButton.className = 'compare-btn';
          
          compareButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Görsel seçme olayının tetiklenmesini engelle
            if (window.addToCompareList) {
              window.addToCompareList(name);
            } else {
              console.warn("addToCompareList fonksiyonu bulunamadı");
              alert("Karşılaştırma listesi henüz yüklenmemiş!");
            }
          });
          
          buttonContainer.appendChild(compareButton);
          box.appendChild(img);
          box.appendChild(buttonContainer);
          batchFragment.appendChild(box);
          allBoxes.push(box);
        }
        
        container.appendChild(batchFragment);
        currentBatch++;
        
        // Bir sonraki batch'i işle (istemciyi bloke etmemek için setTimeout kullan)
        setTimeout(processNextBatch, 10);
        
        // Eğer bu ilk batch ise, görüntüleri gözlemlemek için IntersectionObserver kur
        if (currentBatch === 1) {
          setupLazyLoading();
        }
      }
      
      // Görselleri lazy loading ile yüklemek için IntersectionObserver
      function setupLazyLoading() {
        if ('IntersectionObserver' in window) {
          // Global imgObserver değişkenine atayarak diğer fonksiyonlardan erişilebilir yap
          window.imgObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                const img = entry.target;
                
                // Orijinal kaynak varsa (bellek temizleme sonrası)
                if (img.dataset.originalSrc) {
                  console.log('🔄 Sol panel - Orijinal kaynaktan görsel yükleniyor:', img.dataset.originalSrc);
                  img.src = img.dataset.originalSrc;
                  img.removeAttribute('data-originalSrc');
                  img.classList.add('keep-in-memory'); // Tekrar temizlenmesini önlemek için işaretle
                }
                // Normal lazy loading durumu
                else if (img.dataset.src) {
                  console.log('🔄 Sol panel - Lazy loading görsel yükleniyor:', img.dataset.src);
                  img.src = img.dataset.src;
                  img.removeAttribute('data-src');
                  img.classList.add('keep-in-memory'); // Temizlenmesini önlemek için işaretle
                }
                
                // görsel yüklendi, gözlemi bırak
                observer.unobserve(img);
              }
            });
          }, { 
            rootMargin: '500px', // Görünür alandan 500px önce yüklemeye başla (eskisi: 200px)
            threshold: 0.01     // %1 görünür olduğunda tetikle
          });

          // Görselleri gözlemle (hem data-src hem de data-original-src olanları)
          document.querySelectorAll('.image-box img[data-src], .image-box img[data-original-src]').forEach(img => {
            window.imgObserver.observe(img);
          });
          
          // 10 saniyede bir yeniden kontrol et (bellek temizleme sonrası yeni görseller için)
          const checkInterval = setInterval(() => {
            const pendingImages = document.querySelectorAll('.image-box img[data-src], .image-box img[data-original-src]');
            if (pendingImages.length > 0) {
              console.log(`🔄 Sol panel - ${pendingImages.length} adet bekleyen görsel yeniden gözleme alınıyor...`);
              pendingImages.forEach(img => window.imgObserver.observe(img));
            }
          }, 10000);
          
          // Sayfadan ayrılınca interval'i temizle
          window.addEventListener('beforeunload', () => clearInterval(checkInterval));
        } else {
          // IntersectionObserver desteklenmiyorsa tüm görselleri yükle
          document.querySelectorAll('.image-box img').forEach(img => {
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            if (img.dataset.originalSrc) {
              img.src = img.dataset.originalSrc;
              img.removeAttribute('data-originalSrc');
            }
          });
        }
      }
      
      // İlk batch'i işle
      processNextBatch();

      // Feature select'i de doldur
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
        
        // Mevcut model ve versiyonu günlükçe olarak göster
        const model = window.currentModel || "pattern";
        const version = window.currentVersion || "v1";
        console.log(`Filtreler uygulanıyor - Model: ${model}, Versiyon: ${version}`);

        // Performans iyileştirmesi: DOM yeniden boyutlandırmalarını azaltmak için display özelliğini CSS sınıfı ile yönet
        if (!document.getElementById('dynamic-filter-style')) {
          const style = document.createElement('style');
          style.id = 'dynamic-filter-style';
          style.innerHTML = '.filter-hidden { display: none !important; }';
          document.head.appendChild(style);
        }

        // İlk önce tüm görselleri gizle/göster, sonra detaylı filtreleri uygula
        // Bu şekilde tarayıcının gereksiz yeniden boyutlandırma yapmasını önlüyoruz
        allBoxes.forEach(box => {
          if (!box.dataset) return; // Hatalı veri atla
          
          const matchBlend = !blendValue || box.dataset.blend.toLowerCase().includes(blendValue);
          const matchFeature = !featureValue || box.dataset.features.toLowerCase().includes(featureValue);
          const matchCluster = !clusterValue ||
            (clusterValue === "clustered" && box.dataset.cluster) ||
            (clusterValue === "unclustered" && !box.dataset.cluster);

          // Karışım filtrelerine eşleşme kontrolü
          let matchMix = true;
          if (mixFilters.length > 0) {
            try {
              const blendMap = JSON.parse(box.dataset.blendMap || "{}");
              matchMix = mixFilters.every(filter => {
                const val = blendMap[filter.htype] || 0;
                return val >= filter.min && val <= filter.max;
              });
            } catch (e) {
              console.warn("Blend map parse hatası:", e);
              matchMix = false;
            }
          }

          // Tüm filtrelere eşleşiyorsa göster, aksi halde gizle
          if (matchBlend && matchFeature && matchCluster && matchMix) {
            box.classList.remove('filter-hidden');
          } else {
            box.classList.add('filter-hidden');
          }
        });
      };

      document.getElementById("blend-filter")?.addEventListener("change", applyFilters);
      document.getElementById("feature-filter")?.addEventListener("change", applyFilters);
      document.getElementById("cluster-filter")?.addEventListener("change", applyFilters);
    })
    .catch(err => {
      document.getElementById("image-container").innerText = "Metadata yüklenemedi: " + err;
      console.error("Metadata yüklenemedi:", err);
    });
};
