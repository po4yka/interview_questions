---
id: sysdes-009
title: "Horizontal vs Vertical Scaling / Горизонтальное vs Вертикальное масштабирование"
aliases: ["Horizontal vs Vertical Scaling", "Горизонтальное vs Вертикальное масштабирование"]
topic: system-design
subtopics: [distributed-systems, performance, scalability, scaling]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-scaling-strategies, q-database-sharding-partitioning--system-design--hard, q-load-balancing-strategies--system-design--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [architecture, difficulty/medium, distributed-systems, scalability, system-design]
sources: [https://en.wikipedia.org/wiki/Scalability]
date created: Sunday, October 12th 2025, 8:22:20 pm
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)
> В чём разница между горизонтальным и вертикальным масштабированием? Когда следует использовать каждый подход, и каковы их компромиссы?

# Question (EN)
> What is the difference between horizontal and vertical scaling? When should you use each approach, and what are their trade-offs?

---

## Ответ (RU)

**Теория масштабирования:**
Масштабирование - процесс увеличения ёмкости системы для обработки растущей нагрузки. Два фундаментальных подхода: вертикальное (scaling up) - увеличение ресурсов одного сервера, и горизонтальное (scaling out) - добавление большего количества серверов.

**Вертикальное масштабирование (Scaling Up):**

*Теория:* Добавление ресурсов (CPU, RAM, диск) к существующему серверу. Простой подход, не требует изменений в коде, но имеет физические ограничения и является single point of failure.

*Примеры:*
- Увеличение CPU с 4 до 16 ядер
- Увеличение RAM с 16GB до 128GB
- Переход на более быстрое SSD хранилище

*Преимущества:*
- Простота (нет изменений кода)
- Низкая задержка (одна машина)
- Легкая консистентность данных
- Не нужен load balancer

*Недостатки:*
- Дорого (экспоненциальный рост стоимости)
- Физические ограничения (максимум CPU/RAM)
- Single point of failure
- Требуется downtime для обновления

*Сценарии использования:*
- Базы данных (RDBMS где распределённые записи сложны)
- Legacy приложения (не могут быть легко распределены)
- Однопоточные workloads
- Быстрые исправления

```yaml
# Вертикальное масштабирование PostgreSQL
Initial: m5.large (2 vCPU, 8GB RAM)
Scale:   m5.4xlarge (16 vCPU, 64GB RAM)
# Нет изменений в приложении, ACID гарантии сохранены
```

**Горизонтальное масштабирование (Scaling Out):**

*Теория:* Добавление большего количества серверов в пул ресурсов. Более сложный подход, требует stateless дизайна и распределённой логики, но обеспечивает практически неограниченное масштабирование и высокую доступность.

*Примеры:*
- Добавление веб-серверов за load balancer
- Добавление read replicas для БД
- Увеличение количества инстансов приложения

*Преимущества:*
- Практически неограниченное масштабирование
- Дешевле (линейный рост стоимости)
- Нет single point of failure
- Zero downtime возможен
- Высокая доступность

*Недостатки:*
- Сложность (распределённая логика)
- Сетевая задержка
- Сложная консистентность данных
- Требуется load balancer
- Stateless дизайн обязателен

*Сценарии использования:*
- Веб-серверы (stateless HTTP серверы)
- API сервисы (RESTful APIs)
- Микросервисы
- Read-heavy workloads
- Глобальное распределение

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
| Стоимость | Дорого (экспоненциально) | Дешевле (линейно) |
| Сложность | Просто | Сложно |
| Ограничения | Физические лимиты | Практически нет |
| Downtime | Обычно требуется | Zero downtime возможен |
| SPOF | Да | Нет |
| Консистентность | Легко | Сложно |

**Гибридный подход (наиболее распространённый):**

*Теория:* Большинство production систем используют оба подхода. Веб-серверы масштабируются горизонтально (stateless, легко добавлять), базы данных масштабируются вертикально (primary) + горизонтально (read replicas).

