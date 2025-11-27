---
id: android-250
title: "What Are Intents For / Для чего нужны Intent"
aliases: ["What Are Intents For", "Для чего нужны Intent"]
topic: android
subtopics: [activity, intents-deeplinks, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-intent, q-android-components-besides-activity--android--easy, q-annotation-processing--android--medium, q-what-is-layout-types-and-when-to-use--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/activity, android/intents-deeplinks, android/service, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:07 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)

> Для чего нужны `Intent` в Android?

# Question (EN)

> What are Intents for in Android?

---

## Ответ (RU)

`Intent` — это объект сообщения в Android для коммуникации между компонентами. Основные назначения: запуск `Activity`, запуск и привязка `Service`, отправка Broadcast и передача данных между компонентами и приложениями.

### Основные Сценарии Использования

**1. Запуск `Activity`**

```kotlin
// Явный Intent — запуск конкретной Activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// С передачей данных
val intent = Intent(this, ProductActivity::class.java).apply {
    putExtra("product_id", 123)
    putExtra("product_name", "Laptop")
}
startActivity(intent)

// Получение результата (современный способ)
val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}
launcher.launch(Intent(this, PickerActivity::class.java))
```

**2. Запуск `Service`**

```kotlin
// Запуск сервиса для фоновой работы
val serviceIntent = Intent(this, DownloadService::class.java).apply {
    putExtra("file_url", "https://example.com/file.zip")
}

// ✅ Для кратковременных операций учитывайте ограничения Android 8.0+
// и при необходимости используйте startForegroundService() + foreground notification.
// Для отложенной/гарантированной работы предпочитайте WorkManager.
startService(serviceIntent)

// Привязка к Service
val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
        val binder = service as MyService.MyBinder
        // ✅ Теперь можем вызывать методы сервиса
    }
    override fun onServiceDisconnected(name: ComponentName?) {}
}
bindService(Intent(this, MyService::class.java), connection, Context.BIND_AUTO_CREATE)
```

**3. Отправка Broadcast**

```kotlin
// Broadcast для уведомления других компонентов
val broadcastIntent = Intent("com.example.CUSTOM_ACTION").apply {
    putExtra("data", "Hello World")
}
sendBroadcast(broadcastIntent) // ✅ Подходит для внутренних событий (нечувствительных данных)

// ✅ Для защиты используйте разрешения или ограничивайте получателей
sendBroadcast(
    Intent("com.example.PROTECTED_ACTION"),
    "com.example.permission.CUSTOM"
)

// ❌ Не используйте незащищённые широковещательные Intent для конфиденциальных данных
```

**4. Неявные `Intent` (Implicit)**

Система находит подходящий компонент по action и data:

```kotlin
// Открыть URL в браузере
val webIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(webIntent)

// Поделиться контентом
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Check this out!")
}
startActivity(Intent.createChooser(shareIntent, "Share via")) // ✅ Всегда показывает диалог выбора

// Проверка доступности Intent
fun safeStartActivity(intent: Intent) {
    if (intent.resolveActivity(packageManager) != null) { // ✅ Предотвращает краши
        startActivity(intent)
    } else {
        Toast.makeText(this, "No app can handle this", Toast.LENGTH_SHORT).show()
    }
}
```

### Компоненты `Intent`

```kotlin
val intent = Intent().apply {
    action = Intent.ACTION_VIEW              // 1. Действие
    data = Uri.parse("https://example.com") // 2. Данные (Uri)
    addCategory(Intent.CATEGORY_BROWSABLE)  // 3. Категория
    // Примечание: отдельные присваивания data и type перезаписывают предыдущее значение.
    // Для одновременной установки используйте setDataAndType().
    type = "text/plain"                     // 4. MIME-тип
    putExtra("key", "value")                // 5. Дополнительные данные
    flags = Intent.FLAG_ACTIVITY_NEW_TASK   // 6. Флаги поведения (перезаписывают предыдущие)
}
```

### `Intent` Flags (важные)

```kotlin
// ✅ Очистить стек выше целевой Activity
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP

// ✅ Не создавать новый экземпляр, если уже на вершине стека
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// ✅ Комбинация: сбросить задачу и начать новую (для логаута)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// Примечание: intent.flags = ... перезаписывает существующие флаги.
// Чтобы добавить флаг к уже установленным, используйте addFlags() или побитовое OR с intent.flags.
```

### PendingIntent

`Intent`, который может быть выполнен другим приложением или системой (для уведомлений, алармов и т.п.). Начиная с Android 12 (API 31)+ (фактически рекомендуется с Android 11), нужно явно указать, может ли PendingIntent изменяться (FLAG_IMMUTABLE или FLAG_MUTABLE).

```kotlin
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    this,
    0,
    notificationIntent,
    PendingIntent.FLAG_IMMUTABLE // ✅ Рекомендуется, если Intent не должен изменяться
)

val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setContentIntent(pendingIntent)
    .build()
```

### Когда Использовать Что

| Тип `Intent` | Применение | Пример |
|-----------|-----------|--------|
| **Explicit** | Запуск компонента вашего приложения | `Intent(this, DetailActivity::class.java)` |
| **Implicit** | Запуск системного компонента или другого приложения | `Intent.ACTION_VIEW` |
| **PendingIntent** | Отложенное выполнение через другое приложение или систему | Уведомления, алармы |

