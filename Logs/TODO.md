# TODO - 待处理事项

## 2026-06-16

### 粒子连线网络背景层级问题

**问题描述**：
- canvas 背景把登录框等内容挤到页面底部
- 给内容容器加 `relative z-10` 后仍然被 canvas 挡住

**已尝试的方案**：
1. 背景 canvas 设置 `z-[-1]`
2. 内容容器添加 `relative z-10`

**待尝试的方案**：
1. 检查 canvas 父容器是否有定位上下文影响
2. 尝试用 `-z-10` 替代 `z-[-1]`
3. 检查是否有全局样式覆盖了 z-index
4. 确保 App.tsx 结构为：
   ```tsx
   <ParticlesBackground />
   <div className="relative z-10">
     {/* 内容 */}
   </div>
   ```

**待处理状态**：暂停，等待明天解决
