/**
 * performance-fix.js
 * Oluşturulma: 2025-04-29
 * Hazırlayan: Kafkas
 * 
 * Açıklama:
 * Bu dosya, uygulamanın performans sorunlarını çözmek için özel optimizasyonlar içerir.
 * Diğer JS dosyalarının yüklenme sıralamasını ve bellek yönetimini optimize eder.
 */

// Sayfa yüklendiğinde çalışır
document.addEventListener('DOMContentLoaded', () => {
    console.log('Performance-fix.js: Performans iyileştirmeleri aktif edildi');
    
    // Memory leak temizleme
    window.addEventListener('beforeunload', cleanupMemory);
    
    // Faiss önbelleğini otomatik temizle (60 saniyede bir - eski: 15 saniye)
    setInterval(checkMemoryUsage, 60000);
    
    // Tooltip'leri periyodik olarak temizle (60 saniyede bir)
    setInterval(cleanupTooltips, 60000);
    
    // Hata yakalama
    window.addEventListener('error', handleGlobalError);
    
    // URL parametresi varsa, doğrudan reset işlemi yap
    if (window.location.search.includes('reset_cache=true')) {
        resetAllCaches();
    }
    
    // Sayfa hareketsizlik durumunda tooltip'leri temizle
    setupInactivityCleanup();
    
    // Mouse pozisyonunu takip et (viewport dışına taşan tooltip'ler için)
    setupMousePositionTracking();
    
    // Yeni: Lazily loaded görseller için observer kur
    setupImageObserver();
});

// Bellek kullanımını kontrol et
function checkMemoryUsage() {
    // Tarayıcı bellek bilgisini destekliyorsa
    if (window.performance && window.performance.memory) {
        const memoryInfo = window.performance.memory;
        const usedHeapSize = memoryInfo.usedJSHeapSize / (1024 * 1024);
        const totalHeapSize = memoryInfo.totalJSHeapSize / (1024 * 1024);
        
        // Kullanım oranı
        const usageRatio = usedHeapSize / totalHeapSize;
        
        console.log(`Bellek Kullanımı: ${usedHeapSize.toFixed(2)}MB / ${totalHeapSize.toFixed(2)}MB (${(usageRatio * 100).toFixed(1)}%)`);
        
        // Bellek kritik seviyedeyse temizlik yap - %98 eşiği (çok daha yüksek değer)
        if (usageRatio > 0.98) {
            console.warn('Bellek kullanımı kritik seviyede (%98+), önbellek temizleniyor...');
            clearImageCache();
            resetAllCaches();
        }
        // Yüksek kullanımda hafif temizlik
        else if (usageRatio > 0.95) {
            console.warn('Bellek kullanımı yüksek seviyede (%95+), hafif temizlik yapılıyor...');
            clearImageCache();
        }
    }
}

// Tooltip'leri temizle
function cleanupTooltips() {
    // Açık kalmış tooltip'leri temizle
    const tooltips = document.querySelectorAll('.tooltip');
    if (tooltips.length > 0) {
        console.log(`${tooltips.length} adet açık tooltip temizleniyor...`);
        tooltips.forEach(tooltip => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        });
    }
}

// Sayfa hareketsizlik durumunda tooltip'leri temizleme
function setupInactivityCleanup() {
    let inactivityTimer;
    document.addEventListener('mousemove', function() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(function() {
            cleanupTooltips();
        }, 5000); // 5 saniye hareketsizlik sonrası temizlik
    });
}

// Mouse pozisyonunu takip etme
function setupMousePositionTracking() {
    document.addEventListener('mousemove', function(e) {
        // CSS değişkeni olarak mouse X pozisyonunu ayarla
        document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
    });
}

// Yeni: Görselleri gözlemlemek için Intersection Observer kur
function setupImageObserver() {
    if ('IntersectionObserver' in window) {
        window.imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Orijinal kaynak varsa
                    if (img.dataset.originalSrc) {
                        img.src = img.dataset.originalSrc;
                        delete img.dataset.originalSrc;
                        console.log('🔄 Observer: Görsel geri yüklendi');
                    }
                    // Lazy loading
                    else if (img.dataset.src) {
                        img.src = img.dataset.src;
                        delete img.dataset.src;
                        console.log('🔄 Observer: Lazy loading görsel yüklendi');
                    }
                }
            });
        }, {
            rootMargin: '500px', // 500px marj
            threshold: 0.01 // %1 görünür olduğunda tetikle
        });
        
        // Sayfa yüklendiğinde görselleri gözleme al
        document.querySelectorAll('img[data-src], img[data-original-src]').forEach(img => {
            window.imageObserver.observe(img);
        });
        
        // 10 saniyede bir yeni görselleri kontrol et
        setInterval(() => {
            document.querySelectorAll('img[data-src], img[data-original-src]').forEach(img => {
                window.imageObserver.observe(img);
            });
        }, 10000);
    }
}