```kotlin
// Типичная архитектура
// Load Balancer → Web Servers (horizontal, 3-50 instances)
//              → Redis Cache (horizontal cluster)
//              → Primary DB (vertical, large instance)
//              → Read Replicas (horizontal, 2-5 instances)
```

**Ключевые принципы для горизонтального масштабирования:**

1. **Stateless дизайн** - состояние в Redis/БД, не в памяти сервера
2. **Load balancing** - равномерное распределение нагрузки
3. **Shared storage** - S3/NFS для файлов, не локальный диск
4. **Database separation** - отдельный tier для данных
5. **Idempotency** - операции можно повторять безопасно

## Answer (EN)

**Scaling Theory:**
Scaling is the process of increasing system capacity to handle growing load. Two fundamental approaches: vertical (scaling up) - increasing resources of one server, and horizontal (scaling out) - adding more servers.

**Vertical Scaling (Scaling Up):**

*Theory:* Adding resources (CPU, RAM, disk) to existing server. Simple approach, requires no code changes, but has physical limitations and is single point of failure.

*Examples:*
- Increase CPU from 4 to 16 cores
- Increase RAM from 16GB to 128GB
- Switch to faster SSD storage

*Advantages:*
- Simple (no code changes)
- Low latency (single machine)
- Easy data consistency
- No load balancer needed

*Disadvantages:*
- Expensive (exponential cost growth)
- Physical limits (max CPU/RAM)
- Single point of failure
- Requires downtime for upgrade

*Use cases:*
- Databases (RDBMS where distributed writes are complex)
- Legacy applications (can't be easily distributed)
- Single-threaded workloads
- Quick fixes

```yaml
# Vertical scaling PostgreSQL
Initial: m5.large (2 vCPU, 8GB RAM)
Scale:   m5.4xlarge (16 vCPU, 64GB RAM)
# No application changes, ACID guarantees maintained
```

**Horizontal Scaling (Scaling Out):**

*Theory:* Adding more servers to resource pool. More complex approach, requires stateless design and distributed logic, but provides virtually unlimited scaling and high availability.

*Examples:*
- Add web servers behind load balancer
- Add read replicas for DB
- Increase number of application instances

*Advantages:*
- Virtually unlimited scaling
- Cheaper (linear cost growth)
- No single point of failure
- Zero downtime possible
- High availability

*Disadvantages:*
- Complexity (distributed logic)
- Network latency
- Complex data consistency
- Requires load balancer
- Stateless design mandatory

*Use cases:*
- Web servers (stateless HTTP servers)
- API services (RESTful APIs)
- Microservices
- Read-heavy workloads
- Global distribution

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
| Cost | Expensive (exponential) | Cheaper (linear) |
| Complexity | Simple | Complex |
| Limits | Physical limits | Virtually none |
| Downtime | Usually required | Zero downtime possible |
| SPOF | Yes | No |
| Consistency | Easy | Challenging |

**Hybrid Approach (most common):**

*Theory:* Most production systems use both approaches. Web servers scale horizontally (stateless, easy to add), databases scale vertically (primary) + horizontally (read replicas).

```kotlin
// Typical architecture
// Load Balancer → Web Servers (horizontal, 3-50 instances)
//              → Redis Cache (horizontal cluster)
//              → Primary DB (vertical, large instance)
//              → Read Replicas (horizontal, 2-5 instances)
```

**Key Principles for Horizontal Scaling:**

1. **Stateless design** - state in Redis/DB, not in server memory
2. **Load balancing** - even traffic distribution
3. **Shared storage** - S3/NFS for files, not local disk
4. **Database separation** - separate tier for data
5. **Idempotency** - operations can be safely repeated

---

## Follow-ups

- How do you handle session state in horizontally scaled applications?
- What is the difference between stateless and stateful services?
- How do you implement auto-scaling for horizontal scaling?

## Related Questions

### Prerequisites (Easier)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing
- [[q-caching-strategies--system-design--medium]] - Caching strategies

### Related (Same Level)
- [[q-design-url-shortener--system-design--medium]] - System design example
- [[q-rest-api-design-best-practices--system-design--medium]] - API design

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Database sharding
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
