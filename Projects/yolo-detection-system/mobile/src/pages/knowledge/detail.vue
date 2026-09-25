<template>
	<view class="knowledge-detail-page">
		<LoadingOverlay :visible="loading" text="加载中..." />

		<view v-if="detail" class="content">
			<PageHeader title="知识详情" :show-back="true" />

			<view class="detail-header">
				<text class="detail-title">{{ detail.title }}</text>
				<view class="detail-meta">
					<text class="meta-item">{{ detail.category || '未分类' }}</text>
					<text class="meta-item">{{ formatTime(detail.created_at) }}</text>
				</view>
				<text class="detail-summary">{{ detail.summary }}</text>
			</view>

			<view class="detail-body">
				<text class="body-content">{{ detail.content }}</text>
			</view>

			<view v-if="related.length > 0" class="related-section">
				<text class="section-title">相关知识</text>
				<view class="related-list">
					<view
						v-for="item in related"
						:key="item.id"
						class="related-item"
						@click="goDetail(item.id)"
					>
						<text class="related-title">{{ item.title }}</text>
						<text class="related-arrow">›</text>
					</view>
				</view>
			</view>
		</view>

		<EmptyState v-else-if="!loading" name="document" title="知识不存在" />
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { getKnowledgeDetail, getRelatedKnowledge } from '@/api/knowledge'
import { showError } from '@/utils/error'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'

const loading = ref(true)
const detail = ref(null)
const related = ref([])

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}月${date.getDate()}日`
}

function goDetail(id) {
	uni.redirectTo({ url: `/pages/knowledge/detail?id=${id}` })
}

async function loadDetail() {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const id = currentPage.options?.id

	if (!id) {
		loading.value = false
		return
	}

	try {
		detail.value = await getKnowledgeDetail(id)
		const relatedData = await getRelatedKnowledge(id)
		related.value = relatedData.list || []
	} catch (e) {
		showError(e, '加载失败')
	} finally {
		loading.value = false
		uni.stopPullDownRefresh()
	}
}

onPullDownRefresh(() => {
	loadDetail()
})

onMounted(() => {
	loadDetail()
})
</script>

<style lang="scss" scoped>
.knowledge-detail-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.content {
	padding-bottom: 40rpx;
}

.detail-header {
	background: var(--bg-1);
	padding: 32rpx;
	margin-bottom: 24rpx;
}

.detail-title {
	font-size: 36rpx;
	font-weight: 700;
	color: var(--text-1);
	line-height: 1.4;
	margin-bottom: 16rpx;
	display: block;
}

.detail-meta {
	display: flex;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.meta-item {
	font-size: 24rpx;
	color: var(--text-3);
	background: var(--bg-2);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.detail-summary {
	font-size: 28rpx;
	color: var(--text-2);
	line-height: 1.6;
	display: block;
}

.detail-body {
	background: var(--bg-1);
	padding: 32rpx;
	margin-bottom: 24rpx;
}

.body-content {
	font-size: 28rpx;
	color: var(--text-1);
	line-height: 1.8;
}

.related-section {
	background: var(--bg-1);
	padding: 24rpx 32rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-1);
	margin-bottom: 20rpx;
	display: block;
}

.related-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.related-item {
	display: flex;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid var(--border-light);
}

.related-item:last-child {
	border-bottom: none;
}

.related-title {
	flex: 1;
	font-size: 28rpx;
	color: var(--text-1);
}

.related-arrow {
	font-size: 36rpx;
	color: var(--text-disabled);
}
</style>