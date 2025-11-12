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
            raise ValueError("RABBITMQ_URL environment variable is not set")
        
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchanges and queues
            self.channel.exchange_declare(
                exchange='notifications',
                exchange_type='topic',
                durable=True
            )
            
            self.channel.queue_declare(queue='email_notifications', durable=True)
            self.channel.queue_declare(queue='push_notifications', durable=True)
            
            self.channel.queue_bind(
                exchange='notifications',
                queue='email_notifications',
                routing_key='email.notify'
            )
            self.channel.queue_bind(
                exchange='notifications',
                queue='push_notifications',
                routing_key='push.notify'
            )
            
            logger.info("✅ Connected to CloudAMQP RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            return False
    
    def publish(self, routing_key: str, message: Dict[Any, Any]):
        """Publish message to RabbitMQ"""
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
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

mq = MessageQueue()