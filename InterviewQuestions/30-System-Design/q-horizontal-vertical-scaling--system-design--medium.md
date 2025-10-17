---
id: 20251012-300001
title: "Horizontal vs Vertical Scaling / Горизонтальное vs Вертикальное масштабирование"
topic: system-design
difficulty: medium
status: draft
created: 2025-10-12
tags: - system-design
  - scalability
  - architecture
  - distributed-systems
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-system-design
related_questions:   - q-load-balancing-strategies--system-design--medium
  - q-database-sharding--system-design--hard
  - q-stateless-stateful-services--system-design--medium
slug: horizontal-vertical-scaling-system-design-medium
subtopics:   - scalability
  - scaling
  - distributed-systems
  - performance
---
# Horizontal vs Vertical Scaling

## English Version

### Problem Statement

As your application grows and needs to handle more traffic, you need strategies to scale your system. The two fundamental approaches are **horizontal scaling** (scaling out) and **vertical scaling** (scaling up). Understanding when to use each approach is crucial for building scalable systems.

**The Question:** What is the difference between horizontal and vertical scaling? When should you use each approach, and what are their trade-offs?

### Detailed Answer

#### What is Vertical Scaling?

**Vertical Scaling** (Scaling Up) means adding more resources (CPU, RAM, disk) to an existing server/machine.

**Example:**
- Upgrade from 4-core to 16-core CPU
- Increase RAM from 16GB to 128GB
- Switch to faster SSD storage
- Add more powerful GPU

```
Before:     After:
  
 4 CPU     16 CPU 
 16 GB  →  128 GB 
 500 GB    2 TB   
  
Single Server
```

#### What is Horizontal Scaling?

**Horizontal Scaling** (Scaling Out) means adding more servers/machines to your pool of resources.

**Example:**
- Add more web servers behind a load balancer
- Add more database replicas
- Increase number of application instances

```
Before:          After:
        
Server 1  →   Server 1 Server 2 Server 3
        
              Load Balancer distributes traffic
```

#### Comparison Matrix

| Aspect | Vertical Scaling | Horizontal Scaling |
|--------|-----------------|-------------------|
| **Cost** | Expensive (exponential growth) | Cheaper (linear growth) |
| **Complexity** | Simple (no code changes) | Complex (distributed logic) |
| **Limits** | Hardware limits (max CPU/RAM) | Virtually unlimited |
| **Downtime** | Usually required | Zero downtime possible |
| **Single Point of Failure** | Yes (one server) | No (multiple servers) |
| **Data consistency** | Easy (single machine) | Challenging (distributed) |
| **Load balancing** | Not needed | Required |
| **Latency** | Low (same machine) | Network latency exists |
| **Examples** | Database upgrades | Web server fleet |

#### When to Use Vertical Scaling

 **Good for:**
- **Databases** - especially RDBMS (PostgreSQL, MySQL) where distributed writes are complex
- **Legacy applications** - that can't be easily distributed
- **Single-threaded workloads** - that benefit from faster CPU
- **Quick fixes** - when you need immediate relief
- **Development/staging** - simpler infrastructure

**Example: Database Server**
```yaml
# Vertical scaling PostgreSQL
Initial: m5.large (2 vCPU, 8GB RAM)
Scale:   m5.4xlarge (16 vCPU, 64GB RAM)

Benefits:
  - No application changes needed
  - Single database connection
  - ACID guarantees maintained
  - No data synchronization issues
```

**Real-world Case:**
```
Stack Overflow primarily uses vertical scaling for their SQL Server:
- Single massive database server (vertical)
- Handles millions of requests
- Simpler architecture
- Eventually hit practical limits
```

#### When to Use Horizontal Scaling

 **Good for:**
- **Web servers** - stateless HTTP servers scale perfectly
- **API services** - RESTful APIs with load balancing
- **Microservices** - designed for distribution
- **Read-heavy workloads** - add read replicas
- **High availability** - eliminate single point of failure
- **Global distribution** - servers in multiple regions

