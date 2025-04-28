# train_model.py
# Oluşturulma: 2025-04-19
# Hazırlayan: Kafkas 
# 
# Bu dosya, seçilen model türüne (pattern, color, texture) ve versiyonuna göre öğrenme yapar.
# Power User ekranından alınan aktif parametreler, seçili cluster yapısı ve geribildirimlerle birlikte
# ilgili modelin eğitimini başlatır.
# 
# Çıktı olarak models/{model_type}_v{version}.pt dosyasını üretir.
# 
# İleriki versiyonlarda:
# - augmentasyon parametreleri
# - model mimarisi seçimi (ResNet, EfficientNet, vs)
# - feedback ağırlıkları
# - versiyonlama stratejileri entegre edilecektir.

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# Önce frontend'den gelen parametreleri oku
def load_config():
    with open("train_config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
MODEL_TYPE = config["model_type"]
MODEL_VERSION = config["version"]
EPOCHS = int(config["epochs"])
BATCH_SIZE = int(config["batch_size"])
LEARNING_RATE = float(config["learning_rate"])

# Klasörler
CLUSTER_DIR = os.path.join("exported_clusters", MODEL_TYPE)
SAVE_PATH = os.path.join("models", f"{MODEL_TYPE}_{MODEL_VERSION}.pt")
USE_GPU = torch.cuda.is_available()

# Transformlar (model tipine göre)
if MODEL_TYPE == "pattern":
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(5),
        transforms.ToTensor()
    ])
elif MODEL_TYPE == "color":
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()
    ])
elif MODEL_TYPE == "texture":
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=3),
        transforms.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 2.0)),
        transforms.RandomAutocontrast(),
        transforms.RandomRotation(10),
        transforms.ToTensor()
    ])

elif MODEL_TYPE == "color+pattern":
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(5),
        transforms.ToTensor()
    ])    
else:
    raise ValueError(f"Geçersiz model türü: {MODEL_TYPE}")

# Dataset
print("Cluster dataset'i yükleniyor...")
dataset = datasets.ImageFolder(CLUSTER_DIR, transform=transform)
class_names = dataset.classes
train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# Model
print("Model yapısı oluşturuluyor...")
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, len(class_names))

if USE_GPU:
    model = model.cuda()
    print("GPU aktif!")
else:
    print("GPU bulunamadı, CPU ile devam...")

# Loss ve optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# Eğitim döngüsü
print(f"Eğitim başlıyor ({EPOCHS} epoch)...")
model.train()
for epoch in range(EPOCHS):
    total_loss = 0
    for images, labels in train_loader:
        if USE_GPU:
            images, labels = images.cuda(), labels.cuda()

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {total_loss:.4f}")

# Kaydet
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), SAVE_PATH)
print(f"Model kaydedildi: {SAVE_PATH}")
