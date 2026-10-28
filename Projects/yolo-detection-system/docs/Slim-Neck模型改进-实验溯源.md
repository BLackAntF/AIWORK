# Slim-Neck 模型改进 —— 实验溯源与数据索引

> 实验编号：EXP-SLIMNECK-20261028
> 启动时间：2026-10-28 23:51（Asia/Hong_Kong）
> 状态：训练中（200 epochs，预计约 4.8 小时）
> 用途：论文/毕设/项目文档的唯一数据来源。本文所有数字均来自实测记录文件，未做估算的地方会明确标注。

---

## 1. 实验目的

在现有 YOLO26n 番茄病害检测模型上引入 **Slim-Neck**（GSConv + VoVGSCSP 轻量化颈部），验证在**不损失检测精度**的前提下降低参数量与计算量，并与基线做严格控制变量的对比。

**对照关系**：

| 项目 | 基线（对照组） | 改进版（实验组） |
|------|---------------|-----------------|
| 模型结构 | 官方 `yolo26.yaml` | `yolo26n-SlimNeck.yaml` |
| 数据集 | 番茄 10 类病害（同一份） | 同左 |
| epochs / batch / imgsz | 200 / 64 / 640 | 同左 |
| patience | 999（跑满） | 同左 |
| cache / workers / seed | True / 16 / 0 | 同左 |
| 结果目录 | `runs/tomato/yolo26n_tomato_b64` | `runs/tomato/yolo26n_slimneck_b64` |

> 控制变量说明：除 head 结构外，其余条件完全一致，指标差异可归因于 Slim-Neck 本身。

---

## 2. 结论摘要（结构层面，已实测）

| 指标 | 基线 yolo26n | Slim-Neck 版 | 变化 |
|------|-------------|-------------|------|
| 参数量（nc=80） | 2,572,280（2.572M） | 2,456,696（2.457M） | **−115,584（−4.49%）** |
| GFLOPs @640 | 6.2 | 5.6 | **−0.6（−9.68%）** |
| 层数 | 260 | 276 | +16 |
| 训练时参数量（nc=10） | — | 2,392,116 | — |
| 训练时 GFLOPs（nc=10） | — | 5.3 | — |

数据来源：`training/slimneck_experiment/patch/records/build_summary.txt`（由 `patch_slimneck.py` 实际构建两个模型后计算得出）。

**精度结论待训练完成后补充**（mAP50 / mAP50-95 / Precision / Recall / 收敛轮次 / 单轮耗时）。

---

## 3. 环境快照

数据来源：`training/slimneck_experiment/patch/records/env_snapshot.txt`

| 项 | 值 |
|----|----|
| 平台 | AutoDL 云实例（RTX 4090，24G 显存） |
| Python | 3.8 |
| ultralytics | **8.4.174**（pip 安装，非源码仓库） |
| ultralytics 路径 | `/root/miniconda3/lib/python3.8/site-packages/ultralytics/` |
| 数据集 | `/root/ultralytics-YOLO26/datasets/tomato/data.yaml`（10 类番茄病害） |
| 训练输出 | `/root/ultralytics-YOLO26/runs/tomato/yolo26n_slimneck_b64/` |

---

## 4. 代码改动明细

### 4.1 改动总览（共 3 处）

| # | 文件 | 改动 |
|---|------|------|
| 1 | `ultralytics/nn/modules/Slim_Neck.py` | **新增**：GSConv / GSBottleneck / GSBottleneckC / VoVGSCSP |
| 2 | `ultralytics/nn/tasks.py` | 新增 1 行 import；`GSConv`、`VoVGSCSP` 加入 `base_modules`；`VoVGSCSP` 加入 `repeat_modules` |
| 3 | `patch/yolo26n-SlimNeck.yaml` | 独立模型配置文件（不覆盖官方 cfg），仅改 head |

**官方 ultralytics 源码仅被插入 4 行 + 1 行 import，未删除或改写任何原有逻辑。**

### 4.2 完整 diff（权威证据）

数据来源：`records/tasks.py.diff`

