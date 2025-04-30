import db_utils

# Veritabanında kumaşları listele
fabrics = db_utils.get_all_fabrics()
print(f"Toplam {len(fabrics)} kumaş bulundu.")

# Versiyon bilgilerini getir
versions = db_utils.get_model_versions("pattern")
print(f"Pattern modeli versiyonları: {list(versions.get('versions', {}).keys())}")