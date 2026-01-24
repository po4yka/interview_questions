---
id: sysdes-013
title: Consistency Models in Distributed Systems
aliases:
- Strong Consistency
- Eventual Consistency
- Causal Consistency
topic: system-design
subtopics:
- distributed-systems
- consistency
- replication
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-cap-theorem-distributed-systems--system-design--hard
- q-base-properties--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- consistency
- system-design
anki_cards:
- slug: sysdes-013-0-en
  language: en
  anki_id: 1769158890091
  synced_at: '2026-01-23T13:49:17.720124'
- slug: sysdes-013-0-ru
  language: ru
  anki_id: 1769158890116
  synced_at: '2026-01-23T13:49:17.721806'
---
# Question (EN)
> What are the main consistency models in distributed systems? Explain strong, eventual, and causal consistency with examples.

# Vopros (RU)
> Какие основные модели согласованности существуют в распределенных системах? Объясните строгую, eventual и причинную согласованность с примерами.

---

## Answer (EN)

Consistency models define guarantees about when updates become visible to readers in distributed systems.

### Consistency Spectrum

```
Strongest ←───────────────────────────────→ Weakest

Linearizable → Sequential → Causal → Eventual
     ↑              ↑           ↑          ↑
 Single copy    Global order  Cause-effect  Eventually same
```

### Strong (Linearizable) Consistency

**Definition**: All operations appear to execute atomically in some global order. Every read returns the most recent write.

**Characteristics:**
- Acts like single-copy system
- Total ordering of all operations
- Highest latency, lowest availability

**Example:**
```
Time →
Client A: Write(x=1) ────────────────────────→ ACK
Client B:           Read(x) ─────────────────→ Returns 1 (guaranteed)
```

**Use cases:** Bank balances, inventory counts, leader election

### Eventual Consistency

**Definition**: Given enough time without updates, all replicas converge to the same value.

**Characteristics:**
- No ordering guarantees during propagation
- Reads may return stale data
- Highest availability, lowest latency

**Example:**
```
Time →
Client A: Write(x=1) to Replica1 ────→ ACK
Client B: Read(x) from Replica2 ─────→ Returns old value (temporarily)
          ... time passes, replication completes ...
Client B: Read(x) from Replica2 ─────→ Returns 1
```

**Use cases:** DNS, social media feeds, shopping carts

### Causal Consistency

**Definition**: Operations that are causally related are seen in the same order by all nodes. Concurrent operations may be seen in different orders.

**Characteristics:**
- Preserves cause-and-effect relationships
- If A causes B, everyone sees A before B
- Middle ground between strong and eventual

**Example:**
```
Client A: Post("Hello")         ─────→ ID=1
Client A: Reply(to=1, "World")  ─────→ ID=2

All clients see: Post appears before Reply (causal order preserved)
But: Unrelated posts from Client B may appear in different order
```

**Use cases:** Comment threads, chat messages, collaborative editing

### Comparison Table

| Model | Latency | Availability | Consistency | Complexity |
|-------|---------|--------------|-------------|------------|
| Strong | High | Lower | Perfect | High |
| Causal | Medium | Medium | Cause-effect | Medium |
| Eventual | Low | Highest | Eventually | Lower |

### Implementation Approaches

**Strong consistency:** Consensus protocols (Paxos, Raft), synchronous replication

**Causal consistency:** Vector clocks, version vectors, logical timestamps

**Eventual consistency:** Async replication, conflict resolution (LWW, CRDTs)

---

## Otvet (RU)

Модели согласованности определяют гарантии о том, когда обновления становятся видимы читателям в распределенных системах.

### Спектр согласованности

```
Строже ←───────────────────────────────→ Слабее

Linearizable → Sequential → Causal → Eventual
     ↑              ↑           ↑          ↑
Одна копия    Глобальный    Причинно-   Со временем
                порядок     следственный  одинаково
```

### Строгая (Linearizable) согласованность

**Определение**: Все операции выглядят атомарными в некотором глобальном порядке. Каждое чтение возвращает последнюю запись.

**Характеристики:**
- Работает как система с одной копией
- Полное упорядочивание всех операций
- Наибольшая задержка, наименьшая доступность

**Пример:**
```
Время →
Клиент A: Write(x=1) ────────────────────────→ ACK
Клиент B:           Read(x) ─────────────────→ Возвращает 1 (гарантировано)
```

**Применение:** Банковские балансы, учет товаров, выбор лидера

### Eventual согласованность

**Определение**: При достаточном времени без обновлений все реплики сходятся к одному значению.

**Характеристики:**
- Нет гарантий порядка во время распространения
- Чтение может вернуть устаревшие данные
- Наибольшая доступность, наименьшая задержка

**Пример:**
```
Время →
Клиент A: Write(x=1) в Replica1 ────→ ACK
Клиент B: Read(x) из Replica2 ──────→ Возвращает старое значение (временно)
          ... время проходит, репликация завершается ...
Клиент B: Read(x) из Replica2 ──────→ Возвращает 1
```

**Применение:** DNS, ленты соцсетей, корзины покупок

### Причинная (Causal) согласованность

**Определение**: Операции, связанные причинно-следственной связью, видны всем узлам в одном порядке. Параллельные операции могут быть видны в разном порядке.

**Характеристики:**
- Сохраняет причинно-следственные связи
- Если A вызывает B, все видят A до B
- Золотая середина между строгой и eventual

**Пример:**
```
Клиент A: Post("Hello")         ─────→ ID=1
Клиент A: Reply(to=1, "World")  ─────→ ID=2

Все клиенты видят: Пост появляется до ответа (причинный порядок сохранен)
Но: Несвязанные посты от Клиента B могут появиться в другом порядке
```

**Применение:** Треды комментариев, сообщения чата, совместное редактирование

### Сравнительная таблица

| Модель | Задержка | Доступность | Согласованность | Сложность |
|--------|----------|-------------|-----------------|-----------|
| Строгая | Высокая | Ниже | Идеальная | Высокая |
| Причинная | Средняя | Средняя | Причинно-следственная | Средняя |
| Eventual | Низкая | Наивысшая | Со временем | Ниже |

### Подходы к реализации

**Строгая согласованность:** Протоколы консенсуса (Paxos, Raft), синхронная репликация

**Причинная согласованность:** Векторные часы, векторы версий, логические метки времени

**Eventual согласованность:** Асинхронная репликация, разрешение конфликтов (LWW, CRDT)

---

## Follow-ups

- How do vector clocks help implement causal consistency?
- What is the difference between linearizability and serializability?
- How does Google Spanner achieve strong consistency globally?

## Related Questions

### Prerequisites (Easier)
- [[q-acid-properties--system-design--medium]] - ACID properties
- [[q-base-properties--system-design--medium]] - BASE properties

### Related (Same Level)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem
- [[q-replication-strategies--system-design--medium]] - Replication

### Advanced (Harder)
- [[q-consensus-algorithms--system-design--hard]] - Raft/Paxos
