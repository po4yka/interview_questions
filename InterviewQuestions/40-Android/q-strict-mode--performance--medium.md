---
id: android-perf-002
title: StrictMode for Performance / StrictMode для Производительности
aliases:
- StrictMode
- Thread Policy
- VM Policy
- StrictMode для Производительности
topic: android
subtopics:
- performance
- debugging
- threading
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-anr-debugging--performance--hard
- q-memory-leaks-detection--performance--medium
- q-strictmode-debugging--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/performance
- android/debugging
- difficulty/medium
- strictmode
- threading
anki_cards:
- slug: android-perf-002-0-en
  language: en
- slug: android-perf-002-0-ru
  language: ru
---
# Вопрос (RU)

> Что такое StrictMode? Как его использовать для обнаружения проблем производительности?

# Question (EN)

> What is StrictMode? How do you use it to detect performance issues?

---

## Ответ (RU)

**StrictMode** -- это инструмент разработчика для обнаружения случайных операций, которые могут замедлить приложение или вызвать ANR. Он помогает найти disk/network операции в главном потоке.

### Краткий Ответ

- **ThreadPolicy** -- обнаруживает проблемы в конкретном потоке (disk I/O, network в main thread)
- **VmPolicy** -- обнаруживает проблемы на уровне процесса (утечки Activity, незакрытые ресурсы)
- Включать только в debug-сборках

### Подробный Ответ

### Базовая Настройка

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            enableStrictMode()
        }
    }

    private fun enableStrictMode() {
        // Thread Policy -- для обнаружения блокирующих операций
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll()           // Все проверки
                .penaltyLog()          // Логировать нарушения
                .penaltyFlashScreen()  // Мигать экраном при нарушении
                .build()
        )

        // VM Policy -- для обнаружения утечек
        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
    }
}
```

### Thread Policy: Детальная Настройка

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        // Обнаружение операций
        .detectDiskReads()           // Чтение с диска
        .detectDiskWrites()          // Запись на диск
        .detectNetwork()             // Сетевые операции
        .detectCustomSlowCalls()     // Кастомные медленные вызовы
        .detectResourceMismatches()  // Несоответствие ресурсов (API 23+)
        .detectUnbufferedIo()        // Небуферизованный I/O (API 26+)

        // Наказания
        .penaltyLog()                // Логировать
        .penaltyDialog()             // Показать диалог
        .penaltyDeath()              // Крашить приложение
        .penaltyFlashScreen()        // Мигнуть экраном
        .penaltyDeathOnNetwork()     // Крашить при network

        .build()
)
```

### VM Policy: Детальная Настройка

```kotlin
StrictMode.setVmPolicy(
    StrictMode.VmPolicy.Builder()
        // Обнаружение утечек
        .detectActivityLeaks()              // Утечки Activity
        .detectLeakedClosableObjects()      // Незакрытые Closeable
        .detectLeakedSqlLiteObjects()       // Незакрытые SQLite
        .detectLeakedRegistrationObjects()  // Незакрытые BroadcastReceiver

        // Дополнительные проверки
        .detectFileUriExposure()            // file:// URI вместо content://
        .detectCleartextNetwork()           // HTTP вместо HTTPS (API 23+)
        .detectContentUriWithoutPermission() // ContentUri без permission (API 26+)
        .detectUntaggedSockets()            // Сокеты без тегов (API 26+)
        .detectCredentialProtectedWhileLocked() // Доступ к зашифрованным данным (API 29+)
        .detectIncorrectContextUse()        // Неправильное использование Context (API 31+)
        .detectUnsafeIntentLaunch()         // Unsafe Intent launch (API 31+)

        // Наказания
        .penaltyLog()
        .penaltyDeath()

        .build()
)
```

### Кастомные Медленные Вызовы

```kotlin
// Помечаем собственные медленные операции
class HeavyOperation {

    fun processData(data: List<Item>) {
        StrictMode.noteSlowCall("processData with ${data.size} items")

        // Тяжёлая операция
        data.forEach { process(it) }
    }
}

// StrictMode покажет в логах:
// D/StrictMode: StrictMode policy violation: ~duration=1250 ms: android.os.StrictMode$StrictModeCustomViolation: custom slow call
```

### Типичные Нарушения и Исправления

#### 1. Disk Read в Main Thread

```kotlin
// ПЛОХО -- StrictMode поймает
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Чтение SharedPreferences блокирует main thread
        val prefs = getSharedPreferences("config", MODE_PRIVATE)
        val userId = prefs.getString("user_id", null)
    }
}

// ХОРОШО -- асинхронно
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val userId = withContext(Dispatchers.IO) {
                val prefs = getSharedPreferences("config", MODE_PRIVATE)
                prefs.getString("user_id", null)
            }
            updateUI(userId)
        }
    }
}
```

#### 2. Network в Main Thread

