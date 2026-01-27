---
id: kotlin-kmp-001
title: Expect/Actual Mechanism / Механизм expect/actual
aliases:
- KMP Expect Actual
- Platform Specific Code
- Kotlin Multiplatform Declarations
topic: kotlin
subtopics:
- kmp
- multiplatform
- platform-specific
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kmp
- multiplatform
- expect-actual
- difficulty/medium
anki_cards:
- slug: kotlin-kmp-001-0-en
  language: en
  anki_id: 1769344148440
  synced_at: '2026-01-25T16:29:08.491820'
- slug: kotlin-kmp-001-0-ru
  language: ru
  anki_id: 1769344148490
  synced_at: '2026-01-25T16:29:08.493639'
---
# Question (EN)
> What is the expect/actual mechanism in Kotlin Multiplatform and how does it work?

# Vopros (RU)
> Что такое механизм expect/actual в Kotlin Multiplatform и как он работает?

## Answer (EN)

The **expect/actual** mechanism is Kotlin Multiplatform's approach to declaring platform-specific implementations while maintaining a common API in shared code.

### Core Concept

- **`expect`** declarations define the API contract in common code (what should exist)
- **`actual`** declarations provide platform-specific implementations (how it works)

```kotlin
// commonMain - declares expected interface
expect class Platform() {
    val name: String
    fun currentTimeMillis(): Long
}

// androidMain - actual implementation for Android
actual class Platform actual constructor() {
    actual val name: String = "Android ${android.os.Build.VERSION.SDK_INT}"
    actual fun currentTimeMillis(): Long = System.currentTimeMillis()
}

// iosMain - actual implementation for iOS
actual class Platform actual constructor() {
    actual val name: String = UIDevice.currentDevice.systemName()
    actual fun currentTimeMillis(): Long =
        (NSDate().timeIntervalSince1970 * 1000).toLong()
}
```

### What Can Be expect/actual

| Declaration | Support | Example |
|-------------|---------|---------|
| **Functions** | Yes | `expect fun platformLog(msg: String)` |
| **Properties** | Yes | `expect val platformName: String` |
| **Classes** | Yes | `expect class HttpClient` |
| **Objects** | Yes | `expect object Logger` |
| **Annotations** | Yes | `expect annotation class Parcelize` |
| **Typealias** | Yes | `expect typealias PlatformList<T>` |

### Rules and Constraints

1. **All expect declarations must have actual implementations** for each target platform
2. **Actual declarations must match signatures exactly** (parameters, return types)
3. **Visibility must match** - actual cannot be more restrictive than expect
4. **Actual class can have additional members** not declared in expect

```kotlin
// commonMain
expect class FileSystem {
    fun readFile(path: String): ByteArray
    fun writeFile(path: String, data: ByteArray)
}

// androidMain - can add extra platform-specific methods
actual class FileSystem {
    actual fun readFile(path: String): ByteArray { /* Android impl */ }
    actual fun writeFile(path: String, data: ByteArray) { /* Android impl */ }

    // Additional Android-specific method (not in expect)
    fun getExternalStoragePath(): String { /* ... */ }
}
```

### Common Use Cases

1. **Platform APIs**: `UUID.randomUUID()`, date/time, file system
2. **Logging**: Platform-specific loggers (Logcat on Android, NSLog on iOS)
3. **Cryptography**: Platform cryptographic libraries
4. **Concurrency primitives**: Dispatchers, thread-local storage
5. **UI-related utilities**: Platform-specific formatters

### Best Practices

- **Keep expect declarations minimal** - only what truly differs per platform
- **Prefer interfaces over expect classes** when possible
- **Use expect functions for utilities**, expect classes for complex types
- **Document platform-specific behaviors** in common code

```kotlin
// Prefer this approach when possible
interface Logger {
    fun log(level: LogLevel, message: String)
}

expect fun createLogger(tag: String): Logger

// Platform implementations provide the factory
actual fun createLogger(tag: String): Logger = AndroidLogger(tag)
```

---

## Otvet (RU)

Механизм **expect/actual** - это подход Kotlin Multiplatform к объявлению платформо-специфичных реализаций при сохранении общего API в разделяемом коде.

### Основная концепция

