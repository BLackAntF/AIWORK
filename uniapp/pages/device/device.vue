<template>
	<view class="container">
		<!-- 设备状态概览 -->
		<view class="device-overview card">
			<view class="device-header">
				<view class="device-icon">
					<text class="icon">🔥</text>
				</view>
				<view class="device-info">
					<text class="device-name">智慧烹饪设备</text>
					<view class="device-status-row">
						<text class="status-dot" :class="deviceConnected ? 'online' : 'offline'"></text>
						<text class="status-label">{{ deviceConnected ? '在线' : '离线' }}</text>
					</view>
				</view>
				<view class="device-switch" @tap="togglePower">
					<view class="switch-track" :class="{ on: isPowerOn }">
						<view class="switch-thumb"></view>
					</view>
				</view>
			</view>
		</view>

		<!-- 实时数据 -->
		<view class="real-time-data">
			<view class="data-card">
				<text class="data-value">{{ currentTemp }}°</text>
				<text class="data-label">当前温度</text>
			</view>
			<view class="data-card">
				<text class="data-value">{{ currentTime }}min</text>
				<text class="data-label">剩余时间</text>
			</view>
			<view class="data-card">
				<text class="data-value">{{ powerUsage }}W</text>
				<text class="data-label">功率</text>
			</view>
		</view>

		<!-- 设备信息 -->
		<view class="section">
			<view class="section-title">设备信息</view>
			<view class="info-list card">
				<view class="info-item">
					<text class="info-label">设备名称</text>
					<text class="info-value">{{ deviceName || '--' }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">设备ID</text>
					<text class="info-value">{{ deviceId || '--' }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">固件版本</text>
					<text class="info-value">v1.0.0</text>
				</view>
				<view class="info-item">
					<text class="info-label">蓝牙信号</text>
					<text class="info-value">{{ rssi || '--' }} dBm</text>
				</view>
				<view class="info-item">
					<text class="info-label">连接状态</text>
					<text class="info-value" :style="{ color: deviceConnected ? '#2ecc71' : '#666' }">
						{{ deviceConnected ? '已连接' : '未连接' }}
					</text>
				</view>
			</view>
		</view>

		<!-- 设备操作 -->
		<view class="section">
			<view class="section-title">设备操作</view>
			<view class="action-grid">
				<view class="action-item" @tap="queryStatus">
					<text class="action-icon">📊</text>
					<text class="action-label">查询状态</text>
				</view>
				<view class="action-item" @tap="resetAlarm">
					<text class="action-icon">🔔</text>
					<text class="action-label">重置警报</text>
				</view>
				<view class="action-item danger" @tap="emergencyStop">
					<text class="action-icon">🛑</text>
					<text class="action-label">紧急停止</text>
				</view>
				<view class="action-item" @tap="disconnectDevice">
					<text class="action-icon">🔌</text>
					<text class="action-label">断开连接</text>
				</view>
			</view>
		</view>

		<!-- 异常警报 -->
		<view class="section" v-if="alarms.length > 0">
			<view class="section-title" style="color: #e74c3c;">异常警报</view>
			<view class="alarm-list">
				<view v-for="(alarm, index) in alarms" :key="index" class="alarm-item">
					<text class="alarm-icon">⚠️</text>
					<view class="alarm-content">
						<text class="alarm-title">{{ alarm.title }}</text>
						<text class="alarm-desc">{{ alarm.description }}</text>
						<text class="alarm-time">{{ alarm.time }}</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import bleManager, { CMD } from '@/utils/ble.js'

	export default {
		data() {
			return {
				deviceConnected: false,
				deviceName: '',
				deviceId: '',
				rssi: 0,
				isPowerOn: false,
				currentTemp: 0,
				currentTime: 0,
				powerUsage: 0,
				alarms: []
			}
		},

		onShow() {
			this.checkDeviceStatus()
		},

		methods: {
			checkDeviceStatus() {
				this.deviceConnected = bleManager.isConnected
				this.deviceName = bleManager.deviceName
				this.deviceId = bleManager.deviceId
			},

			async togglePower() {
				if (!this.deviceConnected) {
					uni.showToast({ title: '设备未连接', icon: 'none' })
					return
				}
				try {
					if (this.isPowerOn) {
						await bleManager.sendCommand(CMD.POWER_OFF)
						this.isPowerOn = false
					} else {
						await bleManager.sendCommand(CMD.POWER_ON)
						this.isPowerOn = true
					}
				} catch (err) {
					console.error('电源控制失败', err)
				}
			},

			async queryStatus() {
				if (!this.deviceConnected) {
					uni.showToast({ title: '设备未连接', icon: 'none' })
					return
				}
				try {
					await bleManager.queryStatus()
					uni.showToast({ title: '已发送状态查询', icon: 'none' })
				} catch (err) {
					console.error('查询失败', err)
				}
			},

			async resetAlarm() {
				if (!this.deviceConnected) return
				try {
					await bleManager.sendCommand(CMD.RESET_ALARM)
					this.alarms = []
					uni.showToast({ title: '警报已重置', icon: 'success' })
				} catch (err) {
					console.error('重置警报失败', err)
				}
			},

			async emergencyStop() {
				if (!this.deviceConnected) return
				uni.showModal({
					title: '紧急停止',
					content: '确定要紧急停止设备吗？',
					success: async (res) => {
						if (res.confirm) {
							try {
								await bleManager.sendCommand(CMD.EMERGENCY_STOP)
								this.isPowerOn = false
								uni.showToast({ title: '已紧急停止', icon: 'success' })
							} catch (err) {
								console.error('紧急停止失败', err)
							}
						}
					}
				})
			},

			async disconnectDevice() {
				try {
					await bleManager.disconnect()
					this.deviceConnected = false
					this.isPowerOn = false
					uni.showToast({ title: '已断开连接', icon: 'success' })
				} catch (err) {
					console.error('断开失败', err)
				}
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

	/* 设备概览 */
	.device-overview {
		margin-top: 24rpx;
	}

	.device-header {
		display: flex;
		align-items: center;
		gap: 24rpx;
	}

	.device-icon {
		width: 100rpx;
		height: 100rpx;
		border-radius: 24rpx;
		background: linear-gradient(135deg, #e94560, #c23152);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.device-icon .icon {
		font-size: 48rpx;
	}

	.device-info {
		flex: 1;
	}

	.device-name {
		font-size: 32rpx;
		font-weight: 600;
		color: #fff;
	}

	.device-status-row {
		display: flex;
		align-items: center;
		gap: 8rpx;
		margin-top: 8rpx;
	}

	.status-label {
		font-size: 24rpx;
		color: #a0a0b0;
	}

	/* 开关 */
	.switch-track {
		width: 100rpx;
		height: 52rpx;
		border-radius: 26rpx;
		background: #2a2a4a;
		position: relative;
		transition: all 0.3s;
		padding: 4rpx;
	}

	.switch-track.on {
		background: linear-gradient(135deg, #e94560, #c23152);
	}

	.switch-thumb {
		width: 44rpx;
		height: 44rpx;
		border-radius: 50%;
		background: #fff;
		position: absolute;
		top: 4rpx;
		left: 4rpx;
		transition: all 0.3s;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
	}

	.switch-track.on .switch-thumb {
		left: 52rpx;
	}

	/* 实时数据 */
	.real-time-data {
		display: flex;
		gap: 16rpx;
		padding: 24rpx;
	}

	.data-card {
		flex: 1;
		background: #1a1a2e;
		border-radius: 20rpx;
		padding: 24rpx 16rpx;
		text-align: center;
		border: 1rpx solid #2a2a4a;
	}

	.data-value {
		font-size: 36rpx;
		font-weight: bold;
		color: #e94560;
		display: block;
	}

	.data-label {
		font-size: 22rpx;
		color: #a0a0b0;
		margin-top: 8rpx;
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

	/* 信息列表 */
	.info-list {
		padding: 0;
	}

	.info-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24rpx 32rpx;
		border-bottom: 1rpx solid #2a2a4a;
	}

	.info-item:last-child {
		border-bottom: none;
	}

	.info-label {
		font-size: 26rpx;
		color: #a0a0b0;
	}

	.info-value {
		font-size: 26rpx;
		color: #fff;
		font-weight: 500;
	}

	/* 操作网格 */
	.action-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16rpx;
	}

	.action-item {
		background: #1a1a2e;
		border-radius: 20rpx;
		padding: 32rpx 24rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12rpx;
		border: 1rpx solid #2a2a4a;
	}

	.action-item:active {
		transform: scale(0.96);
		background: #2a2a4a;
	}

	.action-item.danger {
		border-color: #e74c3c;
	}

	.action-icon {
		font-size: 48rpx;
	}

	.action-label {
		font-size: 24rpx;
		color: #a0a0b0;
	}

	/* 警报列表 */
	.alarm-list {
		background: #1a1a2e;
		border-radius: 24rpx;
		overflow: hidden;
	}

	.alarm-item {
		display: flex;
		gap: 16rpx;
		padding: 24rpx 32rpx;
		border-bottom: 1rpx solid #2a2a4a;
		background: rgba(231, 76, 60, 0.05);
	}

	.alarm-item:last-child {
		border-bottom: none;
	}

	.alarm-icon {
		font-size: 36rpx;
	}

	.alarm-content {
		flex: 1;
	}

	.alarm-title {
		font-size: 26rpx;
		color: #e74c3c;
		font-weight: 600;
		display: block;
	}

	.alarm-desc {
		font-size: 22rpx;
		color: #a0a0b0;
		margin-top: 4rpx;
		display: block;
	}

	.alarm-time {
		font-size: 20rpx;
		color: #666;
		margin-top: 8rpx;
		display: block;
	}
</style>
