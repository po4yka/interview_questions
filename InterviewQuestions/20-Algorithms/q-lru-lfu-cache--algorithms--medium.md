---
id: q-lru-lfu-cache
title: LRU and LFU Cache Implementation / Реализация LRU и LFU кэшей
aliases:
- LRU Cache
- LFU Cache
- Least Recently Used
- Least Frequently Used
- Кэш LRU
- Кэш LFU
topic: algorithms
subtopics:
- data-structures
- caching
- design
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-hash-table
- c-linked-list
- q-hash-table-applications--algorithms--easy
- q-linked-list-algorithms--algorithms--medium
created: 2026-01-26
updated: 2026-01-26
tags:
- algorithms
- caching
- difficulty/medium
- design
- data-structures
sources:
- https://leetcode.com/problems/lru-cache/
- https://leetcode.com/problems/lfu-cache/
anki_cards:
- slug: q-lru-lfu-cache-0-en
  language: en
  anki_id: 1769404212970
  synced_at: '2026-01-26T09:10:14.514381'
- slug: q-lru-lfu-cache-0-ru
  language: ru
  anki_id: 1769404212990
  synced_at: '2026-01-26T09:10:14.516086'
---
# Вопрос (RU)
> Как реализовать LRU и LFU кэши с операциями O(1)?

# Question (EN)
> How do you implement LRU and LFU caches with O(1) operations?

---

## Ответ (RU)

### LRU Cache (Least Recently Used)

**Принцип:** вытесняем элемент, который дольше всех не использовался.

**Структура данных:** HashMap + Двусвязный список
- HashMap: ключ -> узел списка (O(1) доступ)
- Двусвязный список: порядок использования (O(1) перемещение)

```kotlin
class LRUCache(private val capacity: Int) {
    // Узел двусвязного списка
    private class Node(
        val key: Int,
        var value: Int,
        var prev: Node? = null,
        var next: Node? = null
    )

    private val cache = HashMap<Int, Node>()

    // Фиктивные узлы для упрощения операций
    private val head = Node(0, 0)  // Самый новый
    private val tail = Node(0, 0)  // Самый старый

    init {
        head.next = tail
        tail.prev = head
    }

    fun get(key: Int): Int {
        val node = cache[key] ?: return -1

        // Перемещаем в начало (самый недавний)
        removeNode(node)
        addToHead(node)

        return node.value
    }

    fun put(key: Int, value: Int) {
        if (key in cache) {
            // Обновляем существующий
            val node = cache[key]!!
            node.value = value
            removeNode(node)
            addToHead(node)
        } else {
            // Добавляем новый
            val newNode = Node(key, value)
            cache[key] = newNode
            addToHead(newNode)

            // Вытесняем, если превышена емкость
            if (cache.size > capacity) {
                val lru = tail.prev!!
                removeNode(lru)
                cache.remove(lru.key)
            }
        }
    }

    private fun addToHead(node: Node) {
        node.prev = head
        node.next = head.next
        head.next?.prev = node
        head.next = node
    }

    private fun removeNode(node: Node) {
        node.prev?.next = node.next
        node.next?.prev = node.prev
    }
}
```

**Визуализация:**
```
Операции: put(1,A), put(2,B), put(3,C), get(1), put(4,D)
Емкость: 3

put(1,A): head <-> [1:A] <-> tail
put(2,B): head <-> [2:B] <-> [1:A] <-> tail
put(3,C): head <-> [3:C] <-> [2:B] <-> [1:A] <-> tail
get(1):   head <-> [1:A] <-> [3:C] <-> [2:B] <-> tail  (1 перемещен в начало)
put(4,D): head <-> [4:D] <-> [1:A] <-> [3:C] <-> tail  (2 вытеснен)
```

### LFU Cache (Least Frequently Used)

**Принцип:** вытесняем элемент с наименьшей частотой использования. При равной частоте - вытесняем самый старый (LRU среди равных).

**Структура данных:** 3 HashMap
1. `keyToValue`: ключ -> значение
2. `keyToFreq`: ключ -> частота
3. `freqToKeys`: частота -> LinkedHashSet ключей (сохраняет порядок вставки)

