import { Channel, ConsumeMessage } from 'amqplib';
import { Controller, Logger } from '@nestjs/common';
import { Ctx, EventPattern, Payload, RmqContext } from '@nestjs/microservices';

interface EmailJob {
  notification_id: string;
  user_id: string;
  user_email: string;
  template_code: string;
  variables: Record<string, any>;
  request_id: string;
  priority?: number;
  metadata?: Record<string, any>;
}

@Controller()
export class EmailConsumer {
  private readonly logger = new Logger(EmailConsumer.name);

  // Simulate sending email (replace with MailerService later)
  private async simulateEmailSend(job: EmailJob) {
    // Simulate async email sending
    await new Promise<void>((resolve) => setTimeout(resolve, 1000));
    this.logger.debug(
      `Simulating email send: to=${job.user_email}, template=${job.template_code}`,
    );
  }

  @EventPattern('email.notify')
  async handleEmailNotification(
    @Payload() data: EmailJob,
    @Ctx() context: RmqContext,
  ) {
    // Properly typed channel and message
    const channel = context.getChannelRef() as Channel;
    const message = context.getMessage() as ConsumeMessage;

    this.logger.log(`Received email job: ${JSON.stringify(data)}`);

    try {
      // TODO: Replace with actual MailerService call
      await this.simulateEmailSend(data);

      this.logger.log(`Email sent successfully to ${data.user_email}`);

      // Acknowledge the message
      channel.ack(message);
    } catch (err: unknown) {
      const errMessage =
        err instanceof Error ? err.message : JSON.stringify(err);

      this.logger.error(`Failed to process email: ${errMessage}`);

      // Send to dead-letter queue or retry later
      channel.nack(message, false, false);
    }
  }
}
