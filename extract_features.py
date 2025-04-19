# extract_features.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas ❤️ Luna
# Açıklama:
# Bu script, realImages/ klasöründeki tüm görselleri işler,
# model türüne (desen, renk, doku) göre uygun şekilde dönüştürür,
# pretrained ResNet18 ile feature vektörlerini çıkarır,
# image_features klasörüne .npy ve .json dosyaları olarak kaydeder.

import os
import json
import torch
import numpy as np
from torchvision import models, transforms
from PIL import Image
from tqdm import tqdm

# Giriş klasörü ve model türü (pattern, color, texture)
INPUT_FOLDER = "realImages"
MODEL_TYPE = "pattern"  # pattern / color / texture

# Çıkış yolları
os.makedirs("image_features", exist_ok=True)
feature_out = f"image_features/{MODEL_TYPE}_features.npy"
filenames_out = f"image_features/{MODEL_TYPE}_filenames.json"

# GPU kullanılabiliyorsa aktif et
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ResNet18 yüklüyoruz (son katmanı kullanmıyoruz)
model = models.resnet18(pretrained=True)
model = torch.nn.Sequential(*list(model.children())[:-1])
model.to(device)
model.eval()

# Model türüne göre transform ayarı
if MODEL_TYPE == "pattern":
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
elif MODEL_TYPE == "color":
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
elif MODEL_TYPE == "texture":
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((224, 224)),
        transforms.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 2.0)),
        transforms.ToTensor()
    ])
else:
    raise ValueError("Geçersiz MODEL_TYPE")

features = []
image_paths = []

print("📦 Görseller işleniyor...")
for fname in tqdm(os.listdir(INPUT_FOLDER)):
    if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    fpath = os.path.join(INPUT_FOLDER, fname)
    try:
        img = Image.open(fpath).convert("RGB")
        img_t = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            vec = model(img_t).squeeze().cpu().numpy()
            features.append(vec)
            image_paths.append(os.path.basename(fpath))
    except Exception as e:
        print(f"⚠️ Hata: {fname} atlandı. {e}")

# Kayıt
np.save(feature_out, np.array(features))
with open(filenames_out, "w", encoding="utf-8") as f:
    json.dump(image_paths, f, indent=2)

print(f"✅ {len(features)} görsel için özellik çıkarımı tamamlandı.")
