# -*- coding: utf-8 -*-
"""蒸馏实验 —— 学生模型训练（Slim-Neck + 蒸馏 + 类别加权）

学生 = Slim-Neck 版 yolo26n（2.457M 参数）
教师 = yolo26s_tomato_teacher 的 best.pt

改进手段（论文贡献点）：
    1. Slim-Neck 轻量化结构（GSConv/VoVGSCSP 替换 head C3k2）—— 结构改进
    2. 知识蒸馏（distill_model + dis）—— 精度恢复
    3. cls_pw=0.5 类别加权 —— 针对类别不平衡
    4. close_mosaic=20 —— 后 20 轮关马赛克，利于分类收敛

用法:
    /root/miniconda3/bin/python train_student_distill.py
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
RUN_NAME = "yolo26n_slimneck_distill"
SLIMNECK_YAML = str(HERE / "yolo26n-SlimNeck.yaml")
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
        # —— 蒸馏 ——
        distill_model=TEACHER_BEST,
        dis=6.0,
        # —— 训练策略优化 ——
        cls_pw=0.5,       # 类别加权损失，针对 3.5x 类别不平衡
        close_mosaic=20,  # 最后 20 轮关闭 mosaic，利于分类收敛
        cls=0.8,          # 加大分类损失权重（默认 0.5）
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
        f"role: student (Slim-Neck + distill + cls_pw)",
        f"teacher: {TEACHER_BEST}",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / "env_snapshot_student.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / "train_args_student.json").write_text(
        json.dumps(args, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(snapshot)


def guard(name: str) -> None:
    run_dir = Path(PROJECT_DIR) / name
    if (run_dir / "results.csv").exists() or (run_dir / "weights").exists():
        raise SystemExit(f"[FAIL] 已存在训练进度: {run_dir}，请先备份/删除后再跑")
    if not Path(TEACHER_BEST).exists():
        raise SystemExit(f"[FAIL] 教师权重不存在: {TEACHER_BEST}，请先跑完 train_teacher_s.py")


def main() -> None:
    args = train_args()
    guard(RUN_NAME)
    record_env(args)

    model = YOLO(SLIMNECK_YAML)
    print("\n===== 学生模型结构（Slim-Neck）=====")
    model.info()
    print(f"\n===== 蒸馏教师: {TEACHER_BEST} =====")
    print("\n===== 开始训练 Slim-Neck 学生（蒸馏+cls_pw+close_mosaic）=====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
