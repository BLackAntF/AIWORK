# 番茄叶片病害智能诊断平台 - 移动端 App 开发文档

> **版本**：v1.0
> **日期**：2026-07-14
> **关联文档**：PRD.md v2.0、APP-需求文档.md
> **技术框架**：uni-app（Vue 3 + Composition API）

---

## 1. 开发环境搭建

### 1.1 环境要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Node.js | ≥18.0 | LTS 版本 |
| HBuilderX | ≥3.8 | uni-app 官方 IDE（推荐） |
| Vue CLI | 可选 | 命令行方式创建 |

### 1.2 项目初始化

**方式一：HBuilderX 创建（推荐）**

1. 打开 HBuilderX → 文件 → 新建 → 项目 → uni-app
2. 选择 Vue 3 模板
3. 项目路径：`yolo-detection-system/mobile`

**方式二：CLI 创建**

```bash
npx degit dcloudio/uni-preset-vue#vite-ts mobile
cd mobile
npm install
```

### 1.3 目录结构

```
mobile/
├── pages/                      # 页面
│   ├── index/index.vue         # 首页（TabBar）
│   ├── detect/index.vue        # 拍照检测（TabBar）
│   ├── chat/index.vue          # AI问答（TabBar）
│   ├── history/index.vue       # 检测历史（TabBar）
│   ├── history/detail.vue      # 历史详情
│   ├── mine/index.vue          # 我的（TabBar）
│   ├── login/index.vue         # 登录
│   ├── register/index.vue      # 注册
│   ├── archive/detail.vue      # 病害档案详情
│   ├── knowledge/list.vue      # 知识库列表
│   ├── knowledge/detail.vue    # 知识详情
│   └── admin/                  # 管理员页面（只读）
│       ├── users.vue
│       ├── pending.vue
│       ├── logs.vue
│       └── dashboard.vue
├── components/                 # 公共组件
│   ├── DiseaseCard.vue         # 病害档案卡片
│   ├── DetectionResult.vue     # 检测结果展示
│   ├── ChatBubble.vue          # 聊天气泡
│   ├── ConfidenceTag.vue       # 置信度标签
│   ├── EmptyState.vue          # 空状态
│   └── LoadingOverlay.vue      # 加载遮罩
├── api/                        # API 接口
│   ├── request.js              # 请求封装
│   ├── auth.js                 # 认证接口
│   ├── detect.js               # 检测接口
│   ├── knowledge.js            # 知识/问答接口
│   ├── history.js              # 历史接口
│   └── admin.js                # 管理员接口
├── store/                      # Pinia 状态
│   ├── index.js
│   ├── user.js                 # 用户状态
│   └── chat.js                 # 问答状态
├── static/                     # 静态资源
│   ├── tabbar/                 # TabBar 图标
│   └── images/                 # 图片资源
├── utils/                      # 工具函数
│   ├── format.js               # 格式化
│   ├── compress.js             # 图片压缩
│   └── storage.js              # 本地存储
├── App.vue                     # 应用入口
├── main.js                     # 主入口
├── pages.json                  # 页面路由配置
├── manifest.json               # 应用配置
└── uni.scss                    # 全局样式变量
```

---

## 2. 核心配置

### 2.1 pages.json（页面路由 + TabBar）

