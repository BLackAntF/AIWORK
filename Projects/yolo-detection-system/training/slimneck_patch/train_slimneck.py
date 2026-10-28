# -*- coding: utf-8 -*-
"""Slim-Neck 改进版番茄病害检测训练脚本（AutoDL 上运行）

先运行 patch_slimneck.py 完成模块注入与验证，再运行本脚本。
训练配置与基线 yolo26n_tomato_b64 完全对齐（200 epochs / batch 64 / 640 / 跑满不早停），
以保证与基线的公平对比。

用法:
    python train_slimneck.py
"""

import warnings
from pathlib import Path

from ultralytics import YOLO

warnings.filterwarnings("ignore")

# ===== 按实际环境修改以下三项 =====
DATA_YAML = "/root/autodl-tmp/dataset/tomato/data.yaml"  # 番茄数据集 data.yaml 路径
PROJECT_DIR = "/root/autodl-tmp/runs"  # 训练输出目录
DEVICE = 0  # GPU 编号

EPOCHS = 200
BATCH = 64
IMGSZ = 640


def main():
    model = YOLO(str(Path(__file__).parent / "yolo26-SlimNeck.yaml"))
    model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        patience=999,  # 跑满 200 轮，生成完整对比数据（与基线一致）
        batch=BATCH,
        imgsz=IMGSZ,
        workers=8,
        device=DEVICE,
        project=PROJECT_DIR,
        name="yolo26n_slimneck_b64",
    )


if __name__ == "__main__":
    main()
