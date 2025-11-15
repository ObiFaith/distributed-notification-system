import { IsString, IsNotEmpty, IsOptional, IsObject, IsUUID, IsNumber } from 'class-validator';

export class SendPushDto {
  @IsString()
  @IsNotEmpty()
  notification_type: string; // push

  @IsString()
  @IsUUID()
  user_id: string;

  @IsString()
  @IsOptional()
  template_code?: string;

  @IsObject()
  variables: Record<string, any>;

  @IsString()
  request_id: string;

  @IsNumber()
  @IsOptional()
  priority?: number;

  @IsObject()
  @IsOptional()
  metadata?: Record<string, any>;
}
