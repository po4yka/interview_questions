---
id: kotlin-100
title: "Kotlin Collections / Коллекции в Kotlin"
aliases: ["Kotlin Collections", "Коллекции в Kotlin"]

# Classification
topic: kotlin
subtopics:
  - collections
  - list
  - sequences
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Kotlin Collections

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-collections, q-expect-actual-kotlin--kotlin--medium, q-flow-basics--kotlin--easy, q-kotlin-val-vs-var--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [collections, difficulty/medium, filter, flatmap, kotlin, list, map, operators, sequences, set]
date created: Sunday, October 12th 2025, 3:02:56 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---

# Вопрос (RU)
> Что такое коллекции в Kotlin? Объясните `List`, `Set`, `Map`, их изменяемые варианты, операторы коллекций и разницу между Collections и Sequences.

---

# Question (EN)
> What are Kotlin collections? Explain `List`, `Set`, `Map`, their mutable variants, collection operators, and the difference between Collections and Sequences.

## Ответ (RU)

Kotlin предоставляет богатый набор типов коллекций и операций, которые делают манипуляцию данными элегантной и лаконичной. Коллекции в Kotlin разделены на **интерфейсы только для чтения** (read-only) и **изменяемые** варианты. Read-only коллекция не гарантирует глубокой неизменяемости данных — она лишь не предоставляет методов модификации через данный тип.

### Обзор Типов Коллекций

Упрощенная иерархия коллекций:

```
Iterable<T>
├── Collection<T>
│   ├── List<T>
│   └── Set<T>

// Map<K, V> — отдельная иерархия (НЕ наследует Iterable<T>):
Map<K, V>
├── Map.Entry<K, V>
```

Основные интерфейсы:

- `List<T>`: упорядоченная коллекция только для чтения с индексным доступом.
- `MutableList<T>`: изменяемый список, позволяет добавлять, удалять и изменять элементы.
- `Set<T>`: коллекция уникальных элементов только для чтения.
- `MutableSet<T>`: изменяемый набор уникальных элементов.
- `Map<K, V>`: коллекция пар ключ-значение только для чтения (ключи уникальны).
- `MutableMap<K, V>`: изменяемая коллекция пар ключ-значение.

### `List` И `MutableList` — Упорядоченные Коллекции

```kotlin
// Создание списков
val numbers = listOf(1, 2, 3, 4, 5)
val names = listOf("Alice", "Bob", "Charlie")
val empty = emptyList<String>()
val single = listOf("only one")

// Доступ к элементам
println(numbers[0])            // 1
println(numbers.first())       // 1
println(numbers.last())        // 5
println(numbers.get(2))        // 3
println(numbers.getOrNull(10)) // null
println(numbers.getOrElse(10) { -1 }) // -1

// Свойства списка
println(numbers.size)          // 5
println(numbers.isEmpty())     // false
println(numbers.indices)       // 0..4

// Проверка элементов
println(3 in numbers)          // true
println(numbers.contains(6))   // false

// Поиск элементов
println(numbers.indexOf(3))     // 2
println(numbers.lastIndexOf(3)) // 2
```

```kotlin
// MutableList — изменяемый список
val mutableNumbers = mutableListOf(1, 2, 3)
val arrayList = arrayListOf("a", "b", "c")

// Добавление элементов
mutableNumbers.add(4)               // [1, 2, 3, 4]
mutableNumbers.add(0, 0)            // [0, 1, 2, 3, 4]
mutableNumbers.addAll(listOf(5, 6)) // [0, 1, 2, 3, 4, 5, 6]

// Удаление элементов
mutableNumbers.remove(0)                // [1, 2, 3, 4, 5, 6]
mutableNumbers.removeAt(0)             // [2, 3, 4, 5, 6]
mutableNumbers.removeAll(listOf(2, 3)) // [4, 5, 6]

// Обновление элементов
mutableNumbers[0] = 10            // [10, 5, 6]
mutableNumbers.set(1, 20)         // [10, 20, 6]

// Другие операции
mutableNumbers.clear()            // []
mutableNumbers.addAll(listOf(1, 2, 3))
mutableNumbers.sort()             // [1, 2, 3]
mutableNumbers.reverse()          // [3, 2, 1]
```

### `Set`, `MutableSet` И `LinkedHashSet` — Уникальные Элементы

