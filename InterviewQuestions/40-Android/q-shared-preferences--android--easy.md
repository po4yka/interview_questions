---
id: "20251015082237455"
title: "Shared Preferences"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: - android
  - data-storage
  - shared-preferences
---
# Что такое SharedPreferences?

**English**: What is SharedPreferences?

## Answer (EN)
SharedPreferences представляет собой механизм для хранения и извлечения простых данных в форме пар ключ-значение. Это один из самых простых способов сохранения небольших объемов данных, таких как пользовательские настройки или состояние приложения между сессиями.

### Основные особенности

#### 1. Простота использования

```kotlin
// Получение SharedPreferences
val sharedPref = context.getSharedPreferences(
    "MyPreferences",
    Context.MODE_PRIVATE
)

// Сохранение данных
sharedPref.edit {
    putString("username", "Alice")
    putInt("age", 30)
    putBoolean("isLoggedIn", true)
}

// Чтение данных
val username = sharedPref.getString("username", "defaultName")
val age = sharedPref.getInt("age", 0)
val isLoggedIn = sharedPref.getBoolean("isLoggedIn", false)
```

#### 2. Частная доступность данных

Данные доступны только внутри приложения (при использовании `MODE_PRIVATE`).

```kotlin
// MODE_PRIVATE - данные доступны только вашему приложению
val privatePrefs = context.getSharedPreferences("private", Context.MODE_PRIVATE)

// Для Activity можно использовать getPreferences()
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Автоматически использует имя Activity
        val prefs = getPreferences(Context.MODE_PRIVATE)
    }
}
```

#### 3. Применение для хранения настроек

```kotlin
class SettingsManager(context: Context) {
    private val prefs = context.getSharedPreferences("AppSettings", Context.MODE_PRIVATE)

    var theme: String
        get() = prefs.getString("theme", "light") ?: "light"
        set(value) = prefs.edit { putString("theme", value) }

    var notificationsEnabled: Boolean
        get() = prefs.getBoolean("notifications_enabled", true)
        set(value) = prefs.edit { putBoolean("notifications_enabled", value) }

    var fontSize: Int
        get() = prefs.getInt("font_size", 14)
        set(value) = prefs.edit { putInt("font_size", value) }
}

// Использование
val settings = SettingsManager(context)
settings.theme = "dark"
settings.notificationsEnabled = false
```

### Поддерживаемые типы данных

```kotlin
sharedPref.edit {
    // Примитивные типы
    putBoolean("bool_key", true)
    putInt("int_key", 42)
    putFloat("float_key", 3.14f)
    putLong("long_key", 1234567890L)
    putString("string_key", "Hello")

    // Set<String>
    putStringSet("set_key", setOf("item1", "item2", "item3"))
}
```

### apply() vs commit()

```kotlin
// apply() - асинхронно, не возвращает результат
sharedPref.edit {
    putString("key", "value")
    apply()  // Выполняется в фоне
}

// commit() - синхронно, возвращает boolean
val success = sharedPref.edit().apply {
    putString("key", "value")
}.commit()  // Блокирует поток до завершения

if (success) {
    println("Saved successfully")
}
```

### Kotlin extensions (современный подход)

```kotlin
// Использование Kotlin extension функции
sharedPref.edit {
    putString("username", "Alice")
    putInt("age", 30)
    // apply() вызывается автоматически
}

// Delegation для удобного доступа
class Settings(context: Context) {
    private val prefs = context.getSharedPreferences("Settings", Context.MODE_PRIVATE)

    var username: String by PreferenceDelegate(prefs, "username", "")
    var isFirstLaunch: Boolean by PreferenceDelegate(prefs, "first_launch", true)
}

// Custom delegate
class PreferenceDelegate<T>(
    private val prefs: SharedPreferences,
    private val key: String,
    private val defaultValue: T
) : ReadWriteProperty<Any?, T> {
    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (defaultValue) {
            is Boolean -> prefs.getBoolean(key, defaultValue) as T
            is Int -> prefs.getInt(key, defaultValue) as T
            is String -> prefs.getString(key, defaultValue) as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit {
            when (value) {
                is Boolean -> putBoolean(key, value)
                is Int -> putInt(key, value)
                is String -> putString(key, value)
            }
        }
    }
}
```

### Наблюдение за изменениями

```kotlin
val listener = SharedPreferences.OnSharedPreferenceChangeListener { prefs, key ->
    when (key) {
        "theme" -> {
            val newTheme = prefs.getString("theme", "light")
            applyTheme(newTheme)
        }
        "notifications_enabled" -> {
            val enabled = prefs.getBoolean("notifications_enabled", true)
            updateNotifications(enabled)
        }
    }
}

// Регистрация listener
sharedPref.registerOnSharedPreferenceChangeListener(listener)

// Не забыть отменить регистрацию
override fun onDestroy() {
    super.onDestroy()
    sharedPref.unregisterOnSharedPreferenceChangeListener(listener)
}
```

### Когда НЕ использовать SharedPreferences

- Большие объемы данных - используйте Room/SQLite
- Сложные структуры данных - используйте Room/DataStore
- Чувствительные данные - используйте EncryptedSharedPreferences
- Структурированные данные - используйте Room database

### Безопасное хранение (EncryptedSharedPreferences)

```kotlin
// Для чувствительных данных используйте шифрование
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secret_shared_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Использование как обычный SharedPreferences
encryptedPrefs.edit {
    putString("api_token", "secret_token_value")
}
```

**English**: SharedPreferences is a simple key-value storage mechanism for saving small amounts of primitive data (boolean, int, float, long, string, string set). Private to the app, used for user settings and app state. Use `edit{}` for writing, `apply()` for async save, `commit()` for sync. For sensitive data, use EncryptedSharedPreferences.
