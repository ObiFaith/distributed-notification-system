import type { Cache } from 'cache-manager';
import { Channel, ConsumeMessage } from 'amqplib';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Inject, Controller, Logger } from '@nestjs/common';
import { Ctx, EventPattern, Payload, RmqContext } from '@nestjs/microservices';

interface EmailJob {
  notification_id: string;
  user_id: string;
  user_email: string;
  template_code: string;
  variables: Record<string, any>;
  request_id: string;
  priority?: number;
  metadata?: Record<string, any>;
}

@Controller()
export class EmailConsumer {
  private readonly logger = new Logger(EmailConsumer.name);

  constructor(@Inject(CACHE_MANAGER) private cache: Cache) {}

  private async simulateEmailSend(job: EmailJob) {
    await new Promise<void>((resolve) => setTimeout(resolve, 1000));
    this.logger.debug(
      `Simulating email send: to=${job.user_email}, template=${job.template_code}`,
    );
  }

  private sendToFailedQueue(channel: Channel, data: EmailJob) {
    try {
      const failedPayload = {
        ...data,
        failed_at: new Date().toISOString(),
      };
      channel.publish(
        'notifications.direct', // exchange
        'failed.queue', // routing key
        Buffer.from(JSON.stringify(failedPayload)),
      );
      this.logger.warn(
        `Sent failed job to DLQ: notification_id=${data.notification_id}`,
      );
    } catch (err) {
      this.logger.error(`Failed to publish to failed.queue: ${err}`);
    }
  }
  @EventPattern('email.notify')
  async handleEmailNotification(
    @Payload() data: EmailJob,
    @Ctx() context: RmqContext,
  ) {
    const channel = context.getChannelRef() as Channel;
    const message = context.getMessage() as ConsumeMessage;

    this.logger.log(`Received email job: ${JSON.stringify(data)}`);

    // Validation
    if (
      !data.notification_id ||
      !data.request_id ||
      !data.user_id ||
      !data.template_code
    ) {
      this.logger.error(`Invalid job payload, missing required fields.`);
      channel.ack(message); // consume message
      this.sendToFailedQueue(channel, data);
      return;
    }

    // Idempotency
    const idempotencyKey = `email:sent:${data.notification_id}`;
    const alreadyProcessed = await this.cache.get(idempotencyKey);
    if (alreadyProcessed) {
      this.logger.warn(
        `Duplicate job detected, skipping notification ${data.notification_id}`,
      );
      channel.ack(message);
      return;
    }

    // Circuit Breaker check
    const circuitKey = 'email:circuit_open';
    const circuitOpen = await this.cache.get(circuitKey);
    if (circuitOpen) {
      this.logger.warn(`Circuit breaker open — temporarily rejecting message`);
      channel.nack(message, false, true); // requeue message
      return;
    }

    try {
      await this.simulateEmailSend(data);

      this.logger.log(`Email sent successfully to ${data.user_email}`);
      await this.cache.set(idempotencyKey, true, 300); // 5 mins TTL

      channel.ack(message);
    } catch (err) {
      const errMessage =
        err instanceof Error ? err.message : JSON.stringify(err);
      this.logger.error(`Failed to process email: ${errMessage}`);

      // Circuit Breaker increment
      const failureKey = 'email:failures';
      const failures = (await this.cache.get(failureKey)) || 0;
      const newCount = (Number(failures) || 0) + 1;
      await this.cache.set(failureKey, newCount, 60); // expire in 60s

      if (newCount >= 5) {
        this.logger.error(
          `⚠️ Too many email failures! Opening circuit for 60 seconds.`,
        );
        await this.cache.set(circuitKey, true, 60);
      }

      // Send to DLQ
      this.sendToFailedQueue(channel, data);

      channel.nack(message, false, false); // remove from queue (goes to DLQ)
    }
  }
}
