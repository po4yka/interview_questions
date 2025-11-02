---
id: sysdes-008
title: "Message Queues and Event-Driven Architecture / Очереди сообщений и событийная архитектура"
aliases: ["Event-Driven Architecture", "Message Queues", "Очереди сообщений", "Событийная архитектура"]
topic: system-design
subtopics: [async-processing, event-driven, kafka, message-queues, rabbitmq]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-message-queues, q-caching-strategies--system-design--medium, q-microservices-vs-monolith--system-design--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [async, difficulty/medium, event-driven, kafka, message-queues, system-design]
sources: [https://en.wikipedia.org/wiki/Message_queue]
date created: Sunday, October 12th 2025, 8:40:11 pm
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)
> Что такое очереди сообщений? Когда их следует использовать? В чём разница между Kafka, RabbitMQ и другими системами обмена сообщениями?

# Question (EN)
> What are message queues? When should you use them? What are the differences between Kafka, RabbitMQ, and other messaging systems?

---

## Ответ (RU)

**Теория асинхронной коммуникации:**
Message Queue - паттерн асинхронной коммуникации, где producers отправляют сообщения в очередь, а consumers обрабатывают их независимо. Решает проблемы tight coupling, cascading failures и позволяет строить масштабируемые, resilient системы.

**Основные преимущества:**
- **Decoupling** - producer/consumer независимы
- **Scalability** - можно добавлять consumers для обработки нагрузки
- **Reliability** - сообщения сохраняются при отказе consumer
- **Async processing** - не блокирует producer
- **Load leveling** - сглаживание пиков нагрузки

**Паттерны обмена сообщениями:**

**1. Point-to-Point (Очередь):**

*Теория:* Одно сообщение обрабатывается одним consumer. Используется для распределения задач между workers. Гарантирует, что каждая задача обработана ровно один раз.

*Архитектура:* Producer → [Queue] → Consumer 1/2/3 (round-robin)

*Сценарии:* Task distribution (отправка email, обработка изображений, генерация отчётов)

```kotlin
// Point-to-Point: отправка email
@Service
class EmailService(private val rabbitTemplate: RabbitTemplate) {
    fun sendEmailAsync(email: Email) {
        rabbitTemplate.convertAndSend("email-queue", EmailMessage(email))
        // Возвращается сразу, email отправляется асинхронно
    }
}

@RabbitListener(queues = ["email-queue"])
fun processEmail(message: EmailMessage) {
    emailSender.send(message)  // Один worker обработает
}
```

**2. Publish-Subscribe (Topic):**

*Теория:* Одно сообщение получают все подписанные consumers. Используется для event notifications. Каждый consumer получает копию сообщения и обрабатывает независимо.

*Архитектура:* Producer → [Topic] → Consumer 1 (Email) + Consumer 2 (SMS) + Consumer 3 (Analytics)

*Сценарии:* Event notifications (регистрация пользователя → email + analytics + CRM)

```kotlin
// Pub-Sub: событие регистрации пользователя
@Service
class UserService(private val kafkaTemplate: KafkaTemplate<String, UserEvent>) {
    suspend fun registerUser(user: User): User {
        val savedUser = userRepository.save(user)
        kafkaTemplate.send("user-events", UserRegisteredEvent(savedUser.id))
        return savedUser
    }
}

// Каждый consumer получает копию события
@KafkaListener(topics = ["user-events"], groupId = "email-service")
fun handleUserRegistered(event: UserRegisteredEvent) {
    emailService.sendWelcomeEmail(event.email)
}

@KafkaListener(topics = ["user-events"], groupId = "analytics-service")
fun handleUserRegistered(event: UserRegisteredEvent) {
    analytics.trackUserRegistration(event.userId)
}
```

**Сравнение популярных систем:**

**1. RabbitMQ (AMQP):**

*Теория:* Traditional message broker с акцентом на гибкую маршрутизацию и надёжную доставку. Использует exchanges для routing логики. Удаляет сообщения после подтверждения обработки.

*Архитектура:* Producer → Exchange (routing) → Queue → Consumer

*Особенности:*
- Message acknowledgment (подтверждение обработки)
- Dead letter queues (для failed messages)
- Priority queues (приоритеты сообщений)
- Flexible routing (exchanges: direct, topic, fanout, headers)
- Push-based (broker отправляет consumers)

