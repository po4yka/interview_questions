---
id: android-261
title: How To Stop Service / Остановка Service
aliases: [How To Stop Service, Остановка Service]
topic: android
subtopics:
  - service
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-service
  - q-async-operations-android--android--medium
  - q-foreground-service-types--android--medium
  - q-how-to-fix-a-bad-element-layout--android--easy
  - q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium
  - q-when-can-the-system-restart-a-service--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/service, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Остановка `Service`

# Question (EN)
> How To Stop `Service`

---

## Ответ (RU)
Способ остановки сервиса зависит от того, как он был запущен и используется ли он как started, bound или foreground.

## `Service` Типы И Способы Остановки

### 1. Started `Service`

Сервис, запущенный через `startService()` (или `startForegroundService()`), работает, пока вы явно не остановите его через `stopSelf()` / `stopService()` (или пока система не завершит его по условиям памяти или политик).

#### Остановка Изнутри `Service`

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            // Выполняем задачу
            downloadFile()

            // Останавливаем сервис по завершении
            stopSelf()  // Запрос на остановку сервиса
        }.start()

        return START_NOT_STICKY
    }

    private fun downloadFile() {
        // Логика скачивания (пример)
        Thread.sleep(5000)
        Log.d("Service", "Download complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

Ключевые моменты:
- `stopSelf()` запрашивает остановку сервиса.
- Безопасно вызывать несколько раз.

#### Остановка Снаружи (`Activity` / `Fragment`)

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startDownloadService() {
        val intent = Intent(this, DownloadService::class.java)
        startService(intent)
    }

    private fun stopDownloadService() {
        val intent = Intent(this, DownloadService::class.java)
        val stopped = stopService(intent)

        if (stopped) {
            Log.d("MainActivity", "Service stop requested")
        } else {
            Log.d("MainActivity", "Service was not running")
        }
    }
}
```

`stopService()` возвращает:
- `true`, если соответствующий started-сервис работал и был запрошен стоп;
- `false`, если такого started-сервиса не было.

#### Множественные Запуски: `stopSelf(startId)`

Если `startService()` вызывается несколько раз, каждый вызов получает увеличивающийся `startId`.

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            downloadFile(intent?.getStringExtra("url"))

            // Запросить остановку, учитывая этот startId
            stopSelf(startId)
        }.start()

        return START_NOT_STICKY
    }

    private fun downloadFile(url: String?) {
        Log.d("Service", "Downloading: $url")
        Thread.sleep(5000)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

Как работает `stopSelf(startId)` (концептуально):

```
startService(intent1) → onStartCommand(..., startId = 1)
startService(intent2) → onStartCommand(..., startId = 2)
startService(intent3) → onStartCommand(..., startId = 3)

stopSelf(1) → сервис не остановится (последний startId = 3)
stopSelf(2) → сервис не остановится (последний startId = 3)
stopSelf(3) → сервис может быть остановлен (нет более новых startId)
```

Точнее: система останавливает сервис, если последний полученный `startId` меньше либо равен ID, переданному в `stopSelf(startId)`. Это позволяет безопасно завершать сервис только после обработки самых последних запусков.

---

### 2. Bound `Service`

Чисто bound-сервис (созданный только через `bindService()`, без `startService()`) существует, пока есть хотя бы один привязанный клиент. Когда последний клиент отвязывается, система (по умолчанию) уничтожает сервис.

#### Остановка Через Отвязку

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
            unbindService(connection)
            isBound = false
            // Если других клиентов нет и сервис не запущен как started,
            // система уничтожит его.
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        unbindFromService()
    }
}
```

Реализация `Service`:

```kotlin
class MyService : Service() {

    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): MyService = this@MyService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onUnbind(intent: Intent?): Boolean {
        Log.d("Service", "All clients unbound")
        // Для чисто bound-сервиса, когда все клиенты отвязались (и rebind не запрошен),
        // система вызовет onDestroy().
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Service destroyed")
    }
}
```

Жизненный цикл (чистый bound):

```
bindService() → onCreate() → onBind() → сервис работает
last unbindService() → onUnbind() → onDestroy() → сервис остановлен
```

---

### 3. Foreground `Service`

Foreground-сервис показывает постоянное уведомление через `startForeground()`. Чтобы корректно его остановить:

1. Остановить foreground-состояние через `stopForeground(...)`.
2. Затем остановить сам сервис (`stopSelf()` или `stopService(...)`).

#### Остановка Foreground `Service`

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
        // Шаг 1: остановить foreground-состояние и убрать уведомление
        stopForeground(STOP_FOREGROUND_REMOVE)

        // Шаг 2: остановить сервис
        stopSelf()
    }

    private fun playMusic() {
        // Логика воспроизведения музыки
    }

    private fun createNotification(): Notification {
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

Остановка из `Activity`:

```kotlin
class MainActivity : AppCompatActivity() {

    private fun stopMusicService() {
        val intent = Intent(this, MusicPlayerService::class.java).apply {
            action = MusicPlayerService.ACTION_STOP
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)  // Передаем команду остановки
        } else {
            startService(intent)
        }

        // Либо напрямую (сервис сам должен корректно обработать foreground-состояние):
        // stopService(Intent(this, MusicPlayerService::class.java))
    }
}
```

Флаги `stopForeground()`:
- `STOP_FOREGROUND_REMOVE`: сразу убрать уведомление.
- `STOP_FOREGROUND_DETACH`: оставить уведомление, отвязав его от foreground-сервиса.

---

## Смешанный `Service` (Started + Bound)

Сервис может быть одновременно started и bound. Он уничтожается только когда:
- started-состояние очищено (`stopSelf()` / `stopService()` обработан), И
- не осталось привязанных клиентов.

Пример:

```kotlin
class HybridService : Service() {

    private val binder = LocalBinder()
    private var isStarted = false
    private var boundClients = 0

    inner class LocalBinder : Binder() {
        fun getService(): HybridService = this@HybridService
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        isStarted = true
        Log.d("Service", "Service started")
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        boundClients++
        Log.d("Service", "Client bound, count=$boundClients")
        return binder
    }

    override fun onUnbind(intent: Intent?): Boolean {
        boundClients--
        Log.d("Service", "Client unbound, count=$boundClients")
        checkIfShouldStop()
        return super.onUnbind(intent)
    }

    fun stopStartedState() {
        // Вызываем, когда работа started-состояния завершена
        isStarted = false
        checkIfShouldStop()
    }

    private fun checkIfShouldStop() {
        if (!isStarted && boundClients == 0) {
            stopSelf()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Service destroyed")
    }
}
```

Сценарии жизненного цикла (концептуально):

```
Сценарий 1: только started
startService() → onStartCommand()
stopService() / stopSelf() → onDestroy()  (остановка)

Сценарий 2: только bound
bindService() → onCreate() → onBind()
last unbindService() → onUnbind() → onDestroy()  (остановка)

Сценарий 3: Started + Bound
startService() → onStartCommand()
bindService() → onBind()
unbindService() → onUnbind()
    сервис еще работает (он started)
stopService() / stopSelf() → onDestroy()  (теперь остановлен)

Сценарий 4: Started + Bound (обратный порядок)
startService() → onStartCommand()
bindService() → onBind()
stopService() / stopSelf() → очистка started-состояния
    сервис еще работает (есть клиент)
unbindService() → onUnbind() → onDestroy()  (теперь остановлен)
```

---

## Полный Пример: Foreground `Service` Для Скачивания С Остановкой

```kotlin
class DownloadService : Service() {

    private val NOTIFICATION_ID = 1
    private var downloadJob: Job? = null
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

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
        downloadJob?.cancel()

        downloadJob = serviceScope.launch {
            try {
                for (i in 1..100) {
                    ensureActive()
                    delay(100)
                    updateNotification("Downloading: $i%")
                }

                updateNotification("Download complete")
                delay(2000)
                stopForegroundAndService()
            } catch (e: CancellationException) {
                Log.d("Service", "Download cancelled")
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
        serviceScope.cancel()
        Log.d("Service", "Service destroyed")
    }

    companion object {
        const val ACTION_START_DOWNLOAD = "ACTION_START_DOWNLOAD"
        const val ACTION_CANCEL_DOWNLOAD = "ACTION_CANCEL_DOWNLOAD"
    }
}
```

`Activity`:

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

## Частые Ошибки

### Ошибка 1: Неправильная Работа С Foreground-состоянием

Плохо (неявный teardown foreground):

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)

    Thread {
        doWork()
        stopSelf()  // Сервис остановится; поведение уведомления зависит от системы.
    }.start()

    return START_NOT_STICKY
}
```

Лучше (явно и предсказуемо):

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)

    Thread {
        doWork()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }.start()

    return START_NOT_STICKY
}
```

