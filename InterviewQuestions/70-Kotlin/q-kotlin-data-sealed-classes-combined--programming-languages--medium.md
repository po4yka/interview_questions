---
id: 20251012-12271111119
title: "Kotlin Data Sealed Classes Combined"
topic: computer-science
difficulty: medium
status: draft
moc: moc-kotlin
related: [q-stateflow-sharedflow-differences--kotlin--medium, q-channels-basics-types--kotlin--medium, q-kotlin-native--kotlin--hard]
created: 2025-10-15
tags:
  - data-class
  - kotlin
  - oop
  - programming-languages
  - sealed-class
  - type-safety
  - when-expressions
---
# Расскажи data классы и sealed классы

# Question (EN)
> Tell me about data classes and sealed classes

# Вопрос (RU)
> Расскажи data классы и sealed классы

---

## Answer (EN)

### Data Classes

Data classes are designed for **storing data** and automatically generate useful methods:
- `equals()` - value-based equality
- `hashCode()` - consistent hashing
- `toString()` - readable string representation
- `copy()` - create modified copies

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = user1.copy(age = 31)
```

### Sealed Classes

Sealed classes represent **restricted inheritance hierarchies** where all possible subclasses are known at compile time:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val error: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

### Combining Both

Together, they create **type-safe and easily manageable data structures**, especially for `when` expressions:

```kotlin
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.error}")
    Result.Loading -> println("Loading...")
}  // Exhaustive - compiler checks all cases!
```

**Benefits of combination:**
- Type safety at compile time
- Exhaustive when expressions
- Clean, maintainable code
- Perfect for state management

---

## Ответ (RU)

### Data классы

Data классы предназначены для **хранения данных** и автоматически генерируют полезные методы:
- `equals()` - равенство на основе значений
- `hashCode()` - согласованное хеширование
- `toString()` - читаемое строковое представление
- `copy()` - создание модифицированных копий

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = user1.copy(age = 31)
```

### Sealed классы

Sealed классы представляют **ограниченные иерархии наследования**, где все возможные подклассы известны во время компиляции:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val error: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

### Комбинация обоих

Вместе они создают **типобезопасные и легко управляемые структуры данных**, особенно для выражений `when`:

```kotlin
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.error}")
    Result.Loading -> println("Loading...")
}  // Исчерпывающе - компилятор проверяет все случаи!
```

**Преимущества комбинации:**
- Типобезопасность во время компиляции
- Исчерпывающие when-выражения
- Чистый, поддерживаемый код
- Идеально для управления состоянием

## Related Questions

- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-channels-basics-types--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