```kotlin
// Создание `Set`
val numbers = setOf(1, 2, 3, 3, 2, 1)      // [1, 2, 3]
val names = setOf("Alice", "Bob", "Alice") // [Alice, Bob]

// Операции множеств
val set1 = setOf(1, 2, 3, 4)
val set2 = setOf(3, 4, 5, 6)

println(set1.union(set2))        // [1, 2, 3, 4, 5, 6]
println(set1.intersect(set2))    // [3, 4]
println(set1.subtract(set2))     // [1, 2]

// Проверка наличия
println(2 in set1)               // true
println(set1.contains(5))        // false

// Преобразование
val list = setOf(1, 2, 3).toList()
val array = setOf(1, 2, 3).toTypedArray()
```

```kotlin
// MutableSet — изменяемое множество
val mutableSet = mutableSetOf(1, 2, 3)

mutableSet.add(4)                 // true (добавлено)
mutableSet.add(3)                 // false (уже есть)
mutableSet.addAll(setOf(5, 6))    // [1, 2, 3, 4, 5, 6]

mutableSet.remove(1)              // [2, 3, 4, 5, 6]
mutableSet.removeAll(setOf(2, 3)) // [4, 5, 6]
mutableSet.retainAll(setOf(4, 5)) // [4, 5]

mutableSet.clear()                // []
```

```kotlin
// `LinkedHashSet` — сохраняет порядок добавления
val linkedSet = linkedSetOf(3, 1, 2)
println(linkedSet)  // [3, 1, 2]

val hashSet = hashSetOf(3, 1, 2)
println(hashSet)    // порядок зависит от hash, не гарантирован
```

### `Map` И `MutableMap` — Пары Ключ-значение

```kotlin
// Создание `Map`
val ages = mapOf("Alice" to 25, "Bob" to 30, "Charlie" to 35)
val scores = mapOf(
    1 to "first",
    2 to "second",
    3 to "third"
)

// Доступ к значениям
println(ages["Alice"])                  // 25
println(ages.get("Alice"))              // 25
println(ages.getOrDefault("Dave", 0))   // 0
println(ages.getOrElse("Dave") { 0 })   // 0
println(ages.getValue("Alice"))         // 25 (бросает исключение, если ключ отсутствует)

// Свойства `Map`
println(ages.size)                       // 3
println(ages.isEmpty())                  // false
println(ages.keys)                       // [Alice, Bob, Charlie]
println(ages.values)                     // [25, 30, 35]
println(ages.entries)                    // `Set<Map.Entry>`

// Проверка ключей/значений
println("Alice" in ages)                // true
println(ages.containsKey("Dave"))       // false
println(ages.containsValue(25))          // true

// Итерация
for ((name, age) in ages) {
    println("$name is $age years old")
}

ages.forEach { (name, age) ->
    println("$name: $age")
}
```

```kotlin
// MutableMap — изменяемая карта
val mutableAges = mutableMapOf("Alice" to 25, "Bob" to 30)

// Добавление/обновление
mutableAges["Charlie"] = 35              // новый ключ
mutableAges["Alice"] = 26                // обновление
mutableAges.put("Dave", 40)
mutableAges.putAll(mapOf("Eve" to 28, "Frank" to 32))

// Удаление
mutableAges.remove("Bob")                // по ключу
mutableAges.remove("Alice", 25)          // по паре ключ-значение (здесь не сработает)

// Прочее
val age = mutableAges.getOrPut("Grace") { 30 } // получить или добавить по умолчанию
mutableAges.clear()                      // очистить всё
```

### Операторы Коллекций

#### Операции Преобразования (Transformation)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val doubled = numbers.map { it * 2 }
// [2, 4, 6, 8, 10]

val strings = numbers.map { "Number $it" }
// ["Number 1", "Number 2", ...]

// mapIndexed — с индексом
val indexed = numbers.mapIndexed { index, value ->
    "[$index] = $value"
}

// mapNotNull — отбрасывает null
val withNulls = listOf("1", "2", "abc", "3")
val onlyInts = withNulls.mapNotNull { it.toIntOrNull() }
// [1, 2, 3]
```

```kotlin
// flatMap и flatten
val lists = listOf(
    listOf(1, 2, 3),
    listOf(4, 5),
    listOf(6, 7, 8)
)

val flattened = lists.flatten()
// [1, 2, 3, 4, 5, 6, 7, 8]

val doubledFlat = lists.flatMap { inner ->
    inner.map { it * 2 }
}
// [2, 4, 6, 8, 10, 12, 14, 16]

// Пример: собрать все теги из постов
data class Post(val title: String, val tags: List<String>)

val posts = listOf(
    Post("Kotlin Basics", listOf("kotlin", "tutorial")),
    Post("Android Guide", listOf("android", "kotlin")),
    Post("iOS Swift", listOf("ios", "swift"))
)

