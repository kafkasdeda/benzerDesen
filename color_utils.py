# color_utils.py
"""
Renk uzayı dönüşümleri ve renk benzerliği hesaplamaları için yardımcı fonksiyonlar.

Bu modül, RGB ve HSV renk uzayları arasında dönüşüm, renk benzerliği hesaplama
ve renk uzayında mesafe ölçümü gibi fonksiyonları içerir. Benzer Desen projesinde
renk modeli iyileştirmeleri için kullanılır.
"""

import math
import colorsys
import numpy as np
from typing import Tuple, List, Union, Optional


def rgb_to_hsv(rgb: Union[Tuple[int, int, int], List[int], np.ndarray]) -> Tuple[float, float, float]:
    """
    RGB renk uzayından HSV renk uzayına dönüşüm yapar.
    
    Args:
        rgb: RGB değerleri içeren tuple, liste veya ndarray (0-255 aralığında)
        
    Returns:
        HSV değerlerini içeren tuple (H: 0-1, S: 0-1, V: 0-1)
        
    Examples:
        >>> rgb_to_hsv((255, 0, 0))  # Kırmızı
        (0.0, 1.0, 1.0)
        >>> rgb_to_hsv([0, 255, 0])  # Yeşil
        (0.33333333333333337, 1.0, 1.0)
    """
    r, g, b = rgb
    
    # RGB değerlerini 0-1 aralığına normalize et
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    
    return colorsys.rgb_to_hsv(r, g, b)


def hsv_to_rgb(hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
    """
    HSV renk uzayından RGB renk uzayına dönüşüm yapar.
    
    Args:
        hsv: HSV değerleri içeren tuple (H: 0-1, S: 0-1, V: 0-1)
        
    Returns:
        RGB değerlerini içeren tuple (0-255 aralığında)
        
    Examples:
        >>> hsv_to_rgb((0.0, 1.0, 1.0))  # Kırmızı
        (255, 0, 0)
        >>> hsv_to_rgb((0.33333333333333337, 1.0, 1.0))  # Yeşil
        (0, 255, 0)
    """
    h, s, v = hsv
    
    # HSV'den RGB'ye dönüştür (0-1 aralığında)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # 0-255 aralığına dönüştür ve yuvarlama yap
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)
    
    return (r, g, b)


def calculate_hue_distance(h1: float, h2: float) -> float:
    """
    İki ton (hue) değeri arasındaki dairesel mesafeyi hesaplar.
    
    Ton değerleri 0-1 aralığında bir dairede gösterildiğinden,
    iki ton arasındaki mesafe daire üzerindeki en kısa yol olarak hesaplanır.
    
    Args:
        h1: Birinci ton değeri (0-1 aralığında)
        h2: İkinci ton değeri (0-1 aralığında)
        
    Returns:
        İki ton değeri arasındaki mesafe (0-0.5 aralığında)
        
    Examples:
        >>> calculate_hue_distance(0.1, 0.2)  # Yakın tonlar
        0.1
        >>> calculate_hue_distance(0.9, 0.1)  # Daire etrafında yakın tonlar
        0.2
    """
    # Mutlak farkı hesapla
    diff = abs(h1 - h2)
    
    # Daire üzerindeki en kısa yolu bul (0.5'ten büyükse diğer yönden git)
    if diff > 0.5:
        diff = 1.0 - diff
        
    return diff


def calculate_hsv_distance(hsv1: Tuple[float, float, float], 
                          hsv2: Tuple[float, float, float],
                          weights: Optional[Tuple[float, float, float]] = None) -> float:
    """
    İki HSV renk değeri arasındaki ağırlıklı mesafeyi hesaplar.
    
    Ton için dairesel mesafe, doygunluk ve parlaklık için doğrusal
    mesafe hesaplanır. Üç bileşen ağırlıklandırılarak toplam mesafe bulunur.
    
    Args:
        hsv1: Birinci HSV değeri (H: 0-1, S: 0-1, V: 0-1)
        hsv2: İkinci HSV değeri (H: 0-1, S: 0-1, V: 0-1)
        weights: Ton, doygunluk ve parlaklık için ağırlıklar (varsayılan: [0.6, 0.3, 0.1])
        
    Returns:
        İki renk arasındaki ağırlıklı mesafe (0-1 aralığında)
        
    Examples:
        >>> calculate_hsv_distance((0.1, 0.5, 0.5), (0.2, 0.5, 0.5))  # Sadece ton farkı
        0.12
        >>> calculate_hsv_distance((0.1, 0.5, 0.5), (0.1, 0.8, 0.5))  # Sadece doygunluk farkı
        0.09
    """
    if weights is None:
        weights = (0.6, 0.3, 0.1)  # Ton, doygunluk, parlaklık ağırlıkları
        
    h1, s1, v1 = hsv1
    h2, s2, v2 = hsv2
    w_h, w_s, w_v = weights
    
    # Ton mesafesi (dairesel)
    h_distance = calculate_hue_distance(h1, h2)
    
    # Doygunluk ve parlaklık mesafesi (doğrusal)
    s_distance = abs(s1 - s2)
    v_distance = abs(v1 - v2)
    
    # Ağırlıklı toplam mesafe
    weighted_distance = (w_h * h_distance) + (w_s * s_distance) + (w_v * v_distance)
    
    # Mesafeyi 0-1 aralığına normalize et
    normalized_distance = weighted_distance / (w_h * 0.5 + w_s + w_v)
    
    return normalized_distance


def calculate_color_similarity(color1: Union[Tuple[int, int, int], List[int], np.ndarray],
                              color2: Union[Tuple[int, int, int], List[int], np.ndarray],
                              weights: Optional[Tuple[float, float, float]] = None) -> float:
    """
    İki RGB renk değeri arasındaki benzerliği hesaplar.
    
    Renkler önce HSV uzayına dönüştürülür, ağırlıklı mesafe hesaplanır
    ve benzerlik değeri (1 - mesafe) olarak döndürülür.
    
    Args:
        color1: Birinci RGB renk değeri (0-255 aralığında)
        color2: İkinci RGB renk değeri (0-255 aralığında)
        weights: Ton, doygunluk ve parlaklık için ağırlıklar (varsayılan: [0.6, 0.3, 0.1])
        
    Returns:
        İki renk arasındaki benzerlik (0-1 aralığında, 1: tam benzer, 0: tamamen farklı)
        
    Examples:
        >>> calculate_color_similarity((255, 0, 0), (255, 0, 0))  # Aynı renk
        1.0
        >>> calculate_color_similarity((255, 0, 0), (0, 255, 0))  # Kırmızı ve yeşil
        0.4
    """
    # RGB'den HSV'ye dönüşüm
    hsv1 = rgb_to_hsv(color1)
    hsv2 = rgb_to_hsv(color2)
    
    # HSV mesafesi hesapla
    distance = calculate_hsv_distance(hsv1, hsv2, weights)
    
    # Benzerlik = 1 - mesafe
    similarity = 1.0 - distance
    
    return similarity