### Ошибка 2: Вызов `stopSelf()` До Завершения Асинхронной Работы

Плохо:

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        doLongRunningTask()
    }.start()

    stopSelf()
    return START_NOT_STICKY
}
```

Хорошо:

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        doLongRunningTask()
        stopSelf()
    }.start()

    return START_NOT_STICKY
}
```

### Ошибка 3: Игнорирование Различий Started Vs Bound В Смешанном Сервисе

Плохо (предполагаем, что `stopSelf()` всегда достаточно, независимо от bound-клиентов):

```kotlin
class MyService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        doWork()
        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder = binder
}
```

Лучше (отслеживаем оба состояния):

```kotlin
class MyService : Service() {

    private var boundClientCount = 0
    private var isStarted = false

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        isStarted = true
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
        if (!isStarted && boundClientCount == 0) {
            stopSelf()
        }
    }
}
```

---

## Резюме

Как останавливать сервис:

Started `Service` (`startService()` / `startForegroundService()`):
- Внутри: `stopSelf()` или `stopSelf(startId)`.
- Снаружи: `stopService(intent)`.
- Используйте `stopSelf(startId)` для корректной работы с несколькими вызовами `startService()`.

Bound `Service` (`bindService()` только):
- Клиенты вызывают `unbindService(connection)`.
- Когда последний клиент отвязался (и сервис не started), система уничтожает сервис.