```json
{
  "pages": [
    { "path": "pages/index/index", "style": { "navigationBarTitleText": "首页" } },
    { "path": "pages/detect/index", "style": { "navigationBarTitleText": "病害检测" } },
    { "path": "pages/chat/index", "style": { "navigationBarTitleText": "AI问答" } },
    { "path": "pages/history/index", "style": { "navigationBarTitleText": "检测历史" } },
    { "path": "pages/mine/index", "style": { "navigationBarTitleText": "我的" } },
    { "path": "pages/login/index", "style": { "navigationBarTitleText": "登录", "navigationStyle": "custom" } },
    { "path": "pages/register/index", "style": { "navigationBarTitleText": "注册" } },
    { "path": "pages/archive/detail", "style": { "navigationBarTitleText": "病害档案" } },
    { "path": "pages/history/detail", "style": { "navigationBarTitleText": "检测详情" } },
    { "path": "pages/knowledge/list", "style": { "navigationBarTitleText": "知识库" } },
    { "path": "pages/knowledge/detail", "style": { "navigationBarTitleText": "知识详情" } },
    { "path": "pages/admin/users", "style": { "navigationBarTitleText": "用户管理" } },
    { "path": "pages/admin/pending", "style": { "navigationBarTitleText": "待审核" } },
    { "path": "pages/admin/logs", "style": { "navigationBarTitleText": "操作日志" } },
    { "path": "pages/admin/dashboard", "style": { "navigationBarTitleText": "数据看板" } }
  ],
  "globalStyle": {
    "navigationBarBackgroundColor": "#4CAF50",
    "navigationBarTextStyle": "white",
    "backgroundColor": "#F5F5F5"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#4CAF50",
    "backgroundColor": "#FFFFFF",
    "list": [
      { "pagePath": "pages/index/index", "text": "首页", "iconPath": "static/tabbar/home.png", "selectedIconPath": "static/tabbar/home-active.png" },
      { "pagePath": "pages/detect/index", "text": "检测", "iconPath": "static/tabbar/camera.png", "selectedIconPath": "static/tabbar/camera-active.png" },
      { "pagePath": "pages/chat/index", "text": "问答", "iconPath": "static/tabbar/chat.png", "selectedIconPath": "static/tabbar/chat-active.png" },
      { "pagePath": "pages/history/index", "text": "历史", "iconPath": "static/tabbar/clock.png", "selectedIconPath": "static/tabbar/clock-active.png" },
      { "pagePath": "pages/mine/index", "text": "我的", "iconPath": "static/tabbar/user.png", "selectedIconPath": "static/tabbar/user-active.png" }
    ]
  }
}
```

### 2.2 manifest.json（应用配置）

```json
{
  "name": "番茄病害诊断",
  "appid": "__UNI__TOMATODISEASE",
  "versionName": "1.0.0",
  "versionCode": 100,
  "app-plus": {
    "modules": {
      "Camera": {}
    },
    "distribute": {
      "android": {
        "minSdkVersion": 26
      },
      "ios": {
        "minimumOSVersion": "12.0"
      }
    }
  }
}
```

### 2.3 uni.scss（全局样式变量）

```scss
// 主题色
$primary-color: #4CAF50;
$warning-color: #FF9800;
$danger-color: #F44336;
$info-color: #2196F3;
$gray-color: #9E9E9E;

// 文字大小
$font-size-sm: 24rpx;
$font-size-base: 28rpx;
$font-size-lg: 32rpx;
$font-size-xl: 36rpx;

// 间距
$spacing-xs: 8rpx;
$spacing-sm: 16rpx;
$spacing-base: 24rpx;
$spacing-lg: 32rpx;
$spacing-xl: 48rpx;

// 圆角
$radius-sm: 8rpx;
$radius-base: 12rpx;
$radius-lg: 16rpx;
```

---

## 3. 请求封装

### 3.1 api/request.js

```javascript
const BASE_URL = 'http://127.0.0.1:5000/api'  // 开发环境

export function request(options) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.header || {})
      },
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.reLaunch({ url: '/pages/login/index' })
          reject(new Error('登录已过期'))
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          if (res.data.code === 200) {
            resolve(res.data.data)
          } else {
            uni.showToast({ title: res.data.message || '请求失败', icon: 'none' })
            reject(new Error(res.data.message))
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      }
    })
  })
}

export function uploadFile(url, filePath, formData) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.uploadFile({
      url: BASE_URL + url,
      filePath,
      name: 'image',
      formData,
      header: {
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      success: (res) => {
        const data = JSON.parse(res.data)
        if (data.code === 200) {
          resolve(data.data)
        } else {
          reject(new Error(data.message))
        }
      },
      fail: reject
    })
  })
}
```

### 3.2 API 接口定义

**api/auth.js**
```javascript
import { request } from './request'

export const login = (data) => request({ url: '/auth/login', method: 'POST', data })
export const register = (data) => request({ url: '/auth/register', method: 'POST', data })
export const getUserInfo = () => request({ url: '/auth/me' })
export const changePassword = (data) => request({ url: '/auth/password', method: 'PUT', data })
```

**api/detect.js**
```javascript
import { uploadFile } from './request'

export const detectImage = (filePath) => uploadFile('/detect/image', filePath, {})
```

