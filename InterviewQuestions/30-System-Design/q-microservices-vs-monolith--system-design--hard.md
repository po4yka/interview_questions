---
id: sysdes-001
title: "Microservices vs Monolith Architecture / Микросервисы vs Монолитная архитектура"
aliases: ["Microservices vs Monolith", "Микросервисы vs Монолит"]
topic: system-design
subtopics: [distributed-systems, microservices, scalability]
question_kind: system-design
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-architecture-patterns, q-load-balancing-strategies--system-design--medium, q-message-queues-event-driven--system-design--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [architecture, difficulty/hard, distributed-systems, microservices, system-design]
sources: ["https://en.wikipedia.org/wiki/Microservices"]

---
# Вопрос (RU)
> Каковы ключевые различия между микросервисами и монолитной архитектурой? Когда следует использовать каждый подход, и каковы компромиссы?

# Question (EN)
> What are the key differences between microservices and monolithic architecture? When should you use each, and what are the trade-offs?

---

## Ответ (RU)

**Теория архитектурных подходов:**
Выбор между монолитом и микросервисами - фундаментальное архитектурное решение, влияющее на скорость разработки, масштабируемость, организацию команды и операционную сложность. Каждый подход имеет свои преимущества и вызовы.

## Answer (EN)

**Architectural Approaches Theory:**
Choosing between monolith and microservices is a fundamental architectural decision affecting development speed, scalability, team organization, and operational complexity. Each approach has its advantages and challenges.

## Дополнительные Вопросы (RU)

- Как обрабатывать распределённые транзакции в микросервисной архитектуре?
- В чём разница между хореографией и оркестрацией в паттерне Saga?
- Как реализовать `service` discovery и балансировку нагрузки?

## Follow-ups

- How do you handle distributed transactions in microservices?
- What is the difference between choreography and orchestration in Saga pattern?
- How do you implement service discovery and load balancing?

## Ссылки (RU)

- [[c-architecture-patterns]]
- [[c-ci-cd]]
- "https://en.wikipedia.org/wiki/Microservices"

## References

- [[c-architecture-patterns]]
- [[c-ci-cd]]
- "https://en.wikipedia.org/wiki/Microservices"

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-rest-api-design-best-practices--system-design--medium]] - Проектирование API
- [[q-message-queues-event-driven--system-design--medium]] - Асинхронное взаимодействие

### Связанные (тот Же уровень)
- [[q-load-balancing-strategies--system-design--medium]] - Стратегии балансировки нагрузки
- [[q-horizontal-vertical-scaling--system-design--medium]] - Горизонтальное и вертикальное масштабирование

### Продвинутые (сложнее)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Теория распределённых систем
- [[q-database-sharding-partitioning--system-design--hard]] - Шардинг и партиционирование данных

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

## Краткая Версия (RU)
- Монолит проще в разработке, деплое и отладке, лучше подходит для небольших команд, MVP и доменов без чётких границ.
- Микросервисы дают независимое масштабирование, автономию команд и технологическую гибкость, но привносят сложность распределённых систем, DevOps и согласованности данных.
- Практический подход: начинать с хорошо спроектированного модульного монолита и эволюционировать к микросервисам при росте команды, нагрузки и ясности границ контекстов.

## Short Version (EN)
- Monolith is simpler to build, deploy, and debug; best for small teams, MVPs, and domains without clear boundaries.
- Microservices enable independent scaling, team autonomy, and tech flexibility, but introduce distributed systems, DevOps, and data consistency complexity.
- Practical guidance: start with a well-structured modular monolith and evolve to microservices when team size, load, and domain clarity justify the added complexity.

## Подробная Версия (RU)

### Требования
**Функциональные (typical):**
- Обслуживание различных доменных областей (пользователи, заказы, платежи и т.п.).
- Возможность добавлять новый функционал без длительных простоев.
**Нефункциональные:**
- Масштабируемость (горизонтальная/селективная).
- Надёжность и устойчивость к отказам.
- Применимость к структуре команды (несколько команд, независимая работа).
- Простота сопровождения и скорости поставки (CI/CD).
- Управляемая сложность: понятная архитектура, трассировка, мониторинг.

### Архитектура
Ниже — как те же требования удовлетворяются монолитом и микросервисами.