// Resim önbelleğini temizle
function clearImageCache() {
    // Görünür olmayan resimleri temizle
    const images = document.querySelectorAll('img');
    let cleared = 0;
    
    // Mevcut görüntü alanını genişlet (yukarı ve aşağı doğru daha fazla 

    const viewportTop = window.scrollY;
    const viewportBottom = window.scrollY + window.innerHeight;
    const viewportMargin = window.innerHeight * 2; // 2 ekran yüksekliği kadar marj
    
    images.forEach(img => {
        // Hangi panelde olduğunu belirle (ebeveyn analizi)
        const isLeftPanel = img.closest('#left-panel') !== null;
        const isCenterPanel = img.closest('#center-panel') !== null;
        const isRightPanel = img.closest('#right-panel') !== null;
        
        // Resmin pozisyonunu al (görünür alandaki pozisyonu değil, sayfadaki mutlak pozisyonu)
        const rect = img.getBoundingClientRect();
        const imgTop = rect.top + window.scrollY;
        const imgBottom = rect.bottom + window.scrollY;
        
        // Görünür alanda olup olmadığını kontrol et (genişletilmiş görünür alan)
        const isVisible = (
            imgBottom >= viewportTop - viewportMargin &&
            imgTop <= viewportBottom + viewportMargin
        );
        
        // Görünür alanda olmayanları temizle
        if (!isVisible && img.src && !img.src.includes('data:image') && !img.src.includes('placeholder')) {
            // Görünür olmayan resmi placeholder ile değiştir
            const originalSrc = img.src;
            img.dataset.originalSrc = originalSrc;
            img.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E";
            img.setAttribute('data-needs-loading', 'true'); // Yüklenmesi gerektiğini belirt
            cleared++;
            
            // Hangi panele ait olduğunu kaydet
            if (isLeftPanel) img.setAttribute('data-panel', 'left');
            else if (isCenterPanel) img.setAttribute('data-panel', 'center');
            else if (isRightPanel) img.setAttribute('data-panel', 'right');
            
            // Console'a log ekle (ebeveyn belirtilerek)
            console.log(`Resim temizlendi: ${originalSrc.split('/').pop()} (Panel: ${isLeftPanel ? 'sol' : isCenterPanel ? 'orta' : isRightPanel ? 'sağ' : 'bilinmiyor'})`);
        }
    });
    
    if (cleared > 0) {
        console.log(`${cleared} adet görünür olmayan resim önbellekten temizlendi`);
    }
    
    // Görünür olmayan resimler için hem scroll hem de intersection observer olayları ekle
    setupScrollLoadingEvents();
}

// Sayfa kaydırıldığında resim önbelleğini yeniden yükle
function handleScroll() {
    // Scroll olayı çok sık tetiklenmesin diye throttle ekleme
    if (window.scrollThrottleTimer) return;
    
    window.scrollThrottleTimer = setTimeout(() => {
        window.scrollThrottleTimer = null;
        
        const images = document.querySelectorAll('img[data-original-src]');
        let restored = 0;
        
        images.forEach(img => {
            const rect = img.getBoundingClientRect();
            const isVisible = (
                rect.top + 2000 >= 0 && // Daha büyük tampon alanı
                rect.left >= 0 &&
                rect.bottom - 2000 <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
            
            if (isVisible && img.dataset.originalSrc) {
                // Görünür olan resimleri orijinal kaynaklarına geri yükle
                img.src = img.dataset.originalSrc;
                delete img.dataset.originalSrc;
                restored++;
                
                // Intersection Observer'a ekle (tekrar temizlenirse diye)
                if (window.imageObserver) {
                    window.imageObserver.observe(img);
                }
            }
        });
        
        if (restored > 0) {
            console.log(`Scroll: ${restored} adet resim önbelleğe geri yüklendi`);
        }
        
        // Scroll olayını kaldırma, her zaman aktif kalsın!
    }, 200); // 200ms throttle
}

// Hata yakalama
function handleGlobalError(event) {
    console.error('Global JS Hatası:', event.message);
    
    // Kritik hatalarda sayfayı yenilemeyi önle
    if (event.message.includes('out of memory') || 
        event.message.includes('heap limit') ||
        event.message.includes('Maximum call stack size exceeded')) {
        
        console.error('Kritik hata tespit edildi, önbellekler temizleniyor...');
        resetAllCaches();
        
        // Kullanıcıya bilgi ver
        if (!document.getElementById('error-notification')) {
            const notification = document.createElement('div');
            notification.id = 'error-notification';
            notification.style.position = 'fixed';
            notification.style.top = '10px';
            notification.style.left = '50%';
            notification.style.transform = 'translateX(-50%)';
            notification.style.backgroundColor = '#f44336';
            notification.style.color = 'white';
            notification.style.padding = '10px 20px';
            notification.style.borderRadius = '4px';
            notification.style.zIndex = '9999';
            notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
            notification.innerHTML = `
                <p>Performans sorunu tespit edildi. Önbellek temizleniyor...</p>
                <button id="reload-page" style="background: white; color: #333; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-left: 10px;">Sayfayı Yenile</button>
            `;
            
            document.body.appendChild(notification);
            
            document.getElementById('reload-page').addEventListener('click', () => {
                location.reload();
            });
            
            // 10 saniye sonra otomatik kaybolma
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 10000);
        }
    }
}

