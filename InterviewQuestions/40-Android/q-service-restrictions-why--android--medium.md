---
id: android-205
title: Service Restrictions / Ограничения Service
aliases: [Service Restrictions, Ограничения Service]
topic: android
subtopics: [service]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-components, q-android-service-types--android--easy, q-foreground-service-types--android--medium, q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium, q-what-is-data-binding--android--easy, q-when-can-the-system-restart-a-service--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/service, difficulty/medium]

---
# Вопрос (RU)
> Ограничения `Service`

# Question (EN)
> `Service` Restrictions

---

## Ответ (RU)

Ограничения на работу `Service` в Android введены для **экономии батареи**, **контроля ресурсов**, **поддержания производительности** и **повышения безопасности/приватности**. Со временем платформа существенно ужесточила правила фоновой активности.

### История Ограничений `Service`

```text
Android 5.0 (Lollipop)   - Введен JobScheduler
Android 6.0 (Marshmallow) - Doze Mode
Android 7.0 (Nougat)     - Doze on the go
Android 8.0 (Oreo)       - Ограничения фонового выполнения и геолокации (главный перелом)
Android 9.0 (Pie)        - App Standby Buckets
Android 10 (Q)           - Ограничения на запуск Activity из фона
Android 11 (R)           - Доп. лимиты, типы Foreground Service
Android 12 (S)           - Ограничения на точные (exact) будильники
Android 13 (T)           - Разрешение на уведомления
```

### Почему Появились Ограничения?

1. **Батарея**
   
   Проблема: долгоживущие фоновые сервисы держат CPU, GPS, сеть и wake lock'и, мешают устройству переходить в глубокий сон.

   ```kotlin
   // ПЛОХО: старый подход (до Android 8.0)
   class LocationTrackingService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           trackLocationContinuously() // Долгая непрерывная работа, разряд батареи
           return START_STICKY
       }
   }
   ```

2. **Память и утечки**

   Сервисы живут дольше `Activity` и могут удерживать контекст/ссылки и вызывать утечки памяти.

   ```kotlin
   // ПЛОХО: Service удерживает ссылку на Activity
   class BadService : Service() {
       private var activity: MainActivity? = null
   
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           activity = intent?.getParcelableExtra("activity") // Риск утечки
           return START_STICKY
       }
   }
   ```

3. **Производительность**

   Множество фоновых сервисов из разных приложений → суммарная нагрузка на CPU/память → устройство «тормозит».

4. **Безопасность и приватность**

   Нельзя допускать, чтобы приложения незаметно для пользователя бесконечно отправляли данные, слушали микрофон, отслеживали местоположение и т.д.

   ```kotlin
   // ВОЗМОЖНО ЗЛОНАМЕРЕННО: скрытый сервис-шпион
   class SpywareService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           recordAudio()
           trackLocation()
           sendDataToServer()
           return START_STICKY // Перезапускается после убийства процесса
       }
   }
   ```

---

### Ограничения Android 8.0+ На Фоновые `Service`

#### Что Изменилось В Android 8.0 (Oreo)

До Oreo можно было запускать `startService()` даже из фона.

```kotlin
// ДОЛГОЕ ВРЕМЯ РАБОТАЛО (до 8.0)
class MyApp : Application() {
    fun doBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent)
    }
}
```

Начиная с Android 8.0:

```kotlin
// В ФОНЕ ПРИВЕДЕТ К IllegalStateException
class MyApp : Application() {
    fun doBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent) // Запрет, если приложение в фоне
    }
}
```

Ошибка:

```java
java.lang.IllegalStateException: Not allowed to start service Intent: app is in background
```

Теперь нужно:
- либо использовать `startForegroundService()` и быстро вызвать `startForeground()` внутри сервиса;
- либо планировать работу через `WorkManager`/`JobScheduler`.

Пример корректного Foreground `Service`:

```kotlin
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification())
        doWork()
        return START_STICKY
    }
}

if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}
```

---

### Doze Mode И App Standby

#### Doze Mode

