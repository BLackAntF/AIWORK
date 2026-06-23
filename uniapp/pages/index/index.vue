<template>
	<view class="page">
		<!-- 顶部导航栏 -->
		<view class="header">
			<text class="header-title">首页</text>
			<view class="header-btn" @click="toggleMenu">
				<view class="header-btn-icon">
					<text class="plus-icon">+</text>
				</view>
			</view>
		</view>

		<!-- 下拉菜单 -->
		<view class="menu-overlay" v-if="menuOpen" @click="menuOpen = false">
		</view>
		<view class="menu-dropdown" v-if="menuOpen" @click.stop="() => {}">
			<view class="menu-item" @click="onCreateGroup">
				<text class="menu-item-icon">📁</text>
				<text class="menu-item-text">创建设备组</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @click="onAddDevice">
				<text class="menu-item-icon">📡</text>
				<text class="menu-item-text">添加设备</text>
			</view>
			<view class="menu-divider"></view>
			<view class="menu-item" @click="onDeleteGroup">
				<text class="menu-item-icon">🗑️</text>
				<text class="menu-item-text">删除设备组</text>
			</view>
		</view>

		<!-- 空状态：无设备组 -->
		<view class="empty-state" v-if="!hasGroups">
			<view class="empty-icon-wrap">
				<text class="empty-icon">🔥</text>
			</view>
			<text class="empty-title">还没有添加设备</text>
			<text class="empty-desc">点击右上角 [+] 添加您的第一台设备或创建设备组</text>
			<view class="empty-actions">
				<view class="empty-btn primary" @click="onCreateGroup">
					<text class="empty-btn-text">创建设备组</text>
				</view>
				<view class="empty-btn" @click="onAddDevice">
					<text class="empty-btn-text">添加设备</text>
				</view>
			</view>
		</view>

		<!-- 主内容区 -->
		<scroll-view class="main" scroll-y :show-scrollbar="false" v-else>
			<view
				class="section"
				v-for="(group, gi) in deviceGroups"
				:key="gi"
				:class="{ 'drag-over': dragOverGroup === gi }"
			>
				<!-- 分组头部 -->
				<view class="section-header" @click="toggleGroup(gi)">
					<view class="section-header-left">
						<text class="section-title" @click.stop="onEditGroupName(gi)">{{ group.name }}</text>
						<view class="section-tag">
							<text class="section-tag-text">{{ group.devices.length }}个设备</text>
						</view>
						<view class="group-more-btn" @click.stop="onGroupMore(gi)">
							<text class="group-more-icon">⋮</text>
						</view>
					</view>
					<view class="section-header-right">
						<template v-if="gi !== (deviceGroups.length - 1) && group.expanded && group.devices.length > 0">
							<view class="batch-btn" @click.stop="batchPowerOn(group)">
								<view class="batch-btn-icon">
									<text class="batch-icon-play">▶</text>
								</view>
								<text class="batch-btn-text">全部开机</text>
							</view>
							<view class="batch-btn batch-off" @click.stop="batchPowerOff(group)">
								<view class="batch-btn-icon batch-off-icon">
									<text class="batch-icon-stop">■</text>
								</view>
								<text class="batch-btn-text batch-off-text">全部关机</text>
							</view>
						</template>
						<view class="section-arrow" :class="{ expanded: group.expanded }">
							<text class="arrow-icon">▶</text>
						</view>
					</view>
				</view>

				<!-- 分组设备列表 -->
				<view class="section-body" v-if="group.expanded">
					<view class="device-grid">
						<view
							class="device-card"
							v-for="(device, di) in group.devices"
							:key="di"
							:class="{ offline: device.offline, dragging: dragDevice === device }"
							:style="getDragStyle(device)"
							@click="onDeviceClick(device)"
							@touchstart="onDeviceTouchStart($event, device, group, gi, di)"
							@touchmove="onDeviceTouchMove($event)"
							@touchend="onDeviceTouchEnd"
						>
							<view class="card-icon-wrap">
								<view class="card-icon-bg" :class="{ 'icon-offline': device.offline }">
									<text class="card-icon">{{ device.icon || '🔥' }}</text>
								</view>
								<view class="card-more-icon">
									<text>⋯</text>
								</view>
							</view>
							<text class="card-name" @click.stop="onEditDeviceName(device)">{{ device.name }}</text>
							<text class="card-status" :class="{ 'status-online': !device.offline && device.power > 0, 'status-stopped': device.power === 0 && !device.offline, 'status-offline': device.offline }">
								{{ device.offline ? '离线' : 'P' + device.power + ' · ' + device.statusText }}
							</text>
							<view class="heat-bar">
								<view v-for="i in 12" :key="i" class="heat-seg" :class="getHeatSegClass(i, device)">
								</view>
							</view>
							<view class="card-close" @click.stop="removeDevice(group, di)">
								<text class="close-icon">✕</text>
							</view>
						</view>
					</view>
					<view class="empty-group" v-if="group.devices.length === 0">
						<text class="empty-text">此组暂无设备，请添加设备</text>
						<view class="empty-group-btn" @click="onAddDevice">
							<text class="empty-group-btn-text">+ 添加设备</text>
						</view>
					</view>
				</view>
			</view>
			<!-- 测试预警按钮 -->
			<view class="section test-alarm-section" @click="showTestAlarm">
				<view class="section-header">
					<text class="section-title">🚨 测试预警</text>
				</view>
				<view class="test-alarm-body">
					<text class="test-alarm-desc">选择一个设备模拟异常上报，用于测试预警功能</text>
					<view class="test-alarm-btn">
						<text class="test-alarm-btn-text">📡 模拟设备异常</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 拖拽浮动层 -->
		<view class="drag-float" v-if="dragDevice && isDragging" :style="dragFloatStyle">
			<view class="drag-float-card">
				<view class="drag-float-icon">{{ dragDevice.icon || '🔥' }}</view>
				<text class="drag-float-name">{{ dragDevice.name }}</text>
			</view>
		</view>

		<!-- 添加设备弹窗 -->
		<view class="modal-overlay" v-if="showAddDevice" @click="closeAddDevice">
		</view>
		<view class="modal" v-if="showAddDevice">
			<view class="modal-header">
				<text class="modal-title">添加设备</text>
				<view class="modal-close" @click="closeAddDevice">
					<text class="modal-close-icon">✕</text>
				</view>
			</view>

			<view class="ble-search" v-if="bleScanning">
				<view class="ble-animation">
					<view class="ble-pulse"></view>
					<view class="ble-pulse delay"></view>
					<view class="ble-pulse delay2"></view>
					<text class="ble-icon">📡</text>
				</view>
				<text class="ble-search-text">正在搜索蓝牙设备...</text>
				<text class="ble-search-hint">请确保设备已开机并靠近手机</text>
				<view class="ble-stop-btn" @click="stopBleScan">
					<text class="ble-stop-text">停止搜索</text>
				</view>
			</view>

			<view class="ble-results" v-if="!bleScanning && bleDevices.length > 0">
				<text class="ble-result-title">发现 {{ bleDevices.length }} 个设备</text>
				<view class="ble-device-list">
					<view class="ble-device-item" v-for="(dev, di) in bleDevices" :key="di" @click="selectBleDevice(dev)">
						<view class="ble-device-info">
							<text class="ble-device-name">{{ dev.name }}</text>
							<text class="ble-device-mac">{{ dev.mac }}</text>
						</view>
						<view class="ble-device-rssi">
							<text class="ble-rssi-icon" :class="getRssiClass(dev.rssi)">📶</text>
						</view>
					</view>
				</view>
				<view class="ble-rescan-btn" @click="startBleScan">
					<text class="ble-rescan-text">重新搜索</text>
				</view>
			</view>

			<view class="ble-no-devices" v-if="!bleScanning && bleDevices.length === 0 && bleSearched">
				<text class="ble-no-icon">🔍</text>
				<text class="ble-no-text">未发现蓝牙设备</text>
				<text class="ble-no-hint">请检查设备是否开机，或使用测试设备</text>
				<view class="ble-rescan-btn" @click="startBleScan">
					<text class="ble-rescan-text">重新搜索</text>
				</view>
			</view>

			<view class="modal-footer" v-if="!bleScanning">
				<view class="modal-btn primary" @click="startBleScan">
					<text class="modal-btn-text">📡 手动搜索</text>
				</view>
				<view class="modal-btn" @click="addTestDevice">
					<text class="modal-btn-text">添加测试设备</text>
				</view>
			</view>
		</view>

		<!-- 自定义底部导航栏 -->
		<view class="custom-tabbar">
			<view class="tabbar-item tabbar-item-active" @click="switchTab(0)">
				<text class="tabbar-text tabbar-text-active">首页</text>
				<view class="tabbar-indicator"></view>
			</view>
			<view class="tabbar-item" @click="switchTab(1)">
				<text class="tabbar-text">控制</text>
			</view>
		</view>

	</view>
