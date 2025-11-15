import { Injectable, Logger } from '@nestjs/common';
import Redis from 'ioredis';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class IdempotencyService {
  private redis: Redis;
  private logger = new Logger(IdempotencyService.name);

  constructor(private config: ConfigService) {
    const url = this.config.get('REDIS_URL') || 'redis://localhost:6379';
    this.redis = new Redis(url);
  }

  // returns true if id was set (i.e., not duplicate), false if already exists
  async reserve(request_id: string, ttlSeconds = 60 * 60) {
    // SET key NX EX ttl
    const key = `push:req:${request_id}`;
    const res = await this.redis.set(key, '1', 'EX', ttlSeconds, 'NX');
    return res === 'OK';
  }

  // Optionally release (delete)
  async release(request_id: string) {
    await this.redis.del(`push:req:${request_id}`);
  }
}

//We reserve request_id before sending. If returns false, we skip send. TTL prevents permanent storage.