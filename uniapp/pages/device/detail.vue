<template>
	<view class="page">
		<!-- 顶部导航 -->
		<view class="header">
			<view class="header-left" @click="goBack">
				<text class="back-icon">←</text>
			</view>
			<text class="header-title">{{ deviceName }}</text>
			<view class="header-right" @click="toggleMenu">
				<text class="more-icon">···</text>
			</view>
		</view>

		<!-- 更多菜单 -->
		<view v-if="menuOpen" class="menu-overlay" @click="menuOpen = false"></view>
		<view v-if="menuOpen" class="menu-dropdown">
			<view class="menu-item" @click="onRename">
				<text class="menu-item-icon">✏️</text>
				<text class="menu-item-text">重命名设备</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @click="onDelete">
				<text class="menu-item-icon">🗑️</text>
				<text class="menu-item-text">删除设备</text>
			</view>
		</view>

		<!-- 空状态：未选中设备 -->
		<view v-if="!hasDevice" class="empty-state">
			<view class="empty-icon-wrap">
				<text class="empty-icon">📡</text>
			</view>
			<text class="empty-title">请先在首页选择设备</text>
			<text class="empty-desc">点击首页的设备卡片即可进入控制界面</text>
			<view class="empty-btn" @click="goToHome">
				<text class="empty-btn-text">去首页选择设备</text>
			</view>
		</view>

		<!-- 主内容 -->
		<scroll-view v-if="hasDevice" class="main" scroll-y :show-scrollbar="false">
			<!-- 开关机控制 -->
			<view class="section">
				<view class="section-header">
					<text class="section-title">开关机控制</text>
				</view>

				<view class="power-control">
					<view class="power-btn power-on" :class="{ disabled: !online || isPoweredOn }" @click="powerOn">
						<text class="power-btn-text">开机</text>
					</view>
					<view class="power-btn power-off" :class="{ disabled: !online || !isPoweredOn }" @click="powerOff">
						<text class="power-btn-text">关机</text>
					</view>
				</view>


			</view>

			<!-- 火候控制 -->
			<view class="section">
				<view class="section-header">
					<text class="section-title">🔥 火候控制</text>
				</view>
				<view class="heat-control">
					<view class="heat-row">
						<view class="heat-btn" :class="{ disabled: !online || !isPoweredOn }" @click="decreaseHeat">
							<text class="heat-btn-text">−</text>
						</view>
						<view class="heat-display">
							<text class="heat-level" :class="getHeatClass()">P{{ heatLevel }}</text>
							<text class="heat-status">{{ heatStatusText }}</text>
						</view>
						<view class="heat-btn" :class="{ disabled: !online || !isPoweredOn }" @click="increaseHeat">
							<text class="heat-btn-text">+</text>
						</view>
					</view>
					<view class="heat-bar">
						<view v-for="i in 12" :key="i" class="heat-seg" :class="getHeatSegClass(i)"></view>
					</view>
					<view class="heat-quick">
						<text class="quick-label">快速火候：</text>
						<view class="quick-btns">
							<view class="quick-btn" :class="{ disabled: !isPoweredOn, active: heatLevel === 3 }" @click="setHeat(3)">小火</view>
							<view class="quick-btn" :class="{ disabled: !isPoweredOn, active: heatLevel === 6 }" @click="setHeat(6)">中火</view>
							<view class="quick-btn" :class="{ disabled: !isPoweredOn, active: heatLevel === 9 }" @click="setHeat(9)">大火</view>
							<view class="quick-btn quick-btn-hot" :class="{ disabled: !isPoweredOn, active: heatLevel === 12 }" @click="setHeat(12)">🔥爆炒</view>
						</view>
					</view>
				</view>
			</view>


			<!-- 定时任务 -->
			<view class="section">
				<view class="section-header">
					<text class="section-title">⏰ 定时任务</text>
				</view>
				<view class="timer-control">
					<view v-if="!timerRunning && !timerPaused" class="timer-empty">
						<text class="timer-empty-text">暂无定时任务</text>
					</view>
					<view v-else class="timer-display">
						<text class="timer-icon">⏰</text>
						<text class="timer-time">{{ timerDisplay }}</text>
						<text v-if="timerPaused" class="timer-paused">(已暂停)</text>
					</view>
					<view class="timer-actions">
						<template v-if="timerRunning || timerPaused">
							<view class="timer-btn" @click="toggleTimer">
								<text>{{ timerPaused ? '▶ 继续' : '⏸ 暂停' }}</text>
							</view>
							<view class="timer-btn timer-btn-cancel" @click="cancelTimer">
								<text>✕ 取消</text>
							</view>
						</template>
						<view class="timer-btn timer-btn-add" @click="addTimer">
							<text>+ 添加定时任务</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 异常警报 -->
			<view class="section">
				<view class="section-header">
					<text class="section-title">⚠️ 异常警报</text>
				</view>
				<view class="alarm-control">
					<view v-if="alarms.length === 0" class="alarm-empty">
						<text class="alarm-empty-text">暂无异常警报</text>
					</view>
					<view v-for="(alarm, idx) in alarms" :key="idx" class="alarm-card">
						<view class="alarm-card-header">
							<text class="alarm-icon">🔴</text>
							<text class="alarm-title">{{ alarm.title }}</text>
						</view>
						<text class="alarm-desc">{{ alarm.desc }}</text>
						<view class="alarm-confirm" @click="shutdownAlarm(idx)">
							<text>关机</text>
						</view>

					</view>

					<view class="alarm-simulate" @click="simulateAlarm">
						<text>📡 模拟警报</text>
					</view>
				</view>
			</view>

			<!-- 指令日志 -->
			<view class="section">
				<view class="section-header">
					<text class="section-title">📋 指令日志</text>
				</view>
				<view class="log-control">
					<view v-if="logs.length === 0" class="log-empty">
						<text class="log-empty-text">暂无操作记录</text>
					</view>
					<view v-for="(log, idx) in logs" :key="idx" class="log-item">
						<text class="log-time">{{ log.time }}</text>
						<text class="log-msg">{{ log.msg }}</text>
					</view>
				</view>
			</view>

			<view style="height: 40rpx;"></view>
		</scroll-view>

		<!-- 自定义底部导航栏 -->
		<view class="custom-tabbar">
			<view class="tabbar-item" @click="switchTab(0)">
				<text class="tabbar-text">首页</text>
			</view>
			<view class="tabbar-item tabbar-item-active" @click="switchTab(1)">
				<text class="tabbar-text tabbar-text-active">控制</text>
				<view class="tabbar-indicator"></view>
			</view>
		</view>

	</view>
