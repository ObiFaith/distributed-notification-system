import { DataSource } from 'typeorm';
import { Injectable, OnModuleInit, Logger } from '@nestjs/common';

@Injectable()
export class DatabaseLogger implements OnModuleInit {
  private readonly logger = new Logger(DatabaseLogger.name);

  constructor(private readonly dataSource: DataSource) {}

  async onModuleInit() {
    try {
      if (!this.dataSource.isInitialized) {
        await this.dataSource.initialize();
      }
      this.logger.log('Database connected successfully');
    } catch (error) {
      this.logger.error('Database connection failed', error);
    }
  }
}