val allTags = posts.flatMap { it.tags }.distinct()
// [kotlin, tutorial, android, ios, swift]
```

#### Операции Фильтрации (Filtering)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val even = numbers.filter { it % 2 == 0 }
val greaterThan5 = numbers.filter { it > 5 }

val odd = numbers.filterNot { it % 2 == 0 }

val filtered = numbers.filterIndexed { index, value ->
    index % 2 == 0 && value > 3
}

val mixed = listOf(1, "two", 3, "four", 5)
val onlyInts = mixed.filterIsInstance<Int>()
val onlyStrings = mixed.filterIsInstance<String>()
```

```kotlin
// partition — разделить на две коллекции
val (evenPart, oddPart) = numbers.partition { it % 2 == 0 }
```

#### Группировка И Associate

```kotlin
val words = listOf("apple", "apricot", "banana", "blueberry", "cherry")

val byFirstLetter = words.groupBy { it.first() }
val byLength = words.groupBy { it.length }

data class User(val name: String, val age: Int)

val users = listOf(
    User("Alice", 25),
    User("Bob", 30),
    User("Charlie", 25),
    User("Dave", 40),
    User("Eve", 30)
)

val byAge = users.groupBy { it.age }

val byAgeRange = users.groupBy {
    when (it.age) {
        in 20..29 -> "20s"
        in 30..39 -> "30s"
        in 40..49 -> "40s"
        else -> "other"
    }
}
```

```kotlin
// associate — построение `Map`
val nums = listOf(1, 2, 3, 4, 5)

val squares = nums.associateWith { it * it }
val reversed = nums.associateBy { it * it }
val custom = nums.associate { it to "Number $it" }
```

#### Агрегация (Aggregation)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

println(numbers.sum())
println(numbers.average())
println(numbers.minOrNull())
println(numbers.maxOrNull())
println(numbers.count())
println(numbers.count { it > 3 })

val product = numbers.reduce { acc, v -> acc * v }
val sumWithInit = numbers.fold(10) { acc, v -> acc + v }

val joined = numbers.joinToString(separator = ", ", prefix = "[", postfix = "]")
val customJoin = numbers.joinToString { "Number $it" }
```

#### Сортировка (Ordering)

```kotlin
val numbers = listOf(5, 2, 8, 1, 9, 3)

println(numbers.sorted())
println(numbers.sortedDescending())

val words = listOf("banana", "apple", "cherry", "date")
println(words.sorted())

data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 30),
    Person("Bob", 25),
    Person("Charlie", 35)
)

val byAge = people.sortedBy { it.age }
val byName = people.sortedBy { it.name }
val byAgeDesc = people.sortedByDescending { it.age }

val complex = people.sortedWith(compareBy({ it.age }, { it.name }))
```

#### Выборка И Поиск (Selection & Search)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

println(numbers.take(3))
println(numbers.takeLast(3))
println(numbers.drop(3))
println(numbers.dropLast(3))

println(numbers.takeWhile { it < 5 })
println(numbers.dropWhile { it < 5 })

println(numbers.slice(2..5))
println(numbers.slice(listOf(0, 2, 4)))

println(numbers.chunked(3))
println(numbers.windowed(3))

println(numbers.find { it > 3 })
println(numbers.findLast { it > 3 })
println(numbers.firstOrNull { it > 10 })

println(numbers.any { it > 3 })
println(numbers.all { it > 0 })
println(numbers.none { it > 10 })

println(numbers.single { it == 3 })
println(numbers.singleOrNull { it > 10 })
```

### Коллекции Vs Sequences

**Коллекции** вычисляются жадно (eager): каждая операция создает новую коллекцию, все элементы проходят через каждую стадию.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .filter {
        println("filter: $it")
        it % 2 == 0
    }
    .map {
        println("map: $it")
        it * 2
    }
    .take(3)

// Все элементы проходят filter, все четные — map.
```

**Последовательности (Sequences)** вычисляются лениво (lazy): элементы обрабатываются по одному, цепочка может останавливаться рано.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.asSequence()
    .filter {
        println("filter: $it")
        it % 2 == 0
    }
    .map {
        println("map: $it")
        it * 2
    }
    .take(3)
    .toList()

// Обработка по элементу, останавливается после 3 подходящих значений.
```

Когда использовать последовательности:

```kotlin
// Подходят для больших коллекций или длинных цепочек,
// особенно если возможна ранняя остановка.

val largeList = (1..1_000_000).toList()

// Жадно — создаются промежуточные списки
val eager = largeList
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(10)

// Лениво — без полноразмерных промежуточных коллекций
val lazy = largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(10)
    .toList()

// Пример с ранней остановкой
val found = (1..1_000_000).asSequence()
    .map { it * 2 }
    .first { it > 100 }
```

