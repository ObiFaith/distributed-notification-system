import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as admin from 'firebase-admin';
import * as fs from 'fs';
import { join } from 'path';

@Injectable()
export class FcmService {
  private readonly logger = new Logger(FcmService.name);

  private adminApp: admin.app.App;

  constructor(private readonly config: ConfigService) {
    const filePath =
      // this.config.get('FCM_SERVICE_ACCOUNT_PATH') ||
      join(process.cwd(), 'firebase-key.json');

    if (!fs.existsSync(filePath)) {
      this.logger.error(`FCM service account key not found at ${filePath}`);
      return;
    }

    const serviceAccount = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

    // ✅ Reuse existing app if already initialized
    if (admin.apps.length) {
      this.adminApp = admin.app(); // get existing default app
      this.logger.log('Reusing existing Firebase app');
    } else {
      this.adminApp = admin.initializeApp({
        credential: admin.credential.cert(serviceAccount),
      });
      this.logger.log('Firebase Admin initialized successfully');
    }
  }

  async sendToDevice(message: admin.messaging.Message) {
    try {
      const res = await this.adminApp.messaging().send(message);
      return { success: true, message_id: res };
    } catch (err) {
      this.logger.error('FCM send error', err);
      return { success: false, error: err };
    }
  }
}