Когда устройство долго не используется (экран выкл., нет движения), включается Doze:
- Откладываются сетевые запросы и обычные `AlarmManager`-события.
- Ограничиваются wake lock'и.
- Фоновая синхронизация и `JobScheduler`-задачи выполняются в коротких maintenance-окнах.

С ростом времени простоя окна обслуживания становятся реже.

#### App Standby

Когда приложение давно не открывали, нет foreground-активности/сервисов и заметных уведомлений, оно попадает в состояние Standby:
- Сильнее ограничиваются сетевые операции.
- Задачи и синхронизация откладываются агрессивнее.

---

### App Standby Buckets (Android 9.0, Pie)

Android 9 вводит «корзины» активности приложения:

- Active — активно используется, минимальные ограничения.
- Working set — используется часто, мягкие лимиты.
- Frequent — периодически используется, больше ограничений.
- Rare — редко используется, сильные задержки фоновой работы.
- Never — никогда не запускалось, максимальные ограничения.

Чем ниже корзина, тем позже и реже система дает выполнять фоновые задачи.

---

### Android 10 (Q) — Запуск `Activity` Из Фона

Android 10 существенно ограничивает старт `Activity` из фона (в том числе из сервисов). Разрешены только отдельные сценарии (пользовательское действие, системные UI, уведомление, полноэкранный интент и т.п.), в остальных случаях запуск будет заблокирован.

```kotlin
// НЕ НАДЕЙТЕСЬ: запуск Activity из фонового сервиса
class MyService : Service() {
    fun showActivity() {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent) // На Android 10+ в большинстве фоновых сценариев блокируется/игнорируется
    }
}
```

Рекомендуемый подход — уведомление с высоким приоритетом или full-screen intent для допустимых сценариев (например, входящий звонок):

```kotlin
val fullScreenIntent = Intent(this, IncomingCallActivity::class.java)
val fullScreenPendingIntent = PendingIntent.getActivity(
    this, 0, fullScreenIntent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
)

val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setSmallIcon(R.drawable.ic_call)
    .setContentTitle("Incoming Call")
    .setFullScreenIntent(fullScreenPendingIntent, true)
    .build()
```

---

### Android 12 (S) — Точные Будильники

На Android 12+ точные (exact) будильники дополнительно контролируются:

- Для свободного использования `setExact()`/`setExactAndAllowWhileIdle()` приложению требуется специальное разрешение `SCHEDULE_EXACT_ALARM` (или статус системного/OEM-приложения, или иное системное исключение).
- Без этого разрешения приоритет отдается неточным/гибким вариантам, и система может не предоставить точное срабатывание.

```kotlin
// Точный будильник на Android 12+ (при наличии соответствующего разрешения/исключения)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    alarmManager.setExact(
        AlarmManager.RTC_WAKEUP,
        triggerTime,
        pendingIntent
    )
}

// Предпочтительно использовать неточный/оконный будильник, если точность не критична
alarmManager.setWindow(
    AlarmManager.RTC_WAKEUP,
    triggerTime,
    10 * 60 * 1000L,
    pendingIntent
)
```

---

### Исключения И Послабления

Во время Doze/Standby часть механик все же разрешена:

1. **Высокоприоритетные FCM-сообщения** — короткое выполнение с доступом к сети (с лимитами и защитой от злоупотреблений).

   ```json
   {
     "message": {
       "token": "device_token",
       "android": {
         "priority": "high"
       },
       "data": {
         "key": "value"
       }
     }
   }
   ```

2. **`setAndAllowWhileIdle()` / `setExactAndAllowWhileIdle()`** — могут срабатывать в Doze, но с ограничением частоты.

   ```kotlin
   alarmManager.setAndAllowWhileIdle(
       AlarmManager.RTC_WAKEUP,
       triggerTime,
       pendingIntent
   )
   ```

