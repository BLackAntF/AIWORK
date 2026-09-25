<template>
  <div class="knowledge-list-page">
    <div class="page-header">
      <h1 class="page-title">知识库</h1>
      <p class="page-subtitle">了解番茄病害识别与防治知识</p>
    </div>

    <div class="search-section glass-card">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索知识文章..."
        clearable
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
      <el-button type="warning" :icon="Upload" @click="openUploadDialog" class="upload-btn">上传知识</el-button>
    </div>

    <div class="filter-section">
      <div class="category-tabs">
        <el-radio-group v-model="selectedCategory" @change="handleCategoryChange">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="disease">病害识别</el-radio-button>
          <el-radio-button value="prevention">防治方法</el-radio-button>
          <el-radio-button value="cultivation">栽培技术</el-radio-button>
          <el-radio-button value="basic">基础知识</el-radio-button>
        </el-radio-group>
      </div>
      <div class="tag-filter" v-if="tagList.length > 0">
        <span class="filter-label">标签:</span>
        <div class="tag-chips">
          <el-tag
            v-for="tag in tagList"
            :key="tag.id"
            :color="selectedTagId === tag.id ? tag.color : ''"
            :effect="selectedTagId === tag.id ? 'dark' : 'light'"
            class="tag-chip"
            @click="handleTagClick(tag)"
          >
            {{ tag.name }}
          </el-tag>
          <el-tag
            v-if="selectedTagId"
            type="info"
            class="clear-tag"
            @click="handleTagClick(null)"
          >
            清除标签
          </el-tag>
        </div>
      </div>
    </div>

    <div v-loading="loading" class="content-section">
      <div v-if="knowledgeList.length === 0 && !loading" class="empty-state">
        <el-icon :size="64" class="empty-icon"><Document /></el-icon>
        <p class="empty-text">暂无相关知识</p>
        <el-button type="primary" @click="resetFilters">重置筛选</el-button>
      </div>

      <div v-else class="knowledge-grid">
        <div
          v-for="item in knowledgeList"
          :key="item.id"
          class="knowledge-card glass-card hover-lift"
          @click="goToDetail(item.id)"
        >
          <div class="card-header">
            <el-tag :type="getCategoryType(item.category)" effect="light" size="small">
              {{ getCategoryLabel(item.category) }}
            </el-tag>
            <span class="views-count">
              <el-icon><View /></el-icon>
              {{ item.views || 0 }}
            </span>
          </div>
          <h3 class="card-title">{{ item.title }}</h3>
          <div class="card-tags" v-if="item.tags?.length">
            <el-tag
              v-for="tag in item.tags.slice(0, 2)"
              :key="tag.id"
              :color="tag.color"
              effect="dark"
              size="small"
              class="card-tag"
            >
              {{ tag.name }}
            </el-tag>
            <span v-if="item.tags.length > 2" class="more-tags">+{{ item.tags.length - 2 }}</span>
          </div>
          <p class="card-summary">{{ item.summary || item.content?.slice(0, 100) + '...' || '暂无摘要' }}</p>
          <div class="card-footer">
            <span class="publish-time">{{ formatTime(item.created_at) }}</span>
          </div>
        </div>
      </div>

      <div v-if="total > 0" class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 上传知识弹窗 -->
    <el-dialog v-model="uploadDialogVisible" title="上传知识文件" width="550px">
      <el-alert
        title="上传的知识需经管理员审核后才会公开展示"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px;"
      />
      <el-form label-width="70px">
        <el-form-item label="文件">
          <el-upload
            class="upload-area"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            accept=".txt,.md,.docx,.pdf"
            :on-change="handleUploadFileChange"
            :on-remove="handleUploadRemove"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持格式：TXT、MD、DOCX、PDF</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="uploadForm.category" placeholder="选择分类（可选）" clearable style="width: 100%">
            <el-option label="病害识别" value="病害识别" />
            <el-option label="防治方法" value="防治方法" />
            <el-option label="栽培技术" value="栽培技术" />
            <el-option label="基础知识" value="基础知识" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="uploadForm.source" placeholder="输入来源（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" :disabled="!uploadFile" @click="handleUpload">开始上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Document, View, Upload, UploadFilled } from '@element-plus/icons-vue'
import { getKnowledgeItems, getKnowledgeTags, uploadKnowledge } from '@/api/knowledge'

const router = useRouter()

const loading = ref(false)
const knowledgeList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchKeyword = ref('')
const selectedCategory = ref('')
const tagList = ref([])
const selectedTagId = ref(null)

const categoryMap = {
  '病害识别': { label: '病害识别', type: 'danger' },
  '防治方法': { label: '防治方法', type: 'warning' },
  '栽培技术': { label: '栽培技术', type: 'success' },
  '基础知识': { label: '基础知识', type: 'primary' },
  '养护知识': { label: '养护知识', type: 'primary' },
  '病害防治': { label: '病害防治', type: 'danger' }
}

function categoryStyle(category) {
  return categoryMap[category] || { label: category, type: 'info' }
}