</template>

<script>
	export default {
		data() {
			return {
				menuOpen: false,
				activeTab: 0,
				tabs: [
					{ icon: '🏠', label: '首页' },
					{ icon: '🔥', label: '控制' }
				],
				deviceGroups: [
					{
						name: '未分组设备',
						expanded: false,
						devices: []
					}
				],
				showAddDevice: false,
				bleScanning: false,
				bleSearched: false,
				bleDevices: [],
				testDeviceCounter: 0,
				dragDevice: null,
				dragSourceGroup: null,
				dragSourceIndex: -1,
				dragOverGroup: -1,
				dragStartX: 0,
				dragStartY: 0,
				dragCurrentX: 0,
				dragCurrentY: 0,
				isDragging: false,
				dragOffsetX: 0,
				dragOffsetY: 0,
				dragReady: false,
				dragTimer: null,
				sectionRects: [],
				dragMoveRAF: null
			}
		},
		computed: {
			hasGroups() {
				return this.deviceGroups.length > 1 || this.deviceGroups[0].devices.length > 0
			},
			dragFloatStyle() {
				if (!this.dragDevice || !this.isDragging) return {}
				const x = this.dragCurrentX - this.dragOffsetX
				const y = this.dragCurrentY - this.dragOffsetY
				return {
					position: 'fixed',
					left: '0px',
					top: '0px',
					transform: 'translate3d(' + x + 'px, ' + y + 'px, 0)',
					WebkitTransform: 'translate3d(' + x + 'px, ' + y + 'px, 0)',
					zIndex: 9999,
					pointerEvents: 'none',
					willChange: 'transform'
				}
			}
		},
		onShow() {
			uni.$on('deviceAlarm', this._onDeviceAlarm)
		},
		onHide() {
			uni.$off('deviceAlarm', this._onDeviceAlarm)
		},
		methods: {
			_onDeviceAlarm(data) {
				if (!data || !data.deviceId) return
				for (const group of this.deviceGroups) {
					for (const device of group.devices) {
						const deviceId = device.mac || device.name
						if (deviceId === data.deviceId) {
							uni.setStorageSync('selectedDeviceId', encodeURIComponent(deviceId))
							uni.navigateTo({ url: '/pages/device/detail' })

							return
						}
					}
				}
			},
			getHeatSegClass(i, device) {
				if (device.offline) return 'seg-offline'
				if (i <= device.power) {
					if (i <= 4) return 'seg-blue'
					if (i <= 8) return 'seg-orange'
					return 'seg-red'
				}
				return 'seg-inactive'
			},
			toggleMenu() { this.menuOpen = !this.menuOpen },
			onCreateGroup() {
				this.menuOpen = false
				uni.showModal({
					title: '创建设备组',
					editable: true,
					placeholderText: '输入组名称...',
					success: (res) => {
						if (res.confirm && res.content) {
							this.deviceGroups.splice(this.deviceGroups.length - 1, 0, {
								name: res.content, expanded: false, devices: []
							})
							uni.showToast({ title: '创建成功', icon: 'success' })
						} else if (res.confirm && !res.content) {
							uni.showToast({ title: '请输入组名称', icon: 'none' })
						}
					}
				})
			},
			onAddDevice() {
				this.menuOpen = false
				this.showAddDevice = true
				this.bleScanning = false
				this.bleSearched = false
				this.bleDevices = []
			},
			closeAddDevice() { this.showAddDevice = false; this.bleScanning = false },
			startBleScan() {
				this.bleScanning = true; this.bleSearched = false; this.bleDevices = []
				uni.openBluetoothAdapter({
					success: () => {
						uni.startBluetoothDevicesDiscovery({
							allowDuplicatesKey: false,
							success: () => {
								uni.onBluetoothDeviceFound((res) => {
									res.devices.forEach(device => {
										if (device.RSSI < -100) return
										const name = device.localName || device.name || '未知设备'
										const mac = device.deviceId
										if (!this.bleDevices.some(d => d.mac === mac)) {
											this.bleDevices.push({ name, mac, rssi: device.RSSI || 0 })
										}
									})
								})
								setTimeout(() => this.stopBleScan(), 5000)
							},
							fail: (err) => {
								this.bleScanning = false; this.bleSearched = true
								uni.showToast({ title: '蓝牙搜索失败: ' + err.errMsg, icon: 'none' })
							}
						})
					},
					fail: () => {
						this.bleScanning = false; this.bleSearched = true
						uni.showToast({ title: '请开启手机蓝牙', icon: 'none' })
					}
				})
			},
			stopBleScan() {
				uni.stopBluetoothDevicesDiscovery({})
				this.bleScanning = false; this.bleSearched = true
			},

			selectBleDevice(dev) {
				const newDevice = { name: dev.name, icon: '🔥', power: 0, statusText: '待机', offline: false, showClose: false, mac: dev.mac, deviceType: 'cooker' }
				this.deviceGroups[this.deviceGroups.length - 1].devices.push(newDevice)
				this.closeAddDevice()
				uni.showToast({ title: `已添加 ${dev.name}`, icon: 'success' })
			},
			getRssiClass(rssi) {
				if (rssi >= -50) return 'rssi-strong'
				if (rssi >= -70) return 'rssi-medium'
				return 'rssi-weak'
			},
			addTestDevice() {
				this.testDeviceCounter++
				const testDevices = [
					{ name: '测试灶具-A', icon: '🔥', type: 'cooker' },
					{ name: '测试灶具-B', icon: '🔥', type: 'cooker' },
					{ name: '测试烤炉-A', icon: '🍖', type: 'grill' },
					{ name: '测试烤炉-B', icon: '🍖', type: 'grill' }
				]
				const dev = testDevices[this.testDeviceCounter % testDevices.length]
				const newDevice = {
					name: dev.name + '-' + Math.ceil(this.testDeviceCounter / testDevices.length),
					icon: dev.icon, power: 0, statusText: '待机', offline: false, showClose: false,
					mac: 'TEST:00:00:00:' + String(this.testDeviceCounter).padStart(2, '0'),
					deviceType: dev.type, isTest: true
				}
				this.deviceGroups[this.deviceGroups.length - 1].devices.push(newDevice)
				uni.showToast({ title: `已添加测试设备 ${newDevice.name}`, icon: 'success' })
			},
			onDeleteGroup() {
				this.menuOpen = false
				const deletableGroups = this.deviceGroups.slice(0, -1)
				if (deletableGroups.length === 0) {
					uni.showToast({ title: '没有可删除的设备组', icon: 'none' })
					return
				}
				uni.showActionSheet({
					itemList: [...deletableGroups.map(g => g.name), '取消'],
					success: (res) => {
						if (res.tapIndex < deletableGroups.length) {
							const group = deletableGroups[res.tapIndex]
							const gi = this.deviceGroups.indexOf(group)
							uni.showModal({
								title: '删除设备组',
								content: `确定删除"${group.name}"？组内 ${group.devices.length} 个设备将移回"未分组设备"`,
								success: (r) => {
									if (r.confirm) {
										const lastGroup = this.deviceGroups[this.deviceGroups.length - 1]
										group.devices.forEach(d => lastGroup.devices.push(d))
										this.deviceGroups.splice(gi, 1)
										uni.showToast({ title: '已删除设备组', icon: 'success' })
									}
								}
							})
						}
					}
				})
			},
			toggleGroup(gi) { this.deviceGroups[gi].expanded = !this.deviceGroups[gi].expanded },
			onEditGroupName(gi) {
				const group = this.deviceGroups[gi]
				if (gi === this.deviceGroups.length - 1) {
					uni.showToast({ title: '未分组设备不可修改名称', icon: 'none' })
					return
				}
				uni.showModal({
					title: '编辑组名', editable: true, placeholderText: '输入新名称...', content: group.name,
					success: (res) => { if (res.confirm && res.content) { group.name = res.content; uni.showToast({ title: '已重命名', icon: 'success' }) } }
				})
			},
			onEditDeviceName(device) {
				uni.showModal({
					title: '修改设备名称', editable: true, placeholderText: '输入新名称...', content: device.name,
					success: (res) => { if (res.confirm && res.content) { device.name = res.content; uni.showToast({ title: '已重命名', icon: 'success' }) } }
				})
			},
			onGroupMore(gi) {
				const group = this.deviceGroups[gi]
				if (gi === this.deviceGroups.length - 1) {
					uni.showActionSheet({
						itemList: ['编辑组名', '取消'],
						success: (res) => { if (res.tapIndex === 0) this.onEditGroupName(gi) }
					})
					return
				}
				uni.showActionSheet({
					itemList: ['编辑组名', '删除组', '取消'],
					success: (res) => {
						if (res.tapIndex === 0) this.onEditGroupName(gi)
						else if (res.tapIndex === 1) {
							uni.showModal({
								title: '删除设备组',
								content: `确定删除"${group.name}"？组内 ${group.devices.length} 个设备将移回"未分组设备"`,
								success: (r) => {
									if (r.confirm) {
										const lastGroup = this.deviceGroups[this.deviceGroups.length - 1]
										group.devices.forEach(d => { d.showClose = false; lastGroup.devices.push(d) })
										this.deviceGroups.splice(gi, 1)
										uni.showToast({ title: '已删除设备组', icon: 'success' })
									}
								}
							})
						}
					}
				})
			},
			batchPowerOn(group) {
				uni.showModal({
					title: '批量开机', content: `确定开启"${group.name}"所有在线设备？`,
					success: (res) => {
						if (res.confirm) {
							let count = 0
							group.devices.forEach(d => { if (!d.offline) { d.power = 1; d.statusText = '运行中'; count++ } })
							uni.showToast({ title: `已开机 ${count} 台设备`, icon: 'success' })
						}
					}
				})
			},
			batchPowerOff(group) {
				uni.showModal({
					title: '批量关机', content: `确定关闭"${group.name}"所有在线设备？`,
					success: (res) => {
						if (res.confirm) {
							let count = 0
							group.devices.forEach(d => { if (!d.offline) { d.power = 0; d.statusText = '已停火'; count++ } })
							uni.showToast({ title: `已关机 ${count} 台设备`, icon: 'success' })
						}
					}
				})
			},
			getDragStyle(device) {
				if (this.dragDevice === device && this.isDragging) return { opacity: 0.3 }
				return {}
			},
			onDeviceTouchStart(e, device, group, gi, di) {
				const touch = e.touches[0]
				this.dragOffsetX = 80; this.dragOffsetY = 40
				this.dragStartX = touch.clientX; this.dragStartY = touch.clientY
				this.dragCurrentX = touch.clientX; this.dragCurrentY = touch.clientY
				this.dragDevice = device; this.dragSourceGroup = group; this.dragSourceIndex = di
				this.dragOverGroup = gi; this.isDragging = false; this.dragReady = false
				const query = uni.createSelectorQuery().in(this)
				query.selectAll('.section').boundingClientRect(data => { this.sectionRects = data || [] }).exec()
				this.dragTimer = setTimeout(() => { this.dragReady = true }, 1000)
			},
			onDeviceTouchMove(e) {
				if (!this.dragDevice || !this.dragReady) return
				const touch = e.touches[0]
				if (Math.abs(touch.clientX - this.dragStartX) > 20 || Math.abs(touch.clientY - this.dragStartY) > 20) {
					this.isDragging = true
					this.dragCurrentX = touch.clientX; this.dragCurrentY = touch.clientY
					const sourceGi = this.deviceGroups.indexOf(this.dragSourceGroup)
					const moveDiff = touch.clientY - this.dragStartY
					if (moveDiff < -80 && sourceGi > 0) this.dragOverGroup = sourceGi - 1
					else if (moveDiff > 80 && sourceGi < this.deviceGroups.length - 1) this.dragOverGroup = sourceGi + 1
					else this.dragOverGroup = sourceGi
				}
			},
			onDeviceTouchEnd() {
				if (this.dragTimer) { clearTimeout(this.dragTimer); this.dragTimer = null }
				if (!this.dragDevice || !this.isDragging) {
					this.dragDevice = null; this.isDragging = false; this.dragOverGroup = -1; this.dragReady = false
					return
				}
				const sourceGi = this.deviceGroups.indexOf(this.dragSourceGroup)
				const moveDiff = this.dragCurrentY - this.dragStartY
				let targetGi = sourceGi
				if (moveDiff < -80 && sourceGi > 0) targetGi = sourceGi - 1
				else if (moveDiff > 80 && sourceGi < this.deviceGroups.length - 1) targetGi = sourceGi + 1
				if (targetGi !== sourceGi) {
					const sourceGroup = this.dragSourceGroup
					const targetGroup = this.deviceGroups[targetGi]
					sourceGroup.devices.splice(this.dragSourceIndex, 1)
					targetGroup.devices.push(this.dragDevice)
					uni.showToast({ title: `已移至"${targetGroup.name}"`, icon: 'none' })
				}
				this.dragDevice = null; this.dragSourceGroup = null; this.dragSourceIndex = -1
				this.dragOverGroup = -1; this.isDragging = false; this.dragReady = false
			},
			removeDevice(group, di) {
				const device = group.devices[di]
				const lastGroup = this.deviceGroups[this.deviceGroups.length - 1]
				if (group === lastGroup) {
					group.devices.splice(di, 1)
					uni.showToast({ title: '已删除设备', icon: 'success' })
				} else {
					group.devices.splice(di, 1)
					lastGroup.devices.push(device)
					uni.showToast({ title: '已移回未分组', icon: 'none' })
				}
			},
			onDeviceClick(device) {
				if (device.offline) { uni.showToast({ title: '设备离线，无法操作', icon: 'none' }); return }
				const deviceId = encodeURIComponent(device.mac || device.name)
				uni.setStorageSync('selectedDeviceId', deviceId)
				uni.navigateTo({ url: '/pages/device/detail' })
			},
			switchTab(ti) {
				this.activeTab = ti
				if (ti === 0) return
				const deviceId = uni.getStorageSync('selectedDeviceId')
				if (!deviceId) { uni.showToast({ title: '请先在首页选择设备', icon: 'none' }); return }
				uni.navigateTo({ url: '/pages/device/detail' })
			},
			showTestAlarm() {
				const allDevices = []
				for (const group of this.deviceGroups) {
					for (const device of group.devices) allDevices.push(device)
				}
				if (allDevices.length === 0) { uni.showToast({ title: '请先添加设备', icon: 'none' }); return }
				const alarmTypes = [
					{ label: '机芯超温', cmd: '>AE1' },
					{ label: '线盘超温', cmd: '>AE2' },
					{ label: '过流保护', cmd: '>AE3' },
					{ label: '电流异常', cmd: '>AE4' },
					{ label: '锅具异常', cmd: '>AE5' },
					{ label: '线盘测温开路', cmd: '>AE6' }
				]
				uni.showActionSheet({
					itemList: [...allDevices.map(d => d.name), '取消'],
					success: (res) => {
						if (res.tapIndex < allDevices.length) {
							const selectedDevice = allDevices[res.tapIndex]
							uni.showActionSheet({
								itemList: [...alarmTypes.map(a => a.label), '取消'],
								success: (r) => {
									if (r.tapIndex < alarmTypes.length) {
										this._triggerAlarm(selectedDevice, alarmTypes[r.tapIndex])
									}
								}
							})
						}
					}
				})
			},
			_triggerAlarm(device, alarm) {
				const deviceId = device.mac || device.name
				const alarmData = {
					deviceId, deviceName: device.name,
					alarmCmd: alarm.cmd, alarmLabel: alarm.label,
					timestamp: Date.now()
				}
				uni.setStorageSync('pendingAlarm', alarmData)
				uni.$emit('deviceAlarm', alarmData)
				uni.setStorageSync('selectedDeviceId', encodeURIComponent(deviceId))
				uni.navigateTo({ url: '/pages/device/detail' })
				uni.showToast({ title: `已模拟: ${device.name} - ${alarm.label}`, icon: 'none' })
			}

		}
	}