</template>



<script>
import { bleManager, CMD, GEAR_NAMES, ALARM_DESCS, ZONE_DESCS, INNER_SEG_DESCS, OUTER_SEG_DESCS } from '@/utils/ble.js'

export default {
	data() {
		return {
			deviceName: '智能动热灶',
			deviceId: '',
			online: true,
			heatLevel: 0,
			menuOpen: false,

			// 定时
			timerRunning: false,
			timerPaused: false,
			timerSeconds: 0,
			timerTotal: 0,
			timerInterval: null,

			// 警报
			alarms: [],
			alarmVibrateInterval: null,

			// 日志
			logs: [],


			// 长按
			longPressTimer: null,
			longPressActive: false,
			longPressDir: null,
			longPressInterval: null,

			// 分区控制
			zoneMode: 'all', // 'inner' | 'outer' | 'all'
			innerSegment: 0, // 0=关闭, 1-5=段位
			outerSegment: 0, // 0=关闭, 1-5=段位
		}
	},
	computed: {
		hasDevice() {
			return !!this.deviceId
		},
		isTestDevice() {
			return this.deviceId && this.deviceId.startsWith('TEST:')
		},

		timerDisplay() {
			const m = Math.floor(this.timerSeconds / 60)
			const s = this.timerSeconds % 60
			return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
		},
		heatStatusText() {
			if (!this.online) return '离线'
			if (this.heatLevel === 0) return '已停火'
			return '运行中'
		},
		isPoweredOn() {
			return this.heatLevel > 0
		}

	},
	onShow() {
		// 每次显示页面时读取选中的设备ID
		const rawDeviceId = uni.getStorageSync('selectedDeviceId')
		if (rawDeviceId) {
			this.deviceId = decodeURIComponent(rawDeviceId)
			this.deviceName = this.deviceId

			this.addLog('进入控制页面')
			this.addLog('设备已连接')
			// 初始化蓝牙消息监听
			this._initBleListener()
		} else {
			this.deviceId = ''
			this.deviceName = '智能动热灶'
		}
		// 监听来自首页的模拟警报事件
		uni.$on('deviceAlarm', this._onExternalAlarm)
		// 检查是否有待处理的警报（从首页跳转过来时）
		const pendingAlarm = uni.getStorageSync('pendingAlarm')
		if (pendingAlarm) {
			uni.removeStorageSync('pendingAlarm')
			this._onExternalAlarm(pendingAlarm)
		}
	},

	onHide() {
		// 取消监听外部警报事件
		uni.$off('deviceAlarm', this._onExternalAlarm)
	},

	onUnload() {

		this.clearTimer()
		this.clearLongPress()
		this.clearAlarmVibrate()
	},

	methods: {
		// ===== 蓝牙消息监听 =====
		_initBleListener() {
			bleManager.onMessage((data) => {
				console.log('设备返回:', data)
				// 处理设备应答 >OK
				if (bleManager.isAckOk(data)) {
					this.addLog('✅ 指令执行成功')
					return
				}
				// 处理异常上报
				if (bleManager.isAlarm(data)) {
					const desc = ALARM_DESCS[data] || '未知异常'
					this.alarms.unshift({
						title: desc,
						desc: `设备上报异常: ${data} - ${desc}`
					})
					this.addLog(`⚠️ ${desc}`)
					// 触发全局事件，通知首页自动跳转到此设备
					uni.$emit('deviceAlarm', { deviceId: this.deviceId })
					// 启动持续震动
					this.startAlarmVibrate()
					return
				}

				// 处理查询数据上报（温度/电参数）
				if (bleManager.isQueryResponse(data)) {
					// 尝试解析温度
					const temp = bleManager.parseTemperatureData(data)
					if (temp) {
						this.addLog(`🌡️ 温度: 1路=${temp.channel1} 2路=${temp.channel2} 3路=${temp.channel3}`)
						return
					}
					// 尝试解析电参数
					const power = bleManager.parsePowerData(data)
					if (power) {
						this.addLog(`⚡ 电压=${power.voltage}V 功率=${power.power}W 电流=${power.current}A`)
						return
					}
				}
			})
		},

		// ===== 导航 =====
		goBack() {
			uni.navigateTo({
				url: '/pages/index/index'
			})
		},
		goToHome() {
			uni.navigateTo({
				url: '/pages/index/index'
			})
		},
		switchTab(ti) {
			if (ti === 0) {
				uni.navigateTo({ url: '/pages/index/index' })
			}
			// ti === 1 是当前页面，不做操作
		},


		toggleMenu() {
			this.menuOpen = !this.menuOpen
		},

		// ===== 更多菜单 =====
		onRename() {
			this.menuOpen = false
			uni.showModal({
				title: '重命名设备',
				content: this.deviceName,
				editable: true,
				placeholderText: '输入新名称...',
				success: (r) => {
					if (r.confirm && r.content) {
						this.deviceName = r.content
						uni.showToast({ title: '已重命名', icon: 'success' })
						this.addLog(`重命名为"${r.content}"`)
					}
				}
			})
		},
		onDelete() {
			this.menuOpen = false
			uni.showModal({
				title: '删除设备',
				content: '确定删除该设备？',
				success: (r) => {
					if (r.confirm) {
						uni.removeStorageSync('selectedDeviceId')
						this.deviceId = ''
						this.deviceName = '智能动热灶'
						this.heatLevel = 0
						this.logs = []
						this.alarms = []
						this.clearTimer()
						uni.showToast({ title: '已删除设备', icon: 'success' })
					}
				}
			})
		},

		// ===== 火候控制 =====
		getHeatClass() {
			if (!this.online || this.heatLevel === 0) return 'heat-level-off'
			return 'heat-level-on'
		},
		getHeatSegClass(i) {
			if (!this.online || this.heatLevel === 0) return 'heat-seg-off'
			if (i > this.heatLevel) return 'heat-seg-off'
			if (this.heatLevel <= 4) return 'heat-seg-blue'
			if (this.heatLevel <= 8) return 'heat-seg-orange'
			return 'heat-seg-red'
		},
		/**
		 * 发送档位指令到机芯
		 * 下发 >AF1~>AFC，机芯返回 >OK 代表执行成功
		 */
		_sendGearCommand(level) {
			if (!this.online) {
				uni.showToast({ title: '设备离线，无法操作', icon: 'none' })
				return Promise.reject(new Error('设备离线'))
			}
			if (level < 0 || level > 12) return Promise.reject(new Error('无效档位'))
			
			if (level === 0) {
				// P0 = 关机
				return bleManager.powerOff().catch(err => {
					console.error('关机指令失败', err)
					if (!this.isTestDevice) uni.showToast({ title: '指令发送失败', icon: 'none' })
				})
			}
			return bleManager.setGear(level).catch(err => {
				console.error('档位指令失败', err)
				if (!this.isTestDevice) uni.showToast({ title: '指令发送失败', icon: 'none' })
			})
		},

		setHeat(level) {
			if (!this.online) {
				uni.showToast({ title: '设备离线，无法操作', icon: 'none' })
				return
			}
			this.heatLevel = level
			this._sendGearCommand(level)
			const names = { 3: '小火', 6: '中火', 9: '大火', 12: '爆炒' }
			const name = names[level] || `P${level}`
			const cmd = level === 0 ? '>AFF(关机)' : `>AF${level > 9 ? String.fromCharCode(55 + level) : level}(档位${level})`
			this.addLog(`快捷火候：${name} [${cmd}]`)
		},
		increaseHeat() {
			if (!this.online) {
				uni.showToast({ title: '设备离线，无法操作', icon: 'none' })
				return
			}
			if (this.heatLevel < 12) {
				this.heatLevel++
				this._sendGearCommand(this.heatLevel)
				const cmd = `>AF${this.heatLevel > 9 ? String.fromCharCode(55 + this.heatLevel) : this.heatLevel}`
				this.addLog(`设置火候 P${this.heatLevel} [${cmd}]`)
			}
		},
		decreaseHeat() {
			if (!this.online) {
				uni.showToast({ title: '设备离线，无法操作', icon: 'none' })
				return
			}
			if (this.heatLevel > 0) {
				this.heatLevel--
				this._sendGearCommand(this.heatLevel)
				if (this.heatLevel === 0) {
					this.addLog(`停火 [>AFF]`)
				} else {
					const cmd = `>AF${this.heatLevel > 9 ? String.fromCharCode(55 + this.heatLevel) : this.heatLevel}`
					this.addLog(`设置火候 P${this.heatLevel} [${cmd}]`)
				}
			}
		},

		// 长按连续加减
		onPressDown(dir) {
			this.clearLongPress()
			this.longPressTimer = setTimeout(() => {
				this.longPressActive = true
				this.longPressDir = dir
				this.longPressInterval = setInterval(() => {
					if (dir === 'down') this.decreaseHeat()
					else this.increaseHeat()
				}, 200)
			}, 500)
		},
		onPressUp() {
			this.clearLongPress()
		},
		clearLongPress() {
			if (this.longPressTimer) {
				clearTimeout(this.longPressTimer)
				this.longPressTimer = null
			}
			if (this.longPressInterval) {
				clearInterval(this.longPressInterval)
				this.longPressInterval = null
			}
			this.longPressActive = false
			this.longPressDir = null
		},

		// ===== 开关机控制 =====
		powerOn() {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			if (this.isPoweredOn) {
				uni.showToast({ title: '设备已开机', icon: 'none' })
				return
			}
			bleManager.powerOn().catch(err => {
				console.error('开机失败', err)
				if (!this.isTestDevice) uni.showToast({ title: '开机指令发送失败', icon: 'none' })
			})

			this.heatLevel = 1
			this.addLog(`开机 [>AFO]`)
		},

		powerOff() {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			bleManager.powerOff().catch(err => {
				console.error('关机失败', err)
				if (!this.isTestDevice) uni.showToast({ title: '关机指令发送失败', icon: 'none' })
			})

			this.heatLevel = 0
			this.addLog(`关机 [>AFF]`)
		},

		// ===== 查询指令 =====
		queryTemperature() {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			bleManager.queryTemperature().catch(err => {
				console.error('温度查询失败', err)
			})
			this.addLog(`查询温度 [>AT?]`)
		},
		queryPower() {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			bleManager.queryPower().catch(err => {
				console.error('电参数查询失败', err)
			})
			this.addLog(`查询电参数 [>AP?]`)
		},

		// ===== 分区控制 =====
		/**
		 * 获取分区模式对应的指令和描述
		 */
		_getZoneInfo(mode) {
			const map = {
				inner: { cmd: '>ACI', desc: '仅内区工作' },
				outer: { cmd: '>ACX', desc: '仅外区工作' },
				all: { cmd: '>ACL', desc: '内外全区同时工作' }
			}
			return map[mode] || { cmd: '', desc: mode }
		},
		setZoneMode(mode) {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			this.zoneMode = mode
			bleManager.setZone(mode).catch(err => {
				console.error('分区指令失败', err)
				if (!this.isTestDevice) uni.showToast({ title: '分区指令发送失败', icon: 'none' })
			})

			const info = this._getZoneInfo(mode)
			this.addLog(`分区控制：${info.desc} [${info.cmd}]`)
		},
		setInnerSegment(seg) {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			this.innerSegment = seg
			bleManager.setInnerSegment(seg).catch(err => {
				console.error('内区分段指令失败', err)
				if (!this.isTestDevice) uni.showToast({ title: '内区分段指令发送失败', icon: 'none' })
			})

			const desc = INNER_SEG_DESCS[seg] || `内区${seg}段`
			this.addLog(`内区分段：${desc} [>AA${seg}]`)
		},
		setOuterSegment(seg) {
			if (!this.online) {
				uni.showToast({ title: '设备离线', icon: 'none' })
				return
			}
			this.outerSegment = seg
			bleManager.setOuterSegment(seg).catch(err => {
				console.error('外区分段指令失败', err)
				if (!this.isTestDevice) uni.showToast({ title: '外区分段指令发送失败', icon: 'none' })
			})

			const desc = OUTER_SEG_DESCS[seg] || `外区${seg}段`
			this.addLog(`外区分段：${desc} [>AB${seg}]`)
		},
		// ===== 定时任务 =====
		addTimer() {
			const items = []
			for (let i = 1; i <= 60; i++) {
				items.push(`${i} 分钟`)
			}
			uni.showActionSheet({
				itemList: items,
				success: (res) => {
					const minutes = res.tapIndex + 1

					this.timerTotal = minutes * 60
					this.timerSeconds = this.timerTotal
					this.timerRunning = true
					this.timerPaused = false
					this.startTimer()
					uni.showToast({ title: `定时 ${minutes} 分钟`, icon: 'success' })
					this.addLog(`启动定时 ${String(minutes).padStart(2, '0')}:00`)
				}
			})
		},
		startTimer() {
			this.clearTimer()
			this.timerInterval = setInterval(() => {
				if (this.timerSeconds > 0) {
					this.timerSeconds--
				}
				if (this.timerSeconds <= 0) {
					this.clearTimer()
					this.timerRunning = false
					this.timerPaused = false
					// 定时结束自动关机
					bleManager.powerOff().catch(err => {
						console.error('定时关机指令失败', err)
					})
					this.heatLevel = 0
					uni.showToast({ title: '时间到！已自动关机', icon: 'none' })
					this.addLog('定时结束，自动关机 [>AFF]')
					uni.vibrateLong()
				}
			}, 1000)
		},

		toggleTimer() {
			if (this.timerPaused) {
				this.timerPaused = false
				this.startTimer()
			} else {
				this.timerPaused = true
				this.clearTimer()
			}
		},
		cancelTimer() {
			this.clearTimer()
			this.timerRunning = false
			this.timerPaused = false
			this.timerSeconds = 0
			this.addLog('取消定时')
			uni.showToast({ title: '已取消定时', icon: 'none' })
		},
		clearTimer() {
			if (this.timerInterval) {
				clearInterval(this.timerInterval)
				this.timerInterval = null
			}
		},

		// ===== 异常警报 =====
		/**
		 * 处理来自首页的外部警报事件
		 */
		_onExternalAlarm(data) {
			if (!data || !data.alarmCmd) return
			const alarmList = {
				'>AE1': { title: '机芯超温', desc: '机芯温度超过安全阈值，请检查散热' },
				'>AE2': { title: '线盘超温', desc: '线盘温度过高，请降低功率使用' },
				'>AE3': { title: '过流保护', desc: '电流超过额定值，设备已启动过流保护' },
				'>AE4': { title: '电流异常', desc: '检测到电流波形异常，请检查电源' },
				'>AE5': { title: '锅具异常', desc: '未检测到锅具或锅具不匹配' },
				'>AE6': { title: '线盘测温开路', desc: '线盘温度传感器开路，请检查传感器连接' },
			}
			const alarm = alarmList[data.alarmCmd]
			if (alarm) {
				this.alarms.unshift({
					title: alarm.title,
					desc: `设备上报异常: ${data.alarmCmd} - ${alarm.desc}`
				})
				this.addLog(`⚠️ ${alarm.title} [${data.alarmCmd}]`)
				// 启动持续震动
				this.startAlarmVibrate()
			}
		},
		startAlarmVibrate() {

			this.clearAlarmVibrate()
			// 立即震动一次
			uni.vibrateLong()
			// 每0.5秒持续震动
			this.alarmVibrateInterval = setInterval(() => {
				uni.vibrateLong()
			}, 500)
		},


		/**
		 * 停止持续震动
		 */
		clearAlarmVibrate() {
			if (this.alarmVibrateInterval) {
				clearInterval(this.alarmVibrateInterval)
				this.alarmVibrateInterval = null
			}
		},

		simulateAlarm() {
			const alarmList = [
				{ key: '>AE1', title: '机芯超温', desc: '机芯温度超过安全阈值，请检查散热' },
				{ key: '>AE2', title: '线盘超温', desc: '线盘温度过高，请降低功率使用' },
				{ key: '>AE3', title: '过流保护', desc: '电流超过额定值，设备已启动过流保护' },
				{ key: '>AE4', title: '电流异常', desc: '检测到电流波形异常，请检查电源' },
				{ key: '>AE5', title: '锅具异常', desc: '未检测到锅具或锅具不匹配' },
				{ key: '>AE6', title: '线盘测温开路', desc: '线盘温度传感器开路，请检查传感器连接' },
			]
			const itemList = alarmList.map(a => `${a.key} ${a.title}`)
			uni.showActionSheet({
				itemList: itemList,
				success: (res) => {
					const alarm = alarmList[res.tapIndex]
					this.alarms.unshift({
						title: alarm.title,
						desc: `设备上报异常: ${alarm.key} - ${alarm.desc}`
					})
					this.addLog(`⚠️ ${alarm.title} [${alarm.key}]`)
					// 启动持续震动，直到用户点击确认
					this.startAlarmVibrate()
				}
			})
		},

		/**
		 * 警报关机 - 发送关机指令并关闭警报
		 * 点击后发送 >AFF 关机指令，然后移除该警报
		 */
		shutdownAlarm(idx) {
			const alarm = this.alarms[idx]
			// 发送关机指令
			bleManager.powerOff().catch(err => {
				console.error('警报关机指令失败', err)
			})
			this.heatLevel = 0
			// 移除警报
			this.alarms.splice(idx, 1)
			this.addLog(`⏻ 已关机：${alarm.title} [>AFF]`)
			uni.showToast({ title: '已发送关机指令', icon: 'success' })
			// 如果没有更多警报，停止震动
			if (this.alarms.length === 0) {
				this.clearAlarmVibrate()
			}
		},



		// ===== 指令日志 =====
		addLog(msg) {
			const now = new Date()
			const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
			this.logs.unshift({ time, msg })
		}
	}
}
</script>


