/**
 * 请求封装
 * 基于后端响应规范：成功 code=0，业务错误 code=401/400 等（HTTP 状态码均为 200）
 * 功能：Token 自动注入、401 自动跳登录、错误提示
 */

// API 基地址：H5 通过 vite 代理转发（相对路径 /api），App 端使用环境变量配置
// #ifdef H5
const BASE_URL = '/api'
// #endif
// #ifndef H5
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api'
// #endif

// Token 在本地存储的 key
const TOKEN_KEY = 'token'

/**
 * 构造请求头（注入 Token）
 */
function buildHeader(customHeader = {}) {
  const token = uni.getStorageSync(TOKEN_KEY)
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...customHeader
  }
}

/**
 * 处理 Token 失效，清除并跳转登录
 */
function handleTokenExpired() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
  setTimeout(() => {
    uni.reLaunch({ url: '/pages/login/index' })
  }, 1000)
}

/**
 * 处理业务响应（code 判断）
 */
function handleBusinessResponse(resData, resolve, reject) {
  // 成功码 code=0（注意：不是 200）
  if (resData.code === 0) {
    resolve(resData.data)
    return
  }
  // Token 失效
  if (resData.code === 401) {
    handleTokenExpired()
    reject(new Error(resData.message || '登录已过期'))
    return
  }
  // 其他业务错误
  const msg = resData.message || '请求失败'
  uni.showToast({ title: msg, icon: 'none' })
  reject(new Error(msg))
}

/**
 * 通用请求
 * @param {Object} options - { url, method, data, header }
 * @returns {Promise}
 */
export function request(options) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: buildHeader(options.header),
      success: (res) => {
        // HTTP 状态码异常
        if (res.statusCode < 200 || res.statusCode >= 300) {
          const msg = `网络错误 ${res.statusCode}`
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
          return
        }
        handleBusinessResponse(res.data, resolve, reject)
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误，请检查网络', icon: 'none' })
        reject(err)
      }
    })
  })
}
