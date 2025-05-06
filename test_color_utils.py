# test_color_utils.py
import color_utils
import time
import os

def test_dominant_color_methods():
    # Test görsel dosyası
    test_image = "realImages/örnek_kumaş.jpg"  # Lütfen gerçek bir dosya yolu ile değiştirin
    
    # Klasördeki ilk görseli bul
    if not os.path.exists(test_image):
        for root, dirs, files in os.walk("realImages"):
            for file in files:
                if file.endswith((".jpg", ".jpeg", ".png")):
                    test_image = os.path.join(root, file)
                    break
            if os.path.exists(test_image):
                break
    
    print(f"Test görseli: {test_image}")
    
    # Farklı yöntemleri test et
    print("\nDominant renk çıkarma yöntemleri karşılaştırması:")
    
    # Resize yöntemi
    start_time = time.time()
    resize_color = color_utils.extract_dominant_color(test_image, "resize")
    resize_time = time.time() - start_time
    print(f"  Resize yöntemi: {resize_color} ({resize_time:.3f} saniye)")
    
    # Average yöntemi
    start_time = time.time()
    avg_color = color_utils.extract_dominant_color(test_image, "average")
    avg_time = time.time() - start_time
    print(f"  Average yöntemi: {avg_color} ({avg_time:.3f} saniye)")
    
    # Histogram yöntemi
    start_time = time.time()
    hist_color = color_utils.extract_dominant_color_histogram(test_image)
    hist_time = time.time() - start_time
    print(f"  Histogram yöntemi: {hist_color} ({hist_time:.3f} saniye)")
    
    # K-means yöntemi (3 küme)
    start_time = time.time()
    kmeans_colors = color_utils.extract_dominant_colors_kmeans(test_image, k=3)
    kmeans_time = time.time() - start_time
    print(f"  K-means yöntemi (k=3): {kmeans_colors[0]} ({kmeans_time:.3f} saniye)")
    print(f"    İkincil renkler: {kmeans_colors[1:]}")
    
    # Geliştirilmiş dominant renk çıkarma
    start_time = time.time()
    improved_color = color_utils.extract_dominant_color_improved(test_image)
    improved_time = time.time() - start_time
    print(f"  Geliştirilmiş yöntem: {improved_color} ({improved_time:.3f} saniye)")
    
    # Renk analizi
    start_time = time.time()
    analysis = color_utils.analyze_image_colors(test_image)
    analysis_time = time.time() - start_time
    print(f"\nRenk analizi ({analysis_time:.3f} saniye):")
    print(f"  Dominant renk: {analysis['dominant_color']}")
    print(f"  Renk adı: {analysis['color_name']}")
    print(f"  HSV değerleri: {analysis['dominant_color_hsv']}")
    print(f"  İkincil renkler: {analysis['secondary_colors'][:2]}")
    print(f"  Renk dağılımı: {analysis['color_distribution']}")

if __name__ == "__main__":
    test_dominant_color_methods()