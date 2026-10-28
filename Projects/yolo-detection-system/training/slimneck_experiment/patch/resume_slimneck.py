# -*- coding: utf-8 -*-
"""Slim-Neck 训练中断后恢复脚本

用法（训练机）:
    python resume_slimneck.py

从 last.pt 恢复训练，沿用 checkpoint 中保存的原始超参数（200 轮 / batch 64 / 640 / patience 999），
仅在 2026-10-29 手动中断（epoch 46）后使用；正常跑完 200 轮则无需此脚本。
"""
from pathlib import Path

from ultralytics import YOLO

RUN_DIR = Path('/root/ultralytics-YOLO26/runs/tomato/yolo26n_slimneck_b64')
LAST_PT = RUN_DIR / 'weights' / 'last.pt'


def resume() -> None:
    """校验 checkpoint 后从断点继续训练"""
    if not LAST_PT.exists():
        raise SystemExit(f'[FAIL] 找不到断点权重: {LAST_PT}')

    print(f'[INFO] 从断点恢复: {LAST_PT}')
    model = YOLO(str(LAST_PT))
    model.train(resume=True)


if __name__ == '__main__':
    resume()