Замечание: для маленьких коллекций или одной-двух операций `Sequence` часто избыточен и медленнее.

### Реальные Примеры

#### Пример 1: Обработка Заказов (E-commerce)

```kotlin
data class Order(
    val id: Int,
    val customerId: Int,
    val items: List<OrderItem>,
    val status: OrderStatus
)

data class OrderItem(
    val productId: Int,
    val name: String,
    val price: Double,
    val quantity: Int
)

enum class OrderStatus { PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED }

class OrderAnalytics(private val orders: List<Order>) {

    fun getTotalRevenue(): Double {
        return orders
            .filter { it.status == OrderStatus.DELIVERED }
            .flatMap { it.items }
            .sumOf { it.price * it.quantity }
    }

    fun getTopProducts(limit: Int): List<Pair<String, Int>> {
        return orders
            .flatMap { it.items }
            .groupBy { it.name }
            .mapValues { (_, items) -> items.sumOf { it.quantity } }
            .toList()
            .sortedByDescending { it.second }
            .take(limit)
    }

    fun getOrdersByStatus(): Map<OrderStatus, Int> {
        return orders.groupingBy { it.status }.eachCount()
    }

    fun getCustomerOrderCount(): Map<Int, Int> {
        return orders.groupingBy { it.customerId }.eachCount()
    }

    fun getAverageOrderValue(): Double {
        return orders.map { order ->
            order.items.sumOf { it.price * it.quantity }
        }.average()
    }
}
```

#### Пример 2: Анализ Логов

```kotlin
data class LogEntry(
    val timestamp: Long,
    val level: LogLevel,
    val message: String,
    val userId: String?
)

enum class LogLevel { DEBUG, INFO, WARNING, ERROR }

class LogAnalyzer(private val logs: List<LogEntry>) {

    fun getErrorLogs(): List<LogEntry> {
        return logs.filter { it.level == LogLevel.ERROR }
    }

    fun groupByLevel(): Map<LogLevel, List<LogEntry>> {
        return logs.groupBy { it.level }
    }

    fun getUserActivityStats(): Map<String, Int> {
        return logs
            .mapNotNull { it.userId }
            .groupingBy { it }
            .eachCount()
            .toList()
            .sortedByDescending { it.second }
            .toMap()
    }

    fun getRecentErrors(hoursAgo: Int): List<LogEntry> {
        val cutoffTime = System.currentTimeMillis() - (hoursAgo * 3600 * 1000)
        return logs.asSequence()
            .filter { it.timestamp >= cutoffTime }
            .filter { it.level == LogLevel.ERROR }
            .sortedByDescending { it.timestamp }
            .take(100)
            .toList()
    }
}
```

#### Пример 3: Конвейер Трансформации Данных

```kotlin
data class RawUser(
    val id: String,
    val firstName: String,
    val lastName: String,
    val email: String,
    val age: String,
    val tags: String  // через запятую
)

data class User(
    val id: Int,
    val fullName: String,
    val email: String,
    val age: Int,
    val tags: Set<String>
)

fun processUsers(rawUsers: List<RawUser>): List<User> {
    return rawUsers.asSequence()
        .mapNotNull { raw ->
            val id = raw.id.toIntOrNull() ?: return@mapNotNull null
            val age = raw.age.toIntOrNull() ?: return@mapNotNull null

            User(
                id = id,
                fullName = "${raw.firstName} ${raw.lastName}",
                email = raw.email.lowercase(),
                age = age,
                tags = raw.tags.split(",")
                    .map { it.trim() }
                    .filter { it.isNotBlank() }
                    .toSet()
            )
        }
        .filter { it.age >= 18 }
        .sortedBy { it.fullName }
        .toList()
}
```

### Лучшие Практики

#### ДЕЛАТЬ:

```kotlin
// Предпочитать интерфейсы только для чтения по умолчанию
val numbers = listOf(1, 2, 3)
val mutable = mutableListOf(1, 2, 3)  // использовать, только если реально нужна мутация

// Цепочки операций для читаемости
val result = users
    .filter { it.age >= 18 }
    .map { it.name }
    .sorted()

// Использовать подходящий тип коллекции
val uniqueIds = setOf(1, 2, 3)
val orderedList = listOf(1, 2, 3)
val keyValue = mapOf("a" to 1)

// Использовать последовательности для больших наборов и длинных цепочек
val seqResult = largeList.asSequence()
    .filter { /* ... */ }
    .map { /* ... */ }
    .toList()

// Использовать готовые агрегирующие функции
val sum = numbers.sum()
val max = numbers.maxOrNull()
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не использовать изменяемые коллекции без необходимости
val numbersBad = mutableListOf(1, 2, 3) // если не изменяется, лучше listOf

// Не создавать лишние промежуточные коллекции
val bad = list
    .filter { /* ... */ }
    .toList()  // лишнее
    .map { /* ... */ }
    .toList()  // часто лишнее
    .sorted()

val good = list
    .filter { /* ... */ }
    .map { /* ... */ }
    .sorted()

// Не использовать sequences для маленьких коллекций с простой логикой
val small = listOf(1, 2, 3)
val overkill = small.asSequence()
    .map { it * 2 }
    .toList()
```

Также см. [[c-collections]] для общей теории коллекций.

---

## Answer (EN)

Kotlin provides a rich set of collection types and operations that make data manipulation elegant and concise. Collections in Kotlin are divided into **read-only interfaces** and **mutable interfaces**. A read-only collection does not guarantee deep immutability of the underlying data; it only does not expose mutating operations via its type.

### Collection Types Overview

Collections hierarchy (simplified):

```
Iterable<T>
├── Collection<T>
│   ├── List<T>
│   └── Set<T>

// Map<K, V> is a separate hierarchy (does NOT extend Iterable<T>):
Map<K, V>
├── Map.Entry<K, V>
```

### List - Ordered Collection

`List`: Read-only, ordered collection with indexed access.

```kotlin
// Creating lists
val numbers = listOf(1, 2, 3, 4, 5)
val names = listOf("Alice", "Bob", "Charlie")
val empty = emptyList<String>()
val single = listOf("only one")

// Accessing elements
println(numbers[0])            // 1
println(numbers.first())       // 1
println(numbers.last())        // 5
println(numbers.get(2))        // 3
println(numbers.getOrNull(10)) // null
println(numbers.getOrElse(10) { -1 }) // -1

// List properties
println(numbers.size)          // 5
println(numbers.isEmpty())     // false
println(numbers.indices)       // 0..4

// Checking elements
println(3 in numbers)          // true
println(numbers.contains(6))   // false

// Finding elements
println(numbers.indexOf(3))    // 2
println(numbers.lastIndexOf(3)) // 2
```

`MutableList`: Mutable variant that allows modifications.

```kotlin
// Creating mutable lists
val mutableNumbers = mutableListOf(1, 2, 3)
val arrayList = arrayListOf("a", "b", "c")

// Adding elements
mutableNumbers.add(4)               // [1, 2, 3, 4]
mutableNumbers.add(0, 0)            // [0, 1, 2, 3, 4]
mutableNumbers.addAll(listOf(5, 6)) // [0, 1, 2, 3, 4, 5, 6]

// Removing elements
mutableNumbers.remove(0)            // [1, 2, 3, 4, 5, 6]
mutableNumbers.removeAt(0)         // [2, 3, 4, 5, 6]
mutableNumbers.removeAll(listOf(2, 3)) // [4, 5, 6]

// Updating elements
mutableNumbers[0] = 10             // [10, 5, 6]
mutableNumbers.set(1, 20)          // [10, 20, 6]

// Other operations
mutableNumbers.clear()             // []
mutableNumbers.addAll(listOf(1, 2, 3))
mutableNumbers.sort()              // [1, 2, 3]
mutableNumbers.reverse()           // [3, 2, 1]
```

### Set - Unique Elements Collection

`Set`: Read-only collection of unique elements.

```kotlin
// Creating sets
val numbers = setOf(1, 2, 3, 3, 2, 1)      // [1, 2, 3]
val names = setOf("Alice", "Bob", "Alice") // [Alice, Bob]

// Set operations
val set1 = setOf(1, 2, 3, 4)
val set2 = setOf(3, 4, 5, 6)

println(set1.union(set2))        // [1, 2, 3, 4, 5, 6]
println(set1.intersect(set2))    // [3, 4]
println(set1.subtract(set2))     // [1, 2]

// Checking membership
println(2 in set1)               // true
println(set1.contains(5))        // false

// Converting
val list = setOf(1, 2, 3).toList()
val array = setOf(1, 2, 3).toTypedArray()
```

`MutableSet`: Mutable variant.