*Сценарии:* Complex routing, RPC patterns, task queues, traditional messaging

```kotlin
// RabbitMQ с routing
@Configuration
class RabbitConfig {
    @Bean fun orderQueue() = Queue("orders", true)  // Durable
    @Bean fun topicExchange() = TopicExchange("order-exchange")
    @Bean fun binding() = BindingBuilder.bind(orderQueue()).to(topicExchange()).with("order.created")
}
```

**2. Apache Kafka:**

*Теория:* Distributed event streaming platform с акцентом на throughput и event log. Сообщения хранятся как append-only log, consumers читают в своём темпе. Retention policy определяет, как долго хранятся сообщения.

*Архитектура:* Producer → Topic (partitions) → Consumer Groups

*Особенности:*
- High throughput (миллионы msg/sec)
- Event log (сообщения не удаляются после чтения)
- Partitioning (горизонтальное масштабирование)
- Consumer groups (load balancing + broadcast)
- Pull-based (consumers читают в своём темпе)
- Replay capability (можно перечитать старые сообщения)

*Сценарии:* Event streaming, log aggregation, real-time analytics, event sourcing

```kotlin
// Kafka с partitioning
@Service
class OrderService(private val kafkaTemplate: KafkaTemplate<String, OrderEvent>) {
    fun createOrder(order: Order) {
        kafkaTemplate.send(
            "orders",
            order.userId.toString(),  // Partition key - все заказы пользователя в одной partition
            OrderCreatedEvent(order)
        )
    }
}
```

**3. AWS SQS (Simple Queue Service):**

*Теория:* Managed message queue service с акцентом на простоту и интеграцию с AWS. Не требует управления инфраструктурой. Два типа: Standard (at-least-once, неупорядоченная) и FIFO (exactly-once, упорядоченная).

*Особенности:*
- Fully managed (нет инфраструктуры)
- Auto-scaling
- Dead letter queues
- Visibility timeout (временная блокировка сообщения)
- Standard vs FIFO queues

*Сценарии:* AWS-based systems, simple queuing, serverless architectures

```kotlin
// AWS SQS
val sqsClient = SqsClient.create()
sqsClient.sendMessage {
    queueUrl = "https://sqs.region.amazonaws.com/account/queue"
    messageBody = json.encodeToString(OrderEvent(order))
}
```

**4. Redis Pub/Sub & Streams:**

*Теория:* In-memory messaging с низкой latency. Pub/Sub - fire-and-forget (нет persistence). Streams - append-only log с persistence и consumer groups (похоже на Kafka, но проще).

*Особенности:*
- Very low latency (in-memory)
- Pub/Sub: no persistence, fire-and-forget
- Streams: persistent, consumer groups, replay
- Simple setup

*Сценарии:* Real-time notifications, chat, caching + messaging, simple event streaming

```kotlin
// Redis Streams
redisTemplate.opsForStream<String, Any>().add(
    StreamRecords.newRecord()
        .ofObject(OrderEvent(order))
        .withStreamKey("orders")
)
```

**Сравнительная таблица:**

| Система | Throughput | Persistence | Ordering | Сложность | Сценарий |
|---------|-----------|-------------|----------|-----------|----------|
| RabbitMQ | Средний | Да | Да | Средняя | Complex routing, RPC |
| Kafka | Очень высокий | Да (log) | Да (partition) | Высокая | Event streaming, analytics |
| AWS SQS | Средний | Да | FIFO only | Низкая | AWS integration, simple |
| Redis | Очень высокий | Streams only | Streams only | Низкая | Real-time, low latency |

**Ключевые концепции:**

**1. Message Acknowledgment:**
*Теория:* Consumer подтверждает успешную обработку. Если нет ack - сообщение возвращается в очередь. Гарантирует at-least-once delivery.

**2. Dead Letter Queue (DLQ):**
*Теория:* Очередь для сообщений, которые не удалось обработать после N попыток. Позволяет изолировать проблемные сообщения и не блокировать остальные.

**3. Consumer Groups (Kafka):**
*Теория:* Группа consumers, где каждая partition читается только одним consumer из группы. Обеспечивает load balancing внутри группы и broadcast между группами.

**4. Idempotency:**
*Теория:* Операция может быть выполнена несколько раз с тем же результатом. Критично для at-least-once delivery - сообщение может быть доставлено повторно.

