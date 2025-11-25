---
id: sysdes-007
title: "Load Balancing Algorithms and Strategies / Алгоритмы и стратегии балансировки нагрузки"
aliases: ["Load Balancing Algorithms", "Алгоритмы балансировки нагрузки"]
topic: system-design
subtopics: [distributed-systems, load-balancing, scalability]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-caching-strategies, q-caching-strategies--system-design--medium, q-horizontal-vertical-scaling--system-design--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [algorithms, difficulty/medium, load-balancing, scalability, system-design]
sources: ["https://en.wikipedia.org/wiki/Load_balancing_(computing)"]

date created: Sunday, October 12th 2025, 8:23:57 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---

# Вопрос (RU)
> Каковы основные алгоритмы балансировки нагрузки? Когда следует использовать каждый алгоритм и каковы их компромиссы?

# Question (EN)
> What are the main load balancing algorithms? When should you use each algorithm, and what are their trade-offs?

---

## Ответ (RU)

### Требования

- Функциональные:
  - Распределение запросов между несколькими серверами
  - Поддержка различных алгоритмов балансировки нагрузки
  - Обработка недоступности инстансов (health checks, выведение из пула)
  - Возможность горизонтального масштабирования балансеров
- Нефункциональные:
  - Высокая доступность и отказоустойчивость
  - Низкая латентность при маршрутизации
  - Масштабируемость при росте трафика
  - Наблюдаемость: метрики, логирование, алёрты

### Архитектура

- Клиенты отправляют запросы на публичную точку входа (DNS или внешний балансировщик)
- L4/L7 балансировщик распределяет трафик по пулу приложений согласно выбранному алгоритму
- Балансировщик использует health checks для исключения нездоровых инстансов
- Интеграция с авто-масштабированием: при добавлении/удалении инстансов пул обновляется
- Возможна многоуровневая схема: DNS → глобальный балансировщик → региональные балансировщики → приложения/кэш/БД

**Теория балансировки нагрузки:**
Load balancing - распределение входящего трафика между несколькими серверами для обеспечения высокой доступности, производительности и эффективного использования ресурсов. Выбор алгоритма критически влияет на справедливость распределения, производительность и пользовательский опыт.

**Основные цели:**
- Предотвращение перегрузки отдельных серверов
- Высокая доступность (при отказе одного сервера работают другие)
- Лучшее время отклика
- Эффективное использование ресурсов

**1. Round Robin (Циклический):**

*Теория:* Последовательное распределение запросов по серверам по кругу. Простейший алгоритм, справедлив для гомогенных серверов.

*Работа:* Request 1 → Server 1, Request 2 → Server 2, Request 3 → Server 3, Request 4 → Server 1 (цикл)

*Преимущества:*
- Простая реализация
- Справедливое распределение при одинаковых серверах
- Не требует знания о текущей нагрузке

*Недостатки:*
- Игнорирует текущую нагрузку сервера
- Игнорирует различия в мощности серверов
- Не учитывает сложность запросов

*Сценарии:* Гомогенные серверы с похожими запросами

```kotlin
// Простейшая реализация Round Robin (иллюстративно)
class RoundRobinLoadBalancer(private val servers: List<Server>) {
    private val currentIndex = AtomicInteger(0)
    fun getNextServer(): Server {
        val i = currentIndex.getAndIncrement()
        // В реальной системе стоит добавить защиту от переполнения
        return servers[Math.floorMod(i, servers.size)]
    }
}
```

**2. Weighted Round Robin (Взвешенный циклический):**

*Теория:* Назначение весов серверам в зависимости от их мощности. Сервер с весом 3 получает примерно в 3 раза больше запросов, чем сервер с весом 1. Учитывает гетерогенность инфраструктуры.

*Работа:* Server 1 (weight=3) получает 3 запроса, Server 2 (weight=2) получает 2 запроса, Server 3 (weight=1) получает 1 запрос за цикл.

*Преимущества:*
- Обрабатывает гетерогенные серверы
- Справедливо относительно мощности
- Простая конфигурация

