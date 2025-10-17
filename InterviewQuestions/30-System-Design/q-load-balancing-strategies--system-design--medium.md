---
id: 20251012-300002
title: "Load Balancing Algorithms and Strategies / Алгоритмы и стратегии балансировки нагрузки"
topic: system-design
difficulty: medium
status: draft
created: 2025-10-12
tags: - system-design
  - load-balancing
  - scalability
  - algorithms
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-system-design
related_questions:   - q-horizontal-vertical-scaling--system-design--medium
  - q-stateless-stateful-services--system-design--medium
  - q-health-checks-circuit-breaker--system-design--hard
slug: load-balancing-strategies-system-design-medium
subtopics:   - load-balancing
  - scalability
  - high-availability
  - distributed-systems
---
# Question (EN)
> What are the main load balancing algorithms? When should you use each algorithm, and what are their trade-offs?

# Вопрос (RU)
> Каковы основные алгоритмы балансировки нагрузки? Когда следует использовать каждый алгоритм и каковы их компромиссы?

---

## Answer (EN)

When you have multiple servers handling requests, you need a **load balancer** to distribute traffic efficiently across them. The algorithm you choose significantly impacts performance, fairness, and user experience.



### What is Load Balancing?

**Load Balancing** distributes incoming network traffic across multiple servers to ensure:
-  No single server is overwhelmed
-  High availability (if one server fails, others continue)
-  Better performance and response times
-  Efficient resource utilization

```
                    
Clients    Load Balancer   
                    
                             
            
                                            
                       
        Server1        Server2       Server3
                       
```

### Load Balancing Algorithms

### 1. Round Robin (Simple, Fair)

**How it works:** Distributes requests sequentially to each server in rotation.

```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1 (back to start)
Request 5 → Server 2
...
```

**Implementation:**
```kotlin
class RoundRobinLoadBalancer(private val servers: List<Server>) {
    private var currentIndex = AtomicInteger(0)

    fun getNextServer(): Server {
        val index = currentIndex.getAndIncrement() % servers.size
        return servers[index]
    }
}

// Usage
val lb = RoundRobinLoadBalancer(listOf(server1, server2, server3))
val request = incomingRequest()
val targetServer = lb.getNextServer()
targetServer.handle(request)
```

** Pros:**
- Simple to implement
- Fair distribution
- No server state needed
- Works well when all servers have equal capacity

** Cons:**
- Ignores server load (busy servers get same traffic as idle)
- Ignores server capacity differences
- No consideration for request complexity

**Best for:** Homogeneous servers with similar requests

---

### 2. Weighted Round Robin

**How it works:** Assigns weight to each server based on capacity. Higher weight = more requests.

```
Server 1 (weight=3) → gets 3 requests per cycle
Server 2 (weight=2) → gets 2 requests per cycle
Server 3 (weight=1) → gets 1 request per cycle

Distribution:
R1→S1, R2→S1, R3→S1,  (Server 1: 3 requests)
R4→S2, R5→S2,         (Server 2: 2 requests)
R6→S3                  (Server 3: 1 request)
[repeat cycle]
```

**Implementation:**
```kotlin
data class WeightedServer(val server: Server, val weight: Int)

class WeightedRoundRobinLoadBalancer(
    private val servers: List<WeightedServer>
) {
    private val effectiveWeights = mutableListOf<Int>()
    private var currentIndex = 0

    init {
        servers.forEach { ws ->
            effectiveWeights.addAll(List(ws.weight) { servers.indexOf(ws) })
        }
    }

    fun getNextServer(): Server {
        val serverIndex = effectiveWeights[currentIndex % effectiveWeights.size]
        currentIndex++
        return servers[serverIndex].server
    }
}

// Usage
val lb = WeightedRoundRobinLoadBalancer(
    listOf(
        WeightedServer(server1, weight = 3), // High capacity
        WeightedServer(server2, weight = 2), // Medium capacity
        WeightedServer(server3, weight = 1)  // Low capacity
    )
)
```

