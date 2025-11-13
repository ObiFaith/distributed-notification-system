import { MigrationInterface, QueryRunner } from "typeorm";

export class CreateNotificationTable1763028710799 implements MigrationInterface {
    name = 'CreateNotificationTable1763028710799'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TYPE "public"."notification_email_status_enum" AS ENUM('pending', 'sent', 'failed', 'retrying')`);
        await queryRunner.query(`CREATE TABLE "notification_email" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "notification_id" uuid NOT NULL, "user_id" uuid NOT NULL, "template_id" text NOT NULL, "status" "public"."notification_email_status_enum" NOT NULL DEFAULT 'pending', "retry_count" integer NOT NULL DEFAULT '0', "error_message" text, "sent_at" TIMESTAMP, "created_at" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_d824f1fa65e77c6784b3fd2788a" PRIMARY KEY ("id"))`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "notification_email"`);
        await queryRunner.query(`DROP TYPE "public"."notification_email_status_enum"`);
    }

}
