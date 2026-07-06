#!/bin/bash
# ========================================
#   AutoDL YOLO26 训练脚本
#   番茄叶片病害检测
#   使用 Ultralytics 最新 YOLO26 模型
# ========================================

# 安装依赖
echo "安装依赖..."
pip install ultralytics opencv-python pillow -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建训练脚本
cat > train_tomato.py << 'EOF'
from ultralytics import YOLO
import os

# 数据集配置文件路径
DATA_yaml = "/root/autodl-tmp/datasets/tomato/data.yaml"

# YOLO26 模型选择
# yolo26n = nano (最快，显存需求最低)
# yolo26s = small
# yolo26m = medium
# yolo26l = large
# yolo26x = xlarge (最准，显存需求最高)
MODEL = "yolo26n.pt"  # 快速训练用 nano 模型

# 训练参数
EPOCHS = 100          # 训练轮数
IMG_SIZE = 640         # 图片尺寸
BATCH = 16            # 批次大小（根据显存调整）
DEVICE = 0             # 使用 GPU 0

def main():
    print("=" * 60)
    print("  番茄叶片病害检测 - YOLO26 训练")
    print("=" * 60)
    print(f"  预训练模型: {MODEL}")
    print(f"  数据集配置: {DATA_yaml}")
    print(f"  训练轮数: {EPOCHS}")
    print(f"  图片尺寸: {IMG_SIZE}")
    print(f"  批次大小: {BATCH}")
    print(f"  设备: GPU {DEVICE}")
    print("=" * 60)

    # 加载预训练模型
    model = YOLO(MODEL)

    # 开始训练
    results = model.train(
        data=DATA_yaml,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH,
        device=DEVICE,
        project='/root/autodl-tmp/training_results',
        name='tomato_disease_yolo26',
        exist_ok=True,
        patience=20,           # 早停耐心值
        save=True,             # 保存模型
        save_period=10,        # 每10轮保存一次
        cache=True,            # 缓存图片加速训练
        workers=4,             # 数据加载线程数
        optimizer='AdamW',     # 优化器
        lr0=0.001,            # 初始学习率
        lrf=0.01,             # 最终学习率
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        box=7.5,
        cls=0.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        copy_paste=0.0,
        pretrained=True,
        verbose=True,
    )

    # 验证模型
    print("\n验证模型性能...")
    metrics = model.val(data=DATA_yaml)
    print(f"\nmAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")

    # 导出模型（可选）
    print("\n导出 ONNX 模型...")
    model.export(format='onnx')

    print("\n" + "=" * 60)
    print("  训练完成！")
    print(f"  最佳模型: /root/autodl-tmp/training_results/tomato_disease_yolo26/weights/best.pt")
    print(f"  ONNX模型: /root/autodl-tmp/training_results/tomato_disease_yolo26/weights/best.onnx")
    print("=" * 60)

if __name__ == "__main__":
    main()
EOF

echo "训练脚本已创建: train_tomato.py"
echo ""
echo "运行命令:"
echo "  python train_tomato.py"
