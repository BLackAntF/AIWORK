import csv
import io
import os
import zipfile
from datetime import datetime

from flask import request, Response, current_app
from models import SamplePool, Notification, db
from utils.response import success, bad_request, not_found
from utils.file_utils import url_to_fs_path
from utils.audit import log_admin_action
from middleware.auth_middleware import admin_required
from routes.admin import admin_bp


@admin_bp.route('/sample-pool', methods=['GET'])
@admin_required
def list_sample_pool(current_user):
    """样本池列表（审核视图）"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    status = request.args.get('status', '').strip()

    query = SamplePool.query
    if status:
        if status not in SamplePool.STATUSES:
            return bad_request('status 参数非法')
        query = query.filter(SamplePool.status == status)

    pagination = query.order_by(SamplePool.created_at.desc()) \
        .paginate(page=page, per_page=page_size, error_out=False)

    stats = {
        'pending': SamplePool.query.filter_by(status=SamplePool.STATUS_PENDING).count(),
        'approved': SamplePool.query.filter_by(status=SamplePool.STATUS_APPROVED).count(),
        'rejected': SamplePool.query.filter_by(status=SamplePool.STATUS_REJECTED).count(),
    }

    return success(data={
        'list': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size,
        'stats': stats
    })


@admin_bp.route('/sample-pool/<int:sample_id>/review', methods=['PUT'])
@admin_required
def review_sample(current_user, sample_id):
    """审核样本反馈（approved / rejected），结果以站内通知告知提交者"""
    data = request.get_json() or {}
    status = data.get('status', '').strip()
    review_note = data.get('review_note', '').strip()

    if status not in (SamplePool.STATUS_APPROVED, SamplePool.STATUS_REJECTED):
        return bad_request('status 必须为 approved/rejected')

    sample = SamplePool.query.get(sample_id)
    if not sample:
        return not_found('样本反馈不存在')
    if sample.status == status:
        return bad_request('该样本已处于该状态')

    sample.status = status
    sample.review_note = review_note or None
    sample.reviewed_by = current_user.id
    sample.reviewed_at = datetime.utcnow()
    db.session.commit()

    if status == SamplePool.STATUS_APPROVED:
        title = '样本反馈已通过审核'
        content = f'您提交的样本反馈 #{sample.id} 已通过审核并纳入训练数据池，感谢协助改进模型！'
    else:
        title = '样本反馈未通过审核'
        content = f'您提交的样本反馈 #{sample.id} 未通过审核。' + (f'原因：{review_note}' if review_note else '')

    db.session.add(Notification(
        user_id=sample.user_id,
        type=Notification.TYPE_SYSTEM,
        title=title,
        content=content,
        related_type='sample_pool',
        related_id=sample.id
    ))
    db.session.commit()

    log_admin_action(
        user_id=current_user.id,
        username=current_user.username,
        action='review_sample',
        target_type='sample_pool',
        target_id=sample.id,
        detail=f'{status} {sample.mark_type} predicted={sample.predicted_class} corrected={sample.corrected_class}'
    )

    return success(data=sample.to_dict(), message='审核完成')


@admin_bp.route('/sample-pool/export', methods=['GET'])
@admin_required
def export_sample_pool(current_user):
    """导出已审核样本为训练数据包（zip）

    结构：
        images/<类别名>/xxx.jpg   按"最终类别"归档（纠错样本用 corrected_class，
                                  正确样本用 predicted_class；漏检/不确定归入 _need_label）
        metadata.csv              样本明细（含预测/纠正类别、置信度、反馈人）
        README.txt                数据包说明
    """
    samples = SamplePool.query.filter_by(status=SamplePool.STATUS_APPROVED) \
        .order_by(SamplePool.created_at.desc()).all()

    zip_buffer = io.BytesIO()
    exported = 0
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        meta_rows = [['sample_id', 'final_class', 'predicted_class',
                      'corrected_class', 'mark_type', 'confidence', 'username', 'created_at']]
        for s in samples:
            if s.mark_type == SamplePool.MARK_MISCLASSIFIED and s.corrected_class:
                final_class = s.corrected_class
            elif s.mark_type == SamplePool.MARK_CORRECT and s.predicted_class:
                final_class = s.predicted_class
            else:
                # missed / uncertain 无可靠类别标签，归入待人工标注目录
                final_class = '_need_label'

            # image_path 存的是 /static 相对 URL，需还原为磁盘路径
            static_dir = os.path.join(current_app.root_path, 'static')
            src = url_to_fs_path(s.image_path, static_dir)
            if src and os.path.exists(src):
                ext = os.path.splitext(src)[1].lower() or '.jpg'
                arcname = f'images/{final_class}/sample_{s.id}{ext}'
                zf.write(src, arcname)
                exported += 1
            else:
                arcname = '(源文件缺失)'

            meta_rows.append([
                s.id, final_class, s.predicted_class or '',
                s.corrected_class or '', s.mark_type,
                s.predicted_confidence if s.predicted_confidence is not None else '',
                s.user.username if s.user else '',
                s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else ''
            ])

        meta_buf = io.StringIO()
        csv.writer(meta_buf).writerows(meta_rows)
        zf.writestr('metadata.csv', meta_buf.getvalue().encode('utf-8-sig'))

        zf.writestr('README.txt', (
            '番茄病害检测 - 增量训练样本数据包\n'
            f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'样本数量: {exported}\n\n'
            '说明:\n'
            '1. images/<类别名>/ 按最终类别归档；纠错样本使用人工纠正类别，\n'
            '   正确样本使用模型预测类别。\n'
            '2. _need_label/ 为漏检与不确定样本，需人工确认类别后再入库。\n'
            '3. 图片无检测框标注；用于目标检测训练时请先用标注工具\n'
            '   （如 LabelImg / X-AnyLabeling）生成 YOLO txt 标签。\n'
            '4. metadata.csv 含每张图的预测/纠正类别与置信度，可辅助标注。\n'
        ).encode('utf-8'))

    zip_buffer.seek(0)
    filename = f'training_pool_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
