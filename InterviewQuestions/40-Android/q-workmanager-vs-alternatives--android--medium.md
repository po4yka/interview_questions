---\
id: android-059
title: "WorkManager vs Alternatives / WorkManager против альтернатив"
aliases: ["WorkManager vs Alternatives", "WorkManager против альтернатив"]
topic: android
subtopics: [background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-background-tasks, c-workmanager]
created: 2025-10-12
updated: 2025-11-10
tags: [android/background-execution, difficulty/medium]
sources: []
anki_cards:
  - slug: android-059-0-en
    front: "When to use WorkManager vs AlarmManager vs Foreground Service?"
    back: |
      | API | Use Case |
      |-----|----------|
      | **WorkManager** | Deferrable, guaranteed background work (default choice) |
      | **Foreground Service** | User-initiated, long-running (music, downloads) |
      | **AlarmManager** | Exact time alarms (reminders, clocks) |
      | **Coroutines** | Short-lived, app-scope work |

      **Decision flow**:
      1. Must run at exact time? -> AlarmManager
      2. User-visible, long-running? -> Foreground Service
      3. Deferrable, guaranteed? -> **WorkManager**
      4. Short, app lifecycle? -> Coroutines
    tags:
      - android_workmanager
      - difficulty::medium
  - slug: android-059-0-ru
    front: "Когда использовать WorkManager vs AlarmManager vs Foreground Service?"
    back: |
      | API | Применение |
      |-----|------------|
      | **WorkManager** | Отложенная, гарантированная фоновая работа (по умолчанию) |
      | **Foreground Service** | Пользовательская, долгая (музыка, загрузки) |
      | **AlarmManager** | Точное время (напоминания, будильники) |
      | **Coroutines** | Короткая работа, жизненный цикл приложения |

      **Алгоритм выбора**:
      1. Точное время? -> AlarmManager
      2. Видимая пользователю, долгая? -> Foreground Service
      3. Отложенная, гарантированная? -> **WorkManager**
      4. Короткая, в рамках приложения? -> Coroutines
    tags:
      - android_workmanager
      - difficulty::medium

---\
# Вопрос (RU)
> Когда использовать `WorkManager` vs AlarmManager vs JobScheduler vs Foreground `Service`?

# Question (EN)
> When to use `WorkManager` vs AlarmManager vs JobScheduler vs Foreground `Service`?

---

## Ответ (RU)

**Теория выбора API:**
Android предоставляет несколько API для фоновой работы с разными гарантиями и ограничениями. Выбор зависит от требований к таймингу, гарантиям выполнения, видимости для пользователя и лимитов фонового выполнения на современных версиях Android. Для отложенных (deferrable) задач по умолчанию рекомендуется использовать `WorkManager`.

**Критерии выбора:**

| API | Когда использовать | Ключевая особенность |
|-----|-------------------|---------------------|
| **`WorkManager`** | Отложенная надёжная работа, не требующая точного времени | Переживает перезагрузки, поддерживает ограничения, использует JobScheduler/AlarmManager/FirebaseJobDispatcher под капотом |
| **AlarmManager** | Будильники и напоминания, когда нужен запуск в конкретное время | Может будить устройство; точность обеспечивается `setExact*`, но подлежит ограничениям Doze/политик точных будильников |
| **Foreground `Service`** | Длительные задачи, ожидаемые и замечаемые пользователем (навигация, музыка, запись, фитнес-трекинг) | Обязательное постоянное уведомление; повышенный приоритет, но не абсолютная защита от убийства |
| **JobScheduler** | Низкоуровневый контроль на API 21+ в системных/легаси сценариях | Обычно не используется напрямую в обычных приложениях, т.к. `WorkManager` абстрагирует его |

**`WorkManager` — гарантированное (best-effort) выполнение:**

```kotlin
// ✅ Правильно: периодическая синхронизация с ограничениями
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ Только Wi‑Fi
    .setRequiresBatteryNotLow(true)                // ✅ Учитывать состояние батареи
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

`WorkManager` подходит для:
- отложенной/периодической работы;
- работ, которые должны быть выполнены даже после перезапуска устройства;
- работ с условиями (Wi‑Fi, зарядка и т.д.).
Не использовать для точных по времени или долго текущих операций с прямым пользовательским взаимодействием.

**AlarmManager — точный или запланированный тайминг:**

```kotlin
// ✅ Правильно: точный будильник для критичных по времени событий
val alarmManager = context.getSystemService(AlarmManager::class.java)
val pendingIntent = PendingIntent.getBroadcast(
    context, 0,
    Intent(context, AlarmReceiver::class.java),
    PendingIntent.FLAG_IMMUTABLE // ✅ Безопасность
)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP, // ✅ Может разбудить устройство
    triggerTime,
    pendingIntent
)
```

Используйте AlarmManager, когда важно срабатывание около указанного времени (например, будильник, напоминание), и последующая работа краткосрочная и запускается из приёмника/сервиса с учётом актуальных ограничений фонового выполнения. На современных версиях Android точные будильники ограничены (Doze, политика точных будильников), поэтому применять их следует только при обоснованной необходимости.

**Foreground `Service` — видимая, долгоживущая работа:**

```kotlin
// ✅ Правильно: музыкальный плеер с уведомлением
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification() // ✅ Обязательное постоянное уведомление
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY // ✅ Просит систему перезапустить сервис при убийстве, если возможно
    }
}

