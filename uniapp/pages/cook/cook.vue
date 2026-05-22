<template>
	<view class="container">
		<!-- 烹饪状态 -->
		<view class="cooking-status card">
			<view class="status-header">
				<text class="status-title">烹饪状态</text>
				<text class="status-badge" :class="cookingState">{{ stateText }}</text>
			</view>
			<view class="status-display">
				<view class="temp-circle">
					<canvas canvas-id="tempCanvas" class="temp-canvas"></canvas>
					<view class="temp-value">
						<text class="temp-num">{{ currentTemp }}</text>
						<text class="temp-unit">°C</text>
					</view>
				</view>
				<view class="status-details">
					<view class="detail-row">
						<text class="detail-label">烹饪模式</text>
						<text class="detail-value">{{ currentMode }}</text>
					</view>
					<view class="detail-row">
						<text class="detail-label">设定温度</text>
						<text class="detail-value">{{ targetTemp }}°C</text>
					</view>
					<view class="detail-row">
						<text class="detail-label">剩余时间</text>
						<text class="detail-value highlight">{{ formatTime(remainingTime) }}</text>
					</view>
					<view class="detail-row">
						<text class="detail-label">已用时间</text>
						<text class="detail-value">{{ formatTime(elapsedTime) }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 烹饪控制 -->
		<view class="section">
			<view class="section-title">烹饪控制</view>
			<view class="control-card card">
				<view class="control-row">
					<text class="control-label">目标温度</text>
					<view class="control-input-group">
						<view class="control-btn" @tap="adjustTemp(-10)">−10</view>
						<view class="control-btn" @tap="adjustTemp(-5)">−5</view>
						<text class="control-value">{{ targetTemp }}°C</text>
						<view class="control-btn" @tap="adjustTemp(5)">+5</view>
						<view class="control-btn" @tap="adjustTemp(10)">+10</view>
					</view>
				</view>
				<view class="control-row">
					<text class="control-label">烹饪时间</text>
					<view class="control-input-group">
						<view class="control-btn" @tap="adjustTime(-5)">−5</view>
						<view class="control-btn" @tap="adjustTime(-1)">−1</view>
						<text class="control-value">{{ targetTime }}min</text>
						<view class="control-btn" @tap="adjustTime(1)">+1</view>
						<view class="control-btn" @tap="adjustTime(5)">+5</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 预设菜谱 -->
		<view class="section">
			<view class="section-title">预设菜谱</view>
			<view class="recipe-list">
				<view 
					v-for="(recipe, index) in recipes" 
					:key="index"
					class="recipe-item"
					@tap="selectRecipe(recipe)"
				>
					<view class="recipe-icon">{{ recipe.icon }}</view>
					<view class="recipe-info">
						<text class="recipe-name">{{ recipe.name }}</text>
						<text class="recipe-desc">{{ recipe.desc }}</text>
					</view>
					<view class="recipe-tags">
						<text class="recipe-tag">{{ recipe.temp }}°C</text>
						<text class="recipe-tag">{{ recipe.time }}min</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 操作按钮 -->
		<view class="action-buttons">
			<view class="btn btn-primary" @tap="startCooking">
				{{ isCooking ? '暂停' : '开始烹饪' }}
			</view>
			<view class="btn btn-secondary" @tap="stopCooking">
				停止
			</view>
		</view>
	</view>
</template>

<script>
	import bleManager, { CMD } from '@/utils/ble.js'

	export default {
		data() {
			return {
				cookingState: 'idle',
				currentTemp: 0,
				targetTemp: 180,
				targetTime: 30,
				remainingTime: 0,
				elapsedTime: 0,
				currentMode: '煎炸',
				isCooking: false,
				timer: null,
				recipes: [
					{ name: '香煎牛排', desc: '外焦里嫩', icon: '🥩', temp: 200, time: 15, mode: '煎炸' },
					{ name: '红烧排骨', desc: '软烂入味', icon: '🍖', temp: 120, time: 45, mode: '炖煮' },
					{ name: '清蒸鲈鱼', desc: '鲜嫩可口', icon: '🐟', temp: 100, time: 12, mode: '蒸' },
					{ name: '烤鸡翅', desc: '香脆多汁', icon: '🍗', temp: 200, time: 25, mode: '烘焙' },
					{ name: '保温米饭', desc: '恒温保温', icon: '🍚', temp: 60, time: 60, mode: '保温' },
				]
			}
		},

		computed: {
			stateText() {
				const map = {
					'idle': '待机中',
					'preheating': '预热中',
					'cooking': '烹饪中',
					'paused': '已暂停',
					'completed': '已完成',
					'warming': '保温中'
				}
				return map[this.cookingState] || '未知'
			}
		},

		onUnload() {
			this.clearTimer()
		},

		methods: {
			adjustTemp(delta) {
				const newTemp = this.targetTemp + delta
				if (newTemp >= 0 && newTemp <= 250) {
					this.targetTemp = newTemp
					if (bleManager.isConnected) {
						bleManager.setTemperature(this.targetTemp)
					}
				}
			},

			adjustTime(delta) {
				const newTime = this.targetTime + delta
				if (newTime >= 0 && newTime <= 180) {
					this.targetTime = newTime
					if (bleManager.isConnected) {
						bleManager.setTime(this.targetTime)
					}
				}
			},

			selectRecipe(recipe) {
				this.targetTemp = recipe.temp
				this.targetTime = recipe.time
				this.currentMode = recipe.mode
				uni.showToast({ title: `已选择: ${recipe.name}`, icon: 'none' })
				
				if (bleManager.isConnected) {
					const modeMap = {
						'煎炸': CMD.MODE_FRY,
						'炖煮': CMD.MODE_STEW,
						'蒸': CMD.MODE_STEAM,
						'烘焙': CMD.MODE_BAKE,
						'保温': CMD.MODE_WARM
					}
					bleManager.setMode(modeMap[recipe.mode])
					bleManager.setTemperature(recipe.temp)
					bleManager.setTime(recipe.time)
				}
			},

			async startCooking() {
				if (!bleManager.isConnected) {
					uni.showToast({ title: '请先连接设备', icon: 'none' })
					return
				}

				try {
					if (this.isCooking) {
						await bleManager.sendCommand(CMD.PAUSE)
						this.cookingState = 'paused'
						this.isCooking = false
						this.clearTimer()
					} else {
						await bleManager.sendCommand(CMD.START)
						this.cookingState = 'cooking'
						this.isCooking = true
						this.remainingTime = this.targetTime
						this.elapsedTime = 0
						this.startTimer()
					}
				} catch (err) {
					console.error('烹饪控制失败', err)
				}
			},

			async stopCooking() {
				if (!bleManager.isConnected) return
				try {
					await bleManager.sendCommand(CMD.STOP)
					this.isCooking = false
					this.cookingState = 'idle'
					this.clearTimer()
					uni.showToast({ title: '烹饪已停止', icon: 'success' })
				} catch (err) {
					console.error('停止失败', err)
				}
			},

			startTimer() {
				this.clearTimer()
				this.timer = setInterval(() => {
					if (this.remainingTime > 0) {
						this.remainingTime--
						this.elapsedTime++
					} else {
						this.cookingState = 'completed'
						this.isCooking = false
						this.clearTimer()
						uni.showToast({ title: '烹饪完成！', icon: 'success' })
					}
				}, 60000) // 每分钟更新
			},

			clearTimer() {
				if (this.timer) {
					clearInterval(this.timer)
					this.timer = null
				}
			},

			formatTime(minutes) {
				if (!minutes && minutes !== 0) return '00:00'
				const h = Math.floor(minutes / 60)
				const m = minutes % 60
				return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
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
	}

	/* 烹饪状态 */
	.cooking-status {
		margin-top: 24rpx;
	}

	.status-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24rpx;
	}

	.status-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #fff;
	}

	.status-badge {
		padding: 8rpx 24rpx;
		border-radius: 20rpx;
		font-size: 22rpx;
		font-weight: 500;
	}

	.status-badge.idle {
		background: #2a2a4a;
		color: #a0a0b0;
	}

	.status-badge.preheating {
		background: rgba(243, 156, 18, 0.2);
		color: #f39c12;
	}

	.status-badge.cooking {
		background: rgba(46, 204, 113, 0.2);
		color: #2ecc71;
	}

	.status-badge.paused {
		background: rgba(243, 156, 18, 0.2);
		color: #f39c12;
	}

	.status-badge.completed {
		background: rgba(46, 204, 113, 0.2);
		color: #2ecc71;
	}

	.status-display {
		display: flex;
		gap: 32rpx;
		align-items: center;
	}

	.temp-circle {
		position: relative;
		width: 200rpx;
		height: 200rpx;
		flex-shrink: 0;
	}

	.temp-canvas {
		width: 200rpx;
		height: 200rpx;
	}

	.temp-value {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		text-align: center;
	}

	.temp-num {
		font-size: 48rpx;
		font-weight: bold;
		color: #e94560;
		display: block;
	}

	.temp-unit {
		font-size: 24rpx;
		color: #a0a0b0;
	}

	.status-details {
		flex: 1;
	}

	.detail-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12rpx 0;
		border-bottom: 1rpx solid #2a2a4a;
	}

	.detail-row:last-child {
		border-bottom: none;
	}

	.detail-label {
		font-size: 24rpx;
		color: #a0a0b0;
	}

	.detail-value {
		font-size: 26rpx;
		color: #fff;
		font-weight: 500;
	}

	.detail-value.highlight {
		color: #e94560;
		font-weight: 600;
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

	/* 控制卡片 */
	.control-card {
		padding: 24rpx;
	}

	.control-row {
		margin-bottom: 24rpx;
	}

	.control-row:last-child {
		margin-bottom: 0;
	}

	.control-label {
		font-size: 26rpx;
		color: #a0a0b0;
		margin-bottom: 16rpx;
		display: block;
	}

	.control-input-group {
		display: flex;
		align-items: center;
		gap: 12rpx;
	}

	.control-btn {
		padding: 12rpx 20rpx;
		background: #2a2a4a;
		border-radius: 16rpx;
		font-size: 22rpx;
		color: #a0a0b0;
		border: 1rpx solid #3a3a5a;
	}

	.control-btn:active {
		background: #3a3a5a;
		transform: scale(0.95);
	}

	.control-value {
		font-size: 36rpx;
		font-weight: bold;
		color: #e94560;
		min-width: 120rpx;
		text-align: center;
	}

	/* 菜谱列表 */
	.recipe-list {
		display: flex;
		flex-direction: column;
		gap: 16rpx;
	}

	.recipe-item {
		background: #1a1a2e;
		border-radius: 20rpx;
		padding: 24rpx 32rpx;
		display: flex;
		align-items: center;
		gap: 20rpx;
		border: 1rpx solid #2a2a4a;
	}

	.recipe-item:active {
		transform: scale(0.98);
		background: #2a2a4a;
	}

	.recipe-icon {
		font-size: 48rpx;
		width: 80rpx;
		text-align: center;
	}

	.recipe-info {
		flex: 1;
	}

	.recipe-name {
		font-size: 28rpx;
		color: #fff;
		font-weight: 600;
		display: block;
	}

	.recipe-desc {
		font-size: 22rpx;
		color: #a0a0b0;
		margin-top: 4rpx;
		display: block;
	}

	.recipe-tags {
		display: flex;
		gap: 8rpx;
	}

	.recipe-tag {
		padding: 6rpx 16rpx;
		background: #2a2a4a;
		border-radius: 12rpx;
		font-size: 20rpx;
		color: #e94560;
	}

	/* 操作按钮 */
	.action-buttons {
		display: flex;
		gap: 24rpx;
		padding: 24rpx;
		margin-top: 16rpx;
	}

	.btn {
		flex: 1;
		height: 88rpx;
		border-radius: 44rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 32rpx;
		font-weight: 600;
	}

	.btn:active {
		transform: scale(0.96);
	}

	.btn-primary {
		background: linear-gradient(135deg, #e94560, #c23152);
		color: #fff;
		box-shadow: 0 8rpx 24rpx rgba(233, 69, 96, 0.3);
	}

	.btn-secondary {
		background: #2a2a4a;
		color: #a0a0b0;
		border: 2rpx solid #3a3a5a;
	}
</style>
