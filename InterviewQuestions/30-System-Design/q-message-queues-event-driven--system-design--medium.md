---
id: sysdes-008
title: "Message Queues and Event-Driven Architecture / Очереди сообщений и событийная архитектура"
aliases: ["Event-Driven Architecture", "Message Queues", "Очереди сообщений", "Событийная архитектура"]
topic: system-design
subtopics: [async-processing, event-driven, kafka]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-architecture-patterns, q-caching-strategies--system-design--medium, q-microservices-vs-monolith--system-design--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [async, difficulty/medium, event-driven, kafka, message-queues, system-design]
sources: ["https://en.wikipedia.org/wiki/Message_queue"]

---

# Вопрос (RU)
> Что такое очереди сообщений? Когда их следует использовать? В чём разница между Kafka, RabbitMQ и другими системами обмена сообщениями?

# Question (EN)
> What are message queues? When should you use them? What are the differences between Kafka, RabbitMQ, and other messaging systems?

---

## Ответ (RU)

**Теория асинхронной коммуникации:**
Message `Queue` - паттерн асинхронной коммуникации, где producers отправляют сообщения в очередь, а consumers обрабатывают их независимо. Решает проблемы tight coupling, cascading failures и позволяет строить масштабируемые, resilient системы. См. также [[c-architecture-patterns]].

### Требования

- Функциональные:
  - Асинхронная доставка сообщений между сервисами
  - Надёжная обработка с возможностью повторной доставки
  - Поддержка разных паттернов (Point-to-Point, Pub/Sub)
- Нефункциональные:
  - Масштабируемость по нагрузке
  - Устойчивость к сбоям (failure isolation, retry, DLQ)
  - Гарантии доставки (at-least-once, по возможности exactly-once)
  - Низкая задержка и предсказуемая производительность

### Архитектура

- Продюсеры публикуют сообщения в брокер.
- Брокер сохраняет сообщения и маршрутизирует их в очереди/топики.
- Консьюмеры читают сообщения из очередей/топиков, обрабатывают и подтверждают.
- Для масштабирования добавляются инстансы консьюмеров и партиции/очереди.

**Основные преимущества:**
- **Decoupling** - producer/consumer независимы
- **Scalability** - можно добавлять consumers для обработки нагрузки
- **Reliability** - сообщения могут сохраняться при отказе consumer
- **Async processing** - не блокирует producer
- **Load leveling** - сглаживание пиков нагрузки

**Паттерны обмена сообщениями:**

**1. Point-to-Point (Очередь):**

*Теория:* Одно сообщение обрабатывается одним consumer из группы конкурирующих получателей. Используется для распределения задач между workers. Типичные брокеры обеспечивают как минимум at-least-once доставку; ровно-один-раз (exactly-once) требует дополнительной логики на уровне приложения (идемпотентность, дедупликация).

*Архитектура:* Producer → [`Queue`] → Consumer 1/2/3 (round-robin или аналогичный механизм распределения)

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
    emailSender.send(message)  // Одно сообщение будет обработано одним worker-ом
}
```

**2. Publish-Subscribe (Topic):**

*Теория:* Одно сообщение получают все подписанные consumers (или все подписанные группы). Используется для event notifications. Каждый consumer получает копию сообщения и обрабатывает независимо.

*Архитектура:* Producer → [Topic] → Consumer 1 (Email) + Consumer 2 (SMS) + Consumer 3 (Analytics)

*Сценарии:* Event notifications (регистрация пользователя → email + analytics + CRM)

```kotlin
// Pub-Sub: событие регистрации пользователя
@Service
class UserService(private val kafkaTemplate: KafkaTemplate<String, UserEvent>) {
    suspend fun registerUser(user: User): User {
        val savedUser = userRepository.save(user)
        // Событие содержит необходимые поля (например id и email)
        kafkaTemplate.send("user-events", UserRegisteredEvent(savedUser.id, savedUser.email))
        return savedUser
    }
}

// Каждый consumer получает копию события
@KafkaListener(topics = ["user-events"], groupId = "email-service")
fun handleUserRegisteredEmail(event: UserRegisteredEvent) {
    emailService.sendWelcomeEmail(event.email)
}