function getCategoryLabel(category) {
  return categoryMap[category]?.label || category || '其他'
}

function getCategoryType(category) {
  return categoryMap[category]?.type || 'info'
}

function getCategoryTagType(category) {
  return categoryStyle(category).type
}

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

async function fetchKnowledgeList() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    if (selectedTagId.value) {
      params.tag_id = selectedTagId.value
    }

    const res = await getKnowledgeItems(params)
    const items = res.items || res.data?.items || []
    knowledgeList.value = items.map(item => ({
      ...item,
      summary: item.summary || (item.content ? item.content.replace(/<[^>]+>/g, '').slice(0, 120) + '...' : '')
    }))
    total.value = res.total || res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载知识列表失败')
    knowledgeList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchTags() {
  try {
    const res = await getKnowledgeTags()
    tagList.value = res || []
  } catch (e) {
    tagList.value = []
  }
}

function handleTagClick(tag) {
  if (selectedTagId.value === (tag ? tag.id : null)) {
    selectedTagId.value = null
  } else {
    selectedTagId.value = tag ? tag.id : null
  }
  currentPage.value = 1
  fetchKnowledgeList()
}

function handleSearch() {
  currentPage.value = 1
  fetchKnowledgeList()
}

function handleCategoryChange() {
  currentPage.value = 1
  fetchKnowledgeList()
}

function handlePageChange() {
  fetchKnowledgeList()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleSizeChange() {
  currentPage.value = 1
  fetchKnowledgeList()
}

function resetFilters() {
  selectedCategory.value = ''
  searchKeyword.value = ''
  selectedTagId.value = null
  currentPage.value = 1
  fetchKnowledgeList()
}

function goToDetail(id) {
  router.push(`/knowledge-detail/${id}`)
}

// 文件上传
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadFile = ref(null)
const uploadForm = ref({ category: '', source: '' })

function openUploadDialog() {
  uploadFile.value = null
  uploadForm.value = { category: '', source: '' }
  uploadDialogVisible.value = true
}

function handleUploadFileChange(file) {
  uploadFile.value = file.raw
}

function handleUploadRemove() {
  uploadFile.value = null
}

async function handleUpload() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    if (uploadForm.value.category) formData.append('category', uploadForm.value.category)
    if (uploadForm.value.source) formData.append('source', uploadForm.value.source)

    await uploadKnowledge(formData)
    ElMessage.success('上传成功，等待管理员审核')
    uploadDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchTags()
  fetchKnowledgeList()
})
</script>

<style scoped>
.knowledge-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 15px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.search-section {
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  flex: 1;
  max-width: 600px;
  margin: 0 auto;
}

.upload-btn {
  flex-shrink: 0;
}

.upload-area {
  width: 100%;
}

:deep(.search-input .el-input__wrapper) {
  border-radius: var(--radius-md) 0 0 var(--radius-md);
}

:deep(.search-input .el-input-group__append) {
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}

:deep(.search-input .el-input-group__append .el-button) {
  color: #fff;
  background: transparent;
  border: none;
}

:deep(.search-input .el-input-group__append .el-button:hover) {
  color: #fff;
}

.filter-section {
  margin-bottom: 24px;
}

.category-tabs {
  display: flex;
  justify-content: center;
}

:deep(.category-tabs .el-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

:deep(.category-tabs .el-radio-button__inner) {
  border-radius: var(--radius-md);
  border-left: 1px solid var(--color-border);
}

:deep(.category-tabs .el-radio-button:first-child .el-radio-button__inner) {
  border-radius: var(--radius-md);
}

:deep(.category-tabs .el-radio-button:last-child .el-radio-button__inner) {
  border-radius: var(--radius-md);
}

.tag-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
  flex-shrink: 0;
}

.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-chip {
  cursor: pointer;
  transition: all 0.2s;
  margin: 0 !important;
}

.tag-chip:hover {
  opacity: 0.85;
  transform: scale(1.02);
}

.clear-tag {
  cursor: pointer;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.card-tag {
  margin: 0 !important;
}

.more-tags {
  font-size: 12px;
  color: var(--color-text-tertiary);
  line-height: 24px;
}

.content-section {
  min-height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  color: var(--color-text-tertiary);
  opacity: 0.5;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin-bottom: 20px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.knowledge-card {
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.views-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.publish-time {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

@media (max-width: 1024px) {
  .knowledge-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .knowledge-list-page {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .knowledge-grid {
    grid-template-columns: 1fr;
  }

  .category-tabs :deep(.el-radio-group) {
    width: 100%;
  }

  .category-tabs :deep(.el-radio-button) {
    flex: 1;
  }

  .category-tabs :deep(.el-radio-button__inner) {
    width: 100%;
    border-radius: var(--radius-md);
    margin: 0 !important;
    border-left: 1px solid var(--color-border) !important;
  }

  :deep(.category-tabs .el-radio-button:first-child .el-radio-button__inner) {
    border-radius: var(--radius-md);
  }

  :deep(.category-tabs .el-radio-button:last-child .el-radio-button__inner) {
    border-radius: var(--radius-md);
  }
}
</style>