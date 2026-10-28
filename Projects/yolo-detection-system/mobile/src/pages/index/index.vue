<template>
	<view class="home-page">
		<!-- 顶部品牌区 -->
		<view class="hero-section">
			<view class="hero-grid"></view>
			<view class="hero-content">
				<view class="hero-top">
					<view class="user-info">
						<view class="avatar">{{ avatarText }}</view>
						<view class="user-text">
							<text class="greeting">你好</text>
							<text class="username">{{ displayName }}</text>
						</view>
					</view>
					<view class="hero-badge" @click="goHistory">
						<AppIcon name="calendar" :size="28" color="#DCE9DF" />
						<text class="badge-text">{{ todayLabel }}</text>
					</view>
				</view>
				<view class="hero-main">
					<text class="hero-eyebrow">TOMATO LEAF DIAGNOSIS</text>
					<text class="hero-title">今天，检查一下叶片状态</text>
				</view>
			</view>
		</view>

		<!-- 统计概览 -->
		<view class="stats-section">
			<view class="stat-card">
				<text class="stat-label">累计检测</text>
				<text class="stat-value">{{ totalCount }}</text>
				<text class="stat-unit">次</text>
			</view>
			<view class="stat-card">
				<text class="stat-label">检出病害</text>
				<text class="stat-value danger">{{ diseaseCount }}</text>
				<text class="stat-unit">次</text>
			</view>
			<view class="stat-card">
				<text class="stat-label">健康叶片</text>
				<text class="stat-value success">{{ healthyCount }}</text>
				<text class="stat-unit">次</text>
			</view>
		</view>

		<!-- 天气卡片 -->
		<view v-if="weather" class="weather-section">
			<view class="weather-card">
				<view class="weather-main">
					<view class="weather-info">
						<view class="weather-title-row">
							<AppIcon name="sprout" :size="34" color="#2C5740" />
							<text class="weather-title">{{ weatherDescription }}</text>
						</view>
						<view class="weather-metrics">
							<text class="weather-temp">{{ formatTemp(weather.current.temperature) }}°C</text>
							<text class="weather-meta">湿度 {{ weather.current.humidity ?? '-' }}%</text>
							<text class="weather-meta">风速 {{ weather.current.wind_speed ?? '-' }} m/s</text>
						</view>
					</view>
					<view class="weather-location">
						<AppIcon name="pin" :size="24" color="#8A938C" />
						<text class="weather-location-text">当前位置</text>
					</view>
				</view>

				<view v-if="forecastDays.length" class="weather-daily">
					<view v-for="day in forecastDays" :key="day.date" class="daily-item">
						<text class="daily-date">{{ formatDay(day.date) }}</text>
						<text class="daily-weather">{{ weatherText(day.weather_code) }}</text>
						<text class="daily-temp">
							{{ formatTemp(day.temperature_2m_min) }}~{{ formatTemp(day.temperature_2m_max) }}°
						</text>
						<text class="daily-rain">降水 {{ day.precipitation_probability_max ?? 0 }}%</text>
					</view>
				</view>

				<view v-if="weather.advice" class="weather-advice" :class="{ suitable: weather.advice.suitable }">
					<AppIcon
						:name="weather.advice.suitable ? 'check' : 'alert'"
						:size="26"
						:color="weather.advice.suitable ? '#3C7A52' : '#D9A11E'"
					/>
					<text class="advice-text">{{ adviceText }}</text>
				</view>
			</view>
		</view>

		<!-- 快速操作 -->
		<view class="action-section">
			<view class="action-card primary" @click="goDetect">
				<view class="action-icon">
					<AppIcon name="camera" :size="52" color="#FFFFFF" />
				</view>
				<view class="action-text">
					<text class="action-title">拍照检测</text>
					<text class="action-desc">上传叶片，AI 识别病害</text>
				</view>
				<text class="action-arrow">→</text>
			</view>
			<view class="action-card secondary" @click="goChat">
				<view class="action-icon light">
					<AppIcon name="chat" :size="48" color="#C8442F" />
				</view>
				<view class="action-text">
					<text class="action-title dark">AI 问答</text>
					<text class="action-desc">咨询防治与用药建议</text>
				</view>
				<text class="action-arrow dark">→</text>
			</view>
		</view>

		<!-- 最近检测 -->
		<view class="recent-section">
			<view class="section-header">
				<view class="section-title-wrap">
					<text class="section-title">最近检测</text>
					<text class="section-count">{{ records.length }} 条</text>
				</view>
				<text class="view-all" @click="goHistory">查看全部</text>
			</view>

			<view v-if="loading" class="loading-row">
				<view class="skeleton-row"></view>
				<view class="skeleton-row"></view>
			</view>

			<EmptyState
				v-else-if="records.length === 0"
				name="leaf"
				title="还没有检测记录"
				desc="上传一张番茄叶片，开始你的第一次检测"
			/>

			<view v-else class="record-list">
				<view
					v-for="record in records"
					:key="record.id"
					class="record-item"
					@click="goHistoryDetail(record.id)"
				>
					<image
						v-if="getRecordImage(record) && !isImageBroken(record.id)"
						:src="getRecordImage(record)"
						mode="aspectFill"
						class="record-image"
						@error="onImageError(record.id)"
					/>
					<view v-else class="record-image image-broken">
						<AppIcon name="leaf" :size="28" color="#C3C9C3" />
					</view>
					<view class="record-info">
						<text class="record-disease">{{ getDiseaseName(record) }}</text>
						<text class="record-time">{{ formatTime(record.created_at) }}</text>
					</view>
					<view class="record-status" :class="{ healthy: isHealthyRecord(record) }">
						<text class="status-text">{{ getStatusLabel(record) }}</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { getHistoryList, getHistoryStats } from '@/api/history'
