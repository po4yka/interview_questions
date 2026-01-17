---\
id: android-147
title: Raise Process Priority / Повышение приоритета процесса
aliases: [Raise Process Priority, Повышение приоритета процесса]
topic: android
subtopics: [lifecycle, processes, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-components, c-lifecycle, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-how-application-priority-is-determined-by-the-system--android--hard, q-network-operations-android--android--medium, q-what-events-are-activity-methods-tied-to--android--medium]
created: 2024-10-15
updated: 2025-11-10
sources: []
tags: [android/lifecycle, android/processes, android/service, difficulty/medium, foreground-service, lifecycle, process-priority, services]
anki_cards:
  - slug: android-147-0-en
    front: "How can you raise process priority in Android?"
    back: |
      **Yes**, indirectly via **foreground service** with `startForeground()`.

      **Process priority levels (high to low):**
      1. Foreground - active UI, foreground service
      2. Visible - visible but not focused
      3. Service - background service
      4. Cached - recently used, no active components
      5. Empty - killed first

      **Requirements:**
      - Must show notification
      - Call `startForeground()` within ~5 seconds
      - Declare `foregroundServiceType` on Android 10+

      Cannot directly change Linux nice/priority.
    tags:
      - android_lifecycle
      - difficulty::medium
  - slug: android-147-0-ru
    front: "Как можно повысить приоритет процесса в Android?"
    back: |
      **Да**, косвенно через **foreground service** с `startForeground()`.

      **Уровни приоритета процессов (от высшего к низшему):**
      1. Foreground - активный UI, foreground service
      2. Visible - видим, но не в фокусе
      3. Service - фоновый сервис
      4. Cached - недавно использованный, без активных компонентов
      5. Empty - убивается первым

      **Требования:**
      - Обязательно показывать уведомление
      - Вызвать `startForeground()` в течение ~5 секунд
      - Указать `foregroundServiceType` на Android 10+

      Нельзя напрямую менять Linux nice/priority.
    tags:
      - android_lifecycle
      - difficulty::medium

---\
# Вопрос (RU)

> Можно ли поднять приоритет процесса в Android?

# Question (EN)

> Can you raise the priority of a process in Android?

---

## Ответ (RU)

**Да**, можно повысить "важность" процесса (его приоритетную категорию в системе) косвенно, запуская **foreground service** через **`startForeground()`** или удерживая в процессе компоненты, которые система считает важными (activity на переднем плане, bound service и т.п.). Напрямую управлять уровнем приоритета процесса на уровне Linux (`nice`/`renice`) для обычного приложения нельзя.

В случае foreground service процесс переводится в более высокую категорию важности и становится значительно менее подвержен уничтожению при нехватке памяти, хотя **полной гарантии сохранения процесса нет**.

### Уровни Приоритета Процессов (упрощённо)

Android использует иерархию важности процессов для принятия решений об освобождении памяти (ниже приведена упрощённая схема, реальные категории и эвристики чуть детальнее):

1. **Foreground Process** (наивысший) — активная activity на переднем плане, foreground service, или компонент, выполняющий важную/видимую для пользователя работу
2. **Visible/Perceptible Process** — видим для пользователя, но не в фокусе, или выполняет пользовательски заметную работу
3. **`Service` Process** — обычный фоновый сервис без foreground-уведомления
4. **Cached Process** — недавно использованный, без активных компонентов
5. **Empty Process** (наименьший приоритет) — убивается первым при нехватке памяти

При нехватке памяти система убивает процессы, начиная с наименее важных.

### Foreground `Service` (высокий приоритет)

