---
id: android-101
title: "Parcelable Implementation / Реализация Parcelable"
aliases: [Android Parcelable, Parcelable, Parcelable Implementation, Реализация Parcelable]
topic: android
subtopics: [intents-deeplinks, performance-memory, serialization]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity, c-service, q-bundle-data-types--android--medium, q-how-to-pass-parameters-to-fragment--android--easy, q-what-are-intents-for--android--medium]
created: 2025-10-13
updated: 2025-10-30
tags: [android/intents-deeplinks, android/performance-memory, android/serialization, bundle, difficulty/medium, ipc, parcelable]
sources: [https://developer.android.com/reference/android/os/Parcelable, https://kotlinlang.org/docs/compiler-plugins.html#parcelable-implementations-generator]
---

# Вопрос (RU)

> Что вы знаете о `Parcelable`?

# Question (EN)

> What do you know about `Parcelable`?

---

## Ответ (RU)

**`Parcelable`** — это Android интерфейс для эффективной сериализации объектов при передаче между компонентами приложения (`Activity`, `Fragment`, `Service`). Оптимизирован для IPC (межпроцессного взаимодействия) и значительно быстрее Java `Serializable` благодаря отсутствию рефлексии.

### Ключевые Характеристики

- **Производительность**: Быстрее `Serializable` в 10+ раз, записывает данные напрямую в Parcel без рефлексии
- **Типобезопасность**: Проверка типов на этапе компиляции
- **IPC-оптимизация**: Использует Binder для передачи через границы процессов
- **Ограничение размера**: Транзакции через `Intent` ограничены ~1MB (TransactionTooLargeException)

### Современная Реализация С @Parcelize

✅ **Рекомендуемый подход** — автоматическая генерация кода:

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-parcelize")
}

// Простой data class
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

// Вложенные объекты
@Parcelize
data class UserProfile(
    val user: User,
    val address: Address,
    val tags: List<String>
) : Parcelable
```

### Передача Данных Между Компонентами

```kotlin
// Отправка
val user = User(1, "John", "john@example.com")
startActivity(Intent(this, DetailActivity::class.java).apply {
    putExtra("user", user)
})

// Получение (type-safe API)
val user = if (Build.VERSION.SDK_INT >= 33) {
    intent.getParcelableExtra("user", User::class.java)
} else {
    intent.getParcelableExtra<User>("user")
}
```

### Кастомная Сериализация С TypeParceler

Для типов, не поддерживающих `Parcelable` (Date, UUID, custom types):

```kotlin
@Parcelize
@TypeParceler<Date, DateParceler>
data class Event(
    val title: String,
    val timestamp: Date
) : Parcelable

object DateParceler : Parceler<Date> {
    override fun create(parcel: Parcel) = Date(parcel.readLong())
    override fun Date.write(parcel: Parcel, flags: Int) = parcel.writeLong(time)
}
```

### Сравнение С `Serializable`

| Характеристика | `Parcelable` | `Serializable` |
|---|---|---|
| Производительность | Быстрый (без рефлексии) | Медленный (рефлексия) |
| Реализация | @Parcelize — минимальная | implements `Serializable` |
| Android-оптимизация | Да (Binder IPC) | Нет |
| Overhead | Низкий | Высокий (GC pressure) |

### Ограничения И Best Practices

❌ **Избегать**:
- Передача больших объектов через `Intent` (используйте ViewModel/`Repository`)
- Циклические ссылки (приводят к StackOverflowError)
- Сериализация non-`Parcelable` полей без TypeParceler

✅ **Рекомендуется**:
- Использовать @Parcelize вместо ручной реализации
- Проверять размер `Bundle` перед отправкой (`Bundle.size()`)
- Для больших данных использовать `ContentProvider` или файлы
- Использовать type-safe методы получения на API 33+

### Когда Использовать

- Передача данных через `Intent` между Activity/`Fragment`
- Аргументы `Fragment` (`setArguments(`Bundle`)`)
- Сохранение состояния в `onSaveInstanceState`
- Межпроцессное взаимодействие (AIDL, Messenger)

## Answer (EN)

**`Parcelable`** is an Android interface for efficient object serialization when passing data between app components (`Activity`, `Fragment`, `Service`). Optimized for IPC (inter-process communication) and significantly faster than Java `Serializable` by avoiding reflection.

### Key Characteristics

- **Performance**: 10x+ faster than `Serializable`, writes directly to Parcel without reflection
- **Type Safety**: Compile-time type checking
- **IPC Optimization**: Uses Binder for cross-process communication
- **Size Limitation**: `Intent` transactions limited to ~1MB (TransactionTooLargeException)

### Modern Implementation with @Parcelize

✅ **Recommended approach** — automatic code generation:

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-parcelize")
}

// Simple data class
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

// Nested objects
@Parcelize
data class UserProfile(
    val user: User,
    val address: Address,
    val tags: List<String>
) : Parcelable
```

