# 规范

约定俗成的做法、代码风格、命名规范、目录结构等。

## 代码风格

- 函数不超过 20 行（单一职责）
- 使用类型提示和 Docstring
- 错误处理必须防御性编程

## 工程方法

- 分层级约束体系：Hard Constraints > Design Intent > Allowed Variance

---

## 前端规范（React + TypeScript）

### 目录结构

```
src/
├── assets/           # 静态资源
├── components/       # 公共组件
│   ├── ui/           # 原子级基础组件 (Button, Input, Card)
│   ├── forms/        # 表单相关组件
│   └── layout/       # 布局组件 (Header, Sidebar, Footer)
├── features/         # 功能模块（按业务域划分）
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   └── dashboard/
├── hooks/            # 全局通用 Hooks
├── lib/              # 第三方库配置 (axios, queryClient)
├── providers/         # React Context Providers
├── routes/           # 路由配置
├── stores/           # 状态管理 (Zustand/Redux)
├── styles/           # 全局样式、主题配置
├── types/            # 全局类型定义
├── utils/            # 纯工具函数（无 React 依赖）
└── App.tsx
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `UserProfile.tsx` |
| 工具文件 | camelCase | `formatDate.ts` |
| 类型文件 | `.types.ts` 后缀 | `user.types.ts` |
| 目录 | kebab-case | `user-profile/` |
| 变量 | camelCase | `userList`, `isLoggedIn` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 接口 | PascalCase + Props 后缀 | `UserProps` |

### 文件组织顺序

1. 导入语句（第三方 → 内部）
2. 接口定义
3. 类型定义
4. Hooks 定义
5. 组件定义
6. 导出语句

### 组件规范

**必须：**
- 使用函数组件 + Hooks
- 明确定义 Props 类型接口
- 组件文件包含 index.ts 统一导出
- 使用 `React.FC` 或直接 `const Component = () => {}` 方式

**禁止：**
- 使用 `any` 类型
- 使用 `var`
- 在组件内直接定义其他组件

### TypeScript 规范

- 启用 `strict: true`
- 禁止使用 `any`，使用 `unknown` 代替
- 使用 `interface` 定义对象结构，`type` 定义联合类型/别名
- 使用 `satisfies` 进行类型验证
- 泛型组件明确定义约束

### Hooks 规范

- Hook 必须以 `use` 开头
- 自定义 Hook 抽离到 `hooks/` 目录
- 每个 Hook 单一职责
- 使用 `useCallback` 和 `useMemo` 优化性能

### 错误处理

- 使用 `try-catch` 包裹异步操作
- 根据 HTTP 状态码区分错误类型（401、403、404、500 等）
- 提供用户友好的错误提示
- 禁止吞掉错误（empty catch）

### API 调用规范

- 使用 axios 或 fetch
- 统一拦截器处理（请求/响应）
- 请求参数类型化
- 响应数据验证

### 状态管理

- 优先使用 React Context（简单场景）
- 复杂状态使用 Zustand/Redux
- 避免 Prop Drilling（深度传递）

### 样式规范

- 使用 CSS Modules 或 Tailwind CSS
- 避免内联样式（除非动态样式）
- 嵌套层级不超过 3 级
