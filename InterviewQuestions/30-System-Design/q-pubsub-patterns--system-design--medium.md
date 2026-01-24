---
id: sysdes-027
title: Pub/Sub Patterns
aliases:
- Publish Subscribe
- Pub/Sub
- Event-Driven Architecture
topic: system-design
subtopics:
- messaging
- architecture
- decoupling
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-message-queues-event-driven--system-design--medium
- q-websockets-sse-long-polling--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- messaging
- difficulty/medium
- architecture
- system-design
anki_cards:
- slug: sysdes-027-0-en
  language: en
  anki_id: 1769158890690
  synced_at: '2026-01-23T13:49:17.762153'
- slug: sysdes-027-0-ru
  language: ru
  anki_id: 1769158890716
  synced_at: '2026-01-23T13:49:17.763871'
---
# Question (EN)
> What is the Pub/Sub pattern? How does it differ from message queues, and when would you use each?

# Vopros (RU)
> Что такое паттерн Pub/Sub? Чем он отличается от очередей сообщений, и когда использовать каждый?

---

## Answer (EN)

**Pub/Sub (Publish-Subscribe)** is a messaging pattern where publishers send messages to topics without knowing who will receive them, and subscribers receive messages from topics they're interested in.

### How Pub/Sub Works

```
Publishers                Topic              Subscribers
    │                       │                    │
[Publisher A] ──publish──→ [Topic] ──deliver──→ [Subscriber 1]
[Publisher B] ──publish──→ [Topic] ──deliver──→ [Subscriber 2]
                            │      ──deliver──→ [Subscriber 3]

All subscribers receive all messages on the topic
```

### Pub/Sub vs Message Queue

**Message Queue (Point-to-Point)**
```
Producer → [Queue] → Consumer A (gets message)
                   ✗ Consumer B (doesn't get it)

One message consumed by exactly one consumer
```

**Pub/Sub (Broadcast)**
```
Publisher → [Topic] → Subscriber A (gets message)
                   → Subscriber B (gets message)

One message delivered to all subscribers
```

### Comparison Table

| Aspect | Message Queue | Pub/Sub |
|--------|---------------|---------|
| Delivery | One consumer | All subscribers |
| Coupling | Producer knows queue | Publishers don't know subscribers |
| Use case | Task distribution | Event notification |
| Message fate | Deleted after consumption | Delivered to all |
| Scaling | Add consumers | Add subscribers |

### Pub/Sub Patterns

**1. Topic-Based**
```
Publisher → "orders" topic → All order subscribers
Publisher → "payments" topic → All payment subscribers

Subscribers filter by topic name
```

**2. Content-Based**
```
Publisher → Broker → Evaluates message content
                  → Routes based on filters

Subscriber: "Give me orders where amount > 1000"
```

**3. Fan-Out**
```
Single message → Multiple queues/subscribers

[Order Created] → [Email Queue]
               → [Inventory Queue]
               → [Analytics Queue]
```

### Implementation Example

```python
# Using Redis Pub/Sub
import redis

# Publisher
def publish_order_event(order):
    r = redis.Redis()
    r.publish('orders', json.dumps(order))

# Subscriber
def subscribe_to_orders():
    r = redis.Redis()
    pubsub = r.pubsub()
    pubsub.subscribe('orders')

    for message in pubsub.listen():
        if message['type'] == 'message':
            order = json.loads(message['data'])
            process_order(order)
```

```python
# Using Kafka
from kafka import KafkaProducer, KafkaConsumer

# Publisher
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('orders', json.dumps(order).encode())

# Subscriber (Consumer Group for load balancing)
consumer = KafkaConsumer(
    'orders',
    group_id='order-processors',
    bootstrap_servers='localhost:9092'
)
for message in consumer:
    process_order(json.loads(message.value))
```

### Technologies

| Technology | Type | Strengths |
|------------|------|-----------|
| Apache Kafka | Log-based | High throughput, durability |
| RabbitMQ | Broker | Flexible routing, protocols |
| Redis Pub/Sub | In-memory | Low latency, simple |
| AWS SNS | Cloud | Managed, integrations |
| Google Pub/Sub | Cloud | Managed, global |

### When to Use Pub/Sub

**Use Pub/Sub when:**
- Multiple consumers need same event
- Decoupling between services
- Event-driven architecture
- Audit/logging requirements
- Real-time notifications

**Use Message Queue when:**
- Work distribution among workers
- Guaranteed single processing
- Task queues (background jobs)
- Rate limiting / buffering

### Best Practices

1. **Idempotent subscribers** (handle duplicates)
2. **Dead letter queues** for failed messages
3. **Message ordering** considerations
4. **At-least-once vs exactly-once** semantics
5. **Schema versioning** for messages