Foreground `Service`:
- Сначала остановите foreground: `stopForeground(STOP_FOREGROUND_REMOVE)` (или другой флаг).
- Затем остановите сервис: `stopSelf()` или `stopService(intent)`.

Смешанный `Service` (Started + Bound):
- Сервис уничтожается только после того, как:
  - все клиенты отвязались, И
  - started-состояние очищено (`stopSelf()` / `stopService()`).

Лучшие практики:
- Явно останавливать foreground-состояние перед остановкой foreground-сервиса.
- Использовать `stopSelf(startId)` при множественных запусках.
- Освобождать ресурсы и отменять асинхронную работу (потоки/корутины) в `onDestroy()`.
- Не выполнять долгие операции в главном потоке; использовать корректные механизмы фонового выполнения.

---

## Answer (EN)
The method to stop a service depends on how it was started and whether it is also bound/foreground:

1. Started `Service` (via `startService()` / `startForegroundService()`):
   - From within the service: `stopSelf()` or `stopSelf(startId)`
   - From outside: `stopService(intent)`

2. Bound `Service` (via `bindService()` only):
   - From clients: `unbindService(connection)`

3. Foreground `Service`:
   - Stop foreground state with `stopForeground(...)`, then stop the service (`stopSelf()` / `stopService(...)`).

4. Mixed (Started + Bound):
   - Must clear the started state AND have all clients unbound before the system destroys the service.

---

## `Service` Types and Stopping Methods

### 1. Started `Service`

A service started with `startService()` (or `startForegroundService()`) runs until you explicitly stop it with `stopSelf()`/`stopService()` (or the system kills it under memory pressure or policy constraints).

#### Stop from Within the `Service`

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            // Perform task
            downloadFile()

            // Stop service when done
            stopSelf()  // Request to stop this service
        }.start()

        return START_NOT_STICKY
    }

    private fun downloadFile() {
        // Download logic (example only)
        Thread.sleep(5000)
        Log.d("Service", "Download complete")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

Key points:
- `stopSelf()` requests that the service be stopped.
- Safe to call multiple times.

---

#### Stop from Outside (`Activity`/`Fragment`)

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startDownloadService() {
        val intent = Intent(this, DownloadService::class.java)
        startService(intent)
    }

    private fun stopDownloadService() {
        val intent = Intent(this, DownloadService::class.java)
        val stopped = stopService(intent)

        if (stopped) {
            Log.d("MainActivity", "Service stop requested")
        } else {
            Log.d("MainActivity", "Service was not running")
        }
    }
}
```

`stopService()` returns:
- `true` if a matching started service was running and a stop was requested.
- `false` if no such started service was running.

---

#### Multiple Starts: `stopSelf(startId)`

If `startService()` is called multiple times, each call receives an incrementing `startId`.

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            downloadFile(intent?.getStringExtra("url"))

            // Request to stop based on this startId
            stopSelf(startId)
        }.start()

        return START_NOT_STICKY
    }

    private fun downloadFile(url: String?) {
        Log.d("Service", "Downloading: $url")
        Thread.sleep(5000)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

How `stopSelf(startId)` works conceptually:

```
startService(intent1) → onStartCommand(..., startId = 1)
startService(intent2) → onStartCommand(..., startId = 2)
startService(intent3) → onStartCommand(..., startId = 3)

