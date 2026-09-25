<template>
	<view class="mine-page">
		<view class="user-section">
			<view class="header-bg"></view>
			<view class="user-info">
				<view class="avatar">{{ avatarText }}</view>
				<view class="user-detail">
					<text class="username">{{ displayName }}</text>
					<text class="role-tag" :class="{ admin: isAdmin }">{{ userRole }}</text>
				</view>
			</view>
		</view>

		<view class="menu-section">
			<view class="menu-group">
				<view class="menu-item" @click="goChangePassword">
					<text class="menu-icon">🔒</text>
					<text class="menu-text">修改密码</text>
					<text class="menu-arrow">›</text>
				</view>
				<view class="menu-item" @click="goKnowledge">
					<text class="menu-icon">📚</text>
					<text class="menu-text">知识库浏览</text>
					<text class="menu-arrow">›</text>
				</view>
				<view class="menu-item" @click="showAbout">
					<text class="menu-icon">ℹ️</text>
					<text class="menu-text">关于</text>
					<text class="menu-arrow">›</text>
				</view>
			</view>

			<view v-if="isAdmin" class="menu-group admin-group">
				<view class="admin-header" @click="adminExpanded = !adminExpanded">
					<text class="admin-icon">⚙️</text>
					<text class="admin-text">管理员入口</text>
					<text class="admin-arrow" :class="{ expanded: adminExpanded }">›</text>
				</view>
				<view class="admin-submenu" :class="{ visible: adminExpanded }">
					<view class="menu-item" @click="goAdmin('users')">
						<text class="menu-icon">👥</text>
						<text class="menu-text">用户管理</text>
						<text class="menu-arrow">›</text>
					</view>
					<view class="menu-item" @click="goAdmin('pending')">
						<text class="menu-icon">📝</text>
						<text class="menu-text">待审核</text>
						<text class="menu-arrow">›</text>
					</view>
					<view class="menu-item" @click="goAdmin('logs')">
						<text class="menu-icon">📜</text>
						<text class="menu-text">操作日志</text>
						<text class="menu-arrow">›</text>
					</view>
					<view class="menu-item" @click="goAdmin('dashboard')">
						<text class="menu-icon">📊</text>
						<text class="menu-text">数据看板</text>
						<text class="menu-arrow">›</text>
					</view>
				</view>
			</view>
		</view>

		<view class="logout-section">
			<button class="logout-btn" @click="handleLogout">退出登录</button>
		</view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const adminExpanded = ref(false)

const displayName = computed(() => userStore.userInfo?.username || '用户')
const avatarText = computed(() => {
	const name = userStore.userInfo?.username || 'U'
	return name.charAt(0).toUpperCase()
})
const userRole = computed(() => {
	const role = userStore.userInfo?.role
	return role === 'admin' ? '管理员' : '普通用户'
})
const isAdmin = computed(() => userStore.isAdmin)

function goChangePassword() {
	uni.navigateTo({ url: '/pages/mine/password' })
}

function goKnowledge() {
	uni.navigateTo({ url: '/pages/knowledge/list' })
}

function showAbout() {
	uni.showModal({
		title: '关于',
		content: '番茄病害诊断 App\n版本：1.0.0\n\n基于 YOLO 模型的智能病害检测系统',
		showCancel: false,
		confirmText: '确定'
	})
}

function goAdmin(page) {
	const urls = {
		users: '/pages/admin/users',
		pending: '/pages/admin/pending',
		logs: '/pages/admin/logs',
		dashboard: '/pages/admin/dashboard'
	}
	uni.navigateTo({ url: urls[page] })
}

function handleLogout() {
	uni.showModal({
		title: '提示',
		content: '确定退出登录吗？',
		confirmColor: '#F44336',
		success: (res) => {
			if (res.confirm) {
				userStore.logout()
			}
		}
	})
}
</script>

<style lang="scss" scoped>
.mine-page {
	min-height: 100vh;
	background: #F5F5F5;
	padding-bottom: 60rpx;
}

.user-section {
	position: relative;
	padding: 60rpx 32rpx;
	padding-top: calc(60rpx + env(safe-area-inset-top));
}

.header-bg {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 360rpx;
	background: linear-gradient(135deg, #E07A5F 0%, #C96247 100%);
}

.user-info {
	position: relative;
	display: flex;
	align-items: center;
}

.avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 48rpx;
	font-weight: 600;
	color: #fff;
	margin-right: 28rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.5);
}

.user-detail {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.username {
	font-size: 36rpx;
	font-weight: 600;
	color: #fff;
}

.role-tag {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
	background: rgba(255, 255, 255, 0.2);
	padding: 4rpx 16rpx;
	border-radius: 8rpx;
	align-self: flex-start;
}

.role-tag.admin {
	background: rgba(255, 152, 0, 0.3);
	color: #FFEB3B;
}

.menu-section {
	padding: 0 24rpx;
	margin-top: -40rpx;
	position: relative;
	z-index: 1;
}

.menu-group {
	background: #fff;
	border-radius: 20rpx;
	margin-bottom: 20rpx;
	overflow: hidden;
}

.menu-item {
	display: flex;
	align-items: center;
	padding: 28rpx 24rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.menu-item:last-child {
	border-bottom: none;
}

.menu-icon {
	font-size: 36rpx;
	margin-right: 20rpx;
}

.menu-text {
	flex: 1;
	font-size: 30rpx;
	color: #333;
}

.menu-arrow {
	font-size: 36rpx;
	color: #ccc;
}

.admin-group {
	background: rgba(224, 122, 95, 0.05);
	border: 1rpx solid rgba(224, 122, 95, 0.2);
}

.admin-header {
	display: flex;
	align-items: center;
	padding: 28rpx 24rpx;
}

.admin-icon {
	font-size: 36rpx;
	margin-right: 20rpx;
}

.admin-text {
	flex: 1;
	font-size: 30rpx;
	color: #E07A5F;
	font-weight: 600;
}

.admin-arrow {
	font-size: 36rpx;
	color: #E07A5F;
	transition: transform 0.3s ease;
}

.admin-arrow.expanded {
	transform: rotate(90deg);
}

.admin-submenu {
	max-height: 0;
	overflow: hidden;
	transition: max-height 0.3s ease;
}

.admin-submenu.visible {
	max-height: 500rpx;
}

.logout-section {
	padding: 0 24rpx;
	margin-top: 40rpx;
}

.logout-btn {
	width: 100%;
	height: 88rpx;
	border-radius: 44rpx;
	background: #fff;
	color: #F44336;
	font-size: 32rpx;
	border: 2rpx solid #F44336;
}

.logout-btn::after {
	border: none;
}
</style>
