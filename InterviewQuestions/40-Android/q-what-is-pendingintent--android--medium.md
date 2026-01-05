---
id: android-411
title: What Is PendingIntent / Что такое PendingIntent
aliases: [What is PendingIntent, Что такое PendingIntent]
topic: android
subtopics: [intents-deeplinks, notifications]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-intent, c-permissions, q-anr-application-not-responding--android--medium, q-compose-core-components--android--medium, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-intent-filters-android--android--medium, q-what-unifies-android-components--android--easy]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android, android/intents-deeplinks, android/notifications, difficulty/medium]

---
# Вопрос (RU)
> Что такое PendingIntent?

# Question (EN)
> What is PendingIntent?

---

## Ответ (RU)

**PendingIntent** — это обёртка вокруг `Intent`, которая позволяет другим компонентам или приложениям позже выполнить этот `Intent` с правами и идентичностью вашего приложения (создателя PendingIntent), даже когда оно неактивно. По сути, это токен разрешения для отложенного действия, выдаваемый системой.

### Ключевые Характеристики

- **Отложенное выполнение** — `Intent` выполняется позже, не сразу.
- **Делегирование прав** — действие выполняется с правами вашего приложения (того, кто создал PendingIntent), а не вызывающего кода.
- **Контролируемая изменяемость**:
  - до Android 12 поведение зависело от комбинации флагов;
  - начиная с Android 12 (targetSdkVersion >= 31) при создании нужно явно указать `FLAG_IMMUTABLE` или `FLAG_MUTABLE`, иначе будет выброшено исключение;
  - `FLAG_IMMUTABLE` делает PendingIntent неизменяемым после создания (рекомендуется, если нет необходимости менять данные через сторонний код);
  - `FLAG_MUTABLE` разрешает изменять/читать вложенный `Intent` через PendingIntent (использовать только при реальной необходимости).
- **Системное использование** — активно используется системой: уведомления, AlarmManager, App Widgets и другие механизмы, которым нужно выполнить код от имени вашего приложения.

### Три Типа PendingIntent

```kotlin
// 1. Для Activity (открыть экран)
val activityPI = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE // ✅ Рекомендуется, если не требуется изменяемость
)

// 2. Для BroadcastReceiver (событие)
val broadcastPI = PendingIntent.getBroadcast(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE // или FLAG_MUTABLE, если принимающая сторона должна работать с динамическими данными
)

// 3. Для Service (фоновая работа)
val servicePI = PendingIntent.getService(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
```

**Основные флаги:**
- `FLAG_IMMUTABLE` — делает PendingIntent неизменяемым (✅ безопасно, используй по умолчанию, если не требуется изменяемость).
- `FLAG_MUTABLE` — разрешает изменять/читать вложенный `Intent` через PendingIntent (используй только если действительно нужно, например, для inline-reply, bubbles, RemoteInput и других функций, где система/чужой код должен иметь доступ к extras).
- `FLAG_UPDATE_CURRENT` — обновить существующий PendingIntent (✅ для обновления extras). На Android 12+ должен использоваться в сочетании с `FLAG_IMMUTABLE` или `FLAG_MUTABLE`.
- `FLAG_NO_CREATE` — не создавать новый, вернуть null если не существует (✅ для проверки перед использованием). На Android 12+ также должен сопровождаться флагом изменяемости.

### Примеры Использования

#### Сценарий 1: Уведомления

```kotlin
fun showNotification(context: Context) {
    val intent = Intent(context, MainActivity::class.java)
    val pendingIntent = PendingIntent.getActivity(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE // На Android 12+ требуется явно указать mutability-флаг
    )

    val notification = NotificationCompat.Builder(context, "channel_id")
        .setContentTitle("New Message")
        .setContentIntent(pendingIntent) // Нажатие на уведомление открывает Activity
        .build()
}
```

#### Сценарий 2: AlarmManager

```kotlin
fun scheduleAlarm(context: Context, triggerTime: Long) {
    val intent = Intent(context, AlarmReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        // Используй FLAG_MUTABLE (вместо FLAG_IMMUTABLE), если AlarmReceiver или система должны иметь доступ к изменяемому Intent/extras
    )

    context.getSystemService(AlarmManager::class.java)
        .setExact(AlarmManager.RTC_WAKEUP, triggerTime, pendingIntent)
}

fun cancelAlarm(context: Context) {
    val intent = Intent(context, AlarmReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE
    )

    pendingIntent?.let {
        context.getSystemService(AlarmManager::class.java).cancel(it)
        it.cancel() // Опционально инвалидируем PendingIntent, если он больше не нужен
    }
}
```