@KafkaListener(topics = ["user-events"], groupId = "analytics-service")
fun handleUserRegisteredAnalytics(event: UserRegisteredEvent) {
    analytics.trackUserRegistration(event.userId)
}
```

**Сравнение популярных систем:**

**1. RabbitMQ (AMQP):**

*Теория:* Traditional message broker с акцентом на гибкую маршрутизацию и надёжную доставку. Использует exchanges для routing логики. Обычно сообщения удаляются из очереди после подтверждения обработки consumer-ом.

*Архитектура:* Producer → Exchange (routing) → `Queue` → Consumer

*Особенности:*
- Message acknowledgment (подтверждение обработки)
- Dead letter queues (для failed messages)
- Priority queues (приоритеты сообщений)
- Flexible routing (exchanges: direct, topic, fanout, headers)
- Push-based (broker отправляет consumers)
- Типичная гарантия: at-least-once delivery при корректной конфигурации

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
- Event log (сообщения не удаляются сразу после чтения)
- Partitioning (горизонтальное масштабирование)
- Consumer groups (load balancing внутри группы, fan-out между группами)
- Pull-based (consumers читают в своём темпе)
- Replay capability (можно перечитать старые сообщения в пределах retention)

*Сценарии:* Event streaming, log aggregation, real-time analytics, event sourcing

```kotlin
// Kafka с partitioning
@Service
class OrderService(private val kafkaTemplate: KafkaTemplate<String, OrderEvent>) {
    fun createOrder(order: Order) {
        kafkaTemplate.send(
            "orders",
            order.userId.toString(),  // Partition key - все заказы пользователя в одной partition (при неизменном количестве партиций)
            OrderCreatedEvent(order)
        )
    }
}
```

**3. AWS SQS (Simple `Queue` `Service`):**

*Теория:* Managed message queue service с акцентом на простоту и интеграцию с AWS. Не требует управления инфраструктурой. Два типа: Standard (at-least-once, возможна внеочередность доставки) и FIFO (semantics, близкие к exactly-once processing и сохранению порядка внутри группы сообщений при соблюдении требований).

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

*Теория:* In-memory messaging с низкой latency. Pub/Sub - fire-and-forget best-effort доставка (нет встроенной персистентности и сообщений для оффлайн-подписчиков). Streams - append-only log с persistence и consumer groups (похоже на Kafka, но проще по функционалу).

*Особенности:*
- Very low latency (in-memory)
- Pub/Sub: no persistence, best-effort delivery
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
| RabbitMQ | Средний | Да | В пределах очереди; может нарушаться при редоставке и множественных consumers | Средняя | Complex routing, RPC |
| Kafka | Очень высокий | Да (log) | В пределах partition | Высокая | Event streaming, analytics |
| AWS SQS | Средний | Да | FIFO-очереди: порядок внутри группы сообщений; Standard: не гарантируется | Низкая | AWS integration, simple |
| Redis | Очень высокий | Streams only | Streams: в пределах stream/группы; Pub/Sub: нет | Низкая | Real-time, low latency |

**Ключевые концепции:**

**1. Message Acknowledgment:**
*Теория:* Consumer подтверждает успешную обработку. Если нет ack - сообщение может быть доставлено повторно. Это даёт at-least-once delivery; для избежания дублей требуется идемпотентность.

**2. Dead Letter `Queue` (DLQ):**
*Теория:* Очередь для сообщений, которые не удалось обработать после N попыток. Позволяет изолировать проблемные сообщения и не блокировать остальные.

**3. Consumer Groups (Kafka):**
*Теория:* Группа consumers, где каждая partition читается только одним consumer из группы. Обеспечивает load balancing внутри группы и "broadcast" между разными группами.

**4. Idempotency:**
*Теория:* Операция может быть выполнена несколько раз с тем же результатом. Критично для at-least-once delivery, так как сообщение может быть доставлено повторно.

**5. Backpressure:**
*Теория:* Механизм контроля скорости producer, когда consumers не успевают обрабатывать. Kafka - pull-based (consumer сам регулирует скорость чтения), RabbitMQ - prefetch limit и другие настройки.

**Когда использовать Message `Queues`:**

✅ **Используйте:**
- Асинхронная обработка (email, reports, image processing)
- Decoupling сервисов (microservices)
- Load leveling (сглаживание пиков)
- Event-driven architecture
- Retry logic для failed operations
- Distributed transactions (saga pattern)

❌ **Не используйте:**
- Строго синхронные запросы/ответы (лучше REST/gRPC)
- Жёсткие требования к ультранизкой задержке (например, около нескольких миллисекунд), где сетевой хоп через брокер нежелателен
- Очень простые CRUD-операции внутри одного приложения/БД
- Когда критичен немедленный ответ непосредственно от обрабатывающего сервиса

## Answer (EN)

**Asynchronous Communication Theory:**
Message `Queue` is an asynchronous communication pattern where producers send messages to a queue and consumers process them independently. It reduces tight coupling and cascading failures and enables building scalable, resilient systems. See also [[c-architecture-patterns]].

### Requirements

- Functional:
  - Asynchronous message delivery between services
  - Reliable processing with retries and redelivery
  - Support for multiple patterns (Point-to-Point, Pub/Sub)
- Non-functional:
  - Scalability under varying load
  - Fault tolerance and isolation (retries, DLQ)
  - Delivery guarantees (at-least-once, and where possible exactly-once semantics)
  - Low latency and predictable performance

### Architecture

- Producers publish messages to a broker.
- Broker persists and routes messages to queues/topics.
- Consumers read from queues/topics, process, and acknowledge.
- Scaling is achieved via more consumer instances and partitions/queues.

**Main Benefits:**
- **Decoupling** - producers/consumers are independent
- **Scalability** - can add consumers to handle load
- **Reliability** - messages can be persisted if a consumer fails
- **Async processing** - doesn't block producer
- **Load leveling** - smooths traffic spikes

**Messaging Patterns:**

**1. Point-to-Point (`Queue`):**

*Theory:* One message is processed by one consumer from a set of competing consumers. Used for task distribution between workers. Typical brokers provide at-least-once delivery; true exactly-once processing requires additional application-level logic (idempotency/deduplication).

*Architecture:* Producer → [`Queue`] → Consumer 1/2/3 (round-robin or similar distribution)

*Use cases:* Task distribution (email sending, image processing, report generation)

```kotlin
// Point-to-Point: email sending
@Service
class EmailService(private val rabbitTemplate: RabbitTemplate) {
    fun sendEmailAsync(email: Email) {
        rabbitTemplate.convertAndSend("email-queue", EmailMessage(email))
        // Returns immediately, email is sent asynchronously
    }
}

