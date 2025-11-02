---
id: android-031
title: "commit() vs apply() in SharedPreferences / commit() против apply() в SharedPreferences"
aliases: ["commit() vs apply() in SharedPreferences", "commit() против apply() в SharedPreferences"]

# Classification
topic: android
subtopics: [datastore, performance-memory]
question_kind: android
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [c-datastore, c-sharedpreferences, q-datastore-migration--android--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-28

tags: [android/datastore, android/performance-memory, sharedpreferences, performance, difficulty/easy]
---
# Вопрос (RU)
> В чем разница между методами commit() и apply() в SharedPreferences?

# Question (EN)
> What is the difference between commit() and apply() methods in SharedPreferences?

---

## Ответ (RU)

**Ключевая разница**: `commit()` работает синхронно и возвращает результат, `apply()` работает асинхронно в фоновом потоке.

### Быстрое сравнение

| Характеристика | commit() | apply() |
|----------------|----------|---------|
| Возврат | Boolean (успех/неудача) | Void |
| Выполнение | Синхронное (блокирует поток) | Асинхронное (фоновый поток) |
| Производительность | Медленнее | Быстрее |
| Использование | Нужен результат операции | Fire-and-forget (99% случаев) |

### Пример 1: commit() - синхронный

```kotlin
val prefs = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// ❌ commit() блокирует текущий поток до завершения записи
val success = prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .commit() // Блокирует UI thread!

if (success) {
    Log.d("Prefs", "Сохранено успешно")
} else {
    Log.e("Prefs", "Ошибка сохранения")
}
```

### Пример 2: apply() - асинхронный

```kotlin
// ✅ apply() возвращается немедленно
prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .apply() // Не блокирует UI

// Этот код выполняется сразу (запись идет в фоне)
Log.d("Prefs", "apply() вызван, запись происходит в фоне")
```

### Пример 3: Когда использовать commit()

```kotlin
// Случай 1: Нужен результат операции
fun saveImportantData(data: String): Boolean {
    return prefs.edit()
        .putString("important_data", data)
        .commit() // Возвращает true/false
}

// Случай 2: Уже на фоновом потоке
suspend fun saveInBackground() = withContext(Dispatchers.IO) {
    val success = prefs.edit()
        .putString("data", "value")
        .commit() // ✅ OK на фоновом потоке

    if (!success) {
        // Обработка ошибки
    }
}
```

### Пример 4: Когда использовать apply()

```kotlin
// ✅ Обычные настройки (99% случаев)
fun saveSettings(darkMode: Boolean, notifications: Boolean) {
    prefs.edit()
        .putBoolean("dark_mode", darkMode)
        .putBoolean("notifications", notifications)
        .apply() // Fire-and-forget
}

// ✅ Частые обновления (слайдер громкости)
fun onSliderChanged(value: Int) {
    prefs.edit()
        .putInt("volume", value)
        .apply() // Не блокирует UI при частых вызовах
}
```

### Типичные ошибки

```kotlin
// ❌ НЕ ДЕЛАЙТЕ: commit() на главном потоке для некритичных данных
fun onClick() {
    prefs.edit()
        .putLong("last_click", System.currentTimeMillis())
        .commit() // Может вызвать ANR!
}

// ❌ НЕ ДЕЛАЙТЕ: игнорирование результата commit()
prefs.edit()
    .putString("data", "value")
    .commit() // Игнорируете результат? Используйте apply()!

// ✅ ПРАВИЛЬНО: apply() для большинства случаев
fun savePreference() {
    prefs.edit()
        .putString("key", "value")
        .apply()
}

// ✅ ПРАВИЛЬНО: commit() только когда нужен результат
fun saveWithValidation(): Boolean {
    return prefs.edit()
        .putString("key", "value")
        .commit()
}
```

### Современная альтернатива: DataStore

```kotlin
// Для нового кода используйте DataStore вместо SharedPreferences
val Context.dataStore by preferencesDataStore("settings")

// DataStore всегда асинхронный и type-safe
suspend fun savePreference(value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey("key")] = value
    }
}
```

### Best Practices

1. **По умолчанию используйте apply()** - подходит для 99% случаев
2. **Используйте commit() только когда**:
   - Нужно знать, успешна ли запись
   - Уже на фоновом потоке
   - Нужны синхронные гарантии
3. **Никогда не используйте commit() на главном потоке** для частых/некритичных записей
4. **Для нового кода мигрируйте на DataStore**

---

## Answer (EN)

**Key Difference**: `commit()` is synchronous and returns a result, `apply()` is asynchronous and runs on a background thread.

### Quick Comparison

| Feature | commit() | apply() |
|---------|----------|---------|
| Return Type | Boolean (success/failure) | Void |
| Execution | Synchronous (blocks) | Asynchronous (background) |
| Performance | Slower | Faster |
| Use Case | Need immediate result | Fire-and-forget (99% of cases) |

### Example 1: commit() - Synchronous

```kotlin
val prefs = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// ❌ commit() blocks current thread until write completes
val success = prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .commit() // Blocks UI thread!

if (success) {
    Log.d("Prefs", "Successfully saved")
} else {
    Log.e("Prefs", "Failed to save")
}
```

### Example 2: apply() - Asynchronous

```kotlin
// ✅ apply() returns immediately
prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .apply() // Non-blocking

// This code runs immediately (write happens in background)
Log.d("Prefs", "apply() called, write may not be complete")
```

### Example 3: When to Use commit()

```kotlin
// Case 1: Need to know if save succeeded
fun saveImportantData(data: String): Boolean {
    return prefs.edit()
        .putString("important_data", data)
        .commit() // Returns true/false
}

// Case 2: Already on background thread
suspend fun saveInBackground() = withContext(Dispatchers.IO) {
    val success = prefs.edit()
        .putString("data", "value")
        .commit() // ✅ OK on background thread

    if (!success) {
        // Handle failure
    }
}
```

### Example 4: When to Use apply()

```kotlin
// ✅ Simple preferences save (99% of cases)
fun saveSettings(darkMode: Boolean, notifications: Boolean) {
    prefs.edit()
        .putBoolean("dark_mode", darkMode)
        .putBoolean("notifications", notifications)
        .apply() // Fire and forget
}

// ✅ Frequent updates (volume slider)
fun onSliderChanged(value: Int) {
    prefs.edit()
        .putInt("volume", value)
        .apply() // Don't block UI on frequent calls
}
```

### Common Mistakes

```kotlin
// ❌ DON'T: Use commit() on main thread for non-critical data
fun onClick() {
    prefs.edit()
        .putLong("last_click", System.currentTimeMillis())
        .commit() // Can cause ANR!
}

// ❌ DON'T: Ignore return value of commit()
prefs.edit()
    .putString("data", "value")
    .commit() // Ignoring result - use apply() instead!

// ✅ DO: Use apply() for most cases
fun savePreference() {
    prefs.edit()
        .putString("key", "value")
        .apply()
}

// ✅ DO: Use commit() only when you need the result
fun saveWithValidation(): Boolean {
    return prefs.edit()
        .putString("key", "value")
        .commit()
}
```

### Modern Alternative: DataStore

```kotlin
// For new code, use DataStore instead of SharedPreferences
val Context.dataStore by preferencesDataStore("settings")

// DataStore is always async and type-safe
suspend fun savePreference(value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey("key")] = value
    }
}
```

### Best Practices

1. **Default to apply()** - suitable for 99% of cases
2. **Use commit() only when**:
   - You need to know if the write succeeded
   - You're already on a background thread
   - You need synchronous guarantees
3. **Never use commit() on main thread** for frequent/non-critical writes
4. **Migrate to DataStore for new code**

---

## Follow-ups

1. What happens if multiple apply() calls are made in quick succession?
2. Can commit() fail, and what are the common failure scenarios?
3. How does SharedPreferences handle concurrent writes from multiple threads?
4. What are the performance implications of using SharedPreferences vs DataStore?
5. How can you migrate existing SharedPreferences data to DataStore?

## References

- [[c-datastore]] - Modern data storage solution
- [[c-sharedpreferences]] - Legacy key-value storage
- [[c-coroutines]] - Asynchronous programming in Android
- [SharedPreferences Documentation](https://developer.android.com/reference/android/content/SharedPreferences)
- [DataStore Documentation](https://developer.android.com/topic/libraries/architecture/datastore)
- [Migration Guide: SharedPreferences to DataStore](https://developer.android.com/codelabs/android-preferences-datastore)

## Related Questions

### Prerequisites (Easier)
- [[q-android-data-storage-options--android--easy]] - Overview of storage options

### Related (Same Level)
- [[q-datastore-preferences-vs-proto--android--easy]] - DataStore types
- [[q-context-modes-android--android--easy]] - Context.MODE_PRIVATE explained

### Advanced (Harder)
- [[q-datastore-migration--android--medium]] - Migrating from SharedPreferences
- [[q-strict-mode-android--android--medium]] - Detecting main thread I/O
- [[q-performance-memory--android--medium]] - Android performance optimization
