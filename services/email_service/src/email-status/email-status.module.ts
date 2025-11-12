import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { NotificationEmail } from 'src/email/entity/email.entity';
import { EmailStatusService } from './email-status.service';

@Module({
  imports: [TypeOrmModule.forFeature([NotificationEmail])],
  providers: [EmailStatusService],
  exports: [EmailStatusService],
})
export class EmailStatusModule {}
