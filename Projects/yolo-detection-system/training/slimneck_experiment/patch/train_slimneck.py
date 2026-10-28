# -*- coding: utf-8 -*-
"""Slim-Neck 改进版 YOLO26n 番茄病害检测 —— 训练脚本（AutoDL）

训练配置与基线 yolo26n_tomato_b64 完全对齐，保证公平对比：
    epochs=200  patience=999(跑满)  batch=64  imgsz=640  cache=True  workers=16  seed=0

训练前自动落盘以下记录（records/，用于文档溯源）：
    env_snapshot.txt      GPU / ultralytics 版本 / Python / 数据集统计
    data.yaml             数据集配置副本
    yolo26_official.yaml  官方原结构快照（对比基线）
    train_args.json       本次训练全部超参数

用法:
    python train_slimneck.py
"""
import json
import platform
import subprocess
import time
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records"

# ===== 环境路径（与 10-11 基线训练保持一致）=====
DATA_YAML = "/root/ultralytics-YOLO26/datasets/tomato/data.yaml"
PROJECT_DIR = "/root/ultralytics-YOLO26/runs/tomato"

# ===== 与基线完全一致的训练超参数 =====
TRAIN_ARGS = dict(
    data=DATA_YAML,
    epochs=200,
    patience=999,  # 禁用早停，跑满 200 轮（与基线一致）
    batch=64,
    imgsz=640,
    cache=True,
    device="0",
    workers=16,
    seed=0,
    optimizer="auto",
    project=PROJECT_DIR,
    name="yolo26n_slimneck_b64",
    exist_ok=True,
)


def _sh(cmd: str) -> str:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=60)
        return out.decode("utf-8", "ignore").strip()
    except Exception as exc:  # noqa: BLE001
        return f"<failed: {exc}>"


def _dataset_stats(data_yaml: str) -> str:
    """统计训练/验证集图片数量"""
    try:
        import yaml

        cfg = yaml.safe_load(Path(data_yaml).read_text(encoding="utf-8"))
        root = Path(cfg.get("path", ""))
        lines = [f"data.yaml: {data_yaml}", f"path: {root}", f"nc: {cfg.get('nc')}"]

        def count(split):
            p = root / split
            return len(list(p.rglob("*.jpg"))) + len(list(p.rglob("*.png"))) if p.exists() else -1

        lines.append(f"train images: {count(cfg.get('train', ''))}")
        lines.append(f"val images: {count(cfg.get('val', ''))}")
        return "\n".join(lines)
    except Exception as exc:  # noqa: BLE001
        return f"<dataset stats failed: {exc}>"


def record_env() -> None:
    import ultralytics

    RECORDS.mkdir(exist_ok=True)
    official = Path(ultralytics.__file__).resolve().parent / "cfg" / "models" / "26" / "yolo26.yaml"

    snapshot = "\n".join([
        f"记录时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
        "dataset:",
        _dataset_stats(DATA_YAML),
    ])
    (RECORDS / "env_snapshot.txt").write_text(snapshot + "\n", encoding="utf-8")

    (RECORDS / "data.yaml").write_text(
        Path(DATA_YAML).read_text(encoding="utf-8"), encoding="utf-8")
    (RECORDS / "yolo26_official.yaml").write_text(
        official.read_text(encoding="utf-8"), encoding="utf-8")
    (RECORDS / "train_args.json").write_text(
        json.dumps(TRAIN_ARGS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(snapshot)
    print(f"\n[记录] 环境与配置快照已写入 {RECORDS}")


def main():
    record_env()
    model = YOLO(str(HERE / "yolo26n-SlimNeck.yaml"))
    print("\n===== Slim-Neck 模型结构 =====")
    model.info()
    print("\n===== 开始训练 =====")
    model.train(**TRAIN_ARGS)


if __name__ == "__main__":
    main()