*Недостатки:*
- Всё ещё игнорирует текущую нагрузку
- Требует ручной настройки весов

*Сценарии:* Серверы разной мощности (m5.large vs m5.2xlarge)

```kotlin
// Упрощённый взвешенный Round Robin (иллюстративно)
data class WeightedServer(val server: Server, val weight: Int)
class WeightedRoundRobinLB(servers: List<WeightedServer>) {
    private val expandedList: List<Server> = servers.flatMap { ws -> List(ws.weight) { ws.server } }
    private val index = AtomicInteger(0)
    fun getNextServer(): Server {
        val i = index.getAndIncrement()
        // В реальной системе стоит добавить защиту от переполнения
        return expandedList[Math.floorMod(i, expandedList.size)]
    }
}
```

**3. Least Connections (Наименьшее количество соединений):**

*Теория:* Отправка запроса серверу с наименьшим количеством активных соединений. Динамически учитывает текущую нагрузку, предполагая, что меньше соединений = меньше нагрузка.

*Работа:* Перед запросом: Server 1 (5 conn), Server 2 (3 conn) ← выбран, Server 3 (7 conn)

*Преимущества:*
- Учитывает текущую нагрузку
- Лучше для long-lived соединений
- Динамическая адаптация

*Недостатки:*
- Требует отслеживания состояния
- Сложнее реализация
- Не учитывает сложность запросов

*Сценарии:* `Long`-lived соединения (WebSocket, database connections, streaming)

```kotlin
// Least Connections (упрощённо, иллюстративно)
class LeastConnectionsLB(private val servers: List<Server>) {
    private val counts = ConcurrentHashMap<Server, AtomicInteger>().apply {
        servers.forEach { putIfAbsent(it, AtomicInteger(0)) }
    }

    fun getNextServer(): Server {
        val server = servers.minByOrNull { counts[it]?.get() ?: 0 }!!
        counts[server]!!.incrementAndGet()
        return server
    }

    fun onRequestComplete(server: Server) {
        counts[server]?.decrementAndGet()
    }
}
```

**4. Least Response Time (Наименьшее время отклика):**

*Теория:* Выбор сервера с минимальным временем отклика и/или наименьшим количеством активных соединений. Комбинирует метрики производительности и нагрузки.

*Работа:* Например, можно выбирать сервер с минимальным (response_time * active_connections) либо с минимальным средним временем отклика при схожем числе соединений.

*Преимущества:*
- Учитывает фактическую производительность сервера
- Улучшает пользовательский опыт
- Адаптивен к изменениям нагрузки

*Недостатки:*
- Требует мониторинга метрик
- Более сложная реализация
- Overhead на измерения

*Сценарии:* Критичные к latency приложения (real-time, trading, gaming)

```kotlin
// Least Response Time (упрощённо, иллюстративно)
class LeastResponseTimeLB(private val servers: List<Server>) {
    private val metrics = ConcurrentHashMap<Server, ServerMetrics>()

    fun getNextServer(): Server {
        val server = servers.minByOrNull { s ->
            val m = metrics[s]
            if (m == null || m.activeConnections == 0) m?.avgResponseTime ?: 0L
            else m.avgResponseTime * m.activeConnections
        }!!
        return server
    }
}
```

**5. IP Hash (Хеширование IP):**

*Теория:* Использование хеша IP-адреса клиента для определения сервера. Обеспечивает session persistence: один клиент обычно попадает на один и тот же сервер (пока конфигурация не меняется и сервер доступен).

*Работа:* hash(client_ip) % server_count = server_index

*Преимущества:*
- Session persistence без внешнего хранилища
- Детерминированная маршрутизация
- Простая реализация

*Недостатки:*
- Неравномерное распределение при NAT
- Перераспределение при изменении количества серверов
- Не учитывает нагрузку

*Сценарии:* Stateful приложения, кеширование на сервере, legacy системы без внешнего хранилища сессий

```kotlin
// IP Hash (упрощённо)
class IPHashLoadBalancer(private val servers: List<Server>) {
    fun getServer(clientIP: String): Server {
        val hash = clientIP.hashCode()
        return servers[Math.floorMod(hash, servers.size)]
    }
}
```

