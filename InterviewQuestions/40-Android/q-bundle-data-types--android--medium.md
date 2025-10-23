---
id: 20251012-122788
title: Bundle Data Types / Типы данных Bundle
aliases:
- Bundle Data Types
- Типы данных Bundle
topic: android
subtopics:
- activity
- fragment
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-manifest-file--android--easy
- q-android-app-components--android--easy
- q-android-project-parts--android--easy
created: 2025-10-15
updated: 2025-10-20
tags:
- android/activity
- android/fragment
- difficulty/medium
---

# Вопрос (RU)
> Типы данных Bundle?

# Question (EN)
> Bundle Data Types?

---

## Ответ (RU)

Bundle используется для передачи данных между компонентами Android (Activity, Fragment, Service). Поддерживает ограниченный набор типов данных.

**Поддерживаемые типы**:
- Примитивы: Int, Long, Float, Double, Boolean, Byte, Char, Short
- Строки: String, CharSequence
- Массивы примитивов: IntArray, LongArray, FloatArray, etc.
- Списки: ArrayList<String>, ArrayList<Int>, etc.
- Parcelable/Serializable объекты
- Bundle (вложенные)

**Пример**:
```kotlin
val bundle = Bundle().apply {
    putString("key_name", "John")
    putInt("key_age", 25)
    putStringArray("key_tags", arrayOf("kotlin", "android"))
}

// Чтение
val name = bundle.getString("key_name")
val age = bundle.getInt("key_age")
```

**Ограничения**:
- Максимальный размер: ~1MB (TransactionTooLargeException)
- Нельзя передавать: функции, активные объекты (Thread, Socket), некоторые системные объекты
- Для больших данных использовать: URI, файлы, ContentProvider, ViewModel

## Answer (EN)

Bundle is used to pass data between Android components (Activity, Fragment, Service). Supports a limited set of data types.

**Supported types**:
- Primitives: Int, Long, Float, Double, Boolean, Byte, Char, Short
- Strings: String, CharSequence
- Primitive arrays: IntArray, LongArray, FloatArray, etc.
- Lists: ArrayList<String>, ArrayList<Int>, etc.
- Parcelable/Serializable objects
- Bundle (nested)

**Example**:
```kotlin
val bundle = Bundle().apply {
    putString("key_name", "John")
    putInt("key_age", 25)
    putStringArray("key_tags", arrayOf("kotlin", "android"))
}

// Reading
val name = bundle.getString("key_name")
val age = bundle.getInt("key_age")
```

**Limitations**:
- Max size: ~1MB (TransactionTooLargeException)
- Cannot pass: functions, live objects (Thread, Socket), some system objects
- For large data use: URI, files, ContentProvider, ViewModel

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
