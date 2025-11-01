---
id: 20251012-122711113
title: "StrictMode Debugging / Отладка StrictMode"
aliases: [StrictMode Debugging, Отладка StrictMode]
topic: android
subtopics: [performance-rendering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-real-time-updates-android--android--medium, q-what-are-fragments-for-if-there-is-activity--android--medium, q-migration-to-compose--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/performance-rendering, difficulty/medium]
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20StrictMode.md
---

# StrictMode in Android / StrictMode в Android

**English**: What is StrictMode?

**Russian**: Что такое StrictMode?

## Answer (EN)
`StrictMode` is a developer tool which detects things you might be doing by accident and brings them to your attention so you can fix them.

`StrictMode` is most commonly used to catch accidental disk or network access on the application's main thread, where UI operations are received and animations take place. Keeping disk and network operations off the main thread makes for much smoother, more responsive applications. By keeping your application's main thread responsive, you also prevent ANR dialogs from being shown to users.

## Example Usage

Example code to enable from early in your `Application`, `Activity`, or other application component's `Application.onCreate()` method:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
     super.onCreate(savedInstanceState)
     StrictMode.setThreadPolicy(
         StrictMode.ThreadPolicy.Builder()
         .detectAll()
         .build()
     )
     StrictMode.setVmPolicy(
         StrictMode.VmPolicy.Builder()
         .detectAll()
         .build()
     )
 }
```

You can decide what should happen when a violation is detected. For example, using `StrictMode.ThreadPolicy.Builder.penaltyLog()` you can watch the output of adb logcat while you use your application to see the violations as they happen.

## Penalty Types

`StrictMode` uses penalties to signal violations:

### penaltyLog()

Logs the violation in the system logcat, making it easy to see what went wrong.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog()
        .build()
)
```

### penaltyDeath()

A drastic measure, forcing the app to crash on a violation. Useful for catching severe problems immediately.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyDeath()
        .build()
)
```

### penaltyDialog()

This would display a dialog to the user (not typically used in production).

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyDialog()
        .build()
)
```

**Note**: The exact policies offered by `StrictMode` have evolved over Android versions.

## Thread Policy

Thread policy detects violations that occur on the main thread:

### Common Detections

- **detectDiskReads()** - Detects when your app reads from disk on the main thread
- **detectDiskWrites()** - Detects when your app writes to disk on the main thread
- **detectNetwork()** - Detects when your app does network operations on the main thread
- **detectCustomSlowCalls()** - Detects when your code does slow operations marked with `StrictMode.noteSlowCall()`
- **detectAll()** - Enables all thread policy detections

### Example

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectDiskWrites()
        .detectNetwork()
        .penaltyLog()
        .build()
)

// This will trigger a violation:
val file = File("/sdcard/test.txt")
file.writeText("Hello World") // Disk write on main thread!
```

## VM Policy

VM policy detects violations across your entire application:

### Common Detections

- **detectActivityLeaks()** - Detects when Activity instances are leaked
- **detectLeakedClosableObjects()** - Detects when closeable objects (like SQLite cursors) are not closed
- **detectLeakedSqlLiteObjects()** - Detects when SQLite objects are not closed
- **detectLeakedRegistrationObjects()** - Detects when BroadcastReceiver or ServiceConnection instances are leaked
- **detectFileUriExposure()** - Detects when file:// URIs are exposed beyond your app
- **detectAll()** - Enables all VM policy detections

### Example

```kotlin
StrictMode.setVmPolicy(
    StrictMode.VmPolicy.Builder()
        .detectActivityLeaks()
        .detectLeakedClosableObjects()
        .penaltyLog()
        .build()
)

// This will trigger a violation:
val cursor = database.query(...) // Not closing cursor causes a leak
```

## Best Practices

### 1. Enable Only in Debug Builds

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
}
```

### 2. Use penaltyLog() in Development