@RabbitListener(queues = ["email-queue"])
fun processEmail(message: EmailMessage) {
    emailSender.send(message)  // Each message is processed by one worker
}
```

**2. Publish-Subscribe (Topic):**

*Theory:* One message is received by all subscribed consumers (or all subscribed groups). Used for event notifications. Each consumer gets a copy and processes it independently.

*Architecture:* Producer → [Topic] → Consumer 1 (Email) + Consumer 2 (SMS) + Consumer 3 (Analytics)

*Use cases:* Event notifications (user registration → email + analytics + CRM)

```kotlin
// Pub-Sub: user registration event
@Service
class UserService(private val kafkaTemplate: KafkaTemplate<String, UserEvent>) {
    suspend fun registerUser(user: User): User {
        val savedUser = userRepository.save(user)
        // Event includes required fields (e.g., id and email)
        kafkaTemplate.send("user-events", UserRegisteredEvent(savedUser.id, savedUser.email))
        return savedUser
    }
}

// Each consumer gets a copy of the event
@KafkaListener(topics = ["user-events"], groupId = "email-service")
fun handleUserRegisteredEmail(event: UserRegisteredEvent) {
    emailService.sendWelcomeEmail(event.email)
}

@KafkaListener(topics = ["user-events"], groupId = "analytics-service")
fun handleUserRegisteredAnalytics(event: UserRegisteredEvent) {
    analytics.trackUserRegistration(event.userId)
}
```

**Popular Systems Comparison:**

**1. RabbitMQ (AMQP):**

*Theory:* Traditional message broker focused on flexible routing and reliable delivery. Uses exchanges for routing logic. Messages are usually removed from the queue after a consumer acknowledges successful processing.

*Architecture:* Producer → Exchange (routing) → `Queue` → Consumer

*Features:*
- Message acknowledgment (processing confirmation)
- Dead letter queues (for failed messages)
- Priority queues (message priorities)
- Flexible routing (exchanges: direct, topic, fanout, headers)
- Push-based (broker pushes to consumers)
- Typical guarantee: at-least-once delivery with proper configuration

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

*Theory:* Distributed event streaming platform focused on throughput and durable event logs. Messages are stored as an append-only log; consumers read at their own pace. Retention policy controls how long messages are kept.

*Architecture:* Producer → Topic (partitions) → Consumer Groups

*Features:*
- High throughput (millions msg/sec)
- Event log (messages are not immediately deleted after reading)
- Partitioning (horizontal scaling)
- Consumer groups (load balancing within a group, fan-out across groups)
- Pull-based (consumers read at their own pace)
- Replay capability (can re-read old messages within retention)

*Use cases:* Event streaming, log aggregation, real-time analytics, event sourcing

```kotlin
// Kafka with partitioning
@Service
class OrderService(private val kafkaTemplate: KafkaTemplate<String, OrderEvent>) {
    fun createOrder(order: Order) {
        kafkaTemplate.send(
            "orders",
            order.userId.toString(),  // Partition key - all orders of a user go to one partition (as long as partitioning is stable)
            OrderCreatedEvent(order)
        )
    }
}
```

**3. AWS SQS (Simple `Queue` `Service`):**

*Theory:* Managed message queue service focused on simplicity and AWS integration. No infrastructure management required. Two main types: Standard (at-least-once delivery, best-effort ordering) and FIFO (strong ordering and exactly-once processing semantics within constraints documented by AWS).

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

*Theory:* In-memory messaging with low latency. Pub/Sub is fire-and-forget best-effort delivery (no persistence and no delivery for offline subscribers). Streams are an append-only log with persistence and consumer groups (similar conceptually to Kafka, but simpler and in-memory-first).

*Features:*
- Very low latency (in-memory)
- Pub/Sub: no persistence, best-effort
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
| RabbitMQ | Medium | Yes | Per-queue; may be affected by redelivery and multiple consumers | Medium | Complex routing, RPC |
| Kafka | Very High | Yes (log) | Per partition | High | Event streaming, analytics |
| AWS SQS | Medium | Yes | FIFO queues: ordered within message group; Standard: not guaranteed | Low | AWS integration, simple |
| Redis | Very High | Streams only | Streams: ordered within a stream/group; Pub/Sub: none | Low | Real-time, low latency |

**Key Concepts:**

**1. Message Acknowledgment:**
*Theory:* Consumer confirms successful processing. If no ack is sent, the message may be redelivered. This provides at-least-once delivery; idempotency is required to handle duplicates safely.

**2. Dead Letter `Queue` (DLQ):**
*Theory:* `Queue` for messages that failed processing after N attempts. Allows isolating problematic messages without blocking others.

**3. Consumer Groups (Kafka):**
*Theory:* Group of consumers where each partition is read by only one consumer within that group. Provides load balancing within a group and fan-out/broadcast across different groups.

**4. Idempotency:**
*Theory:* Operation can be executed multiple times with the same result. Critical for at-least-once delivery because a message may be delivered more than once.

**5. Backpressure:**
*Theory:* Mechanism to control producer rate when consumers cannot keep up. Kafka is pull-based (consumer controls read rate), RabbitMQ supports backpressure via prefetch limits and related settings.

**When to Use Message `Queues`:**

✅ **Use:**
- Asynchronous processing (email, reports, image processing)
- `Service` decoupling (microservices)
- Load leveling (smoothing spikes)
- Event-driven architecture
- Retry logic for failed operations
- Distributed transactions (saga pattern)

❌ **Don't use:**
- Strict synchronous request/response flows (prefer REST/gRPC)
- Scenarios with hard ultra-low-latency requirements (e.g., a few milliseconds) where broker hops are unacceptable
- Very simple CRUD operations within a single app/DB boundary
- When an immediate response from the processing service itself is required

---

## Follow-ups

- How do you handle message ordering in distributed systems?
- What is the difference between at-least-once and exactly-once delivery?
- How do you implement saga pattern for distributed transactions?

## References

- [[c-architecture-patterns]]
- "https://en.wikipedia.org/wiki/Message_queue"

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