**Монолитная архитектура:**
*Теория:* Единое приложение, где все компоненты разворачиваются как одна единица. Все модули (UI, бизнес-логика, доступ к данным) работают в одном процессе и обычно используют одну общую базу данных. Это позволяет относительно просто использовать ACID-транзакции в пределах одного приложения и одной БД (т.е. «между модулями» в рамках общего транзакционного контура), но не гарантирует ACID для внешних или распределённых интеграций.
*Архитектура:*
```text
Monolithic Application
├─ UI Layer
├─ Business Logic (User, Order, Payment, Inventory)
└─ Single Database
→ Single Deployment Unit
```
*Преимущества:*
- Простая разработка (один codebase, легче понять)
- Легкая отладка (один процесс, stack traces работают)
- ACID-транзакции в рамках общей БД (транзакции могут охватывать несколько модулей, так как они используют одну базу данных)
- Производительность (нет сетевых оверхедов между компонентами внутри процесса)
- Простое развёртывание (один artifact)
- Нет сложности распределённых систем
*Недостатки:*
- Масштабируемость (нужно масштабировать всё приложение целиком)
- Technology lock-in (один язык/framework для всего)
- Риск развёртывания (малое изменение требует полного redeployment)
- Bottleneck разработки (команды мешают друг другу)
- Долгое время сборки (большой codebase)
- Сложность понимания (со временем превращается в "big ball of mud")
*Сценарии:* Startups, MVP, маленькие команды, простые домены, CRUD-приложения
```kotlin
// Монолит: все доменные сервисы в одном приложении и транзакционном контуре
@Service
class OrderService(
    private val userService: UserService,        // Прямая зависимость
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService,
    private val orderRepo: OrderRepository
) {
    @Transactional  // ACID-транзакция в рамках одной БД и одного приложения
    fun placeOrder(order: Order): Order {
        val user = userService.getUser(order.userId)
        inventoryService.reserveItems(order.items)
        paymentService.processPayment(order.payment)
        return orderRepo.save(order)
    }
}
```

**Микросервисная архитектура:**
*Теория:* Приложение, состоящее из небольших, независимых сервисов, которые коммуницируют по сети. Каждый сервис — отдельное приложение со своей базой данных (паттерн Database per `Service`), может быть написан на разных языках и развёртывается независимо. ACID-транзакции возможны внутри каждого сервиса и его локальной БД, но не существуют «из коробки» для операций, затрагивающих несколько сервисов и БД.
*Архитектура:*
```text
API Gateway/Load Balancer
├─ User Service → User DB
├─ Order Service → Order DB
├─ Inventory Service → Inventory DB
└─ Payment Service → Payment DB
→ Independent deployment, scaling, database
```
*Преимущества:*
- Независимое масштабирование (масштабируем только нужные сервисы)
- Технологическая гибкость (разные языки/frameworks для разных сервисов)
- Независимое развёртывание (изменение одного сервиса не требует redeployment других)
- Автономия команд (команды владеют сервисами и работают независимо)
- Изоляция отказов (падение одного сервиса не обязано ронять всё приложение)
- Проще понимать отдельно взятый сервис (каждый сервис маленький и сфокусированный), хотя общая картина системы сложнее
*Недостатки:*
- Сложность распределённых систем (сетевые задержки, частичные отказы, согласованность)
- Нет автоматических распределённых ACID-транзакций (нужны паттерны: Saga, 2PC и др.)
- Сложная отладка (нужны централизованные логи, метрики, distributed tracing)
- Операционный оверхед (множественные деплойменты, мониторинг, логирование, оркестрация)
- Проблемы согласованности данных (часто eventual consistency между сервисами)
- Сетевой оверхед (HTTP/gRPC вызовы между сервисами)
*Сценарии:* Большие команды, сложные домены, требования к независимому масштабированию, polyglot-стек, зрелая платформа и DevOps-практики
```kotlin
// Микросервис: Order Service (отдельное приложение)
@Service
class OrderService(
    private val userClient: UserServiceClient,          // HTTP/gRPC вызовы
    private val inventoryClient: InventoryServiceClient,
    private val paymentClient: PaymentServiceClient,
    private val orderRepo: OrderRepository
) {
    suspend fun placeOrder(order: Order): Order {
        // Сетевые вызовы — нет единой ACID-транзакции на все учаcтвуемые сервисы
        val user = userClient.getUser(order.userId)  // HTTP GET
        // Упрощённый пример Saga-подхода для распределённой операции
        try {
            inventoryClient.reserveItems(order.items)
            paymentClient.processPayment(order.payment)
            return orderRepo.save(order)
        } catch (e: Exception) {
            // Компенсирующие действия (в реальной саге компенсируются все затронутые шаги)
            inventoryClient.releaseItems(order.items)
            // Здесь также мог бы быть вызов компенсации платежа, если он уже прошёл
            throw e
        }
    }
}
```

