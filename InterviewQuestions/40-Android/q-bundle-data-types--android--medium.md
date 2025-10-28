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
status: draft
moc: moc-android
related:
  - q-android-app-components--android--easy
  - q-android-manifest-file--android--easy
  - q-android-project-parts--android--easy
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/activity, android/fragment, difficulty/medium]
---
# Вопрос (RU)
> Какие типы данных поддерживает Bundle?

# Question (EN)
> What data types does Bundle support?

---

## Ответ (RU)

Bundle передает данные между компонентами Android (Activity, Fragment, Service). Поддерживает ограниченный набор сериализуемых типов.

**Поддерживаемые типы**:
- Примитивы: Int, Long, Float, Double, Boolean, Byte, Char, Short
- Строки: String, CharSequence
- Массивы: IntArray, StringArray, и другие примитивные массивы
- Коллекции: ArrayList<String>, ArrayList<Int>, ArrayList<Parcelable>
- Parcelable/Serializable объекты
- Bundle (вложенные)

**Пример базового использования**:
```kotlin
// ✅ Передача примитивов и строк
val bundle = Bundle().apply {
    putString("name", "John")
    putInt("age", 25)
    putBoolean("isPremium", true)
}

// ✅ Чтение с значениями по умолчанию
val age = bundle.getInt("age", 0)
val name = bundle.getString("name") // nullable
```

**Parcelable (рекомендуется)**:
```kotlin
@Parcelize
data class User(val id: Long, val name: String) : Parcelable

// ✅ Передача Parcelable объектов
bundle.putParcelable("user", User(1, "Alice"))
val user = bundle.getParcelable<User>("user")
```

**Критические ограничения**:
- Лимит размера: ~1MB (TransactionTooLargeException при превышении)
- Запрещено: лямбды, Thread, Socket, Context, View
- Для больших данных: используйте URI, ViewModel, файлы, ContentProvider

## Answer (EN)

Bundle passes data between Android components (Activity, Fragment, Service). Supports a limited set of serializable types.

**Supported types**:
- Primitives: Int, Long, Float, Double, Boolean, Byte, Char, Short
- Strings: String, CharSequence
- Arrays: IntArray, StringArray, and other primitive arrays
- Collections: ArrayList<String>, ArrayList<Int>, ArrayList<Parcelable>
- Parcelable/Serializable objects
- Bundle (nested)

**Basic usage example**:
```kotlin
// ✅ Passing primitives and strings
val bundle = Bundle().apply {
    putString("name", "John")
    putInt("age", 25)
    putBoolean("isPremium", true)
}

// ✅ Reading with default values
val age = bundle.getInt("age", 0)
val name = bundle.getString("name") // nullable
```

**Parcelable (recommended)**:
```kotlin
@Parcelize
data class User(val id: Long, val name: String) : Parcelable

// ✅ Passing Parcelable objects
bundle.putParcelable("user", User(1, "Alice"))
val user = bundle.getParcelable<User>("user")
```

**Critical limitations**:
- Size limit: ~1MB (TransactionTooLargeException when exceeded)
- Forbidden: lambdas, Thread, Socket, Context, View
- For large data: use URI, ViewModel, files, ContentProvider

## Follow-ups

- How to detect TransactionTooLargeException before it crashes?
- When to prefer Parcelable vs Serializable for custom objects?
- How to pass large images between Activities safely?
- What happens to Bundle data on configuration changes?
- How does Navigation Component's Safe Args improve type safety?

## References

- [[c-service]]
- https://developer.android.com/reference/android/os/Bundle
- https://developer.android.com/reference/android/os/Parcelable
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
