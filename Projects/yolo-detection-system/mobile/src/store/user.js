/**
 * 用户状态管理
 * token 用 uni.getStorageSync 持久化
 */
import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo } from '@/api/auth'

const TOKEN_KEY = 'token'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync(TOKEN_KEY) || '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },

  actions: {
    /** 设置 token 并持久化 */
    setToken(token) {
      this.token = token
      uni.setStorageSync(TOKEN_KEY, token)
    },

    /** 设置用户信息 */
    setUserInfo(info) {
      this.userInfo = info
    },

    /** 登录：调用 API 并存储 token */
    async login(loginForm) {
      const res = await loginApi(loginForm)
      const token = res.access_token
      if (!token) {
        throw new Error('登录失败，未返回 token')
      }
      this.setToken(token)
      this.userInfo = res.user || null
      return res
    },

    /** 拉取用户信息 */
    async fetchUserInfo() {
      if (!this.token) return null
      const res = await getUserInfo()
      this.userInfo = res
      return res
    },

    /** 清除登录态：清 token 与用户信息并移除本地缓存（不跳转） */
    clearAuth() {
      this.token = ''
      this.userInfo = null
      uni.removeStorageSync(TOKEN_KEY)
    },

    /** 退出登录：清除本地状态并跳转登录页 */
    logout() {
      this.clearAuth()
      uni.reLaunch({ url: '/pages/login/index' })
    }
  }
})
