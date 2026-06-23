/**
 * 蓝牙通信工具模块
 * 智慧烹饪系统 - 设备控制协议
 */

// 设备服务UUID
const SERVICE_UUID = {
	COOKER: '0000FFB0-0000-1000-8000-00805F9B34FB',
	// 可扩展其他设备
}

// 特征值UUID
const CHARACTERISTIC_UUID = {
	WRITE: '0000FFB2-0000-1000-8000-00805F9B34FB',
	NOTIFY: '0000FFB1-0000-1000-8000-00805F9B34FB',
}

/**
 * 12KW电磁机芯串口完整指令集
 * 串口通讯参数：波特率9600，无校验位，8数据位，1停止位，无流控
 * 
 * 协议格式说明：
 *   下发指令 → 机芯返回 >OK 代表执行成功
 *   查询指令 → 机芯上报数据
 *   异常情况 → 机芯主动推送 >AE1~>AE6
 * 
 * 一、查询类下发指令（读取设备数据）
 *   1. >AT?：查询三路温度
 *      机芯上报格式：>A XX XX XX XX XX XX（依次为1路温度、2路温度、3路温度）
 *   2. >AP?：查询电参数
 *      机芯上报格式：>A XX XX XX XX XX XX（依次为电压、功率、电流）
 * 
 * 二、机芯自动故障上报（设备异常主动推送）
 *   >AE1：机芯超温  >AE2：线盘超温  >AE3：过流保护
 *   >AE4：电流异常  >AE5：锅具异常  >AE6：线盘测温开路
 * 
 * 三、开关机基础控制指令（下发后机芯返回 >OK）
 *   >AFO：开机  >AFF：关机
 * 
 * 四、12档火力档位控制指令（下发后机芯返回 >OK）
 *   >AF1~>AF9：一档~九档  >AFA：十档  >AFB：十一档  >AFC：十二档
 * 
 * 五、内外分区整体控制指令（下发后机芯返回 >OK）
 *   >ACI：仅内区工作  >ACX：仅外区工作  >ACL：内外全区同时工作
 * 
 * 六、内区分段独立控制指令（下发后机芯返回 >OK）
 *   >AA1~>AA5：内区1段~5段
 * 
 * 七、外区分段独立控制指令（下发后机芯返回 >OK）
 *   >AB1~>AB5：外区1段~5段
 */
const CMD = {
	// ===== 一、查询类指令（手机→设备） =====
	
	/** 查询三路温度 */
	QUERY_TEMP: '>AT?',
	
	/** 查询电参数（电压/功率/电流） */
	QUERY_POWER: '>AP?',
	
	// ===== 二、异常码（设备→手机主动上报） =====
	ALARM_OVERTEMP: '>AE1',          // 机芯超温
	ALARM_COIL_OVERTEMP: '>AE2',     // 线盘超温
	ALARM_OVERCURRENT: '>AE3',       // 过流保护
	ALARM_CURRENT_ABNORMAL: '>AE4',  // 电流异常
	ALARM_POT_ABNORMAL: '>AE5',      // 锅具异常
	ALARM_SENSOR_OPEN: '>AE6',       // 线盘测温开路
	
	// ===== 三、开关机基础控制指令 =====
	/** 开机 */
	POWER_ON: '>AFO',
	/** 关机 */
	POWER_OFF: '>AFF',
	
	// ===== 四、12档火力档位控制指令 =====
	GEAR_1: '>AF1',   // 一档
	GEAR_2: '>AF2',   // 二档
	GEAR_3: '>AF3',   // 三档
	GEAR_4: '>AF4',   // 四档
	GEAR_5: '>AF5',   // 五档
	GEAR_6: '>AF6',   // 六档
	GEAR_7: '>AF7',   // 七档
	GEAR_8: '>AF8',   // 八档
	GEAR_9: '>AF9',   // 九档
	GEAR_10: '>AFA',  // 十档
	GEAR_11: '>AFB',  // 十一档
	GEAR_12: '>AFC',  // 十二档
	
	// ===== 五、内外分区整体控制指令 =====
	/** 仅内区工作 */
	ZONE_INNER_ONLY: '>ACI',
	/** 仅外区工作 */
	ZONE_OUTER_ONLY: '>ACX',
	/** 内外全区同时工作 */
	ZONE_ALL: '>ACL',
	
	// ===== 六、内区分段独立控制指令（5段） =====
	INNER_SEG_1: '>AA1',  // 内区1段
	INNER_SEG_2: '>AA2',  // 内区2段
	INNER_SEG_3: '>AA3',  // 内区3段
	INNER_SEG_4: '>AA4',  // 内区4段
	INNER_SEG_5: '>AA5',  // 内区5段
	
	// ===== 七、外区分段独立控制指令（5段） =====
	OUTER_SEG_1: '>AB1',  // 外区1段
	OUTER_SEG_2: '>AB2',  // 外区2段
	OUTER_SEG_3: '>AB3',  // 外区3段
	OUTER_SEG_4: '>AB4',  // 外区4段
	OUTER_SEG_5: '>AB5',  // 外区5段
	
	// ===== 设备应答 =====
	/** 设备执行成功应答 */
	ACK_OK: '>OK',
}

