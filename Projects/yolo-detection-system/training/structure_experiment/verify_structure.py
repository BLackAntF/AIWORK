# -*- coding: utf-8 -*-
"""结构改进实验 —— 本地 CPU 合法性验证（不占 GPU、不训练）

验证内容（每个 yaml）：
    1. 能否被 parse_model 正确构建（维度/索引错误会在这一步暴露）
    2. 参数量 / GFLOPs 与官方基线 yolo26n 的差值
    3. 一次 dummy forward 是否产出 3 个检测头输出

用法:
    python verify_structure.py
"""
from pathlib import Path

import torch

from ultralytics import YOLO
from ultralytics.utils.torch_utils import get_flops

HERE = Path(__file__).resolve().parent
VARIANTS = {
    "baseline yolo26n": "yolo26n.yaml",
    "yolo26n-CBAM": str(HERE / "yolo26n-CBAM.yaml"),
    "yolo26n-C2PSA2": str(HERE / "yolo26n-C2PSA2.yaml"),
}


def probe(name: str, yaml_path: str) -> dict:
    """构建模型并返回参数量/GFLOPs/前向是否成功"""
    try:
        model = YOLO(yaml_path)
        net = model.model.eval()
        params = sum(p.numel() for p in net.parameters())
        flops = get_flops(net, imgsz=640)
        with torch.no_grad():
            out = net(torch.zeros(1, 3, 640, 640))
        return {"name": name, "params": params, "flops": flops, "out": _shapes(out), "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"name": name, "params": 0, "flops": 0.0, "out": [], "error": f"{type(exc).__name__}: {exc}"}


def _shapes(out) -> list:
    """统一提取输出维度（YOLO26 end2end 模式输出为 dict）"""
    if isinstance(out, dict):
        return [(k, tuple(v.shape)) for k, v in out.items() if hasattr(v, "shape")]
    if isinstance(out, (list, tuple)):
        return [tuple(o.shape) if hasattr(o, "shape") else type(o).__name__ for o in out]
    return [tuple(out.shape)]


def main() -> None:
    rows = [probe(n, p) for n, p in VARIANTS.items()]
    base = rows[0]
    print(f"{'variant':<20}{'params':>12}{'Δparams':>12}{'GFLOPs':>10}{'ΔGFLOPs':>12}  heads")
    print("-" * 78)
    for r in rows:
        if r["error"]:
            print(f"{r['name']:<20}{'BUILD FAILED':>12}  {r['error']}")
            continue
        dp = r["params"] - base["params"]
        df = r["flops"] - base["flops"]
        print(
            f"{r['name']:<20}{r['params']:>12,}{dp:>+12,}{r['flops']:>10.2f}{df:>+12.2f}  {r['out']}"
        )
    print("\n[结论] BUILD FAILED 表示结构不合法，必须先修 yaml 再上 GPU。")


if __name__ == "__main__":
    main()
