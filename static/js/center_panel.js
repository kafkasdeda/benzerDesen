// center_panel.js
// Oluşturulma: 2025-04-19
// Hazırlayan: Kafkas ❤️ Luna
// Açıklama:
// Orta panelde, seçilen görsele göre benzer desenleri gösteren dinamik yapı.
// Sunucudan gelen benzerlik sonuçlarını gösterir. Hover'da metadata + büyük görsel içerir.

const centerContainer = document.getElementById("center-panel");

// Bu fonksiyon dışarıdan çağrılır
function loadSimilarImages(selectedFilename, model = "pattern", topN = 10, metric = "cosine") {
  centerContainer.innerHTML = "🔄 Benzer görseller yükleniyor...";

  fetch(`/find-similar?filename=${encodeURIComponent(selectedFilename)}&model=${model}&topN=${topN}&metric=${metric}`)
    .then(res => res.json())
    .then(results => {
      centerContainer.innerHTML = "";

      results.forEach(result => {
        const box = document.createElement("div");
        box.className = "image-box";

        const img = document.createElement("img");
        img.src = `thumbnails/${result.filename}`;
        img.loading = "lazy";
        img.alt = result.filename;

        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";

        const blendText = result.features?.length
          ? result.features.map(f => `${f[0]} (${f[1]}%)`).join(", ")
          : "Yok";

        tooltip.innerHTML = `
          <img src='realImages/${result.filename}' />
          <strong>${result.design}</strong><br>
          Season: ${result.season}<br>
          Quality: ${result.quality}<br>
          Blend: ${blendText}<br>
          Cluster: ${result.cluster || 'Yok'}<br>
          Similarity: ${result.similarity?.toFixed(3) || '—'}
        `;

        box.appendChild(img);
        box.appendChild(tooltip);
        centerContainer.appendChild(box);
      });
    })
    .catch(err => {
      centerContainer.innerText = `❌ Benzer görseller yüklenemedi: ${err}`;
    });
}