/** 档位名称映射 */
const GEAR_NAMES = {
	1: '一档', 2: '二档', 3: '三档', 4: '四档',
	5: '五档', 6: '六档', 7: '七档', 8: '八档',
	9: '九档', 10: '十档', 11: '十一档', 12: '十二档'
}

/** 异常码描述 */
const ALARM_DESCS = {
	'>AE1': '机芯超温',
	'>AE2': '线盘超温',
	'>AE3': '过流保护',
	'>AE4': '电流异常',
	'>AE5': '锅具异常',
	'>AE6': '线盘测温开路'
}

/** 分区模式描述 */
const ZONE_DESCS = {
	'>ACI': '仅内区工作',
	'>ACX': '仅外区工作',
	'>ACL': '内外全区同时工作'
}

/** 内区分段描述 */
const INNER_SEG_DESCS = {
	1: '内区1段', 2: '内区2段', 3: '内区3段', 4: '内区4段', 5: '内区5段'
}

/** 外区分段描述 */
const OUTER_SEG_DESCS = {
	1: '外区1段', 2: '外区2段', 3: '外区3段', 4: '外区4段', 5: '外区5段'
}


class BLEManager {
	constructor() {
		this.deviceId = ''
		this.serviceId = SERVICE_UUID.COOKER
		this.writeId = CHARACTERISTIC_UUID.WRITE
		this.notifyId = CHARACTERISTIC_UUID.NOTIFY
		this._connected = false
		this.deviceName = ''
		this.onMessageCallback = null
		this.onStatusChangeCallback = null
	}

	/**
	 * 字符串转 ArrayBuffer
	 */
	stringToBuffer(str) {
		let array = new Uint8Array(str.length)
		for (let i = 0; i < str.length; i++) {
			array[i] = str.charCodeAt(i)
		}
		return array.buffer
	}

	/**
	 * ArrayBuffer 转字符串
	 */
	bufferToString(buffer) {
		let array = new Uint8Array(buffer)
		return String.fromCharCode.apply(null, array)
	}

	/**
	 * 初始化蓝牙适配器
	 */
	init() {
		return new Promise((resolve, reject) => {
			uni.openBluetoothAdapter({
				success: (res) => {
					console.log('蓝牙适配器初始化成功', res)
					resolve(res)
				},
				fail: (err) => {
					console.error('蓝牙适配器初始化失败', err)
					reject(err)
				}
			})
		})
	}

