/**
 * 文件上传封装
 * 基于 uni.uploadFile，用于图片上传
 */
import { handleTokenExpired } from '@/utils/error'

// API 基地址：H5 通过 vite 代理转发（相对路径 /api），App 端使用环境变量配置
// #ifdef H5
const BASE_URL = '/api'
// #endif
// #ifndef H5
const BASE_URL = import.meta.env.VITE_API_BASE_URL
// #endif
const TOKEN_KEY = 'token'

/**
 * 构造上传请求头（注入 Token）
 */
function buildUploadHeader() {
  const token = uni.getStorageSync(TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * 处理上传响应
 * @returns {boolean} 是否为 Token 失效
 */
function handleUploadResponse(resData, resolve, reject) {
  if (resData.code === 0) {
    resolve(resData.data)
    return false
  }
  if (resData.code === 401) {
    handleTokenExpired()
    reject(new Error(resData.message || '登录已过期'))
    return true
  }
  const msg = resData.message || '上传失败'
  uni.showToast({ title: msg, icon: 'none' })
  reject(new Error(msg))
  return false
}

/**
 * 上传文件
 * @param {string} url - 接口路径（如 /detect/image）
 * @param {string} filePath - 本地文件路径
 * @param {Object} formData - 额外表单数据
 * @param {string} name - 文件字段名，默认 image
 * @returns {Promise}
 */
export function uploadFile(url, filePath, formData = {}, name = 'image') {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: BASE_URL + url,
      filePath,
      name,
      formData,
      header: buildUploadHeader(),
      success: (res) => {
        let resData
        try {
          resData = JSON.parse(res.data)
        } catch (e) {
          uni.showToast({ title: '响应解析失败', icon: 'none' })
          reject(new Error('响应解析失败'))
          return
        }
        handleUploadResponse(resData, resolve, reject)
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败，请重试', icon: 'none' })
        reject(err)
      }
    })
  })
}
