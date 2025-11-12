import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { PushModule } from './push/push.module';
import { RabbitMQModule } from '@golevelup/nestjs-rabbitmq';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    RabbitMQModule.forRoot({
      exchanges: [
        {
          name: 'notifications.direct',
          type: 'direct',
        },
      ],
      uri: process.env.RABBITMQ_URI,
      connectionInitOptions: { wait: false },
    }),
    PushModule,
  ],
})
export class AppModule {}
