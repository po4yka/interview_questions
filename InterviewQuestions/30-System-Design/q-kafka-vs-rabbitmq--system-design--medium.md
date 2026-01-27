---
id: q-kafka-vs-rabbitmq
title: Kafka vs RabbitMQ vs ActiveMQ / Сравнение Kafka, RabbitMQ и ActiveMQ
aliases:
- Kafka vs RabbitMQ
- Message Broker Comparison
- Сравнение брокеров сообщений
topic: system-design
subtopics:
- message-queues
- distributed-systems
- comparison
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
- q-pubsub-patterns--system-design--medium
- q-event-sourcing--system-design--hard
created: 2026-01-26
updated: 2026-01-26
tags:
- comparison
- difficulty/medium
- kafka
- message-queues
- rabbitmq
- system-design
sources:
- https://kafka.apache.org/documentation/
- https://www.rabbitmq.com/documentation.html
- https://activemq.apache.org/components/classic/documentation
anki_cards:
- slug: q-kafka-vs-rabbitmq-0-en
  anki_id: null
  synced_at: null
- slug: q-kafka-vs-rabbitmq-0-ru
  anki_id: null
  synced_at: null
---

# Question (EN)

> What are the differences between Kafka, RabbitMQ, and ActiveMQ? When should you use each?

# Vopros (RU)

> В чём различия между Kafka, RabbitMQ и ActiveMQ? Когда следует использовать каждый?

---

## Answer (EN)

### Overview

All three are message brokers, but they have fundamentally different architectures and use cases:

| Broker | Core Model | Primary Use Case |
|--------|------------|------------------|
| **Kafka** | Distributed commit log | Event streaming, log aggregation |
| **RabbitMQ** | Traditional message broker (AMQP) | Task queues, RPC, complex routing |
| **ActiveMQ** | JMS-compliant enterprise broker | Enterprise integration, legacy systems |

---

### Apache Kafka

**Architecture:** Distributed append-only log with partitioned topics.

**Key Characteristics:**
- **Throughput:** Millions of messages/second
- **Message retention:** Configurable (time or size-based), messages persist after consumption
- **Ordering:** Guaranteed within partition only
- **Consumer model:** Pull-based with consumer groups
- **Replay:** Can reread historical messages

**How It Works:**
```
Producer → Topic (Partition 0, 1, 2...) → Consumer Group
                                        ↓
                          Each partition → One consumer in group
```

**Best For:**
- Event streaming and event sourcing
- Log aggregation (collecting logs from many services)
- Real-time analytics pipelines
- High-throughput data ingestion
- Microservices event-driven architecture

**Example Use Case:**
```kotlin
// Kafka: Event streaming for user activity
@Service
class ActivityTracker(private val kafka: KafkaTemplate<String, ActivityEvent>) {
    fun trackPageView(userId: String, page: String) {
        kafka.send("user-activity", userId, PageViewEvent(userId, page, Instant.now()))
        // Key = userId ensures all events for a user go to same partition (ordering)
    }
}

// Multiple consumer groups can read independently
@KafkaListener(topics = ["user-activity"], groupId = "analytics")
fun processForAnalytics(event: ActivityEvent) { /* real-time dashboard */ }

@KafkaListener(topics = ["user-activity"], groupId = "recommendations")
fun processForRecommendations(event: ActivityEvent) { /* ML pipeline */ }
```

---

### RabbitMQ

**Architecture:** Traditional message broker with exchanges and queues (AMQP protocol).

**Key Characteristics:**
- **Throughput:** Tens of thousands of messages/second
- **Message retention:** Messages removed after acknowledgment
- **Ordering:** Within single queue (can be affected by redelivery)
- **Consumer model:** Push-based with acknowledgments
- **Routing:** Flexible via exchanges (direct, topic, fanout, headers)

**How It Works:**
```
Producer → Exchange (routing logic) → Queue(s) → Consumer(s)
              ↓
    Direct: exact match
    Topic: pattern match (order.*)
    Fanout: broadcast to all queues
```

**Best For:**
- Task distribution (work queues)
- RPC patterns (request/reply)
- Complex routing requirements
- When message acknowledgment is critical
- Traditional enterprise messaging

