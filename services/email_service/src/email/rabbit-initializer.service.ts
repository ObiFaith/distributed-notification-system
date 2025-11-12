// rabbit-initializer-service.ts
import { connect } from 'amqplib';
import { Injectable, OnModuleInit, Logger } from '@nestjs/common';

@Injectable()
export class RabbitInitializer implements OnModuleInit {
  private readonly logger = new Logger(RabbitInitializer.name);

  async onModuleInit() {
    const rabbitMqUrl = process.env.RABBITMQ_URL;

    if (!rabbitMqUrl) {
      throw new Error(
        'RabbitInitializer: RABBITMQ_URL or EMAIL_QUEUE is not defined!',
      );
    }

    const conn = await connect(rabbitMqUrl);
    const channel = await conn.createChannel();

    const emailQueue = process.env.EMAIL_QUEUE;
    const failedQueue = process.env.FAILED_QUEUE;
    const notificationExchange = process.env.NOTIFICATIONS_EXCHANGE;

    if (!notificationExchange || !emailQueue || !failedQueue) {
      throw new Error(
        'RabbitInitializer: NOTIFICATIONS_EXCHANGE, EMAIL_QUEUE or FAILED_QUEUE is not defined!',
      );
    }

    // Declare exchange
    await channel.assertExchange(notificationExchange, 'direct', {
      durable: true,
    });

    // Declare main email queue with DLX
    await channel.assertQueue(emailQueue, {
      durable: true,
      arguments: {
        'x-dead-letter-exchange': notificationExchange,
        'x-dead-letter-routing-key': failedQueue,
      },
    });

    // Declare DLQ
    await channel.assertQueue(failedQueue, { durable: true });

    // Bind main queue to exchange with routing key
    await channel.bindQueue(emailQueue, notificationExchange, 'email.notify');

    // Bind DLQ to exchange
    await channel.bindQueue(failedQueue, notificationExchange, failedQueue);

    await channel.close();
    await conn.close();

    this.logger.log('RabbitMQ queues and bindings initialized');
  }
}
