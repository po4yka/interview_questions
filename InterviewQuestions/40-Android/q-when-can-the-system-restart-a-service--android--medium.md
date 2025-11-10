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

---

# Вопрос (RU)

> Когда система может перезапустить сервис?

# Question (EN)

> When can the system restart a service?

---

## Ответ (RU)

Система Android может попытаться автоматически перезапустить "запущенный" сервис (started service), если он был уничтожен системой из-за нехватки ресурсов, в зависимости от значения, которое возвращает `onStartCommand()`, и типа сервиса. Если сервис/приложение был явно остановлен (например, `stopSelf()`, `stopService()`, пользователь закрыл приложение и удалил задачу/"смахнул" из Overview), система его не перезапустит, независимо от режима.

Режимы ниже относятся к started-сервисам (работающим через `startService()` / `startForegroundService()` и `onStartCommand()`), а не к чисто bound-сервисам.

### Режимы перезапуска

**START_STICKY** — при убийстве сервисного процесса системой сервис может быть воссоздан, но `intent` при повторном запуске будет `null`:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Подходит для долгоживущих задач, например, музыкальных плееров
        setupMediaPlayer()
        return START_STICKY // При перезапуске система вызовет onStartCommand с intent = null
    }
}
```

**START_REDELIVER_INTENT** — при убийстве процесса система может перезапустить сервис и повторно доставить последний `Intent` (или очередь `Intent`-ов), чтобы задача могла быть завершена:

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
        return START_NOT_STICKY // ❌ Сам по себе не перезапускается после убийства процесса
    }
}
```

### Foreground-сервисы

Foreground-сервисы запускаются через `startForegroundService()` (на современных версиях) и обязаны вызвать `startForeground(...)` в пределах ограниченного времени. Они имеют более высокий приоритет и реже уничтожаются системой, но это НЕ гарантирует, что они не будут убиты и автоматически перезапущены.

```kotlin
class MusicService : Service() {
    override fun onCreate() {
        super.onCreate()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ Повышенный приоритет, но без гарантии вечной работы
    }
}
```

### Условия перезапуска (упрощённо)

Система может попытаться перезапустить сервис (в соответствии с режимом `onStartCommand()`), если:

- ранее сервис был убит именно системой из-за нехватки ресурсов;
- впоследствии ресурсы стали доступны, и система решила восстановить процесс;
- режим `START_STICKY` или `START_REDELIVER_INTENT` позволяет перезапуск (для `START_NOT_STICKY` — только при новом входящем `Intent`);
- это started-сервис, не остановленный явно.

Важно: поведение не детерминированное и зависит от политики планировщика, версии Android и текущей нагрузки.

### Обработка null `Intent`

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

### Сравнение режимов

| Режим | Перезапуск при убийстве системой | `Intent` при перезапуске | Типичные случаи |
|-------|-----------------------------------|--------------------------|------------------|
| START_STICKY | Может быть перезапущен | null | Музыка, мониторинг состояний |
| START_REDELIVER_INTENT | Может быть перезапущен | Повторно доставлен | Загрузки, синхронизация |
| START_NOT_STICKY | Нет автоперезапуска (только при новом `Intent`) | — | Одноразовые/некритичные задачи |
| Foreground + STICKY | Меньше шанс быть убитым, возможен перезапуск | Обычно null | Долгая пользовательски видимая работа |

**Современная альтернатива:** [[c-workmanager]] для отложенных и гарантированных фоновых задач вместо прямого использования started-сервисов.

## Answer (EN)

The Android system may attempt to restart a "started" service if its process was killed by the system due to resource constraints, depending on the value returned from `onStartCommand()` and the service type. If the service/app is explicitly stopped (e.g., `stopSelf()`, `stopService()`, user force stop, or task swipe-away with no ongoing foreground work), the system will not restart it regardless of the mode.

The modes below apply to started services (using `startService()` / `startForegroundService()` and `onStartCommand()`), not to purely bound-only services.

### Restart Modes

**START_STICKY** — when the process is killed, the system may recreate the service and call `onStartCommand()` again with a `null` intent:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Good for long-running tasks such as music playback
        setupMediaPlayer()
        return START_STICKY // On restart, onStartCommand will be invoked with intent = null
    }
}
```

**START_REDELIVER_INTENT** — when the process is killed, the system may restart the service and redeliver the last `Intent` (or pending intents), allowing completion of the work:

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val fileUrl = intent?.getStringExtra("file_url")
        fileUrl?.let { downloadFile(it) }

        return START_REDELIVER_INTENT // ✅ For critical tasks that must be finished
    }
}
```

**START_NOT_STICKY** — if the process hosting the service is killed, the system generally does NOT restart the service automatically. If a new `Intent` arrives later (a new `startService()` call), the service will start again in response to that new request:

```kotlin
class OneTimeTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performTask()
        return START_NOT_STICKY // ❌ No automatic restart after kill by the system
    }
}
```

### Foreground Services

Foreground services are typically started with `startForegroundService()` (on modern Android) and must call `startForeground(...)` within a short window. They have higher priority and are less likely to be killed by the system, but this does NOT guarantee that they will never be killed or that they will always be restarted.

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
- it is a started service that was not explicitly stopped.

This behavior is best-effort and non-deterministic; it depends on Android version, system policies, and current load.

### Handling null `Intent`

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
| START_REDELIVER_INTENT | May be restarted | Redelivered | Downloads, sync |
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