## Answer (EN)

`Intent` is a messaging object in Android for component communication. Core purposes: starting Activities, starting and binding to Services, sending broadcasts, and passing data between components and apps.

### Main Use Cases

**1. Starting Activities**

```kotlin
// Explicit Intent - start specific Activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// With data
val intent = Intent(this, ProductActivity::class.java).apply {
    putExtra("product_id", 123)
    putExtra("product_name", "Laptop")
}
startActivity(intent)

// Get result (modern approach)
val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}
launcher.launch(Intent(this, PickerActivity::class.java))
```

**2. Starting Services**

```kotlin
// Start a service for background work
val serviceIntent = Intent(this, DownloadService::class.java).apply {
    putExtra("file_url", "https://example.com/file.zip")
}

// ✅ For short-lived work, be aware of Android 8.0+ background execution limits.
// Use startForegroundService() + foreground notification when required.
// For deferrable/guaranteed background work prefer WorkManager.
startService(serviceIntent)

// Bind to Service
val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
        val binder = service as MyService.MyBinder
        // ✅ Now can call service methods
    }
    override fun onServiceDisconnected(name: ComponentName?) {}
}
bindService(Intent(this, MyService::class.java), connection, Context.BIND_AUTO_CREATE)
```

**3. Broadcasting Messages**

```kotlin
// Broadcast to notify other components
val broadcastIntent = Intent("com.example.CUSTOM_ACTION").apply {
    putExtra("data", "Hello World")
}
sendBroadcast(broadcastIntent) // ✅ Good for internal, non-sensitive events

// ✅ For protection, use permissions or otherwise restrict receivers
sendBroadcast(
    Intent("com.example.PROTECTED_ACTION"),
    "com.example.permission.CUSTOM"
)

// ❌ Do not use unsecured implicit broadcasts for sensitive data
```

**4. Implicit Intents**

System finds appropriate component based on action and data:

```kotlin
// Open URL in browser
val webIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(webIntent)

// Share content
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Check this out!")
}
startActivity(Intent.createChooser(shareIntent, "Share via")) // ✅ Always shows chooser dialog

// Check Intent availability
fun safeStartActivity(intent: Intent) {
    if (intent.resolveActivity(packageManager) != null) { // ✅ Prevents crashes
        startActivity(intent)
    } else {
        Toast.makeText(this, "No app can handle this", Toast.LENGTH_SHORT).show()
    }
}
```

### `Intent` Components

```kotlin
val intent = Intent().apply {
    action = Intent.ACTION_VIEW              // 1. Action
    data = Uri.parse("https://example.com") // 2. Data (Uri)
    addCategory(Intent.CATEGORY_BROWSABLE)  // 3. Category
    // Note: separate assignments to data and type overwrite previous values.
    // Use setDataAndType() when you need both.
    type = "text/plain"                     // 4. MIME type
    putExtra("key", "value")                // 5. Extra data
    flags = Intent.FLAG_ACTIVITY_NEW_TASK   // 6. Behavior flags (overwrite previous)
}
```

### `Intent` Flags (important)

```kotlin
// ✅ Clear all activities above target
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP

// ✅ Don't create new instance if already on top
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// ✅ Combination: clear task and start new (for logout)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// Note: intent.flags = ... overwrites existing flags.
// To add a flag, use addFlags() or bitwise OR with intent.flags.
```

### PendingIntent

`Intent` that can be executed by another app or by the system (for notifications, alarms, etc.). Starting from Android 12 (API 31)+ (and recommended since Android 11), you must explicitly declare whether the PendingIntent is mutable or immutable using FLAG_IMMUTABLE or FLAG_MUTABLE.

```kotlin
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    this,
    0,
    notificationIntent,
    PendingIntent.FLAG_IMMUTABLE // ✅ Recommended when the Intent should not be modified
)

val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setContentIntent(pendingIntent)
    .build()
```

### When to Use What

| `Intent` Type | Use Case | Example |
|-----------|----------|---------|
| **Explicit** | Launch component in your app | `Intent(this, DetailActivity::class.java)` |
| **Implicit** | Launch system component or other app | `Intent.ACTION_VIEW` |
| **PendingIntent** | Deferred execution by another app or the system | Notifications, alarms |

---

## Follow-ups

- How do `Intent` Filters work in AndroidManifest.xml?
- What's the difference between startActivity() and startActivityForResult() (deprecated)?
- When should you use LocalBroadcastManager vs system broadcasts?
- What are the security implications of implicit Intents?
- How do deep links and app links relate to Intents?

## References

- [[c-android-components]] - Overview of Android components
- [[c-activity-lifecycle]] - `Activity` lifecycle and `Intent` handling
- [Android Developer Guide: Intents and `Intent` Filters](https://developer.android.com/guide/components/intents-filters)
- [Common Intents Reference](https://developer.android.com/guide/components/intents-common)

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - Understanding Android components
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread and component communication

### Related (Medium)
- [[q-intent-filters-android--android--medium]] - How apps declare `Intent` handling
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Component architecture

### Advanced (Harder)
- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - System component management
```