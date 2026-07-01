<template>
  <div class="image-upload">
    <div
      class="upload-area glass-card"
      :class="{ 'drag-over': isDragOver, 'has-image': imageUrl }"
      @click="triggerUpload"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        class="file-input"
        @change="handleFileChange"
        hidden
      />
      <div v-if="imageUrl && showPreview" class="preview-wrapper">
        <img :src="imageUrl" alt="preview" class="preview-image" />
        <button class="remove-btn" @click.stop="removeImage">
          <el-icon><Close /></el-icon>
        </button>
      </div>
      <div v-else class="upload-placeholder">
        <el-icon :size="48" class="upload-icon"><UploadFilled /></el-icon>
        <p class="upload-text">点击或拖拽图片到此处上传</p>
        <p v-if="tipText" class="upload-tip">{{ tipText }}</p>
        <p class="upload-info">支持 {{ accept }} 格式，大小不超过 {{ maxSize }}MB</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Close } from '@element-plus/icons-vue'

const props = defineProps({
  accept: {
    type: String,
    default: 'image/*'
  },
  maxSize: {
    type: Number,
    default: 10
  },
  showPreview: {
    type: Boolean,
    default: true
  },
  tipText: {
    type: String,
    default: ''
  },
  modelValue: {
    type: [Object, String],
    default: null
  }
})

const emit = defineEmits(['change', 'upload', 'update:modelValue'])

const fileInput = ref(null)
const isDragOver = ref(false)
const imageUrl = ref('')
const currentFile = ref(null)

function triggerUpload() {
  if (!imageUrl.value) {
    fileInput.value?.click()
  }
}

function validateFile(file) {
  const maxSizeBytes = props.maxSize * 1024 * 1024
  if (file.size > maxSizeBytes) {
    ElMessage.error(`图片大小不能超过 ${props.maxSize}MB`)
    return false
  }
  if (props.accept !== 'image/*') {
    const acceptTypes = props.accept.split(',').map(t => t.trim())
    const isValidType = acceptTypes.some(type => {
      if (type.endsWith('/*')) {
        return file.type.startsWith(type.replace('/*', '/'))
      }
      return file.type === type
    })
    if (!isValidType) {
      ElMessage.error('图片格式不正确')
      return false
    }
  }
  return true
}

function handleFile(file) {
  if (!validateFile(file)) return

  currentFile.value = file
  emit('change', file)
  emit('update:modelValue', file)

  if (props.showPreview) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imageUrl.value = e.target?.result
    }
    reader.readAsDataURL(file)
  }

  emit('upload', file)
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) {
    handleFile(file)
  }
  e.target.value = ''
}

function handleDragOver() {
  isDragOver.value = true
}

function handleDragLeave() {
  isDragOver.value = false
}

function handleDrop(e) {
  isDragOver.value = false
  const file = e.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) {
    handleFile(file)
  } else {
    ElMessage.error('请上传图片文件')
  }
}

function removeImage() {
  imageUrl.value = ''
  currentFile.value = null
  emit('change', null)
  emit('update:modelValue', null)
}

watch(() => props.modelValue, (val) => {
  if (!val) {
    imageUrl.value = ''
    currentFile.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.upload-area {
  position: relative;
  width: 100%;
  min-height: 200px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.upload-area:hover {
  border-color: var(--color-accent);
  box-shadow: 0 0 20px var(--color-accent-glow);
}

.upload-area.drag-over {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  transform: scale(1.02);
}

.upload-area.has-image {
  border-style: solid;
}

.upload-placeholder {
  text-align: center;
  padding: 40px 20px;
}

.upload-icon {
  color: var(--color-accent);
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.upload-info {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.preview-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.remove-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.remove-btn:hover {
  background: var(--color-error);
  transform: scale(1.1);
}

.file-input {
  display: none;
}
</style>
