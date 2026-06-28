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

（待补充 - 由前端任务完成后生成代码报告，管理任务整理写入）