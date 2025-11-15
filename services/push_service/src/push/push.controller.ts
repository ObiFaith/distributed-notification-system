import { Body, Controller, Post } from '@nestjs/common';
import { PushService } from './push.service';
import { SendPushDto } from './dto/send_push.dto';

@Controller('push')
export class PushController {
  constructor(private readonly pushService: PushService) {}

  // Test endpoint to send a push directly (bypass RabbitMQ)
  @Post('test')
  async testPush(@Body() body: any) {
    // For testing, we accept a simplified payload
    return this.pushService.sendDirect(body);
  }

  // Internal endpoint to receive status (gateway or service can call this)
  @Post('status')
  async status(@Body() body: any) {
    // store or process status updates (simple echo for now)
    return { success: true, data: body, message: 'status received' };
  }
}