**api/knowledge.js**
```javascript
import { request } from './request'

export const askQuestion = (data) => request({ url: '/knowledge/ask', method: 'POST', data })
export const getSessionList = () => request({ url: '/knowledge/sessions' })
export const getChatHistory = (sessionId) => request({ url: '/knowledge/history', data: { session_id: sessionId } })
export const deleteSession = (sessionId) => request({ url: `/knowledge/session/${sessionId}`, method: 'DELETE' })
export const getKnowledgeList = (params) => request({ url: '/knowledge/list', data: params })
export const getKnowledgeDetail = (id) => request({ url: `/knowledge/${id}` })
export const getRelatedKnowledge = (id) => request({ url: `/knowledge/${id}/related` })
export const getCategories = () => request({ url: '/knowledge/categories' })
```

**api/history.js**
```javascript
import { request } from './request'

export const getHistoryList = (params) => request({ url: '/history', data: params })
export const getHistoryDetail = (id) => request({ url: `/history/${id}` })
export const deleteHistory = (id) => request({ url: `/history/${id}`, method: 'DELETE' })
```

**api/admin.js**
```javascript
import { request } from './request'

export const getUsers = (params) => request({ url: '/admin/users', data: params })
export const getPendingKnowledge = (params) => request({ url: '/admin/knowledge/pending', data: params })
export const getLogs = (params) => request({ url: '/admin/logs', data: params })
export const getDashboardStats = () => request({ url: '/admin/stats/dashboard' })
```

---

## 4. 状态管理

### 4.1 store/user.js

```javascript
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: null
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },
  actions: {
    setToken(token) {
      this.token = token
      uni.setStorageSync('token', token)
    },
    setUserInfo(info) {
      this.userInfo = info
    },
    logout() {
      this.token = ''
      this.userInfo = null
      uni.removeStorageSync('token')
      uni.reLaunch({ url: '/pages/login/index' })
    }
  }
})
```

### 4.2 store/chat.js

```javascript
import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    currentSessionId: null,
    messages: [],
    sessions: []
  }),
  actions: {
    setSession(sessionId) {
      this.currentSessionId = sessionId
      this.messages = []
    },
    addMessage(msg) {
      this.messages.push(msg)
    },
    setSessions(list) {
      this.sessions = list
    }
  }
})
```

---

## 5. 核心页面开发

### 5.1 登录页（pages/login/index.vue）

```vue
<template>
  <view class="login-page">
    <view class="logo-section">
      <image src="/static/images/logo.png" mode="aspectFit" class="logo" />
      <text class="title">番茄病害诊断</text>
    </view>
    <view class="form-section">
      <input v-model="form.username" placeholder="用户名" class="input" />
      <input v-model="form.password" type="password" placeholder="密码" class="input" />
      <button @click="handleLogin" :loading="loading" class="btn-primary">登录</button>
      <view class="register-link" @click="goRegister">没有账号？去注册</view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '@/api/auth'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
    return
  }
  loading.value = true
  try {
    const res = await login(form.value)
    userStore.setToken(res.access_token)
    uni.switchTab({ url: '/pages/index/index' })
  } catch (e) {
    // request.js 已处理错误提示
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/register/index' })
}
</script>
```

### 5.2 检测页（pages/detect/index.vue）

```vue
<template>
  <view class="detect-page">
    <!-- 图片选择区 -->
    <view class="upload-section" v-if="!imageUrl">
      <view class="upload-placeholder" @click="chooseImage">
        <text class="upload-icon">+</text>
        <text class="upload-text">点击拍照或选择图片</text>
      </view>
    </view>

    <!-- 图片预览 -->
    <view class="preview-section" v-else>
      <image :src="imageUrl" mode="widthFix" class="preview-image" />
      <view class="preview-actions">
        <button size="mini" @click="chooseImage">重新选择</button>
        <button type="primary" size="mini" @click="handleDetect" :loading="detecting">开始检测</button>
      </view>
    </view>

    <!-- 检测结果 -->
    <view class="result-section" v-if="result">
      <image :src="result.result_image_url" mode="widthFix" class="result-image" />
      <view v-for="(item, idx) in result.detections" :key="idx" class="detection-item">
        <text class="disease-name">{{ item.disease_name }}</text>
        <text class="confidence">置信度: {{ (item.confidence * 100).toFixed(1) }}%</text>
        <DiseaseCard v-if="item.profile" :profile="item.profile" />
      </view>
      <button type="primary" @click="goChat" class="btn-ask">咨询AI</button>
    </view>

    <LoadingOverlay v-if="detecting" text="正在检测中..." />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { detectImage } from '@/api/detect'
import DiseaseCard from '@/components/DiseaseCard.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const imageUrl = ref('')
const imagePath = ref('')
const detecting = ref(false)
const result = ref(null)

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sourceType: ['camera', 'album'],
    success: (res) => {
      imagePath.value = res.tempFilePaths[0]
      imageUrl.value = res.tempFilePaths[0]
      result.value = null
    }
  })
}

async function handleDetect() {
  detecting.value = true
  try {
    const data = await detectImage(imagePath.value)
    result.value = data
  } catch (e) {
    uni.showToast({ title: '检测失败，请重试', icon: 'none' })
  } finally {
    detecting.value = false
  }
}

function goChat() {
  uni.switchTab({ url: '/pages/chat/index' })
  // 通过全局事件传递检测图片
  uni.$emit('detect-to-chat', { imageUrl: result.value?.result_image_url })
}
</script>
```

