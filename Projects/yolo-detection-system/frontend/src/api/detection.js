import request from './axios'

export function detectImage(file, saveHistory = true) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('save_history', saveHistory)
  return request.post('/detect/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function detectVideo(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/detect/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
