from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
import os
import logging

db = SQLAlchemy()
migrate = Migrate()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    from config import Config
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Redis
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.redis = redis.from_url(redis_url)
    logger.info("✅ Redis connected successfully")
    
    # Initialize RabbitMQ
    try:
        from app.message_queue import mq
        mq.connect()
    except Exception as e:
        logger.warning(f"⚠️  RabbitMQ not connected: {e}")
    
    # Register routes
    from app.routes import register_routes
    register_routes(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        from app.models import User
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(name='Admin User', email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("✅ Admin user created: admin@example.com")
    
    return app