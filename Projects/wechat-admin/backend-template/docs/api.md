# API 接口文档

## 概述

本文档描述了后端系统的所有 API 接口，包括认证、资源管理等功能。

---

## 基础信息

- **基础 URL**: `http://localhost:3000/api`
- **认证方式**: JWT Token（Bearer Token）
- **响应格式**: JSON

---

## 错误响应格式

```json
{
  "success": false,
  "error": "错误描述"
}
```

---

## 接口列表

### 1. 健康检查

| 属性 | 值 |
|------|-----|
| **路径** | `/health` |
| **方法** | `GET` |
| **认证** | 不需要 |

**响应示例**:
```json
{
  "success": true,
  "message": "Server is running",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

---

### 2. 用户注册

| 属性 | 值 |
|------|-----|
| **路径** | `/auth/register` |
| **方法** | `POST` |
| **认证** | 不需要 |

**请求体**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `email` | string | 是 | 用户邮箱 |
| `password` | string | 是 | 用户密码 |

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**成功响应** (201):
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**失败响应** (400):
```json
{
  "success": false,
  "error": "User already exists"
}
```

---

### 3. 用户登录

| 属性 | 值 |
|------|-----|
| **路径** | `/auth/login` |
| **方法** | `POST` |
| **认证** | 不需要 |

**请求体**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `email` | string | 是 | 用户邮箱 |
| `password` | string | 是 | 用户密码 |

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "email": "user@example.com",
    "role": "user",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**失败响应** (401):
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---

### 4. 获取当前用户信息

| 属性 | 值 |
|------|-----|
| **路径** | `/auth/me` |
| **方法** | `GET` |
| **认证** | 需要 |

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "userId": "1",
    "email": "user@example.com",
    "role": "user"
  }
}
```

**失败响应** (401):
```json
{
  "success": false,
  "error": "Unauthorized"
}
```

---

### 5. 获取物品列表

| 属性 | 值 |
|------|-----|
| **路径** | `/items` |
| **方法** | `GET` |
| **认证** | 需要 |

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | string | 否 | 物品ID（不传则返回全部） |

**成功响应** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Item 1",
      "description": "Description",
      "created_at": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

---

### 6. 创建物品

| 属性 | 值 |
|------|-----|
| **路径** | `/items` |
| **方法** | `POST` |
| **认证** | 需要 |

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | 是 | 物品名称 |
| `description` | string | 否 | 物品描述 |

```json
{
  "name": "New Item",
  "description": "Item description"
}
```

**成功响应** (201):
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "New Item",
    "description": "Item description"
  }
}
```

---

### 7. 更新物品

| 属性 | 值 |
|------|-----|
| **路径** | `/items` |
| **方法** | `PUT` |
| **认证** | 需要 |

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | string | 是 | 物品ID |

**请求体**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | 是 | 物品名称 |
| `description` | string | 否 | 物品描述 |

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "id": "1",
    "name": "Updated Item",
    "description": "Updated description"
  }
}
```

**失败响应** (404):
```json
{
  "success": false,
  "error": "Item not found"
}
```

---

### 8. 删除物品

| 属性 | 值 |
|------|-----|
| **路径** | `/items` |
| **方法** | `DELETE` |
| **认证** | 需要 |

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | string | 是 | 物品ID |

**成功响应** (200):
```json
{
  "success": true,
  "message": "Item deleted successfully"
}
```

**失败响应** (404):
```json
{
  "success": false,
  "error": "Item not found"
}
```

---

## 认证与权限

### JWT Token

- Token 格式: `Bearer <token>`
- Token 过期时间: 7 天（可配置）
- Token 包含信息: `userId`, `email`, `role`

### 角色权限

| 角色 | 权限 |
|------|------|
| `admin` | read, write, delete, admin |
| `moderator` | read, write, delete |
| `user` | read, write |

---

## 速率限制

- 注册/登录接口: 10次/分钟
- 其他接口: 可配置

---

## 响应状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 405 | 方法不允许 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
