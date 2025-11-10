import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const logger = new Logger('RabbitMQ');
  const rabbitMqUrl = process.env.RABBITMQ_URL;
  const emailQueue = process.env.EMAIL_QUEUE;

  if (!rabbitMqUrl || !emailQueue) {
    throw new Error('RABBITMQ_URL or EMAIL_QUEUE is not defined in .env');
  }

  const app = await NestFactory.createMicroservice<MicroserviceOptions>(
    AppModule,
    {
      transport: Transport.RMQ,
      options: {
        urls: [rabbitMqUrl],
        queue: emailQueue,
        queueOptions: { durable: true },
      },
    },
  );

  try {
    await app.listen();
    logger.log('RabbitMQ connected and Email Service is listening...');
  } catch (error) {
    logger.error('RabbitMQ connection failed!', error);
    process.exit(1);
  }
}

bootstrap();
