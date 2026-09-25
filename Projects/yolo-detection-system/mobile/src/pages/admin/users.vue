<template>
	<view class="admin-page">
		<view class="page-header">
			<view class="back-btn" @click="goBack">
				<text class="back-icon">‹</text>
			</view>
			<text class="header-title">用户管理</text>
			<view class="placeholder"></view>
		</view>

		<view class="read-only-hint">
			<text class="hint-icon">⚠️</text>
			<text class="hint-text">仅查看，编辑请在 Web 端操作</text>
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

			<EmptyState v-else-if="users.length === 0" icon="👥" title="暂无用户" />

			<view v-else class="user-list">
				<view
					v-for="user in users"
					:key="user.id"
					class="user-item"
				>
					<view class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</view>
					<view class="user-info">
						<view class="info-row">
							<text class="user-name">{{ user.username }}</text>
							<text class="role-tag" :class="{ admin: user.role === 'admin' }">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</text>
						</view>
						<text class="user-email">{{ user.email || '未绑定邮箱' }}</text>
					</view>
					<text class="user-time">{{ formatTime(user.created_at) }}</text>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminUsers } from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'

const users = ref([])
const loading = ref(false)
const refreshing = ref(false)

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return `${date.getMonth() + 1}/${date.getDate()}`
}

async function loadUsers() {
	loading.value = true
	try {
		const data = await getAdminUsers()
		users.value = data.items || []
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	loadUsers()
}

function goBack() {
	uni.navigateBack()
}

onMounted(() => {
	loadUsers()
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

.user-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.user-item {
	display: flex;
	align-items: center;
	background: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
}

.user-avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	background: rgba(224, 122, 95, 0.1);
	color: #E07A5F;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.user-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.info-row {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.user-name {
	font-size: 28rpx;
	font-weight: 600;
	color: #333;
}

.role-tag {
	font-size: 22rpx;
	color: #666;
	background: #F5F5F5;
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
}

.role-tag.admin {
	color: #FF9800;
	background: rgba(255, 152, 0, 0.1);
}

.user-email {
	font-size: 24rpx;
	color: #999;
}

.user-time {
	font-size: 22rpx;
	color: #bbb;
}
</style>