<style>
.page {
	width: 750rpx;
	min-height: 100vh;
	background-color: #f5f6fa;
	display: flex;
	flex-direction: column;
	position: relative;
	margin: 0 auto;
}

/* ===== 顶部导航 ===== */
.header {
	height: 88rpx;
	padding: 0 32rpx;
	padding-top: var(--status-bar-height, 44rpx);
	background-color: #fcf8ff;
	display: flex;
	align-items: center;
	justify-content: space-between;
	position: relative;
	z-index: 100;
	flex-shrink: 0;
}
.header-left, .header-right {
	width: 80rpx;
	height: 80rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}
.back-icon {
	font-size: 40rpx;
	color: #1a1a2e;
	font-weight: 700;
}
.more-icon {
	font-size: 36rpx;
	color: #1a1a2e;
	font-weight: 700;
	letter-spacing: 4rpx;
}
.header-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #0057bf;
}

/* ===== 更多菜单 ===== */
.menu-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	z-index: 50;
}
.menu-dropdown {
	position: absolute;
	top: 120rpx;
	right: 32rpx;
	background: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.12);
	width: 360rpx;
	overflow: hidden;
	z-index: 200;
}
.menu-item {
	padding: 28rpx 40rpx;
	display: flex;
	align-items: center;
	gap: 20rpx;
}
.menu-item:active {
	background-color: #f5f6fa;
}
.menu-item-icon {
	font-size: 32rpx;
	width: 48rpx;
	text-align: center;
}
.menu-item-text {
	font-size: 28rpx;
	color: #1a1a2e;
}
.menu-divider {
	height: 2rpx;
	background-color: #f5f6fa;
	margin: 0 20rpx;
}

