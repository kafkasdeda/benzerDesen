// train_interface.js - Eğitim arayüzü ve fonksiyonları

// Modal yönetimi
function openTrainingModal() {
    document.getElementById('training-modal').style.display = 'block';
  }
  
  function closeTrainingModal() {
    document.getElementById('training-modal').style.display = 'none';
  }
  
  // Modal içeriğini temizle
  function clearModalContent() {
    document.getElementById('modal-body').innerHTML = '';
  }
  
  // Modal içeriğini ayarla
  function setModalContent(content) {
    document.getElementById('modal-body').innerHTML = content;
  }
  
  // Eğitim arayüzünü göster
  function showTrainingInterface(model, version) {
    // Modal'ı aç
    openTrainingModal();
    
    // Modal içeriğini temizle
    clearModalContent();
    
    // İçeriği yükle
    const modalBody = document.getElementById('modal-body');
    
    // Yükleniyor mesajı
    modalBody.innerHTML = '<div style="text-align: center; padding: 20px;">Eğitim arayüzü yükleniyor...</div>';
    
    // Eğitim arayüzünü yükle
    fetchTrainingInterface(model, version);
  }
  
  // Model bilgilerini al
  function fetchTrainingInterface(model, version) {
    // Model bilgilerini almak için API çağrısı
    fetch(`/check-model-exists?model=${model}&version=${version}`)
      .then(res => res.json())
      .then(data => {
        createTrainingForm(model, version, data);
      })
      .catch(err => {
        console.error("Model bilgileri alınamadı:", err);
        createTrainingForm(model, version, { exists: false });
      });
  }
  
  // Eğitim formunu oluştur
  function createTrainingForm(model, version, modelData) {
    const container = document.createElement("div");
    container.className = "training-form-container";
    container.style.padding = "15px";
    container.style.backgroundColor = "#fff";
    container.style.border = "1px solid #ddd";
    container.style.borderRadius = "5px";
    
    // Başlık
    const title = document.createElement("h3");
    title.textContent = `🧠 ${model.toUpperCase()} MODELİ EĞİTİM AYARLARI`;
    title.style.textAlign = "center";
    title.style.marginBottom = "20px";
    container.appendChild(title);
    
    // Model durumu
    const statusContainer = document.createElement("div");
    statusContainer.style.padding = "10px";
    statusContainer.style.backgroundColor = modelData.exists ? "#e8f5e9" : "#fff3e0";
    statusContainer.style.borderRadius = "4px";
    statusContainer.style.marginBottom = "20px";
    
    if (modelData.exists) {
      statusContainer.innerHTML = `
        <strong>✅ Mevcut Model Durumu:</strong> Daha önce eğitilmiş<br>
        <span>Son Eğitim: ${modelData.last_trained || 'Bilinmiyor'}</span>
      `;
    } else {
      statusContainer.innerHTML = `
        <strong>🆕 Mevcut Model Durumu:</strong> İlk kez eğitilecek<br>
        <span>Tahmini süre: ~15 dakika</span>
      `;
    }
    container.appendChild(statusContainer);
    
    // GPU kontrol
    const gpuContainer = document.createElement("div");
    gpuContainer.style.padding = "10px";
    gpuContainer.style.backgroundColor = "#f5f5f5";
    gpuContainer.style.borderRadius = "4px";
    gpuContainer.style.marginBottom = "20px";
    gpuContainer.innerHTML = `
      <span id="gpu-status">🖥️ Donanım durumu kontrol ediliyor...</span>
    `;
    container.appendChild(gpuContainer);
    
    // Eğitim tipi
    const trainingTypeContainer = document.createElement("div");
    trainingTypeContainer.style.marginBottom = "15px";
    trainingTypeContainer.innerHTML = `
      <label style="display: block; margin-bottom: 5px;"><strong>📋 Eğitim Tipi:</strong></label>
      <div style="margin-left: 20px;">
        <label style="display: block; margin-bottom: 5px;">
          <input type="radio" name="training-type" value="fine-tune" ${modelData.exists ? 'checked' : 'disabled'}>
          Fine-tuning ${modelData.exists ? '(tavsiye edilir)' : '(mevcut model gerekli)'}
        </label>
        <label>
          <input type="radio" name="training-type" value="full-train" ${!modelData.exists ? 'checked' : ''}>
          Tamamen ${modelData.exists ? 'yeniden ' : ''}eğit${!modelData.exists ? ' (ilk eğitim)' : ''}
        </label>
      </div>
    `;
    container.appendChild(trainingTypeContainer);
    
    // Temel parametreler
    const basicParamsContainer = document.createElement("div");
    basicParamsContainer.style.marginBottom = "20px";
    
    // Model türüne göre özel ayarları hazırla
    let modelSpecificSettings = '';
    
    if (model === 'pattern') {
      modelSpecificSettings = `
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px;"><strong>🔄 Görsel İşleme:</strong></label>
          <div style="margin-left: 20px;">
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="grayscale" checked>
              Griye çevir (desen modeli için önerilir)
            </label>
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="random-flip" checked>
              Rastgele yatay döndür
            </label>
            <label>
              <input type="checkbox" name="random-rotate" checked>
              ±5° Rastgele döndürme
            </label>
          </div>
        </div>
      `;
    } else if (model === 'color') {
      modelSpecificSettings = `
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px;"><strong>🔄 Görsel İşleme:</strong></label>
          <div style="margin-left: 20px;">
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="color-jitter" checked>
              Renk değişimi (brightness, contrast, saturation)
            </label>
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="random-flip" checked>
              Rastgele yatay döndür
            </label>
          </div>
        </div>
      `;
    } else if (model === 'texture') {
      modelSpecificSettings = `
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px;"><strong>🔄 Görsel İşleme:</strong></label>
          <div style="margin-left: 20px;">
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="grayscale" checked>
              Griye çevir
            </label>
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="gaussian-blur" checked>
              Gaussian bulanıklaştırma
            </label>
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="random-contrast" checked>
              Rastgele kontrast
            </label>
          </div>
        </div>
      `;
    } else if (model === 'color+pattern') {
      modelSpecificSettings = `
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px;"><strong>🔄 Görsel İşleme:</strong></label>
          <div style="margin-left: 20px;">
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="keep-original" checked>
              Orijinal renk korunsun
            </label>
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="separate-features" checked>
              Ayrı renk ve desen özellikleri çıkarılsın
            </label>
            <label style="display: block; margin-bottom: 5px;">
              <input type="checkbox" name="combine-vectors" checked>
              Renk ve desen vektörleri birleştirilsin
            </label>
          </div>
        </div>
      `;
    }
    
    basicParamsContainer.innerHTML = `
      <div style="margin-bottom: 15px;">
        <label style="display: block; margin-bottom: 5px;"><strong>📈 Epoch Sayısı:</strong></label>
        <input type="number" name="epochs" value="${modelData.exists ? '10' : '15'}" min="1" max="100" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
      </div>
      
      <div style="margin-bottom: 15px;">
        <label style="display: block; margin-bottom: 5px;"><strong>📦 Batch Size:</strong></label>
        <input type="number" name="batch-size" value="16" min="1" max="128" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
      </div>
      
      <div style="margin-bottom: 15px;">
        <label style="display: block; margin-bottom: 5px;"><strong>🔍 Öğrenme Hızı:</strong></label>
        <input type="number" name="learning-rate" value="${modelData.exists ? '0.0001' : '0.0005'}" min="0.00001" max="0.1" step="0.0001" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
      </div>
      
      <div style="margin-bottom: 15px;">
        <label style="display: block; margin-bottom: 5px;"><strong>⭐ Feedback Etkisi:</strong></label>
        <input type="range" name="feedback-weight" min="0" max="100" value="50" style="width: 100%;">
        <div style="display: flex; justify-content: space-between;">
          <span>Düşük</span>
          <span>Yüksek</span>
        </div>
      </div>
      
      ${modelSpecificSettings}
    `;
    container.appendChild(basicParamsContainer);
    
    // Butonlar
    const buttonsContainer = document.createElement("div");
    buttonsContainer.style.display = "flex";
    buttonsContainer.style.justifyContent = "space-between";
    buttonsContainer.style.marginTop = "20px";
    
    const cancelButton = document.createElement("button");
    cancelButton.textContent = "EĞİTİMİ İPTAL ET";
    cancelButton.style.padding = "10px 15px";
    cancelButton.style.backgroundColor = "#f5f5f5";
    cancelButton.style.border = "1px solid #ddd";
    cancelButton.style.borderRadius = "4px";
    cancelButton.style.cursor = "pointer";
    cancelButton.addEventListener("click", () => {
      closeTrainingModal();
    });
    
    const startButton = document.createElement("button");
    startButton.innerHTML = "🚀 EĞİTİMİ BAŞLAT";
    startButton.style.padding = "10px 15px";
    startButton.style.backgroundColor = "#4CAF50";
    startButton.style.color = "white";
    startButton.style.border = "none";
    startButton.style.borderRadius = "4px";
    startButton.style.cursor = "pointer";
    startButton.addEventListener("click", () => {
      startTraining(model, version);
    });
    
    buttonsContainer.appendChild(cancelButton);
    buttonsContainer.appendChild(startButton);
    container.appendChild(buttonsContainer);
    
    // Form içeriğini modal'a ekle
    setModalContent('');
    document.getElementById('modal-body').appendChild(container);
    
    // GPU durumunu kontrol et
    checkGPUStatus();
  }
  
  function checkGPUStatus() {
    // Sunucudan GPU durumunu al
    fetch('/check-gpu-status')
      .then(res => res.json())
      .then(data => {
        const gpuStatusElement = document.getElementById('gpu-status');
        if (data.gpu_available) {
          gpuStatusElement.innerHTML = `
            🖥️ Donanım: ${data.gpu_name || 'GPU'}<br>
            ✅ GPU kullanılacak (yaklaşık ${data.speedup || '5-10'}x hızlanma)
          `;
          gpuStatusElement.parentElement.style.backgroundColor = "#e8f5e9";
        } else {
          gpuStatusElement.innerHTML = `
            🖥️ Donanım: CPU-only<br>
            ⚠️ GPU bulunamadı (eğitim yavaş olabilir)
          `;
          gpuStatusElement.parentElement.style.backgroundColor = "#fff3e0";
        }
      })
      .catch(err => {
        document.getElementById('gpu-status').innerHTML = `
          🖥️ Donanım: Bilinmiyor<br>
          ⚠️ Donanım durumu kontrol edilemedi
        `;
      });
  }
  
  function startTraining(model, version) {
    // Form verilerini topla
    const trainingType = document.querySelector('input[name="training-type"]:checked').value;
    const epochs = document.querySelector('input[name="epochs"]').value;
    const batchSize = document.querySelector('input[name="batch-size"]').value;
    const learningRate = document.querySelector('input[name="learning-rate"]').value;
    const feedbackWeight = document.querySelector('input[name="feedback-weight"]').value;
    
    // Model özel ayarları topla
    const modelSpecificSettings = {};
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
      modelSpecificSettings[checkbox.name] = checkbox.checked;
    });
    
    // Eğitim konfigürasyonu oluştur
    const trainingConfig = {
      model_type: model,
      version: version,
      training_type: trainingType,
      epochs: parseInt(epochs),
      batch_size: parseInt(batchSize),
      learning_rate: parseFloat(learningRate),
      feedback_weight: parseInt(feedbackWeight) / 100,
      model_settings: modelSpecificSettings
    };
    
    // Eğitim durumu ekranını göster
    showTrainingProgress(model, version);
    
    // Eğitimi başlat
    fetch('/start-training', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(trainingConfig)
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'started') {
        // Eğitim başladı, durumu güncellemeye başla
        startProgressUpdates(data.training_id);
      } else {
        // Hata oluştu
        alert(`Eğitim başlatılamadı: ${data.message}`);
        closeTrainingModal();
      }
    })
    .catch(err => {
      alert(`Eğitim başlatılamadı: ${err}`);
      closeTrainingModal();
    });
  }
  
  function showTrainingProgress(model, version) {
    // Modal içeriğini temizle
    clearModalContent();
    
    // İlerleme arayüzü
    const progressContainer = document.createElement("div");
    progressContainer.style.padding = "15px";
    
    progressContainer.innerHTML = `
      <h3 style="text-align: center; margin-bottom: 20px;">🧠 MODEL EĞİTİMİ DEVAM EDİYOR</h3>
      
      <div style="margin-bottom: 15px;">
        <strong>Model:</strong> ${model}
        <strong style="margin-left: 20px;">Versiyon:</strong> ${version}
      </div>
      
      <div style="margin-bottom: 10px;">
        <strong>İlerleme:</strong> <span id="progress-epoch">Başlıyor...</span>
      </div>
      
      <div style="margin-bottom: 15px; background-color: #f5f5f5; border-radius: 4px; height: 20px; overflow: hidden;">
        <div id="progress-bar" style="width: 0%; height: 100%; background-color: #4CAF50;"></div>
      </div>
      
      <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
        <div><strong>Geçen süre:</strong> <span id="elapsed-time">0:00</span></div>
        <div><strong>Tahmini kalan süre:</strong> <span id="remaining-time">--:--</span></div>
      </div>
      
      <div style="margin-bottom: 15px;">
        <strong>Güncel Loss:</strong> <span id="current-loss">--</span>
      </div>
      
      <div style="margin-bottom: 15px;">
        <strong>Loss Grafiği:</strong>
        <div id="loss-chart" style="height: 150px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px;">
          <div style="text-align: center; line-height: 150px; color: #999;">
            Eğitim başladığında grafik gösterilecek
          </div>
        </div>
      </div>
      
      <div style="margin-bottom: 15px;">
        <strong>Son log mesajı:</strong>
        <div id="log-message" style="padding: 5px; background-color: #f5f5f5; border-radius: 4px; margin-top: 5px; font-family: monospace;">
          Eğitim başlıyor...
        </div>
      </div>
      
      <div style="display: flex; justify-content: space-between; margin-top: 20px;">
        <button id="stop-training" style="padding: 10px 15px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">EĞİTİMİ DURDUR</button>
        <button id="background-training" style="padding: 10px 15px; background-color: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">ARKAPLANDA DEVAM ET</button>
      </div>
    `;
    
    document.getElementById('modal-body').appendChild(progressContainer);
    
    // Buton olayları
    document.getElementById("stop-training").addEventListener("click", () => {
      if (confirm("Eğitimi durdurmak istediğinize emin misiniz? İlerleme kaydedilmeyecek.")) {
        stopTraining();
      }
    });
    
    document.getElementById("background-training").addEventListener("click", () => {
      alert("Eğitim arka planda devam edecek.");
      closeTrainingModal();
    });
  }
  
  function startProgressUpdates(trainingId) {
    // Her 2 saniyede bir eğitim durumunu güncelle
    const intervalId = setInterval(() => {
      fetch(`/training-status?id=${trainingId}`)
        .then(res => res.json())
        .then(data => {
          updateProgressUI(data);
          
          if (data.status === 'completed' || data.status === 'failed' || data.status === 'stopped') {
            clearInterval(intervalId);
            handleTrainingCompletion(data);
          }
        })
        .catch(err => {
          console.error("Eğitim durumu alınamadı:", err);
        });
    }, 2000);
  }
  
  function updateProgressUI(data) {
    // İlerleme bilgilerini güncelle
    document.getElementById("progress-epoch").textContent = `Epoch ${data.current_epoch}/${data.total_epochs}`;
    document.getElementById("progress-bar").style.width = `${data.progress_percent}%`;
    document.getElementById("elapsed-time").textContent = data.elapsed_time;
    document.getElementById("remaining-time").textContent = data.remaining_time;
    document.getElementById("current-loss").textContent = `${data.current_loss} ${data.loss_trend === 'decreasing' ? '(↓ İyileşiyor)' : data.loss_trend === 'increasing' ? '(↑ Kötüleşiyor)' : ''}`;
    document.getElementById("log-message").textContent = data.last_log;
    
    // Loss grafiği güncelleme (basit şekilde)
    if (data.loss_history && data.loss_history.length > 0) {
      const chartDiv = document.getElementById("loss-chart");
      // Gerçek bir grafik kütüphanesi kullanmak daha iyi olur
      chartDiv.innerHTML = `<div style="height: 150px; position: relative;">
        ${data.loss_history.map((loss, i) => {
          const height = 100 - Math.min(100, loss * 100);
          return `<div style="position: absolute; bottom: 0; left: ${(i / (data.loss_history.length - 1)) * 100}%; width: 4px; height: ${height}%; background-color: #3f51b5;"></div>`;
        }).join('')}
      </div>`;
    }
  }
  
  function handleTrainingCompletion(data) {
    // Eğitim tamamlandı, başarılı veya başarısız olabilir
    if (data.status === 'completed') {
      alert("Eğitim başarıyla tamamlandı!");
    } else if (data.status === 'failed') {
      alert(`Eğitim başarısız oldu: ${data.error_message}`);
    } else if (data.status === 'stopped') {
      alert("Eğitim durduruldu.");
    }
    
    // Modal'ı kapat
    closeTrainingModal();
  }
  
  function stopTraining() {
    fetch('/stop-training', {
      method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'stopped') {
        alert("Eğitim durduruldu.");
        closeTrainingModal();
      } else {
        alert(`Eğitim durdurulamadı: ${data.message}`);
      }
    })
    .catch(err => {
      alert(`Eğitim durdurulamadı: ${err}`);
    });
  }