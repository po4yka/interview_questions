---
id: 20251012-300008
title: "Message Queues and Event-Driven Architecture / Очереди сообщений и событийная архитектура"
topic: system-design
difficulty: medium
status: draft
created: 2025-10-12
tags: - system-design
  - message-queues
  - kafka
  - event-driven
  - async
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-system-design
related_questions:   - q-microservices-vs-monolith--system-design--hard
  - q-distributed-transactions--system-design--hard
  - q-event-sourcing-cqrs--system-design--hard
slug: message-queues-event-driven-system-design-medium
subtopics:   - message-queues
  - event-driven
  - kafka
  - rabbitmq
  - async-processing
---
# Question (EN)
> What are message queues? When should you use them? What are the differences between Kafka, RabbitMQ, and other messaging systems?

# Вопрос (RU)
> Что такое очереди сообщений? Когда их следует использовать? В чём разница между Kafka, RabbitMQ и другими системами обмена сообщениями?

---

## Answer (EN)

Synchronous communication between services creates tight coupling and can lead to cascading failures. Message queues and event-driven architecture enable asynchronous, scalable, and resilient systems.



### What are Message Queues?

**Message Queue** = Asynchronous communication pattern where producers send messages to a queue, and consumers process them independently.

```
Producer → [Queue] → Consumer

                  
 Producer  →  Queue  →  Consumer 
                  
   (Sends)          (Stores)           (Processes)
```

**Benefits:**
-  **Decoupling** - Producer/consumer independent
-  **Scalability** - Add more consumers to handle load
-  **Reliability** - Messages persisted if consumer fails
-  **Async processing** - Don't block producer
-  **Load leveling** - Handle traffic spikes

---

### Message Queue Patterns

### 1. Point-to-Point (Queue)

One message → One consumer

```
Producer → [Queue] → Consumer 1
                  ↘ Consumer 2  (Round-robin or similar)
                  ↘ Consumer 3
```

**Use case:** Task distribution (email sending, image processing)

```kotlin
// RabbitMQ Point-to-Point Example
@Service
class EmailService(private val rabbitTemplate: RabbitTemplate) {
    
    fun sendEmailAsync(email: Email) {
        rabbitTemplate.convertAndSend(
            "email-queue",
            EmailMessage(
                to = email.to,
                subject = email.subject,
                body = email.body
            )
        )
        // Returns immediately, email sent asynchronously
    }
}

@Service
class EmailConsumer {
    
    @RabbitListener(queues = ["email-queue"])
    fun processEmail(message: EmailMessage) {
        // Process email
        emailSender.send(message)
        log.info("Email sent to ${message.to}")
    }
}
```

### 2. Publish-Subscribe (Topic)

One message → Multiple consumers (all receive copy)

```
                    → Consumer 1 (Email)
Producer → [Topic] → Consumer 2 (SMS)
                    → Consumer 3 (Push)
```

**Use case:** Event notifications (user registered → send email, update analytics, send welcome)

```kotlin
// Kafka Pub-Sub Example
@Service
class UserService(private val kafkaTemplate: KafkaTemplate<String, UserEvent>) {
    
    suspend fun registerUser(user: User): User {
        val savedUser = userRepository.save(user)
        
        // Publish event - multiple consumers will receive
        kafkaTemplate.send(
            "user-events",
            UserRegisteredEvent(
                userId = savedUser.id,
                email = savedUser.email,
                timestamp = Instant.now()
            )
        )
        
        return savedUser
    }
}

// Consumer 1: Send welcome email
@Service
class EmailNotificationConsumer {
    
    @KafkaListener(topics = ["user-events"], groupId = "email-service")
    fun handleUserRegistered(event: UserRegisteredEvent) {
        emailService.sendWelcomeEmail(event.email)
    }
}

// Consumer 2: Update analytics
@Service
class AnalyticsConsumer {
    
    @KafkaListener(topics = ["user-events"], groupId = "analytics-service")
    fun handleUserRegistered(event: UserRegisteredEvent) {
        analytics.trackUserRegistration(event.userId)
    }
}

// Consumer 3: Send to CRM
@Service
class CRMConsumer {
    
    @KafkaListener(topics = ["user-events"], groupId = "crm-service")
    fun handleUserRegistered(event: UserRegisteredEvent) {
        crmService.createContact(event)
    }
}
```

