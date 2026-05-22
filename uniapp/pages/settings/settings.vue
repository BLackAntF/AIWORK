<template>
	<view class="container">
		<!-- 用户信息 -->
		<view class="user-profile card">
			<view class="avatar">
				<text class="avatar-text">{{ userName.charAt(0) }}</text>
			</view>
			<view class="user-info">
				<text class="user-name">{{ userName }}</text>
				<text class="user-role">智慧烹饪系统</text>
			</view>
		</view>

		<!-- 系统设置 -->
		<view class="section">
			<view class="section-title">系统设置</view>
			<view class="settings-list card">
				<view class="setting-item" @tap="navigateTo('device')">
					<text class="setting-icon">🔧</text>
					<view class="setting-content">
						<text class="setting-label">设备管理</text>
						<text class="setting-desc">管理连接的烹饪设备</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
				<view class="setting-item" @tap="navigateTo('alarm')">
					<text class="setting-icon">🔔</text>
					<view class="setting-content">
						<text class="setting-label">警报设置</text>
						<text class="setting-desc">配置异常警报通知</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
				<view class="setting-item" @tap="navigateTo('temp')">
					<text class="setting-icon">🌡️</text>
					<view class="setting-content">
						<text class="setting-label">温度单位</text>
						<text class="setting-desc">当前: {{ tempUnit }}</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
				<view class="setting-item" @tap="navigateTo('language')">
					<text class="setting-icon">🌐</text>
					<view class="setting-content">
						<text class="setting-label">语言设置</text>
						<text class="setting-desc">当前: 简体中文</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
			</view>
		</view>

		<!-- 烹饪偏好 -->
		<view class="section">
			<view class="section-title">烹饪偏好</view>
			<view class="settings-list card">
				<view class="setting-item">
					<text class="setting-icon">🔊</text>
					<view class="setting-content">
						<text class="setting-label">声音提示</text>
						<text class="setting-desc">烹饪完成时播放提示音</text>
					</view>
					<switch :checked="soundEnabled" color="#e94560" @change="toggleSound" />
				</view>
				<view class="setting-item">
					<text class="setting-icon">💡</text>
					<view class="setting-content">
						<text class="setting-label">自动保温</text>
						<text class="setting-desc">烹饪完成后自动进入保温模式</text>
					</view>
					<switch :checked="autoWarm" color="#e94560" @change="toggleAutoWarm" />
				</view>
				<view class="setting-item">
					<text class="setting-icon">⏰</text>
					<view class="setting-content">
						<text class="setting-label">定时启动</text>
						<text class="setting-desc">设置设备自动启动时间</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
				<view class="setting-item">
					<text class="setting-icon">🌙</text>
					<view class="setting-content">
						<text class="setting-label">夜间模式</text>
						<text class="setting-desc">降低屏幕亮度，减少噪音</text>
					</view>
					<switch :checked="nightMode" color="#e94560" @change="toggleNightMode" />
				</view>
			</view>
		</view>

		<!-- 关于 -->
		<view class="section">
			<view class="section-title">关于</view>
			<view class="settings-list card">
				<view class="setting-item">
					<text class="setting-icon">📱</text>
					<view class="setting-content">
						<text class="setting-label">应用版本</text>
						<text class="setting-desc">v1.0.0</text>
					</view>
				</view>
				<view class="setting-item">
					<text class="setting-icon">📄</text>
					<view class="setting-content">
						<text class="setting-label">用户协议</text>
						<text class="setting-desc">查看服务条款</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
				<view class="setting-item">
					<text class="setting-icon">🔒</text>
					<view class="setting-content">
						<text class="setting-label">隐私政策</text>
						<text class="setting-desc">了解我们如何保护您的数据</text>
					</view>
					<text class="setting-arrow">›</text>
				</view>
			</view>
		</view>

		<!-- 退出登录 -->
		<view class="logout-area">
			<view class="btn-logout" @tap="logout">
				退出登录
			</view>
		</view>
	</view>
</template>

<script>
	import bleManager from '@/utils/ble.js'

	export default {
		data() {
			return {
				userName: '智慧厨师',
				tempUnit: '°C',
				soundEnabled: true,
				autoWarm: true,
				nightMode: false
			}
		},

		methods: {
			navigateTo(type) {
				const pages = {
					'device': '/pages/device/device',
					'alarm': '',
					'temp': '',
					'language': ''
				}
				const url = pages[type]
				if (url) {
					uni.navigateTo({ url })
				} else {
					uni.showToast({ title: '功能开发中', icon: 'none' })
				}
			},

			toggleSound(e) {
				this.soundEnabled = e.detail.value
			},

			toggleAutoWarm(e) {
				this.autoWarm = e.detail.value
			},

			toggleNightMode(e) {
				this.nightMode = e.detail.value
			},

			logout() {
				uni.showModal({
					title: '退出登录',
					content: '确定要退出登录吗？',
					success: (res) => {
						if (res.confirm) {
							// 断开蓝牙连接
							bleManager.disconnect()
							uni.showToast({ title: '已退出', icon: 'success' })
						}
					}
				})
			}
		}
	}
</script>

<style scoped>
	.container {
		padding-bottom: 40rpx;
	}

	.card {
		background: #1a1a2e;
		border-radius: 24rpx;
		padding: 32rpx;
		margin: 0 24rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.3);
	}

	/* 用户信息 */
	.user-profile {
		margin-top: 24rpx;
		display: flex;
		align-items: center;
		gap: 24rpx;
	}

	.avatar {
		width: 100rpx;
		height: 100rpx;
		border-radius: 50%;
		background: linear-gradient(135deg, #e94560, #c23152);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.avatar-text {
		font-size: 40rpx;
		font-weight: bold;
		color: #fff;
	}

	.user-info {
		flex: 1;
	}

	.user-name {
		font-size: 32rpx;
		font-weight: 600;
		color: #fff;
		display: block;
	}

	.user-role {
		font-size: 24rpx;
		color: #a0a0b0;
		margin-top: 4rpx;
		display: block;
	}

	/* 区块标题 */
	.section {
		margin: 24rpx;
	}

	.section-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #fff;
		margin-bottom: 20rpx;
		padding-left: 16rpx;
		border-left: 6rpx solid #e94560;
	}

	/* 设置列表 */
	.settings-list {
		padding: 0;
		overflow: hidden;
	}

	.setting-item {
		display: flex;
		align-items: center;
		gap: 20rpx;
		padding: 28rpx 32rpx;
		border-bottom: 1rpx solid #2a2a4a;
	}

	.setting-item:last-child {
		border-bottom: none;
	}

	.setting-icon {
		font-size: 36rpx;
		width: 48rpx;
		text-align: center;
	}

	.setting-content {
		flex: 1;
	}

	.setting-label {
		font-size: 28rpx;
		color: #fff;
		font-weight: 500;
		display: block;
	}

	.setting-desc {
		font-size: 22rpx;
		color: #a0a0b0;
		margin-top: 4rpx;
		display: block;
	}

	.setting-arrow {
		font-size: 40rpx;
		color: #666;
		font-weight: 300;
	}

	/* 退出登录 */
	.logout-area {
		padding: 40rpx 24rpx;
	}

	.btn-logout {
		height: 88rpx;
		border-radius: 44rpx;
		background: #1a1a2e;
		border: 2rpx solid #e74c3c;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 30rpx;
		color: #e74c3c;
		font-weight: 500;
	}

	.btn-logout:active {
		background: rgba(231, 76, 60, 0.1);
		transform: scale(0.98);
	}
</style>
