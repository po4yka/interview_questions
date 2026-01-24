---
id: kotlin-208
title: Partition Function / Функция partition
aliases:
- Collection Partition
- Filtering
- Partition
- Partition Function
topic: kotlin
subtopics:
- collections
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-coroutine-job-lifecycle--kotlin--medium
- q-testing-viewmodel-coroutines--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- collections
- difficulty/easy
- filtering
- kotlin
- pair
- partition
anki_cards:
- slug: kotlin-208-0-en
  language: en
  anki_id: 1768326291431
  synced_at: '2026-01-23T17:03:51.509618'
- slug: kotlin-208-0-ru
  language: ru
  anki_id: 1768326291456
  synced_at: '2026-01-23T17:03:51.510557'
---
# Вопрос (RU)

> Что делает функция `partition()` в Kotlin и когда её стоит использовать?

# Question (EN)

> What does the `partition()` function in Kotlin do, and when should you use it?

## Ответ (RU)

`partition()` разделяет коллекцию на **два списка** на основе предиката: первый содержит элементы, для которых предикат вернул `true`, второй — элементы, для которых предикат вернул `false`. Возвращает `Pair<List<T>, List<T>>`. Удобна, когда нужно отфильтровать данные, сохранив обе группы.

### Базовый Пример

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// Разделить на чётные и нечётные
val (even, odd) = numbers.partition { it % 2 == 0 }

println("Even: $even")  // Even: [2, 4, 6, 8, 10]
println("Odd: $odd")    // Odd: [1, 3, 5, 7, 9]
```

Эквивалентно двум фильтрам, но с одним проходом по коллекции:

```kotlin
val even = numbers.filter { it % 2 == 0 }
val odd = numbers.filter { it % 2 != 0 }
```

### Тип Возвращаемого Значения

```kotlin
val result: Pair<List<Int>, List<Int>> = numbers.partition { it > 5 }

val matching = result.first       // [6, 7, 8, 9, 10]
val nonMatching = result.second   // [1, 2, 3, 4, 5]

// Или через деструктуризацию
val (matching2, nonMatching2) = numbers.partition { it > 5 }
```

### Сравнение С Filter

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)

// filter — два прохода по коллекции
val positive = numbers.filter { it > 3 }      // [4, 5, 6]
val negative = numbers.filter { it <= 3 }     // [1, 2, 3]

// partition — один проход для этого предиката
val (positive2, negative2) = numbers.partition { it > 3 }
// positive2 = [4, 5, 6]
// negative2 = [1, 2, 3]
```

### Практические Примеры

#### Пример 1: Валидация Данных

```kotlin
data class User(val name: String, val email: String, val age: Int) {
    fun isValid(): Boolean {
        return name.isNotBlank() &&
               email.contains("@") &&
               age in 18..120
    }
}

val users = listOf(
    User("Alice", "alice@example.com", 25),
    User("", "bob@example.com", 30),          // Неверное имя
    User("Charlie", "invalid-email", 22),     // Неверный email
    User("David", "david@example.com", 150),  // Неверный возраст
    User("Eve", "eve@example.com", 28)
)

// Разделить на валидных и невалидных
val (valid, invalid) = users.partition { it.isValid() }

println("Valid users: ${valid.map { it.name }}")
// Valid users: [Alice, Eve]

println("Invalid users: ${invalid.map { it.name }}")
// Invalid users: [, Charlie, David]

// Можно обработать обе группы
valid.forEach { saveToDatabase(it) }
invalid.forEach { logValidationError(it) }
```

#### Пример 2: Обработка Результатов API

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String) : ApiResult<Nothing>()
}

data class ApiUser(val id: Int, val name: String)

val results = listOf(
    ApiResult.Success(ApiUser(1, "Alice")),
    ApiResult.Error("Network timeout"),
    ApiResult.Success(ApiUser(2, "Bob")),
    ApiResult.Error("404 Not Found"),
    ApiResult.Success(ApiUser(3, "Charlie"))
)

// Разделяем на успешные и ошибочные результаты
val (successes, errors) = results.partition { it is ApiResult.Success }

val usersFromSuccess = successes.filterIsInstance<ApiResult.Success<ApiUser>>()
    .map { it.data }

val errorMessages = errors.filterIsInstance<ApiResult.Error>()
    .map { it.message }

println("Users: ${usersFromSuccess.map { it.name }}")
// Users: [Alice, Bob, Charlie]

println("Errors: $errorMessages")
// Errors: [Network timeout, 404 Not Found]
```

#### Пример 3: Сортировка Файлов

```kotlin
val files = listOf(
    File("document.pdf"),
    File("image.jpg"),
    File("data.json"),
    File("photo.png"),
    File("config.xml"),
    File("archive.zip")
)

// Разделить на изображения и остальные
val (images, others) = files.partition {
    it.extension in listOf("jpg", "jpeg", "png", "gif", "bmp")
}

println("Images: ${images.map { it.name }}")
// Images: [image.jpg, photo.png]

println("Other files: ${others.map { it.name }}")
// Other files: [document.pdf, data.json, config.xml, archive.zip]
```

#### Пример 4: Разделение Задач По Приоритету

```kotlin
data class Task(val title: String, val priority: Int) {
    val isHighPriority get() = priority >= 8
}

val tasks = listOf(
    Task("Fix critical bug", 10),
    Task("Update docs", 3),
    Task("Refactor code", 5),
    Task("Security patch", 9),
    Task("Add tests", 6)
)

// Разделить на высокий и обычный приоритет
val (urgent, regular) = tasks.partition { it.isHighPriority }

println("Urgent tasks:")
urgent.forEach { println("  - ${it.title} (priority ${it.priority})") }

println("Regular tasks:")
regular.forEach { println("  - ${it.title} (priority ${it.priority})") }
```

#### Пример 5: Обработка Платежей

```kotlin
data class Payment(val id: Int, val amount: Double, val status: String)

val payments = listOf(
    Payment(1, 100.0, "completed"),
    Payment(2, 250.0, "failed"),
    Payment(3, 75.0, "completed"),
    Payment(4, 500.0, "pending"),
    Payment(5, 150.0, "completed")
)

// Разделить на успешные и требующие внимания (pending/failed)
val (completed, needsAttention) = payments.partition {
    it.status == "completed"
}

val totalCompleted = completed.sumOf { it.amount }
val totalPending = needsAttention.filter { it.status == "pending" }
    .sumOf { it.amount }
val totalFailed = needsAttention.filter { it.status == "failed" }
    .sumOf { it.amount }

println("Completed: $$totalCompleted")  // Completed: $325.0
println("Pending: $$totalPending")      // Pending: $500.0
println("Failed: $$totalFailed")        // Failed: $250.0
```

### Работа С Пустыми Коллекциями

```kotlin
val empty = emptyList<Int>()
val (matching, nonMatching) = empty.partition { it > 0 }

println(matching)     // []
println(nonMatching)  // []
// Обе части пустые
```

### Вложенное Использование И Деструктуризация

```kotlin
data class Student(val name: String, val grade: Int, val isPassing: Boolean)

val students = listOf(
    Student("Alice", 85, true),
    Student("Bob", 45, false),
    Student("Charlie", 92, true),
    Student("David", 38, false),
    Student("Eve", 78, true)
)

// Сначала разделить на успевающих и неуспевающих
val (passing, failing) = students.partition { it.isPassing }

// Затем разделить успевающих на отличников и хорошистов
val (excellent, good) = passing.partition { it.grade >= 90 }

println("Excellent: ${excellent.map { it.name }}")
println("Good: ${good.map { it.name }}")
println("Failing: ${failing.map { it.name }}")
```

### Performance / Ленивость Против Eager

```kotlin
val largeList = (1..1_000_000).toList()

// Два filter — два прохода
val time1 = measureTimeMillis {
    val positive = largeList.filter { it > 500_000 }
    val negative = largeList.filter { it <= 500_000 }
}
println("filter x2: $time1 ms")

// partition — один проход
val time2 = measureTimeMillis {
    val (positive, negative) = largeList.partition { it > 500_000 }
}
println("partition: $time2 ms")
```

- `partition()` всегда делает eager-разделение и возвращает `List`-ы.
- Для `Sequence` результат тоже немедленно материализуется в `List` (в отличие от ленивых цепочек операций `Sequence`).

### Работа С Разными Коллекциями

```kotlin
// Set
val numbers = setOf(1, 2, 3, 4, 5, 6)
val (even, odd) = numbers.partition { it % 2 == 0 }
// even и odd имеют тип `List<Int>`, не `Set<Int>`

// Sequence
val sequence = sequenceOf(1, 2, 3, 4, 5, 6)
val (evenSeq, oddSeq) = sequence.partition { it % 2 == 0 }
// partition материализует Sequence в `List<Int>` (eager), в отличие от ленивых операций Sequence
```

### Типичные Use Cases

1. Разделение на категории (например, `URGENT` / `NORMAL`).
2. Разделение результатов (`success` / `error`).
3. Фильтрация с логированием (валидные данные + лог невалидных).
4. A/B тестирование (две группы пользователей).

### Best Practices

Используйте `partition`, когда:

1. Нужны обе группы (matching и non-matching) одновременно.
2. Хотите избежать нескольких проходов по коллекции с одним и тем же предикатом.
3. Работаете с большими коллекциями и важна производительность.

Не используйте `partition`, когда:

1. Нужна только одна группа — используйте `filter`.

```kotlin
// Анти-паттерн: берём только одну группу
val (validOnly, _) = data.partition { it.isValid() }
// Правильно:
val validOnly2 = data.filter { it.isValid() }
```

1. Нужно разбить на более чем две группы — используйте `groupBy`.

```kotlin
// Анти-паттерн: последовательные partition для приоритетов
val (low, notLow) = items.partition { it.priority < 5 }
val (medium, high) = notLow.partition { it.priority < 8 }

// Лучше сразу сгруппировать
val byPriority = items.groupBy {
    when (it.priority) {
        in 0..4 -> "low"
        in 5..7 -> "medium"
        else -> "high"
    }
}
```

## Answer (EN)

`partition()` splits a collection into **two lists** based on a predicate: the first contains elements for which the predicate returns `true`, the second contains elements for which it returns `false`. Returns `Pair<List<T>, List<T>>`. It is eager and always materializes both result lists. Convenient when you need to filter while keeping both groups.

### Basic Usage

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// Split into even and odd
val (even, odd) = numbers.partition { it % 2 == 0 }

println("Even: $even")  // Even: [2, 4, 6, 8, 10]
println("Odd: $odd")    // Odd: [1, 3, 5, 7, 9]
```

Equivalent to:

```kotlin
val even = numbers.filter { it % 2 == 0 }
val odd = numbers.filter { it % 2 != 0 }
// But partition traverses the collection only once for this predicate!
```

### Return Type

```kotlin
val result: Pair<List<Int>, List<Int>> = numbers.partition { it > 5 }

val matching = result.first       // [6, 7, 8, 9, 10]
val nonMatching = result.second   // [1, 2, 3, 4, 5]

// Or with destructuring
val (matching2, nonMatching2) = numbers.partition { it > 5 }
```

### Comparison with Filter

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)

// With filter - two passes through the collection
val positive = numbers.filter { it > 3 }       // [4, 5, 6]
val negative = numbers.filter { it <= 3 }      // [1, 2, 3]

// With partition - one pass through the collection for this predicate
val (positive2, negative2) = numbers.partition { it > 3 }
// positive2 = [4, 5, 6]
// negative2 = [1, 2, 3]
```

### Practical Examples

#### Example 1: Data Validation

```kotlin
data class User(val name: String, val email: String, val age: Int) {
    fun isValid(): Boolean {
        return name.isNotBlank() &&
               email.contains("@") &&
               age in 18..120
    }
}

val users = listOf(
    User("Alice", "alice@example.com", 25),
    User("", "bob@example.com", 30),          // Invalid name
    User("Charlie", "invalid-email", 22),     // Invalid email
    User("David", "david@example.com", 150),  // Invalid age
    User("Eve", "eve@example.com", 28)
)

// Split into valid and invalid
val (valid, invalid) = users.partition { it.isValid() }

println("Valid users: ${valid.map { it.name }}")
// Valid users: [Alice, Eve]

println("Invalid users: ${invalid.map { it.name }}")
// Invalid users: [, Charlie, David]

// Can process both groups
valid.forEach { saveToDatabase(it) }
invalid.forEach { logValidationError(it) }
```

#### Example 2: Processing API Results

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String) : ApiResult<Nothing>()
}

data class ApiUser(val id: Int, val name: String)

val results = listOf(
    ApiResult.Success(ApiUser(1, "Alice")),
    ApiResult.Error("Network timeout"),
    ApiResult.Success(ApiUser(2, "Bob")),
    ApiResult.Error("404 Not Found"),
    ApiResult.Success(ApiUser(3, "Charlie"))
)

// Split into successes and errors
val (successes, errors) = results.partition { it is ApiResult.Success }

val usersFromSuccess = successes.filterIsInstance<ApiResult.Success<ApiUser>>()
    .map { it.data }

val errorMessages = errors.filterIsInstance<ApiResult.Error>()
    .map { it.message }

println("Users: ${usersFromSuccess.map { it.name }}")
// Users: [Alice, Bob, Charlie]

println("Errors: $errorMessages")
// Errors: [Network timeout, 404 Not Found]
```

#### Example 3: File Sorting

```kotlin
val files = listOf(
    File("document.pdf"),
    File("image.jpg"),
    File("data.json"),
    File("photo.png"),
    File("config.xml"),
    File("archive.zip")
)

// Split into images and others
val (images, others) = files.partition {
    it.extension in listOf("jpg", "jpeg", "png", "gif", "bmp")
}

println("Images: ${images.map { it.name }}")
// Images: [image.jpg, photo.png]

println("Other files: ${others.map { it.name }}")
// Other files: [document.pdf, data.json, config.xml, archive.zip]
```

#### Example 4: Tasks by Priority

```kotlin
data class Task(val title: String, val priority: Int) {
    val isHighPriority get() = priority >= 8
}

val tasks = listOf(
    Task("Fix critical bug", 10),
    Task("Update docs", 3),
    Task("Refactor code", 5),
    Task("Security patch", 9),
    Task("Add tests", 6)
)

val (urgent, regular) = tasks.partition { it.isHighPriority }

println("Urgent tasks:")
urgent.forEach { println("  - ${it.title} (priority ${it.priority})") }

println("Regular tasks:")
regular.forEach { println("  - ${it.title} (priority ${it.priority})") }
```

#### Example 5: Payments

```kotlin
data class Payment(val id: Int, val amount: Double, val status: String)

val payments = listOf(
    Payment(1, 100.0, "completed"),
    Payment(2, 250.0, "failed"),
    Payment(3, 75.0, "completed"),
    Payment(4, 500.0, "pending"),
    Payment(5, 150.0, "completed")
)

val (completed, needsAttention) = payments.partition {
    it.status == "completed"
}

val totalCompleted = completed.sumOf { it.amount }
val totalPending = needsAttention.filter { it.status == "pending" }
    .sumOf { it.amount }
val totalFailed = needsAttention.filter { it.status == "failed" }
    .sumOf { it.amount }

println("Completed: $$totalCompleted")
println("Pending: $$totalPending")
println("Failed: $$totalFailed")
```

### Working with Empty Collections

```kotlin
val empty = emptyList<Int>()
val (matching, nonMatching) = empty.partition { it > 0 }

println(matching)     // []
println(nonMatching)  // []
```

### Nested Usage

```kotlin
data class Student(val name: String, val grade: Int, val isPassing: Boolean)

val students = listOf(
    Student("Alice", 85, true),
    Student("Bob", 45, false),
    Student("Charlie", 92, true),
    Student("David", 38, false),
    Student("Eve", 78, true)
)

val (passing, failing) = students.partition { it.isPassing }
val (excellent, good) = passing.partition { it.grade >= 90 }

println("Excellent: ${excellent.map { it.name }}")
println("Good: ${good.map { it.name }}")
println("Failing: ${failing.map { it.name }}")
```

### Performance / Eager Vs Lazy

```kotlin
val largeList = (1..1_000_000).toList()

// Two filters = two passes
val time1 = measureTimeMillis {
    val positive = largeList.filter { it > 500_000 }
    val negative = largeList.filter { it <= 500_000 }
}
println("filter x2: $time1 ms")

// partition = one pass
val time2 = measureTimeMillis {
    val (positive, negative) = largeList.partition { it > 500_000 }
}
println("partition: $time2 ms")
```

- `partition()` is always eager and returns `List`s.
- For a `Sequence`, `partition()` also eagerly materializes both result lists (unlike other lazy `Sequence` operations).

### With other Collections

```kotlin
// Set
val numbers = setOf(1, 2, 3, 4, 5, 6)
val (even, odd) = numbers.partition { it % 2 == 0 }
// even and odd are `List<Int>`, not `Set<Int>`

// Sequence
val sequence = sequenceOf(1, 2, 3, 4, 5, 6)
val (evenSeq, oddSeq) = sequence.partition { it % 2 == 0 }
// partition eagerly materializes to `List<Int>` (not lazy like other Sequence ops)
```

### Typical Use Cases

1. Splitting into two categories (e.g., `URGENT` / `NORMAL`).
2. Separating results (`success` / `error`).
3. Filtering with logging.
4. A/B testing.

### Best Practices

Use `partition` when:

1. You need both matching and non-matching elements.
2. You want to avoid multiple passes for the same predicate.
3. Working with large collections where performance matters.

Do NOT use `partition` when:

1. You need only one group — use `filter`.

```kotlin
// Wrong: only one group is needed
val (validOnly, _) = data.partition { it.isValid() }
// Better:
val validOnly2 = data.filter { it.isValid() }
```

1. You need more than two groups — use `groupBy`.

```kotlin
// Wrong: multiple partition calls
val (low, notLow) = items.partition { it.priority < 5 }
val (medium, high) = notLow.partition { it.priority < 8 }

// Better:
val byPriority = items.groupBy {
    when (it.priority) {
        in 0..4 -> "low"
        in 5..7 -> "medium"
        else -> "high"
    }
}
```

## Дополнительные Вопросы (RU)

- В чём отличие использования `partition()` от нескольких вызовов `filter`?
- В каких практических случаях вы бы применили `partition()`?
- Каковы типичные ошибки при использовании `partition()`?

## Follow-ups

- What are the key differences between this and multiple `filter` calls?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Официальная документация Kotlin: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]

## References

- Kotlin Documentation: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]
