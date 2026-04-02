import torch
import numpy as np
import os
import random
from model import SignModel

# ====================== 【GPU 强制开启】 ======================
DEVICE = torch.device("cuda")
print(f"✅ 运行设备: {DEVICE}")

# ====================== 固定配置 ======================
FRAME_LEN = 150
INPUT_DIM = 50
TEST_SAMPLES = 100

# ====================== 加载模型 ======================
print("🔹 加载模型...")
label_map = np.load("label_map.npy", allow_pickle=True).item()
idx2label = {v: k for k, v in label_map.items()}

model = SignModel(num_classes=len(label_map)).to(DEVICE)
model.load_state_dict(torch.load("best_model.pth", map_location=DEVICE))
model.eval()

mean, std = np.load("mean_std.npy", allow_pickle=True)

# ====================== 收集所有文件 ======================
all_txt_files = []
for root, _, files in os.walk("dataset"):
    for f in files:
        if f.endswith(".txt"):
            all_txt_files.append(os.path.join(root, f))

random.seed(42)
test_files = random.sample(all_txt_files, TEST_SAMPLES)
print(f"✅ 总文件数：{len(all_txt_files)}")
print(f"✅ 随机抽取：{TEST_SAMPLES} 份")

# ====================== 预处理 ======================
def preprocess(txt_path):
    frames = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            coords = list(map(float, line.split()))
            frames.append(coords[:INPUT_DIM])

    arr = np.array(frames, dtype=np.float32)
    if len(arr) < FRAME_LEN:
        pad = np.zeros((FRAME_LEN - len(arr), INPUT_DIM), dtype=np.float32)
        arr = np.concatenate([arr, pad])
    else:
        arr = arr[:FRAME_LEN]

    arr = (arr - mean) / std
    return arr

# ====================== 批量测试 ======================
correct = 0
print("\n" + "="*60)
print("开始测试 100 份随机文件...")
print("="*60)

for i, file_path in enumerate(test_files, 1):
    # ✅ 真实标签：文件夹名（数字）
    true_folder = os.path.basename(os.path.dirname(file_path))
    true_idx = int(true_folder)

    # 预处理
    data = preprocess(file_path)

    # ✅ 推理（修复维度，绝对不报错）
    with torch.no_grad():
        x = torch.tensor(data).float().to(DEVICE)
        output = model(x)
        pred_idx = output.argmax(1).item()

    # ✅ 对比数字ID（正确逻辑）
    if true_idx == pred_idx:
        correct += 1
        status = "✅ 正确"
    else:
        status = "❌ 错误"

    print(f"[{i:03d}/100] 真实ID:{true_idx:4d} | 预测ID:{pred_idx:4d} {status}")

# ====================== 最终结果 ======================
acc = correct / TEST_SAMPLES
print("\n" + "="*60)
print(f"🎯 总正确数：{correct}/{TEST_SAMPLES}")
print(f"🎯 模型准确率：{acc:.1%}")
print(f"⚡️ 运行设备：GPU")
print("="*60)