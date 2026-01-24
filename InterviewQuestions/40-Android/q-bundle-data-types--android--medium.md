---
id: android-387
title: Типы данных Bundle / Bundle Data Types
aliases:
- Bundle Data Types
- Типы данных Bundle
topic: android
subtopics:
- serialization
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity
- q-android-app-components--android--easy
- q-data-sync-unstable-network--android--hard
- q-foreground-service-types--android--medium
- q-parcelable-implementation--android--medium
- q-what-is-layout-types-and-when-to-use--android--easy
created: 2024-10-15
updated: 2025-11-10
sources: []
tags:
- android/serialization
- difficulty/medium
anki_cards:
- slug: android-387-0-en
  language: en
  anki_id: 1768364992400
  synced_at: '2026-01-23T16:45:06.308192'
- slug: android-387-0-ru
  language: ru
  anki_id: 1768364992423
  synced_at: '2026-01-23T16:45:06.309071'
---
# Вопрос (RU)
> Какие типы данных поддерживает `Bundle`?

# Question (EN)
> What data types does `Bundle` support?

---

## Ответ (RU)

`Bundle` — это контейнер «ключ-значение» для передачи данных между компонентами Android (например, аргументы `Activity`/`Fragment`, `savedInstanceState`, extras `Intent`, IPC). Он построен поверх `Parcel` и предоставляет типизированные методы `put*/get*`.

**Основные устойчиво поддерживаемые типы** (API 34+, не исчерпывающий список, но ключевые категории для безопасного использования, особенно при IPC):
- Примитивы и массивы:
  - `boolean`, `byte`, `char`, `short`, `int`, `long`, `float`, `double`
  - `boolean[]`, `byte[]`, `char[]`, `short[]`, `int[]`, `long[]`, `float[]`, `double[]`
- Строки и текст:
  - `String`, `String[]`
  - `CharSequence`, `CharSequence[]`
- Коллекции (для отдельных поддерживаемых типов элементов):
  - `ArrayList<String>`
  - `ArrayList<CharSequence>`
  - `ArrayList<Integer>` (через `putIntegerArrayList`)
  - `ArrayList<Parcelable>` (через `putParcelableArrayList`)
- Объекты:
  - `Parcelable`
  - `Parcelable[]`
  - `Serializable` (включая массивы/коллекции, если сами объекты реализуют `Serializable`; используется, но менее предпочтителен по производительности)
- Специальные типы:
  - вложенный `Bundle`
  - `SparseArray<Parcelable>` (через `putSparseParcelableArray`)

(Другие типы нужно конвертировать в поддерживаемую форму или реализовать `Parcelable`/`Serializable`, чтобы корректно сохранять в `Bundle`, особенно если данные должны пережить процесс или пройти через IPC.)

**Базовое использование**:
```kotlin
// ✅ API типизирован по имени метода, что снижает риск ClassCastException:
// используйте согласованные пары put*/get* для одного и того же ключа.
val bundle = Bundle().apply {
    putString("user_id", "12345")
    putInt("count", 42)
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}

// ✅ Безопасное чтение со значениями по умолчанию
val count = bundle.getInt("count", 0)
val userId = bundle.getString("user_id") // String?
```

**`Parcelable` vs `Serializable`**:
```kotlin
@Parcelize
data class Profile(val id: String, val name: String) : Parcelable

// ✅ Parcelable: оптимизирован под Android, без рефлексии, обычно заметно быстрее Serializable
bundle.putParcelable("profile", Profile("1", "Alice"))

// ⚠️ Serializable: использует рефлексию, обычно медленнее и менее эффективен по памяти;
// поддерживается, но считается менее предпочтительным и может быть менее предсказуем при IPC
bundle.putSerializable("data", hashMapOf("key" to "value"))
```

**Коллекции и массивы**:
```kotlin
// ✅ Типизированные коллекции для Parcelable
val profiles = arrayListOf(Profile("1", "Alice"), Profile("2", "Bob"))
bundle.putParcelableArrayList("profiles", profiles)

// ✅ SparseArray для int-ключей (более эффективен по памяти)
val sparse = SparseArray<Profile>().apply {
    put(1, Profile("1", "Alice"))
    put(2, Profile("2", "Bob"))
}
bundle.putSparseParcelableArray("sparse_profiles", sparse)
```

**Критические ограничения**:
- Размер: ориентировочно около 1MB на одну транзакцию `Binder` (включая служебные данные); превышение может привести к `TransactionTooLargeException`.
- Нельзя класть объекты, не являющиеся `Parcelable` или `Serializable`, такие как `Context`, `View`, `Thread`, `Handler`, `Socket` и т.п. Это приводит к ошибкам выполнения или утечкам/некорректному поведению.
- Альтернативы для больших данных: `Uri`, файлы, `ViewModel`, `WorkManager`, `ContentProvider`.
- `Bundle` не является потокобезопасным без явной синхронизации.

**Безопасность**:
```kotlin
// ❌ Опасно: использовать внешние extras без проверки
val intent = getIntent()
val untrusted = intent.getStringExtra("url") // может содержать произвольные потенциально опасные данные

// ✅ Пример простой валидации:
val url = intent.getStringExtra("url")
    ?.takeIf { it.startsWith("https://") }
    ?: return
```

