---
tags:
  - coroutines
  - extensions
  - features
  - kotlin
  - null-safety
  - overview
  - programming-languages
difficulty: easy
status: draft
---

# Расскажи про три любимых фичи в Kotlin

**English**: Tell me about three favorite Kotlin features

## Answer

Three favorite Kotlin features:

### 1. Extension Functions
Add new functions to existing classes without modifying them or using inheritance/patterns:
```kotlin
fun String.addExclamation() = this + "!"
"Hello".addExclamation()  // "Hello!"
```

### 2. Null Safety
Protection from NullPointerException at language level with explicit nullable types:
```kotlin
var name: String = "John"    // Cannot be null
var nullable: String? = null // Can be null
nullable?.length             // Safe call
```

### 3. Coroutines
Convenient asynchronous code and multithreading with simple, synchronous-looking syntax:
```kotlin
suspend fun fetchData() {
    val data = withContext(Dispatchers.IO) {
        // Async operation
    }
}
```

**Why these features matter:**
- **Extensions**: Code reuse without inheritance complexity
- **Null Safety**: Prevents most runtime crashes
- **Coroutines**: Simplifies async programming dramatically

## Ответ

Три любимые фичи в Kotlin: Extension Functions для добавления новых функций к существующим классам без их изменения, Null Safety для защиты от NullPointerException и упрощенного управления null-значениями, а также Coroutines для удобной работы с асинхронным кодом и многопоточностью...

