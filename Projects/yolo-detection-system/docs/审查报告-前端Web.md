# Web 前端代码审查报告（日期 2026-10-30）

审查范围：`frontend/src` 下 views/（含 admin/）、components/、api/、store/、utils/、router/。只读审查，未修改任何代码。

## 1. 死代码（未使用的组件/导入/变量/函数）

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| components/DetectionResult.vue（整文件） | 中 | 组件在全项目中无任何 import/使用 | 删除或接入 Detect.vue |
| components/ImageUpload.vue（整文件） | 中 | 组件在全项目中无任何 import/使用（Detect.vue 自行实现了上传） | 删除或重构 Detect.vue 复用它 |
| api/admin.js#29 | 低 | `getUserStats()` 导出但无调用 | 删除 |
| api/admin.js#101/105/109 | 中 | `addCategory/updateCategory/deleteCategory` 导出但无调用（admin/Knowledge.vue 分类管理是假实现，见第 3 节） | 让分类管理真正调用这些 API |
| utils/storage.js#18/27/35/51 | 低 | `getUser/setUser/clearAuth/removeTheme` 无调用；USER_KEY 从不写入，getUser 永远返回 null | 删除或在 user store 中真正使用 setUser 持久化 |
| utils/format.js#43 | 低 | `formatDuration()` 无调用 | 删除 |
| utils/format.js#22 | 低 | `formatFileSize()` 无调用（HistoryDetail.vue#413 本地重复实现了一份） | 删除 HistoryDetail 本地版本，统一用 utils |
| views/Login.vue#109 | 低 | `loginForm.remember`「记住我」勾选后无任何逻辑使用 | 实现记住我或移除该 checkbox |
| views/admin/Detections.vue#181 | 低 | 导入 `Search` 图标但模板未使用 | 移除导入 |
| views/History.vue#292-293 | 低 | `handleResize` 是空函数，监听本身无意义 | 删除注册与函数（另见内存泄漏节） |
| views/History.vue#285 | 低 | `isMobile` computed 读 `window.innerWidth`，无响应式依赖，永远只在首次求值 | 删除或改为监听式 |
| components/ParticlesBackground.vue#162 | 低 | `watch(() => themeStore.isDark, () => {})` 空 watch | 删除 |
| views/admin/Dashboard.vue#323 | 低 | `emptyData` 不是合法 echarts option，属无效配置 | 删除该字段 |
| views/HistoryDetail.vue#452-454 | 低 | `handleRedetect` 是「开发中」桩函数 | 实现或移除入口 |
| store/modules/chat.js#8/#16-18 | 低 | `detectionResult` 存入 store 后无消费方（Knowledge.vue 只读 context 字段） | 删除或改用 |

