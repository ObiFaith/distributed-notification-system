import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as amqp from 'amqplib';

@Injectable()
export class RabbitmqService implements OnModuleInit, OnModuleDestroy {
  private connection: amqp.Connection;
  private channel: amqp.Channel;
  private exchange: string;
  private readonly logger = new Logger(RabbitmqService.name);

  constructor(private readonly config: ConfigService) {
    this.exchange = this.config.get('EXCHANGE') || 'notifications.direct';
  }

  // Connect to RabbitMQ when the module initializes
  async onModuleInit() {
    const url = this.config.get('RABBITMQ_URL') || 'amqp://localhost:5672';
    await this.connectWithRetry(url);
  }

  /**
   * 🩵 FIX: Retry connection if RabbitMQ isn't ready yet (ECONNREFUSED)
   */
  private async connectWithRetry(url: string, retries = 5, delay = 5000) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        this.logger.log(`Attempt ${attempt} to connect to RabbitMQ...`);
        this.connection = await amqp.connect(url);
        this.channel = await this.connection.createChannel();

        // Ensure exchange exists (direct)
        await this.channel.assertExchange(this.exchange, 'direct', { durable: true });

        // Ensure queues
        const pushQueue = this.config.get('PUSH_QUEUE') || 'push.queue';
        const retryQueue = this.config.get('RETRY_QUEUE') || 'push.retry.queue';
        const failedQueue = this.config.get('FAILED_QUEUE') || 'push.failed.queue';

        await this.channel.assertQueue(pushQueue, { durable: true });
        await this.channel.assertQueue(retryQueue, { durable: true });
        await this.channel.assertQueue(failedQueue, { durable: true });

        await this.channel.bindQueue(pushQueue, this.exchange, pushQueue);
        await this.channel.bindQueue(retryQueue, this.exchange, retryQueue);
        await this.channel.bindQueue(failedQueue, this.exchange, failedQueue);

        this.logger.log('✅ Connected to RabbitMQ, exchange & queues asserted');
        return; // ✅ success, exit loop
      } catch (error) {
        this.logger.error(`❌ Connection failed (attempt ${attempt}): ${error.message}`);
        if (attempt < retries) {
          this.logger.warn(`Retrying in ${delay / 1000}s...`);
          await new Promise((res) => setTimeout(res, delay));
        } else {
          this.logger.error('❌ Could not connect to RabbitMQ after several attempts.');
          throw error;
        }
      }
    }
  }

  /**
   * 🩵 FIX: Ensure channel exists before consuming or publishing
   */
  private async ensureChannelReady() {
    if (!this.channel) {
      this.logger.warn('⚠️ Channel not ready, waiting 2s...');
      await new Promise((res) => setTimeout(res, 2000));
      if (!this.channel) {
        throw new Error('RabbitMQ channel not initialized');
      }
    }
  }

  // Publish to exchange using routing key (usually equal to queue name)
  async publish(routingKey: string, data: any, options = { persistent: true }) {
    await this.ensureChannelReady(); // ✅ Ensure ready before publishing
    const payload = Buffer.from(JSON.stringify(data));
    this.channel.publish(this.exchange, routingKey, payload, options);
    this.logger.log(`📤 Message published to ${routingKey}`);
  }

  // Consume messages from a queue using a handler
  async consume(queue: string, handler: (msg: amqp.ConsumeMessage) => Promise<void>) {
    await this.ensureChannelReady(); // ✅ Ensure ready before consuming
    await this.channel.consume(
      queue,
      async (msg) => {
        if (!msg) return;
        try {
          await handler(msg);
        } catch (err) {
          this.logger.error(`❌ Error handling message from ${queue}: ${err.message}`);
          this.channel.nack(msg, false, false);
        }
      },
      { noAck: false },
    );
    this.logger.log(`📩 Consuming messages from queue: ${queue}`);
  }

  ack(msg: amqp.ConsumeMessage) {
    this.channel.ack(msg);
  }

  nack(msg: amqp.ConsumeMessage, requeue = false) {
    this.channel.nack(msg, false, requeue);
  }

  async onModuleDestroy() {
    await this.channel?.close();
    await this.connection?.close();
    this.logger.log('🧹 RabbitMQ connection closed');
  }
}
