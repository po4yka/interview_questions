---
id: android-411
title: What Is PendingIntent / Что такое PendingIntent
aliases:
- What is PendingIntent
- Что такое PendingIntent
topic: android
subtopics:
- intents-deeplinks
- notifications
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-intent
- c-permissions
- q-anr-application-not-responding--android--medium
- q-intent-filters-android--android--medium
- q-what-unifies-android-components--android--easy
created: 2025-10-15
updated: 2025-10-29
sources: []
tags:
- android
- android/intents-deeplinks
- android/notifications
- difficulty/medium
date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)
> Что такое PendingIntent?

# Question (EN)
> What is PendingIntent?

---

## Ответ (RU)

**PendingIntent** — это обёртка вокруг Intent, которая позволяет другим компонентам или приложениям выполнить Intent с правами вашего приложения, даже когда оно неактивно. По сути, это токен разрешения для отложенного действия.

### Ключевые Характеристики

- **Отложенное выполнение** — Intent выполняется позже, не сразу
- **Делегирование прав** — выполняется с правами вашего приложения
- **Неизменяемость** — нельзя изменить после создания (FLAG_IMMUTABLE)
- **Системное использование** — уведомления, AlarmManager, виджеты

### Три Типа PendingIntent

```kotlin
// 1. Для Activity (открыть экран)
val activityPI = PendingIntent.getActivity(context, requestCode, intent,
    PendingIntent.FLAG_IMMUTABLE)  // ✅ Рекомендуется для Android 12+

// 2. Для BroadcastReceiver (событие)
val broadcastPI = PendingIntent.getBroadcast(context, requestCode, intent,
    PendingIntent.FLAG_IMMUTABLE)

// 3. Для Service (фоновая работа)
val servicePI = PendingIntent.getService(context, requestCode, intent,
    PendingIntent.FLAG_IMMUTABLE)
```

**Основные флаги:**
- `FLAG_IMMUTABLE` — неизменяемый (✅ безопасно, используй по умолчанию)
- `FLAG_MUTABLE` — изменяемый (❌ только если действительно нужно)
- `FLAG_UPDATE_CURRENT` — обновить существующий (✅ для обновления extras)
- `FLAG_NO_CREATE` — не создавать, вернуть null если не существует (✅ для проверки)

---

## Answer (EN)

**PendingIntent** is a wrapper around an Intent that grants other components or applications permission to execute that Intent with your app's permissions, even when your app is not active. Essentially, it's a permission token for deferred actions.

### Key Characteristics

- **Deferred execution** — Intent executes later, not immediately
- **Permission delegation** — runs with your app's permissions
- **Immutability** — cannot be modified after creation (FLAG_IMMUTABLE)
- **System integration** — notifications, AlarmManager, widgets

### Three Types of PendingIntent

```kotlin
// 1. For Activity (launch screen)
val activityPI = PendingIntent.getActivity(context, requestCode, intent,
    PendingIntent.FLAG_IMMUTABLE)  // ✅ Recommended for Android 12+

// 2. For BroadcastReceiver (event)
val broadcastPI = PendingIntent.getBroadcast(context, requestCode, intent,
    PendingIntent.FLAG_IMMUTABLE)

// 3. For Service (background work)
val servicePI = PendingIntent.getService(context, requestCode, intent,
    PendingIntent.FLAG_IMMUTABLE)
```

**Essential Flags:**
- `FLAG_IMMUTABLE` — immutable (✅ safe, use by default)
- `FLAG_MUTABLE` — mutable (❌ only if truly necessary)
- `FLAG_UPDATE_CURRENT` — update existing (✅ for updating extras)
- `FLAG_NO_CREATE` — don't create, return null if doesn't exist (✅ for checking)

### Use Case 1: Notifications

```kotlin
fun showNotification(context: Context) {
    val intent = Intent(context, MainActivity::class.java)
    val pendingIntent = PendingIntent.getActivity(context, 0, intent,
        PendingIntent.FLAG_IMMUTABLE)  // ✅ Required for Android 12+

    val notification = NotificationCompat.Builder(context, "channel_id")
        .setContentTitle("New Message")
        .setContentIntent(pendingIntent)  // Notification tap opens Activity
        .build()
}
```

### Use Case 2: AlarmManager

```kotlin
fun scheduleAlarm(context: Context, triggerTime: Long) {
    val intent = Intent(context, AlarmReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(context, 0, intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)

    context.getSystemService(AlarmManager::class.java)
        .setExact(AlarmManager.RTC_WAKEUP, triggerTime, pendingIntent)
}

fun cancelAlarm(context: Context) {
    val intent = Intent(context, AlarmReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(context, 0, intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE)  // ✅ Check if exists

    pendingIntent?.let {
        context.getSystemService(AlarmManager::class.java).cancel(it)
        it.cancel()  // Clean up PendingIntent
    }
}
```

### Use Case 3: App Widgets

```kotlin
class MyWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, ids: IntArray) {
        ids.forEach { widgetId ->
            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(context,
                widgetId,  // ✅ Unique requestCode per widget
                intent, PendingIntent.FLAG_IMMUTABLE)

            val views = RemoteViews(context.packageName, R.layout.widget_layout)
            views.setOnClickPendingIntent(R.id.widget_root, pendingIntent)
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
```

### Best Practices

1. **FLAG_IMMUTABLE by default** — required for Android 12+
2. **Unique requestCodes** — use different codes for different PendingIntents
3. **FLAG_UPDATE_CURRENT** — to update extras in existing PendingIntent
4. **Explicit Intents** — always specify concrete component for security
5. **Cancel when done** — call `cancel()` to clean up unused PendingIntents

---

## Follow-ups

- How does requestCode affect PendingIntent equality and updates?
- When should you use FLAG_MUTABLE instead of FLAG_IMMUTABLE?
- How do you handle PendingIntent with WorkManager for background tasks?
- What happens if you don't cancel a PendingIntent after use?
- How to debug PendingIntent security vulnerabilities in Android 12+?

## References

- [[q-intent-filters-android--android--medium]] - Intent fundamentals
- [[q-what-unifies-android-components--android--easy]] - Android components
- https://developer.android.com/reference/android/app/PendingIntent
- https://developer.android.com/about/versions/12/behavior-changes-12#pending-intent-mutability

---

## Related Questions

### Prerequisites / Concepts

- [[c-intent]]
- [[c-permissions]]


### Prerequisites (Easier)
- [[q-what-unifies-android-components--android--easy]] - Intent basics
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Android threading

### Related (Same Level)
- [[q-intent-filters-android--android--medium]] - Intent deep dive
- [[q-anr-application-not-responding--android--medium]] - Background work patterns

### Advanced (Harder)
- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Process lifecycle
