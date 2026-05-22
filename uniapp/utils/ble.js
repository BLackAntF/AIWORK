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

// 指令集
const CMD = {
	// 基本控制
	POWER_ON: '>A',        // 开机
	POWER_OFF: '>B',       // 关机
	STANDBY: '>C',         // 待机
	
	// 模式选择
	MODE_FRY: '>D',        // 煎炸模式
	MODE_STEW: '>E',       // 炖煮模式
	MODE_STEAM: '>F',      // 蒸模式
	MODE_BAKE: '>G',       // 烘焙模式
	MODE_WARM: '>H',       // 保温模式
	
	// 温度控制
	TEMP_UP: '>I',         // 升温
	TEMP_DOWN: '>J',       // 降温
	TEMP_SET_PREFIX: '>K', // 设置温度 + 数值 (如 >K180 表示180度)
	
	// 时间控制
	TIME_UP: '>L',         // 时间增加
	TIME_DOWN: '>M',       // 时间减少
	TIME_SET_PREFIX: '>N', // 设置时间 + 数值 (如 >N30 表示30分钟)
	
	// 功能控制
	START: '>O',           // 开始烹饪
	PAUSE: '>P',           // 暂停
	STOP: '>Q',            // 停止
	TIMER: '>R',           // 定时
	
	// 状态查询
	QUERY_STATUS: '>S',    // 查询状态
	QUERY_TEMP: '>T',      // 查询温度
	QUERY_TIME: '>U',      // 查询剩余时间
	
	// 异常处理
	RESET_ALARM: '>V',     // 重置警报
	EMERGENCY_STOP: '>W',  // 紧急停止
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
	 * 设置温度
	 */
	setTemperature(temp) {
		const cmd = CMD.TEMP_SET_PREFIX + temp
		return this.sendCommand(cmd)
	}

	/**
	 * 设置时间（分钟）
	 */
	setTime(minutes) {
		const cmd = CMD.TIME_SET_PREFIX + minutes
		return this.sendCommand(cmd)
	}

	/**
	 * 设置模式
	 */
	setMode(mode) {
		return this.sendCommand(mode)
	}

	/**
	 * 查询设备状态
	 */
	queryStatus() {
		return this.sendCommand(CMD.QUERY_STATUS)
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
export { bleManager, CMD, SERVICE_UUID, CHARACTERISTIC_UUID }
export default bleManager
