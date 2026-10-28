# -*- coding: utf-8 -*-
"""Slim-Neck 补丁脚本（适配 ultralytics 8.4.x）

功能：
1. 注入 ultralytics/nn/modules/Slim_Neck.py
2. 在 tasks.py 中注册 GSConv / VoVGSCSP（8.4.x 的 base_modules / repeat_modules）
3. 自动生成源码改动 diff（用于文档溯源）
4. 构建 Slim-Neck 模型并打印参数量 / GFLOPs

用法（训练机，Python 3.8+）:
    python patch_slimneck.py

输出记录（同目录 records/）:
    tasks.py.diff          对 ultralytics 源码的完整改动 diff
    patch.log              本脚本执行日志
    build_summary.txt      结构对比（基线 vs Slim-Neck）
"""
import difflib
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records"
MODULES = ("GSConv", "VoVGSCSP")
INDENT = " " * 12


def log(msg, lines=None):
    print(msg)
    if lines is not None:
        lines.append(msg)


def locate_ultralytics() -> Path:
    import ultralytics

    return Path(ultralytics.__file__).resolve().parent


def inject_module(pkg: Path, lines) -> None:
    """复制 Slim_Neck.py 到 ultralytics/nn/modules/"""
    dst = pkg / "nn" / "modules" / "Slim_Neck.py"
    shutil.copyfile(HERE / "Slim_Neck.py", dst)
    log(f"[OK] 模块已注入: {dst}", lines)


def insert_into_frozenset(src: str, name: str, modules) -> str:
    """把模块名插入 parse_model 中的 frozenset 定义"""
    marker = f"{name} = frozenset("
    idx = src.find(marker)
    if idx == -1:
        sys.exit(f"[FAIL] 在 tasks.py 中找不到 {name} 定义")
    brace = src.find("{", idx)
    body_end = src.find("}", brace)
    body = src[brace + 1 : body_end]
    existing = {item.strip() for item in body.split(",")}
    missing = [m for m in modules if m not in existing]
    if not missing:
        return src
    insert = "".join(f"\n{INDENT}{m}," for m in missing)
    return src[: brace + 1] + insert + src[brace + 1 :]


def patch_tasks(tasks_file: Path, lines) -> None:
    """在 tasks.py 注册模块，并保存 diff"""
    original = tasks_file.read_text(encoding="utf-8")
    src = original

    import_line = (
        "from ultralytics.nn.modules.Slim_Neck import "
        "GSConv, GSBottleneck, GSBottleneckC, VoVGSCSP\n\n"
    )
    if "from ultralytics.nn.modules.Slim_Neck import" not in src:
        idx = src.find("def parse_model(")
        if idx == -1:
            sys.exit("[FAIL] 在 tasks.py 中找不到 parse_model 函数")
        src = src[:idx] + import_line + src[idx:]

    src = insert_into_frozenset(src, "base_modules", MODULES)
    src = insert_into_frozenset(src, "repeat_modules", ("VoVGSCSP",))

    if src == original:
        log("[SKIP] tasks.py 已注册过 Slim-Neck，无需重复修改", lines)
        return

    RECORDS.mkdir(exist_ok=True)
    diff = difflib.unified_diff(
        original.splitlines(True),
        src.splitlines(True),
        fromfile="ultralytics/nn/tasks.py.orig",
        tofile="ultralytics/nn/tasks.py.slimneck",
        n=3,
    )
    (RECORDS / "tasks.py.diff").write_text("".join(diff), encoding="utf-8")

    backup = tasks_file.with_suffix(".py.bak_slimneck")
    if not backup.exists():
        shutil.copyfile(tasks_file, backup)
    tasks_file.write_text(src, encoding="utf-8")
    log(f"[OK] tasks.py 已注册（备份: {backup.name}，diff: records/tasks.py.diff）", lines)


def build_and_record(lines) -> None:
    """构建两个模型，记录参数量 / GFLOPs 对比"""
    from ultralytics import YOLO

    pkg = locate_ultralytics()
    official = pkg / "cfg" / "models" / "26" / "yolo26.yaml"
    # 基线 yaml 文件名需含尺度字母，否则 ultralytics 无法推断 scale
    base_cfg = RECORDS / "yolo26n_official.yaml"
    base_cfg.write_text(official.read_text(encoding="utf-8"), encoding="utf-8")
    records = []

    for tag, path in (("baseline_yolo26n", base_cfg), ("slimneck_yolo26n", HERE / "yolo26n-SlimNeck.yaml")):
        log(f"\n===== 构建 {tag} =====", lines)
        model = YOLO(str(path))
        model.info(verbose=False)
        log(f"{tag} 构建成功", lines)
        records.append((tag, model))

    _dump_info(records, lines)


def _dump_info(records, lines) -> None:
    from ultralytics.utils.torch_utils import get_flops

    out = []
    for tag, model in records:
        params = sum(p.numel() for p in model.model.parameters())
        try:
            res = get_flops(model.model, 640)
            flops = res[0] if isinstance(res, (tuple, list)) else res
        except Exception as exc:  # noqa: BLE001
            flops = float("nan")
            log(f"[WARN] {tag} GFLOPs 计算失败: {exc}", lines)
        line = f"{tag}: params={params:,} ({params / 1e6:.3f}M)  GFLOPs={flops:.1f}"
        log(line, lines)
        out.append(line)

    RECORDS.mkdir(exist_ok=True)
    (RECORDS / "build_summary.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    log(f"\n[OK] 结构对比已保存: {RECORDS / 'build_summary.txt'}", lines)


def main():
    RECORDS.mkdir(exist_ok=True)
    lines = [f"patch_slimneck.py 执行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    pkg = locate_ultralytics()
    import ultralytics

    log(f"[INFO] ultralytics {ultralytics.__version__} @ {pkg}", lines)

    inject_module(pkg, lines)
    patch_tasks(pkg / "nn" / "tasks.py", lines)
    build_and_record(lines)

    (RECORDS / "patch.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[记录] {RECORDS / 'patch.log'}")


if __name__ == "__main__":
    main()
