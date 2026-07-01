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
  return request.get('/knowledge/items', { params })
}

export function getKnowledgeItem(id) {
  return request.get(`/knowledge/items/${id}`)
}

export function getCategories() {
  return request.get('/knowledge/categories')
}
