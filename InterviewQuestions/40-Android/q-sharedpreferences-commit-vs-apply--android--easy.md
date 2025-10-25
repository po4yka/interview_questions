---
id: 20251006-100007
title: "commit() vs apply() in SharedPreferences?"
aliases: []

# Classification
topic: android
subtopics: [datastore, performance-memory]
question_kind: comparison
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru, android/sharedpreferences, android/data-storage, android/performance, difficulty/easy]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [datastore, shared-preferences, data-storage]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android/datastore, android/performance-memory, en, ru, difficulty/easy]
---

# Question (EN)
> What is the difference between commit() and apply() in SharedPreferences?
# Вопрос (RU)
> В чем разница между commit() и apply() в SharedPreferences?

---

## Answer (EN)

`commit()` and `apply()` are both methods to save changes to SharedPreferences, but they differ in behavior and performance.

### Quick Comparison

| Feature | commit() | apply() |
|---------|----------|---------|
| **Return Type** | Boolean (success/failure) | Void |
| **Execution** | Synchronous (blocks) | Asynchronous (background) |
| **Performance** | Slower | Faster |
| **Thread** | Current thread | Background thread |
| **Use Case** | Need immediate result | Fire-and-forget |

### 1. commit() - Synchronous

```kotlin
val prefs = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// commit() blocks until write completes
val success = prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .commit() // Blocks current thread!

if (success) {
    Log.d("Prefs", "Successfully saved")
} else {
    Log.e("Prefs", "Failed to save")
}

// Code here runs AFTER write completes
```

### 2. apply() - Asynchronous

```kotlin
val prefs = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// apply() returns immediately
prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .apply() // Returns immediately

// Code here runs IMMEDIATELY (write happens in background)
Log.d("Prefs", "apply() called, but write may not be complete")
```

### 3. Performance Impact

```kotlin
// BAD: Using commit() on main thread
fun saveUserData(user: User) {
    // This BLOCKS the UI thread!
    prefs.edit()
        .putString("name", user.name)
        .putString("email", user.email)
        .commit() // Can cause ANR if disk is slow
}

// GOOD: Using apply() on main thread
fun saveUserData(user: User) {
    // This returns immediately
    prefs.edit()
        .putString("name", user.name)
        .putString("email", user.email)
        .apply() // Non-blocking
}
```

### 4. When to Use commit()

```kotlin
// Case 1: Need to know if save succeeded
fun saveImportantData(data: String): Boolean {
    return prefs.edit()
        .putString("important_data", data)
        .commit() // Returns true/false
}

// Case 2: Need guarantee before next operation
fun saveAndNavigate() {
    val saved = prefs.edit()
        .putBoolean("onboarding_complete", true)
        .commit()
    
    if (saved) {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}

// Case 3: Background thread (already off main thread)
fun saveInBackground() = viewModelScope.launch(Dispatchers.IO) {
    val success = prefs.edit()
        .putString("data", "value")
        .commit() // OK on background thread
    
    if (!success) {
        // Handle failure
    }
}
```

### 5. When to Use apply()

```kotlin
// Case 1: Simple preferences save (most common)
fun saveSettings(darkMode: Boolean, notifications: Boolean) {
    prefs.edit()
        .putBoolean("dark_mode", darkMode)
        .putBoolean("notifications", notifications)
        .apply() // Fire and forget
}

// Case 2: Frequent updates
fun onSliderChanged(value: Int) {
    // Called frequently, don't block UI
    prefs.edit()
        .putInt("volume", value)
        .apply()
}

// Case 3: App settings changes
fun toggleFeature(enabled: Boolean) {
    prefs.edit()
        .putBoolean("feature_enabled", enabled)
        .apply() // Return immediately
}
```

### 6. Common Mistakes

#### - DON'T:

```kotlin
// Don't use commit() on main thread for non-critical data
fun onClick() {
    prefs.edit()
        .putLong("last_click", System.currentTimeMillis())
        .commit() // Blocks UI!
}

// Don't ignore return value of commit()
fun saveData() {
    prefs.edit()
        .putString("data", "value")
        .commit() // Ignoring result - use apply() instead!
}

// Don't chain apply() calls expecting immediate visibility
prefs.edit().putString("key", "value1").apply()
val value = prefs.getString("key", null) // May not be "value1" yet!
```

#### - DO:

```kotlin
// Use apply() for most cases
fun savePreference() {
    prefs.edit()
        .putString("key", "value")
        .apply()
}

// Use commit() only when you need the result
fun saveWithValidation(): Boolean {
    return prefs.edit()
        .putString("key", "value")
        .commit()
}

// Use commit() on background threads if you need blocking behavior
suspend fun saveData() = withContext(Dispatchers.IO) {
    prefs.edit()
        .putString("key", "value")
        .commit()
}
```

### 7. Modern Alternative: DataStore

```kotlin
// For new code, use DataStore instead
val Context.dataStore by preferencesDataStore("settings")

// DataStore is always async and type-safe
suspend fun savePreference(value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey("key")] = value
    }
}
```

### Best Practices Summary

1. **Default to apply()** for most use cases
2. **Use commit() only when**:
   - You need to know if the write succeeded
   - You're already on a background thread
   - You need synchronous guarantees
3. **Never use commit() on main thread** for frequent/non-critical writes
4. **Consider migrating to DataStore** for new code

---

## Ответ (RU)

`commit()` и `apply()` - оба метода для сохранения изменений в SharedPreferences, но отличаются поведением и производительностью.

### Быстрое сравнение

| Характеристика | commit() | apply() |
|----------------|----------|---------|
| **Возврат** | Boolean | Void |
| **Выполнение** | Синхронное | Асинхронное |
| **Производительность** | Медленнее | Быстрее |
| **Поток** | Текущий | Фоновый |

### Когда использовать commit()

- Нужен результат операции
- Гарантия сохранения перед следующей операцией
- Уже на фоновом потоке

### Когда использовать apply()

- Обычные настройки (99% случаев)
- Частые обновления
- Не важен результат

### Современная альтернатива

Для нового кода используйте **DataStore** вместо SharedPreferences.

---

## Related Questions

### Related (Easy)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Advanced (Harder)
- [[q-reduce-apk-size-techniques--android--medium]] - Build Optimization
- [[q-macrobenchmark-startup--android--medium]] - Performance
- [[q-recomposition-compose--android--medium]] - Jetpack Compose

## References
- [SharedPreferences Documentation](https://developer.android.com/reference/android/content/SharedPreferences)
- [DataStore](https://developer.android.com/topic/libraries/architecture/datastore)
