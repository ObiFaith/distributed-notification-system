import os
import logging
from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the app directly - no waiting needed since Railway manages service readiness
logger.info("🚀 Creating Flask application...")
app = create_app()
logger.info("✅ Application created successfully")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)