import { getWeather } from '@/api/weather'
import { getFullUrl } from '@/utils/format'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'

const userStore = useUserStore()
const loading = ref(false)
const records = ref([])
const brokenImages = ref([])
const stats = ref({ total: 0, disease_count: 0, healthy_count: 0 })
const weather = ref(null)
const weatherRequested = ref(false)

const DEFAULT_LOCATION = { lat: 39.9042, lon: 116.4074 }

const weatherDescription = computed(() => weatherText(weather.value?.current?.weather_code))
const forecastDays = computed(() => (weather.value?.daily || []).slice(0, 3))
const adviceText = computed(() => {
	const advice = weather.value?.advice
	if (!advice) return ''
	if (advice.suitable) return '近期适宜施药'
	return `暂缓施药：${advice.reason || '天气条件不佳'}`
})

function weatherText(code) {
	if (code === 0) return '晴'
	if (code >= 1 && code <= 3) return '多云'
	if (code === 45 || code === 48) return '雾'
	if (code >= 51 && code <= 67) return '雨'
	if (code >= 71 && code <= 77) return '雪'
	if (code >= 80 && code <= 82) return '阵雨'
	if (code >= 95 && code <= 99) return '雷雨'
	return '未知'
}

function formatTemp(value) {
	return typeof value === 'number' ? Math.round(value) : '--'
}

function formatDay(dateStr) {
	if (!dateStr) return ''
	const date = new Date(`${dateStr}T00:00:00`)
	if (Number.isNaN(date.getTime())) return dateStr
	const today = new Date()
	const tomorrow = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1)
	if (date.toDateString() === today.toDateString()) return '今天'
	if (date.toDateString() === tomorrow.toDateString()) return '明天'
	return `${date.getMonth() + 1}/${date.getDate()}`
}

