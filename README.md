# 智慧烹饪系统 (Intelligent Heating Furnace)

<div align="center">
  <p>
    <strong>基于 uni-app 的智能烹饪设备控制应用</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/uni--app-3.x-blue" alt="uni-app">
    <img src="https://img.shields.io/badge/Vue-3.x-brightgreen" alt="Vue">
    <img src="https://img.shields.io/badge/Bluetooth-LE-orange" alt="Bluetooth">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

## 📖 项目简介

智慧烹饪系统是一款基于 uni-app 框架开发的跨平台移动应用，通过蓝牙 BLE 技术连接智能加热烹饪设备，实现远程控制、实时监控、菜谱管理等功能。支持 Android、iOS 及微信小程序等多端部署。

### 主要功能

- **蓝牙设备管理**：扫描、连接、断开蓝牙烹饪设备
- **烹饪控制**：温度调节、时间设定、模式切换（煎炸/炖煮/蒸/烘焙/保温）
- **实时监控**：设备状态、温度、剩余时间实时显示
- **预设菜谱**：内置多种菜谱一键设置
- **设备管理**：设备信息查看、异常警报、紧急停止
- **系统设置**：声音提示、自动保温、夜间模式等

## 🚀 快速开始

### 环境要求

- [HBuilderX](https://www.dcloud.io/hbuilderx.html) (推荐使用)
- Node.js >= 16.x
- npm / yarn / pnpm

### 安装步骤

```bash
# 1. 克隆项目
git clone https://gitee.com/huolanrenzi/intelligent-heating-furnace.git

# 2. 进入项目目录
cd intelligent-heating-furnace

# 3. 安装依赖
npm install
# 或
yarn install
```

### 运行项目

使用 HBuilderX 打开项目目录，然后：

1. **运行到浏览器**：点击工具栏 `运行` → `运行到浏览器`
2. **运行到手机**：点击工具栏 `运行` → `运行到手机或模拟器`
3. **运行到微信小程序**：点击工具栏 `运行` → `运行到小程序模拟器` → `微信开发者工具`

### 构建发布

```bash
# 构建 H5
npm run build:h5

# 构建微信小程序
npm run build:mp-weixin

# 构建 App
npm run build:app-plus
```

## 📁 项目结构

```
uniapp-demo/
├── uniapp/                    # 主项目目录
│   ├── App.vue                # 应用入口组件（全局样式）
│   ├── main.js                # 应用入口文件
│   ├── manifest.json          # 应用配置文件
│   ├── pages.json             # 页面路由配置
│   ├── uni.scss               # 全局样式变量
│   ├── index.html             # H5 入口 HTML
│   ├── uni.promisify.adaptor.js  # uni-app Promise 适配
│   ├── pages/                 # 页面目录
│   │   ├── index/             # 首页 - 设备操控面板
│   │   │   └── index.vue
│   │   ├── device/            # 设备控制页
│   │   │   └── device.vue
│   │   ├── cook/              # 烹饪控制页
│   │   │   └── cook.vue
│   │   └── settings/          # 系统设置页
│   │       └── settings.vue
│   ├── utils/                 # 工具模块
│   │   └── ble.js             # 蓝牙 BLE 通信模块
│   ├── static/                # 静态资源
│   │   └── logo.png
│   └── .gitignore
├── README.md                  # 项目说明文档
├── CHANGELOG.md               # 版本变更日志
├── CONTRIBUTING.md            # 贡献指南
├── API.md                     # 蓝牙通信协议文档
└── LICENSE                    # 开源许可证
```

## 📱 页面说明

| 页面 | 路径 | 功能描述 |
|------|------|----------|
| 🏠 首页 | `/pages/index/index` | 设备操控面板、蓝牙扫描连接、模式选择、温度/时间控制 |
| 🔧 设备 | `/pages/device/device` | 设备状态概览、实时数据、设备信息、操作控制、异常警报 |
| 🍳 烹饪 | `/pages/cook/cook` | 烹饪状态监控、温度/时间调节、预设菜谱选择 |
| ⚙️ 设置 | `/pages/settings/settings` | 用户信息、系统设置、烹饪偏好、关于信息 |

## 🔌 蓝牙通信协议

详见 [API.md](./API.md) 文档。

### 通信规范

- **服务 UUID**: `0000FFB0-0000-1000-8000-00805F9B34FB`
- **写特征值 UUID**: `0000FFB2-0000-1000-8000-00805F9B34FB`
- **通知特征值 UUID**: `0000FFB1-0000-1000-8000-00805F9B34FB`

### 指令集

| 指令 | 功能 | 说明 |
|------|------|------|
| `>A` | 开机 | 设备上电 |
| `>B` | 关机 | 设备下电 |
| `>C` | 待机 | 进入待机模式 |
| `>D` ~ `>H` | 模式选择 | 煎炸/炖煮/蒸/烘焙/保温 |
| `>K{temp}` | 设置温度 | 如 `>K180` 表示 180°C |
| `>N{time}` | 设置时间 | 如 `>N30` 表示 30 分钟 |
| `>O` | 开始烹饪 | 启动烹饪程序 |
| `>P` | 暂停 | 暂停烹饪 |
| `>Q` | 停止 | 停止烹饪 |
| `>S` | 查询状态 | 查询设备当前状态 |
| `>W` | 紧急停止 | 紧急停止设备 |

## 🎨 主题样式

项目采用深色主题设计，主色调为 `#e94560`（红色），辅以深色背景 `#0f0f23` 和卡片背景 `#1a1a2e`。

### 样式变量

```scss
$primary-color: #e94560;     // 主色
$bg-dark: #0f0f23;           // 背景色
$bg-card: #1a1a2e;           // 卡片背景
$text-primary: #ffffff;       // 主文字
$text-secondary: #a0a0b0;    // 次要文字
$success-color: #2ecc71;     // 成功
$warning-color: #f39c12;     // 警告
$danger-color: #e74c3c;      // 危险
```

## 🧪 测试

```bash
# 运行单元测试
npm run test:unit

# 运行端到端测试
npm run test:e2e
```

## 🤝 贡献指南

请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解如何参与项目贡献。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件。

## 📞 联系方式

- 项目主页: [https://gitee.com/huolanrenzi/intelligent-heating-furnace](https://gitee.com/huolanrenzi/intelligent-heating-furnace)
- 问题反馈: [提交 Issue](https://gitee.com/huolanrenzi/intelligent-heating-furnace/issues)
