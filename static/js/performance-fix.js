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
    console.log('🚀 Performance-fix.js: Performans iyileştirmeleri aktif edildi');
    
    // Memory leak temizleme
    window.addEventListener('beforeunload', cleanupMemory);
    
    // Faiss önbelleğini otomatik temizle (15 saniyede bir)
    setInterval(checkMemoryUsage, 15000);
    
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
});

// Bellek kullanımını kontrol et
function checkMemoryUsage() {
    // Tarayıcı bellek bilgisini destekliyorsa
    if (window.performance && window.performance.memory) {
        const memoryInfo = window.performance.memory;
        const usedHeapSize = memoryInfo.usedJSHeapSize / (1024 * 1024);
        const totalHeapSize = memoryInfo.totalJSHeapSize / (1024 * 1024);
        
        console.log(`📊 Bellek Kullanımı: ${usedHeapSize.toFixed(2)}MB / ${totalHeapSize.toFixed(2)}MB`);
        
        // Bellek kritik seviyedeyse temizlik yap
        if (usedHeapSize > totalHeapSize * 0.8) {
            console.warn('⚠️ Bellek kullanımı kritik seviyede, önbellek temizleniyor...');
            clearImageCache();
            resetAllCaches();
        }
    }
}

// Tooltip'leri temizle
function cleanupTooltips() {
    // Açık kalmış tooltip'leri temizle
    const tooltips = document.querySelectorAll('.tooltip');
    if (tooltips.length > 0) {
        console.log(`🧹 ${tooltips.length} adet açık tooltip temizleniyor...`);
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

// Resim önbelleğini temizle
function clearImageCache() {
    // Görünür olmayan resimleri temizle
    const images = document.querySelectorAll('img');
    let cleared = 0;
    
    images.forEach(img => {
        // Görünür alanda olmayanları kontrol et
        const rect = img.getBoundingClientRect();
        const isVisible = (
            rect.top + 1000 >= 0 &&
            rect.left >= 0 &&
            rect.bottom - 1000 <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        
        if (!isVisible && img.src) {
            // Görünür olmayan resmi placeholder ile değiştir
            const originalSrc = img.src;
            img.dataset.originalSrc = originalSrc;
            img.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E";
            cleared++;
        }
    });
    
    if (cleared > 0) {
        console.log(`🧹 ${cleared} adet görünür olmayan resim önbellekten temizlendi`);
    }
    
    // Görünür olmayan resimler için olay dinleyicisi ekle
    document.addEventListener('scroll', handleScroll, { passive: true });
}

// Sayfa kaydırıldığında resim önbelleğini yeniden yükle
function handleScroll() {
    const images = document.querySelectorAll('img[data-original-src]');
    let restored = 0;
    
    images.forEach(img => {
        const rect = img.getBoundingClientRect();
        const isVisible = (
            rect.top + 500 >= 0 &&
            rect.left >= 0 &&
            rect.bottom - 500 <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        
        if (isVisible && img.dataset.originalSrc) {
            // Görünür olan resimleri orijinal kaynaklarına geri yükle
            img.src = img.dataset.originalSrc;
            delete img.dataset.originalSrc;
            restored++;
        }
    });
    
    if (restored > 0) {
        console.log(`🔄 ${restored} adet resim önbelleğe geri yüklendi`);
    }
    
    // Tüm resimler işlendiyse scroll olayını temizle
    if (images.length === 0) {
        document.removeEventListener('scroll', handleScroll);
    }
}

// Hata yakalama
function handleGlobalError(event) {
    console.error('🔴 Global JS Hatası:', event.message);
    
    // Kritik hatalarda sayfayı yenilemeyi önle
    if (event.message.includes('out of memory') || 
        event.message.includes('heap limit') ||
        event.message.includes('Maximum call stack size exceeded')) {
        
        console.error('🚨 Kritik hata tespit edildi, önbellekler temizleniyor...');
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

// Tüm önbellekleri sıfırla
function resetAllCaches() {
    console.log('🧹 Tüm önbellekler temizleniyor...');
    
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
    
    // Sunucuya önbellek temizleme isteği gönder
    fetch('/reset-faiss-indexes')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Sunucu önbelleği temizlendi:', data.message);
        })
        .catch(error => {
            console.error('❌ Sunucu önbelleği temizlenirken hata:', error);
        });
}

// Bellek temizliği
function cleanupMemory() {
    console.log('🧹 Bellek temizleniyor...');
    
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