**Сравнение:**
| Аспект | Монолит | Микросервисы |
|--------|---------|--------------|
| Deployment | Один unit | Множество независимых |
| Scaling | Всё приложение | Отдельные сервисы |
| Technology | Один stack | Polyglot возможен |
| Transactions | ACID в пределах общей БД | Локально ACID, между сервисами Saga/2PC и др. |
| Complexity | Ниже | Выше (распределённая система) |
| Team size | Small-medium | Large |
| Development speed | Быстрый старт | Медленный старт, быстрее при масштабировании |
| Debugging | Легко | Сложно (distributed tracing и централизованные логи) |
| Data consistency | Как правило сильная в рамках единой БД | Сильная локально, часто eventual между сервисами |
| Network overhead | Нет | Есть (HTTP/gRPC) |

**Ключевые паттерны микросервисов:**
1. API Gateway
2. `Service` Discovery
3. Circuit Breaker
4. Saga (распределённые транзакции)
5. Database per `Service`

**Когда использовать монолит:**
✅ Используйте монолит, если:
- Startup/MVP (быстрый time-to-market)
- Small team (< 10 разработчиков)
- Simple domain (CRUD-приложение)
- Неясные границы домена
- Ограниченные ресурсы, слабые DevOps-практики
- Нужна сильная согласованность в пределах одной системы

**Когда использовать микросервисы:**
✅ Используйте микросервисы, если:
- Large team (> 20-30 разработчиков)
- Complex domain (чёткие bounded contexts)
- Требуется независимое масштабирование
- Polyglot-требования
- Высокие требования к отказоустойчивости и изоляции отказов
- Зрелая DevOps-культура

**Эволюция архитектуры:**
Частый путь: монолит → модульный монолит → постепенное выделение микросервисов вокруг чётких границ и самых нагруженных частей.

## Detailed Version (EN)

### Requirements
**Functional (typical):**
- Support multiple domains (users, orders, payments, etc.).
- Allow adding new features without long downtime.
**Non-functional:**
- Scalability (horizontal/targeted).
- Reliability and fault tolerance.
- Fit to team structure (multiple teams, independent work).
- Maintainability and delivery speed (CI/CD).
- Manageable complexity: clear architecture, tracing, monitoring.

### Architecture
Below is how the same requirements are addressed by monolith vs microservices.

**Monolithic Architecture:**
*Theory:* A single application where all components are deployed as one unit. All modules (UI, business logic, data access) run in one process and usually share a single database. This makes it straightforward to use ACID transactions within one application and one DB (across modules within the same transactional boundary), but does not guarantee ACID for external or distributed integrations.
*Architecture:*
```text
Monolithic Application
├─ UI Layer
├─ Business Logic (User, Order, Payment, Inventory)
└─ Single Database
→ Single Deployment Unit
```
*Advantages:*
- Simple development (one codebase, easier to understand)
- Easy debugging (single process, straightforward stack traces)
- ACID transactions within the shared DB (transactions can span multiple modules because they share one database)
- Performance (no network overhead between in-process components)
- Simple deployment (single artifact)
- No distributed systems complexity
*Disadvantages:*
- Scalability (must scale the entire application)
- Technology lock-in (one language/framework for everything)
- Deployment risk (small change requires full redeployment)
- Development bottleneck (teams stepping on each other)
- Long build times (large codebase)
- Hard to understand over time (can become a "big ball of mud")
*Use cases:* Startups, MVPs, small teams, simple domains, CRUD applications
```kotlin
// Monolith: all domain services in one application and transactional boundary
@Service
class OrderService(
    private val userService: UserService,        // Direct dependency
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService,
    private val orderRepo: OrderRepository
) {
    @Transactional  // ACID transaction within a single DB and application
    fun placeOrder(order: Order): Order {
        val user = userService.getUser(order.userId)
        inventoryService.reserveItems(order.items)
        paymentService.processPayment(order.payment)
        return orderRepo.save(order)
    }
}
```

