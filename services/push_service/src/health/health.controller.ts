import { Controller, Get } from '@nestjs/common';

@Controller()
export class HealthController {
  @Get('health')
  health() {
    // Minimal health. In production include DB/Rabbit/Redis checks.
    return { status: 'ok', time: new Date().toISOString() };
  }
}
