<template>
  <div class="knowledge-detail-page">
    <div v-loading="loading" class="detail-container">
      <div v-if="!loading && !knowledge" class="not-found">
        <el-icon :size="64" class="not-found-icon"><DocumentDelete /></el-icon>
        <h2 class="not-found-title">知识不存在</h2>
        <p class="not-found-text">该知识文章可能已被删除或移动</p>
        <el-button type="primary" @click="goBack">返回知识库</el-button>
      </div>

      <template v-else-if="knowledge">
        <div class="article-container glass-card">
          <div class="article-header">
            <el-tag :type="getCategoryType(knowledge.category)" effect="light">
              {{ getCategoryLabel(knowledge.category) }}
            </el-tag>
            <span class="views-count">
              <el-icon><View /></el-icon>
              {{ knowledge.views || 0 }} 次阅读
            </span>
          </div>

          <h1 class="article-title">{{ knowledge.title }}</h1>

          <div class="article-tags" v-if="knowledge.tags?.length">
            <el-tag
              v-for="tag in knowledge.tags"
              :key="tag.id"
              :color="tag.color"
              effect="dark"
              size="small"
              class="article-tag"
            >
              {{ tag.name }}
            </el-tag>
          </div>

          <div class="article-meta">
            <span v-if="knowledge.source" class="meta-item">
              <el-icon><Link /></el-icon>
              来源：{{ knowledge.source }}
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatTime(knowledge.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><Edit /></el-icon>
              更新于 {{ formatTime(knowledge.updated_at) }}
            </span>
          </div>

          <div class="article-content rich-content" v-html="renderedContent"></div>

          <div class="article-footer">
            <div class="footer-left">
              <el-button @click="goBack">
                <el-icon><ArrowLeft /></el-icon>
                返回知识库
              </el-button>
              <el-button
                :type="isFavorite ? 'warning' : 'default'"
                :loading="favoriteLoading"
                @click="toggleFavorite"
              >
                <el-icon><StarFilled v-if="isFavorite" /><Star v-else /></el-icon>
                {{ isFavorite ? '已收藏' : '收藏' }}
              </el-button>
            </div>
            <el-button type="primary" @click="goToChat">
              <el-icon><ChatDotRound /></el-icon>
              咨询相关问题
            </el-button>
          </div>
        </div>

        <!-- 相关推荐 -->
        <div v-if="relatedList.length > 0" class="related-section glass-card">
          <h3 class="related-title">
            <el-icon><Connection /></el-icon>
            相关推荐
          </h3>
          <div class="related-list">
            <div
              v-for="item in relatedList"
              :key="item.id"
              class="related-item"
              @click="goToDetail(item.id)"
            >
              <el-tag :type="getCategoryType(item.category)" effect="light" size="small">
                {{ getCategoryLabel(item.category) }}
              </el-tag>
              <h4 class="related-item-title">{{ item.title }}</h4>
              <div class="related-item-tags" v-if="item.tags?.length">
                <el-tag
                  v-for="tag in item.tags.slice(0, 2)"
                  :key="tag.id"
                  :color="tag.color"
                  effect="dark"
                  size="small"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DocumentDelete, View, Clock, Link, Edit, ChatDotRound, ArrowLeft, Connection, Star, StarFilled } from '@element-plus/icons-vue'
import { getKnowledgeItem, getRelatedKnowledge, getFavoriteStatus, addFavorite, removeFavorite } from '@/api/knowledge'
import { renderMarkdown } from '@/utils/markdown'
import { useChatStore } from '@/store/modules/chat'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

const loading = ref(false)
const knowledge = ref(null)
const relatedList = ref([])
const isFavorite = ref(false)
const favoriteLoading = ref(false)

const categoryMap = {
  '病害识别': { label: '病害识别', type: 'danger' },
  '防治方法': { label: '防治方法', type: 'warning' },
  '栽培技术': { label: '栽培技术', type: 'success' },
  '基础知识': { label: '基础知识', type: 'primary' },
  '养护知识': { label: '养护知识', type: 'primary' },
  '病害防治': { label: '病害防治', type: 'danger' }
}

function getCategoryLabel(category) {
  return categoryMap[category]?.label || category || '其他'
}

function getCategoryType(category) {
  return categoryMap[category]?.type || 'info'
}

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const renderedContent = computed(() => {
  if (!knowledge.value?.content) return ''
  return renderMarkdown(knowledge.value.content)
})

async function fetchKnowledgeDetail() {
  const id = route.params.id
  if (!id) {
    ElMessage.error('知识ID不存在')
    router.push('/knowledge-list')
    return
  }

  loading.value = true
  try {
    const res = await getKnowledgeItem(id)
    knowledge.value = res
    if (res.tags?.length) {
      fetchRelatedKnowledge(id, res.tags)
    }
  } catch (error) {
    ElMessage.error('加载知识详情失败')
    knowledge.value = null
  } finally {
    loading.value = false
  }
}