**Example Use Case:**
```kotlin
// RabbitMQ: Task queue for image processing
@Service
class ImageProcessor(private val rabbit: RabbitTemplate) {
    fun submitForProcessing(imageId: String, operations: List<String>) {
        rabbit.convertAndSend(
            "image-exchange",
            "image.process",
            ImageTask(imageId, operations)
        )
    }
}

@RabbitListener(queues = ["image-processing-queue"])
fun processImage(task: ImageTask, channel: Channel, @Header(AmqpHeaders.DELIVERY_TAG) tag: Long) {
    try {
        imageService.process(task)
        channel.basicAck(tag, false)  // Manual acknowledgment
    } catch (e: Exception) {
        channel.basicNack(tag, false, true)  // Requeue on failure
    }
}
```

---

### Apache ActiveMQ

**Architecture:** JMS-compliant enterprise message broker supporting multiple protocols.

**Key Characteristics:**
- **Throughput:** Moderate (thousands to tens of thousands/second)
- **Message retention:** Configurable, typically removed after consumption
- **Ordering:** Within queue/topic (FIFO)
- **Consumer model:** Both push and pull
- **Protocols:** JMS, AMQP, STOMP, MQTT, OpenWire

**Two Variants:**
- **ActiveMQ Classic:** Traditional, feature-rich, mature
- **ActiveMQ Artemis:** Next-gen, higher performance, non-blocking

**Best For:**
- Enterprise Java applications (JMS requirement)
- Legacy system integration
- Multi-protocol environments (IoT with MQTT, web with STOMP)
- When JMS compliance is mandatory
- Bridging different messaging systems

**Example Use Case:**
```kotlin
// ActiveMQ: Enterprise integration with JMS
@Service
class OrderProcessor(
    private val jmsTemplate: JmsTemplate
) {
    fun submitOrder(order: Order) {
        jmsTemplate.send("ORDER.QUEUE") { session ->
            session.createObjectMessage(order).apply {
                setStringProperty("orderType", order.type.name)
                setIntProperty("priority", order.priority)
            }
        }
    }
}

@JmsListener(destination = "ORDER.QUEUE", selector = "orderType = 'PRIORITY'")
fun processPriorityOrders(order: Order) {
    // JMS selector filters messages at broker level
    priorityOrderService.process(order)
}
```

---

### Comparison Table

| Feature | Kafka | RabbitMQ | ActiveMQ |
|---------|-------|----------|----------|
| **Model** | Distributed log | Message broker | JMS broker |
| **Throughput** | Very high (millions/sec) | Medium (tens of thousands/sec) | Medium (thousands/sec) |
| **Ordering** | Per partition | Per queue | Per queue/topic |
| **Persistence** | Log-based (configurable retention) | Until acknowledged | Configurable |
| **Message Replay** | Yes (within retention) | No | Limited |
| **Routing** | Topic/partition key | Exchanges (flexible) | JMS selectors |
| **Protocol** | Kafka protocol | AMQP (primary) | JMS, AMQP, MQTT, STOMP |
| **Consumer Model** | Pull (consumer groups) | Push (with prefetch) | Both |
| **Complexity** | High (ZooKeeper/KRaft) | Medium | Medium |
| **Cloud-Native** | Yes (K8s-friendly) | Yes | Legacy focus |

---

### Use Case Decision Tree

```
Need message replay or event sourcing?
  └─ Yes → Kafka

Need complex routing (topic patterns, headers)?
  └─ Yes → RabbitMQ

JMS compliance required?
  └─ Yes → ActiveMQ

Need very high throughput (>100K msg/sec)?
  └─ Yes → Kafka

Simple task queue with acknowledgments?
  └─ Yes → RabbitMQ

Multi-protocol support (MQTT, STOMP)?
  └─ Yes → ActiveMQ

Microservices event-driven architecture?
  └─ Yes → Kafka

Traditional request/reply patterns?
  └─ Yes → RabbitMQ
```

---

### Key Trade-offs

**Kafka:**
- (+) Highest throughput, message replay, event sourcing
- (-) Operational complexity, no built-in routing, larger resource footprint

**RabbitMQ:**
- (+) Flexible routing, mature, easy to operate, good for RPC
- (-) Lower throughput, no native replay, message loss if not persisted