def identify_color_group(hsv: Tuple[float, float, float]) -> str:
    """
    HSV renk değerine göre renk grubunu belirler.
    
    Args:
        hsv: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        
    Returns:
        Renk grubu adı (Kırmızı, Turuncu, Sarı, vb.)
        
    Examples:
        >>> identify_color_group((0.0, 1.0, 1.0))
        'Kırmızı'
        >>> identify_color_group((0.33, 1.0, 1.0))
        'Yeşil'
    """
    h, s, v = hsv
    
    # Doygunluk ve parlaklık düşükse, gri tonları
    if s < 0.15:
        if v < 0.25:
            return "Siyah"
        elif v < 0.7:
            return "Gri"
        else:
            return "Beyaz"
    
    # Parlaklık çok düşükse siyah
    if v < 0.15:
        return "Siyah"
    
    # Ton değerine göre renk grupları
    h_360 = h * 360  # 0-360 aralığına dönüştür
    
    if 0 <= h_360 < 15 or h_360 >= 345:
        return "Kırmızı"
    elif 15 <= h_360 < 45:
        return "Turuncu"
    elif 45 <= h_360 < 75:
        return "Sarı"
    elif 75 <= h_360 < 105:
        return "Sarı-Yeşil"
    elif 105 <= h_360 < 135:
        return "Yeşil"
    elif 135 <= h_360 < 165:
        return "Yeşil-Cyan"
    elif 165 <= h_360 < 195:
        return "Cyan"
    elif 195 <= h_360 < 225:
        return "Cyan-Mavi"
    elif 225 <= h_360 < 255:
        return "Mavi"
    elif 255 <= h_360 < 285:
        return "Mavi-Mor"
    elif 285 <= h_360 < 315:
        return "Mor"
    elif 315 <= h_360 < 345:
        return "Mor-Kırmızı"
    
    return "Bilinmeyen"


def get_color_name(rgb: Union[Tuple[int, int, int], List[int], np.ndarray]) -> str:
    """
    RGB renk değerine göre renk adını döndürür.
    
    Args:
        rgb: RGB renk değeri (0-255 aralığında)
        
    Returns:
        Renk adı
        
    Examples:
        >>> get_color_name((255, 0, 0))
        'Kırmızı'
        >>> get_color_name((0, 255, 0))
        'Yeşil'
    """
    hsv = rgb_to_hsv(rgb)
    return identify_color_group(hsv)


def extract_dominant_color(image_path: str, method: str = 'average') -> Tuple[int, int, int]:
    """
    Bir görselden dominant rengi çıkarır.
    
    Args:
        image_path: Görsel dosyasının yolu
        method: Kullanılacak yöntem ('average' veya 'resize')
        
    Returns:
        Dominant RGB renk değeri (0-255 aralığında)
        
    Examples:
        >>> extract_dominant_color('realImages/fabric001.jpg')
        (120, 87, 95)
    """
    import cv2
    
    # Görseli oku
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Görsel bulunamadı: {image_path}")
    
    # BGR'den RGB'ye dönüştür
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    if method == 'resize':
        # 1x1'e küçült - en basit dominant renk metodu
        resized = cv2.resize(img, (1, 1))
        dominant_color = resized[0, 0].tolist()
    else:  # 'average'
        # Ortalama rengi hesapla
        avg_color_per_row = np.average(img, axis=0)
        dominant_color = np.average(avg_color_per_row, axis=0).astype(int).tolist()
    
    return tuple(dominant_color)


def find_harmonious_colors(rgb_color: Tuple[int, int, int], 
                          harmony_type: str = "complementary") -> List[Tuple[int, int, int]]:
    """
    Belirli bir renk için uyumlu renkleri bulur.
    
    Desteklenen uyum tipleri:
    - complementary: Tamamlayıcı renk (renk çemberinde 180° karşıt)
    - analogous: Analog renkler (renk çemberinde yanındaki renkler, ±30°)
    - triadic: Triadik renkler (renk çemberinde eşit aralıklı üç renk, 120° arayla)
    - split-complementary: Ayrık tamamlayıcı (tamamlayıcının her iki yanından 30°)
    - monochromatic: Aynı rengin farklı doygunluk ve parlaklık değerleri
    
    Args:
        rgb_color: RGB renk değeri (0-255 aralığında)
        harmony_type: Uyum tipi 
        
    Returns:
        Uyumlu RGB renkleri listesi
        
    Examples:
        >>> find_harmonious_colors((255, 0, 0), "complementary")
        [(0, 255, 255)]
        >>> find_harmonious_colors((255, 0, 0), "analogous")
        [(255, 128, 0), (255, 0, 128)]
    """
    # RGB'den HSV'ye dönüştür
    r, g, b = rgb_color
    h, s, v = rgb_to_hsv(rgb_color)
    
    harmonious_colors = []
    
    if harmony_type == "complementary":
        # Tamamlayıcı renk (180° karşısı)
        complementary_h = (h + 0.5) % 1.0
        complementary_rgb = hsv_to_rgb((complementary_h, s, v))
        harmonious_colors.append(complementary_rgb)
        
    elif harmony_type == "analogous":
        # Analog renkler (±30°)
        for angle in [-30, 30]:
            analog_h = (h + angle/360) % 1.0
            analog_rgb = hsv_to_rgb((analog_h, s, v))
            harmonious_colors.append(analog_rgb)
            
    elif harmony_type == "triadic":
        # Triadik renkler (120° arayla)
        for angle in [120, 240]:
            triadic_h = (h + angle/360) % 1.0
            triadic_rgb = hsv_to_rgb((triadic_h, s, v))
            harmonious_colors.append(triadic_rgb)
            
    elif harmony_type == "split-complementary":
        # Ayrık tamamlayıcı (tamamlayıcının her iki yanı)
        comp_h = (h + 0.5) % 1.0
        for angle in [-30, 30]:
            split_h = (comp_h + angle/360) % 1.0
            split_rgb = hsv_to_rgb((split_h, s, v))
            harmonious_colors.append(split_rgb)
            
    elif harmony_type == "monochromatic":
        # Monokromatik renkler (aynı rengin farklı doygunluk ve parlaklık değerleri)
        # Daha açık ve daha koyu versiyonlar
        for value_mod in [-0.3, -0.15, 0.15, 0.3]:
            new_v = max(0.1, min(0.9, v + value_mod))
            mono_rgb = hsv_to_rgb((h, s, new_v))
            harmonious_colors.append(mono_rgb)
    
    return harmonious_colors