function resolveLocation() {
	return new Promise((resolve) => {
		uni.getLocation({
			type: 'wgs84',
			success: (res) => {
				if (typeof res.latitude === 'number' && typeof res.longitude === 'number') {
					resolve({ lat: res.latitude, lon: res.longitude })
				} else {
					resolve(DEFAULT_LOCATION)
				}
			},
			fail: () => resolve(DEFAULT_LOCATION)
		})
	})
}

async function loadWeather() {
	if (weatherRequested.value) return
	weatherRequested.value = true
	try {
		const location = await resolveLocation()
		weather.value = await getWeather(location.lat, location.lon)
	} catch (e) {
		// 天气加载失败静默降级，不显示卡片，不影响首页其他内容
		weather.value = null
	}
}

const HEALTHY_NAMES = ['健康', '健康叶片', '健康叶子', '正常叶片', 'Healthy']

function isImageBroken(id) {
	return brokenImages.value.includes(id)
}

function onImageError(id) {
	if (!brokenImages.value.includes(id)) {
		brokenImages.value = [...brokenImages.value, id]
	}
}

const displayName = computed(() => userStore.userInfo?.username || '用户')
const avatarText = computed(() => {
	const name = userStore.userInfo?.username || 'U'
	return name.charAt(0).toUpperCase()
})

const todayLabel = computed(() => {
	const now = new Date()
	const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
	return `${now.getMonth() + 1}月${now.getDate()}日 ${week[now.getDay()]}`
})

const totalCount = computed(() => stats.value.total || 0)
const diseaseCount = computed(() => stats.value.disease_count || 0)
const healthyCount = computed(() => stats.value.healthy_count || 0)

function classList(record) {
	return (record.class_names || '').split(',').map(n => n.trim()).filter(Boolean)
}

function isHealthyRecord(record) {
	const names = classList(record)
	return names.length > 0 && names.every(n => HEALTHY_NAMES.includes(n))
}

function getStatusLabel(record) {
	const names = classList(record)
	if (names.length === 0) return '待查看'
	return names.every(n => HEALTHY_NAMES.includes(n)) ? '健康' : '需关注'
}

function getRecordImage(record) {
	const path = record.result_path || record.original_path
	return path ? getFullUrl(path) : ''
}

function getDiseaseName(record) {
	const names = classList(record)
	if (names.length === 0) {
		return record.original_filename || '未知结果'
	}
	return names.join(', ')
}

function formatTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	const now = new Date()
	const diff = now.getTime() - date.getTime()
	const days = Math.floor(diff / (1000 * 60 * 60 * 24))
	if (days === 0) {
		const hours = Math.floor(diff / (1000 * 60 * 60))
		if (hours === 0) {
			const minutes = Math.floor(diff / (1000 * 60))
			return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
		}
		return `${hours}小时前`
	}
	if (days === 1) return '昨天'
	if (days < 7) return `${days}天前`
	return `${date.getMonth() + 1}月${date.getDate()}日`
}

async function loadStats() {
	try {
		const data = await getHistoryStats()
		stats.value = data || { total: 0, disease_count: 0, healthy_count: 0 }
	} catch (e) {
		// 统计失败保持原值，不影响列表展示
	}
}

async function loadRecords() {
	loading.value = true
	try {
		const data = await getHistoryList({ page: 1, page_size: 5 })
		records.value = data.list || []
		brokenImages.value = []
	} catch (e) {
		// 静默失败，显示空状态
	} finally {
		loading.value = false
		uni.stopPullDownRefresh()
	}
	loadStats()
}

onPullDownRefresh(() => {
	loadRecords()
})

function goDetect() {
	uni.switchTab({ url: '/pages/detect/index' })
}

function goChat() {
	uni.switchTab({ url: '/pages/chat/index' })
}

function goHistory() {
	uni.switchTab({ url: '/pages/history/index' })
}

function goHistoryDetail(id) {
	uni.navigateTo({ url: `/pages/history/detail?id=${id}` })
}

