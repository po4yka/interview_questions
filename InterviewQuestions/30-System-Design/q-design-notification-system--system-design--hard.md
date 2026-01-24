---
id: sysdes-030
title: Design Notification System
aliases:
- Notification System
- Push Notifications
- Alert System
topic: system-design
subtopics:
- messaging
- real-time
- scalability
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-pubsub-patterns--system-design--medium
- q-message-queues-event-driven--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- system-design
- difficulty/hard
- messaging
- real-time
anki_cards:
- slug: sysdes-030-0-en
  language: en
  anki_id: 1769158890941
  synced_at: '2026-01-23T13:49:17.783702'
- slug: sysdes-030-0-ru
  language: ru
  anki_id: 1769158890966
  synced_at: '2026-01-23T13:49:17.785388'
---
# Question (EN)
> Design a notification system that can send push notifications, SMS, and email at scale.

# Vopros (RU)
> Спроектируйте систему уведомлений, которая может отправлять push-уведомления, SMS и email в масштабе.

---

## Answer (EN)

### Requirements

**Functional:**
- Send push notifications (iOS, Android, Web)
- Send SMS notifications
- Send email notifications
- Support templates and personalization
- User preferences (opt-out, channels, frequency)
- Scheduling and rate limiting
- Delivery tracking and analytics

**Non-Functional:**
- 10M notifications/day
- Soft real-time (<1min for critical)
- At-least-once delivery
- High availability (99.9%)
- Pluggable providers (Twilio, SendGrid, FCM)

### High-Level Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              API Gateway                │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │         Notification Service            │
                    │   (validation, rate limiting, routing)  │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │           Message Queue                 │
                    │        (Kafka / RabbitMQ)               │
                    └───────┬─────────┬──────────┬────────────┘
                            │         │          │
              ┌─────────────▼───┐  ┌──▼────┐  ┌──▼──────────┐
              │   Push Worker   │  │ SMS   │  │   Email     │
              │  (FCM, APNS)    │  │Worker │  │   Worker    │
              └────────┬────────┘  └───┬───┘  └──────┬──────┘
                       │               │             │
                 ┌─────▼─────┐   ┌─────▼─────┐  ┌────▼─────┐
                 │ FCM/APNS  │   │  Twilio   │  │ SendGrid │
                 └───────────┘   └───────────┘  └──────────┘
```

### Core Components

**1. Notification Service**
- API for sending notifications
- Validates requests
- Checks user preferences
- Routes to appropriate channel
- Applies rate limiting

**2. Message Queue**
- Decouples sending from processing
- Handles back-pressure
- Enables retries
- Separate queues per channel (priority)

**3. Channel Workers**
- Push: FCM (Android), APNS (iOS), Web Push
- SMS: Twilio, Vonage
- Email: SendGrid, SES, Mailgun

**4. Template Service**
- Store notification templates
- Personalization ({{user.name}})
- Localization (i18n)

### Data Models

**Notification Request**
```json
{
    "user_id": "123",
    "type": "order_shipped",
    "channels": ["push", "email"],
    "data": {
        "order_id": "456",
        "tracking_url": "..."
    },
    "priority": "high",
    "scheduled_at": null
}
```

**User Preferences**
```sql
user_notification_preferences (
    user_id: bigint PRIMARY KEY,
    push_enabled: boolean,
    email_enabled: boolean,
    sms_enabled: boolean,
    quiet_hours_start: time,
    quiet_hours_end: time,
    frequency_cap: int,  -- max per day
    channels_by_type: jsonb  -- {"marketing": ["email"], "transactional": ["push", "email"]}
)
```

**Notification Log**
```sql
notification_logs (
    id: uuid PRIMARY KEY,
    user_id: bigint,
    type: varchar,
    channel: varchar,
    status: enum(pending, sent, delivered, failed),
    provider_id: varchar,
    sent_at: timestamp,
    delivered_at: timestamp,
    error: text
)
```

### Notification Flow

```
1. API receives notification request
2. Validate request, check user preferences
3. Apply rate limiting (user-level, global)
4. For each enabled channel:
   a. Render template with data
   b. Enqueue to channel-specific queue
5. Worker picks up message
6. Send to external provider (FCM, Twilio, etc.)
7. Handle response:
   - Success: Log delivery, update status
   - Failure: Retry with backoff or DLQ
8. Track analytics (sent, delivered, opened)
```

### Rate Limiting Strategy

```python
# Multi-level rate limiting
class NotificationRateLimiter:
    def check_limits(self, user_id, notification_type):
        # Global limit: 1M/min across system
        if not self.check_global_limit():
            return False, "System overloaded"

        # User limit: 10 notifications/hour
        if not self.check_user_limit(user_id, limit=10, window="1h"):
            return False, "User rate limited"

        # Type limit: 1 marketing email/day
        if notification_type == "marketing":
            if not self.check_type_limit(user_id, "marketing", limit=1, window="24h"):
                return False, "Marketing limit reached"

        return True, None
