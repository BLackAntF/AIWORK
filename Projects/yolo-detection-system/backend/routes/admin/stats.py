import csv
import io
from collections import defaultdict
from datetime import datetime, date, timedelta
from flask import request, Response
from routes.admin import admin_bp
from models import User, DetectionHistory, ChatHistory, Knowledge, db
from utils.response import success, bad_request, error
from middleware.auth_middleware import admin_required

NON_DISEASE_CLASSES = {'健康', '健康叶片', '健康叶子', '正常叶片'}

# 旧版数据集的类别别名归一化到当前名称，避免同一病害在统计中被拆成多项
CLASS_ALIASES = {
    '斑点病': '细菌性斑点病'
}


@admin_bp.route('/stats/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats(current_user):
    """综合统计看板（用户、检测、知识库、对话总数）"""
    total_users = User.query.count()
    total_detections = DetectionHistory.query.count()
    total_knowledge = Knowledge.query.filter_by(is_active=True).count()
    total_chats = ChatHistory.query.count()

    # 今日数据
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    today_users = User.query.filter(User.created_at >= today_start).count()
    today_detections = DetectionHistory.query.filter(
        DetectionHistory.created_at >= today_start
    ).count()
    today_chats = ChatHistory.query.filter(
        ChatHistory.created_at >= today_start
    ).count()

    return success(data={
        'total_users': total_users,
        'total_detections': total_detections,
        'total_knowledge': total_knowledge,
        'total_chats': total_chats,
        'today_users': today_users,
        'today_detections': today_detections,
        'today_chats': today_chats
    })


@admin_bp.route('/stats/users-trend', methods=['GET'])
@admin_required
def get_users_trend(current_user):
    """用户增长趋势

    Query Params:
        days: 天数，默认 7
    """
    days = int(request.args.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    today = date.today()
    trend = []
    cumulative = 0

    for i in range(days - 1, -1, -1):
        current_date = today - timedelta(days=i)
        date_start = datetime.combine(current_date, datetime.min.time())
        date_end = date_start + timedelta(days=1)

        day_count = User.query.filter(
            User.created_at >= date_start,
            User.created_at < date_end
        ).count()

        cumulative += day_count
        trend.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': day_count,
            'cumulative': cumulative
        })

    return success(data={
        'days': days,
        'trend': trend
    })


@admin_bp.route('/stats/detections-trend', methods=['GET'])
@admin_required
def get_detections_trend(current_user):
    """检测量趋势

    Query Params:
        days: 天数，默认 7
    """
    days = int(request.args.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    today = date.today()
    trend = []

    for i in range(days - 1, -1, -1):
        current_date = today - timedelta(days=i)
        date_start = datetime.combine(current_date, datetime.min.time())
        date_end = date_start + timedelta(days=1)

        day_count = DetectionHistory.query.filter(
            DetectionHistory.created_at >= date_start,
            DetectionHistory.created_at < date_end
        ).count()

        trend.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': day_count
        })

    return success(data={
        'days': days,
        'trend': trend
    })


@admin_bp.route('/stats/knowledge', methods=['GET'])
@admin_required
def get_knowledge_stats(current_user):
    """知识库统计（按分类分布）"""
    total = Knowledge.query.filter_by(is_active=True).count()

    # 按分类统计
    category_stats = {}
    results = db.session.query(
        Knowledge.category,
        db.func.count(Knowledge.id)
    ).filter(
        Knowledge.is_active == True
    ).group_by(Knowledge.category).all()

    for cat, count in results:
        name = cat if cat else '未分类'
        category_stats[name] = count

    return success(data={
        'total': total,
        'category_distribution': category_stats
    })


