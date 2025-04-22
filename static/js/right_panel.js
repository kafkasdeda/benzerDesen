// right_panel.js
// Oluşturulma: 2025-04-20
// Hazırlayan: Kafkas
// Açıklama:
// Sağ panelde, model versiyonuna ait temsilci görseller (her bir cluster için) gösterilir.
// Ayrıca model versiyonuna ait genel yorum (version_comment) üstte gösterilir ve kullanıcı tarafından düzenlenebilir.
// Ek olarak, seçilen görsellerle yeni bir cluster oluşturulabilir.

const rightPanel = document.getElementById("right-panel");

function loadClusterRepresentatives(model, version) {
  rightPanel.innerHTML = "\u{1F50D} Cluster verisi yükleniyor...";

  // ✅ URL düzeltildi: doğru route /clusters/... ile uyumlu
  fetch(`/clusters/${model}/${version}/representatives.json`)
    .then(res => res.json())
    .then(data => {
      if (!data.clusters || !Array.isArray(data.clusters)) {
        rightPanel.innerHTML = "❌ Cluster verisi beklenen formatta değil.";
        return;
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
      rightPanel.innerHTML = "";
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

      const container = document.createElement("div");
      container.className = "image-grid";

      data.clusters.forEach(item => {
        const box = document.createElement("div");
        box.className = "cluster-box";
       

        const img = document.createElement("img");
        img.src = `thumbnails/${item.filename}`;
        img.alt = item.filename;
        img.loading = "lazy";

        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        tooltip.innerHTML = `
          <img src='thumbnails/${item.filename}' />
          <strong>${item.cluster}</strong><br>
          ${item.comment || "(Yorum yok)"}
        `;

        box.appendChild(img);
        box.appendChild(tooltip);
        const moveButton = document.createElement("button");
        moveButton.textContent = "Seçilenleri Bu Cluster'a Taşı";
        moveButton.className = "move-to-cluster-btn";
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
            cluster: item.cluster,
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
      createButton.onclick = () => {
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
          } else {
            alert("❌ Oluşturulamadı: " + result.message);
          }
        });
      };

      rightPanel.appendChild(createButton);
    })
    .catch(err => {
      rightPanel.innerText = `❌ Cluster verisi yüklenemedi: ${err}`;
    });
}