	/**
	 * 开始扫描设备
	 */
	startScan() {
		return new Promise((resolve, reject) => {
			uni.startBluetoothDevicesDiscovery({
				services: [],
				allowDuplicatesKey: false,
				success: (res) => {
					console.log('开始扫描设备', res)
					resolve(res)
				},
				fail: (err) => {
					console.error('扫描失败', err)
					reject(err)
				}
			})
		})
	}

	/**
	 * 停止扫描
	 */
	stopScan() {
		return new Promise((resolve, reject) => {
			uni.stopBluetoothDevicesDiscovery({
				success: (res) => {
					console.log('停止扫描', res)
					resolve(res)
				},
				fail: (err) => {
					reject(err)
				}
			})
		})
	}

	/**
	 * 监听发现的设备
	 */
	onDeviceFound(callback) {
		uni.onBluetoothDeviceFound((res) => {
			const devices = res.devices || []
			devices.forEach(device => {
				if (device.name && device.name.includes('Cooker')) {
					callback(device)
				}
			})
		})
	}

	/**
	 * 连接设备
	 */
	connect(deviceId, deviceName = '') {
		return new Promise((resolve, reject) => {
			this.deviceId = deviceId
			this.deviceName = deviceName
			
			uni.createBLEConnection({
				deviceId,
				success: (res) => {
					console.log('连接成功', res)
					this.isConnected = true
					this._notifyStatusChange(true)
					// 连接成功后获取服务
					this._getServices().then(() => {
						resolve(res)
					}).catch(reject)
				},
				fail: (err) => {
					console.error('连接失败', err)
					this.isConnected = false
					this._notifyStatusChange(false)
					reject(err)
				}
			})
		})
	}

	/**
	 * 断开连接
	 */
	disconnect() {
		return new Promise((resolve, reject) => {
			if (!this.deviceId) {
				resolve()
				return
			}
			uni.closeBLEConnection({
				deviceId: this.deviceId,
				success: (res) => {
					console.log('断开连接', res)
					this.isConnected = false
					this._notifyStatusChange(false)
					resolve(res)
				},
				fail: (err) => {
					reject(err)
				}
			})
		})
	}

	/**
	 * 获取服务
	 */
	_getServices() {
		return new Promise((resolve, reject) => {
			uni.getBLEDeviceServices({
				deviceId: this.deviceId,
				success: (res) => {
					console.log('获取服务成功', res)
					// 先用完整UUID匹配
					let service = res.services.find(s => 
						s.uuid.toUpperCase() === this.serviceId.toUpperCase()
					)
					// 再用16位UUID部分匹配
					if (!service) {
						service = res.services.find(s => 
							s.uuid.toUpperCase().includes(this.serviceId.toUpperCase().substring(4, 8))
						)
					}
					// 最后用第一个可用的Primary Service
					if (!service) {
						service = res.services.find(s => s.uuid && s.uuid.length > 0)
						console.log('使用第一个可用服务:', service?.uuid)
					}
					if (service) {
						this.serviceId = service.uuid
						this._getCharacteristics().then(resolve).catch(reject)
					} else {
						reject(new Error('未找到任何服务'))
					}
				},
				fail: (err) => {
					reject(err)
				}
			})
		})
	}