onShow(() => {
	if (userStore.token && !userStore.userInfo) {
		userStore.fetchUserInfo().catch(() => {})
	}
	loadRecords()
	loadWeather()
})
</script>

<style lang="scss" scoped>
.home-page {
	min-height: 100vh;
	padding-bottom: 48rpx;
	background: var(--bg-2);
}

/* 顶部品牌区 */
.hero-section {
	position: relative;
	overflow: hidden;
	background: var(--forest);
}

.hero-grid {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 420rpx;
	background-image:
		linear-gradient(rgba(255, 255, 255, 0.04) 1rpx, transparent 1rpx),
		linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1rpx, transparent 1rpx);
	background-size: 48rpx 48rpx;
}

.hero-content {
	position: relative;
	padding: calc(32rpx + env(safe-area-inset-top)) 36rpx 56rpx;
	z-index: 2;
}

.hero-top {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 48rpx;
}

.user-info {
	display: flex;
	align-items: center;
}

.avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.14);
	border: 2rpx solid rgba(255, 255, 255, 0.24);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	font-weight: 700;
	color: #fff;
	margin-right: 20rpx;
}

.user-text {
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.greeting {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.68);
	letter-spacing: 2rpx;
}

.username {
	font-size: 32rpx;
	font-weight: 700;
	color: #fff;
}

.hero-badge {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 12rpx 20rpx;
	border-radius: 999rpx;
	background: rgba(255, 255, 255, 0.1);
	border: 1rpx solid rgba(255, 255, 255, 0.14);
}

.badge-text {
	font-size: 22rpx;
	color: #DCE9DF;
}

.hero-main {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.hero-eyebrow {
	font-size: 20rpx;
	color: #8FBF9F;
	letter-spacing: 4rpx;
}

.hero-title {
	font-size: 44rpx;
	line-height: 1.25;
	font-weight: 700;
	color: #FFFFFF;
}

/* 统计概览 */
.stats-section {
	display: flex;
	gap: 16rpx;
	padding: 0 28rpx;
	margin-top: -28rpx;
	position: relative;
	z-index: 3;
}

.stat-card {
	flex: 1;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 20rpx;
	padding: 24rpx 20rpx;
	box-shadow: var(--shadow-sm);
}

.stat-label {
	display: block;
	font-size: 22rpx;
	color: var(--text-3);
	margin-bottom: 12rpx;
}

.stat-value {
	font-size: 40rpx;
	font-weight: 700;
	color: var(--text-1);
	line-height: 1;
}

.stat-value.danger {
	color: var(--brand);
}

.stat-value.success {
	color: var(--success);
}

.stat-unit {
	font-size: 20rpx;
	color: var(--text-3);
	margin-left: 4rpx;
}

/* 天气卡片 */
.weather-section {
	padding: 0 28rpx;
	margin-top: 24rpx;
}

.weather-card {
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 24rpx;
	padding: 24rpx;
	box-shadow: var(--shadow-sm);
	display: flex;
	flex-direction: column;
	gap: 18rpx;
}

.weather-main {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 16rpx;
}

.weather-info {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
	min-width: 0;
}

.weather-title-row {
	display: flex;
	align-items: center;
	gap: 10rpx;
}

.weather-title {
	font-size: 30rpx;
	font-weight: 700;
	color: var(--text-1);
}

.weather-metrics {
	display: flex;
	align-items: baseline;
	flex-wrap: wrap;
	gap: 16rpx;
}

.weather-temp {
	font-size: 52rpx;
	font-weight: 700;
	color: var(--forest);
	line-height: 1;
}

.weather-meta {
	font-size: 22rpx;
	color: var(--text-3);
}

.weather-location {
	display: flex;
	align-items: center;
	gap: 6rpx;
	flex-shrink: 0;
}

.weather-location-text {
	font-size: 20rpx;
	color: var(--text-3);
}

.weather-daily {
	display: flex;
	gap: 12rpx;
}

.daily-item {
	flex: 1;
	background: var(--bg-2);
	border-radius: 16rpx;
	padding: 14rpx 12rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 6rpx;
}

.daily-date {
	font-size: 21rpx;
	color: var(--text-3);
}

.daily-weather {
	font-size: 24rpx;
	font-weight: 600;
	color: var(--text-1);
}

.daily-temp {
	font-size: 22rpx;
	color: var(--text-2);
}

.daily-rain {
	font-size: 20rpx;
	color: var(--info);
}

.weather-advice {
	display: flex;
	align-items: center;
	gap: 10rpx;
	padding: 14rpx 18rpx;
	border-radius: 16rpx;
	background: rgba(217, 161, 30, 0.12);
}

.weather-advice.suitable {
	background: var(--forest-light);
}

.advice-text {
	flex: 1;
	font-size: 23rpx;
	line-height: 1.5;
	color: var(--text-1);
}

/* 快速操作 */
.action-section {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
	padding: 28rpx 28rpx 0;
}

.action-card {
	display: flex;
	align-items: center;
	border-radius: 24rpx;
	padding: 28rpx;
}

.action-card.primary {
	background: var(--brand);
	box-shadow: var(--shadow-brand);
}

.action-card.secondary {
	background: var(--bg-1);
	border: 1rpx solid var(--border);
}

.action-icon {
	width: 88rpx;
	height: 88rpx;
	border-radius: 24rpx;
	background: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	margin-right: 24rpx;
}

.action-icon.light {
	background: var(--forest-light);
}

.action-text {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 6rpx;
}

.action-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #fff;
}

