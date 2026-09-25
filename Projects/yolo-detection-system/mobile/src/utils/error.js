/**
 * 统一错误与登录过期处理
 */
import { useUserStore } from '@/store/user'

const TOKEN_KEY = 'token'
let isTokenRedirecting = false

/**
 * 统一展示错误信息
 * @param {Error} e - 捕获的错误对象
 * @param {string} fallback - 无 message 时展示的兜底文案
 * @returns {string} 实际展示的文案
 */
export function showError(e, fallback = '操作失败') {
  const msg = (e && e.message) || fallback
  console.error('[request error]', e)
  uni.showToast({ title: msg, icon: 'none' })
  return msg
}

/**
 * 处理 Token 失效：清登录态、单飞保护、已在登录页则跳过
 */
export function handleTokenExpired() {
  uni.removeStorageSync(TOKEN_KEY)
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  if (currentPage && currentPage.route === 'pages/login/index') return
  if (isTokenRedirecting) return
  isTokenRedirecting = true
  try {
    useUserStore().clearAuth()
  } catch (e) {
    // store 不可用时本地缓存已在上方清除
  }
  uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
  setTimeout(() => {
    isTokenRedirecting = false
    uni.reLaunch({ url: '/pages/login/index' })
  }, 1000)
}