- **`expect`** объявления определяют контракт API в общем коде (что должно существовать)
- **`actual`** объявления предоставляют платформо-специфичные реализации (как это работает)

```kotlin
// commonMain - объявляет ожидаемый интерфейс
expect class Platform() {
    val name: String
    fun currentTimeMillis(): Long
}

// androidMain - actual реализация для Android
actual class Platform actual constructor() {
    actual val name: String = "Android ${android.os.Build.VERSION.SDK_INT}"
    actual fun currentTimeMillis(): Long = System.currentTimeMillis()
}

// iosMain - actual реализация для iOS
actual class Platform actual constructor() {
    actual val name: String = UIDevice.currentDevice.systemName()
    actual fun currentTimeMillis(): Long =
        (NSDate().timeIntervalSince1970 * 1000).toLong()
}
```

### Что может быть expect/actual

| Объявление | Поддержка | Пример |
|------------|-----------|--------|
| **Функции** | Да | `expect fun platformLog(msg: String)` |
| **Свойства** | Да | `expect val platformName: String` |
| **Классы** | Да | `expect class HttpClient` |
| **Объекты** | Да | `expect object Logger` |
| **Аннотации** | Да | `expect annotation class Parcelize` |
| **Typealias** | Да | `expect typealias PlatformList<T>` |

### Правила и ограничения

1. **Все expect объявления должны иметь actual реализации** для каждой целевой платформы
2. **Actual объявления должны точно соответствовать сигнатурам** (параметры, типы возврата)
3. **Видимость должна совпадать** - actual не может быть более ограничительным чем expect
4. **Actual класс может иметь дополнительные члены**, не объявленные в expect

```kotlin
// commonMain
expect class FileSystem {
    fun readFile(path: String): ByteArray
    fun writeFile(path: String, data: ByteArray)
}

// androidMain - может добавлять дополнительные платформо-специфичные методы
actual class FileSystem {
    actual fun readFile(path: String): ByteArray { /* Android реализация */ }
    actual fun writeFile(path: String, data: ByteArray) { /* Android реализация */ }

    // Дополнительный Android-специфичный метод (не в expect)
    fun getExternalStoragePath(): String { /* ... */ }
}
```

### Типичные случаи использования

1. **Платформенные API**: `UUID.randomUUID()`, дата/время, файловая система
2. **Логирование**: Платформо-специфичные логгеры (Logcat на Android, NSLog на iOS)
3. **Криптография**: Платформенные криптографические библиотеки
4. **Примитивы конкурентности**: Диспатчеры, thread-local хранилище
5. **UI-утилиты**: Платформо-специфичные форматтеры

### Лучшие практики

- **Минимизируйте expect объявления** - только то, что действительно отличается на платформах
- **Предпочитайте интерфейсы expect классам** когда возможно
- **Используйте expect функции для утилит**, expect классы для сложных типов
- **Документируйте платформо-специфичное поведение** в общем коде

```kotlin
// Предпочтительный подход когда возможно
interface Logger {
    fun log(level: LogLevel, message: String)
}

expect fun createLogger(tag: String): Logger

// Платформенные реализации предоставляют фабрику
actual fun createLogger(tag: String): Logger = AndroidLogger(tag)
```

---

## Follow-ups

- How does the compiler verify expect/actual matching?
- What happens if an actual declaration is missing for a target?
- How do expect/actual work with generics?
- When should you use expect/actual vs dependency injection?

## Dopolnitelnye Voprosy (RU)

- Как компилятор проверяет соответствие expect/actual?
- Что происходит, если actual объявление отсутствует для целевой платформы?
- Как expect/actual работает с дженериками?
- Когда следует использовать expect/actual против внедрения зависимостей?

## References

- [Kotlin Multiplatform Documentation](https://kotlinlang.org/docs/multiplatform-expect-actual.html)
- [KMP Official Guide](https://kotlinlang.org/docs/multiplatform.html)

## Ssylki (RU)

- [[c-kotlin]]
- [Документация Kotlin Multiplatform](https://kotlinlang.org/docs/multiplatform-expect-actual.html)

## Related Questions

- [[q-kmp-project-structure--kmp--medium]]
- [[q-kmp-shared-code-strategy--kmp--hard]]