**6. Consistent Hashing (Консистентное хеширование):**

*Теория:* Использование кольца хешей для минимизации перераспределения при добавлении/удалении серверов. При изменении количества серверов перемещается только часть ключей (порядка K/n, где K - количество ключей, n - серверов), а не все.

*Работа:* Серверы и ключи (запросы) размещаются на кольце хешей, запрос идёт на ближайший сервер по часовой стрелке.

*Преимущества:*
- Минимальное перераспределение при масштабировании
- Хорошо для distributed caching
- Предсказуемая маршрутизация

*Недостатки:*
- Более сложная реализация
- Для хорошего баланса обычно нужны virtual nodes
- Не учитывает текущую нагрузку

*Сценарии:* Distributed caching (Redis, Memcached), CDN, распределённые базы данных

```kotlin
// Consistent Hashing (упрощённо, иллюстративно)
class ConsistentHashLB(servers: List<Server>, virtualNodes: Int = 150) {
    private val ring = TreeMap<Int, Server>()

    init {
        servers.forEach { server ->
            repeat(virtualNodes) { i ->
                val hash = ("$server-$i").hashCode()
                ring[hash] = server
            }
        }
    }

    fun getServer(key: String): Server {
        val hash = key.hashCode()
        val entry = ring.ceilingEntry(hash) ?: ring.firstEntry()
        return entry.value
    }
}
```

**Сравнительная таблица:**

| Алгоритм | Сложность выбора (на запрос) | Состояние балансера | Справедливость | Сценарий |
|----------|------------------------------|----------------------|----------------|----------|
| Round Robin | O(1) | Да (индекс) | Высокая при одинаковых серверах | Гомогенные серверы |
| Weighted RR | O(1) | Да (индекс/веса) | Высокая относительно весов | Гетерогенные серверы |
| Least Conn | O(n) | Да (счётчики) | Высокая | `Long`-lived соединения |
| Least RT | O(n) | Да (метрики) | Высокая | Latency-critical |
| IP Hash | O(1) | Нет (по сути только конфиг) | Зависит от распределения IP | Session persistence |
| Consistent Hash | O(log n) | Нет/минимальное (кольцо) | Средняя, улучшается виртуальными нодами | Distributed cache |

**Уровни балансировки:**

*Layer 4 (Transport):* Балансировка на уровне TCP/UDP, быстрая, не видит содержимое запроса. Используется для высокой производительности.

*Layer 7 (`Application`):* Балансировка на уровне HTTP, видит URL/headers/cookies, медленнее, но гибче. Используется для content-based routing.

**Дополнительные концепции:**

- **Health checks** - периодическая проверка доступности серверов
- **Sticky sessions** - привязка клиента к серверу через cookies/маркеры
- **Connection draining** - корректное выведение инстанса из пула с завершением активных соединений
- **Auto-scaling integration** - динамическое добавление/удаление серверов

## Answer (EN)

### Requirements

- Functional:
  - Distribute requests across multiple servers
  - Support multiple load balancing algorithms
  - Handle instance failures (health checks, draining, removal from pool)
  - Allow horizontal scaling of load balancers
- Non-functional:
  - High availability and fault tolerance
  - Low latency routing
  - Scalability with traffic growth
  - Observability: metrics, logging, alerting

### Architecture

- Clients send requests to a public entry point (DNS or external load balancer)
- L4/L7 load balancer routes traffic to application pool using the chosen algorithm
- Load balancer performs health checks and stops sending traffic to unhealthy instances
- Integrated with auto-scaling: when instances are added/removed, the pool is updated
- Possible multi-layer setup: DNS → global LB → regional LBs → app/cache/DB tiers

**Load Balancing Theory:**
Load balancing is distributing incoming traffic across multiple servers to ensure high availability, performance, and efficient resource utilization. Algorithm choice critically impacts fairness, performance, and user experience.

**Main Goals:**
- Prevent individual server overload
- High availability (if one server fails, others continue)
- Better response times
- Efficient resource utilization

**1. Round Robin:**

