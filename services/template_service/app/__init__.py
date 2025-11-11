import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    # extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)

    # blueprints
    from .routes.templates import bp as templates_bp
    app.register_blueprint(templates_bp)

    # health endpoint (for k8s/compose readiness)
    @app.get("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "ok", "dependencies": {"db": "ok"}}), 200
        except Exception:
            return jsonify({"status": "degraded", "dependencies": {"db": "down"}}), 503

    return app
