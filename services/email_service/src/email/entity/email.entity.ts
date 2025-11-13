import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

export type EmailStatus = 'pending' | 'sent' | 'failed' | 'retrying';

@Entity('notification_email')
export class NotificationEmail {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid' })
  notification_id: string;

  @Column({ type: 'uuid' })
  user_id: string;

  @Column({ type: 'text' })
  template_id: string;

  @Column({
    type: 'enum',
    enum: ['pending', 'sent', 'failed', 'retrying'],
    default: 'pending',
  })
  status: EmailStatus;

  @Column({ type: 'int', default: 0 })
  retry_count: number;

  @Column({ type: 'text', nullable: true })
  error_message?: string;

  @Column({ type: 'timestamp', nullable: true })
  sent_at?: Date;

  @CreateDateColumn({ type: 'timestamp' })
  created_at: Date;
}
