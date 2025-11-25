---
id: android-144
title: "When Can The System Restart A Service / Когда система может перезапустить Service"
aliases: ["When Can The System Restart A Service", "Когда система может перезапустить Service"]
topic: android
subtopics: [background-execution, lifecycle, service]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-lifecycle, c-service, q-android-service-types--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/background-execution, android/lifecycle, android/service, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:10 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Когда система может перезапустить сервис?

# Question (EN)

> When can the system restart a service?

---

## Ответ (RU)

Система Android может попытаться автоматически перезапустить "запущенный" сервис (started service), если он был уничтожен системой из-за нехватки ресурсов, в зависимости от значения, которое возвращает `onStartCommand()`, и типа сервиса. Если сервис/приложение был явно остановлен (например, `stopSelf()`, `stopService()`, пользователь сделал Force Stop приложения), система его не перезапустит, независимо от режима. Простое "смахивание" задачи из Overview обычно завершает процесс, но не является гарантированным механизмом остановки для всех сервисов (например, foreground-сервис с уведомлением может продолжить работу или быть восстановлен в соответствии с режимом).

Режимы ниже относятся к started-сервисам (работающим через `startService()` / `startForegroundService()` и `onStartCommand()`), а не к чисто bound-сервисам. Чисто bound-сервисы существуют, пока есть активные клиенты, и не перезапускаются системой после потери всех связей.

### Режимы Перезапуска

**START_STICKY** — при убийстве сервисного процесса системой сервис может быть воссоздан, и `onStartCommand()` будет вызван снова, но `intent` при повторном запуске будет `null`:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Подходит для долгоживущих задач, например, музыкальных плееров
        setupMediaPlayer()
        return START_STICKY // При перезапуске система вызовет onStartCommand с intent = null
    }
}
```

**START_REDELIVER_INTENT** — при убийстве процесса системой сервис может быть перезапущен, и последний ещё не завершённо обработанный `Intent` (или несколько таких `Intent`-ов) будет повторно доставлен, чтобы задача могла быть завершена:

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val fileUrl = intent?.getStringExtra("file_url")
        fileUrl?.let { downloadFile(it) }

        return START_REDELIVER_INTENT // ✅ Для критичных задач, которые должны быть доведены до конца
    }
}
```

**START_NOT_STICKY** — если процесс с сервисом был убит системой, сервис обычно НЕ будет перезапущен автоматически. Однако если после этого придёт новый `Intent` (новый вызов `startService()`), сервис будет запущен заново уже в ответ на этот новый запрос:

```kotlin
class OneTimeTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performTask()
        return START_NOT_STICKY // ❌ Сам по себе не перезапускается после убийства процесса системой
    }
}
```

### Foreground-сервисы

Foreground-сервисы запускаются через `startForegroundService()` (на современных версиях) и обязаны вызвать `startForeground(...)` в пределах ограниченного времени. Они имеют более высокий приоритет и реже уничтожаются системой, но это НЕ гарантирует, что они не будут убиты или что они всегда будут перезапущены. Фактическое поведение при перезапуске по-прежнему определяется значением, возвращаемым `onStartCommand()`.

```kotlin
class MusicService : Service() {
    override fun onCreate() {
        super.onCreate()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ Повышенный приоритет, но без гарантии вечной работы
    }
}
```

### Условия Перезапуска (упрощённо)

Система может попытаться перезапустить сервис (в соответствии с режимом `onStartCommand()`), если:

- ранее сервис был убит именно системой из-за нехватки ресурсов/давления на память;
- впоследствии ресурсы стали доступны, и система решила восстановить процесс;
- режим `START_STICKY` или `START_REDELIVER_INTENT` позволяет перезапуск (для `START_NOT_STICKY` — только при новом входящем `Intent`);
- это started-сервис, не остановленный явно (включая отсутствие Force Stop приложения пользователем).

Важно: поведение недетерминированное и зависит от политики планировщика, версии Android и текущей нагрузки.

