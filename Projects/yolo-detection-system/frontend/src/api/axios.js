import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken } from '@/utils/storage'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 90000
})

request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    // 文件下载（CSV 等）不走业务响应体解析，直接返回完整响应以便读取响应头
    if (response.config.responseType === 'blob') {
      const blobType = response.data?.type || ''
      if (blobType.includes('application/json')) {
        return response.data.text().then((text) => {
          const res = JSON.parse(text)
          ElMessage.error(res.message || '请求失败')
          return Promise.reject(new Error(res.message || '请求失败'))
        })
      }
      return response
    }
    const res = response.data
    if (res.code === 0) {
      return res.data
    } else {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  (error) => {
    if (error.response?.status === 401 || error.response?.data?.code === 401) {
      import('@/utils/storage').then(({ removeToken, removeUser }) => {
        removeToken()
        removeUser()
      })
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