** Pros:**
- Handles heterogeneous servers
- Fair according to capacity
- Simple to configure

** Cons:**
- Still ignores current load
- Requires manual weight tuning

**Best for:** Servers with different capacities (e.g., m5.large vs m5.2xlarge)

---

### 3. Least Connections

**How it works:** Sends request to server with fewest active connections.

```
Before request arrives:
Server 1: 5 connections
Server 2: 3 connections  ← chosen (least connections)
Server 3: 7 connections

After routing:
Server 1: 5 connections
Server 2: 4 connections  ← now has one more
Server 3: 7 connections
```

**Implementation:**
```kotlin
class LeastConnectionsLoadBalancer(private val servers: List<Server>) {
    private val connectionCounts = ConcurrentHashMap<Server, AtomicInteger>()

    init {
        servers.forEach { connectionCounts[it] = AtomicInteger(0) }
    }

    fun getNextServer(): Server {
        return servers.minByOrNull {
            connectionCounts[it]?.get() ?: Int.MAX_VALUE
        } ?: servers.first()
    }

    fun handleRequest(request: Request) {
        val server = getNextServer()
        connectionCounts[server]?.incrementAndGet()

        try {
            server.handle(request)
        } finally {
            connectionCounts[server]?.decrementAndGet()
        }
    }
}
```

** Pros:**
- Considers current server load
- Better for long-lived connections
- Handles heterogeneous workloads

** Cons:**
- Connection count ≠ actual load
- Requires state tracking
- Slightly more overhead

**Best for:** Long-lived connections (WebSockets, database connections, streaming)

---

### 4. Weighted Least Connections

**How it works:** Combines least connections with server weights.

```kotlin
class WeightedLeastConnectionsLoadBalancer(
    private val servers: List<WeightedServer>
) {
    private val connectionCounts = ConcurrentHashMap<Server, AtomicInteger>()

    init {
        servers.forEach { ws ->
            connectionCounts[ws.server] = AtomicInteger(0)
        }
    }

    fun getNextServer(): Server {
        return servers.minByOrNull { ws ->
            val connections = connectionCounts[ws.server]?.get() ?: 0
            // Lower ratio = less loaded relative to capacity
            connections.toDouble() / ws.weight
        }?.server ?: servers.first().server
    }
}
```

**Best for:** Heterogeneous servers with long-lived connections

---

### 5. IP Hash (Session Affinity)

**How it works:** Uses client IP address to determine which server to route to. Same client always goes to same server.

```
Hash(Client IP) % Number of Servers = Server Index

Client 192.168.1.10 → Hash → Server 2 (always)
Client 192.168.1.11 → Hash → Server 1 (always)
Client 192.168.1.12 → Hash → Server 3 (always)
```

**Implementation:**
```kotlin
class IPHashLoadBalancer(private val servers: List<Server>) {

    fun getServerForClient(clientIP: String): Server {
        val hash = clientIP.hashCode()
        val index = abs(hash) % servers.size
        return servers[index]
    }
}

// Advanced: Consistent Hashing (handles server changes better)
class ConsistentHashLoadBalancer(private val servers: List<Server>) {
    private val ring = TreeMap<Int, Server>()
    private val virtualNodes = 150 // Replicas per server

    init {
        servers.forEach { server ->
            repeat(virtualNodes) { i ->
                val hash = "${server.id}-$i".hashCode()
                ring[hash] = server
            }
        }
    }

    fun getServerForClient(clientIP: String): Server {
        val hash = clientIP.hashCode()
        val entry = ring.ceilingEntry(hash) ?: ring.firstEntry()
        return entry.value
    }
}
```

** Pros:**
- Session persistence without storing session state
- Good for caching (same client = same server = cache hits)
- No session replication needed

** Cons:**
- Uneven distribution if few clients
- Server removal affects some clients
- Can't handle server capacity differences

**Best for:**
- Stateful applications
- Caching scenarios
- Applications that need session persistence

---