**Example: Web Application**
```yaml
# Horizontal scaling web tier
Architecture:
  Load Balancer:
    - AWS ALB / Nginx
  Web Servers (auto-scaling):
    - 3-50 instances based on load
  Stateless design:
    - Session in Redis
    - Files in S3
    - Database separate tier
```

**Implementation Example:**
```python
# Stateless Flask API designed for horizontal scaling
from flask import Flask, session
import redis

app = Flask(__name__)
# Session data in Redis (not local memory)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://cache:6379')

@app.route('/api/user/<user_id>')
def get_user(user_id):
    # No local state - can run on any server
    user = database.query(f"SELECT * FROM users WHERE id={user_id}")
    return jsonify(user)

@app.route('/api/order', methods=['POST'])
def create_order(order_data):
    # Stateless - any instance can handle this
    order_id = database.insert_order(order_data)
    cache.invalidate(f"user:{order_data['user_id']}:orders")
    return {"order_id": order_id}
```

#### Hybrid Approach (Most Common)

Most production systems use **both**:

```

         Load Balancer (ALB)             

              
    
                                    
             
Web Srv1         Web Srv2    Web Srv3  ← Horizontal
(small)          (small)     (small) 
             
                                   
    
                
        
          Cache (Redis)  ← Horizontal (cluster)
        
                
        
          Primary DB     ← Vertical (large instance)
          (m5.4xlarge)  
        
                
    
                           
         
Read               Read        ← Horizontal
Replica 1          Replica 2 
         
```

**Scaling Strategy by Tier:**
- **Web/API tier** → Horizontal (stateless, easily distributed)
- **Cache tier** → Horizontal (Redis cluster, Memcached)
- **Database primary** → Vertical (writes need consistency)
- **Database reads** → Horizontal (read replicas)
- **Background jobs** → Horizontal (worker queues)

#### Cost Analysis

**Vertical Scaling Costs:**
```
AWS EC2 pricing (example):
t3.medium  (2 vCPU, 4GB)   = $30/month
t3.large   (2 vCPU, 8GB)   = $60/month   (2x cost)
t3.xlarge  (4 vCPU, 16GB)  = $120/month  (4x cost)
t3.2xlarge (8 vCPU, 32GB)  = $240/month  (8x cost)

Notice: Exponential cost growth
```

**Horizontal Scaling Costs:**
```
10x t3.medium = $300/month
- 20 vCPU total, 40GB RAM
- Same cost as 1x t3.2xlarge but:
   More total resources
   High availability
   Better fault tolerance
   Can scale gradually
```

#### Limitations & Challenges

**Vertical Scaling Limits:**
```
 Hardware ceiling: Largest AWS instance is 448 vCPU, 24TB RAM
 Downtime for upgrades
 No redundancy
 Cost grows exponentially
 Single point of failure
```

**Horizontal Scaling Challenges:**
```
 Distributed data consistency
 Session management (need sticky sessions or external store)
 File storage (need S3/shared storage)
 Complex deployment
 Network latency between servers
 Load balancer required
 More operational complexity
```

#### Real-World System Design

**E-commerce Platform Architecture:**
```kotlin
// Horizontally scaled API tier
@RestController
class ProductController(
    private val productService: ProductService,
    private val cache: RedisCache
) {
    @GetMapping("/products/{id}")
    suspend fun getProduct(@PathVariable id: Long): ProductDto {
        // Check distributed cache first
        return cache.get("product:$id") ?: run {
            val product = productService.findById(id)
            cache.set("product:$id", product, ttl = 5.minutes)
            product
        }
    }

    @PostMapping("/orders")
    suspend fun createOrder(@RequestBody order: OrderRequest): OrderDto {
        // Stateless - any instance can handle this
        // State stored in database (vertically scaled)
        return orderService.create(order)
    }
}

// Configuration for horizontal scaling
@Configuration
class ScalingConfig {
    @Bean
    fun sessionStore(): RedisSessionStore {
        // Session stored externally, not in local memory
        return RedisSessionStore(
            cluster = listOf("redis-1:6379", "redis-2:6379")
        )
    }
}
```

