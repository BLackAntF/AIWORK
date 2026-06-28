# 前端规范

前端设计规范、开发规范、组件设计等。

## 设计规范

### 配色方案（黑白灰 + 陶土红）
```css
:root {
  /* 背景色 */
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F8F9FA;
  --color-bg-tertiary: #F1F3F5;
  
  /* 文字色 */
  --color-text-primary: #1A1A2E;
  --color-text-secondary: #4A4A68;
  --color-text-muted: #6C757D;
  --color-text-inverse: #FFFFFF;
  
  /* 点缀色 - 陶土红 */
  --color-accent: #E07A5F;
  --color-accent-hover: #C96A52;
  --color-accent-light: #F5E6E2;
  
  /* 功能色 */
  --color-success: #6B8E23;
  --color-warning: #D4A574;
  --color-error: #CD5C5C;
  --color-info: #5D7B93;
  
  /* 边框 */
  --color-border: #DEE2E6;
  --color-border-light: #E9ECEF;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

### 配色方案 - 黑夜模式（黑金）
```css
[data-theme="dark"] {
  /* 背景色 */
  --color-bg-primary: #0A0A0A;
  --color-bg-secondary: #141414;
  --color-bg-tertiary: #1E1E1E;
  
  /* 文字色 */
  --color-text-primary: #F5F5F5;
  --color-text-secondary: #B8B8B8;
  --color-text-muted: #808080;
  --color-text-inverse: #0A0A0A;
  
  /* 点缀色 - 金色 */
  --color-accent: #D4AF37;
  --color-accent-hover: #F4CF57;
  --color-accent-light: #2A2518;
  
  /* 功能色 */
  --color-success: #8FBC8F;
  --color-warning: #DAA520;
  --color-error: #CD5C5C;
  --color-info: #7EB6CF;
  
  /* 边框 */
  --color-border: #2D2D2D;
  --color-border-light: #1E1E1E;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
}
```

### 字体规范（科技感）
```css
:root {
  /* 主字体 - 中文 */
  --font-family-cn: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
  
  /* 数字/代码/英文 */
  --font-family-mono: "JetBrains Mono", "Fira Code", "SF Mono", "Consolas", monospace;
  
  /* 字体大小 */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  
  /* 字体粗细 */
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* 行高 */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

## 视觉效果规范

### 粒子连线网络背景
- **组件位置**：必须在 `App.tsx` 最外层，所有页面共享同一个背景
- **层级保障**：背景 `zIndex: 0`，内容容器 `relative z-10`
- **配置参数**：`mouseDistance: 80`，`mouseGlowColor: rgba(224, 122, 95, 0.2)`
- **禁止**：不要在单个页面组件内单独使用背景

### 悬停发光效果
- 按钮：添加 `btn-glow` 类
- 卡片/容器：添加 `glow-border` 类
- 配合 CSS 变量 `--color-accent` 自动应用主题色

### 光晕效果
- 鼠标光晕大小：80px
- 光晕透明度：0.2

## 开发规范

### 项目架构
- **技术栈**: React + TypeScript + Vite
- **状态管理**: React Context API（AuthContext、ThemeContext）
- **HTTP 客户端**: axios（统一配置、拦截器）
- **路由**: 组件级 onNavigate 回调（后续可升级为 React Router）

### 目录结构
```
src/
├── api/              # API 层
│   ├── axios.ts      # axios 实例配置
│   ├── auth.ts       # 认证相关 API
│   ├── items.ts      # 业务 API
│   └── types.ts      # API 类型定义
├── components/       # 页面组件
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   └── ParticlesBackground.tsx
├── context/          # Context 状态
│   ├── AuthContext.tsx
│   └── ThemeContext.tsx
├── assets/           # 静态资源
│   ├── antLogo.ico
│   └── fonts/
├── App.tsx           # 应用入口
├── main.tsx          # React 挂载
├── App.css
└── index.css         # 全局样式（CSS 变量）
```

### Context 设计规范
- 每个 Context 必须导出 `Provider` 组件和自定义 hook（如 `useAuth`、`useTheme`）
- 自定义 hook 必须检查 context 是否为 `undefined`，未在 Provider 内使用时抛出明确错误
- 状态持久化（localStorage）必须有 try-catch 保护，防止 JSON.parse 失败
- 从 localStorage 读取的值必须进行类型验证，不能直接断言

### 错误处理规范
- axios 响应拦截器统一处理 HTTP 错误：401（清除 token + 跳转登录）、403、404、500、网络错误
- 组件级别通过 try-catch 捕获 API 调用错误，根据状态码设置不同提示
- 错误信息使用中文，面向最终用户
- 错误必须通过 `Promise.reject(error)` 继续抛出，供组件级处理

### 认证规范
- Token 存储在 localStorage，key 为 `token`
- 用户信息存储在 localStorage，key 为 `user`（JSON 字符串）
- 请求拦截器自动添加 `Authorization: Bearer <token>`
- 401 响应时清除本地存储并跳转登录页

### 主题切换规范
- 使用 `data-theme` 属性（`light` / `dark`）标记当前主题
- 主题状态持久化到 localStorage，key 为 `theme`
- 所有颜色通过 CSS 变量定义，支持主题自动切换
- 读取 localStorage 主题值时必须验证是否为合法值（'light' 或 'dark'）

### 性能与最佳实践
- 使用 `useCallback` 优化传递给子组件的回调函数
- 副作用必须正确清理（useEffect return）
- 异步请求使用 `AbortController` 防止内存泄漏
- 避免在多个页面组件中重复声明相同的状态逻辑

### 类型安全
- 所有组件 Props、API 响应、Context 类型必须完整定义
- 禁止使用 `any` 类型
- API 错误使用 `AxiosError<T>` 泛型指定响应数据类型

### 代码质量
- 函数保持单一职责，不超过 20 行
- 使用语义化的组件和变量命名
- UI 文本使用中文本地化
- 密码强度验证：长度≥8，包含大小写字母和数字