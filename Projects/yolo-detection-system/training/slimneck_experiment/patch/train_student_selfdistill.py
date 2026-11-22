# -*- coding: utf-8 -*-
"""实验四 —— 学生模型训练（Slim-Neck + 基线自蒸馏 + 类别加权）

与实验三的唯一变量差异：
    实验三 教师 = yolo26s_tomato_teacher/best.pt  （best mAP50-95 0.92875，弱于基线）
    实验四 教师 = yolo26n_tomato_b64/best.pt      （best mAP50-95 0.93667，手里最强模型，自蒸馏）

其余超参与实验三严格对齐（cls_pw / close_mosaic / cls / dis / epochs / batch / imgsz / seed），
保证消融时教师差异是唯一变量。

学生 = Slim-Neck 版 yolo26n（2.457M 参数，−4.49% / −9.68% GFLOPs）

用法:
    /root/miniconda3/bin/python train_student_selfdistill.py
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
RUN_NAME = "yolo26n_slimneck_selfdistill"
SLIMNECK_YAML = str(HERE / "yolo26n-SlimNeck.yaml")
# 自蒸馏教师：基线 yolo26n 的 best.pt（本数据集上最强模型，mAP50-95 0.93667）
TEACHER_BEST = str(Path(PROJECT_DIR) / "yolo26n_tomato_b64" / "weights" / "best.pt")


def train_args() -> dict:
    return dict(
        data=DATA_YAML,
        epochs=200,
        patience=999,
        batch=64,
        imgsz=640,
        cache=True,
        device="0",
        workers=16,
        seed=0,
        optimizer="auto",
        project=PROJECT_DIR,
        name=RUN_NAME,
        exist_ok=False,
        # —— 蒸馏 ——
        distill_model=TEACHER_BEST,
        dis=6.0,
        # —— 训练策略优化（与实验三一致）——
        cls_pw=0.5,
        close_mosaic=20,
        cls=0.8,
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
        "role: student (Slim-Neck + self-distill from baseline yolo26n)",
        f"teacher: {TEACHER_BEST}  (baseline yolo26n, best mAP50-95 0.93667)",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / "env_snapshot_selfdistill.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / "train_args_selfdistill.json").write_text(
        json.dumps(args, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(snapshot)


def guard(name: str) -> None:
    run_dir = Path(PROJECT_DIR) / name
    if (run_dir / "results.csv").exists() or (run_dir / "weights").exists():
        raise SystemExit(f"[FAIL] 已存在训练进度: {run_dir}，请先备份/删除后再跑")
    if not Path(TEACHER_BEST).exists():
        raise SystemExit(f"[FAIL] 教师权重不存在: {TEACHER_BEST}")


def main() -> None:
    args = train_args()
    guard(RUN_NAME)
    record_env(args)

    model = YOLO(SLIMNECK_YAML)
    print("\n===== 学生模型结构（Slim-Neck）=====")
    model.info()
    print(f"\n===== 自蒸馏教师: {TEACHER_BEST}（基线 yolo26n best.pt）=====")
    print("\n===== 开始训练 Slim-Neck 学生（自蒸馏 + cls_pw + close_mosaic）=====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
