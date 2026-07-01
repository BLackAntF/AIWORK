import request from './axios'

// ========== 用户管理 ==========

export function getUserList(params) {
  return request.get('/admin/users', { params })
}

export function getUserDetail(id) {
  return request.get(`/admin/users/${id}`)
}

export function updateUserStatus(id, is_active) {
  return request.put(`/admin/users/${id}/status`, { is_active })
}

export function updateUserRole(id, role) {
  return request.put(`/admin/users/${id}/role`, { role })
}

export function deleteUser(id) {
  return request.delete(`/admin/users/${id}`)
}

export function getUserStats() {
  return request.get('/admin/users/stats')
}

// ========== 知识库管理 ==========

export function getKnowledgeList(params) {
  return request.get('/admin/knowledge', { params })
}

export function addKnowledge(data) {
  return request.post('/admin/knowledge', data)
}

export function updateKnowledge(id, data) {
  return request.put(`/admin/knowledge/${id}`, data)
}

export function deleteKnowledge(id) {
  return request.delete(`/admin/knowledge/${id}`)
}

export function batchDeleteKnowledge(ids) {
  return request.delete('/admin/knowledge', { data: { ids } })
}

export function importKnowledge(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/admin/knowledge/import', formData)
}

export function syncVector() {
  return request.post('/admin/knowledge/sync-vector')
}

// ========== 分类管理 ==========

export function getCategories() {
  return request.get('/admin/categories')
}

export function addCategory(name) {
  return request.post('/admin/categories', { name })
}

export function updateCategory(id, name) {
  return request.put(`/admin/categories/${id}`, { name })
}

export function deleteCategory(id) {
  return request.delete(`/admin/categories/${id}`)
}

// ========== 检测记录管理 ==========

export function getDetectionList(params) {
  return request.get('/admin/detections', { params })
}

export function getDetectionDetail(id) {
  return request.get(`/admin/detections/${id}`)
}

export function deleteDetection(id) {
  return request.delete(`/admin/detections/${id}`)
}

export function batchDeleteDetection(ids) {
  return request.delete('/admin/detections', { data: { ids } })
}

export function getDetectionStats(params) {
  return request.get('/admin/detections/stats', { params })
}

// ========== 数据统计 ==========

export function getDashboardStats() {
  return request.get('/admin/stats/dashboard')
}

export function getUsersTrend(days = 7) {
  return request.get('/admin/stats/users-trend', { params: { days } })
}

export function getDetectionsTrend(days = 7) {
  return request.get('/admin/stats/detections-trend', { params: { days } })
}

export function getKnowledgeStats() {
  return request.get('/admin/stats/knowledge')
}

export function exportStats(type, start_date, end_date) {
  return request.get('/admin/stats/export', {
    params: { type, start_date, end_date },
    responseType: 'blob'
  })
}

// ========== 系统配置 ==========

export function getConfigList() {
  return request.get('/admin/config')
}

export function updateConfig(key, value) {
  return request.put(`/admin/config/${key}`, { value })
}

// ========== 模型管理 ==========

export function getModelList() {
  return request.get('/admin/models')
}

export function uploadModel(file, name) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  return request.post('/admin/models', formData)
}

export function setActiveModel(model_id) {
  return request.put('/admin/models/active', { model_id })
}
