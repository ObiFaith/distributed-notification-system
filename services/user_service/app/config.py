import os
from datetime import timedelta

class Config:
    def __call__(self):
        return self

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@postgres:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Auth / Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    PASSWORD_HASH_SCHEME = os.getenv("PASSWORD_HASH_SCHEME", "bcrypt")

    # App
    JSON_SORT_KEYS = False