Use `penaltyLog()` during development to catch issues without crashing your app:

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog() // Just log, don't crash
        .build()
)
```

### 3. Use penaltyDeath() for Critical Issues

For critical violations that should never happen, use `penaltyDeath()` to catch them immediately:

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectNetwork()
        .penaltyDeath() // Crash on network access from main thread
        .build()
)
```

### 4. Customize for Different Scenarios

```kotlin
// Strict policy for development
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyDeath()
            .build()
    )
} else {
    // Lenient policy for production (or disabled)
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .permitAll()
            .build()
    )
}
```

## Common Violations and Fixes

### 1. Network on Main Thread

**Problem:**
```kotlin
// - BAD - Network call on main thread
fun loadData() {
    val response = httpClient.get("https://api.example.com/data")
}
```

**Solution:**
```kotlin
// - GOOD - Move to background thread
suspend fun loadData() = withContext(Dispatchers.IO) {
    val response = httpClient.get("https://api.example.com/data")
}
```

### 2. Disk I/O on Main Thread

**Problem:**
```kotlin
// - BAD - Reading file on main thread
fun loadConfig(): String {
    return File("config.txt").readText()
}
```

**Solution:**
```kotlin
// - GOOD - Move to background thread
suspend fun loadConfig(): String = withContext(Dispatchers.IO) {
    File("config.txt").readText()
}
```

### 3. Leaked Closeable Objects

**Problem:**
```kotlin
// - BAD - Cursor not closed
fun getUsers(): List<User> {
    val cursor = database.query(...)
    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(User(cursor))
    }
    return users
}
```

**Solution:**
```kotlin
// - GOOD - Close cursor properly
fun getUsers(): List<User> {
    database.query(...).use { cursor ->
        val users = mutableListOf<User>()
        while (cursor.moveToNext()) {
            users.add(User(cursor))
        }
        return users
    }
}
```

## Ответ (RU)
`StrictMode` - это инструмент разработчика, который обнаруживает вещи, которые вы можете делать случайно, и обращает на них ваше внимание, чтобы вы могли их исправить.

`StrictMode` чаще всего используется для обнаружения случайного доступа к диску или сети в основном потоке приложения, где принимаются операции UI и происходят анимации. Вынос дисковых и сетевых операций из основного потока делает приложения более плавными и отзывчивыми. Сохраняя основной поток вашего приложения отзывчивым, вы также предотвращаете показ диалогов ANR пользователям.

## Пример использования

Пример кода для включения на ранней стадии вашего `Application`, `Activity` или метода `Application.onCreate()` другого компонента приложения:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
     super.onCreate(savedInstanceState)
     StrictMode.setThreadPolicy(
         StrictMode.ThreadPolicy.Builder()
         .detectAll()
         .build()
     )
     StrictMode.setVmPolicy(
         StrictMode.VmPolicy.Builder()
         .detectAll()
         .build()
     )
 }
