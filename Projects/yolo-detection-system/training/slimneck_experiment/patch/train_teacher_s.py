# -*- coding: utf-8 -*-
"""蒸馏实验 —— 教师模型训练（yolo26s on tomato）

教师用 yolo26s（10M 参数），在番茄数据集上微调 200 轮，
作为后续 Slim-Neck 学生蒸馏的监督来源。

用法:
    /root/miniconda3/bin/python train_teacher_s.py
"""
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records"

DATA_YAML = "/root/ultralytics-YOLO26/datasets/tomato/data.yaml"
PROJECT_DIR = "/root/ultralytics-YOLO26/runs/tomato"
RUN_NAME = "yolo26s_tomato_teacher"


def train_args() -> dict:
    return dict(
        data=DATA_YAML,
        epochs=200,
        patience=999,
        batch=32,  # yolo26s 较大，batch 减半防 OOM
        imgsz=640,
        cache=True,
        device="0",
        workers=16,
        seed=0,
        optimizer="auto",
        project=PROJECT_DIR,
        name=RUN_NAME,
        exist_ok=False,
    )


def _sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=60).decode(
            "utf-8", "ignore"
        ).strip()
    except Exception as exc:  # noqa: BLE001
        return f"<failed: {exc}>"


def record_env(args: dict) -> None:
    import ultralytics

    RECORDS.mkdir(exist_ok=True)
    snapshot = "\n".join([
        f"记录时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"role: teacher (yolo26s)",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / "env_snapshot_teacher.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / "train_args_teacher.json").write_text(
        json.dumps(args, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(snapshot)


def guard(name: str) -> None:
    run_dir = Path(PROJECT_DIR) / name
    if (run_dir / "results.csv").exists() or (run_dir / "weights").exists():
        raise SystemExit(f"[FAIL] 已存在训练进度: {run_dir}，请先备份/删除后再跑")


def main() -> None:
    args = train_args()
    guard(RUN_NAME)
    record_env(args)

    # 从 COCO 预训练权重微调（联网下载 yolo26s.pt），收敛更快、教师更强
    model = YOLO("yolo26s.pt")
    print("\n===== 教师模型结构 =====")
    model.info()
    print("\n===== 开始训练 yolo26s 教师 =====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
