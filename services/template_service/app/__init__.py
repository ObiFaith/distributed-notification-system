from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
import os
import logging

db = SQLAlchemy()
migrate = Migrate()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    from config import Config
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    app.redis = redis.from_url(redis_url)
    logger.info("✅ Redis connected successfully")
    
    # Initialize RabbitMQ
    try:
        from app.message_queue import mq
        mq.connect()
    except Exception as e:
        logger.warning(f"⚠️  RabbitMQ not connected: {e}")
    
    from app.routes import register_routes
    register_routes(app)
    
    with app.app_context():
        db.create_all()
    
    return app