/* ===== 空状态 ===== */
.empty-state {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 0 80rpx;
	padding-bottom: 200rpx;
}
.empty-icon-wrap {
	width: 160rpx;
	height: 160rpx;
	border-radius: 80rpx;
	background: #e8f4fd;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 32rpx;
}
.empty-icon {
	font-size: 64rpx;
}
.empty-title {
	font-size: 36rpx;
	font-weight: 700;
	color: #1a1a2e;
	margin-bottom: 16rpx;
}
.empty-desc {
	font-size: 28rpx;
	color: #414754;
	text-align: center;
	margin-bottom: 48rpx;
	line-height: 1.5;
}
.empty-btn {
	padding: 24rpx 64rpx;
	border-radius: 44rpx;
	background: #0057bf;
	display: flex;
	align-items: center;
	justify-content: center;
}
.empty-btn-text {
	font-size: 32rpx;
	font-weight: 600;
	color: #ffffff;
}

/* ===== 主内容 ===== */
.main {
	flex: 1;
	padding: 24rpx 0;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
	padding-bottom: 200rpx;
}

/* ===== 通用卡片 ===== */
.section {
	margin: 0 32rpx 24rpx;
	background: #ffffff;
	border-radius: 48rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 40rpx rgba(0, 0, 0, 0.06);
}
.section-header {
	margin-bottom: 32rpx;
}
.section-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #1a1a2e;
}