.action-title.dark {
	color: var(--text-1);
}

.action-desc {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.85);
}

.action-desc.dark {
	color: var(--text-3);
}

.action-arrow {
	font-size: 36rpx;
	color: rgba(255, 255, 255, 0.8);
}

.action-arrow.dark {
	color: var(--text-3);
}

/* 最近检测 */
.recent-section {
	padding: 40rpx 28rpx 0;
}

.section-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20rpx;
}

.section-title-wrap {
	display: flex;
	align-items: baseline;
	gap: 12rpx;
}

.section-title {
	font-size: 34rpx;
	font-weight: 700;
	color: var(--text-1);
}

.section-count {
	font-size: 22rpx;
	color: var(--text-3);
}

.view-all {
	font-size: 24rpx;
	color: var(--brand);
	font-weight: 500;
}

.loading-row {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.skeleton-row {
	height: 136rpx;
	border-radius: 20rpx;
	background: linear-gradient(90deg, var(--bg-3) 25%, var(--bg-1) 50%, var(--bg-3) 75%);
	background-size: 200% 100%;
	animation: shimmer 1.6s infinite;
}

@keyframes shimmer {
	to { background-position: -200% 0; }
}

.record-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.record-item {
	display: flex;
	align-items: center;
	background: var(--bg-1);
	border: 1rpx solid var(--border-light);
	border-radius: 20rpx;
	padding: 16rpx;
	transition: transform 0.15s ease;
}

.record-item:active {
	transform: scale(0.99);
}

.record-image {
	width: 112rpx;
	height: 112rpx;
	border-radius: 16rpx;
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--bg-3);
}

.record-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 6rpx;
	padding: 0 20rpx;
	min-width: 0;
}

.record-disease {
	font-size: 28rpx;
	font-weight: 600;
	color: var(--text-1);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.record-time {
	font-size: 22rpx;
	color: var(--text-3);
}

.record-status {
	padding: 8rpx 16rpx;
	border-radius: 999rpx;
	background: rgba(200, 68, 47, 0.1);
	flex-shrink: 0;
}

.record-status.healthy {
	background: var(--forest-light);
}

.status-text {
	font-size: 22rpx;
	font-weight: 600;
	color: var(--brand);
}

.record-status.healthy .status-text {
	color: var(--success);
}
</style>
