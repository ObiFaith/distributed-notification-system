import Redis from 'ioredis';
import { Module } from '@nestjs/common';
import { CacheModule } from '@nestjs/cache-manager';

@Module({
  imports: [
    CacheModule.registerAsync({
      isGlobal: true,
      useFactory: () => {
        if (!process.env.REDIS_URL) {
          throw new Error('CacheModule: REDIS_URL is not defined!');
        }

        const redisClient = new Redis(process.env.REDIS_URL);

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
