# 记忆

存储历史信息、背景、偏好等。

## 目录规则

- **工作目录**: `D:\Develop\CODE\AIWORK\`
- **项目目录**: `D:\Develop\CODE\AIWORK\Projects\` (如果是项目)
- **记忆存储**: `D:\Develop\CODE\AIWORK\Memory\`
- **日志目录**: `D:\Develop\CODE\AIWORK\Logs\`
- **Git日志**: `D:\Develop\CODE\AIWORK\Logs\git\`

## Git 操作规则

- **每次 git 操作后**，必须写 log 到 `D:\Develop\CODE\AIWORK\Logs\git\`

## 项目背景

### Redis 启动
- 启动命令: `D:\Develop\CODE\itheima\nginx-1.20.2\RedisOpen.bat`

### 项目信息
- **项目名称**: BLackAnt
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

### 前端配色方案（黑白灰 + 陶土红）

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

### 前端配色方案 - 黑夜模式（黑金）

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

### 前端字体规范（科技感）

```css
/* 字体家族 */
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

/* 使用方式 */
/* 中文内容 */
.text-cn {
  font-family: var(--font-family-cn);
}

/* 数字/代码/英文内容 */
.text-mono {
  font-family: var(--font-family-mono);
  font-feature-settings: 'tnum' on, 'lnum' on; /* 等宽数字 */
}

/* 标题 - 科技感用中等偏细 */
h1, h2, h3 {
  font-family: var(--font-family-cn);
  font-weight: var(--font-weight-medium);
  letter-spacing: 0.02em;
}

/* 数据展示 - 使用等宽字体 */
.data-display,
.stat-number,
.code-block {
  font-family: var(--font-family-mono);
}
```

### 视觉效果规范 - 悬停发光边框

```css
/* 悬停发光边框效果 */
.glow-border {
  position: relative;
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
}

.glow-border::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(
    135deg,
    var(--color-accent) 0%,
    transparent 50%,
    var(--color-accent) 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.glow-border:hover {
  border-color: var(--color-accent);
  box-shadow: 
    0 0 10px rgba(224, 122, 95, 0.3),
    0 0 20px rgba(224, 122, 95, 0.2),
    0 0 30px rgba(224, 122, 95, 0.1);
}

.glow-border:hover::before {
  opacity: 1;
}

/* 按钮专用发光效果 */
.btn-glow {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.btn-glow::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(224, 122, 95, 0.4) 0%,
    transparent 50%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.btn-glow:hover {
  box-shadow: 
    0 0 15px rgba(224, 122, 95, 0.4),
    0 0 30px rgba(224, 122, 95, 0.2);
  transform: translateY(-1px);
}

.btn-glow:hover::after {
  opacity: 1;
}
```

**使用方式**：
- 按钮：添加 `btn-glow` 类
- 卡片/容器：添加 `glow-border` 类
- 配合 CSS 变量 `--color-accent` 自动应用主题色

### 视觉效果规范 - 粒子连线网络背景

```tsx
// ParticlesBackground.tsx
// 粒子连线网络背景组件 - 确保在最底层不影响其他组件

import { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
}

export function ParticlesBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const particlesRef = useRef<Particle[]>([]);
  const animationRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 配置
    const config = {
      particleCount: 80,
      connectionDistance: 150,
      mouseDistance: 80, // 鼠标光晕范围
      particleColor: '#E07A5F',
      mouseGlowColor: 'rgba(224, 122, 95, 0.2)', // 光晕透明度
    };

    // 初始化画布 - 全屏覆盖
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // 初始化粒子
    const initParticles = () => {
      particlesRef.current = [];
      for (let i = 0; i < config.particleCount; i++) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1,
          color: config.particleColor,
        });
      }
    };
    initParticles();

    // 鼠标移动追踪
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener('mousemove', handleMouseMove);

    // 动画循环
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 更新和绘制粒子
      particlesRef.current.forEach((p, i) => {
        // 鼠标交互 - 粒子被排斥
        const dx = p.x - mouseRef.current.x;
        const dy = p.y - mouseRef.current.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < config.mouseDistance) {
          const force = (config.mouseDistance - dist) / config.mouseDistance;
          p.x += dx * force * 0.02;
          p.y += dy * force * 0.02;
        }

        // 自由移动
        p.x += p.vx;
        p.y += p.vy;

        // 边界反弹
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        // 绘制粒子
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();

        // 粒子间连线
        for (let j = i + 1; j < particlesRef.current.length; j++) {
          const p2 = particlesRef.current[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < config.connectionDistance) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(224, 122, 95, ${1 - distance / config.connectionDistance})`;
            ctx.stroke();
          }
        }
      });

      // 鼠标光晕效果
      const gradient = ctx.createRadialGradient(
        mouseRef.current.x, mouseRef.current.y, 0,
        mouseRef.current.x, mouseRef.current.y, config.mouseDistance
      );
      gradient.addColorStop(0, config.mouseGlowColor);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    // 清理
    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full pointer-events-none"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        background: 'transparent',
      }}
    />
  );
}
```

**使用方式**：
1. 创建组件文件：`src/components/ParticlesBackground.tsx`
2. 在 `App.tsx` 中作为第一个组件导入使用
3. **重要**：确保内容容器有相对定位和更高的 z-index

**⚠️ 全局应用要求（重要）**：
- **必须**：背景组件必须在 `App.tsx` 的最外层，确保所有页面共享同一个背景
- **禁止**：不要在单个页面组件内单独使用背景，每个页面不需要单独引入
- **结构**：`App.tsx` → `Fragment` → `ParticlesBackground` + 内容容器
- **效果**：切换页面时背景保持不变，只有内容区域变化

```tsx
// App.tsx - 正确的全局背景应用结构
return (
  <>
    <ParticlesBackground /> {/* 背景在最外层，所有页面共享 */}
    <div className="relative z-10 min-h-screen">
      {/* 所有页面内容都包裹在这个容器中 */}
      {currentPage === 'login' && <Login onNavigate={navigate} />}
      {currentPage === 'register' && <Register onNavigate={navigate} />}
      {currentPage === 'dashboard' && <Dashboard onNavigate={navigate} />}
    </div>
  </>
);
```

**层级保障**：
- 背景组件：使用内联样式 `position: fixed; z-index: 0;`
- 内容容器：`relative z-10`（确保比背景高）
- 背景必须设置 `pointer-events-none` 允许点击穿透

**常见问题解决**：

**Q: 背景把内容挤到页面底部怎么办？**

A: 给内容容器添加 `relative z-10`：
```tsx
// App.tsx
<div className="app relative z-10">
  {/* 登录框等内容 */}
</div>
```

**Q: 背景 canvas 把所有组件挡住了怎么办？**

A: 两个解决方案：
1. **推荐**：内容容器加 `relative z-10`
2. 背景 canvas 改 `z-[-1]` 为 `-z-10`（某些框架可能不支持负数 z-index）

**效果特点**：
- 80个粒子随机漂浮
- 距离近的粒子自动连线形成网络
- **鼠标移动时**：粒子被排斥散开 + 鼠标周围产生渐变光晕
- 整体科技感强，交互体验流畅

（待补充）
