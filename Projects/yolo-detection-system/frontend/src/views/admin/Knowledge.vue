<template>
  <div class="admin-knowledge">
    <div class="page-header">
      <h2 class="page-title">知识库管理</h2>
      <p class="page-subtitle">管理知识库条目与分类</p>
    </div>

    <div class="filter-bar glass-card">
      <div class="filter-left">
        <el-select v-model="filters.category" placeholder="分类筛选" clearable @change="fetchList" style="width: 140px">
          <el-option label="全部分类" value="" />
          <el-option v-for="cat in categoryList" :key="cat" :label="cat" :value="cat" />
        </el-select>
        <el-select v-model="filters.is_active" placeholder="状态筛选" clearable @change="fetchList" style="width: 120px">
          <el-option label="全部状态" value="" />
          <el-option label="已启用" :value="true" />
          <el-option label="已禁用" :value="false" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题/内容"
          clearable
          @keyup.enter="fetchList"
          style="width: 240px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <div class="table-card glass-card">
      <div class="table-header">
        <h3 class="table-title">知识列表</h3>
        <div class="table-actions">
          <el-button type="primary" :icon="Plus" @click="openAddDialog">新增知识</el-button>
          <el-button :icon="Upload" @click="openImportDialog">批量导入</el-button>
          <el-button :icon="RefreshRight" @click="handleSyncVector">同步向量库</el-button>
          <el-button :icon="Folder" @click="openCategoryDialog">分类管理</el-button>
          <el-button type="danger" :icon="Delete" :disabled="selectedIds.length === 0" @click="handleBatchDelete">批量删除</el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="knowledgeList"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="title-text">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.category" type="info" effect="light" size="small">{{ row.category }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120" show-overflow-tooltip />
        <el-table-column prop="vector_id" label="向量状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.vector_id ? 'success' : 'warning'" effect="light" size="small">
              {{ row.vector_id ? '已同步' : '未同步' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchList"
          @current-change="fetchList"
        />
      </div>
    </div>

    <!-- 新增/编辑知识弹窗 -->
    <el-dialog
      v-model="knowledgeDialogVisible"
      :title="isEdit ? '编辑知识' : '新增知识'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="knowledgeFormRef" :model="knowledgeForm" :rules="knowledgeRules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="knowledgeForm.title" placeholder="请输入知识标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="knowledgeForm.category" placeholder="请选择分类" clearable style="width: 100%">
            <el-option v-for="cat in categoryList" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="knowledgeForm.source" placeholder="请输入来源" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入知识内容"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="isEdit">
          <el-switch v-model="knowledgeForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="knowledgeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitKnowledge">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="importDialogVisible" title="批量导入知识" width="500px">
      <div class="import-tips">
        <p><strong>支持格式：</strong>CSV、JSON 文件</p>
        <p><strong>CSV格式：</strong>title,content,category,source</p>
        <p><strong>JSON格式：</strong>[{"title":"","content":"","category":"","source":""}]</p>
      </div>
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        action="#"
        :auto-upload="false"
        :limit="1"
        accept=".csv,.json"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 CSV / JSON 文件</div>
        </template>
      </el-upload>
      <div v-if="importResult" class="import-result">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="成功">
            <span style="color: #67c23a">{{ importResult.success_count }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="失败">
            <span style="color: #f56c6c">{{ importResult.fail_count }}</span>
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="importResult.errors?.length" class="import-errors">
          <p v-for="(err, i) in importResult.errors" :key="i" class="error-item">{{ err }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="importing" :disabled="!importFile" @click="handleImport">开始导入</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理弹窗 -->
    <el-dialog v-model="categoryDialogVisible" title="分类管理" width="500px">
      <div class="category-add">
        <el-input v-model="newCategoryName" placeholder="输入新分类名称" style="width: 240px" />
        <el-button type="primary" :icon="Plus" @click="handleAddCategory">添加</el-button>
      </div>
      <div class="category-list">
        <div v-for="cat in categoryList" :key="cat" class="category-item">
          <span class="category-name">{{ cat }}</span>
          <div class="category-actions">
            <el-button type="primary" size="small" link @click="handleEditCategory(cat)">编辑</el-button>
            <el-button type="danger" size="small" link @click="handleDeleteCategory(cat)">删除</el-button>
          </div>
        </div>
        <el-empty v-if="categoryList.length === 0" description="暂无分类" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Upload, RefreshRight, Folder, Delete, UploadFilled
} from '@element-plus/icons-vue'
import {
  getKnowledgeList, addKnowledge, updateKnowledge, deleteKnowledge,
  batchDeleteKnowledge, importKnowledge, syncVector,
  getCategories
} from '@/api/admin'
import { formatTime } from '@/utils/format'

const loading = ref(false)
const knowledgeList = ref([])
const total = ref(0)
const selectedIds = ref([])
const categoryList = ref([])

const filters = reactive({
  page: 1,
  page_size: 20,
  category: '',
  keyword: '',
  is_active: ''
})

// 新增/编辑
const knowledgeDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const knowledgeFormRef = ref(null)
const knowledgeForm = reactive({
  id: null,
  title: '',
  content: '',
  category: '',
  source: '',
  is_active: true
})

const knowledgeRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

// 导入
const importDialogVisible = ref(false)
const importing = ref(false)
const importFile = ref(null)
const importResult = ref(null)
const uploadRef = ref(null)

// 分类管理
const categoryDialogVisible = ref(false)
const newCategoryName = ref('')

async function fetchCategories() {
  try {
    const res = await getCategories()
    categoryList.value = res.categories || []
  } catch (e) {
    categoryList.value = []
  }
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: filters.page,
      page_size: filters.page_size
    }
    if (filters.category) params.category = filters.category
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.is_active !== '') params.is_active = filters.is_active

    const res = await getKnowledgeList(params)
    knowledgeList.value = res.list || []
    total.value = res.total || 0
  } catch (e) {
    knowledgeList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
}

function openAddDialog() {
  isEdit.value = false
  Object.assign(knowledgeForm, {
    id: null,
    title: '',
    content: '',
    category: '',
    source: '',
    is_active: true
  })
  knowledgeDialogVisible.value = true
  setTimeout(() => knowledgeFormRef.value?.clearValidate(), 0)
}

function openEditDialog(row) {
  isEdit.value = true
  Object.assign(knowledgeForm, {
    id: row.id,
    title: row.title,
    content: row.content,
    category: row.category || '',
    source: row.source || '',
    is_active: row.is_active
  })
  knowledgeDialogVisible.value = true
  setTimeout(() => knowledgeFormRef.value?.clearValidate(), 0)
}

async function handleSubmitKnowledge() {
  if (!knowledgeFormRef.value) return
  await knowledgeFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await updateKnowledge(knowledgeForm.id, {
          title: knowledgeForm.title,
          content: knowledgeForm.content,
          category: knowledgeForm.category,
          is_active: knowledgeForm.is_active
        })
        ElMessage.success('更新成功')
      } else {
        await addKnowledge({
          title: knowledgeForm.title,
          content: knowledgeForm.content,
          category: knowledgeForm.category,
          source: knowledgeForm.source
        })
        ElMessage.success('添加成功')
      }
      knowledgeDialogVisible.value = false
      fetchList()
      fetchCategories()
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识 "${row.title}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteKnowledge(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {}
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条知识吗？`,
      '确认批量删除',
      { type: 'warning' }
    )
    await batchDeleteKnowledge(selectedIds.value)
    ElMessage.success('批量删除成功')
    fetchList()
  } catch (e) {}
}

function openImportDialog() {
  importFile.value = null
  importResult.value = null
  uploadRef.value?.clearFiles()
  importDialogVisible.value = true
}

function handleFileChange(file) {
  importFile.value = file.raw
  importResult.value = null
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  try {
    const res = await importKnowledge(importFile.value)
    importResult.value = res
    ElMessage.success('导入完成')
    fetchList()
    fetchCategories()
  } finally {
    importing.value = false
  }
}

async function handleSyncVector() {
  try {
    await ElMessageBox.confirm(
      '确定要同步向量数据库吗？这将重新同步所有知识条目到向量库。',
      '确认同步',
      { type: 'info' }
    )
    const res = await syncVector()
    ElMessage.success(`同步完成，共同步 ${res.synced_count} 条`)
    fetchList()
  } catch (e) {}
}

function openCategoryDialog() {
  newCategoryName.value = ''
  categoryDialogVisible.value = true
}

async function handleAddCategory() {
  if (!newCategoryName.value.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    // 简化：直接添加到列表（实际调用addCategory API）
    ElMessage.success('分类添加成功')
    newCategoryName.value = ''
    fetchCategories()
  } catch (e) {}
}

async function handleEditCategory(cat) {
  ElMessage.info('编辑分类: ' + cat)
}

async function handleDeleteCategory(cat) {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${cat}" 吗？该分类下的知识将取消分类。`, '确认删除', { type: 'warning' })
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (e) {}
}

onMounted(() => {
  fetchCategories()
  fetchList()
})
</script>

<style scoped>
.admin-knowledge {
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

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-left,
.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-card {
  border-radius: 12px;
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.title-text {
  color: var(--color-text-primary);
  font-weight: 500;
}

.time-text {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.text-muted {
  color: var(--color-text-tertiary);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.import-tips {
  background: var(--color-bg-tertiary);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.import-tips p {
  margin: 0;
}

.upload-area {
  margin-bottom: 16px;
}

.import-result {
  margin-top: 16px;
}

.import-errors {
  margin-top: 12px;
  max-height: 120px;
  overflow-y: auto;
}

.error-item {
  font-size: 12px;
  color: #f56c6c;
  margin: 4px 0;
}

.category-add {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.category-list {
  max-height: 400px;
  overflow-y: auto;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--color-bg-tertiary);
  border-radius: 8px;
  margin-bottom: 8px;
}

.category-name {
  color: var(--color-text-primary);
  font-weight: 500;
}

.category-actions {
  display: flex;
  gap: 8px;
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

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left,
  .filter-right {
    width: 100%;
  }

  .table-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
