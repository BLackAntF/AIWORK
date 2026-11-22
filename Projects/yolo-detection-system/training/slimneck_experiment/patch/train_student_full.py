# -*- coding: utf-8 -*-
"""实验五（最强组合）—— Slim-Neck + 基线自蒸馏 + 分辨率800 + copy_paste + 类别加权

目标：以涨点为第一优先级，叠加所有已验证有效的手段，争取 mAP50-95 超过基线 0.93667。

相对实验四（自蒸馏@640）增加的变量：
    1. imgsz 640 -> 800    病害斑点为小目标，提分辨率是检测领域最稳的涨点手段
    2. copy_paste=0.1      ultralytics 内置实例复制粘贴增强，提升小目标/稀有类鲁棒性

其余与实验四严格一致（教师=基线 yolo26n best.pt 自蒸馏、cls_pw=0.5、close_mosaic=20、cls=0.8、dis=6.0、seed=0）。

显存：800 分辨率下 batch 由 64 降至 48，避免 OOM（RTX 4090 24G）。

用法:
    /root/miniconda3/bin/python train_student_full.py
"""
import json
import platform
import subprocess
import time
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records"

DATA_YAML = "/root/ultralytics-YOLO26/datasets/tomato/data.yaml"
PROJECT_DIR = "/root/ultralytics-YOLO26/runs/tomato"
RUN_NAME = "yolo26n_slimneck_full"
SLIMNECK_YAML = str(HERE / "yolo26n-SlimNeck.yaml")
TEACHER_BEST = str(Path(PROJECT_DIR) / "yolo26n_tomato_b64" / "weights" / "best.pt")


def train_args() -> dict:
    return dict(
        data=DATA_YAML,
        epochs=200,
        patience=999,
        batch=48,            # 800 分辨率显存上涨，由 64 降至 48 防止 OOM
        imgsz=800,           # ★ 小目标病害斑点：640 -> 800，最稳的涨点手段
        cache=True,
        device="0",
        workers=16,
        seed=0,
        optimizer="auto",
        project=PROJECT_DIR,
        name=RUN_NAME,
        exist_ok=False,
        # —— 蒸馏（自蒸馏，教师=基线 yolo26n best.pt）——
        distill_model=TEACHER_BEST,
        dis=6.0,
        # —— 数据增强（定向涨点）——
        copy_paste=0.1,      # ★ 实例复制粘贴，增强小目标/稀有类鲁棒性
        close_mosaic=20,     # 后 20 轮关 mosaic，利于分类收敛
        # —— 训练策略 ——
        cls_pw=0.5,          # 类别加权，针对类别不平衡（最弱类花叶病毒病仅 0.78）
        cls=0.8,             # 加大分类损失权重
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
        "role: student (Slim-Neck + self-distill + imgsz800 + copy_paste + cls_pw)",
        f"teacher: {TEACHER_BEST}  (baseline yolo26n, best mAP50-95 0.93667)",
        "added_vs_exp4: imgsz=800, copy_paste=0.1, batch=48",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / "env_snapshot_full.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / "train_args_full.json").write_text(
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
    print(f"\n===== 配置：自蒸馏(基线教师) + imgsz800 + copy_paste0.1 + cls_pw0.5 =====")
    print("\n===== 开始训练（最强组合，目标 mAP50-95 > 0.93667）=====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
