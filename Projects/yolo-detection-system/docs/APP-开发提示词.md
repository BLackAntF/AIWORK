# 移动端 App 开发提示词

> **版本**：v1.0
> **日期**：2026-07-14
> **用法**：用户给出关键词（如"Phase1"），AI 从本文档中提取对应提示词，用户复制到新 Task 执行

---

## 通用上下文（每个提示词都必须包含）

```
## 项目背景
- 项目：番茄叶片病害智能诊断平台 移动端 App
- 技术框架：uni-app（Vue 3 + Composition API + Pinia）
- 后端：Flask，与 Web 端共用 API，后端零改动
- 项目目录：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\mobile\
- 开发预览：npm run dev:h5（浏览器 H5 预览）

## 必读文档
1. 需求文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-需求文档.md
2. 开发文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-开发文档.md
3. Web 端风格参考：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\（API封装、Store、页面结构）
4. PRD：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\PRD.md

## Web 端代码复用规范
- API 接口定义：参照 frontend/src/api/ 下的接口文件，App 端改为 uni.request 封装
- Pinia Store：参照 frontend/src/store/modules/ 下的 store，App 端改为 uni.getStorageSync
- 页面逻辑：参照 frontend/src/views/ 下对应页面，UI 组件从 Element Plus 改为 uni-ui
- 后端响应格式：{ code: 0, data: {...}, message: "..." }，注意 code=0 表示成功（不是 200）

## 编码规范
- Vue 3 Composition API（<script setup>）
- 函数不超过 20 行
- 变量命名：camelCase
- 文件命名：kebab-case
- 中文注释
- 不硬编码 API 地址，使用环境变量
```

---

## Phase 1：基础框架

### 关键词：`Phase1` / `基础框架`

```
## 任务：搭建 uni-app 项目基础框架

### 1. 创建项目
在 d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\ 下创建 mobile 目录，使用 CLI 初始化 uni-app Vue 3 项目：
- 运行：npx degit dcloudio/uni-preset-vue#vite mobile
- 安装依赖：cd mobile && npm install && npm install pinia

### 2. 核心配置
参照文档 d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-开发文档.md 的第 2 节，完成：
- pages.json：配置 15 个页面路由 + 5 个 TabBar 项（首页/检测/问答/历史/我的）
- manifest.json：应用名"番茄病害诊断"，Android minSdkVersion 26，iOS 12.0
- uni.scss：定义全局样式变量（主色 #4CAF50，字体，间距，圆角）

### 3. 请求封装
参照 Web 端 d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\api\axios.js 的逻辑，创建：
- api/request.js：封装 uni.request，含 Token 自动注入、401 自动跳登录、错误提示
  注意：后端成功码是 code=0（不是 200），参照 Web 端 axios.js 的 response 拦截器
- api/upload.js：封装 uni.uploadFile，用于图片上传

### 4. API 接口文件
参照 Web 端 frontend/src/api/ 下的文件，创建对应的 App 端接口文件：
- api/auth.js：login, register, getUserInfo, changePassword
- api/detect.js：detectImage（用 uni.uploadFile）
- api/knowledge.js：askQuestion, getSessionList, getChatHistory, deleteSession, getKnowledgeList, getKnowledgeDetail, getCategories
- api/history.js：getHistoryList, getHistoryDetail, deleteHistory
- api/admin.js：getUsers, getPendingKnowledge, getLogs, getDashboardStats

### 5. Pinia Store
参照 Web 端 frontend/src/store/modules/user.js，创建：
- store/index.js：注册 Pinia
- store/user.js：token（用 uni.getStorageSync）、userInfo、isAdmin、login、logout
- store/chat.js：currentSessionId、messages、sessions

### 6. 登录/注册页
- pages/login/index.vue：用户名+密码登录，参照需求文档 AUTH-01
- pages/register/index.vue：用户名+邮箱+密码注册，参照需求文档 AUTH-02

### 验收
- npm run dev:h5 可正常启动，浏览器打开可见登录页
- 登录页输入账密可调用后端 API 登录
- 登录成功后 Token 存入 Storage，跳转首页
```

---

## Phase 2：检测流程

### 关键词：`Phase2` / `检测流程` / `拍照检测`

