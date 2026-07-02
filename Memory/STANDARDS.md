# 规范

约定俗成的做法、代码风格、命名规范、目录结构、设计标准等。

> **前端规范**: 见 `frontend-standards.md`
> **后端规范**: 见 `backend-standards.md`

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

## 项目结构规范

### 目录布局
```
AIWORK/
├── Memory/              # 记忆文档
│   ├── MEMORY.md        # 记忆/背景
│   ├── STANDARDS.md     # 通用规范
│   ├── CONSTRAINTS.md   # 约束
│   ├── frontend-standards.md  # 前端规范
│   └── backend-standards.md   # 后端规范
├── Projects/            # 项目目录
│   └── wechat-admin/    # 主项目
│       ├── backend-template/  # 后端
│       └── frontend/          # 前端
├── Logs/                # 日志
│   └── git/             # Git日志（日期命名）
└── Reports/             # 代码审查报告
```

## 开发职责

- 后端开发仅编写后端代码（API、数据库逻辑、业务逻辑等），禁止编写前端代码
- 前端开发由专门任务负责，后端开发不涉及前端实现

## 任务协作流程

### 角色分工

| 角色 | 职责 | 禁止事项 |
|------|------|----------|
| 管理 Task | 检查项目、发现问题、编写任务文档、生成开发提示词、代码审查、更新规范 | **禁止直接修改代码** |
| 前端开发 Task | 根据提示词修改前端代码、自测验证 | 禁止修改后端代码 |
| 后端开发 Task | 根据提示词修改后端代码、自测验证 | 禁止修改前端代码 |

### 工作流

```
管理 Task 检查项目 → 发现问题 → 编写任务文档（含提示词）
                                              ↓
                          前端开发 Task ←────┴────→ 后端开发 Task
                                ↓                        ↓
                          修复代码                    修复代码
                          自测验证                    自测验证
                                              ↓
                                    管理 Task 代码审查
                                              ↓
                                    验收通过 / 要求修复
                                              ↓
                                    更新规范文件（如需要）
```

### 任务文档规范

- 文档存放位置：项目的 `docs/` 目录下
- 命名格式：`Bug修复任务-MMDD.md` 或 `功能开发任务-MMDD.md`
- 文档必须包含：
  1. 概述（优先级、工时预估）
  2. 每个 Bug/功能的详细描述
  3. 影响范围
  4. 修复/开发内容（含文件路径）
  5. 验收标准
  6. **前端开发提示词**（可直接复制使用）
  7. **后端开发提示词**（可直接复制使用）

### 任务指令协议（关键词触发）

用户通过简短关键词指令启动开发 task，无需手动复制提示词。

**指令格式**：`执行<前端|后端>任务 <MMDD>`

**示例**：
- `执行后端任务 0702` → 后端开发 task 自动执行 0702 的任务
- `执行前端任务 0702` → 前端开发 task 自动执行 0702 的任务

**开发 Task 收到指令后的执行流程**：
1. 读取 `Memory/STANDARDS.md` 了解任务协作流程
2. 前往 `Projects/<对应项目>/docs/` 目录
3. 查找文件名匹配 `*任务-<MMDD>.md` 的文档
4. 读取文档，找到 `<前端|后端>开发提示词` 章节
5. 复制提示词内容，按提示词要求执行开发/修复工作
6. 完成后自测验证，确保满足文档中的验收标准

**注意事项**：
- 如果找到多个匹配文档，向用户确认具体是哪一个
- 如果文档不存在，告知用户未找到对应日期的任务文档
- 执行前必须先读 `Memory/STANDARDS.md` 和 `Memory/CONSTRAINTS.md` 了解约束

### 产品决策记录

- 重要产品决策（如"网页端不做视频检测"）必须在任务文档中记录
- 决策内容需同步到项目记忆中，避免后续重复讨论

## Skill 使用规范

### 前端代码编写
- **使用 Skill**: `frontend-design`
- **用途**: 创建前端界面、web组件、页面、应用
- **输出**: React 组件、CSS 样式、页面结构
- **完成后**: 生成代码报告

### 后端代码编写
- **使用 Skill**: `backend-patterns`
- **用途**: 后端架构模式、API设计、数据库优化、Node.js/Express/Next.js API路由
- **输出**: API 路由、数据库操作、认证中间件、业务逻辑
- **完成后**: 生成代码报告

### 代码报告处理
- 前端/后端任务完成后生成代码报告
- 管理任务分析代码报告，提炼规范要点
- 规范要点整理写入对应的规范文件（frontend-standards.md 或 backend-standards.md）

### 代码审查
- **使用 Skill**: `TRAE-code-review`
- **时机**: 代码编写完成后
- **输出**: 代码审查报告，存储到 `Reports/` 目录
- **后续**: 根据审查报告进行修复，并更新规范