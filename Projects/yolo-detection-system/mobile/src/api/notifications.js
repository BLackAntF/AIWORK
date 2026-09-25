/**
 * 站内通知接口
 */
import { request } from './request'

/** 获取通知列表（分页） */
export function getNotifications(params) {
  return request({ url: '/notifications', data: params })
}

/** 获取未读通知数 */
export function getUnreadCount() {
  return request({ url: '/notifications/unread-count' })
}

/** 标记单条通知已读 */
export function markNotificationRead(id) {
  return request({ url: `/notifications/${id}/read`, method: 'PUT' })
}

/** 全部标记已读 */
export function markAllNotificationsRead() {
  return request({ url: '/notifications/read-all', method: 'PUT' })
}

/** 删除通知 */
export function deleteNotification(id) {
  return request({ url: `/notifications/${id}`, method: 'DELETE' })
}