## 2. 内存泄漏（定时器/监听/echarts 未清理）

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| views/History.vue#289 | 中 | `window.addEventListener('resize', handleResize)` 注册后组件无 onUnmounted，永不解绑（且 handler 为空函数） | 直接删除该监听，或在 onUnmounted 中 removeEventListener |
| views/Knowledge.vue#509 | 中 | `typewriterTimer = setInterval(...)` 仅在 stopTypewriter 中清理，组件无 onUnmounted；用户在打字机效果进行中离开页面，定时器永久运行并持续渲染 markdown | 增加 `onUnmounted(stopTypewriter)` |
| views/admin/DataScreen.vue#303-310 | 低 | clockTimer、3 个 echarts 实例、resize/fullscreenchange 均已正确清理，无问题 | 无需处理（正面示例） |
| views/admin/Stats.vue#242-247 / Dashboard.vue#471-477 / ModelCompare.vue#174-177 | 低 | echarts dispose 与 resize 解绑均已正确处理 | 无需处理 |
| views/admin/ModelCompare.vue#140-144 | 低 | `renderDistChart` 直接 `echarts.init`，若将来被二次调用会在同一 DOM 上重复 init（echarts 警告+旧实例泄漏） | init 前先 `distChart?.dispose()`（参考 DataScreen 的 initChart） |
| views/HistoryDetail.vue#466-467 | 低 | `URL.createObjectURL(blob)` 后 `window.open`，URL 永不 revoke；弹窗被拦截时提前 return 也未 revoke | 弹窗拦截分支补 revoke；可用 load 事件后延时 revoke |
| components/ParticlesBackground.vue / Layout/*.vue / RichEditor.vue | 低 | rAF、window 监听、tiptap 实例均正确清理 | 无需处理 |
| store/modules/notification.js#44 | 低 | 轮询 timer 依赖 AppHeader/AdminHeader 的 onUnmounted 停止；store 本身无 $onDispose，若未来在非 Header 场景 startPolling 会泄漏 | 当前可用，建议在 store 内用 scope 管理 |

## 3. 重复请求 / 缺失 loading 与错误处理

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| views/admin/Knowledge.vue#742-765 | 高 | 分类「添加/编辑/删除」只弹成功提示、刷新列表，**未调用任何 API**（代码注释自承"简化"），用户误以为操作成功 | 接入 addCategory/updateCategory/deleteCategory（api/admin.js 已备好） |
| views/admin/Stats.vue#214-215 | 高 | `handleExport` 中 `exportStats` 因 axios 拦截器对 blob 返回**完整 response 对象**，`new Blob([blob])` 得到的是 response 的字符串化内容，导出的 CSV 实际为 "[object Object]" | 使用 `const res = await exportStats(...); new Blob([res.data])`，并与 SamplePool/History 的写法统一 |
| views/Login.vue#139-142、Register.vue#177-180、Profile.vue#365-368 等 | 中 | axios 拦截器已 ElMessage.error，本地 catch 又弹一次 `error.message`，同一失败出现**两条相同错误提示** | 本地 catch 不再重复弹，或给请求加 skipErrorMessage |
| views/Profile.vue#322 | 中 | `getHistoryList({ page: 1, pageSize: 1000 })` 参数名错误（后端约定 page_size），只拿到默认第一页，`stats.today/image` 统计口径错误；且 `res.items || res.data?.items` 与拦截器已解包为 data 的事实不符（应为 res.list） | 改为 `{ page: 1, page_size: 1000 }` 并读 `res.list`；更好的做法是后端提供用户统计接口 |
| views/admin/Knowledge.vue#587-615、#656-668、#779-796 | 中 | handleSubmitKnowledge/handleImport/handleUpload 只有 try/finally 无 catch，依赖拦截器弹错但异常会继续抛出为未处理 rejection（submit 场景还在 validate 回调内） | 补 catch 或确认拦截器已提示后显式吞掉 |
| views/admin/Config.vue#230-244 | 低 | handleUploadModel 无 catch，同上 | 同上 |
| views/admin/Detections.vue#258-266 | 低 | handleViewDetail 接口失败时静默降级用行数据，用户无感知数据可能不全 | 至少 console.warn 或轻提示 |
| views/admin/Dashboard.vue#408-448 / Stats.vue#207-209 / ModelCompare.vue#156-158 | 低 | 图表数据加载失败仅 console.error 或静默置空，页面无任何反馈 | 图表区给空态/错误态提示 |
| views/Notifications.vue#147-148、Knowledge.vue#270 | 低 | 列表加载失败本地弹错，与拦截器提示重复 | 统一由拦截器处理 |

## 4. 可复用逻辑重复

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| admin/Stats.vue#215-222、admin/SamplePool.vue#234-243、History.vue#389-394、HistoryDetail.vue#485-492 | 中 | `createObjectURL + a.download + revokeObjectURL` blob 下载逻辑在 4 处重复，且写法不一致（Stats 还有 bug，History 未 appendChild） | 抽 `utils/download.js: downloadBlob(blob, filename)` 统一替换 |
| views/HistoryDetail.vue#463-464、views/Knowledge.vue#354 | 中 | 手动 `VITE_API_BASE_URL.replace('/api','') || 'http://localhost:5000'` 拼 baseUrl，与 `utils/format.js#getFullUrl` 逻辑重复且不一致 | 收敛到 getFullUrl 或抽 getBaseUrl |
| views/History.vue#295-304、views/Knowledge.vue#244-254、views/HistoryDetail.vue#413 | 低 | formatDateTime/formatTime（相对时间）/formatFileSize 各页面本地重复实现，utils/format.js 已有等价函数 | 统一使用 utils/format |
| components/Layout/AppLayout.vue#79-81、AdminLayout.vue#79-81、AppHeader.vue#85-87、AdminHeader.vue#98-100 | 低 | `checkMobile`（innerWidth<768 + resize 监听）在 4 个组件重复 | 抽 composable `useIsMobile()` |

## 5. echarts dispose / resize 解绑

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| views/admin/Dashboard.vue、Stats.vue、DataScreen.vue、ModelCompare.vue | 低 | 四个图表页均在 onUnmounted 中 dispose 实例并 removeEventListener('resize')，处理规范 | 无重大问题；ModelCompare 重复 init 风险见第 2 节 |

## 6. 路由守卫与权限

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| router/index.js#173-186 | 中 | admin 权限仅校验前端 `userInfo.role === 'admin'`，且 userInfo 不持久化（刷新后需重新 fetch）；前端校验可被绕过，必须确认后端每个 /admin 接口都做了服务端鉴权 | 后端强制鉴权（本次为前端审查，仅提示）；前端可在 login 后持久化 userInfo |
| router/index.js | 低 | 无 404 catch-all 路由，访问未知路径渲染空白页 | 增加 `{ path: '/:pathMatch(.*)*' }` NotFound 页 |
| router/index.js#163 | 低 | requiresAuth 只判断 token 是否存在，不校验有效性；过期 token 进入页面后靠各接口 401 跳转 | 可接受；如需更好体验可在守卫中校验 exp |
| store/modules/user.js#6-9 | 中 | userInfo 不持久化：刷新后非 admin 页面 userInfo 为 null，Header 用户名显示「用户」占位，只有 Profile 页会触发 fetchUserInfo | 登录后 setUser 持久化，或 AppLayout onMounted 统一 fetchUserInfo |
| api/axios.js#47-53 | 低 | 401 处理用动态 import('@/utils/storage')（顶部已静态引入 getToken，风格不一致）；跳转 /login 未带 redirect 参数 | 静态导入 removeToken/removeUser；push 时带 `query: { redirect: route.fullPath }` |

## 7. XSS 风险（v-html / markdown）

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| utils/markdown.js#6 | 高 | `marked.setOptions({ sanitize: false })` 且未引入 DOMPurify；marked 会原样透传内容中的 HTML/`<script onxxx>` 等 | 渲染前用 DOMPurify.sanitize(marked.parse(content)) |
| views/Knowledge.vue#89 | 高 | AI 回答 `v-html="msg.displayHtml"`，内容为 LLM 输出+知识库检索文本，间接包含用户可上传的知识内容 → 存储型 XSS 链路 | 同上，渲染前消毒 |
| views/KnowledgeDetail.vue#53 | 高 | 知识详情 `v-html="renderedContent"`；知识支持用户上传（knowledge/upload）仅经人工审核，审核遗漏即 XSS | 同上 |
| views/admin/Knowledge.vue#224 | 高 | 除 XSS 外，`renderMarkdown` **未在 script 中导入**（仅 import 了 formatTime），打开「查看」弹窗会抛 ReferenceError 导致渲染失败 | 补 `import { renderMarkdown } from '@/utils/markdown'` 并消毒 |
| components/RichEditor.vue#45 | 低 | 编辑器产出 HTML 直接入库，回显走上述 v-html 链路 | 依赖第 7 节统一消毒即可 |

## 8. 硬编码密钥/地址

| 文件#行号 | 等级 | 描述 | 建议 |
|---|---|---|---|
| utils/format.js#63、views/Knowledge.vue#354、views/HistoryDetail.vue#464 | 低 | 硬编码回退地址 `http://localhost:5000`（3 处）；未发现硬编码密钥/token | 统一抽 `getBaseUrl()`，回退值保留但集中管理 |
| views/HistoryDetail.vue#464 | 低 | 正则替换 `src="/static/` 拼报告 HTML，依赖后端模板路径约定 | 可接受，建议后端直接输出绝对路径 |

---

## 建议优先处理 Top 5

1. **views/admin/Knowledge.vue#224**：`renderMarkdown` 未导入，知识「查看」弹窗必崩（ReferenceError）——功能级 bug，立即修复。
2. **views/admin/Stats.vue#214**：导出报表把 axios response 对象写入 Blob，下载的 CSV 内容是 "[object Object]"——导出功能完全不可用。
3. **utils/markdown.js + 三处 v-html（Knowledge.vue#89、KnowledgeDetail.vue#53、admin/Knowledge.vue#224）**：marked 未消毒 + 知识内容用户可上传，存在存储型 XSS 链路，引入 DOMPurify 统一消毒。
4. **views/admin/Knowledge.vue#742-765**：分类增/删/改是假实现（提示成功但未调 API），api/admin.js 中对应接口已成死代码——管理端功能造假。
5. **views/History.vue#289 + views/Knowledge.vue#509**：空 resize 监听永不解绑、打字机 setInterval 离开页面不清理——两处实际内存泄漏，且都只需几行修复。
