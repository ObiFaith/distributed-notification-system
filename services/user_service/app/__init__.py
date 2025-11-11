# app/__init__.py
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    # extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # blueprints
    from .routes.users import bp as users_bp
    from .routes.auth import bp as auth_bp
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)

    # health endpoint
    @app.get("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "ok", "dependencies": {"db": "ok"}}), 200
        except Exception:
            return jsonify({"status": "degraded", "dependencies": {"db": "down"}}), 503

    # declare RabbitMQ topology once (non-fatal if broker is down)
    try:
        from .rabbit_topology import ensure_topology
        ensure_topology()
    except Exception as e:
        app.logger.warning(f"RabbitMQ topology setup skipped/failed: {e}")

    return app
