---
anki_cards:
- slug: q-guard-conditions-when--kotlin--medium-0-en
  language: en
  anki_id: 1769173419908
  synced_at: '2026-01-23T17:03:51.584646'
- slug: q-guard-conditions-when--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173419934
  synced_at: '2026-01-23T17:03:51.585455'
---
# Вопрос (RU)
> Объясните guard conditions в выражениях when в Kotlin. Как они улучшают сопоставление с образцом? Приведите практические примеры.

# Question (EN)
> Explain guard conditions in Kotlin when expressions. How do they improve pattern matching? Provide practical examples.

## Ответ (RU)

**Введено в Kotlin 2.1, стабильно с 2.2**

**Guard conditions** позволяют добавлять дополнительные условия к веткам `when` с помощью ключевого слова `if`. Это упрощает сложные проверки, которые раньше требовали вложенных `if` или нескольких веток.

---

### Синтаксис

```kotlin
when (value) {
    pattern if condition -> result
    // или
    is Type if additionalCheck -> result
}
```

---

### До Kotlin 2.1 (вложенные if)

```kotlin
sealed interface Result
data class Success(val data: List<String>) : Result
data class Error(val message: String) : Result

fun processOld(result: Result): String {
    return when (result) {
        is Success -> {
            if (result.data.isNotEmpty()) {
                "Success: ${result.data.size} items"
            } else {
                "Success but empty"
            }
        }
        is Error -> {
            if (result.message.isNotBlank()) {
                "Error: ${result.message}"
            } else {
                "Unknown error"
            }
        }
    }
}
```

---

### С Guard Conditions (Kotlin 2.1+)

```kotlin
fun processNew(result: Result): String {
    return when (result) {
        is Success if result.data.isNotEmpty() -> "Success: ${result.data.size} items"
        is Success -> "Success but empty"
        is Error if result.message.isNotBlank() -> "Error: ${result.message}"
        is Error -> "Unknown error"
    }
}
```

**Преимущества:**
- Более плоская структура кода
- Условие и обработка на одной строке
- Smart cast работает внутри guard condition

---

### Практические примеры

**Обработка HTTP-ответов:**

```kotlin
sealed class HttpResponse(val code: Int)
class Success(code: Int, val body: String) : HttpResponse(code)
class ClientError(code: Int, val error: String) : HttpResponse(code)
class ServerError(code: Int) : HttpResponse(code)

fun handleResponse(response: HttpResponse): String = when (response) {
    is Success if response.body.isNotEmpty() -> "OK: ${response.body}"
    is Success -> "Empty response"
    is ClientError if response.code == 404 -> "Not found"
    is ClientError if response.code == 401 -> "Unauthorized"
    is ClientError -> "Client error: ${response.error}"
    is ServerError if response.code >= 500 -> "Server error: ${response.code}"
    else -> "Unknown response"
}
```

**Валидация данных:**

```kotlin
data class User(val name: String, val age: Int, val email: String?)

fun validateUser(user: User): String = when {
    user.name.isBlank() -> "Name required"
    user.age < 0 -> "Invalid age"
    user.age if user.age < 18 -> "Must be 18+"
    user.email if user.email?.contains("@") != true -> "Invalid email"
    else -> "Valid"
}
```

**Комбинация с destructuring:**

```kotlin
data class Point(val x: Int, val y: Int)

fun classifyPoint(point: Point): String = when (point) {
    Point(0, 0) -> "Origin"
    Point(x, y) if x == y -> "On diagonal"
    Point(x, 0) if x > 0 -> "Positive X axis"
    Point(0, y) if y > 0 -> "Positive Y axis"
    Point(x, y) if x > 0 && y > 0 -> "First quadrant"
    else -> "Other"
}
```

---

### Включение функции

