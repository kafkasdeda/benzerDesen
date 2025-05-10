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
        this.currentModelId = null;
        
        // Model listesi
        this.modelList = null;
        this.modelListPath = 'static/js/models/model_list.json';
        
        // Durum takibi
        this.isInitialized = false;
        this.isModelLoaded = false;
        this.isModelListLoaded = false;
        
        // Yükleme yönetimi
        this.loadingManager = null;
        this.gltfLoader = null;
        this.textureLoader = null;
        this.jsonLoader = null;
        this.isLoading = false;
        this.loadingElement = null;
        
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
            this.jsonLoader = new THREE.FileLoader(this.loadingManager);
            this.jsonLoader.setResponseType('json');
            
            // Yükleme göstergesi oluştur
            this._createLoadingIndicator();
            
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
     * Yükleme göstergesi oluştur
     * @private
     */
    _createLoadingIndicator() {
        // Eğer zaten varsa, tekrar oluşturma
        if (this.loadingElement) return;
        
        // Loading div
        this.loadingElement = document.createElement('div');
        this.loadingElement.className = 'fabric3d-loading';
        this.loadingElement.style.position = 'absolute';
        this.loadingElement.style.top = '0';
        this.loadingElement.style.left = '0';
        this.loadingElement.style.width = '100%';
        this.loadingElement.style.height = '100%';
        this.loadingElement.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        this.loadingElement.style.display = 'flex';
        this.loadingElement.style.alignItems = 'center';
        this.loadingElement.style.justifyContent = 'center';
        this.loadingElement.style.zIndex = '1000';
        this.loadingElement.style.color = 'white';
        this.loadingElement.style.display = 'none';
        
        // Progress container
        const progressContainer = document.createElement('div');
        progressContainer.className = 'fabric3d-progress-container';
        progressContainer.style.width = '80%';
        progressContainer.style.maxWidth = '300px';
        progressContainer.style.textAlign = 'center';
        
        // Progress text
        const progressText = document.createElement('div');
        progressText.className = 'fabric3d-progress-text';
        progressText.textContent = 'Yükleniyor...';
        progressText.style.marginBottom = '10px';
        progressText.style.fontWeight = 'bold';
        
        // Progress bar container
        const progressBarContainer = document.createElement('div');
        progressBarContainer.className = 'fabric3d-progress-bar-container';
        progressBarContainer.style.width = '100%';
        progressBarContainer.style.height = '10px';
        progressBarContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
        progressBarContainer.style.borderRadius = '5px';
        progressBarContainer.style.overflow = 'hidden';
        
        // Progress bar
        const progressBar = document.createElement('div');
        progressBar.className = 'fabric3d-progress-bar';
        progressBar.style.width = '0%';
        progressBar.style.height = '100%';
        progressBar.style.backgroundColor = '#4CAF50';
        progressBar.style.transition = 'width 0.3s ease';
        
        // Progress percentage
        const progressPercentage = document.createElement('div');
        progressPercentage.className = 'fabric3d-progress-percentage';
        progressPercentage.textContent = '0%';
        progressPercentage.style.marginTop = '5px';
        
        // Yapıyı oluştur
        progressBarContainer.appendChild(progressBar);
        progressContainer.appendChild(progressText);
        progressContainer.appendChild(progressBarContainer);
        progressContainer.appendChild(progressPercentage);
        this.loadingElement.appendChild(progressContainer);
        
        // Container'a ekle
        this.container.appendChild(this.loadingElement);
    }
    
    /**
     * Yükleme göstergesini göster/gizle
     * @param {boolean} show Gösterme durumu
     * @private
     */
    _toggleLoadingIndicator(show) {
        if (!this.loadingElement) return;
        
        this.isLoading = show;
        this.loadingElement.style.display = show ? 'flex' : 'none';
        
        // Gösterge sıfırla
        if (show) {
            const progressBar = this.loadingElement.querySelector('.fabric3d-progress-bar');
            const progressPercentage = this.loadingElement.querySelector('.fabric3d-progress-percentage');
            
            if (progressBar) progressBar.style.width = '0%';
            if (progressPercentage) progressPercentage.textContent = '0%';
        }
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
        
        // Görsel ilerleme göstergesini güncelle
        if (this.loadingElement) {
            const progressBar = this.loadingElement.querySelector('.fabric3d-progress-bar');
            const progressPercentage = this.loadingElement.querySelector('.fabric3d-progress-percentage');
            
            if (progressBar) progressBar.style.width = `${progress}%`;
            if (progressPercentage) progressPercentage.textContent = `${progress}%`;
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
        
        // Yükleme göstergesini gizle
        this._toggleLoadingIndicator(false);
        
        // Hata mesajı göster
        if (this.loadingElement) {
            const progressText = this.loadingElement.querySelector('.fabric3d-progress-text');
            if (progressText) {
                progressText.textContent = `Yükleme Hatası: ${url}`;
                progressText.style.color = '#ff0000';
            }
            
            // 3 saniye sonra gizle
            setTimeout(() => {
                this._toggleLoadingIndicator(false);
                if (progressText) {
                    progressText.textContent = 'Yükleniyor...';
                    progressText.style.color = 'white';
                }
            }, 3000);
        }
        
        console.error(`Yükleme hatası: ${url}`);
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
     * Model listesini yükle
     * @param {string} [modelListPath=null] Model listesi JSON dosyasının yolu
     * @returns {Promise} Yükleme tamamlandığında çözümlenen Promise
     */
    loadModelList(modelListPath = null) {
        return new Promise((resolve, reject) => {
            const path = modelListPath || this.modelListPath;
            
            this._debug(`Model listesi yükleniyor: ${path}`);
            this._toggleLoadingIndicator(true);
            
            this.jsonLoader.load(
                path,
                (data) => {
                    this.modelList = data;
                    this.isModelListLoaded = true;
                    this._toggleLoadingIndicator(false);
                    this._debug('Model listesi başarıyla yüklendi.');
                    resolve(this.modelList);
                },
                (xhr) => {
                    // İlerleme LoadingManager tarafından ele alınıyor
                },
                (error) => {
                    this._toggleLoadingIndicator(false);
                    console.error('Model listesi yüklenirken hata oluştu:', error);
                    reject(error);
                }
            );
        });
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
            this._toggleLoadingIndicator(true);
            
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
                    this._toggleLoadingIndicator(false);
                    
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
                    this._toggleLoadingIndicator(false);
                    console.error('Model yüklenirken hata oluştu:', error);
                    reject(error);
                }
            );
        });
    }
    
    /**
     * ID ile modeli yükle
     * @param {string} modelId Model ID'si
     * @returns {Promise} Yükleme tamamlandığında çözümlenen Promise
     */
    loadModelById(modelId) {
        return new Promise(async (resolve, reject) => {
            if (!this.isInitialized) {
                reject(new Error('Three.js ortamı başlatılmamış. Önce init() çağırın.'));
                return;
            }
            
            // Model listesi yüklü değilse, yükle
            if (!this.isModelListLoaded) {
                try {
                    await this.loadModelList();
                } catch (error) {
                    reject(new Error('Model listesi yüklenemedi: ' + error.message));
                    return;
                }
            }
            
            // Model ID'yi kontrol et
            if (!this.modelList || !this.modelList.models) {
                reject(new Error('Model listesi bulunamadı veya geçersiz.'));
                return;
            }
            
            // Model bilgilerini bul
            const modelInfo = this.modelList.models.find(model => model.id === modelId);
            if (!modelInfo) {
                reject(new Error(`"${modelId}" ID'li model bulunamadı.`));
                return;
            }
            
            try {
                // Modeli yükle
                const model = await this.loadModel(modelInfo.path);
                this.currentModelId = modelId;
                
                // Modele özel ayarları uygula
                if (modelInfo.defaultScale && modelInfo.defaultScale !== 1.0) {
                    this.model.scale.set(
                        modelInfo.defaultScale,
                        modelInfo.defaultScale,
                        modelInfo.defaultScale
                    );
                }
                
                if (modelInfo.defaultPosition) {
                    this.model.position.set(
                        modelInfo.defaultPosition[0],
                        modelInfo.defaultPosition[1],
                        modelInfo.defaultPosition[2]
                    );
                }
                
                if (modelInfo.defaultRotation) {
                    this.model.rotation.set(
                        modelInfo.defaultRotation[0] * (Math.PI / 180),
                        modelInfo.defaultRotation[1] * (Math.PI / 180),
                        modelInfo.defaultRotation[2] * (Math.PI / 180)
                    );
                }
                
                resolve({
                    model: model,
                    info: modelInfo
                });
            } catch (error) {
                reject(error);
            }
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
     * Sonraki modele geç
     * @returns {Promise} İşlem tamamlandığında çözümlenen Promise
     */
    nextModel() {
        return new Promise(async (resolve, reject) => {
            if (!this.isModelListLoaded || !this.currentModelId) {
                reject(new Error('Geçerli model yok veya model listesi yüklenmedi.'));
                return;
            }
            
            // Gezinme bilgisini bul
            const navigation = this.modelList.navigation[this.currentModelId];
            if (!navigation || !navigation.next) {
                reject(new Error('Sonraki model bulunamadı.'));
                return;
            }
            
            try {
                // Sonraki modeli yükle
                const result = await this.loadModelById(navigation.next);
                resolve(result);
            } catch (error) {
                reject(error);
            }
        });
    }
    
    /**
     * Önceki modele geç
     * @returns {Promise} İşlem tamamlandığında çözümlenen Promise
     */
    prevModel() {
        return new Promise(async (resolve, reject) => {
            if (!this.isModelListLoaded || !this.currentModelId) {
                reject(new Error('Geçerli model yok veya model listesi yüklenmedi.'));
                return;
            }
            
            // Gezinme bilgisini bul
            const navigation = this.modelList.navigation[this.currentModelId];
            if (!navigation || !navigation.prev) {
                reject(new Error('Önceki model bulunamadı.'));
                return;
            }
            
            try {
                // Önceki modeli yükle
                const result = await this.loadModelById(navigation.prev);
                resolve(result);
            } catch (error) {
                reject(error);
            }
        });
    }
    
    /**
     * Varsayılan modeli yükle
     * @param {string} [category='unknown'] Model kategorisi (men, women, unknown)
     * @returns {Promise} İşlem tamamlandığında çözümlenen Promise
     */
    loadDefaultModel(category = 'unknown') {
        return new Promise(async (resolve, reject) => {
            if (!this.isModelListLoaded) {
                try {
                    await this.loadModelList();
                } catch (error) {
                    reject(new Error('Model listesi yüklenemedi: ' + error.message));
                    return;
                }
            }
            
            // Varsayılan model ID'sini bul
            if (!this.modelList.mappings || !this.modelList.mappings.defaults) {
                reject(new Error('Varsayılan model eşleştirmeleri bulunamadı.'));
                return;
            }
            
            const defaultModelId = this.modelList.mappings.defaults[category] || 
                                 this.modelList.mappings.defaults.unknown;
            
            if (!defaultModelId) {
                reject(new Error('Varsayılan model bulunamadı.'));
                return;
            }
            
            try {
                // Varsayılan modeli yükle
                const result = await this.loadModelById(defaultModelId);
                resolve(result);
            } catch (error) {
                reject(error);
            }
        });
    }
    
    /**
     * Kumaş tipine göre uygun model yükle
     * @param {string} fabricType Kumaş tipi (KM, KW, KP vb.)
     * @returns {Promise} İşlem tamamlandığında çözümlenen Promise
     */
    loadModelByFabricType(fabricType) {
        return new Promise(async (resolve, reject) => {
            if (!this.isModelListLoaded) {
                try {
                    await this.loadModelList();
                } catch (error) {
                    reject(new Error('Model listesi yüklenemedi: ' + error.message));
                    return;
                }
            }
            
            // Kumaş tipi eşleştirmelerini kontrol et
            if (!this.modelList.mappings || 
                !this.modelList.mappings['fabric-type'] || 
                !this.modelList.mappings['fabric-type'][fabricType]) {
                // Varsayılan modeli yükle
                try {
                    const result = await this.loadDefaultModel();
                    resolve(result);
                } catch (error) {
                    reject(error);
                }
                return;
            }
            
            // Kumaş tipine uygun ilk modeli al
            const modelId = this.modelList.mappings['fabric-type'][fabricType][0];
            
            if (!modelId) {
                reject(new Error(`"${fabricType}" kumaş tipi için uygun model bulunamadı.`));
                return;
            }
            
            try {
                // Modeli yükle
                const result = await this.loadModelById(modelId);
                resolve(result);
            } catch (error) {
                reject(error);
            }
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