```kotlin
// ПЛОХО -- краш с NetworkOnMainThreadException
fun fetchData(): String {
    val url = URL("https://api.example.com/data")
    return url.readText() // Блокирующий вызов!
}

// ХОРОШО -- suspend функция
suspend fun fetchData(): String = withContext(Dispatchers.IO) {
    val url = URL("https://api.example.com/data")
    url.readText()
}
```

#### 3. Незакрытый Cursor

```kotlin
// ПЛОХО -- StrictMode поймает утечку
fun getUsers(): List<User> {
    val cursor = database.query("users", null, null, null, null, null, null)
    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(User.fromCursor(cursor))
    }
    // cursor не закрыт!
    return users
}

// ХОРОШО -- используем use
fun getUsers(): List<User> {
    return database.query("users", null, null, null, null, null, null).use { cursor ->
        val users = mutableListOf<User>()
        while (cursor.moveToNext()) {
            users.add(User.fromCursor(cursor))
        }
        users
    }
}
```

### Временное Отключение StrictMode

```kotlin
// Иногда нужно выполнить операцию, зная о нарушении
fun loadConfigSync(): Config {
    val oldPolicy = StrictMode.allowThreadDiskReads()
    try {
        // Синхронное чтение -- знаем что делаем
        return loadConfigFromDisk()
    } finally {
        StrictMode.setThreadPolicy(oldPolicy)
    }
}
```

### Анализ Логов StrictMode

```
D/StrictMode: StrictMode policy violation; ~duration=150 ms: android.os.StrictMode$StrictModeDiskReadViolation
    at android.os.StrictMode$AndroidBlockGuardPolicy.onReadFromDisk(StrictMode.java:1504)
    at java.io.UnixFileSystem.checkAccess(UnixFileSystem.java:251)
    at java.io.File.exists(File.java:815)
    at com.example.app.MainActivity.onCreate(MainActivity.kt:25)
```

**Ключевая информация:**
- `~duration=150 ms` -- сколько времени заняла операция
- `DiskReadViolation` -- тип нарушения
- Stack trace показывает точное место в коде

### Конфигурация для Разных Сборок

```kotlin
object StrictModeConfig {

    fun setup(application: Application) {
        when {
            BuildConfig.DEBUG -> setupDebug()
            BuildConfig.BUILD_TYPE == "beta" -> setupBeta()
            // Production -- не включаем
        }
    }

    private fun setupDebug() {
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .penaltyFlashScreen() // Визуальная индикация
                .build()
        )

        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
    }

    private fun setupBeta() {
        // Только логирование без визуальных эффектов
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectDiskReads()
                .detectDiskWrites()
                .detectNetwork()
                .penaltyLog()
                .build()
        )
    }
}
```

---

## Answer (EN)

**StrictMode** is a developer tool for detecting accidental operations that may slow down your app or cause ANR. It helps find disk/network operations on the main thread.

### Short Answer

- **ThreadPolicy** -- detects issues in a specific thread (disk I/O, network on main thread)
- **VmPolicy** -- detects process-level issues (Activity leaks, unclosed resources)
- Enable only in debug builds

### Detailed Answer

### Basic Setup

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            enableStrictMode()
        }
    }

    private fun enableStrictMode() {
        // Thread Policy -- for detecting blocking operations
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll()           // All checks
                .penaltyLog()          // Log violations
                .penaltyFlashScreen()  // Flash screen on violation
                .build()
        )

        // VM Policy -- for detecting leaks
        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
    }
}
```

### Thread Policy: Detailed Configuration

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        // Detection
        .detectDiskReads()           // Disk reads
        .detectDiskWrites()          // Disk writes
        .detectNetwork()             // Network operations
        .detectCustomSlowCalls()     // Custom slow calls
        .detectResourceMismatches()  // Resource mismatches (API 23+)
        .detectUnbufferedIo()        // Unbuffered I/O (API 26+)

        // Penalties
        .penaltyLog()                // Log
        .penaltyDialog()             // Show dialog
        .penaltyDeath()              // Crash app
        .penaltyFlashScreen()        // Flash screen
        .penaltyDeathOnNetwork()     // Crash on network

        .build()
)
```

### VM Policy: Detailed Configuration

```kotlin
StrictMode.setVmPolicy(
    StrictMode.VmPolicy.Builder()
        // Leak detection
        .detectActivityLeaks()              // Activity leaks
        .detectLeakedClosableObjects()      // Unclosed Closeable
        .detectLeakedSqlLiteObjects()       // Unclosed SQLite
        .detectLeakedRegistrationObjects()  // Unclosed BroadcastReceiver

        // Additional checks
        .detectFileUriExposure()            // file:// URI instead of content://
        .detectCleartextNetwork()           // HTTP instead of HTTPS (API 23+)
        .detectContentUriWithoutPermission() // ContentUri without permission (API 26+)
        .detectUntaggedSockets()            // Untagged sockets (API 26+)
        .detectCredentialProtectedWhileLocked() // Encrypted data access (API 29+)
        .detectIncorrectContextUse()        // Incorrect Context use (API 31+)
        .detectUnsafeIntentLaunch()         // Unsafe Intent launch (API 31+)

        // Penalties
        .penaltyLog()
        .penaltyDeath()

        .build()
)
```