**Auto-scaling Configuration (Kubernetes):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-api
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 2
        periodSeconds: 120
```

#### Decision Tree

```
Start: Need to scale?

 Is it a database?
   Yes → Start with VERTICAL
           (Add read replicas for horizontal)
   No → Continue

 Is the application stateless?
   Yes → HORIZONTAL SCALING
           (Web servers, APIs, microservices)
   No → Can you make it stateless?
             Yes → Refactor → HORIZONTAL
             No → VERTICAL (or redesign)

 Budget constraints?
   Limited → HORIZONTAL (cheaper)
   Flexible → Consider VERTICAL first (simpler)

 Need high availability?
   Yes → HORIZONTAL (redundancy)
   No → Either works

 Quick fix needed?
    Yes → VERTICAL (faster to implement)
    No → HORIZONTAL (better long-term)
```

### Key Takeaways

1. **Vertical Scaling** = More powerful servers (scaling UP)
2. **Horizontal Scaling** = More servers (scaling OUT)
3. **Most production systems use BOTH** - hybrid approach
4. **Web/API tier** → Horizontal (easy, stateless)
5. **Database writes** → Vertical (consistency)
6. **Database reads** → Horizontal (replicas)
7. **Cost:** Horizontal is cheaper long-term
8. **Complexity:** Vertical is simpler to implement
9. **Limits:** Horizontal is virtually unlimited
10. **High availability:** Horizontal provides redundancy

---

## Russian Version

### Постановка задачи

По мере роста вашего приложения и необходимости обработки большего трафика, нужны стратегии масштабирования системы. Два фундаментальных подхода - это **горизонтальное масштабирование** (scaling out) и **вертикальное масштабирование** (scaling up). Понимание, когда использовать каждый подход, критически важно для построения масштабируемых систем.

**Вопрос:** В чём разница между горизонтальным и вертикальным масштабированием? Когда следует использовать каждый подход, и каковы их компромиссы?

### Детальный ответ

#### Что такое вертикальное масштабирование?

**Вертикальное масштабирование** (Scaling Up) означает добавление большего количества ресурсов (CPU, RAM, диск) к существующему серверу/машине.

**Пример:**
- Обновление с 4-ядерного до 16-ядерного процессора
- Увеличение RAM с 16GB до 128GB
- Переход на более быстрое SSD хранилище
- Добавление более мощного GPU

```
До:         После:
  
 4 CPU     16 CPU 
 16 GB  →  128 GB 
 500 GB    2 TB   
  
Один сервер
```

#### Что такое горизонтальное масштабирование?

**Горизонтальное масштабирование** (Scaling Out) означает добавление большего количества серверов/машин в пул ресурсов.

**Пример:**
- Добавление веб-серверов за балансировщиком нагрузки
- Добавление реплик базы данных
- Увеличение количества экземпляров приложения

```
До:              После:
        
Сервер 1  →   Сервер 1 Сервер 2 Сервер 3
        
           Балансировщик распределяет трафик
```

#### Матрица сравнения

| Аспект | Вертикальное | Горизонтальное |
|--------|--------------|----------------|
| **Стоимость** | Дорого (экспоненциальный рост) | Дешевле (линейный рост) |
| **Сложность** | Просто (без изменений кода) | Сложно (распределённая логика) |
| **Ограничения** | Лимиты железа (макс CPU/RAM) | Практически безграничное |
| **Downtime** | Обычно требуется | Возможен zero downtime |
| **Единая точка отказа** | Да (один сервер) | Нет (несколько серверов) |
| **Консистентность данных** | Легко (одна машина) | Сложно (распределённая) |
| **Балансировка нагрузки** | Не нужна | Требуется |
| **Задержка** | Низкая (та же машина) | Сетевая задержка |
| **Примеры** | Обновление БД | Флот веб-серверов |

#### Когда использовать вертикальное масштабирование

 **Подходит для:**
- **Баз данных** - особенно RDBMS (PostgreSQL, MySQL), где распределённые записи сложны
- **Legacy приложений** - которые нельзя легко распределить
- **Однопоточных workload** - которые выигрывают от более быстрого CPU
- **Быстрых решений** - когда нужно немедленное облегчение
- **Dev/staging окружений** - более простая инфраструктура

**Пример: Сервер базы данных**
```yaml
# Вертикальное масштабирование PostgreSQL
Начало: m5.large (2 vCPU, 8GB RAM)
Масштабирование: m5.4xlarge (16 vCPU, 64GB RAM)

