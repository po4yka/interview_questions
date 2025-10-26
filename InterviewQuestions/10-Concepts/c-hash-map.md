---
id: "20251018-140001"
title: "Hash Map / Хеш-таблица"
aliases: ["Hash Map", "HashMap", "Hash Table", "Хеш-таблица", "Хеш-карта", "Associative Array", "Dictionary"]
summary: "Data structure providing O(1) average-case lookup, insert, and delete operations using hash functions"
topic: "data-structures"
subtopics: ["hash-map", "algorithms", "collections"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-algorithms"
related: []
created: "2025-10-18"
updated: "2025-10-18"
tags: ["concept", "data-structures", "hash-map", "algorithms", "collections"]
---

# Summary (EN)

A **hash map** (also called hash table, dictionary, or associative array) is a data structure that stores key-value pairs and provides extremely fast lookup, insertion, and deletion operations. It uses a hash function to compute an index into an array of buckets, from which the desired value can be found. Hash maps offer O(1) average-case time complexity for basic operations, making them one of the most widely used data structures in programming.

# Краткое описание (RU)

**Хеш-таблица** (также называется hash map, словарь или ассоциативный массив) - это структура данных, которая хранит пары ключ-значение и обеспечивает очень быструю операцию поиска, вставки и удаления. Она использует хеш-функцию для вычисления индекса в массиве корзин (buckets), из которого можно найти нужное значение. Хеш-таблицы обеспечивают среднюю временную сложность O(1) для базовых операций, что делает их одной из наиболее используемых структур данных в программировании.

---

## How It Works

### Core Components

1. **Hash Function**: A function that takes a key and produces an integer hash code
2. **Buckets Array**: An array that stores the key-value pairs
3. **Collision Resolution**: A strategy for handling multiple keys that hash to the same index

### Step-by-Step Process

1. **Insertion**: `map.put(key, value)`
   - Compute hash code: `hash = hashFunction(key)`
   - Calculate bucket index: `index = hash % arraySize`
   - Store the key-value pair at that index (handling collisions if needed)

2. **Lookup**: `map.get(key)`
   - Compute hash code: `hash = hashFunction(key)`
   - Calculate bucket index: `index = hash % arraySize`
   - Search the bucket for the key and return its value

3. **Deletion**: `map.remove(key)`
   - Find the key using the same hash and index calculation
   - Remove the key-value pair from the bucket

### Hash Function Properties

A good hash function should:
- Be deterministic (same key always produces same hash)
- Distribute keys uniformly across buckets
- Be fast to compute
- Minimize collisions

```kotlin
// Example: Simple hash function for strings
fun simpleHash(key: String, arraySize: Int): Int {
    var hash = 0
    for (char in key) {
        hash = (hash * 31 + char.code) % arraySize
    }
    return hash
}
```

---

## Collision Resolution

When two different keys hash to the same index, a **collision** occurs. Two main strategies:

### 1. Chaining (Separate Chaining)

Each bucket contains a linked list (or other data structure) of all key-value pairs that hash to that index.

```kotlin
// Simplified chaining implementation
class HashMapChaining<K, V> {
    private data class Entry<K, V>(val key: K, var value: V)
    private val buckets: Array<MutableList<Entry<K, V>>> = Array(16) { mutableListOf() }

    fun put(key: K, value: V) {
        val index = key.hashCode() % buckets.size
        val bucket = buckets[index]

        // Update existing key or add new entry
        val existing = bucket.find { it.key == key }
        if (existing != null) {
            existing.value = value
        } else {
            bucket.add(Entry(key, value))
        }
    }

    fun get(key: K): V? {
        val index = key.hashCode() % buckets.size
        return buckets[index].find { it.key == key }?.value
    }
}
```

**Pros**: Simple, never runs out of space
**Cons**: Requires extra memory for linked list pointers

### 2. Open Addressing (Linear Probing, Quadratic Probing)

All entries are stored in the buckets array itself. When a collision occurs, probe for the next available slot.

```kotlin
// Simplified linear probing implementation
class HashMapOpenAddressing<K, V>(private val capacity: Int = 16) {
    private data class Entry<K, V>(val key: K, var value: V, var isDeleted: Boolean = false)
    private val buckets: Array<Entry<K, V>?> = arrayOfNulls(capacity)

    fun put(key: K, value: V) {
        var index = key.hashCode() % capacity

        // Linear probing: find next available slot
        while (buckets[index] != null &&
               buckets[index]?.key != key &&
               !buckets[index]!!.isDeleted) {
            index = (index + 1) % capacity
        }

        buckets[index] = Entry(key, value)
    }

    fun get(key: K): V? {
        var index = key.hashCode() % capacity

        while (buckets[index] != null) {
            val entry = buckets[index]!!
            if (entry.key == key && !entry.isDeleted) {
                return entry.value
            }
            index = (index + 1) % capacity
        }
        return null
    }
}
```

**Pros**: Better cache locality, no extra pointer overhead
**Cons**: Can suffer from clustering, requires careful deletion handling

---

## Time Complexity

| Operation | Average Case | Worst Case |
|-----------|--------------|------------|
| Insertion | O(1)         | O(n)       |
| Lookup    | O(1)         | O(n)       |
| Deletion  | O(1)         | O(n)       |
| Space     | O(n)         | O(n)       |

**Average Case**: When hash function distributes keys uniformly
**Worst Case**: When all keys hash to the same bucket (degrades to linked list)

### Load Factor and Resizing

**Load Factor** = Number of entries / Number of buckets

- Typical threshold: 0.75 (75% full)
- When exceeded, the hash map typically doubles in size and rehashes all entries
- Resizing ensures average-case O(1) performance is maintained

```kotlin
fun resize() {
    val oldBuckets = buckets
    buckets = Array(oldBuckets.size * 2) { mutableListOf() }

    for (bucket in oldBuckets) {
        for (entry in bucket) {
            put(entry.key, entry.value) // Rehash
        }
    }
}
```

---

## Use Cases

### When to Use Hash Maps

1. **Fast Lookup**: Need to quickly find values by key (e.g., caching, indexes)
2. **Counting/Frequency**: Count occurrences of elements
3. **Deduplication**: Remove duplicates or check for uniqueness
4. **Grouping**: Group items by category or property
5. **Two-way Mapping**: Map between two sets of values

### Common Patterns

**Pattern 1: Counting Frequencies**
```kotlin
fun countWords(words: List<String>): Map<String, Int> {
    val frequency = mutableMapOf<String, Int>()
    for (word in words) {
        frequency[word] = frequency.getOrDefault(word, 0) + 1
    }
    return frequency
}
```

**Pattern 2: Two Sum Problem**
```kotlin
fun twoSum(nums: IntArray, target: Int): IntArray {
    val map = mutableMapOf<Int, Int>() // value -> index
    for (i in nums.indices) {
        val complement = target - nums[i]
        if (complement in map) {
            return intArrayOf(map[complement]!!, i)
        }
        map[nums[i]] = i
    }
    return intArrayOf()
}
```

**Pattern 3: Group Anagrams**
```kotlin
fun groupAnagrams(words: List<String>): List<List<String>> {
    val groups = mutableMapOf<String, MutableList<String>>()
    for (word in words) {
        val key = word.toCharArray().sorted().joinToString("")
        groups.getOrPut(key) { mutableListOf() }.add(word)
    }
    return groups.values.toList()
}
```

---

## Trade-offs

### Advantages

- **Very Fast**: O(1) average-case operations
- **Flexible**: Works with any hashable key type
- **Dynamic**: Can grow as needed
- **Versatile**: Solves many common problems efficiently

### Disadvantages

- **Memory Overhead**: Requires extra space for buckets and collision handling
- **No Ordering**: Elements are not stored in any particular order (use LinkedHashMap or TreeMap for ordering)
- **Hash Function Dependency**: Performance depends on quality of hash function
- **Worst-Case Performance**: Can degrade to O(n) with poor hash function or many collisions
- **Not Cache-Friendly**: Chaining involves pointer chasing

### Hash Map vs Other Data Structures

| Structure | Lookup | Insert | Delete | Ordered | Use Case |
|-----------|--------|--------|--------|---------|----------|
| Hash Map  | O(1)   | O(1)   | O(1)   | No      | Fast key-value lookup |
| TreeMap   | O(log n) | O(log n) | O(log n) | Yes   | Sorted key-value pairs |
| Array     | O(n)   | O(n)   | O(n)   | By index | Sequential access |
| Linked List | O(n) | O(1)   | O(1)   | No      | Frequent insertions/deletions |

---

## Implementation in Different Languages

### Kotlin
```kotlin
// Standard library
val map = hashMapOf<String, Int>()
map["apple"] = 1
map["banana"] = 2
println(map["apple"]) // 1

// Mutable vs Immutable
val mutableMap = mutableMapOf("a" to 1)
val immutableMap = mapOf("a" to 1)
```

### Java
```java
// java.util.HashMap
Map<String, Integer> map = new HashMap<>();
map.put("apple", 1);
map.put("banana", 2);
System.out.println(map.get("apple")); // 1

// Initial capacity and load factor
Map<String, Integer> map2 = new HashMap<>(16, 0.75f);
```

### Python
```python
# dict (built-in hash map)
map = {}
map["apple"] = 1
map["banana"] = 2
print(map["apple"])  # 1

# or
map = {"apple": 1, "banana": 2}
```

---

## Advanced Topics

### Concurrent Hash Maps

For multi-threaded environments:

```kotlin
// Java's ConcurrentHashMap
import java.util.concurrent.ConcurrentHashMap

val threadSafeMap = ConcurrentHashMap<String, Int>()
```

Features:
- Thread-safe without locking entire map
- Uses segment-level locking or lock-free techniques
- Allows concurrent reads and writes

### Custom Hash Functions

Implementing `hashCode()` and `equals()`:

```kotlin
data class Person(val name: String, val age: Int) {
    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false
        return name == other.name && age == other.age
    }
}

val map = hashMapOf<Person, String>()
map[Person("Alice", 30)] = "Engineer"
```

**Contract**: If `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` must also be true.

---

## Related Questions

### Algorithm Questions
- [[q-data-structures-overview--algorithms--easy]]
- [[q-binary-search-variants--algorithms--medium]]
- [[q-sorting-algorithms-comparison--algorithms--medium]]
- [[q-two-pointers-sliding-window--algorithms--medium]]

### Programming Questions
- [[q-hashmap-how-it-works--programming-languages--medium]]
- [[q-equals-hashcode-purpose--programming-languages--hard]]
- [[q-equals-hashcode-contracts--programming-languages--medium]]
- [[q-equals-hashcode-rules--programming-languages--medium]]
- [[q-kotlin-equals-hashcode-purpose--programming-languages--medium]]

### Kotlin-Specific
- [[q-equals-hashcode-purpose--kotlin--medium]]
- [[q-equals-hashcode-contracts--programming-languages--hard]]

---

## References

### Documentation
- [Java HashMap Documentation](https://docs.oracle.com/javase/8/docs/api/java/util/HashMap.html)
- [Kotlin Collections Overview](https://kotlinlang.org/docs/collections-overview.html)
- [Python dict Documentation](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)

### Books
- "Introduction to Algorithms" (CLRS) - Chapter 11: Hash Tables
- "Data Structures and Algorithm Analysis in Java" by Mark Allen Weiss

### Articles
- [Hash Table - Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
- [Understanding Hash Tables](https://www.cs.cornell.edu/courses/cs312/2008sp/lectures/lec20.html)

---

## Краткие примеры кода (RU)

### Базовое использование
```kotlin
// Создание и работа с HashMap
val phoneBook = hashMapOf<String, String>()
phoneBook["Алиса"] = "+7-900-123-45-67"
phoneBook["Боб"] = "+7-900-987-65-43"

// Поиск
println(phoneBook["Алиса"]) // +7-900-123-45-67

// Проверка наличия ключа
if ("Чарли" in phoneBook) {
    println(phoneBook["Чарли"])
} else {
    println("Чарли не найден")
}
```

### Подсчет частоты элементов
```kotlin
fun подсчетЧастоты(слова: List<String>): Map<String, Int> {
    val частота = mutableMapOf<String, Int>()
    for (слово in слова) {
        частота[слово] = частота.getOrDefault(слово, 0) + 1
    }
    return частота
}

val текст = listOf("кот", "пёс", "кот", "птица", "пёс", "кот")
println(подсчетЧастоты(текст)) // {кот=3, пёс=2, птица=1}
```

### Группировка данных
```kotlin
data class Студент(val имя: String, val факультет: String)

fun группироватьПоФакультету(студенты: List<Студент>): Map<String, List<Студент>> {
    val группы = mutableMapOf<String, MutableList<Студент>>()
    for (студент in студенты) {
        группы.getOrPut(студент.факультет) { mutableListOf() }.add(студент)
    }
    return группы
}
```
