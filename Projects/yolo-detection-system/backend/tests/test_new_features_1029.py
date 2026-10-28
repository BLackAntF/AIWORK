# -*- coding: utf-8 -*-
"""4 项新功能验证（使用 Flask test_client，不占用 5000 端口）

覆盖：病害防治方案结构化字段 / 低置信度兜底自动进样本池 /
检测结果分享（含过期与无效 token）/ 天气联动（mock 网络 + 缓存 + 降级）。
运行：python backend/tests/test_new_features_1029.py
"""
import base64
import io
import os
import shutil
import sqlite3
import sys
import tempfile

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import requests  # noqa: E402

from app import create_app  # noqa: E402
from config import Config  # noqa: E402
from extensions import db  # noqa: E402

_DB_FD, _DB_PATH = tempfile.mkstemp(suffix='.db')
os.close(_DB_FD)
# 临时目录放在项目所在盘符，避免与 static 目录跨盘导致 relpath 失败
_TMP_DIR = tempfile.mkdtemp(prefix='yolo_test_', dir=os.path.dirname(BACKEND_DIR))

PASSED = []
FAILED = []
_APP = None

LEGACY_DDL = """
CREATE TABLE disease_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  disease_id VARCHAR(50) NOT NULL UNIQUE,
  disease_name VARCHAR(100) NOT NULL,
  class_id INTEGER NOT NULL,
  causes TEXT, symptoms TEXT, occurrence TEXT, prevention TEXT,
  treatment TEXT, pesticides TEXT,
  is_active BOOLEAN, created_at DATETIME, updated_at DATETIME
);
"""


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _DB_PATH.replace('\\', '/')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    YOLO_USE_MOCK = True
    LOW_CONFIDENCE_THRESHOLD = 0.99  # mock 置信度 0.6~0.98，必然触发低置信度
    UPLOAD_FOLDER = os.path.join(_TMP_DIR, 'uploads')
    RESULT_FOLDER = os.path.join(_TMP_DIR, 'results')
    CHROMA_PATH = os.path.join(_TMP_DIR, 'chroma')
    YOLO_MODEL_PATH = os.path.join(_TMP_DIR, 'model', 'best.pt')


def check(name, condition, detail=''):
    if condition:
        PASSED.append(name)
        print(f'[PASS] {name}')
    else:
        FAILED.append(name)
        print(f'[FAIL] {name} {detail}')


def _prepare_legacy_db():
    """构造旧版 disease_profiles 表，验证启动时的加列迁移"""
    with sqlite3.connect(_DB_PATH) as conn:
        conn.executescript(LEGACY_DDL)


def _seed(app):
    """写入管理员与带新字段的病害档案，返回 profile_id"""
    from models import DiseaseProfile, User
    with app.app_context():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('password123')
        profile = DiseaseProfile(
            disease_id='EarlyBlight', disease_name='早疫病', class_id=1,
            causes='真菌引起', symptoms='同心轮纹病斑', occurrence='高温高湿',
            prevention='轮作', treatment='百菌清喷雾', pesticides='75%百菌清',
            dosage='75%百菌清可湿性粉剂 600 倍液，亩用量 60~80kg',
            safety_interval='安全间隔期 7 天，每季最多 3 次',
            biological_control='枯草芽孢杆菌 1000 亿 CFU/g 稀释 800 倍喷施'
        )
        db.session.add_all([admin, profile])
        db.session.commit()
        return profile.id


def _login(client):
    resp = client.post('/api/auth/login', json={'username': 'admin', 'password': 'password123'})
    token = resp.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def _upload(client, headers, save_history=True):
    png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 64
    return client.post('/api/detect/image', data={
        'file': (io.BytesIO(png), 'test_leaf.png'),
        'save_history': 'true' if save_history else 'false'
    }, content_type='multipart/form-data', headers=headers)


