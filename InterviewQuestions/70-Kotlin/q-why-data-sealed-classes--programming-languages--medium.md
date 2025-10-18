---
id: 20251012-154393
title: "Why Data Sealed Classes"
topic: kotlin
difficulty: medium
status: draft
moc: moc-kotlin
related: [q-kotlin-visibility-modifiers--kotlin--easy, q-fan-in-fan-out--kotlin--hard, q-kotlin-crossinline--programming-languages--hard]
created: 2025-10-15
tags:
  - programming-languages
---
# Why are Data Class and Sealed Classes needed?

**English**: Why are Data Class and Sealed Classes needed in Kotlin?

## Answer (EN)

Data classes and sealed classes serve different purposes in Kotlin's type system.

### Data Classes
Automatically generate useful methods:
```kotlin
data class User(val name: String, val age: Int)
// Auto-generates: equals(), hashCode(), toString(), copy(), componentN()

val user = User("Alice", 25)
val older = user.copy(age = 26)
```

**Why use data classes:**
- Need value equality
- Need copy functionality
- Working with immutable data
- Need destructuring

### Sealed Classes
Restrict inheritance to known subtypes:
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

// Exhaustive when
fun handle(result: Result) = when (result) {
    is Result.Success -> show(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // No else needed - compiler knows all cases
}
```

**Why use sealed classes:**
- Represent restricted type hierarchies
- Exhaustive when expressions
- Better than enum when states have data
- ADTs (Algebraic Data Types)

---
---

## Ответ (RU)

Data классы и sealed классы служат разным целям в системе типов Kotlin.

### Data классы
Автоматически генерируют полезные методы:
```kotlin
data class User(val name: String, val age: Int)
// Авто-генерирует: equals(), hashCode(), toString(), copy(), componentN()

val user = User("Alice", 25)
val older = user.copy(age = 26)
```

**Зачем использовать data классы:**
- Нужно равенство по значению
- Нужна функциональность copy
- Работа с неизменяемыми данными
- Нужна деструктуризация

### Sealed классы
Ограничивают наследование известными подтипами:
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

// Исчерпывающий when
fun handle(result: Result) = when (result) {
    is Result.Success -> show(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // else не нужен - компилятор знает все случаи
}
```

**Зачем использовать sealed классы:**
- Представить ограниченные иерархии типов
- Исчерпывающие when выражения
- Лучше чем enum когда состояния имеют данные
- ADTs (Алгебраические типы данных)

---

## Related Questions

- [[q-kotlin-visibility-modifiers--kotlin--easy]]
- [[q-fan-in-fan-out--kotlin--hard]]
- [[q-kotlin-crossinline--programming-languages--hard]]