/* ===== 开关机控制 ===== */
.power-control {
	display: flex;
	gap: 24rpx;
	justify-content: center;
}
.power-btn {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12rpx;
	padding: 28rpx 0;
	border-radius: 32rpx;
	font-size: 32rpx;
	font-weight: 700;
}
.power-btn:active {
	opacity: 0.8;
}
.power-btn.disabled {
	opacity: 0.35;
}
.power-on {
	background: #e8f4fd;
	color: #0057bf;
	border: 2rpx solid #0057bf;
}
.power-off {
	background: #f5f6fa;
	color: #414754;
	border: 2rpx solid #414754;
}
.power-btn-icon {
	font-size: 28rpx;
}
.power-btn-text {
	font-size: 32rpx;
}

/* ===== 火候控制 ===== */
.heat-row {

	display: flex;
	align-items: center;
	justify-content: center;
	gap: 40rpx;
	margin-bottom: 24rpx;
}
.heat-btn {
	width: 80rpx;
	height: 80rpx;
	border-radius: 40rpx;
	background: #f5f6fa;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}
.heat-btn:active {
	background: #e8f4fd;
}
.heat-btn.disabled {
	opacity: 0.4;
}
.heat-btn-text {
	font-size: 48rpx;
	font-weight: 700;
	color: #0057bf;
	line-height: 1;
}
.heat-display {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8rpx;
}
.heat-level {
	font-size: 48rpx;
	font-weight: 700;
}
.heat-level-on {
	color: #0057bf;
}
.heat-level-off {
	color: #b0bec5;
}
.heat-status {
	font-size: 24rpx;
	color: #414754;
}
.heat-bar {
	display: flex;
	gap: 8rpx;
	margin-bottom: 32rpx;
	justify-content: center;
}
.heat-seg {
	width: 40rpx;
	height: 16rpx;
	border-radius: 8rpx;
}
.heat-seg-off {
	background: #f5f6fa;
}
.heat-seg-blue {
	background: #2b7fff;
}
.heat-seg-orange {
	background: #f39c12;
}
.heat-seg-red {
	background: #ff4d4f;
}
.heat-quick {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}
.quick-label {
	font-size: 26rpx;
	color: #414754;
}
.quick-btns {
	display: flex;
	gap: 16rpx;
}
.quick-btn {
	flex: 1;
	padding: 20rpx 0;
	border-radius: 24rpx;
	background: #f5f6fa;
	text-align: center;
	font-size: 26rpx;
	color: #1a1a2e;
}
.quick-btn:active {
	background: #e8f4fd;
}
.quick-btn.active {
	background: #0057bf;
	color: #ffffff;
}
.quick-btn-hot {
	background: #fff1f0;
	color: #ff4d4f;
}
.quick-btn-hot.active {
	background: #ff4d4f;
	color: #ffffff;
}

/* ===== 定时任务 ===== */
.timer-control {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 24rpx;
}
.timer-empty {
	padding: 32rpx 0;
}
.timer-empty-text {
	font-size: 28rpx;
	color: #b0bec5;
}
.timer-display {
	display: flex;
	align-items: center;
	gap: 16rpx;
}
.timer-icon {
	font-size: 40rpx;
}
.timer-time {
	font-size: 56rpx;
	font-weight: 700;
	color: #1a1a2e;
	font-family: 'Courier New', monospace;
}
.timer-paused {
	font-size: 24rpx;
	color: #f39c12;
}
.timer-actions {
	display: flex;
	gap: 16rpx;
	flex-wrap: wrap;
	justify-content: center;
}
.timer-btn {
	padding: 16rpx 32rpx;
	border-radius: 24rpx;
	background: #f5f6fa;
	font-size: 26rpx;
	color: #1a1a2e;
}
.timer-btn:active {
	background: #e8f4fd;
}
.timer-btn-cancel {
	color: #ff4d4f;
}
.timer-btn-add {
	background: #e8f4fd;
	color: #0057bf;
}

/* ===== 异常警报 ===== */
.alarm-control {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}
.alarm-empty {
	padding: 32rpx 0;
	text-align: center;
}
.alarm-empty-text {
	font-size: 28rpx;
	color: #b0bec5;
}
.alarm-card {
	background: #fff1f0;
	border: 2rpx solid #ff4d4f;
	border-radius: 24rpx;
	padding: 24rpx;
}
.alarm-card-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 12rpx;
}
.alarm-icon {
	font-size: 24rpx;
}
.alarm-title {
	font-size: 28rpx;
	font-weight: 700;
	color: #ff4d4f;
}
.alarm-desc {
	font-size: 26rpx;
	color: #414754;
	display: block;
	margin-bottom: 16rpx;
}
.alarm-confirm {
	display: inline-block;
	padding: 12rpx 32rpx;
	border-radius: 20rpx;
	background: #ff4d4f;
	font-size: 24rpx;
	color: #ffffff;
	text-align: center;
}
.alarm-confirm:active {
	opacity: 0.8;
}
.alarm-simulate {
	padding: 20rpx 0;
	text-align: center;
	font-size: 26rpx;
	color: #0057bf;
	background: #f5f6fa;
	border-radius: 24rpx;
}
.alarm-simulate:active {
	background: #e8f4fd;
}