**ActiveMQ:**
- (+) JMS compliance, multi-protocol, enterprise features
- (-) Lower performance, aging architecture (Classic), less cloud-native

---

## Otvet (RU)

### Обзор

Все три являются брокерами сообщений, но имеют принципиально разные архитектуры и сценарии использования:

| Брокер | Модель | Основной сценарий |
|--------|--------|-------------------|
| **Kafka** | Распределённый журнал коммитов | Потоковая обработка событий, агрегация логов |
| **RabbitMQ** | Традиционный брокер сообщений (AMQP) | Очереди задач, RPC, сложная маршрутизация |
| **ActiveMQ** | JMS-совместимый корпоративный брокер | Корпоративная интеграция, legacy-системы |

---

### Apache Kafka

**Архитектура:** Распределённый append-only лог с партиционированными топиками.

**Ключевые характеристики:**
- **Пропускная способность:** Миллионы сообщений в секунду
- **Хранение сообщений:** Настраиваемое (по времени или размеру), сообщения сохраняются после чтения
- **Порядок:** Гарантирован только в пределах партиции
- **Модель потребления:** Pull-based с consumer groups
- **Перечитывание:** Можно перечитать исторические сообщения

**Как это работает:**
```
Producer → Topic (Partition 0, 1, 2...) → Consumer Group
                                        ↓
                          Каждая партиция → Один consumer в группе
```

**Лучше всего подходит для:**
- Потоковой обработки событий и event sourcing
- Агрегации логов (сбор логов со многих сервисов)
- Конвейеров real-time аналитики
- Высокопроизводительного приёма данных
- Event-driven архитектуры микросервисов

**Пример использования:**
```kotlin
// Kafka: Потоковая обработка активности пользователей
@Service
class ActivityTracker(private val kafka: KafkaTemplate<String, ActivityEvent>) {
    fun trackPageView(userId: String, page: String) {
        kafka.send("user-activity", userId, PageViewEvent(userId, page, Instant.now()))
        // Key = userId гарантирует, что все события пользователя попадут в одну партицию
    }
}

// Несколько consumer groups читают независимо
@KafkaListener(topics = ["user-activity"], groupId = "analytics")
fun processForAnalytics(event: ActivityEvent) { /* real-time дашборд */ }

@KafkaListener(topics = ["user-activity"], groupId = "recommendations")
fun processForRecommendations(event: ActivityEvent) { /* ML пайплайн */ }
```

---

### RabbitMQ

**Архитектура:** Традиционный брокер сообщений с exchanges и очередями (протокол AMQP).

**Ключевые характеристики:**
- **Пропускная способность:** Десятки тысяч сообщений в секунду
- **Хранение сообщений:** Сообщения удаляются после подтверждения
- **Порядок:** В пределах одной очереди (может нарушаться при redelivery)
- **Модель потребления:** Push-based с подтверждениями
- **Маршрутизация:** Гибкая через exchanges (direct, topic, fanout, headers)

**Как это работает:**
```
Producer → Exchange (логика маршрутизации) → Queue(s) → Consumer(s)
              ↓
    Direct: точное совпадение
    Topic: паттерн (order.*)
    Fanout: broadcast во все очереди
```

**Лучше всего подходит для:**
- Распределения задач (work queues)
- RPC паттернов (запрос/ответ)
- Сложных требований к маршрутизации
- Когда критично подтверждение обработки сообщений
- Традиционного корпоративного обмена сообщениями

**Пример использования:**
```kotlin
// RabbitMQ: Очередь задач для обработки изображений
@Service
class ImageProcessor(private val rabbit: RabbitTemplate) {
    fun submitForProcessing(imageId: String, operations: List<String>) {
        rabbit.convertAndSend(
            "image-exchange",
            "image.process",
            ImageTask(imageId, operations)
        )
    }
}

@RabbitListener(queues = ["image-processing-queue"])
fun processImage(task: ImageTask, channel: Channel, @Header(AmqpHeaders.DELIVERY_TAG) tag: Long) {
    try {
        imageService.process(task)
        channel.basicAck(tag, false)  // Ручное подтверждение
    } catch (e: Exception) {
        channel.basicNack(tag, false, true)  // Вернуть в очередь при ошибке
    }
}
```

---

