import { Injectable, Logger } from '@nestjs/common';
import { MailerSend, EmailParams } from 'mailersend';
import { config } from 'dotenv';

config();

@Injectable()
export class MailerSendService {
  private readonly logger = new Logger(MailerSendService.name);
  private readonly mailerSend: MailerSend;

  constructor() {
    this.mailerSend = new MailerSend({
      apiKey: process.env.MAILERSEND_API_KEY as string,
    });
  }

  async sendEmail(
    user_email: string,
    template_code: string,
    variables?: Record<string, any>,
  ) {
    const params: EmailParams = {
      from: 'MS_t9br9x@test-pzkmgq7xj0vl059v.mlsender.net',
      to: [{ email: user_email }],
      subject: `Notification: ${template_code}`,
      html: `<p>Hello ${variables?.name || 'User'},</p>
             <p>Your notification "${template_code}" has been triggered.</p>`,
    };

    try {
      await this.mailerSend.email.send(params);
      this.logger.log(`Email sent successfully to ${user_email}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : JSON.stringify(err);
      this.logger.error(`Failed to send email: ${message}`);
      throw err;
    }
  }
}