```kotlin
val mutableSet = mutableSetOf(1, 2, 3)

// Adding elements
mutableSet.add(4)                 // true (added)
mutableSet.add(3)                 // false (already exists)
mutableSet.addAll(setOf(5, 6))    // [1, 2, 3, 4, 5, 6]

// Removing elements
mutableSet.remove(1)              // [2, 3, 4, 5, 6]
mutableSet.removeAll(setOf(2, 3)) // [4, 5, 6]
mutableSet.retainAll(setOf(4, 5)) // [4, 5]

// Clear
mutableSet.clear()                // []
```

`LinkedHashSet` maintains insertion order:

```kotlin
val linkedSet = linkedSetOf(3, 1, 2)
println(linkedSet)  // [3, 1, 2] - insertion order preserved

val hashSet = hashSetOf(3, 1, 2)
println(hashSet)    // order based on hash; not insertion-ordered
```

### Map - Key-Value Pairs

`Map`: Read-only collection of key-value pairs.

```kotlin
// Creating maps
val ages = mapOf("Alice" to 25, "Bob" to 30, "Charlie" to 35)
val scores = mapOf(
    1 to "first",
    2 to "second",
    3 to "third"
)

// Accessing values
println(ages["Alice"])                  // 25
println(ages.get("Alice"))              // 25
println(ages.getOrDefault("Dave", 0))   // 0
println(ages.getOrElse("Dave") { 0 })   // 0
println(ages.getValue("Alice"))         // 25 (throws if key missing)

// Map properties
println(ages.size)                       // 3
println(ages.isEmpty())                  // false
println(ages.keys)                       // [Alice, Bob, Charlie]
println(ages.values)                     // [25, 30, 35]
println(ages.entries)                    // Set of Map.Entry

// Checking keys/values
println("Alice" in ages)                // true
println(ages.containsKey("Dave"))       // false
println(ages.containsValue(25))         // true

// Iterating
for ((name, age) in ages) {
    println("$name is $age years old")
}

ages.forEach { (name, age) ->
    println("$name: $age")
}
```

`MutableMap`: Mutable variant.

```kotlin
val mutableAges = mutableMapOf("Alice" to 25, "Bob" to 30)

// Adding/updating entries
mutableAges["Charlie"] = 35              // Add new
mutableAges["Alice"] = 26                // Update existing
mutableAges.put("Dave", 40)              // Add new
mutableAges.putAll(mapOf("Eve" to 28, "Frank" to 32))

// Removing entries
mutableAges.remove("Bob")                // Remove by key
mutableAges.remove("Alice", 25)          // Remove by key-value pair (no-op here)

// Other operations
val age = mutableAges.getOrPut("Grace") { 30 } // Get or put default
mutableAges.clear()                      // Remove all
```

### Collection Operators

#### Transformation Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val doubled = numbers.map { it * 2 }
val strings = numbers.map { "Number $it" }

val indexed = numbers.mapIndexed { index, value ->
    "[$index] = $value"
}

val withNulls = listOf("1", "2", "abc", "3")
val onlyInts = withNulls.mapNotNull { it.toIntOrNull() }
```

```kotlin
val lists = listOf(
    listOf(1, 2, 3),
    listOf(4, 5),
    listOf(6, 7, 8)
)

val flattened = lists.flatten()

val doubledFlat = lists.flatMap { innerList ->
    innerList.map { it * 2 }
}

// Real-world example: Get all tags from posts
data class Post(val title: String, val tags: List<String>)

val posts = listOf(
    Post("Kotlin Basics", listOf("kotlin", "tutorial")),
    Post("Android Guide", listOf("android", "kotlin")),
    Post("iOS Swift", listOf("ios", "swift"))
)

val allTags = posts.flatMap { it.tags }.distinct()
```

#### Filtering Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val even = numbers.filter { it % 2 == 0 }
val greaterThan5 = numbers.filter { it > 5 }

val odd = numbers.filterNot { it % 2 == 0 }

val filtered = numbers.filterIndexed { index, value ->
    index % 2 == 0 && value > 3
}

val mixed = listOf(1, "two", 3, "four", 5)
val onlyInts = mixed.filterIsInstance<Int>()
val onlyStrings = mixed.filterIsInstance<String>()
```

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)
val (evenPart, oddPart) = numbers.partition { it % 2 == 0 }
```

#### Grouping Operators

```kotlin
val words = listOf("apple", "apricot", "banana", "blueberry", "cherry")

val byFirstLetter = words.groupBy { it.first() }
val byLength = words.groupBy { it.length }

data class User(val name: String, val age: Int)

val users = listOf(
    User("Alice", 25),
    User("Bob", 30),
    User("Charlie", 25),
    User("Dave", 40),
    User("Eve", 30)
)

val byAge = users.groupBy { it.age }

val byAgeRange = users.groupBy {
    when (it.age) {
        in 20..29 -> "20s"
        in 30..39 -> "30s"
        in 40..49 -> "40s"
        else -> "other"
    }
}
```

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val map = numbers.associateWith { it * it }
val reversed = numbers.associateBy { it * it }
val custom = numbers.associate { it to "Number $it" }
```

#### Aggregation Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

println(numbers.sum())
println(numbers.average())
println(numbers.minOrNull())
println(numbers.maxOrNull())
println(numbers.count())
println(numbers.count { it > 3 })

val product = numbers.reduce { acc, value -> acc * value }

val sum = numbers.fold(10) { acc, value -> acc + value }

val joined = numbers.joinToString(separator = ", ", prefix = "[", postfix = "]")
val custom = numbers.joinToString { "Number $it" }
```

#### Ordering Operators

```kotlin
val numbers = listOf(5, 2, 8, 1, 9, 3)

println(numbers.sorted())
println(numbers.sortedDescending())

val words = listOf("banana", "apple", "cherry", "date")
println(words.sorted())

data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 30),
    Person("Bob", 25),
    Person("Charlie", 35)
)

val byAge = people.sortedBy { it.age }
val byName = people.sortedBy { it.name }
val byAgeDesc = people.sortedByDescending { it.age }

val complex = people.sortedWith(
    compareBy({ it.age }, { it.name })
)
```

#### Selection Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

println(numbers.take(3))
println(numbers.takeLast(3))
println(numbers.drop(3))
println(numbers.dropLast(3))

println(numbers.takeWhile { it < 5 })
println(numbers.dropWhile { it < 5 })

println(numbers.slice(2..5))
println(numbers.slice(listOf(0, 2, 4)))

println(numbers.chunked(3))
println(numbers.windowed(3))
```

#### Search Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

println(numbers.find { it > 3 })
println(numbers.findLast { it > 3 })
println(numbers.firstOrNull { it > 10 })

println(numbers.any { it > 3 })
println(numbers.all { it > 0 })
println(numbers.none { it > 10 })

println(numbers.single { it == 3 })
println(numbers.singleOrNull { it > 10 })
```

### Collections Vs Sequences

Collections evaluate eagerly (immediately) — each intermediate step creates a new collection, all elements flow through each step.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .filter {
        println("filter: $it")
        it % 2 == 0
    }
    .map {
        println("map: $it")
        it * 2
    }
    .take(3)

// All elements go through filter; all even go through map.
```

Sequences evaluate lazily (on-demand) — processed element by element with possible early termination.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers.asSequence()
    .filter {
        println("filter: $it")
        it % 2 == 0
    }
    .map {
        println("map: $it")
        it * 2
    }
    .take(3)
    .toList()

// Stops once it has 3 matching results.
```

When to use Sequences:

```kotlin
// Use for large datasets or long chains of operations,
// especially when early termination is expected.

val largeList = (1..1_000_000).toList()

val eager = largeList
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(10)

val lazy = largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(10)
    .toList()

val found = (1..1_000_000).asSequence()
    .map { it * 2 }
    .first { it > 100 }
```

Note: For very small collections or simple operations, sequence overhead may make them slower.

### Real-World Examples

#### Example 1: E-commerce Order Processing

```kotlin
data class Order(
    val id: Int,
    val customerId: Int,
    val items: List<OrderItem>,
    val status: OrderStatus
)

data class OrderItem(
    val productId: Int,
    val name: String,
    val price: Double,
    val quantity: Int
)

enum class OrderStatus { PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED }

class OrderAnalytics(private val orders: List<Order>) {

    fun getTotalRevenue(): Double {
        return orders
            .filter { it.status == OrderStatus.DELIVERED }
            .flatMap { it.items }
            .sumOf { it.price * it.quantity }
    }

    fun getTopProducts(limit: Int): List<Pair<String, Int>> {
        return orders
            .flatMap { it.items }
            .groupBy { it.name }
            .mapValues { (_, items) -> items.sumOf { it.quantity } }
            .toList()
            .sortedByDescending { it.second }
            .take(limit)
    }

    fun getOrdersByStatus(): Map<OrderStatus, Int> {
        return orders.groupingBy { it.status }.eachCount()
    }

    fun getCustomerOrderCount(): Map<Int, Int> {
        return orders.groupingBy { it.customerId }.eachCount()
    }

    fun getAverageOrderValue(): Double {
        return orders.map { order ->
            order.items.sumOf { it.price * it.quantity }
        }.average()
    }
}
```

#### Example 2: Log Analysis

```kotlin
data class LogEntry(
    val timestamp: Long,
    val level: LogLevel,
    val message: String,
    val userId: String?
)

