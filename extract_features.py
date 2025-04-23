# extract_features.py
# Oluşturulma: 2025-04-19
# Güncelleme: Renk + Desen modeli eklendi
# Hazırlayan: Kafkas
# Açıklama:
# Bu script, realImages/ klasöründeki tüm görselleri işler,
# model türüne (desen, renk, doku, renk+desen) göre uygun şekilde dönüştürür,
# pretrained ResNet18 ile feature vektörlerini çıkarır,
# image_features klasörüne .npy ve .json dosyaları olarak kaydeder.

import os
import json
import torch
import numpy as np
from torchvision import models, transforms
from PIL import Image
from tqdm import tqdm
import argparse

# Komut satırı parametrelerini ayarla
parser = argparse.ArgumentParser(description="Görsel özellik çıkarım aracı")
parser.add_argument("--model_type", type=str, default="pattern", 
                    choices=["pattern", "color", "texture", "color+pattern"],
                    help="Model türü: pattern, color, texture veya color+pattern")
args = parser.parse_args()

# Giriş klasörü ve model türü
INPUT_FOLDER = "realImages"
MODEL_TYPE = args.model_type  # pattern / color / texture / color+pattern

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
elif MODEL_TYPE == "color+pattern":
    # Renk + Desen için her iki özelliği de işliyoruz
    # Önce ayrı ayrı özellikleri çıkarıp sonra birleştireceğiz
    transform_color = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    transform_pattern = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    # Ana transform kullanmayacağız, iki modeli ayrı uygulayacağız
    transform = None
else:
    raise ValueError("Geçersiz MODEL_TYPE")

features = []
image_paths = []

print(f"📬 {MODEL_TYPE} modülü için görsel özellikler çıkarılıyor...")

if MODEL_TYPE == "color+pattern":
    # Renk + Desen için özel işlem
    for fname in tqdm(os.listdir(INPUT_FOLDER)):
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        fpath = os.path.join(INPUT_FOLDER, fname)
        try:
            img = Image.open(fpath).convert("RGB")
            
            # Renk özelliklerini çıkar
            img_color = transform_color(img).unsqueeze(0).to(device)
            with torch.no_grad():
                vec_color = model(img_color).squeeze().cpu().numpy()
                
            # Desen özelliklerini çıkar
            img_pattern = transform_pattern(img).unsqueeze(0).to(device)
            with torch.no_grad():
                vec_pattern = model(img_pattern).squeeze().cpu().numpy()
            
            # İki özellik vektörünü birleştir
            # Sırayla birleştirme (concatenate)
            combined_vec = np.concatenate([vec_color, vec_pattern])
            
            features.append(combined_vec)
            image_paths.append(os.path.basename(fpath))
        except Exception as e:
            print(f"⚠️ Hata: {fname} atlandı. {e}")
else:
    # Normal modeller için standart işlem
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

feature_dim = features[0].shape[0] if features else 0
print(f"✅ {len(features)} görsel için {MODEL_TYPE} özellik çıkarımı tamamlandı.")
print(f"Her görsel için özellik boyutu: {feature_dim}")
