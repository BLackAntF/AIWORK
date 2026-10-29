/**
 * 检测相关接口
 */
import { uploadFile } from './upload'

/**
 * 图片检测
 * @param {string} filePath - 本地图片路径
 * @param {boolean} saveHistory - 是否保存到历史记录
 * @param {number|null} modelId - 指定模型 ID（仅管理员）
 * @returns {Promise}
 */
export function detectImage(filePath, saveHistory = true, modelId = null) {
  const formData = { save_history: saveHistory }
  if (modelId) formData.model_id = modelId
  return uploadFile('/detect/image', filePath, formData, 'file')
}
