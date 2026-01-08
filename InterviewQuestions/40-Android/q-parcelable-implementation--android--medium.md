---\
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
updated: 2025-11-10
tags: [android/intents-deeplinks, android/performance-memory, android/serialization, bundle, difficulty/medium, ipc, parcelable]
sources: ["https://developer.android.com/reference/android/os/Parcelable", "https://kotlinlang.org/docs/compiler-plugins.html#parcelable-implementations-generator"]

---\
# Вопрос (RU)

> Что вы знаете о `Parcelable`?

# Question (EN)

> What do you know about `Parcelable`?

---

## Ответ (RU)

**`Parcelable`** — это Android интерфейс для эффективной сериализации объектов при передаче между компонентами приложения (`Activity`, `Fragment`, `Service`). Оптимизирован для IPC (межпроцессного взаимодействия) и как правило значительно быстрее Java `Serializable` благодаря отсутствию рефлексии и работе с `Parcel` на более низком уровне.

### Ключевые Характеристики

- **Производительность**: Обычно гораздо быстрее `Serializable`, записывает данные напрямую в Parcel без рефлексии
- **IPC-оптимизация**: Используется для передачи данных через Binder при взаимодействии между процессами
- **Ограничение размера**: Транзакции Binder (включая данные в `Intent`/`Bundle`) ограничены ~1MB (TransactionTooLargeException)

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

// Подразумевается, что Address тоже реализует Parcelable
@Parcelize
data class Address(
    val city: String,
    val street: String
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

// Получение (type-safe API по сигнатуре метода)
val user = if (Build.VERSION.SDK_INT >= 33) {
    intent.getParcelableExtra("user", User::class.java)
} else {
    @Suppress("DEPRECATION")
    intent.getParcelableExtra<User>("user")
}
```

### Кастомная Сериализация С TypeParceler

Для типов, не поддерживающих `Parcelable` (Date, UUID, кастомные типы):

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
| Производительность | Быстрый (без рефлексии, оптимизирован под Android) | Медленнее (рефлексия, дополнительный overhead) |
| Реализация | @Parcelize — минимальный шаблонный код | implements `Serializable` |
| Android-оптимизация | Да (Binder IPC, `Bundle`/`Intent`) | Нет |
| Overhead | Низкий | Более высокий (GC pressure) |

### Ограничения И Best Practices

❌ **Избегать**:
- Передачи больших объектов через `Intent`/`Bundle` (используйте `ViewModel`/Repository, передавайте идентификаторы и загружайте данные по месту)
- Сложных графов объектов и избыточных ссылок, которые усложняют сериализацию и могут привести к ошибкам или лишнему потреблению памяти
- Сериализации non-`Parcelable` полей без TypeParceler или другой явной стратегии

✅ **Рекомендуется**:
- Использовать @Parcelize вместо ручной реализации, когда это возможно
- Минимизировать размер передаваемых `Bundle`/`Intent` extras; для больших данных использовать альтернативы (например, `ContentProvider`, файлы, БД)
- Использовать type-safe методы получения на API 33+ (`getParcelableExtra(key, Class)`, `getParcelableArrayListExtra(key, Class)`)

### Когда Использовать

- Передача данных через `Intent` между `Activity`
- Аргументы `Fragment` (`setArguments(``Bundle``)` / Safe Args)
- Сохранение состояния в `onSaveInstanceState`
- Межпроцессное взаимодействие (AIDL, Messenger), где AIDL типы должны быть `Parcelable`

## Answer (EN)

**`Parcelable`** is an Android interface for efficient object serialization when passing data between app components (`Activity`, `Fragment`, `Service`). It is optimized for IPC and is typically significantly faster than Java `Serializable` by avoiding reflection and working directly with a Parcel.

### Key Characteristics

- **Performance**: Typically much faster than `Serializable`, writes directly to Parcel without reflection
- **IPC Optimization**: Used for data transfer over Binder in cross-process communication
- **Size Limitation**: Binder transactions (including `Intent`/`Bundle` extras) are limited to about 1MB (TransactionTooLargeException)

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

// Assume Address also implements Parcelable
@Parcelize
data class Address(
    val city: String,
    val street: String
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

// Receiving (type-safe by method signature)
val user = if (Build.VERSION.SDK_INT >= 33) {
    intent.getParcelableExtra("user", User::class.java)
} else {
    @Suppress("DEPRECATION")
    intent.getParcelableExtra<User>("user")
}
```

### Custom Serialization with TypeParceler

For types that don't support `Parcelable` directly (Date, UUID, custom types):

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
| Performance | Fast (no reflection, Android-optimized) | Slower (uses reflection, more overhead) |
| Implementation | Minimal boilerplate with @Parcelize | Simple marker interface |
| Android optimization | Yes (Binder IPC, `Bundle`/`Intent` integration) | No |
| Overhead | Low | Higher (GC pressure) |

### Limitations and Best Practices

❌ **Avoid**:
- Passing large objects via `Intent`/`Bundle` (use `ViewModel`/Repository, pass IDs and load data on demand instead)
- Overly complex object graphs and excessive references that complicate serialization and increase memory usage
- Serializing non-`Parcelable` fields without TypeParceler or another explicit strategy

✅ **Recommended**:
- Prefer @Parcelize over manual `Parcelable` implementation when possible
- Keep `Bundle`/`Intent` extras small; use alternatives (`ContentProvider`, files, database) for large data
- Use type-safe retrieval methods on API 33+ (`getParcelableExtra(key, Class)`, `getParcelableArrayListExtra(key, Class)`)

### When to Use

- Passing data via `Intent` between Activities
- `Fragment` arguments (`setArguments(``Bundle``)` / Safe Args)
- Saving state in `onSaveInstanceState`
- Inter-process communication (AIDL, Messenger), where AIDL types must be `Parcelable`

---

## Дополнительные Вопросы (RU)

1. Что произойдет, если превысить лимит ~1MB для транзакции Binder при передаче `Parcelable` через `Intent`/`Bundle`?
2. Как `Parcelable` (c `@Parcelize`) обрабатывает вложенные объекты и коллекции?
3. Можно ли передавать кастомные типы, не реализующие `Parcelable`? Как это сделать (например, через `TypeParceler` или ручную реализацию чтения/записи)?
4. В чем разница между флагами `writeToParcel()` `PARCELABLE_WRITE_RETURN_VALUE` и `0`?
5. Как отлаживать `TransactionTooLargeException` при передаче `Parcelable` данных?

## Follow-ups

1. What happens if you exceed the 1MB Binder transaction limit when using `Parcelable` in an `Intent`/`Bundle`?
2. How does `Parcelable` handle nested objects and collections with @Parcelize?
3. Can you pass custom non-`Parcelable` types? How (e.g., using TypeParceler or manual write/read)?
4. What's the difference between `writeToParcel()` flags `PARCELABLE_WRITE_RETURN_VALUE` and `0`?
5. How to debug TransactionTooLargeException when passing `Parcelable` data?

## References

- [[c-activity]] — `Activity` lifecycle and `Intent` handling
- [[c-service]] — `Service` communication patterns
- [[q-bundle-data-types--android--medium]] — `Bundle` data types and size limits
- [Android `Parcelable`](https://developer.android.com/reference/android/os/Parcelable)
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
