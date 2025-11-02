---
id: android-144
title: "When Can The System Restart A Service / Когда система может перезапустить Service"
aliases: ["When Can The System Restart A Service", "Когда система может перезапустить Service"]
topic: android
subtopics: [service, lifecycle, background-execution]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-service, c-lifecycle, q-android-service-types--android--easy]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags:
  - android
  - android/service
  - android/lifecycle
  - android/background-execution
  - difficulty/medium
date created: Monday, October 27th 2025, 3:47:51 pm
date modified: Thursday, October 30th 2025, 3:18:09 pm
---

# Вопрос (RU)

> Когда система может перезапустить сервис?

# Question (EN)

> When can the system restart a service?

---

## Ответ (RU)

Система Android может автоматически перезапустить сервис после его уничтожения в зависимости от возвращаемого значения `onStartCommand()` и типа сервиса.

### Режимы перезапуска

**START_STICKY** — система перезапустит сервис, но Intent будет null:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Подходит для музыкальных плееров
        setupMediaPlayer()
        return START_STICKY // Intent будет null при перезапуске
    }
}
```

**START_REDELIVER_INTENT** — система перезапустит сервис и повторно доставит последний Intent:

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val fileUrl = intent?.getStringExtra("file_url")
        fileUrl?.let { downloadFile(it) }

        return START_REDELIVER_INTENT // ✅ Для критичных задач
    }
}
```

**START_NOT_STICKY** — система НЕ перезапустит сервис автоматически:

```kotlin
class OneTimeTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performTask()
        return START_NOT_STICKY // ❌ Не перезапускается
    }
}
```

### Foreground-сервисы

Foreground-сервисы имеют наивысший приоритет и редко уничтожаются системой:

```kotlin
class MusicService : Service() {
    override fun onCreate() {
        super.onCreate()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ Высокий приоритет
    }
}
```

### Условия перезапуска

- Снижается нагрузка на память
- Сервис имеет высокий приоритет (foreground)
- Есть ожидающие Intent (для START_NOT_STICKY)

### Обработка null Intent

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    if (intent == null) {
        // ✅ Сервис перезапущен системой
        initializeDefaultState()
    } else {
        processIntent(intent)
    }
    return START_STICKY
}
```

### Сравнение режимов

| Режим | Перезапуск | Intent | Применение |
|-------|------------|--------|------------|
| START_STICKY | Да | Null | Музыка, мониторинг |
| START_REDELIVER_INTENT | Да | Повторно | Загрузки, синхронизация |
| START_NOT_STICKY | Нет | — | Одноразовые задачи |
| Foreground + STICKY | Да (приоритет) | Null | Видимая работа |

**Современная альтернатива:** [[c-workmanager]] для фоновых задач вместо сервисов.

## Answer (EN)

The Android system can automatically restart a service after it has been killed, depending on the return value from `onStartCommand()` and the service type.

### Restart Modes

**START_STICKY** — system restarts the service, but Intent will be null:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Good for music players
        setupMediaPlayer()
        return START_STICKY // Intent will be null on restart
    }
}
```

**START_REDELIVER_INTENT** — system restarts the service and redelivers the last Intent:

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val fileUrl = intent?.getStringExtra("file_url")
        fileUrl?.let { downloadFile(it) }

        return START_REDELIVER_INTENT // ✅ For critical tasks
    }
}
```

**START_NOT_STICKY** — system does NOT restart the service automatically:

```kotlin
class OneTimeTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performTask()
        return START_NOT_STICKY // ❌ Will not restart
    }
}
```

### Foreground Services

Foreground services have the highest priority and are rarely killed by the system:

```kotlin
class MusicService : Service() {
    override fun onCreate() {
        super.onCreate()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ High priority
    }
}
```

### Restart Conditions

- Memory pressure decreases
- Service has high priority (foreground)
- Pending Intents exist (for START_NOT_STICKY)

### Handling Null Intent

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    if (intent == null) {
        // ✅ Service restarted by system
        initializeDefaultState()
    } else {
        processIntent(intent)
    }
    return START_STICKY
}
```

### Mode Comparison

| Mode | Restarts | Intent | Use Case |
|------|----------|--------|----------|
| START_STICKY | Yes | Null | Music, monitoring |
| START_REDELIVER_INTENT | Yes | Redelivered | Downloads, sync |
| START_NOT_STICKY | No | — | One-time tasks |
| Foreground + STICKY | Yes (priority) | Null | User-visible work |

**Modern alternative:** [[c-workmanager]] for background work instead of services.

## Follow-ups

- How does JobScheduler differ from Service restart mechanisms?
- What happens to pending Intents when a service is killed with START_NOT_STICKY?
- How can you implement idempotent operations when using START_REDELIVER_INTENT?
- What are the foreground service type restrictions and how do they affect restart behavior?

## References

- [[c-service]] — Service component concepts
- [[c-lifecycle]] — Android lifecycle fundamentals
- [[c-workmanager]] — Modern alternative for background work
- https://developer.android.com/guide/components/services

## Related Questions

### Prerequisites

- [[q-android-service-types--android--easy]] — Understanding service types

### Related

- [[q-service-component--android--medium]] — Service component details
- [[q-foreground-service-types--android--medium]] — Foreground service types
- [[q-keep-service-running-background--android--medium]] — Keeping services alive
- [[q-background-vs-foreground-service--android--medium]] — Service comparison

### Advanced

- [[q-service-lifecycle-binding--android--hard]] — Service lifecycle and binding
