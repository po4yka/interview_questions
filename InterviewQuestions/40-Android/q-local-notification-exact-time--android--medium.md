---
id: android-032
title: How to schedule local notifications at exact time? / Как запланировать локальные уведомления на точное время?
aliases:
- How to schedule local notifications at exact time?
- Как запланировать локальные уведомления на точное время?
topic: android
subtopics:
- background-execution
- notifications
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository
status: draft
moc: moc-android
related:
- c-background-tasks
- q-fragments-history-and-purpose--android--hard
- q-recomposition-choreographer--android--hard
- q-which-event-is-called-when-user-touches-screen--android--medium
created: 2025-10-06
updated: 2025-11-10
tags:
- android/background-execution
- android/notifications
- difficulty/medium
- en
- ru

---

# Вопрос (RU)
> Как запланировать локальные уведомления на точное время?

# Question (EN)
> How to schedule local notifications at exact time?

---

## Ответ (RU)

Для планирования локального (на устройстве) уведомления на (почти) точное время в Android обычно используют AlarmManager с PendingIntent, который в нужный момент запустит код, создающий уведомление.

Ключевые моменты:
- Используем AlarmManager для локальных, основанных на времени событий, а не для удалённых уведомлений (FCM).
- По возможности применяем неточные (inexact) будильники; точные (exact) используем только при реальной бизнес-необходимости (календарь, будильник, критичные напоминания).
- Поведение зависит от версии Android (Doze, standby, ограничения на точные будильники).

Типичный поток:
1) Создать `BroadcastReceiver` (или другую точку входа: `Service`/Worker), который собирает и показывает уведомление.
2) Запланировать будильник через AlarmManager с PendingIntent на этот receiver.

Пример (Kotlin):

```kotlin
class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val channelId = "reminders"
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Reminders",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(context, channelId)
            .setContentTitle("Напоминание")
            .setContentText("Пора!")
            .setSmallIcon(R.drawable.ic_notification)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(1001, notification)
    }
}
```

Планирование точного будильника:

```kotlin
fun scheduleExactReminder(context: Context, triggerAtMillis: Long) {
    val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager

    val intent = Intent(context, ReminderReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )

    when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.M -> {
            // Будет стараться сработать точно и разбудить устройство при необходимости
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent
            )
        }
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT -> {
            alarmManager.setExact(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent)
        }
        else -> {
            alarmManager.set(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent)
        }
    }
}
```

Важные нюансы:
- Ограничения на точные будильники (Android 12+):
  - Для некоторых приложений требуется permission `SCHEDULE_EXACT_ALARM` или принадлежность к льготным категориям (часы, календарь и т.п.). Актуальные требования смотрите в документации.
  - Пользователь может запретить приложению использование точных будильников.
- Не используйте точные будильники для частых фоновых задач; вместо этого применяйте WorkManager или неточные будильники.
- После перезагрузки устройства будильники сбрасываются. Если напоминания должны сохраняться:
  - Обрабатывайте `BOOT_COMPLETED` в `BroadcastReceiver`.
  - Восстанавливайте будильники из сохранённых данных.

Такой подход позволяет показывать локальные уведомления максимально близко к заданному времени с учётом ограничений по энергопотреблению и фоновому выполнению в Android.

## Answer (EN)

To schedule a truly local (on-device) notification at (approximately) an exact time on Android, you typically use AlarmManager with a PendingIntent that eventually posts the notification.

Key points:
- Use AlarmManager for time-based triggers, not remote/FCM.
- Prefer inexact alarms when possible; use exact alarms only when product requirements demand it (e.g., calendar, alarms, critical reminders).
- Behavior and restrictions depend on Android version (Doze, app standby, exact alarm restrictions).

Typical flow:
1) Create a `BroadcastReceiver` (or a `Service`/Worker entry point) that builds and shows the notification.
2) Schedule an alarm with AlarmManager and a PendingIntent targeting that receiver.

Example (Kotlin):

```kotlin
class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val channelId = "reminders"
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Reminders",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(context, channelId)
            .setContentTitle("Reminder")
            .setContentText("It's time!")
            .setSmallIcon(R.drawable.ic_notification)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(1001, notification)
    }
}
```

Scheduling an exact alarm:

```kotlin
fun scheduleExactReminder(context: Context, triggerAtMillis: Long) {
    val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager

    val intent = Intent(context, ReminderReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )

    when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.M -> {
            // Wakes device if needed; attempts to be exact even in Doze
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent
            )
        }
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT -> {
            alarmManager.setExact(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent)
        }
        else -> {
            alarmManager.set(AlarmManager.RTC_WAKEUP, triggerAtMillis, pendingIntent)
        }
    }
}
```

Important considerations:
- Exact alarm restrictions (Android 12+):
  - Some apps must declare the `SCHEDULE_EXACT_ALARM` permission or be in exempt categories (e.g., clock, calendar). Check current platform guidelines.
  - The user can revoke exact alarm access.
- Do not use exact alarms for frequent background work; use WorkManager or inexact alarms instead.
- After a device reboot, scheduled alarms are lost. If the reminders must persist:
  - Listen for `BOOT_COMPLETED` in a `BroadcastReceiver`.
  - Re-schedule alarms from persisted data.

This approach ensures local notifications are fired as close as possible to the requested time while respecting Android's power-management and background-execution constraints.

---

## Дополнительные вопросы (RU)

- [[q-fragments-history-and-purpose--android--hard]]
- [[q-recomposition-choreographer--android--hard]]
- [[q-which-event-is-called-when-user-touches-screen--android--medium]]

## Follow-ups

- [[q-fragments-history-and-purpose--android--hard]]
- [[q-recomposition-choreographer--android--hard]]
- [[q-which-event-is-called-when-user-touches-screen--android--medium]]

## Связанные вопросы и концепты (RU)

### Предпосылки / Концепты

- [[c-background-tasks]]

## Related Questions and Concepts

### Prerequisites / Concepts

- [[c-background-tasks]]

## References
- [Android Documentation](https://developer.android.com)