---

### Popular Message Queue Systems

### 1. RabbitMQ (AMQP)

**Best for:** Complex routing, traditional message queuing

**Features:**
- Message acknowledgment
- Dead letter queues
- Priority queues
- Flexible routing (exchanges)
- Good for RPC patterns

**Architecture:**
```
Producer → Exchange → Queue → Consumer
          (routing)
```

**Implementation:**
```kotlin
@Configuration
class RabbitMQConfig {
    
    @Bean
    fun orderQueue() = Queue("orders", true)  // Durable
    
    @Bean
    fun orderExchange() = TopicExchange("order-exchange")
    
    @Bean
    fun binding() = BindingBuilder
        .bind(orderQueue())
        .to(orderExchange())
        .with("order.created")
}

@Service
class OrderService(private val rabbitTemplate: RabbitTemplate) {
    
    fun placeOrder(order: Order) {
        rabbitTemplate.convertAndSend(
            "order-exchange",
            "order.created",
            OrderCreatedEvent(order.id, order.total)
        )
    }
}

@Service
class OrderProcessor {
    
    @RabbitListener(queues = ["orders"])
    fun processOrder(event: OrderCreatedEvent) {
        // Process order
        // Auto-acknowledgment on success
        // Retry on failure (can configure)
    }
}
```

**Pros:**
- Easy to set up
- Flexible routing
- Message acknowledgment
- Good documentation

**Cons:**
- Not designed for huge throughput
- Can lose messages if not configured properly
- Single broker can be bottleneck

---

### 2. Apache Kafka

**Best for:** High throughput, event streaming, real-time data pipelines

**Features:**
- Distributed, partitioned log
- High throughput (millions/sec)
- Message retention (days/weeks)
- Replay messages
- Exactly-once semantics

**Architecture:**
```
Producers → Topic (partitioned) → Consumer Groups
            Partition 0
            Partition 1
            Partition 2
```

**Implementation:**
```kotlin
@Configuration
class KafkaConfig {
    
    @Bean
    fun producerFactory(): ProducerFactory<String, OrderEvent> {
        return DefaultKafkaProducerFactory(mapOf(
            ProducerConfig.BOOTSTRAP_SERVERS_CONFIG to "localhost:9092",
            ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG to StringSerializer::class.java,
            ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG to JsonSerializer::class.java,
            ProducerConfig.ACKS_CONFIG to "all",  // Wait for all replicas
            ProducerConfig.RETRIES_CONFIG to 3
        ))
    }
}

@Service
class OrderEventPublisher(
    private val kafkaTemplate: KafkaTemplate<String, OrderEvent>
) {
    suspend fun publishOrderCreated(order: Order) {
        val event = OrderCreatedEvent(
            orderId = order.id,
            userId = order.userId,
            total = order.total,
            items = order.items,
            timestamp = Instant.now()
        )
        
        // Partition by userId for ordering guarantee
        kafkaTemplate.send(
            "order-events",
            order.userId.toString(),  // Key (determines partition)
            event
        ).get()  // Wait for acknowledgment
    }
}

@Service
class OrderEventConsumer {
    
    @KafkaListener(
        topics = ["order-events"],
        groupId = "order-processor",
        concurrency = "3"  // 3 consumer threads
    )
    fun handleOrderCreated(
        event: OrderCreatedEvent,
        @Header(KafkaHeaders.RECEIVED_PARTITION) partition: Int,
        @Header(KafkaHeaders.OFFSET) offset: Long
    ) {
        log.info("Processing order ${event.orderId} from partition $partition, offset $offset")
        
        // Process order
        orderProcessor.process(event)
        
        // Kafka auto-commits offset after successful processing
    }
}
```