async function fetchRelatedKnowledge(id, tags) {
  try {
    const tagIds = tags.map(t => t.id).join(',')
    const res = await getRelatedKnowledge(id, { limit: 4 })
    relatedList.value = (res || []).filter(item => item.id !== Number(id)).slice(0, 4)
  } catch (e) {
    relatedList.value = []
  }
}

function goBack() {
  router.push('/knowledge-list')
}

function goToDetail(id) {
  router.push(`/knowledge-list/${id}`)
}

function goToChat() {
  if (knowledge.value) {
    chatStore.setDetectionContext({
      detected_class_id: null,
      disease_name: knowledge.value.title,
      detection_context: `来自知识库: ${knowledge.value.title}`
    })
  }
  router.push('/knowledge')
}

async function fetchFavoriteStatus() {
  const id = route.params.id
  if (!id) return
  try {
    const res = await getFavoriteStatus(id)
    isFavorite.value = !!res.is_favorite
  } catch (e) {
    isFavorite.value = false
  }
}

async function toggleFavorite() {
  const id = route.params.id
  if (!id) return
  favoriteLoading.value = true
  try {
    if (isFavorite.value) {
      await removeFavorite(id)
      isFavorite.value = false
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(id)
      isFavorite.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
  } finally {
    favoriteLoading.value = false
  }
}

onMounted(() => {
  fetchKnowledgeDetail()
  fetchFavoriteStatus()
})
</script>

<style scoped>
.knowledge-detail-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.detail-container {
  min-height: 500px;
}

.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  text-align: center;
}

.not-found-icon {
  color: var(--color-text-tertiary);
  opacity: 0.5;
  margin-bottom: 20px;
}

.not-found-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
}

.not-found-text {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0 0 24px 0;
}

.article-container {
  padding: 32px;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.views-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.article-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.article-tag {
  margin: 0 !important;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--color-text-secondary);
  margin-bottom: 40px;
}

:deep(.article-content h1),
:deep(.article-content h2),
:deep(.article-content h3),
:deep(.article-content h4) {
  margin: 24px 0 12px 0;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
}

:deep(.article-content h1) {
  font-size: 26px;
}

:deep(.article-content h2) {
  font-size: 22px;
}

:deep(.article-content h3) {
  font-size: 18px;
}

:deep(.article-content p) {
  margin: 16px 0;
}

:deep(.article-content ul),
:deep(.article-content ol) {
  margin: 16px 0;
  padding-left: 28px;
}

:deep(.article-content li) {
  margin: 8px 0;
}

:deep(.article-content strong) {
  font-weight: 600;
  color: var(--color-text-primary);
}

:deep(.article-content code) {
  background: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-family: var(--font-family-mono);
}

:deep(.article-content pre) {
  background: var(--color-bg-tertiary);
  padding: 16px 20px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 20px 0;
}

:deep(.article-content pre code) {
  background: none;
  padding: 0;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.article-content blockquote) {
  border-left: 4px solid var(--color-accent);
  padding: 12px 20px;
  margin: 20px 0;
  background: var(--color-bg-tertiary);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  color: var(--color-text-secondary);
}

:deep(.article-content a) {
  color: var(--color-accent);
  text-decoration: none;
}

:deep(.article-content a:hover) {
  text-decoration: underline;
}

:deep(.article-content table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

:deep(.article-content th),
:deep(.article-content td) {
  border: 1px solid var(--color-border-light);
  padding: 10px 14px;
  text-align: left;
}

:deep(.article-content th) {
  background: var(--color-bg-tertiary);
  font-weight: 600;
  color: var(--color-text-primary);
}

:deep(.article-content img) {
  max-width: 100%;
  border-radius: var(--radius-md);
  margin: 16px 0;
}

.related-section {
  margin-top: 24px;
  padding: 24px;
}

.related-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 20px 0;
}

.related-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.related-item {
  padding: 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.related-item:hover {
  background: var(--color-bg-tertiary);
  border-color: var(--color-accent);
  transform: translateY(-2px);
}

.related-item-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 10px 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.related-item-tags .el-tag {
  margin: 0 !important;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 24px;
  border-top: 1px solid var(--color-border-light);
}

.footer-left {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .knowledge-detail-page {
    padding: 16px;
  }

  .article-container {
    padding: 20px;
  }

  .article-title {
    font-size: 24px;
  }

  .article-meta {
    flex-direction: column;
    gap: 12px;
  }

  .article-content {
    font-size: 15px;
  }

  .article-footer {
    flex-direction: column;
    gap: 12px;
  }

  .footer-left {
    flex-direction: column;
    gap: 12px;
  }

  .article-footer .el-button {
    width: 100%;
  }
}
</style>