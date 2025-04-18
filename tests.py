import torch
import torch.nn as nn
import torch.optim as optim
import time

# Rastgele veri seti oluştur (1000 örnek, her biri 100 özellikli, 10 sınıf)
num_samples = 1000
num_features = 100
num_classes = 10

X = torch.randn(num_samples, num_features)
y = torch.randint(0, num_classes, (num_samples,))

# Basit bir MLP modeli
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(num_features, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

def train(model, device):
    model.to(device)
    X_dev = X.to(device)
    y_dev = y.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    start = time.time()
    for epoch in range(10):  # 10 epoch eğitim
        optimizer.zero_grad()
        outputs = model(X_dev)
        loss = criterion(outputs, y_dev)
        loss.backward()
        optimizer.step()
    if device.type == 'cuda':
        torch.cuda.synchronize()
    end = time.time()
    return end - start

# CPU'da eğitim
model_cpu = SimpleNet()
cpu_time = train(model_cpu, torch.device('cpu'))
print(f"🧠 CPU ile eğitim süresi: {cpu_time:.4f} saniye")

# GPU varsa eğitim
if torch.cuda.is_available():
    model_gpu = SimpleNet()
    gpu_time = train(model_gpu, torch.device('cuda'))
    print(f"⚡ GPU ile eğitim süresi: {gpu_time:.4f} saniye")
else:
    print("⚠️ GPU bulunamadı, GPU testi atlandı.")