Для Kotlin 2.1 требуется флаг компилятора:

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xwhen-guards")
    }
}
```

В Kotlin 2.2+ guard conditions стабильны и не требуют флага.

---

### Ключевые особенности

| Аспект | Описание |
|--------|----------|
| Smart cast | Работает внутри guard condition |
| Порядок веток | Важен: проверяется сверху вниз |
| Совместимость | Можно комбинировать с `is`, значениями, ranges |
| Exhaustiveness | Компилятор проверяет полноту покрытия |

---

## Answer (EN)

**Introduced in Kotlin 2.1, stable since 2.2**

**Guard conditions** allow adding extra conditions to `when` branches using the `if` keyword. This simplifies complex checks that previously required nested `if` statements or multiple branches.

---

### Syntax

```kotlin
when (value) {
    pattern if condition -> result
    // or
    is Type if additionalCheck -> result
}
```

---

### Before Kotlin 2.1 (Nested if)

```kotlin
sealed interface Result
data class Success(val data: List<String>) : Result
data class Error(val message: String) : Result

fun processOld(result: Result): String {
    return when (result) {
        is Success -> {
            if (result.data.isNotEmpty()) {
                "Success: ${result.data.size} items"
            } else {
                "Success but empty"
            }
        }
        is Error -> {
            if (result.message.isNotBlank()) {
                "Error: ${result.message}"
            } else {
                "Unknown error"
            }
        }
    }
}
```

---

### With Guard Conditions (Kotlin 2.1+)

```kotlin
fun processNew(result: Result): String {
    return when (result) {
        is Success if result.data.isNotEmpty() -> "Success: ${result.data.size} items"
        is Success -> "Success but empty"
        is Error if result.message.isNotBlank() -> "Error: ${result.message}"
        is Error -> "Unknown error"
    }
}
```

**Benefits:**
- Flatter code structure
- Condition and handling on single line
- Smart cast works inside guard condition

---

### Practical Examples

**HTTP Response Handling:**

```kotlin
sealed class HttpResponse(val code: Int)
class Success(code: Int, val body: String) : HttpResponse(code)
class ClientError(code: Int, val error: String) : HttpResponse(code)
class ServerError(code: Int) : HttpResponse(code)

fun handleResponse(response: HttpResponse): String = when (response) {
    is Success if response.body.isNotEmpty() -> "OK: ${response.body}"
    is Success -> "Empty response"
    is ClientError if response.code == 404 -> "Not found"
    is ClientError if response.code == 401 -> "Unauthorized"
    is ClientError -> "Client error: ${response.error}"
    is ServerError if response.code >= 500 -> "Server error: ${response.code}"
    else -> "Unknown response"
}
```

**Data Validation:**

```kotlin
data class User(val name: String, val age: Int, val email: String?)

fun validateUser(user: User): String = when {
    user.name.isBlank() -> "Name required"
    user.age < 0 -> "Invalid age"
    user.age if user.age < 18 -> "Must be 18+"
    user.email if user.email?.contains("@") != true -> "Invalid email"
    else -> "Valid"
}
```

**Combined with Destructuring:**

```kotlin
data class Point(val x: Int, val y: Int)

fun classifyPoint(point: Point): String = when (point) {
    Point(0, 0) -> "Origin"
    Point(x, y) if x == y -> "On diagonal"
    Point(x, 0) if x > 0 -> "Positive X axis"
    Point(0, y) if y > 0 -> "Positive Y axis"
    Point(x, y) if x > 0 && y > 0 -> "First quadrant"
    else -> "Other"
}
```

---

### Enabling the Feature

For Kotlin 2.1, a compiler flag is required:

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xwhen-guards")
    }
}
```

In Kotlin 2.2+, guard conditions are stable and require no flag.

---

### Key Features

| Aspect | Description |
|--------|-------------|
| Smart cast | Works inside guard condition |
| Branch order | Matters: checked top to bottom |
| Compatibility | Can combine with `is`, values, ranges |
| Exhaustiveness | Compiler checks full coverage |

---

## Follow-ups

- How do guard conditions interact with sealed classes exhaustiveness checking?
- Can you use multiple conditions in a single guard?
- What are the performance implications of guard conditions?

## Related Questions

- [[q-kotlin-sealed-when-exhaustive--kotlin--medium]]
- [[q-sealed-classes--kotlin--medium]]

## References

- https://kotlinlang.org/docs/whatsnew21.html#guard-conditions-in-when-with-a-subject
- https://kotlinlang.org/docs/control-flow.html#when-expression
