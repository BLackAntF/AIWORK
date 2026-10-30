# -*- coding: utf-8 -*-
"""结构改进实验训练脚本（AutoDL）

用法:
    /root/miniconda3/bin/python train_structure.py cbam     # CBAM 实验组
    /root/miniconda3/bin/python train_structure.py c2psa    # C2PSA 叠层实验组

与基线 yolo26n_tomato_b64 完全对齐：epochs=200 patience=999 batch=64 imgsz=640 cache=True workers=16 seed=0
唯一变量：模型结构（yaml）
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

# 实验组登记表：variant -> (yaml 文件名, 运行目录名)
VARIANTS = {
    "cbam": ("yolo26n-CBAM.yaml", "yolo26n_cbam_b64"),
    "c2psa": ("yolo26n-C2PSA2.yaml", "yolo26n_c2psa2_b64"),
}


def train_args(name: str) -> dict:
    """与基线完全一致的训练超参数"""
    return dict(
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
        name=name,
        exist_ok=False,  # 禁止覆盖已有 run 目录
    )


def _sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=60).decode(
            "utf-8", "ignore"
        ).strip()
    except Exception as exc:  # noqa: BLE001
        return f"<failed: {exc}>"


def record_env(variant: str, args: dict) -> None:
    """落盘环境与超参快照，供实验溯源"""
    import ultralytics

    RECORDS.mkdir(exist_ok=True)
    snapshot = "\n".join([
        f"记录时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"variant: {variant}",
        f"hostname: {platform.node()}",
        f"python: {platform.python_version()}",
        f"ultralytics: {ultralytics.__version__}",
        f"ultralytics path: {ultralytics.__file__}",
        "gpu:",
        _sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
    ])
    (RECORDS / f"env_snapshot_{variant}.txt").write_text(snapshot + "\n", encoding="utf-8")
    (RECORDS / f"train_args_{variant}.json").write_text(
        json.dumps(args, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(snapshot)


def guard(name: str) -> None:
    """已有训练进度时拒绝从头重跑"""
    run_dir = Path(PROJECT_DIR) / name
    if (run_dir / "results.csv").exists() or (run_dir / "weights").exists():
        raise SystemExit(f"[FAIL] 已存在训练进度: {run_dir}，请先备份/删除后再跑")


def main() -> None:
    variant = sys.argv[1] if len(sys.argv) > 1 else "cbam"
    yaml_name, run_name = VARIANTS[variant]
    args = train_args(run_name)
    guard(run_name)
    record_env(variant, args)

    model = YOLO(str(HERE / yaml_name))
    print("\n===== 模型结构 =====")
    model.info()
    print("\n===== 开始训练 =====", flush=True)
    model.train(**args)


if __name__ == "__main__":
    main()