### 6. Least Response Time

**How it works:** Sends traffic to server with lowest response time and fewest connections.

```kotlin
class LeastResponseTimeLoadBalancer(private val servers: List<Server>) {
    private val metrics = ConcurrentHashMap<Server, ServerMetrics>()

    data class ServerMetrics(
        val activeConnections: AtomicInteger = AtomicInteger(0),
        val avgResponseTime: AtomicLong = AtomicLong(0)
    )

    init {
        servers.forEach { metrics[it] = ServerMetrics() }
    }

    fun getNextServer(): Server {
        return servers.minByOrNull { server ->
            val m = metrics[server]!!
            val connections = m.activeConnections.get()
            val avgTime = m.avgResponseTime.get()

            // Combined score: connections * avg response time
            connections * avgTime
        } ?: servers.first()
    }

    suspend fun handleRequest(request: Request) {
        val server = getNextServer()
        val m = metrics[server]!!

        m.activeConnections.incrementAndGet()
        val startTime = System.currentTimeMillis()

        try {
            server.handle(request)
        } finally {
            val responseTime = System.currentTimeMillis() - startTime

            // Update moving average
            val currentAvg = m.avgResponseTime.get()
            val newAvg = (currentAvg * 0.9 + responseTime * 0.1).toLong()
            m.avgResponseTime.set(newAvg)

            m.activeConnections.decrementAndGet()
        }
    }
}
```

** Pros:**
- Most responsive to actual server performance
- Adapts to changing conditions
- Best user experience

** Cons:**
- Complex implementation
- Requires health monitoring
- More computational overhead

**Best for:** Performance-critical applications, varying request complexities

---

### 7. Random

**How it works:** Randomly selects a server for each request.

```kotlin
class RandomLoadBalancer(private val servers: List<Server>) {
    private val random = Random()

    fun getNextServer(): Server {
        return servers[random.nextInt(servers.size)]
    }
}
```

** Pros:**
- Simple
- No state needed
- Surprisingly effective at scale

** Cons:**
- Can create imbalance with few requests
- No intelligence

**Best for:** Large-scale systems where random distribution averages out

---

### Comparison Matrix

| Algorithm | Complexity | State Required | Use Case | Server Awareness |
|-----------|-----------|----------------|----------|-----------------|
| Round Robin | Low | Minimal | Equal servers, simple requests | None |
| Weighted RR | Low | Minimal | Different server capacities | Static capacity |
| Least Connections | Medium | Yes | Long connections, varying load | Active connections |
| Weighted LC | Medium | Yes | Different capacities + long conn | Capacity + connections |
| IP Hash | Low | Minimal | Session persistence | None |
| Least Response Time | High | Yes | Performance critical | Response time + connections |
| Random | Very Low | None | Large scale, stateless | None |

---

### Real-World Configuration

**Nginx Load Balancer:**
```nginx
upstream backend {
    # Least connections algorithm
    least_conn;

    # Server definitions with weights
    server backend1.example.com weight=3 max_fails=3 fail_timeout=30s;
    server backend2.example.com weight=2 max_fails=3 fail_timeout=30s;
    server backend3.example.com weight=1 max_fails=3 fail_timeout=30s;

    # Backup server
    server backup.example.com backup;

    # Health checks
    check interval=3000 rise=2 fall=3 timeout=1000;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend;
        proxy_next_upstream error timeout http_500 http_502 http_503;

        # Session persistence (IP hash)
        # ip_hash;
    }
}
```

**AWS Application Load Balancer:**
```yaml
# Terraform configuration
resource "aws_lb_target_group" "app" {
  name     = "app-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  # Round robin by default, can use least_outstanding_requests
  load_balancing_algorithm_type = "least_outstanding_requests"

  # Health check
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  # Sticky sessions
  stickiness {
    enabled         = true
    type            = "lb_cookie"
    cookie_duration = 86400 # 24 hours
  }
}
```

---

### Advanced Patterns

### Layer 4 vs Layer 7 Load Balancing

