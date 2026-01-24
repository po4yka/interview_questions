---
id: android-032
title: How to schedule local notifications at exact time? / Как запланировать локальные
  уведомления на точное время?
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
- q-dagger-build-time-optimization--android--medium
- q-fragments-history-and-purpose--android--hard
- q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy
- q-mvi-one-time-events--android--medium
- q-recomposition-choreographer--android--hard
- q-which-event-is-called-when-user-touches-screen--android--medium
created: 2025-10-06
updated: 2025-11-11
tags:
- android/background-execution
- android/notifications
- difficulty/medium
anki_cards:
- slug: android-032-0-en
  language: en
  anki_id: 1768379978752
  synced_at: '2026-01-23T16:45:06.387996'
- slug: android-032-0-ru
  language: ru
  anki_id: 1768379978774
  synced_at: '2026-01-23T16:45:06.388870'
---
# Вопрос (RU)
> Как запланировать локальные уведомления на точное время?

# Question (EN)
> How to schedule local notifications at exact time?

---

## Ответ (RU)

Для планирования локального (на устройстве) уведомления на точное время (с учётом ограничений Doze/стэндбая и возможного небольшого дрейфа, контролируемого системой) в Android обычно используют AlarmManager с PendingIntent, который в нужный момент запустит код (например, `BroadcastReceiver`), создающий уведомление.

Ключевые моменты:
- Используем AlarmManager для локальных, основанных на времени событий, а не для удалённых уведомлений (FCM).
- По возможности применяем неточные (inexact) будильники; точные (exact) используем только при реальной бизнес-необходимости (календарь, будильник, критичные напоминания).
- Поведение зависит от версии Android (Doze, standby, ограничения на точные будильники с Android 12+ и особенно Android 13+).

Типичный поток:
1. Создать `BroadcastReceiver` (или другую точку входа: `Service`/Worker), который собирает и показывает уведомление.
2. Запланировать будильник через AlarmManager с PendingIntent на этот receiver.

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
            .setContentTitle("Reminder")
            .setContentText("It's time!")
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
            // Будет стараться сработать как можно точнее и разбудить устройство при необходимости,
            // включая режим Doze (при наличии соответствующих разрешений на точные будильники, если требуются)
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
- Ограничения на точные будильники (Android 12+ / 13+):
  - Для некоторых приложений требуется permission `SCHEDULE_EXACT_ALARM` или принадлежность к льготным категориям (часы, календарь и т.п.). Актуальные требования смотрите в документации к вашей целевой версии Android.
  - На Android 13+ пользователь может управлять доступом приложения к точным будильникам и запретить их использование.
- AlarmManager только запускает ваш код (через PendingIntent); само уведомление нужно создать и показать внутри обработчика (например, в `BroadcastReceiver`).
- Не используйте точные будильники для частых фоновых задач; вместо этого применяйте `WorkManager` или неточные будильники.
- После перезагрузки устройства будильники сбрасываются. Если напоминания должны сохраняться:
  - Обрабатывайте `BOOT_COMPLETED` в `BroadcastReceiver`.
  - Восстанавливайте будильники из сохранённых данных.

Такой подход позволяет показывать локальные уведомления максимально близко к заданному времени с учётом ограничений по энергопотреблению и фоновому выполнению в Android.

## Answer (EN)

To schedule a local (on-device) notification at an exact time (subject to Doze/standby constraints and small system-controlled drift), you typically use AlarmManager with a PendingIntent that, at the trigger time, starts your code (e.g., a `BroadcastReceiver`) which posts the notification.

Key points:
- Use AlarmManager for time-based local triggers, not remote/FCM.
- Prefer inexact alarms when possible; use exact alarms only when product requirements demand it (e.g., calendar events, alarms, critical reminders).
- Behavior and restrictions depend on Android version (Doze, app standby, and exact alarm restrictions starting Android 12+ and especially Android 13+).

Typical flow:
1. Create a `BroadcastReceiver` (or a `Service`/Worker entry point) that builds and shows the notification.
2. Schedule an alarm with AlarmManager and a PendingIntent targeting that receiver.

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
            // Attempts to be exact and wake the device if needed, including in Doze,
            // assuming the app has the required exact alarm permission when applicable
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
- Exact alarm restrictions (Android 12+ / 13+):
  - Some apps must declare the `SCHEDULE_EXACT_ALARM` permission or belong to exempt categories (e.g., clock, calendar). Check the official docs for your target API level.
  - On Android 13+, the user can control and revoke an app's ability to use exact alarms.
- AlarmManager only triggers your PendingIntent; you must build and post the notification in the handler (e.g., in the `BroadcastReceiver`).
- Do not use exact alarms for frequent background work; use `WorkManager` or inexact alarms instead.
- After device reboot, scheduled alarms are lost. If reminders must persist:
  - Listen for `BOOT_COMPLETED` in a `BroadcastReceiver`.
  - Re-schedule alarms from persisted data.

This approach schedules local notifications to fire as close as possible to the requested time while respecting Android's power-management and background-execution constraints.

---

## Follow-ups

- [[q-fragments-history-and-purpose--android--hard]]
- [[q-recomposition-choreographer--android--hard]]
- [[q-which-event-is-called-when-user-touches-screen--android--medium]]

## References

- "https://developer.android.com/training/scheduling/alarms"
- "https://developer.android.com/training/notify-user/build-notification"

## Дополнительные Вопросы (RU)
## Связанные Вопросы И Концепты (RU)
### Предпосылки / Концепты
- [[c-background-tasks]]
## Related Questions and Concepts
### Prerequisites / Concepts
- [[c-background-tasks]]