```

Вы можете решить, что должно произойти при обнаружении нарушения. Например, используя `StrictMode.ThreadPolicy.Builder.penaltyLog()`, вы можете наблюдать вывод adb logcat во время использования приложения, чтобы видеть нарушения по мере их возникновения.

## Типы наказаний

`StrictMode` использует наказания для сигнализации о нарушениях:

### penaltyLog()

Записывает нарушение в системный logcat, упрощая понимание того, что пошло не так.

### penaltyDeath()

Радикальная мера, заставляющая приложение аварийно завершиться при нарушении. Полезно для немедленного обнаружения серьезных проблем.

### penaltyDialog()

Отображает диалоговое окно пользователю (обычно не используется в продакшене).

**Примечание**: Точные политики, предлагаемые `StrictMode`, развивались с версиями Android.

## Thread Policy

Thread policy обнаруживает нарушения, происходящие в основном потоке:

### Общие обнаружения

- **detectDiskReads()** - Обнаруживает, когда ваше приложение читает с диска в основном потоке
- **detectDiskWrites()** - Обнаруживает, когда ваше приложение пишет на диск в основном потоке
- **detectNetwork()** - Обнаруживает, когда ваше приложение выполняет сетевые операции в основном потоке
- **detectCustomSlowCalls()** - Обнаруживает, когда ваш код выполняет медленные операции, помеченные `StrictMode.noteSlowCall()`
- **detectAll()** - Включает все обнаружения политики потоков

## VM Policy

VM policy обнаруживает нарушения во всем приложении:

### Общие обнаружения

- **detectActivityLeaks()** - Обнаруживает утечки экземпляров Activity
- **detectLeakedClosableObjects()** - Обнаруживает, когда закрываемые объекты (как курсоры SQLite) не закрыты
- **detectLeakedSqlLiteObjects()** - Обнаруживает, когда объекты SQLite не закрыты
- **detectLeakedRegistrationObjects()** - Обнаруживает утечки экземпляров BroadcastReceiver или ServiceConnection
- **detectFileUriExposure()** - Обнаруживает, когда file:// URI раскрываются за пределами вашего приложения
- **detectAll()** - Включает все обнаружения VM policy

## Лучшие практики

### 1. Включайте только в отладочных сборках

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
}
```

### 2. Используйте penaltyLog() при разработке

Используйте `penaltyLog()` во время разработки, чтобы обнаруживать проблемы без сбоя приложения.

### 3. Используйте penaltyDeath() для критических проблем

Для критических нарушений, которые никогда не должны происходить, используйте `penaltyDeath()`, чтобы немедленно их обнаружить.

## Распространенные нарушения и их исправления

### 1. Сеть в основном потоке

**Проблема:**
```kotlin
// - ПЛОХО - Сетевой вызов в основном потоке
fun loadData() {
    val response = httpClient.get("https://api.example.com/data")
}
```

**Решение:**
```kotlin
// - ХОРОШО - Переместить в фоновый поток
suspend fun loadData() = withContext(Dispatchers.IO) {
    val response = httpClient.get("https://api.example.com/data")
}
```

### 2. Дисковый I/O в основном потоке

**Проблема:**
```kotlin
// - ПЛОХО - Чтение файла в основном потоке
fun loadConfig(): String {
    return File("config.txt").readText()
}
```

**Решение:**
```kotlin
// - ХОРОШО - Переместить в фоновый поток
suspend fun loadConfig(): String = withContext(Dispatchers.IO) {
    File("config.txt").readText()
}
```

### 3. Утечка закрываемых объектов

**Проблема:**
```kotlin
// - ПЛОХО - Курсор не закрыт
fun getUsers(): List<User> {
    val cursor = database.query(...)
    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(User(cursor))
    }
    return users
}
```

**Решение:**
```kotlin
// - ХОРОШО - Правильно закрыть курсор
fun getUsers(): List<User> {
    database.query(...).use { cursor ->
        val users = mutableListOf<User>()
        while (cursor.moveToNext()) {
            users.add(User(cursor))
        }
        return users
    }
}
```

## Links

- [StrictMode](https://developer.android.com/reference/android/os/StrictMode)
- [StrictMode: Your Android App's Watchdog](https://medium.com/@sandeepkella23/strictmode-your-android-apps-watchdog-4c97be188d57)
- [Smooth Operator: Using StrictMode to make your Android App ANR free](https://riggaroo.dev/smooth-operator-using-strictmode-to-make-your-android-app-anr-free/)
- [Android Best Practices: StrictMode](https://code.tutsplus.com/android-best-practices-strictmode--mobile-7581t)
- [Raising the Bar with Android StrictMode](https://medium.com/wizeline-mobile/raising-the-bar-with-android-strictmode-7042d8a9e67b)

## Related Questions

- [[q-real-time-updates-android--android--medium]]
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]]
- [[q-migration-to-compose--android--medium]]
