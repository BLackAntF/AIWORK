# 记忆

存储历史信息、背景、偏好、资源位置等。

## 目录规则

- **工作目录**: `D:\Develop\CODE\AIWORK\`
- **项目目录**: `D:\Develop\CODE\AIWORK\Projects\` (如果是项目)
- **记忆存储**: `D:\Develop\CODE\AIWORK\Memory\`
- **日志目录**: `D:\Develop\CODE\AIWORK\Logs\`
- **Git日志**: `D:\Develop\CODE\AIWORK\Logs\git\`

## 项目背景

### Redis 启动
- 启动命令: `D:\Develop\CODE\itheima\nginx-1.20.2\RedisOpen.bat`

### 项目信息
- **项目名称**: BLackAntProject
- **前端项目**: `D:\Develop\CODE\AIWORK\Projects\wechat-admin\frontend`

### Logo 资源
- **Logo 文件**: `Projects/wechat-admin/frontend/src/assets/antLogo.ico`
- **使用规范**: 作为网站 Favicon 和登录页Logo使用

### 字体资源
- **特殊字体**: `Projects/wechat-admin/frontend/src/assets/fonts/azonix.zip`
- **使用规范**: 用于特殊Logo位置和品牌标识文字

### 资源目录结构
```
assets/
├── antLogo.ico          # Logo图标
└── fonts/               # 字体文件目录
    └── azonix.zip       # 特殊Logo字体
```

## 历史变更记录

### 2026-06-28
- 添加粒子连线网络背景效果
- 更新 .gitignore 排除规则
- 清理误提交的临时文件和Skills目录

### 2026-10-29（yolo-detection-system）
- Slim-Neck 对比实验：head 换 GSConv/VoVGSCSP，参数 −4.49%、GFLOPs −9.68%；训练暂停于 epoch 46/200，产物落盘 AutoDL，续训用 `training/slimneck_experiment/patch/resume_slimneck.py`
- 新增 4 项功能（后端测试 23/23 通过）：
  - 低置信度兜底（阈值 0.5，SystemConfig 可改）+ 自动收录样本池（`sample_pool.auto_created`）
  - 结果分享：只读链接 + 二维码，免登录，7 天有效，隐私脱敏（新表 `share_links`）
  - H5 天气联动：Open-Meteo 代理 + 施药适宜性判断，30 分钟缓存
  - 病害防治结构化：`disease_profiles` 新增 dosage/safety_interval/biological_control，PDF 与问答引用，管理端可写
- 配套补全：样本池管理页「自动」标识、`low_confidence_threshold` 默认配置入库
- 交付文档：功能变更说明-1029、Slim-Neck实验溯源、后续工作规划-1028、功能清单与操作手册更新、Git 日志 2026-10-29
- 未做：病害严重度分级（需新算法）、地块/作物病程跟踪（需数据模型重构）、视频实时检测（与 Web 不做视频约束冲突）
