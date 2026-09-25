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
    class_names = db.Column(db.String(500), index=True)
    max_confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('detection_histories', lazy='dynamic'))

    def set_detection_result(self, result_dict):
        """设置检测结果（JSON序列化，并同步冗余的筛选字段）

        Args:
            result_dict: 含 detections / total_count / class_summary 的检测结果
        """
        self.detection_result = json.dumps(result_dict, ensure_ascii=False)
        class_summary = result_dict.get('class_summary') or {}
        self.class_names = ','.join(class_summary.keys()) or None
        confidences = [
            det.get('confidence') for det in result_dict.get('detections') or []
            if isinstance(det.get('confidence'), (int, float))
        ]
        self.max_confidence = max(confidences) if confidences else None

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
            'class_names': self.class_names,
            'max_confidence': self.max_confidence,
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
    summary = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active', index=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    tags = db.relationship('Tag', secondary='knowledge_tag', backref='knowledges')
    uploader = db.relationship('User', backref=db.backref('uploaded_knowledges', lazy='dynamic'))

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
            'summary': self.summary,
            'views': self.views,
            'status': self.status,
            'uploader_id': self.uploader_id,
            'uploader_name': self.uploader.username if self.uploader else None,
            'file_path': self.file_path,
            'tags': [tag.to_dict() for tag in self.tags] if self.tags else [],
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


class AdminLog(db.Model):
    """管理端操作日志模型"""
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    username = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False, index=True)
    target_type = db.Column(db.String(50), index=True)
    target_id = db.Column(db.Integer, index=True)
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('admin_logs', lazy='dynamic'))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DiseaseProfile(db.Model):
    """病害档案模型"""
    __tablename__ = 'disease_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_id = db.Column(db.String(50), unique=True, nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, nullable=False)

    causes = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    occurrence = db.Column(db.Text)
    prevention = db.Column(db.Text)
    treatment = db.Column(db.Text)
    pesticides = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'disease_id': self.disease_id,
            'disease_name': self.disease_name,
            'class_id': self.class_id,
            'causes': self.causes,
            'symptoms': self.symptoms,
            'occurrence': self.occurrence,
            'prevention': self.prevention,
            'treatment': self.treatment,
            'pesticides': self.pesticides,
            'is_active': self.is_active
        }


class Tag(db.Model):
    """知识标签模型"""
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), default='primary')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class KnowledgeTag(db.Model):
    """知识-标签关联模型"""
    __tablename__ = 'knowledge_tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), index=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), index=True)

    __table_args__ = (
        db.UniqueConstraint('knowledge_id', 'tag_id', name='uq_knowledge_tag'),
    )


class Notification(db.Model):
    """站内通知模型"""
    __tablename__ = 'notifications'

    TYPE_DETECTION_COMPLETED = 'detection_completed'
    TYPE_KNOWLEDGE_APPROVED = 'knowledge_approved'
    TYPE_KNOWLEDGE_REJECTED = 'knowledge_rejected'
    TYPE_SYSTEM = 'system'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False, index=True)
    related_type = db.Column(db.String(50))
    related_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def to_dict(self) -> dict:
        """转换为字典

        Returns:
            dict: 通知字段字典
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'is_read': self.is_read,
            'related_type': self.related_type,
            'related_id': self.related_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