**Kafka Partitioning:**
```kotlin
// Messages with same key go to same partition
// Guarantees ordering within partition

Producer:
  userId=123 → Partition 0 
  userId=456 → Partition 1  Ordering preserved per partition
  userId=123 → Partition 0 

Consumer Group:
  Consumer 1 → Partition 0  (processes userId=123 in order)
  Consumer 2 → Partition 1  (processes userId=456 in order)
  Consumer 3 → Partition 2
```

**Pros:**
- Extremely high throughput
- Horizontal scaling (partitions)
- Message replay capability
- Persistent storage
- Exactly-once semantics

**Cons:**
- Complex setup/operation
- Steeper learning curve
- Requires ZooKeeper (or KRaft)
- Overkill for simple use cases

---

### 3. AWS SQS/SNS

**SQS** = Simple Queue Service (queue)
**SNS** = Simple Notification Service (pub/sub)

**Best for:** AWS-native applications, managed service

```kotlin
@Service
class SQSService(private val sqsClient: SqsClient) {
    
    suspend fun sendMessage(message: String) {
        sqsClient.sendMessage {
            queueUrl = "https://sqs.us-east-1.amazonaws.com/123456/my-queue"
            messageBody = message
            delaySeconds = 10  // Delay delivery
        }
    }
    
    suspend fun receiveMessages(): List<Message> {
        val response = sqsClient.receiveMessage {
            queueUrl = "https://sqs.us-east-1.amazonaws.com/123456/my-queue"
            maxNumberOfMessages = 10
            waitTimeSeconds = 20  // Long polling
        }
        
        return response.messages
    }
    
    suspend fun deleteMessage(receiptHandle: String) {
        sqsClient.deleteMessage {
            queueUrl = "https://sqs.us-east-1.amazonaws.com/123456/my-queue"
            this.receiptHandle = receiptHandle
        }
    }
}

// SNS Pub/Sub
@Service
class SNSService(private val snsClient: SnsClient) {
    
    suspend fun publishEvent(event: UserEvent) {
        snsClient.publish {
            topicArn = "arn:aws:sns:us-east-1:123456:user-events"
            message = Json.encodeToString(event)
            messageAttributes = mapOf(
                "eventType" to MessageAttributeValue.builder()
                    .dataType("String")
                    .stringValue(event.type)
                    .build()
            )
        }
    }
}
```

**Pros:**
- Fully managed (no ops)
- Auto-scaling
- Integrated with AWS
- Pay per use

**Cons:**
- AWS lock-in
- Higher latency than Kafka
- Limited message size (256KB)
- Limited throughput per queue

---

### Comparison Matrix

| Feature | RabbitMQ | Kafka | AWS SQS/SNS |
|---------|----------|-------|-------------|
| **Use Case** | Task queues, RPC | Event streaming, logs | AWS-native apps |
| **Throughput** | Thousands/sec | Millions/sec | Thousands/sec |
| **Message Size** | No limit | 1MB default | 256KB |
| **Retention** | Until consumed | Days/weeks | 14 days max |
| **Ordering** | Queue-level | Partition-level | FIFO queues |
| **Replay** | No | Yes | No |
| **Complexity** | Medium | High | Low (managed) |
| **Ops** | Self-managed | Self-managed | Fully managed |
| **Cost** | Infrastructure | Infrastructure | Pay per request |

---

### Event-Driven Architecture Patterns

### 1. Event Notification

```kotlin
// Service publishes event when something happens
@Service
class OrderService {
    suspend fun createOrder(order: Order): Order {
        val savedOrder = repository.save(order)
        
        // Publish event (fire and forget)
        eventBus.publish(OrderCreatedEvent(savedOrder.id))
        
        return savedOrder
    }
}

// Other services react to event
@Service
class InventoryService {
    @EventListener
    suspend fun onOrderCreated(event: OrderCreatedEvent) {
        reserveInventory(event.orderId)
    }
}
```

### 2. Event-Carried State Transfer

