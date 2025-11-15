import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { RabbitmqModule } from './rabbitmq/rabbitmq.module';
import { PushModule } from './push/push.module';
import { FcmService } from './fcm/fcm.service';
import { IdempotencyService } from './idempotency/idempotency.service';
import { HealthController } from './health/health.controller';

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true }), RabbitmqModule, PushModule],
  controllers: [HealthController],
  providers: [FcmService, IdempotencyService],
})
export class AppModule {}