def calculate_color_distance(rgb1: Tuple[int, int, int], 
                            rgb2: Tuple[int, int, int], 
                            metric: str = "hsv") -> float:
    """
    İki renk arasındaki mesafeyi hesaplar.
    
    Args:
        rgb1: Birinci RGB renk değeri (0-255 aralığında)
        rgb2: İkinci RGB renk değeri (0-255 aralığında)
        metric: Kullanılacak metrik ('hsv', 'rgb', 'lab')
        
    Returns:
        İki renk arasındaki mesafe (0-1 aralığında)
        
    Examples:
        >>> calculate_color_distance((255, 0, 0), (255, 0, 0))
        0.0
        >>> calculate_color_distance((255, 0, 0), (0, 255, 0))
        0.6
    """
    if metric == "hsv":
        # HSV bazlı mesafe
        hsv1 = rgb_to_hsv(rgb1)
        hsv2 = rgb_to_hsv(rgb2)
        return calculate_hsv_distance(hsv1, hsv2)
        
    elif metric == "rgb":
        # RGB öklid mesafesi
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        
        # 0-1 aralığına normalize et
        r1, g1, b1 = r1/255.0, g1/255.0, b1/255.0
        r2, g2, b2 = r2/255.0, g2/255.0, b2/255.0
        
        distance = math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)
        
        # 0-1 aralığına normalize et (maksimum mesafe = √3)
        return min(1.0, distance / math.sqrt(3))
        
    elif metric == "lab":
        # Lab renk uzayında mesafe (daha algısal)
        # Tam implementasyon için skimage veya opencv kullanımı gerekir
        # Burada basit bir yaklaşım kullanıyoruz
        return calculate_color_similarity(rgb1, rgb2, weights=(0.5, 0.3, 0.2))
    
    # Varsayılan: HSV benzerliği
    return 1.0 - calculate_color_similarity(rgb1, rgb2)

def extract_dominant_colors_kmeans(image_path: str, k: int = 3, 
                                 sample_size: int = 1000) -> List[Tuple[int, int, int]]:
    """
    K-Means kümeleme kullanarak bir görselden dominant renkleri çıkarır.
    
    Args:
        image_path: Görsel dosyasının yolu
        k: Çıkarılacak renk sayısı
        sample_size: Analiz için kullanılacak piksel örnek sayısı. None ise tüm pikseller kullanılır.
        
    Returns:
        En baskın k adet RGB renk değerini büyükten küçüğe sıralanmış olarak döndürür
        
    Examples:
        >>> extract_dominant_colors_kmeans('realImages/fabric001.jpg', k=3)
        [(120, 87, 95), (78, 45, 49), (180, 142, 158)]
    """
    import cv2
    from sklearn.cluster import KMeans
    
    # Görseli oku
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Görsel bulunamadı: {image_path}")
    
    # BGR'den RGB'ye dönüştür
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Görsel boyutlarını al
    height, width, _ = img.shape
    
    # Görseli yeniden şekillendir (pikselleri düzleştir)
    pixels = img.reshape((-1, 3))
    
    # Örnek boyutu 
    if sample_size is not None and sample_size < len(pixels):
        import numpy as np
        indices = np.random.permutation(len(pixels))[:sample_size]
        pixels = pixels[indices]
    
    # K-Means kümeleme uygula
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    kmeans.fit(pixels)
    
    # Küme merkezlerini alma (renk değerleri)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Küme boyutlarını hesapla
    labels = kmeans.labels_
    counts = [sum(labels == i) for i in range(k)]
    
    # Küme boyutlarına göre renkleri sırala (büyükten küçüğe)
    colors_with_counts = list(zip(colors, counts))
    colors_with_counts.sort(key=lambda x: x[1], reverse=True)
    
    # Sadece renkleri döndür
    dominant_colors = [tuple(color) for color, _ in colors_with_counts]
    
    return dominant_colors


def extract_dominant_color_kmeans(image_path: str, k: int = 5) -> Tuple[int, int, int]:
    """
    K-Means kümeleme kullanarak bir görselden en dominant rengi çıkarır.
    
    Bu fonksiyon extract_dominant_colors_kmeans fonksiyonunu çağırır ve 
    sadece en baskın rengi döndürür.
    
    Args:
        image_path: Görsel dosyasının yolu
        k: Analiz için kullanılacak küme sayısı (daha yüksek k değeri daha iyi sonuç verir)
        
    Returns:
        En baskın RGB renk değeri
        
    Examples:
        >>> extract_dominant_color_kmeans('realImages/fabric001.jpg')
        (120, 87, 95)
    """
    dominant_colors = extract_dominant_colors_kmeans(image_path, k=k)
    if dominant_colors:
        return dominant_colors[0]
    return (0, 0, 0)  # Hata durumunda siyah döndür


