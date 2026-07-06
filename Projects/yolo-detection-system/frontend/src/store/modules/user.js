import { defineStore } from 'pinia'
import { login as loginApi, getUserInfo } from '@/api/auth'
import { setToken, getToken, removeToken } from '@/utils/storage'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    userInfo: null
  }),

  actions: {
    async login(loginForm) {
      const res = await loginApi(loginForm)
      const token = res.access_token
      if (!token) {
        throw new Error('登录失败，未返回token')
      }
      this.token = token
      setToken(token)
      this.userInfo = res.user || null
      return res
    },

    async fetchUserInfo() {
      if (!this.token) return
      try {
        const res = await getUserInfo()
        this.userInfo = res
        return res
      } catch (e) {
        this.logout()
        throw e
      }
    },

    logout() {
      this.token = ''
      this.userInfo = null
      removeToken()
    }
  }
})
