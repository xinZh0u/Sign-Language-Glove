import os
import numpy as np

# 配置
FRAME_LEN = 150
INPUT_DIM = 50
DATA_ROOT = "dataset"

def load_dictionary():
    word_dict = {}
    with open("dictionary.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            code, word = line.split()
            # 【关键：去掉前3个0】
            short_code = code[3:]
            word_dict[short_code] = word
    return word_dict

def load_all_dataset():
    word_dict = load_dictionary()
    X, y = [], []
    label_map = {}

    # 遍历 dataset 下的 500 个文件夹（000 ~ 499）
    for folder_name in os.listdir(DATA_ROOT):
        folder_path = os.path.join(DATA_ROOT, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # 文件夹名就是去0后的编码：000、001...499
        short_code = folder_name
        if short_code not in word_dict:
            continue

        # 拿到词汇
        word = word_dict[short_code]

        # 建立标签ID
        if word not in label_map:
            label_map[word] = len(label_map)
        label_id = label_map[word]

        # 读取当前文件夹下 250 个 txt
        for fname in os.listdir(folder_path):
            if not fname.endswith(".txt"):
                continue

            frames = []
            txt_path = os.path.join(folder_path, fname)
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    nums = list(map(float, line.split()))
                    frames.append(nums[:INPUT_DIM])

            # 统一长度 150 帧
            frames = np.array(frames, dtype=np.float32)
            if len(frames) < FRAME_LEN:
                pad = np.zeros((FRAME_LEN - len(frames), INPUT_DIM))
                frames = np.concatenate([frames, pad])
            else:
                frames = frames[:FRAME_LEN]

            X.append(frames)
            y.append(label_id)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)

    # 归一化
    mean = X.mean(axis=(0, 1), keepdims=True)
    std = X.std(axis=(0, 1), keepdims=True) + 1e-6
    X = (X - mean) / std

    np.save("label_map.npy", label_map)
    np.save("mean_std.npy", (mean, std))

    print(f"总样本数：{len(X)}")
    print(f"总词汇数：{len(label_map)}")
    return X, y, len(label_map)