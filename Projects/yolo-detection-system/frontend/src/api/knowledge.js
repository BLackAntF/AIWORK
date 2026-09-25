import request from './axios'

export function askQuestion(data) {
  return request.post('/knowledge/ask', data)
}

export function getChatHistory(params) {
  return request.get('/knowledge/history', { params })
}

export function getSessions() {
  return request.get('/knowledge/sessions')
}

export function deleteSession(id) {
  return request.delete(`/knowledge/session/${id}`)
}

export function getKnowledgeItems(params) {
  return request.get('/knowledge/list', { params })
}

export function getKnowledgeItem(id) {
  return request.get(`/knowledge/${id}`)
}

export function getCategories() {
  return request.get('/knowledge/category-list')
}

export function getKnowledgeTags() {
  return request.get('/knowledge/tags')
}

export function createKnowledgeTag(data) {
  return request.post('/knowledge/tags', data)
}

export function updateKnowledgeTag(id, data) {
  return request.put(`/knowledge/tags/${id}`, data)
}

export function deleteKnowledgeTag(id) {
  return request.delete(`/knowledge/tags/${id}`)
}

export function getRelatedKnowledge(id, params) {
  return request.get(`/knowledge/${id}/related`, { params })
}

export function addFavorite(id) {
  return request.post(`/knowledge/${id}/favorite`)
}

export function removeFavorite(id) {
  return request.delete(`/knowledge/${id}/favorite`)
}

export function getMyFavorites(params) {
  return request.get('/knowledge/favorites', { params })
}

export function getFavoriteStatus(id) {
  return request.get(`/knowledge/${id}/favorite-status`)
}

export function uploadKnowledge(data) {
  return request.post('/knowledge/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
