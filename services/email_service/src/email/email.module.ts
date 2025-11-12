import { Module } from '@nestjs/common';
import { EmailConsumer } from './email.consumer';
import { RabbitInitializer } from './rabbit-initializer.service';

@Module({
  controllers: [EmailConsumer],
  providers: [RabbitInitializer],
})
export class EmailModule {}
