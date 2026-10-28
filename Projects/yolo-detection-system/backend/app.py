import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException
from config import Config
from extensions import db, jwt, cors
from utils.response import server_error

# SQLite 新增列定义：db.create_all() 不会为已存在的表补列，启动时按需 ALTER
TABLE_NEW_COLUMNS = {
    'disease_profiles': {
        'dosage': 'TEXT',
        'safety_interval': 'VARCHAR(100)',
        'biological_control': 'TEXT'
    },
    'sample_pool': {
        'auto_created': 'BOOLEAN DEFAULT 0'
    }
}


def _migrate_added_columns(app):
    """为已存在的表补齐新增列（幂等）

    Args:
        app: Flask 应用实例（需已有应用上下文）
    """
    with app.app_context():
        if db.engine.dialect.name != 'sqlite':
            return
        for table, columns in TABLE_NEW_COLUMNS.items():
            rows = db.session.execute(db.text(f'PRAGMA table_info({table})')).fetchall()
            existing = {row[1] for row in rows}
            if not existing:
                continue
            for column, ddl in columns.items():
                if column not in existing:
                    db.session.execute(db.text(
                        f'ALTER TABLE {table} ADD COLUMN {column} {ddl}'
                    ))
        db.session.commit()


def create_app(config_class=Config):
    """创建 Flask 应用工厂

    Args:
        config_class: 配置类

    Returns:
        Flask: Flask 应用实例
    """
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_class)

    # 确保必要目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CHROMA_PATH'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['YOLO_MODEL_PATH']), exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    _migrate_added_columns(app)

    # CORS 配置：使用具体的允许来源
    cors_origins = app.config.get('CORS_ORIGINS', 'http://localhost:5173')
    cors.init_app(app, resources={
        r'/api/*': {
            'origins': cors_origins.split(',') if cors_origins else ['http://localhost:5173'],
            'supports_credentials': True,
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization'],
            'expose_headers': ['Content-Disposition']
        }
    })

    # 注册蓝图
    from routes import auth_bp, detection_bp, knowledge_bp, history_bp, health_bp, admin_bp, \
        knowledge_user_bp, disease_bp, notifications_bp, sample_pool_bp, share_bp, weather_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(knowledge_user_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(sample_pool_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(weather_bp)

    # 根路径重定向到健康检查
    @app.route('/')
    def index():
        return {'message': 'YOLO Detection System API', 'status': 'running'}

    # 全局错误处理（使用正确的 HTTP 状态码）
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'code': 404, 'message': '接口不存在', 'data': None}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return server_error()

    @app.errorhandler(Exception)
    def unhandled_exception(exc):
        """兜底处理路由内未捕获的异常，避免其被伪装成 401"""
        if isinstance(exc, HTTPException):
            return jsonify({'code': exc.code, 'message': exc.description, 'data': None}), exc.code
        db.session.rollback()
        app.logger.exception('未捕获的异常')
        return server_error()

    return app


if __name__ == '__main__':
    app = create_app()

    # 确保数据库表已创建
    with app.app_context():
        db.create_all()

    # 启动服务：Debug 模式通过环境变量控制
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug
    )