stopSelf(1) → no stop yet (latest startId is 3)
stopSelf(2) → no stop yet (latest startId is 3)
stopSelf(3) → service can stop (no newer startIds)
```

More precisely: the system stops the service if the most recent start ID is less than or equal to the ID you pass. This lets you safely stop only after handling the most recent start.

---

### 2. Bound `Service`

A purely bound service (created only via `bindService()`, without `startService()`) exists as long as there is at least one bound client. When the last client unbinds, the system will (by default) destroy the service.

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
            unbindService(connection)
            isBound = false
            // If there are no other clients and the service is not started,
            // the system will destroy it.
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        unbindFromService()
    }
}
```

`Service` implementation:

```kotlin
class MyService : Service() {

    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): MyService = this@MyService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onUnbind(intent: Intent?): Boolean {
        Log.d("Service", "All clients unbound")
        // For a purely bound service, once all clients unbind (and no rebind is requested),
        // the system will call onDestroy().
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Service destroyed")
    }
}
```

Lifecycle (purely bound):

```
bindService() → onCreate() → onBind() → Service running
last unbindService() → onUnbind() → onDestroy() → Service stopped
```

---

### 3. Foreground `Service`

A foreground service shows a persistent notification via `startForeground()`. To stop it cleanly:

1. Stop the foreground state with `stopForeground(...)`.
2. Then stop the service (`stopSelf()` or `stopService(...)`).

#### Stop Foreground `Service`

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
        stopForeground(STOP_FOREGROUND_REMOVE)

        // Step 2: Stop the service
        stopSelf()
    }

    private fun playMusic() {
        // Music playback logic
    }

    private fun createNotification(): Notification {
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

Stop from `Activity`:

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

        // Alternatively, stop directly (service must handle foreground state):
        // stopService(Intent(this, MusicPlayerService::class.java))
    }
}
```

`stopForeground()` flags:
- `STOP_FOREGROUND_REMOVE`: Remove notification immediately.
- `STOP_FOREGROUND_DETACH`: Keep notification but detach it from foreground service.

---

## Mixed `Service` (Started + Bound)

A service can be both started and bound. It is destroyed only when:
- The started state is cleared (`stopSelf()` / `stopService()` has been processed), AND
- No clients remain bound.

Example:

```kotlin
class HybridService : Service() {

    private val binder = LocalBinder()
    private var isStarted = false
    private var boundClients = 0

    inner class LocalBinder : Binder() {
        fun getService(): HybridService = this@HybridService
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        isStarted = true
        Log.d("Service", "Service started")
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        boundClients++
        Log.d("Service", "Client bound, count=$boundClients")
        return binder
    }

    override fun onUnbind(intent: Intent?): Boolean {
        boundClients--
        Log.d("Service", "Client unbound, count=$boundClients")
        checkIfShouldStop()
        return super.onUnbind(intent)
    }

    fun stopStartedState() {
        // Call when started work is done to clear started state
        isStarted = false
        checkIfShouldStop()
    }

