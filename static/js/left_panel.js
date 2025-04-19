// left_panel.js
// Oluşturulma: 2025-04-19
// Hazırlayan: Kafkas ❤️ Luna
// Açıklama:
// Sol panelde tüm görseller listelenir. Hover'da metadata ve büyük görsel görünür.
// Bir görsele tıklanınca seçilen modele göre benzerleri orta panelde yüklenir.

window.onload = function () {
    console.log("✅ left_panel.js window.onload tetiklendi");
  
    fetch('image_metadata_map.json')
      .then(res => res.json())
      .then(metadataMap => {
        console.log("📦 Metadata başarıyla alındı. Toplam:", Object.keys(metadataMap).length);
        const container = document.getElementById("image-container");
        const filenames = Object.keys(metadataMap);
  
        filenames.forEach((name) => {
          const data = metadataMap[name];
          const box = document.createElement("div");
          box.className = "image-box";
          box.style.cursor = "pointer";
  
          // ✅ Click eventi: orta paneli tetikler
          box.addEventListener("click", () => {
            console.log("🖱️ Benzer görseller yükleniyor:", name);
            const model = "pattern";
            const topN = 10;
            const metric = "cosine";
            loadSimilarImages(name, model, topN, metric);
          });
  
          if (data.cluster) box.classList.add("clustered");
  
          const img = document.createElement("img");
          img.loading = "lazy";
          img.src = `realImages/${name}`;
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
        });
      })
      .catch(err => {
        document.getElementById("image-container").innerText = "❌ Metadata yüklenemedi: " + err;
        console.error("❌ Metadata yüklenemedi:", err);
      });
  };