### Обработка Null `Intent`

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    if (intent == null) {
        // ✅ Сервис перезапущен системой в режиме START_STICKY
        initializeDefaultState()
    } else {
        processIntent(intent)
    }
    return START_STICKY
}
```

### Сравнение Режимов

| Режим | Перезапуск при убийстве системой | `Intent` при перезапуске | Типичные случаи |
|-------|-----------------------------------|--------------------------|------------------|
| START_STICKY | Может быть перезапущен | null | Музыка, мониторинг состояний |
| START_REDELIVER_INTENT | Может быть перезапущен | Повторно доставлен (необработанные) | Загрузки, синхронизация |
| START_NOT_STICKY | Нет автоперезапуска (только при новом `Intent`) | — | Одноразовые/некритичные задачи |
| Foreground + STICKY | Меньше шанс быть убитым, возможен перезапуск | Обычно null | Долгая пользовательски видимая работа |

**Современная альтернатива:** [[c-workmanager]] для отложенных и гарантированных фоновых задач вместо прямого использования started-сервисов.

## Answer (EN)

The Android system may attempt to restart a "started" service if its process was killed by the system due to resource constraints, depending on the value returned from `onStartCommand()` and the service type. If the service/app is explicitly stopped (e.g., `stopSelf()`, `stopService()`, user performs a Force Stop), the system will not restart it regardless of the mode. Simply swiping the task away from Overview usually terminates the process, but is not a reliable/guaranteed explicit stop for all services (for example, a proper foreground service with a notification may continue or be recreated according to its restart mode).

The modes below apply to started services (using `startService()` / `startForegroundService()` and `onStartCommand()`), not to purely bound-only services. A purely bound service lives only while it has active clients; once all clients are gone, it is destroyed and is not automatically restarted by the system.

### Restart Modes

**START_STICKY** — when the process is killed by the system, it may recreate the service and call `onStartCommand()` again, but the restart `intent` will be `null`:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Good for long-running tasks such as music playback
        setupMediaPlayer()
        return START_STICKY // On restart, onStartCommand will be invoked with intent = null
    }
}
```

**START_REDELIVER_INTENT** — when the process is killed by the system, it may restart the service and redeliver the last not-yet-completely-processed `Intent` (or several such intents), allowing completion of the work:

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val fileUrl = intent?.getStringExtra("file_url")
        fileUrl?.let { downloadFile(it) }

        return START_REDELIVER_INTENT // ✅ For critical tasks that must be finished
    }
}
```

**START_NOT_STICKY** — if the process hosting the service is killed by the system, it generally does NOT restart the service automatically. If a new `Intent` arrives later (a new `startService()` call), the service will start again in response to that new request:

```kotlin
class OneTimeTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performTask()
        return START_NOT_STICKY // ❌ No automatic restart after kill by the system
    }
}
```

### Foreground Services

Foreground services are typically started with `startForegroundService()` (on modern Android) and must call `startForeground(...)` within a short window. They have higher priority and are less likely to be killed by the system, but this does NOT guarantee that they will never be killed or that they will always be restarted. Actual restart behavior still depends on the value returned from `onStartCommand()` and system conditions.

```kotlin
class MusicService : Service() {
    override fun onCreate() {
        super.onCreate()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ Higher priority, but no guarantee of immortality
    }
}
```

### Restart Conditions (high level)

The system may attempt to restart the service (according to the `onStartCommand()` mode) when:

- the service was previously killed by the system due to memory/CPU pressure;
- resources later become available and the system decides to recreate the process;
- the return mode is `START_STICKY` or `START_REDELIVER_INTENT` (for `START_NOT_STICKY`, only if a new incoming `Intent` triggers a new start);
- it is a started service that has not been explicitly stopped (including no user Force Stop on the app).

This behavior is best-effort and non-deterministic; it depends on Android version, system policies, and current load.

### Handling Null `Intent`

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    if (intent == null) {
        // ✅ Service was restarted by the system in START_STICKY mode
        initializeDefaultState()
    } else {
        processIntent(intent)
    }
    return START_STICKY
}
```

### Mode Comparison

| Mode | Restart on system kill | `Intent` on restart | Use Case |
|------|------------------------|---------------------|----------|
| START_STICKY | May be restarted | null | Music, monitoring |
| START_REDELIVER_INTENT | May be restarted | Redelivered (pending) | Downloads, sync |
| START_NOT_STICKY | No auto-restart (only on new `Intent`) | — | One-time / non-critical tasks |
| Foreground + STICKY | Less likely to be killed, may restart | Typically null | Long-running user-visible work |

**Modern alternative:** [[c-workmanager]] for deferred and guaranteed background work instead of direct long-running started services where appropriate.

## Follow-ups

- How does JobScheduler differ from `Service` restart mechanisms?
- What happens to pending Intents when a service is killed with START_NOT_STICKY?
- How can you implement idempotent operations when using START_REDELIVER_INTENT?
- What are the foreground service type restrictions and how do they affect restart behavior?

## References

- [[c-service]] — `Service` component concepts
- [[c-lifecycle]] — Android lifecycle fundamentals
- [[c-workmanager]] — Modern alternative for background work
- https://developer.android.com/guide/components/services

## Related Questions

### Prerequisites

- [[q-android-service-types--android--easy]] — Understanding service types

### Related

- [[q-service-component--android--medium]] — `Service` component details
- [[q-foreground-service-types--android--medium]] — Foreground service types
- [[q-keep-service-running-background--android--medium]] — Keeping services alive
- [[q-background-vs-foreground-service--android--medium]] — `Service` comparison

### Advanced

- [[q-service-lifecycle-binding--android--hard]] — `Service` lifecycle and binding