**Layer 4 (Transport Layer):**
- Routes based on IP + Port
- Faster (doesn't inspect payload)
- Can't route based on URL path
- Examples: AWS NLB, HAProxy (TCP mode)

**Layer 7 (Application Layer):**
- Routes based on HTTP headers, URL, cookies
- Content-based routing
- Can terminate SSL
- Examples: AWS ALB, Nginx, HAProxy (HTTP mode)

```
Layer 7 Load Balancer (ALB):

  /api/*     → API servers       
  /static/*  → CDN/Static server 
  /admin/*   → Admin servers     
  User-Agent → Mobile/Web servers

```

### Health Checks

```kotlin
class HealthCheckLoadBalancer(
    private val servers: List<Server>,
    private val checkInterval: Duration = 5.seconds
) {
    private val healthyServers = ConcurrentHashMap<Server, Boolean>()

    init {
        servers.forEach { healthyServers[it] = true }
        startHealthChecks()
    }

    private fun startHealthChecks() {
        GlobalScope.launch {
            while (isActive) {
                servers.forEach { server ->
                    launch {
                        try {
                            val response = server.healthCheck()
                            healthyServers[server] = response.isOk
                        } catch (e: Exception) {
                            healthyServers[server] = false
                        }
                    }
                }
                delay(checkInterval)
            }
        }
    }

    fun getHealthyServers(): List<Server> {
        return servers.filter { healthyServers[it] == true }
    }
}
```

### Key Takeaways

1. **Round Robin** - Simple, fair, equal servers
2. **Weighted Round Robin** - Different server capacities
3. **Least Connections** - Long-lived connections
4. **IP Hash** - Session persistence/sticky sessions
5. **Least Response Time** - Best performance, complex
6. **Layer 7** load balancing enables content-based routing
7. **Health checks** are essential for high availability
8. Choose algorithm based on your specific needs
9. Most systems use **Least Connections** or **Weighted Round Robin**
10. **Sticky sessions** can be achieved with IP hash or cookies

---

## Ответ (RU)

Когда у вас есть несколько серверов, обрабатывающих запросы, вам нужен **балансировщик нагрузки** для эффективного распределения трафика между ними. Выбранный алгоритм значительно влияет на производительность, справедливость и пользовательский опыт.



### Что такое балансировка нагрузки?

**Балансировка нагрузки** распределяет входящий сетевой трафик между несколькими серверами для обеспечения:
-  Ни один сервер не перегружен
-  Высокая доступность (если один сервер падает, другие продолжают работать)
-  Лучшая производительность и время отклика
-  Эффективное использование ресурсов

### Алгоритмы балансировки нагрузки

### 1. Round Robin (Круговой, по очереди)

**Как работает:** Распределяет запросы последовательно каждому серверу по кругу.

```
Запрос 1 → Сервер 1
Запрос 2 → Сервер 2
Запрос 3 → Сервер 3
Запрос 4 → Сервер 1 (возврат к началу)
Запрос 5 → Сервер 2
...
```

** Плюсы:**
- Простая реализация
- Справедливое распределение
- Не требуется состояние сервера
- Хорошо работает когда все серверы имеют равную мощность

** Минусы:**
- Игнорирует загрузку сервера
- Игнорирует различия в мощности серверов
- Не учитывает сложность запросов

**Подходит для:** Однородных серверов с похожими запросами

---

### 2. Weighted Round Robin (Взвешенный круговой)

**Как работает:** Назначает вес каждому серверу на основе мощности. Больший вес = больше запросов.

```
Сервер 1 (вес=3) → получает 3 запроса за цикл
Сервер 2 (вес=2) → получает 2 запроса за цикл
Сервер 3 (вес=1) → получает 1 запрос за цикл
```

** Плюсы:**
- Обрабатывает разнородные серверы
- Справедливо согласно мощности
- Просто настроить

** Минусы:**
- Все еще игнорирует текущую загрузку
- Требует ручной настройки весов

**Подходит для:** Серверов с разной мощностью

---

### 3. Least Connections (Наименьшее количество соединений)

**Как работает:** Отправляет запрос на сервер с наименьшим количеством активных соединений.

```
До прибытия запроса:
Сервер 1: 5 соединений
Сервер 2: 3 соединения  ← выбран (наименьшее)
Сервер 3: 7 соединений

После маршрутизации:
Сервер 1: 5 соединений
Сервер 2: 4 соединения  ← теперь на одно больше
Сервер 3: 7 соединений
```

** Плюсы:**
- Учитывает текущую загрузку сервера
- Лучше для долгоживущих соединений
- Обрабатывает неоднородные workloads

** Минусы:**
- Количество соединений ≠ реальная нагрузка
- Требуется отслеживание состояния
- Немного больше overhead

**Подходит для:** Долгоживущих соединений (WebSockets, БД соединения, streaming)

---

### 4. IP Hash (Привязка к сессии)

**Как работает:** Использует IP адрес клиента для определения сервера. Один клиент всегда идет на один сервер.

```
Hash(IP клиента) % Количество серверов = Индекс сервера

Клиент 192.168.1.10 → Hash → Сервер 2 (всегда)
Клиент 192.168.1.11 → Hash → Сервер 1 (всегда)
```

** Плюсы:**
- Персистентность сессии без хранения состояния
- Хорошо для кеширования
- Не нужна репликация сессий

** Минусы:**
- Неравномерное распределение при малом количестве клиентов
- Удаление сервера влияет на некоторых клиентов

**Подходит для:**
- Stateful приложений
- Сценариев кеширования
- Приложений с персистентностью сессий

---

### 5. Least Response Time (Наименьшее время отклика)

**Как работает:** Отправляет трафик на сервер с наименьшим временем отклика и наименьшим количеством соединений.

** Плюсы:**
- Наиболее отзывчив к реальной производительности
- Адаптируется к изменяющимся условиям
- Лучший пользовательский опыт

** Минусы:**
- Сложная реализация
- Требуется мониторинг здоровья
- Больше вычислительных затрат

**Подходит для:** Критичных к производительности приложений

---

### Матрица сравнения

| Алгоритм | Сложность | Требуется состояние | Сценарий использования |
|----------|-----------|---------------------|------------------------|
| Round Robin | Низкая | Минимальное | Равные серверы |
| Weighted RR | Низкая | Минимальное | Разные мощности |
| Least Connections | Средняя | Да | Долгие соединения |
| IP Hash | Низкая | Минимальное | Персистентность сессий |
| Least Response Time | Высокая | Да | Критичная производительность |
| Random | Очень низкая | Нет | Большой масштаб |

### Ключевые выводы

1. **Round Robin** - Простой, справедливый, равные серверы
2. **Weighted Round Robin** - Разные мощности серверов
3. **Least Connections** - Долгоживущие соединения
4. **IP Hash** - Персистентность сессий
5. **Least Response Time** - Лучшая производительность, сложный
6. **Layer 7** балансировка позволяет маршрутизацию на основе контента
7. **Health checks** необходимы для высокой доступности
8. Выбирайте алгоритм исходя из ваших специфических потребностей
9. Большинство систем используют **Least Connections** или **Weighted Round Robin**
10. **Sticky sessions** можно реализовать через IP hash или cookies

## Follow-ups

1. What is the difference between Layer 4 and Layer 7 load balancing?
2. How do health checks work in load balancers?
3. Explain the concept of "sticky sessions" and when you need them
4. What is consistent hashing and how does it improve IP hash load balancing?
5. How do you handle SSL/TLS termination in load balancers?
6. What are the trade-offs between DNS-based and hardware load balancing?
7. How do you implement cross-region load balancing?
8. Explain the difference between active-active and active-passive load balancing
9. How do you prevent session loss during server maintenance with load balancers?
10. What metrics should you monitor to evaluate load balancer performance?

---

## Related Questions

### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