```kotlin
class LFUCache(private val capacity: Int) {
    private val keyToValue = HashMap<Int, Int>()
    private val keyToFreq = HashMap<Int, Int>()

    // LinkedHashSet сохраняет порядок вставки (для LRU среди равных частот)
    private val freqToKeys = HashMap<Int, LinkedHashSet<Int>>()

    private var minFreq = 0

    fun get(key: Int): Int {
        if (key !in keyToValue) return -1

        updateFrequency(key)
        return keyToValue[key]!!
    }

    fun put(key: Int, value: Int) {
        if (capacity <= 0) return

        if (key in keyToValue) {
            // Обновляем существующий
            keyToValue[key] = value
            updateFrequency(key)
        } else {
            // Вытесняем, если нужно
            if (keyToValue.size >= capacity) {
                evictLFU()
            }

            // Добавляем новый с частотой 1
            keyToValue[key] = value
            keyToFreq[key] = 1
            freqToKeys.getOrPut(1) { LinkedHashSet() }.add(key)
            minFreq = 1
        }
    }

    private fun updateFrequency(key: Int) {
        val freq = keyToFreq[key]!!

        // Удаляем из старой группы частот
        freqToKeys[freq]!!.remove(key)

        // Обновляем minFreq, если группа опустела
        if (freqToKeys[freq]!!.isEmpty()) {
            freqToKeys.remove(freq)
            if (minFreq == freq) {
                minFreq++
            }
        }

        // Добавляем в новую группу частот
        val newFreq = freq + 1
        keyToFreq[key] = newFreq
        freqToKeys.getOrPut(newFreq) { LinkedHashSet() }.add(key)
    }

    private fun evictLFU() {
        val keys = freqToKeys[minFreq]!!

        // Первый элемент - самый старый (LRU среди LFU)
        val evictKey = keys.iterator().next()

        keys.remove(evictKey)
        if (keys.isEmpty()) {
            freqToKeys.remove(minFreq)
        }

        keyToValue.remove(evictKey)
        keyToFreq.remove(evictKey)
    }
}
```

**Визуализация:**
```
Операции: put(1,A), put(2,B), get(1), put(3,C), get(1), put(4,D)
Емкость: 3

put(1,A): val={1:A}, freq={1:1}, groups={1:[1]}, minFreq=1
put(2,B): val={1:A,2:B}, freq={1:1,2:1}, groups={1:[1,2]}, minFreq=1
get(1):   val={1:A,2:B}, freq={1:2,2:1}, groups={1:[2],2:[1]}, minFreq=1
put(3,C): val={1:A,2:B,3:C}, freq={1:2,2:1,3:1}, groups={1:[2,3],2:[1]}, minFreq=1
get(1):   freq={1:3,2:1,3:1}, groups={1:[2,3],3:[1]}, minFreq=1
put(4,D): вытесняем 2 (minFreq=1, первый в группе)
          val={1:A,3:C,4:D}, freq={1:3,3:1,4:1}, groups={1:[3,4],3:[1]}, minFreq=1
```

### Сравнение LRU vs LFU

| Критерий | LRU | LFU |
|----------|-----|-----|
| Принцип | Давность использования | Частота использования |
| Сложность реализации | Проще | Сложнее |
| Память | O(n) | O(n) + доп. структуры |
| Когда лучше | Временная локальность | Частотная локальность |
| Проблема | Сканирование удаляет полезные данные | "Загрязнение" старыми частыми элементами |

### Когда использовать

**LRU:**
- Веб-кэш браузера
- Кэш страниц памяти (Linux page cache)
- CDN кэширование
- Случаи с временной локальностью

**LFU:**
- DNS кэш
- Кэш часто запрашиваемых данных
- Когда "горячие" данные стабильны
- Случаи с частотной локальностью

### Потокобезопасность

