---
id: sysdes-034
title: Consistent Hashing Deep Dive
aliases:
- Consistent Hashing
- Hash Ring
topic: system-design
subtopics:
- distributed-systems
- load-balancing
- partitioning
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-database-sharding-partitioning--system-design--hard
- q-load-balancing-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- partitioning
- system-design
anki_cards:
- slug: sysdes-034-0-en
  language: en
  anki_id: 1769159520696
  synced_at: '2026-01-23T13:49:17.756745'
- slug: sysdes-034-0-ru
  language: ru
  anki_id: 1769159520719
  synced_at: '2026-01-23T13:49:17.757851'
---
# Question (EN)
> How does consistent hashing work? Why is it preferred over simple modulo hashing for distributed systems?

# Vopros (RU)
> Как работает консистентное хеширование? Почему оно предпочтительнее простого modulo-хеширования для распределенных систем?

---

## Answer (EN)

**Consistent hashing** distributes data across nodes while minimizing redistribution when nodes are added or removed.

### Problem with Modulo Hashing

```
Simple: server = hash(key) % N

With 3 servers: hash("user1") % 3 = 1 → Server 1
Add server:    hash("user1") % 4 = 2 → Server 2 (remapped!)

Adding 1 server remaps ~75% of keys (N-1)/N
```

### Consistent Hashing Solution

```
1. Hash ring: 0 to 2^32-1 arranged in circle
2. Hash servers onto ring (by IP/name)
3. Hash keys onto ring
4. Key belongs to first server clockwise

        Server A
           ↑
    key1 → ●───────● ← Server B
           │       │
           │   ●   │
           │  key2 │
           ●───────●
              ↓
           Server C
```

### Adding/Removing Nodes

```
Add Server D between A and B:
- Only keys between A and D move to D
- Other keys unchanged

Remove Server B:
- Only B's keys move to next server (C)
- ~1/N keys affected (not all)
```

### Virtual Nodes

**Problem:** Uneven distribution with few physical nodes.

**Solution:** Each physical node gets multiple virtual nodes.

```
Server A → hash("A-1"), hash("A-2"), hash("A-3")...
Server B → hash("B-1"), hash("B-2"), hash("B-3")...

More points on ring = more even distribution
Typical: 100-200 virtual nodes per physical node
```

### Implementation

```python
class ConsistentHash:
    def __init__(self, nodes, replicas=100):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            self.add_node(node)

    def add_node(self, node):
        for i in range(self.replicas):
            key = hash(f"{node}-{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()

    def get_node(self, key):
        h = hash(key)
        # Find first node clockwise
        for ring_key in self.sorted_keys:
            if h <= ring_key:
                return self.ring[ring_key]
        return self.ring[self.sorted_keys[0]]  # Wrap around
```

### Use Cases

| System | Usage |
|--------|-------|
| Cassandra | Data partitioning |
| DynamoDB | Partition key distribution |
| Memcached | Cache server selection |
| CDN | Edge server selection |

---

## Otvet (RU)

**Консистентное хеширование** распределяет данные между узлами, минимизируя перераспределение при добавлении/удалении узлов.

### Проблема с Modulo-хешированием

```
Простой подход: server = hash(key) % N

С 3 серверами: hash("user1") % 3 = 1 → Сервер 1
Добавляем сервер: hash("user1") % 4 = 2 → Сервер 2 (перемещен!)

Добавление 1 сервера перемещает ~75% ключей (N-1)/N
```

### Решение: Консистентное хеширование

```
1. Хеш-кольцо: от 0 до 2^32-1 по кругу
2. Хешируем серверы на кольцо (по IP/имени)
3. Хешируем ключи на кольцо
4. Ключ принадлежит первому серверу по часовой стрелке
```

### Добавление/Удаление узлов

```
Добавление Сервера D между A и B:
- Только ключи между A и D переезжают на D
- Остальные ключи без изменений

Удаление Сервера B:
- Только ключи B переезжают на следующий сервер (C)
- Затрагивается ~1/N ключей (не все)
```

### Виртуальные узлы

**Проблема:** Неравномерное распределение при малом числе физических узлов.

**Решение:** Каждый физический узел получает несколько виртуальных.

```
Сервер A → hash("A-1"), hash("A-2"), hash("A-3")...
Сервер B → hash("B-1"), hash("B-2"), hash("B-3")...

Больше точек на кольце = более равномерное распределение
Типично: 100-200 виртуальных узлов на физический
```

### Применение

| Система | Использование |
|---------|---------------|
| Cassandra | Партиционирование данных |
| DynamoDB | Распределение partition key |
| Memcached | Выбор сервера кеша |
| CDN | Выбор edge-сервера |

---

## Follow-ups

- How do you handle hotspots in consistent hashing?
- What is jump consistent hashing?
- How does Cassandra use consistent hashing with vnodes?
