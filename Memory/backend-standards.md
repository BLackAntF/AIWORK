# 后端规范

后端架构模式、API设计、数据库规范等。

## 技术栈
- **框架**: Next.js API Routes（Node.js）
- **语言**: TypeScript
- **数据库**: MySQL（mysql2/promise）
- **缓存**: Redis（ioredis）
- **认证**: JWT（jsonwebtoken）+ bcryptjs
- **输入验证**: zod
- **限流**: 内存级 RateLimiter（可扩展 Redis）

## 目录结构
```
src/
├── lib/              # 核心库
│   ├── auth.ts       # 认证、JWT、密码哈希、权限
│   ├── db.ts         # 数据库连接池、查询封装
│   ├── redis.ts      # Redis 缓存封装
│   ├── error.ts      # 错误类、错误处理器
│   ├── logger.ts     # 日志工具
│   └── rateLimiter.ts # 限流器
├── middleware/       # 中间件
│   ├── auth.ts       # 认证中间件、权限中间件
│   ├── rateLimit.ts  # 限流中间件
│   └── index.ts      # 中间件聚合导出
├── pages/
│   └── api/          # API 路由
│       ├── health.ts # 健康检查
│       ├── items.ts  # 资源 CRUD
│       └── auth/     # 认证相关
│           ├── login.ts
│           ├── register.ts
│           └── me.ts
└── scripts/
    └── init-db.sql   # 数据库初始化脚本
```

## API 设计规范

### 响应格式
```typescript
// 成功响应
{
  success: true,
  data: T
}

// 失败响应
{
  success: false,
  error: string
}
```

### HTTP 状态码
- `200` - GET/PUT/DELETE 成功
- `201` - POST 创建成功
- `400` - 请求参数错误
- `401` - 未认证 / Token 无效
- `403` - 权限不足
- `404` - 资源不存在
- `405` - 方法不允许
- `429` - 请求过于频繁
- `500` - 服务器内部错误

### 路由结构
- RESTful 风格：`/api/items` 对应资源集合，`/api/items?id=` 对应单个资源
- 认证相关：`/api/auth/login`、`/api/auth/register`、`/api/auth/me`
- 健康检查：`/api/health`

## 数据库规范

### 查询规范
- **必须使用参数化查询**：通过 `pool.execute(sql, params)` 执行，禁止字符串拼接 SQL
- 查询封装：`query<T>()` 返回多行，`queryOne<T>()` 返回单行或 null
- 使用连接池（mysql2/promise createPool），配置 connectionLimit

### 表设计原则
- 主键使用自增 `id`
- 时间字段使用 `created_at`、`updated_at`
- 密码存储为 `password_hash`（bcrypt 哈希）

## 认证与授权规范

### JWT 规范
- Payload 包含：`userId`、`email`、`role`
- 密钥通过 `process.env.JWT_SECRET` 环境变量配置
- 默认过期时间 7 天，可通过 `JWT_EXPIRES_IN` 配置

### 密码规范
- 使用 bcryptjs 哈希，salt rounds = 10
- 禁止明文存储密码
- 登录验证使用 `comparePassword` 函数

### 权限系统
- 角色：`admin`、`moderator`、`user`
- 权限：`read`、`write`、`delete`、`admin`
- 角色-权限映射集中在 `rolePermissions` 对象
- 中间件：`withAuth` 验证登录，`withPermission` 验证权限

## 中间件模式
- 使用高阶函数模式：`withAuth(handler)`、`withPermission(perm)(handler)`、`withRateLimit(n, ms)(handler)`
- 中间件可组合使用
- 认证中间件将解析后的用户信息挂载到 `req.user`

## 缓存规范

### Redis 缓存策略
- 缓存 key 命名：`item:${id}`（单个资源）、`items:all`（列表）
- 缓存过期时间：300 秒（5 分钟）
- 写操作（创建/更新/删除）后必须删除相关缓存
- 先查缓存，缓存未命中再查数据库，然后回填缓存

## 错误处理规范
- 自定义错误类 `ApiError`，包含 `statusCode`、`message`、`isOperational`
- 统一错误处理器 `errorHandler`，区分操作错误和未知错误
- 未知错误返回 500，不暴露内部细节
- 控制台仅记录未知错误（`console.error`）

## 限流规范
- 登录接口限流：10 次 / 60 秒
- 基于内存的滑动窗口限流（RateLimiter 类）
- 标识符可基于 IP 或用户 ID
- 返回 429 状态码

## 安全红线（强制执行）
- ❌ 禁止硬编码密钥、密码、API Key（使用 `.env` 环境变量）
- ✅ 所有数据库查询必须参数化（使用 `pool.execute` + params 数组）
- ✅ 用户输入必须验证（推荐使用 zod）
- ❌ 禁止使用 `eval`、字符串拼接 SQL
- ✅ 敏感操作必须权限校验
- ✅ 密码必须 bcrypt 哈希存储

## 代码质量
- 函数保持单一职责，不超过 20 行
- 使用 TypeScript 类型定义，禁止 `any`
- 环境变量访问使用 `process.env`，提供默认值
- 导出的函数和类型有明确的命名和用途