def extract_color_histogram(image_path: str, bins: int = 8) -> dict:
    """
    Bir görselin renk histogramını çıkarır.
    
    Args:
        image_path: Görsel dosyasının yolu
        bins: Her bir kanal için bin sayısı
        
    Returns:
        Renk histogramı bilgilerini içeren sözlük:
        {
            'histogram': 3D histogram array,
            'bin_edges': Histogram aralıkları,
            'centers': Bin merkezleri,
            'dominant_colors': [(renk1, frekans1), (renk2, frekans2), ...]
        }
        
    Examples:
        >>> hist = extract_color_histogram('realImages/fabric001.jpg')
        >>> len(hist['dominant_colors'])
        10
    """
    import cv2
    import numpy as np
    
    # Görseli oku
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Görsel bulunamadı: {image_path}")
    
    # BGR'den RGB'ye dönüştür
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 3D histogram hesapla (R, G, B)
    hist_range = [0, 256]
    hist = np.histogramdd(
        img.reshape(-1, 3),
        bins=bins,
        range=[hist_range, hist_range, hist_range]
    )
    
    # Histogram ve bin kenarlarını çıkar
    hist_values = hist[0]
    bin_edges = hist[1]
    
    # Bin merkezlerini hesapla
    centers = []
    for i, edges in enumerate(bin_edges):
        centers.append((edges[:-1] + edges[1:]) / 2)
    
    # En yüksek frekansa sahip bin'leri bul
    indices = np.argsort(hist_values.flatten())[::-1]  # İndeksleri büyükten küçüğe sırala
    
    # Top-10 dominant renkleri çıkar
    dominant_colors = []
    for i in range(min(10, len(indices))):
        # 3D indeksi hesapla
        idx = np.unravel_index(indices[i], hist_values.shape)
        
        # Renk değerlerini hesapla
        r = int(centers[0][idx[0]])
        g = int(centers[1][idx[1]])
        b = int(centers[2][idx[2]])
        
        # Frekansı normalleştir
        frequency = hist_values[idx] / hist_values.sum()
        
        dominant_colors.append(((r, g, b), float(frequency)))
    
    return {
        'histogram': hist_values,
        'bin_edges': bin_edges,
        'centers': centers,
        'dominant_colors': dominant_colors
    }


def extract_dominant_color_histogram(image_path: str, bins: int = 32) -> Tuple[int, int, int]:
    """
    Histogram analizi kullanarak bir görselden en dominant rengi çıkarır.
    
    Bu yaklaşım K-Means'e göre daha hızlıdır ve küçük kumaş görselleri için 
    genelde yeterli doğruluk sağlar.
    
    Args:
        image_path: Görsel dosyasının yolu
        bins: Histogram için bin sayısı (daha yüksek değer daha iyi sonuç verir)
        
    Returns:
        En baskın RGB renk değeri
        
    Examples:
        >>> extract_dominant_color_histogram('realImages/fabric001.jpg')
        (118, 85, 93)
    """
    hist_result = extract_color_histogram(image_path, bins=bins)
    if hist_result['dominant_colors']:
        return hist_result['dominant_colors'][0][0]
    return (0, 0, 0)  # Hata durumunda siyah döndür


def extract_dominant_color_improved(image_path: str, method: str = 'kmeans') -> Tuple[int, int, int]:
    """
    Geliştirilmiş dominant renk çıkarma fonksiyonu.
    
    Farklı yöntemleri destekler:
    - 'kmeans': K-Means kümeleme (en doğru ama yavaş)
    - 'histogram': Renk histogramı analizi (hızlı)
    - 'average': Ortalama renk (en hızlı ama en az doğru)
    - 'resize': 1x1 piksel küçültme (hızlı ama yeterince doğru değil)
    
    Args:
        image_path: Görsel dosyasının yolu
        method: Kullanılacak yöntem ('kmeans', 'histogram', 'average', 'resize')
        
    Returns:
        En baskın RGB renk değeri
        
    Examples:
        >>> extract_dominant_color_improved('realImages/fabric001.jpg', 'kmeans')
        (120, 87, 95)
        >>> extract_dominant_color_improved('realImages/fabric001.jpg', 'histogram')
        (118, 85, 93)
    """
    if method == 'kmeans':
        return extract_dominant_color_kmeans(image_path)
    elif method == 'histogram':
        return extract_dominant_color_histogram(image_path)
    else:
        # Eski fonksiyonu kullan ('average' veya 'resize' için)
        return extract_dominant_color(image_path, method)


def extract_dominant_colors(image_path: str, method: str = 'kmeans', 
                          k: int = 5) -> List[Tuple[int, int, int]]:
    """
    Bir görselden birden fazla dominant renk çıkarır.
    
    Args:
        image_path: Görsel dosyasının yolu
        method: Kullanılacak yöntem ('kmeans', 'histogram')
        k: Çıkarılacak renk sayısı (sadece 'kmeans' için geçerli)
        
    Returns:
        Dominant RGB renk değerleri listesi (en baskından en az baskına doğru)
        
    Examples:
        >>> colors = extract_dominant_colors('realImages/fabric001.jpg', 'kmeans', k=3)
        >>> len(colors)
        3
    """
    if method == 'kmeans':
        return extract_dominant_colors_kmeans(image_path, k=k)
    elif method == 'histogram':
        hist_result = extract_color_histogram(image_path, bins=min(k*2, 32))
        return [color for color, _ in hist_result['dominant_colors'][:k]]
    else:
        # Yöntem desteklenmiyor, sadece bir renk döndür
        return [extract_dominant_color(image_path, method)]


def convert_image_to_hsv(image_path: str) -> np.ndarray:
    """
    Bir görseli HSV renk uzayına dönüştürür.
    
    Args:
        image_path: Görsel dosyasının yolu
        
    Returns:
        HSV renk uzayındaki görsel (numpy array)
        
    Examples:
        >>> hsv_img = convert_image_to_hsv('realImages/fabric001.jpg')
        >>> hsv_img.shape
        (height, width, 3)
    """
    import cv2
    
    # Görseli oku
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Görsel bulunamadı: {image_path}")
    
    # BGR'den HSV'ye dönüştür
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    return hsv_img