	/**
	 * 获取特征值
	 */
	_getCharacteristics() {
		return new Promise((resolve, reject) => {
			uni.getBLEDeviceCharacteristics({
				deviceId: this.deviceId,
				serviceId: this.serviceId,
				success: (res) => {
					console.log('获取特征值成功', res)
					const characteristics = res.characteristics
					let foundWrite = false
					let foundNotify = false
					// 查找写特征值和通知特征值
					characteristics.forEach(char => {
						if (char.properties.write) {
							this.writeId = char.uuid
							foundWrite = true
							console.log('找到Write特征值:', char.uuid)
						}
						if (char.properties.notify) {
							this.notifyId = char.uuid
							foundNotify = true
							console.log('找到Notify特征值:', char.uuid)
						}
					})
					// 如果没找到Write，尝试用UUID匹配
					if (!foundWrite) {
						const writeChar = characteristics.find(c => 
							c.uuid.toUpperCase().includes('FFB2')
						)
						if (writeChar) {
							this.writeId = writeChar.uuid
							console.log('通过UUID匹配到Write:', writeChar.uuid)
						}
					}
					// 如果没找到Notify，尝试用UUID匹配
					if (!foundNotify) {
						const notifyChar = characteristics.find(c => 
							c.uuid.toUpperCase().includes('FFB1')
						)
						if (notifyChar) {
							this.notifyId = notifyChar.uuid
							console.log('通过UUID匹配到Notify:', notifyChar.uuid)
						}
					}
					// 开启通知监听（即使没找到也不影响连接）
					this._startNotify()
					resolve(res)
				},
				fail: (err) => {
					console.error('获取特征值失败', err)
					// 获取特征值失败也不阻断连接流程
					resolve(res)
				}
			})
		})
	}

	/**
	 * 开启通知
	 */
	_startNotify() {
		uni.notifyBLECharacteristicValueChange({
			deviceId: this.deviceId,
			serviceId: this.serviceId,
			characteristicId: this.notifyId,
			state: true,
			success: (res) => {
				console.log('开启通知成功', res)
				// 监听设备返回数据
				uni.onBLECharacteristicValueChange((res) => {
					const data = this.bufferToString(res.value)
					console.log('设备返回数据:', data)
					if (this.onMessageCallback) {
						this.onMessageCallback(data)
					}
				})
			},
			fail: (err) => {
				console.error('开启通知失败', err)
			}
		})
	}

	/**
	 * 发送指令
	 */
	sendCommand(command) {
		return new Promise((resolve, reject) => {
			if (!this.isConnected) {
				reject(new Error('设备未连接'))
				return
			}
			const buffer = this.stringToBuffer(command)
			uni.writeBLECharacteristicValue({
				deviceId: this.deviceId,
				serviceId: this.serviceId,
				characteristicId: this.writeId,
				value: buffer,
				success: (res) => {
					console.log('指令发送成功:', command)
					resolve(res)
				},
				fail: (err) => {
					console.error('指令发送失败:', command, err)
					reject(err)
				}
			})
		})
	}

	// ===== 便捷指令方法 =====

	/**
	 * 开机
	 * 机芯返回 >OK 代表执行成功
	 */
	powerOn() {
		return this.sendCommand(CMD.POWER_ON)
	}

	/**
	 * 关机
	 * 机芯返回 >OK 代表执行成功
	 */
	powerOff() {
		return this.sendCommand(CMD.POWER_OFF)
	}

	/**
	 * 设置火力档位（1-12档）
	 * @param {number} level 档位 1-12
	 * 机芯返回 >OK 代表执行成功
	 */
	setGear(level) {
		const key = `GEAR_${level}`
		if (!CMD[key]) {
			return Promise.reject(new Error(`无效档位: ${level}`))
		}
		return this.sendCommand(CMD[key])
	}

	/**
	 * 查询温度（3路）
	 * 机芯上报格式: >A XX XX XX XX XX XX（依次为1路温度、2路温度、3路温度）
	 */
	queryTemperature() {
		return this.sendCommand(CMD.QUERY_TEMP)
	}

	/**
	 * 查询电参数（电压/功率/电流）
	 * 机芯上报格式: >A XX XX XX XX XX XX（依次为电压、功率、电流）
	 */
	queryPower() {
		return this.sendCommand(CMD.QUERY_POWER)
	}

	/**
	 * 设置内外分区整体控制
	 * @param {'inner'|'outer'|'all'} zone 分区模式
	 * 机芯返回 >OK 代表执行成功
	 */
	setZone(zone) {
		const map = {
			inner: CMD.ZONE_INNER_ONLY,
			outer: CMD.ZONE_OUTER_ONLY,
			all: CMD.ZONE_ALL
		}
		const cmd = map[zone]
		if (!cmd) {
			return Promise.reject(new Error(`无效分区模式: ${zone}`))
		}
		return this.sendCommand(cmd)
	}

