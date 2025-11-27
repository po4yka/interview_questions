---
id: android-031
title: "commit() vs apply() in SharedPreferences / commit() против apply() в SharedPreferences"
aliases: ["commit() vs apply() in SharedPreferences", "commit() против apply() в SharedPreferences"]
topic: android
subtopics: [datastore]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-android-storage-options, q-android-storage-types--android--medium]
created: 2025-10-06
updated: 2025-11-10
tags: [android/datastore, difficulty/easy, performance, sharedpreferences]

date created: Saturday, November 1st 2025, 1:24:28 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)
> В чем разница между методами `commit()` и `apply()` в `SharedPreferences`?

# Question (EN)
> What is the difference between `commit()` and `apply()` methods in `SharedPreferences`?

---

## Ответ (RU)

**Ключевая разница**: `commit()` работает синхронно и возвращает результат успешности записи на диск, `apply()` сразу обновляет данные в памяти и планирует запись на диск асинхронно, не блокируя вызывающий поток.

### Быстрое Сравнение

| Характеристика | commit() | apply() |
|----------------|----------|---------|
| Возврат | `Boolean` (успех/неудача записи на диск) | Void |
| Выполнение | Полностью синхронное (обновление памяти + запись на диск, блокирует поток) | Обновление памяти синхронно, запись на диск асинхронно |
| Видимость для читателей | После завершения commit() данные гарантированно записаны и видимы | Данные доступны другим читателям сразу после вызова (из памяти), запись на диск может еще идти |
| Производительность | Медленнее, может блокировать UI | Быстрее с точки зрения вызывающего потока, меньше риск блокировок |
| Использование | Нужен результат/гарантия записи на диск | Fire-and-forget (большинство случаев) |

### Пример 1: commit() - Синхронный

```kotlin
val prefs = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// ❌ commit() блокирует текущий поток до завершения записи на диск
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

### Пример 2: apply() - Асинхронная Запись На Диск

```kotlin
// ✅ apply() синхронно обновляет память и сразу возвращается
prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .apply() // Не блокирует UI при записи на диск

// Этот код выполняется сразу; данные уже доступны через SharedPreferences,
// хотя физическая запись на диск может еще выполняться в фоне
Log.d("Prefs", "apply() вызван, запись на диск выполняется асинхронно")
```

### Пример 3: Когда Использовать commit()

```kotlin
// Случай 1: Нужен результат операции (гарантия записи на диск)
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
        // Обработка ошибки (например, проблема с файловой системой)
    }
}
```

### Пример 4: Когда Использовать apply()

```kotlin
// ✅ Обычные настройки (большинство случаев)
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

### Типичные Ошибки

```kotlin
// ❌ НЕ ДЕЛАЙТЕ: commit() на главном потоке для некритичных данных
fun onClick() {
    prefs.edit()
        .putLong("last_click", System.currentTimeMillis())
        .commit() // Может вызвать лаги и в крайних случаях ANR
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

// ✅ ПРАВИЛЬНО: commit() только когда нужен результат/гарантия
fun saveWithValidation(): Boolean {
    return prefs.edit()
        .putString("key", "value")
        .commit()
}
```

### Современная Альтернатива: DataStore

```kotlin
// Для нового кода используйте DataStore вместо SharedPreferences
val Context.dataStore by preferencesDataStore("settings")

// Preferences DataStore асинхронен и использует типизированные ключи,
// Proto DataStore дает полную типобезопасность через proto-схему
suspend fun savePreference(value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey("key")] = value
    }
}
```

### Рекомендации (Best Practices)

1. Используйте `apply()` по умолчанию — он подходит для большинства сценариев и снижает риск блокировки UI.
2. Используйте `commit()` только когда:
   - нужно знать, успешна ли запись на диск;
   - вы уже находитесь на фоновом потоке;
   - требуются строгие синхронные гарантии.
3. Не используйте `commit()` на главном потоке для частых или некритичных записей.
4. Для нового кода предпочитайте `DataStore`, используя его асинхронное поведение и более сильную модель согласованности данных.

---

## Answer (EN)

**Key Difference**: `commit()` is fully synchronous and reports whether data was persisted to disk; `apply()` updates the in-memory state synchronously and schedules the disk write asynchronously without blocking the caller thread.

### Quick Comparison

| Feature | commit() | apply() |
|---------|----------|---------|
| Return Type | `Boolean` (success/failure of disk write) | Void |
| Execution | Fully synchronous (memory update + disk write, blocks caller) | Memory update is synchronous, disk write is asynchronous |
| Visibility | After commit() returns, data is guaranteed written to disk and visible | Data becomes visible to readers immediately; disk write may still be in progress |
| Performance | Slower, can block (risk on main thread) | Faster from caller perspective, avoids disk I/O blocking |
| Use Case | Need confirmation/guarantee of persistence | Fire-and-forget (most cases) |

### Example 1: commit() - Synchronous

