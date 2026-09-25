/**
 * 管理员接口（App 端只读）
 */
import { request } from './request'

/** 获取用户列表 */
export function getUsers(params) {
  return request({ url: '/admin/users', data: params })
}

/** 获取待审核知识列表 */
export function getPendingKnowledge(params) {
  return request({ url: '/admin/knowledge/pending', data: params })
}

/** 获取操作日志列表 */
export function getLogs(params) {
  return request({ url: '/admin/logs', data: params })
}

/** 获取数据看板统计 */
export function getDashboardStats() {
  return request({ url: '/admin/stats/dashboard' })
}
