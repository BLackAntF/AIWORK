import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 判断是否为生产环境
IS_PRODUCTION = os.environ.get('FLASK_ENV', 'development') == 'production'


def _get_secret_key(key_name, default_value):
    """获取密钥，生产环境强制要求设置"""
    value = os.environ.get(key_name)
    if IS_PRODUCTION and not value:
        raise RuntimeError(f'{key_name} environment variable is required in production')
    return value or default_value


class Config:
    # 安全密钥（生产环境必须通过环境变量设置）
    SECRET_KEY = _get_secret_key('SECRET_KEY', 'dev-secret-key-yolo-detection')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 密钥（生产环境必须通过环境变量设置）
    JWT_SECRET_KEY = _get_secret_key('JWT_SECRET_KEY', 'dev-jwt-secret-key-yolo')
    JWT_ACCESS_TOKEN_EXPIRES = 86400

    # CORS 允许的来源（生产环境应配置具体域名）
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, 'static', 'results')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

    YOLO_MODEL_PATH = os.path.join(BASE_DIR, 'data', 'model', 'best.pt')
    YOLO_CONF_THRESHOLD = 0.5
    YOLO_IOU_THRESHOLD = 0.45
    YOLO_USE_MOCK = True

    LLM_API_KEY = os.environ.get('LLM_API_KEY') or ''
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL') or ''
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'qwen-turbo'
    LLM_USE_MOCK = True

    CHROMA_PATH = os.path.join(BASE_DIR, 'data', 'chroma')
    CHROMA_COLLECTION = 'knowledge'
