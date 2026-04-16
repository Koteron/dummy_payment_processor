# Async Payment Processing Service

## Overview

Сервис для асинхронной обработки платежей. Принимает запрос, сохраняет его в БД и обрабатывает через RabbitMQ с последующим webhook-уведомлением.

## Run

1. Переименовать `.env.example` в `.env`. После этого проект уже будет готов к запуску, но можно также поменять какие-либо переменные окружения. Посмотреть их полный список можно в `/app/config/settings.py`

2. Из корневой папки запустить:

```bash
docker-compose up --build -d
```

3. После этого можно удобно взаимодействовать с API по `http://localhost:8000/docs` или `http://localhost:8000/redoc`


## API

### POST /api/v1/payments

Headers: `Idempotency-Key`, `X-API-Key`

Body: сумма, валюта, описание, meta, webhook_url

Response: `202 Accepted` + payment_id, статус, created_at

### GET /api/v1/payments/{id}

Headers: `X-API-Key`

Response: информация о платеже

## Flow

1. API сохраняет платеж + outbox событие (одна транзакция)
2. Outbox worker публикует событие в `payments.new`
3. Consumer:

   * обрабатывает платеж (эмуляция)
   * обновляет статус
   * отправляет webhook


## Features

* Idempotency через `Idempotency-Key`
* Outbox pattern (гарантия доставки)
* Retry (3 попытки (настраивается через переменные окружения), exponential backoff)
* Dead Letter Queue (`payments.dlq`)

## Stack

FastAPI, PostgreSQL, SQLAlchemy (async), RabbitMQ (FastStream), Alembic, Docker
