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
 * 12KW 协议指令集
 * 根据智慧烹饪系统PDF定义
 * 
 * 手机→设备：
 *   >OK     开机/关机/设置档位
 *   >AT?    查询温度（3路）
 *   >AP?    查询电参数（电压/功率/电流）
 * 
 * 设备→手机：
 *   >A + 12位十六进制    温度上报（每4位=1路，如 >A123456789ABC）
 *   >A + 12位十六进制    电参数上报（电压+功率+电流）
 *   >AE1~AE6            异常报警
 */
const CMD = {
	// ===== 控制指令（手机→设备） =====
	
	/** 开机/关机/设置档位 */
	OK: '>OK',
	
	/** 查询温度（3路） */
	QUERY_TEMP: '>AT?',
	
	/** 查询电参数（电压/功率/电流） */
	QUERY_POWER: '>AP?',
	
	// ===== 档位定义（1-12档） =====
	/** 档位1-12 */
	GEAR_1: '>OK',   // 一档
	GEAR_2: '>OK',   // 二档
	GEAR_3: '>OK',   // 三档
	GEAR_4: '>OK',   // 四档
	GEAR_5: '>OK',   // 五档
	GEAR_6: '>OK',   // 六档
	GEAR_7: '>OK',   // 七档
	GEAR_8: '>OK',   // 八档
	GEAR_9: '>OK',   // 九档
	GEAR_10: '>OK',  // 一十
	GEAR_11: '>OK',  // 十一
	GEAR_12: '>OK',  // 十二
	
	// ===== 异常码（设备→手机） =====
	ALARM_OVERTEMP: '>AE1',       // 机芯超温
	ALARM_COIL_OVERTEMP: '>AE2',  // 线盘超温
	ALARM_OVERCURRENT: '>AE3',    // 过流保护
	ALARM_CURRENT_ABNORMAL: '>AE4', // 电流异常
	ALARM_POT_ABNORMAL: '>AE5',   // 锅具异常
	ALARM_SENSOR_OPEN: '>AE6',    // 线盘测温开路
}

/** 档位名称映射 */
const GEAR_NAMES = {
	1: '一档', 2: '二档', 3: '三档', 4: '四档',
	5: '五档', 6: '六档', 7: '七档', 8: '八档',
	9: '九档', 10: '一十', 11: '十一', 12: '十二'
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

	/**
	 * 发送 >OK 指令（开机/关机/设置档位）
	 * 设备应答 >OK 表示执行成功
	 */
	sendOK() {
		return this.sendCommand(CMD.OK)
	}

	/**
	 * 查询温度（3路）
	 * 设备上报格式: >A + 12位十六进制（每4位=1路温度）
	 */
	queryTemperature() {
		return this.sendCommand(CMD.QUERY_TEMP)
	}

	/**
	 * 查询电参数（电压/功率/电流）
	 * 设备上报格式: >A + 12位十六进制
	 */
	queryPower() {
		return this.sendCommand(CMD.QUERY_POWER)
	}

	/**
	 * 解析温度上报数据
	 * 格式: >A + 12位十六进制
	 * 每4位=1路温度，如 >A123456789ABC
	 *   1路=0x1234=4660（需根据实际精度换算）
	 *   2路=0x5678=22136
	 *   3路=0x9ABC=39612
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
	 * 格式: >A + 12位十六进制
	 *   电压=前4位, 功率=中间4位, 电流=后4位
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
export { bleManager, CMD, GEAR_NAMES, ALARM_DESCS, SERVICE_UUID, CHARACTERISTIC_UUID }
export default bleManager