### 5.3 AI 问答页（pages/chat/index.vue）

```vue
<template>
  <view class="chat-page">
    <!-- 消息列表 -->
    <scroll-view scroll-y class="message-list" :scroll-top="scrollTop">
      <view v-for="(msg, idx) in messages" :key="idx" class="message-item">
        <ChatBubble :message="msg" />
      </view>
      <view v-if="aiThinking" class="thinking-indicator">
        <text>AI 正在思考...</text>
      </view>
    </scroll-view>

    <!-- 快捷问题 -->
    <view class="quick-questions" v-if="messages.length === 0">
      <view v-for="q in quickQuestions" :key="q" class="quick-item" @click="sendQuestion(q)">
        {{ q }}
      </view>
    </view>

    <!-- 检测图片预览（传入问答） -->
    <view class="context-image" v-if="contextImage">
      <image :src="contextImage" mode="aspectFill" class="ctx-img" />
      <text class="ctx-label">检测图片已带入</text>
      <text class="ctx-remove" @click="contextImage = ''">×</text>
    </view>

    <!-- 输入区 -->
    <view class="input-section">
      <input v-model="inputText" placeholder="输入问题..." class="chat-input" maxlength="500" />
      <button type="primary" size="mini" @click="sendQuestion()" :disabled="!inputText || aiThinking">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { askQuestion } from '@/api/knowledge'
import { useChatStore } from '@/store/chat'
import ChatBubble from '@/components/ChatBubble.vue'

const chatStore = useChatStore()
const inputText = ref('')
const messages = ref([])
const aiThinking = ref(false)
const scrollTop = ref(0)
const contextImage = ref('')
const sessionId = ref(null)

const quickQuestions = [
  '这个病严重吗？',
  '怎么防治？',
  '用什么药剂？',
  '多久能治好？'
]

onMounted(() => {
  // 监听检测页传入的图片
  uni.$on('detect-to-chat', (data) => {
    contextImage.value = data.imageUrl || ''
  })
})

async function sendQuestion(question) {
  const text = question || inputText.value
  if (!text || aiThinking.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  await scrollToBottom()

  // 请求 AI
  aiThinking.value = true
  try {
    const data = await askQuestion({
      question: text,
      session_id: sessionId.value,
      image_url: contextImage.value || undefined
    })
    sessionId.value = data.session_id
    // AI 回答（含置信度列表）
    messages.value.push({ role: 'assistant', content: data.answer, items: data.items })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，回答失败，请重试', items: [] })
  } finally {
    aiThinking.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  scrollTop.value = 99999
}
</script>
```

---

## 6. 公共组件

### 6.1 DiseaseCard.vue（病害档案卡片）

```vue
<template>
  <view class="disease-card" @click="goDetail">
    <view class="card-header">
      <text class="card-title">{{ profile.disease_name }}</text>
    </view>
    <view class="card-body">
      <view class="info-row"><text class="label">诱因：</text><text>{{ profile.cause }}</text></view>
      <view class="info-row"><text class="label">症状：</text><text>{{ profile.symptoms }}</text></view>
      <view class="info-row"><text class="label">防治：</text><text>{{ profile.treatment }}</text></view>
      <view class="info-row" v-if="profile.medicines">
        <text class="label">推荐药剂：</text>
        <view class="tag-list">
          <text v-for="med in profile.medicines" :key="med" class="med-tag">{{ med }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({ profile: { type: Object, required: true } })

function goDetail() {
  uni.navigateTo({ url: `/pages/archive/detail?id=${props.profile.id}` })
}
</script>
```

### 6.2 ChatBubble.vue（聊天气泡）

