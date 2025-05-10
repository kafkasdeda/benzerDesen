/**
 * Fabric3DVisualizer - 3D Kumaş Görselleştirme Sınıfı
 * 
 * Benzer Desen projesi için kumaş desenlerini 3D giysi modelleri üzerinde
 * görselleştirmeyi sağlayan JavaScript sınıfı.
 * 
 * @author Benzer Desen Ekibi
 * @version 1.0.0
 * @date 2025-05-10
 */

// Ana Three.js sınıfları
class Fabric3DVisualizer {
    constructor(containerId) {
        // DOM elemanı referansı
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container element with id '${containerId}' not found.`);
            return;
        }

        // Three.js bileşenleri
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.model = null;
        this.lights = {};
        
        // Model ve texture bilgileri
        this.loadedModelPath = null;
        this.currentFabricTexture = null;
        
        // Durum takibi
        this.isInitialized = false;
        this.isModelLoaded = false;
        
        // Yükleme yönetimi
        this.loadingManager = null;
        this.gltfLoader = null;
        this.textureLoader = null;
        
        // Animasyon
        this.animationFrameId = null;
        
        // Boyut kontrolü
        this.resizeObserver = null;
        
        // Debug modu
        this.debugMode = false;
    }
    
    /**
     * Three.js ortamını başlatır
     * @returns {boolean} Başarılı olup olmadığı
     */
    init() {
        try {
            if (!this.container) return false;
            
            // ThreeJS kontrolü
            if (!window.THREE) {
                console.error('Three.js kütüphanesi yüklenmemiş!');
                return false;
            }
            
            // Sahne oluştur
            this.scene = new THREE.Scene();
            this.scene.background = new THREE.Color(0xf0f0f0);
            
            // Kamera ayarları
            const width = this.container.clientWidth;
            const height = this.container.clientHeight;
            const aspect = width / height;
            this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
            this.camera.position.set(0, 1, 5);
            this.camera.lookAt(0, 0, 0);
            
            // Renderer oluştur
            this.renderer = new THREE.WebGLRenderer({ 
                antialias: true,
                alpha: true 
            });
            this.renderer.setPixelRatio(window.devicePixelRatio);
            this.renderer.setSize(width, height);
            this.renderer.shadowMap.enabled = true;
            this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            this.container.appendChild(this.renderer.domElement);
            
            // Işıklandırma
            this._setupLights();
            
            // Yükleme yöneticisi
            this.loadingManager = new THREE.LoadingManager();
            this.loadingManager.onProgress = (url, loaded, total) => {
                const progress = (loaded / total * 100).toFixed(0);
                this._onLoadProgress(progress);
            };
            
            this.loadingManager.onError = (url) => {
                console.error(`Yükleme hatası: ${url}`);
                this._onLoadError(url);
            };
            
            // Yükleyiciler
            this.gltfLoader = new THREE.GLTFLoader(this.loadingManager);
            this.textureLoader = new THREE.TextureLoader(this.loadingManager);
            
            // Kontroller
            this._setupControls();
            
            // Boyut değişikliğini izle
            this._setupResizeObserver();
            
            // İlk render
            this._animate();
            
            this.isInitialized = true;
            this._debug('Three.js ortamı başarıyla başlatıldı.');
            
            return true;
        } catch (error) {
            console.error('Three.js ortamı başlatılırken hata oluştu:', error);
            return false;
        }
    }
    
    /**
     * Işıklandırma kurulumu
     * @private
     */
    _setupLights() {
        // Ambient ışık
        this.lights.ambient = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(this.lights.ambient);
        
        // Directional ışık (ana ışık)
        this.lights.main = new THREE.DirectionalLight(0xffffff, 1);
        this.lights.main.position.set(5, 5, 5);
        this.lights.main.castShadow = true;
        this.scene.add(this.lights.main);
        
        // Gölge ayarları
        if (this.lights.main.shadow) {
            this.lights.main.shadow.mapSize.width = 2048;
            this.lights.main.shadow.mapSize.height = 2048;
            this.lights.main.shadow.camera.near = 0.5;
            this.lights.main.shadow.camera.far = 50;
            this.lights.main.shadow.bias = -0.001;
        }
        
        // Dolgu ışığı
        this.lights.fill = new THREE.DirectionalLight(0xffffff, 0.5);
        this.lights.fill.position.set(-5, 3, -5);
        this.scene.add(this.lights.fill);
    }
    
    /**
     * Kontrolleri kurulumu
     * @private
     */
    _setupControls() {
        if (!window.THREE || !THREE.OrbitControls) {
            console.warn('OrbitControls bulunamadı. Kontroller devre dışı.');
            return;
        }
        
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 2;
        this.controls.maxDistance = 10;
        this.controls.maxPolarAngle = Math.PI / 1.5;
        this.controls.update();
    }
    
    /**
     * Boyut değişikliği gözlemcisi kurulumu
     * @private
     */
    _setupResizeObserver() {
        if (window.ResizeObserver) {
            this.resizeObserver = new ResizeObserver(entries => {
                for (const entry of entries) {
                    if (entry.target === this.container) {
                        this._handleResize();
                    }
                }
            });
            this.resizeObserver.observe(this.container);
        } else {
            // Fallback
            window.addEventListener('resize', () => this._handleResize());
        }
    }
    
    /**
     * Boyut değişikliği işleyicisi
     * @private
     */
    _handleResize() {
        if (!this.camera || !this.renderer || !this.container) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    /**
     * Animasyon döngüsü
     * @private
     */
    _animate() {
        this.animationFrameId = requestAnimationFrame(() => this._animate());
        
        if (this.controls) {
            this.controls.update();
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    /**
     * Yükleme ilerlemesi geri çağrısı
     * @param {number} progress İlerleme yüzdesi
     * @private
     */
    _onLoadProgress(progress) {
        // İlerleme göstergesi için hook
        if (typeof this.onProgress === 'function') {
            this.onProgress(progress);
        }
        
        this._debug(`Yükleme ilerlemesi: %${progress}`);
    }
    
    /**
     * Yükleme hatası geri çağrısı
     * @param {string} url Yüklenemeyen URL
     * @private
     */
    _onLoadError(url) {
        // Hata göstergesi için hook
        if (typeof this.onError === 'function') {
            this.onError(url);
        }
    }
    
    /**
     * Debug log
     * @param {string} message Log mesajı
     * @private
     */
    _debug(message) {
        if (this.debugMode) {
            console.log(`[Fabric3D] ${message}`);
        }
    }
    
    /**
     * 3D modeli yükler
     * @param {string} modelPath Model dosyasının yolu
     * @returns {Promise} Yükleme tamamlandığında çözümlenen Promise
     */
    loadModel(modelPath) {
        return new Promise((resolve, reject) => {
            if (!this.isInitialized) {
                reject(new Error('Three.js ortamı başlatılmamış. Önce init() çağırın.'));
                return;
            }
            
            // Önceki modeli temizle
            if (this.model) {
                this.scene.remove(this.model);
                this.model = null;
            }
            
            this._debug(`Model yükleniyor: ${modelPath}`);
            
            this.gltfLoader.load(
                modelPath,
                (gltf) => {
                    this.model = gltf.scene;
                    
                    // Modeli sahneye ekle
                    this.scene.add(this.model);
                    
                    // Kamerayı modele göre ayarla
                    this._fitCameraToModel();
                    
                    // Model materyal referanslarını sakla
                    this._processMaterials();
                    
                    this.isModelLoaded = true;
                    this.loadedModelPath = modelPath;
                    
                    this._debug('Model başarıyla yüklendi.');
                    
                    // Önceki texture varsa, uygula
                    if (this.currentFabricTexture) {
                        this.applyFabricTexture(this.currentFabricTexture);
                    }
                    
                    resolve(this.model);
                },
                (xhr) => {
                    // İlerleme LoadingManager tarafından ele alınıyor
                },
                (error) => {
                    console.error('Model yüklenirken hata oluştu:', error);
                    reject(error);
                }
            );
        });
    }
    
    /**
     * Kamerayı modele göre ayarla
     * @private
     */
    _fitCameraToModel() {
        if (!this.model) return;
        
        // Modelin sınırlayıcı kutusunu hesapla
        const box = new THREE.Box3().setFromObject(this.model);
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());
        
        // Modelin merkezini origin'e getir
        this.model.position.sub(center);
        
        // Kamera pozisyonunu ayarla
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / (2 * Math.tan(fov / 2)));
        
        // Biraz daha uzaklaş
        cameraZ *= 1.5;
        
        this.camera.position.z = cameraZ;
        
        // Kamera hedefini ayarla
        const minZ = box.min.z;
        const cameraToFarEdge = (minZ < 0) ? -minZ + cameraZ : cameraZ - minZ;
        
        this.camera.far = cameraToFarEdge * 3;
        this.camera.updateProjectionMatrix();
        
        if (this.controls) {
            // Kontrolleri modelin merkezine ayarla
            this.controls.target = new THREE.Vector3(0, 0, 0);
            this.controls.maxDistance = cameraZ * 2;
            this.controls.saveState();
            this.controls.update();
        }
    }
    
    /**
     * Model materyallerini işle
     * @private
     */
    _processMaterials() {
        if (!this.model) return;
        
        // Tüm meshler üzerinde döngü
        this.model.traverse((child) => {
            if (child.isMesh && child.material) {
                // Gölgeleri etkinleştir
                child.castShadow = true;
                child.receiveShadow = true;
                
                // Material array ise, her birini işle
                if (Array.isArray(child.material)) {
                    child.material.forEach(material => {
                        this._enhanceMaterial(material);
                    });
                } else {
                    this._enhanceMaterial(child.material);
                }
            }
        });
    }
    
    /**
     * Materyali iyileştir
     * @param {THREE.Material} material İyileştirilecek materyal
     * @private
     */
    _enhanceMaterial(material) {
        // Gölgelendirme ekle
        material.shadowSide = THREE.FrontSide;
        
        // PBR materyal özelliklerini ayarla (eğer destekliyorsa)
        if (material.metalness !== undefined) {
            material.metalness = 0.0;  // Kumaşlar metalik değildir
        }
        
        if (material.roughness !== undefined) {
            material.roughness = 0.8;  // Kumaşlar genellikle pürüzlüdür
        }
    }
    
    /**
     * Kumaş desenini uygula
     * @param {string} texturePath Desen görüntüsünün yolu
     * @returns {Promise} İşlem tamamlandığında çözümlenen Promise
     */
    applyFabricTexture(texturePath) {
        return new Promise((resolve, reject) => {
            if (!this.isInitialized) {
                reject(new Error('Three.js ortamı başlatılmamış. Önce init() çağırın.'));
                return;
            }
            
            if (!this.model) {
                // Aktif model yoksa, texture'ı kaydet ve model yüklendiğinde uygula
                this.currentFabricTexture = texturePath;
                this._debug('Model yüklenmediği için texture kaydedildi. Model yüklendiğinde uygulanacak.');
                resolve(null);
                return;
            }
            
            this._debug(`Kumaş dokusu yükleniyor: ${texturePath}`);
            
            this.textureLoader.load(
                texturePath,
                (texture) => {
                    // Texture ayarları
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.repeat.set(2, 2);
                    texture.encoding = THREE.sRGBEncoding;
                    
                    // Tüm model meshlerine texture'ı uygula
                    this.model.traverse((child) => {
                        if (child.isMesh && child.material) {
                            // Material array ise, her birini işle
                            if (Array.isArray(child.material)) {
                                child.material.forEach(material => {
                                    material.map = texture;
                                    material.needsUpdate = true;
                                });
                            } else {
                                child.material.map = texture;
                                child.material.needsUpdate = true;
                            }
                        }
                    });
                    
                    this.currentFabricTexture = texturePath;
                    this._debug('Kumaş dokusu başarıyla uygulandı.');
                    
                    resolve(texture);
                },
                undefined,
                (error) => {
                    console.error('Kumaş dokusu yüklenirken hata oluştu:', error);
                    reject(error);
                }
            );
        });
    }
    
    /**
     * Kaynakları temizle
     */
    dispose() {
        // Animasyon döngüsünü durdur
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
        
        // Kontrolleri temizle
        if (this.controls) {
            this.controls.dispose();
            this.controls = null;
        }
        
        // Renderer temizle
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
            this.renderer = null;
        }
        
        // Boyut gözlemcisini temizle
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
            this.resizeObserver = null;
        } else {
            window.removeEventListener('resize', this._handleResize);
        }
        
        // Referansları temizle
        this.scene = null;
        this.camera = null;
        this.model = null;
        this.lights = {};
        
        this.isInitialized = false;
        this.isModelLoaded = false;
        
        this._debug('Fabric3D kaynakları temizlendi.');
    }
    
    /**
     * Debug modunu etkinleştir/devre dışı bırak
     * @param {boolean} enabled Debug modu durumu
     */
    setDebugMode(enabled) {
        this.debugMode = !!enabled;
    }
}
