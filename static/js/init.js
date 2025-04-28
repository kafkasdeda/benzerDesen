/**
 * init.js
 * Oluşturulma: 2025-04-29
 * Hazırlayan: Kafkas
 * 
 * Açıklama:
 * Bu dosya, uygulamanın ilk yüklendiğinde çalışacak kodları içerir.
 * Faiss indekslerinin hazır olup olmadığını kontrol eder ve gerekirse sunucudan yeniler.
 */

// Sayfa tamamen yüklendiğinde çalış
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 init.js: Sayfa yüklendi, Faiss indeksleri kontrol ediliyor...');
    
    // Faiss indekslerini sıfırla
    fetch('/reset-faiss-indexes')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Faiss indeksleri sıfırlandı:', data.message);
            
            // Sistem bilgilerini al
            return fetch('/system-info');
        })
        .then(response => response.json())
        .then(info => {
            console.log('📊 Sistem bilgileri alındı:', info);
            
            // Kullanıcıya bilgi ver
            if (info.faiss && info.faiss.gpu_count > 0) {
                console.log(`🚀 GPU desteği bulundu! ${info.faiss.gpu_count} adet GPU kullanılabilir.`);
            } else {
                console.log('💻 CPU modu: GPU desteği bulunamadı, CPU kullanılacak.');
            }
            
            // Değişiklikleri kontrol et
            return fetch('/check-updates');
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'changes_detected') {
                console.log('🔄 Değişiklikler algılandı:', data.message);
                
                // Kullanıcıya sor
                if (confirm(`Değişiklikler algılandı: ${data.message}\n\nGüncellemek ister misiniz?`)) {
                    return fetch('/apply-updates', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                }
            } else {
                console.log('✓ Sistem güncel:', data.message);
            }
        })
        .catch(error => {
            console.error('❌ Başlangıç kontrolü sırasında hata:', error);
        });
});
