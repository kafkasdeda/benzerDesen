
# reset_cache.py
# Bu betik, tüm önbellek ve bayrak dosyalarını temizleyerek temiz bir başlangıç yapmanızı sağlar
import os
import json
import datetime

# Metadata cache dosyasını sıfırla
if os.path.exists("metadata_cache.json"):
    os.remove("metadata_cache.json")
    print("✅ metadata_cache.json dosyası silindi")

# Flag dosyalarını temizle
for flag_file in ["updating_clusters.flag", "reset_faiss_indexes.flag"]:
    if os.path.exists(flag_file):
        os.remove(flag_file)
        print(f"✅ {flag_file} dosyası silindi")

# Varsayılan boş bir metadata cache oluştur
with open("metadata_cache.json", "w", encoding="utf-8") as f:
    empty_cache = {
        "images": [],
        "json_hashes": {}
    }
    json.dump(empty_cache, f, indent=2)
    print("✅ Boş metadata_cache.json dosyası oluşturuldu")

# Faiss indekslerini sıfırlamak için flag dosyasını oluştur
with open("reset_faiss_indexes.flag", "w") as f:
    f.write(datetime.datetime.now().isoformat())
    print("✅ Faiss indekslerini sıfırlama bayrağı oluşturuldu")

print("\n🔄 Önbellek ve bayrak dosyaları başarıyla sıfırlandı.")
print("⚠️ Lütfen uygulamayı yeniden başlatın (app.py)")