*Theory:* Sequentially distributes requests across servers in a loop. Simplest algorithm, fair for homogeneous servers.

*How it works:* Request 1 → Server 1, Request 2 → Server 2, Request 3 → Server 3, Request 4 → Server 1 (cycle)

*Advantages:*
- Simple implementation
- Fair distribution for identical servers
- Does not require load awareness

*Disadvantages:*
- Ignores current server load
- Ignores server capacity differences
- Doesn't consider request complexity

*Use cases:* Homogeneous servers with similar requests

```kotlin
// Simple Round Robin implementation (illustrative)
class RoundRobinLoadBalancer(private val servers: List<Server>) {
    private val currentIndex = AtomicInteger(0)
    fun getNextServer(): Server {
        val i = currentIndex.getAndIncrement()
        // In real systems, handle overflow/wrap-around explicitly
        return servers[Math.floorMod(i, servers.size)]
    }
}
```

**2. Weighted Round Robin:**

*Theory:* Assigns weights to servers based on capacity. A server with weight 3 receives roughly 3x more requests than a server with weight 1. Accounts for infrastructure heterogeneity.

*How it works:* Server 1 (weight=3) gets 3 requests, Server 2 (weight=2) gets 2, Server 3 (weight=1) gets 1 per cycle.

*Advantages:*
- Handles heterogeneous servers
- Fair relative to capacity
- Simple configuration

*Disadvantages:*
- Still ignores current load
- Requires manual weight tuning

*Use cases:* Servers with different capacities (m5.large vs m5.2xlarge)

```kotlin
// Simplified Weighted Round Robin (illustrative)
data class WeightedServer(val server: Server, val weight: Int)
class WeightedRoundRobinLB(servers: List<WeightedServer>) {
    private val expandedList: List<Server> = servers.flatMap { ws -> List(ws.weight) { ws.server } }
    private val index = AtomicInteger(0)
    fun getNextServer(): Server {
        val i = index.getAndIncrement()
        // In real systems, handle overflow/wrap-around explicitly
        return expandedList[Math.floorMod(i, expandedList.size)]
    }
}
```

**3. Least Connections:**

*Theory:* Sends each new request to the server with the fewest active connections. Dynamically accounts for current load, assuming fewer connections ≈ less load.

*How it works:* Before request: Server 1 (5 conn), Server 2 (3 conn) ← chosen, Server 3 (7 conn)

*Advantages:*
- Accounts for current load
- Better for long-lived connections
- Dynamic adaptation

*Disadvantages:*
- Requires state tracking
- More complex implementation
- Doesn't consider request complexity

*Use cases:* `Long`-lived connections (WebSocket, database connections, streaming)

```kotlin
// Least Connections (simplified, illustrative)
class LeastConnectionsLB(private val servers: List<Server>) {
    private val counts = ConcurrentHashMap<Server, AtomicInteger>().apply {
        servers.forEach { putIfAbsent(it, AtomicInteger(0)) }
    }

    fun getNextServer(): Server {
        val server = servers.minByOrNull { counts[it]?.get() ?: 0 }!!
        counts[server]!!.incrementAndGet()
        return server
    }

    fun onRequestComplete(server: Server) {
        counts[server]?.decrementAndGet()
    }
}
```

**4. Least Response Time:**

*Theory:* Chooses server with the lowest observed response time and/or fewest active connections. Combines performance and load metrics.

*How it works:* For example, select server with minimal (response_time * active_connections) or minimal average latency among servers with similar load.

*Advantages:*
- Accounts for actual server performance
- Better user experience
- Adaptive to changing conditions

*Disadvantages:*
- Requires metrics collection/monitoring
- More complex implementation
- Measurement overhead

*Use cases:* Latency-critical applications (real-time, trading, gaming)

```kotlin
// Least Response Time (simplified, illustrative)
class LeastResponseTimeLB(private val servers: List<Server>) {
    private val metrics = ConcurrentHashMap<Server, ServerMetrics>()

    fun getNextServer(): Server {
        val server = servers.minByOrNull { s ->
            val m = metrics[s]
            if (m == null || m.activeConnections == 0) m?.avgResponseTime ?: 0L
            else m.avgResponseTime * m.activeConnections
        }!!
        return server
    }
}
```

