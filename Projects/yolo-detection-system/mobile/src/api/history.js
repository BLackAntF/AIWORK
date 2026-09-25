/**
 * 检测历史接口
 */
import { request } from './request'

/** 获取检测历史列表（分页） */
export function getHistoryList(params) {
  return request({ url: '/history', data: params })
}

/** 获取检测历史详情 */
export function getHistoryDetail(id) {
  return request({ url: `/history/${id}` })
}

/** 删除检测历史记录 */
export function deleteHistory(id) {
  return request({ url: `/history/${id}`, method: 'DELETE' })
}