3. **Foreground `Service`** — при корректном запуске (`startForegroundService()` + быстрый `startForeground()`) получает повышенный приоритет.

   ```kotlin
   if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
       startForegroundService(intent)
   } else {
       startService(intent)
   }
   ```

   Начиная с Android 10+/11+ для таких сервисов также важно указывать корректный `foregroundServiceType` в манифесте в соответствии с задачей сервиса.

---

### Современные Альтернативы Фоновых `Service`

1. **WorkManager (рекомендуется)** — для отложенных, гарантированных задач.

   ```kotlin
   val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
       .setConstraints(
           Constraints.Builder()
               .setRequiredNetworkType(NetworkType.CONNECTED)
               .setRequiresBatteryNotLow(true)
               .build()
       )
       .build()
   
   WorkManager.getInstance(context).enqueue(uploadWork)
   ```

   Плюсы: уважает системные ограничения, переживает перезапуски, поддерживает цепочки и ретраи.

2. **Foreground `Service`** — для длительных, заметных пользователю задач (музыка, навигация, загрузки, звонки, запись экрана).

   ```kotlin
   class MusicPlayerService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           val notification = createNotification()
           startForeground(NOTIFICATION_ID, notification)
           playMusic()
           return START_STICKY
       }
   }
   ```

3. **Firebase Cloud Messaging (FCM)** — для триггеров с сервера с делегированием тяжелой работы в WorkManager/FGS.

   ```kotlin
   class MyFirebaseMessagingService : FirebaseMessagingService() {
       override fun onMessageReceived(message: RemoteMessage) {
           processBackgroundTask(message.data)
       }
   }
   ```

---

### Лучшие Практики

1. **Выбирать правильный инструмент**

   ```kotlin
   // НЕПРАВИЛЬНО: started Service для периодической синхронизации
   class SyncService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           syncData()
           return START_STICKY
       }
   }
   
   // ПРАВИЛЬНО: WorkManager для периодической работы
   val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
       .setConstraints(
           Constraints.Builder()
               .setRequiredNetworkType(NetworkType.CONNECTED)
               .build()
       )
       .build()
   
   WorkManager.getInstance(context).enqueue(syncWork)
   ```

2. **Минимизировать фоновую работу**

   ```kotlin
   // НЕПРАВИЛЬНО: бесконечный цикл в фоне
   class BadWorker : Worker() {
       override fun doWork(): Result {
           while (true) {
               processData()
               Thread.sleep(1000)
           }
       }
   }
   
   // ПРАВИЛЬНО: конечная, ограниченная по времени задача
   class GoodWorker : CoroutineWorker() {
       override suspend fun doWork(): Result {
           processData()
           return Result.success()
       }
   }
   ```

3. **Использовать подходящий тип `Service`/планировщик**

   ```kotlin
   // Foreground Service для длительной пользовательской задачи
   startForegroundService(Intent(this, MusicService::class.java))
   
   // WorkManager для гарантированной отложенной работы
   WorkManager.getInstance(context).enqueue(uploadWork)
   
   // JobScheduler — прямое использование системного планировщика при необходимости
   val jobScheduler = getSystemService(Context.JOB_SCHEDULER_SERVICE) as JobScheduler
   jobScheduler.schedule(jobInfo)
   ```

---

### Итоги (RU)

Почему введены ограничения:
- Экономия батареи.
- Стабильность производительности и памяти.
- Безопасность и приватность.
- Предсказуемый пользовательский опыт.

Ключевые моменты:
- Нельзя свободно запускать фоновые `Service` из фона на Android 8.0+.
- Doze/App Standby/App Standby Buckets агрессивно откладывают фоновую работу.
- Android 10+ ограничивает запуск `Activity` из фона, кроме специально разрешенных сценариев.
- Android 12+ ужесточает использование точных будильников; Android 13+ требует разрешение на уведомления.

Используйте:
- WorkManager/JobScheduler для отложенных задач.
- Foreground `Service` (с корректным `foregroundServiceType`) для длительной, заметной пользователю работы.
- FCM (+ WorkManager/FGS) для событий с сервера.
- `setAndAllowWhileIdle()` / `setExactAndAllowWhileIdle()` только для действительно критичных будильников.

