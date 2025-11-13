import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import * as admin from 'firebase-admin';
import { ConfigService } from '@nestjs/config';
import { RabbitSubscribe } from '@golevelup/nestjs-rabbitmq';
import * as path from 'path';
import * as fs from 'fs';

interface PushMessageDto {
  device_token: string;
  title: string;
  message: string;
}

@Injectable()
export class PushService implements OnModuleInit {
  private readonly logger = new Logger(PushService.name);

  constructor(private configService: ConfigService) {}

  onModuleInit() {
    const firebaseEnv = this.configService.get<string>(
      'FIREBASE_CREDENTIALS_JSON',
    );
    const firebasePath = this.configService.get<string>('FIREBASE_CREDENTIALS');

    let serviceAccount: admin.ServiceAccount;

    if (firebaseEnv) {
      serviceAccount = JSON.parse(firebaseEnv) as admin.ServiceAccount;
    } else if (firebasePath) {
      const serviceAccountPath = path.resolve(
        __dirname,
        '../../',
        firebasePath,
      );
      serviceAccount = JSON.parse(
        fs.readFileSync(serviceAccountPath, 'utf8'),
      ) as admin.ServiceAccount;
    } else {
      throw new Error('No Firebase credentials provided');
    }

    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
    });

    this.logger.log('Connected to Firebase successfully');
    this.logger.log(' PushService is listening to RabbitMQ queue: push.queue');
  }

  @RabbitSubscribe({
    exchange: 'notifications.direct',
    routingKey: 'push.queue',
    queue: 'push.queue',
  })
  async handlePushMessage(payload: PushMessageDto) {
    this.logger.log(`Received message from RabbitMQ: ${JSON.stringify(payload)}
    `);

    try {
      const response = await admin.messaging().send({
        token: payload.device_token,
        notification: {
          title: payload.title,
          body: payload.message,
        },
      });

      this.logger.log(`Push sent successfully: ${response}`);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : JSON.stringify(error);
      this.logger.error(`Failed to send push: ${errorMessage}`);
      return { success: false, message: 'Failed to send notification', error };
    }
  }
}
