<template>
  <section class="weather-card glass-card" aria-label="天气与施药建议">
    <div v-if="loading" class="weather-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在获取天气与施药建议...</span>
    </div>
    <div v-else-if="errorMessage" class="weather-state weather-error">
      <el-icon><Warning /></el-icon>
      <span>{{ errorMessage }}</span>
      <el-button link type="primary" @click="loadWeather">重新获取</el-button>
    </div>
    <template v-else-if="weather">
      <div class="weather-header">
        <div class="weather-heading">
          <el-icon :size="24"><Sunny /></el-icon>
          <div>
            <h2>{{ weatherText(weather.current?.weather_code) }} {{ temperatureText(weather.current?.temperature) }}</h2>
            <p>{{ usingDefaultLocation ? '默认位置：北京' : '当前位置' }} · 实时天气</p>
          </div>
        </div>
        <el-button link :icon="RefreshRight" title="刷新天气" @click="loadWeather" />
      </div>

      <div class="weather-metrics">
        <span>湿度 {{ weather.current?.humidity ?? '—' }}%</span>
        <span>风速 {{ weather.current?.wind_speed ?? '—' }} m/s</span>
        <span>降水 {{ weather.current?.precipitation ?? 0 }} mm</span>
      </div>

      <div v-if="forecastDays.length" class="forecast-list">
        <div v-for="day in forecastDays" :key="day.date" class="forecast-item">
          <span class="forecast-date">{{ formatDay(day.date) }}</span>
          <span>{{ weatherText(day.weather_code) }}</span>
          <strong>{{ temperatureRange(day) }}</strong>
          <span class="rain-text">降水 {{ day.precipitation_probability_max ?? 0 }}%</span>
        </div>
      </div>

      <div v-if="weather.advice" class="advice" :class="{ suitable: weather.advice.suitable }">
        <el-icon><CircleCheck v-if="weather.advice.suitable" /><Warning v-else /></el-icon>
        <div>
          <strong>{{ weather.advice.suitable ? '近期适宜施药' : '建议暂缓施药' }}</strong>
          <p>{{ weather.advice.reason }}</p>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { CircleCheck, Loading, RefreshRight, Sunny, Warning } from '@element-plus/icons-vue'
import { getWeather } from '@/api/weather'

const DEFAULT_LOCATION = { lat: 39.9042, lon: 116.4074 }
const weather = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const usingDefaultLocation = ref(false)
const forecastDays = computed(() => (weather.value?.daily || []).slice(0, 3))

function resolveLocation() {
  return new Promise((resolve) => {
    const useDefault = () => {
      usingDefaultLocation.value = true
      resolve(DEFAULT_LOCATION)
    }
    if (!navigator.geolocation) {
      useDefault()
      return
    }
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        usingDefaultLocation.value = false
        resolve({ lat: coords.latitude, lon: coords.longitude })
      },
      useDefault,
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 30 * 60 * 1000 }
    )
  })
}

async function loadWeather() {
  if (loading.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const location = await resolveLocation()
    weather.value = await getWeather(location.lat, location.lon)
  } catch (error) {
    weather.value = null
    errorMessage.value = error?.response?.data?.message || '天气服务暂不可用，不影响图片检测'
  } finally {
    loading.value = false
  }
}

function weatherText(code) {
  if (code === 0) return '晴'
  if (code >= 1 && code <= 3) return '多云'
  if (code === 45 || code === 48) return '雾'
  if (code >= 51 && code <= 67) return '雨'
  if (code >= 71 && code <= 77) return '雪'
  if (code >= 80 && code <= 82) return '阵雨'
  if (code >= 95 && code <= 99) return '雷雨'
  return '天气未知'
}

function temperatureText(value) {
  return typeof value === 'number' ? `${Math.round(value)}°C` : '—'
}

function temperatureRange(day) {
  const min = typeof day.temperature_2m_min === 'number' ? Math.round(day.temperature_2m_min) : '—'
  const max = typeof day.temperature_2m_max === 'number' ? Math.round(day.temperature_2m_max) : '—'
  return `${min}~${max}°`
}

function formatDay(value) {
  if (!value) return '—'
  const date = new Date(`${value}T00:00:00`)
  const today = new Date()
  const tomorrow = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1)
  if (date.toDateString() === today.toDateString()) return '今天'
  if (date.toDateString() === tomorrow.toDateString()) return '明天'
  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(loadWeather)
</script>

<style scoped>
.weather-card {
  margin-bottom: 20px;
  padding: 20px 24px;
}

.weather-state {
  min-height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--color-text-secondary);
}

.weather-error {
  color: var(--color-warning);
}

.weather-header,
.weather-heading,
.weather-metrics,
.advice {
  display: flex;
  align-items: center;
}

.weather-header {
  justify-content: space-between;
}

.weather-heading {
  gap: 12px;
  color: var(--color-accent);
}

.weather-heading h2 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: 20px;
}

.weather-heading p,
.advice p {
  margin: 4px 0 0;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.weather-metrics {
  flex-wrap: wrap;
  gap: 24px;
  margin: 16px 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.forecast-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.forecast-item {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 12px;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: 13px;
}

.forecast-item strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.forecast-date,
.rain-text {
  color: var(--color-text-tertiary);
}

.advice {
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(217, 161, 30, 0.12);
  color: var(--color-warning);
}

.advice.suitable {
  background: rgba(58, 125, 85, 0.1);
  color: var(--color-forest);
}

@media (max-width: 768px) {
  .weather-card {
    padding: 16px;
  }

  .forecast-list {
    grid-template-columns: 1fr;
  }

  .weather-metrics {
    gap: 12px;
  }
}
</style>
