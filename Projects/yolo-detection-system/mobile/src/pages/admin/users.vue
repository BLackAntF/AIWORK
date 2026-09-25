<template>
	<view class="admin-page">
		<PageHeader title="用户管理" :show-back="true" />

		<view class="read-only-hint">
			<AppIcon name="alert" :size="28" color="#FAAD14" />
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

			<EmptyState v-else-if="users.length === 0" name="users" title="暂无用户" />

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
import { getUsers } from '@/api/admin'
import { showError } from '@/utils/error'
import EmptyState from '@/components/EmptyState.vue'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'

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
		const data = await getUsers()
		users.value = data.list || []
	} catch (e) {
		showError(e, '加载失败')
	} finally {
		loading.value = false
		refreshing.value = false
	}
}

function onRefresh() {
	refreshing.value = true
	loadUsers()
}

onMounted(() => {
	loadUsers()
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

.user-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.user-item {
	display: flex;
	align-items: center;
	background: var(--bg-1);
	border-radius: 20rpx;
	padding: 20rpx;
}

.user-avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	background: rgba(224, 122, 95, 0.1);
	color: var(--brand);
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
	color: var(--text-1);
}

.role-tag {
	font-size: 22rpx;
	color: var(--text-2);
	background: var(--bg-2);
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
}

.role-tag.admin {
	color: var(--warning);
	background: rgba(250, 173, 20, 0.1);
}

.user-email {
	font-size: 24rpx;
	color: var(--text-3);
}

.user-time {
	font-size: 22rpx;
	color: var(--text-disabled);
}
</style>