Преимущества:
  - Не нужны изменения приложения
  - Одно подключение к БД
  - ACID гарантии сохраняются
  - Нет проблем синхронизации данных
```

#### Когда использовать горизонтальное масштабирование

 **Подходит для:**
- **Веб-серверов** - stateless HTTP серверы отлично масштабируются
- **API сервисов** - RESTful API с балансировкой нагрузки
- **Микросервисов** - спроектированы для распределения
- **Read-heavy workloads** - добавить read replicas
- **Высокой доступности** - устранить единую точку отказа
- **Глобального распределения** - серверы в разных регионах

**Пример: Веб-приложение**
```python
# Stateless Flask API для горизонтального масштабирования
from flask import Flask, session
import redis

app = Flask(__name__)
# Сессии в Redis (не в локальной памяти)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://cache:6379')

@app.route('/api/user/<user_id>')
def get_user(user_id):
    # Без локального состояния - может работать на любом сервере
    user = database.query(f"SELECT * FROM users WHERE id={user_id}")
    return jsonify(user)
```

#### Гибридный подход (наиболее распространённый)

Большинство production систем используют **оба подхода**:

```

      Балансировщик нагрузки (ALB)       

              
    
                                    
             
Веб-сер1         Веб-сер2    Веб-сер3  ← Горизонтально
(малый)          (малый)     (малый) 
             
    
                
        
          Кэш (Redis)    ← Горизонтально (кластер)
        
                
        
         Основная БД     ← Вертикально (большой инстанс)
         (m5.4xlarge)   
        
                
    
                           
         
Read               Read        ← Горизонтально
Replica 1          Replica 2 
         
```

**Стратегия масштабирования по уровням:**
- **Web/API уровень** → Горизонтально (stateless, легко распределяется)
- **Cache уровень** → Горизонтально (Redis cluster, Memcached)
- **БД primary** → Вертикально (записи требуют консистентности)
- **БД reads** → Горизонтально (read replicas)
- **Background jobs** → Горизонтально (worker queues)

### Ключевые выводы

1. **Вертикальное масштабирование** = Более мощные серверы (scaling UP)
2. **Горизонтальное масштабирование** = Больше серверов (scaling OUT)
3. **Большинство production систем используют ОБА** - гибридный подход
4. **Web/API уровень** → Горизонтально (легко, stateless)
5. **Записи в БД** → Вертикально (консистентность)
6. **Чтение из БД** → Горизонтально (реплики)
7. **Стоимость:** Горизонтальное дешевле в долгосрочной перспективе
8. **Сложность:** Вертикальное проще в реализации
9. **Ограничения:** Горизонтальное практически безграничное
10. **Высокая доступность:** Горизонтальное обеспечивает избыточность

## Follow-ups

1. How do you handle session management in horizontally scaled web applications?
2. What is database sharding and how does it relate to horizontal scaling?
3. Explain the concept of "sticky sessions" in load balancing
4. How does auto-scaling work in cloud environments (AWS, GCP, Azure)?
5. What are the challenges of horizontally scaling stateful services?
6. Compare different load balancing algorithms (Round Robin, Least Connections, IP Hash)
7. How do you ensure data consistency across horizontally scaled databases?
8. What is the CAP theorem and how does it relate to horizontal scaling?
9. Explain the difference between stateless and stateful applications
10. How do you monitor and measure the effectiveness of your scaling strategy?

---

## Related Questions

### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