def test_disease_fields(client, headers, profile_id):
    """功能1：新字段可读 + 迁移生效 + 管理端可写"""
    with sqlite3.connect(_DB_PATH) as conn:
        columns = {row[1] for row in conn.execute('PRAGMA table_info(disease_profiles)')}
    check('启动迁移补齐 3 个新列',
          {'dosage', 'safety_interval', 'biological_control'} <= columns,
          f'columns={sorted(columns)}')

    resp = client.get('/api/disease-profiles/1', headers=headers)
    data = resp.get_json().get('data') or {}
    check('病害档案读取新字段',
          data.get('dosage') and data.get('safety_interval') and data.get('biological_control'),
          f'data={data}')

    resp = client.put(f'/api/admin/disease-profiles/{profile_id}', json={
        'dosage': '25%嘧菌酯悬浮剂 1500 倍液',
        'safety_interval': '安全间隔期 5 天',
        'biological_control': '木霉菌制剂灌根'
    }, headers=headers)
    updated = resp.get_json().get('data') or {}
    check('管理端可写入新字段',
          resp.get_json().get('code') == 0
          and updated.get('safety_interval') == '安全间隔期 5 天',
          f'resp={resp.get_json()}')


def test_low_confidence(client, headers):
    """功能2：低置信度兜底 + 自动进样本池 + 防重复"""
    from models import SamplePool
    resp = _upload(client, headers)
    data = resp.get_json().get('data') or {}
    check('低置信度场景标记 low_confidence', data.get('low_confidence') is True,
          f'data_keys={list(data)[:8]}')
    check('返回 confidence_threshold', data.get('confidence_threshold') == 0.99,
          f"threshold={data.get('confidence_threshold')}")
    candidates = data.get('top_candidates') or []
    check('top_candidates 为 1~3 个并按置信度降序',
          1 <= len(candidates) <= 3
          and candidates == sorted(candidates, key=lambda c: c['confidence'], reverse=True),
          f'candidates={candidates}')
    check('自动创建样本池 sample_pool_id', isinstance(data.get('sample_pool_id'), int),
          f"pool_id={data.get('sample_pool_id')}")
    check('原有字段保持兼容',
          data.get('success') is True and data.get('id') and 'detections' in data,
          f'data={list(data)[:8]}')
    history_id = data.get('id')

    with _APP.app_context():
        sample = SamplePool.query.filter_by(id=data.get('sample_pool_id')).first()
        check('样本池记录为 uncertain/pending 且关联历史',
              bool(sample) and sample.mark_type == SamplePool.MARK_UNCERTAIN
              and sample.status == SamplePool.STATUS_PENDING
              and sample.history_id == data.get('id'),
              f'sample={sample.to_dict() if sample else None}')
        pool_count = SamplePool.query.filter_by(history_id=data.get('id')).count()
        check('同一历史仅自动采集一次', pool_count == 1, f'count={pool_count}')

    resp = _upload(client, headers, save_history=False)
    data = resp.get_json().get('data') or {}
    check('不保存历史时不写入样本池',
          data.get('low_confidence') is True and data.get('sample_pool_id') is None,
          f"pool_id={data.get('sample_pool_id')}")
    return history_id


def test_share(client, headers, history_id):
    """功能3：分享创建 / 公开访问 / 复用 / 无效与过期 token"""
    from models import ShareLink
    resp = client.post(f'/api/history/{history_id}/share', json={'expires_days': 3},
                       headers=headers)
    data = resp.get_json().get('data') or {}
    token = data.get('token') or ''
    qr = data.get('qr_code') or ''
    check('分享接口返回 token/share_url/expires_at/qr_code',
          resp.get_json().get('code') == 0 and token
          and data.get('share_url', '').endswith(f'/share/{token}')
          and data.get('expires_at'),
          f'data={data}')
    check('qr_code 为 base64 PNG',
          base64.b64decode(qr)[:8] == b'\x89PNG\r\n\x1a\n', f'qr_len={len(qr)}')

    resp2 = client.post(f'/api/history/{history_id}/share', json={}, headers=headers)
    check('未过期分享直接复用 token',
          resp2.get_json()['data']['token'] == token,
          f"token2={resp2.get_json()['data'].get('token')}")

    resp = client.get(f'/api/share/{token}')
    shared = resp.get_json().get('data') or {}
    raw = resp.get_data(as_text=True)
    check('公开访问无需登录且返回只读结果',
          resp.status_code == 200 and shared.get('history', {}).get('id') == history_id
          and isinstance(shared.get('detections'), list),
          f'data={shared}')
    check('公开接口不含 username/email 隐私',
          'username' not in shared.get('history', {}) and 'admin@example.com' not in raw,
          f'raw={raw[:120]}')

    resp = client.get('/api/share/not-exist-token')
    check('无效 token 返回 404 + 中文提示',
          resp.status_code == 404 and '不存在' in (resp.get_json().get('message') or ''),
          f'body={resp.get_data(as_text=True)}')

    app = _APP
    with app.app_context():
        link = ShareLink.query.filter_by(token=token).first()
        link.expires_at = link.expires_at.replace(year=link.expires_at.year - 1)
        db.session.commit()

    resp = client.get(f'/api/share/{token}')
    check('过期 token 返回 410 + 中文提示',
          resp.status_code == 410 and '过期' in (resp.get_json().get('message') or ''),
          f'body={resp.get_data(as_text=True)}')


