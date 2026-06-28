# 规范

约定俗成的做法、代码风格、命名规范、目录结构等。

## 代码风格

- 函数不超过 20 行（单一职责）
- 使用类型提示和 Docstring
- 错误处理必须防御性编程

## 工程方法

- 分层级约束体系：Hard Constraints > Design Intent > Allowed Variance

## Git 管理规范

### 推送规则
- 默认推送到 **master** 分支
- 所有文件正常推送，除了 `.gitignore` 中排除的目录

### 日志记录
- 每次 git 操作（commit、push）后必须写 log 到 `D:\Develop\CODE\AIWORK\Logs\git\`
- 日志文件名格式：`YYYY-MM-DD.md`
- 日志内容必须包含：Commit ID、变更文件、变更内容、统计信息、Push状态

### .gitignore 排除规则
```
# 项目目录
Projects/Comprehensive Training Documentation/

# Skills目录
Skills/
DO_NOT_USE_pr_skill/

# Office临时文件
~$*.pptx
~$*.docx
~$*.xlsx

# 根目录临时文件
antLogo.ico
azonix.zip
test_img/
slides_check/

# 依赖和工具
node_modules/
Tools/
```

## 视觉效果规范

### 粒子连线网络背景
- **组件位置**：必须在 `App.tsx` 最外层，所有页面共享同一个背景
- **层级保障**：背景 `zIndex: 0`，内容容器 `relative z-10`
- **配置参数**：`mouseDistance: 80`（鼠标光晕范围），`mouseGlowColor: rgba(224, 122, 95, 0.2)`（光晕透明度）
- **禁止**：不要在单个页面组件内单独使用背景

### 光晕效果
- 鼠标光晕大小：80px
- 光晕透明度：0.2

## 项目结构规范

### 目录布局
```
AIWORK/
├── Memory/              # 记忆文档（MEMORY.md、STANDARDS.md、CONSTRAINTS.md）
├── Projects/            # 项目目录
│   └── wechat-admin/    # 主项目
│       ├── backend-template/  # 后端
│       └── frontend/          # 前端
├── Logs/                # 日志
│   └── git/             # Git日志（日期命名）
└── Reports/             # 代码审查报告
```

### 记忆存储
- 记忆、规范、约束必须存储到 `D:\Develop\CODE\AIWORK\Memory\`
- 文件名：`MEMORY.md`、`STANDARDS.md`、`CONSTRAINTS.md`

## 开发职责

- 后端开发仅编写后端代码（API、数据库逻辑、业务逻辑等），禁止编写前端代码
- 前端开发由专门任务负责，后端开发不涉及前端实现