// ❌ Неправильно: запускать скрытую работу без уведомления
// ❌ Неправильно: использовать для быстрых/разовых фоновых операций (используй WorkManager или другие механизмы)
```

Foreground `Service` подходит для задач, о которых пользователь должен знать и которые активны продолжительное время. Сервис должен быть запущен как foreground-сервис (для API 26+ — через `startForegroundService()`), и всё равно может быть убит системой при нехватке ресурсов, поэтому "защита от kill" не абсолютна.

---

## Answer (EN)

**API Selection Theory:**
Android provides multiple APIs for background work with different guarantees and constraints. The choice depends on timing requirements, execution guarantees, user visibility, and modern background execution limits. For deferrable work, `WorkManager` is the recommended default.

**Selection Criteria:**

| API | When to Use | Key Feature |
|-----|------------|-------------|
| **`WorkManager`** | Deferrable, reliable work that does not require exact timing | Survives reboots, supports constraints, built on JobScheduler/AlarmManager/FirebaseJobDispatcher internally |
| **AlarmManager** | Alarms/reminders when you need to run at a specific time | Can wake the device; precision via `setExact*`, but subject to Doze and exact alarm restrictions |
| **Foreground `Service`** | `Long`-running tasks expected and noticed by the user (navigation, music, recording, fitness tracking) | Mandatory ongoing notification; elevated priority, but not absolute kill protection |
| **JobScheduler** | Low-level scheduling on API 21+ for system/legacy use cases | Typically not used directly in modern apps because `WorkManager` abstracts it |

**`WorkManager` — guaranteed (best-effort) execution:**

```kotlin
// ✅ Correct: periodic sync with constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ Wi‑Fi only
    .setRequiresBatteryNotLow(true)                // ✅ Respect battery state
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

`WorkManager` is suitable for:
- deferrable/periodic work;
- work that should run even after device reboot;
- work with constraints (Wi‑Fi, charging, etc.).
Do not use it for exact-time triggers or long-running, user-interactive operations.

**AlarmManager — exact or scheduled timing:**

```kotlin
// ✅ Correct: exact alarm for time-critical events
val alarmManager = context.getSystemService(AlarmManager::class.java)
val pendingIntent = PendingIntent.getBroadcast(
    context, 0,
    Intent(context, AlarmReceiver::class.java),
    PendingIntent.FLAG_IMMUTABLE // ✅ Security
)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP, // ✅ Can wake the device
    triggerTime,
    pendingIntent
)
```

Use AlarmManager when you need execution around a specific clock time (e.g., alarm clock, reminder), and ensure the actual follow-up work is short-lived and launched from the receiver/service in compliance with current background execution limits. On modern Android versions, exact alarms are restricted (Doze, exact alarm policies), so use them only when strictly justified.

**Foreground `Service` — visible, long-running work:**

```kotlin
// ✅ Correct: music player with notification
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification() // ✅ Mandatory ongoing notification
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY // ✅ Requests restart after kill when possible
    }
}

// ❌ Wrong: using for hidden work without a notification
// ❌ Wrong: using for quick/one-off background operations (use WorkManager or other mechanisms instead)
```

Foreground `Service` is appropriate for tasks the user expects and that run for a noticeable duration. The service must run as a foreground service (for API 26+ typically started via `startForegroundService()`), and it still can be killed under memory pressure; "kill protection" is not absolute.

---

## Follow-ups (RU)

- Как `WorkManager` обрабатывает ограничения на разных версиях Android (API 14+ vs 23+ vs 26+)?
- Каковы последствия для батареи у каждого подхода и как на них влияет режим Doze?
- Как выполнять миграцию с устаревших API JobScheduler или AlarmManager на `WorkManager`?
- Когда имеет смысл комбинировать несколько подходов (например, `WorkManager` + Foreground `Service`)?
- Каковы компромиссы между точными будильниками и неточными (окно запуска) с точки зрения батареи?

## References (RU)

- [[c-workmanager]] — концепция `WorkManager`
- [Документация WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Ограничения фонового выполнения](https://developer.android.com/about/versions/oreo/background)
- [Планирование задач с WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/basics)

## Related Questions (RU)

### База (проще)
- [[q-android-app-components--android--easy]] — Компоненты приложения

### Связанные (тот Же уровень)
- [[q-workmanager-return-result--android--medium]] — Результаты `WorkManager`
- [[q-foreground-service-types--android--medium]] — Типы foreground-сервисов

### Продвинутые (сложнее)
- [[q-workmanager-advanced--android--medium]] — Продвинутый `WorkManager`
- [[q-android-runtime-internals--android--hard]] — Внутреннее устройство Runtime

---

## Follow-ups

- How does `WorkManager` handle constraints on different Android versions (API 14+ vs 23+ vs 26+)?
- What are the battery optimization implications of each approach, and how does Doze mode affect them?
- How do you migrate from deprecated JobScheduler or AlarmManager APIs to `WorkManager`?
- When would you combine multiple approaches (e.g., `WorkManager` + Foreground `Service`)?
- What are the trade-offs between exact alarms and inexact window-based alarms for battery life?

## References

- [[c-workmanager]] - `WorkManager` concept
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Background Execution Limits](https://developer.android.com/about/versions/oreo/background)
- [Schedule Tasks with WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/basics)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-workmanager-return-result--android--medium]] - `WorkManager` results
- [[q-foreground-service-types--android--medium]] - Foreground services

### Advanced (Harder)
- [[q-workmanager-advanced--android--medium]] - Advanced `WorkManager`
- [[q-android-runtime-internals--android--hard]] - Runtime internals
