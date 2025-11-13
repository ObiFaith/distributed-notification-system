import { config } from 'dotenv';
import { DataSource } from 'typeorm';
import { NotificationEmail } from '../email/entity/email.entity';

config();

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
  username: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  entities: [NotificationEmail],
  migrations: ['src/migrations/*.ts'],
  synchronize: true, // TODO: false
  logging: true,
});
