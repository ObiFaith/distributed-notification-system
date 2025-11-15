import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { RabbitmqService } from '../rabbitmq/rabbitmq.service';
import { ConfigService } from '@nestjs/config';
import { FcmService } from '../fcm/fcm.service';
import { IdempotencyService } from '../idempotency/idempotency.service';
import * as amqp from 'amqplib';
import { default as axios } from 'axios';
import * as admin from 'firebase-admin';

@Injectable()
export class PushService implements OnModuleInit {
  private readonly logger = new Logger(PushService.name);
  private pushQueue: string;
  private retryQueue: string;
  private failedQueue: string;
  private maxRetry: number;

  constructor(
    private readonly rabbit: RabbitmqService,
    private readonly config: ConfigService,
    private readonly fcm: FcmService,
    private readonly idempotency: IdempotencyService,
  ) {
    this.pushQueue = this.config.get('PUSH_QUEUE') || 'push.queue';
    this.retryQueue = this.config.get('RETRY_QUEUE') || 'push.retry.queue';
    this.failedQueue = this.config.get('FAILED_QUEUE') || 'push.failed.queue';
    this.maxRetry = parseInt(this.config.get('MAX_RETRY', '3'), 10);
  }

  async onModuleInit() {
  // Wait until the RabbitMQ channel is ready
  while (!this.rabbit['channel']) {
    this.logger.log('Waiting for RabbitMQ channel to be ready...');
    await new Promise((resolve) => setTimeout(resolve, 500)); // wait 500ms
  }

  // start consuming push and retry queues
  await this.rabbit.consume(this.pushQueue, (msg) => this.handleMessage(msg));
  await this.rabbit.consume(this.retryQueue, (msg) => this.handleMessage(msg));

  this.logger.log(`Started consuming ${this.pushQueue} and ${this.retryQueue}`);
}

  // Handler for messages from push & retry queues
  async handleMessage(msg: amqp.ConsumeMessage) {
    const content = msg.content.toString();
    let payload: any;

    try {
      payload = JSON.parse(content);
    } catch (err) {
      this.logger.error('Invalid JSON payload, sending to failed queue', err);
      this.rabbit.ack(msg);
      await this.rabbit.publish(this.failedQueue, { error: 'invalid_json', raw: content });
      return;
    }

    const request_id = payload.request_id;
    const attempts = payload.attempts || 0;

    // Idempotency check
    const reserved = await this.idempotency.reserve(request_id, 60 * 60);
    if (!reserved) {
      this.logger.warn(`Duplicate request detected ${request_id}. Acking message.`);
      this.rabbit.ack(msg);
      return;
    }

    // Ensure push token
    let push_token = payload.push_token;
    if (!push_token && payload.user_id) {
      try {
        const userServiceUrl =
          `${this.config.get('USER_SERVICE_URL') || 'http://user-service:3001'}/api/v1/users/${payload.user_id}`;
        const res = await axios.get(userServiceUrl, { timeout: 3000 });
        push_token = res.data?.push_token;
      } catch (err) {
        this.logger.error('Failed to fetch user token', err.message || err);
      }
    }

    if (!push_token) {
      this.logger.error(`No push token for request ${request_id}. Moving to failed queue.`);
      this.rabbit.ack(msg);
      await this.rabbit.publish(this.failedQueue, { ...payload, error: 'no_push_token' });
      return;
    }

    // Prepare FCM payload
    const fcmMessage: admin.messaging.Message = {
      token: push_token, // REQUIRED by Firebase Admin
      notification: {
        title: payload.variables?.title || payload.metadata?.title || 'Notification',
        body: payload.variables?.message || payload.metadata?.message || 'You have a new notification',
      },
      data: payload.variables?.meta || payload.metadata?.meta || {},
    };

    // Send via FCM
    const fcmResult = await this.fcm.sendToDevice(fcmMessage);
    if (fcmResult.success) {
      this.logger.log(`Push delivered for ${request_id}: ${fcmResult.message_id}`);
      this.rabbit.ack(msg);

      // Publish delivered status
      await this.rabbit.publish('notification.status.queue', {
        notification_id: request_id,
        status: 'delivered',
        message_id: fcmResult.message_id,
        timestamp: new Date().toISOString(),
      });
    } else {
      this.logger.warn(`Push send failed for ${request_id}. attempt ${attempts}`);
      this.rabbit.ack(msg);

      if (attempts + 1 <= this.maxRetry) {
        const nextAttempt = attempts + 1;
        const delayMs = this.calculateDelay(nextAttempt);

        // Schedule retry
        setTimeout(async () => {
          await this.rabbit.publish(this.retryQueue, { ...payload, attempts: nextAttempt });
        }, delayMs);

        this.logger.log(`Scheduled retry ${nextAttempt} for ${request_id} after ${delayMs}ms`);
      } else {
        // Move to failed queue
        await this.rabbit.publish(this.failedQueue, { ...payload, error: fcmResult.error || 'send_failed' });
        this.logger.error(`Exceeded retries for ${request_id}, moved to failed queue`);
      }
    }
  }

  // Exponential backoff: 1s, 2s, 4s, 8s...
  calculateDelay(attempt: number) {
    const base = 1000;
    return base * Math.pow(2, attempt - 1);
  }

  // Direct test send (bypassing RabbitMQ)
  async sendDirect(body: any) {
    const dummyMsg = {
      ...body,
      request_id: body.request_id || `direct-${Date.now()}`,
    };

    // Idempotency check
    const reserved = await this.idempotency.reserve(dummyMsg.request_id, 60 * 60);
    if (!reserved) return { success: false, message: 'duplicate_request' };

    const push_token = dummyMsg.device_token || dummyMsg.push_token;
    if (!push_token) return { success: false, message: 'no_device_token' };

    const fcmMessage: admin.messaging.Message = {
      token: push_token,
      notification: {
        title: dummyMsg.title || 'Test',
        body: dummyMsg.message || 'Test message',
      },
      data: dummyMsg.data || {},
    };

    const res = await this.fcm.sendToDevice(fcmMessage);
    if (res.success) return { success: true, data: { message_id: res.message_id || res } };
    return { success: false, error: res.error };
  }
}
