---
id: 20251016-161808
title: "Background Vs Foreground Service"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/foreground-service, android/services, background-service, foreground-service, process-priority, services, difficulty/medium]
---
# Background service vs Foreground service

# Question (EN)
> How does background service differ from foreground service?

# Вопрос (RU)
> Чем background service отличается от foreground service?

---

## Answer (EN)

**Background service** runs in the background and **can be killed** by the system when resources are low.

**Foreground service** requires a **persistent notification** and has **high priority** - the system won't kill it easily.

---

## Detailed Comparison

| Aspect | Background Service | Foreground Service |
|--------|-------------------|-------------------|
| **Notification** | No notification | Required persistent notification |
| **Priority** | Low (can be killed) | High (protected from being killed) |
| **User awareness** | Hidden from user | User sees notification |
| **System behavior** | Kills when memory is low | Preserves as long as possible |
| **Use cases** | Simple tasks, sync | Music, navigation, downloads |
| **Android 8.0+ limits** | Severe restrictions | Can run longer |

---

## Background Service

### Definition

A **background service** runs **without user awareness** and has **low priority**.

```kotlin
class BackgroundSyncService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background service - can be killed anytime
        Thread {
            syncData()  // May be interrupted!
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    private fun syncData() {
        // Sync logic
        Thread.sleep(5000)
        Log.d("Service", "Sync complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Characteristics:**
- No notification required
- Low priority (Service Process level)
- Can be killed by system when memory is low
- **Android 8.0+ severely restricts background service execution**

---

### Android 8.0+ Background Limitations

On Android 8.0 (API 26) and higher, **background services are restricted**:

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startBackgroundService() {
        val intent = Intent(this, BackgroundSyncService::class.java)

        // On Android 8.0+, this might throw IllegalStateException
        // if app is in background!
        startService(intent)
    }
}
```

**Exception thrown:**
```
java.lang.IllegalStateException: Not allowed to start service Intent
{cmp=com.example/.BackgroundSyncService}: app is in background
```

**Solution:** Use foreground service or WorkManager instead.

---

## Foreground Service

### Definition

A **foreground service** runs with **user awareness** via a **persistent notification** and has **high priority**.

```kotlin
class ForegroundDownloadService : Service() {

    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Foreground service - protected from being killed
        startForeground(NOTIFICATION_ID, createNotification())

        Thread {
            downloadFile()  // Guaranteed to complete!
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Downloads",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading file")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)  // Can't be dismissed by user
            .build()
    }

    private fun downloadFile() {
        // Download logic
        Thread.sleep(10000)
        Log.d("Service", "Download complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Characteristics:**
- **Notification is required** (shown to user)
- **High priority** (Foreground Process level)
- **Protected** from being killed
- Can run on Android 8.0+ (with restrictions)

---

### Starting a Foreground Service

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startForegroundService() {
        val intent = Intent(this, ForegroundDownloadService::class.java)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            //  Must use startForegroundService() on Android 8.0+
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}
```

**Important:** On Android 8.0+, you **must** call `startForeground()` within **5 seconds** of starting the service, or the system will kill it.

---

## Process Priority Levels

### Background Service Priority

```
Process Priority Hierarchy (Low to High):

 5. Empty Process                    

 4. Cached Process                   

 3. Service Process (Background)      Can be killed when memory is low

 2. Visible Process                  

 1. Foreground Process               

```

**Background service:**
- Priority: **Service Process (Level 3)**
- System kills when memory is low
- No guarantee of completion

---

### Foreground Service Priority

```
Process Priority Hierarchy (Low to High):

 5. Empty Process                    

 4. Cached Process                   

 3. Service Process                  

 2. Visible Process                  

 1. Foreground Process (Foreground)   Highest priority, protected

```

**Foreground service:**
- Priority: **Foreground Process (Level 1)**
- System preserves as long as possible
- High guarantee of completion

---

## Real-World Examples