```kotlin
class ThreadSafeLRUCache<K, V>(private val capacity: Int) {
    private val cache = Collections.synchronizedMap(
        object : LinkedHashMap<K, V>(capacity, 0.75f, true) {
            override fun removeEldestEntry(eldest: Map.Entry<K, V>): Boolean {
                return size > capacity
            }
        }
    )

    fun get(key: K): V? = cache[key]
    fun put(key: K, value: V) { cache[key] = value }
}
```

**Для высоконагруженных систем:**
- Сегментированные блокировки (ConcurrentHashMap)
- Read-write locks для частого чтения
- Lock-free структуры (CAS операции)

## Answer (EN)

### LRU Cache (Least Recently Used)

**Principle:** evict the element that has not been used for the longest time.

**Data Structure:** HashMap + Doubly Linked List
- HashMap: key -> list node (O(1) access)
- Doubly Linked List: usage order (O(1) move operations)

```kotlin
class LRUCache(private val capacity: Int) {
    // Doubly linked list node
    private class Node(
        val key: Int,
        var value: Int,
        var prev: Node? = null,
        var next: Node? = null
    )

    private val cache = HashMap<Int, Node>()

    // Dummy nodes simplify edge cases
    private val head = Node(0, 0)  // Most recent
    private val tail = Node(0, 0)  // Least recent

    init {
        head.next = tail
        tail.prev = head
    }

    fun get(key: Int): Int {
        val node = cache[key] ?: return -1

        // Move to head (most recently used)
        removeNode(node)
        addToHead(node)

        return node.value
    }

    fun put(key: Int, value: Int) {
        if (key in cache) {
            // Update existing
            val node = cache[key]!!
            node.value = value
            removeNode(node)
            addToHead(node)
        } else {
            // Add new
            val newNode = Node(key, value)
            cache[key] = newNode
            addToHead(newNode)

            // Evict if over capacity
            if (cache.size > capacity) {
                val lru = tail.prev!!
                removeNode(lru)
                cache.remove(lru.key)
            }
        }
    }

    private fun addToHead(node: Node) {
        node.prev = head
        node.next = head.next
        head.next?.prev = node
        head.next = node
    }

    private fun removeNode(node: Node) {
        node.prev?.next = node.next
        node.next?.prev = node.prev
    }
}
```

**Visualization:**
```
Operations: put(1,A), put(2,B), put(3,C), get(1), put(4,D)
Capacity: 3

put(1,A): head <-> [1:A] <-> tail
put(2,B): head <-> [2:B] <-> [1:A] <-> tail
put(3,C): head <-> [3:C] <-> [2:B] <-> [1:A] <-> tail
get(1):   head <-> [1:A] <-> [3:C] <-> [2:B] <-> tail  (1 moved to front)
put(4,D): head <-> [4:D] <-> [1:A] <-> [3:C] <-> tail  (2 evicted)
```

### LFU Cache (Least Frequently Used)

**Principle:** evict the element with the lowest access frequency. On ties, evict the least recently used among the least frequent.

**Data Structure:** 3 HashMaps
1. `keyToValue`: key -> value
2. `keyToFreq`: key -> frequency
3. `freqToKeys`: frequency -> LinkedHashSet of keys (preserves insertion order)

