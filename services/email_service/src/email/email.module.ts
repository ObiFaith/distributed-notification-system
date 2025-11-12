import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { EmailConsumer } from './email.consumer';
import { NotificationEmail } from './entity/email.entity';
import { RabbitInitializer } from './rabbit-initializer.service';

@Module({
  imports: [TypeOrmModule.forFeature([NotificationEmail])],
  controllers: [EmailConsumer],
  providers: [RabbitInitializer],
})
export class EmailModule {}
