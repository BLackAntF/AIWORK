# TRAE Work 任务指南

本文档用于 TRAE Work 四个任务（管理、前端、后端、审查）的启动参考。

---

## 项目信息

- **工作目录**: `D:\Develop\CODE\AIWORK\`
- **项目位置**: `Projects/wechat-admin/`
- **前端位置**: `Projects/wechat-admin/frontend/`
- **后端位置**: `Projects/wechat-admin/backend-template/`
- **GitHub**: `git@github.com:BLackAntF/AIWORK.git`

---

## 一、管理任务

### 启动时读取的文件
```
Memory/MEMORY.md          # 项目背景
Memory/STANDARDS.md       # 通用规范
Memory/CONSTRAINTS.md     # 约束条件
```

### 职责
1. 协调前端、后端、审查任务
2. 收集代码报告，提炼规范要点
3. 更新规范文件（STANDARDS.md、frontend-standards.md、backend-standards.md）
4. Git 管理（commit、push、写日志）

### 工作流程
```
1. 读取规范文件
2. 协调其他任务执行
3. 收集代码报告和审查报告
4. 分析报告，提炼规范要点
5. 更新对应规范文件
6. Git commit + push
7. 写日志到 Logs/git/YYYY-MM-DD.md
```

### Git 日志格式
```
## Commit N: <提交信息>

**Commit ID**: <hash>

**变更文件**:
- 文件列表

**变更内容**:
1. 变更描述

**统计**: N files changed, X insertions(+), Y deletions(-)

**Push**: ✅ 已推送到 GitHub
```

---

## 二、前端任务

### 启动时读取的文件
```
Memory/MEMORY.md              # 项目背景
Memory/frontend-standards.md  # 前端设计规范（配色、字体、视觉效果）
Memory/CONSTRAINTS.md         # 约束条件
```

### 使用 Skill
```
frontend-design
```

### 职责
1. 创建前端界面、组件、样式
2. 遵循配色规范（黑白灰 + 陶土红 / 黑金）
3. 遵循视觉效果规范（粒子背景、光晕效果）
4. 完成后生成代码报告

### 工作流程
```
1. 读取规范文件
2. 使用 frontend-design skill 编写代码
3. 确保视觉效果符合规范：
   - 粒子背景在 App.tsx 最外层
   - 光晕大小 80px
   - 配色使用 CSS 变量
4. 完成后生成代码报告
5. 交给管理任务
```

### 视觉效果要点
- **粒子背景**: 必须在 `App.tsx` 最外层，所有页面共享
- **层级**: 背景 `zIndex: 0`，内容 `relative z-10`
- **光晕**: `mouseDistance: 80`，`mouseGlowColor: rgba(224, 122, 95, 0.2)`
- **配色**: 白天用陶土红点缀，夜晚用金色点缀

---

## 三、后端任务

### 启动时读取的文件
```
Memory/MEMORY.md              # 项目背景
Memory/backend-standards.md   # 后端规范（待补充）
Memory/CONSTRAINTS.md         # 约束条件（安全红线）
```

### 使用 Skill
```
backend-patterns
```

### 职责
1. 设计 API 路由、数据库操作
2. 实现认证机制、业务逻辑
3. 遵循安全红线（禁止硬编码密钥、参数化查询）
4. 完成后生成代码报告

### 工作流程
```
1. 读取规范文件
2. 使用 backend-patterns skill 编写代码
3. 遵循安全约束：
   - 禁止硬编码密钥、API Key、密码
   - 所有数据库查询必须参数化
   - 用户输入必须验证
   - 禁止使用 eval、字符串拼接 SQL
4. 完成后生成代码报告
5. 交给管理任务
```

### 安全红线
- ❌ 禁止硬编码密钥（使用 `.env`）
- ✅ 所有数据库查询参数化
- ✅ 用户输入必须验证
- ❌ 禁止 `eval`、字符串拼接 SQL

---

## 四、审查任务

### 启动时读取的文件
```
Memory/CONSTRAINTS.md         # 约束条件
Reports/                      # 查看历史审查报告
```

### 使用 Skill
```
TRAE-code-review
```

### 职责
1. 审查前端/后端代码
2. 检查安全漏洞、代码质量
3. 生成审查报告到 `Reports/` 目录
4. 提出修复建议

### 工作流程
```
1. 读取约束条件
2. 使用 TRAE-code-review skill 审查代码
3. 生成审查报告：
   - 文件名：code-review-report-YYYY-MM-DD.md
   - 存储位置：Reports/
4. 提出修复建议
5. 交给管理任务
```

### 审查要点
- 🔐 安全漏洞（密钥硬编码、SQL注入）
- 📝 代码质量（命名规范、错误处理）
- ⚡ 性能问题（查询优化、缓存）
- 🎨 前端规范（配色、视觉效果）

---

## 任务协作流程

```
┌─────────────┐
│   管理任务   │ ← 协调中心
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌─────────────┐                       ┌─────────────┐
│   前端任务   │                       │   后端任务   │
│ frontend-   │                       │ backend-    │
│   design    │                       │  patterns   │
└──────┬──────┘                       └──────┬──────┘
       │                                     │
       │ 代码报告                             │ 代码报告
       │                                     │
       ▼                                     ▼
┌─────────────┐                       ┌─────────────┐
│   审查任务   │ ←─────────────────────│              │
│ TRAE-code-  │                       │              │
│   review    │                       │              │
└──────┬──────┘                       └──────┬──────┘
       │                                     │
       │ 审查报告                             │
       │                                     │
       ▼                                     ▼
┌─────────────┐
│   管理任务   │
│ 更新规范     │
│ Git 管理     │
│ 写日志       │
└─────────────┘
```

---

## 快速启动提示词

### 管理任务
```
读取 Memory/MEMORY.md、Memory/STANDARDS.md、Memory/CONSTRAINTS.md。
工作目录：D:\Develop\CODE\AIWORK\。
协调前端、后端、审查任务，收集代码报告和审查报告，更新规范文件，Git commit + push，写日志到 Logs/git/。
```

### 前端任务
```
读取 Memory/MEMORY.md、Memory/frontend-standards.md、Memory/CONSTRAINTS.md。
使用 frontend-design skill 编写前端代码。
项目位置：Projects/wechat-admin/frontend/。
遵循配色和视觉效果规范，完成后生成代码报告。
```

### 后端任务
```
读取 Memory/MEMORY.md、Memory/backend-standards.md、Memory/CONSTRAINTS.md。
使用 backend-patterns skill 编写后端代码。
项目位置：Projects/wechat-admin/backend-template/。
遵循安全红线，完成后生成代码报告。
```

### 审查任务
```
读取 Memory/CONSTRAINTS.md。
使用 TRAE-code-review skill 审查代码。
审查报告存储到 Reports/code-review-report-YYYY-MM-DD.md。
提出修复建议，交给管理任务。
```