from app import db
from datetime import datetime
import uuid

class Template(db.Model):
    __tablename__ = 'templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(10), default='en', nullable=False)
    
    subject = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON, nullable=False, default=lambda: [])
    
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    versions = db.relationship('TemplateVersion', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'notification_type': self.notification_type,
            'language': self.language,
            'subject': self.subject,
            'body': self.body,
            'variables': self.variables,
            'description': self.description,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Template {self.code}>'


class TemplateVersion(db.Model):
    __tablename__ = 'template_versions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('templates.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    
    subject = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), nullable=True)
    change_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'version': self.version,
            'subject': self.subject,
            'body': self.body,
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'change_notes': self.change_notes
        }
    
    def __repr__(self):
        return f'<TemplateVersion {self.template_id} v{self.version}>'