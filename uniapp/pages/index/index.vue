<template>
	<view class="container">
		<!-- 蓝牙连接状态栏 -->
		<view class="status-bar">
			<view class="device-status">
				<text class="status-dot" :class="deviceConnected ? 'online' : 'offline'"></text>
				<text class="status-text">{{ deviceConnected ? '已连接' : '未连接' }}</text>
			</view>
			<view class="device-name" v-if="deviceName">{{ deviceName }}</view>
			<view class="disconnect-btn" v-if="deviceConnected" @click="disconnectDevice">断开</view>
		</view>

		<!-- 设备扫描区域 -->
		<view class="section">
			<view class="section-title">
				蓝牙设备
				<text class="device-count" v-if="devices.length > 0">发现 {{ devices.length }} 个设备</text>
			</view>
			
			<view class="scan-area">
				<view class="btn-scan" :class="{ scanning: isScanning }" @click="scanDevice">
					<text>{{ isScanning ? '扫描中...' : '扫描设备' }}</text>
				</view>
			</view>

			<view class="scan-tip" v-if="!isScanning && devices.length === 0 && !hasScanned">
				点击"扫描设备"搜索附近的蓝牙设备
			</view>

			<view class="device-list" v-if="devices.length > 0">
				<view v-for="device in devices" :key="device.deviceId" class="device-item" :class="{ connecting: connectingId === device.deviceId, connected: deviceConnected && deviceId === device.deviceId }" @click="connectDevice(device)">
					<view class="device-icon">
						<text class="device-emoji">📡</text>
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

		<!-- ===== 设备操控面板（连接后显示） ===== -->
		<view class="section" v-if="deviceConnected">
			<view class="section-title">设备操控面板</view>
			
			<!-- 操控面板主体 - 模拟真实设备 -->
			<view class="device-panel">
				<!-- 设备名称 -->
				<view class="panel-header">
					<text class="panel-header-name">{{ deviceName || '智能动热灶' }}</text>
					<text class="panel-header-status" :class="'dot-' + deviceStatus">{{ statusText }}</text>
				</view>

				<!-- 中间显示屏 -->
				<view class="panel-screen">
					<!-- 倒计时运行中 - 显示剩余时间 -->
					<view class="screen-timer" v-if="countdownTimer && currentTime > 0">
						<text class="screen-timer-value">{{ timerDisplay }}</text>
						<text class="screen-timer-label">剩余时间</text>
					</view>
					<!-- 定时设定模式 -->
					<view class="screen-timer" v-else-if="timingMode">
						<text class="screen-timer-value">{{ timerDisplay }}</text>
						<text class="screen-timer-label">设定时间</text>
					</view>
					<!-- 待机/档位显示 -->
					<view class="screen-gear" v-else>
						<text class="screen-gear-prefix">-</text>
						<text class="screen-gear-value" :class="{ 'text-green': devicePower && deviceGear > 0 }">P{{ deviceGear }}</text>
						<text class="screen-gear-suffix">-</text>
					</view>
					
					<!-- 档位指示灯（P1亮1个，P5亮5个...） -->
					<view class="screen-indicators" v-if="devicePower && deviceGear > 0">
						<view v-for="i in 12" :key="i" class="indicator-bar" :class="{ active: i <= deviceGear }"></view>
					</view>
				</view>

				<!-- 五个按键：定时 | 减 | 显示屏(占位) | 加 | 开关 -->
				<view class="panel-keys">
					<!-- 定时键 -->
					<view class="panel-key" @click="onTimerKey">
						<view class="key-icon">⏱</view>
						<view class="key-label">定时</view>
					</view>

					<!-- 减键 -->
					<view class="panel-key" @click="onMinusKey">
						<view class="key-icon">−</view>
						<view class="key-label">减</view>
					</view>

					<!-- 中间装饰（对应显示屏位置，不可点击） -->
					<view class="panel-key spacer">
						<view class="key-icon">⬤</view>
						<view class="key-label">·</view>
					</view>

					<!-- 加键 -->
					<view class="panel-key" @click="onPlusKey">
						<view class="key-icon">+</view>
						<view class="key-label">加</view>
					</view>

					<!-- 开关键 -->
					<view class="panel-key power" :class="{ 'is-on': devicePower }" @click="onPowerKey">
						<view class="key-icon">{{ devicePower ? '🔴' : '⚪' }}</view>
						<view class="key-label">{{ devicePower ? '关' : '开' }}</view>
					</view>
				</view>

				<!-- 操作提示 -->
				<view class="panel-tips">
					<text class="tip-text" v-if="!devicePower">双击开关按键开机</text>
					<text class="tip-text" v-else-if="timingMode">按加/减调整时间，再按定时确认</text>
					<text class="tip-text" v-else-if="deviceGear === 0">点击"加"开始工作</text>
					<text class="tip-text" v-else>点击加/减调整火力</text>
				</view>

				<!-- 模拟报警按钮（无设备时测试用） -->
				<view class="simulate-section">
					<view class="simulate-btn" @click="showAlarmPicker = true">
						<text class="simulate-icon">🧪</text>
						<text class="simulate-text">模拟异常报警</text>
					</view>
				</view>
			</view>
		</view>

		<!-- ===== 模拟报警选择弹窗 ===== -->
		<view class="modal-mask" v-if="showAlarmPicker" @click="showAlarmPicker = false">
			<view class="modal-content" @click.stop>
				<view class="modal-title">选择模拟的异常类型</view>
				<view class="alarm-sim-list">
					<view v-for="item in alarmTypes" :key="item.code" class="alarm-sim-item" @click="simulateAlarm(item.code)">
						<text class="alarm-sim-code">{{ item.code }}</text>
						<text class="alarm-sim-desc">{{ item.desc }}</text>
						<text class="alarm-sim-arrow">›</text>
					</view>
				</view>
				<view class="modal-close" @click="showAlarmPicker = false">取消</view>
			</view>
		</view>

		<!-- 指令日志 -->
		<view class="section" v-if="logs.length > 0">
			<view class="section-title">
				指令日志
				<text class="clear-log" @click="clearLogs">清空</text>
			</view>
			<view class="log-list">
				<view v-for="(log, index) in logs" :key="index" class="log-item" :class="log.type">
					<text class="log-time">{{ log.time }}</text>
					<text class="log-content">{{ log.content }}</text>
				</view>
			</view>
		</view>

		<!-- 异常报警区域 -->
		<view class="section" v-if="alarms.length > 0">
			<view class="section-title" style="color: #e74c3c;">
				异常报警
				<text class="clear-log" @click="clearAlarms">清空</text>
			</view>
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
	import bleManager, { CMD, GEAR_NAMES, ALARM_DESCS } from '@/utils/ble.js'

	export default {
		data() {
			return {
				// 蓝牙连接相关
				deviceConnected: false,
				deviceName: '',
				deviceId: '',
				devices: [],
				connectingId: '',
				isScanning: false,
				hasScanned: false,
				commandText: '',
				logs: [],
				alarms: [],

				// ===== 操控面板数据（真实设备模拟） =====
				// 设备电源状态
				devicePower: false,
				// 设备状态: idle | running | paused | heating | standby
				deviceStatus: 'idle',
				// 当前档位 (0-12, 0=P0待机)
				deviceGear: 0,
				// 当前温度（从设备上报获取）
				currentTemp: 0,
				// 3路温度值
				tempChannel1: 0,
				tempChannel2: 0,
				tempChannel3: 0,
				// 电参数
				voltage: 0,
				power: 0,
				current: 0,
				// 当前剩余时间（分钟）
				currentTime: 0,
				// 倒计时定时器
				countdownTimer: null,

				// 定时模式
				timingMode: false,
				// 定时设置临时值（分钟）
				timerSetting: 0,

				// 开关双击检测
				powerClickCount: 0,
				powerClickTimer: null,

				// 模拟报警弹窗
				showAlarmPicker: false,
				// 异常类型列表（用于模板遍历）
				alarmTypes: Object.entries(ALARM_DESCS).map(([code, desc]) => ({ code, desc })),
			}
		},


		computed: {
			// 定时显示（mm:ss格式）- 设定模式显示设定值，倒计时模式显示剩余时间
			timerDisplay() {
				const totalSeconds = this.timingMode ? this.timerSetting * 60 : this.currentTime
				const m = Math.floor(totalSeconds / 60)
				const s = totalSeconds % 60
				return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
			},

			// 状态文本
			statusText() {
				const map = {
					idle: '待机',
					running: '运行中',
					paused: '已暂停',
					heating: '加热中',
					standby: '待机'
				}
				return map[this.deviceStatus] || '未知'
			},
			// 显示时间
			displayTime() {
				if (this.currentTime <= 0) return '--:--'
				const h = Math.floor(this.currentTime / 60)
				const m = this.currentTime % 60
				if (h > 0) {
					return `${h}时${m.toString().padStart(2, '0')}分`
				}
				return `${m}分`
			}
		},

		onLoad() {
			this.initBLE()
		},

		onUnload() {
			this.stopScan()
			this.clearCountdown()
		},

		methods: {
			// ===== 真实设备按键操作 =====

			/**
			 * 开关键 - 双击开机/单击关机
			 * 操作说明：双击开机→显示P0→点击加开始P1工作
			 */
			onPowerKey() {
				if (!this.deviceConnected) {
					uni.showToast({ title: '设备未连接', icon: 'none' })
					return
				}
				if (this.devicePower) {
					// 已开机：单击关机
					this.sendQuickCommand(CMD.OK)
					this.devicePower = false
					this.deviceGear = 0
					this.deviceStatus = 'idle'
					this.timingMode = false
					this.clearCountdown()
					this.addLog('system', '设备已关机')
				} else {
					// 未开机：双击开机
					this.powerClickCount++
					if (this.powerClickCount === 1) {
						this.powerClickTimer = setTimeout(() => {
							this.powerClickCount = 0
						}, 500)
					} else if (this.powerClickCount >= 2) {
						clearTimeout(this.powerClickTimer)
						this.powerClickCount = 0
						// 双击开机
						this.sendQuickCommand(CMD.OK)
						this.devicePower = true
						this.deviceGear = 0
						this.deviceStatus = 'idle'
						this.addLog('system', '设备已开机，显示 P0')
						uni.showToast({ title: '已开机 P0', icon: 'success' })
					}
				}
			},

			/**
			 * 加键 - 增加档位/增加定时时间
			 */
			onPlusKey() {
				if (!this.deviceConnected || !this.devicePower) return
				if (this.timingMode) {
					// 定时模式：增加时间（步长1分钟）
					this.timerSetting = Math.min(this.timerSetting + 1, 180)
				} else {
					// 正常模式：增加档位（P0→P1开始工作，最高P12）
					if (this.deviceGear < 12) {
						this.deviceGear++
						this.sendQuickCommand(CMD.OK)
						this.deviceStatus = 'running'
						this.addLog('system', `档位升至: P${this.deviceGear}`)
					}
				}
			},

			/**
			 * 减键 - 减小档位/减少定时时间
			 */
			onMinusKey() {
				if (!this.deviceConnected || !this.devicePower) return
				if (this.timingMode) {
					// 定时模式：减少时间
					this.timerSetting = Math.max(this.timerSetting - 1, 0)
				} else {
					// 正常模式：减小档位
					if (this.deviceGear > 0) {
						this.deviceGear--
						this.sendQuickCommand(CMD.OK)
						if (this.deviceGear === 0) {
							this.deviceStatus = 'idle'
							this.addLog('system', '档位降至: P0 待机')
						} else {
							this.addLog('system', `档位降至: P${this.deviceGear}`)
						}
					}
				}
			},

			/**
			 * 定时键 - 进入/退出定时设定
			 */
			onTimerKey() {
				if (!this.deviceConnected || !this.devicePower) return
				if (this.timingMode) {
					// 再次按定时：完成设定，开始计时
					this.currentTime = this.timerSetting
					this.timingMode = false
					if (this.currentTime > 0) {
						this.startCountdown()
						this.addLog('system', `定时设定完成: ${this.displayTime}`)
						uni.showToast({ title: `定时 ${this.displayTime}`, icon: 'success' })
					}
				} else {
					// 进入定时设定模式
					this.timerSetting = this.currentTime || 0
					this.timingMode = true
					this.addLog('system', '进入定时设定模式')
				}
			},

			async initBLE() {

				try {
					await bleManager.init()
					this.addLog('system', '蓝牙适配器初始化成功')
					bleManager.onStatusChange((connected) => {
						this.deviceConnected = connected
						if (!connected) this.connectingId = ''
					})
					bleManager.onMessage((data) => {
						this.handleDeviceMessage(data)
					})
				} catch (err) {
					this.addLog('error', '蓝牙初始化失败: ' + err.errMsg)
				}
			},

			async scanDevice() {
				if (this.isScanning) return
				this.isScanning = true
				this.hasScanned = true
				this.devices = []
				try {
					await bleManager.startScan()
					this.addLog('system', '开始扫描设备...')
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
					this.addLog('error', '扫描失败: ' + err.errMsg)
					this.isScanning = false
				}
			},

			async stopScan() {
				try { await bleManager.stopScan() } catch (err) { console.error(err) }
				this.isScanning = false
				this.addLog('system', '扫描结束')
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
					this.addLog('success', `已连接到设备: ${device.name}`)
					uni.showToast({ title: '连接成功', icon: 'success' })
				} catch (err) {
					this.connectingId = ''
					uni.hideLoading()
					this.addLog('error', '连接失败: ' + (err.errMsg || err.message))
					uni.showToast({ title: '连接失败', icon: 'none' })
				}
			},

			async disconnectDevice() {
				try {
					await bleManager.disconnect()
					this.deviceConnected = false
					this.deviceId = ''
					this.deviceName = ''
					this.addLog('system', '已断开设备连接')
					uni.showToast({ title: '已断开', icon: 'success' })
				} catch (err) { 
					this.addLog('error', '断开失败: ' + (err.errMsg || err.message))
				}
			},

			async sendCommand() {
				if (!this.commandText.trim()) {
					uni.showToast({ title: '请输入指令', icon: 'none' })
					return
				}
				if (!this.deviceConnected) {
					uni.showToast({ title: '设备未连接', icon: 'none' })
					return
				}
				try {
					await bleManager.sendCommand(this.commandText.trim())
					this.addLog('send', `发送: ${this.commandText.trim()}`)
					this.commandText = ''
				} catch (err) {
					this.addLog('error', `指令发送失败: ${this.commandText.trim()}`)
				}
			},

			async sendQuickCommand(cmd) {
				if (!this.deviceConnected) {
					uni.showToast({ title: '设备未连接', icon: 'none' })
					return
				}
				try {
					await bleManager.sendCommand(cmd)
					this.addLog('send', `发送: ${cmd}`)
				} catch (err) {
					this.addLog('error', `指令发送失败: ${cmd}`)
				}
			},

			handleDeviceMessage(data) {
				this.addLog('receive', `收到: ${data}`)

				// 1. 检测异常报警（12KW协议: >AE1~>AE6）
				if (bleManager.isAlarm(data)) {
					const desc = ALARM_DESCS[data] || '未知异常'
					this.addAlarm('设备异常', `${desc} (${data})`)
					return
				}

				// 2. 解析温度上报数据（>A + 12位十六进制）
				if (data.startsWith('>A') && data.length >= 14) {
					const tempData = bleManager.parseTemperatureData(data)
					if (tempData) {
						this.tempChannel1 = tempData.channel1
						this.tempChannel2 = tempData.channel2
						this.tempChannel3 = tempData.channel3
						// 显示第一路温度作为主温度
						this.currentTemp = tempData.channel1
						this.addLog('receive', `温度数据 - 1路:${tempData.channel1} 2路:${tempData.channel2} 3路:${tempData.channel3}`)
						return
					}
					// 尝试解析电参数
					const powerData = bleManager.parsePowerData(data)
					if (powerData) {
						this.voltage = powerData.voltage
						this.power = powerData.power
						this.current = powerData.current
						this.addLog('receive', `电参数 - 电压:${powerData.voltage} 功率:${powerData.power} 电流:${powerData.current}`)
						return
					}
				}

				// 3. 设备应答 >OK
				if (data === '>OK') {
					this.addLog('receive', '设备应答: 执行成功')
				}
			},

			addLog(type, content) {
				const now = new Date()
				const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
				this.logs.unshift({ type, content, time })
				// 最多保留50条日志
				if (this.logs.length > 50) {
					this.logs = this.logs.slice(0, 50)
				}
			},

			addAlarm(title, description) {
				const now = new Date()
				const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
				this.alarms.unshift({ title, description, time })
				uni.showToast({ title: '⚠️ ' + title, icon: 'none' })
			},

			clearLogs() {
				this.logs = []
			},

			clearAlarms() {
				this.alarms = []
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

			/**
			 * 开始倒计时
			 */
			startCountdown() {
				this.clearCountdown()
				// 将分钟转换为秒
				this.currentTime = this.timerSetting * 60
				this.countdownTimer = setInterval(() => {
					if (this.currentTime > 0) {
						this.currentTime--
						// 倒计时结束时自动关机
						if (this.currentTime <= 0) {
							this.clearCountdown()
							// 关机
							this.devicePower = false
							this.deviceGear = 0
							this.deviceStatus = 'idle'
							this.addLog('system', '定时结束，设备已关机')
							uni.showToast({ title: '⏰ 定时结束，已关机', icon: 'none' })
						}
					}
				}, 1000)
			},


			/**
			 * 清除倒计时
			 */
			clearCountdown() {
				if (this.countdownTimer) {
					clearInterval(this.countdownTimer)
					this.countdownTimer = null
				}
				this.currentTime = 0
			},

			/**
			 * 模拟异常报警（无设备时测试用）
			 */
			simulateAlarm(code) {
				this.showAlarmPicker = false
				const desc = ALARM_DESCS[code] || '未知异常'
				this.addLog('receive', `收到: ${code}`)
				this.addAlarm('设备异常', `${desc} (${code})`)
				uni.showToast({ title: `⚠️ ${desc}`, icon: 'none' })
			}

		}
	}
