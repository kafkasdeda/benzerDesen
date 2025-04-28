/**
 * notifications.js
 * Oluşturulma: 2025-04-28
 * Hazırlayan: Claude
 * 
 * Açıklama:
 * Bu dosya, web arayüzü için bildirim sistemini yönetir. Özellikle yeni görsel eklenme,
 * silinme veya metadata değişikliklerini kullanıcıya bildirmek ve gerekli işlemleri
 * yapmak için kullanılır.
 */

// Bildirim durumunu saklayacak değişken
let currentNotification = null;

// Notifikasyon konteynerinin HTML'ini oluştur
function createNotificationContainer() {
  // Eğer zaten varsa tekrar oluşturma
  if (document.getElementById("notification-container")) {
    return;
  }

  const container = document.createElement("div");
  container.id = "notification-container";
  container.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    width: 400px;
    max-width: 90%;
    display: flex;
    flex-direction: column;
    gap: 10px;
  `;

  document.body.appendChild(container);
}

// Stilleri enjekte et
function injectStyles() {
  const style = document.createElement("style");
  style.textContent = `
    .app-notification {
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      padding: 15px;
      margin-bottom: 10px;
      animation: slideIn 0.3s ease-out;
      overflow: hidden;
      transition: all 0.3s ease;
    }
    
    .notification-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    
    .notification-title {
      font-weight: bold;
      font-size: 16px;
      margin: 0;
      flex-grow: 1;
    }
    
    .notification-close {
      cursor: pointer;
      font-size: 20px;
      color: #666;
      padding: 0 5px;
      background: none;
      border: none;
    }
    
    .notification-body {
      font-size: 14px;
      color: #333;
      margin-bottom: 15px;
    }
    
    .notification-progress {
      height: 4px;
      background-color: #f0f0f0;
      border-radius: 2px;
      margin-bottom: 10px;
      overflow: hidden;
    }
    
    .notification-progress-bar {
      height: 100%;
      background-color: #4CAF50;
      width: 0%;
      transition: width 0.3s linear;
    }
    
    .notification-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    }
    
    .notification-btn {
      padding: 6px 12px;
      border-radius: 4px;
      border: none;
      font-size: 14px;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    
    .notification-btn-primary {
      background-color: #4CAF50;
      color: white;
    }
    
    .notification-btn-secondary {
      background-color: #f0f0f0;
      color: #333;
    }
    
    .notification-btn:hover {
      opacity: 0.9;
    }
    
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes fadeOut {
      from {
        opacity: 1;
      }
      to {
        opacity: 0;
      }
    }
    
    .notification-detail-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 10px;
      font-size: 12px;
    }
    
    .notification-detail-table th,
    .notification-detail-table td {
      padding: 5px;
      border: 1px solid #eee;
      text-align: left;
    }
    
    .notification-detail-table th {
      background-color: #f5f5f5;
    }
    
    .notification-detail-toggle {
      background: none;
      border: none;
      color: #0066cc;
      cursor: pointer;
      padding: 0;
      font-size: 14px;
      text-decoration: underline;
      margin-bottom: 10px;
      display: inline-block;
    }
    
    .notification-detail-content {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s ease;
    }
    
    .notification-detail-content.show {
      max-height: 300px;
      overflow-y: auto;
    }
    
    .notification-badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 10px;
      font-size: 12px;
      color: white;
      margin-right: 5px;
    }
    
    .notification-badge-success {
      background-color: #4CAF50;
    }
    
    .notification-badge-warning {
      background-color: #FF9800;
    }
    
    .notification-badge-error {
      background-color: #F44336;
    }
    
    .notification-loading {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 3px solid rgba(0,0,0,0.1);
      border-top-color: #3498db;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-right: 8px;
    }
    
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `;

  document.head.appendChild(style);
}

// Bildirim oluşturma fonksiyonu
function showNotification(options) {
  const {
    title,
    message,
    type = 'info',
    duration = 10000,
    actions = [],
    details = null,
    progress = false,
  } = options;

  createNotificationContainer();
  const container = document.getElementById("notification-container");

  // Bildirim elementini oluştur
  const notification = document.createElement("div");
  notification.className = `app-notification notification-${type}`;
  
  // Bildirim içeriği
  notification.innerHTML = `
    <div class="notification-header">
      <h3 class="notification-title">${title}</h3>
      <button class="notification-close">&times;</button>
    </div>
    <div class="notification-body">${message}</div>
    ${progress ? '<div class="notification-progress"><div class="notification-progress-bar"></div></div>' : ''}
    ${details ? `
      <button class="notification-detail-toggle">Detayları Göster</button>
      <div class="notification-detail-content">
        ${details}
      </div>
    ` : ''}
    ${actions.length > 0 ? `
      <div class="notification-actions">
        ${actions.map(action => `
          <button class="notification-btn notification-btn-${action.primary ? 'primary' : 'secondary'}" 
                  data-action="${action.action}">
            ${action.label}
          </button>
        `).join('')}
      </div>
    ` : ''}
  `;

  // Bildirim konteynerine ekle
  container.appendChild(notification);

  // Kapat düğmesi işlevselliği
  const closeBtn = notification.querySelector(".notification-close");
  closeBtn.addEventListener("click", () => {
    closeNotification(notification);
  });

  // Detay göster/gizle işlevselliği
  if (details) {
    const detailToggle = notification.querySelector(".notification-detail-toggle");
    const detailContent = notification.querySelector(".notification-detail-content");
    
    detailToggle.addEventListener("click", () => {
      detailContent.classList.toggle("show");
      detailToggle.textContent = detailContent.classList.contains("show") ? "Detayları Gizle" : "Detayları Göster";
    });
  }

  // Aksiyon düğmeleri
  const actionButtons = notification.querySelectorAll("[data-action]");
  actionButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const action = btn.getAttribute("data-action");
      const actionObj = actions.find(a => a.action === action);
      
      if (actionObj && typeof actionObj.onClick === 'function') {
        actionObj.onClick(notification);
      }
    });
  });

  // Otomatik kapatma
  if (duration > 0 && type !== 'loading') {
    setTimeout(() => {
      closeNotification(notification);
    }, duration);
  }

  // İlerleme çubuğu
  if (progress) {
    const progressBar = notification.querySelector(".notification-progress-bar");
    let width = 0;
    const interval = setInterval(() => {
      if (width >= 100) {
        clearInterval(interval);
      } else {
        width++;
        progressBar.style.width = width + "%";
      }
    }, duration / 100);
  }

  // Güncel bildirimi kaydet
  currentNotification = notification;
  return notification;
}

// Bildirimi kapat
function closeNotification(notification) {
  notification.style.opacity = "0";
  notification.style.height = "0";
  notification.style.margin = "0";
  notification.style.padding = "0";
  
  setTimeout(() => {
    notification.remove();
    if (currentNotification === notification) {
      currentNotification = null;
    }
  }, 300);
}

// Tüm bildirimleri kapat
function closeAllNotifications() {
  const container = document.getElementById("notification-container");
  if (!container) return;
  
  const notifications = container.querySelectorAll(".app-notification");
  notifications.forEach(notification => {
    closeNotification(notification);
  });
}

// İlerleme bildirimini güncelle
function updateProgressNotification(notification, progress, message = null) {
  if (!notification) return;
  
  const progressBar = notification.querySelector(".notification-progress-bar");
  if (progressBar) {
    progressBar.style.width = `${progress}%`;
  }
  
  if (message) {
    const messageEl = notification.querySelector(".notification-body");
    if (messageEl) {
      messageEl.innerHTML = message;
    }
  }
}

// Değişiklik kontrolü yap
function checkForUpdates() {
  // Mevcut bildirimi kontrol et
  if (currentNotification) {
    return; // Zaten aktif bildirim varsa çık
  }

  // Yükleme bildirimini göster
  const loadingNotification = showNotification({
    title: "Değişiklikler Kontrol Ediliyor",
    message: '<div class="notification-loading"></div> Görsel ve metadata değişiklikleri kontrol ediliyor...',
    type: 'loading',
    duration: 0, // Otomatik kapanmasın
  });

  // Backend API'ına istek at
  fetch("/check-updates")
    .then(response => response.json())
    .then(data => {
      // Yükleme bildirimini kapat
      closeNotification(loadingNotification);

      // Sonuçları işle
      if (data.status === "changes_detected") {
        const changes = data.changes;
        const summary = changes.summary || {};
        
        // Değişiklik detaylarını oluştur
        let detailsHTML = '';
        
        // Yeni görseller
        if (summary.new_images_count > 0) {
          detailsHTML += `
            <h4>Yeni Görseller (${summary.new_images_count})</h4>
            <table class="notification-detail-table">
              <thead>
                <tr>
                  <th>Dosya Adı</th>
                  <th>Boyut</th>
                </tr>
              </thead>
              <tbody>
                ${changes.details.new_images.map(img => `
                  <tr>
                    <td>${img.filename}</td>
                    <td>${img.file_size_formatted}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        }
        
        // Silinen görseller
        if (summary.removed_images_count > 0) {
          detailsHTML += `
            <h4>Silinen Görseller (${summary.removed_images_count})</h4>
            <table class="notification-detail-table">
              <thead>
                <tr>
                  <th>Dosya Adı</th>
                </tr>
              </thead>
              <tbody>
                ${changes.details.removed_images.map(img => `
                  <tr>
                    <td>${img.filename}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        }
        
        // JSON değişiklikleri
        if (summary.json_changes_count > 0) {
          detailsHTML += `
            <h4>Değişen JSON Dosyaları (${summary.json_changes_count})</h4>
            <ul>
              ${changes.details.json_changes.map(file => `<li>${file}</li>`).join('')}
            </ul>
          `;
        }
        
        // Cluster güncellemeleri
        if (summary.cluster_updates_count > 0) {
          detailsHTML += `
            <h4>Cluster Güncellemeleri (${summary.cluster_updates_count})</h4>
            <table class="notification-detail-table">
              <thead>
                <tr>
                  <th>Görsel</th>
                  <th>Cluster</th>
                </tr>
              </thead>
              <tbody>
                ${changes.details.cluster_updates.details.map(update => `
                  <tr>
                    <td>${update[0]}</td>
                    <td>${update[1]}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        }
        
        // Gerekli işlemler
        if (changes.required_actions && changes.required_actions.length > 0) {
          detailsHTML += `
            <h4>Yapılacak İşlemler</h4>
            <ul>
              ${changes.required_actions.map(action => `<li>${action.description}</li>`).join('')}
            </ul>
          `;
        }
        
        // Değişiklik bildirimini göster
        showNotification({
          title: changes.notification.title,
          message: changes.notification.message,
          type: 'warning',
          duration: 0, // Manuel kapatılana kadar kalsın
          details: detailsHTML,
          actions: [
            {
              label: "Güncelle",
              action: "apply_updates",
              primary: true,
              onClick: () => applyUpdates(changes)
            },
            {
              label: "Yoksay",
              action: "ignore",
              onClick: () => ignoreUpdates(changes)
            }
          ]
        });
      }
    })
    .catch(error => {
      // Yükleme bildirimini kapat
      closeNotification(loadingNotification);
      
      // Hata bildirimini göster
      showNotification({
        title: "Hata",
        message: `Değişiklikler kontrol edilirken bir hata oluştu: ${error.message}`,
        type: 'error',
        duration: 5000
      });
      
      console.error("Değişiklik kontrolü sırasında hata:", error);
    });
}

// Değişiklikleri uygula
function applyUpdates(changes) {
  // Uygulama bildirimi göster
  const loadingNotification = showNotification({
    title: "Değişiklikler Uygulanıyor",
    message: '<div class="notification-loading"></div> Gerekli güncellemeler yapılıyor... Bu işlem biraz zaman alabilir.',
    type: 'loading',
    duration: 0,
    progress: true
  });

  // Backend API'ına istek at
  fetch("/apply-updates", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }
  })
    .then(response => response.json())
    .then(data => {
      // Yükleme bildirimini kapat
      closeNotification(loadingNotification);

      // Sonuçları işle
      let detailsHTML = '';
      
      if (data.results && data.results.actions) {
        detailsHTML += `
          <h4>Yapılan İşlemler</h4>
          <ul>
            ${data.results.actions.map(action => `
              <li>
                <span class="notification-badge notification-badge-success">✓</span>
                ${action.message}
              </li>
            `).join('')}
          </ul>
        `;
      }
      
      if (data.results && data.results.errors && data.results.errors.length > 0) {
        detailsHTML += `
          <h4>Hatalar</h4>
          <ul>
            ${data.results.errors.map(error => `
              <li>
                <span class="notification-badge notification-badge-error">✗</span>
                ${error.action}: ${error.error}
              </li>
            `).join('')}
          </ul>
        `;
      }
      
      // Başarı/hata bildirimini göster
      showNotification({
        title: data.status === "success" ? "Güncelleme Tamamlandı" : "Güncelleme Kısmen Tamamlandı",
        message: data.message,
        type: data.status === "success" ? "success" : "warning",
        duration: 5000,
        details: detailsHTML,
        actions: [
          {
            label: "Sayfayı Yenile",
            action: "refresh",
            primary: true,
            onClick: () => window.location.reload()
          }
        ]
      });
    })
    .catch(error => {
      // Yükleme bildirimini kapat
      closeNotification(loadingNotification);
      
      // Hata bildirimini göster
      showNotification({
        title: "Güncelleme Hatası",
        message: `Değişiklikler uygulanırken bir hata oluştu: ${error.message}`,
        type: 'error',
        duration: 5000
      });
      
      console.error("Değişiklik uygulama sırasında hata:", error);
    });
}

// Değişiklikleri yoksay
function ignoreUpdates(changes) {
  // Yoksayma bildirimini göster
  const loadingNotification = showNotification({
    title: "Değişiklikler Yoksayılıyor",
    message: '<div class="notification-loading"></div> Değişiklikler yoksayılıyor...',
    type: 'loading',
    duration: 0
  });

  // Backend API'ına istek at
  fetch("/ignore-updates", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      previous_cache: changes.previous_cache
    })
  })
    .then(response => response.json())
    .then(data => {
      // Yükleme bildirimini kapat
      closeNotification(loadingNotification);

      // Sonuçları işle
      if (data.status === "ok") {
        showNotification({
          title: "Değişiklikler Yoksayıldı",
          message: "Değişiklikler geçici olarak yoksayıldı. Bir sonraki kontrol sırasında tekrar hatırlatılacak.",
          type: 'info',
          duration: 5000
        });
      } else {
        showNotification({
          title: "Hata",
          message: data.message || "Değişiklikler yoksayılırken bir hata oluştu.",
          type: 'error',
          duration: 5000
        });
      }
    })
    .catch(error => {
      // Yükleme bildirimini kapat
      closeNotification(loadingNotification);
      
      // Hata bildirimini göster
      showNotification({
        title: "Hata",
        message: `Değişiklikler yoksayılırken bir hata oluştu: ${error.message}`,
        type: 'error',
        duration: 5000
      });
      
      console.error("Değişiklik yoksayma sırasında hata:", error);
    });
}

// Periyodik kontrol
function startPeriodicCheck(interval = 60000) {
  // Sayfa yüklendiğinde ilk kontrolü yap
  setTimeout(checkForUpdates, 3000);
  
  // Belirtilen aralıklarla kontrol et
  setInterval(checkForUpdates, interval);
}

// Sayfa yüklendiğinde başlat
document.addEventListener("DOMContentLoaded", () => {
  injectStyles();
  createNotificationContainer();
  startPeriodicCheck();
  
  // Test amaçlı bir buton ekle
  const rightPanel = document.getElementById("right-panel");
  if (rightPanel) {
    const testButton = document.createElement("button");
    testButton.textContent = "🔍 Değişiklikleri Kontrol Et";
    testButton.style.marginTop = "10px";
    testButton.addEventListener("click", checkForUpdates);
    rightPanel.appendChild(testButton);
  }
});

// Dışa aktarılacak fonksiyonlar
window.appNotifications = {
  show: showNotification,
  close: closeNotification,
  closeAll: closeAllNotifications,
  updateProgress: updateProgressNotification,
  checkForUpdates: checkForUpdates
};