---

## Answer (EN)

`Service` restrictions are primarily about **battery optimization**, **performance**, **resource management**, and **security/privacy**. Over time Android has tightened what apps can do in the background.

Key reasons:

1. Long-running background services drain battery.
2. Many services increase memory pressure and CPU load.
3. Too much hidden background work degrades device performance.
4. Malicious or opaque services can abuse permissions and user data.

### History of `Service` Restrictions

```text
Android 5.0 (Lollipop)   - JobScheduler introduced
Android 6.0 (Marshmallow) - Doze mode
Android 7.0 (Nougat)     - Doze on the go
Android 8.0 (Oreo)       - Background execution and location limits
Android 9.0 (Pie)        - App Standby Buckets
Android 10 (Q)           - Background activity starts restricted
Android 11 (R)           - Further background limits, FGS types
Android 12 (S)           - Exact alarms gated by special permission
Android 13 (T)           - Notification permission required
```

### Android 8.0+ Background `Service` Restrictions

Before Android 8.0 you could freely call `startService()` even from the background:

```kotlin
// WORKED pre-8.0
class MyApp : Application() {
    fun doBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent)
    }
}
```

On Android 8.0+ starting a background service while your app is in background leads to:

```kotlin
// THROWS when app is backgrounded
class MyApp : Application() {
    fun doBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent) // Illegal if app in background
    }
}
```

Error:

```java
java.lang.IllegalStateException: Not allowed to start service Intent: app is in background
```

You must either:
- use `startForegroundService()` and call `startForeground()` quickly, or
- schedule work via WorkManager/JobScheduler.

```kotlin
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification())
        doWork()
        return START_STICKY
    }
}

if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}
```

### Why These Restrictions?

1. Battery drain — prevent 24/7 background services (GPS, network, wake locks) from killing battery.
2. Memory/CPU — limit always-running processes that pressure system resources.
3. Performance — keep the device responsive.
4. Security/privacy — reduce opportunities for spyware-like behavior.

```kotlin
// MALICIOUS example
class SpywareService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        recordAudio()
        trackLocation()
        sendDataToServer()
        return START_STICKY
    }
}
```

### Doze Mode and App Standby

- Doze: when device is idle, batches network, defers alarms, restricts wake locks and jobs.
- App Standby: unused apps get stricter limits on network and background work.

### Android 9.0 (Pie) - App Standby Buckets

Apps are categorized into buckets:
- Active, Working set, Frequent, Rare, Never — each with increasing background restrictions.

System delays and batches work more aggressively for less-used apps.

### Android 10 (Q) - Background `Activity` Starts

Android 10 significantly restricts starting activities from the background (including from services). Only specific cases are allowed (user-initiated actions, system UI, notification taps, full-screen intents, etc.); in other cases the start is blocked.

```kotlin
class MyService : Service() {
    fun showActivity() {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent) // On Android 10+ blocked/ignored in most background scenarios
    }
}
```

Use notifications/high-priority or full-screen intents for legitimate cases (e.g., incoming call):

```kotlin
val fullScreenIntent = Intent(this, IncomingCallActivity::class.java)
val fullScreenPendingIntent = PendingIntent.getActivity(
    this, 0, fullScreenIntent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
)

val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setSmallIcon(R.drawable.ic_call)
    .setContentTitle("Incoming Call")
    .setFullScreenIntent(fullScreenPendingIntent, true)
    .build()
```

### Android 12 (S) - Exact Alarms

On Android 12+ exact alarms are gated:

- To freely use `setExact()`/`setExactAndAllowWhileIdle()` an app typically needs the `SCHEDULE_EXACT_ALARM` special permission (or system/OEM/other privileged exemption).
- Without this, the system may restrict exact behavior and encourage inexact/batched alarms.

```kotlin
// Exact alarm on Android 12+ (assuming the app holds the proper permission/exemption)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    alarmManager.setExact(
        AlarmManager.RTC_WAKEUP,
        triggerTime,
        pendingIntent
    )
}

// Prefer inexact/window alarms when strict exactness is not critical
alarmManager.setWindow(
    AlarmManager.RTC_WAKEUP,
    triggerTime,
    10 * 60 * 1000L,
    pendingIntent
)
```