FAKE_WEATHER = {
    'current': {'temperature_2m': 26.5, 'relative_humidity_2m': 61,
                'precipitation': 0.0, 'weather_code': 1, 'wind_speed_10m': 2.4},
    'daily': {'time': ['2026-10-29', '2026-10-30'],
              'weather_code': [1, 3],
              'temperature_2m_max': [28.0, 27.0],
              'temperature_2m_min': [18.0, 17.5],
              'precipitation_probability_max': [10, 20]}
}

FAKE_RAINY = {
    'current': {'temperature_2m': 22.0, 'relative_humidity_2m': 93,
                'precipitation': 5.2, 'weather_code': 61, 'wind_speed_10m': 2.0},
    'daily': {'time': ['2026-10-29'],
              'weather_code': [61], 'temperature_2m_max': [23.0],
              'temperature_2m_min': [19.0], 'precipitation_probability_max': [85]}
}


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_weather(client):
    """功能4：天气联动（mock 网络 / 缓存 / 参数校验 / 降级）"""
    import routes.weather as weather_module
    original_get = weather_module.requests.get

    resp = client.get('/api/weather?lat=95&lon=114')
    check('非法纬度返回 bad_request',
          resp.get_json().get('code') == 400, f'body={resp.get_data(as_text=True)}')

    weather_module.requests.get = lambda url, params=None, timeout=None: _FakeResponse(FAKE_WEATHER)
    try:
        resp = client.get('/api/weather?lat=30.51&lon=114.31')
        data = resp.get_json().get('data') or {}
        check('天气接口返回 current/daily/advice',
              resp.get_json().get('code') == 0
              and data.get('current', {}).get('temperature') == 26.5
              and isinstance(data.get('daily'), list) and data.get('daily')
              and data.get('advice', {}).get('suitable') is True,
              f'data={data}')

        resp = client.get('/api/weather?lat=30.51&lon=114.31')
        check('30 分钟内命中内存缓存', resp.get_json().get('code') == 0, resp.get_data(as_text=True))
    finally:
        weather_module.requests.get = original_get

    weather_module.requests.get = lambda url, params=None, timeout=None: _FakeResponse(FAKE_RAINY)
    try:
        resp = client.get('/api/weather?lat=40.11&lon=116.41')
        advice = (resp.get_json().get('data') or {}).get('advice') or {}
        check('降水概率 >60% 时不建议施药',
              advice.get('suitable') is False and '降水' in (advice.get('reason') or ''),
              f'advice={advice}')
    finally:
        weather_module.requests.get = original_get

    def _boom(url, params=None, timeout=None):
        raise requests.RequestException('network down')

    weather_module.requests.get = _boom
    try:
        resp = client.get('/api/weather?lat=10.12&lon=20.22')
        check('网络异常优雅降级为 server_error',
              resp.get_json().get('code') == 500
              and resp.get_json().get('message') == '天气服务暂不可用',
              f'body={resp.get_data(as_text=True)}')
    finally:
        weather_module.requests.get = original_get


def main():
    global _APP
    _prepare_legacy_db()
    _APP = create_app(TestConfig)
    with _APP.app_context():
        db.create_all()
    profile_id = _seed(_APP)

    client = _APP.test_client()
    headers = _login(client)

    test_disease_fields(client, headers, profile_id)
    history_id = test_low_confidence(client, headers)
    test_share(client, headers, history_id)
    test_weather(client)

    print(f'\n结果: {len(PASSED)} passed, {len(FAILED)} failed')
    return 1 if FAILED else 0


if __name__ == '__main__':
    exit_code = 1
    try:
        exit_code = main()
    finally:
        if _APP is not None:
            with _APP.app_context():
                db.session.remove()
                db.engine.dispose()
        shutil.rmtree(_TMP_DIR, ignore_errors=True)
        try:
            os.remove(_DB_PATH)
        except OSError:
            pass
    sys.exit(exit_code)
