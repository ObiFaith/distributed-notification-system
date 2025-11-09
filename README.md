# 📨 Distributed Notification System

A microservices-based notification system designed to handle large-scale email and push notifications using asynchronous messaging via **RabbitMQ**.

Each service operates independently and communicates through queues, coordinated via a **Traefik API Gateway**.

The system is containerized with **Docker** and built with **NestJS**, **FastAPI**, and **Flask** microservices.

## 🎯 Objective

To build a distributed, fault-tolerant notification system capable of:

- Sending **emails** and **push notifications** reliably.
- Managing **user preferences** and **notification templates**.
- Scaling horizontally to handle **1,000+ notifications per minute**.

## ⚡ Key Features

- Asynchronous messaging via RabbitMQ.
- Circuit breaker and retry system with exponential backoff.
- Idempotency using request IDs to prevent duplicate sends.
- Dead-letter queues for failed message recovery.
- Health checks (`/health`) on each service.
- Monitoring dashboards (Prometheus + Grafana).

## 🧩 Microservices Architecture

| Service              | Framework | Description                                                                                        |
| -------------------- | --------- | -------------------------------------------------------------------------------------------------- |
| **API Gateway**      | `FastAPI` | Entry point for all external requests. Handles authentication, validation, and routing to queues.  |
| **User Service**     | `Flask`   | Manages user profiles, contact info, and notification preferences.                                 |
| **Template Service** | `Flask`   | Stores and manages notification templates and language variations.                                 |
| **Email Service**    | `NestJS`  | Consumes messages from the `email.queue` and sends templated emails via SMTP or an email provider. |
| **Push Service**     | `NestJS`  | Consumes messages from the `push.queue` and sends mobile/web push notifications.                   |

## 🔐 Authentication

The **API Gateway** (`FastAPI`) will handle:

- Request validation
- JWT authentication
- Routing to internal services or message queues

## 🧩 Service Communication

| Type             | Use Case                                   | Method          |
| ---------------- | ------------------------------------------ | --------------- |
| **Synchronous**  | User preference lookup, Template retrieval | REST (HTTP)     |
| **Asynchronous** | Notification dispatch, Retry handling      | RabbitMQ Queues |

---

## 🛠️ Tech Stack

| Category                 | Tools                                                              |
| ------------------------ | ------------------------------------------------------------------ |
| **Languages/Frameworks** | NestJS (Node.js), FastAPI (Python), Flask (Python)                 |
| **Message Queue**        | RabbitMQ                                                           |
| **Databases**            | PostgreSQL (User, Template, Status), Redis (Cache + Rate limiting) |
| **Gateway**              | Traefik                                                            |
| **Containerization**     | Docker + Docker Compose                                            |
| **Monitoring & Logs**    | Prometheus, Grafana, Loki                                          |
| **CI/CD**                | GitHub Actions                                                     |
| **Documentation**        | Swagger / OpenAPI                                                  |

## 🧭 Architecture Diagram (Conceptual)

```sh
Client → Traefik (API Gateway)
├── /users/_ → User Service (Flask)
├── /templates/_ → Template Service (Flask)
├── /notify/email → Publishes message → RabbitMQ (email.queue)
└── /notify/push → Publishes message → RabbitMQ (push.queue)
```

```sh
RabbitMQ
├── email.queue → Email Service (NestJS)
├── push.queue → Push Service (NestJS)
└── failed.queue → Dead Letter Queue (retry handling)
```

**Email / Push Services**
\
→ Status updates → Redis / PostgreSQL
\
→ Logs & metrics → Prometheus + Grafana + Loki

---

## 🗂️ Repository Structure

```sh
distributed-notification-system/
│
├── docker-compose.yml
├── traefik/
│ ├── traefik.yml
│ └── dynamic_conf.yml
│
├── services/
│ ├── api_gateway/ # FastAPI
│ ├── user_service/ # Flask
│ ├── template_service/ # Flask
│ ├── email_service/ # NestJS
│ └── push_service/ # NestJS
│
├── shared/ # Common utilities & configs
├── monitoring/ # Prometheus, Grafana, Loki setup
├── .github/workflows/ # CI/CD pipeline
├── scripts/ # Helper scripts (init DB, seed data, etc.)
├── .env.example
└── README.md # (This file)
```

## 🧰 Getting Started

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Node.js](https://nodejs.org/) (for NestJS services)
- [Python](https://www.python.org/downloads/)
- [RabbitMQ Management UI](https://www.rabbitmq.com/management.html) _(optional)_

### 2. Clone the Repository

```bash
git clone https://github.com/ObiFaith/distributed-notification-system.git

cd distributed-notification-system
```

> Each developer should now navigate into their assigned service folder before making any changes.

**For example**:

```sh
cd services/api_gateway      # FastAPI developer
cd services/user_service     # Flask developer
cd services/template_service # Flask developer
cd services/email_service    # NestJS developer
cd services/push_service     # NestJS developer
```

> This ensures isolation and prevents cross-service conflicts in the mono-repo.

### 3. Environment Setup

Each service may also contain its own `.env.example` file with service-specific variables.

Duplicate `.env.example` into `.env` and configure:

```sh
cp .env.example .env
```

### 4. Start the Services

To build and start all containers (RabbitMQ, Traefik, services, monitoring):

```sh
docker-compose up --build
```

---

## 🤝 Contributing

## 🧾 License

This project is licensed under the [Apache License](LICENSE).