```kotlin
class DownloadService : Service() {
    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Повышаем важность процесса через foreground service
        startForeground(NOTIFICATION_ID, createNotification())

        // Долгая задача теперь значительно лучше защищена от убийства системой
        performDownload()

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        // Android 8.0+ требует канал уведомлений
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "Downloads", NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Запуск Foreground `Service`

```kotlin
// Android 8.0+ требует startForegroundService() при запуске из фона
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(Intent(this, DownloadService::class.java))
} else {
    startService(Intent(this, DownloadService::class.java))
}
```

**Важно:** На Android 8.0+ необходимо вызвать `startForeground()` в течение примерно **5 секунд** после `startForegroundService()`; иначе система остановит сервис (и может выбросить `IllegalStateException` или убить процесс). Это требование относится к сервисам, запущенным как foreground.

### Когда Использовать

**✅ Используйте** foreground service для:
- Воспроизведения музыки
- Навигации/отслеживания местоположения
- Активного фитнес-трекинга
- Скачивания файлов (инициировано пользователем)

**❌ НЕ используйте** для:
- Простых фоновых задач (используйте `WorkManager`)
- Периодической синхронизации (используйте JobScheduler / `WorkManager`)

### Другие Способы Влияния На Приоритет

**Bound `Service` с foreground/visible activity:**
```kotlin
// Важность процесса с сервисом повышается, пока на него ссылается компонент с высокой важностью
bindService(Intent(this, MyService::class.java), connection, BIND_AUTO_CREATE)
```

Процесс с bound service получает более высокий приоритет, если на сервис ссылаются компоненты с высокой важностью (например, foreground/visible activity). Это не "наследование приоритета" через явный API, а результат правил системы, учитывающих важность вызывающей стороны и тип привязки.

**JobScheduler priority hint (API 26+):**
```kotlin
// ❌ Priority здесь — подсказка для планировщика (реализация и доступность зависят от версии/устройства), не гарантия важности процесса
val job = JobInfo.Builder(JOB_ID, componentName)
    .setPriority(JobInfo.PRIORITY_HIGH)
    .build()
```

### Ограничения

1. **Обязательное уведомление** — foreground service обязан показывать уведомление; нельзя скрыть долгую работу сервиса от пользователя.
2. **Ограничения Android 12+** — запуск foreground service из фона в общем случае запрещён; существуют документированные исключения (например, отдельные типы foreground service и определённые сценарии), их нужно учитывать.
3. **Тип сервиса (Android 10+)** — для некоторых сценариев необходимо указать `foregroundServiceType` в манифесте (и это обязательно для определённых типов/разрешений); в остальных случаях это рекомендуется для корректного поведения.

```xml
<service
    android:name=".LocationService"
    android:foregroundServiceType="location" />
```

### Best Practices

- Используйте foreground service только когда это **действительно необходимо** и оправдано пользовательским сценарием.
- Всегда вызывайте `stopForeground(STOP_FOREGROUND_REMOVE)` и останавливайте сервис по завершении задачи.
- Указывайте корректный `foregroundServiceType` на Android 10+ для соответствующих кейсов.
- Рассмотрите `WorkManager` для отложенных / периодических задач вместо удержания высокого приоритета процесса.

---

## Answer (EN)

**Yes**, you can indirectly raise a process's importance (its priority class in the system) by running components that the framework treats as important, most notably a **foreground service** via **`startForeground()`**, or by keeping foreground/visible UI or bound services in that process. You cannot directly change the underlying Linux process priority (like `nice/renice`) for a regular app.

When using a foreground service, the hosting process is moved into a higher-importance bucket and becomes much less likely to be killed under memory pressure, though **this is not an absolute guarantee**.

### Process Priority Levels (simplified)

Android uses a process importance hierarchy for memory management decisions (simplified; real categories and heuristics are more detailed):

1. **Foreground Process** (highest) — activity in the foreground, foreground service, or other components doing visible/critical user work
2. **Visible/Perceptible Process** — visible to the user but not in focus, or doing user-perceptible work
3. **`Service` Process** — background service without a foreground notification
4. **Cached Process** — recently used, no active components
5. **Empty Process** (lowest) — killed first under memory pressure

On low memory, the system kills from the least important upwards.

### Foreground `Service` (high priority)

```kotlin
class DownloadService : Service() {
    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Raise process importance via foreground service
        startForeground(NOTIFICATION_ID, createNotification())

