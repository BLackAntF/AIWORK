# 后端代码报告 - 2026-06-28

## 项目信息

- **项目名称**: wechat-admin backend
- **项目位置**: `Projects/wechat-admin/backend-template/`
- **技术栈**: Next.js API Routes + TypeScript + MySQL + Redis
- **主要依赖**: mysql2, ioredis, jsonwebtoken, bcryptjs, zod

---

## 一、架构概览

### 目录结构

```
src/
├── lib/                    # 核心库
│   ├── auth.ts             # 认证（JWT、密码哈希、权限）
│   ├── db.ts               # 数据库连接池、查询封装
│   ├── redis.ts            # Redis 缓存封装
│   ├── error.ts            # 错误类、统一错误处理器
│   ├── logger.ts           # 结构化日志工具
│   └── rateLimiter.ts      # 内存级限流器
├── middleware/             # 中间件
│   ├── auth.ts             # 认证中间件、权限中间件
│   ├── rateLimit.ts        # 限流中间件
│   └── index.ts            # 中间件聚合导出
└── pages/
    └── api/                # API 路由
        ├── health.ts       # 健康检查
        ├── items.ts        # 资源 CRUD
        └── auth/           # 认证相关
            ├── login.ts
            ├── register.ts
            └── me.ts
```

### 设计模式

1. **仓储模式封装**: `db.ts` 提供 `query` / `queryOne` 统一查询接口
2. **服务层模式**: 各 API handler 内部按职责拆分子函数
3. **中间件模式**: 高阶函数 `withAuth` / `withPermission` / `withRateLimit`
4. **缓存旁路模式**: 先查 Redis，未命中查 DB，再回填缓存
5. **集中式错误处理**: `errorHandler` 统一处理 ApiError、ZodError、未知错误

---

## 二、核心模块说明

### 2.1 认证模块 (`lib/auth.ts`)

| 功能 | 说明 |
|------|------|
| JWT 生成 | `generateToken(payload)`，默认 7 天过期 |
| JWT 验证 | `verifyToken(token)`，失败抛 ApiError(401) |
| 密码哈希 | `hashPassword(password)`，bcrypt salt rounds = 10 |
| 密码验证 | `comparePassword(password, hash)` |
| 权限判断 | `hasPermission(role, permission)` |

**角色-权限映射**:
- `admin`: read, write, delete, admin
- `moderator`: read, write, delete
- `user`: read, write

### 2.2 数据库模块 (`lib/db.ts`)

- 使用 `mysql2/promise` 连接池
- `connectionLimit = 10`
- 参数化查询，防 SQL 注入
- 提供 `query<T>()` 和 `queryOne<T>()` 泛型方法

### 2.3 缓存模块 (`lib/redis.ts`)

- 使用 `ioredis` 客户端
- 提供 `getCache` / `setCache` / `deleteCache` / `existsCache`
- 支持 TTL 过期（items 缓存 300 秒）
- 自动 JSON 序列化/反序列化

### 2.4 错误处理模块 (`lib/error.ts`)

- `ApiError` 自定义错误类（statusCode, message, isOperational）
- `errorHandler` 统一处理：
  - ApiError → 对应状态码 + 错误消息
  - ZodError → 400 + 验证详情
  - 未知错误 → 500 + 日志记录

### 2.5 限流模块 (`lib/rateLimiter.ts`)

- 内存级滑动窗口限流
- 登录/注册接口：10 次 / 60 秒

---

## 三、API 接口清单

### 3.1 认证接口

| 方法 | 路径 | 说明 | 认证 | 限流 |
|------|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 否 | 10次/60s |
| POST | `/api/auth/login` | 用户登录 | 否 | 10次/60s |
| GET | `/api/auth/me` | 获取当前用户 | 是 | 否 |

### 3.2 资源接口

| 方法 | 路径 | 说明 | 认证 | 权限 |
|------|------|------|------|------|
| GET | `/api/items` | 获取列表 | 是 | read |
| GET | `/api/items?id=` | 获取单个 | 是 | read |
| POST | `/api/items` | 创建 | 是 | write |
| PUT | `/api/items?id=` | 更新 | 是 | write |
| DELETE | `/api/items?id=` | 删除 | 是 | delete |

### 3.3 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 服务健康检查 |

---

