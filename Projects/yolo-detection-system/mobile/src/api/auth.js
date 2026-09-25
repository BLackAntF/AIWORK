/**
 * 认证相关接口
 */
import { request } from './request'

/** 用户登录 */
export function login(data) {
  return request({ url: '/auth/login', method: 'POST', data })
}

/** 用户注册 */
export function register(data) {
  return request({ url: '/auth/register', method: 'POST', data })
}

/** 获取当前登录用户信息 */
export function getUserInfo() {
  return request({ url: '/auth/me' })
}

/** 修改密码 */
export function changePassword(data) {
  return request({ url: '/auth/password', method: 'PUT', data })
}