```kotlin
// Event contains all necessary data (no need to query source)
data class OrderCreatedEvent(
    val orderId: Long,
    val userId: Long,
    val items: List<OrderItem>,  // Full data
    val totalAmount: BigDecimal,
    val shippingAddress: Address,
    val timestamp: Instant
)

// Consumer has all info needed, no additional queries
@Service
class ShippingService {
    @KafkaListener(topics = ["order-events"])
    suspend fun onOrderCreated(event: OrderCreatedEvent) {
        // Has all data needed to create shipping label
        createShippingLabel(
            address = event.shippingAddress,
            items = event.items
        )
    }
}
```

### 3. Event Sourcing

```kotlin
// Store events, not current state
sealed class OrderEvent {
    abstract val orderId: Long
    abstract val timestamp: Instant
}

data class OrderCreatedEvent(
    override val orderId: Long,
    val userId: Long,
    val items: List<OrderItem>,
    override val timestamp: Instant
) : OrderEvent()

data class OrderShippedEvent(
    override val orderId: Long,
    val trackingNumber: String,
    override val timestamp: Instant
) : OrderEvent()

// Reconstruct current state from events
class Order {
    fun applyEvents(events: List<OrderEvent>): OrderState {
        var state = OrderState.CREATED
        
        events.forEach { event ->
            when (event) {
                is OrderCreatedEvent -> state = OrderState.CREATED
                is OrderShippedEvent -> state = OrderState.SHIPPED
                // ...
            }
        }
        
        return state
    }
}
```

---

### Real-World Example: E-commerce Order Processing

```kotlin
// 1. User places order
@Service
class OrderService(
    private val kafkaTemplate: KafkaTemplate<String, OrderEvent>
) {
    suspend fun placeOrder(request: CreateOrderRequest): Order {
        val order = Order(
            userId = request.userId,
            items = request.items,
            status = OrderStatus.PENDING
        )
        
        val savedOrder = repository.save(order)
        
        // Publish event to Kafka
        kafkaTemplate.send(
            "order-events",
            savedOrder.userId.toString(),
            OrderCreatedEvent(
                orderId = savedOrder.id,
                userId = savedOrder.userId,
                items = savedOrder.items,
                total = savedOrder.total
            )
        )
        
        return savedOrder
    }
}

// 2. Inventory service reserves items
@Service
class InventoryEventConsumer {
    @KafkaListener(topics = ["order-events"], groupId = "inventory-service")
    suspend fun onOrderCreated(event: OrderCreatedEvent) {
        try {
            inventoryService.reserveItems(event.items)
            
            // Publish success event
            kafkaTemplate.send(
                "inventory-events",
                InventoryReservedEvent(event.orderId)
            )
        } catch (e: OutOfStockException) {
            // Publish failure event
            kafkaTemplate.send(
                "inventory-events",
                InventoryReservationFailedEvent(event.orderId, e.message)
            )
        }
    }
}

// 3. Payment service processes payment
@Service
class PaymentEventConsumer {
    @KafkaListener(topics = ["inventory-events"], groupId = "payment-service")
    suspend fun onInventoryReserved(event: InventoryReservedEvent) {
        try {
            val order = orderService.getOrder(event.orderId)
            paymentService.processPayment(order.userId, order.total)
            
            // Publish success
            kafkaTemplate.send(
                "payment-events",
                PaymentProcessedEvent(event.orderId)
            )
        } catch (e: PaymentFailedException) {
            // Publish failure - triggers compensation
            kafkaTemplate.send(
                "payment-events",
                PaymentFailedEvent(event.orderId)
            )
        }
    }
}

// 4. Shipping service creates shipment
@Service
class ShippingEventConsumer {
    @KafkaListener(topics = ["payment-events"], groupId = "shipping-service")
    suspend fun onPaymentProcessed(event: PaymentProcessedEvent) {
        val order = orderService.getOrder(event.orderId)
        val shipment = shippingService.createShipment(order)
        
        kafkaTemplate.send(
            "shipping-events",
            ShipmentCreatedEvent(event.orderId, shipment.trackingNumber)
        )
        
        // Update order status
        orderService.updateStatus(event.orderId, OrderStatus.SHIPPED)
    }
}

// 5. Notification service sends email
@Service
class NotificationEventConsumer {
    @KafkaListener(topics = ["shipping-events"], groupId = "notification-service")
    suspend fun onShipmentCreated(event: ShipmentCreatedEvent) {
        val order = orderService.getOrder(event.orderId)
        emailService.sendShippingNotification(
            email = order.user.email,
            trackingNumber = event.trackingNumber
        )
    }
}
```

