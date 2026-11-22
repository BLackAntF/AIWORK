#!/bin/bash
# 接力脚本：等对照组 D 训练结束后，自动启动 2x2 第 3 格（官方结构 + yolo26s 教师）
# bracket 技巧避免 pgrep 匹配到自身
PATCH=/root/ultralytics-YOLO26/slimneck_experiment/patch
cd "$PATCH" || exit 1

echo "[relay] start $(date '+%F %T'), waiting for D to finish..."
while pgrep -f 'train_ctrl_distill_strateg[y].py' >/dev/null; do
    sleep 60
done

echo "[relay] D finished at $(date '+%F %T'), launching cell E"
sleep 20
nohup /root/miniconda3/bin/python train_ctrl_official_teacher26s.py \
    > train_ctrl_official_teacher26s.log 2>&1 < /dev/null &
echo "[relay] cell E launched, pid=$!"
