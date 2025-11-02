---
id: sysdes-007
title: "Load Balancing Algorithms and Strategies / Алгоритмы и стратегии балансировки нагрузки"
aliases: ["Load Balancing Algorithms", "Алгоритмы балансировки нагрузки"]
topic: system-design
subtopics: [distributed-systems, high-availability, load-balancing, scalability]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-load-balancing, q-caching-strategies--system-design--medium, q-horizontal-vertical-scaling--system-design--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [algorithms, difficulty/medium, load-balancing, scalability, system-design]
sources: [https://en.wikipedia.org/wiki/Load_balancing_(computing)]
date created: Sunday, October 12th 2025, 8:23:57 pm
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)
> Каковы основные алгоритмы балансировки нагрузки? Когда следует использовать каждый алгоритм и каковы их компромиссы?

# Question (EN)
> What are the main load balancing algorithms? When should you use each algorithm, and what are their trade-offs?

---

## Ответ (RU)

**Теория балансировки нагрузки:**
Load balancing - распределение входящего трафика между несколькими серверами для обеспечения высокой доступности, производительности и эффективного использования ресурсов. Выбор алгоритма критически влияет на справедливость распределения, производительность и пользовательский опыт.

**Основные цели:**
- Предотвращение перегрузки отдельных серверов
- Высокая доступность (при отказе одного сервера работают другие)
- Лучшее время отклика
- Эффективное использование ресурсов

**1. Round Robin (Циклический):**

*Теория:* Последовательное распределение запросов по серверам в порядке очереди. Простейший алгоритм, не требует состояния, справедлив для гомогенных серверов.

*Работа:* Request 1 → Server 1, Request 2 → Server 2, Request 3 → Server 3, Request 4 → Server 1 (цикл)

*Преимущества:*
- Простая реализация
- Справедливое распределение
- Не требует состояния сервера
- Работает хорошо для одинаковых серверов

*Недостатки:*
- Игнорирует текущую нагрузку сервера
- Игнорирует различия в мощности серверов
- Не учитывает сложность запросов

*Сценарии:* Гомогенные серверы с похожими запросами

```kotlin
// Простейшая реализация Round Robin
class RoundRobinLoadBalancer(private val servers: List<Server>) {
    private var currentIndex = AtomicInteger(0)
    fun getNextServer() = servers[currentIndex.getAndIncrement() % servers.size]
}
```

**2. Weighted Round Robin (Взвешенный циклический):**

*Теория:* Назначение весов серверам в зависимости от их мощности. Сервер с весом 3 получает в 3 раза больше запросов, чем сервер с весом 1. Учитывает гетерогенность инфраструктуры.

*Работа:* Server 1 (weight=3) получает 3 запроса, Server 2 (weight=2) получает 2 запроса, Server 3 (weight=1) получает 1 запрос за цикл

*Преимущества:*
- Обрабатывает гетерогенные серверы
- Справедливо относительно мощности
- Простая конфигурация

*Недостатки:*
- Всё ещё игнорирует текущую нагрузку
- Требует ручной настройки весов

*Сценарии:* Серверы разной мощности (m5.large vs m5.2xlarge)

