import * as amqp from 'amqplib';
import { ConfigService } from '@nestjs/config';
import { Controller, Get } from '@nestjs/common';
import { HealthCheck, TypeOrmHealthIndicator } from '@nestjs/terminus';

@Controller('health')
export class HealthController {
  constructor(
    private config: ConfigService,
    private db: TypeOrmHealthIndicator,
  ) {}

  @Get()
  @HealthCheck()
  async check() {
    const dbCheck = await this.db.pingCheck('database');

    try {
      const connection = await amqp.connect(
        this.config.get('RABBITMQ_URL') as string,
      );

      await connection.close();

      return {
        status: 'ok',
        info: {
          ...dbCheck,
          rabbitmq: { status: 'up' },
        },
      };
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unknown error while connecting to RabbitMQ';

      return {
        status: 'error',
        info: { ...dbCheck },
        error: { rabbitmq: { status: 'down', message } },
      };
    }
  }
}
