<template>
  <div class="admin-config">
    <div class="page-header">
      <h2 class="page-title">系统配置</h2>
      <p class="page-subtitle">管理系统参数与模型配置</p>
    </div>

    <!-- 系统配置 -->
    <div class="section-card glass-card">
      <div class="section-header">
        <h3 class="section-title">系统参数配置</h3>
      </div>
      <el-table v-loading="configLoading" :data="configList" style="width: 100%">
        <el-table-column prop="key" label="配置键" width="240">
          <template #default="{ row }">
            <code class="config-key">{{ row.key }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="配置值" min-width="200">
          <template #default="{ row }">
            <el-input
              v-if="editingKey === row.key"
              v-model="row._editValue"
              size="small"
              @keyup.enter="saveConfig(row)"
            />
            <span v-else class="config-value">{{ row.value }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="editingKey === row.key"
              type="success"
              size="small"
              link
              @click="saveConfig(row)"
            >
              保存
            </el-button>
            <el-button
              v-else
              type="primary"
              size="small"
              link
              @click="startEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="editingKey === row.key"
              type="info"
              size="small"
              link
              @click="cancelEdit(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 模型管理 -->
    <div class="section-card glass-card">
      <div class="section-header">
        <h3 class="section-title">模型管理</h3>
        <el-button type="primary" :icon="Plus" @click="openUploadModel">上传新模型</el-button>
      </div>
      <el-table v-loading="modelLoading" :data="modelList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="模型名称" min-width="200">
          <template #default="{ row }">
            <div class="model-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_active" type="success" effect="light" size="small" class="active-tag">
                当前激活
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="120" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" size="small">
              {{ row.is_active ? '激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_active"
              type="primary"
              size="small"
              link
              @click="handleSetActive(row)"
            >
              设为激活
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 上传模型弹窗 -->
    <el-dialog v-model="uploadDialogVisible" title="上传新模型" width="500px">
      <el-form :model="modelForm" label-width="100px">
        <el-form-item label="模型名称" required>
          <el-input v-model="modelForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型文件" required>
          <el-upload
            ref="modelUploadRef"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            accept=".pt,.pth,.onnx"
            :on-change="handleModelFileChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽模型文件到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 .pt / .pth / .onnx 格式</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" :disabled="!modelForm.file" @click="handleUploadModel">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled } from '@element-plus/icons-vue'
import {
  getConfigList, updateConfig,
  getModelList, uploadModel, setActiveModel
} from '@/api/admin'
import { formatTime } from '@/utils/format'

const configLoading = ref(false)
const modelLoading = ref(false)
const configList = ref([])
const modelList = ref([])
const editingKey = ref('')

// 上传模型
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const modelUploadRef = ref(null)
const modelForm = reactive({
  name: '',
  file: null
})

async function fetchConfig() {
  configLoading.value = true
  try {
    const res = await getConfigList()
    configList.value = (res.configs || []).map(item => ({
      ...item,
      _editValue: item.value
    }))
  } catch (e) {
    configList.value = []
  } finally {
    configLoading.value = false
  }
}

async function fetchModels() {
  modelLoading.value = true
  try {
    const res = await getModelList()
    modelList.value = res.models || []
  } catch (e) {
    modelList.value = []
  } finally {
    modelLoading.value = false
  }
}

function startEdit(row) {
  row._editValue = row.value
  editingKey.value = row.key
}

function cancelEdit(row) {
  row._editValue = row.value
  editingKey.value = ''
}

async function saveConfig(row) {
  try {
    await updateConfig(row.key, row._editValue)
    row.value = row._editValue
    editingKey.value = ''
    ElMessage.success('配置更新成功')
  } catch (e) {
    row._editValue = row.value
  }
}

function openUploadModel() {
  modelForm.name = ''
  modelForm.file = null
  modelUploadRef.value?.clearFiles()
  uploadDialogVisible.value = true
}

function handleModelFileChange(file) {
  modelForm.file = file.raw
}

async function handleUploadModel() {
  if (!modelForm.name || !modelForm.file) {
    ElMessage.warning('请填写模型名称并选择文件')
    return
  }
  uploading.value = true
  try {
    await uploadModel(modelForm.file, modelForm.name)
    ElMessage.success('模型上传成功')
    uploadDialogVisible.value = false
    fetchModels()
  } finally {
    uploading.value = false
  }
}

async function handleSetActive(row) {
  try {
    await ElMessageBox.confirm(
      `确定要将模型 "${row.name}" 设为激活状态吗？`,
      '确认切换',
      { type: 'warning' }
    )
    await setActiveModel(row.id)
    ElMessage.success('模型已激活')
    fetchModels()
  } catch (e) {}
}

onMounted(() => {
  fetchConfig()
  fetchModels()
})
</script>

<style scoped>
.admin-config {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.section-card {
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.config-key {
  background: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--color-accent);
}

.config-value {
  color: var(--color-text-primary);
  font-weight: 500;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.active-tag {
  margin-left: 8px;
}

.time-text {
  color: var(--color-text-secondary);
  font-size: 13px;
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--color-bg-tertiary);
  --el-table-border-color: var(--color-border);
  --el-table-text-color: var(--color-text-primary);
  --el-table-header-text-color: var(--color-text-secondary);
}

:deep(.el-table th.el-table__cell) {
  background-color: var(--color-bg-tertiary) !important;
  font-weight: 600;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
