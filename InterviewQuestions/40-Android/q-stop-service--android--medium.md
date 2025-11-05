---
id: android-261
title: "How To Stop Service / Остановка Service"
aliases: [How To Stop Service, Остановка Service]
topic: android
subtopics: [service]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-async-operations-android--android--medium, q-derived-state-snapshot-system--jetpack-compose--hard, q-how-to-fix-a-bad-element-layout--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [android/service, difficulty/medium]
date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Как Остановить Сервис?

**English**: How to stop a service?

## Answer (EN)
The method to stop a service depends on **how it was started**:

1. **Started Service** (via `startService()`):
   - From within the service: `stopSelf()`
   - From outside: `stopService(intent)`

2. **Bound Service** (via `bindService()`):
   - Call `unbindService(connection)`

3. **Foreground Service**:
   - Call `stopForeground()` first, then `stopSelf()` or `stopService()`

---

## Service Types and Stopping Methods

### 1. Started Service

A service started with `startService()` runs **indefinitely** until explicitly stopped.

#### Stop from Within the Service

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            // Perform task
            downloadFile()

            // Stop service when done
            stopSelf()  // - Stops this service
        }.start()

        return START_NOT_STICKY
    }

    private fun downloadFile() {
        // Download logic
        Thread.sleep(5000)
        Log.d("Service", "Download complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Key points:**
- `stopSelf()` stops the service from within
- Service stops **after** all work is done
- Safe to call even if service is already stopping

---

#### Stop from Outside (Activity/Fragment)

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startDownloadService() {
        val intent = Intent(this, DownloadService::class.java)
        startService(intent)
    }

    private fun stopDownloadService() {
        val intent = Intent(this, DownloadService::class.java)
        val stopped = stopService(intent)  // - Stops the service

        if (stopped) {
            Log.d("MainActivity", "Service stopped successfully")
        } else {
            Log.d("MainActivity", "Service was not running")
        }
    }
}
```

**Returns:**
- `true` if the service was running and is now stopped
- `false` if the service was not running

---

#### Stop Specific Request (Multiple Starts)

If `startService()` is called **multiple times**, you can stop a specific request:

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            downloadFile(intent?.getStringExtra("url"))

            // Stop only this specific start request
            stopSelf(startId)  // - Stops service if no other startId is active
        }.start()

        return START_NOT_STICKY
    }

    private fun downloadFile(url: String?) {
        // Download logic
        Log.d("Service", "Downloading: $url")
        Thread.sleep(5000)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**How it works:**
```
startService(intent1) → startId = 1
startService(intent2) → startId = 2
startService(intent3) → startId = 3

stopSelf(1) → Service continues (startId 2, 3 still active)
stopSelf(2) → Service continues (startId 3 still active)
stopSelf(3) → Service stops (no active startIds)
```

---

### 2. Bound Service

A service started with `bindService()` runs **as long as clients are bound** to it.

#### Stop by Unbinding

```kotlin
class MyActivity : AppCompatActivity() {

    private var myService: MyService? = null
    private var isBound = false

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            val serviceBinder = binder as MyService.LocalBinder
            myService = serviceBinder.getService()
            isBound = true
            Log.d("Activity", "Service connected")
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            myService = null
            isBound = false
            Log.d("Activity", "Service disconnected")
        }
    }

    private fun bindToService() {
        val intent = Intent(this, MyService::class.java)
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    private fun unbindFromService() {
        if (isBound) {
            unbindService(connection)  // - Unbind from service
            isBound = false
            // Service stops automatically if no other clients are bound
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        unbindFromService()
    }
}
```

**Service implementation:**

```kotlin
class MyService : Service() {

    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): MyService = this@MyService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onUnbind(intent: Intent?): Boolean {
        Log.d("Service", "All clients unbound")
        // Service stops automatically after this
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Service destroyed")
    }
}
```

**Lifecycle:**
```
bindService() → onCreate() → onBind() → Service running
unbindService() → onUnbind() → onDestroy() → Service stopped
```

---

### 3. Foreground Service

A foreground service requires **stopping the foreground state** before stopping the service.

#### Stop Foreground Service

```kotlin
class MusicPlayerService : Service() {

    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> {
                startForeground(NOTIFICATION_ID, createNotification())
                playMusic()
            }
            ACTION_STOP -> {
                stopForegroundAndService()
            }
        }

        return START_STICKY
    }

    private fun stopForegroundAndService() {
        // Step 1: Stop foreground state and remove notification
        stopForeground(STOP_FOREGROUND_REMOVE)  // or STOP_FOREGROUND_DETACH

        // Step 2: Stop the service
        stopSelf()
    }

    private fun playMusic() {
        // Music playback logic
    }

    private fun createNotification(): Notification {
        // Notification creation
        return NotificationCompat.Builder(this, "music_channel")
            .setContentTitle("Music Player")
            .setContentText("Playing...")
            .setSmallIcon(android.R.drawable.ic_media_play)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Music service destroyed")
    }

    companion object {
        const val ACTION_PLAY = "ACTION_PLAY"
        const val ACTION_STOP = "ACTION_STOP"
    }
}
```

**Stop from Activity:**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun stopMusicService() {
        val intent = Intent(this, MusicPlayerService::class.java).apply {
            action = MusicPlayerService.ACTION_STOP
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)  // Deliver stop command
        } else {
            startService(intent)
        }

        // Alternative: Stop directly
        // stopService(Intent(this, MusicPlayerService::class.java))
    }
}
```

