---
topic: android
tags:
  - android
  - android/background-processing
  - background-processing
  - battery-optimization
  - doze-mode
  - services
  - workmanager
difficulty: medium
status: reviewed
---

# Why are there restrictions on starting services?

**Russian**: С чем связаны ограничения на запуск сервисов?

**English**: Why are there restrictions on starting services?

## Answer

Service restrictions are related to **battery optimization** and **performance**:

1. **Battery life** - Long-running background services drain battery
2. **Memory usage** - Too many services cause memory pressure
3. **Performance** - Background work slows down the device
4. **Security** - Prevents malicious apps from running indefinitely

**Solution:** Use **WorkManager** or **Foreground Services** instead of background services.

---

## History of Service Restrictions

### Android Evolution

```
Android 5.0 (Lollipop) - JobScheduler introduced
Android 6.0 (Marshmallow) - Doze mode
Android 7.0 (Nougat) - Doze on the go
Android 8.0 (Oreo) - Background execution limits ← Major change
Android 9.0 (Pie) - App Standby Buckets
Android 10 (Q) - Background activity starts restricted
Android 11 (R) - Further background restrictions
Android 12 (S) - Exact alarms restricted
Android 13 (T) - Notification permissions required
```

---

## Android 8.0+ Background Service Restrictions

### What Changed in Android 8.0 (Oreo)

**Before Android 8.0:**
```kotlin
// ✅ WORKED: Start service in background
class MyApp : Application() {
    fun doBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent) // Worked fine
    }
}
```

**Android 8.0+:**
```kotlin
// ❌ THROWS: IllegalStateException
class MyApp : Application() {
    fun doBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent) // Crashes when app is in background!
    }
}
```

**Error:**
```
java.lang.IllegalStateException: Not allowed to start service Intent:
app is in background
```

---

## Why These Restrictions?

### 1. Battery Drain

**Problem:** Apps running services 24/7 consume battery.

```kotlin
// ❌ BAD: Old approach (pre-Android 8.0)
class LocationTrackingService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Runs forever, drains battery
        trackLocationContinuously()
        return START_STICKY
    }
}
```

**Impact:**
- Continuous GPS usage
- Network requests while sleeping
- Wake locks preventing device sleep
- Background CPU usage

---

### 2. Memory Leaks

**Problem:** Services can cause memory leaks if not properly managed.

```kotlin
// ❌ BAD: Service holding Activity reference
class BadService : Service() {
    private var activity: MainActivity? = null // Memory leak!

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // If Activity is destroyed, service still holds reference
        activity = intent?.getParcelableExtra("activity")
        return START_STICKY
    }
}
```

---

### 3. Performance Degradation

**Problem:** Too many background services slow down the device.

```
100 apps × 1 service each = 100 background processes
Each consuming: 50MB RAM + CPU cycles
Total: 5GB RAM, constant CPU usage
→ Device becomes sluggish
```

---

### 4. Security and Privacy

**Problem:** Malicious apps can abuse services.

```kotlin
// ❌ MALICIOUS: Spyware service
class SpywareService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Runs in background, user unaware
        recordAudio()
        trackLocation()
        sendDataToServer()
        return START_STICKY // Restarts if killed
    }
}
```

---

## Specific Restrictions by Android Version

### Android 8.0 (Oreo) - Background Execution Limits

**Restrictions:**
1. **Cannot start background services** when app is in background
2. **Implicit broadcasts** mostly disabled
3. **Background location updates** limited

**Workarounds:**
```kotlin
// ✅ GOOD: Use Foreground Service
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification())
        doWork()
        return START_STICKY
    }
}

// Start foreground service (allowed)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}
```

---

### Android 9.0 (Pie) - App Standby Buckets

Apps are categorized into buckets based on usage:

| Bucket | Restrictions |
|--------|--------------|
| **Active** | App currently in use | No restrictions |
| **Working set** | Used frequently | Mild restrictions |
| **Frequent** | Used regularly | Moderate restrictions |
| **Rare** | Rarely used | Heavy restrictions |
| **Never** | Never opened | Maximum restrictions |

**Impact:** Background jobs delayed based on bucket.

---

### Android 10 (Q) - Background Activity Starts

**Restriction:** Apps cannot start activities from background.

```kotlin
// ❌ DOESN'T WORK: Start activity from background
class MyService : Service() {
    fun showActivity() {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent) // Blocked on Android 10+
    }
}

// ✅ WORKAROUND: Use full-screen intent notification
val fullScreenIntent = Intent(this, IncomingCallActivity::class.java)
val fullScreenPendingIntent = PendingIntent.getActivity(
    this, 0, fullScreenIntent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
)

val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setSmallIcon(R.drawable.ic_call)
    .setContentTitle("Incoming Call")
    .setFullScreenIntent(fullScreenPendingIntent, true) // Shows on lock screen
    .build()
```

---

### Android 12 (S) - Exact Alarms

**Restriction:** Exact alarms require special permission.

```kotlin
// ❌ RESTRICTED: Exact alarms
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    // Requires SCHEDULE_EXACT_ALARM permission
    alarmManager.setExact(
        AlarmManager.RTC_WAKEUP,
        triggerTime,
        pendingIntent
    )
}

// ✅ ALTERNATIVE: Use inexact alarms
alarmManager.setWindow(
    AlarmManager.RTC_WAKEUP,
    triggerTime,
    10 * 60 * 1000, // 10-minute window
    pendingIntent
)
```

---

## Doze Mode and App Standby

### Doze Mode

When device is stationary and screen off for a while:

**Restrictions applied:**
- Network access suspended
- Wake locks ignored
- Alarms deferred
- Wi-Fi scans disabled
- JobScheduler and SyncAdapter deferred

**Maintenance windows:**
```
Screen off
  ↓
[30 min] → [Doze] → [Maintenance] (few minutes)
           ↓
[60 min] → [Doze] → [Maintenance]
           ↓
[120 min] → [Doze] → [Maintenance]
```

### App Standby

App enters standby when:
- User hasn't used app recently
- App has no foreground services
- No notifications shown

**Restrictions:**
- Network access limited
- Jobs and syncs deferred

---

## Exemptions from Restrictions

### Activities Allowed During Doze

1. **High-priority FCM messages**
   ```kotlin
   {
     "message": {
       "token": "device_token",
       "android": {
         "priority": "high" // Bypasses Doze
       },
       "data": {
         "key": "value"
       }
     }
   }
   ```

2. **setAndAllowWhileIdle() alarms**
   ```kotlin
   alarmManager.setAndAllowWhileIdle(
       AlarmManager.RTC_WAKEUP,
       triggerTime,
       pendingIntent
   ) // Works during Doze (limited frequency)
   ```

3. **Foreground services**
   ```kotlin
   startForegroundService(intent) // Always allowed
   ```

---

## Modern Alternatives to Background Services

### 1. WorkManager (Recommended)

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

**Advantages:**
- ✅ Respects system constraints
- ✅ Survives app restarts
- ✅ Automatic retry
- ✅ Compatible with all Android versions

---

### 2. Foreground Services

For user-visible tasks:

```kotlin
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        playMusic()

        return START_STICKY
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Playing Music")
            .setContentText(currentSong.title)
            .setSmallIcon(R.drawable.ic_music)
            .build()
    }
}
```

**Use cases:**
- Music playback
- Navigation
- File downloads
- Ongoing calls

---

### 3. Firebase Cloud Messaging (FCM)

For triggered background work:

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        // Triggered by server, bypasses restrictions
        processBackgroundTask(message.data)
    }
}
```

---

## Best Practices

### 1. Choose the Right Tool

```kotlin
// ❌ DON'T: Background service for periodic sync
class SyncService : Service() {
    override fun onStartCommand(...): Int {
        syncData() // Restricted on Android 8.0+
        return START_STICKY
    }
}

// ✅ DO: WorkManager for periodic work
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .build()

WorkManager.getInstance(context).enqueue(syncWork)
```

---

### 2. Minimize Background Work

```kotlin
// ❌ DON'T: Continuous background processing
class BadWorker : Worker() {
    override fun doWork(): Result {
        while (true) { // Infinite loop!
            processData()
            Thread.sleep(1000)
        }
    }
}

// ✅ DO: Discrete, time-limited tasks
class GoodWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        processData() // Completes and exits
        return Result.success()
    }
}
```

---

### 3. Use Appropriate Service Type

```kotlin
// ✅ Foreground service for user-visible work
startForegroundService(Intent(this, MusicService::class.java))

// ✅ WorkManager for deferrable work
WorkManager.getInstance(context).enqueue(uploadWork)

// ✅ JobScheduler for system-scheduled work (pre-WorkManager)
val jobScheduler = getSystemService(Context.JOB_SCHEDULER_SERVICE) as JobScheduler
jobScheduler.schedule(jobInfo)
```

---

## Summary

**Why service restrictions exist:**

1. **Battery optimization** - Prevent unnecessary battery drain
2. **Performance** - Reduce memory pressure and CPU usage
3. **Security** - Prevent malicious background activity
4. **User experience** - Keep devices responsive

**Key restrictions:**
- ❌ Cannot start background services on Android 8.0+ (when app in background)
- ❌ Doze mode limits network access and wake locks
- ❌ App Standby defers background jobs
- ❌ Android 10+ blocks starting activities from background

**Solutions:**
- ✅ Use **WorkManager** for deferrable background work
- ✅ Use **Foreground Services** for user-visible tasks
- ✅ Use **FCM** for server-triggered work
- ✅ Use **AlarmManager.setAndAllowWhileIdle()** for time-critical tasks

**Migration guide:**
```kotlin
// OLD: Background service (pre-Android 8.0)
startService(Intent(this, MyService::class.java))

// NEW: WorkManager (Android 8.0+)
WorkManager.getInstance(context).enqueue(myWorkRequest)

// NEW: Foreground service (for user-visible work)
startForegroundService(Intent(this, MyService::class.java))
```

---

## Ответ

Ограничения на запуск сервисов связаны с **оптимизацией энергопотребления** и **производительности**:

1. **Батарея** - Долгоживущие фоновые сервисы разряжают батарею
2. **Память** - Много сервисов вызывают нехватку памяти
3. **Производительность** - Фоновая работа замедляет устройство
4. **Безопасность** - Предотвращает работу вредоносных приложений

**Начиная с Android 8.0:**
- ❌ Нельзя запускать background services из фона
- ✅ Используйте **WorkManager** для отложенной работы
- ✅ Используйте **Foreground Services** для видимых задач

**Решения:**

```kotlin
// ❌ СТАРЫЙ способ (не работает на Android 8.0+)
startService(Intent(this, MyService::class.java))

// ✅ WorkManager (для отложенных задач)
WorkManager.getInstance(context).enqueue(myWorkRequest)

// ✅ Foreground Service (для видимых пользователю задач)
startForegroundService(Intent(this, MyService::class.java))
```

**Причины ограничений:**
- Оптимизация батареи (Doze mode)
- Управление памятью (App Standby)
- Безопасность и приватность
- Улучшение UX