```kotlin
val prefs = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// ❌ commit() blocks current thread until data is written to disk
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

### Example 2: apply() - Asynchronous Disk Write

```kotlin
// ✅ apply() updates memory synchronously and returns immediately
prefs.edit()
    .putString("username", "john_doe")
    .putInt("age", 25)
    .apply() // Non-blocking disk write

// This code runs immediately; updated values are already visible via SharedPreferences,
// while the actual disk persistence is handled in the background
Log.d("Prefs", "apply() called, disk write is scheduled asynchronously")
```

### Example 3: When to Use commit()

```kotlin
// Case 1: Need to know if save succeeded (disk persistence)
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
        // Handle failure (e.g., filesystem issues)
    }
}
```

### Example 4: When to Use apply()

```kotlin
// ✅ Simple preference saves (most cases)
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
        .apply() // Avoid blocking UI on frequent writes
}
```

### Common Mistakes

```kotlin
// ❌ DON'T: Use commit() on main thread for non-critical data
fun onClick() {
    prefs.edit()
        .putLong("last_click", System.currentTimeMillis())
        .commit() // May cause jank and, in worst cases, ANR
}

// ❌ DON'T: Ignore return value of commit()
prefs.edit()
    .putString("data", "value")
    .commit() // Ignoring result? Prefer apply() here.

// ✅ DO: Use apply() for most cases
fun savePreference() {
    prefs.edit()
        .putString("key", "value")
        .apply()
}

// ✅ DO: Use commit() only when you need result/guarantee
fun saveWithValidation(): Boolean {
    return prefs.edit()
        .putString("key", "value")
        .commit()
}
```

### Modern Alternative: DataStore

```kotlin
// For new code, consider DataStore instead of SharedPreferences
val Context.dataStore by preferencesDataStore("settings")

// Preferences DataStore is asynchronous and uses typed keys;
// Proto DataStore provides full type safety via a schema
suspend fun savePreference(value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey("key")] = value
    }
}
```

### Best Practices

1. **Default to apply()** — suitable for most scenarios and reduces UI blocking risk.
2. **Use commit() only when**:
   - You must know if the write to disk succeeded
   - You're already on a background thread
   - You require strict synchronous guarantees
3. **Avoid commit() on main thread** for frequent or non-critical writes.
4. **Prefer DataStore for new code**, leveraging its asynchronous behavior and stronger data consistency model.

---

## Дополнительные Вопросы (Follow-ups, RU)

1. Как `SharedPreferences` обрабатывает несколько последовательных вызовов `apply()`, и как это влияет на производительность и целостность данных?
2. В каких сценариях использование `commit()` строго необходимо, несмотря на его блокирующее поведение?
3. Как `SharedPreferences` ведет себя при конкурентных изменениях из разных потоков или процессов?
4. В чем состоят различия между `SharedPreferences` и `DataStore` с точки зрения согласованности, производительности и обработки ошибок?
5. Как безопасно мигрировать критичные данные из `SharedPreferences` в `DataStore` в продакшн-приложении?

## Follow-ups

1. How does SharedPreferences batch or coalesce multiple apply() calls, and what are the implications?
2. In which scenarios is commit() strictly required despite its blocking nature?
3. How does SharedPreferences behave with concurrent edits from multiple threads or processes?
4. What are the trade-offs between SharedPreferences and DataStore in terms of consistency, performance, and error handling?
5. How would you safely migrate critical SharedPreferences data to DataStore in a production app?

## Ссылки (RU)

- [[c-android-storage-options]]
- [Документация SharedPreferences](https://developer.android.com/reference/android/content/SharedPreferences)
- [Документация DataStore](https://developer.android.com/topic/libraries/architecture/datastore)
- [Руководство по миграции с SharedPreferences на DataStore](https://developer.android.com/codelabs/android-preferences-datastore)

## References

- [[c-android-storage-options]]
- [SharedPreferences Documentation](https://developer.android.com/reference/android/content/SharedPreferences)
- [DataStore Documentation](https://developer.android.com/topic/libraries/architecture/datastore)
- [Migration Guide: SharedPreferences to DataStore](https://developer.android.com/codelabs/android-preferences-datastore)

## Связанные Вопросы (RU)

### Предпосылки (Проще)
- [[q-android-storage-types--android--medium]] - Обзор вариантов хранения данных на Android

### Связанные (Тот Же уровень)
- [[q-android-app-bundles--android--easy]] - Основы `App Bundle`

### Продвинутые (Сложнее)
- [[q-android-runtime-art--android--medium]] - Внутреннее устройство Android Runtime
- [[q-android-performance-measurement-tools--android--medium]] - Инструменты измерения производительности на Android

## Related Questions

### Prerequisites (Easier)
- [[q-android-storage-types--android--medium]] - Overview of storage options

### Related (Same Level)
- [[q-android-app-bundles--android--easy]] - App `Bundle` basics

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]] - Android Runtime internals
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools on Android