**`stopForeground()` flags:**

| Flag | Behavior |
|------|----------|
| `STOP_FOREGROUND_REMOVE` | Remove notification immediately |
| `STOP_FOREGROUND_DETACH` | Keep notification, but detach from service |

---

## Mixed Service (Started + Bound)

A service can be **both started and bound**. It stops only when:
- All clients have **unbound**
- **AND** `stopSelf()` or `stopService()` is called

### Example

```kotlin
class HybridService : Service() {

    private val binder = LocalBinder()
    private var isStarted = false

    inner class LocalBinder : Binder() {
        fun getService(): HybridService = this@HybridService
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        isStarted = true
        Log.d("Service", "Service started")
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        Log.d("Service", "Client bound")
        return binder
    }

    override fun onUnbind(intent: Intent?): Boolean {
        Log.d("Service", "Client unbound")
        checkIfShouldStop()
        return super.onUnbind(intent)
    }

    fun stopService() {
        isStarted = false
        checkIfShouldStop()
    }

    private fun checkIfShouldStop() {
        // Stop only if:
        // 1. No clients are bound (checked by system)
        // 2. Service was explicitly stopped
        if (!isStarted) {
            stopSelf()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Service destroyed")
    }
}
```

**Lifecycle scenarios:**

```
Scenario 1: Started only
startService() → onStartCommand()
stopService() → onDestroy()  - Stops

Scenario 2: Bound only
bindService() → onCreate() → onBind()
unbindService() → onUnbind() → onDestroy()  - Stops

Scenario 3: Started + Bound
startService() → onStartCommand()
bindService() → onBind()
unbindService() → onUnbind()
                  Service still running!  WARNING
stopService() → onDestroy()  - Now stops

Scenario 4: Started + Bound (different order)
startService() → onStartCommand()
bindService() → onBind()
stopService() → stopSelf() called
                Service still running (client bound)!  WARNING
unbindService() → onUnbind() → onDestroy()  - Now stops
```

---

## Complete Example: Download Service with Stop

```kotlin
class DownloadService : Service() {

    private val NOTIFICATION_ID = 1
    private var downloadJob: Job? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_DOWNLOAD -> {
                startForeground(NOTIFICATION_ID, createNotification("Starting..."))
                startDownload()
            }
            ACTION_CANCEL_DOWNLOAD -> {
                cancelDownload()
                stopForegroundAndService()
            }
        }

        return START_NOT_STICKY
    }

    private fun startDownload() {
        downloadJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                for (i in 1..100) {
                    // Check if cancelled
                    if (!isActive) {
                        Log.d("Service", "Download cancelled")
                        return@launch
                    }

                    delay(100)
                    updateNotification("Downloading: $i%")
                }

                updateNotification("Download complete")
                delay(2000)
                stopForegroundAndService()
            } catch (e: Exception) {
                Log.e("Service", "Download failed", e)
                stopForegroundAndService()
            }
        }
    }

    private fun cancelDownload() {
        downloadJob?.cancel()
        downloadJob = null
    }

    private fun stopForegroundAndService() {
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun createNotification(text: String): Notification {
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

        // Cancel intent
        val cancelIntent = Intent(this, DownloadService::class.java).apply {
            action = ACTION_CANCEL_DOWNLOAD
        }
        val cancelPendingIntent = PendingIntent.getService(
            this,
            0,
            cancelIntent,
            PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Download Service")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .addAction(android.R.drawable.ic_delete, "Cancel", cancelPendingIntent)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(text: String) {
        val notification = createNotification(text)
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        cancelDownload()
        Log.d("Service", "Service destroyed")
    }

    companion object {
        const val ACTION_START_DOWNLOAD = "ACTION_START_DOWNLOAD"
        const val ACTION_CANCEL_DOWNLOAD = "ACTION_CANCEL_DOWNLOAD"
    }
}
```

