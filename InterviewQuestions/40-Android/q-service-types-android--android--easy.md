---
id: android-340
title: "Service Types Android / Типы Service в Android"
aliases: ["Service Types Android", "Типы Service в Android"]
topic: android
subtopics: [background-execution, service]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-android-components, q-android-app-components--android--easy]
created: 2025-10-15
updated: 2025-10-28
tags: [android/background-execution, android/service, background-tasks, difficulty/easy]

---

# Вопрос (RU)

> Какие существуют типы `Service` в Android?

# Question (EN)

> What types of `Service` exist in Android?

---

## Ответ (RU)

В Android традиционно выделяют три основных способа использования `Service` (по типу поведения):

### 1. Foreground `Service`

Выполняет операции, видимые пользователю, и **обязан** отображать постоянное уведомление (persistent notification). Используется для задач, о которых пользователь должен знать: воспроизведение музыки, навигация, отслеживание тренировки.

С Android 8.0 (API 26) при запуске foreground-сервиса из фона используется `startForegroundService()`, после чего сервис должен вызвать `startForeground(...)` в короткий срок.

```kotlin
// ✅ Правильно: запуск Foreground Service с уведомлением
val notification = createNotification()
startForeground(NOTIFICATION_ID, notification)
```

### 2. Background `Service`

Под "background service" обычно понимают запущенный (started) `Service`, выполняющий операции без прямого взаимодействия с пользователем: синхронизация данных, загрузка файлов и т.п.

**Критическое ограничение**: с Android 8.0 (API 26) приложение **не может свободно запускать background service, находясь в фоне** (background execution limits). Если нужно длительное выполнение в фоне, следует использовать Foreground `Service` (с уведомлением) или такие компоненты, как WorkManager / JobScheduler.

```kotlin
// ⚠️ Ограничение: такой вызов из фонового состояния приложения
// может быть заблокирован или привести к ошибке на API 26+.
startService(Intent(this, BackgroundService::class.java))

// ✅ Рекомендуемый подход для отложенных/гарантированных задач
val request = OneTimeWorkRequestBuilder<SyncWorker>().build()
WorkManager.getInstance(context).enqueue(request)
```

### 3. Bound `Service`

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

**Важно**: `IntentService` устарел (deprecated с API 30). Для фоновых задач вместо него обычно используют:
- WorkManager / JobScheduler — для отложенных и гарантированных задач;
- обычный `Service` (или Foreground `Service`) с потоками/корутинами — если нужен прямой контроль выполнения.

См. также: [[c-android-components]], [[q-android-app-components--android--easy]].

## Answer (EN)

In Android, we traditionally distinguish three main `Service` usage patterns (by behavior):

### 1. Foreground `Service`

Performs user-visible operations and **must** display a persistent notification. Used for tasks the user should be aware of: music playback, navigation, workout tracking.

Since Android 8.0 (API 26), when starting a foreground service from the background you must use `startForegroundService()`, and the service must call `startForeground(...)` shortly after starting.

```kotlin
// ✅ Correct: run Foreground Service with a notification
val notification = createNotification()
startForeground(NOTIFICATION_ID, notification)
```

### 2. Background `Service`

"Background service" usually refers to a started `Service` performing work without direct user interaction: data sync, file downloads, etc.

**Critical limitation**: since Android 8.0 (API 26), an app **cannot freely start background services while in the background** (background execution limits). For long-running background work, you should use a Foreground `Service` (with a notification) or components like WorkManager / JobScheduler instead.

```kotlin
// ⚠️ Limitation: this call from a backgrounded app
// may be blocked or cause an error on API 26+.
startService(Intent(this, BackgroundService::class.java))

// ✅ Recommended for deferred/guaranteed work
val request = OneTimeWorkRequestBuilder<SyncWorker>().build()
WorkManager.getInstance(context).enqueue(request)
```

### 3. Bound `Service`

Provides an interface for interaction with other components via `bindService()`. It remains running only while at least one client is bound to it.

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

**Important**: `IntentService` is deprecated (since API 30). For background work instead you typically use:
- WorkManager / JobScheduler for deferred and guaranteed tasks;
- a regular `Service` (or Foreground `Service`) with threads/coroutines when you need direct execution control.

See also: [[c-android-components]], [[q-android-app-components--android--easy]].

---

## Follow-ups

- What are Foreground `Service` types and when were they introduced?
- How does WorkManager differ from Services in terms of execution guarantees?
- What happens to a Bound `Service` when all clients unbind?
- What are the specific background execution limits on API 26+?
- Can a `Service` be both foreground and bound simultaneously?

## References

- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/background

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android components overview

### Related (Same Level)
- [[q-service-component--android--medium]] - `Service` lifecycle and implementation

### Advanced (Harder)
- [[q-foreground-service-types--android--medium]] - Foreground `Service` type categories
- [[q-when-can-the-system-restart-a-service--android--medium]] - `Service` restart behavior
