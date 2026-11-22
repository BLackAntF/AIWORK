# -*- coding: utf-8 -*-
"""2x2 因子设计第 3 格 —— 官方结构 + yolo26s 教师 + 训练策略

目的：隔离「Slim-Neck 结构」与「蒸馏教师」两个变量。

2x2 设计（学生结构 x 蒸馏教师，训练策略统一）：
    D   官方 yolo26n  + 基线自蒸馏      <- 已跑 (yolo26n_ctrl_distill_strategy)
    E   官方 yolo26n  + yolo26s 教师    <- 本脚本
    F   Slim-Neck     + 基线自蒸馏      <- 实验四（仅 epoch 14，未完成）
    C   Slim-Neck     + yolo26s 教师    <- 实验三（已完成，mAP50 0.95905）

由此可得到两个实测差值（不依赖可加性假设）：
    C - E  = yolo26s 教师下，Slim-Neck 的结构效应
    E - D  = 官方结构下，更换教师（自蒸馏 -> yolo26s）的效应

与 C / D 的唯一差异：教师权重。
其余超参与实验三、对照组 D 严格一致。

初始化方式与实验三 / D 一致：从 yaml 随机初始化。

用法:
    /root/miniconda3/bin/python train_ctrl_official_teacher26s.py
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
RUN_NAME = "yolo26n_ctrl_official_teacher26s"
# 第 3 格：官方 yolo26n 结构（与 D 相同，不用 Slim-Neck）
OFFICIAL_YAML = "yolo26n.yaml"
# 与实验三相同的教师：yolo26s
TEACHER_BEST = str(Path(PROJECT_DIR) / "yolo26s_tomato_teacher" / "weights" / "best.pt")


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
        # —— 蒸馏（教师与实验三一致）——
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
        "role: 2x2 cell E (official yolo26n + yolo26s teacher + cls_pw)",
        "structure: official yolo26n.yaml (NO Slim-Neck), 2,572,280 params / 6.24 GFLOPs",
        f"teacher: {TEACHER_BEST}  (yolo26s, best mAP50-95 0.92875)",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / "env_snapshot_ctrl_E.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / "train_args_ctrl_E.json").write_text(
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

    model = YOLO(OFFICIAL_YAML)
    print("\n===== 2x2 第 3 格模型结构（官方 yolo26n，无 Slim-Neck）=====")
    model.info()
    print(f"\n===== 蒸馏教师: {TEACHER_BEST}（yolo26s）=====")
    print("\n===== 开始训练（官方结构 + yolo26s 教师 + 策略）=====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