### Example 1: Music Player (Foreground Service)

```kotlin
class MusicPlayerService : Service() {

    private val NOTIFICATION_ID = 100
    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> {
                // Foreground service with notification
                startForeground(NOTIFICATION_ID, createNotification("Playing"))
                playMusic()
            }
            ACTION_PAUSE -> {
                pauseMusic()
                updateNotification("Paused")
            }
            ACTION_STOP -> {
                stopMusic()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }

        return START_STICKY  // Restart if killed
    }

    private fun createNotification(status: String): Notification {
        val channelId = "music_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Music Player",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Music Player")
            .setContentText(status)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(status: String) {
        val notification = createNotification(status)
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    private fun playMusic() {
        mediaPlayer = MediaPlayer.create(this, R.raw.music_file)
        mediaPlayer?.start()
    }

    private fun pauseMusic() {
        mediaPlayer?.pause()
    }

    private fun stopMusic() {
        mediaPlayer?.stop()
        mediaPlayer?.release()
        mediaPlayer = null
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        stopMusic()
    }

    companion object {
        const val ACTION_PLAY = "ACTION_PLAY"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_STOP = "ACTION_STOP"
    }
}
```

**Why foreground?**
- User expects music to continue playing
- High priority prevents interruption
- Notification shows playback status

---

### Example 2: Data Sync (Background Service → WorkManager)

```kotlin
// DON'T: Background service (restricted on Android 8.0+)
class SyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            syncDataToServer()  // May be killed!
            stopSelf()
        }.start()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// DO: Use WorkManager instead
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncDataToServer()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun syncDataToServer() {
        // Sync logic
        withContext(Dispatchers.IO) {
            // Network call
        }
    }
}

// Schedule sync
val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

**Why WorkManager?**
- Sync is deferrable (can wait)
- User doesn't need to see notification
- System handles execution intelligently

---

## When to Use Each

### Use Background Service When:

** Note:** Background services are **highly restricted** on Android 8.0+. Consider using **WorkManager** or **JobScheduler** instead.

**Rare cases:**
- App is in foreground
- Very short task (< 1 second)
- Legacy app (target API < 26)

---

### Use Foreground Service When:

**Use foreground service when:**

1. **User-Visible Task**
   ```kotlin
   // Music playback
   // User expects music to continue
   class MusicPlayerService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(NOTIFICATION_ID, notification)
           playMusic()
           return START_STICKY
       }
   }
   ```

2. **Time-Sensitive Task**
   ```kotlin
   // Navigation
   // User needs real-time location updates
   class NavigationService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(NOTIFICATION_ID, notification)
           startLocationUpdates()
           return START_STICKY
       }
   }
   ```

3. **User-Initiated Download/Upload**
   ```kotlin
   // File download
   // User tapped "Download" button
   class DownloadService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(NOTIFICATION_ID, notification)
           downloadFile()
           return START_NOT_STICKY
       }
   }
   ```

---

## Manifest Requirements

### Background Service

```xml
<manifest>
    <application>
        <service
            android:name=".BackgroundSyncService"
            android:exported="false" />
    </application>
