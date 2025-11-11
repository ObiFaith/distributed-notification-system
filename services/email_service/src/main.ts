import { AppModule } from './app.module';
import { NestFactory } from '@nestjs/core';
import { Logger, ValidationPipe } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';

async function bootstrap() {
  const port = process.env.PORT || 3000;
  const logger = new Logger('Bootstrap');
  const emailQueue = process.env.EMAIL_QUEUE;
  const rabbitMqUrl = process.env.RABBITMQ_URL;
  const failedQueue = process.env.FAILED_QUEUE;
  const notificationExchange = process.env.NOTIFICATIONS_EXCHANGE;

  console.log(failedQueue, notificationExchange);

  if (!rabbitMqUrl || !emailQueue) {
    throw new Error('RABBITMQ_URL or EMAIL_QUEUE is not defined in .env');
  }

  const app = await NestFactory.create(AppModule);

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.RMQ,
    options: {
      urls: [rabbitMqUrl],
      queue: emailQueue,
      queueOptions: {
        durable: true,
        arguments: {
          'x-dead-letter-exchange': notificationExchange,
          'x-dead-letter-routing-key': failedQueue,
        },
      },
      exchange: notificationExchange,
      exchangeType: 'direct',
    },
  });

  app.useGlobalPipes(new ValidationPipe({ whitelist: true }));

  const config = new DocumentBuilder()
    .setTitle('Email Service API')
    .setDescription('API documentation for the Email microservice')
    .setVersion('1.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  await app.startAllMicroservices();
  await app.listen(port);

  logger.log(`Email Service running on: http://localhost:${port}`);
  logger.log(`Swagger docs available at: http://localhost:${port}/docs`);
}

bootstrap();