```kotlin
class LFUCache(private val capacity: Int) {
    private val keyToValue = HashMap<Int, Int>()
    private val keyToFreq = HashMap<Int, Int>()

    // LinkedHashSet preserves insertion order (for LRU among equal frequencies)
    private val freqToKeys = HashMap<Int, LinkedHashSet<Int>>()

    private var minFreq = 0

    fun get(key: Int): Int {
        if (key !in keyToValue) return -1

        updateFrequency(key)
        return keyToValue[key]!!
    }

    fun put(key: Int, value: Int) {
        if (capacity <= 0) return

        if (key in keyToValue) {
            // Update existing
            keyToValue[key] = value
            updateFrequency(key)
        } else {
            // Evict if needed
            if (keyToValue.size >= capacity) {
                evictLFU()
            }

            // Add new with frequency 1
            keyToValue[key] = value
            keyToFreq[key] = 1
            freqToKeys.getOrPut(1) { LinkedHashSet() }.add(key)
            minFreq = 1
        }
    }

    private fun updateFrequency(key: Int) {
        val freq = keyToFreq[key]!!

        // Remove from old frequency group
        freqToKeys[freq]!!.remove(key)

        // Update minFreq if group became empty
        if (freqToKeys[freq]!!.isEmpty()) {
            freqToKeys.remove(freq)
            if (minFreq == freq) {
                minFreq++
            }
        }

        // Add to new frequency group
        val newFreq = freq + 1
        keyToFreq[key] = newFreq
        freqToKeys.getOrPut(newFreq) { LinkedHashSet() }.add(key)
    }

    private fun evictLFU() {
        val keys = freqToKeys[minFreq]!!

        // First element is the oldest (LRU among LFU)
        val evictKey = keys.iterator().next()

        keys.remove(evictKey)
        if (keys.isEmpty()) {
            freqToKeys.remove(minFreq)
        }

        keyToValue.remove(evictKey)
        keyToFreq.remove(evictKey)
    }
}
```

**Visualization:**
```
Operations: put(1,A), put(2,B), get(1), put(3,C), get(1), put(4,D)
Capacity: 3

put(1,A): val={1:A}, freq={1:1}, groups={1:[1]}, minFreq=1
put(2,B): val={1:A,2:B}, freq={1:1,2:1}, groups={1:[1,2]}, minFreq=1
get(1):   val={1:A,2:B}, freq={1:2,2:1}, groups={1:[2],2:[1]}, minFreq=1
put(3,C): val={1:A,2:B,3:C}, freq={1:2,2:1,3:1}, groups={1:[2,3],2:[1]}, minFreq=1
get(1):   freq={1:3,2:1,3:1}, groups={1:[2,3],3:[1]}, minFreq=1
put(4,D): evict 2 (minFreq=1, first in group)
          val={1:A,3:C,4:D}, freq={1:3,3:1,4:1}, groups={1:[3,4],3:[1]}, minFreq=1
```

### LRU vs LFU Comparison

| Criterion | LRU | LFU |
|-----------|-----|-----|
| Principle | Recency of access | Frequency of access |
| Implementation complexity | Simpler | More complex |
| Memory | O(n) | O(n) + extra structures |
| Best when | Temporal locality | Frequency-based locality |
| Weakness | Scanning evicts useful data | "Pollution" by old frequent items |

### When to Use

**LRU:**
- Web browser cache
- Memory page cache (Linux page cache)
- CDN caching
- Workloads with temporal locality

**LFU:**
- DNS cache
- Frequently accessed data cache
- When "hot" data is stable
- Workloads with frequency-based locality

### Thread-Safety Considerations

```kotlin
class ThreadSafeLRUCache<K, V>(private val capacity: Int) {
    private val cache = Collections.synchronizedMap(
        object : LinkedHashMap<K, V>(capacity, 0.75f, true) {
            override fun removeEldestEntry(eldest: Map.Entry<K, V>): Boolean {
                return size > capacity
            }
        }
    )

    fun get(key: K): V? = cache[key]
    fun put(key: K, value: V) { cache[key] = value }
}
```

**For high-throughput systems:**
- Segmented locking (ConcurrentHashMap approach)
- Read-write locks for read-heavy workloads
- Lock-free structures (CAS operations)

---

## Follow-ups

- What happens if we access the same key multiple times in LFU?
- How would you implement a TTL-based cache?
- What is ARC (Adaptive Replacement Cache) and how does it combine LRU/LFU?

## Related Questions

### Prerequisites (Easier)
- [[q-hash-table-applications--algorithms--easy]] - Hash table fundamentals
- [[q-linked-list-algorithms--algorithms--medium]] - Linked list operations

### Related (Same Level)
- [[q-heap-priority-queue--algorithms--medium]] - Priority-based data structures
- [[q-data-structures-overview--algorithms--easy]] - Data structures comparison

### Advanced (Harder)
- System Design: Distributed caching (Redis, Memcached)
- Concurrency patterns for high-performance caches