```diff
--- ultralytics/nn/tasks.py.orig
+++ ultralytics/nn/tasks.py.slimneck
@@ -2027,6 +2027,8 @@
     return model, ckpt


+from ultralytics.nn.modules.Slim_Neck import GSConv, GSBottleneck, GSBottleneckC, VoVGSCSP
+
 def parse_model(d, ch, verbose=True):
     """Parse a YOLO model.yaml dictionary into a PyTorch model.

@@ -2069,6 +2071,8 @@
     layers, save, c2 = [], [], ch[-1]  # layers, savelist, ch out
     base_modules = frozenset(
         {
+            GSConv,
+            VoVGSCSP,
             Classify,
             Conv,
             ConvTranspose,
@@ -2107,6 +2111,7 @@
     )
     repeat_modules = frozenset(  # modules with 'repeat' arguments
         {
+            VoVGSCSP,
             BottleneckCSP,
             C1,
             C2,
```

### 4.3 head 逐层对照

| 层索引 | 官方 yolo26n | Slim-Neck 版 | 说明 |
|--------|-------------|-------------|------|
| 13 | `C3k2 [512, True]` | `VoVGSCSP [512]` | 上采样融合 P4 |
| 16 | `C3k2 [256, True]` | `VoVGSCSP [256]` | 上采样融合 P3 |
| 17 | `Conv [256, 3, 2]` | `GSConv [256, 3, 2]` | 下采样 |
| 19 | `C3k2 [512, True]` | `VoVGSCSP [512]` | 下采样融合 P4 |
| 20 | `Conv [512, 3, 2]` | `GSConv [512, 3, 2]` | 下采样 |
| 22 | `C3k2 [1024, True, 0.5, True]` | `VoVGSCSP [1024]` | 下采样融合 P5 |

> `C3k2` 的 `c3k` 参数在 `VoVGSCSP` 中无对应项，按 Slim-Neck 原实现使用默认 `shortcut=True` / `e=0.5`。
> backbone（层 0–10）与官方逐字一致，未做任何改动。

### 4.4 与网上教程的关键差异（重要，写论文时可作为工程贡献点）

多数公开教程（含本篇参考的 51CTO 文章）基于 **ultralytics 8.1/8.2 及更早版本**，其 `parse_model` 使用：

```python
if m in {Conv, ..., SPPF, ...}:   # 旧版分支写法
```

而本项目训练机为 **8.4.174**，`parse_model` 已重构为两个 `frozenset`：

```python
base_modules = frozenset({...})
repeat_modules = frozenset({...})
```

因此直接照搬旧教程的代码补丁**会失败**。本次按 8.4.174 实际源码重新适配，改动点见 4.2 的 diff。

另外两个实际踩到的坑（已在脚本中处理）：

1. **文件名必须含尺度字母**：`YOLO("yolo26-SlimNeck.yaml")` 会因 `guess_model_scale()` 匹配不到 `n/s/m/l/x` 而报错，故命名为 `yolo26n-SlimNeck.yaml`。
2. **AMP 校验会下载 `yolo26n.pt`**：GitHub 下载约 20KB/s 极慢，已改为复用实例上已有的 `/root/ultralytics-YOLO26/yolo26n.pt`。

---

## 5. 训练配置（与基线逐项一致）

数据来源：`records/train_args.json`

```json
{
  "data": "/root/ultralytics-YOLO26/datasets/tomato/data.yaml",
  "epochs": 200,
  "patience": 999,
  "batch": 64,
  "imgsz": 640,
  "cache": true,
  "device": "0",
  "workers": 16,
  "seed": 0,
  "optimizer": "auto",
  "project": "/root/ultralytics-YOLO26/runs/tomato",
  "name": "yolo26n_slimneck_b64",
  "exist_ok": true
}
```

`patience=999` 的目的：禁用早停、跑满 200 轮，与基线一致，便于逐轮曲线对比（注：基线当时因早停问题最终也跑满 200 轮）。

---

## 6. 数据来源索引（写文档时按需引用）

### 6.1 本地路径（项目仓库内）

