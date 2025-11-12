import os
import logging
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("🚀 Creating Template Service application...")
app = create_app()
logger.info("✅ Template Service created successfully")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    logger.info(f"🚀 Starting Template Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)