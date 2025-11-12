import { Controller, Get } from '@nestjs/common';

@Controller('push')
export class PushController {
  @Get('health')
  healthCheck() {
    return { status: 'ok', message: 'Push service is running' };
  }
}