```

### Reliability Patterns

**1. Retry with Exponential Backoff**
```python
def send_with_retry(notification, max_retries=3):
    for attempt in range(max_retries):
        try:
            return send(notification)
        except TransientError:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    # Move to dead letter queue
    dlq.send(notification)
```

**2. Circuit Breaker per Provider**
```
If Twilio fails 5 times in 1 minute:
  - Open circuit
  - Failover to backup provider (Vonage)
  - Periodically test Twilio
  - Close circuit when healthy
```

**3. Idempotency**
```python
def send_notification(request):
    idempotency_key = f"{request.user_id}:{request.type}:{request.data_hash}"

    if cache.exists(idempotency_key):
        return "Duplicate, skipped"

    result = process_notification(request)
    cache.set(idempotency_key, result, ttl=24h)
    return result
```

### Scaling Considerations

| Component | Scaling Strategy |
|-----------|------------------|
| API | Horizontal (stateless) |
| Queue | Partitioned by user_id |
| Workers | Auto-scale based on queue depth |
| Templates | Cache in Redis |
| Preferences | Cache with write-through |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Отправка push-уведомлений (iOS, Android, Web)
- Отправка SMS-уведомлений
- Отправка email-уведомлений
- Поддержка шаблонов и персонализации
- Предпочтения пользователей (opt-out, каналы, частота)
- Планирование и rate limiting
- Отслеживание доставки и аналитика

**Нефункциональные:**
- 10M уведомлений/день
- Мягкий real-time (<1мин для критичных)
- At-least-once доставка
- Высокая доступность (99.9%)
- Подключаемые провайдеры (Twilio, SendGrid, FCM)

### Основные компоненты

**1. Notification Service**
- API для отправки уведомлений
- Валидация запросов
- Проверка предпочтений пользователя
- Маршрутизация в нужный канал
- Rate limiting

**2. Message Queue**
- Декаплинг отправки от обработки
- Обработка back-pressure
- Возможность retry
- Отдельные очереди по каналам (приоритет)

**3. Channel Workers**
- Push: FCM (Android), APNS (iOS), Web Push
- SMS: Twilio, Vonage
- Email: SendGrid, SES, Mailgun

### Поток уведомления

```
1. API получает запрос на уведомление
2. Валидация запроса, проверка предпочтений
3. Применение rate limiting (user-level, global)
4. Для каждого включенного канала:
   a. Рендер шаблона с данными
   b. Постановка в очередь канала
5. Worker берет сообщение
6. Отправка во внешний провайдер (FCM, Twilio)
7. Обработка ответа:
   - Успех: Логирование доставки, обновление статуса
   - Сбой: Retry с backoff или DLQ
8. Трекинг аналитики (отправлено, доставлено, открыто)
```

### Паттерны надежности

**1. Retry с Exponential Backoff**
```python
def send_with_retry(notification, max_retries=3):
    for attempt in range(max_retries):
        try:
            return send(notification)
        except TransientError:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    # Переместить в dead letter queue
    dlq.send(notification)
```

**2. Circuit Breaker по провайдеру**
```
Если Twilio упал 5 раз за 1 минуту:
  - Открыть circuit
  - Failover на backup провайдер (Vonage)
  - Периодически тестировать Twilio
  - Закрыть circuit когда здоров
```

**3. Идемпотентность**
```python
def send_notification(request):
    idempotency_key = f"{request.user_id}:{request.type}:{request.data_hash}"

    if cache.exists(idempotency_key):
        return "Дубликат, пропущено"

    result = process_notification(request)
    cache.set(idempotency_key, result, ttl=24h)
    return result
```

### Масштабирование

| Компонент | Стратегия масштабирования |
|-----------|---------------------------|
| API | Горизонтальное (stateless) |
| Queue | Партиционирование по user_id |
| Workers | Авто-масштабирование по глубине очереди |
| Templates | Кеш в Redis |
| Preferences | Кеш с write-through |

---

## Follow-ups

- How do you handle notification prioritization?
- How do you implement notification batching/digests?
- How do you track notification delivery across channels?

## Related Questions

### Prerequisites (Easier)
- [[q-pubsub-patterns--system-design--medium]] - Pub/Sub
- [[q-message-queues-event-driven--system-design--medium]] - Message queues

### Related (Same Level)
- [[q-design-twitter--system-design--hard]] - Twitter
- [[q-design-instagram--system-design--hard]] - Instagram

### Advanced (Harder)
- [[q-rate-limiting-algorithms--system-design--medium]] - Rate limiting details