</manifest>
```

### Foreground Service

```xml
<manifest>
    <!-- Required for foreground service -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

    <!-- Required for posting notifications (Android 13+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".ForegroundDownloadService"
            android:foregroundServiceType="dataSync"
            android:exported="false" />
    </application>
</manifest>
```

**Foreground service types (Android 10+):**
- `camera` - Camera access
- `connectedDevice` - Bluetooth/USB devices
- `dataSync` - Data transfer/sync
- `location` - Location tracking
- `mediaPlayback` - Audio/video playback
- `mediaProjection` - Screen recording
- `microphone` - Audio recording
- `phoneCall` - Phone call handling

---

## Android Version Differences

### Android 7.1 and Below

```kotlin
// Both background and foreground work similarly
startService(Intent(this, MyService::class.java))
```

### Android 8.0 (API 26)

**Background service restrictions:**
- Can't start background services when app is in background
- Must use `startForegroundService()` for foreground services

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)  // Must call startForeground() within 5s
} else {
    startService(intent)
}
```

### Android 12 (API 31)

**Foreground service launch restrictions:**
- Can't start foreground services from background (with exceptions)
- Must use WorkManager or exact alarms for background starts

```kotlin
//  May throw ForegroundServiceStartNotAllowedException on Android 12+
// if app is in background
startForegroundService(intent)

//  Use WorkManager instead
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
WorkManager.getInstance(context).enqueue(workRequest)
```

---

## Common Mistakes

### Mistake 1: Using Background Service on Android 8.0+

```kotlin
// BAD: Doesn't work on Android 8.0+
class MainActivity : AppCompatActivity() {
    private fun syncData() {
        startService(Intent(this, SyncService::class.java))
        // Throws IllegalStateException if app is in background!
    }
}

// GOOD: Use WorkManager
class MainActivity : AppCompatActivity() {
    private fun syncData() {
        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>().build()
        WorkManager.getInstance(this).enqueue(syncRequest)
    }
}
```

### Mistake 2: Not Calling startForeground() Fast Enough

```kotlin
// BAD: Delay before startForeground()
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            Thread.sleep(10000)  // 10 seconds delay
            startForeground(NOTIFICATION_ID, notification)  // Too late! Service killed
        }.start()
        return START_NOT_STICKY
    }
}

// GOOD: Call startForeground() immediately
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, notification)  // Within 5 seconds
        Thread {
            doLongRunningTask()
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }.start()
        return START_NOT_STICKY
    }
}
```

### Mistake 3: Using Foreground Service for Deferrable Tasks

```kotlin
// BAD: Foreground service for periodic sync
class PeriodicSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, notification)  // User sees unnecessary notification
        syncData()
        return START_STICKY
    }
}

// GOOD: Use WorkManager for periodic tasks
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

---

## Summary

### Background Service
- **Runs:** In background, hidden from user
- **Priority:** Low (can be killed when memory is low)
- **Notification:** No notification
- **Android 8.0+:** **Severely restricted** (use WorkManager instead)
- **Use case:** Almost never (use WorkManager for background tasks)

### Foreground Service
- **Runs:** With user awareness via notification
- **Priority:** High (protected from being killed)
- **Notification:** **Required** persistent notification
- **Android 8.0+:** Allowed, but requires `startForegroundService()`
- **Use case:** Music, navigation, user-initiated downloads

### Decision Guide

```
Is the task user-visible and time-sensitive?
|-- YES → Foreground Service
-- NO → Is the task deferrable?
    |-- YES → WorkManager
    -- NO → Consider if truly necessary
        -- If yes, likely needs Foreground Service
```

**Best practice:** Avoid background services on Android 8.0+. Use:
- **Foreground service** for user-visible tasks
- **WorkManager** for deferrable background tasks
- **JobScheduler** for system-optimized periodic tasks

---

## Ответ (RU)

**Background service** работает в фоне и **может быть остановлен системой** при нехватке ресурсов.

**Foreground service** требует **постоянное уведомление** и имеет **высокий приоритет** - система не убьет его просто так.

---

## Детальное сравнение

| Аспект | Background Service | Foreground Service |
|--------|-------------------|-------------------|
| **Уведомление** | Не требуется | Обязательное постоянное уведомление |
| **Приоритет** | Низкий (может быть убит) | Высокий (защищен от завершения) |
| **Осведомленность пользователя** | Скрыт от пользователя | Пользователь видит уведомление |
| **Поведение системы** | Убивает при нехватке памяти | Сохраняет как можно дольше |
| **Случаи использования** | Простые задачи, синхронизация | Музыка, навигация, загрузки |
| **Ограничения Android 8.0+** | Серьезные ограничения | Может работать дольше |

---

## Background Service

### Определение

**Background service** работает **без осведомленности пользователя** и имеет **низкий приоритет**.

```kotlin
class BackgroundSyncService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background service - может быть убит в любой момент
        Thread {
            syncData()  // Может быть прерван!
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    private fun syncData() {
        // Логика синхронизации
        Thread.sleep(5000)
        Log.d("Service", "Sync complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Характеристики:**
- Уведомление не требуется
- Низкий приоритет (уровень Service Process)
- Может быть убит системой при нехватке памяти
- **Android 8.0+ серьезно ограничивает выполнение background service**

---

### Ограничения Android 8.0+ для Background

На Android 8.0 (API 26) и выше **background services ограничены**:

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startBackgroundService() {
        val intent = Intent(this, BackgroundSyncService::class.java)

        // На Android 8.0+ это может выбросить IllegalStateException
        // если приложение в фоне!
        startService(intent)
    }
}
```

**Выбрасываемое исключение:**
```
java.lang.IllegalStateException: Not allowed to start service Intent
{cmp=com.example/.BackgroundSyncService}: app is in background
```

**Решение:** Используйте foreground service или WorkManager вместо этого.

---

## Foreground Service

### Определение

**Foreground service** работает с **осведомленностью пользователя** через **постоянное уведомление** и имеет **высокий приоритет**.

```kotlin
class ForegroundDownloadService : Service() {

    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Foreground service - защищен от завершения
        startForeground(NOTIFICATION_ID, createNotification())

        Thread {
            downloadFile()  // Гарантированно завершится!
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Downloads",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading file")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)  // Не может быть отклонено пользователем
            .build()
    }

    private fun downloadFile() {
        // Логика загрузки
        Thread.sleep(10000)
        Log.d("Service", "Download complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Характеристики:**
- **Уведомление обязательно** (показывается пользователю)
- **Высокий приоритет** (уровень Foreground Process)
- **Защищен** от завершения
- Может работать на Android 8.0+ (с ограничениями)

---

### Запуск Foreground Service

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startForegroundService() {
        val intent = Intent(this, ForegroundDownloadService::class.java)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            //  Необходимо использовать startForegroundService() на Android 8.0+
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}
```

**Важно:** На Android 8.0+ вы **должны** вызвать `startForeground()` в течение **5 секунд** после запуска сервиса, иначе система его убьет.

---

## Уровни приоритета процессов

### Приоритет Background Service

```
Иерархия приоритетов процессов (от низкого к высокому):

 5. Empty Process

 4. Cached Process

 3. Service Process (Background)      Может быть убит при нехватке памяти

 2. Visible Process

 1. Foreground Process

```

**Background service:**
- Приоритет: **Service Process (Уровень 3)**
- Система убивает при нехватке памяти
- Нет гарантии завершения

---

### Приоритет Foreground Service

```
Иерархия приоритетов процессов (от низкого к высокому):

 5. Empty Process

 4. Cached Process

 3. Service Process

 2. Visible Process

 1. Foreground Process (Foreground)   Высший приоритет, защищен

```

**Foreground service:**
- Приоритет: **Foreground Process (Уровень 1)**
- Система сохраняет как можно дольше
- Высокая гарантия завершения

---

## Примеры из реальной практики

### Пример 1: Музыкальный плеер (Foreground Service)

```kotlin
class MusicPlayerService : Service() {

    private val NOTIFICATION_ID = 100
    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> {
                // Foreground service с уведомлением
                startForeground(NOTIFICATION_ID, createNotification("Playing"))
                playMusic()
            }
            ACTION_PAUSE -> {
                pauseMusic()
                updateNotification("Paused")
            }
            ACTION_STOP -> {
                stopMusic()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }

        return START_STICKY  // Перезапустить если убит
    }

    private fun createNotification(status: String): Notification {
        val channelId = "music_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Music Player",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Music Player")
            .setContentText(status)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(status: String) {
        val notification = createNotification(status)
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    private fun playMusic() {
        mediaPlayer = MediaPlayer.create(this, R.raw.music_file)
        mediaPlayer?.start()
    }

    private fun pauseMusic() {
        mediaPlayer?.pause()
    }

    private fun stopMusic() {
        mediaPlayer?.stop()
        mediaPlayer?.release()
        mediaPlayer = null
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        stopMusic()
    }

    companion object {
        const val ACTION_PLAY = "ACTION_PLAY"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_STOP = "ACTION_STOP"
    }
}
```

**Почему foreground?**
- Пользователь ожидает продолжения воспроизведения музыки
- Высокий приоритет предотвращает прерывание
- Уведомление показывает статус воспроизведения

---

### Пример 2: Синхронизация данных (Background Service → WorkManager)

```kotlin
// НЕ ДЕЛАЙТЕ ТАК: Background service (ограничен на Android 8.0+)
class SyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            syncDataToServer()  // Может быть убит!
            stopSelf()
        }.start()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// ДЕЛАЙТЕ ТАК: Используйте WorkManager
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncDataToServer()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun syncDataToServer() {
        // Логика синхронизации
        withContext(Dispatchers.IO) {
            // Сетевой вызов
        }
    }
}

// Запланировать синхронизацию
val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

**Почему WorkManager?**
- Синхронизация может быть отложена
- Пользователю не нужно видеть уведомление
- Система управляет выполнением интеллектуально

---

## Когда использовать каждый

### Используйте Background Service когда:

** Примечание:** Background services **сильно ограничены** на Android 8.0+. Рассмотрите использование **WorkManager** или **JobScheduler** вместо этого.

**Редкие случаи:**
- Приложение на переднем плане
- Очень короткая задача (< 1 секунды)
- Устаревшее приложение (target API < 26)

---

### Используйте Foreground Service когда:

**Используйте foreground service когда:**

1. **Задача видимая пользователю**
   ```kotlin
   // Воспроизведение музыки
   // Пользователь ожидает продолжения музыки
   class MusicPlayerService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(NOTIFICATION_ID, notification)
           playMusic()
           return START_STICKY
       }
   }
   ```

2. **Задача, чувствительная ко времени**
   ```kotlin
   // Навигация
   // Пользователю нужны обновления местоположения в реальном времени
   class NavigationService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(NOTIFICATION_ID, notification)
           startLocationUpdates()
           return START_STICKY
       }
   }
   ```

3. **Загрузка/выгрузка по инициативе пользователя**
   ```kotlin
   // Загрузка файла
   // Пользователь нажал кнопку "Загрузить"
   class DownloadService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(NOTIFICATION_ID, notification)
           downloadFile()
           return START_NOT_STICKY
       }
   }
   ```

---

## Требования к манифесту

### Background Service

```xml
<manifest>
    <application>
        <service
            android:name=".BackgroundSyncService"
            android:exported="false" />
    </application>
</manifest>
```

### Foreground Service

```xml
<manifest>
    <!-- Требуется для foreground service -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

    <!-- Требуется для отправки уведомлений (Android 13+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".ForegroundDownloadService"
            android:foregroundServiceType="dataSync"
            android:exported="false" />
    </application>
</manifest>
```

**Типы foreground service (Android 10+):**
- `camera` - Доступ к камере
- `connectedDevice` - Устройства Bluetooth/USB
- `dataSync` - Передача/синхронизация данных
- `location` - Отслеживание местоположения
- `mediaPlayback` - Воспроизведение аудио/видео
- `mediaProjection` - Запись экрана
- `microphone` - Запись аудио
- `phoneCall` - Обработка телефонных звонков

---

## Различия между версиями Android

### Android 7.1 и ниже

```kotlin
// Background и foreground работают похоже
startService(Intent(this, MyService::class.java))
```

### Android 8.0 (API 26)

**Ограничения background service:**
- Нельзя запускать background services когда приложение в фоне
- Нужно использовать `startForegroundService()` для foreground services

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)  // Нужно вызвать startForeground() в течение 5с
} else {
    startService(intent)
}
```

### Android 12 (API 31)

**Ограничения запуска foreground service:**
- Нельзя запускать foreground services из фона (с исключениями)
- Нужно использовать WorkManager или точные alarm'ы для запуска из фона

```kotlin
//  Может выбросить ForegroundServiceStartNotAllowedException на Android 12+
// если приложение в фоне
startForegroundService(intent)

//  Используйте WorkManager вместо этого
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
WorkManager.getInstance(context).enqueue(workRequest)
```

---

## Распространенные ошибки

### Ошибка 1: Использование Background Service на Android 8.0+

```kotlin
// ПЛОХО: Не работает на Android 8.0+
class MainActivity : AppCompatActivity() {
    private fun syncData() {
        startService(Intent(this, SyncService::class.java))
        // Выбрасывает IllegalStateException если приложение в фоне!
    }
}

// ХОРОШО: Используйте WorkManager
class MainActivity : AppCompatActivity() {
    private fun syncData() {
        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>().build()
        WorkManager.getInstance(this).enqueue(syncRequest)
    }
}
```

### Ошибка 2: Не вызываете startForeground() достаточно быстро

```kotlin
// ПЛОХО: Задержка перед startForeground()
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            Thread.sleep(10000)  // 10 секунд задержки
            startForeground(NOTIFICATION_ID, notification)  // Слишком поздно! Service убит
        }.start()
        return START_NOT_STICKY
    }
}