        // Long-running task is now significantly better protected from being killed
        performDownload()

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        // Android 8.0+ requires notification channel
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "Downloads", NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Starting Foreground `Service`

```kotlin
// On Android 8.0+ use startForegroundService() when starting from the background
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(Intent(this, DownloadService::class.java))
} else {
    startService(Intent(this, DownloadService::class.java))
}
```

**Important:** On Android 8.0+, you must call `startForeground()` within roughly **5 seconds** after `startForegroundService()`; otherwise the system will stop the service (and may throw `IllegalStateException` or kill the process). This applies to services started as foreground services.

### When to Use

**✅ Use** foreground service for:
- Music playback
- Navigation/location tracking
- Active fitness tracking
- User-initiated file downloads

**❌ DON'T use** for:
- Simple background work (use `WorkManager`)
- Periodic sync (use JobScheduler / `WorkManager`)

### Other Ways to Influence Priority

**Bound `Service` with foreground/visible activity:**
```kotlin
// Process importance is raised while a high-importance component (e.g., foreground/visible activity) is bound to the service
bindService(Intent(this, MyService::class.java), connection, BIND_AUTO_CREATE)
```

A process hosting a bound service gets higher importance when it is bound to by high-importance components (e.g., a foreground activity). This is not a literal "priority inheritance" API, but the effect of the system's importance rules based on the caller's importance and binding type.

**JobScheduler priority hint (API 26+):**
```kotlin
// ❌ Priority here is only a scheduler hint (implementation and availability vary by version/device), not a guarantee of process importance
val job = JobInfo.Builder(JOB_ID, componentName)
    .setPriority(JobInfo.PRIORITY_HIGH)
    .build()
```

### Limitations

1. **Notification required** — a foreground service must show a notification; you cannot hide long-running work from the user.
2. **Android 12+ restrictions** — generally you cannot start a foreground service from the background; there are specific documented exceptions (including certain foreground service types and scenarios) that must be respected.
3. **`Service` type (Android 10+)** — for some use cases you must declare `foregroundServiceType` in the manifest (mandatory for certain types/permissions); in other cases it is recommended for correct behavior.

```xml
<service
    android:name=".LocationService"
    android:foregroundServiceType="location" />
```

### Best Practices

- Use a foreground service only when **truly necessary** and justified by user-visible work.
- Always call `stopForeground(STOP_FOREGROUND_REMOVE)` and stop the service when the task is complete.
- Declare the correct `foregroundServiceType` on Android 10+ where applicable.
- Prefer `WorkManager` for deferrable / periodic tasks instead of artificially holding a high process priority.

---

## Дополнительные Вопросы (RU)

- Что произойдет, если не вызвать `startForeground()` в течение 5 секунд на Android 8.0+?
- Чем приоритет bound service отличается от foreground service?
- Когда следует выбрать `WorkManager` вместо foreground service?
- Какие типы foreground service существуют и как они связаны с разрешениями?

## Follow-ups

- What happens if you don't call `startForeground()` within 5 seconds on Android 8.0+?
- How does bound service priority differ from foreground service priority?
- When should you choose `WorkManager` over foreground service?
- What foreground service types are available and how do they affect permissions?

## Ссылки (RU)

- Официальная документация Android: Services и Foreground Services
- Официальная документация Android: Process и `Application` `Lifecycle`

## References

- Android Documentation: Services and Foreground Services
- Android Documentation: Process and `Application` `Lifecycle`

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-android-components]]
- [[c-lifecycle]]

### Предварительные Вопросы
- [[q-what-events-are-activity-methods-tied-to--android--medium]] — понимание жизненного цикла `Activity` помогает при работе с сервисами

### Связанные Вопросы
- [[q-network-operations-android--android--medium]] — типичный кейс фоновых сервисов

### Продвинутое
- Рассмотрите bound services, подсказки приоритета в JobScheduler и ограничения на запуск из фона в Android 12+

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]
- [[c-lifecycle]]

### Prerequisites
- [[q-what-events-are-activity-methods-tied-to--android--medium]] — understanding `Activity` lifecycle helps with service lifecycle

### Related
- [[q-network-operations-android--android--medium]] — common use case for background services

### Advanced
- Consider bound services, JobScheduler priority hints, and Android 12+ background launch restrictions
