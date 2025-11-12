---
id: sysdes-009
title: "Horizontal vs Vertical Scaling / Горизонтальное vs Вертикальное масштабирование"
aliases: ["Horizontal vs Vertical Scaling", "Горизонтальное vs Вертикальное масштабирование"]
topic: system-design
subtopics: [distributed-systems, performance, scalability]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [q-database-sharding-partitioning--system-design--hard, q-load-balancing-strategies--system-design--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [architecture, difficulty/medium, distributed-systems, scalability, system-design]
sources: ["https://en.wikipedia.org/wiki/Scalability"]

---

# Вопрос (RU)
> В чём разница между горизонтальным и вертикальным масштабированием? Когда следует использовать каждый подход, и каковы их компромиссы?

# Question (EN)
> What is the difference between horizontal and vertical scaling? When should you use each approach, and what are their trade-offs?

## Ответ (RU)

**Теория масштабирования:**
Масштабирование - процесс увеличения ёмкости системы для обработки растущей нагрузки. Два фундаментальных подхода: вертикальное (scaling up) - увеличение ресурсов одного сервера, и горизонтальное (scaling out) - добавление большего количества серверов.

**Вертикальное масштабирование (Scaling Up):**

*Теория:* Добавление ресурсов (CPU, RAM, диск) к существующему серверу. Простой подход, часто не требует изменений в коде, но имеет физические ограничения и создаёт single point of failure.

*Примеры:*
- Увеличение CPU с 4 до 16 ядер
- Увеличение RAM с 16GB до 128GB
- Переход на более быстрое SSD-хранилище

*Преимущества:*
- Простота (часто без изменений кода)
- Низкая задержка (одна машина)
- Простая модель консистентности данных
- Не нужен load balancer

*Недостатки:*
- Дорого (часто нелинейный, близкий к экспоненциальному рост стоимости за дополнительные ресурсы)
- Физические ограничения (максимум CPU/RAM)
- Single point of failure
- Часто требуется downtime для обновления

*Сценарии использования:*
- Базы данных (RDBMS, где распределённые записи сложны)
- Legacy-приложения (не могут быть легко распределены)
- Однопоточные нагрузки
- Быстрые временные решения (buy time)

# Вертикальное масштабирование PostgreSQL (RU пример)
Initial: m5.large (2 vCPU, 8GB RAM)
Scale:   m5.4xlarge (16 vCPU, 64GB RAM)
# Нет изменений в приложении, ACID гарантии сохранены

**Горизонтальное масштабирование (Scaling Out):**

*Теория:* Добавление большего количества серверов в пул ресурсов. Более сложный подход, обычно требует stateless-дизайна для сервисов и распределённой логики, но обеспечивает высокий потенциал масштабирования и высокую доступность при правильной архитектуре.

*Примеры:*
- Добавление веб-серверов за load balancer
- Добавление read replicas для БД
- Увеличение количества инстансов приложения

*Преимущества:*
- Практически неограниченное масштабирование (в пределах архитектурных ограничений)
- Как правило дешевле (более предсказуемый, близкий к линейному рост стоимости)
- Возможность уменьшить риск single point of failure (при отказоустойчивой архитектуре без одиночных центральных точек)
- Zero-downtime обновления часто достижимы
- Высокая доступность

*Недостатки:*
- Повышенная сложность (распределённая логика, синхронизация)
- Сетевая задержка между компонентами
- Более сложная консистентность данных
- Требуется load balancer или иной механизм распределения трафика
- Stateless-дизайн сервисов настоятельно рекомендуется; для stateful-компонентов нужны дополнительные механизмы (шардинг, репликация)

*Сценарии использования:*
- Веб-серверы (stateless HTTP-серверы)
- API-сервисы (RESTful APIs)
- Микросервисы
- Read-heavy нагрузки
- Глобальное распределение трафика

```kotlin
// Stateless дизайн для горизонтального масштабирования
class UserService(
    private val cache: RedisCache,  // Внешнее состояние
    private val database: Database
) {
    fun getUser(userId: Long): User {
        // Нет локального состояния - может работать на любом сервере
        return cache.get(userId) ?: database.findUser(userId)
    }
}
```

**Сравнительная матрица:**

| Аспект | Вертикальное | Горизонтальное |
|--------|--------------|----------------|
| Стоимость | Дорого (нелинейно) | Дешевле (почти линейно) |
| Сложность | Просто | Сложно |
| Ограничения | Жёсткие физические лимиты | Выше пределы, зависят от архитектуры |
| Downtime | Часто требуется | Zero downtime возможен |
| SPOF | Да | Может быть устранён при правильном дизайне |
| Консистентность | Легко | Сложнее |

**Гибридный подход (наиболее распространённый):**

*Теория:* Большинство production-систем используют оба подхода. Веб-серверы масштабируются горизонтально (stateless, легко добавлять), базы данных часто сначала масштабируются вертикально (primary на более мощной машине) + горизонтально (read replicas), а при дальнейшем росте нагрузки могут использоваться более продвинутые техники (шардинг/partitioning и др.).

```kotlin
// Типичная архитектура
// Load Balancer → Web Servers (horizontal, 3-50 instances)
//              → Redis Cache (horizontal cluster)
//              → Primary DB (vertical, large instance)
//              → Read Replicas (horizontal, 2-5 instances)
```

**Ключевые принципы для горизонтального масштабирования:**
1. Stateless-дизайн сервисов, где возможно — состояние в Redis/БД, не в памяти конкретного сервера
2. Load balancing — равномерное распределение нагрузки
3. Shared storage — S3/NFS для файлов, не только локальный диск
4. Database separation — отдельный tier для данных
5. Idempotency — операции можно повторять безопасно

### Требования (RU)

**Функциональные:**
- Обработка растущего числа запросов.
- Обеспечение непрерывной работы сервиса при обновлениях и отказах отдельных узлов.

**Нефункциональные:**
- Высокая доступность и отказоустойчивость.
- Масштабируемость (возможность увеличивать ресурсы вертикально и/или горизонтально).
- Предсказуемая производительность при росте нагрузки.

### Архитектура (RU)

- Вертикальное масштабирование: усиление одного узла (например, одного инстанса БД или монолита) до тех пор, пока это экономически и технически оправдано.
- Горизонтальное масштабирование: использование нескольких экземпляров сервисов за load balancer, разделение состояния через общие хранилища, кеши и реплики БД.
- Комбинированный подход: вертикальное усиление критичных компонентов (например, primary DB) плюс горизонтальное масштабирование stateless-слоёв и чтений.

### Дополнительные вопросы (RU)

- Как обрабатывать сессионное состояние в горизонтально масштабируемых приложениях?
- В чём разница между stateless и stateful сервисами?
- Как реализовать авто-масштабирование для горизонтального масштабирования?

### Ссылки (RU)

- [[q-load-balancing-strategies--system-design--medium]]
- [[q-database-sharding-partitioning--system-design--hard]]

### Связанные вопросы (RU)

#### Предпосылки (проще)
- [[q-load-balancing-strategies--system-design--medium]] - Стратегии балансировки нагрузки
- [[q-caching-strategies--system-design--medium]] - Стратегии кеширования

#### Похожие (средний уровень)
- [[q-design-url-shortener--system-design--medium]] - Пример проектирования системы
- [[q-rest-api-design-best-practices--system-design--medium]] - Рекомендации по проектированию API

#### Продвинутые (сложнее)
- [[q-database-sharding-partitioning--system-design--hard]] - Шардинг и партиционирование баз данных
- [[q-microservices-vs-monolith--system-design--hard]] - Паттерны архитектуры

## Answer (EN)

**Scaling Theory:**
Scaling is the process of increasing system capacity to handle growing load. Two fundamental approaches: vertical (scaling up) - increasing resources of a single server, and horizontal (scaling out) - adding more servers.

**Vertical Scaling (Scaling Up):**

*Theory:* Adding resources (CPU, RAM, disk) to an existing server. A simple approach that often requires no or minimal code changes, but has physical limits and creates a single point of failure.

*Examples:*
- Increase CPU from 4 to 16 cores
- Increase RAM from 16GB to 128GB
- Switch to faster SSD storage

*Advantages:*
- Simple (often no code changes)
- Low latency (single machine)
- Simple data consistency model
- No load balancer needed

*Disadvantages:*
- Expensive (often non-linear, near-exponential cost for high-end hardware)
- Physical limits (max CPU/RAM)
- Single point of failure
- Often requires downtime for upgrade

*Use cases:*
- Databases (RDBMS where distributed writes are complex)
- Legacy applications (cannot be easily distributed)
- Single-threaded workloads
- `Short`-term quick fixes (to buy time)

# Vertical scaling PostgreSQL (EN example)
Initial: m5.large (2 vCPU, 8GB RAM)
Scale:   m5.4xlarge (16 vCPU, 64GB RAM)
# No application changes, ACID guarantees maintained

**Horizontal Scaling (Scaling Out):**

*Theory:* Adding more servers to the resource pool. A more complex approach that typically requires stateless service design and distributed logic, but enables high scalability potential and high availability when architected correctly.

*Examples:*
- Add web servers behind a load balancer
- Add read replicas for DB
- Increase number of application instances

*Advantages:*
- Virtually unlimited scaling (bounded by architecture, not a single machine)
- Typically cheaper (more predictable, near-linear cost growth)
- Can reduce single point of failure risk (if you avoid centralized bottlenecks)
- Zero-downtime deployments often achievable
- High availability

*Disadvantages:*
- Higher complexity (distributed logic, coordination)
- Network latency between components
- More complex data consistency
- Requires a load balancer or similar traffic distribution mechanism
- Stateless design is strongly recommended; stateful components require extra mechanisms (sharding, replication)

*Use cases:*
- Web servers (stateless HTTP servers)
- API services (RESTful APIs)
- Microservices
- Read-heavy workloads
- Global traffic distribution

```kotlin
// Stateless design for horizontal scaling
class UserService(
    private val cache: RedisCache,  // External state
    private val database: Database
) {
    fun getUser(userId: Long): User {
        // No local state - can run on any server
        return cache.get(userId) ?: database.findUser(userId)
    }
}
```

**Comparison Matrix:**

| Aspect | Vertical | Horizontal |
|--------|----------|------------|
| Cost | Expensive (non-linear) | Cheaper (near-linear) |
| Complexity | Simple | Complex |
| Limits | Hard physical limits | Higher limits, depend on architecture |
| Downtime | Often required | Zero downtime possible |
| SPOF | Yes | Can be eliminated with proper design |
| Consistency | Easy | More challenging |

**Hybrid Approach (most common):**

*Theory:* Most production systems use both approaches. Web servers scale horizontally (stateless, easy to add), databases often scale vertically first (primary on a larger instance) + horizontally (read replicas), and at higher scale may use advanced techniques (sharding/partitioning, etc.).

```kotlin
// Typical architecture
// Load Balancer → Web Servers (horizontal, 3-50 instances)
//              → Redis Cache (horizontal cluster)
//              → Primary DB (vertical, large instance)
//              → Read Replicas (horizontal, 2-5 instances)
```

**Key Principles for Horizontal Scaling:**
1. Stateless design for services where possible — state in Redis/DB, not in server memory.
2. Load balancing — even traffic distribution.
3. Shared storage — S3/NFS for files, not only local disk.
4. Database separation — separate tier for data.
5. Idempotency — operations can be safely retried.

### Requirements

**Functional:**
- Handle increasing number of requests.
- Ensure continuous service operation during deployments and individual node failures.

**Non-functional:**
- High availability and fault tolerance.
- Scalability (ability to grow vertically and/or horizontally).
- Predictable performance as load increases.

### Architecture

- Vertical scaling: strengthen a single node (e.g., a DB instance or monolith) while it is cost-effective and technically feasible.
- Horizontal scaling: multiple service instances behind a load balancer, with shared storage, caches, and DB replicas to distribute state and load.
- Combined strategy: vertically scale critical components (e.g., primary DB) and horizontally scale stateless layers and read paths.

### Follow-ups

- How do you handle session state in horizontally scaled applications?
- What is the difference between stateless and stateful services?
- How do you implement auto-scaling for horizontal scaling?

### References

- [[q-load-balancing-strategies--system-design--medium]]
- [[q-database-sharding-partitioning--system-design--hard]]

### Related Questions

#### Prerequisites (Easier)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing
- [[q-caching-strategies--system-design--medium]] - Caching strategies

#### Related (Same Level)
- [[q-design-url-shortener--system-design--medium]] - System design example
- [[q-rest-api-design-best-practices--system-design--medium]] - API design

#### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Database sharding
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
