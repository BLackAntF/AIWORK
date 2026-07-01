from datetime import datetime
from flask import Blueprint
from utils.response import success

health_bp = Blueprint('health', __name__, url_prefix='/api')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return success(data={
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
