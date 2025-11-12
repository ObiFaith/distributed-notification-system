import pika
import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self):
        # Get from environment variable (CloudAMQP URL)
        self.rabbitmq_url = os.getenv('RABBITMQ_URL')
        if not self.rabbitmq_url:
            logger.warning("⚠️ RABBITMQ_URL environment variable is not set")
            self.rabbitmq_url = None
        
        self.connection = None
        self.channel = None
        self.connected = False
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        if not self.rabbitmq_url:
            logger.warning("⚠️ RabbitMQ URL not configured, skipping connection")
            return False
            
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            parameters.socket_timeout = 5
            parameters.connection_attempts = 3
            parameters.retry_delay = 2
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchanges and queues
            self.channel.exchange_declare(
                exchange='notifications',
                exchange_type='topic',
                durable=True
            )
            
            self.channel.queue_declare(queue='email.queue', durable=True)
            self.channel.queue_declare(queue='push.queue', durable=True)
            
            self.channel.queue_bind(
                exchange='notifications.direct',
                queue='email.queue',
                routing_key='email.notify'
            )
            self.channel.queue_bind(
                exchange='notifications.direct',
                queue='push.queue',
                routing_key='push.notify'
            )
            
            self.connected = True
            logger.info("✅ Connected to CloudAMQP RabbitMQ")
            return True
        except pika.exceptions.ProbableAuthenticationError as e:
            logger.error(f"❌ RabbitMQ Authentication Failed: {e}")
            logger.error("⚠️ Please verify your CloudAMQP credentials in .env file")
            logger.warning("📝 Service will continue without message queue - notifications won't be sent")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            logger.warning("📝 Service will continue without message queue")
            self.connected = False
            return False
    
    def publish(self, routing_key: str, message: Dict[Any, Any]):
        """Publish message to RabbitMQ"""
        if not self.connected:
            logger.warning(f"⚠️ RabbitMQ not connected, message not sent: {routing_key}")
            return False
            
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            if not self.connected:
                return False
            
            self.channel.basic_publish(
                exchange='notifications',
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            logger.info(f"📤 Published message to {routing_key}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to publish message: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
            self.connected = False

mq = MessageQueue()