**Microservices Architecture:**
*Theory:* An application composed of small, independent services communicating over the network. Each service is a separate application with its own database (Database per `Service` pattern), can be written in different languages, and is deployed independently. ACID transactions are possible inside each service and its local DB, but you do not get ACID across multiple services/databases out of the box.
*Architecture:*
```text
API Gateway/Load Balancer
├─ User Service → User DB
├─ Order Service → Order DB
├─ Inventory Service → Inventory DB
└─ Payment Service → Payment DB
→ Independent deployment, scaling, database
```
*Advantages:*
- Independent scaling (scale only the services that need it)
- Technology flexibility (different languages/frameworks per service)
- Independent deployment (changing one service doesn't require redeploying others)
- Team autonomy (teams own services and work independently)
- Fault isolation (one service failing does not have to bring down the entire system)
- Easier to understand per service (each one small and focused), though overall system complexity is higher
*Disadvantages:*
- Distributed systems complexity (network latency, partial failures, consistency)
- No automatic distributed ACID transactions (requires patterns like Saga, 2PC, etc.)
- Complex debugging (need centralized logging, metrics, distributed tracing)
- Operational overhead (multiple deployments, monitoring, logging, orchestration)
- Data consistency challenges (often eventual consistency between services)
- Network overhead (HTTP/gRPC calls between services)
*Use cases:* Large teams, complex domains, need for independent scaling, polyglot requirements, mature platform/DevOps capability
```kotlin
// Microservice: Order Service (separate application)
@Service
class OrderService(
    private val userClient: UserServiceClient,          // HTTP/gRPC calls
    private val inventoryClient: InventoryServiceClient,
    private val paymentClient: PaymentServiceClient,
    private val orderRepo: OrderRepository
) {
    suspend fun placeOrder(order: Order): Order {
        // Network calls — no single ACID transaction covering all participating services
        val user = userClient.getUser(order.userId)  // HTTP GET
        // Simplified example of Saga-style handling for a distributed operation
        try {
            inventoryClient.reserveItems(order.items)
            paymentClient.processPayment(order.payment)
            return orderRepo.save(order)
        } catch (e: Exception) {
            // Compensating actions (in a real saga, all affected steps are compensated)
            inventoryClient.releaseItems(order.items)
            // A payment compensation (refund) would also be invoked here if payment succeeded
            throw e
        }
    }
}
```

**Comparison:**
| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| Deployment | Single unit | Multiple independent |
| Scaling | Entire application | Individual services |
| Technology | Single stack | Polyglot possible |
| Transactions | ACID within shared DB | Local ACID; cross-service via Saga/2PC/etc. |
| Complexity | Lower | Higher (distributed system) |
| Team size | Small-medium | Large |
| Development speed | Fast start | Slower start, faster at scale |
| Debugging | Easy | Hard (distributed tracing, centralized logs) |
| Data consistency | Typically strong within one DB | Strong locally, often eventual across services |
| Network overhead | None | Yes (HTTP/gRPC) |

**Key Microservices Patterns:**
1. API Gateway
2. `Service` Discovery
3. Circuit Breaker
4. Saga (distributed transactions)
5. Database per `Service`

**When to Use Monolith:**
✅ Use monolith when:
- Startup/MVP (fast time-to-market)
- Small team (< 10 developers)
- Simple domain (CRUD application)
- Unclear domain boundaries
- Limited resources, weak DevOps maturity
- Strong consistency required within a single system boundary

**When to Use Microservices:**
✅ Use microservices when:
- Large team (> 20-30 developers)
- Complex domain (clear bounded contexts)
- Need independent scaling
- Polyglot requirements
- High availability and fault isolation are critical
- Mature DevOps culture (CI/CD, monitoring, orchestration, etc.)

**Architecture Evolution:**
Common path: monolith → modular monolith → gradually extracted microservices around clear boundaries and hottest spots.
