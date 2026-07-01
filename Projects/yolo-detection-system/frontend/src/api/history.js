import request from './axios'

export function getHistoryList(params) {
  return request.get('/history', { params })
}

export function getHistoryDetail(id) {
  return request.get(`/history/${id}`)
}

export function deleteHistory(id) {
  return request.delete(`/history/${id}`)
}

export function batchDeleteHistory(ids) {
  return request.delete('/history', { data: { ids } })
}
