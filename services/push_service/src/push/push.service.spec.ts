import { Test, TestingModule } from '@nestjs/testing';
import { PushService } from './push.service';
import { RabbitmqService } from '../rabbitmq/rabbitmq.service';
import { FcmService } from '../fcm/fcm.service';
import { IdempotencyService } from '../idempotency/idempotency.service';
import { ConfigModule } from '@nestjs/config';

describe('PushService', () => {
  let service: PushService;

  const mockRabbit = {
    consume: jest.fn(),
    ack: jest.fn(),
    nack: jest.fn(),
    publish: jest.fn(),
  };

  const mockFcm = {
    sendToDevice: jest.fn(),
  };

  const mockIdem = {
    reserve: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [ConfigModule.forRoot()],
      providers: [
        PushService,
        { provide: RabbitmqService, useValue: mockRabbit },
        { provide: FcmService, useValue: mockFcm },
        { provide: IdempotencyService, useValue: mockIdem },
      ],
    }).compile();

    service = module.get<PushService>(PushService);
  });

  it('should send direct push successfully', async () => {
    mockIdem.reserve.mockResolvedValue(true);
    mockFcm.sendToDevice.mockResolvedValue({ success: true, message_id: 'msg123' });

    const res = await service.sendDirect({
      device_token: 'token-1',
      title: 'Hi',
      message: 'Hello',
      request_id: 'req-1',
    });

    expect(res.success).toBe(true);
    expect(mockFcm.sendToDevice).toHaveBeenCalled();
  });

  it('should reject duplicate direct push', async () => {
    mockIdem.reserve.mockResolvedValue(false);
    const res = await service.sendDirect({ device_token: 'token-2', request_id: 'req-dup' });
    expect(res.success).toBe(false);
    expect(res.message).toBe('duplicate_request');
  });
});
