/**
 * 知识库与 AI 问答接口
 */
import { request } from './request'

/** AI 问答（支持图片上下文） */
export function askQuestion(data) {
  return request({ url: '/knowledge/ask', method: 'POST', data })
}

/** 获取会话列表 */
export function getSessionList() {
  return request({ url: '/knowledge/sessions' })
}

/** 获取会话聊天历史 */
export function getChatHistory(sessionId, params = {}) {
  return request({ url: '/knowledge/history', data: { session_id: sessionId, ...params } })
}

/** 删除会话 */
export function deleteSession(sessionId) {
  return request({ url: `/knowledge/session/${sessionId}`, method: 'DELETE' })
}

/** 获取知识库列表 */
export function getKnowledgeList(params) {
  return request({ url: '/knowledge/list', data: params })
}

/** 获取知识详情 */
export function getKnowledgeDetail(id) {
  return request({ url: `/knowledge/${id}` })
}

/** 获取相关知识 */
export function getRelatedKnowledge(id, params) {
  return request({ url: `/knowledge/${id}/related`, data: params })
}

/** 获取分类列表 */
export function getCategories() {
  return request({ url: '/knowledge/category-list' })
}

/** 获取病害档案列表 */
export function getDiseaseProfileList(params) {
  return request({ url: '/disease-profiles', data: params })
}

/** 按病害类别 ID 获取档案详情 */
export function getDiseaseProfile(classId) {
  return request({ url: `/disease-profiles/${classId}` })
}
