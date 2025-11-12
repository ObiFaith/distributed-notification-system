import os
import time
import logging
from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_services():
    """Wait for database and redis to be ready"""
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            # Try to create app (which will connect to DB and Redis)
            app = create_app()
            logger.info("✅ All services ready!")
            return app
        except Exception as e:
            logger.warning(f"⏳ Waiting for services... ({i+1}/{max_retries})")
            logger.debug(f"Error: {e}")
            time.sleep(retry_interval)
    
    raise Exception("❌ Failed to connect to services after maximum retries")

app = wait_for_services()

if __name__ == '__main__':
    app = wait_for_services()
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"🚀 Starting User Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)