def analyze_image_colors(image_path: str) -> dict:
    """
    Bir görselin renk özelliklerini analiz eder.
    
    Args:
        image_path: Görsel dosyasının yolu
        
    Returns:
        Renk analizi sonuçlarını içeren sözlük:
        {
            'dominant_color': (r, g, b),
            'dominant_color_hsv': (h, s, v),
            'color_name': 'Kırmızı',
            'secondary_colors': [(r, g, b), ...],
            'histogram_data': {...},
            'color_distribution': {'Kırmızı': 0.3, 'Mavi': 0.2, ...}
        }
        
    Examples:
        >>> analysis = analyze_image_colors('realImages/fabric001.jpg')
        >>> analysis['color_name']
        'Bordo'
    """
    import cv2
    import numpy as np
    
    # Görseli oku
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Görsel bulunamadı: {image_path}")
    
    # BGR'den RGB'ye dönüştür
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # BGR'den HSV'ye dönüştür
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Dominant renkler
    dominant_colors = extract_dominant_colors_kmeans(image_path, k=5)
    dominant_color_rgb = dominant_colors[0] if dominant_colors else (0, 0, 0)
    
    # RGB'den HSV'ye dönüştür
    dominant_color_hsv = rgb_to_hsv(dominant_color_rgb)
    
    # Renk adı
    color_name = identify_color_group(dominant_color_hsv)
    
    # Renk dağılımı
    color_distribution = {}
    for color in dominant_colors:
        hsv = rgb_to_hsv(color)
        name = identify_color_group(hsv)
        if name in color_distribution:
            color_distribution[name] += 1
        else:
            color_distribution[name] = 1
    
    # Normalleştirme
    total = sum(color_distribution.values())
    if total > 0:
        color_distribution = {k: v/total for k, v in color_distribution.items()}
    
    # Histogram
    hist_result = extract_color_histogram(image_path, bins=16)
    
    return {
        'dominant_color': dominant_color_rgb,
        'dominant_color_hsv': dominant_color_hsv,
        'color_name': color_name,
        'secondary_colors': dominant_colors[1:] if len(dominant_colors) > 1 else [],
        'histogram_data': hist_result,
        'color_distribution': color_distribution
    }


def create_color_spectrum_structure(divisions: int = 12, saturation_levels: int = 3, 
                                  value_levels: int = 3) -> dict:
    """
    Renk spektrumu organizasyon yapısı oluşturur.
    
    Args:
        divisions: Ton (hue) bölümlerinin sayısı (12 = her 30 derece)
        saturation_levels: Doygunluk seviyelerinin sayısı
        value_levels: Parlaklık seviyelerinin sayısı
        
    Returns:
        Renk spektrumu organizasyon yapısını içeren sözlük
        
    Examples:
        >>> spectrum = create_color_spectrum_structure()
        >>> len(spectrum['hue_divisions'])
        12
    """
    # Renk isimleri (ton bölümleri için)
    color_names = [
        "Kırmızı", "Kırmızı-Turuncu", "Turuncu", "Sarı-Turuncu",
        "Sarı", "Sarı-Yeşil", "Yeşil", "Yeşil-Cyan",
        "Cyan", "Cyan-Mavi", "Mavi", "Mor"
    ]
    
    # Doygunluk seviyeleri için etiketler
    saturation_labels = ["Soluk", "Orta", "Canlı"]
    
    # Parlaklık seviyeleri için etiketler
    value_labels = ["Koyu", "Orta", "Açık"]
    
    # Ton bölümleri oluştur
    hue_divisions = []
    for i in range(divisions):
        start_hue = i / divisions
        end_hue = (i + 1) / divisions
        
        # İlk bölüm kırmızı olacak şekilde ayarla
        name = color_names[i % len(color_names)]
        
        hue_divisions.append({
            'index': i,
            'name': name,
            'start_hue': start_hue,
            'end_hue': end_hue,
            'center_hue': (start_hue + end_hue) / 2,
            'saturation_groups': []
        })
    
    # Her ton bölümüne doygunluk grupları ekle
    for hue_div in hue_divisions:
        for s in range(saturation_levels):
            start_sat = s / saturation_levels
            end_sat = (s + 1) / saturation_levels
            
            saturation_group = {
                'index': s,
                'name': saturation_labels[s % len(saturation_labels)],
                'start_saturation': start_sat,
                'end_saturation': end_sat,
                'center_saturation': (start_sat + end_sat) / 2,
                'value_groups': []
            }
            
            # Her doygunluk grubuna parlaklık grupları ekle
            for v in range(value_levels):
                start_val = v / value_levels
                end_val = (v + 1) / value_levels
                
                value_group = {
                    'index': v,
                    'name': value_labels[v % len(value_labels)],
                    'start_value': start_val,
                    'end_value': end_val,
                    'center_value': (start_val + end_val) / 2,
                    'members': []  # Bu gruba ait görsel dosya adları buraya eklenecek
                }
                
                saturation_group['value_groups'].append(value_group)
            
            hue_div['saturation_groups'].append(saturation_group)
    
    return {
        'hue_divisions': hue_divisions,
        'divisions': divisions,
        'saturation_levels': saturation_levels,
        'value_levels': value_levels,
        'metadata': {
            'color_names': color_names,
            'saturation_labels': saturation_labels,
            'value_labels': value_labels
        }
    }


def classify_color_in_spectrum(hsv: Tuple[float, float, float], 
                             spectrum: dict) -> Tuple[int, int, int]:
    """
    Bir HSV renk değerini spektrum yapısında sınıflandırır.
    
    Args:
        hsv: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        spectrum: create_color_spectrum_structure ile oluşturulan spektrum yapısı
        
    Returns:
        (hue_index, saturation_index, value_index) üçlüsü
        
    Examples:
        >>> spectrum = create_color_spectrum_structure()
        >>> classify_color_in_spectrum((0.0, 1.0, 1.0), spectrum)  # Kırmızı
        (0, 2, 2)
    """
    h, s, v = hsv
    divisions = spectrum['divisions']
    saturation_levels = spectrum['saturation_levels']
    value_levels = spectrum['value_levels']
    
    # Ton indeksini hesapla (dairesel özelliği göz önünde bulundurarak)
    hue_index = int((h * divisions) % divisions)
    
    # Doygunluk indeksini hesapla
    saturation_index = min(int(s * saturation_levels), saturation_levels - 1)
    
    # Parlaklık indeksini hesapla
    value_index = min(int(v * value_levels), value_levels - 1)
    
    return (hue_index, saturation_index, value_index)


