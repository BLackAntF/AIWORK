/**
 * 检测相关接口
 */
import { uploadFile } from './upload'

/**
 * 图片检测
 * @param {string} filePath - 本地图片路径
 * @param {boolean} saveHistory - 是否保存到历史记录
 * @returns {Promise}
 */
export function detectImage(filePath, saveHistory = true) {
  return uploadFile('/detect/image', filePath, { save_history: saveHistory }, 'image')
}
