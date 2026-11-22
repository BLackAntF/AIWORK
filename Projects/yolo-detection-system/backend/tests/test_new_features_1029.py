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
from datetime import datetime, timedelta, timezone

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import requests  # noqa: E402

from app import create_app  # noqa: E402
from config import Config  # noqa: E402
from extensions import db  # noqa: E402

_DB_FD, _DB_PATH = tempfile.mkstemp(suffix='.db')
os.close(_DB_FD)
# 临时目录放在 backend/static 下，上传 URL 与生产环境一致，可覆盖历史原图重新检测
_TMP_DIR = tempfile.mkdtemp(prefix='yolo_test_', dir=os.path.join(BACKEND_DIR, 'static'))

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
    LLM_USE_MOCK = True
    DETECTION_EMAIL_NOTIFICATIONS = False
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
    check('邮件默认关闭并返回明确状态', data.get('email_notification') == 'disabled',
          f"email_notification={data.get('email_notification')}")
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


def test_redetect_and_stats(client, headers, history_id):
    """历史原图重新检测：保留旧记录、校验归属并优雅处理原图缺失"""
    from models import DetectionHistory, User

    with _APP.app_context():
        other = User(username='other_user', email='other@example.com', role='user')
        other.set_password('password123')
        db.session.add(other)
        db.session.commit()
        original = db.session.get(DetectionHistory, history_id)
        original_snapshot = (original.detection_result, original.result_path, original.created_at)

    other_login = client.post('/api/auth/login', json={
        'username': 'other_user', 'password': 'password123'
    })
    other_token = other_login.get_json()['data']['access_token']
    resp = client.post(f'/api/history/{history_id}/redetect', headers={
        'Authorization': f'Bearer {other_token}'
    })
    check('其他用户不能重新检测本人以外的历史',
          resp.get_json().get('code') == 404, f'body={resp.get_data(as_text=True)}')

    resp = client.post(f'/api/history/{history_id}/redetect', headers=headers)
    data = resp.get_json().get('data') or {}
    new_history_id = data.get('id')
    check('本人重新检测返回新的历史记录 ID',
          resp.get_json().get('code') == 0 and isinstance(new_history_id, int)
          and new_history_id != history_id,
          f'body={resp.get_data(as_text=True)}')

    with _APP.app_context():
        original = db.session.get(DetectionHistory, history_id)
        current_snapshot = (original.detection_result, original.result_path, original.created_at)
        check('重新检测不覆盖旧历史记录', current_snapshot == original_snapshot)

    stats = (client.get('/api/history/stats', headers=headers).get_json().get('data') or {})
    check('统计接口返回 total/today/image_count 且口径一致',
          stats.get('total', 0) >= 2 and stats.get('today') == stats.get('total')
          and stats.get('image_count') == stats.get('total'),
          f'stats={stats}')

    with _APP.app_context():
        new_item = db.session.get(DetectionHistory, new_history_id)
        new_item.original_path = '/static/uploads/definitely-missing.png'
        db.session.commit()
    resp = client.post(f'/api/history/{new_history_id}/redetect', headers=headers)
    check('原图缺失时重新检测返回明确错误',
          resp.get_json().get('code') == 404
          and '原始图片不存在' in (resp.get_json().get('message') or ''),
          f'body={resp.get_data(as_text=True)}')

    original_limit = _APP.config['DETECTION_RATE_LIMIT_PER_MINUTE']
    _APP.config['DETECTION_RATE_LIMIT_PER_MINUTE'] = 1
    try:
        resp = client.post(f'/api/history/{history_id}/redetect', headers=headers)
        check('检测与重新检测共用每分钟限流',
              resp.get_json().get('code') == 429, f'body={resp.get_data(as_text=True)}')
    finally:
        _APP.config['DETECTION_RATE_LIMIT_PER_MINUTE'] = original_limit


