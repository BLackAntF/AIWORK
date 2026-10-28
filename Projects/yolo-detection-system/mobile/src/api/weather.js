/**
 * 天气接口
 */
import { request } from './request'

/** 按经纬度获取天气与施药建议（公开接口，失败静默） */
export function getWeather(lat, lon) {
  return request({ url: '/weather', data: { lat, lon }, silent: true })
}
