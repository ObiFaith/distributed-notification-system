import { Controller, Post, Body } from '@nestjs/common';
import { EmailStatusService } from '../email-status/email-status.service';

@Controller('api/v1/email')
export class EmailController {
  constructor(private readonly emailStatusService: EmailStatusService) {}

  @Post('status')
  async updateStatus(@Body() body: any) {
    return this.emailStatusService.handleStatusUpdate(body);
  }
}