@admin_bp.route('/stats/disease-distribution', methods=['GET'])
@admin_required
def get_disease_distribution(current_user):
    """病害检出分布统计

    Query Params:
        days: 统计近 N 天（含今天），默认 30
    """
    days = int(request.args.get('days', 30))
    if days < 1:
        days = 30
    if days > 365:
        days = 365

    since = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())

    records = db.session.query(
        DetectionHistory.class_names
    ).filter(
        DetectionHistory.created_at >= since,
        DetectionHistory.class_names.isnot(None),
        DetectionHistory.class_names != ''
    ).all()

    distribution = defaultdict(int)
    for (class_names,) in records:
        for name in class_names.split(','):
            name = name.strip()
            if name and name not in NON_DISEASE_CLASSES:
                distribution[CLASS_ALIASES.get(name, name)] += 1

    total_records = len(records)
    return success(data={
        'days': days,
        'total_records': total_records,
        'distribution': dict(sorted(distribution.items(), key=lambda x: -x[1]))
    })


@admin_bp.route('/stats/disease-trend', methods=['GET'])
@admin_required
def get_disease_trend(current_user):
    """近 N 日病害检出趋势

    Query Params:
        days: 天数，默认 7
    """
    days = int(request.args.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    today = date.today()
    since = datetime.combine(today - timedelta(days=days - 1), datetime.min.time())

    records = db.session.query(
        DetectionHistory.class_names,
        DetectionHistory.created_at
    ).filter(
        DetectionHistory.created_at >= since,
        DetectionHistory.class_names.isnot(None),
        DetectionHistory.class_names != ''
    ).all()

    by_day = defaultdict(lambda: defaultdict(int))
    for class_names, created_at in records:
        day_key = created_at.date().strftime('%Y-%m-%d')
        for name in class_names.split(','):
            name = name.strip()
            if name and name not in NON_DISEASE_CLASSES:
                by_day[day_key][CLASS_ALIASES.get(name, name)] += 1

    dates = []
    for i in range(days - 1, -1, -1):
        dates.append((today - timedelta(days=i)).strftime('%Y-%m-%d'))

    all_names = set()
    for day_dist in by_day.values():
        all_names.update(day_dist.keys())

    series_map = defaultdict(list)
    for d in dates:
        day_dist = by_day.get(d, {})
        for name in all_names:
            series_map[name].append(day_dist.get(name, 0))

    series = [
        {'name': name, 'data': counts}
        for name, counts in series_map.items()
    ]

    return success(data={
        'days': days,
        'dates': dates,
        'series': series
    })


@admin_bp.route('/stats/export', methods=['GET'])
@admin_required
def export_stats(current_user):
    """导出报表 CSV

    Query Params:
        type: users/detections/all
    """
    export_type = request.args.get('type', 'all').strip()

    if export_type not in ('users', 'detections', 'all'):
        return bad_request('type 参数必须为 users/detections/all')

    output = io.StringIO()
    writer = csv.writer(output)

    if export_type in ('users', 'all'):
        writer.writerow(['=== 用户数据 ==='])
        writer.writerow(['ID', '用户名', '邮箱', '角色', '状态', '注册时间'])
        users = User.query.order_by(User.created_at.desc()).all()
        for u in users:
            writer.writerow([
                u.id,
                u.username,
                u.email or '',
                u.role,
                '启用' if u.is_active else '禁用',
                u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else ''
            ])
        writer.writerow([])

    if export_type in ('detections', 'all'):
        writer.writerow(['=== 检测数据 ==='])
        writer.writerow(['ID', '用户ID', '类型', '处理时间(ms)', '检测目标数', '检测时间'])
        dets = DetectionHistory.query.order_by(DetectionHistory.created_at.desc()).all()
        for d in dets:
            obj_count = 0
            result = d.get_detection_result()
            if result:
                obj_count = len(result.get('detections', []))
            writer.writerow([
                d.id,
                d.user_id,
                d.type,
                d.processing_time or 0,
                obj_count,
                d.created_at.strftime('%Y-%m-%d %H:%M:%S') if d.created_at else ''
            ])

    csv_content = output.getvalue()
    output.close()

    filename = f"export_{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_content.encode('utf-8-sig'),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )
