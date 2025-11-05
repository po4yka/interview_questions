---
id: kotlin-100
title: "Kotlin Collections / Коллекции в Kotlin"
aliases: ["Kotlin Collections, Коллекции в Kotlin"]

# Classification
topic: kotlin
subtopics:
  - collections
  - list
  - map
  - sequences
  - set
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
related: [q-expect-actual-kotlin--kotlin--medium, q-flow-basics--kotlin--easy, q-kotlin-val-vs-var--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [collections, difficulty/medium, filter, flatmap, kotlin, list, map, operators, sequences, set]
date created: Sunday, October 12th 2025, 3:02:56 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Question (EN)
> What are Kotlin collections? Explain List, Set, Map, their mutable variants, collection operators, and the difference between Collections and Sequences.

# Вопрос (RU)
> Что такое коллекции в Kotlin? Объясните List, Set, Map, их изменяемые варианты, операторы коллекций и разницу между Collections и Sequences.

---

## Answer (EN)

Kotlin provides a rich set of collection types and operations that make data manipulation elegant and concise. Collections in Kotlin are divided into **immutable** (read-only) and **mutable** variants.

### Collection Types Overview

```
Collections Hierarchy:

    Iterable<T>





 List      Set      Map



 MutableList


          MutableSet


                     MutableMap

```

### List - Ordered Collection

**List**: Read-only, ordered collection with indexed access:

```kotlin
// Creating lists
val numbers = listOf(1, 2, 3, 4, 5)
val names = listOf("Alice", "Bob", "Charlie")
val empty = emptyList<String>()
val single = listOf("only one")

// Accessing elements
println(numbers[0])           // 1
println(numbers.first())      // 1
println(numbers.last())       // 5
println(numbers.get(2))       // 3
println(numbers.getOrNull(10)) // null
println(numbers.getOrElse(10) { -1 }) // -1

// List properties
println(numbers.size)         // 5
println(numbers.isEmpty())    // false
println(numbers.indices)      // 0..4

// Checking elements
println(3 in numbers)         // true
println(numbers.contains(6))  // false

// Finding elements
println(numbers.indexOf(3))   // 2
println(numbers.lastIndexOf(3)) // 2
```

**MutableList**: Mutable variant that allows modifications:

```kotlin
// Creating mutable lists
val mutableNumbers = mutableListOf(1, 2, 3)
val arrayList = arrayListOf("a", "b", "c")

// Adding elements
mutableNumbers.add(4)              // [1, 2, 3, 4]
mutableNumbers.add(0, 0)           // [0, 1, 2, 3, 4]
mutableNumbers.addAll(listOf(5, 6)) // [0, 1, 2, 3, 4, 5, 6]

// Removing elements
mutableNumbers.remove(0)           // [1, 2, 3, 4, 5, 6]
mutableNumbers.removeAt(0)         // [2, 3, 4, 5, 6]
mutableNumbers.removeAll(listOf(2, 3)) // [4, 5, 6]

// Updating elements
mutableNumbers[0] = 10            // [10, 5, 6]
mutableNumbers.set(1, 20)         // [10, 20, 6]

// Other operations
mutableNumbers.clear()            // []
mutableNumbers.addAll(listOf(1, 2, 3))
mutableNumbers.sort()             // [1, 2, 3]
mutableNumbers.reverse()          // [3, 2, 1]
```

### Set - Unique Elements Collection

**Set**: Read-only collection of unique elements:

```kotlin
// Creating sets
val numbers = setOf(1, 2, 3, 3, 2, 1)  // [1, 2, 3] - duplicates removed
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

**MutableSet**: Mutable variant:

```kotlin
val mutableSet = mutableSetOf(1, 2, 3)

// Adding elements
mutableSet.add(4)                // true (added)
mutableSet.add(3)                // false (already exists)
mutableSet.addAll(setOf(5, 6))   // [1, 2, 3, 4, 5, 6]

// Removing elements
mutableSet.remove(1)             // [2, 3, 4, 5, 6]
mutableSet.removeAll(setOf(2, 3)) // [4, 5, 6]
mutableSet.retainAll(setOf(4, 5)) // [4, 5]

// Clear
mutableSet.clear()               // []
```

**LinkedHashSet** - maintains insertion order:

```kotlin
val linkedSet = linkedSetOf(3, 1, 2)
println(linkedSet)  // [3, 1, 2] - insertion order preserved

val hashSet = hashSetOf(3, 1, 2)
println(hashSet)    // [1, 2, 3] - no order guaranteed
```

### Map - Key-Value Pairs

**Map**: Read-only collection of key-value pairs:

```kotlin
// Creating maps
val ages = mapOf("Alice" to 25, "Bob" to 30, "Charlie" to 35)
val scores = mapOf(
    1 to "first",
    2 to "second",
    3 to "third"
)

// Accessing values
println(ages["Alice"])           // 25
println(ages.get("Alice"))       // 25
println(ages.getOrDefault("Dave", 0)) // 0
println(ages.getOrElse("Dave") { 0 }) // 0
println(ages.getValue("Alice"))  // 25 (throws if key missing)

// Map properties
println(ages.size)               // 3
println(ages.isEmpty())          // false
println(ages.keys)               // [Alice, Bob, Charlie]
println(ages.values)             // [25, 30, 35]
println(ages.entries)            // Set of Map.Entry

// Checking keys/values
println("Alice" in ages)         // true
println(ages.containsKey("Dave")) // false
println(ages.containsValue(25))  // true

// Iterating
for ((name, age) in ages) {
    println("$name is $age years old")
}

ages.forEach { (name, age) ->
    println("$name: $age")
}
```

**MutableMap**: Mutable variant:

```kotlin
val mutableAges = mutableMapOf("Alice" to 25, "Bob" to 30)

// Adding/updating entries
mutableAges["Charlie"] = 35          // Add new
mutableAges["Alice"] = 26            // Update existing
mutableAges.put("Dave", 40)          // Add new
mutableAges.putAll(mapOf("Eve" to 28, "Frank" to 32))

// Removing entries
mutableAges.remove("Bob")            // Remove by key
mutableAges.remove("Alice", 25)      // Remove by key-value pair

// Other operations
val age = mutableAges.getOrPut("Grace") { 30 } // Get or put default
mutableAges.clear()                  // Remove all
```

### Collection Operators

#### Transformation Operators

**map** - Transform each element:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val doubled = numbers.map { it * 2 }
// [2, 4, 6, 8, 10]

val strings = numbers.map { "Number $it" }
// ["Number 1", "Number 2", "Number 3", "Number 4", "Number 5"]

// mapIndexed - includes index
val indexed = numbers.mapIndexed { index, value ->
    "[$index] = $value"
}
// ["[0] = 1", "[1] = 2", "[2] = 3", "[3] = 4", "[4] = 5"]

// mapNotNull - filters out nulls
val withNulls = listOf("1", "2", "abc", "3")
val onlyInts = withNulls.mapNotNull { it.toIntOrNull() }
// [1, 2, 3]
```

**flatMap** - Transform and flatten:

```kotlin
val lists = listOf(
    listOf(1, 2, 3),
    listOf(4, 5),
    listOf(6, 7, 8)
)

val flattened = lists.flatten()
// [1, 2, 3, 4, 5, 6, 7, 8]

val doubled = lists.flatMap { innerList ->
    innerList.map { it * 2 }
}
// [2, 4, 6, 8, 10, 12, 14, 16]

// Real-world example: Get all tags from posts
data class Post(val title: String, val tags: List<String>)

val posts = listOf(
    Post("Kotlin Basics", listOf("kotlin", "tutorial")),
    Post("Android Guide", listOf("android", "kotlin")),
    Post("iOS Swift", listOf("ios", "swift"))
)

val allTags = posts.flatMap { it.tags }.distinct()
// [kotlin, tutorial, android, ios, swift]
```

#### Filtering Operators

**filter** - Select elements matching predicate:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val even = numbers.filter { it % 2 == 0 }
// [2, 4, 6, 8, 10]

val greaterThan5 = numbers.filter { it > 5 }
// [6, 7, 8, 9, 10]

// filterNot - opposite of filter
val odd = numbers.filterNot { it % 2 == 0 }
// [1, 3, 5, 7, 9]

// filterIndexed - with index
val filtered = numbers.filterIndexed { index, value ->
    index % 2 == 0 && value > 3
}
// [5, 7, 9]

// filterIsInstance - filter by type
val mixed = listOf(1, "two", 3, "four", 5)
val onlyInts = mixed.filterIsInstance<Int>()
// [1, 3, 5]
val onlyStrings = mixed.filterIsInstance<String>()
// [two, four]
```

**partition** - Split into two lists:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)
val (even, odd) = numbers.partition { it % 2 == 0 }
// even = [2, 4, 6], odd = [1, 3, 5]
```

#### Grouping Operators

**groupBy** - Group elements by key:

```kotlin
val words = listOf("apple", "apricot", "banana", "blueberry", "cherry")

val byFirstLetter = words.groupBy { it.first() }
// {a=[apple, apricot], b=[banana, blueberry], c=[cherry]}

val byLength = words.groupBy { it.length }
// {5=[apple], 7=[apricot, banana, cherry], 9=[blueberry]}

// Real-world example: Group users by age range
data class User(val name: String, val age: Int)

val users = listOf(
    User("Alice", 25),
    User("Bob", 30),
    User("Charlie", 25),
    User("Dave", 40),
    User("Eve", 30)
)

val byAge = users.groupBy { it.age }
// {25=[User(Alice, 25), User(Charlie, 25)], 30=[User(Bob, 30), User(Eve, 30)], 40=[User(Dave, 40)]}

val byAgeRange = users.groupBy {
    when (it.age) {
        in 20..29 -> "20s"
        in 30..39 -> "30s"
        in 40..49 -> "40s"
        else -> "other"
    }
}
// {20s=[User(Alice, 25), User(Charlie, 25)], 30s=[User(Bob, 30), User(Eve, 30)], 40s=[User(Dave, 40)]}
```

**associate** - Create map from collection:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val map = numbers.associateWith { it * it }
// {1=1, 2=4, 3=9, 4=16, 5=25}

val reversed = numbers.associateBy { it * it }
// {1=1, 4=2, 9=3, 16=4, 25=5}

val custom = numbers.associate { it to "Number $it" }
// {1=Number 1, 2=Number 2, 3=Number 3, 4=Number 4, 5=Number 5}
```

#### Aggregation Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

println(numbers.sum())           // 15
println(numbers.average())       // 3.0
println(numbers.min())           // 1
println(numbers.max())           // 5
println(numbers.count())         // 5
println(numbers.count { it > 3 }) // 2

// reduce - combine elements
val product = numbers.reduce { acc, value -> acc * value }
// 120 (1 * 2 * 3 * 4 * 5)

// fold - with initial value
val sum = numbers.fold(10) { acc, value -> acc + value }
// 25 (10 + 1 + 2 + 3 + 4 + 5)

// joinToString - create string
val joined = numbers.joinToString(separator = ", ", prefix = "[", postfix = "]")
// "[1, 2, 3, 4, 5]"

val custom = numbers.joinToString { "Number $it" }
// "Number 1, Number 2, Number 3, Number 4, Number 5"
```

#### Ordering Operators

```kotlin
val numbers = listOf(5, 2, 8, 1, 9, 3)

println(numbers.sorted())        // [1, 2, 3, 5, 8, 9]
println(numbers.sortedDescending()) // [9, 8, 5, 3, 2, 1]

val words = listOf("banana", "apple", "cherry", "date")
println(words.sorted())          // [apple, banana, cherry, date]

// sortedBy - custom comparator
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 30),
    Person("Bob", 25),
    Person("Charlie", 35)
)

val byAge = people.sortedBy { it.age }
// [Bob(25), Alice(30), Charlie(35)]

val byName = people.sortedBy { it.name }
// [Alice(30), Bob(25), Charlie(35)]

val byAgeDesc = people.sortedByDescending { it.age }
// [Charlie(35), Alice(30), Bob(25)]

// sortedWith - complex sorting
val complex = people.sortedWith(
    compareBy({ it.age }, { it.name })
)
```

#### Selection Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

println(numbers.take(3))         // [1, 2, 3]
println(numbers.takeLast(3))     // [8, 9, 10]
println(numbers.drop(3))         // [4, 5, 6, 7, 8, 9, 10]
println(numbers.dropLast(3))     // [1, 2, 3, 4, 5, 6, 7]

println(numbers.takeWhile { it < 5 }) // [1, 2, 3, 4]
println(numbers.dropWhile { it < 5 }) // [5, 6, 7, 8, 9, 10]

println(numbers.slice(2..5))     // [3, 4, 5, 6]
println(numbers.slice(listOf(0, 2, 4))) // [1, 3, 5]

// Chunked - split into chunks
println(numbers.chunked(3))      // [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

// Windowed - sliding window
println(numbers.windowed(3))     // [[1, 2, 3], [2, 3, 4], [3, 4, 5], ...]
```

#### Search Operators

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

println(numbers.find { it > 3 })        // 4 (first match)
println(numbers.findLast { it > 3 })    // 5 (last match)
println(numbers.firstOrNull { it > 10 }) // null

println(numbers.any { it > 3 })         // true
println(numbers.all { it > 0 })         // true
println(numbers.none { it > 10 })       // true

println(numbers.single { it == 3 })     // 3
// println(numbers.single { it > 3 })   // Error: multiple matches
println(numbers.singleOrNull { it > 10 }) // null
```

### Collections Vs Sequences

**Collections** evaluate eagerly (immediately):

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

// Output:
// filter: 1
// filter: 2
// filter: 3
// ... (all 10 elements filtered)
// map: 2
// map: 4
// ... (all 5 even elements mapped)
// Result: [4, 8, 12]
```

**Sequences** evaluate lazily (on-demand):

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

// Output:
// filter: 1
// filter: 2
// map: 2
// filter: 3
// filter: 4
// map: 4
// filter: 5
// filter: 6
// map: 6
// Result: [4, 8, 12]
```

**When to use Sequences:**

```kotlin
// Use sequences for large datasets
val largeList = (1..1_000_000).toList()

// Collections - creates 3 intermediate lists
val eager = largeList
    .filter { it % 2 == 0 }  // 500k list
    .map { it * 2 }          // 500k list
    .take(10)                // 10 list

// Sequences - no intermediate lists
val lazy = largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(10)
    .toList()

// Sequences with early termination
val found = (1..1_000_000).asSequence()
    .map { it * 2 }
    .first { it > 100 }  // Stops at 51
```

**Performance comparison:**

```kotlin
// Small collection - Collections faster
val small = (1..100).toList()
small.filter { it % 2 == 0 }.map { it * 2 }  // Faster

// Large collection with chaining - Sequences faster
val large = (1..1_000_000).toList()
large.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .filter { it > 1000 }
    .toList()  // Faster

// When to use what:
// Collections: small data, single operation, need indexed access
// Sequences: large data, multiple operations, early termination
```

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
// Use immutable collections by default
val numbers = listOf(1, 2, 3)  // Prefer this
val mutable = mutableListOf(1, 2, 3)  // Only when needed

// Chain operations for readability
val result = users
    .filter { it.age >= 18 }
    .map { it.name }
    .sorted()

// Use sequences for large datasets
val result = largeList.asSequence()
    .filter { /* ... */ }
    .map { /* ... */ }
    .toList()

// Use appropriate collection type
val uniqueIds = setOf(1, 2, 3)  // For uniqueness
val orderedList = listOf(1, 2, 3)  // For order
val keyValue = mapOf("a" to 1)  // For lookup

// Use collection-specific operations
val sum = numbers.sum()  // Better than reduce
val max = numbers.maxOrNull()  // Better than fold
```

#### DON'T:

```kotlin
// Don't use mutable collections when immutable works
val numbers = mutableListOf(1, 2, 3)  // Unnecessary
numbers.add(4)  // If you're not modifying, use listOf

// Don't create unnecessary intermediate collections
val result = list
    .filter { /* ... */ }
    .toList()  // Unnecessary
    .map { /* ... */ }
    .toList()  // Unnecessary
    .sorted()

// Better:
val result = list
    .filter { /* ... */ }
    .map { /* ... */ }
    .sorted()

// Don't use sequences for small collections
val small = listOf(1, 2, 3)
val result = small.asSequence()  // Overhead not worth it
    .map { it * 2 }
    .toList()
```

---

## Ответ (RU)

Kotlin предоставляет богатый набор типов коллекций и операций, которые делают манипуляцию данными элегантной и лаконичной. Коллекции в Kotlin разделены на **неизменяемые** (read-only) и **изменяемые** варианты.

### Обзор Типов Коллекций

**List**: Упорядоченная коллекция только для чтения с индексным доступом
**MutableList**: Изменяемый вариант, позволяющий модификации
**Set**: Коллекция уникальных элементов только для чтения
**MutableSet**: Изменяемый набор
**Map**: Коллекция пар ключ-значение только для чтения
**MutableMap**: Изменяемая карта

### Операторы Коллекций

#### Map - Преобразовать Каждый Элемент:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }
// [2, 4, 6, 8, 10]
```

#### Filter - Выбрать Элементы По Условию:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)
val even = numbers.filter { it % 2 == 0 }
// [2, 4, 6]
```

#### flatMap - Преобразовать И Сгладить:

```kotlin
val lists = listOf(listOf(1, 2), listOf(3, 4))
val flattened = lists.flatten()
// [1, 2, 3, 4]
```

#### groupBy - Группировать Элементы По Ключу:

```kotlin
val words = listOf("apple", "banana", "apricot")
val byFirstLetter = words.groupBy { it.first() }
// {a=[apple, apricot], b=[banana]}
```

### Коллекции Vs Последовательности

**Коллекции** оцениваются немедленно (eagerly):
- Каждая операция создаёт промежуточную коллекцию
- Все элементы обрабатываются сразу
- Хороши для небольших наборов данных

**Последовательности** оцениваются лениво (lazily):
- Не создают промежуточные коллекции
- Обрабатывают элементы по требованию
- Хороши для больших наборов данных
- Поддерживают досрочное завершение

```kotlin
// Использовать последовательности для больших датасетов
val largeList = (1..1_000_000).toList()

val result = largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(10)
    .toList()
```

### Реальные Примеры

```kotlin
data class User(val name: String, val age: Int)

val users = listOf(
    User("Alice", 25),
    User("Bob", 30),
    User("Charlie", 25)
)

// Группировка по возрасту
val byAge = users.groupBy { it.age }
// {25=[User(Alice, 25), User(Charlie, 25)], 30=[User(Bob, 30)]}

// Получить имена взрослых пользователей
val adultNames = users
    .filter { it.age >= 18 }
    .map { it.name }
    .sorted()
// [Alice, Bob, Charlie]
```

### Лучшие Практики

#### ДЕЛАТЬ:

```kotlin
// Использовать неизменяемые коллекции по умолчанию
val numbers = listOf(1, 2, 3)

// Цепочки операций для читаемости
val result = users
    .filter { it.age >= 18 }
    .map { it.name }
    .sorted()

// Использовать последовательности для больших датасетов
val result = largeList.asSequence()
    .filter { /* ... */ }
    .map { /* ... */ }
    .toList()
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не использовать изменяемые коллекции когда работают неизменяемые
val numbers = mutableListOf(1, 2, 3)  // Лишнее

// Не создавать лишние промежуточные коллекции
val result = list
    .filter { /* ... */ }
    .toList()  // Лишнее
    .map { /* ... */ }
```

---

## References

- [Kotlin Collections Overview](https://kotlinlang.org/docs/collections-overview.html)
- [Collection Operations](https://kotlinlang.org/docs/collection-operations.html)
- [Sequences](https://kotlinlang.org/docs/sequences.html)
- [List Operations](https://kotlinlang.org/docs/list-operations.html)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-flow-basics--kotlin--easy]]
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## MOC Links

- [[moc-kotlin]]
