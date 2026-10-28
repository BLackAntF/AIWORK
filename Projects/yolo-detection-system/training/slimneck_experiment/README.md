# Slim-Neck 改进实验档案

> 目的：为 YOLO26n 番茄病害检测模型引入 Slim-Neck（GSConv + VoVGSCSP）轻量化颈部，
> 与基线 yolo26n_tomato_b64 做公平对比，所有改动与产出均留痕，供论文/毕设文档引用。

## 1. 实验设计

| 项目 | 基线 | 改进版 |
|------|------|--------|
| 模型结构 | 官方 `yolo26.yaml`（backbone + C3k2 head） | `yolo26n-SlimNeck.yaml`（backbone 不变，head 换 Slim-Neck） |
| 数据集 | `/root/ultralytics-YOLO26/datasets/tomato`（10 类番茄病害） | 同左（完全一致） |
| 训练参数 | epochs=200 / batch=64 / imgsz=640 / patience=999 / cache=True / seed=0 | 同左（完全一致） |
| 结果目录 | `runs/tomato/yolo26n_tomato_b64` | `runs/tomato/yolo26n_slimneck_b64` |

**控制变量说明**：除 head 结构外，数据集、超参、随机种子、硬件全部一致，确保指标差异可归因于 Slim-Neck。

## 2. 代码改动明细

基线环境：ultralytics **8.4.174**（pip 安装于 `/root/miniconda3/lib/python3.8/site-packages/ultralytics/`）

改动共 3 处，全部由 `patch_slimneck.py` 自动完成并留档：

| # | 目标文件 | 改动内容 |
|---|----------|----------|
| 1 | `ultralytics/nn/modules/Slim_Neck.py` | 新增文件：`GSConv` / `GSBottleneck` / `GSBottleneckC` / `VoVGSCSP` |
| 2 | `ultralytics/nn/tasks.py` | 新增 import；`GSConv`、`VoVGSCSP` 加入 `base_modules`；`VoVGSCSP` 加入 `repeat_modules` |
| 3 | `patch/yolo26n-SlimNeck.yaml`（独立文件，不改官方 cfg） | 基于官方 yolo26.yaml，仅替换 head 的 4 处 C3k2 → VoVGSCSP、2 处 Conv → GSConv |

**关键差异（与网上旧版教程）**：ultralytics 8.4.x 的 `parse_model` 已重构，不再使用
`if m in {SPPF, ...}` 分支，而是通过 `base_modules` / `repeat_modules` 两个 frozenset 注册。
本补丁按 8.4.174 实际源码适配，未照搬旧教程（旧教程直接照抄会失败）。

### head 改动逐层对照

| 层索引 | 官方 yolo26 | Slim-Neck 版 |
|--------|-------------|--------------|
| 13 | `C3k2 [512, True]` | `VoVGSCSP [512]` |
| 16 | `C3k2 [256, True]` | `VoVGSCSP [256]` |
| 17 | `Conv [256, 3, 2]` | `GSConv [256, 3, 2]` |
| 19 | `C3k2 [512, True]` | `VoVGSCSP [512]` |
| 20 | `Conv [512, 3, 2]` | `GSConv [512, 3, 2]` |
| 22 | `C3k2 [1024, True, 0.5, True]` | `VoVGSCSP [1024]` |

## 3. 数据来源清单（写文档时引用这些文件）

| 文件 | 内容 |
|------|------|
| `records/tasks.py.diff` | 对 ultralytics 源码的完整 unified diff（唯一权威改动证据） |
| `records/build_summary.txt` | 基线 vs Slim-Neck 参数量 / GFLOPs 实测值 |
| `records/patch.log` | 补丁执行全过程日志（含版本、路径、时间） |
| `records/env_snapshot.txt` | GPU / ultralytics 版本 / Python / 数据集图片数 |
| `records/data.yaml` | 数据集配置副本（10 类中文类别名） |
| `records/yolo26_official.yaml` | 官方原结构快照（对比基线） |
| `records/train_args.json` | 本次训练全部超参数 |
| `runs/tomato/yolo26n_slimneck_b64/results.csv` | 逐轮指标（mAP50 / mAP50-95 / P / R / loss） |
| `runs/tomato/yolo26n_slimneck_b64/` | 权重、曲线图、混淆矩阵、PR 曲线 |
| `runs/tomato/yolo26n_tomato_b64/results.csv` | 基线逐轮指标（已有） |

## 4. 结果

> 训练完成后填写

- 参数量 / GFLOPs：见 `records/build_summary.txt`
- 最佳轮次与指标：待填
- 与基线对比：待填

## 5. 复现步骤

```bash
cd /root/ultralytics-YOLO26/slimneck_experiment/patch
python patch_slimneck.py      # 注入 + 生成 diff + 结构对比
python train_slimneck.py      # 训练 200 轮
```