**Activity:**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startDownload() {
        val intent = Intent(this, DownloadService::class.java).apply {
            action = DownloadService.ACTION_START_DOWNLOAD
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    private fun cancelDownload() {
        val intent = Intent(this, DownloadService::class.java).apply {
            action = DownloadService.ACTION_CANCEL_DOWNLOAD
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}
```

---

## Common Mistakes

### Mistake 1: Not Stopping Foreground State First

```kotlin
// - BAD: Stopping service without stopping foreground
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)

    Thread {
        doWork()
        stopSelf()  // - Notification might remain!
    }.start()

    return START_NOT_STICKY
}

// - GOOD: Stop foreground first
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)

    Thread {
        doWork()
        stopForeground(STOP_FOREGROUND_REMOVE)  // - Remove notification
        stopSelf()  // - Then stop service
    }.start()

    return START_NOT_STICKY
}
```

### Mistake 2: Calling stopSelf() Too Early

```kotlin
// - BAD: stopSelf() before async work completes
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        doLongRunningTask()  // 10 seconds
    }.start()

    stopSelf()  // - Service stops immediately, thread might be killed!
    return START_NOT_STICKY
}

// - GOOD: stopSelf() after work completes
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        doLongRunningTask()  // 10 seconds
        stopSelf()  // - Stop after work is done
    }.start()

    return START_NOT_STICKY
}
```

### Mistake 3: Not Handling Bound Service Properly

```kotlin
// - BAD: stopSelf() while clients are still bound
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        doWork()
        stopSelf()  // - Won't stop if clients are bound!
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder = binder
}

// - GOOD: Check if service is bound before stopping
class MyService : Service() {
    private var boundClientCount = 0

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        doWork()
        checkIfShouldStop()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        boundClientCount++
        return binder
    }

    override fun onUnbind(intent: Intent?): Boolean {
        boundClientCount--
        checkIfShouldStop()
        return super.onUnbind(intent)
    }

    private fun checkIfShouldStop() {
        if (boundClientCount == 0) {
            stopSelf()  // - Safe to stop
        }
    }
}
```

---

## Summary

**How to stop a service:**

### **Started Service** (`startService()`)
- **From within:** `stopSelf()` or `stopSelf(startId)`
- **From outside:** `stopService(intent)`
- Service stops when **explicitly stopped**

### **Bound Service** (`bindService()`)
- **From client:** `unbindService(connection)`
- Service stops when **all clients unbind**

### **Foreground Service**
1. **Stop foreground state:** `stopForeground(STOP_FOREGROUND_REMOVE)`
2. **Stop service:** `stopSelf()` or `stopService(intent)`

### **Mixed Service** (Started + Bound)
- Must **unbind all clients** AND **call stopSelf()/stopService()**
- Order doesn't matter - both must happen

**Best practices:**
1. - Always `stopForeground()` before `stopSelf()` for foreground services
2. - Use `stopSelf(startId)` to handle multiple start requests
3. - Clean up resources in `onDestroy()`
4. - Cancel ongoing work when service stops

---

## Ответ (RU)
Способ остановки сервиса зависит от **типа сервиса**:

### **Started Service** (`startService()`)
- **Внутри сервиса:** `stopSelf()`
- **Снаружи:** `stopService(intent)`

### **Bound Service** (`bindService()`)
- **Из клиента:** `unbindService(connection)`
- Сервис останавливается когда все клиенты отвяжутся

### **Foreground Service**
1. Остановить foreground: `stopForeground(STOP_FOREGROUND_REMOVE)`
2. Остановить сервис: `stopSelf()` или `stopService()`

### **Смешанный сервис** (Started + Bound)
- Необходимо **отвязать всех клиентов** И **вызвать stopSelf()/stopService()**


---


## Follow-ups

- Follow-up questions to be populated

## References

- References to be populated
## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Service

### Related (Medium)
- [[q-service-component--android--medium]] - Service
- [[q-foreground-service-types--android--medium]] - Service
- [[q-when-can-the-system-restart-a-service--android--medium]] - Service
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Service
- [[q-keep-service-running-background--android--medium]] - Service

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Service
