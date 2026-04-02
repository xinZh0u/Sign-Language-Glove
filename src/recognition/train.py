import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from dataset import load_all_dataset
from model import SignModel
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # 禁用 GPU，强制用 CPU
DEVICE = torch.device("cuda")
BATCH_SIZE = 16
EPOCHS = 30
LR = 0.0005

class SignDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X)
        self.y = torch.tensor(y)
    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# 加载数据
X, y, NUM_CLASSES = load_all_dataset()

# 自动划分训练/验证
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

train_loader = DataLoader(SignDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(SignDataset(X_val, y_val), batch_size=BATCH_SIZE, shuffle=False)

# 模型
model = SignModel(num_classes=NUM_CLASSES).to(DEVICE)
optimizer = optim.AdamW(model.parameters(), lr=LR)
criterion = nn.CrossEntropyLoss()

best_val = 0.0

print("\n开始训练...")
for epoch in range(EPOCHS):
    model.train()
    loss_sum, corr, total = 0, 0, 0
    for data, label in train_loader:
        data, label = data.to(DEVICE), label.to(DEVICE)
        out = model(data)
        loss = criterion(out, label)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        loss_sum += loss.item()
        corr += (out.argmax(1) == label).sum().item()
        total += label.size(0)
    train_acc = corr / total

    # 验证
    model.eval()
    v_corr, v_total = 0, 0
    with torch.no_grad():
        for data, label in val_loader:
            data, label = data.to(DEVICE), label.to(DEVICE)
            out = model(data)
            v_corr += (out.argmax(1) == label).sum().item()
            v_total += label.size(0)
    val_acc = v_corr / v_total

    if val_acc > best_val:
        best_val = val_acc
        torch.save(model.state_dict(), "best_model.pth")

    print(f"Ep{epoch+1:2d} | Train:{train_acc:.1%} | Val:{val_acc:.1%} | Best:{best_val:.1%}")

print("\n训练完成！最优模型：best_model.pth")