---
id: 20251012-203116
title: "Microservices vs Monolith Architecture / Микросервисы vs Монолитная архитектура"
topic: system-design
difficulty: hard
status: draft
created: 2025-10-12
updated: 2025-10-12
tags: [design, microservices, architecture, distributed-systems, difficulty/hard]
aliases: []
original_language: en
language_tags: [en, ru]
question_kind: system-design
moc: moc-system-design
subtopics:   - microservices
  - monolith
  - architecture
  - distributed-systems
  - scalability
related:   - q-api-gateway-pattern--system-design--medium
  - q-service-mesh--system-design--hard
  - q-distributed-transactions--system-design--hard
---
# Question (EN)
> What are the key differences between microservices and monolithic architecture? When should you use each, and what are the trade-offs?

# Вопрос (RU)
> Каковы ключевые различия между микросервисами и монолитной архитектурой? Когда следует использовать каждый подход, и каковы компромиссы?

---

## Answer (EN)

Choosing between monolithic and microservices architecture is a fundamental architectural decision that impacts development speed, scalability, team organization, and operational complexity. Each approach has distinct advantages and challenges.

### Monolithic Architecture

**What is it?**
Single, unified application where all components are tightly coupled and deployed as one unit.

```

      Monolithic Application        
                                    
          
     UI          API          
          
                                    
    
      Business Logic            
    - User Management           
    - Order Processing          
    - Payment                   
    - Inventory                 
    - Notifications             
    
                                    
    
      Single Database           
    

       Single Deployment Unit
```

**Example Code Structure:**
```kotlin
// Monolithic E-commerce Application
@SpringBootApplication
class EcommerceApplication

// All services in one application
@Service
class UserService(private val userRepo: UserRepository) {
    fun createUser(user: User): User = userRepo.save(user)
}

@Service
class OrderService(
    private val orderRepo: OrderRepository,
    private val userService: UserService,        // Direct dependency
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService
) {
    @Transactional  // Single database transaction
    fun placeOrder(order: Order): Order {
        // All in same application, same transaction
        val user = userService.getUser(order.userId)
        inventoryService.reserveItems(order.items)
        paymentService.processPayment(order.payment)
        return orderRepo.save(order)
    }
}

@Service
class InventoryService(private val inventoryRepo: InventoryRepository) {
    fun reserveItems(items: List<Item>) { /* ... */ }
}

@Service
class PaymentService(private val paymentRepo: PaymentRepository) {
    fun processPayment(payment: Payment) { /* ... */ }
}

// All deployed together as single JAR/WAR
```

** Pros:**
- **Simple development** - Single codebase, easy to understand
- **Easy debugging** - Single process, stack traces work
- **ACID transactions** - Database transactions across all modules
- **Performance** - No network overhead between components
- **Simple deployment** - Single artifact to deploy
- **No distributed systems complexity**

