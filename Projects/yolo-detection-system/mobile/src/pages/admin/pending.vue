<template>
	<view class="admin-page">
		<PageHeader title="待审核" :show-back="true" />

		<view class="read-only-hint">
			<AppIcon name="alert" :size="28" color="#FAAD14" />
			<text class="hint-text">仅查看，审核请在 Web 端操作</text>
		</view>

		<scroll-view
			class="content"
			scroll-y
			@refresherrefresh="onRefresh"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
			:show-scrollbar="false"
		>
			<view v-if="loading && !refreshing" class="loading-row">
				<text class="loading-text">加载中...</text>
			</view>

			<EmptyState v-else-if="items.length === 0" name="edit" title="暂无待审核" desc="所有内容已审核通过" />

			<view v-else class="pending-list">
				<view
					v-for="item in items"
					:key="item.id"
					class="pending-item"
				>
					<view class="item-header">
						<text class="item-title">{{ item.title }}</text>
						<text class="item-status">待审核</text>
					</view>
					<text class="item-summary">{{ item.summary }}</text>
					<view class="item-footer">
						<text class="item-author">{{ item.uploader_name || '未知' }}</text>
						<text class="item-time">{{ formatTime(item.created_at) }}</text>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPendingKnowledge } from '@/api/admin'
import { showError } from '@/utils/error'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'

const items = ref([])
const loading = ref(false)
const refreshing = ref(false)

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}/${date.getDate()}`
}

async function loadPending() {
	loading.value = true
	try {
		const data = await getPendingKnowledge()
		items.value = data.list || []
	} catch (e) {
		showError(e, '加载失败')
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	loadPending()
}

onMounted(() => {
	loadPending()
})
</script>

<style lang="scss" scoped>
.admin-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.read-only-hint {
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 16rpx 24rpx;
	background: rgba(250, 173, 20, 0.1);
}

.hint-text {
	font-size: 24rpx;
	color: var(--warning);
}

.content {
	height: calc(100vh - 180rpx);
	padding: 24rpx;
}

.loading-row {
	padding: 60rpx;
	text-align: center;
}

.loading-text {
	font-size: 28rpx;
	color: var(--text-3);
}

.pending-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.pending-item {
	background: var(--bg-1);
	border-radius: 20rpx;
	padding: 24rpx;
	border-left: 6rpx solid var(--warning);
}

.item-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 12rpx;
}

.item-title {
	flex: 1;
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-1);
}

.item-status {
	font-size: 24rpx;
	color: var(--warning);
	background: rgba(250, 173, 20, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
	margin-left: 16rpx;
}

.item-summary {
	font-size: 26rpx;
	color: var(--text-2);
	line-height: 1.5;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
	margin-bottom: 16rpx;
}

.item-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.item-author {
	font-size: 24rpx;
	color: var(--text-3);
}

.item-time {
	font-size: 22rpx;
	color: var(--text-disabled);
}
</style>