// Sunucuya önbellek temizleme isteği gönder - optimize edilmiş
let lastCacheClearTime = 0;
function requestCacheClear() {
    const now = Date.now();
    
    // Son temizlemeden bu yana en az 30 saniye geçtiyse yeni istek gönder
    if (now - lastCacheClearTime > 30000) {
        lastCacheClearTime = now;
        
        fetch('/reset-faiss-indexes')
            .then(response => response.json())
            .then(data => {
                console.log('Sunucu önbelleği temizlendi:', data.message);
            })
            .catch(error => {
                console.error('Sunucu önbelleği temizlenirken hata:', error);
            });
    } else {
        console.log('Sunucu önbelleği temizleme isteği çok sık, atlandı.');
    }
}

// Tüm önbellekleri sıfırla
function resetAllCaches() {
    console.log('Tüm önbellekler temizleniyor...');
    
    // Faiss indekslerini sıfırla
    if (window.hasOwnProperty('faiss_indexes')) {
        window.faiss_indexes = {};
    }
    
    // Metadata cache'i temizle
    if (window.hasOwnProperty('cached_metadata')) {
        window.cached_metadata = null;
    }
    
    // Diğer önbellekleri temizle
    if (window.hasOwnProperty('cached_features')) {
        window.cached_features = {};
    }
    
    if (window.hasOwnProperty('cached_filenames')) {
        window.cached_filenames = {};
    }
    
    // Sunucuya önbellek temizleme isteği gönder (optimize edilmiş fonksiyon)
    requestCacheClear();
}

// Bellek temizliği
function cleanupMemory() {
    console.log('Bellek temizleniyor...');
    
    // Tooltip'leri temizle
    cleanupTooltips();
    
    // Önbellekleri temizle
    resetAllCaches();
    
    // Olay dinleyicilerini temizle
    document.removeEventListener('scroll', handleScroll);
    
    // Görsel yükleme işlemlerini iptal et
    if ('IntersectionObserver' in window && window.imgObserver) {
        window.imgObserver.disconnect();
    }
    
    // Tüm yükleme bayraklarını temizle
    Array.from(document.querySelectorAll('[data-loading]')).forEach(el => {
        el.removeAttribute('data-loading');
    });
    
    // Kaynamış olabilecek global nesneleri temizle
    for (let key in window) {
        if (key.startsWith('temp_') || key.includes('cache')) {
            delete window[key];
        }
    }
}

// Debug panel ekleyen fonksiyon
let debugPanelActive = false;
let debugIntervalId = null;