def get_color_group_name(hsv: Tuple[float, float, float], spectrum: dict) -> str:
    """
    Bir HSV renk değerinin spektrum yapısındaki tam grup adını döndürür.
    
    Args:
        hsv: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        spectrum: create_color_spectrum_structure ile oluşturulan spektrum yapısı
        
    Returns:
        Renk grubunun tam adı (örn. "Koyu Soluk Kırmızı")
        
    Examples:
        >>> spectrum = create_color_spectrum_structure()
        >>> get_color_group_name((0.0, 0.2, 0.3), spectrum)
        'Koyu Soluk Kırmızı'
    """
    hue_idx, sat_idx, val_idx = classify_color_in_spectrum(hsv, spectrum)
    
    hue_div = spectrum['hue_divisions'][hue_idx]
    sat_group = hue_div['saturation_groups'][sat_idx]
    val_group = sat_group['value_groups'][val_idx]
    
    return f"{val_group['name']} {sat_group['name']} {hue_div['name']}"


def add_image_to_spectrum(image_path: str, spectrum: dict, 
                         dominant_color_method: str = 'histogram') -> Tuple[str, Tuple[int, int, int]]:
    """
    Bir görseli, dominant rengine göre renk spektrumunda sınıflandırır ve ekler.
    
    Args:
        image_path: Görsel dosyasının yolu
        spectrum: create_color_spectrum_structure ile oluşturulan spektrum yapısı
        dominant_color_method: Dominant renk çıkarma metodu
        
    Returns:
        (renk_grubu_adı, indeks_üçlüsü) çifti
        
    Examples:
        >>> spectrum = create_color_spectrum_structure()
        >>> add_image_to_spectrum('realImages/fabric001.jpg', spectrum)
        ('Koyu Canlı Kırmızı-Turuncu', (1, 2, 0))
    """
    # Dominant rengi bul
    dominant_rgb = extract_dominant_color_improved(image_path, method=dominant_color_method)
    
    # RGB'den HSV'ye dönüştür
    dominant_hsv = rgb_to_hsv(dominant_rgb)
    
    # Spektrumda sınıflandır
    indices = classify_color_in_spectrum(dominant_hsv, spectrum)
    hue_idx, sat_idx, val_idx = indices
    
    # İlgili gruba ekle
    hue_div = spectrum['hue_divisions'][hue_idx]
    sat_group = hue_div['saturation_groups'][sat_idx]
    val_group = sat_group['value_groups'][val_idx]
    
    # Görsel dosya adını üyelere ekle (eğer zaten yoksa)
    filename = os.path.basename(image_path)
    if filename not in val_group['members']:
        val_group['members'].append(filename)
    
    # Grup adını döndür
    group_name = get_color_group_name(dominant_hsv, spectrum)
    
    return (group_name, indices)