**5. Backpressure:**
*Теория:* Механизм контроля скорости producer, когда consumers не успевают обрабатывать. Kafka - pull-based (consumer контролирует), RabbitMQ - prefetch limit.

**Когда использовать Message Queues:**

✅ **Используйте:**
- Асинхронная обработка (email, reports, image processing)
- Decoupling сервисов (microservices)
- Load leveling (сглаживание пиков)
- Event-driven architecture
- Retry logic для failed operations
- Distributed transactions (saga pattern)

❌ **Не используйте:**
- Синхронные запросы (используйте REST/gRPC)
- Real-time требования < 10ms (используйте in-memory)
- Simple CRUD операции
- Когда нужен immediate response

## Answer (EN)

**Asynchronous Communication Theory:**
Message Queue - asynchronous communication pattern where producers send messages to queue, and consumers process them independently. Solves tight coupling, cascading failures problems and enables building scalable, resilient systems.

**Main Benefits:**
- **Decoupling** - producer/consumer independent
- **Scalability** - can add consumers to handle load
- **Reliability** - messages persisted if consumer fails
- **Async processing** - doesn't block producer
- **Load leveling** - smoothing traffic spikes

**Messaging Patterns:**

**1. Point-to-Point (Queue):**

*Theory:* One message processed by one consumer. Used for task distribution between workers. Guarantees each task processed exactly once.

*Architecture:* Producer → [Queue] → Consumer 1/2/3 (round-robin)

*Use cases:* Task distribution (email sending, image processing, report generation)

```kotlin
// Point-to-Point: email sending
@Service
class EmailService(private val rabbitTemplate: RabbitTemplate) {
    fun sendEmailAsync(email: Email) {
        rabbitTemplate.convertAndSend("email-queue", EmailMessage(email))
        // Returns immediately, email sent asynchronously
    }
}

@RabbitListener(queues = ["email-queue"])
fun processEmail(message: EmailMessage) {
    emailSender.send(message)  // One worker processes
}
```

**2. Publish-Subscribe (Topic):**

*Theory:* One message received by all subscribed consumers. Used for event notifications. Each consumer gets message copy and processes independently.

*Architecture:* Producer → [Topic] → Consumer 1 (Email) + Consumer 2 (SMS) + Consumer 3 (Analytics)

*Use cases:* Event notifications (user registration → email + analytics + CRM)

```kotlin
// Pub-Sub: user registration event
@Service
class UserService(private val kafkaTemplate: KafkaTemplate<String, UserEvent>) {
    suspend fun registerUser(user: User): User {
        val savedUser = userRepository.save(user)
        kafkaTemplate.send("user-events", UserRegisteredEvent(savedUser.id))
        return savedUser
    }
}

// Each consumer gets event copy
@KafkaListener(topics = ["user-events"], groupId = "email-service")
fun handleUserRegistered(event: UserRegisteredEvent) {
    emailService.sendWelcomeEmail(event.email)
}

@KafkaListener(topics = ["user-events"], groupId = "analytics-service")
fun handleUserRegistered(event: UserRegisteredEvent) {
    analytics.trackUserRegistration(event.userId)
}
```

**Popular Systems Comparison:**

**1. RabbitMQ (AMQP):**

*Theory:* Traditional message broker focused on flexible routing and reliable delivery. Uses exchanges for routing logic. Deletes messages after processing acknowledgment.

*Architecture:* Producer → Exchange (routing) → Queue → Consumer

*Features:*
- Message acknowledgment (processing confirmation)
- Dead letter queues (for failed messages)
- Priority queues (message priorities)
- Flexible routing (exchanges: direct, topic, fanout, headers)
- Push-based (broker pushes to consumers)

*Use cases:* Complex routing, RPC patterns, task queues, traditional messaging

```kotlin
// RabbitMQ with routing
@Configuration
class RabbitConfig {
    @Bean fun orderQueue() = Queue("orders", true)  // Durable
    @Bean fun topicExchange() = TopicExchange("order-exchange")
    @Bean fun binding() = BindingBuilder.bind(orderQueue()).to(topicExchange()).with("order.created")
}
```

**2. Apache Kafka:**

*Theory:* Distributed event streaming platform focused on throughput and event log. Messages stored as append-only log, consumers read at their own pace. Retention policy determines how long messages are kept.

*Architecture:* Producer → Topic (partitions) → Consumer Groups

