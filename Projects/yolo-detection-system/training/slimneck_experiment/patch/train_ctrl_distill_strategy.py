# -*- coding: utf-8 -*-
"""对照组 —— 基线官方结构 + 自蒸馏 + 训练策略（消融隔离用）

与实验三（Slim-Neck + 蒸馏 + 策略）的唯一变量差异：
    实验三 学生结构 = Slim-Neck yolo26n（yolo26n-SlimNeck.yaml，2.457M 参数）
    对照组 学生结构 = 官方 yolo26n（yolo26n.yaml，2.572M 参数，未改动 head）

其余超参与实验三 / 实验四严格对齐，保证消融时「模型结构」是唯一变量：
    蒸馏: distill_model = 基线 yolo26n_tomato_b64/weights/best.pt（自蒸馏）, dis = 6.0
    策略: cls_pw = 0.5, close_mosaic = 20, cls = 0.8
    训练: epochs = 200, patience = 999, batch = 64, imgsz = 640, seed = 0

初始化方式与实验三学生一致：从 yaml 随机初始化（实验三学生无对应预训练权重，
同样从头训），避免「预训练 vs 从头」成为额外混淆变量。

用法:
    /root/miniconda3/bin/python train_ctrl_distill_strategy.py
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
RUN_NAME = "yolo26n_ctrl_distill_strategy"
# 对照组：官方 yolo26n 结构（不使用 Slim-Neck yaml）
OFFICIAL_YAML = "yolo26n.yaml"
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
        # —— 蒸馏（与实验三/实验四一致）——
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
        "role: control (official yolo26n + self-distill from baseline + cls_pw)",
        "structure: official yolo26n.yaml (NO Slim-Neck), 2,572,280 params / 6.24 GFLOPs",
        f"teacher: {TEACHER_BEST}  (baseline yolo26n, best mAP50-95 0.93667)",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / "env_snapshot_ctrl.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / "train_args_ctrl.json").write_text(
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
    print("\n===== 对照组模型结构（官方 yolo26n，无 Slim-Neck）=====")
    model.info()
    print(f"\n===== 自蒸馏教师: {TEACHER_BEST}（基线 yolo26n best.pt）=====")
    print("\n===== 开始训练对照组（官方结构 + 自蒸馏 + cls_pw + close_mosaic）=====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