| 文件 | 内容 | 可信度 |
|------|------|--------|
| `training/slimneck_experiment/README.md` | 实验档案总览 | 说明性 |
| `training/slimneck_experiment/patch/yolo26n-SlimNeck.yaml` | 改进版结构（逐行标注 6 处改动） | 权威 |
| `training/slimneck_experiment/patch/Slim_Neck.py` | 模块实现源码 | 权威 |
| `training/slimneck_experiment/patch/patch_slimneck.py` | 自动补丁脚本（幂等、自动备份、生成 diff） | 权威 |
| `training/slimneck_experiment/patch/train_slimneck.py` | 训练脚本（自动落盘环境/配置快照） | 权威 |
| `training/slimneck_experiment/patch/records/tasks.py.diff` | ultralytics 源码改动 diff | **权威（唯一证据）** |
| `training/slimneck_experiment/patch/records/build_summary.txt` | 参数量/GFLOPs 实测 | **权威** |
| `training/slimneck_experiment/patch/records/env_snapshot.txt` | 硬件/软件/数据集快照 | **权威** |
| `training/slimneck_experiment/patch/records/train_args.json` | 训练超参 | **权威** |
| `training/slimneck_experiment/patch/records/data.yaml` | 数据集配置副本 | **权威** |
| `training/slimneck_experiment/patch/records/yolo26_official.yaml` | 官方原结构快照 | **权威** |
| `training/slimneck_experiment/tools/adl_remote.py` | 远端执行/上传/下载工具 | 辅助 |

### 6.2 远端路径（AutoDL，训练结束后拉回本地）

| 文件 | 内容 |
|------|------|
| `runs/tomato/yolo26n_slimneck_b64/results.csv` | 逐轮指标（核心数据） |
| `runs/tomato/yolo26n_slimneck_b64/weights/best.pt` | 最佳权重 |
| `runs/tomato/yolo26n_slimneck_b64/weights/last.pt` | 最后一轮权重 |
| `runs/tomato/yolo26n_slimneck_b64/results.png` | 训练曲线汇总图 |
| `runs/tomato/yolo26n_slimneck_b64/confusion_matrix.png` | 混淆矩阵 |
| `runs/tomato/yolo26n_slimneck_b64/BoxPR_curve.png` 等 | PR / F1 / P / R 曲线 |
| `runs/tomato/yolo26n_slimneck_b64/args.yaml` | ultralytics 落盘的实际参数 |
| `runs/tomato/yolo26n_slimneck_b64/train.log` | 完整训练日志 |
| `runs/tomato/yolo26n_tomato_b64/` | 基线同结构产物（已有） |

### 6.3 追溯方式（从数字反查来源）

| 想引用的数字 | 去哪里查 |
|-------------|---------|
| 参数量 / GFLOPs | `records/build_summary.txt` |
| 环境版本 | `records/env_snapshot.txt`、`records/patch.log` |
| 改了哪几行源码 | `records/tasks.py.diff` |
| 训练超参 | `records/train_args.json`、远端 `args.yaml` |
| 每轮 mAP/P/R/loss | 远端 `results.csv` |
| 训练过程异常 | 远端 `train.log` |

---

## 7. 复现步骤

```bash
# 远端（AutoDL）
cd /root/ultralytics-YOLO26/slimneck_experiment/patch
python patch_slimneck.py    # 注入模块 + 注册 + 生成 diff + 结构对比
python train_slimneck.py    # 训练 200 轮
```

`patch_slimneck.py` 是**幂等**的：重复执行不会重复插入；首次修改前会自动备份 `tasks.py.bak_slimneck`。

---

## 8. 时间线

| 时间 | 事件 |
|------|------|
| 2026-10-28 23:4x | 探查远端环境：ultralytics 8.4.174、RTX 4090、数据集确认 |
| 2026-10-28 23:4x | 发现 8.4.x 注册机制与旧教程不同，重写补丁脚本 |
| 2026-10-28 23:5x | 补丁执行成功，结构验证 2.457M / 5.6 GFLOPs |
| 2026-10-28 23:51 | 训练启动（Epoch 1，单轮约 87s） |
| 待定 | 200 轮完成，拉回产物、写对比分析 |

---

## 9. 待补充项

- [ ] 训练完成后填写第 2 节的精度指标（与基线对比）
- [ ] 拉回 `results.csv` 与曲线图到 `training/slimneck_experiment/runs/yolo26n_slimneck_b64/`
- [ ] 判断是否替换线上模型（决策依据：精度不降或降幅 <0.3% 且速度有收益）
- [ ] 若替换，记录后端模型替换过程（对应 `backend` 中的模型路径配置）