**5. IP Hash:**

*Theory:* Uses a hash of the client IP address to choose server. Provides basic session persistence: the same client tends to hit the same server (while configuration is stable and server is available).

*How it works:* hash(client_ip) % server_count = server_index

*Advantages:*
- Session persistence without external storage
- Deterministic routing
- Simple implementation

*Disadvantages:*
- Uneven distribution with NAT
- Rebalancing when server count changes
- Doesn't account for load

*Use cases:* Stateful applications, server-side caching, legacy systems without external session storage

```kotlin
// IP Hash (simplified)
class IPHashLoadBalancer(private val servers: List<Server>) {
    fun getServer(clientIP: String): Server {
        val hash = clientIP.hashCode()
        return servers[Math.floorMod(hash, servers.size)]
    }
}
```

**6. Consistent Hashing:**

*Theory:* Uses a hash ring to minimize redistribution when adding/removing servers. When server count changes, only a fraction (~K/n) of keys move instead of all keys.

*How it works:* Servers and keys are placed on a hash ring; each key maps to the next server clockwise.

*Advantages:*
- Minimal redistribution on scaling
- Great for distributed caching
- Predictable routing

*Disadvantages:*
- More complex implementation
- Needs virtual nodes for good balance
- Doesn't inherently account for current load

*Use cases:* Distributed caching (Redis, Memcached), CDNs, distributed databases

```kotlin
// Consistent Hashing (simplified, illustrative)
class ConsistentHashLB(servers: List<Server>, virtualNodes: Int = 150) {
    private val ring = TreeMap<Int, Server>()

    init {
        servers.forEach { server ->
            repeat(virtualNodes) { i ->
                val hash = ("$server-$i").hashCode()
                ring[hash] = server
            }
        }
    }

    fun getServer(key: String): Server {
        val hash = key.hashCode()
        val entry = ring.ceilingEntry(hash) ?: ring.firstEntry()
        return entry.value
    }
}
```

**Comparison Table:**

| Algorithm | Selection Complexity (per request) | Balancer State | Fairness | Use Case |
|-----------|------------------------------------|----------------|----------|----------|
| Round Robin | O(1) | Yes (index) | High for homogeneous servers | Homogeneous servers |
| Weighted RR | O(1) | Yes (index/weights) | High relative to weights | Heterogeneous servers |
| Least Conn | O(n) | Yes (connection counters) | High | `Long`-lived connections |
| Least RT | O(n) | Yes (metrics) | High | Latency-critical |
| IP Hash | O(1) | No (beyond config) | Depends on IP distribution | Session persistence |
| Consistent Hash | O(log n) | Minimal (hash ring) | Medium, improved with virtual nodes | Distributed cache |

**Load Balancing Layers:**

*Layer 4 (Transport):* Balancing at TCP/UDP level, fast, unaware of request content. Used for high throughput and generic traffic.

*Layer 7 (`Application`):* Balancing at HTTP/application level, can inspect URL/headers/cookies, slower but more flexible. Used for content-based routing.

**Additional Concepts:**

- **Health checks** - periodic verification of server availability
- **Sticky sessions** - client-to-server affinity via cookies/tokens
- **Connection draining** - graceful instance removal allowing active connections to complete
- **Auto-scaling integration** - dynamic server addition/removal

---

## Follow-ups

- How do you implement health checks for load balancers?
- What is the difference between Layer 4 and Layer 7 load balancing?
- How do you handle session persistence in distributed systems?

## References

- "Load balancing (computing)" on Wikipedia: "https://en.wikipedia.org/wiki/Load_balancing_(computing)"
- [[c-caching-strategies]]

## Related Questions

### Prerequisites (Easier)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies
- [[q-caching-strategies--system-design--medium]] - Caching patterns

### Related (Same Level)
- [[q-design-url-shortener--system-design--medium]] - System design example
- [[q-rest-api-design-best-practices--system-design--medium]] - API design

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Data distribution
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Distributed systems theory