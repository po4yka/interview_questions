---
id: android-387
title: Bundle Data Types / Типы данных Bundle
aliases:
- Bundle Data Types
- Типы данных Bundle
topic: android
subtopics:
- intents-deeplinks
- serialization
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-activity
- c-intent
- q-android-app-components--android--easy
- q-parcelable-implementation--android--medium
created: 2025-10-15
updated: 2025-11-02
sources: []
tags:
- android/intents-deeplinks
- android/serialization
- difficulty/medium
---

# Вопрос (RU)
> Какие типы данных поддерживает `Bundle`?

# Question (EN)
> What data types does `Bundle` support?

---

## Ответ (RU)

`Bundle` — key-value контейнер для передачи данных между компонентами Android через IPC. Основан на `Parcel`, использует типизированные методы `put*/get*`.

**Поддерживаемые типы**:
- Примитивы и массивы: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Byte`, `Char`, `Short` и их массивы
- Строки: `String`, `CharSequence`
- Коллекции: `ArrayList<`String`>`, `ArrayList<`Int`>`, `ArrayList<`Parcelable`>`
- Объекты: `Parcelable`, `Serializable`
- Специальные: `Bundle` (вложенные), `SparseArray<`Parcelable`>`

**Базовое использование**:
```kotlin
// ✅ Type-safe API предотвращает ошибки каста
val bundle = Bundle().apply {
    putString("user_id", "12345")
    putInt("count", 42)
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}

// ✅ Безопасное чтение с default значениями
val count = bundle.getInt("count", 0)
val userId = bundle.getString("user_id") // String?
```

**`Parcelable` vs `Serializable`**:
```kotlin
@Parcelize
data class Profile(val id: String, val name: String) : Parcelable

// ✅ Parcelable: fast, no reflection, Android-оптимизирован
bundle.putParcelable("profile", Profile("1", "Alice"))

// ❌ Serializable: медленнее в 10x, рефлексия, legacy
bundle.putSerializable("data", hashMapOf("key" to "value"))
```

**Коллекции и массивы**:
```kotlin
// ✅ Typed collections для Parcelable
val profiles = arrayListOf(Profile("1", "Alice"), Profile("2", "Bob"))
bundle.putParcelableArrayList("profiles", profiles)

// ✅ SparseArray для int ключей (экономия памяти)
val sparse = SparseArray<Profile>().apply {
    put(1, Profile("1", "Alice"))
    put(2, Profile("2", "Bob"))
}
bundle.putSparseParcelableArray("sparse_profiles", sparse)
```

**Критические ограничения**:
- Размер: ~1MB для IPC через `Binder` (`TransactionTooLargeException`)
- Запрещено: `lambda`, `Thread`, `Socket`, `Context`, `View`, `Handler`
- Альтернативы для больших данных: `URI`, `ViewModel`, files, `WorkManager`, `ContentProvider`
- Не thread-safe без явной синхронизации

**Безопасность**:
```kotlin
// ❌ Опасно: внешние данные без проверки
val intent = getIntent()
val untrusted = intent.getStringExtra("url") // может быть "javascript:..."

// ✅ Валидация перед использованием
val url = intent.getStringExtra("url")
    ?.takeIf { it.startsWith("https://") }
    ?: return
```

## Answer (EN)

`Bundle` is a key-value container for passing data between Android components via IPC. Built on `Parcel`, uses type-safe `put*/get*` methods.

**Supported types**:
- Primitives and arrays: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Byte`, `Char`, `Short` and their arrays
- Strings: `String`, `CharSequence`
- Collections: `ArrayList<`String`>`, `ArrayList<`Int`>`, `ArrayList<`Parcelable`>`
- Objects: `Parcelable`, `Serializable`
- Special: `Bundle` (nested), `SparseArray<`Parcelable`>`

**Basic usage**:
```kotlin
// ✅ Type-safe API prevents cast errors
val bundle = Bundle().apply {
    putString("user_id", "12345")
    putInt("count", 42)
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}

// ✅ Safe reading with default values
val count = bundle.getInt("count", 0)
val userId = bundle.getString("user_id") // String?
```

**`Parcelable` vs `Serializable`**:
```kotlin
@Parcelize
data class Profile(val id: String, val name: String) : Parcelable

// ✅ Parcelable: fast, no reflection, Android-optimized
bundle.putParcelable("profile", Profile("1", "Alice"))

// ❌ Serializable: 10x slower, uses reflection, legacy
bundle.putSerializable("data", hashMapOf("key" to "value"))
```

**Collections and arrays**:
```kotlin
// ✅ Typed collections for Parcelable
val profiles = arrayListOf(Profile("1", "Alice"), Profile("2", "Bob"))
bundle.putParcelableArrayList("profiles", profiles)

// ✅ SparseArray for int keys (memory efficient)
val sparse = SparseArray<Profile>().apply {
    put(1, Profile("1", "Alice"))
    put(2, Profile("2", "Bob"))
}
bundle.putSparseParcelableArray("sparse_profiles", sparse)
```

**Critical limitations**:
- Size: ~1MB for IPC via `Binder` (`TransactionTooLargeException`)
- Forbidden: `lambda`, `Thread`, `Socket`, `Context`, `View`, `Handler`
- Alternatives for large data: `URI`, `ViewModel`, files, `WorkManager`, `ContentProvider`
- Not thread-safe without explicit synchronization

**Security**:
```kotlin
// ❌ Dangerous: external data without validation
val intent = getIntent()
val untrusted = intent.getStringExtra("url") // could be "javascript:..."

// ✅ Validate before use
val url = intent.getStringExtra("url")
    ?.takeIf { it.startsWith("https://") }
    ?: return
```

## Follow-ups

- How does `Bundle` size calculation work and how to measure it before IPC?
- What's the internal difference between Parcel and `Bundle` serialization mechanisms?
- How does `Bundle` handle versioning when adding/removing fields in `Parcelable` objects?
- Why are `Context` and `View` references forbidden in `Bundle`, and what are memory leak implications?
- How does Navigation Component's Safe Args generate type-safe `Bundle` accessors at compile time?

## References

- https://developer.android.com/reference/android/os/`Bundle`
- https://developer.android.com/reference/android/os/`Parcelable`
- https://developer.android.com/guide/components/intents-filters

## Related Questions

### Prerequisites / Concepts

- [[c-activity]]
- [[c-intent]]


### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — Understanding Activity/`Fragment` lifecycle
- [[q-android-manifest-file--android--easy]] — Component declaration and intent filters

### Related (Same Level)
- [[q-parcelable-implementation--android--medium]] — Custom `Parcelable` objects
- `Intent` extras and deep linking patterns
- `ViewModel` state preservation via SavedStateHandle

### Advanced (Harder)
- TransactionTooLargeException debugging and IPC size limits
- `Parcelable` versioning and backward compatibility strategies