** Cons:**
- **Scalability** - Must scale entire app (can't scale parts)
- **Technology lock-in** - One language/framework for everything
- **Deployment risk** - Small change requires full redeployment
- **Development bottleneck** - Team stepping on each other's toes
- **Long build times** - Large codebase
- **Difficult to understand** - Over time becomes a "big ball of mud"

---

### Microservices Architecture

**What is it?**
Application composed of small, independent services that communicate over the network.

```

              API Gateway/Load Balancer        

                                  
   
 User        Order    Inventory  Payment  
 Service     Service   Service   Service  
   
                                    
   
 User DB    Order DB  Inv. DB   Payment DB
   

Each service: Independent deployment, scaling, database
```

**Example Code Structure:**
```kotlin
// User Microservice (separate application)
@SpringBootApplication
class UserServiceApplication

@RestController
@RequestMapping("/api/users")
class UserController(private val userService: UserService) {
    @PostMapping
    fun createUser(@RequestBody user: User): User {
        return userService.createUser(user)
    }
}

// Order Microservice (separate application)
@SpringBootApplication
class OrderServiceApplication

@RestController
@RequestMapping("/api/orders")
class OrderController(private val orderService: OrderService) {
    @PostMapping
    suspend fun placeOrder(@RequestBody order: Order): Order {
        return orderService.placeOrder(order)
    }
}

@Service
class OrderService(
    private val orderRepo: OrderRepository,
    private val userClient: UserServiceClient,      // HTTP call to User Service
    private val inventoryClient: InventoryServiceClient,  // HTTP call
    private val paymentClient: PaymentServiceClient       // HTTP call
) {
    suspend fun placeOrder(order: Order): Order {
        // Network calls to other services
        val user = userClient.getUser(order.userId)  // HTTP GET
        
        // No ACID transaction across services
        // Need distributed transaction patterns (Saga)
        try {
            inventoryClient.reserveItems(order.items)  // HTTP POST
            paymentClient.processPayment(order.payment)  // HTTP POST
            return orderRepo.save(order)
        } catch (e: Exception) {
            // Compensating transactions
            inventoryClient.releaseItems(order.items)
            throw e
        }
    }
}

// User Service Client (Feign/HTTP)
@FeignClient(name = "user-service", url = "\${services.user.url}")
interface UserServiceClient {
    @GetMapping("/api/users/{id}")
    suspend fun getUser(@PathVariable id: Long): User
}

// Each service deployed independently
// Can use different technologies:
// - User Service: Kotlin + PostgreSQL
// - Order Service: Java + MongoDB
// - Payment Service: Go + MySQL
```

** Pros:**
- **Independent scaling** - Scale only what needs scaling
- **Technology flexibility** - Different languages/frameworks per service
- **Fault isolation** - One service failure doesn't bring down everything
- **Faster deployment** - Deploy one service independently
- **Team autonomy** - Teams own entire services
- **Easier to understand** - Each service is small and focused

** Cons:**
- **Complexity** - Distributed system challenges (network, latency, failures)
- **No ACID transactions** - Distributed transactions are hard
- **Network overhead** - Inter-service communication adds latency
- **Data consistency** - Eventual consistency, harder to maintain
- **Operational overhead** - Many services to deploy, monitor, debug
- **Testing complexity** - Integration testing is harder

---

### Detailed Comparison

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| **Codebase** | Single repository | Multiple repositories |
| **Deployment** | All-or-nothing | Independent per service |
| **Scaling** | Scale everything | Scale individual services |
| **Technology** | Single stack | Polyglot (multiple stacks) |
| **Transactions** | ACID (easy) | Distributed (complex) |
| **Data** | Shared database | Database per service |
| **Communication** | Method calls | Network (HTTP/gRPC/messaging) |
| **Development** | Easy to start | Complex from day one |
| **Team** | One team | Multiple teams |
| **Debugging** | Simple | Distributed tracing needed |
| **Performance** | Fast (no network) | Network latency |
| **Failure** | Cascading failure | Isolated failures |
| **Onboarding** | Easy | Steeper learning curve |

---

### When to Use Monolith

 **Monolith is better when:**

1. **Small team** (< 10 developers)
2. **Simple application**
3. **Fast time to market** crucial
4. **Limited resources** (can't manage many services)
5. **Startup/MVP** phase
6. **Well-defined bounded context**
7. **Strong ACID requirements**

**Example Scenarios:**
```
- Small e-commerce store
- Internal admin tools
- MVPs and prototypes
- Applications with low complexity
- Teams new to distributed systems
```

---

### When to Use Microservices

 **Microservices are better when:**

1. **Large team** (multiple teams)
2. **Complex domain** (multiple bounded contexts)
3. **Different scaling needs** per component
4. **Need technology diversity**
5. **Frequent deployments**
6. **Have DevOps maturity**
7. **Can handle distributed systems complexity**

**Example Scenarios:**
```
- Netflix: Different services for streaming, recommendations, billing
- Amazon: Millions of services for different functions
- Uber: Separate services for rides, payments, maps, matching
- Large enterprises with multiple products
```

---

### Migration Path: Monolith → Microservices

**DON'T start with microservices unless you have:**
- Large team
- Clear service boundaries
- DevOps infrastructure
- Distributed systems expertise

**Start with Modular Monolith:**
```kotlin
// Modular Monolith: Organized but still one deployment
@SpringBootApplication
class EcommerceApplication

// Module 1: Users (could become a microservice later)
package com.ecommerce.users
@Service
class UserService { /* ... */ }

// Module 2: Orders (could become a microservice later)
package com.ecommerce.orders
@Service
class OrderService { /* ... */ }

// Module 3: Payments (could become a microservice later)
package com.ecommerce.payments
@Service
class PaymentService { /* ... */ }

// Clear boundaries, but still deployed together
// Easy to split into microservices when needed
```

**Strangler Fig Pattern:**
```
Step 1: Start with Monolith

   Monolith    
  - Users      
  - Orders     
  - Payments   


Step 2: Extract one service
  
   Monolith       Payment    
  - Users         Service    
  - Orders        (NEW)      
  

Step 3: Extract another
  
   Monolith       Payment    
  - Users         Service    
  
                   
                    Order      
                    Service    
                    (NEW)      
                   

Step 4: Complete migration
  
 User          Payment    
 Service       Service    
  

 Order      
 Service    

```

---

### Microservices Challenges & Solutions

#### 1. Distributed Transactions

**Problem:** No ACID across services

**Solution: Saga Pattern**
```kotlin
// Saga Pattern: Choreography-based
class OrderSaga(
    private val orderService: OrderService,
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService,
    private val eventBus: EventBus
) {
    suspend fun createOrder(order: Order) {
        try {
            // Step 1: Create order
            orderService.createPendingOrder(order)
            eventBus.publish(OrderCreatedEvent(order.id))
            
            // Step 2: Reserve inventory (triggered by event)
            inventoryService.reserveItems(order.items)
            eventBus.publish(InventoryReservedEvent(order.id))
            
            // Step 3: Process payment (triggered by event)
            paymentService.processPayment(order.payment)
            eventBus.publish(PaymentProcessedEvent(order.id))
            
            // Step 4: Confirm order
            orderService.confirmOrder(order.id)
            
        } catch (e: Exception) {
            // Compensating transactions (rollback)
            eventBus.publish(OrderFailedEvent(order.id))
            paymentService.refund(order.payment)
            inventoryService.releaseItems(order.items)
            orderService.cancelOrder(order.id)
        }
    }
}
```

#### 2. Service Discovery

**Problem:** Services need to find each other

**Solution: Service Registry (Consul, Eureka)**
```kotlin
@Service
class OrderService(
    @Autowired private val discoveryClient: DiscoveryClient
) {
    suspend fun callUserService(userId: Long): User {
        // Get available instances
        val instances = discoveryClient.getInstances("user-service")
        val instance = instances.random()  // Load balance
        
        val url = "${instance.uri}/api/users/$userId"
        return httpClient.get(url)
    }
}
```

#### 3. API Gateway

**Problem:** Clients don't want to call many services

**Solution: API Gateway Pattern**
```
Client
  
  

 API Gateway   Single entry point

         
         
 User Order Payment  (Internal services)
```

#### 4. Distributed Tracing

**Problem:** Hard to debug across services

**Solution: Distributed Tracing (Jaeger, Zipkin)**
```kotlin
@Component
class TracingInterceptor : ClientHttpRequestInterceptor {
    override fun intercept(
        request: HttpRequest,
        body: ByteArray,
        execution: ClientHttpRequestExecution
    ): ClientHttpResponse {
        // Add trace ID to every request
        val traceId = MDC.get("traceId") ?: UUID.randomUUID().toString()
        request.headers.add("X-Trace-Id", traceId)
        return execution.execute(request, body)
    }
}
```

---

### Hybrid: Modular Monolith

**Best of both worlds for many applications:**

```kotlin
// Modular Monolith with clear boundaries
@SpringBootApplication
class EcommerceApplication

// Module interfaces (could be extracted to microservices)
interface UserModule {
    fun getUser(id: Long): User
    fun createUser(user: User): User
}

interface OrderModule {
    fun placeOrder(order: Order): Order
}

// Implementations in same deployment
@Component
class UserModuleImpl : UserModule { /* ... */ }

@Component
class OrderModuleImpl(
    private val userModule: UserModule  // Dependency injection
) : OrderModule { /* ... */ }

// Benefits:
// - Clear boundaries (easy to extract later)
// - Single deployment (simpler operations)
// - ACID transactions (when needed)
// - Can extract to microservices when team grows
```

---

### Key Takeaways

1. **Monolith** = Simple, fast development, ACID transactions
2. **Microservices** = Scalability, flexibility, complexity
3. **Start with monolith** unless you have strong reasons
4. **Modular monolith** = Good middle ground
5. **Microservices need:** DevOps, monitoring, distributed tracing
6. **Distributed transactions** are hard - use Saga pattern
7. **Service mesh** helps manage service-to-service communication
8. **Don't do microservices** just because it's trendy
9. **Strangler fig pattern** for gradual migration
10. **Microservices ≠ better** - choose based on team size, complexity

## Ответ (RU)

Выбор между монолитной и микросервисной архитектурой - фундаментальное архитектурное решение, которое влияет на скорость разработки, масштабируемость, организацию команды и операционную сложность. Каждый подход имеет свои преимущества и недостатки.

### Монолитная архитектура

**Что это?**
Единое унифицированное приложение, где все компоненты тесно связаны и развёртываются как одна единица.

```

      Монолитное приложение


     UI          API



      Бизнес-логика
    - Управление пользователями
    - Обработка заказов
    - Платежи
    - Инвентарь
    - Уведомления



      Единая база данных



       Единица развёртывания
```

**Пример структуры кода:**
```kotlin
// Монолитное E-commerce приложение
@SpringBootApplication
class EcommerceApplication

// Все сервисы в одном приложении
@Service
class UserService(private val userRepo: UserRepository) {
    fun createUser(user: User): User = userRepo.save(user)
}

@Service
class OrderService(
    private val orderRepo: OrderRepository,
    private val userService: UserService,        // Прямая зависимость
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService
) {
    @Transactional  // Единая транзакция БД
    fun placeOrder(order: Order): Order {
        // Всё в одном приложении, одна транзакция
        val user = userService.getUser(order.userId)
        inventoryService.reserveItems(order.items)
        paymentService.processPayment(order.payment)
        return orderRepo.save(order)
    }
}
```

**Плюсы:**
- **Простая разработка** - Единая кодовая база, легко понять
- **Легкая отладка** - Единый процесс, stack traces работают
- **ACID транзакции** - Транзакции БД между всеми модулями
- **Производительность** - Нет сетевых накладных расходов между компонентами
- **Простое развёртывание** - Один артефакт для развёртывания
- **Нет сложности распределённых систем**

**Минусы:**
- **Масштабируемость** - Нужно масштабировать всё приложение (нельзя масштабировать части)
- **Технологическая привязка** - Один язык/фреймворк для всего
- **Риск развёртывания** - Малое изменение требует полного передеплоя
- **Узкое место разработки** - Команды мешают друг другу
- **Долгая сборка** - Большая кодовая база
- **Сложно понять** - Со временем становится "большим клубком грязи"

---

### Микросервисная архитектура

**Что это?**
Приложение, состоящее из небольших независимых сервисов, которые общаются по сети.

```

              API Gateway/Load Balancer



 User        Order    Inventory  Payment
 Service     Service   Service   Service



 User DB    Order DB  Inv. DB   Payment DB


Каждый сервис: Независимое развёртывание, масштабирование, БД
```

**Пример структуры кода:**
```kotlin
// User Microservice (отдельное приложение)
@SpringBootApplication
class UserServiceApplication

@RestController
@RequestMapping("/api/users")
class UserController(private val userService: UserService) {
    @PostMapping
    fun createUser(@RequestBody user: User): User {
        return userService.createUser(user)
    }
}

// Order Microservice (отдельное приложение)
@SpringBootApplication
class OrderServiceApplication

@Service
class OrderService(
    private val orderRepo: OrderRepository,
    private val userClient: UserServiceClient,      // HTTP вызов к User Service
    private val inventoryClient: InventoryServiceClient,
    private val paymentClient: PaymentServiceClient
) {
    suspend fun placeOrder(order: Order): Order {
        // Сетевые вызовы к другим сервисам
        val user = userClient.getUser(order.userId)  // HTTP GET

        // Нет ACID транзакций между сервисами
        // Нужны паттерны распределённых транзакций (Saga)
        try {
            inventoryClient.reserveItems(order.items)
            paymentClient.processPayment(order.payment)
            return orderRepo.save(order)
        } catch (e: Exception) {
            // Компенсирующие транзакции
            inventoryClient.releaseItems(order.items)
            throw e
        }
    }
}
```

**Плюсы:**
- **Независимое масштабирование** - Масштабируйте только то, что нужно
- **Технологическая гибкость** - Разные языки/фреймворки для каждого сервиса
- **Изоляция сбоев** - Сбой одного сервиса не роняет всё
- **Быстрое развёртывание** - Развёртывайте один сервис независимо
- **Автономия команд** - Команды владеют целыми сервисами
- **Легче понять** - Каждый сервис небольшой и сфокусированный

**Минусы:**
- **Сложность** - Проблемы распределённых систем (сеть, задержки, сбои)
- **Нет ACID транзакций** - Распределённые транзакции сложны
- **Сетевые накладные расходы** - Коммуникация между сервисами добавляет задержку
- **Консистентность данных** - Eventual consistency, сложнее поддерживать
- **Операционные затраты** - Много сервисов для развёртывания, мониторинга, отладки
- **Сложность тестирования** - Интеграционное тестирование сложнее

---

### Подробное сравнение

| Аспект | Монолит | Микросервисы |
|--------|----------|---------------|
| **Кодовая база** | Единый репозиторий | Множество репозиториев |
| **Развёртывание** | Всё или ничего | Независимое по сервисам |
| **Масштабирование** | Масштабировать всё | Масштабировать отдельные сервисы |
| **Технологии** | Единый стек | Polyglot (множество стеков) |
| **Транзакции** | ACID (легко) | Распределённые (сложно) |
| **Данные** | Общая БД | БД на сервис |
| **Коммуникация** | Вызовы методов | Сеть (HTTP/gRPC/messaging) |
| **Разработка** | Легко начать | Сложно с первого дня |
| **Команда** | Одна команда | Множество команд |
| **Отладка** | Простая | Нужен distributed tracing |
| **Производительность** | Быстро (без сети) | Сетевая задержка |
| **Сбои** | Каскадные сбои | Изолированные сбои |

---

### Когда использовать монолит

**Монолит лучше когда:**

1. **Малая команда** (< 10 разработчиков)
2. **Простое приложение**
3. **Быстрый выход на рынок** критичен
4. **Ограниченные ресурсы** (не можете управлять множеством сервисов)
5. **Startup/MVP** фаза
6. **Хорошо определённый ограниченный контекст**
7. **Строгие ACID требования**

**Примеры сценариев:**
```
- Небольшой e-commerce магазин
- Внутренние административные инструменты
- MVP и прототипы
- Приложения с низкой сложностью
- Команды новые в распределённых системах
```

---

### Когда использовать микросервисы

**Микросервисы лучше когда:**

1. **Большая команда** (множество команд)
2. **Сложный домен** (множество ограниченных контекстов)
3. **Разные потребности масштабирования** для компонентов
4. **Нужна технологическая гибкость**
5. **Частые развёртывания**
6. **Есть DevOps зрелость**
7. **Можете справиться со сложностью распределённых систем**

**Примеры сценариев:**
```
- Netflix: Разные сервисы для стриминга, рекомендаций, биллинга
- Amazon: Миллионы сервисов для разных функций
- Uber: Отдельные сервисы для поездок, платежей, карт, сопоставления
- Крупные предприятия с множеством продуктов
```

---

### Путь миграции: Монолит → Микросервисы

**НЕ НАЧИНАЙТЕ с микросервисов если у вас нет:**
- Большой команды
- Чётких границ сервисов
- DevOps инфраструктуры
- Экспертизы в распределённых системах

**Начните с модульного монолита:**
```kotlin
// Модульный монолит: Организованный, но всё ещё одно развёртывание
@SpringBootApplication
class EcommerceApplication

// Модуль 1: Users (может стать микросервисом позже)
package com.ecommerce.users
@Service
class UserService { /* ... */ }

// Модуль 2: Orders (может стать микросервисом позже)
package com.ecommerce.orders
@Service
class OrderService { /* ... */ }

// Чёткие границы, но всё ещё развёртывается вместе
// Легко разделить на микросервисы когда нужно
```

**Паттерн Strangler Fig:**
```
Шаг 1: Начните с монолита

   Монолит
  - Users
  - Orders
  - Payments


Шаг 2: Извлеките один сервис

   Монолит       Payment
  - Users         Service
  - Orders        (НОВЫЙ)


Шаг 3: Извлеките ещё один

   Монолит       Payment
  - Users         Service


                    Order
                    Service
                    (НОВЫЙ)


Шаг 4: Завершите миграцию

 User          Payment
 Service       Service


 Order
 Service

```

---

### Проблемы микросервисов и решения

#### 1. Распределённые транзакции

**Проблема:** Нет ACID между сервисами

**Решение: Saga Pattern**
```kotlin
// Saga Pattern: На основе хореографии
class OrderSaga(
    private val orderService: OrderService,
    private val inventoryService: InventoryService,
    private val paymentService: PaymentService,
    private val eventBus: EventBus
) {
    suspend fun createOrder(order: Order) {
        try {
            // Шаг 1: Создать заказ
            orderService.createPendingOrder(order)
            eventBus.publish(OrderCreatedEvent(order.id))

            // Шаг 2: Зарезервировать товары
            inventoryService.reserveItems(order.items)
            eventBus.publish(InventoryReservedEvent(order.id))

            // Шаг 3: Обработать платёж
            paymentService.processPayment(order.payment)
            eventBus.publish(PaymentProcessedEvent(order.id))

            // Шаг 4: Подтвердить заказ
            orderService.confirmOrder(order.id)

        } catch (e: Exception) {
            // Компенсирующие транзакции (откат)
            eventBus.publish(OrderFailedEvent(order.id))
            paymentService.refund(order.payment)
            inventoryService.releaseItems(order.items)
            orderService.cancelOrder(order.id)
        }
    }
}
```

#### 2. Service Discovery

**Проблема:** Сервисам нужно находить друг друга

**Решение: Service Registry (Consul, Eureka)**

#### 3. API Gateway

**Проблема:** Клиенты не хотят вызывать множество сервисов

**Решение: Паттерн API Gateway**
```
Client



 API Gateway   Единая точка входа



 User Order Payment  (Внутренние сервисы)
```

#### 4. Distributed Tracing

**Проблема:** Сложно отлаживать между сервисами

**Решение: Distributed Tracing (Jaeger, Zipkin)**

---

### Гибрид: Модульный монолит

**Лучшее из обоих миров для многих приложений:**

```kotlin
// Модульный монолит с чёткими границами
@SpringBootApplication
class EcommerceApplication

// Интерфейсы модулей (могут быть извлечены в микросервисы)
interface UserModule {
    fun getUser(id: Long): User
    fun createUser(user: User): User
}

interface OrderModule {
    fun placeOrder(order: Order): Order
}

// Реализации в том же развёртывании
@Component
class UserModuleImpl : UserModule { /* ... */ }

@Component
class OrderModuleImpl(
    private val userModule: UserModule  // Dependency injection
) : OrderModule { /* ... */ }

// Преимущества:
// - Чёткие границы (легко извлечь позже)
// - Единое развёртывание (проще операции)
// - ACID транзакции (когда нужно)
// - Можно извлечь в микросервисы когда команда растёт
```

---

### Ключевые выводы

1. **Монолит** = Простая, быстрая разработка, ACID транзакции
2. **Микросервисы** = Масштабируемость, гибкость, сложность
3. **Начинайте с монолита** если нет веских причин
4. **Модульный монолит** = Хороший компромисс
5. **Микросервисам нужны:** DevOps, мониторинг, distributed tracing
6. **Распределённые транзакции** сложны - используйте Saga pattern
7. **Service mesh** помогает управлять коммуникацией между сервисами
8. **Не делайте микросервисы** просто потому что это модно
9. **Strangler fig pattern** для постепенной миграции
10. **Микросервисы ≠ лучше** - выбирайте исходя из размера команды, сложности

## Follow-ups

1. What is the Saga pattern for distributed transactions?
2. How do you implement service discovery in microservices?
3. What is an API Gateway and why is it needed?
4. Explain the difference between orchestration and choreography in microservices
5. How do you handle data consistency across microservices?
6. What is a service mesh and what problems does it solve?
7. How do you implement distributed tracing?
8. What is the Strangler Fig pattern for migrating to microservices?
9. How do you handle authentication and authorization in microservices?
10. What are the deployment strategies for microservices (blue-green, canary)?

---

## Related Questions

### Related (Hard)
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system

