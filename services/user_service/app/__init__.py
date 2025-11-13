from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
import redis
import logging
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "User Service API",
            "description": "API for managing users and authentication in the HNG Notification System",
            "version": "1.0.0",
            "contact": {
                "name": "HNG Team",
                "url": "https://hng.tech"
            }
        },
        "host": os.getenv("SWAGGER_HOST"),
        "basePath": "/",
        "schemes": ["https"],
        "tags": [
            {
                "name": "Users",
                "description": "User management endpoints"
            },
            {
                "name": "Authentication",
                "description": "Authentication endpoints"
            },
            {
                "name": "Preferences",
                "description": "User preferences endpoints"
            },
            {
                "name": "Health",
                "description": "Service health check"
            }
        ]
    }
    
    # Initialize Swagger
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Redis
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        app.redis = redis.from_url(redis_url)
        app.redis.ping()
        logger.info("✅ Redis connected successfully")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        app.redis = None
    
    # Initialize RabbitMQ
    from app.message_queue import mq
    try:
        mq.connect()
    except Exception as e:
        logger.error(f"❌ RabbitMQ connection failed: {e}")
    
    # Register routes
    with app.app_context():
        from app.routes import register_routes
        register_routes(app)
        
        # Create database tables
        db.create_all()
    
    return app