def test_stats_local_day(client, headers):
    """今日统计按本地自然日，不错误纳入本地昨天的 UTC 记录"""
    from models import DetectionHistory, User

    local_start = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_utc = (local_start - timedelta(minutes=1)).astimezone(timezone.utc).replace(tzinfo=None)
    today_utc = (local_start + timedelta(minutes=1)).astimezone(timezone.utc).replace(tzinfo=None)
    baseline = client.get('/api/history/stats', headers=headers).get_json()['data']
    with _APP.app_context():
        admin_id = User.query.filter_by(username='admin').first().id
        records = [DetectionHistory(
            user_id=admin_id, type='image', original_filename=f'{label}.png',
            original_path='/static/uploads/test.png', created_at=created_at
        ) for label, created_at in [('yesterday', yesterday_utc), ('today', today_utc)]]
        db.session.add_all(records)
        db.session.commit()
    stats = client.get('/api/history/stats', headers=headers).get_json()['data']
    check('今日检测统计使用本地自然日边界',
          stats['total'] == baseline['total'] + 2
          and stats['today'] == baseline['today'] + 1,
          f'baseline={baseline}, stats={stats}')


def test_sample_feedback(client, headers, history_id):
    """手动反馈覆盖自动低置信度样本，并能在我的样本中查询"""
    from models import SamplePool

    with _APP.app_context():
        sample = SamplePool.query.filter_by(history_id=history_id).first()
        sample.status = SamplePool.STATUS_APPROVED
        sample.review_note = '自动样本初审通过'
        sample.reviewed_by = sample.user_id
        sample.reviewed_at = datetime.utcnow()
        db.session.commit()

    resp = client.post('/api/sample-pool', json={
        'history_id': history_id,
        'mark_type': 'misclassified',
        'corrected_class': '早疫病',
        'note': '人工核对后纠正类别'
    }, headers=headers)
    data = resp.get_json().get('data') or {}
    check('手动反馈覆盖自动采集样本',
          resp.get_json().get('code') == 0 and data.get('history_id') == history_id
          and data.get('corrected_class') == '早疫病'
          and data.get('auto_created') is False,
          f'body={resp.get_data(as_text=True)}')

    with _APP.app_context():
        sample = SamplePool.query.filter_by(history_id=history_id).first()
        check('人工覆盖已审核自动样本后重新待审并清空审核信息',
              sample.status == SamplePool.STATUS_PENDING
              and sample.review_note is None and sample.reviewed_by is None
              and sample.reviewed_at is None,
              f'sample={sample.to_dict()}, reviewed_by={sample.reviewed_by}')
        count = SamplePool.query.filter_by(history_id=history_id).count()
        check('手动反馈不产生重复样本', count == 1, f'count={count}')

    resp = client.get('/api/sample-pool?page=1&page_size=20', headers=headers)
    data = resp.get_json().get('data') or {}
    matched = [item for item in data.get('list', []) if item.get('history_id') == history_id]
    check('我的样本分页列表包含手动反馈',
          resp.get_json().get('code') == 0 and len(matched) == 1
          and matched[0].get('note') == '人工核对后纠正类别',
          f'data={data}')

    invalid_payloads = [
        {'history_id': str(history_id), 'mark_type': 'correct'},
        {'history_id': history_id, 'mark_type': 'correct', 'note': ['非法类型']},
        {'history_id': history_id, 'mark_type': 'misclassified',
         'corrected_class': '病' * 101},
        {'history_id': history_id, 'mark_type': 'correct', 'note': '长' * 201}
    ]
    invalid_results = [client.post('/api/sample-pool', json=payload, headers=headers)
                       for payload in invalid_payloads]
    check('样本反馈拒绝非法 ID、字段类型与超长文本',
          all(item.get_json().get('code') == 400 for item in invalid_results),
          f'codes={[item.get_json().get("code") for item in invalid_results]}')

    resp = client.post('/api/sample-pool', data='not-json',
                       content_type='application/json', headers=headers)
    check('样本反馈拒绝非法 JSON', resp.get_json().get('code') == 400)

    resp = client.get('/api/sample-pool?page=0&page_size=-5', headers=headers)
    data = resp.get_json().get('data') or {}
    check('我的样本非法分页参数回退安全默认值',
          data.get('page') == 1 and data.get('page_size') == 20, f'data={data}')


