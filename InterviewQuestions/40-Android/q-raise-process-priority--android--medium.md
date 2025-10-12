---
topic: android
tags:
  - android
  - android/foreground-service
  - android/services
  - foreground-service
  - lifecycle
  - process-priority
  - services
difficulty: medium
status: draft
---

# Можно ли поднять приоритет процесса?

**English**: Can you raise the priority of a process?

## Answer (EN)
**Yes**, you can raise the priority of a process in Android using **`startForeground()`** in Services. This makes the service run as a **foreground service**, ensuring it has **high priority** and is protected from being killed by the system.

---

## Process Priority in Android

### Process Priority Levels

Android uses a **hierarchy of process importance** to decide which processes to keep when memory is low:

```
┌─────────────────────────────────────┐
│ 1. Foreground Process (Highest)    │ ← Active UI or foreground service
├─────────────────────────────────────┤
│ 2. Visible Process                  │ ← Visible but not in focus
├─────────────────────────────────────┤
│ 3. Service Process                  │ ← Running service (background)
├─────────────────────────────────────┤
│ 4. Cached Process                   │ ← Recently used, no active components
├─────────────────────────────────────┤
│ 5. Empty Process (Lowest)           │ ← No components, killed first
└─────────────────────────────────────┘
```

**System behavior:**
- When memory is low, Android kills processes **starting from the bottom**
- Foreground processes are **last to be killed**
- Background services can be killed **anytime** to free memory

---

## Raising Priority with startForeground()

### 1. Standard Background Service (Low Priority)

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // - Background service - can be killed anytime
        Thread {
            // Long-running download
            for (i in 1..100) {
                Thread.sleep(1000)
                // May be killed before completion!
            }
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Problem:** System can kill this service when memory is low, interrupting the download.

---

### 2. Foreground Service (High Priority)

```kotlin
class DownloadService : Service() {
    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // - Raise priority with startForeground()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        Thread {
            // Long-running download
            for (i in 1..100) {
                Thread.sleep(1000)
                updateNotification(i)
                // Protected from being killed!
            }
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
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(progress: Int) {
        val notification = NotificationCompat.Builder(this, "download_channel")
            .setContentTitle("Downloading")
            .setContentText("Progress: $progress%")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()

        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Benefits:**
- **High priority** - System won't kill the service easily
- **User visibility** - Notification shows ongoing work
- **Guaranteed completion** - Download won't be interrupted

---

## Starting a Foreground Service

### From Activity/Fragment

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startDownload() {
        val intent = Intent(this, DownloadService::class.java)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // - Android 8.0+ requires startForegroundService()
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}
```

**Important:** On Android 8.0+, you **must** call `startForeground()` within **5 seconds** of starting the service, or the system will kill it.

---

## Complete Example: Music Player Service

```kotlin
class MusicPlayerService : Service() {
    private val NOTIFICATION_ID = 100
    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> {
                startForeground(NOTIFICATION_ID, createNotification("Playing"))
                playMusic()
            }
            ACTION_PAUSE -> {
                pauseMusic()
                // Still foreground, just update notification
                updateNotification("Paused")
            }
            ACTION_STOP -> {
                stopMusic()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }

        return START_STICKY
    }

    private fun createNotification(status: String): Notification {
        val channelId = "music_player_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Music Player",
                NotificationManager.IMPORTANCE_LOW
            )
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        // Create intent for tapping notification
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )

        // Create action intents
        val playIntent = createActionIntent(ACTION_PLAY)
        val pauseIntent = createActionIntent(ACTION_PAUSE)
        val stopIntent = createActionIntent(ACTION_STOP)

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Music Player")
            .setContentText(status)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setContentIntent(pendingIntent)
            .addAction(android.R.drawable.ic_media_play, "Play", playIntent)
            .addAction(android.R.drawable.ic_media_pause, "Pause", pauseIntent)
            .addAction(android.R.drawable.ic_delete, "Stop", stopIntent)
            .setOngoing(true)
            .build()
    }

    private fun createActionIntent(action: String): PendingIntent {
        val intent = Intent(this, MusicPlayerService::class.java).apply {
            this.action = action
        }
        return PendingIntent.getService(
            this,
            action.hashCode(),
            intent,
            PendingIntent.FLAG_IMMUTABLE
        )
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

---

## Process Priority Comparison

### Before startForeground()

```
Process Priority: Service Process (Level 3)
┌─────────────────────────────────────┐
│ App Process                         │
│ └── DownloadService                 │
│     └── Background work             │
└─────────────────────────────────────┘

System: "Low memory! Kill this service."
Result: - Service killed, work interrupted
```

### After startForeground()

```
Process Priority: Foreground Process (Level 1)
┌─────────────────────────────────────┐
│ App Process                         │
│ └── DownloadService (Foreground)    │
│     ├── Notification visible        │
│     └── Protected work              │
└─────────────────────────────────────┘

System: "Low memory! But this is foreground, keep it."
Result: - Service protected, work continues
```

---

## Other Ways to Influence Priority

### 1. Process Importance (Read-Only)

```kotlin
// - Can't directly set this
// It's determined by Android based on components
val activityManager = getSystemService(ActivityManager::class.java)
val processes = activityManager.runningAppProcesses

for (process in processes) {
    if (process.processName == packageName) {
        when (process.importance) {
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND ->
                Log.d("Priority", "Foreground")
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_SERVICE ->
                Log.d("Priority", "Service")
            // Can't change this value directly!
        }
    }
}
```

### 2. Bound Service with Foreground Activity

```kotlin
// When activity binds to service, service inherits activity's priority
class MyActivity : AppCompatActivity() {
    private var service: MyService? = null

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            service = (binder as MyService.LocalBinder).getService()
            // Service now has higher priority (visible process level)
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            service = null
        }
    }

    override fun onStart() {
        super.onStart()
        bindService(Intent(this, MyService::class.java), connection, BIND_AUTO_CREATE)
    }

    override fun onStop() {
        super.onStop()
        unbindService(connection)
        // Service priority drops back down
    }
}
```

### 3. JobScheduler (For Background Tasks)

```kotlin
// - System manages priority based on constraints
val jobScheduler = getSystemService(JobScheduler::class.java)

