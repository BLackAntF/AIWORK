# AIWORK 工作区

AI 工作站文件组织结构

## 目录结构

```
AIWORK/
├── Tools/              # 工具程序
│   ├── agent-reach/    # 17平台工具集合
│   ├── uv-tools/       # UV 包管理工具
│   └── .agent-reach-venv/  # agent-reach 虚拟环境
│
├── Skills/             # AI 技能/提示库
│   ├── agents/         # Agent skills
│   └── claude/         # Claude skills
│
├── Config/             # 配置文件
│   └── .agent-reach/   # agent-reach 配置
│
├── Projects/           # 项目文件夹（预留）
│
├── Docs/               # 说明文档（预留）
│
├── Logs/               # 日志文件
│   └── git/            # Git 操作日志
│
├── Knowledge/          # 知识库（预留）
│
└── README.md           # 本文件
```

## 用途说明

| 文件夹 | 说明 |
|--------|------|
| `Tools/` | 可执行工具、CLI 程序 |
| `Skills/` | AI 技能定义、提示词模板 |
| `Config/` | 工具配置文件 |
| `Projects/` | 放置项目代码 |
| `Docs/` | 放置说明文档、使用指南 |
| `Logs/` | 操作日志、Git 日志 |
| `Knowledge/` | 知识库、参考资料 |

## 工具列表

### agent-reach
- 17平台工具集合
- 支持: 搜索、社交媒体、GitHub、网页阅读、视频字幕等
- 文档: `Tools/agent-reach/SKILL.md`

### uv-tools

- UV 包管理工具

## 更新日志

- 2026-06-07: 初始化目录结构
