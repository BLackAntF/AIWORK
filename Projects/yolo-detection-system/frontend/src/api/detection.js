import request from './axios'

export function detectImage(file, saveHistory = true, modelId = null) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('save_history', saveHistory)
  if (modelId) formData.append('model_id', modelId)
  return request.post('/detect/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function detectBatch(files, saveHistory = true, modelId = null) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  formData.append('save_history', saveHistory)
  if (modelId) formData.append('model_id', modelId)
  return request.post('/detect/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  })
}