**Benefits of this approach:**
- Each service independent
- Async processing (fast response to user)
- Scalable (add more consumers)
- Resilient (failures isolated)
- Auditable (event log)

---

### Key Takeaways

1. **Message Queues** = Async communication, decoupling
2. **Point-to-Point** = Task distribution (one consumer)
3. **Pub-Sub** = Event notification (multiple consumers)
4. **RabbitMQ** = Traditional queuing, complex routing
5. **Kafka** = High throughput, event streaming, replay
6. **SQS/SNS** = AWS managed, simple
7. **Event-Driven** = Services react to events, not direct calls
8. **Event Sourcing** = Store events, derive state
9. **Saga Pattern** = Distributed transactions via events
10. **Choose based on:** Throughput needs, ops capacity, cloud vs on-prem

---

## Ответ (RU)

Синхронная коммуникация между сервисами создаёт тесную связанность и может привести к каскадным сбоям. Очереди сообщений и событийная архитектура обеспечивают асинхронные, масштабируемые и устойчивые системы.



### Что такое очереди сообщений?

**Message Queue** = Паттерн асинхронной коммуникации, где производители отправляют сообщения в очередь, а потребители обрабатывают их независимо.

**Преимущества:**
-  **Разделение** - Producer/consumer независимы
-  **Масштабируемость** - Добавить больше consumers для обработки нагрузки
-  **Надёжность** - Сообщения сохраняются при сбое consumer
-  **Async обработка** - Не блокировать producer
-  **Выравнивание нагрузки** - Обработка пиков трафика

### Популярные системы очередей сообщений

### 1. RabbitMQ (AMQP)
**Лучше для:** Сложная маршрутизация, традиционные очереди сообщений

### 2. Apache Kafka
**Лучше для:** Высокая пропускная способность, потоковая передача событий

### 3. AWS SQS/SNS
**Лучше для:** AWS-native приложения, управляемый сервис

### Ключевые выводы

1. **Message Queues** = Async коммуникация, разделение
2. **Point-to-Point** = Распределение задач (один consumer)
3. **Pub-Sub** = Уведомление о событиях (несколько consumers)
4. **RabbitMQ** = Традиционные очереди, сложная маршрутизация
5. **Kafka** = Высокая пропускная способность, стриминг событий, replay
6. **SQS/SNS** = AWS управляемый, простой
7. **Event-Driven** = Сервисы реагируют на события
8. **Выбирайте исходя из:** Потребностей пропускной способности, операционных возможностей

## Follow-ups

1. What is the difference between message queues and event streaming?
2. How do you ensure message ordering in distributed systems?
3. What is exactly-once delivery and how does Kafka achieve it?
4. How do you handle poison messages (messages that always fail)?
5. What is the dead letter queue pattern?
6. How do you implement request-reply pattern with message queues?
7. What is event sourcing and when should you use it?
8. How do you handle schema evolution in event-driven systems?
9. What is the outbox pattern for reliable event publishing?
10. How do you monitor and debug event-driven architectures?

---

## Related Questions

### Android Implementation
- [[q-compose-canvas-graphics--jetpack-compose--hard]] - Data Structures
- [[q-cache-implementation-strategies--android--medium]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures

### Related Algorithms
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Data Structures
- [[q-advanced-graph-algorithms--algorithms--hard]] - Data Structures
- [[q-binary-search-trees-bst--algorithms--hard]] - Data Structures
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Data Structures