</script>

<style>
.page { width: 750rpx; min-height: 100vh; background-color: #f5f6fa; display: flex; flex-direction: column; position: relative; }
.header { height: 88rpx; padding: 0 32rpx; padding-top: var(--status-bar-height, 44rpx); background-color: #fcf8ff; display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 100; flex-shrink: 0; }
.header-title { font-size: 32rpx; font-weight: 700; color: #0057bf; }
.header-btn { width: 80rpx; height: 80rpx; border-radius: 40rpx; display: flex; align-items: center; justify-content: center; background: transparent; }
.header-btn-icon { width: 32rpx; height: 32rpx; display: flex; align-items: center; justify-content: center; }
.plus-icon { font-size: 44rpx; font-weight: 300; color: #0057bf; line-height: 1; }
.menu-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 50; }
.menu-dropdown { position: absolute; top: 120rpx; right: 32rpx; background: #ffffff; border-radius: 24rpx; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.12); width: 360rpx; overflow: hidden; z-index: 200; }
.menu-item { padding: 28rpx 40rpx; display: flex; align-items: center; gap: 20rpx; }
.menu-item:active { background-color: #f5f6fa; }
.menu-item-icon { font-size: 32rpx; width: 48rpx; text-align: center; }
.menu-item-text { font-size: 28rpx; color: #1a1a2e; }
.menu-divider { height: 1px; background-color: #f0f0f0; margin: 0 32rpx; }
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 80rpx; padding-bottom: 200rpx; }
.empty-icon-wrap { width: 160rpx; height: 160rpx; border-radius: 80rpx; background: #e8f4fd; display: flex; align-items: center; justify-content: center; margin-bottom: 32rpx; }
.empty-icon { font-size: 64rpx; }
.empty-title { font-size: 36rpx; font-weight: 700; color: #1a1a2e; margin-bottom: 16rpx; }
.empty-desc { font-size: 28rpx; color: #414754; text-align: center; margin-bottom: 48rpx; line-height: 1.5; }
.empty-actions { display: flex; flex-direction: column; gap: 24rpx; width: 100%; }
.empty-btn { width: 100%; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; border: 2rpx solid #0057bf; background: transparent; }
.empty-btn.primary { background: #0057bf; border: none; }
.empty-btn-text { font-size: 32rpx; color: #0057bf; font-weight: 600; }
.empty-btn.primary .empty-btn-text { color: #ffffff; }
.main { flex: 1; overflow: hidden; padding: 0 24rpx; padding-bottom: 120rpx; }
.section { background: #ffffff; border-radius: 24rpx; margin-top: 24rpx; overflow: hidden; }
.section-header { padding: 28rpx 32rpx; display: flex; align-items: center; justify-content: space-between; }
.section-header-left { display: flex; align-items: center; gap: 16rpx; flex: 1; }
.section-title { font-size: 30rpx; font-weight: 700; color: #1a1a2e; }
.section-tag { background: #f0f4ff; border-radius: 8rpx; padding: 4rpx 16rpx; }
.section-tag-text { font-size: 22rpx; color: #0057bf; }
.group-more-btn { width: 48rpx; height: 48rpx; display: flex; align-items: center; justify-content: center; }
.group-more-icon { font-size: 36rpx; color: #414754; }
.section-header-right { display: flex; align-items: center; gap: 16rpx; }
.batch-btn { display: flex; align-items: center; gap: 8rpx; padding: 8rpx 20rpx; border-radius: 20rpx; background: #e8f4fd; }
.batch-btn-icon { width: 28rpx; height: 28rpx; display: flex; align-items: center; justify-content: center; }
.batch-icon-play { font-size: 20rpx; color: #0057bf; }
.batch-btn-text { font-size: 22rpx; color: #0057bf; }
.batch-off { background: #fde8e8; }
.batch-icon-stop { font-size: 20rpx; color: #e74c3c; }
.batch-off-text { color: #e74c3c; }
.section-arrow { width: 40rpx; height: 40rpx; display: flex; align-items: center; justify-content: center; transition: transform 0.3s; }
.section-arrow.expanded { transform: rotate(90deg); }
.arrow-icon { font-size: 24rpx; color: #414754; }
.section-body { padding: 0 32rpx 32rpx; }
.device-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20rpx; }
.device-card { background: #f8f9fc; border-radius: 20rpx; padding: 24rpx; position: relative; transition: all 0.2s; }
.device-card:active { transform: scale(0.97); }
.device-card.offline { opacity: 0.6; }
.device-card.dragging { opacity: 0.3; }
.card-icon-wrap { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.card-icon-bg { width: 64rpx; height: 64rpx; border-radius: 32rpx; background: #e8f4fd; display: flex; align-items: center; justify-content: center; }
.card-icon-bg.icon-offline { background: #e0e0e0; }
.card-icon { font-size: 32rpx; }
.card-more-icon { width: 32rpx; height: 32rpx; display: flex; align-items: center; justify-content: center; }
.card-name { font-size: 26rpx; font-weight: 600; color: #1a1a2e; display: block; margin-bottom: 8rpx; }
.card-status { font-size: 22rpx; display: block; margin-bottom: 12rpx; }
.status-online { color: #0057bf; }
.status-stopped { color: #414754; }
.status-offline { color: #999; }
.heat-bar { display: flex; gap: 4rpx; }
.heat-seg { flex: 1; height: 8rpx; border-radius: 4rpx; background: #e0e0e0; }
.heat-seg.seg-blue { background: #0057bf; }
.heat-seg.seg-orange { background: #ff9500; }
.heat-seg.seg-red { background: #e74c3c; }
.heat-seg.seg-offline { background: #e0e0e0; }
.heat-seg.seg-inactive { background: #e0e0e0; }
.card-close { position: absolute; top: 8rpx; right: 8rpx; width: 36rpx; height: 36rpx; border-radius: 18rpx; background: rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center; }
.close-icon { font-size: 20rpx; color: #999; }
.empty-group { padding: 40rpx 0; display: flex; flex-direction: column; align-items: center; gap: 16rpx; }
.empty-text { font-size: 26rpx; color: #999; }
.empty-group-btn { padding: 12rpx 32rpx; border-radius: 24rpx; border: 2rpx solid #0057bf; }
.empty-group-btn-text { font-size: 26rpx; color: #0057bf; }
.test-alarm-section { margin-bottom: 24rpx; }
.test-alarm-body { padding: 0 32rpx 32rpx; }
.test-alarm-desc { font-size: 24rpx; color: #666; display: block; margin-bottom: 16rpx; }
.test-alarm-btn { padding: 16rpx 32rpx; border-radius: 24rpx; background: #fff3e0; display: inline-flex; }
.test-alarm-btn-text { font-size: 26rpx; color: #e67e22; }
.drag-float { position: fixed; z-index: 9999; pointer-events: none; }
.drag-float-card { width: 200rpx; padding: 24rpx; background: #ffffff; border-radius: 20rpx; box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.15); display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.drag-float-icon { font-size: 48rpx; }
.drag-float-name { font-size: 24rpx; color: #1a1a2e; font-weight: 600; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 500; }
.modal { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-radius: 32rpx 32rpx 0 0; z-index: 501; max-height: 80vh; overflow-y: auto; padding-bottom: 40rpx; }
.modal-header { padding: 32rpx; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 32rpx; font-weight: 700; color: #1a1a2e; }
.modal-close { width: 48rpx; height: 48rpx; display: flex; align-items: center; justify-content: center; }
.modal-close-icon { font-size: 32rpx; color: #999; }
.ble-search { padding: 60rpx 32rpx; display: flex; flex-direction: column; align-items: center; gap: 16rpx; }
.ble-animation { position: relative; width: 120rpx; height: 120rpx; display: flex; align-items: center; justify-content: center; }
.ble-pulse { position: absolute; width: 120rpx; height: 120rpx; border-radius: 60rpx; background: #e8f4fd; animation: pulse 2s infinite; }
.ble-pulse.delay { animation-delay: 0.5s; }
.ble-pulse.delay2 { animation-delay: 1s; }
@keyframes pulse { 0% { transform: scale(0.8); opacity: 0.8; } 100% { transform: scale(1.5); opacity: 0; } }
.ble-icon { font-size: 48rpx; z-index: 1; }
.ble-search-text { font-size: 28rpx; color: #1a1a2e; font-weight: 600; }
.ble-search-hint { font-size: 24rpx; color: #999; }
.ble-stop-btn { padding: 16rpx 48rpx; border-radius: 32rpx; background: #f5f6fa; margin-top: 16rpx; }
.ble-stop-text { font-size: 26rpx; color: #e74c3c; }
.ble-results { padding: 32rpx; }
.ble-result-title { font-size: 28rpx; color: #1a1a2e; font-weight: 600; display: block; margin-bottom: 16rpx; }
.ble-device-list { display: flex; flex-direction: column; gap: 12rpx; }
.ble-device-item { padding: 24rpx 32rpx; background: #f8f9fc; border-radius: 16rpx; display: flex; align-items: center; justify-content: space-between; }
.ble-device-info { display: flex; flex-direction: column; gap: 4rpx; }
.ble-device-name { font-size: 28rpx; color: #1a1a2e; font-weight: 600; }
.ble-device-mac { font-size: 22rpx; color: #999; }
.ble-rssi-icon { font-size: 32rpx; }
.rssi-strong { opacity: 1; }
.rssi-medium { opacity: 0.6; }
.rssi-weak { opacity: 0.3; }
.ble-rescan-btn { padding: 16rpx 48rpx; border-radius: 32rpx; background: #f5f6fa; display: inline-flex; margin-top: 16rpx; }
.ble-rescan-text { font-size: 26rpx; color: #0057bf; }
.ble-no-devices { padding: 60rpx 32rpx; display: flex; flex-direction: column; align-items: center; gap: 16rpx; }
.ble-no-icon { font-size: 64rpx; }
.ble-no-text { font-size: 28rpx; color: #1a1a2e; font-weight: 600; }
.ble-no-hint { font-size: 24rpx; color: #999; text-align: center; }
.modal-footer { padding: 32rpx; display: flex; flex-direction: column; gap: 16rpx; }
.modal-btn { width: 100%; height: 88rpx; border-radius: 44rpx; display: flex; align-items: center; justify-content: center; border: 2rpx solid #0057bf; background: transparent; }
.modal-btn.primary { background: #0057bf; border: none; }
.modal-btn-text { font-size: 32rpx; color: #0057bf; font-weight: 600; }
.modal-btn.primary .modal-btn-text { color: #ffffff; }

/* ===== 自定义底部导航栏 ===== */
.custom-tabbar { position: fixed; bottom: 0; left: 0; right: 0; height: 100rpx; background: #fcf8ff; display: flex; align-items: center; justify-content: space-around; border-top: 1px solid #e8e8e8; z-index: 100; padding-bottom: var(--safe-area-inset-bottom, 0); }
.tabbar-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: relative; }
.tabbar-text { font-size: 28rpx; color: #414754; font-weight: 500; }
.tabbar-text-active { font-size: 32rpx; color: #0057bf; font-weight: 700; }
.tabbar-indicator { position: absolute; bottom: 0; width: 40rpx; height: 6rpx; border-radius: 3rpx; background: #0057bf; }
.tabbar-item-active .tabbar-text { font-size: 32rpx; color: #0057bf; font-weight: 700; }

</style>


