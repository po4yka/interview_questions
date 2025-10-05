---
tags:
  - kotlin
  - collections
  - filtering
  - pair
difficulty: easy
---

# partition(): разделение коллекции на две части

**English**: partition() function in Kotlin collections

## Answer

`partition()` делит коллекцию на **два списка**: первый содержит элементы, соответствующие условию (`true`), второй — не соответствующие (`false`). Возвращает `Pair<List, List>`. Удобно для фильтрации без потери "невалидных" элементов.

### Базовое использование

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// Разделить на четные и нечетные
val (even, odd) = numbers.partition { it % 2 == 0 }

println("Even: $even")  // Even: [2, 4, 6, 8, 10]
println("Odd: $odd")    // Odd: [1, 3, 5, 7, 9]
```

**Эквивалентно:**
```kotlin
val even = numbers.filter { it % 2 == 0 }
val odd = numbers.filter { it % 2 != 0 }
// Но partition проходит по коллекции только один раз!
```

### Возвращаемый тип

```kotlin
val result: Pair<List<Int>, List<Int>> = numbers.partition { it > 5 }

val matching = result.first   // [6, 7, 8, 9, 10]
val nonMatching = result.second  // [1, 2, 3, 4, 5]

// Или с деструктуризацией
val (matching, nonMatching) = numbers.partition { it > 5 }
```

### Сравнение с filter

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)

// С filter - два прохода по коллекции
val positive = numbers.filter { it > 3 }       // [4, 5, 6]
val negative = numbers.filter { it <= 3 }      // [1, 2, 3]

// С partition - один проход
val (positive, negative) = numbers.partition { it > 3 }
// positive = [4, 5, 6]
// negative = [1, 2, 3]
```

### Практические примеры

#### Пример 1: Валидация данных

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
    User("", "bob@example.com", 30),          // Невалидное имя
    User("Charlie", "invalid-email", 22),     // Невалидный email
    User("David", "david@example.com", 150),  // Невалидный возраст
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

#### Пример 2: Обработка результатов API

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String) : ApiResult<Nothing>()
}

val results = listOf(
    ApiResult.Success(User(1, "Alice")),
    ApiResult.Error("Network timeout"),
    ApiResult.Success(User(2, "Bob")),
    ApiResult.Error("404 Not Found"),
    ApiResult.Success(User(3, "Charlie"))
)

// Разделить на успешные и ошибки
val (successes, errors) = results.partition { it is ApiResult.Success }

val users = successes.filterIsInstance<ApiResult.Success<User>>()
    .map { it.data }

val errorMessages = errors.filterIsInstance<ApiResult.Error>()
    .map { it.message }

println("Users: ${users.map { it.name }}")
// Users: [Alice, Bob, Charlie]

println("Errors: $errorMessages")
// Errors: [Network timeout, 404 Not Found]
```

#### Пример 3: Сортировка файлов

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

#### Пример 4: Разделение задач по приоритету

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

// Разделить на высокий и низкий приоритет
val (urgent, regular) = tasks.partition { it.isHighPriority }

println("Urgent tasks:")
urgent.forEach { println("  - ${it.title} (priority ${it.priority})") }
// Urgent tasks:
//   - Fix critical bug (priority 10)
//   - Security patch (priority 9)

println("Regular tasks:")
regular.forEach { println("  - ${it.title} (priority ${it.priority})") }
// Regular tasks:
//   - Update docs (priority 3)
//   - Refactor code (priority 5)
//   - Add tests (priority 6)
```

#### Пример 5: Обработка платежей

```kotlin
data class Payment(val id: Int, val amount: Double, val status: String)

val payments = listOf(
    Payment(1, 100.0, "completed"),
    Payment(2, 250.0, "failed"),
    Payment(3, 75.0, "completed"),
    Payment(4, 500.0, "pending"),
    Payment(5, 150.0, "completed")
)

// Разделить на успешные и требующие внимания
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

### Работа с пустыми коллекциями

```kotlin
val empty = emptyList<Int>()
val (matching, nonMatching) = empty.partition { it > 0 }

println(matching)     // []
println(nonMatching)  // []
// Обе части пустые
```

### Вложенное использование

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

println("Excellent: ${excellent.map { it.name }}")  // Excellent: [Charlie]
println("Good: ${good.map { it.name }}")            // Good: [Alice, Eve]
println("Failing: ${failing.map { it.name }}")      // Failing: [Bob, David]
```

### Performance

```kotlin
val largeList = (1..1_000_000).toList()

// С filter - два прохода
val time1 = measureTimeMillis {
    val positive = largeList.filter { it > 500_000 }
    val negative = largeList.filter { it <= 500_000 }
}
println("filter x2: $time1 ms")  // ~80-100 ms

// С partition - один проход
val time2 = measureTimeMillis {
    val (positive, negative) = largeList.partition { it > 500_000 }
}
println("partition: $time2 ms")  // ~40-50 ms

// partition в ~2 раза быстрее!
```

### С другими коллекциями

```kotlin
// Set
val numbers = setOf(1, 2, 3, 4, 5, 6)
val (even, odd) = numbers.partition { it % 2 == 0 }
// even и odd теперь List, не Set!

// Sequence
val sequence = sequenceOf(1, 2, 3, 4, 5, 6)
val (even, odd) = sequence.partition { it % 2 == 0 }
// partition материализует Sequence в List
```

### Типичные use cases

**1. Разделение на категории**

```kotlin
enum class Category { URGENT, NORMAL }

val (urgent, normal) = items.partition { it.category == Category.URGENT }
```

**2. Обработка ошибок**

```kotlin
val (successes, failures) = results.partition { it.isSuccess }
```

**3. Фильтрация с логированием**

```kotlin
val (valid, invalid) = data.partition { it.isValid() }

invalid.forEach { logger.warn("Invalid data: $it") }
processData(valid)
```

**4. A/B тестирование**

```kotlin
val (groupA, groupB) = users.partition { it.id % 2 == 0 }

groupA.forEach { showFeatureA(it) }
groupB.forEach { showFeatureB(it) }
```

### Best Practices

**✅ Используйте partition когда:**

1. Нужны обе группы (matching и non-matching)
2. Хотите избежать двух проходов по коллекции
3. Важна производительность для больших коллекций

**❌ НЕ используйте partition когда:**

1. Нужна только одна группа (используйте `filter`)
2. Нужно разделить на >2 группы (используйте `groupBy`)

```kotlin
// ❌ НЕПРАВИЛЬНО - нужна только одна группа
val (valid, _) = data.partition { it.isValid() }
// Лучше использовать filter
val valid = data.filter { it.isValid() }

// ❌ НЕПРАВИЛЬНО - нужно >2 групп
val (low, notLow) = items.partition { it.priority < 5 }
val (medium, high) = notLow.partition { it.priority < 8 }
// Лучше использовать groupBy
val byPriority = items.groupBy {
    when (it.priority) {
        in 0..4 -> "low"
        in 5..7 -> "medium"
        else -> "high"
    }
}
```

**English**: `partition()` splits collection into **two lists** based on predicate: first contains matching elements (`true`), second contains non-matching (`false`). Returns `Pair<List, List>`. Use destructuring: `val (matching, nonMatching) = list.partition { condition }`. Traverses collection **once** (2x faster than two `filter` calls). Use for: validation (valid/invalid), results (success/error), categorization (urgent/normal). Don't use if need only one group (use `filter`) or >2 groups (use `groupBy`). Works with List, Set, Sequence (materializes to List).

