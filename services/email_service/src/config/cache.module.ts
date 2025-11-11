import Redis from 'ioredis';
import { Module } from '@nestjs/common';
import { CacheModule } from '@nestjs/cache-manager';

console.log('redis', process.env.REDIS_URL);

@Module({
  imports: [
    CacheModule.registerAsync({
      isGlobal: true,
      useFactory: () => {
        const redisClient = new Redis(
          process.env.REDIS_URL || 'redis://localhost:6379',
        );

        // optional logging
        redisClient.on('connect', () => console.log('Redis connected'));
        redisClient.on('error', (err) => console.error('Redis error:', err));

        return {
          store: {
            get: async (key: string): Promise<any> => {
              const val = await redisClient.get(key);
              return val ? JSON.parse(val) : null;
            },
            set: async (key: string, value: any, ttl: number) => {
              return redisClient.set(key, JSON.stringify(value), 'EX', ttl);
            },
            del: async (key: string) => {
              return redisClient.del(key);
            },
          },
        };
      },
    }),
  ],
  exports: [CacheModule],
})
export class CacheConfigModule {}
