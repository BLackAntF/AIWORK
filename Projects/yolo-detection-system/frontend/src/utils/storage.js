const TOKEN_KEY = 'yolo_token'
const USER_KEY = 'yolo_user'
const THEME_KEY = 'yolo_theme'
const VALID_THEMES = ['light', 'dark']

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getUser() {
  const userStr = localStorage.getItem(USER_KEY)
  try {
    return userStr ? JSON.parse(userStr) : null
  } catch {
    return null
  }
}

export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeUser() {
  localStorage.removeItem(USER_KEY)
}

export function clearAuth() {
  removeToken()
  removeUser()
}

export function getTheme() {
  const stored = localStorage.getItem(THEME_KEY)
  return VALID_THEMES.includes(stored) ? stored : null
}

export function setTheme(theme) {
  if (VALID_THEMES.includes(theme)) {
    localStorage.setItem(THEME_KEY, theme)
  }
}

export function removeTheme() {
  localStorage.removeItem(THEME_KEY)
}
