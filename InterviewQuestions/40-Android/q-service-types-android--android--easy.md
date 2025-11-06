---
id: android-340
title: "Service Types Android / Типы Service в Android"
aliases: ["Service Types Android", "Типы Service в Android"]

# Classification
topic: android
subtopics: [background-execution, service]
question_kind: android
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-four-main-components-of-android--android--easy]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags (EN only; no leading #)
tags: [android/background-execution, android/service, background-tasks, difficulty/easy]
---

# Вопрос (RU)

Какие существуют типы Service в Android?

# Question (EN)

What types of Service exist in Android?

---

## Ответ (RU)

В Android существуют три основных типа Service:

### 1. Foreground Service

Выполняет операции, видимые пользователю, и **обязан** отображать постоянное уведомление (persistent notification). Используется для задач, о которых пользователь должен знать: воспроизведение музыки, навигация, отслеживание тренировки.

```kotlin
// ✅ Правильно: запуск Foreground Service с уведомлением
val notification = createNotification()
startForeground(NOTIFICATION_ID, notification)
```

### 2. Background Service

Выполняет операции, не требующие прямого взаимодействия с пользователем: синхронизация данных, загрузка файлов.

**Критическое ограничение**: с Android 8.0 (API 26) система жёстко ограничивает Background Services для приложений в фоне. Рекомендуется использовать WorkManager или Foreground Service.

```kotlin
// ❌ Неправильно: Background Service ограничен с API 26+
startService(Intent(this, BackgroundService::class.java))

// ✅ Правильно: использовать WorkManager
val request = OneTimeWorkRequestBuilder<SyncWorker>().build()
WorkManager.getInstance(context).enqueue(request)
```

### 3. Bound Service

Предоставляет интерфейс для взаимодействия с другими компонентами через `bindService()`. Работает только пока к нему привязан хотя бы один клиент.

```kotlin
// ✅ Пример Bound Service
class LocalService : Service() {
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): LocalService = this@LocalService
    }

    override fun onBind(intent: Intent): IBinder = binder
}
```

**Важно**: IntentService устарел (deprecated с API 30). Для последовательного выполнения задач используйте WorkManager.

## Answer (EN)

Android has three main types of Service:

### 1. Foreground Service

Performs user-visible operations and **must** display a persistent notification. Used for tasks the user should be aware of: music playback, navigation, workout tracking.

```kotlin
// ✅ Correct: start Foreground Service with notification
val notification = createNotification()
startForeground(NOTIFICATION_ID, notification)
```

### 2. Background Service

Performs operations that don't require direct user interaction: data synchronization, file downloads.

**Critical limitation**: since Android 8.0 (API 26), the system strictly limits Background Services for apps in the background. Use WorkManager or Foreground Service instead.

```kotlin
// ❌ Wrong: Background Service is restricted on API 26+
startService(Intent(this, BackgroundService::class.java))

// ✅ Correct: use WorkManager
val request = OneTimeWorkRequestBuilder<SyncWorker>().build()
WorkManager.getInstance(context).enqueue(request)
```

### 3. Bound Service

Provides an interface for interaction with other components via `bindService()`. Lives only while at least one client is bound to it.

```kotlin
// ✅ Bound Service example
class LocalService : Service() {
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): LocalService = this@LocalService
    }

    override fun onBind(intent: Intent): IBinder = binder
}
```

**Important**: IntentService is deprecated (since API 30). Use WorkManager for sequential task execution.

---

## Follow-ups

- What are Foreground Service types and when were they introduced?
- How does WorkManager differ from Services in terms of execution guarantees?
- What happens to a Bound Service when all clients unbind?
- What are the specific background execution limits on API 26+?
- Can a Service be both foreground and bound simultaneously?

## References

- [[c-service]] - Service component fundamentals
- [[c-workmanager]] - WorkManager architecture
- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/background

## Related Questions

### Prerequisites (Easier)
- [[q-four-main-components-of-android--android--easy]] - Android components overview

### Related (Same Level)
- [[q-service-component--android--medium]] - Service lifecycle and implementation

### Advanced (Harder)
- [[q-foreground-service-types--android--medium]] - Foreground Service type categories
- [[q-when-can-the-system-restart-a-service--android--medium]] - Service restart behavior
