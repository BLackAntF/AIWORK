<template>
	<view class="admin-page">
		<view class="page-header">
			<view class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</view>
			<text class="header-title">待审核</text>
			<view class="placeholder"></view>
		</view>

		<view class="read-only-hint">
			<text class="hint-icon">⚠️</text>
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

			<EmptyState v-else-if="items.length === 0" icon="📝" title="暂无待审核" desc="所有内容已审核通过" />

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
						<text class="item-author">{{ item.author_name || '未知' }}</text>
						<text class="item-time">{{ formatTime(item.created_at) }}</text>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminPending } from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'

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
		const data = await getAdminPending()
		items.value = data.items || []
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	loadPending()
}

function goBack() {
	uni.navigateBack()
}

onMounted(() => {
	loadPending()
})
</script>

<style lang="scss" scoped>
.admin-page {
	min-height: 100vh;
	background: #F5F5F5;
}

.page-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 32rpx;
	background: #E07A5F;
}

.back-btn {
	width: 64rpx;
	height: 64rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.back-icon {
	font-size: 48rpx;
	color: #fff;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #fff;
}

.placeholder {
	width: 64rpx;
}

.read-only-hint {
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 16rpx 24rpx;
	background: rgba(255, 152, 0, 0.1);
}

.hint-icon {
	font-size: 28rpx;
}

.hint-text {
	font-size: 24rpx;
	color: #FF9800;
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
	color: #999;
}

.pending-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.pending-item {
	background: #fff;
	border-radius: 20rpx;
	padding: 24rpx;
	border-left: 6rpx solid #FF9800;
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
	color: #333;
}

.item-status {
	font-size: 24rpx;
	color: #FF9800;
	background: rgba(255, 152, 0, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
	margin-left: 16rpx;
}

.item-summary {
	font-size: 26rpx;
	color: #666;
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
	color: #999;
}

.item-time {
	font-size: 22rpx;
	color: #bbb;
}
</style>
