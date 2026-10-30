# -*- coding: utf-8 -*-
"""把官方 CBAM 注册到 ultralytics 的 parse_model 命名空间（幂等 + 可回滚）

背景：
    CBAM 类完整存在于 ultralytics/nn/modules/conv.py（官方自带），
    但 tasks.py 没有 import 它，而 parse_model 用 globals()[m] 解析 yaml 里的模块名，
    因此 yaml 写 CBAM 会 KeyError。本脚本只做一件事：在 tasks.py 的 import 列表里加一行 CBAM。

用法:
    python register_cbam.py status     # 查看当前状态
    python register_cbam.py apply      # 应用（首次会备份 tasks.py.bak_cbam）
    python register_cbam.py revert     # 回滚到备份
"""
import shutil
import sys
from pathlib import Path

import ultralytics

TASKS_PY = Path(ultralytics.__file__).resolve().parent / "nn" / "tasks.py"
BACKUP = TASKS_PY.with_suffix(".py.bak_cbam")
ANCHOR = "from ultralytics.nn.modules import (\n"
INJECT = "    CBAM,\n"


def is_applied(text: str) -> bool:
    """判断 CBAM 是否已出现在 import 列表中"""
    head = text.split(ANCHOR, 1)[-1].split(")", 1)[0]
    return any(line.strip() == "CBAM," for line in head.splitlines())


def apply() -> None:
    """注入 import 行（已注入则跳过）"""
    text = TASKS_PY.read_text(encoding="utf-8")
    if is_applied(text):
        print("[SKIP] CBAM 已注册")
        return
    if not BACKUP.exists():
        shutil.copy2(TASKS_PY, BACKUP)
        print(f"[BACKUP] {BACKUP}")
    TASKS_PY.write_text(text.replace(ANCHOR, ANCHOR + INJECT, 1), encoding="utf-8")
    print("[APPLY] 已在 tasks.py import 列表注入 CBAM")


def revert() -> None:
    """从备份还原 tasks.py"""
    if not BACKUP.exists():
        print("[SKIP] 无备份文件，无需回滚")
        return
    shutil.copy2(BACKUP, TASKS_PY)
    print("[REVERT] 已还原 tasks.py")


def status() -> None:
    """打印当前注册状态"""
    text = TASKS_PY.read_text(encoding="utf-8")
    print(f"tasks.py      : {TASKS_PY}")
    print(f"backup exists : {BACKUP.exists()}")
    print(f"CBAM imported : {is_applied(text)}")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"apply": apply, "revert": revert, "status": status}[action]()
