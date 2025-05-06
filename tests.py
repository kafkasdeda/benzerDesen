# tests.py
import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BenzerDesenTests:
    def __init__(self):
        self.driver = None
        self.test_results = {}
        
    def setup(self):
        # Selenium WebDriver başlatma
        print("Test ortamı hazırlanıyor...")
        options = webdriver.ChromeOptions()
        # Headless modu isteğe bağlı - görsel arayüz görmeden arka planda çalışır
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        
    def teardown(self):
        # Test sonrası temizlik
        if self.driver:
            self.driver.quit()
    
    def run_all_tests(self):
        self.setup()
        try:
            # Testleri çalıştır
            self.test_version_persistence()
            self.print_test_results()
        finally:
            self.teardown()
    
    def test_version_persistence(self):
        """
        Test: Model ve versiyon seçildikten sonra, sol panelden yeni görsel seçildiğinde
        versiyon bilgisinin korunup korunmadığını kontrol eder.
        """
        test_name = "versiyon_bilgisi_korunuyor"
        print(f"\nTest başlatılıyor: {test_name}")
        
        try:
            # Ana sayfaya git
            self.driver.get("http://localhost:5000")
            time.sleep(2)  # Sayfanın yüklenmesi için bekle
            
            # Sol paneldeki ilk görsele tıkla
            first_image = self.driver.find_element(By.CSS_SELECTOR, ".left-panel .image-box")
            first_image.click()
            time.sleep(2)  # Sonuçların yüklenmesi için bekle
            
            # Model ve versiyon seç
            model_selector = self.driver.find_element(By.ID, "model-selector")
            model_selector.click()
            model_option = self.driver.find_element(By.CSS_SELECTOR, "#model-selector option[value='color']")
            model_option.click()
            time.sleep(1)  # Versiyonların güncellenmesi için bekle
            
            version_selector = self.driver.find_element(By.ID, "version-selector")
            version_selector.click()
            if len(version_selector.find_elements(By.TAG_NAME, "option")) > 1:
                version_option = self.driver.find_element(By.CSS_SELECTOR, "#version-selector option:nth-child(2)")
                version_option.click()
            
            # Seçilen model ve versiyonu kaydet
            selected_model = model_selector.get_attribute("value")
            selected_version = version_selector.get_attribute("value")
            
            print(f"Seçilen model: {selected_model}, versiyon: {selected_version}")
            
            # Sol paneldeki ikinci görsele tıkla
            second_image = self.driver.find_elements(By.CSS_SELECTOR, ".left-panel .image-box")[1]
            second_image.click()
            time.sleep(2)  # Sonuçların yüklenmesi için bekle
            
            # Tıklamadan sonra model ve versiyonun hala aynı olup olmadığını kontrol et
            current_model = self.driver.find_element(By.ID, "model-selector").get_attribute("value")
            current_version = self.driver.find_element(By.ID, "version-selector").get_attribute("value")
            
            print(f"İkinci görsel seçimi sonrası model: {current_model}, versiyon: {current_version}")
            
            # Sonucu değerlendir
            is_model_preserved = selected_model == current_model
            is_version_preserved = selected_version == current_version
            
            result = is_model_preserved and is_version_preserved
            self.test_results[test_name] = {
                "passed": result,
                "details": {
                    "initial_model": selected_model,
                    "initial_version": selected_version,
                    "final_model": current_model,
                    "final_version": current_version,
                    "model_preserved": is_model_preserved,
                    "version_preserved": is_version_preserved
                }
            }
            
            print(f"Test sonucu: {'BAŞARILI' if result else 'BAŞARISIZ'}")
            
        except Exception as e:
            print(f"Test sırasında hata: {str(e)}")
            self.test_results[test_name] = {
                "passed": False,
                "error": str(e)
            }
    
    def print_test_results(self):
        """Test sonuçlarını ekrana yazdırır"""
        print("\n===== TEST SONUÇLARI =====")
        
        all_passed = True
        for test_name, result in self.test_results.items():
            passed = result.get("passed", False)
            all_passed = all_passed and passed
            status = "BAŞARILI" if passed else "BAŞARISIZ"
            print(f"{test_name}: {status}")
            
            if not passed:
                if "error" in result:
                    print(f"  Hata: {result['error']}")
                elif "details" in result:
                    details = result["details"]
                    print("  Detaylar:")
                    for key, value in details.items():
                        print(f"    {key}: {value}")
        
        overall = "BAŞARILI" if all_passed else "BAŞARISIZ"
        print(f"\nGenel Sonuç: {overall}")
        print("=========================")

if __name__ == "__main__":
    tester = BenzerDesenTests()
    tester.run_all_tests()