def build_color_spectrum_from_files(image_folder: str, 
                                   dominant_color_method: str = 'histogram') -> dict:
    """
    Bir klasördeki tüm görsellerden renk spektrumu organizasyonu oluşturur.
    
    Args:
        image_folder: Görsellerin bulunduğu klasör yolu
        dominant_color_method: Dominant renk çıkarma metodu
        
    Returns:
        Görsellerle doldurulmuş renk spektrumu organizasyon yapısı
        
    Examples:
        >>> spectrum = build_color_spectrum_from_files('realImages')
        >>> total_images = sum(len(val_group['members']) 
        ...     for hue_div in spectrum['hue_divisions'] 
        ...     for sat_group in hue_div['saturation_groups'] 
        ...     for val_group in sat_group['value_groups'])
        >>> print(f"Toplam {total_images} görsel sınıflandırıldı")
        Toplam 3500 görsel sınıflandırıldı
    """
    import os
    
    # Spektrum yapısını oluştur
    spectrum = create_color_spectrum_structure()
    
    # Klasördeki tüm görselleri bul
    image_files = []
    for file in os.listdir(image_folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image_files.append(file)
    
    # Her görseli işle
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        try:
            # Görseli spektruma ekle
            add_image_to_spectrum(img_path, spectrum, dominant_color_method)
        except Exception as e:
            print(f"Hata: {img_file} işlenirken bir sorun oluştu: {str(e)}")
    
    return spectrum



def find_similar_colors_in_spectrum(hsv_color: Tuple[float, float, float], 
                                  hue_range: Tuple[float, float] = (0.0, 1.0),
                                  min_saturation: float = 0.0,
                                  min_value: float = 0.0,
                                  color_group: Optional[str] = None,
                                  limit: int = 100) -> List[dict]:
    """
    Verilen HSV rengine benzer renkleri spektrumda arar.
    
    Args:
        hsv_color: HSV renk değeri (H: 0-1, S: 0-1, V: 0-1)
        hue_range: Aranacak ton aralığı (min, max) - 0-1 aralığında 
        min_saturation: Minimum doygunluk değeri (0-1 aralığında)
        min_value: Minimum parlaklık değeri (0-1 aralığında)
        color_group: Filtrelenecek renk grubu (ör: "Kırmızı", "Mavi", vb.)
        limit: Maksimum sonuç sayısı
        
    Returns:
        Benzer renkli görsellerin bilgilerini içeren liste:
        [
            {
                'filename': 'görsel.jpg',
                'dominant_color': (r, g, b),
                'color_group': 'Kırmızı',
                'hsv': (h, s, v),
                'similarity': 0.95,
                'group_name': 'Orta Canlı Kırmızı'
            },
            ...
        ]
    """
    import os
    
    # Spektrum yapısını yükle
    spectrum_file = "color_spectrum.json"
    if not os.path.exists(spectrum_file):
        # Spektrum yoksa oluştur
        from color_spectrum import build_color_spectrum
        spectrum = build_color_spectrum()
        # Kaydet
        import json
        with open(spectrum_file, "w", encoding="utf-8") as f:
            json.dump(spectrum, f, ensure_ascii=False, indent=2)
    else:
        # Mevcut spektrumu yükle
        import json
        with open(spectrum_file, "r", encoding="utf-8") as f:
            spectrum = json.load(f)
    
    # Referans rengin indekslerini bul
    h, s, v = hsv_color
    ref_indices = classify_color_in_spectrum(hsv_color, spectrum)
    
    # Sonuçlar listesi
    results = []
    
    # Tüm görsel bilgilerini yükle
    all_images_file = "all_images_color_data.json"
    if os.path.exists(all_images_file):
        with open(all_images_file, "r", encoding="utf-8") as f:
            all_images = json.load(f)
    else:
        # Görsel bilgileri yoksa oluştur
        all_images = {}
        image_files = [f for f in os.listdir("realImages") if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        for img_file in image_files:
            try:
                img_path = os.path.join("realImages", img_file)
                rgb = extract_dominant_color_improved(img_path, method='histogram')
                img_hsv = rgb_to_hsv(rgb)
                img_group = identify_color_group(img_hsv)
                all_images[img_file] = {
                    "dominant_color": rgb,
                    "hsv": img_hsv,
                    "color_group": img_group
                }
            except Exception as e:
                print(f"Görsel işleme hatası ({img_file}): {str(e)}")
        
        # Kaydet
        with open(all_images_file, "w", encoding="utf-8") as f:
            json.dump(all_images, f, ensure_ascii=False, indent=2)
    
    # Filtreleme kriterleri
    h_min, h_max = hue_range
    
    # Renk spektrumu üzerinde arama
    for img_filename, img_data in all_images.items():
        img_hsv = img_data.get("hsv")
        if not img_hsv:
            continue
        
        img_h, img_s, img_v = img_hsv
        img_group = img_data.get("color_group")
        
        # Ton (Hue) filtreleme - dairesel uzayda karşılaştırma
        # Burada ton değerleri 0-1 aralığında (0=0°, 1=360°)
        if h_min <= h_max:
            # Normal aralık (örn: 0.1-0.3)
            if img_h < h_min or img_h > h_max:
                continue
        else:
            # Geçiş aralığı (örn: 0.9-0.1, kırmızıların olduğu bölge)
            if img_h > h_max and img_h < h_min:
                continue
        
        # Doygunluk (Saturation) filtreleme
        if img_s < min_saturation:
            continue
        
        # Parlaklık (Value) filtreleme
        if img_v < min_value:
            continue
        
        # Renk grubu filtreleme
        if color_group and img_group != color_group:
            continue
        
        # Benzerlik hesaplama
        # Ton için dairesel mesafe, doygunluk ve parlaklık için doğrusal mesafe
        h_distance = calculate_hue_distance(h, img_h)
        s_distance = abs(s - img_s)
        v_distance = abs(v - img_v)
        
        # Ağırlıklı benzerlik skoru
        similarity = 1.0 - (h_distance * 0.6 + s_distance * 0.25 + v_distance * 0.15)
        
        # Sonuç ekle
        results.append({
            'filename': img_filename,
            'dominant_color': img_data.get("dominant_color"),
            'color_group': img_group,
            'hsv': img_hsv,
            'similarity': similarity,
            'group_name': f"{img_group} (H:{int(img_h*360)}°, S:{int(img_s*100)}%, V:{int(img_v*100)}%)"
        })
    
    # Benzerliğe göre sırala
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Sonuç sayısını sınırla
    return results[:limit]


def get_spectrum_statistics(spectrum: dict) -> dict:
    """
    Renk spektrumu yapısı hakkında istatistikler üretir.
    
    Args:
        spectrum: Renk spektrumu yapısı
        
    Returns:
        İstatistikleri içeren sözlük
        
    Examples:
        >>> spectrum = build_color_spectrum_from_files('realImages')
        >>> stats = get_spectrum_statistics(spectrum)
        >>> print(f"En popüler renk grubu: {stats['most_popular_group']}")
        En popüler renk grubu: Koyu Canlı Kırmızı
    """
    stats = {
        'total_images': 0,
        'hue_distribution': {},
        'saturation_distribution': {},
        'value_distribution': {},
        'most_popular_group': '',
        'empty_groups': 0,
        'group_counts': {}
    }
    
    max_count = 0
    max_group = ''
    empty_groups = 0
    
    # Her grup için istatistik topla
    for hue_div in spectrum['hue_divisions']:
        hue_name = hue_div['name']
        stats['hue_distribution'][hue_name] = 0
        
        for sat_group in hue_div['saturation_groups']:
            sat_name = sat_group['name']
            if sat_name not in stats['saturation_distribution']:
                stats['saturation_distribution'][sat_name] = 0
            
            for val_group in sat_group['value_groups']:
                val_name = val_group['name']
                if val_name not in stats['value_distribution']:
                    stats['value_distribution'][val_name] = 0
                
                # Grup üye sayısı
                members_count = len(val_group['members'])
                group_name = f"{val_name} {sat_name} {hue_name}"
                stats['group_counts'][group_name] = members_count
                
                # İstatistikleri güncelle
                stats['total_images'] += members_count
                stats['hue_distribution'][hue_name] += members_count
                stats['saturation_distribution'][sat_name] += members_count
                stats['value_distribution'][val_name] += members_count
                
                # En popüler grubu kontrol et
                if members_count > max_count:
                    max_count = members_count
                    max_group = group_name
                
                # Boş grup sayısını say
                if members_count == 0:
                    empty_groups += 1
    
    stats['most_popular_group'] = max_group
    stats['empty_groups'] = empty_groups
    
    return stats


def save_spectrum_to_json(spectrum: dict, output_path: str) -> None:
    """
    Renk spektrumu yapısını JSON dosyasına kaydeder.
    
    Args:
        spectrum: Renk spektrumu yapısı
        output_path: Çıktı JSON dosyasının yolu
        
    Returns:
        None
    
    Examples:
        >>> spectrum = build_color_spectrum_from_files('realImages')
        >>> save_spectrum_to_json(spectrum, 'exported_clusters/color/spectrum.json')
    """
    import json
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spectrum, f, ensure_ascii=False, indent=2)


def load_spectrum_from_json(input_path: str) -> dict:
    """
    Renk spektrumu yapısını JSON dosyasından yükler.
    
    Args:
        input_path: Girdi JSON dosyasının yolu
        
    Returns:
        Renk spektrumu yapısı
        
    Examples:
        >>> spectrum = load_spectrum_from_json('exported_clusters/color/spectrum.json')
        >>> len(spectrum['hue_divisions'])
        12
    """
    import json
    
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def export_spectrum_as_version(spectrum: dict, model_type: str, version_name: str) -> None:
    """
    Renk spektrumunu kümeleme versiyonu olarak dışa aktarır.
    
    Bu fonksiyon, renk spektrumu yapısını sistem tarafından tanınan bir versiyon 
    formatına dönüştürür ve 'exported_clusters/' klasörüne kaydeder.
    
    Args:
        spectrum: Renk spektrumu yapısı
        model_type: Model tipi ('color')
        version_name: Versiyon adı ('v1', 'v2', vb.)
        
    Returns:
        None
        
    Examples:
        >>> spectrum = build_color_spectrum_from_files('realImages')
        >>> export_spectrum_as_version(spectrum, 'color', 'spectrum_v1')
    """
    import os
    import json
    
    # Klasör yolları
    base_path = f"exported_clusters/{model_type}"
    version_path = f"{base_path}/{version_name}"
    
    # Klasörleri oluştur
    os.makedirs(version_path, exist_ok=True)
    
    # Versiyon bilgisi için versions.json dosyasını kontrol et/oluştur
    versions_file = f"{base_path}/versions.json"
    if os.path.exists(versions_file):
        with open(versions_file, 'r', encoding='utf-8') as f:
            versions_data = json.load(f)
    else:
        versions_data = {"versions": {}}
    
    # Renk spektrumundan clusters oluştur
    clusters = []
    
    # Her ton bölümü bir küme olacak
    for h_idx, hue_div in enumerate(spectrum['hue_divisions']):
        # Küme üyelerini topla
        members = []
        for sat_group in hue_div['saturation_groups']:
            for val_group in sat_group['value_groups']:
                members.extend(val_group['members'])
        
        # Boş kümeleri atlayabiliriz
        if not members:
            continue
        
        # Bir temsilci seç (ilk üye)
        representative = members[0] if members else None
        
        # Kümeyi oluştur
        cluster = {
            "number": h_idx,
            "representative": representative,
            "images": members
        }
        
        clusters.append(cluster)
    
    # Nadir renkler için özel bir küme
    rare_colors = []
    for h_idx, hue_div in enumerate(spectrum['hue_divisions']):
        for s_idx, sat_group in enumerate(hue_div['saturation_groups']):
            # Çok düşük doygunluk veya parlaklık gruplarındaki görseller
            if s_idx == 0:  # En düşük doygunluk
                for val_group in sat_group['value_groups']:
                    rare_colors.extend(val_group['members'])
    
    # Nadir renkler kümesi (boş değilse)
    if rare_colors:
        rare_cluster = {
            "number": "rare_colors",
            "representative": rare_colors[0] if rare_colors else None,
            "images": rare_colors
        }
        clusters.append(rare_cluster)
    
    # Versiyonlar dosyasını güncelle
    versions_data["versions"][version_name] = {
        "name": version_name,
        "algorithm": "color_spectrum",
        "parameters": {
            "divisions": spectrum['divisions'],
            "saturation_levels": spectrum['saturation_levels'],
            "value_levels": spectrum['value_levels']
        },
        "created_at": import_time().strftime("%Y-%m-%d %H:%M:%S"),
        "clusters": clusters
    }
    
    # Versiyonlar dosyasını kaydet
    with open(versions_file, 'w', encoding='utf-8') as f:
        json.dump(versions_data, f, ensure_ascii=False, indent=2)
    
    # Spektrumu da kaydet
    save_spectrum_to_json(spectrum, f"{version_path}/spectrum.json")
    
    print(f"Renk spektrumu '{version_name}' versiyonu olarak dışa aktarıldı.")


def import_time():
    """
    Şimdiki zamanı döndürür, datetime modülünü içe aktarma yardımcı fonksiyonu.
    """
    from datetime import datetime
    return datetime


def create_color_wheel_visualization(spectrum: dict) -> None:
    """
    Renk spektrumunun görsel bir renk çarkı temsilini oluşturur.
    
    Args:
        spectrum: Renk spektrumu yapısı
        
    Returns:
        None
        
    Examples:
        >>> spectrum = create_color_spectrum_structure()
        >>> create_color_wheel_visualization(spectrum)
    """
    # Bu fonksiyon proje kapsamında opsiyoneldir ve UI tarafında gerçekleştirilebilir
    pass




if __name__ == "__main__":
    # Test örnekleri
    print("RGB -> HSV dönüşümü:")
    print(f"  RGB(255, 0, 0) -> HSV {rgb_to_hsv((255, 0, 0))}")
    print(f"  RGB(0, 255, 0) -> HSV {rgb_to_hsv((0, 255, 0))}")
    print(f"  RGB(0, 0, 255) -> HSV {rgb_to_hsv((0, 0, 255))}")
    
    print("\nHSV -> RGB dönüşümü:")
    print(f"  HSV(0.0, 1.0, 1.0) -> RGB {hsv_to_rgb((0.0, 1.0, 1.0))}")
    print(f"  HSV(0.33, 1.0, 1.0) -> RGB {hsv_to_rgb((0.33, 1.0, 1.0))}")
    print(f"  HSV(0.67, 1.0, 1.0) -> RGB {hsv_to_rgb((0.67, 1.0, 1.0))}")
    
    print("\nRenk benzerliği:")
    print(f"  Kırmızı-Kırmızı: {calculate_color_similarity((255, 0, 0), (255, 0, 0))}")
    print(f"  Kırmızı-Yeşil: {calculate_color_similarity((255, 0, 0), (0, 255, 0))}")
    print(f"  Kırmızı-Turuncu: {calculate_color_similarity((255, 0, 0), (255, 165, 0))}")
    
    print("\nRenk grupları:")
    print(f"  RGB(255, 0, 0) -> {get_color_name((255, 0, 0))}")
    print(f"  RGB(0, 255, 0) -> {get_color_name((0, 255, 0))}")
    print(f"  RGB(0, 0, 255) -> {get_color_name((0, 0, 255))}")
    print(f"  RGB(255, 165, 0) -> {get_color_name((255, 165, 0))}")
    print(f"  RGB(128, 128, 128) -> {get_color_name((128, 128, 128))}")
    
    print("\nUyumlu renkler (Kırmızı):")
    print(f"  Tamamlayıcı: {find_harmonious_colors((255, 0, 0), 'complementary')}")
    print(f"  Analog: {find_harmonious_colors((255, 0, 0), 'analogous')}")
    print(f"  Triadik: {find_harmonious_colors((255, 0, 0), 'triadic')}")
    print(f"  Ayrık Tamamlayıcı: {find_harmonious_colors((255, 0, 0), 'split-complementary')}")
    print(f"  Monokromatik: {find_harmonious_colors((255, 0, 0), 'monochromatic')}")