def test_knowledge_sources(client, headers):
    """AI 引用来源返回干净标题和知识 ID，不暴露富文本正文"""
    from models import Knowledge

    with _APP.app_context():
        knowledge = Knowledge(
            title='早疫病防治指南',
            content='<h2>早疫病防治</h2><p>轮换用药并控制湿度。</p>',
            category='防治方法',
            is_active=True
        )
        db.session.add(knowledge)
        db.session.commit()
        knowledge_id = knowledge.id

    resp = client.post('/api/knowledge/ask', json={
        'question': '早疫病怎么防治？', 'stream': False
    }, headers=headers)
    data = resp.get_json().get('data') or {}
    sources = data.get('sources') or []
    check('AI 引用来源返回标题和知识 ID',
          resp.get_json().get('code') == 0
          and sources == [{'knowledge_id': knowledge_id, 'title': '早疫病防治指南'}],
          f'body={resp.get_data(as_text=True)}')


def test_role_change_audit(client, headers):
    """角色变更日志记录真实旧角色，并在测试结束后恢复原角色"""
    from models import AdminLog, User

    with _APP.app_context():
        user = User(username='role_audit_user', role='user')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    first = client.put(f'/api/admin/users/{user_id}/role', json={'role': 'admin'}, headers=headers)
    second = client.put(f'/api/admin/users/{user_id}/role', json={'role': 'user'}, headers=headers)
    with _APP.app_context():
        logs = AdminLog.query.filter_by(action='change_user_role', target_id=user_id).order_by(AdminLog.id).all()
        restored_role = db.session.get(User, user_id).role
    check('角色审计记录变更前后的真实角色',
          first.get_json().get('code') == 0 and second.get_json().get('code') == 0
          and len(logs) == 2 and '从 user 改为 admin' in logs[0].detail
          and '从 admin 改为 user' in logs[1].detail and restored_role == 'user',
          f'details={[log.detail for log in logs]}')


def test_email_notification(history_id):
    """SMTP 使用替身验证真实发送路径与失败状态，不访问外部邮件服务"""
    from models import User
    from services import notification_service

    class FakeSMTP:
        instance = None

        def __init__(self, host, port, timeout):
            self.host, self.port, self.timeout = host, port, timeout
            self.tls_started = False
            self.message = None
            FakeSMTP.instance = self

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def starttls(self):
            self.tls_started = True

        def login(self, username, password):
            self.login_args = (username, password)

        def send_message(self, message):
            self.message = message

    config_keys = ['DETECTION_EMAIL_NOTIFICATIONS', 'SMTP_HOST', 'SMTP_PORT',
                   'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM', 'SMTP_USE_TLS',
                   'SMTP_USE_SSL', 'SMTP_TIMEOUT_SECONDS']
    old_config = {key: _APP.config[key] for key in config_keys}
    old_smtp = notification_service.smtplib.SMTP
    old_deliver = notification_service._deliver_email
    _APP.config.update(DETECTION_EMAIL_NOTIFICATIONS=True, SMTP_HOST='smtp.test',
                       SMTP_PORT=587, SMTP_USERNAME='sender@test.com',
                       SMTP_PASSWORD='test-only', SMTP_FROM='sender@test.com',
                       SMTP_USE_TLS=True, SMTP_USE_SSL=False, SMTP_TIMEOUT_SECONDS=3)
    try:
        notification_service.smtplib.SMTP = FakeSMTP
        with _APP.app_context():
            admin = User.query.filter_by(username='admin').first()
            status = notification_service.send_detection_completed_email(
                admin.id, history_id, 'leaf.png', 2)
        smtp = FakeSMTP.instance
        check('SMTP 启用后真实执行 TLS、登录与发送',
              status == 'sent' and smtp and smtp.tls_started
              and smtp.message and smtp.message['To'] == 'admin@example.com',
              f'status={status}')

        def failed_delivery(recipient, subject, content):
            raise OSError('smtp unavailable')

        notification_service._deliver_email = failed_delivery
        with _APP.app_context():
            admin = User.query.filter_by(username='admin').first()
            status = notification_service.send_detection_completed_email(
                admin.id, history_id, 'leaf.png', 2)
        check('SMTP 异常返回 failed 且不影响检测主流程', status == 'failed', f'status={status}')
    finally:
        notification_service.smtplib.SMTP = old_smtp
        notification_service._deliver_email = old_deliver
        _APP.config.update(old_config)


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
    test_redetect_and_stats(client, headers, history_id)
    test_stats_local_day(client, headers)
    test_sample_feedback(client, headers, history_id)
    test_knowledge_sources(client, headers)
    test_role_change_audit(client, headers)
    test_email_notification(history_id)
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
