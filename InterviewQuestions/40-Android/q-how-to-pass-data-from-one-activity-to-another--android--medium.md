---\
id: android-366
title: "How To Pass Data From One Activity To Another / Как передать данные из одной Activity в другую"
aliases: [Intent Extras, Parcelable Android, Pass Data Between Activities, Передача данных между Activity]
topic: android
subtopics: [activity, ui-navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity, q-activity-lifecycle-methods--android--medium, q-android-components-besides-activity--android--easy, q-how-is-navigation-implemented--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [activity, android, android/activity, android/ui-navigation, difficulty/medium, intent, navigation]
sources: []

---\
# Вопрос (RU)

> Как передать данные из одной `Activity` в другую?

# Question (EN)

> How to pass data from one `Activity` to another?

---

## Ответ (RU)

В Android есть несколько способов передачи данных между `Activity`:

### 1. `Intent` Extras (Рекомендуется Для Простых данных)

Для примитивных типов и строк:

```kotlin
// ✅ Отправка
val intent = Intent(this, SecondActivity::class.java).apply {
    putExtra("user_name", "John Doe")
    putExtra("user_age", 25)
}
startActivity(intent)

// ✅ Получение (в SecondActivity)
val name = intent.getStringExtra("user_name")
val age = intent.getIntExtra("user_age", 0)
```

### 2. `Parcelable` (Рекомендуется Для объектов)

Эффективная передача сложных объектов:

```kotlin
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

// ✅ Отправка
val intent = Intent(this, SecondActivity::class.java).apply {
    putExtra("user", user)
}
startActivity(intent)

// ✅ Получение (SecondActivity)
@Suppress("DEPRECATION")
val user: User? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    intent.getParcelableExtra("user", User::class.java)
} else {
    intent.getParcelableExtra("user")
}
```

### 3. `Bundle` (Группировка данных)

```kotlin
// ✅ Отправка
val bundle = Bundle().apply {
    putString("name", "Alice")
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}

val intent = Intent(this, SecondActivity::class.java).apply {
    putExtras(bundle)
}
startActivity(intent)

// ✅ Получение
intent.extras?.let { bundle ->
    val name = bundle.getString("name")
}
```

### 4. `Activity` Result API (Двусторонний обмен)

```kotlin
// ✅ Регистрация лончера (в вызывающей Activity)
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}

// ✅ Запуск SecondActivity
val intent = Intent(this, SecondActivity::class.java)
launcher.launch(intent)
```

```kotlin
// ✅ Возврат результата (во второй Activity перед finish())
val resultIntent = Intent().putExtra("result", "value")
setResult(RESULT_OK, resultIntent)
finish()
```

**Важные ограничения**:

- **Размер `Intent`**: данные передаются через Binder-транзакцию (буфер ~1MB на одну транзакцию, общий для всех данных в ней). На практике рекомендуется держать payload заметно меньше (~500KB), чтобы избежать `TransactionTooLargeException`.
- **Сериализация**: `Parcelable`, как правило, значительно быстрее и более эффективно использует память, чем `Serializable`, и предпочтителен для межпроцессного/межкомпонентного обмена данными.
- **Type safety**: Используйте константы для ключей.

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

**Для больших данных**: Храните их в локальном хранилище (например, Room/DataStore/файл) и передавайте между `Activity` только идентификаторы или ключи.

## Answer (EN)

Android provides several methods for passing data between Activities:

### 1. `Intent` Extras (Recommended for Simple data)

For simple data types:

```kotlin
// ✅ Sending
val intent = Intent(this, SecondActivity::class.java).apply {
    putExtra("user_name", "John Doe")
    putExtra("user_age", 25)
}
startActivity(intent)

// ✅ Receiving (in SecondActivity)
val name = intent.getStringExtra("user_name")
val age = intent.getIntExtra("user_age", 0)
```

### 2. `Parcelable` (Recommended For objects)

Efficient complex object transfer:

```kotlin
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

// ✅ Sending
val intent = Intent(this, SecondActivity::class.java).apply {
    putExtra("user", user)
}
startActivity(intent)

// ✅ Receiving (SecondActivity)
@Suppress("DEPRECATION")
val user: User? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    intent.getParcelableExtra("user", User::class.java)
} else {
    intent.getParcelableExtra("user")
}
```

### 3. `Bundle` (Grouping data)

```kotlin
// ✅ Sending
val bundle = Bundle().apply {
    putString("name", "Alice")
    putStringArrayList("tags", arrayListOf("kotlin", "android"))
}

val intent = Intent(this, SecondActivity::class.java).apply {
    putExtras(bundle)
}
startActivity(intent)

// ✅ Receiving
intent.extras?.let { bundle ->
    val name = bundle.getString("name")
}
```

### 4. `Activity` Result API (Bidirectional)

```kotlin
// ✅ Register launcher (in calling Activity)
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}

// ✅ Launch SecondActivity
val intent = Intent(this, SecondActivity::class.java)
launcher.launch(intent)
```

```kotlin
// ✅ Return result (in SecondActivity before finish())
val resultIntent = Intent().putExtra("result", "value")
setResult(RESULT_OK, resultIntent)
finish()
```

**Key limitations**:

- **`Intent` size**: Data is passed via a Binder transaction (buffer is about 1MB per transaction, shared by all data in it). In practice, keep payloads well below that (around or under ~500KB) to avoid `TransactionTooLargeException`.
- **Serialization**: `Parcelable` is generally significantly faster and more memory-efficient than `Serializable`, and is preferred for component/IPC data transfer.
- **Type safety**: Use constants for keys.

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

**For large data**: Store it in local storage (e.g., Room/DataStore/file) and pass only identifiers or keys between Activities.

---

## Дополнительные Вопросы (RU)

- Каков лимит размера буфера транзакции `Intent`?
- Когда следует использовать `Parcelable` против `Serializable`?
- Как `Navigation Component` обрабатывает передачу аргументов?
- Можно ли передавать между `Activity` объекты, которые нельзя сериализовать?
- Как обрабатывать данные `Intent` в много-процессных приложениях?

## Follow-ups

- What is the `Intent` transaction buffer size limit?
- When should you use `Parcelable` vs `Serializable`?
- How does Navigation `Component` handle argument passing?
- Can you pass non-serializable objects between Activities?
- How to handle `Intent` data in multi-process apps?

## Ссылки (RU)

- [[c-activity]]

## References

- [[c-activity]]
- Official Android documentation: `Intent` and `Intent` Filters

## Связанные Вопросы (RU)

### Предварительные (Проще)
- [[q-android-components-besides-activity--android--easy]]

### Связанные (Средний уровень)
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-how-is-navigation-implemented--android--medium]]
- [[q-single-activity-pros-cons--android--medium]]

### Продвинутые (Сложнее)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]]

### Related (Same Level)
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-how-is-navigation-implemented--android--medium]]
- [[q-single-activity-pros-cons--android--medium]]

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]