---

## Otvet (RU)

**Pub/Sub (Publish-Subscribe)** - паттерн обмена сообщениями, где издатели отправляют сообщения в топики не зная, кто их получит, а подписчики получают сообщения из интересующих их топиков.

### Как работает Pub/Sub

```
Publishers                Topic              Subscribers
    │                       │                    │
[Publisher A] ──publish──→ [Topic] ──deliver──→ [Subscriber 1]
[Publisher B] ──publish──→ [Topic] ──deliver──→ [Subscriber 2]
                            │      ──deliver──→ [Subscriber 3]

Все подписчики получают все сообщения топика
```

### Pub/Sub vs Message Queue

**Message Queue (Point-to-Point)**
```
Producer → [Queue] → Consumer A (получает сообщение)
                   ✗ Consumer B (не получает)

Одно сообщение потребляется ровно одним consumer
```

**Pub/Sub (Broadcast)**
```
Publisher → [Topic] → Subscriber A (получает сообщение)
                   → Subscriber B (получает сообщение)

Одно сообщение доставляется всем подписчикам
```

### Сравнительная таблица

| Аспект | Message Queue | Pub/Sub |
|--------|---------------|---------|
| Доставка | Одному consumer | Всем подписчикам |
| Связанность | Producer знает очередь | Publishers не знают подписчиков |
| Применение | Распределение задач | Уведомление о событиях |
| Судьба сообщения | Удаляется после потребления | Доставляется всем |
| Масштабирование | Добавить consumers | Добавить подписчиков |

### Паттерны Pub/Sub

**1. Topic-Based**
```
Publisher → топик "orders" → Все подписчики заказов
Publisher → топик "payments" → Все подписчики платежей

Подписчики фильтруют по имени топика
```

**2. Content-Based**
```
Publisher → Broker → Оценивает содержимое сообщения
                  → Маршрутизирует по фильтрам

Подписчик: "Дай мне заказы где amount > 1000"
```

**3. Fan-Out**
```
Одно сообщение → Множество очередей/подписчиков

[Order Created] → [Email Queue]
               → [Inventory Queue]
               → [Analytics Queue]
```

### Пример реализации

```python
# Используя Redis Pub/Sub
import redis

# Publisher
def publish_order_event(order):
    r = redis.Redis()
    r.publish('orders', json.dumps(order))

# Subscriber
def subscribe_to_orders():
    r = redis.Redis()
    pubsub = r.pubsub()
    pubsub.subscribe('orders')

    for message in pubsub.listen():
        if message['type'] == 'message':
            order = json.loads(message['data'])
            process_order(order)
```

```python
# Используя Kafka
from kafka import KafkaProducer, KafkaConsumer

# Publisher
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('orders', json.dumps(order).encode())

# Subscriber (Consumer Group для балансировки)
consumer = KafkaConsumer(
    'orders',
    group_id='order-processors',
    bootstrap_servers='localhost:9092'
)
for message in consumer:
    process_order(json.loads(message.value))
```

### Технологии

| Технология | Тип | Преимущества |
|------------|-----|--------------|
| Apache Kafka | Log-based | Высокая пропускная способность, durability |
| RabbitMQ | Broker | Гибкая маршрутизация, протоколы |
| Redis Pub/Sub | In-memory | Низкая задержка, простой |
| AWS SNS | Cloud | Managed, интеграции |
| Google Pub/Sub | Cloud | Managed, глобальный |

### Когда использовать Pub/Sub

**Используйте Pub/Sub когда:**
- Несколько consumers нужно одно событие
- Декаплинг между сервисами
- Event-driven архитектура
- Требования аудита/логирования
- Real-time уведомления

**Используйте Message Queue когда:**
- Распределение работы между workers
- Гарантия однократной обработки
- Task queues (фоновые задачи)
- Rate limiting / буферизация

### Лучшие практики

1. **Идемпотентные подписчики** (обработка дубликатов)
2. **Dead letter queues** для failed сообщений
3. **Ordering сообщений** - учитывать
4. **At-least-once vs exactly-once** семантика
5. **Версионирование схемы** сообщений

---

## Follow-ups

- How does Kafka differ from traditional message brokers?
- What is event sourcing and how does it relate to Pub/Sub?
- How do you handle message ordering in distributed Pub/Sub?

## Related Questions

### Prerequisites (Easier)
- [[q-message-queues-event-driven--system-design--medium]] - Message queues

### Related (Same Level)
- [[q-websockets-sse-long-polling--system-design--medium]] - Real-time comms
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture

### Advanced (Harder)
- [[q-design-notification-system--system-design--hard]] - Notifications
