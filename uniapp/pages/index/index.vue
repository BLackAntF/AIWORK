<template>
	<view class="container">
		<!-- 顶部状态栏 -->
		<view class="status-bar">
			<view class="device-status">
				<text class="status-dot" :class="deviceConnected ? 'online' : 'offline'"></text>
				<text class="status-text">{{ deviceConnected ? '已连接' : '未连接' }}</text>
			</view>
			<view class="device-name" v-if="deviceName">{{ deviceName }}</view>
			<view class="disconnect-btn" v-if="deviceConnected" @click="disconnectDevice">断开</view>
		</view>

		<!-- 设备操控面板 - 模拟真实设备 -->
		<view class="control-panel">
			<view class="touch-control top-left" @click="onTempDown">
				<view class="touch-icon">−</view>
				<view class="touch-label">温度减</view>
			</view>
			<view class="touch-control top-right" @click="onTempUp">
				<view class="touch-icon">+</view>
				<view class="touch-label">温度加</view>
			</view>
			<view class="display-screen">
				<view class="display-mode">{{ currentMode }}</view>
				<view class="display-temp">{{ currentTemp }}°</view>
				<view class="display-time">{{ formatTime(currentTime) }}</view>
				<view class="display-status" v-if="isCooking">
					<text class="cooking-dot"></text>
					<text>烹饪中</text>
				</view>
			</view>
			<view class="touch-control bottom-left" @click="onTimeDown">
				<view class="touch-icon">−</view>
				<view class="touch-label">时间减</view>
			</view>
			<view class="touch-control bottom-right" @click="onTimeUp">
				<view class="touch-icon">+</view>
				<view class="touch-label">时间加</view>
			</view>
		</view>

		<!-- 模式选择 -->
		<view class="section">
			<view class="section-title">烹饪模式</view>
			<view class="mode-grid">
				<view v-for="(mode, index) in cookingModes" :key="index" class="mode-item" :class="{ active: currentMode === mode.label }" @click="selectMode(mode)">
					<view class="mode-icon">{{ mode.icon }}</view>
					<view class="mode-label">{{ mode.label }}</view>
				</view>
			</view>
		</view>

		<!-- 控制按钮 -->
		<view class="control-buttons">
			<view class="btn btn-start" :class="{ active: isCooking }" @click="toggleCooking">
				{{ isCooking ? '暂停' : '开始烹饪' }}
			</view>
			<view class="btn btn-stop" @click="stopCooking">停止</view>
		</view>

		<!-- 温度/时间滑块 -->
		<view class="section">
			<view class="slider-group">
				<view class="slider-item">
					<text class="slider-label">温度: {{ currentTemp }}°C</text>
					<slider :value="currentTemp" min="0" max="250" step="5" backgroundColor="#2a2a4a" activeColor="#e94560" blockColor="#e94560" blockSize="20" @change="onTempChange" />
				</view>
				<view class="slider-item">
					<text class="slider-label">时间: {{ currentTime }} 分钟</text>
					<slider :value="currentTime" min="0" max="180" step="1" backgroundColor="#2a2a4a" activeColor="#0f3460" blockColor="#0f3460" blockSize="20" @change="onTimeChange" />
				</view>
			</view>
		</view>

		<!-- 设备连接区域 -->
		<view class="section">
			<view class="section-title">
				设备连接
				<text class="device-count" v-if="devices.length > 0">发现 {{ devices.length }} 个设备</text>
			</view>
			
			<view class="scan-area">
				<view class="btn-scan" :class="{ scanning: isScanning }" @click="scanDevice">
					<view class="scan-icon" v-if="isScanning">
						<view class="scan-dot"></view>
						<view class="scan-dot"></view>
						<view class="scan-dot"></view>
					</view>
					<text>{{ isScanning ? '扫描中...' : '扫描设备' }}</text>
				</view>
			</view>

			<view class="scan-tip" v-if="!isScanning && devices.length === 0 && !hasScanned">
				点击"扫描设备"搜索附近的蓝牙设备
			</view>

			<view class="scanning-indicator" v-if="isScanning">
				<view class="scanning-wave"></view>
				<text class="scanning-text">正在搜索设备...</text>
			</view>

			<view class="device-list" v-if="devices.length > 0">
				<view v-for="device in devices" :key="device.deviceId" class="device-item" :class="{ connecting: connectingId === device.deviceId, connected: deviceConnected && deviceId === device.deviceId }" @click="connectDevice(device)">
					<view class="device-icon">
						<text class="device-emoji">{{ getDeviceIcon(device) }}</text>
					</view>
					<view class="device-info">
						<view class="device-name-row">
							<text class="device-name">{{ device.name || '未知设备' }}</text>
							<text class="device-status-tag" v-if="deviceConnected && deviceId === device.deviceId">已连接</text>
						</view>
						<view class="device-meta">
							<text class="device-meta-item">
								<text class="meta-label">信号</text>
								<text class="meta-value" :style="{ color: getRSSIColor(device.RSSI) }">{{ device.RSSI || 0 }} dBm</text>
							</text>
							<text class="device-meta-item">
								<text class="meta-label">地址</text>
								<text class="meta-value addr">{{ formatDeviceId(device.deviceId) }}</text>
							</text>
						</view>
					</view>
					<view class="device-action">
						<view v-if="deviceConnected && deviceId === device.deviceId" class="action-btn connected">已连接</view>
						<view v-else-if="connectingId === device.deviceId" class="action-btn connecting">连接中...</view>
						<view v-else class="action-btn connect">连接</view>
					</view>
				</view>
			</view>

			<view class="empty-result" v-if="!isScanning && hasScanned && devices.length === 0">
				<text class="empty-icon">📡</text>
				<text class="empty-text">未发现设备</text>
				<text class="empty-tip">请确保设备已开机并靠近手机</text>
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
				devices: [],
				connectingId: '',
				isScanning: false,
				hasScanned: false,
				isCooking: false,
				currentTemp: 180,
				currentTime: 30,
				currentMode: '煎炸',
				cookingModes: [
					{ label: '煎炸', value: CMD.MODE_FRY, icon: '🍳' },
					{ label: '炖煮', value: CMD.MODE_STEW, icon: '🍲' },
					{ label: '蒸', value: CMD.MODE_STEAM, icon: '♨️' },
					{ label: '烘焙', value: CMD.MODE_BAKE, icon: '🥧' },
					{ label: '保温', value: CMD.MODE_WARM, icon: '🔥' },
				]
			}
		},

		onLoad() {
			this.initBLE()
		},

		onUnload() {
			this.stopScan()
		},

		methods: {
			async initBLE() {
				try {
					await bleManager.init()
					console.log('蓝牙初始化成功')
					bleManager.onStatusChange((connected) => {
						this.deviceConnected = connected
						if (!connected) this.connectingId = ''
					})
					bleManager.onMessage((data) => {
						this.handleDeviceMessage(data)
					})
				} catch (err) {
					console.error('蓝牙初始化失败', err)
				}
			},

			async scanDevice() {
				if (this.isScanning) return
				this.isScanning = true
				this.hasScanned = true
				this.devices = []
				try {
					await bleManager.startScan()
					uni.onBluetoothDeviceFound((res) => {
						const foundDevices = res.devices || []
						foundDevices.forEach(device => {
							if (device.name && device.name.trim() !== '') {
								const exists = this.devices.some(d => d.deviceId === device.deviceId)
								if (!exists) {
									this.devices.push(device)
								} else {
									const idx = this.devices.findIndex(d => d.deviceId === device.deviceId)
									if (idx !== -1 && device.RSSI) {
										this.devices[idx].RSSI = device.RSSI
									}
								}
							}
						})
					})
					setTimeout(() => { this.stopScan() }, 8000)
				} catch (err) {
					console.error('扫描失败', err)
					this.isScanning = false
				}
			},

			async stopScan() {
				try { await bleManager.stopScan() } catch (err) { console.error(err) }
				this.isScanning = false
			},

			async connectDevice(device) {
				if (this.connectingId) return
				if (this.deviceConnected && this.deviceId === device.deviceId) return
				this.connectingId = device.deviceId
				try {
					uni.showLoading({ title: '连接中...' })
					await bleManager.connect(device.deviceId, device.name)
					this.deviceName = device.name
					this.deviceId = device.deviceId
					this.deviceConnected = true
					this.connectingId = ''
					uni.hideLoading()
					uni.showToast({ title: '连接成功', icon: 'success' })
				} catch (err) {
					this.connectingId = ''
					uni.hideLoading()
					uni.showToast({ title: '连接失败', icon: 'none' })
				}
			},

			async disconnectDevice() {
				try {
					await bleManager.disconnect()
					this.deviceConnected = false
					this.deviceId = ''
					this.deviceName = ''
					uni.showToast({ title: '已断开', icon: 'success' })
				} catch (err) { console.error('断开失败', err) }
			},

			async selectMode(mode) {
				this.currentMode = mode.label
				if (this.deviceConnected) {
					try {
						await bleManager.setMode(mode.value)
						uni.showToast({ title: `已切换${mode.label}模式`, icon: 'none' })
					} catch (err) { console.error('切换模式失败', err) }
				}
			},

			async toggleCooking() {
				if (!this.deviceConnected) { uni.showToast({ title: '请先连接设备', icon: 'none' }); return }
				try {
					if (this.isCooking) { await bleManager.sendCommand(CMD.PAUSE); this.isCooking = false }
					else { await bleManager.sendCommand(CMD.START); this.isCooking = true }
				} catch (err) { console.error('控制失败', err) }
			},

			async stopCooking() {
				if (!this.deviceConnected) return
				try { await bleManager.sendCommand(CMD.STOP); this.isCooking = false; uni.showToast({ title: '已停止', icon: 'none' }) }
				catch (err) { console.error('停止失败', err) }
			},

			onTempUp() { if (this.currentTemp < 250) { this.currentTemp += 5; if (this.deviceConnected) bleManager.setTemperature(this.currentTemp) } },
			onTempDown() { if (this.currentTemp > 0) { this.currentTemp -= 5; if (this.deviceConnected) bleManager.setTemperature(this.currentTemp) } },
			onTempChange(e) { this.currentTemp = e.detail.value; if (this.deviceConnected) bleManager.setTemperature(this.currentTemp) },
			onTimeUp() { if (this.currentTime < 180) { this.currentTime += 1; if (this.deviceConnected) bleManager.setTime(this.currentTime) } },
			onTimeDown() { if (this.currentTime > 0) { this.currentTime -= 1; if (this.deviceConnected) bleManager.setTime(this.currentTime) } },
			onTimeChange(e) { this.currentTime = e.detail.value; if (this.deviceConnected) bleManager.setTime(this.currentTime) },

			handleDeviceMessage(data) {
				console.log('设备消息:', data)
				if (data.startsWith('>T')) { const t = parseInt(data.substring(2)); if (!isNaN(t)) this.currentTemp = t }
				else if (data.startsWith('>U')) { const t = parseInt(data.substring(2)); if (!isNaN(t)) this.currentTime = t }
			},

			getDeviceIcon(device) {
				const name = (device.name || '').toLowerCase()
				if (name.includes('cook') || name.includes('烹饪') || name.includes('灶')) return '🔥'
				if (name.includes('phone') || name.includes('手机')) return '📱'
				if (name.includes('watch') || name.includes('手表')) return '⌚'
				if (name.includes('ear') || name.includes('耳机')) return '🎧'
				if (name.includes('speaker') || name.includes('音箱')) return '🔊'
				if (name.includes('light') || name.includes('灯')) return '💡'
				return '📡'
			},

			getRSSIColor(rssi) {
				if (!rssi) return '#666'
				if (rssi > -50) return '#2ecc71'
				if (rssi > -70) return '#f39c12'
				return '#e74c3c'
			},

			formatDeviceId(id) {
				if (!id) return '--'
				return id.substring(0, 8) + '...' + id.substring(id.length - 4)
			},

			formatTime(minutes) {
				if (!minutes && minutes !== 0) return '--:--'
				const h = Math.floor(minutes / 60)
				const m = minutes % 60
				return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
			}
		}
	}
