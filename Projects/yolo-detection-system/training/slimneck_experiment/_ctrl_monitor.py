# -*- coding: utf-8 -*-
"""对照组训练后台监护：探测训练结束 -> 下载关键产物 -> 解析最终 best。

密码通过环境变量 ADL_HOST/ADL_PORT/ADL_USER/ADL_PWD 传入，不写死。
"""
import csv
import os
import sys
import time
from pathlib import Path

sys.path.insert(
    0,
    r"d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\training\slimneck_experiment\tools",
)
from adl_remote import client, run  # noqa: E402

REMOTE_RUN = "/root/ultralytics-YOLO26/runs/tomato/yolo26n_ctrl_distill_strategy"
LOCAL_DIR = Path(
    r"d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\training\slimneck_experiment\ctrl_output"
)
# bracket trick 避免 pgrep 匹配到探测命令自身
CHECK = "if pgrep -f 'train_ctrl_distill_strateg[y].py' >/dev/null; then echo RUNNING; else echo DONE; fi"
WANTED = ["results.csv", "args.yaml", "results.png"]

LOCAL_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOCAL_DIR / "monitor.log"


def w(msg: str) -> None:
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def grab(c, remote_path: str, local_path: str) -> bool:
    sftp = c.open_sftp()
    try:
        sftp.get(remote_path, local_path)
        return True
    except IOError:
        return False
    finally:
        sftp.close()


def parse_best() -> None:
    rcsv = LOCAL_DIR / "results.csv"
    if not rcsv.exists():
        w("WARN results.csv missing locally")
        return
    rows = list(csv.DictReader(open(rcsv, encoding="utf-8")))
    if not rows:
        w("WARN results.csv empty")
        return
    best = max(rows, key=lambda r: float(r["metrics/mAP50(B)"]))
    w("FINAL rows=%d best_mAP50=%s @epoch=%s mAP50-95=%s P=%s R=%s last_epoch=%s" % (
        len(rows),
        best["metrics/mAP50(B)"], best["epoch"],
        best["metrics/mAP50-95(B)"], best["metrics/precision(B)"], best["metrics/recall(B)"],
        rows[-1]["epoch"],
    ))


w("monitor started; checking every 300s")
while True:
    time.sleep(300)
    c = client()
    try:
        code, out, err = run(c, CHECK, 90)
    except Exception as exc:  # noqa: BLE001
        w("check error: %s" % exc)
        continue
    finally:
        c.close()
    txt = (out or "") + (err or "")
    if "DONE" in txt:
        w("training process finished -> downloading key artifacts")
        break
    w("still running")

# 精准下载关键文件（跳过 weights/ 子目录）
c = client()
try:
    for fn in WANTED:
        ok = grab(c, "%s/%s" % (REMOTE_RUN, fn), str(LOCAL_DIR / fn))
        w("download %s -> %s" % (fn, "OK" if ok else "SKIP(missing)"))
finally:
    c.close()

parse_best()
(LOCAL_DIR / "_DONE.flag").write_text("done\n", encoding="utf-8")
w("monitor exiting")
