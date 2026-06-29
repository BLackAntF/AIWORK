# BLackAntProject - 功能规划文档

## 一、产品定位

**产品名称**: BLackAntProject
**产品类型**: 通用管理后台系统
**目标用户**: 企业内部管理系统、运营人员

---

## 二、功能模块规划

### 模块 1：数据概览仪表盘（首页）

**功能说明**: 展示关键运营数据，一目了然掌握系统状态

**包含内容**:
| 指标 | 说明 |
|------|------|
| 今日活跃用户 | 当天登录用户数 |
| 今日新增记录 | 当天新增数据条目 |
| 总记录数 | 当前系统总数据量 |
| 任务完成率 | 进行中任务完成百分比 |
| 系统状态 | 在线/离线服务数量 |

**图表组件**:
- 7日/30日趋势折线图（活跃用户、增长趋势）
- 数据分布柱状图
- TOP 5 数据排行

---

### 模块 2：内容管理

**功能说明**: 管理系统的核心内容数据

**功能清单**:
| 功能 | 描述 |
|------|------|
| 内容列表 | 分页展示所有内容，显示标题、状态、创建时间 |
| 创建内容 | 添加新的内容条目 |
| 编辑内容 | 修改已有内容 |
| 删除内容 | 确认后删除，带软删除（可恢复） |
| 草稿箱 | 保存未发布的内容 |
| 分类标签 | 给内容添加分类/标签 |
| 搜索筛选 | 按标题、分类、日期搜索 |

**内容状态**:
- `草稿` - 未发布
- `已发布` - 线上可见
- `已下架` - 不展示但保留

---

### 模块 3：用户管理

**功能说明**: 管理系统用户和权限

**功能清单**:
| 功能 | 描述 |
|------|------|
| 用户列表 | 分页展示用户，显示昵称、角色、状态、注册时间 |
| 用户详情 | 查看用户基本信息、操作记录 |
| 用户角色 | 设置用户角色（管理员、普通用户） |
| 用户搜索 | 按昵称、邮箱搜索 |
| 禁用/启用 | 冻结或恢复用户账号 |

**用户字段**:
- `id` - 用户唯一标识
- `nickname` - 昵称
- `email` - 邮箱
- `role` - 角色（admin/user）
- `status` - 状态（active/inactive）
- `created_at` - 注册时间

---

### 模块 4：消息/通知管理

**功能说明**: 系统消息和通知处理

**功能清单**:
| 功能 | 描述 |
|------|------|
| 消息列表 | 展示所有系统消息，支持分页 |
| 发送消息 | 向指定用户或全员发送通知 |
| 已读/未读 | 标记消息阅读状态 |
| 消息搜索 | 按内容、发送者搜索 |

---

### 模块 5：数据统计

**功能说明**: 详细的数据分析报表

**功能清单**:
| 功能 | 描述 |
|------|------|
| 内容分析 | 各类内容的数量、浏览量统计 |
| 用户分析 | 新增用户、活跃用户趋势 |
| 操作日志 | 用户操作行为记录 |
| 数据导出 | 导出统计数据为 Excel |

**图表类型**:
- 折线图 - 趋势变化
- 柱状图 - 对比数据
- 饼图 - 占比分布

---

## 三、技术实现方案

### 数据库表设计

```sql
-- 用户表
users (id, email, password_hash, nickname, role, status, created_at, updated_at)

-- 内容表
contents (id, title, body, summary, status, views, user_id, created_at, updated_at, deleted_at)

-- 分类表
categories (id, name, description, created_at)

-- 标签表
tags (id, name, created_at)

-- 内容-分类关联表
content_categories (content_id, category_id)

-- 内容-标签关联表
content_tags (content_id, tag_id)

-- 消息表
notifications (id, user_id, title, content, is_read, created_at)

-- 操作日志表
logs (id, user_id, action, target_type, target_id, details, created_at)

-- 数据统计表（每日汇总）
daily_stats (id, stat_date, active_users, new_records, total_records, created_at)
```

### API 接口设计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stats/today | 今日数据概览 |
| GET | /api/stats/trend | 数据趋势（7日/30日） |
| GET | /api/contents | 内容列表（分页+筛选） |
| POST | /api/contents | 创建内容 |
| PUT | /api/contents/:id | 编辑内容 |
| DELETE | /api/contents/:id | 删除内容 |
| GET | /api/users | 用户列表 |
| GET | /api/users/:id | 用户详情 |
| PUT | /api/users/:id | 更新用户信息 |
| PUT | /api/users/:id/status | 启用/禁用用户 |
| GET | /api/notifications | 消息列表 |
| POST | /api/notifications | 发送消息 |
| PUT | /api/notifications/:id/read | 标记已读 |
| GET | /api/analytics/contents | 内容分析数据 |
| GET | /api/analytics/users | 用户分析数据 |
| GET | /api/logs | 操作日志 |

---

## 四、实施优先级建议

### 第一期（MVP）- 基础框架

1. **数据概览仪表盘** - 首页核心数据展示
2. **内容管理** - 基本的 CRUD
3. **用户管理** - 用户列表查看、角色管理

### 第二期（扩展功能）

4. **消息/通知管理** - 系统消息发送
5. **搜索筛选** - 高级搜索功能

### 第三期（数据分析）

6. **数据统计** - 详细报表
7. **图表可视化** - 趋势图表
8. **数据导出** - Excel 导出

---

## 五、请确认

在开始实现之前，请告诉我：

1. **您希望先实现哪个模块？** （推荐从"数据概览仪表盘"开始）
2. **是否需要调整功能范围？** （增减某些功能）
3. **数据来源？** （模拟数据 / 真实业务数据）
4. **界面风格偏好？** （保持现有粒子背景 + 主题色，或有其他想法）

确认后我会调整规划文档，然后你可以通过前端/后端任务来逐步实现。
