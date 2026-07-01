import { defineStore } from 'pinia'
import { getTheme, setTheme as setStorageTheme } from '@/utils/storage'

const VALID_THEMES = ['light', 'dark']

function validateTheme(theme) {
  return VALID_THEMES.includes(theme) ? theme : 'light'
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: validateTheme(getTheme())
  }),

  getters: {
    isDark: (state) => state.theme === 'dark'
  },

  actions: {
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      this.applyTheme()
    },

    setTheme(theme) {
      this.theme = validateTheme(theme)
      this.applyTheme()
    },

    applyTheme() {
      this.theme = validateTheme(this.theme)
      if (this.theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark')
      } else {
        document.documentElement.removeAttribute('data-theme')
      }
      setStorageTheme(this.theme)
    },

    initTheme() {
      this.theme = validateTheme(getTheme())
      this.applyTheme()
    }
  }
})
