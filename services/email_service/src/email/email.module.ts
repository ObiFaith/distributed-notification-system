import { Module } from '@nestjs/common';
import { EmailConsumer } from './email.consumer';

@Module({
  controllers: [EmailConsumer],
})
export class EmailModule {}
