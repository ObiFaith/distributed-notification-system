import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { EmailConsumer } from './email.consumer';
import { EmailController } from './email.controller';
import { NotificationEmail } from './entity/email.entity';
import { SendGridService } from 'src/sendgrid/sendgrid.service';
import { RabbitInitializer } from './rabbit-initializer.service';
import { EmailStatusModule } from 'src/email-status/email-status.module';

@Module({
  imports: [TypeOrmModule.forFeature([NotificationEmail]), EmailStatusModule],
  controllers: [EmailConsumer, EmailController],
  providers: [RabbitInitializer, SendGridService],
})
export class EmailModule {}