```kotlin
// Взвешенный Round Robin
data class WeightedServer(val server: Server, val weight: Int)
class WeightedRoundRobinLB(servers: List<WeightedServer>) {
    private val expandedList = servers.flatMap { ws -> List(ws.weight) { ws.server } }
    private var index = AtomicInteger(0)
    fun getNextServer() = expandedList[index.getAndIncrement() % expandedList.size]
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

*Сценарии:* Long-lived соединения (WebSocket, database connections, streaming)

```kotlin
// Least Connections
class LeastConnectionsLB(private val servers: List<Server>) {
    private val counts = ConcurrentHashMap<Server, AtomicInteger>()
    fun getNextServer() = servers.minByOrNull { counts[it]?.get() ?: 0 }!!
    fun onRequestComplete(server: Server) { counts[server]?.decrementAndGet() }
}
```

**4. Least Response Time (Наименьшее время отклика):**

*Теория:* Выбор сервера с наименьшим временем отклика и наименьшим количеством активных соединений. Комбинирует метрики производительности и нагрузки для оптимального выбора.

*Работа:* Выбирается сервер с минимальным (response_time * active_connections)

*Преимущества:*
- Учитывает производительность сервера
- Лучший user experience
- Адаптивный к производительности

*Недостатки:*
- Требует мониторинга метрик
- Сложная реализация
- Overhead на измерения

*Сценарии:* Критичные к latency приложения (real-time, trading, gaming)

```kotlin
// Least Response Time
class LeastResponseTimeLB(private val servers: List<Server>) {
    private val metrics = ConcurrentHashMap<Server, ServerMetrics>()
    fun getNextServer() = servers.minByOrNull {
        val m = metrics[it]!!
        m.avgResponseTime * m.activeConnections
    }!!
}
```

**5. IP Hash (Хеширование IP):**

*Теория:* Использование хеша IP-адреса клиента для определения сервера. Обеспечивает session persistence - один клиент всегда попадает на один сервер (пока сервер доступен).

*Работа:* hash(client_ip) % server_count = server_index

*Преимущества:*
- Session persistence без внешнего хранилища
- Детерминированная маршрутизация
- Простая реализация

*Недостатки:*
- Неравномерное распределение при NAT
- Проблемы при изменении количества серверов
- Не учитывает нагрузку

*Сценарии:* Stateful приложения, кеширование на сервере, legacy системы без внешней сессии

```kotlin
// IP Hash
class IPHashLoadBalancer(private val servers: List<Server>) {
    fun getServer(clientIP: String): Server {
        val hash = clientIP.hashCode().absoluteValue
        return servers[hash % servers.size]
    }
}
```

**6. Consistent Hashing (Консистентное хеширование):**

*Теория:* Использование кольца хешей для минимизации перераспределения при добавлении/удалении серверов. При изменении количества серверов перемещается только K/n ключей (K - ключи, n - серверы), а не все.

*Работа:* Серверы и запросы размещаются на кольце хешей, запрос идёт на ближайший сервер по часовой стрелке

*Преимущества:*
- Минимальное перераспределение при масштабировании
- Хорошо для distributed caching
- Predictable routing

*Недостатки:*
- Сложная реализация
- Требует virtual nodes для баланса
- Не учитывает текущую нагрузку

*Сценарии:* Distributed caching (Redis, Memcached), CDN, distributed databases

```kotlin
// Consistent Hashing (упрощённо)
class ConsistentHashLB(servers: List<Server>, virtualNodes: Int = 150) {
    private val ring = TreeMap<Int, Server>()
    init {
        servers.forEach { server ->
            repeat(virtualNodes) { i ->
                ring["$server-$i".hashCode()] = server
            }
        }
    }
    fun getServer(key: String) = ring.ceilingEntry(key.hashCode())?.value ?: ring.firstEntry().value
}
```

**Сравнительная таблица:**

| Алгоритм | Сложность | State | Справедливость | Сценарий |
|----------|-----------|-------|----------------|----------|
| Round Robin | O(1) | Нет | Высокая | Гомогенные серверы |
| Weighted RR | O(1) | Нет | Средняя | Гетерогенные серверы |
| Least Conn | O(n) | Да | Высокая | Long-lived соединения |
| Least RT | O(n) | Да | Высокая | Latency-critical |
| IP Hash | O(1) | Нет | Низкая | Session persistence |
| Consistent Hash | O(log n) | Нет | Средняя | Distributed cache |

**Уровни балансировки:**

*Layer 4 (Transport):* Балансировка на уровне TCP/UDP, быстрая, не видит содержимое запроса. Используется для высокой производительности.

*Layer 7 (Application):* Балансировка на уровне HTTP, видит URL/headers/cookies, медленнее, но умнее. Используется для content-based routing.

**Дополнительные концепции:**

- **Health checks** - периодическая проверка доступности серверов
- **Sticky sessions** - привязка клиента к серверу через cookies
- **Connection draining** - graceful shutdown с завершением активных соединений
- **Auto-scaling integration** - динамическое добавление/удаление серверов

## Answer (EN)

**Load Balancing Theory:**
Load balancing - distributing incoming traffic across multiple servers to ensure high availability, performance, and efficient resource utilization. Algorithm choice critically impacts distribution fairness, performance, and user experience.

**Main Goals:**
- Prevent individual server overload
- High availability (if one server fails, others continue)
- Better response times
- Efficient resource utilization

**1. Round Robin (Sequential):**

*Theory:* Sequential distribution of requests across servers in queue order. Simplest algorithm, requires no state, fair for homogeneous servers.

*How it works:* Request 1 → Server 1, Request 2 → Server 2, Request 3 → Server 3, Request 4 → Server 1 (cycle)

*Advantages:*
- Simple implementation
- Fair distribution
- No server state needed
- Works well for identical servers

*Disadvantages:*
- Ignores current server load
- Ignores server capacity differences
- Doesn't consider request complexity

*Use cases:* Homogeneous servers with similar requests

```kotlin
// Simple Round Robin implementation
class RoundRobinLoadBalancer(private val servers: List<Server>) {
    private var currentIndex = AtomicInteger(0)
    fun getNextServer() = servers[currentIndex.getAndIncrement() % servers.size]
}
```

**2. Weighted Round Robin:**

*Theory:* Assigning weights to servers based on their capacity. Server with weight 3 gets 3x more requests than server with weight 1. Accounts for infrastructure heterogeneity.

*How it works:* Server 1 (weight=3) gets 3 requests, Server 2 (weight=2) gets 2 requests, Server 3 (weight=1) gets 1 request per cycle

*Advantages:*
- Handles heterogeneous servers
- Fair relative to capacity
- Simple configuration

*Disadvantages:*
- Still ignores current load
- Requires manual weight tuning

*Use cases:* Servers with different capacities (m5.large vs m5.2xlarge)

```kotlin
// Weighted Round Robin
data class WeightedServer(val server: Server, val weight: Int)
class WeightedRoundRobinLB(servers: List<WeightedServer>) {
    private val expandedList = servers.flatMap { ws -> List(ws.weight) { ws.server } }
    private var index = AtomicInteger(0)
    fun getNextServer() = expandedList[index.getAndIncrement() % expandedList.size]
}
```

**3. Least Connections:**

*Theory:* Sending request to server with fewest active connections. Dynamically accounts for current load, assuming fewer connections = less load.

*How it works:* Before request: Server 1 (5 conn), Server 2 (3 conn) ← chosen, Server 3 (7 conn)

*Advantages:*
- Accounts for current load
- Better for long-lived connections
- Dynamic adaptation

*Disadvantages:*
- Requires state tracking
- More complex implementation
- Doesn't consider request complexity

*Use cases:* Long-lived connections (WebSocket, database connections, streaming)

```kotlin
// Least Connections
class LeastConnectionsLB(private val servers: List<Server>) {
    private val counts = ConcurrentHashMap<Server, AtomicInteger>()
    fun getNextServer() = servers.minByOrNull { counts[it]?.get() ?: 0 }!!
    fun onRequestComplete(server: Server) { counts[server]?.decrementAndGet() }
}
```

**4. Least Response Time:**

*Theory:* Choosing server with lowest response time and fewest active connections. Combines performance and load metrics for optimal selection.

*How it works:* Selects server with minimum (response_time * active_connections)

*Advantages:*
- Accounts for server performance
- Better user experience
- Adaptive to performance

*Disadvantages:*
- Requires metrics monitoring
- Complex implementation
- Measurement overhead

*Use cases:* Latency-critical applications (real-time, trading, gaming)

```kotlin
// Least Response Time
class LeastResponseTimeLB(private val servers: List<Server>) {
    private val metrics = ConcurrentHashMap<Server, ServerMetrics>()
    fun getNextServer() = servers.minByOrNull {
        val m = metrics[it]!!
        m.avgResponseTime * m.activeConnections
    }!!
}
```

**5. IP Hash:**

*Theory:* Using client IP address hash to determine server. Provides session persistence - one client always hits same server (while server is available).

*How it works:* hash(client_ip) % server_count = server_index

*Advantages:*
- Session persistence without external storage
- Deterministic routing
- Simple implementation

*Disadvantages:*
- Uneven distribution with NAT
- Problems when server count changes
- Doesn't account for load

*Use cases:* Stateful applications, server-side caching, legacy systems without external sessions

```kotlin
// IP Hash
class IPHashLoadBalancer(private val servers: List<Server>) {
    fun getServer(clientIP: String): Server {
        val hash = clientIP.hashCode().absoluteValue
        return servers[hash % servers.size]
    }
}
```

**6. Consistent Hashing:**

*Theory:* Using hash ring to minimize redistribution when adding/removing servers. When server count changes, only K/n keys move (K - keys, n - servers), not all.

*How it works:* Servers and requests placed on hash ring, request goes to nearest server clockwise

*Advantages:*
- Minimal redistribution on scaling
- Good for distributed caching
- Predictable routing

*Disadvantages:*
- Complex implementation
- Requires virtual nodes for balance
- Doesn't account for current load

*Use cases:* Distributed caching (Redis, Memcached), CDN, distributed databases

```kotlin
// Consistent Hashing (simplified)
class ConsistentHashLB(servers: List<Server>, virtualNodes: Int = 150) {
    private val ring = TreeMap<Int, Server>()
    init {
        servers.forEach { server ->
            repeat(virtualNodes) { i ->
                ring["$server-$i".hashCode()] = server
            }
        }
    }
    fun getServer(key: String) = ring.ceilingEntry(key.hashCode())?.value ?: ring.firstEntry().value
}
```

**Comparison Table:**

| Algorithm | Complexity | State | Fairness | Use Case |
|-----------|-----------|-------|----------|----------|
| Round Robin | O(1) | No | High | Homogeneous servers |
| Weighted RR | O(1) | No | Medium | Heterogeneous servers |
| Least Conn | O(n) | Yes | High | Long-lived connections |
| Least RT | O(n) | Yes | High | Latency-critical |
| IP Hash | O(1) | No | Low | Session persistence |
| Consistent Hash | O(log n) | No | Medium | Distributed cache |

**Load Balancing Layers:**

*Layer 4 (Transport):* Balancing at TCP/UDP level, fast, doesn't see request content. Used for high performance.

*Layer 7 (Application):* Balancing at HTTP level, sees URL/headers/cookies, slower but smarter. Used for content-based routing.

**Additional Concepts:**

- **Health checks** - periodic server availability verification
- **Sticky sessions** - client-to-server binding via cookies
- **Connection draining** - graceful shutdown with active connection completion
- **Auto-scaling integration** - dynamic server addition/removal

---

## Follow-ups

- How do you implement health checks for load balancers?
- What is the difference between Layer 4 and Layer 7 load balancing?
- How do you handle session persistence in distributed systems?

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
