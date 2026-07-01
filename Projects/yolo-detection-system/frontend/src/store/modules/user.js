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
      this.token = res.access_token
      setToken(res.access_token)
      this.userInfo = res.user
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