// ХОРОШО: Вызовите startForeground() немедленно
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, notification)  // В течение 5 секунд
        Thread {
            doLongRunningTask()
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }.start()
        return START_NOT_STICKY
    }
}
```

### Ошибка 3: Использование Foreground Service для откладываемых задач

```kotlin
// ПЛОХО: Foreground service для периодической синхронизации
class PeriodicSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, notification)  // Пользователь видит ненужное уведомление
        syncData()
        return START_STICKY
    }
}

// ХОРОШО: Используйте WorkManager для периодических задач
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

---

## Резюме

### Background Service
- **Работает:** В фоне, скрыт от пользователя
- **Приоритет:** Низкий (может быть убит при нехватке памяти)
- **Уведомление:** Не требуется
- **Android 8.0+:** **Сильно ограничен** (используйте WorkManager вместо этого)
- **Случай использования:** Почти никогда (используйте WorkManager для фоновых задач)

### Foreground Service
- **Работает:** С осведомленностью пользователя через уведомление
- **Приоритет:** Высокий (защищен от завершения)
- **Уведомление:** **Обязательное** постоянное уведомление
- **Android 8.0+:** Разрешен, но требует `startForegroundService()`
- **Случай использования:** Музыка, навигация, загрузки по инициативе пользователя

### Руководство по принятию решения

```
Задача видима пользователю и чувствительна ко времени?
|-- ДА → Foreground Service
-- НЕТ → Задача может быть отложена?
    |-- ДА → WorkManager
    -- НЕТ → Рассмотрите действительно ли это необходимо
        -- Если да, вероятно нужен Foreground Service
```

**Лучшая практика:** Избегайте background services на Android 8.0+. Используйте:
- **Foreground service** для задач видимых пользователю
- **WorkManager** для откладываемых фоновых задач
- **JobScheduler** для оптимизированных системой периодических задач


---

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Service

### Related (Medium)
- [[q-service-component--android--medium]] - Service
- [[q-foreground-service-types--background--medium]] - Service
- [[q-when-can-the-system-restart-a-service--android--medium]] - Service
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Service
- [[q-keep-service-running-background--android--medium]] - Service

### Advanced (Harder)
- [[q-service-lifecycle-binding--background--hard]] - Service