```
## 任务：开发检测流程页面（拍照/检测/结果/档案）

参照文档：
- 需求文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-需求文档.md 第 3.2-3.3 节
- 开发文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-开发文档.md 第 5.2 节
- Web 端检测页：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\views\Detect.vue

### 1. 检测页 pages/detect/index.vue
- 图片选择：调用 uni.chooseImage，sourceType 包含 camera 和 album
- 图片预览：选择后显示预览，支持重新选择
- 图片压缩：上传前用 uni.compressImage 压缩到质量 60，控制大小 ≤5MB
- 开始检测：调用 api/detect.js 的 detectImage 上传，显示 Loading
- 结果展示：展示检测后带标注框的图片 + 病害名称 + 置信度
- 多病害：一张图检测到多种病害时全部展示
- Healthy：检测为健康时显示健康提示
- "咨询AI"按钮：跳转问答 Tab 并传入检测图片（用 uni.$emit）

### 2. 病害档案卡片 components/DiseaseCard.vue
- 展示病害名称、诱因、症状、防治方案
- 推荐药剂用标签样式展示
- 点击跳转档案详情页

### 3. 病害档案详情 pages/archive/detail.vue
- 接收档案 ID 参数，调用 API 获取详情
- 用折叠面板（uni-collapse）展示：诱因、症状、发生规律、预防措施、治疗方案、推荐药剂

### 4. 首页 pages/index/index.vue
- 顶部快速检测入口按钮
- 最近 5 条检测记录列表
- 点击记录跳转历史详情

### 5. 公共组件
- components/LoadingOverlay.vue：全屏加载遮罩
- components/EmptyState.vue：空状态占位

### 验收
- H5 预览中可点击"选择图片"（H5 不支持相机，但支持相册选择）
- 选择图片后可上传检测（需后端运行中）
- 检测结果正确展示
- 病害档案卡片和详情页正常显示
```

---

## Phase 3：AI 问答

### 关键词：`Phase3` / `AI问答` / `聊天`

```
## 任务：开发 AI 智能问答页面

参照文档：
- 需求文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-需求文档.md 第 3.4 节
- 开发文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-开发文档.md 第 5.3 节
- Web 端 AI 问答：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\views\Knowledge.vue
- PRD RAG 架构：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\PRD.md 第 2.1.4 节

### 1. AI 问答页 pages/chat/index.vue
- 消息列表：scroll-view 展示聊天记录
- 输入区：底部输入框 + 发送按钮，maxlength 500
- 发送消息：调用 api/knowledge.js 的 askQuestion
- AI 思考状态：发送后显示"AI 正在思考..."打字动画
- 自动滚动：新消息后自动滚到底部

### 2. 图片传入问答
- 监听 uni.$on('detect-to-chat')，接收检测页传入的图片
- 问答区顶部显示检测图片缩略图 + "检测图片已带入"提示
- 可点击 × 移除图片上下文
- 发送问题时附带 image_url 参数

### 3. 置信度展示
- AI 回答以列表形式展示，每条附带置信度标签
- 高可信=绿色，中可信=橙色，仅供参考=灰色

### 4. 快捷提问
- 问答页初始显示 4 个快捷问题："这个病严重吗？""怎么防治？""用什么药剂？""多久能治好？"
- 点击快捷问题直接发送

### 5. 会话管理（P1）
- 侧滑面板展示历史会话列表
- 新建会话 / 切换会话 / 删除会话

### 6. 公共组件
- components/ChatBubble.vue：聊天气泡（区分用户/AI）
- components/ConfidenceTag.vue：置信度标签（high/medium/low）

### 验收
- 问答页可发送文字问题并收到 AI 回答（需后端运行中）
- 检测页"咨询AI"跳转问答页，图片自动带入
- 置信度标签正确显示颜色
- 快捷问题可点击发送
```

---

## Phase 4：历史和知识库

### 关键词：`Phase4` / `历史` / `知识库`

