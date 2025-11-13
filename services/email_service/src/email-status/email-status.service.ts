import { Repository } from 'typeorm';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { NotificationEmail } from '../email/entity/email.entity';

@Injectable()
export class EmailStatusService {
  constructor(
    @InjectRepository(NotificationEmail)
    private readonly notificationEmailRepo: Repository<NotificationEmail>,
  ) {}

  async handleStatusUpdate(body: any) {
    const { notification_id, status, error } = body;

    const email = await this.notificationEmailRepo.findOne({
      where: { notification_id },
    });
    if (!email) return { success: false, message: 'Notification not found' };

    email.status = status || 'failed';
    email.error_message = error || null;
    await this.notificationEmailRepo.save(email);

    return {
      success: true,
      data: { notification_id, status },
      message: 'Notification status updated',
      meta: {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    };
  }
}