## Answer (EN)

`Bundle` is a key-value container for passing data between Android components (e.g., `Activity`/`Fragment` arguments, `savedInstanceState`, `Intent` extras, and IPC). It is built on top of `Parcel` and exposes typed `put*/get*` methods.

**Main reliably supported types** (API 34+, not exhaustive, but key categories recommended for safe use, especially across IPC):
- Primitives and arrays:
  - `boolean`, `byte`, `char`, `short`, `int`, `long`, `float`, `double`
  - `boolean[]`, `byte[]`, `char[]`, `short[]`, `int[]`, `long[]`, `float[]`, `double[]`
- Strings and text:
  - `String`, `String[]`
  - `CharSequence`, `CharSequence[]`
- Collections (for specific element types):
  - `ArrayList<String>`
  - `ArrayList<CharSequence>`
  - `ArrayList<Integer>` (via `putIntegerArrayList`)
  - `ArrayList<Parcelable>` (via `putParcelableArrayList`)
- Objects:
  - `Parcelable`
  - `Parcelable[]`
  - `Serializable` (including arrays/collections when elements implement `Serializable`; supported but less preferred due to performance)
- Special:
  - nested `Bundle`
  - `SparseArray<Parcelable>` (via `putSparseParcelableArray`)

(Other types must be converted to supported forms or implement `Parcelable`/`Serializable` to be stored correctly, especially if data must survive process death or cross-process boundaries.)

**Basic usage**:
```kotlin
// ✅ The API is typed per method name, reducing ClassCastException risk:
// use matching put*/get* pairs for the same key.
val bundle = Bundle().apply {
    putString("user_id", "12345")
    putInt("count", 42)
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}

// ✅ Safe reading with defaults
val count = bundle.getInt("count", 0)
val userId = bundle.getString("user_id") // String?
```

**`Parcelable` vs `Serializable`**:
```kotlin
@Parcelize
data class Profile(val id: String, val name: String) : Parcelable

// ✅ Parcelable: Android-optimized, no reflection, typically significantly faster than Serializable
bundle.putParcelable("profile", Profile("1", "Alice"))

// ⚠️ Serializable: uses reflection, often slower and less memory-efficient;
// supported but generally discouraged in performance-sensitive or IPC-heavy paths
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
- Size: approximately 1 MB per `Binder` transaction (including overhead); going beyond this can cause `TransactionTooLargeException`.
- Do not put objects that are not `Parcelable` or `Serializable`, such as `Context`, `View`, `Thread`, `Handler`, `Socket`, etc. Doing so either fails at runtime or leads to leaks/incorrect behavior.
- Alternatives for large payloads: `Uri`, files, `ViewModel`, `WorkManager`, `ContentProvider`.
- `Bundle` is not thread-safe without explicit synchronization.

**Security**:
```kotlin
// ❌ Dangerous: using external extras without validation
val intent = getIntent()
val untrusted = intent.getStringExtra("url") // can contain arbitrary, potentially unsafe data

// ✅ Example of simple validation:
val url = intent.getStringExtra("url")
    ?.takeIf { it.startsWith("https://") }
    ?: return
```

## Дополнительные Вопросы (RU)

- Как оценить размер `Bundle` и риск `TransactionTooLargeException` при IPC?
- В чем внутренние различия между сериализацией в `Parcel` и хранением данных в `Bundle`?
- Как `Bundle` ведет себя при изменении полей в `Parcelable` (добавление/удаление) с точки зрения совместимости?
- Почему нельзя класть `Context` и `View` в `Bundle` и какие утечки памяти это может вызвать?
- Как Navigation `Component` Safe Args генерирует типобезопасные обертки над `Bundle` на этапе компиляции?

## Follow-ups

- How does `Bundle` size calculation work and how to measure it before IPC?
- What's the internal difference between Parcel and `Bundle` serialization mechanisms?
- How does `Bundle` handle versioning when adding/removing fields in `Parcelable` objects?
- Why are `Context` and `View` references forbidden in `Bundle`, and what are memory leak implications?
- How does Navigation `Component`'s Safe Args generate type-safe `Bundle` accessors at compile time?

## Ссылки (RU)

- https://developer.android.com/reference/android/os/Bundle
- https://developer.android.com/reference/android/os/Parcelable
- https://developer.android.com/guide/components/intents-filters

## References

- https://developer.android.com/reference/android/os/Bundle
- https://developer.android.com/reference/android/os/Parcelable
- https://developer.android.com/guide/components/intents-filters

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-activity]]

### Предпосылки (проще)
- [[q-android-app-components--android--easy]] — понимание компонентов приложения и их связи

### Похожие (того Же уровня)
- [[q-parcelable-implementation--android--medium]] — реализация собственных `Parcelable` объектов

### Продвинутые (сложнее)
- Анализ и отладка `TransactionTooLargeException` и лимитов IPC
- Стратегии версионирования `Parcelable` и обеспечения обратной совместимости

## Related Questions

### Prerequisites / Concepts

- [[c-activity]]

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — Understanding app components and their relations

### Related (Same Level)
- [[q-parcelable-implementation--android--medium]] — Custom `Parcelable` objects

### Advanced (Harder)
- TransactionTooLargeException debugging and IPC size limits
- `Parcelable` versioning and backward compatibility strategies
