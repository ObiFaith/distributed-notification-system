import {
  DatabaseModule,
  CacheConfigModule,
  MailerConfigModule,
} from './config';
import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { ConfigModule } from '@nestjs/config';
import { TerminusModule } from '@nestjs/terminus';
import { EmailModule } from './email/email.module';
import { HealthController } from './health/health.controller';
import { DatabaseLogger } from './utils/database-logger.service';
import { EmailStatusModule } from './email-status/email-status.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: '.env' }),
    DatabaseModule,
    MailerConfigModule,
    TerminusModule,
    HttpModule,
    CacheConfigModule,
    EmailModule,
    EmailStatusModule,
  ],
  controllers: [HealthController],
  providers: [DatabaseLogger],
})
export class AppModule {}
