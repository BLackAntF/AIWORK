# 贡献指南

> 感谢您考虑为智慧烹饪系统项目做出贡献！

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [分支管理](#分支管理)
- [Issue 指南](#issue-指南)
- [Pull Request 指南](#pull-request-指南)

---

## 行为准则

### 我们的承诺

为了营造一个开放、友好的社区环境，我们承诺：

- **尊重包容**：尊重不同的观点和经验
- **友善协作**：以建设性的方式进行沟通
- **关注本质**：关注问题本身而非个人
- **开放接纳**：欢迎新手和不同背景的贡献者

### 不可接受的行为

- 人身攻击或挑衅性言论
- 发布他人隐私信息
- 其他不道德或不合法的行为

---

## 如何贡献

### 适合新手的贡献方式

1. **报告 Bug**
   - 提交 Issue 描述问题
   - 提供复现步骤和环境信息

2. **改进文档**
   - 修正拼写或语法错误
   - 补充缺失的文档内容
   - 优化文档结构和可读性

3. **提交功能建议**
   - 描述你期望的功能
   - 说明使用场景和价值

### 进阶贡献

1. **修复 Bug**
   - 认领 Issue 中的 Bug
   - 提交 Pull Request

2. **实现新功能**
   - 先讨论功能设计
   - 确保向后兼容

3. **代码审查**
   - 审查他人的 Pull Request
   - 提供建设性意见

---

## 开发流程

### 环境搭建

```bash
# 1. Fork 项目
# 2. 克隆你的 Fork
git clone https://gitee.com/你的用户名/intelligent-heating-furnace.git

# 3. 添加上游仓库
git remote add upstream https://gitee.com/huolanrenzi/intelligent-heating-furnace.git

# 4. 安装依赖
npm install

# 5. 创建功能分支
git checkout -b feature/your-feature-name
```

### 开发步骤

1. **同步最新代码**
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **编写代码**
   - 遵循代码规范
   - 添加必要的注释
   - 编写单元测试

3. **本地测试**
   ```bash
   # 运行测试
   npm run test:unit
   
   # 运行在浏览器验证
   # 使用 HBuilderX 运行到浏览器
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**
   - 提交到 `master` 分支
   - 描述变更内容和测试情况

---

## 代码规范

### Vue 组件规范

```vue
<template>
  <!-- 模板部分 -->
</template>

<script>
export default {
  name: 'ComponentName',
  
  data() {
    return {}
  },
  
  computed: {},
  
  methods: {}
}
</script>

<style scoped>
/* 样式部分 */
</style>
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件名 | PascalCase | `DevicePanel.vue` |
| 变量 | camelCase | `deviceName` |
| 常量 | UPPER_SNAKE_CASE | `SERVICE_UUID` |
| 方法 | camelCase | `connectDevice()` |
| CSS 类 | kebab-case | `device-status` |

### JavaScript 规范

- 使用 ES6+ 语法
- 优先使用 `const` / `let`
- 使用箭头函数
- 异步操作使用 `async/await`
- 添加必要的 JSDoc 注释

```javascript
/**
 * 连接蓝牙设备
 * @param {string} deviceId - 设备 ID
 * @param {string} deviceName - 设备名称
 * @returns {Promise<void>}
 */
async connectDevice(deviceId, deviceName) {
  // ...
}
```

### CSS 规范

- 使用 scoped 样式
- 使用 rpx 单位适配
- 遵循 BEM 命名规范
- 使用 CSS 变量管理主题

---

## 提交规范

### Commit 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 代码重构 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建/工具链变更 |

### 示例

```
feat(ble): 添加设备自动重连功能

- 实现断线自动重连机制
- 添加指数退避重试策略
- 最大重试次数限制为 5 次

Closes #123
```

---

## 分支管理

### 分支命名

| 分支 | 用途 | 命名规则 |
|------|------|----------|
| `master` | 主分支，稳定版本 | `master` |
| `develop` | 开发分支 | `develop` |
| 功能分支 | 新功能开发 | `feature/xxx` |
| 修复分支 | Bug 修复 | `fix/xxx` |
| 发布分支 | 版本发布 | `release/v*.*.*` |

### 分支策略

```
master
  ↑
release/v1.0.0
  ↑
develop
  ↑
feature/xxx
```

---

## Issue 指南

### 提交 Bug

```markdown
## Bug 描述
[清晰描述问题]

## 复现步骤
1. 打开应用
2. 点击...
3. 出现错误

## 预期行为
[描述应该发生什么]

## 实际行为
[描述实际发生了什么]

## 环境信息
- 设备: [如 iPhone 14]
- 系统: [如 iOS 16.0]
- 应用版本: [如 v1.0.0]

## 补充信息
[日志、截图等]
```

### 功能建议

```markdown
## 功能描述
[清晰描述你期望的功能]

## 使用场景
[描述在什么场景下使用]

## 实现思路
[可选] 你对实现的建议

## 优先级
[高/中/低]
```

---

## Pull Request 指南

### PR 模板

```markdown
## 变更内容
[描述变更的具体内容]

## 关联 Issue
Closes #[issue_number]

## 测试情况
- [ ] 本地测试通过
- [ ] 蓝牙连接测试
- [ ] 多端兼容测试

## 截图（可选）
[UI 变更时提供截图]

## 检查清单
- [ ] 代码符合规范
- [ ] 已添加必要注释
- [ ] 文档已更新
- [ ] 无破坏性变更
```

### PR 审查标准

- 代码质量和规范
- 功能完整性和正确性
- 异常处理和边界情况
- 性能和安全性
- 向后兼容性

---

## 获取帮助

- 提交 [Issue](https://gitee.com/huolanrenzi/intelligent-heating-furnace/issues)
- 在 PR 中 @ 维护者

---

> **最后更新**: 2024-01  
> **维护者**: 智慧烹饪系统开发团队
