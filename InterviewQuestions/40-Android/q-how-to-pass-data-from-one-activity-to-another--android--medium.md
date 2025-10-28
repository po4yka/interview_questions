---
id: 20251012-1227188
title: "How To Pass Data From One Activity To Another / Как передать данные из одной Activity в другую"
aliases: [Pass Data Between Activities, Передача данных между Activity, Intent Extras, Parcelable Android]
topic: android
subtopics: [activity, intent, navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-components-besides-activity--android--easy, q-activity-lifecycle-methods--android--medium, q-how-is-navigation-implemented--android--medium]
created: 2025-10-15
updated: 2025-10-28
tags: [android, android/activity, android/intent, android/navigation, activity, intent, navigation, difficulty/medium]
sources: []
---

# Вопрос (RU)

> Как передать данные из одной Activity в другую?

# Question (EN)

> How to pass data from one Activity to another?

---

## Ответ (RU)

В Android есть несколько способов передачи данных между Activity:

### 1. Intent Extras (Рекомендуется для простых данных)

Для примитивных типов и строк:

```kotlin
// ✅ Отправка
val intent = Intent(this, SecondActivity::class.java).apply {
    putExtra("user_name", "John Doe")
    putExtra("user_age", 25)
}
startActivity(intent)

// ✅ Получение
val name = intent.getStringExtra("user_name")
val age = intent.getIntExtra("user_age", 0)
```

### 2. Parcelable (Рекомендуется для объектов)

Эффективная передача сложных объектов:

```kotlin
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

// ✅ Отправка
intent.putExtra("user", user)

// ✅ Получение (API 33+)
val user = intent.getParcelableExtra("user", User::class.java)
```

### 3. Bundle (Группировка данных)

```kotlin
// ✅ Отправка
val bundle = Bundle().apply {
    putString("name", "Alice")
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}
intent.putExtras(bundle)

// ✅ Получение
intent.extras?.let { bundle ->
    val name = bundle.getString("name")
}
```

### 4. Activity Result API (Двусторонний обмен)

```kotlin
// ✅ Регистрация лончера
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}

// ✅ Запуск Activity
launcher.launch(intent)

// ✅ Возврат результата
setResult(RESULT_OK, Intent().putExtra("result", "value"))
finish()
```

**Важные ограничения**:

- **Размер Intent**: До ~500KB (транзакционный буфер 1MB для всех транзакций)
- **Сериализация**: Parcelable быстрее Serializable в ~10 раз
- **Type safety**: Используйте константы для ключей

```kotlin
// ❌ Без type safety
intent.putExtra("usr_nm", name)
val name = intent.getStringExtra("user_name") // Опечатка!

// ✅ С type safety
object Keys {
    const val USER_NAME = "user_name"
}
intent.putExtra(Keys.USER_NAME, name)
```

**Для больших данных**: Используйте Room/DataStore и передавайте только ID.

## Answer (EN)

Android provides several methods for passing data between Activities:

### 1. Intent Extras (Recommended for primitives)

For simple data types:

```kotlin
// ✅ Sending
val intent = Intent(this, SecondActivity::class.java).apply {
    putExtra("user_name", "John Doe")
    putExtra("user_age", 25)
}
startActivity(intent)

// ✅ Receiving
val name = intent.getStringExtra("user_name")
val age = intent.getIntExtra("user_age", 0)
```

### 2. Parcelable (Recommended for objects)

Efficient complex object transfer:

```kotlin
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

// ✅ Sending
intent.putExtra("user", user)

// ✅ Receiving (API 33+)
val user = intent.getParcelableExtra("user", User::class.java)
```

### 3. Bundle (Grouping data)

```kotlin
// ✅ Sending
val bundle = Bundle().apply {
    putString("name", "Alice")
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}
intent.putExtras(bundle)

// ✅ Receiving
intent.extras?.let { bundle ->
    val name = bundle.getString("name")
}
```

### 4. Activity Result API (Bidirectional)

```kotlin
// ✅ Register launcher
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}

// ✅ Launch Activity
launcher.launch(intent)

// ✅ Return result
setResult(RESULT_OK, Intent().putExtra("result", "value"))
finish()
```

**Key limitations**:

- **Intent size**: Up to ~500KB (1MB transaction buffer for all transactions)
- **Serialization**: Parcelable is ~10x faster than Serializable
- **Type safety**: Use constants for keys

```kotlin
// ❌ Without type safety
intent.putExtra("usr_nm", name)
val name = intent.getStringExtra("user_name") // Typo!

// ✅ With type safety
object Keys {
    const val USER_NAME = "user_name"
}
intent.putExtra(Keys.USER_NAME, name)
```

**For large data**: Use Room/DataStore and pass only IDs.

---

## Follow-ups

- What is the Intent transaction buffer size limit?
- When should you use Parcelable vs Serializable?
- How does Navigation Component handle argument passing?
- Can you pass non-serializable objects between Activities?
- How to handle Intent data in multi-process apps?

## References

- [[c-intent]]
- [[c-parcelable]]
- [[c-activity-lifecycle]]
- Official Android documentation: Intent and Intent Filters

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]]

### Related (Same Level)
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-how-is-navigation-implemented--android--medium]]
- [[q-single-activity-pros-cons--android--medium]]

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]
