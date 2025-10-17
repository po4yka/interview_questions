---
id: 20251017-150433
title: "Shared Preferences"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [data-storage, shared-preferences, difficulty/easy]
---
# Что такое SharedPreferences?

**English**: What is SharedPreferences?

## Answer (EN)
SharedPreferences представляет собой механизм для хранения и извлечения простых данных в форме пар ключ-значение. Это один из самых простых способов сохранения небольших объемов данных, таких как пользовательские настройки или состояние приложения между сессиями.

### Key features

#### 1. Ease of use

```kotlin
// Get SharedPreferences
val sharedPref = context.getSharedPreferences(
    "MyPreferences",
    Context.MODE_PRIVATE
)

// Save data
sharedPref.edit {
    putString("username", "Alice")
    putInt("age", 30)
    putBoolean("isLoggedIn", true)
}

// Read data
val username = sharedPref.getString("username", "defaultName")
val age = sharedPref.getInt("age", 0)
val isLoggedIn = sharedPref.getBoolean("isLoggedIn", false)
```

#### 2. Private data accessibility

Data is only accessible within the app (when using `MODE_PRIVATE`).

```kotlin
// MODE_PRIVATE - data accessible only to your app
val privatePrefs = context.getSharedPreferences("private", Context.MODE_PRIVATE)

// For Activity you can use getPreferences()
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Automatically uses Activity name
        val prefs = getPreferences(Context.MODE_PRIVATE)
    }
}
```

#### 3. Application for storing settings

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

// Usage
val settings = SettingsManager(context)
settings.theme = "dark"
settings.notificationsEnabled = false
```

### Supported data types

```kotlin
sharedPref.edit {
    // Primitive types
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
// apply() - asynchronous, doesn't return result
sharedPref.edit {
    putString("key", "value")
    apply()  // Executes in background
}

// commit() - synchronous, returns boolean
val success = sharedPref.edit().apply {
    putString("key", "value")
}.commit()  // Blocks thread until complete

if (success) {
    println("Saved successfully")
}
```

### Kotlin extensions (modern approach)

```kotlin
// Using Kotlin extension function
sharedPref.edit {
    putString("username", "Alice")
    putInt("age", 30)
    // apply() called automatically
}

// Delegation for convenient access
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

### Observing changes

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

// Register listener
sharedPref.registerOnSharedPreferenceChangeListener(listener)

// Don't forget to unregister
override fun onDestroy() {
    super.onDestroy()
    sharedPref.unregisterOnSharedPreferenceChangeListener(listener)
}
```

### When NOT to use SharedPreferences

- Large amounts of data - use Room/SQLite
- Complex data structures - use Room/DataStore
- Sensitive data - use EncryptedSharedPreferences
- Structured data - use Room database

### Secure storage (EncryptedSharedPreferences)

```kotlin
// For sensitive data use encryption
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

// Use like regular SharedPreferences
encryptedPrefs.edit {
    putString("api_token", "secret_token_value")
}
```

**English**: SharedPreferences is a simple key-value storage mechanism for saving small amounts of primitive data (boolean, int, float, long, string, string set). Private to the app, used for user settings and app state. Use `edit{}` for writing, `apply()` for async save, `commit()` for sync. For sensitive data, use EncryptedSharedPreferences.
