---
id: 20251012-203116
title: "Microservices vs Monolith Architecture / Микросервисы vs Монолитная архитектура"
aliases: ["Microservices vs Monolith", "Микросервисы vs Монолит"]
topic: system-design
subtopics: [architecture, distributed-systems, microservices, monolith, scalability]
question_kind: system-design
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-microservices, q-load-balancing-strategies--system-design--medium, q-message-queues-event-driven--system-design--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [architecture, difficulty/hard, distributed-systems, microservices, system-design]
sources: [https://en.wikipedia.org/wiki/Microservices]
date created: Sunday, October 12th 2025, 8:31:16 pm
date modified: Saturday, October 25th 2025, 8:27:44 pm
---

# Вопрос (RU)
> Каковы ключевые различия между микросервисами и монолитной архитектурой? Когда следует использовать каждый подход, и каковы компромиссы?

# Question (EN)
> What are the key differences between microservices and monolithic architecture? When should you use each, and what are the trade-offs?

---

## Ответ (RU)

**Теория архитектурных подходов:**
Выбор между монолитом и микросервисами - фундаментальное архитектурное решение, влияющее на скорость разработки, масштабируемость, организацию команды и операционную сложность. Каждый подход имеет свои преимущества и вызовы.

**Монолитная архитектура:**

*Теория:* Единое, unified приложение, где все компоненты тесно связаны и развёртываются как одна единица. Все модули (UI, business logic, data access) работают в одном процессе и используют одну базу данных. ACID транзакции работают из коробки.

*Архитектура:*
```
Monolithic Application
├─ UI Layer
├─ Business Logic (User, Order, Payment, Inventory)
└─ Single Database
→ Single Deployment Unit
```

*Преимущества:*
- Простая разработка (один codebase, легко понять)
- Легкая отладка (один процесс, stack traces работают)
- ACID транзакции (database transactions across all modules)
- Производительность (нет network overhead между компонентами)
- Простое развёртывание (один artifact)
- Нет сложности distributed systems

*Недостатки:*
- Масштабируемость (нужно масштабировать всё приложение целиком)
- Technology lock-in (один язык/framework для всего)
- Риск развёртывания (малое изменение требует полного redeployment)
- Bottleneck разработки (команды мешают друг другу)
- Долгое время сборки (большой codebase)
- Сложность понимания (со временем становится "big ball of mud")

*Сценарии:* Startups, MVP, small teams, simple domains, CRUD applications

```kotlin
// Монолит: все сервисы в одном приложении
@Service
class OrderService(
    private val userService: UserService,        // Прямая зависимость
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService
) {
    @Transactional  // ACID транзакция across all services
    fun placeOrder(order: Order): Order {
        val user = userService.getUser(order.userId)
        inventoryService.reserveItems(order.items)
        paymentService.processPayment(order.payment)
        return orderRepo.save(order)
    }
}
```

**Микросервисная архитектура:**

*Теория:* Приложение, состоящее из небольших, независимых сервисов, которые коммуницируют по сети. Каждый сервис - отдельное приложение со своей базой данных, может быть написан на разных языках, развёртывается независимо. Database per service pattern.

*Архитектура:*
```
API Gateway/Load Balancer
├─ User Service → User DB
├─ Order Service → Order DB
├─ Inventory Service → Inventory DB
└─ Payment Service → Payment DB
→ Independent deployment, scaling, database
```

*Преимущества:*
- Независимое масштабирование (scale только нужные сервисы)
- Technology flexibility (разные языки/frameworks для разных сервисов)
- Независимое развёртывание (изменение одного сервиса не требует redeployment других)
- Team autonomy (команды работают независимо)
- Fault isolation (падение одного сервиса не роняет всё)
- Easier to understand (каждый сервис маленький и focused)

*Недостатки:*
- Distributed systems complexity (network latency, failures, consistency)
- Нет ACID транзакций (нужны distributed transaction patterns: Saga, 2PC)
- Сложная отладка (distributed tracing нужен)
- Operational overhead (множество deployments, monitoring, logging)
- Data consistency challenges (eventual consistency)
- Network overhead (HTTP/gRPC calls между сервисами)

*Сценарии:* Large teams, complex domains, need independent scaling, polyglot requirements

```kotlin
// Микросервис: Order Service (отдельное приложение)
@Service
class OrderService(
    private val userClient: UserServiceClient,      // HTTP call
    private val inventoryClient: InventoryServiceClient,
    private val paymentClient: PaymentServiceClient
) {
    suspend fun placeOrder(order: Order): Order {
        // Network calls - нет ACID транзакций
        val user = userClient.getUser(order.userId)  // HTTP GET

        // Saga pattern для distributed transaction
        try {
            inventoryClient.reserveItems(order.items)
            paymentClient.processPayment(order.payment)
            return orderRepo.save(order)
        } catch (e: Exception) {
            // Compensating transaction
            inventoryClient.releaseItems(order.items)
            throw e
        }
    }
}
```

**Сравнительная таблица:**

| Аспект | Монолит | Микросервисы |
|--------|---------|--------------|
| Deployment | Один unit | Множество независимых |
| Scaling | Всё приложение | Отдельные сервисы |
| Technology | Один stack | Polyglot возможен |
| Transactions | ACID из коробки | Distributed (Saga, 2PC) |
| Complexity | Низкая | Высокая (distributed) |
| Team size | Small-medium | Large |
| Development speed | Быстрый старт | Медленный старт, быстрее позже |
| Debugging | Легко | Сложно (distributed tracing) |
| Data consistency | Strong | Eventual |
| Network overhead | Нет | Да (HTTP/gRPC) |

**Ключевые паттерны микросервисов:**

**1. API Gateway:**
*Теория:* Единая точка входа для всех клиентов. Маршрутизирует запросы к нужным сервисам, агрегирует ответы, обрабатывает authentication/authorization, rate limiting.

```kotlin
// API Gateway routing
@RestController
class ApiGateway(
    private val userClient: UserServiceClient,
    private val orderClient: OrderServiceClient
) {
    @GetMapping("/api/user-profile/{id}")
    suspend fun getUserProfile(id: Long): UserProfile {
        // Aggregate data from multiple services
        val user = userClient.getUser(id)
        val orders = orderClient.getUserOrders(id)
        return UserProfile(user, orders)
    }
}
```

**2. Service Discovery:**
*Теория:* Автоматическое обнаружение сервисов. Сервисы регистрируются в registry (Consul, Eureka), клиенты запрашивают адреса динамически. Позволяет auto-scaling и dynamic routing.

**3. Circuit Breaker:**
*Теория:* Защита от cascading failures. Если сервис недоступен, circuit breaker открывается и возвращает fallback response вместо бесконечных retry. Состояния: Closed (работает), Open (fallback), Half-Open (проверка).

```kotlin
// Circuit Breaker pattern
@Service
class OrderService(private val inventoryClient: InventoryServiceClient) {
    @CircuitBreaker(name = "inventory", fallbackMethod = "inventoryFallback")
    suspend fun checkInventory(itemId: Long): Boolean {
        return inventoryClient.isAvailable(itemId)
    }

    fun inventoryFallback(itemId: Long, ex: Exception): Boolean {
        return false  // Assume unavailable if service down
    }
}
```

**4. Saga Pattern (Distributed Transactions):**
*Теория:* Управление distributed transactions через последовательность локальных транзакций. Каждый шаг публикует event. Если шаг fails - выполняются compensating transactions для rollback предыдущих шагов.

*Типы:*
- **Choreography** - каждый сервис слушает events и решает, что делать
- **Orchestration** - центральный orchestrator управляет flow

```kotlin
// Saga Orchestrator
class OrderSaga(
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService
) {
    suspend fun execute(order: Order) {
        try {
            // Step 1: Reserve inventory
            inventoryService.reserve(order.items)
            // Step 2: Process payment
            paymentService.charge(order.payment)
            // Step 3: Complete order
            orderService.complete(order)
        } catch (e: Exception) {
            // Compensating transactions (rollback)
            inventoryService.release(order.items)
            paymentService.refund(order.payment)
            throw e
        }
    }
}
```

**5. Database per Service:**
*Теория:* Каждый микросервис имеет свою базу данных. Обеспечивает loose coupling и независимое scaling. Но усложняет queries across services и требует eventual consistency.

**Когда использовать монолит:**

✅ **Используйте монолит:**
- Startup/MVP (быстрый time-to-market)
- Small team (< 10 разработчиков)
- Simple domain (CRUD приложение)
- Неясные boundaries (domain ещё не устоялся)
- Limited resources (нет DevOps expertise)
- Strong consistency requirements

**Когда использовать микросервисы:**

✅ **Используйте микросервисы:**
- Large team (> 20-30 разработчиков)
- Complex domain (чёткие bounded contexts)
- Independent scaling needs (разные части нагружены по-разному)
- Polyglot requirements (разные технологии для разных задач)
- High availability requirements (fault isolation критичен)
- Mature DevOps culture (CI/CD, monitoring, orchestration)

**Эволюция архитектуры:**

*Теория:* Большинство успешных систем начинают с монолита и эволюционируют в микросервисы по мере роста. "Modular Monolith" - промежуточный шаг: монолит с чёткими module boundaries, который легко разделить позже.

**Путь миграции:**
1. **Start**: Monolith
2. **Grow**: Modular Monolith (чёткие boundaries)
3. **Extract**: Выделить первый микросервис (обычно наиболее нагруженный)
4. **Iterate**: Постепенно выделять другие сервисы
5. **Stabilize**: Hybrid (core monolith + key microservices)

## Answer (EN)

**Architectural Approaches Theory:**
Choosing between monolith and microservices is a fundamental architectural decision affecting development speed, scalability, team organization, and operational complexity. Each approach has its advantages and challenges.

**Monolithic Architecture:**

*Theory:* Single, unified application where all components are tightly coupled and deployed as one unit. All modules (UI, business logic, data access) run in one process and use single database. ACID transactions work out of the box.

*Architecture:*
```
Monolithic Application
├─ UI Layer
├─ Business Logic (User, Order, Payment, Inventory)
└─ Single Database
→ Single Deployment Unit
```

*Advantages:*
- Simple development (one codebase, easy to understand)
- Easy debugging (single process, stack traces work)
- ACID transactions (database transactions across all modules)
- Performance (no network overhead between components)
- Simple deployment (single artifact)
- No distributed systems complexity

*Disadvantages:*
- Scalability (must scale entire application)
- Technology lock-in (one language/framework for everything)
- Deployment risk (small change requires full redeployment)
- Development bottleneck (teams stepping on each other)
- Long build times (large codebase)
- Difficult to understand (becomes "big ball of mud" over time)

*Use cases:* Startups, MVP, small teams, simple domains, CRUD applications

```kotlin
// Monolith: all services in one application
@Service
class OrderService(
    private val userService: UserService,        // Direct dependency
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService
) {
    @Transactional  // ACID transaction across all services
    fun placeOrder(order: Order): Order {
        val user = userService.getUser(order.userId)
        inventoryService.reserveItems(order.items)
        paymentService.processPayment(order.payment)
        return orderRepo.save(order)
    }
}
```

**Microservices Architecture:**

*Theory:* Application composed of small, independent services communicating over network. Each service is separate application with own database, can be written in different languages, deployed independently. Database per service pattern.

*Architecture:*
```
API Gateway/Load Balancer
├─ User Service → User DB
├─ Order Service → Order DB
├─ Inventory Service → Inventory DB
└─ Payment Service → Payment DB
→ Independent deployment, scaling, database
```

*Advantages:*
- Independent scaling (scale only needed services)
- Technology flexibility (different languages/frameworks per service)
- Independent deployment (changing one service doesn't require redeploying others)
- Team autonomy (teams work independently)
- Fault isolation (one service failure doesn't bring down everything)
- Easier to understand (each service small and focused)

*Disadvantages:*
- Distributed systems complexity (network latency, failures, consistency)
- No ACID transactions (need distributed transaction patterns: Saga, 2PC)
- Complex debugging (distributed tracing needed)
- Operational overhead (multiple deployments, monitoring, logging)
- Data consistency challenges (eventual consistency)
- Network overhead (HTTP/gRPC calls between services)

*Use cases:* Large teams, complex domains, need independent scaling, polyglot requirements

```kotlin
// Microservice: Order Service (separate application)
@Service
class OrderService(
    private val userClient: UserServiceClient,      // HTTP call
    private val inventoryClient: InventoryServiceClient,
    private val paymentClient: PaymentServiceClient
) {
    suspend fun placeOrder(order: Order): Order {
        // Network calls - no ACID transactions
        val user = userClient.getUser(order.userId)  // HTTP GET

        // Saga pattern for distributed transaction
        try {
            inventoryClient.reserveItems(order.items)
            paymentClient.processPayment(order.payment)
            return orderRepo.save(order)
        } catch (e: Exception) {
            // Compensating transaction
            inventoryClient.releaseItems(order.items)
            throw e
        }
    }
}
```

**Comparison Table:**

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| Deployment | Single unit | Multiple independent |
| Scaling | Entire application | Individual services |
| Technology | Single stack | Polyglot possible |
| Transactions | ACID out of box | Distributed (Saga, 2PC) |
| Complexity | Low | High (distributed) |
| Team size | Small-medium | Large |
| Development speed | Fast start | Slow start, faster later |
| Debugging | Easy | Hard (distributed tracing) |
| Data consistency | Strong | Eventual |
| Network overhead | None | Yes (HTTP/gRPC) |

**Key Microservices Patterns:**

**1. API Gateway:**
*Theory:* Single entry point for all clients. Routes requests to appropriate services, aggregates responses, handles authentication/authorization, rate limiting.

```kotlin
// API Gateway routing
@RestController
class ApiGateway(
    private val userClient: UserServiceClient,
    private val orderClient: OrderServiceClient
) {
    @GetMapping("/api/user-profile/{id}")
    suspend fun getUserProfile(id: Long): UserProfile {
        // Aggregate data from multiple services
        val user = userClient.getUser(id)
        val orders = orderClient.getUserOrders(id)
        return UserProfile(user, orders)
    }
}
```

**2. Service Discovery:**
*Theory:* Automatic service discovery. Services register in registry (Consul, Eureka), clients query addresses dynamically. Enables auto-scaling and dynamic routing.

**3. Circuit Breaker:**
*Theory:* Protection from cascading failures. If service unavailable, circuit breaker opens and returns fallback response instead of infinite retries. States: Closed (working), Open (fallback), Half-Open (testing).

```kotlin
// Circuit Breaker pattern
@Service
class OrderService(private val inventoryClient: InventoryServiceClient) {
    @CircuitBreaker(name = "inventory", fallbackMethod = "inventoryFallback")
    suspend fun checkInventory(itemId: Long): Boolean {
        return inventoryClient.isAvailable(itemId)
    }

    fun inventoryFallback(itemId: Long, ex: Exception): Boolean {
        return false  // Assume unavailable if service down
    }
}
```

**4. Saga Pattern (Distributed Transactions):**
*Theory:* Managing distributed transactions through sequence of local transactions. Each step publishes event. If step fails - compensating transactions execute to rollback previous steps.

*Types:*
- **Choreography** - each service listens to events and decides what to do
- **Orchestration** - central orchestrator manages flow

```kotlin
// Saga Orchestrator
class OrderSaga(
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService
) {
    suspend fun execute(order: Order) {
        try {
            // Step 1: Reserve inventory
            inventoryService.reserve(order.items)
            // Step 2: Process payment
            paymentService.charge(order.payment)
            // Step 3: Complete order
            orderService.complete(order)
        } catch (e: Exception) {
            // Compensating transactions (rollback)
            inventoryService.release(order.items)
            paymentService.refund(order.payment)
            throw e
        }
    }
}
```

**5. Database per Service:**
*Theory:* Each microservice has its own database. Ensures loose coupling and independent scaling. But complicates queries across services and requires eventual consistency.

**When to Use Monolith:**

✅ **Use monolith:**
- Startup/MVP (fast time-to-market)
- Small team (< 10 developers)
- Simple domain (CRUD application)
- Unclear boundaries (domain not yet established)
- Limited resources (no DevOps expertise)
- Strong consistency requirements

**When to Use Microservices:**

✅ **Use microservices:**
- Large team (> 20-30 developers)
- Complex domain (clear bounded contexts)
- Independent scaling needs (different parts loaded differently)
- Polyglot requirements (different technologies for different tasks)
- High availability requirements (fault isolation critical)
- Mature DevOps culture (CI/CD, monitoring, orchestration)

**Architecture Evolution:**

*Theory:* Most successful systems start with monolith and evolve to microservices as they grow. "Modular Monolith" - intermediate step: monolith with clear module boundaries, easy to split later.

**Migration Path:**
1. **Start**: Monolith
2. **Grow**: Modular Monolith (clear boundaries)
3. **Extract**: Extract first microservice (usually most loaded)
4. **Iterate**: Gradually extract other services
5. **Stabilize**: Hybrid (core monolith + key microservices)

---

## Follow-ups

- How do you handle distributed transactions in microservices?
- What is the difference between choreography and orchestration in Saga pattern?
- How do you implement service discovery and load balancing?

## Related Questions

### Prerequisites (Easier)
- [[q-rest-api-design-best-practices--system-design--medium]] - API design
- [[q-message-queues-event-driven--system-design--medium]] - Async communication

### Related (Same Level)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies

### Advanced (Harder)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Distributed systems theory
- [[q-database-sharding-partitioning--system-design--hard]] - Data distribution
