import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    avatar = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def set_password(self, password):
        """设置密码（哈希存储）"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'avatar': self.avatar,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_email:
            data['email'] = self.email
        return data


class DetectionHistory(db.Model):
    """检测历史模型"""
    __tablename__ = 'detection_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False, default='image', index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(500), nullable=False)
    result_path = db.Column(db.String(500))
    detection_count = db.Column(db.Integer, default=0)
    detection_result = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    processing_time = db.Column(db.Float)
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('detection_histories', lazy='dynamic'))

    def set_detection_result(self, result_dict):
        """设置检测结果（JSON序列化）"""
        self.detection_result = json.dumps(result_dict, ensure_ascii=False)

    def get_detection_result(self):
        """获取检测结果（JSON反序列化）"""
        if self.detection_result:
            return json.loads(self.detection_result)
        return None

    def to_dict(self, include_detail=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'original_filename': self.original_filename,
            'result_path': self.result_path,
            'detection_count': self.detection_count,
            'file_size': self.file_size,
            'processing_time': self.processing_time,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_detail:
            data['original_path'] = self.original_path
            data['detection_result'] = self.get_detection_result()
        return data


class ChatHistory(db.Model):
    """对话历史模型"""
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_id = db.Column(db.String(50), index=True)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    extra_metadata = db.Column('metadata', db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('chat_histories', lazy='dynamic'))

    def set_metadata(self, meta_dict):
        """设置元数据（JSON序列化）"""
        self.extra_metadata = json.dumps(meta_dict, ensure_ascii=False)

    def get_metadata(self):
        """获取元数据（JSON反序列化）"""
        if self.extra_metadata:
            return json.loads(self.extra_metadata)
        return None

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Knowledge(db.Model):
    """知识库模型"""
    __tablename__ = 'knowledge'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), index=True)
    source = db.Column(db.String(255))
    vector_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'source': self.source,
            'vector_id': self.vector_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'key': self.config_key,
            'value': self.config_value,
            'description': self.description
        }


class ModelInfo(db.Model):
    """模型信息模型"""
    __tablename__ = 'models'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    version = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'version': self.version,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class KnowledgeCategory(db.Model):
    """知识分类模型"""
    __tablename__ = 'knowledge_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