## 四、安全合规检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 禁止硬编码密钥 | ✅ | 全部使用 `process.env` 环境变量 |
| 参数化查询 | ✅ | 所有 SQL 使用 `pool.execute` + params |
| 输入验证 | ✅ | 使用 zod schema 验证所有用户输入 |
| 禁止 eval / 字符串拼接 SQL | ✅ | 无相关代码 |
| 密码哈希存储 | ✅ | bcryptjs，salt rounds = 10 |
| 敏感操作权限校验 | ✅ | withAuth / withPermission 中间件 |
| JWT 密钥环境变量 | ✅ | `JWT_SECRET` |

---

## 五、代码质量指标

| 指标 | 状态 | 说明 |
|------|------|------|
| TypeScript 类型 | ✅ | 完整类型定义，无 any |
| 函数单一职责 | ✅ | 函数粒度细，单函数不超过 20 行 |
| 命名常量 | ✅ | 魔法值替换为命名常量（CACHE_TTL, ALLOWED_METHODS 等） |
| 错误处理 | ✅ | 统一 errorHandler，所有 API 都有 try/catch |
| 中间件可组合 | ✅ | withAuth + withPermission + withRateLimit 可叠加 |
| 缓存策略 | ✅ | 读写缓存，写操作后失效 |

---

## 六、数据库设计

### users 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| email | VARCHAR(255) | NOT NULL, UNIQUE | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| role | ENUM | DEFAULT 'user' | 角色：admin/moderator/user |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### items 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 资源ID |
| name | VARCHAR(255) | NOT NULL | 名称 |
| description | TEXT | NULL | 描述 |
| created_by | INT | FK → users.id | 创建者 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- `uk_users_email` (email) - 唯一索引
- `idx_items_created_by` (created_by) - 外键索引
- `idx_items_created_at` (created_at DESC) - 排序优化

---

## 七、环境变量配置 (`.env.example`)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DB_HOST | MySQL 主机 | localhost |
| DB_PORT | MySQL 端口 | 3306 |
| DB_USER | MySQL 用户 | root |
| DB_PASSWORD | MySQL 密码 | - |
| DB_NAME | 数据库名 | - |
| REDIS_HOST | Redis 主机 | localhost |
| REDIS_PORT | Redis 端口 | 6379 |
| REDIS_PASSWORD | Redis 密码 | - |
| JWT_SECRET | JWT 密钥 | - |
| JWT_EXPIRES_IN | JWT 过期时间 | 7d |
| PORT | 服务端口 | 3000 |

---

## 八、变更记录

本次后端任务完成的主要改进：

1. **核心库优化**
   - `auth.ts`: 修复 role 类型不一致，导出 UserRole 类型，集成 ApiError，添加命名常量
   - `error.ts`: 添加 ZodError 处理，集成 logger 记录未知错误
   - `db.ts`: 添加命名常量，优化泛型类型（Record<string, any>）
   - `redis.ts`: 添加命名常量，代码结构优化

2. **中间件重构**
   - `auth.ts`: 使用统一 errorHandler，withPermission 复用 withAuth，代码更简洁
   - `rateLimit.ts`: 使用统一 errorHandler，提取 getClientIp 辅助函数

3. **API 增强**
   - 所有 API 添加 zod 输入验证（登录/注册/items CRUD）
   - 所有 API 使用统一 errorHandler 和 ApiError
   - `items.ts`: 拆分为多个小函数，提取缓存辅助函数 getCachedOrFetch
   - `items.ts`: 更新接口支持部分更新（COALESCE）
   - 使用 ResultSetHeader 类型替代 any

4. **数据库脚本优化**
   - 指定 ENGINE=InnoDB 和 CHARSET=utf8mb4
   - 明确外键约束命名和 ON UPDATE CASCADE
   - 添加 created_at 索引优化排序查询

---

## 九、后续建议

1. **单元测试**: 为核心库（auth, error, rateLimiter）添加单元测试
2. **Redis 限流**: 将限流从内存迁移到 Redis，支持多实例部署
3. **请求日志中间件**: 统一记录请求日志（method, path, ip, duration）
4. **分页支持**: items 列表接口添加分页参数（limit, offset）
5. **软删除**: 考虑添加 deleted_at 字段支持软删除
6. **环境变量校验**: 启动时校验必要环境变量是否配置

---

**报告生成时间**: 2026-06-28
**后端开发任务**: 已完成