### Passing Data Between Components

```kotlin
// Sending
val user = User(1, "John", "john@example.com")
startActivity(Intent(this, DetailActivity::class.java).apply {
    putExtra("user", user)
})

// Receiving (type-safe API)
val user = if (Build.VERSION.SDK_INT >= 33) {
    intent.getParcelableExtra("user", User::class.java)
} else {
    intent.getParcelableExtra<User>("user")
}
```

### Custom Serialization with TypeParceler

For types that don't support `Parcelable` (Date, UUID, custom types):

```kotlin
@Parcelize
@TypeParceler<Date, DateParceler>
data class Event(
    val title: String,
    val timestamp: Date
) : Parcelable

object DateParceler : Parceler<Date> {
    override fun create(parcel: Parcel) = Date(parcel.readLong())
    override fun Date.write(parcel: Parcel, flags: Int) = parcel.writeLong(time)
}
```

### Comparison with `Serializable`

| Feature | `Parcelable` | `Serializable` |
|---|---|---|
| Performance | Fast (no reflection) | Slow (uses reflection) |
| Implementation | @Parcelize — minimal | implements `Serializable` |
| Android optimization | Yes (Binder IPC) | No |
| Overhead | Low | High (GC pressure) |

### Limitations and Best Practices

❌ **Avoid**:
- Passing large objects through `Intent` (use ViewModel/`Repository`)
- Circular references (cause StackOverflowError)
- Serializing non-`Parcelable` fields without TypeParceler

✅ **Recommended**:
- Use @Parcelize instead of manual implementation
- Check `Bundle` size before sending (`Bundle.size()`)
- Use `ContentProvider` or files for large data
- Use type-safe retrieval methods on API 33+

### When to Use

- Passing data via `Intent` between Activity/`Fragment`
- `Fragment` arguments (`setArguments(`Bundle`)`)
- Saving state in `onSaveInstanceState`
- Inter-process communication (AIDL, Messenger)

---

## Follow-ups

1. What happens if you exceed the 1MB `Intent` transaction limit?
2. How does `Parcelable` handle nested objects and collections?
3. Can you pass custom non-`Parcelable` types? How?
4. What's the difference between `writeToParcel()` flags PARCELABLE_WRITE_RETURN_VALUE and 0?
5. How to debug TransactionTooLargeException when passing `Parcelable` data?

## References

- [[c-activity]] — `Activity` lifecycle and `Intent` handling
- [[c-service]] — `Service` communication patterns
- [[q-bundle-data-types--android--medium]] — `Bundle` data types and size limits
- [Android `Parcelable`](https://developer.android.com/reference/android/os/`Parcelable`)
- [Kotlin Parcelize Plugin](https://kotlinlang.org/docs/compiler-plugins.html#parcelable-implementations-generator)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-intent--android--easy]] — Understanding `Intent` basics
- [[q-how-to-pass-parameters-to-fragment--android--easy]] — `Fragment` argument passing

### Related (Same Level)
- [[q-what-are-intents-for--android--medium]] — `Intent` use cases and patterns
- [[q-bundle-data-types--android--medium]] — `Bundle` types and limitations
- [[q-what-is-pendingintent--android--medium]] — PendingIntent with `Parcelable`

### Advanced (Harder)
- [[q-fragments-and-activity-relationship--android--hard]] — Complex data flow patterns
- [[q-android-architectural-patterns--android--medium]] — Architecture with data passing
