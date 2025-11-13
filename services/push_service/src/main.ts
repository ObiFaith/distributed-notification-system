import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const port = process.env.PORT ? parseInt(process.env.PORT) : 3000;

  await app.listen(port);
  Logger.log(`Application is listening on port ${port}`, 'Bootstrap');
}
bootstrap().catch((err) => {
  console.error('Failed to start application:', err);
  process.exit(1);
});