val job = JobInfo.Builder(JOB_ID, ComponentName(this, MyJobService::class.java))
    .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
    .setPriority(JobInfo.PRIORITY_HIGH)  // Hint to system
    .build()

jobScheduler.schedule(job)
```

**Note:** Priority is a **hint**, not a guarantee. System still decides based on resources.

---

## Limitations and Best Practices

### Limitations

1. **Notification Required**
   ```kotlin
   // - Can't do this on Android 8.0+
   startForeground(NOTIFICATION_ID, null)  // Crashes!

   // - Must provide notification
   startForeground(NOTIFICATION_ID, createNotification())
   ```

2. **User Visibility**
   - Foreground service **must** show a **persistent notification**
   - User sees the service is running
   - Can't hide it

3. **Android 12+ Restrictions**
   ```kotlin
   // Android 12+ restricts starting foreground services from background
   if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
       // Need to use WorkManager or exact alarm for background starts
   }
   ```

### Best Practices

1. **Only Use When Necessary**
   ```kotlin
   // - DON'T: Foreground service for simple background task
   class SimpleTaskService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(1, notification)  // Overkill!
           doSimpleTask()  // Could use WorkManager instead
           return START_NOT_STICKY
       }
   }

   // - DO: Foreground service for user-visible long-running task
   class NavigationService : Service() {
       override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
           startForeground(1, notification)
           startNavigation()  // User expects this to continue
           return START_STICKY
       }
   }
   ```

2. **Stop Foreground When Done**
   ```kotlin
   // - Always stop foreground when task completes
   fun completeTask() {
       stopForeground(STOP_FOREGROUND_REMOVE)  // Remove notification
       stopSelf()  // Stop service
   }
   ```

3. **Use Appropriate Service Type (Android 10+)**
   ```kotlin
   // Manifest
   <service
       android:name=".LocationService"
       android:foregroundServiceType="location" />

   // Code
   startForeground(
       NOTIFICATION_ID,
       notification,
       ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
   )
   ```

---

## Summary

**Can you raise process priority?**
- **Yes**, using `startForeground()` in services
- Makes service a **foreground service** with high priority
- Requires a **visible notification**
- **Protects** from being killed by the system

**How it works:**
1. Call `startForeground(id, notification)` in service
2. Service moves from **Service Process** → **Foreground Process**
3. System gives **high priority**, won't kill easily
4. User sees **persistent notification**

**When to use:**
- - Music playback
- - Navigation/location tracking
- - File download/upload (user-initiated)
- - Active fitness tracking
- - Simple background tasks (use WorkManager)
- - Periodic sync (use JobScheduler)

**Other priority influences:**
- Bound service with foreground activity (inherits priority)
- JobScheduler priority hints
- Process importance (read-only, managed by system)

**Best practices:**
- Only use when **truly necessary**
- Stop foreground when task completes
- Use appropriate service type (Android 10+)
- Consider WorkManager for deferrable tasks

---

## Ответ (RU)
**Да**, можно поднять приоритет процесса используя **`startForeground()`** в сервисах. Это позволяет сервису работать как **foreground service**, обеспечивая его **высокий приоритет** и защиту от уничтожения системой.

**Как это работает:**
1. Вызовите `startForeground(id, notification)` в сервисе
2. Сервис переходит из **Service Process** → **Foreground Process**
3. Система дает **высокий приоритет**, не убивает просто так
4. Пользователь видит **постоянное уведомление**

**Когда использовать:**
- Воспроизведение музыки
- Навигация/отслеживание местоположения
- Скачивание/загрузка файлов
- НЕ для простых фоновых задач (используйте WorkManager)

**Пример:**

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Поднимаем приоритет
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        // Теперь сервис защищен от уничтожения
        performDownload()

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
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }
}
```

**Важно:**
- На Android 8.0+ необходимо вызвать `startForeground()` в течение 5 секунд после запуска сервиса
- Обязательно требуется видимое уведомление
- Всегда вызывайте `stopForeground()` и `stopSelf()` когда задача завершена
- Используйте только когда действительно необходимо - для задач, которые пользователь ожидает увидеть работающими

