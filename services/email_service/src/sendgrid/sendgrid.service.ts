import { Injectable, Logger } from '@nestjs/common';
import sendgridMail from '@sendgrid/mail'; // Correct import
import { config } from 'dotenv';

config();

@Injectable()
export class SendGridService {
  private readonly logger = new Logger(SendGridService.name);

  constructor() {
    sendgridMail.setApiKey(process.env.SENDGRID_API_KEY as string);
  }

  async sendEmail(
    user_email: string,
    template_code: string,
    variables?: Record<string, any>,
  ) {
    const message = {
      to: user_email,
      from: process.env.MAIL_USER as string,
      subject: `Notification: ${template_code}`,
      text: `Hello ${variables?.name || 'User'}, Your notification "${template_code}" has been triggered.`,
      html: `<p>Hello ${variables?.name || 'User'},</p><p>Your notification "${template_code}" has been triggered.</p>`,
    };

    try {
      this.logger.log('Sending email with params:', message);
      await sendgridMail.send(message);
      this.logger.log(`Email sent successfully to ${user_email}`);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : JSON.stringify(err);
      this.logger.error(`Failed to send email: ${errorMessage}`);
      throw err;
    }
  }
}
