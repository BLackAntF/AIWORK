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

export function exportHistory(params) {
  return request.get('/history/export', { params, responseType: 'blob' })
}

export function getHistoryReport(id) {
  return request.get(`/history/${id}/report`, { responseType: 'blob' })
}

export function downloadHistoryReportPdf(id) {
  return request.get(`/history/${id}/report/pdf`, { responseType: 'blob' })
}

export function shareHistory(id, expires_days = 7) {
  // base_url 让后端生成指向前端站点的分享链接（后端端口无法直接打开前端页面）
  return request.post(`/history/${id}/share`, {
    expires_days,
    base_url: window.location.origin
  })
}

export function getSharedResult(token) {
  return request.get(`/share/${token}`, { skipErrorMessage: true })
}