#### Сценарий 3: App Widgets

```kotlin
class MyWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, ids: IntArray) {
        ids.forEach { widgetId ->
            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(
                context,
                widgetId, // ✅ Уникальный requestCode на каждый виджет
                intent,
                PendingIntent.FLAG_IMMUTABLE
            )

            val views = RemoteViews(context.packageName, R.layout.widget_layout)
            views.setOnClickPendingIntent(R.id.widget_root, pendingIntent)
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
```

### Best Practices (RU)

1. На Android 12+ (при targetSdkVersion >= 31) всегда явно указывай `FLAG_IMMUTABLE` или `FLAG_MUTABLE` при создании PendingIntent.
2. Используй `FLAG_IMMUTABLE` по умолчанию для безопасности, если нет реальной необходимости в изменяемости.
3. Используй уникальные `requestCode` для различения PendingIntent с одинаковыми `Intent`-параметрами.
4. Применяй `FLAG_UPDATE_CURRENT`, когда нужно обновлять extras уже существующего PendingIntent (вместе с корректным флагом изменяемости).
5. Для PendingIntent, доступных другим приложениям, старайся использовать явные `Intent` (конкретный компонент), чтобы снизить риск перехвата или подмены; implicit `Intent` допустим в контролируемых сценариях.
6. Для долгоживущих или повторяющихся задач, которые больше не нужны, вызови `cancel()` (и отмени через соответствующий менеджер, например AlarmManager), чтобы избежать неожиданных срабатываний.

---

## Answer (EN)

**PendingIntent** is a wrapper around an `Intent` that allows other components or applications to trigger that `Intent` later with your app's identity and permissions (the identity of the creator), even when your app is not in the foreground. Essentially, it is a permission token for deferred actions, issued and enforced by the system.

### Key Characteristics

- **Deferred execution** — the `Intent` is executed later, not immediately.
- **Permission delegation** — it runs with the identity/permissions of your app (the creator of the PendingIntent), not the caller.
- **Controlled mutability**:
  - prior to Android 12, behavior depended on the combination of flags;
  - starting from Android 12 (when targetSdkVersion >= 31), you must explicitly specify `FLAG_IMMUTABLE` or `FLAG_MUTABLE` when creating a PendingIntent, otherwise an exception is thrown;
  - `FLAG_IMMUTABLE` makes the wrapped `Intent` unchangeable via the PendingIntent after creation (recommended when mutation is not needed by external code);
  - `FLAG_MUTABLE` allows the wrapped `Intent`/extras to be read or modified via the PendingIntent (use only when truly required).
- **System integration** — heavily used by the system: notifications, AlarmManager, app widgets, and other mechanisms that need to act on behalf of your app.

### Three Types of PendingIntent

```kotlin
// 1. For Activity (launch screen)
val activityPI = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE // ✅ Recommended when you don't need mutability
)

// 2. For BroadcastReceiver (event)
val broadcastPI = PendingIntent.getBroadcast(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE // or FLAG_MUTABLE if the receiver/system must work with dynamic data
)

// 3. For Service (background work)
val servicePI = PendingIntent.getService(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
```

**Essential Flags:**
- `FLAG_IMMUTABLE` — makes the PendingIntent immutable (✅ safe, prefer by default when mutability is not required).
- `FLAG_MUTABLE` — allows the wrapped `Intent` to be read/modified via the PendingIntent (use only when absolutely needed, e.g., for inline reply, bubbles, RemoteInput, and similar features).
- `FLAG_UPDATE_CURRENT` — update an existing PendingIntent (✅ for updating extras for the same logical operation). On Android 12+, must be combined with either `FLAG_IMMUTABLE` or `FLAG_MUTABLE`.
- `FLAG_NO_CREATE` — do not create; return null if it does not exist (✅ for checking before use). On Android 12+, should also be combined with an explicit mutability flag.

### Use Case 1: Notifications

```kotlin
fun showNotification(context: Context) {
    val intent = Intent(context, MainActivity::class.java)
    val pendingIntent = PendingIntent.getActivity(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE // On Android 12+, you must explicitly specify a mutability flag
    )

    val notification = NotificationCompat.Builder(context, "channel_id")
        .setContentTitle("New Message")
        .setContentIntent(pendingIntent) // Notification tap opens Activity
        .build()
}
```

### Use Case 2: AlarmManager