```vue
<template>
  <view class="chat-bubble" :class="message.role">
    <text v-if="message.role === 'user'" class="bubble-content">{{ message.content }}</text>
    <view v-else class="bubble-content ai-content">
      <view v-if="message.items && message.items.length > 0" class="answer-list">
        <view v-for="(item, idx) in message.items" :key="idx" class="answer-item">
          <text class="answer-text">{{ item.content }}</text>
          <ConfidenceTag :level="item.confidence" />
        </view>
      </view>
      <text v-else>{{ message.content }}</text>
    </view>
  </view>
</template>

<script setup>
import ConfidenceTag from './ConfidenceTag.vue'
defineProps({ message: { type: Object, required: true } })
</script>
```

### 6.3 ConfidenceTag.vue（置信度标签）

```vue
<template>
  <text class="confidence-tag" :class="level">{{ labels[level] }}</text>
</template>

<script setup>
defineProps({ level: { type: String, default: 'low' } })
const labels = { high: '高可信', medium: '中可信', low: '仅供参考' }
</script>

<style scoped>
.confidence-tag { font-size: 20rpx; padding: 2rpx 12rpx; border-radius: 6rpx; }
.high { background: #E8F5E9; color: #4CAF50; }
.medium { background: #FFF3E0; color: #FF9800; }
.low { background: #F5F5F5; color: #9E9E9E; }
</style>
```

---

## 7. 图片压缩

**utils/compress.js**

```javascript
export function compressImage(filePath, quality = 80) {
  return new Promise((resolve) => {
    uni.compressImage({
      src: filePath,
      quality,
      success: (res) => resolve(res.tempFilePath),
      fail: () => resolve(filePath)  // 压缩失败用原图
    })
  })
}
```

在检测页上传前调用：
```javascript
const compressedPath = await compressImage(imagePath.value, 60)
const data = await detectImage(compressedPath)
```

---

## 8. 后端适配说明

App 与 Web 共用后端 API，后端**无需新增接口**。以下是需要确认的适配点：

| 适配点 | 说明 | 状态 |
|--------|------|------|
| CORS 配置 | 后端需允许 App 请求（uni-app App 端无 CORS 限制，H5 调试时需配置） | 需确认 |
| 图片上传字段名 | 后端 `/api/detect/image` 接收字段名需与 App 上传 `name` 一致 | 需确认为 `image` |
| AI 问答图片传入 | `/api/knowledge/ask` 需支持 `image_url` 参数（多模态） | 需后端支持 |
| 置信度返回 | AI 问答返回格式需包含 `items[].confidence` | 需后端支持 |

---

## 9. 开发顺序建议

### Phase 1：基础框架（P0 核心）
1. 创建 uni-app 项目，配置 pages.json 和 manifest.json
2. 封装 request.js 和 API 接口
3. 实现 Pinia store（user + chat）
4. 开发登录/注册页

### Phase 2：检测流程（P0 核心）
5. 开发检测页（拍照/相册/上传/结果展示）
6. 开发病害档案卡片组件
7. 开发病害档案详情页
8. 图片压缩工具

### Phase 3：AI 问答（P0 核心）
9. 开发 AI 问答页（消息列表/输入/发送）
10. 开发 ChatBubble 和 ConfidenceTag 组件
11. 实现检测图片传入问答
12. 实现快捷问题

### Phase 4：历史和知识库（P1-P2）
13. 开发检测历史列表和详情
14. 开发知识库列表和详情（只读）

### Phase 5：管理员端（P2）
15. 开发管理员只读页面
16. 管理员入口权限控制

### Phase 6：优化和测试
17. 下拉刷新/上拉加载
18. 空状态/错误处理
19. 真机测试（Android + iOS）

---

## 10. 常见问题

### Q: uni-app App 端是否有 CORS 限制？
A: App 端（非 H5）没有 CORS 限制，直接请求后端即可。H5 调试时需要后端配置 CORS 或使用代理。

### Q: 相机权限如何处理？
A: `uni.chooseImage` 会自动请求相机权限。Android 需在 manifest.json 中声明 `Camera` 模块。

### Q: 图片上传用什么方式？
A: 使用 `uni.uploadFile`，不是 `uni.request`。注意 `name` 参数要和后端 Flask `request.files[name]` 一致。

### Q: Pinia 在 uni-app 中如何使用？
A: 与 Web 端 Vue 3 完全一致，`npm install pinia` 后在 main.js 中注册即可。
