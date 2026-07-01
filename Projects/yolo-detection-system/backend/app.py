import os
from flask import Flask, jsonify, send_from_directory
from config import Config
from extensions import db, jwt, cors


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

    # CORS 配置：使用具体的允许来源
    cors_origins = app.config.get('CORS_ORIGINS', 'http://localhost:5173')
    cors.init_app(app, resources={
        r'/api/*': {
            'origins': cors_origins.split(',') if cors_origins else ['http://localhost:5173'],
            'supports_credentials': True,
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization']
        }
    })

    # 注册蓝图
    from routes import auth_bp, detection_bp, knowledge_bp, history_bp, health_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(admin_bp)

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
        return jsonify({'code': 500, 'message': '服务器内部错误', 'data': None}), 500

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