### Exemptions

Allowed (with limits) even under Doze/standby:

1. High-priority FCM messages.
2. `setAndAllowWhileIdle()` / `setExactAndAllowWhileIdle()` (rate-limited).
3. Foreground services started via `startForegroundService()` that promptly call `startForeground()`.
   
   On modern Android versions it is also important to declare an appropriate `foregroundServiceType` in the manifest corresponding to what the FGS does.

### Modern Alternatives to Background Services

1. WorkManager — deferrable, guaranteed background work.

```kotlin
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadWork)
```

1. Foreground services — ongoing, user-visible tasks (music, navigation, downloads, calls, screen recording).

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        playMusic()
        return START_STICKY
    }
}
```

1. FCM — server-triggered tasks; offload heavy work to WorkManager/FGS.

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        processBackgroundTask(message.data)
    }
}
```

### Best Practices

1. Choose the right tool:

```kotlin
// DON'T: started Service for periodic sync
class SyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        syncData()
        return START_STICKY
    }
}

// DO: WorkManager
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncWork)
```

1. Minimize background work:

```kotlin
// DON'T: infinite loop
class BadWorker : Worker() {
    override fun doWork(): Result {
        while (true) {
            processData()
            Thread.sleep(1000)
        }
    }
}

// DO: finite, time-bounded
class GoodWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        processData()
        return Result.success()
    }
}
```

1. Use appropriate `Service`/scheduler:

```kotlin
startForegroundService(Intent(this, MusicService::class.java))
WorkManager.getInstance(context).enqueue(uploadWork)
val jobScheduler = getSystemService(Context.JOB_SCHEDULER_SERVICE) as JobScheduler
jobScheduler.schedule(jobInfo)
```

---

## Summary (EN)

Why restrictions exist:
- Battery optimization.
- Performance and memory stability.
- Security and privacy.
- Better, predictable UX.

Key points:
- No free-form background services on Android 8.0+ from background.
- Doze/App Standby/App Standby Buckets aggressively defer work.
- Android 10+ restricts background activity starts, except for explicitly allowed cases.
- Android 12+ gates exact alarms; Android 13+ gates notifications.

Use:
- WorkManager/JobScheduler for deferrable tasks.
- Foreground services (with correct `foregroundServiceType`) for user-visible ongoing work.
- FCM (+ WorkManager/FGS) for server-driven events.
- `setAndAllowWhileIdle()` / `setExactAndAllowWhileIdle()` only for truly critical alarms.

---

## Дополнительные Вопросы (RU)

- [[q-what-is-data-binding--android--easy]]
- [[q-android-service-types--android--easy]]
- [[q-service-component--android--medium]]
- [[q-foreground-service-types--android--medium]]
- [[q-when-can-the-system-restart-a-service--android--medium]]

## Follow-ups (EN)

- [[q-what-is-data-binding--android--easy]]
- [[q-android-service-types--android--easy]]
- [[q-service-component--android--medium]]
- [[q-foreground-service-types--android--medium]]
- [[q-when-can-the-system-restart-a-service--android--medium]]

---

## Ссылки (RU)

- [Services](https://developer.android.com/develop/background-work/services)

## References (EN)

- [Services](https://developer.android.com/develop/background-work/services)

---

## Related Questions (RU/EN)

### Prerequisites / Concepts

- [[c-android-components]]
- [[q-android-service-types--android--easy]]

### Prerequisites (Easier)

- [[q-what-is-data-binding--android--easy]]

### Related (Medium)

- [[q-service-component--android--medium]]
- [[q-foreground-service-types--android--medium]]
- [[q-when-can-the-system-restart-a-service--android--medium]]
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]]
- [[q-keep-service-running-background--android--medium]]

### Advanced (Harder)

- [[q-service-lifecycle-binding--android--hard]]
