import json
from datetime import datetime, date, timedelta
from flask import request
from routes.admin import admin_bp
from models import DetectionHistory, db
from utils.response import success, bad_request, not_found, error
from middleware.auth_middleware import admin_required


@admin_bp.route('/detections/stats', methods=['GET'])
@admin_required
def get_detection_stats(current_user):
    """获取检测统计数据"""
    total = DetectionHistory.query.count()

    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_count = DetectionHistory.query.filter(
        DetectionHistory.created_at >= today_start
    ).count()

    avg_time = db.session.query(db.func.avg(DetectionHistory.processing_time)).scalar() or 0

    category_counts = {}
    all_detections = DetectionHistory.query.all()
    for det in all_detections:
        result = det.get_detection_result()
        if result:
            detections = result.get('detections', [])
            for d in detections:
                label = d.get('label', 'unknown')
                category_counts[label] = category_counts.get(label, 0) + 1

    return success(data={
        'total': total,
        'today': today_count,
        'avg_processing_time': round(float(avg_time), 2),
        'category_distribution': category_counts
    })


@admin_bp.route('/detections', methods=['GET'])
@admin_required
def get_detections(current_user):
    """获取全局检测列表（分页、筛选）

    Query Params:
        page: 页码
        page_size: 每页数量
        user_id: 用户ID筛选
        type: 检测类型 image/video
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    user_id = request.args.get('user_id', '').strip()
    detection_type = request.args.get('type', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = DetectionHistory.query

    if user_id:
        try:
            query = query.filter(DetectionHistory.user_id == int(user_id))
        except ValueError:
            pass

    if detection_type:
        query = query.filter(DetectionHistory.type == detection_type)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(DetectionHistory.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
            query = query.filter(DetectionHistory.created_at < end)
        except ValueError:
            pass

    total = query.count()
    items = query.order_by(DetectionHistory.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return success(data={
        'list': [d.to_dict(include_detail=True) for d in items],
        'total': total,
        'page': page,
        'page_size': page_size
    })


@admin_bp.route('/detections/<int:det_id>', methods=['GET'])
@admin_required
def get_detection_detail(current_user, det_id):
    """获取检测详情"""
    det = DetectionHistory.query.get(det_id)
    if not det:
        return not_found('检测记录不存在')

    return success(data=det.to_dict(include_detail=True))


@admin_bp.route('/detections/<int:det_id>', methods=['DELETE'])
@admin_required
def delete_detection(current_user, det_id):
    """删除检测记录"""
    det = DetectionHistory.query.get(det_id)
    if not det:
        return not_found('检测记录不存在')

    db.session.delete(det)
    db.session.commit()

    return success(message='检测记录已删除')


@admin_bp.route('/detections', methods=['DELETE'])
@admin_required
def batch_delete_detections(current_user):
    """批量删除检测记录

    Body: { ids: [] }
    """
    data = request.get_json() or {}
    ids = data.get('ids', [])

    if not ids or not isinstance(ids, list):
        return bad_request('ids 参数必须为非空数组')

    count = DetectionHistory.query.filter(DetectionHistory.id.in_(ids)).delete(
        synchronize_session=False
    )
    db.session.commit()

    return success(message=f'已删除 {count} 条检测记录')
