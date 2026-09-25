import csv
import io
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, request, current_app, Response
from markupsafe import escape
from models import DetectionHistory, DiseaseProfile, db
from utils.response import success, bad_request, not_found
from middleware.auth_middleware import login_required

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

DATE_FORMAT = '%Y-%m-%d'
EXPORT_HEADERS = ['ID', '文件名', '类型', '检测目标数', '检出病害', '最高置信度',
                  '处理耗时(秒)', '模型版本', '检测时间']

HEALTHY_CLASS_NAMES = {'健康', '健康叶片', '健康叶子', '正常叶片', 'Healthy'}

REPORT_PAGE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif; background: #f5f6f8; color: #2d3436; line-height: 1.6; }
.page { max-width: 900px; margin: 24px auto; padding: 0 16px; }
.report-header { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #e07a5f, #c96247); color: #fff; border-radius: 12px; padding: 24px 28px; margin-bottom: 20px; }
.report-header h1 { font-size: 22px; }
.report-header .subtitle { opacity: .85; font-size: 13px; margin-top: 4px; }
.print-btn { background: rgba(255,255,255,.22); color: #fff; border: 1px solid rgba(255,255,255,.6); padding: 8px 18px; border-radius: 8px; cursor: pointer; font-size: 14px; }
.print-btn:hover { background: rgba(255,255,255,.34); }
.card { background: #fff; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.card h2 { font-size: 16px; color: #c96247; border-left: 4px solid #e07a5f; padding-left: 10px; margin-bottom: 14px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
.info-table th { width: 150px; text-align: left; color: #636e72; font-weight: 500; background: #fafafa; }
.info-table th, .info-table td { padding: 8px 12px; border-bottom: 1px solid #f0f0f0; }
.detail-table th { background: #fafafa; color: #636e72; }
.detail-table th, .detail-table td { padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; }
.figures { display: flex; gap: 16px; flex-wrap: wrap; }
.report-figure { flex: 1; min-width: 280px; }
.report-figure img { width: 100%; border-radius: 8px; border: 1px solid #eee; background: #fafafa; }
.report-figure figcaption { text-align: center; color: #636e72; font-size: 13px; margin-top: 6px; }
.conf-bar { width: 110px; height: 8px; border-radius: 4px; background: #f0f0f0; display: inline-block; vertical-align: middle; margin-left: 8px; }
.conf-bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #f29780, #e07a5f); }
.tag { display: inline-block; padding: 2px 10px; border-radius: 10px; font-size: 12px; }
.tag-disease { background: #ffe3e0; color: #c96247; }
.tag-healthy { background: #e8f7ee; color: #2e9e5b; }
.profile-card { border: 1px solid #eee; border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; }
.profile-card h3 { color: #c96247; margin-bottom: 10px; }
.profile-card dl { display: grid; grid-template-columns: 90px 1fr; gap: 6px 12px; font-size: 14px; }
.profile-card dt { color: #636e72; }
.profile-card dd { word-break: break-word; }
.muted { color: #b2bec3; }
.report-footer { text-align: center; color: #636e72; font-size: 13px; padding: 8px 0 24px; }
@media print {
  body { background: #fff; }
  .page { max-width: none; margin: 0; }
  .print-btn { display: none; }
  .card { box-shadow: none; border: 1px solid #eee; }
  .report-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


def _parse_date_range(start_date: Optional[str],
                      end_date: Optional[str]) -> tuple:
    """解析日期范围，end_date 含当天

    Args:
        start_date: 起始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD

    Returns:
        tuple: (start, end, 错误消息)
    """
    start = end = None
    if start_date:
        try:
            start = datetime.strptime(start_date, DATE_FORMAT)
        except ValueError:
            return None, None, 'start_date 格式应为 YYYY-MM-DD'
    if end_date:
        try:
            end = datetime.strptime(end_date, DATE_FORMAT) + timedelta(days=1)
        except ValueError:
            return None, None, 'end_date 格式应为 YYYY-MM-DD'
    return start, end, None


def _parse_confidence(value: Optional[str]) -> tuple:
    """解析最低置信度

    Args:
        value: 置信度字符串

    Returns:
        tuple: (threshold, 错误消息)
    """
    if not value:
        return None, None
    try:
        threshold = float(value)
    except (TypeError, ValueError):
        return None, 'min_confidence 必须为 0~1 的数字'
    if threshold < 0 or threshold > 1:
        return None, 'min_confidence 必须为 0~1 的数字'
    return threshold, None


def _parse_filters() -> tuple:
    """解析列表与导出共用的筛选参数

    Returns:
        tuple: (filters 字典, 错误消息)
    """
    start, end, date_error = _parse_date_range(
        request.args.get('start_date', '').strip() or None,
        request.args.get('end_date', '').strip() or None
    )
    if date_error:
        return None, date_error

    threshold, conf_error = _parse_confidence(
        request.args.get('min_confidence', '').strip() or None
    )
    if conf_error:
        return None, conf_error

    return {
        'type': request.args.get('type', '').strip() or None,
        'keyword': request.args.get('keyword', '').strip() or None,
        'class_name': request.args.get('class_name', '').strip() or None,
        'model_version': request.args.get('model_version', '').strip() or None,
        'start': start,
        'end': end,
        'min_confidence': threshold
    }, None


def _build_history_query(user_id: int, filters: dict):
    """按筛选条件构建历史查询

    Args:
        user_id: 当前用户 ID
        filters: 归一化后的筛选条件

    Returns:
        Query: 已应用全部筛选条件的查询对象
    """
    query = DetectionHistory.query.filter(DetectionHistory.user_id == user_id)
    if filters['type'] in ('image', 'video'):
        query = query.filter(DetectionHistory.type == filters['type'])
    if filters['keyword']:
        # contains() 由 ORM 生成参数化的 LIKE，避免 SQL 注入且兼容 SQLite
        query = query.filter(
            DetectionHistory.original_filename.contains(filters['keyword'])
        )
    if filters['class_name']:
        query = query.filter(DetectionHistory.class_names.contains(filters['class_name']))
    if filters['model_version']:
        query = query.filter(DetectionHistory.model_version == filters['model_version'])
    if filters['start']:
        query = query.filter(DetectionHistory.created_at >= filters['start'])
    if filters['end']:
        query = query.filter(DetectionHistory.created_at < filters['end'])
    if filters['min_confidence'] is not None:
        query = query.filter(DetectionHistory.max_confidence >= filters['min_confidence'])
    return query


@history_bp.route('', methods=['GET'])
@login_required
def get_history_list(current_user):
    """获取检测历史列表

    Query:
        type / keyword / page / page_size
        start_date / end_date: YYYY-MM-DD，按检测时间范围筛选
        class_name: 按检出病害名称模糊匹配
        min_confidence: 最低置信度 0~1
        model_version: 按模型版本精确匹配
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10

    filters, error_message = _parse_filters()
    if error_message:
        return bad_request(error_message)

    query = _build_history_query(current_user.id, filters)
    total = query.count()
    items = query.order_by(DetectionHistory.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [item.to_dict(include_detail=False) for item in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@history_bp.route('/export', methods=['GET'])
@login_required
def export_history(current_user):
    """按同一套筛选条件导出检测历史 CSV（utf-8-sig，Excel 直接打开不乱码）

    Query: 与列表接口一致
    """
    filters, error_message = _parse_filters()
    if error_message:
        return bad_request(error_message)

    max_rows = current_app.config['EXPORT_MAX_ROWS']
    items = _build_history_query(current_user.id, filters) \
        .order_by(DetectionHistory.created_at.desc()) \
        .limit(max_rows) \
        .all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(EXPORT_HEADERS)
    for item in items:
        writer.writerow([
            item.id,
            item.original_filename,
            item.type,
            item.detection_count or 0,
            item.class_names or '',
            item.max_confidence if item.max_confidence is not None else '',
            item.processing_time if item.processing_time is not None else 0,
            item.model_version or '',
            item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else ''
        ])

    csv_content = output.getvalue()
    output.close()

    filename = f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_content.encode('utf-8-sig'),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@history_bp.route('/<int:history_id>', methods=['GET'])
@login_required
def get_history_detail(current_user, history_id):
    """获取单条历史详情"""
    item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first()

    if not item:
        return not_found('记录不存在')

    return success(data=item.to_dict(include_detail=True))


def _render_history_report(item: DetectionHistory) -> str:
    """渲染单条检测记录的报告 HTML（自包含，可直接打印/另存为 PDF）

    Args:
        item: 检测历史记录

    Returns:
        str: 完整 HTML 文档
    """
    result = item.get_detection_result() or {}
    detections = result.get('detections') or []
    created_text = item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '-'
    generated_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    profile_by_class_id = {}
    for det in detections:
        cls_id = det.get('class_id')
        if cls_id is None or cls_id in profile_by_class_id:
            continue
        profile = DiseaseProfile.query.filter_by(class_id=cls_id, is_active=True).first()
        if profile:
            profile_by_class_id[cls_id] = profile

    info_rows = [
        ('报告编号', f'RPT-{item.id:06d}'),
        ('原始文件名', item.original_filename or '-'),
        ('检测时间', created_text),
        ('检测目标数', str(item.detection_count or 0)),
        ('检出病害', (item.class_names or '无').replace(',', '、')),
        ('最高置信度', f'{item.max_confidence * 100:.1f}%' if item.max_confidence is not None else '-'),
        ('处理耗时', f'{item.processing_time:.2f} 秒' if item.processing_time is not None else '-'),
        ('模型版本', item.model_version or '-'),
        ('报告生成时间', generated_text)
    ]
    info_html = ''.join(
        f'<tr><th>{escape(key)}</th><td>{escape(value)}</td></tr>'
        for key, value in info_rows
    )

    figures_html = ''
    if item.original_path:
        figures_html += (
            f'<figure class="report-figure"><img src="{escape(item.original_path)}" alt="原始图片">'
            '<figcaption>原始图片</figcaption></figure>'
        )
    if item.result_path:
        figures_html += (
            f'<figure class="report-figure"><img src="{escape(item.result_path)}" alt="检测结果图">'
            '<figcaption>检测结果图</figcaption></figure>'
        )

    detail_rows = []
    for index, det in enumerate(detections, start=1):
        cls_name = det.get('class_name') or '未知'
        conf = det.get('confidence')
        if isinstance(conf, (int, float)):
            conf_text = f'{conf * 100:.1f}%'
            bar_html = (
                f'<div class="conf-bar"><div class="conf-bar-fill" '
                f'style="width:{min(conf, 1.0) * 100:.1f}%"></div></div>'
            )
        else:
            conf_text = '-'
            bar_html = '<div class="conf-bar"></div>'
        area = det.get('area_ratio')
        area_text = f'{area * 100:.1f}%' if isinstance(area, (int, float)) else '—'
        tag_html = (
            '<span class="tag tag-healthy">健康</span>'
            if cls_name in HEALTHY_CLASS_NAMES
            else '<span class="tag tag-disease">病害</span>'
        )
        profile_text = '有' if det.get('class_id') in profile_by_class_id else '—'
        detail_rows.append(
            f'<tr><td>{index}</td><td>{escape(cls_name)}</td><td>{tag_html}</td>'
            f'<td>{conf_text}{bar_html}</td><td>{area_text}</td><td>{profile_text}</td></tr>'
        )
    detail_body = '\n'.join(detail_rows) or '<tr><td colspan="6" class="muted">未检出目标</td></tr>'

    profiles_html = ''
    for profile in profile_by_class_id.values():
        profiles_html += f'''
        <div class="profile-card">
          <h3>{escape(profile.disease_name)}</h3>
          <dl>
            <dt>诱因</dt><dd>{escape(profile.causes or '-')}</dd>
            <dt>典型症状</dt><dd>{escape(profile.symptoms or '-')}</dd>
            <dt>预防措施</dt><dd>{escape(profile.prevention or '-')}</dd>
            <dt>治疗方案</dt><dd>{escape(profile.treatment or '-')}</dd>
            <dt>推荐药剂</dt><dd>{escape(profile.pesticides or '-')}</dd>
          </dl>
        </div>'''
    profiles_block = profiles_html or '<p class="muted">未检出病害，无需防治建议。</p>'

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>检测报告 RPT-{item.id:06d} - 番茄卫士</title>
<style>
{REPORT_PAGE_CSS}
</style>
</head>
<body>
<div class="page">
  <header class="report-header">
    <div>
      <h1>番茄卫士 · 目标检测报告</h1>
      <p class="subtitle">检测报告 RPT-{item.id:06d} · {created_text}</p>
    </div>
    <button class="print-btn" onclick="window.print()">打印 / 另存为 PDF</button>
  </header>

  <section class="card">
    <h2>一、检测信息</h2>
    <table class="info-table">
      {info_html}
    </table>
  </section>

  <section class="card">
    <h2>二、检测图像</h2>
    <div class="figures">
      {figures_html or '<p class="muted">无图像</p>'}
    </div>
  </section>

  <section class="card">
    <h2>三、检测明细</h2>
    <table class="detail-table">
      <thead>
        <tr><th>#</th><th>目标</th><th>类型</th><th>置信度</th><th>占比</th><th>档案</th></tr>
      </thead>
      <tbody>
        {detail_body}
      </tbody>
    </table>
  </section>

  <section class="card">
    <h2>四、防治建议参考</h2>
    {profiles_block}
  </section>

  <footer class="report-footer">
    <p>本报告由番茄卫士系统自动生成 · {generated_text}</p>
    <p class="muted">防治建议仅供参考，具体用药请遵医嘱，必要时建议咨询当地植保站。</p>
  </footer>
</div>
</body>
</html>'''


@history_bp.route('/<int:history_id>/report', methods=['GET'])
@login_required
def get_history_report(current_user, history_id):
    """生成单条检测记录的 HTML 报告（自包含，可直接打印/另存为 PDF）"""
    item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first()

    if not item:
        return not_found('记录不存在')

    html = _render_history_report(item)
    filename = f'detection_report_{history_id}.html'
    return Response(
        html,
        mimetype='text/html',
        headers={'Content-Disposition': f'inline; filename="{filename}"'}
    )


@history_bp.route('/<int:history_id>', methods=['DELETE'])
@login_required
def delete_history(current_user, history_id):
    """删除单条历史记录"""
    item = DetectionHistory.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first()

    if not item:
        return not_found('记录不存在')

    db.session.delete(item)
    db.session.commit()

    return success(message='删除成功')


@history_bp.route('', methods=['DELETE'])
@login_required
def batch_delete_history(current_user):
    """批量删除历史记录"""
    data = request.get_json() or {}
    ids = data.get('ids', [])

    if not ids or not isinstance(ids, list):
        return bad_request('请提供要删除的记录ID列表')

    deleted = DetectionHistory.query.filter(
        DetectionHistory.id.in_(ids),
        DetectionHistory.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.session.commit()

    return success(message='批量删除成功', data={'deleted_count': deleted})