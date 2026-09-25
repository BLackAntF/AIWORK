<template>
	<view class="notifications-page">
		<PageHeader title="站内通知" :show-back="true">
			<template #actions>
				<text v-if="list.length > 0" class="read-all" @click="handleReadAll">全部已读</text>
			</template>
		</PageHeader>

		<scroll-view
			class="notify-content"
			scroll-y
			@refresherrefresh="onRefresh"
			@scrolltolower="onLoadMore"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
			:show-scrollbar="false"
		>
			<view v-if="loading && !refreshing" class="loading-row">
				<text class="loading-text">加载中...</text>
			</view>

			<EmptyState v-else-if="list.length === 0" name="bell" title="暂无通知" desc="暂无站内通知" />

			<view v-else class="notify-list">
				<view
					v-for="item in list"
					:key="item.id"
					class="notify-item"
					:class="{ unread: !item.is_read }"
					@click="handleItemClick(item)"
				>
					<view class="notify-header">
						<text class="notify-title">{{ item.title }}</text>
						<view class="notify-meta">
							<view v-if="!item.is_read" class="unread-dot"></view>
							<text class="notify-time">{{ formatTime(item.created_at) }}</text>
						</view>
					</view>
					<text class="notify-content">{{ item.content }}</text>
					<view class="notify-footer">
						<text class="notify-type">{{ getTypeText(item.type) }}</text>
						<view class="notify-actions">
							<view v-if="!item.is_read" class="item-action" @click.stop="handleItemClick(item)">标为已读</view>
							<view class="item-action danger" @click.stop="handleDelete(item)">删除</view>
						</view>
					</view>
				</view>
			</view>

			<view v-if="hasMore && !loading && list.length > 0" class="load-more">
				<text class="load-more-text">加载更多...</text>
			</view>
			<view v-if="!hasMore && list.length > 0" class="no-more">
				<text class="no-more-text">- 已加载全部 -</text>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onPullDownRefresh } from '@dcloudio/uni-app'
import {
	getNotifications,
	markNotificationRead,
	markAllNotificationsRead,
	deleteNotification
} from '@/api/notifications'
import { showError } from '@/utils/error'
import PageHeader from '@/components/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'

const TYPE_TEXT = {
	'detection_completed': '检测完成',
	'knowledge_approved': '审核通过',
	'knowledge_rejected': '审核未过',
	'system': '系统'
}

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = ref(10)
const hasMore = ref(true)

function getTypeText(type) {
	return TYPE_TEXT[type] || '系统'
}

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

async function loadList(isRefresh = false) {
	if (loading.value) return

	loading.value = true
	try {
		const data = await getNotifications({ page: page.value, page_size: pageSize.value })
		const items = data.list || []
		if (isRefresh) {
			list.value = items
		} else {
			list.value = [...list.value, ...items]
		}
		hasMore.value = items.length >= pageSize.value
	} catch (e) {
		showError(e, '加载失败')
	} finally {
		loading.value = false
		refreshing.value = false
		uni.stopPullDownRefresh()
	}
}

function onRefresh() {
	refreshing.value = true
	page.value = 1
	hasMore.value = true
	loadList(true)
}

function onLoadMore() {
	if (hasMore.value && !loading.value) {
		page.value++
		loadList()
	}
}

async function handleItemClick(item) {
	if (item.is_read) return
	try {
		await markNotificationRead(item.id)
		item.is_read = true
	} catch (e) {
		showError(e, '操作失败')
	}
}

async function handleReadAll() {
	try {
		await markAllNotificationsRead()
		list.value.forEach(item => { item.is_read = true })
		uni.showToast({ title: '已全部标记', icon: 'none' })
	} catch (e) {
		showError(e, '操作失败')
	}
}

async function handleDelete(item) {
	try {
		await deleteNotification(item.id)
		list.value = list.value.filter(n => n.id !== item.id)
		uni.showToast({ title: '已删除', icon: 'none' })
	} catch (e) {
		showError(e, '删除失败')
	}
}

onLoad(() => {
	loadList(true)
})

onPullDownRefresh(() => {
	onRefresh()
})
</script>

<style lang="scss" scoped>
.notifications-page {
	min-height: 100vh;
	background: var(--bg-2);
}

.read-all {
	font-size: 26rpx;
	color: #fff;
}

.notify-content {
	height: calc(100vh - 140rpx);
}

.loading-row {
	padding: 60rpx;
	text-align: center;
}

.loading-text {
	font-size: 28rpx;
	color: var(--text-3);
}

.notify-list {
	padding: 24rpx;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.notify-item {
	background: var(--bg-1);
	border-radius: 20rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.notify-item.unread {
	border-left: 6rpx solid var(--brand);
}

.notify-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 12rpx;
}

.notify-title {
	flex: 1;
	font-size: 30rpx;
	font-weight: 600;
	color: var(--text-1);
	margin-right: 16rpx;
}

.notify-meta {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.notify-time {
	font-size: 24rpx;
	color: var(--text-3);
}

.unread-dot {
	width: 16rpx;
	height: 16rpx;
	border-radius: 50%;
	background: var(--error);
}

.notify-content {
	font-size: 26rpx;
	color: var(--text-2);
	line-height: 1.6;
	display: -webkit-box;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
	overflow: hidden;
	margin-bottom: 16rpx;
}

.notify-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.notify-type {
	font-size: 24rpx;
	color: var(--brand);
	background: rgba(224, 122, 95, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 12rpx;
}

.notify-actions {
	display: flex;
	gap: 24rpx;
}

.item-action {
	font-size: 24rpx;
	color: var(--text-3);
}

.item-action.danger {
	color: var(--error);
}

.load-more {
	padding: 32rpx;
	text-align: center;
}

.load-more-text {
	font-size: 26rpx;
	color: var(--text-3);
}

.no-more {
	padding: 24rpx;
	text-align: center;
}

.no-more-text {
	font-size: 24rpx;
	color: var(--text-disabled);
}
</style>