</script>

<style>
.container { padding-bottom: 40rpx; }

/* 状态栏 - 蓝白主题 */
.status-bar { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 24rpx; background: #ffffff; border-bottom: 1rpx solid #e8edf5; }
.device-status { display: flex; align-items: center; gap: 12rpx; }
.status-text { font-size: 24rpx; color: #7f8c9b; }
.device-name { font-size: 24rpx; color: #3498db; flex: 1; text-align: center; font-weight: 500; }
.disconnect-btn { padding: 8rpx 20rpx; background: #fff0f0; border: 1rpx solid #ff6b6b; border-radius: 20rpx; font-size: 22rpx; color: #ff6b6b; }
.disconnect-btn:active { background: #ffe0e0; }

/* 通用区块 */
.section { margin: 24rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: #2c3e50; margin-bottom: 20rpx; padding-left: 16rpx; border-left: 6rpx solid #3498db; display: flex; align-items: center; justify-content: space-between; }
.device-count { font-size: 22rpx; color: #95a5a6; font-weight: 400; }
.clear-log { font-size: 22rpx; color: #3498db; font-weight: 400; padding: 4rpx 12rpx; border: 1rpx solid #3498db; border-radius: 12rpx; }
.clear-log:active { background: rgba(52,152,219,0.1); }

/* 扫描区域 */
.scan-area { margin-bottom: 20rpx; }
.btn-scan { height: 88rpx; background: linear-gradient(135deg, #3498db, #2980b9); border-radius: 44rpx; display: flex; align-items: center; justify-content: center; gap: 16rpx; font-size: 30rpx; color: #fff; font-weight: 600; box-shadow: 0 8rpx 24rpx rgba(52,152,219,0.3); transition: all 0.3s; }
.btn-scan:active { transform: scale(0.97); }
.btn-scan.scanning { background: linear-gradient(135deg, #f39c12, #e67e22); box-shadow: 0 8rpx 24rpx rgba(243,156,18,0.3); }
.scan-tip { text-align: center; padding: 40rpx 0; font-size: 26rpx; color: #95a5a6; }

/* 设备列表 */
.device-list { background: #ffffff; border-radius: 24rpx; overflow: hidden; border: 1rpx solid #e8edf5; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04); }
.device-item { display: flex; align-items: center; gap: 20rpx; padding: 24rpx 28rpx; border-bottom: 1rpx solid #f0f4fa; transition: all 0.2s; }
.device-item:last-child { border-bottom: none; }
.device-item:active { background: #f8faff; }
.device-item.connected { background: rgba(46,204,113,0.03); border-left: 4rpx solid #2ecc71; }
.device-item.connecting { background: rgba(243,156,18,0.03); border-left: 4rpx solid #f39c12; }
.device-icon { width: 72rpx; height: 72rpx; border-radius: 16rpx; background: #f0f6ff; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.device-emoji { font-size: 36rpx; }
.device-info { flex: 1; min-width: 0; }
.device-name-row { display: flex; align-items: center; gap: 12rpx; }
.device-name { font-size: 28rpx; color: #2c3e50; font-weight: 500; }
.device-status-tag { padding: 2rpx 12rpx; background: rgba(46,204,113,0.1); border: 1rpx solid rgba(46,204,113,0.3); border-radius: 12rpx; font-size: 18rpx; color: #2ecc71; }
.device-meta { display: flex; gap: 24rpx; margin-top: 8rpx; }
.device-meta-item { font-size: 20rpx; display: flex; align-items: center; gap: 4rpx; }
.meta-label { color: #95a5a6; }
.meta-value { color: #7f8c9b; font-weight: 500; }
.meta-value.addr { font-family: 'Courier New', monospace; font-size: 18rpx; color: #b0bec5; }
.device-action { flex-shrink: 0; }
.action-btn { padding: 12rpx 28rpx; border-radius: 30rpx; font-size: 24rpx; font-weight: 500; text-align: center; min-width: 100rpx; }
.action-btn.connect { background: linear-gradient(135deg, #3498db, #2980b9); color: #fff; }
.action-btn.connecting { background: #f8faff; color: #f39c12; border: 1rpx solid #f39c12; }
.action-btn.connected { background: rgba(46,204,113,0.1); color: #2ecc71; border: 1rpx solid rgba(46,204,113,0.3); }

/* 空结果 */
.empty-result { display: flex; flex-direction: column; align-items: center; padding: 60rpx 0; gap: 12rpx; }
.empty-icon { font-size: 64rpx; }
.empty-text { font-size: 28rpx; color: #7f8c9b; font-weight: 500; }
.empty-tip { font-size: 24rpx; color: #95a5a6; }

/* ===== 设备操控面板 - 模拟真实设备 ===== */
.device-panel { background: #ffffff; border-radius: 32rpx; padding: 28rpx; border: 1rpx solid #e8edf5; box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.06); }

/* 面板头部 */
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; padding: 0 8rpx; }
.panel-header-name { font-size: 26rpx; color: #2c3e50; font-weight: 600; }
.panel-header-status { font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 20rpx; }
.panel-header-status.dot-idle { background: #f0f4fa; color: #95a5a6; }
.panel-header-status.dot-running { background: rgba(46,204,113,0.1); color: #2ecc71; }
.panel-header-status.dot-paused { background: rgba(243,156,18,0.1); color: #f39c12; }
.panel-header-status.dot-heating { background: rgba(231,76,60,0.1); color: #e74c3c; }

/* 中间显示屏 - 模拟真实设备LED屏 */
.panel-screen { background: #1a1a2e; border-radius: 20rpx; padding: 32rpx 24rpx; margin-bottom: 28rpx; text-align: center; min-height: 200rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16rpx; box-shadow: inset 0 4rpx 16rpx rgba(0,0,0,0.3), 0 0 20rpx rgba(26,26,46,0.3); }

/* 档位显示 - 七段数码管风格 */
.screen-gear { display: flex; align-items: center; justify-content: center; gap: 12rpx; }
.screen-gear-prefix, .screen-gear-suffix { font-size: 48rpx; color: #4a4a6a; font-weight: 300; }
.screen-gear-value { font-size: 96rpx; font-weight: 700; color: #4a4a6a; font-family: 'Courier New', monospace; letter-spacing: 4rpx; transition: color 0.3s; }
.screen-gear-value.text-green { color: #00ff88; text-shadow: 0 0 20rpx rgba(0,255,136,0.5); }

/* 定时显示 */
.screen-timer { display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.screen-timer-value { font-size: 72rpx; font-weight: 700; color: #00ff88; font-family: 'Courier New', monospace; letter-spacing: 6rpx; text-shadow: 0 0 20rpx rgba(0,255,136,0.5); }
.screen-timer-label { font-size: 22rpx; color: #4a7a5a; letter-spacing: 4rpx; }


/* 档位指示灯条 */
.screen-indicators { display: flex; gap: 6rpx; width: 100%; justify-content: center; flex-wrap: wrap; }
.indicator-bar { width: 16rpx; height: 32rpx; border-radius: 4rpx; background: #2a2a4a; transition: all 0.3s; }
.indicator-bar.active { background: #00ff88; box-shadow: 0 0 12rpx rgba(0,255,136,0.6); }

/* 五个按键布局 */
.panel-keys { display: flex; gap: 16rpx; justify-content: center; margin-bottom: 20rpx; }
.panel-key { flex: 1; max-width: 120rpx; display: flex; flex-direction: column; align-items: center; gap: 8rpx; padding: 20rpx 8rpx; background: #f8fbff; border-radius: 20rpx; border: 2rpx solid #e0e6ef; transition: all 0.15s; }
.panel-key:active { transform: scale(0.92); background: #eef3fa; }
.panel-key.spacer { opacity: 0.3; pointer-events: none; }
.panel-key.power.is-on { border-color: #ff6b6b; background: linear-gradient(145deg, #fff5f5, #ffe8e8); }
.key-icon { font-size: 36rpx; line-height: 1; }
.key-label { font-size: 20rpx; color: #7f8c9b; font-weight: 500; }
.panel-key.power.is-on .key-label { color: #ff6b6b; }

/* 操作提示 */
.panel-tips { text-align: center; padding: 8rpx 0; }
.tip-text { font-size: 22rpx; color: #95a5a6; }

/* 模拟报警按钮 */
.simulate-section { margin-top: 20rpx; padding-top: 20rpx; border-top: 1rpx dashed #e0e6ef; }
.simulate-btn { display: flex; align-items: center; justify-content: center; gap: 12rpx; padding: 20rpx; background: #fff8f0; border: 1rpx dashed #ffa726; border-radius: 20rpx; }
.simulate-btn:active { background: #fff0e0; transform: scale(0.97); }
.simulate-icon { font-size: 28rpx; }
.simulate-text { font-size: 24rpx; color: #ff8c00; font-weight: 500; }

/* 弹窗 - 蓝白主题 */
.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(44,62,80,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-content { background: #ffffff; border-radius: 32rpx; padding: 32rpx; width: 85%; max-width: 600rpx; border: 1rpx solid #e8edf5; max-height: 80vh; overflow-y: auto; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.1); }
.modal-title { font-size: 32rpx; font-weight: 600; color: #2c3e50; text-align: center; margin-bottom: 28rpx; }
.modal-close { text-align: center; padding: 16rpx; font-size: 26rpx; color: #95a5a6; border-top: 1rpx solid #e8edf5; margin-top: 16rpx; }

/* 模拟报警列表 */
.alarm-sim-list { display: flex; flex-direction: column; gap: 12rpx; }
.alarm-sim-item { display: flex; align-items: center; gap: 16rpx; padding: 20rpx 24rpx; background: #f8fbff; border-radius: 16rpx; border: 1rpx solid #e8edf5; transition: all 0.2s; }
.alarm-sim-item:active { transform: scale(0.97); background: #fff5f5; border-color: #ff6b6b; }
.alarm-sim-code { font-size: 28rpx; font-weight: 700; color: #e74c3c; font-family: 'Courier New', monospace; min-width: 80rpx; }
.alarm-sim-desc { flex: 1; font-size: 26rpx; color: #2c3e50; }
.alarm-sim-arrow { font-size: 32rpx; color: #b0bec5; }

/* 日志列表 */
.log-list { background: #ffffff; border-radius: 24rpx; overflow: hidden; border: 1rpx solid #e8edf5; max-height: 600rpx; overflow-y: auto; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04); }
.log-item { display: flex; gap: 16rpx; padding: 16rpx 24rpx; border-bottom: 1rpx solid #f0f4fa; align-items: flex-start; }
.log-item:last-child { border-bottom: none; }
.log-item.system { border-left: 4rpx solid #3498db; }
.log-item.send { border-left: 4rpx solid #3498db; }
.log-item.receive { border-left: 4rpx solid #2ecc71; }
.log-item.error { border-left: 4rpx solid #ff6b6b; background: rgba(255,107,107,0.03); }
.log-item.success { border-left: 4rpx solid #2ecc71; }
.log-time { font-size: 20rpx; color: #b0bec5; font-family: 'Courier New', monospace; white-space: nowrap; padding-top: 2rpx; }
.log-content { font-size: 24rpx; color: #7f8c9b; flex: 1; word-break: break-all; }
.log-item.error .log-content { color: #ff6b6b; }
.log-item.send .log-content { color: #3498db; }
.log-item.receive .log-content { color: #2ecc71; }
.log-item.success .log-content { color: #2ecc71; }

/* 报警列表 */
.alarm-list { background: #ffffff; border-radius: 24rpx; overflow: hidden; border: 1rpx solid #ff6b6b; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04); }
.alarm-item { display: flex; gap: 16rpx; padding: 24rpx 32rpx; border-bottom: 1rpx solid #f0f4fa; background: rgba(255,107,107,0.03); }
.alarm-item:last-child { border-bottom: none; }
.alarm-icon { font-size: 36rpx; }
.alarm-content { flex: 1; }
.alarm-title { font-size: 26rpx; color: #ff6b6b; font-weight: 600; display: block; }
.alarm-desc { font-size: 22rpx; color: #7f8c9b; margin-top: 4rpx; display: block; }
.alarm-time { font-size: 20rpx; color: #b0bec5; margin-top: 8rpx; display: block; }
</style>
