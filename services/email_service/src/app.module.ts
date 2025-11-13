import { Module } from '@nestjs/common';
import { AppService } from './app.service';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller';
import { DatabaseModule } from './config/database.module';
import { MailerConfigModule } from './config/mailer.module';
import { DatabaseLogger } from './utils/database-logger.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: '.env' }),
    DatabaseModule,
    MailerConfigModule,
  ],
  controllers: [AppController],
  providers: [AppService, DatabaseLogger],
})
export class AppModule {}
