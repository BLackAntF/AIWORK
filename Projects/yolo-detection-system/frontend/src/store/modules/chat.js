import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    detectedClassId: null,
    diseaseName: '',
    detectionContext: '',
    detectionResult: null
  }),
  actions: {
    setDetectionContext(context) {
      this.detectedClassId = context.class_id || context.detected_class_id
      this.diseaseName = context.disease_name || ''
      this.detectionContext = context.detection_context || ''
    },
    setDetectionResult(result) {
      this.detectionResult = result
    },
    clearContext() {
      this.detectedClassId = null
      this.diseaseName = ''
      this.detectionContext = ''
      this.detectionResult = null
    }
  }
})
