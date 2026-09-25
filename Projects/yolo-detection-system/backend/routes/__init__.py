from .auth import auth_bp
from .detection import detection_bp
from .knowledge import knowledge_bp
from .history import history_bp
from .health import health_bp
from .admin import admin_bp
from .knowledge_user import knowledge_user_bp
from .disease import disease_bp
from .notifications import notifications_bp

__all__ = ['auth_bp', 'detection_bp', 'knowledge_bp', 'history_bp', 'health_bp', 'admin_bp',
           'knowledge_user_bp', 'disease_bp', 'notifications_bp']