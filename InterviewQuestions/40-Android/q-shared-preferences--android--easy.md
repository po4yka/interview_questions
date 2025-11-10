---
id: android-287
title: "SharedPreferences / Хранилище пар ключ-значение"
aliases: ["Shared Preferences", "SharedPreferences", "Хранилище пар ключ-значение"]
topic: android
subtopics: [datastore, files-media]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [q-room-relations-embedded--android--medium]
created: 2023-10-15
updated: 2025-11-10
tags: [android, android/datastore, android/files-media, difficulty/easy]

---

# Вопрос (RU)

> Что такое SharedPreferences и для чего используется?

# Question (EN)

> What is SharedPreferences and what is it used for?

---

## Ответ (RU)

SharedPreferences — это механизм Android для хранения небольших наборов пар ключ-значение (обычно настроек и флагов) в приватном хранилище приложения. Под капотом данные сохраняются в XML-файле во внутреннем хранилище приложения. Данные удаляются при удалении приложения.

См. также: [[q-room-relations-embedded--android--medium]].

### Поддерживаемые Типы Данных

```kotlin
sharedPref.edit {
    putBoolean("is_logged_in", true)
    putInt("user_id", 42)
    putFloat("rating", 4.5f)
    putLong("timestamp", System.currentTimeMillis())
    putString("username", "alice")
    putStringSet("tags", setOf("kotlin", "android"))
}
```

### Получение SharedPreferences

```kotlin
// ✅ Именованные preferences
val prefs = context.getSharedPreferences(
    "app_settings",
    Context.MODE_PRIVATE  // Доступ только вашему приложению
)

// ✅ Activity-scoped preferences
class MainActivity : AppCompatActivity() {
    private val prefs by lazy {
        getPreferences(Context.MODE_PRIVATE)  // Имя файла = имя Activity
    }
}
```

### Запись Данных: apply() Vs commit()

```kotlin
// ✅ apply() — асинхронно записывает изменения на диск, не блокирует вызывающий поток
prefs.edit {
    putString("theme", "dark")
    // apply() вызывается автоматически
}

// ✅ commit() — синхронно записывает изменения на диск, возвращает boolean
val success = prefs.edit()
    .putString("api_key", "xyz123")
    .commit()  // Блокирует поток до завершения записи

if (!success) {
    Log.e("Prefs", "Failed to save")
}
```

**Правило**: Для UI-потока по умолчанию используйте `apply()`; `commit()` — только если нужна гарантия успешной записи до продолжения выполнения.

### Типичный Use Case: Settings Manager

```kotlin
class SettingsManager(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    var isDarkMode: Boolean
        get() = prefs.getBoolean("dark_mode", false)
        set(value) = prefs.edit { putBoolean("dark_mode", value) }

    var language: String
        get() = prefs.getString("language", "en") ?: "en"
        set(value) = prefs.edit { putString("language", value) }
}

// Использование
val settings = SettingsManager(context)
settings.isDarkMode = true
```

### Когда НЕ Использовать SharedPreferences

| Сценарий | Альтернатива |
|----------|--------------|
| Большие объемы данных (вплоть до сотен КБ/МБ) — ухудшение производительности и чтения в память | Room, SQLite |
| Сложные структурированные данные | Room |
| Чувствительные данные (токены, пароли) | EncryptedSharedPreferences или другие решения с шифрованием |
| Типобезопасные / реактивные настройки | DataStore (Preferences) |

### EncryptedSharedPreferences Для Чувствительных Данных

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// ✅ Ключи и значения шифруются автоматически
securePrefs.edit {
    putString("auth_token", "secret_value")
}
```

## Answer (EN)

SharedPreferences is an Android mechanism for storing small sets of key-value pairs (typically flags and simple settings) in the app's private storage. Internally, data is saved in an XML file in the app's internal storage. Data is removed when the app is uninstalled.

See also: [[q-room-relations-embedded--android--medium]].

### Supported Data Types

```kotlin
sharedPref.edit {
    putBoolean("is_logged_in", true)
    putInt("user_id", 42)
    putFloat("rating", 4.5f)
    putLong("timestamp", System.currentTimeMillis())
    putString("username", "alice")
    putStringSet("tags", setOf("kotlin", "android"))
}
```

### Obtaining SharedPreferences

```kotlin
// ✅ Named preferences
val prefs = context.getSharedPreferences(
    "app_settings",
    Context.MODE_PRIVATE  // Only accessible to your app
)

// ✅ Activity-scoped preferences
class MainActivity : AppCompatActivity() {
    private val prefs by lazy {
        getPreferences(Context.MODE_PRIVATE)  // File name = Activity name
    }
}
```

### Writing Data: apply() Vs commit()

```kotlin
// ✅ apply() — writes to disk asynchronously, does not block the calling thread
prefs.edit {
    putString("theme", "dark")
    // apply() is called automatically
}

// ✅ commit() — writes to disk synchronously, returns boolean
val success = prefs.edit()
    .putString("api_key", "xyz123")
    .commit()  // Blocks the thread until the write completes

if (!success) {
    Log.e("Prefs", "Failed to save")
}
```

**Rule**: Use `apply()` by default on the UI thread; use `commit()` only when you need guaranteed write completion before proceeding.

### Typical Use Case: Settings Manager

```kotlin
class SettingsManager(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    var isDarkMode: Boolean
        get() = prefs.getBoolean("dark_mode", false)
        set(value) = prefs.edit { putBoolean("dark_mode", value) }

    var language: String
        get() = prefs.getString("language", "en") ?: "en"
        set(value) = prefs.edit { putString("language", value) }
}

// Usage
val settings = SettingsManager(context)
settings.isDarkMode = true
```

### When NOT to Use SharedPreferences

| Scenario | Alternative |
|----------|-------------|
| Large data (hundreds of KB / MB) — poor performance and full-file reads | Room, SQLite |
| Complex structured data | Room |
| Sensitive data (tokens, passwords) | EncryptedSharedPreferences or other encrypted storage solutions |
| Type-safe / reactive preferences | DataStore (Preferences) |

### EncryptedSharedPreferences for Sensitive Data

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// ✅ Keys and values are encrypted automatically
securePrefs.edit {
    putString("auth_token", "secret_value")
}
```

---

## Дополнительные вопросы (RU)

- Что происходит с данными SharedPreferences при удалении приложения?
- Как выполнить миграцию с SharedPreferences на DataStore?
- Могут ли операции с SharedPreferences вызвать ANR (`Application Not Responding`)?
- Каков практический лимит размера файла SharedPreferences?
- Как реактивно отслеживать изменения в SharedPreferences (с помощью `Flow`)?

## Follow-ups

- What happens to SharedPreferences data on app uninstall?
- How do you migrate from SharedPreferences to DataStore?
- Can SharedPreferences cause ANR (`Application` Not Responding)?
- What's the file size limit for SharedPreferences in practice?
- How do you observe changes in SharedPreferences reactively (with `Flow`)?

## Ссылки (RU)

- https://developer.android.com/training/data-storage/shared-preferences
- https://developer.android.com/reference/android/content/SharedPreferences

## References

- https://developer.android.com/training/data-storage/shared-preferences
- https://developer.android.com/reference/android/content/SharedPreferences

## Связанные вопросы (RU)

### Предпосылки

- [[q-room-relations-embedded--android--medium]]

### Похожие

- [[q-datastore-preferences-proto--android--medium]]

### Продвинутое

## Related Questions

### Prerequisites

- [[q-room-relations-embedded--android--medium]]

### Related

- [[q-datastore-preferences-proto--android--medium]]

### Advanced