*Features:*
- High throughput (millions msg/sec)
- Event log (messages not deleted after reading)
- Partitioning (horizontal scaling)
- Consumer groups (load balancing + broadcast)
- Pull-based (consumers read at their pace)
- Replay capability (can re-read old messages)

*Use cases:* Event streaming, log aggregation, real-time analytics, event sourcing

```kotlin
// Kafka with partitioning
@Service
class OrderService(private val kafkaTemplate: KafkaTemplate<String, OrderEvent>) {
    fun createOrder(order: Order) {
        kafkaTemplate.send(
            "orders",
            order.userId.toString(),  // Partition key - all user orders in one partition
            OrderCreatedEvent(order)
        )
    }
}
```

**3. AWS SQS (Simple Queue Service):**

*Theory:* Managed message queue service focused on simplicity and AWS integration. No infrastructure management needed. Two types: Standard (at-least-once, unordered) and FIFO (exactly-once, ordered).

*Features:*
- Fully managed (no infrastructure)
- Auto-scaling
- Dead letter queues
- Visibility timeout (temporary message lock)
- Standard vs FIFO queues

*Use cases:* AWS-based systems, simple queuing, serverless architectures

```kotlin
// AWS SQS
val sqsClient = SqsClient.create()
sqsClient.sendMessage {
    queueUrl = "https://sqs.region.amazonaws.com/account/queue"
    messageBody = json.encodeToString(OrderEvent(order))
}
```

**4. Redis Pub/Sub & Streams:**

*Theory:* In-memory messaging with low latency. Pub/Sub - fire-and-forget (no persistence). Streams - append-only log with persistence and consumer groups (similar to Kafka, but simpler).

*Features:*
- Very low latency (in-memory)
- Pub/Sub: no persistence, fire-and-forget
- Streams: persistent, consumer groups, replay
- Simple setup

*Use cases:* Real-time notifications, chat, caching + messaging, simple event streaming

```kotlin
// Redis Streams
redisTemplate.opsForStream<String, Any>().add(
    StreamRecords.newRecord()
        .ofObject(OrderEvent(order))
        .withStreamKey("orders")
)
```

**Comparison Table:**

| System | Throughput | Persistence | Ordering | Complexity | Use Case |
|--------|-----------|-------------|----------|-----------|----------|
| RabbitMQ | Medium | Yes | Yes | Medium | Complex routing, RPC |
| Kafka | Very High | Yes (log) | Yes (partition) | High | Event streaming, analytics |
| AWS SQS | Medium | Yes | FIFO only | Low | AWS integration, simple |
| Redis | Very High | Streams only | Streams only | Low | Real-time, low latency |

**Key Concepts:**

**1. Message Acknowledgment:**
*Theory:* Consumer confirms successful processing. If no ack - message returns to queue. Guarantees at-least-once delivery.

**2. Dead Letter Queue (DLQ):**
*Theory:* Queue for messages that failed processing after N attempts. Allows isolating problematic messages without blocking others.

**3. Consumer Groups (Kafka):**
*Theory:* Group of consumers where each partition read by only one consumer from group. Provides load balancing within group and broadcast between groups.

**4. Idempotency:**
*Theory:* Operation can be executed multiple times with same result. Critical for at-least-once delivery - message may be delivered again.

**5. Backpressure:**
*Theory:* Mechanism to control producer speed when consumers can't keep up. Kafka - pull-based (consumer controls), RabbitMQ - prefetch limit.

**When to Use Message Queues:**

✅ **Use:**
- Asynchronous processing (email, reports, image processing)
- Service decoupling (microservices)
- Load leveling (smoothing spikes)
- Event-driven architecture
- Retry logic for failed operations
- Distributed transactions (saga pattern)

❌ **Don't use:**
- Synchronous requests (use REST/gRPC)
- Real-time requirements < 10ms (use in-memory)
- Simple CRUD operations
- When immediate response needed

---

## Follow-ups

- How do you handle message ordering in distributed systems?
- What is the difference between at-least-once and exactly-once delivery?
- How do you implement saga pattern for distributed transactions?

## Related Questions

### Prerequisites (Easier)
- [[q-rest-api-design-best-practices--system-design--medium]] - API design
- [[q-caching-strategies--system-design--medium]] - Caching patterns

### Related (Same Level)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Distributed systems theory
