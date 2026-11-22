import request from './axios'

export function getWeather(lat, lon) {
  return request.get('/weather', {
    params: { lat, lon },
    skipErrorMessage: true
  })
}
