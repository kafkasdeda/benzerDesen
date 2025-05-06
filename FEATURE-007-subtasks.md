# FEATURE-007-database-integration Alt Görevleri

## Alt Görev Özeti
FEATURE-007 veritabanı entegrasyonunun tamamlanması için alt görevler

**Ana Görev**: FEATURE-007-database-integration
**Ana Görev Durumu**: Beklemede ⏳
**Ana Görev Önceliği**: P2
**Toplam Tahmini Süre**: 10s

## Alt Görevler

### FEATURE-007.1-endpoint-migration-batch-1
- **Durum**: Beklemede ⏳
- **Öncelik**: P2
- **Tahmini**: 2s
- **Açıklama**: İlk grup endpoint'leri SQLite'a geçirme
- **Kabul Kriterleri**:
  - `/available-versions` endpoint'ini SQLite kullanacak şekilde güncelleme
  - `/move-to-cluster` endpoint'ini SQLite kullanacak şekilde güncelleme
  - Uygun hata yönetimi ekleme
  - Unit testler oluşturma
- **Bağımlılıklar**: Yok (Ana görev FEATURE-007 devam ediyor)

### FEATURE-007.2-endpoint-migration-batch-2
- **Durum**: Beklemede ⏳
- **Öncelik**: P2
- **Tahmini**: 2s
- **Açıklama**: İkinci grup endpoint'leri SQLite'a geçirme
- **Kabul Kriterleri**:
  - `/create-new-version` endpoint'ini SQLite kullanacak şekilde güncelleme
  - `/find-harmonious` endpoint'ini SQLite kullanacak şekilde güncelleme
  - Uygun hata yönetimi ekleme
  - Unit testler oluşturma
- **Bağımlılıklar**: FEATURE-007.1

### FEATURE-007.3-db-performance-optimization
- **Durum**: Beklemede ⏳
- **Öncelik**: P2
- **Tahmini**: 2s
- **Açıklama**: Veritabanı performans optimizasyonu
- **Kabul Kriterleri**:
  - Sorgu optimizasyonları
  - İndeksleme stratejileri
  - Bağlantı havuzu (connection pool) implementasyonu
  - Performans testleri
- **Bağımlılıklar**: FEATURE-007.2

### FEATURE-007.4-json-to-sqlite-transition
- **Durum**: Beklemede ⏳
- **Öncelik**: P2
- **Tahmini**: 2s
- **Açıklama**: JSON'dan veritabanına tam geçiş
- **Kabul Kriterleri**:
  - Kalan JSON dosyaları için veritabanı tablolarını güncelleme
  - Migrasyon scriptlerini iyileştirme
  - Veri bütünlüğü doğrulama
  - Eski JSON okuma kodunu kaldırma
- **Bağımlılıklar**: FEATURE-007.3

### FEATURE-007.5-integration-testing-documentation
- **Durum**: Beklemede ⏳
- **Öncelik**: P2
- **Tahmini**: 2s
- **Açıklama**: Entegrasyon testleri ve dokümantasyon
- **Kabul Kriterleri**:
  - Entegrasyon testleri oluşturma
  - Yeni veritabanı şemasını dokümante etme
  - API dokümantasyonunu güncelleme
  - SQLite entegrasyonu hakkında bilgilendirici yorum eklemesi
- **Bağımlılıklar**: FEATURE-007.4
