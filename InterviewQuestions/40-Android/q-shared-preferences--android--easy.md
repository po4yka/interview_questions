---
id: android-287
title: "SharedPreferences / Хранилище пар ключ-значение"
aliases: ["SharedPreferences", "Хранилище пар ключ-значение", "Shared Preferences"]

# Classification
topic: android
subtopics: [datastore, files-media]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-room-relations-embedded--room--medium, q-how-is-navigation-implemented--android--medium]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags (EN only; no leading #)
tags: [android, android/datastore, android/files-media, data-storage, difficulty/easy]
---

# Вопрос (RU)

> Что такое SharedPreferences и для чего используется?

# Question (EN)

> What is SharedPreferences and what is it used for?

---

## Ответ (RU)

SharedPreferences — это механизм Android для хранения пар ключ-значение. Данные сохраняются в XML-файле в приватном хранилище приложения.

### Поддерживаемые типы данных

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
        getPreferences(Context.MODE_PRIVATE)  // Имя = имя Activity
    }
}
```

### Запись данных: apply() vs commit()

```kotlin
// ✅ apply() — асинхронная, не блокирует UI
prefs.edit {
    putString("theme", "dark")
    // apply() вызывается автоматически
}

// ✅ commit() — синхронная, возвращает boolean
val success = prefs.edit()
    .putString("api_key", "xyz123")
    .commit()  // Блокирует поток до завершения

if (!success) {
    Log.e("Prefs", "Failed to save")
}
```

**Правило**: Используйте `apply()` для UI-потока, `commit()` только если нужна гарантия успешной записи до продолжения.

### Типичный use case: Settings Manager

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

### Когда НЕ использовать SharedPreferences

| Сценарий | Альтернатива |
|----------|--------------|
| Большие объемы данных (>1 MB) | Room, SQLite |
| Структурированные данные | Room |
| Чувствительные данные (токены, пароли) | EncryptedSharedPreferences |
| Типизированные настройки | DataStore (Preferences) |

### EncryptedSharedPreferences для чувствительных данных

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

SharedPreferences is an Android mechanism for storing key-value pairs. Data is saved in an XML file in the app's private storage.

### Supported data types

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
        getPreferences(Context.MODE_PRIVATE)  // Name = Activity name
    }
}
```

### Writing data: apply() vs commit()

```kotlin
// ✅ apply() — asynchronous, doesn't block UI
prefs.edit {
    putString("theme", "dark")
    // apply() called automatically
}

// ✅ commit() — synchronous, returns boolean
val success = prefs.edit()
    .putString("api_key", "xyz123")
    .commit()  // Blocks thread until complete

if (!success) {
    Log.e("Prefs", "Failed to save")
}
```

**Rule**: Use `apply()` for UI thread, `commit()` only when you need guaranteed write completion before proceeding.

### Typical use case: Settings Manager

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

### When NOT to use SharedPreferences

| Scenario | Alternative |
|----------|-------------|
| Large data volumes (>1 MB) | Room, SQLite |
| Structured data | Room |
| Sensitive data (tokens, passwords) | EncryptedSharedPreferences |
| Type-safe preferences | DataStore (Preferences) |

### EncryptedSharedPreferences for sensitive data

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

## Follow-ups

- What happens to SharedPreferences data on app uninstall?
- How do you migrate from SharedPreferences to DataStore?
- Can SharedPreferences cause ANR (Application Not Responding)?
- What's the file size limit for SharedPreferences in practice?
- How do you observe changes in SharedPreferences reactively (with Flow)?

## References

- [[c-android-storage-options]]
- [[c-encryption-android]]
- https://developer.android.com/training/data-storage/shared-preferences
- https://developer.android.com/reference/android/content/SharedPreferences

## Related Questions

### Prerequisites
- [[q-context-in-android--android--easy]]

### Related
- [[q-room-relations-embedded--room--medium]]
- [[q-datastore-preferences--android--medium]]

### Advanced
- [[q-encrypted-shared-preferences-implementation--android--hard]]
