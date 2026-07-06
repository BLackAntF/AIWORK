# AutoDL 数据集上传与训练指南

## 一、数据集准备

### 1.1 先整理本地目录

运行 `整理目录.bat`，整理后的结构：
```
Tomato/
├── images/
│   ├── train/       (~12000 张图片)
│   └── val/         (~3000 张图片)
├── labels/
│   ├── train/       (~5000 个标注)
│   └── val/         (需要从训练集划分)
├── data.yaml        # 配置文件
├── train_autodl.sh # 训练脚本
└── README.md        # 本文档
```

### 1.2 注意验证集标注问题

**问题**：原始数据集的 val 图片没有对应标注

**解决方案**：
- 方案 A：用训练集全部数据训练，不划分验证集
- 方案 B：从训练集中手动划分 20% 作为验证集（更推荐）

---

## 二、上传到 AutoDL

### 2.1 方式一：通过 AutoDL 控制台上传（推荐小数据）

1. 打开 AutoDL 控制台：https://console.autodl.com
2. 进入你的实例
3. 使用 JupyterLab 或 FileZilla 上传

### 2.2 方式二：SCP 上传（大文件推荐）

```bash
# 在本地 PowerShell 执行
scp -r D:\Develop\CODE\AIWORK\Projects\yolo-detection-system\dataset\Tomato root@你的实例IP:/root/autodl-tmp/datasets/
```

**获取实例 IP**：
- 登录 AutoDL 控制台
- 查看实例详情，找到公网 IP

### 2.3 方式三：阿里云 OSS 中转（超大文件）

如果数据集太大（>10GB），建议：
1. 上传到阿里云 OSS
2. 在 AutoDL 实例中用 wget 下载

---

## 三、AutoDL 实例准备

### 3.1 选择镜像

推荐使用 **PyTorch 镜像**，自带 CUDA：

```
镜像：PyTorch 2.0+ / Python 3.10 / CUDA 11.8
```

### 3.2 创建数据集目录

登录实例后执行：
```bash
mkdir -p /root/autodl-tmp/datasets/tomato
```

### 3.3 上传文件

用 FileZilla 或 scp 上传整个 Tomato 文件夹到：
```
/root/autodl-tmp/datasets/tomato/
```

### 3.4 安装依赖

```bash
pip install ultralytics opencv-python pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 四、开始训练

### 4.1 上传训练脚本

上传 `train_autodl.sh` 或直接创建 `train_tomato.py`

### 4.2 修改 data.yaml

确保服务器上的 `data.yaml` 路径正确：
```yaml
path: /root/autodl-tmp/datasets/tomato
```

### 4.3 运行训练

```bash
python train_tomato.py
```

### 4.4 训练时间预估

| 硬件 | YOLOv8n (nano) | YOLOv8s (small) | YOLOv8m (medium) |
|:---|:---:|:---:|:---:|
| RTX 3060 (12GB) | ~2-3 小时 | ~5-8 小时 | ~12-24 小时 |
| RTX 3090 (24GB) | ~1-2 小时 | ~3-4 小时 | ~6-12 小时 |
| A100 (40GB) | ~30 分钟 | ~1-2 小时 | ~3-6 小时 |

---

## 五、训练结果

训练完成后，模型保存在：
```
/root/autodl-tmp/training_results/tomato_disease/weights/
├── best.pt      # 最佳模型
└── last.pt      # 最后一轮模型
```

### 5.1 下载模型

用 FileZilla 或 scp 下载到本地：
```bash
scp root@你的实例IP:/root/autodl-tmp/training_results/tomato_disease/weights/best.pt D:\Models\
```

### 5.2 使用模型

将 `best.pt` 放到项目的 `backend/models/` 目录，然后在管理后台切换激活该模型。

---

## 六、快速命令汇总

```bash
# 1. 创建目录
mkdir -p /root/autodl-tmp/datasets/tomato
mkdir -p /root/autodl-tmp/training_results

# 2. 安装依赖
pip install ultralytics opencv-python pillow -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 启动训练
python train_tomato.py

# 4. 查看训练进度（另开终端）
tensorboard --logdir /root/autodl-tmp/training_results/tomato_disease

# 5. 下载模型
scp root@实例IP:/root/autodl-tmp/training_results/tomato_disease/weights/best.pt 本地路径/
```

---

## 七、常见问题

### Q1: 显存不够怎么办？
- 减小 BATCH_SIZE（从 16 改成 8 或 4）
- 减小 IMG_SIZE（从 640 改成 416 或 320）

### Q2: 训练中断怎么办？
- 模型会自动保存 best.pt
- 修改 `exist_ok=False` 可以断点续训

### Q3: 如何查看训练效果？
- 训练完成后查看 `results.csv`
- 用 `runs/detect/val/` 下的图片查看预测效果
