---
id: sysdes-012
title: BASE Properties in Distributed Systems
aliases:
- BASE
- Eventual Consistency
topic: system-design
subtopics:
- distributed-systems
- consistency
- nosql
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-acid-properties--system-design--medium
- q-cap-theorem-distributed-systems--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/medium
- consistency
- system-design
anki_cards:
- slug: sysdes-012-0-en
  language: en
  anki_id: 1769158890341
  synced_at: '2026-01-23T13:49:17.731333'
- slug: sysdes-012-0-ru
  language: ru
  anki_id: 1769158890366
  synced_at: '2026-01-23T13:49:17.732686'
---
# Question (EN)
> What are BASE properties? How do they differ from ACID, and when should you choose BASE over ACID?

# Vopros (RU)
> Что такое свойства BASE? Чем они отличаются от ACID, и когда следует выбирать BASE вместо ACID?

---

## Answer (EN)

**BASE** is an alternative to ACID for distributed systems that prioritizes availability and partition tolerance over strict consistency.

### BASE Properties

**B**asically **A**vailable
- System guarantees availability (responds to requests)
- May return stale data rather than failing
- Partial failures don't bring down entire system

**S**oft state
- System state may change over time even without input
- Data can be in flux as it propagates across nodes
- No guarantee all nodes have same data at any moment

**E**ventually consistent
- Given enough time without updates, all replicas converge
- Reads may return outdated values temporarily
- System prioritizes availability over immediate consistency

### ACID vs BASE Comparison

| Aspect | ACID | BASE |
|--------|------|------|
| Consistency | Immediate, strong | Eventual |
| Availability | May sacrifice for consistency | Prioritized |
| Complexity | Simpler mental model | More complex |
| Scalability | Harder to scale | Easier to scale horizontally |
| Use case | Financial, critical data | Social media, analytics |

### When to Choose BASE

**Choose BASE when:**
- High availability is critical
- System needs horizontal scaling
- Brief inconsistency is acceptable
- Read-heavy workloads

**Examples:**
- Social media feeds (seeing post 1s late is OK)
- Shopping cart (can merge conflicts)
- DNS (propagation delay acceptable)
- Session stores

### Eventual Consistency Patterns

```
Write to Primary → Async Replication → Replicas Converge

Timeline:
T0: Write "A" to primary
T1: Read from replica returns old value
T2: Replication completes
T3: Read from replica returns "A"
```

---

## Otvet (RU)

**BASE** - альтернатива ACID для распределенных систем, которая приоритизирует доступность и устойчивость к разделению над строгой согласованностью.

### Свойства BASE

**B**asically **A**vailable (Базовая доступность)
- Система гарантирует доступность (отвечает на запросы)
- Может вернуть устаревшие данные вместо ошибки
- Частичные сбои не ломают всю систему

**S**oft state (Мягкое состояние)
- Состояние системы может меняться со временем без входных данных
- Данные могут быть в процессе распространения между узлами
- Нет гарантии, что все узлы имеют одинаковые данные в любой момент

**E**ventually consistent (Согласованность в конечном счете)
- При отсутствии обновлений все реплики со временем сходятся
- Чтение может временно возвращать устаревшие значения
- Система приоритизирует доступность над немедленной согласованностью

### Сравнение ACID и BASE

| Аспект | ACID | BASE |
|--------|------|------|
| Согласованность | Немедленная, строгая | Eventual |
| Доступность | Может жертвовать ради согласованности | Приоритет |
| Сложность | Проще ментальная модель | Сложнее |
| Масштабируемость | Сложнее масштабировать | Легче горизонтально |
| Применение | Финансы, критичные данные | Соцсети, аналитика |

### Когда выбирать BASE

**Выбирайте BASE когда:**
- Критична высокая доступность
- Нужно горизонтальное масштабирование
- Кратковременная несогласованность допустима
- Преобладают операции чтения

**Примеры:**
- Ленты соцсетей (увидеть пост на 1с позже - ОК)
- Корзина покупок (можно мержить конфликты)
- DNS (задержка распространения допустима)
- Хранилища сессий

### Паттерны Eventual Consistency

```
Запись в Primary → Асинхронная репликация → Реплики сходятся

Временная шкала:
T0: Запись "A" в primary
T1: Чтение с реплики возвращает старое значение
T2: Репликация завершена
T3: Чтение с реплики возвращает "A"
```

---

## Follow-ups

- How do you handle conflicts in eventually consistent systems?
- What is the difference between strong and eventual consistency?
- How does CRDTs help with eventual consistency?

## Related Questions

### Prerequisites (Easier)
- [[q-acid-properties--system-design--medium]] - ACID properties

### Related (Same Level)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem
- [[q-replication-strategies--system-design--medium]] - Replication

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding patterns