```kotlin
fun scheduleAlarm(context: Context, triggerTime: Long) {
    val intent = Intent(context, AlarmReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        // Use FLAG_MUTABLE (instead of FLAG_IMMUTABLE) when the receiver or system must access/modify dynamic extras via the PendingIntent
    )

    context.getSystemService(AlarmManager::class.java)
        .setExact(AlarmManager.RTC_WAKEUP, triggerTime, pendingIntent)
}

fun cancelAlarm(context: Context) {
    val intent = Intent(context, AlarmReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE
    )

    pendingIntent?.let {
        context.getSystemService(AlarmManager::class.java).cancel(it)
        it.cancel() // Optionally invalidate the PendingIntent if it should no longer fire
    }
}
```

### Use Case 3: App Widgets

```kotlin
class MyWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, ids: IntArray) {
        ids.forEach { widgetId ->
            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(
                context,
                widgetId, // ✅ Unique requestCode per widget
                intent,
                PendingIntent.FLAG_IMMUTABLE
            )

            val views = RemoteViews(context.packageName, R.layout.widget_layout)
            views.setOnClickPendingIntent(R.id.widget_root, pendingIntent)
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
```

### Best Practices

1. On Android 12+ (when targetSdkVersion >= 31), always explicitly specify `FLAG_IMMUTABLE` or `FLAG_MUTABLE` when creating a PendingIntent.
2. Prefer `FLAG_IMMUTABLE` by default for security when you do not need to mutate the PendingIntent.
3. Use unique `requestCode` values to distinguish different PendingIntents that otherwise share the same `Intent` parameters.
4. Use `FLAG_UPDATE_CURRENT` when you need to update extras of an existing PendingIntent (combined with the appropriate mutability flag).
5. When exposing PendingIntents to other apps or untrusted callers, prefer explicit Intents (with a concrete component) to reduce hijacking/forgery risks; implicit Intents can be acceptable in controlled scenarios.
6. For long-lived/repeating operations you no longer need, call `cancel()` (and cancel via the relevant manager, e.g., AlarmManager) to prevent unintended future executions.

---

## Дополнительные Вопросы (RU)

- Как `requestCode` влияет на равенство и обновление PendingIntent?
- Когда следует использовать `FLAG_MUTABLE` вместо `FLAG_IMMUTABLE`?
- Как использовать PendingIntent совместно с WorkManager для фоновых задач?
- Что произойдет, если не вызывать `cancel()` для PendingIntent после использования?
- Как отлаживать проблемы безопасности PendingIntent на Android 12+?

## Follow-ups

- How does requestCode affect PendingIntent equality and updates?
- When should you use FLAG_MUTABLE instead of FLAG_IMMUTABLE?
- How do you handle PendingIntent with WorkManager for background tasks?
- What happens if you don't cancel a PendingIntent after use?
- How to debug PendingIntent security vulnerabilities in Android 12+?

---

## Ссылки (RU)

- [[q-intent-filters-android--android--medium]] - основы `Intent`
- [[q-what-unifies-android-components--android--easy]] - компоненты Android
- https://developer.android.com/reference/android/app/PendingIntent
- https://developer.android.com/about/versions/12/behavior-changes-12#pending-intent-mutability

## References

- [[q-intent-filters-android--android--medium]] - `Intent` fundamentals
- [[q-what-unifies-android-components--android--easy]] - Android components
- https://developer.android.com/reference/android/app/PendingIntent
- https://developer.android.com/about/versions/12/behavior-changes-12#pending-intent-mutability

---

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-intent]]
- [[c-permissions]]

### Предварительные (проще)

- [[q-what-unifies-android-components--android--easy]] - основы `Intent`
- [[q-what-is-the-main-application-execution-thread--android--easy]] - поток выполнения в Android

### Связанные (средний уровень)

- [[q-intent-filters-android--android--medium]] - подробности об `Intent`
- [[q-anr-application-not-responding--android--medium]] - паттерны фоновой работы

### Продвинутые (сложнее)

- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - жизненный цикл процессов

## Related Questions

### Prerequisites / Concepts

- [[c-intent]]
- [[c-permissions]]

### Prerequisites (Easier)
- [[q-what-unifies-android-components--android--easy]] - `Intent` basics
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Android threading

### Related (Same Level)
- [[q-intent-filters-android--android--medium]] - `Intent` deep dive
- [[q-anr-application-not-responding--android--medium]] - Background work patterns

### Advanced (Harder)
- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Process lifecycle
