import uuid
import datetime as dt
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

def gen_uuid() -> str:
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=gen_uuid)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default="user")  # "user" | "admin"
    push_tokens = db.Column(JSONB, nullable=False, default=list)
    preferences = db.Column(JSONB, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow
    )

    # helpers
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
