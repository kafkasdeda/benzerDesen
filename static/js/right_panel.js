// right_panel.js
// Oluşturulma: 2025-04-20
// Hazırlayan: Kafkas ❤️ Luna
// Amaç:
// Power User ekranının sağ panelinde her cluster'ı temsilen bir görsel gösterilir.
// Kullanıcı bu görsele tıkladığında cluster detay ekranına gider (ileride eklenecek).
// Her model (pattern, color, texture) ve versiyona ait cluster yapısı farklıdır.
// Bu panel yalnızca aktif model ve versiyon seçimine göre görseleri gösterir.

const rightPanel = document.getElementById("right-panel");

function loadClusterRepresentatives(model = "pattern", version = "v1") {
  rightPanel.innerHTML = `<h2>🧠 Cluster Temsilcileri (${model} / ${version})</h2>`;

  fetch(`/clusters/${model}/${version}/representatives.json`)
    .then(res => res.json())
    .then(data => {
      const container = document.createElement("div");
      container.className = "image-grid";

      data.forEach(rep => {
        const box = document.createElement("div");
        box.className = "image-box";

        const img = document.createElement("img");
        img.src = `thumbnails/${rep.filename}`;
        img.loading = "lazy";
        img.alt = rep.cluster;
        img.title = `Cluster: ${rep.cluster}`;

        // İleride detay sayfasına gitmek için tıklanabilir
        img.addEventListener("click", () => {
          alert(`Cluster detay ekranına gidilecek: ${rep.cluster}`);
        });

        const label = document.createElement("div");
        label.style.textAlign = "center";
        label.style.marginTop = "4px";
        label.innerText = rep.cluster;

        box.appendChild(img);
        box.appendChild(label);
        container.appendChild(box);
      });

      rightPanel.appendChild(container);
    })
    .catch(err => {
      rightPanel.innerHTML += `<p style="color:red">❌ Cluster verisi yüklenemedi: ${err}</p>`;
    });
}
