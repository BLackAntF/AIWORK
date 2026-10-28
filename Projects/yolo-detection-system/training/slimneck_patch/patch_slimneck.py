# -*- coding: utf-8 -*-
"""Slim-Neck 补丁脚本（在训练机上运行，如 AutoDL）

功能：
1. 把同目录 Slim_Neck.py 注入 ultralytics/nn/modules/models/
2. 在 ultralytics/nn/tasks.py 的 parse_model 中注册 GSConv / VoVGSCSP
3. 自动验证：用同目录 yolo26-SlimNeck.yaml 构建模型并打印参数量/GFLOPs

用法（在已装 ultralytics 的训练环境里）:
    python patch_slimneck.py

特性：
- 幂等：重复执行不会重复插入
- 安全：tasks.py 修改前自动备份为 tasks.py.bak_slimneck
"""

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_NAMES = ("GSConv", "VoVGSCSP")


def locate_ultralytics():
    import ultralytics

    return Path(ultralytics.__file__).resolve().parent


def inject_module(pkg: Path) -> None:
    """复制 Slim_Neck.py 到 ultralytics/nn/modules/models/ 并写 __init__.py"""
    models_dir = pkg / "nn" / "modules" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(HERE / "Slim_Neck.py", models_dir / "Slim_Neck.py")

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from .Slim_Neck import GSConv, GSBottleneck, GSBottleneckC, VoVGSCSP\n\n"
        '__all__ = ("GSConv", "GSBottleneck", "GSBottleneckC", "VoVGSCSP")\n',
        encoding="utf-8",
    )
    print(f"[OK] 模块已注入: {models_dir}")


def patch_tasks(tasks_file: Path) -> bool:
    """在 tasks.py 中注册模块，返回是否有改动"""
    src = tasks_file.read_text(encoding="utf-8")
    if all(f" {name}," in src or f" {name},\n" in src for name in MODULE_NAMES):
        print("[SKIP] tasks.py 已注册过 Slim-Neck 模块")
        return False

    # 1) 导入行
    import_line = "from ultralytics.nn.modules.models import GSConv, VoVGSCSP\n"
    anchor_import = "from ultralytics.nn.modules import"
    if import_line not in src:
        idx = src.find(anchor_import)
        if idx == -1:
            sys.exit("[FAIL] tasks.py 中找不到 ultralytics 模块导入区，请把 ultralytics 版本发给开发者")
        line_end = src.find("\n", idx) + 1
        src = src[:line_end] + import_line + src[line_end:]

    # 2) parse_model 中 c2=args[0] 的集合行（特征：行内含 SPPF）
    def insert_into_set(match, names):
        body = match.group(1)
        if all(name in body for name in names):
            return match.group(0)
        return "if m in {" + ", ".join(list(names) + [body.strip()]) + "}:"

    c2_pattern = re.compile(r"if m in \{([^}]*)\}:")
    c2_line, n_line = None, None
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if "if m in {" in line and "SPPF" in line and c2_line is None:
            c2_line = i
        if "if m in {" in line and c2_line is not None and i > c2_line and n_line is None:
            follow = "\n".join(lines[i + 1 : i + 3])
            if "args.insert(2, n)" in follow:
                n_line = i
    if c2_line is None or n_line is None:
        sys.exit("[FAIL] 未能定位 parse_model 注册集合（c2 组或 n 组），请把 ultralytics 版本发给开发者")

    def add_names(line):
        body = line[line.find("{") + 1 : line.find("}")]
        names = [n.strip() for n in body.split(",") if n.strip()]
        for name in MODULE_NAMES if "SPPF" in line else ["VoVGSCSP"]:
            if name not in names:
                names.insert(0, name)
        return "if m in {" + ", ".join(names) + "}:"

    lines[c2_line] = add_names(lines[c2_line])
    lines[n_line] = add_names(lines[n_line])
    src = "\n".join(lines)

    shutil.copyfile(tasks_file, tasks_file.with_suffix(".py.bak_slimneck"))
    tasks_file.write_text(src, encoding="utf-8")
    print(f"[OK] tasks.py 已注册（备份: {tasks_file.name}.bak_slimneck）")
    return True


def verify_build() -> None:
    """构建 Slim-Neck 模型验证注册是否成功"""
    from ultralytics import YOLO

    model = YOLO(str(HERE / "yolo26-SlimNeck.yaml"))
    model.info()
    print("[OK] Slim-Neck 模型构建成功，可开始训练")


def main():
    pkg = locate_ultralytics()
    print(f"[INFO] ultralytics 位置: {pkg}")
    inject_module(pkg)
    patch_tasks(pkg / "nn" / "tasks.py")
    verify_build()


if __name__ == "__main__":
    main()
