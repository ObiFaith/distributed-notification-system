import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { ConfigModule } from '@nestjs/config';
import { TerminusModule } from '@nestjs/terminus';
import { EmailConsumer } from './email/email.consumer';
import { DatabaseModule } from './config/database.module';
import { MailerConfigModule } from './config/mailer.module';
import { HealthController } from './health/health.controller';
import { DatabaseLogger } from './utils/database-logger.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: '.env' }),
    DatabaseModule,
    MailerConfigModule,
    TerminusModule,
    HttpModule,
  ],
  controllers: [HealthController, EmailConsumer],
  providers: [DatabaseLogger],
})
export class AppModule {}
