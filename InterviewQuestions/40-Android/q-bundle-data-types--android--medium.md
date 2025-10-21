---
id: 20251012-122788
title: Bundle Data Types / Типы данных Bundle
aliases: [Bundle Data Types, Типы данных Bundle]
topic: android
subtopics: [activity, fragment]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-android-manifest-file--android--easy, q-android-app-components--android--easy, q-android-project-parts--android--easy]
created: 2025-10-15
updated: 2025-10-20
tags: [android/activity, android/fragment, data-passing, intent, bundle, difficulty/medium]
---

# Вопрос (RU)
> Что можно класть в `Bundle` и какие есть ограничения/лучшие практики?

# Question (EN)
> What can you put into a `Bundle`, and what are the limits/best practices?

---

## Ответ (RU)

### Что такое `Bundle`
- Контейнер «ключ → значение» для передачи данных между `Activity`/`Fragment`/`Service`.
- Используется в `Intent` (`putExtras`) и `Fragment.arguments`.

### Поддерживаемые типы (основное)
- Примитивы и их массивы: `int/long/short/byte/boolean/char/float/double` + соответствующие `*Array`.
- Строки: `String`, `CharSequence`, массивы/`ArrayList<String|CharSequence>`.
- `Parcelable` (рекомендуется) и `Serializable` (медленнее).
- Вложенные `Bundle`, `Binder`, `Size/SizeF`, и др. типы платформы.

### Минимальные примеры
```kotlin
val b = Bundle()
b.putString("name", "Alice")
b.putInt("age", 25)
val name = b.getString("name")
val age = b.getInt("age")
```

```kotlin
@Parcelize
data class User(val id: String, val name: String) : Parcelable

val b = Bundle().apply { putParcelable("user", User("1", "Alice")) }
// Android 13+ (type‑safe)
val u = b.getParcelable("user", User::class.java)
```

### Ограничения и рекомендации
- Лимит размера транзакции ~1MB: не кладите большие объекты (битмапы/файлы) → передавайте `Uri`/путь/ID.
- Предпочитайте `Parcelable` вместо `Serializable` (быстрее/меньше аллокаций).
- Не кладите сложные/тяжелые объекты: `Context`, `ViewModel`, соединения БД.
- Для общих данных между фрагментами используйте `ViewModel`/хранилище, а в `Bundle` передавайте только ключ/ID.

## Answer (EN)

### What is a `Bundle`
- Key–value container for passing data across `Activity`/`Fragment`/`Service`.
- Used in `Intent` (`putExtras`) and `Fragment.arguments`.

### Supported types (essentials)
- Primitives and arrays: `int/long/short/byte/boolean/char/float/double` + matching `*Array`.
- Strings: `String`, `CharSequence`, arrays/`ArrayList<String|CharSequence>`.
- `Parcelable` (recommended) and `Serializable` (slower).
- Nested `Bundle`, `Binder`, `Size/SizeF`, and other platform types.

### Minimal examples
```kotlin
val b = Bundle()
b.putString("name", "Alice")
b.putInt("age", 25)
val name = b.getString("name")
val age = b.getInt("age")
```

```kotlin
@Parcelize
data class User(val id: String, val name: String) : Parcelable

val b = Bundle().apply { putParcelable("user", User("1", "Alice")) }
// Android 13+ (type‑safe)
val u = b.getParcelable("user", User::class.java)
```

### Limits and best practices
- Transaction size ~1MB: avoid large objects (bitmaps/files) → pass `Uri`/path/ID instead.
- Prefer `Parcelable` over `Serializable` (faster/less memory).
- Do not put heavy/complex objects: `Context`, `ViewModel`, DB connections.
- For shared state between Fragments use `ViewModel`/store; put only keys/IDs into `Bundle`.

---

## Follow-ups
- How to pass large images/files safely (URIs, cache files, ContentProvider)?
- When to choose `Parcelable` vs `Serializable` in legacy code?
- How to use Safe Args (Navigation) to enforce type safety?

## References
- https://developer.android.com/reference/android/os/Bundle
- https://developer.android.com/guide/components/intents-filters
- https://developer.android.com/guide/fragments/communicate

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-android-project-parts--android--easy]]

### Advanced (Harder)
- [[q-android-modularization--android--medium]]