### Custom Slow Calls

```kotlin
// Mark your own slow operations
class HeavyOperation {

    fun processData(data: List<Item>) {
        StrictMode.noteSlowCall("processData with ${data.size} items")

        // Heavy operation
        data.forEach { process(it) }
    }
}

// StrictMode will show in logs:
// D/StrictMode: StrictMode policy violation: ~duration=1250 ms: android.os.StrictMode$StrictModeCustomViolation: custom slow call
```

### Common Violations and Fixes

#### 1. Disk Read on Main Thread

```kotlin
// BAD -- StrictMode will catch
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Reading SharedPreferences blocks main thread
        val prefs = getSharedPreferences("config", MODE_PRIVATE)
        val userId = prefs.getString("user_id", null)
    }
}

// GOOD -- async
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val userId = withContext(Dispatchers.IO) {
                val prefs = getSharedPreferences("config", MODE_PRIVATE)
                prefs.getString("user_id", null)
            }
            updateUI(userId)
        }
    }
}
```

#### 2. Network on Main Thread

```kotlin
// BAD -- crashes with NetworkOnMainThreadException
fun fetchData(): String {
    val url = URL("https://api.example.com/data")
    return url.readText() // Blocking call!
}

// GOOD -- suspend function
suspend fun fetchData(): String = withContext(Dispatchers.IO) {
    val url = URL("https://api.example.com/data")
    url.readText()
}
```

#### 3. Unclosed Cursor

```kotlin
// BAD -- StrictMode will catch the leak
fun getUsers(): List<User> {
    val cursor = database.query("users", null, null, null, null, null, null)
    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(User.fromCursor(cursor))
    }
    // cursor not closed!
    return users
}

// GOOD -- use `use`
fun getUsers(): List<User> {
    return database.query("users", null, null, null, null, null, null).use { cursor ->
        val users = mutableListOf<User>()
        while (cursor.moveToNext()) {
            users.add(User.fromCursor(cursor))
        }
        users
    }
}
```

### Temporarily Disabling StrictMode

```kotlin
// Sometimes you need to perform an operation knowing about the violation
fun loadConfigSync(): Config {
    val oldPolicy = StrictMode.allowThreadDiskReads()
    try {
        // Synchronous read -- we know what we're doing
        return loadConfigFromDisk()
    } finally {
        StrictMode.setThreadPolicy(oldPolicy)
    }
}
```

### Analyzing StrictMode Logs

```
D/StrictMode: StrictMode policy violation; ~duration=150 ms: android.os.StrictMode$StrictModeDiskReadViolation
    at android.os.StrictMode$AndroidBlockGuardPolicy.onReadFromDisk(StrictMode.java:1504)
    at java.io.UnixFileSystem.checkAccess(UnixFileSystem.java:251)
    at java.io.File.exists(File.java:815)
    at com.example.app.MainActivity.onCreate(MainActivity.kt:25)
```

**Key information:**
- `~duration=150 ms` -- how long the operation took
- `DiskReadViolation` -- violation type
- Stack trace shows exact location in code

### Configuration for Different Builds

```kotlin
object StrictModeConfig {

    fun setup(application: Application) {
        when {
            BuildConfig.DEBUG -> setupDebug()
            BuildConfig.BUILD_TYPE == "beta" -> setupBeta()
            // Production -- don't enable
        }
    }

    private fun setupDebug() {
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .penaltyFlashScreen() // Visual indication
                .build()
        )

        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
    }

    private fun setupBeta() {
        // Only logging without visual effects
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectDiskReads()
                .detectDiskWrites()
                .detectNetwork()
                .penaltyLog()
                .build()
        )
    }
}
```

---

## Ссылки (RU)

- [StrictMode](https://developer.android.com/reference/android/os/StrictMode)
- [Performance Testing](https://developer.android.com/topic/performance/testing)

## References (EN)

- [StrictMode](https://developer.android.com/reference/android/os/StrictMode)
- [Performance Testing](https://developer.android.com/topic/performance/testing)

## Follow-ups (EN)

- How does StrictMode affect app performance in production?
- What's the difference between `penaltyDeath()` and `penaltyDialog()`?
- How to use StrictMode with Kotlin coroutines?
- Can StrictMode detect memory leaks?

## Дополнительные Вопросы (RU)

- Как StrictMode влияет на производительность в production?
- В чём разница между `penaltyDeath()` и `penaltyDialog()`?
- Как использовать StrictMode с Kotlin coroutines?
- Может ли StrictMode обнаруживать утечки памяти?
