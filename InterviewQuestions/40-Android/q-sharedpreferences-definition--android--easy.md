---
id: "20251015082237265"
title: "Sharedpreferences Definition / Определение SharedPreferences"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: - android
  - android/data-storage
  - data-storage
  - key-value
  - persistence
  - sharedpreferences
---

# Question (EN)

> What is SharedPreferences?

# Вопрос (RU)

> Что такое SharedPreferences?

---

## Answer (EN)

**SharedPreferences** is a mechanism for **storing and retrieving simple data** in the form of **key-value pairs**.

It's one of the **simplest ways** to save small amounts of data, such as user settings or application state between sessions.

**Key Characteristics:**

-   -   **Simple to use** - minimal API
-   **Private by default** - data accessible only within the app
-   **Persistent** - survives app restarts
-   **Small data only** - not for large datasets
-   **Perfect for**: User preferences, settings, flags, tokens

**Suitable For:**

-   User preferences (theme, language, notifications on/off)
-   Application state (first launch flag, tutorial completed)
-   Simple configuration values
-   Login tokens or session IDs
-   UI state (checkbox states, selected tabs)

**Basic Usage:**

```kotlin
// 1. Get SharedPreferences instance
val sharedPreferences = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// 2. Write data using Editor
val editor = sharedPreferences.edit()
editor.putString("username", "john_doe")
editor.putInt("user_age", 25)
editor.putBoolean("is_logged_in", true)
editor.apply()  // Async save

// 3. Read data
val username = sharedPreferences.getString("username", "")  // Default: ""
val age = sharedPreferences.getInt("user_age", 0)         // Default: 0
val isLoggedIn = sharedPreferences.getBoolean("is_logged_in", false)
```

**Two Save Methods:**

**apply() - Asynchronous:**

```kotlin
editor.putString("key", "value")
editor.apply()  // - Async, doesn't block UI
```

**commit() - Synchronous:**

```kotlin
editor.putString("key", "value")
val success = editor.commit()  // - Blocks UI, returns boolean
if (success) {
    // Data saved successfully
}
```

**Recommended: Use apply() for better performance**

**Getting SharedPreferences:**

**1. Named SharedPreferences (multiple files):**

```kotlin
val prefs = getSharedPreferences("user_settings", Context.MODE_PRIVATE)
```

**2. Activity-specific preferences:**

```kotlin
val prefs = getPreferences(Context.MODE_PRIVATE)  // Uses Activity name as file
```

**Complete Example:**

```kotlin
class SettingsManager(private val context: Context) {
    private val prefs = context.getSharedPreferences("app_settings", Context.MODE_PRIVATE)

    // Save settings
    fun saveTheme(isDarkMode: Boolean) {
        prefs.edit()
            .putBoolean(KEY_DARK_MODE, isDarkMode)
            .apply()
    }

    fun saveLanguage(language: String) {
        prefs.edit()
            .putString(KEY_LANGUAGE, language)
            .apply()
    }

    fun saveNotificationsEnabled(enabled: Boolean) {
        prefs.edit()
            .putBoolean(KEY_NOTIFICATIONS, enabled)
            .apply()
    }

    // Read settings
    fun isDarkMode(): Boolean {
        return prefs.getBoolean(KEY_DARK_MODE, false)
    }

    fun getLanguage(): String {
        return prefs.getString(KEY_LANGUAGE, "en") ?: "en"
    }

    fun areNotificationsEnabled(): Boolean {
        return prefs.getBoolean(KEY_NOTIFICATIONS, true)
    }

    // Clear all settings
    fun clearAll() {
        prefs.edit().clear().apply()
    }

    // Remove specific key
    fun removeKey(key: String) {
        prefs.edit().remove(key).apply()
    }

    companion object {
        private const val KEY_DARK_MODE = "dark_mode"
        private const val KEY_LANGUAGE = "language"
        private const val KEY_NOTIFICATIONS = "notifications_enabled"
    }
}
```

**Usage in Activity:**

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var settingsManager: SettingsManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        settingsManager = SettingsManager(this)

        // Read settings
        val isDark = settingsManager.isDarkMode()
        val language = settingsManager.getLanguage()

        // Apply theme
        if (isDark) {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
        }

        // Save new setting
        darkModeSwitch.setOnCheckedChangeListener { _, isChecked ->
            settingsManager.saveTheme(isChecked)
        }
    }
}
```

**Modern Approach with Kotlin Extensions:**

```kotlin
// Extension functions
fun SharedPreferences.edit(action: SharedPreferences.Editor.() -> Unit) {
    val editor = edit()
    editor.action()
    editor.apply()
}

// Usage
sharedPreferences.edit {
    putString("username", "john")
    putInt("age", 25)
    putBoolean("premium", true)
}
```

**Supported Data Types:**

```kotlin
editor.putString("name", "John")           // String
editor.putInt("age", 25)                   // Int
editor.putLong("timestamp", 123456789L)    // Long
editor.putFloat("rating", 4.5f)            // Float
editor.putBoolean("enabled", true)         // Boolean
editor.putStringSet("tags", setOf("a", "b"))  // Set<String>
```

**Observing Changes (Flow):**

```kotlin
fun SharedPreferences.observeKey(key: String, default: String): Flow<String> = callbackFlow {
    val listener = SharedPreferences.OnSharedPreferenceChangeListener { _, k ->
        if (k == key) {
            trySend(getString(key, default) ?: default)
        }
    }
    registerOnSharedPreferenceChangeListener(listener)

    // Emit initial value
    trySend(getString(key, default) ?: default)

    awaitClose { unregisterOnSharedPreferenceChangeListener(listener) }
}
```

**Limitations:**

-   -   Not suitable for large data (use Room/SQLite)
-   -   Not suitable for complex objects (use JSON or Serialization)
-   -   Not encrypted by default (use EncryptedSharedPreferences for sensitive data)
-   -   Not suitable for structured/relational data

**Security - EncryptedSharedPreferences:**

```kotlin
// For sensitive data
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secret_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Use same API
encryptedPrefs.edit {
    putString("auth_token", "sensitive_token")
}
```

**Summary:**

-   **SharedPreferences**: Simple key-value storage
-   **Use for**: Settings, preferences, flags, small data
-   **apply()**: Async (recommended)
-   **commit()**: Sync (returns boolean)
-   **Private by default**: Data accessible only within app
-   **Limitations**: Not for large/complex/sensitive data
-   **Security**: Use EncryptedSharedPreferences for sensitive data

---

## Ответ (RU)

SharedPreferences представляет собой механизм для хранения и извлечения простых данных в форме пар ключ-значение. Это один из самых простых способов сохранения небольших объемов данных, таких как пользовательские настройки или состояние приложения между сессиями использования приложения. Подходят для сохранения приватных данных доступных только внутри приложения. Основные особенности: Простота использования, частная доступность данных и применение для хранения настроек пользователя или флагов состояния. Для работы с SharedPreferences необходимо получить экземпляр через getSharedPreferences(String name, int mode) или getPreferences(int mode). Данные записываются через SharedPreferences.Editor и сохраняются с помощью apply() или commit().

---

## Follow-ups

-   When should you use SharedPreferences vs Room database for data storage?
-   What are the differences between apply() and commit() methods in SharedPreferences?
-   How do you migrate from SharedPreferences to DataStore for modern Android apps?

## References

-   `https://developer.android.com/training/data-storage/shared-preferences` — SharedPreferences guide
-   `https://developer.android.com/topic/libraries/architecture/datastore` — DataStore migration
-   `https://developer.android.com/topic/security/data` — EncryptedSharedPreferences

## Related Questions