enum class LogLevel { DEBUG, INFO, WARNING, ERROR }

class LogAnalyzer(private val logs: List<LogEntry>) {

    fun getErrorLogs(): List<LogEntry> {
        return logs.filter { it.level == LogLevel.ERROR }
    }

    fun groupByLevel(): Map<LogLevel, List<LogEntry>> {
        return logs.groupBy { it.level }
    }

    fun getUserActivityStats(): Map<String, Int> {
        return logs
            .mapNotNull { it.userId }
            .groupingBy { it }
            .eachCount()
            .toList()
            .sortedByDescending { it.second }
            .toMap()
    }

    fun getRecentErrors(hoursAgo: Int): List<LogEntry> {
        val cutoffTime = System.currentTimeMillis() - (hoursAgo * 3600 * 1000)
        return logs.asSequence()
            .filter { it.timestamp >= cutoffTime }
            .filter { it.level == LogLevel.ERROR }
            .sortedByDescending { it.timestamp }
            .take(100)
            .toList()
    }
}
```

#### Example 3: Data Transformation Pipeline

```kotlin
data class RawUser(
    val id: String,
    val firstName: String,
    val lastName: String,
    val email: String,
    val age: String,
    val tags: String  // comma-separated
)

data class User(
    val id: Int,
    val fullName: String,
    val email: String,
    val age: Int,
    val tags: Set<String>
)

fun processUsers(rawUsers: List<RawUser>): List<User> {
    return rawUsers.asSequence()
        .mapNotNull { raw ->
            val id = raw.id.toIntOrNull() ?: return@mapNotNull null
            val age = raw.age.toIntOrNull() ?: return@mapNotNull null

            User(
                id = id,
                fullName = "${raw.firstName} ${raw.lastName}",
                email = raw.email.lowercase(),
                age = age,
                tags = raw.tags.split(",")
                    .map { it.trim() }
                    .filter { it.isNotBlank() }
                    .toSet()
            )
        }
        .filter { it.age >= 18 }
        .sortedBy { it.fullName }
        .toList()
}
```

### Best Practices

#### DO:

```kotlin
// Prefer read-only collection interfaces by default
val numbers = listOf(1, 2, 3)
val mutable = mutableListOf(1, 2, 3)  // Use when you actually need to modify

// Chain operations for readability
val result = users
    .filter { it.age >= 18 }
    .map { it.name }
    .sorted()

// Use appropriate collection type
val uniqueIds = setOf(1, 2, 3)          // For uniqueness
val orderedList = listOf(1, 2, 3)       // For order
val keyValue = mapOf("a" to 1)         // For lookup

// Use sequences for large datasets or long chains where laziness helps
val resultSeq = largeList.asSequence()
    .filter { /* ... */ }
    .map { /* ... */ }
    .toList()

// Use dedicated aggregation helpers
val sum = numbers.sum()
val max = numbers.maxOrNull()
```

#### DON'T:

```kotlin
// Don't use mutable collections when you don't need mutation
val numbersBad = mutableListOf(1, 2, 3) // If you never modify it, prefer listOf

// Don't create unnecessary intermediate collections
val bad = list
    .filter { /* ... */ }
    .toList()
    .map { /* ... */ }
    .toList()
    .sorted()

val better = list
    .filter { /* ... */ }
    .map { /* ... */ }
    .sorted()

// Don't use sequences for trivial small collections
val small = listOf(1, 2, 3)
val overkill = small.asSequence()
    .map { it * 2 }
    .toList()
```

Also see [[c-collections]] for conceptual overview.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия коллекций Kotlin от Java-коллекций?
- Когда вы будете применять те или иные типы коллекций и `Sequence` на практике?
- Какие распространенные ошибки при работе с коллекциями стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- https://kotlinlang.org/docs/collections-overview.html
- https://kotlinlang.org/docs/collection-operations.html
- https://kotlinlang.org/docs/sequences.html
- https://kotlinlang.org/docs/list-operations.html

## References

- [Kotlin Collections Overview](https://kotlinlang.org/docs/collections-overview.html)
- [Collection Operations](https://kotlinlang.org/docs/collection-operations.html)
- [Sequences](https://kotlinlang.org/docs/sequences.html)
- [List Operations](https://kotlinlang.org/docs/list-operations.html)

## Связанные Вопросы (RU)

- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-flow-basics--kotlin--easy]]
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## Related Questions

- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-flow-basics--kotlin--easy]]
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## MOC Ссылки (RU)

- [[moc-kotlin]]

## MOC Links

- [[moc-kotlin]]
