---
id: android-lc-016
title: Foreground Service Lifecycle / Жизненный цикл Foreground Service
aliases: []
topic: android
subtopics:
- lifecycle
- services
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-services
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/services
- difficulty/medium
anki_cards:
- slug: android-lc-016-0-en
  language: en
  anki_id: 1769172234509
  synced_at: '2026-01-23T16:45:05.253835'
- slug: android-lc-016-0-ru
  language: ru
  anki_id: 1769172234532
  synced_at: '2026-01-23T16:45:05.255438'
---
# Question (EN)
> How does Foreground Service lifecycle differ from started and bound services?

# Vopros (RU)
> Чем жизненный цикл Foreground Service отличается от started и bound services?

---

## Answer (EN)

**Foreground Service** is a started service with a persistent notification that has higher priority and is less likely to be killed.

**Service types comparison:**

| Type | Notification | Survives | Kill Priority |
|------|-------------|----------|---------------|
| Started | None | Until stopSelf() | Low (killed when needed) |
| Bound | None | Until all unbind | Medium |
| Foreground | Required | User awareness | High (rarely killed) |

**Foreground service lifecycle:**
```
startForegroundService() or startService()
    -> onCreate()
    -> onStartCommand()
    -> startForeground(id, notification)  // MUST call within 5 seconds

[Running with notification]

stopForeground() / stopSelf()
    -> onDestroy()
```

**Implementation (API 26+):**
```kotlin
class MyForegroundService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Create notification
        val notification = createNotification()

        // MUST call within 5 seconds of startForegroundService()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        // Do work
        doBackgroundWork()

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Starting from Activity:**
```kotlin
// API 26+
val intent = Intent(this, MyForegroundService::class.java)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}
```

**Required permissions (API 28+):**
```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

<!-- API 34+: Specific type permissions -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
```

**Foreground service types (API 29+):**
```xml
<service
    android:name=".MyService"
    android:foregroundServiceType="location|camera|microphone" />
```

Types: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`

**Lifecycle with bound clients:**
```
startForegroundService()
    -> onCreate() -> onStartCommand() -> startForeground()

bindService() from Activity
    -> onBind()

unbindService()
    -> onUnbind() (service continues running)

stopSelf() or stopService()
    -> onDestroy()
```

**Common mistakes:**
```kotlin
// BAD: Not calling startForeground within 5 seconds
// Results in ANR: "Context.startForegroundService() did not then call Service.startForeground()"

// BAD: Using wrong notification channel importance
// Must be at least IMPORTANCE_LOW for foreground services

// BAD: Not declaring foreground service type (API 34+)
// Service won't start without proper type declaration
```

## Otvet (RU)

**Foreground Service** - это started сервис с постоянным уведомлением, который имеет более высокий приоритет и реже убивается.

**Сравнение типов сервисов:**

| Тип | Уведомление | Живёт | Приоритет убийства |
|-----|-------------|-------|-------------------|
| Started | Нет | До stopSelf() | Низкий (убивается когда нужно) |
| Bound | Нет | До всех unbind | Средний |
| Foreground | Обязательно | Осведомлённость | Высокий (редко убивается) |

**Жизненный цикл foreground service:**
```
startForegroundService() или startService()
    -> onCreate()
    -> onStartCommand()
    -> startForeground(id, notification)  // ОБЯЗАТЕЛЬНО в течение 5 секунд

[Работает с уведомлением]

stopForeground() / stopSelf()
    -> onDestroy()
```

**Реализация (API 26+):**
```kotlin
class MyForegroundService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Создать уведомление
        val notification = createNotification()

        // ОБЯЗАТЕЛЬНО вызвать в течение 5 секунд после startForegroundService()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        // Выполнить работу
        doBackgroundWork()

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Запуск из Activity:**
```kotlin
// API 26+
val intent = Intent(this, MyForegroundService::class.java)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}
```

**Необходимые разрешения (API 28+):**
```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

<!-- API 34+: Специфичные разрешения по типу -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
```

**Типы foreground service (API 29+):**
```xml
<service
    android:name=".MyService"
    android:foregroundServiceType="location|camera|microphone" />
```

Типы: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`

**Lifecycle с bound клиентами:**
```
startForegroundService()
    -> onCreate() -> onStartCommand() -> startForeground()

bindService() из Activity
    -> onBind()

unbindService()
    -> onUnbind() (сервис продолжает работать)

stopSelf() или stopService()
    -> onDestroy()
```

**Частые ошибки:**
```kotlin
// ПЛОХО: Не вызвать startForeground в течение 5 секунд
// Результат ANR: "Context.startForegroundService() did not then call Service.startForeground()"

// ПЛОХО: Неправильная важность канала уведомлений
// Должна быть минимум IMPORTANCE_LOW для foreground services

// ПЛОХО: Не объявить тип foreground service (API 34+)
// Сервис не запустится без правильного объявления типа
```

---

## Follow-ups
- What are all foreground service types and when to use each?
- How to handle foreground service restrictions in API 31+?
- What is the difference between START_STICKY and START_NOT_STICKY?

## References
- [[c-lifecycle]]
- [[c-services]]
- [[moc-android]]