</script>

<style>
.container { padding-bottom: 40rpx; }

/* 状态栏 */
.status-bar { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 24rpx; background: #1a1a2e; border-bottom: 1rpx solid #2a2a4a; }
.device-status { display: flex; align-items: center; gap: 12rpx; }
.status-text { font-size: 24rpx; color: #a0a0b0; }
.device-name { font-size: 24rpx; color: #e94560; flex: 1; text-align: center; }
.disconnect-btn { padding: 8rpx 20rpx; background: rgba(231,76,60,0.15); border: 1rpx solid #e74c3c; border-radius: 20rpx; font-size: 22rpx; color: #e74c3c; }
.disconnect-btn:active { background: rgba(231,76,60,0.3); }

/* 操控面板 */
.control-panel { position: relative; width: 600rpx; height: 600rpx; margin: 40rpx auto; background: linear-gradient(145deg,#1a1a2e,#16213e); border-radius: 50%; box-shadow: 0 20rpx 60rpx rgba(0,0,0,0.5), inset 0 4rpx 20rpx rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; border: 2rpx solid #2a2a4a; }
.touch-control { position: absolute; width: 120rpx; height: 120rpx; border-radius: 50%; background: linear-gradient(145deg,#2a2a4a,#1a1a2e); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.4); border: 2rpx solid #3a3a5a; transition: all 0.2s; }
.touch-control:active { transform: scale(0.92); background: linear-gradient(145deg,#3a3a5a,#2a2a4a); }
.touch-control.top-left { top: 40rpx; left: 40rpx; }
.touch-control.top-right { top: 40rpx; right: 40rpx; }
.touch-control.bottom-left { bottom: 40rpx; left: 40rpx; }
.touch-control.bottom-right { bottom: 40rpx; right: 40rpx; }
.touch-icon { font-size: 48rpx; font-weight: bold; color: #e94560; line-height: 1; }
.touch-label { font-size: 18rpx; color: #a0a0b0; margin-top: 4rpx; }

/* 显示屏 */
.display-screen { width: 280rpx; height: 280rpx; border-radius: 50%; background: linear-gradient(135deg,#0a0a1a,#16213e); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 0 40rpx rgba(0,0,0,0.8); border: 2rpx solid #3a3a5a; }
.display-mode { font-size: 28rpx; color: #e94560; font-weight: 600; margin-bottom: 8rpx; }
.display-temp { font-size: 72rpx; font-weight: bold; color: #fff; line-height: 1; text-shadow: 0 0 20rpx rgba(233,69,96,0.3); }
.display-time { font-size: 32rpx; color: #a0a0b0; margin-top: 8rpx; font-family: 'Courier New', monospace; }
.display-status { font-size: 20rpx; color: #2ecc71; margin-top: 8rpx; display: flex; align-items: center; gap: 8rpx; }
.cooking-dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #2ecc71; animation: pulse 1s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

/* 通用区块 */
.section { margin: 24rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: #fff; margin-bottom: 20rpx; padding-left: 16rpx; border-left: 6rpx solid #e94560; display: flex; align-items: center; justify-content: space-between; }
.device-count { font-size: 22rpx; color: #a0a0b0; font-weight: 400; }

/* 模式网格 */
.mode-grid { display: flex; justify-content: space-between; gap: 16rpx; }
.mode-item { flex: 1; background: #1a1a2e; border-radius: 20rpx; padding: 20rpx 8rpx; display: flex; flex-direction: column; align-items: center; gap: 8rpx; border: 2rpx solid #2a2a4a; transition: all 0.3s; }
.mode-item.active { border-color: #e94560; background: linear-gradient(135deg,#1a1a2e,#2a1a2e); box-shadow: 0 0 20rpx rgba(233,69,96,0.2); }
.mode-item:active { transform: scale(0.95); }
.mode-icon { font-size: 48rpx; }
.mode-label { font-size: 22rpx; color: #a0a0b0; }
.mode-item.active .mode-label { color: #e94560; font-weight: 600; }

/* 控制按钮 */
.control-buttons { display: flex; gap: 24rpx; padding: 0 24rpx; margin: 32rpx 0; }
.btn { flex: 1; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; font-size: 32rpx; font-weight: 600; transition: all 0.2s; }
.btn:active { transform: scale(0.96); }
.btn-start { background: linear-gradient(135deg,#e94560,#c23152); color: #fff; box-shadow: 0 8rpx 24rpx rgba(233,69,96,0.3); }
.btn-start.active { background: linear-gradient(135deg,#f39c12,#e67e22); box-shadow: 0 8rpx 24rpx rgba(243,156,18,0.3); }
.btn-stop { background: #2a2a4a; color: #a0a0b0; border: 2rpx solid #3a3a5a; }

/* 滑块 */
.slider-group { background: #1a1a2e; border-radius: 24rpx; padding: 32rpx; }
.slider-item { margin-bottom: 24rpx; }
.slider-item:last-child { margin-bottom: 0; }
.slider-label { font-size: 26rpx; color: #a0a0b0; margin-bottom: 12rpx; display: block; }

/* 设备连接 */
.scan-area { margin-bottom: 20rpx; }
.btn-scan { height: 88rpx; background: linear-gradient(135deg,#e94560,#c23152); border-radius: 44rpx; display: flex; align-items: center; justify-content: center; gap: 16rpx; font-size: 30rpx; color: #fff; font-weight: 600; box-shadow: 0 8rpx 24rpx rgba(233,69,96,0.3); transition: all 0.3s; }
.btn-scan:active { transform: scale(0.97); }
.btn-scan.scanning { background: linear-gradient(135deg,#f39c12,#e67e22); box-shadow: 0 8rpx 24rpx rgba(243,156,18,0.3); }
.scan-icon { display: flex; gap: 6rpx; }
.scan-dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #fff; animation: scanDot 1.4s infinite ease-in-out both; }
.scan-dot:nth-child(1) { animation-delay: -0.32s; }
.scan-dot:nth-child(2) { animation-delay: -0.16s; }
.scan-dot:nth-child(3) { animation-delay: 0s; }
@keyframes scanDot { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }
.scan-tip { text-align: center; padding: 40rpx 0; font-size: 26rpx; color: #666; }

/* 扫描中动画 */
.scanning-indicator { display: flex; flex-direction: column; align-items: center; padding: 40rpx 0; gap: 20rpx; }
.scanning-wave { width: 120rpx; height: 120rpx; border-radius: 50%; border: 4rpx solid #e94560; animation: wave 2s infinite; position: relative; }
.scanning-wave::before { content: ''; position: absolute; top: -20rpx; left: -20rpx; right: -20rpx; bottom: -20rpx; border-radius: 50%; border: 4rpx solid rgba(233,69,96,0.3); animation: wave 2s infinite 0.5s; }
.scanning-wave::after { content: ''; position: absolute; top: -40rpx; left: -40rpx; right: -40rpx; bottom: -40rpx; border-radius: 50%; border: 4rpx solid rgba(233,69,96,0.1); animation: wave 2s infinite 1s; }
@keyframes wave { 0% { transform: scale(0.5); opacity: 1; } 100% { transform: scale(1.5); opacity: 0; } }
.scanning-text { font-size: 26rpx; color: #a0a0b0; }

/* 设备列表 */
.device-list { background: #1a1a2e; border-radius: 24rpx; overflow: hidden; border: 1rpx solid #2a2a4a; }
.device-item { display: flex; align-items: center; gap: 20rpx; padding: 24rpx 28rpx; border-bottom: 1rpx solid #2a2a4a; transition: all 0.2s; }
.device-item:last-child { border-bottom: none; }
.device-item:active { background: #2a2a4a; }
.device-item.connected { background: rgba(46,204,113,0.05); border-left: 4rpx solid #2ecc71; }
.device-item.connecting { background: rgba(243,156,18,0.05); border-left: 4rpx solid #f39c12; }
.device-icon { width: 72rpx; height: 72rpx; border-radius: 16rpx; background: #2a2a4a; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.device-emoji { font-size: 36rpx; }
.device-info { flex: 1; min-width: 0; }
.device-name-row { display: flex; align-items: center; gap: 12rpx; }
.device-name { font-size: 28rpx; color: #fff; font-weight: 500; }
.device-status-tag { padding: 2rpx 12rpx; background: rgba(46,204,113,0.15); border: 1rpx solid rgba(46,204,113,0.3); border-radius: 12rpx; font-size: 18rpx; color: #2ecc71; }
.device-meta { display: flex; gap: 24rpx; margin-top: 8rpx; }
.device-meta-item { font-size: 20rpx; display: flex; align-items: center; gap: 4rpx; }
.meta-label { color: #666; }
.meta-value { color: #a0a0b0; font-weight: 500; }
.meta-value.addr { font-family: 'Courier New', monospace; font-size: 18rpx; color: #666; }
.device-action { flex-shrink: 0; }
.action-btn { padding: 12rpx 28rpx; border-radius: 30rpx; font-size: 24rpx; font-weight: 500; text-align: center; min-width: 100rpx; }
.action-btn.connect { background: linear-gradient(135deg,#e94560,#c23152); color: #fff; }
.action-btn.connecting { background: #2a2a4a; color: #f39c12; border: 1rpx solid #f39c12; }
.action-btn.connected { background: rgba(46,204,113,0.15); color: #2ecc71; border: 1rpx solid rgba(46,204,113,0.3); }

/* 空结果 */
.empty-result { display: flex; flex-direction: column; align-items: center; padding: 60rpx 0; gap: 12rpx; }
.empty-icon { font-size: 64rpx; }
.empty-text { font-size: 28rpx; color: #a0a0b0; font-weight: 500; }
.empty-tip { font-size: 24rpx; color: #666; }
</style>