function setupDebugPanel() {
    // Eğer panel zaten aktifse tekrar oluşturma
    if (debugPanelActive) return;
    
    // Panel önceden varsa temizle
    const existingPanel = document.getElementById('thumb-debug-panel');
    if (existingPanel) {
        existingPanel.remove();
    }
    
    // Debug paneli oluştur
    const debugPanel = document.createElement('div');
    debugPanel.id = 'thumb-debug-panel';
    debugPanel.style.position = 'fixed';
    debugPanel.style.bottom = '10px';
    debugPanel.style.right = '10px';
    debugPanel.style.backgroundColor = 'rgba(0,0,0,0.7)';
    debugPanel.style.color = 'white';
    debugPanel.style.padding = '10px';
    debugPanel.style.fontSize = '12px';
    debugPanel.style.maxHeight = '300px';
    debugPanel.style.overflow = 'auto';
    debugPanel.style.zIndex = '9999';
    debugPanel.style.borderRadius = '4px';
    debugPanel.style.boxShadow = '0 2px 8px rgba(0,0,0,0.5)';
    debugPanel.innerHTML = '<h3 style="margin-top: 0">Thumbnail Debug Panel</h3><div id="thumb-debug-log"></div>';
    
    // Kapatma butonu ekle
    const closeButton = document.createElement('button');
    closeButton.textContent = 'Kapat';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '5px';
    closeButton.style.right = '5px';
    closeButton.style.padding = '2px 5px';
    closeButton.style.backgroundColor = '#f44336';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.borderRadius = '3px';
    closeButton.style.cursor = 'pointer';
    
    // Panel kapatma işlemi (tamamen kapatma, sadece görünümü gizleme değil)
    closeButton.addEventListener('click', () => {
        debugPanelActive = false;
        
        // Interval'i temizle
        if (debugIntervalId) {
            clearInterval(debugIntervalId);
            debugIntervalId = null;
        }
        
        // Paneli kaldır
        debugPanel.remove();
        
        console.log('Debug paneli kapatıldı, periyodik kontrol durduruldu');
    });
    
    debugPanel.appendChild(closeButton);
    
    // Temizleme butonu ekle
    const clearButton = document.createElement('button');
    clearButton.textContent = 'Temizle';
    clearButton.style.margin = '10px 0 0 0';
    clearButton.style.padding = '5px 10px';
    clearButton.style.backgroundColor = '#2196F3';
    clearButton.style.color = 'white';
    clearButton.style.border = 'none';
    clearButton.style.borderRadius = '3px';
    clearButton.style.cursor = 'pointer';
    clearButton.addEventListener('click', () => document.getElementById('thumb-debug-log').innerHTML = '');
    debugPanel.appendChild(clearButton);
    
    // Sayfaya ekle
    document.body.appendChild(debugPanel);
    debugPanelActive = true;
    
    // Görsel durumlarını günlüğe kaydetme fonksiyonu
    window.logImageStatus = function() {
        // Panel kapanmışsa günlük tutma
        if (!debugPanelActive) return;
        
        const log = document.getElementById('thumb-debug-log');
        if (!log) return; // Panel yoksa çık
        
        const images = document.querySelectorAll('.image-box img');
        
        const logEntry = document.createElement('div');
        logEntry.style.borderBottom = '1px solid rgba(255,255,255,0.2)';
        logEntry.style.padding = '5px 0';
        logEntry.style.marginBottom = '5px';
        logEntry.style.fontSize = '11px';
        
        logEntry.innerHTML = `
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #aaa;">${new Date().toLocaleTimeString()}</span>
                <span style="color: #4CAF50;">Bellek: ${Math.round(window.performance?.memory?.usedJSHeapSize / 1024 / 1024 || 0)}MB</span>
            </div>
            <p>Toplam görsel: <b>${images.length}</b></p>
            <p>data-src olanlar: <b>${document.querySelectorAll('img[data-src]').length}</b></p>
            <p>data-originalSrc olanlar: <b>${document.querySelectorAll('img[data-original-src]').length}</b></p>
            <p>src boş olanlar: <b>${Array.from(images).filter(img => !img.src || img.src === '').length}</b></p>
            <p>src placeholder olanlar: <b>${Array.from(images).filter(img => img.src && img.src.includes('svg')).length}</b></p>
        `;
        
        if (log.children.length > 30) {
            log.removeChild(log.firstChild);
        }
        
        log.appendChild(logEntry);
    };
    
    // 5 saniyede bir durumu güncelleyin
    if (debugIntervalId) clearInterval(debugIntervalId);
    debugIntervalId = setInterval(window.logImageStatus, 5000);
    
    console.log('Debug paneli aktif edildi, 5 saniyede bir güncelleniyor');
}

// Sayfa yüklendiğinde debug panelini ekle
document.addEventListener('DOMContentLoaded', () => {
    // Debug paneli aktif etmek için URL parametresi kontrol et
    if (window.location.search.includes('debug=true')) {
        setTimeout(setupDebugPanel, 1000); // Sayfanın yüklenmesi için biraz bekle
    }
    
    // Debug panelini aç/kapat anahtarı ekle
    document.addEventListener('keydown', (event) => {
        // Alt+D kombinasyonu ile debug panelini aç/kapat
        if (event.altKey && event.key === 'd') {
            if (debugPanelActive) {
                // Panel açıksa kapat
                const panel = document.getElementById('thumb-debug-panel');
                if (panel) {
                    debugPanelActive = false;
                    if (debugIntervalId) {
                        clearInterval(debugIntervalId);
                        debugIntervalId = null;
                    }
                    panel.remove();
                    console.log('Debug paneli klavye kısayolu ile kapatıldı');
                }
            } else {
                // Panel kapalıysa aç
                setupDebugPanel();
                console.log('Debug paneli klavye kısayolu ile açıldı');
            }
        }
    });
});

