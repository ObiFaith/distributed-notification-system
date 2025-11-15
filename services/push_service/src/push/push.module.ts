import { Module } from '@nestjs/common';
import { PushController } from './push.controller';
import { PushService } from './push.service';
import { RabbitmqService } from '../rabbitmq/rabbitmq.service';
import { FcmService } from '../fcm/fcm.service';
import { IdempotencyService } from '../idempotency/idempotency.service';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [ConfigModule],
  controllers: [PushController],
  providers: [PushService, RabbitmqService, FcmService, IdempotencyService],
})
export class PushModule {}