### Apache ActiveMQ

**Архитектура:** JMS-совместимый корпоративный брокер сообщений с поддержкой множества протоколов.

**Ключевые характеристики:**
- **Пропускная способность:** Умеренная (тысячи — десятки тысяч/сек)
- **Хранение сообщений:** Настраиваемое, обычно удаляются после потребления
- **Порядок:** В пределах очереди/топика (FIFO)
- **Модель потребления:** И push, и pull
- **Протоколы:** JMS, AMQP, STOMP, MQTT, OpenWire

**Два варианта:**
- **ActiveMQ Classic:** Традиционный, богатый функционал, зрелый
- **ActiveMQ Artemis:** Следующее поколение, выше производительность, неблокирующий

**Лучше всего подходит для:**
- Корпоративных Java-приложений (требование JMS)
- Интеграции с legacy-системами
- Мультипротокольных сред (IoT с MQTT, веб со STOMP)
- Когда обязательна JMS-совместимость
- Связывания различных систем обмена сообщениями

**Пример использования:**
```kotlin
// ActiveMQ: Корпоративная интеграция с JMS
@Service
class OrderProcessor(
    private val jmsTemplate: JmsTemplate
) {
    fun submitOrder(order: Order) {
        jmsTemplate.send("ORDER.QUEUE") { session ->
            session.createObjectMessage(order).apply {
                setStringProperty("orderType", order.type.name)
                setIntProperty("priority", order.priority)
            }
        }
    }
}

@JmsListener(destination = "ORDER.QUEUE", selector = "orderType = 'PRIORITY'")
fun processPriorityOrders(order: Order) {
    // JMS-селектор фильтрует сообщения на уровне брокера
    priorityOrderService.process(order)
}
```

---

### Сравнительная таблица

| Характеристика | Kafka | RabbitMQ | ActiveMQ |
|----------------|-------|----------|----------|
| **Модель** | Распределённый лог | Брокер сообщений | JMS-брокер |
| **Пропускная способность** | Очень высокая (млн/сек) | Средняя (десятки тыс/сек) | Средняя (тысячи/сек) |
| **Порядок** | В пределах партиции | В пределах очереди | В пределах очереди/топика |
| **Персистентность** | На основе лога (настраиваемое хранение) | До подтверждения | Настраиваемая |
| **Перечитывание** | Да (в пределах retention) | Нет | Ограниченно |
| **Маршрутизация** | Топик/ключ партиции | Exchanges (гибкая) | JMS-селекторы |
| **Протокол** | Kafka protocol | AMQP (основной) | JMS, AMQP, MQTT, STOMP |
| **Модель потребления** | Pull (consumer groups) | Push (с prefetch) | Оба |
| **Сложность** | Высокая (ZooKeeper/KRaft) | Средняя | Средняя |
| **Cloud-Native** | Да (K8s-friendly) | Да | Фокус на legacy |

---

### Дерево принятия решений

```
Нужно перечитывание сообщений или event sourcing?
  └─ Да → Kafka

Нужна сложная маршрутизация (паттерны топиков, headers)?
  └─ Да → RabbitMQ

Требуется JMS-совместимость?
  └─ Да → ActiveMQ

Нужна очень высокая пропускная способность (>100K msg/sec)?
  └─ Да → Kafka

Простая очередь задач с подтверждениями?
  └─ Да → RabbitMQ

Поддержка нескольких протоколов (MQTT, STOMP)?
  └─ Да → ActiveMQ

Event-driven архитектура микросервисов?
  └─ Да → Kafka

Традиционные паттерны запрос/ответ?
  └─ Да → RabbitMQ
```

---

### Ключевые компромиссы

**Kafka:**
- (+) Высочайшая пропускная способность, перечитывание сообщений, event sourcing
- (-) Операционная сложность, нет встроенной маршрутизации, больше ресурсов

**RabbitMQ:**
- (+) Гибкая маршрутизация, зрелый, прост в эксплуатации, хорош для RPC
- (-) Ниже пропускная способность, нет нативного replay, возможна потеря сообщений без персистентности

**ActiveMQ:**
- (+) JMS-совместимость, мультипротокольность, корпоративные функции
- (-) Ниже производительность, устаревающая архитектура (Classic), менее cloud-native
