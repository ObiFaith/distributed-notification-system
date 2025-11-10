# Email Service — Distributed Notification System

The Email Service is a microservice responsible for sending transactional emails asynchronously. It consumes messages from a `RabbitMQ` queue, applies dynamic templates, sends emails via `SMTP`, and logs notification status to a `PostgreSQL` database.

## 🚀 Features

- Consume messages from email.queue in `RabbitMQ`
- Fetch dynamic user and template data (mocked or via service APIs)
- Send emails via `SMTP` (SendGrid, Gmail, Mailgun)
- Persist email notification status in `PostgreSQL`
- Retry failed emails with exponential backoff
- Move permanently failed messages to `Dead Letter Queue` (failed.queue)
- Health endpoint (`/health`) to monitor service status
- Structured logging with correlation ID for observability
- Ready for integration with Monitoring stack (Prometheus + Grafana)

## 📦 Tech Stack

- **Language / Framework**: NestJS
- **Database**: PostgreSQL
- **Message Queue**: RabbitMQ
- **Email Transport**: SMTP (NestJS MailerModule)
- **Caching / Queue Retry**: Redis (optional)
- **Containerization**: Docker
- **Environment Management**: @nestjs/config

## 🗂 Project Structure

```sh
email-service/
│
├── src/
│ ├── main.ts # Entry point
│ ├── app.module.ts # Root module
│ ├── queue/
│ │ └── email.consumer.ts # RabbitMQ consumer
│ ├── services/
│ │ ├── email.service.ts # Email sending logic
│ │ └── template.service.ts # Template processing (mocked or API)
│ ├── entities/
│ │ └── notification.entity.ts # TypeORM entity for PostgreSQL
│ ├── controllers/
│ │ └── health.controller.ts # /health endpoint
│ ├── dtos/
│ │ └── email.dto.ts # DTOs for message payloads
│ └── utils/
│ └── logger.ts # Logging helper
│
├── docker/
│ └── Dockerfile
├── .env.example
├── package.json
└── README.md
```

## ⚡ Installation

#### 1. Clone the repository:

```sh
git clone https://github.com/ObiFaith/distributed-notification-system
cd distributed-notification-system
cd email-service
```

#### 2. Install dependencies:

```sh
npm install
```

#### 3. Set up environment variables:

```sh
cp .env.example .env
```

Edit `.env` to include:

```sh
PORT=3000
RABBITMQ_URL=amqp://<username>:<password>@<host>:5672
EMAIL_QUEUE=email.queue
DB_HOST=<host>
DB_PORT=<port>
DB_USER=<username>
DB_PASS=<password>
DB_NAME=<database>
MAIL_HOST=<smtp-host>
MAIL_PORT=<smtp-port>
SMTP_USER=<your-email>
SMTP_PASS=<your-password>
MAIL_FROM="Framez <noreply@framez.app>"
```

#### 4. Run PostgreSQL and RabbitMQ (via Docker Compose or local):

```sh
docker-compose up -d postgres rabbitmq
```

## Running the Service

```sh
npm run start:dev
```

- Health check: **GET** `/health`
- Service will automatically consume messages from `email.queue`.

## 📬 Message Format

- **Queue**: notifications.direct → email.queue
- **Payload**:

```json
{
  "notification_id": "uuid",
  "user_id": "uuid",
  "template_code": "welcome_email",
  "variables": { "name": "Obi Faith", "link": "https://framez.app" },
  "request_id": "abc123",
  "priority": 1,
  "metadata": {}
}
```

## 💾 Database Schema

**Table**: `notifications_email`

| Column          | Type        | Description                             |
| --------------- | ----------- | --------------------------------------- |
| id              | `UUID`      | Primary Key                             |
| notification_id | `UUID`      | Unique ID of the notification           |
| user_id         | `UUID`      | Recipient user ID                       |
| template_id     | `TEXT`      | Template used for email                 |
| status          | `TEXT`      | 'pending', 'sent', 'failed', 'retrying' |
| retry_count     | `INT`       | Number of retries                       |
| error_message   | `TEXT`      | Error if sending failed                 |
| sent_at         | `TIMESTAMP` | When email was sent                     |
| created_at      | `TIMESTAMP` | Record creation timestamp               |

## 🔄 Retry & Failure Handling

- **Retry Logic**: Up to 3 attempts with exponential backoff
- **Dead Letter Queue**: Messages failing all retries → `failed.queue`
- **Logging**: Errors and delivery status persisted in PostgreSQL and optionally sent to monitoring/logging stack

## 🛠 Future Integration

- Replace mock user/template fetches with live API calls:
  - `GET /api/v1/users/:id`
  - `GET /api/v1/templates/:code`

- Status reporting via `POST /api/v1/email/status/`
- Integrate metrics with `Prometheus` + `Grafana`

## 🧪 Testing

- Push a test message to RabbitMQ `email.queue`
- Confirm that the message is consumed, email is sent, and status is persisted in DB.

## 📝 Notes

- Supports **idempotency** via `request_id` to avoid duplicate emails
- Health endpoint and logs provide observability for distributed system
- Scalable — multiple instances can run concurrently, consuming from the same queue
