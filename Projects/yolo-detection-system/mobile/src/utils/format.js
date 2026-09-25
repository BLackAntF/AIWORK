/**
 * 工具函数 - 格式化相关
 */

// 静态资源基地址：去掉 API 前缀 /api（与网页端一致）
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api').replace('/api', '')

/**
 * 获取完整的图片 URL
 * @param {string} path - 图片路径
 * @returns {string} 完整 URL
 */
export function getFullUrl(path) {
	if (!path) return ''
	if (path.startsWith('http://') || path.startsWith('https://')) {
		return path
	}
	if (path.startsWith('/')) {
		return BASE_URL + path
	}
	return BASE_URL + '/' + path
}