```
## 任务：开发检测历史和知识库浏览页面

参照文档：
- 需求文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-需求文档.md 第 3.5-3.6 节
- Web 端历史页：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\views\History.vue
- Web 端知识库：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\views\KnowledgeList.vue

### 1. 检测历史列表 pages/history/index.vue
- 调用 GET /api/history 获取列表
- 每条显示：缩略图、病害名称、检测时间
- 下拉刷新 + 上拉加载更多（分页）
- 点击进入详情页
- 滑动删除（P2）

### 2. 检测历史详情 pages/history/detail.vue
- 接收记录 ID，调用 GET /api/history/:id 获取详情
- 展示原图 + 检测结果图 + 病害信息
- 底部展示对应病害档案卡片

### 3. 知识库列表 pages/knowledge/list.vue（只读）
- 调用 GET /api/knowledge/list 获取列表
- 分类筛选：调用 GET /api/knowledge/categories 获取分类
- 关键词搜索
- 下拉刷新 + 上拉加载更多
- 点击进入详情

### 4. 知识详情 pages/knowledge/detail.vue
- 调用 GET /api/knowledge/:id 获取详情
- 展示标题、内容、分类、来源
- 底部推荐相关知识：调用 GET /api/knowledge/:id/related

### 验收
- 历史列表正确展示，下拉刷新和上拉加载正常
- 历史详情展示完整
- 知识库列表和详情正常（只读，无编辑按钮）
```

---

## Phase 5：管理员端 + 个人中心

### 关键词：`Phase5` / `管理员` / `个人中心`

```
## 任务：开发管理员只读页面和个人中心

参照文档：
- 需求文档：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\docs\APP-需求文档.md 第 3.7-3.8 节
- Web 端管理端：d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\frontend\src\views\admin\

### 1. 个人中心 pages/mine/index.vue
- 顶部：用户头像、用户名、角色标签
- 中部菜单：
  - 修改密码（跳转修改页）
  - 知识库浏览（跳转 pages/knowledge/list）
  - 关于（显示版本号）
- 底部：退出登录按钮
- 管理员入口：仅 admin 角色可见，点击展开子菜单

### 2. 管理员页面（只读）
- pages/admin/users.vue：用户列表，仅查看，不提供编辑操作
- pages/admin/pending.vue：待审核知识列表，仅查看
- pages/admin/logs.vue：操作日志列表，仅查看
- pages/admin/dashboard.vue：数据看板（用户数/检测数/知识数）

所有管理员页面：
- 不提供编辑/删除按钮
- 需要编辑时提示"请在 Web 端管理后台操作"

### 验收
- 个人中心正确显示用户信息
- 退出登录功能正常
- admin 用户可见管理员入口，普通用户不可见
- 管理员页面只读，无操作按钮
```

---

## Phase 6：优化和测试

### 关键词：`Phase6` / `优化` / `测试`

```
## 任务：App 整体优化和测试

### 1. 交互优化
- 所有列表页支持下拉刷新 + 上拉加载更多
- 网络错误时显示 Toast + 重试按钮
- 列表为空时显示空状态插画
- 图片加载中显示占位图
- 按钮防重复点击（loading 状态）

### 2. Token 生命周期
- 启动时检查 Token 有效性（调用 /api/auth/me）
- Token 过期自动跳登录页
- 登录后自动跳回上次页面

### 3. 样式统一
- 所有页面使用 uni.scss 中定义的变量
- 导航栏统一绿色背景白色文字
- TabBar 图标和颜色统一

### 4. H5 预览测试
- npm run dev:h5 启动后逐页检查
- 登录/注册/检测/问答/历史/知识库/管理员各功能是否正常
- 网络断开时错误处理是否正常

### 验收
- 所有 P0 功能在 H5 模式下正常运行
- 无控制台报错
- 交互流畅，无明显卡顿
```

---

## 使用方式

1. 用户给出关键词（如 "Phase1"）
2. AI 从本文档提取对应提示词
3. 用户复制到新 Task 执行开发
4. 完成后可在当前会话做 code review

**关键词速查**：

| 关键词 | Phase | 内容 |
|--------|-------|------|
| Phase1 / 基础框架 | 1 | 项目初始化、请求封装、Store、登录注册 |
| Phase2 / 检测流程 | 2 | 拍照检测、结果展示、病害档案、首页 |
| Phase3 / AI问答 | 3 | 聊天页面、图片传入、置信度、会话管理 |
| Phase4 / 历史 | 4 | 检测历史、知识库浏览 |
| Phase5 / 管理员 | 5 | 个人中心、管理员只读页面 |
| Phase6 / 优化 | 6 | 交互优化、Token生命周期、测试 |
