# 代码审查报告

**审查日期**: 2026-06-28
**审查范围**: wechat-admin 项目前端与后端核心代码
**审查依据**: Memory/CONSTRAINTS.md 安全红线

---

## 一、审查摘要

| 项目 | 状态 | 说明 |
|------|------|------|
| 硬编码密钥检查 | ✅ 通过 | 后端使用环境变量，前端无密钥 |
| SQL 注入防护 | ⚠️ 部分问题 | items.ts 存在参数类型验证缺失 |
| 用户输入验证 | ⚠️ 部分问题 | email 格式未验证，id 参数类型未校验 |
| eval/SQL拼接 | ✅ 通过 | 未发现使用 |
| 权限校验 | ✅ 通过 | withAuth 中间件正常 |
| 前端错误处理 | ✅ 通过 | axios.ts 已实现多状态码处理 |

---

## 二、详细问题

### 🔴 高风险问题

#### 1. items.ts - ID 参数类型未验证
**位置**: `backend-template/src/pages/api/items.ts`

```typescript
// handleGetItems (line 27)
if (id) {
  const item = await queryOne('SELECT id, name, description, created_at FROM items WHERE id = ?', [id])
}

// handleUpdateItem (line 94)
const [result] = await query(
  'UPDATE items SET name = ?, description = ? WHERE id = ?',
  [name, description, id]
)

// handleDeleteItem (line 123)
const [result] = await query('DELETE FROM items WHERE id = ?', [id])
```

**问题**: `id` 来自 `req.query`，未验证是否为有效数字类型，可能导致 SQL 类型错误或缓存键注入。

**修复建议**:
```typescript
const itemId = Number(id)
if (!Number.isInteger(itemId) || itemId <= 0) {
  return res.status(400).json({ error: 'Invalid item ID' })
}
```

#### 2. login.ts - Email 格式未验证
**位置**: `backend-template/src/pages/api/auth/login.ts` (line 13)

```typescript
if (!email || !password) {
  return res.status(400).json({ error: 'Email and password are required' })
}
```

**问题**: 仅检查非空，未验证 email 格式是否为有效邮箱。

**修复建议**:
```typescript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
if (!email || !emailRegex.test(email)) {
  return res.status(400).json({ error: 'Invalid email format' })
}
```

---

### 🟡 中等风险问题

#### 3. auth.ts - JWT_SECRET 缺少默认值
**位置**: `backend-template/src/lib/auth.ts` (line 11)

```typescript
return jwt.sign(payload, process.env.JWT_SECRET!, {
```

**问题**: 如果 `JWT_SECRET` 环境变量未设置，应用启动时会直接崩溃。

**修复建议**:
```typescript
const secret = process.env.JWT_SECRET
if (!secret) {
  throw new Error('JWT_SECRET environment variable is not set')
}
return jwt.sign(payload, secret, { ... })
```

#### 4. items.ts - handleCreateItem 缺少 description 验证
**位置**: `backend-template/src/pages/api/items.ts` (line 60-65)

```typescript
const { name, description } = req.body

if (!name) {
  return res.status(400).json({ error: 'Name is required' })
}
```

**问题**: `description` 可为 null 或过长字符串，应有长度限制。

**修复建议**:
```typescript
if (!name || name.length > 255) {
  return res.status(400).json({ error: 'Name is required and must be ≤ 255 characters' })
}
if (description && description.length > 1000) {
  return res.status(400).json({ error: 'Description must be ≤ 1000 characters' })
}
```

---

### 🟢 低风险问题 (建议改进)

#### 5. App.tsx - 缺少路由守卫组件
**位置**: `frontend/src/App.tsx`

**问题**: 直接通过 state 控制页面显示，未使用 React Router。页面权限控制分散在各个组件中。

**建议**: 考虑引入 React Router + ProtectedRoute 组件统一管理权限。

---

## 三、已确认良好的实践

| 文件 | 优点 |
|------|------|
| `db.ts` | ✅ 使用 mysql2/promise 连接池，参数化查询正确 |
| `login.ts` | ✅ 使用 bcrypt.comparePassword 密码比对，参数化查询防注入 |
| `axios.ts` | ✅ 已实现 401/403/404/500 及网络错误的中文提示 |
| `AuthContext.tsx` | ✅ JSON.parse 错误处理，防止 localStorage 损坏导致崩溃 |
| `App.tsx` | ✅ 粒子背景在正确位置（最外层），z-index 层级正确 |
| `middleware/auth.ts` | ✅ withAuth 和 withPermission 中间件实现正确 |

---

## 四、修复优先级

| 优先级 | 问题编号 | 描述 |
|--------|----------|------|
| P0 | #1 | items.ts ID 参数类型验证 |
| P0 | #2 | login.ts Email 格式验证 |
| P1 | #3 | auth.ts JWT_SECRET 默认值检查 |
| P2 | #4 | items.ts description 长度限制 |
| P3 | #5 | App.tsx 路由守卫（长期改进） |

---

## 五、审查结论

本次审查共发现 **5 个问题**，其中 **2 个高风险**，**2 个中等风险**，**1 个低风险建议**。

代码整体安全水平较好，后端正确使用了参数化查询和权限中间件，前端错误处理完善。主要问题集中在**输入验证不完整**，建议优先修复高风险问题。

---

**审查人**: TRAE AI 审查任务
**报告生成时间**: 2026-06-28
