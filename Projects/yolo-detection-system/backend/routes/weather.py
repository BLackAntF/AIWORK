import time

import requests
from flask import Blueprint, current_app, request
from utils.response import success, bad_request, server_error

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'
CACHE_TTL_SECONDS = 30 * 60
CACHE_MAX_ENTRIES = 200
_weather_cache = {}

DAILY_FIELDS = ('weather_code', 'temperature_2m_max', 'temperature_2m_min',
                'precipitation_probability_max')


def _parse_lat(raw) -> tuple:
    """解析纬度，需在 -90~90

    Args:
        raw: 请求参数字符串

    Returns:
        tuple: (纬度, 错误消息)
    """
    try:
        lat = float(raw)
    except (TypeError, ValueError):
        return None, 'lat 参数必须为 -90~90 的数字'
    if lat < -90 or lat > 90:
        return None, 'lat 参数必须为 -90~90 的数字'
    return lat, None


def _parse_lon(raw) -> tuple:
    """解析经度，需在 -180~180

    Args:
        raw: 请求参数字符串

    Returns:
        tuple: (经度, 错误消息)
    """
    try:
        lon = float(raw)
    except (TypeError, ValueError):
        return None, 'lon 参数必须为 -180~180 的数字'
    if lon < -180 or lon > 180:
        return None, 'lon 参数必须为 -180~180 的数字'
    return lon, None


def _build_daily(daily_raw: dict) -> list:
    """把 Open-Meteo 的并行数组转换为按天的列表

    Args:
        daily_raw: daily 原始字段

    Returns:
        list: 每天一条天气摘要
    """
    dates = daily_raw.get('time') or []
    rows = []
    for index, date in enumerate(dates):
        row = {'date': date}
        for field in DAILY_FIELDS:
            values = daily_raw.get(field) or []
            row[field] = values[index] if index < len(values) else None
        rows.append(row)
    return rows


def _build_advice(current: dict, daily: list) -> dict:
    """按未来 24 小时降水概率与风速给出施药建议

    Args:
        current: 当前天气
        daily: 逐日天气列表

    Returns:
        dict: {suitable, reason}
    """
    rain = (daily[0].get('precipitation_probability_max') or 0) if daily else 0
    wind = current.get('wind_speed') or 0
    if rain > 60:
        return {'suitable': False, 'reason': f'未来24小时降水概率 {rain}%，建议雨后施药'}
    if wind > 5:
        return {'suitable': False, 'reason': f'当前风速 {wind} m/s 偏大，药液易飘移，不建议施药'}
    return {'suitable': True, 'reason': '未来24小时降水概率低、风力适宜，可安排施药'}


def _normalize_payload(raw: dict) -> dict:
    """将 Open-Meteo 原始响应转换为接口返回结构

    Args:
        raw: Open-Meteo JSON

    Returns:
        dict: {current, daily, advice}
    """
    current_raw = raw.get('current') or {}
    current = {
        'temperature': current_raw.get('temperature_2m'),
        'humidity': current_raw.get('relative_humidity_2m'),
        'precipitation': current_raw.get('precipitation'),
        'weather_code': current_raw.get('weather_code'),
        'wind_speed': current_raw.get('wind_speed_10m')
    }
    daily = _build_daily(raw.get('daily') or {})
    return {'current': current, 'daily': daily, 'advice': _build_advice(current, daily)}


def _fetch_weather(lat: float, lon: float) -> dict:
    """请求 Open-Meteo 预报接口

    Args:
        lat: 纬度
        lon: 经度

    Returns:
        dict: 原始 JSON
    """
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
        'daily': ','.join(DAILY_FIELDS),
        'timezone': 'auto',
        'forecast_days': 5
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=8)
    response.raise_for_status()
    return response.json()


def _load_weather(lat: float, lon: float) -> tuple:
    """带 30 分钟内存缓存地获取天气数据

    Args:
        lat: 纬度
        lon: 经度

    Returns:
        tuple: (数据, 错误消息)
    """
    key = f'{lat:.2f},{lon:.2f}'
    cached = _weather_cache.get(key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1], None

    try:
        payload = _normalize_payload(_fetch_weather(lat, lon))
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        current_app.logger.warning('天气服务请求失败: %s', exc)
        return None, '天气服务暂不可用'

    if len(_weather_cache) >= CACHE_MAX_ENTRIES:
        _weather_cache.clear()
    _weather_cache[key] = (time.time(), payload)
    return payload, None


@weather_bp.route('', methods=['GET'])
def get_weather():
    """根据经纬度获取天气与施药建议（公开接口）

    Query:
        lat: 纬度 -90~90
        lon: 经度 -180~180
    """
    lat, error_message = _parse_lat(request.args.get('lat'))
    if error_message:
        return bad_request(error_message)

    lon, error_message = _parse_lon(request.args.get('lon'))
    if error_message:
        return bad_request(error_message)

    payload, error_message = _load_weather(lat, lon)
    if error_message:
        return server_error(error_message)

    return success(data=payload)