	/**
	 * 设置内区分段（1-5段）
	 * @param {number} seg 段位 1-5
	 * 机芯返回 >OK 代表执行成功
	 */
	setInnerSegment(seg) {
		const key = `INNER_SEG_${seg}`
		if (!CMD[key]) {
			return Promise.reject(new Error(`无效内区分段: ${seg}`))
		}
		return this.sendCommand(CMD[key])
	}

	/**
	 * 设置外区分段（1-5段）
	 * @param {number} seg 段位 1-5
	 * 机芯返回 >OK 代表执行成功
	 */
	setOuterSegment(seg) {
		const key = `OUTER_SEG_${seg}`
		if (!CMD[key]) {
			return Promise.reject(new Error(`无效外区分段: ${seg}`))
		}
		return this.sendCommand(CMD[key])
	}

	/**
	 * 解析温度上报数据
	 * 机芯上报格式: >A XX XX XX XX XX XX
	 * 依次为1路温度、2路温度、3路温度（各2字节十六进制）
	 */
	parseTemperatureData(data) {
		if (!data || !data.startsWith('>A') || data.length < 14) return null
		const hexStr = data.substring(2, 14)
		if (hexStr.length < 12) return null
		return {
			channel1: parseInt(hexStr.substring(0, 4), 16),
			channel2: parseInt(hexStr.substring(4, 8), 16),
			channel3: parseInt(hexStr.substring(8, 12), 16),
			raw: data
		}
	}

	/**
	 * 解析电参数上报数据
	 * 机芯上报格式: >A XX XX XX XX XX XX
	 * 依次为电压、功率、电流（各2字节十六进制）
	 */
	parsePowerData(data) {
		if (!data || !data.startsWith('>A') || data.length < 14) return null
		const hexStr = data.substring(2, 14)
		if (hexStr.length < 12) return null
		return {
			voltage: parseInt(hexStr.substring(0, 4), 16),
			power: parseInt(hexStr.substring(4, 8), 16),
			current: parseInt(hexStr.substring(8, 12), 16),
			raw: data
		}
	}

	/**
	 * 判断是否为异常上报
	 */
	isAlarm(data) {
		return data && (data.startsWith('>AE1') || data.startsWith('>AE2') || 
			data.startsWith('>AE3') || data.startsWith('>AE4') || 
			data.startsWith('>AE5') || data.startsWith('>AE6'))
	}

	/**
	 * 判断是否为设备应答成功
	 */
	isAckOk(data) {
		return data && data.trim() === CMD.ACK_OK
	}

	/**
	 * 判断是否为查询类数据上报（温度或电参数）
	 */
	isQueryResponse(data) {
		return data && data.startsWith('>A') && data.length >= 14
	}

	/**
	 * 设置消息回调
	 */
	onMessage(callback) {
		this.onMessageCallback = callback
	}

	/**
	 * 设置状态变化回调
	 */
	onStatusChange(callback) {
		this.onStatusChangeCallback = callback
	}

	/**
	 * 通知状态变化
	 */
	_notifyStatusChange(connected) {
		if (this.onStatusChangeCallback) {
			this.onStatusChangeCallback(connected)
		}
	}

	/**
	 * 获取连接状态
	 */
	get isConnected() {
		return this._connected
	}

	set isConnected(val) {
		this._connected = val
	}
}

// 导出单例
const bleManager = new BLEManager()
export { 
	bleManager, 
	CMD, 
	GEAR_NAMES, 
	ALARM_DESCS, 
	ZONE_DESCS, 
	INNER_SEG_DESCS, 
	OUTER_SEG_DESCS, 
	SERVICE_UUID, 
	CHARACTERISTIC_UUID 
}
export default bleManager


