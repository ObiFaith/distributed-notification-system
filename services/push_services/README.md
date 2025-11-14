# [Push Service (NestJS)]

## Overview

The Push Service is one of the microservices in the Distributed Notification System.
Its responsibility is to:

Receive push notification jobs from RabbitMQ (push.queue)

Fetch user device tokens if missing

Send push notifications using Firebase Cloud Messaging (FCM)

Handle retries with exponential backoff

Publish delivery status updates to the notification.status.queue

Ensure idempotency using request_id

This service works asynchronously and is triggered by messages published from the API Gateway through RabbitMQ.

## Tech Stack

- Framework: NestJS
- Notifications: Firebase Cloud Messaging (FCM)
- Idempotency / Cache: Redis (or in-memory fallback)
- Language: TypeScript
- Queue: RabbitMQ
- Containerization: Docker & Docker Compose

## Setup

Steps to run this service locally.

1. Clone the repo
    git clone https://github.com/ObiFaith/distributed-notification-system.git

    cd distributed-notification-system/push-service

2. Create your .env file

## Environment Variables
   
List of required `.env` variables.
    PORT=3002
    RABBITMQ_URL1=amqp://guest:guest@localhost:5672
    PUSH_QUEUE=push.queue
    RETRY_QUEUE=push.retry.queue
    FAILED_QUEUE=push.failed.queue
    EXCHANGE=notifications.direct
    FCM_SERVICE_ACCOUNT_PATH=./firebase-key.json
    REDIS_URL1=redis://127.0.0.1:6379
    API_GATEWAY_URL=http://gateway:3000
    MAX_RETRY=3
    REDIS_HOST=127.0.0.1
    REDIS_PORT=6379

3. Add Firebase service account
    Place your Firebase Admin SDK JSON file here:
    push-service/firebase-key.json

4. Install dependencies
    npm install

5. Start services (RabbitMQ, Redis, Push Service) using docker
    docker-compose up -d

6. Start the NestJS push service
    npm run start:dev

## API Endpoints

Outline of main endpoints or routes.
1. Test push (bypass RabbitMQ)
    POST /api/v1/push/test

2. Status callback endpoint
    POST /api/v1/push/status

3. Health Check
    GET /api/v1/health

## Notes

Any relevant integration or dependency info.


1. Create `.env` based on `.env.example`
2. Place firebase service account at `firebase-key.json`
3. Start services:
