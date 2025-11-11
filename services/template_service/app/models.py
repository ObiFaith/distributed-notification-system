import uuid
import datetime as dt
from sqlalchemy.dialects.postgresql import JSONB
from . import db

def gen_uuid() -> str:
    return str(uuid.uuid4())

class Template(db.Model):
    __tablename__ = "templates"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    code = db.Column(db.String, nullable=False, index=True)      # e.g., "welcome_email"
    language = db.Column(db.String, nullable=False, default="en") # ISO code
    version = db.Column(db.Integer, nullable=False, default=1)
    subject = db.Column(db.Text)                                  # email-specific (optional)
    body_html = db.Column(db.Text)
    body_text = db.Column(db.Text)
    meta = db.Column(JSONB, nullable=False, default=dict)         # e.g., {"channels":["email","push"]}
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("code", "language", "version", name="uq_template_code_lang_version"),
    )
