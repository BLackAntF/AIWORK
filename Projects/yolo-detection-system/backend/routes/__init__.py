from .auth import auth_bp
from .detection import detection_bp
from .knowledge import knowledge_bp
from .history import history_bp
from .health import health_bp
from .admin import admin_bp

__all__ = ['auth_bp', 'detection_bp', 'knowledge_bp', 'history_bp', 'health_bp', 'admin_bp']