/* ===== 指令日志 ===== */
.log-control {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}
.log-empty {
	padding: 32rpx 0;
	text-align: center;
}
.log-empty-text {
	font-size: 28rpx;
	color: #b0bec5;
}
.log-item {
	display: flex;
	gap: 16rpx;
	line-height: 48rpx;
}
.log-time {
	font-size: 24rpx;
	color: #b0bec5;
	font-family: 'Courier New', monospace;
	flex-shrink: 0;
}
.log-msg {
	font-size: 26rpx;
	color: #414754;
}

/* ===== 自定义底部导航栏 ===== */
.custom-tabbar { position: fixed; bottom: 0; left: 0; right: 0; height: 100rpx; background: #fcf8ff; display: flex; align-items: center; justify-content: space-around; border-top: 1px solid #e8e8e8; z-index: 100; padding-bottom: var(--safe-area-inset-bottom, 0); }
.tabbar-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: relative; }
.tabbar-text { font-size: 28rpx; color: #414754; font-weight: 500; }
.tabbar-text-active { font-size: 32rpx; color: #0057bf; font-weight: 700; }
.tabbar-indicator { position: absolute; bottom: 0; width: 40rpx; height: 6rpx; border-radius: 3rpx; background: #0057bf; }
.tabbar-item-active .tabbar-text { font-size: 32rpx; color: #0057bf; font-weight: 700; }

</style>



