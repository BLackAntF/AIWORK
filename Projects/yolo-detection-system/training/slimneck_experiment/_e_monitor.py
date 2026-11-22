# -*- coding: utf-8 -*-
"""E 训练后台监护：探测结束 -> 下载产物 -> 解析最终 best。

密码通过环境变量 ADL_HOST/ADL_PORT/ADL_USER/ADL_PWD 传入，不写死。
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(
    0,
    r"d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\training\slimneck_experiment\tools",
)
from adl_remote import client, run  # noqa: E402

REMOTE_RUN = "/root/ultralytics-YOLO26/runs/tomato/yolo26n_ctrl_official_teacher26s"
LOCAL_DIR = Path(
    r"d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\training\slimneck_experiment\ctrl_output_E"
)
CHECK = "if pgrep -f 'train_ctrl_official_teacher26[s].py' >/dev/null; then echo RUNNING; else echo DONE; fi"
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
    b = max(rows, key=lambda r: float(r["metrics/mAP50(B)"]))
    w("FINAL_E rows=%d mAP50=%s @ep=%s mAP50-95=%s P=%s R=%s last_ep=%s" % (
        len(rows),
        b["metrics/mAP50(B)"], b["epoch"],
        b["metrics/mAP50-95(B)"], b["metrics/precision(B)"], b["metrics/recall(B)"],
        rows[-1]["epoch"],
    ))


w("E monitor started; checking every 300s")
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
    if "DONE" in ((out or "") + (err or "")):
        w("E training finished -> downloading")
        break
    w("E still running")

c = client()
try:
    for fn in WANTED:
        ok = grab(c, "%s/%s" % (REMOTE_RUN, fn), str(LOCAL_DIR / fn))
        w("download %s -> %s" % (fn, "OK" if ok else "SKIP"))
finally:
    c.close()

parse_best()
(LOCAL_DIR / "_DONE.flag").write_text("done\n", encoding="utf-8")
w("E monitor exiting")