    private fun checkIfShouldStop() {
        if (!isStarted && boundClients == 0) {
            stopSelf()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Service destroyed")
    }
}
```

Lifecycle scenarios (conceptual):

```
Scenario 1: Started only
startService() → onStartCommand()
stopService() / stopSelf() → onDestroy()  (stops)

Scenario 2: Bound only
bindService() → onCreate() → onBind()
last unbindService() → onUnbind() → onDestroy()  (stops)

Scenario 3: Started + Bound
startService() → onStartCommand()
bindService() → onBind()
unbindService() → onUnbind()
    Service still running (because started)
stopService() / stopSelf() → onDestroy()  (now stops)

Scenario 4: Started + Bound (reverse order)
startService() → onStartCommand()
bindService() → onBind()
stopService() / stopSelf() → clear started state
    Service still running (client bound)
unbindService() → onUnbind() → onDestroy()  (now stops)
```

---

## Complete Example: Download Foreground `Service` with Stop

```kotlin
class DownloadService : Service() {

    private val NOTIFICATION_ID = 1
    private var downloadJob: Job? = null
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

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
        downloadJob?.cancel()

        downloadJob = serviceScope.launch {
            try {
                for (i in 1..100) {
                    ensureActive()
                    delay(100)
                    updateNotification("Downloading: $i%")
                }

                updateNotification("Download complete")
                delay(2000)
                stopForegroundAndService()
            } catch (e: CancellationException) {
                Log.d("Service", "Download cancelled")
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
        serviceScope.cancel()
        Log.d("Service", "Service destroyed")
    }

    companion object {
        const val ACTION_START_DOWNLOAD = "ACTION_START_DOWNLOAD"
        const val ACTION_CANCEL_DOWNLOAD = "ACTION_CANCEL_DOWNLOAD"
    }
}
```

`Activity`:

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

### Mistake 1: Not Handling Foreground State Properly

Bad (implicit foreground teardown):

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)

    Thread {
        doWork()
        stopSelf()  // Service will stop; notification removal depends on system behavior.
    }.start()

    return START_NOT_STICKY
}
```

Better (explicit and predictable):

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)

    Thread {
        doWork()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }.start()

    return START_NOT_STICKY
}
```

### Mistake 2: Calling `stopSelf()` Before Async Work Completes

Bad:

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        doLongRunningTask()
    }.start()

    stopSelf()
    return START_NOT_STICKY
}
```

Good:

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        doLongRunningTask()
        stopSelf()
    }.start()

    return START_NOT_STICKY
}
```

### Mistake 3: Ignoring Started Vs Bound States in a Mixed `Service`

Bad (assuming `stopSelf()` is always enough regardless of bound clients):

```kotlin
class MyService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        doWork()
        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder = binder
}
```

Better (track both states):

```kotlin
class MyService : Service() {

    private var boundClientCount = 0
    private var isStarted = false

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        isStarted = true
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
        if (!isStarted && boundClientCount == 0) {
            stopSelf()
        }
    }
}
```

---

## Summary

How to stop a service:

Started `Service` (`startService()` / `startForegroundService()`):
- From within: `stopSelf()` or `stopSelf(startId)`.
- From outside: `stopService(intent)`.
- Use `stopSelf(startId)` to coordinate multiple `startService()` calls.

Bound `Service` (`bindService()` only):
- Clients call `unbindService(connection)`.
- When the last client unbinds (and the service is not also started), the system destroys the service.

Foreground `Service`:
- Stop foreground state: `stopForeground(STOP_FOREGROUND_REMOVE)` (or appropriate flag).
- Then stop service: `stopSelf()` or `stopService(intent)`.

Mixed `Service` (Started + Bound):
- `Service` is destroyed only after:
  - all clients unbind, AND
  - started state has been cleared via `stopSelf()` / `stopService()`.

Best practices:
- Explicitly stop foreground state before stopping a foreground service.
- Use `stopSelf(startId)` with multiple `startService()` calls.
- Clean up resources and cancel async work (threads/coroutines) in `onDestroy()`.
- Avoid long-running work on the main thread; use proper background execution.

---

## Follow-ups

- [[q-async-operations-android--android--medium]]
- [[q-how-to-fix-a-bad-element-layout--android--easy]]

## References

- [Services](https://developer.android.com/develop/background-work/services)

## Related Questions

### Prerequisites / Concepts

- [[c-service]]

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - `Service`

### Related (Medium)
- [[q-service-component--android--medium]] - `Service`
- [[q-foreground-service-types--android--medium]] - `Service`
- [[q-when-can-the-system-restart-a-service--android--medium]] - `Service`
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - `Service`
- [[q-keep-service-running-background--android--medium]] - `Service`

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - `Service`
