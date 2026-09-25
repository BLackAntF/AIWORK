import csv
import io
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, request, current_app, Response
from models import DetectionHistory, db
from utils.response import success, bad_request, not_found
from middleware.auth_middleware import login_required

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

DATE_FORMAT = '%Y-%m-%d'
EXPORT_HEADERS = ['ID', '文件名', '类型', '检测目标数', '检出病害', '最高置信度',
                  '处理耗时(秒)', '模型版本', '检测时间']


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