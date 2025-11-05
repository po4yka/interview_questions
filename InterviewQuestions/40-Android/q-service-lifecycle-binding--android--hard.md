---
id: android-325
title: "Service Lifecycle and Binding / Жизненный цикл и привязка Service"
aliases: [Service Lifecycle and Binding, Жизненный цикл и привязка Service]
topic: android
subtopics: [service]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-add-custom-attributes-to-custom-view--android--medium, q-migration-to-compose--android--medium, q-viewmodel-pattern--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [android/service, difficulty/hard]
date created: Saturday, November 1st 2025, 12:47:04 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Service Lifecycle and Binding - Advanced Patterns

# Question (EN)
>
Explain the Service lifecycle, binding mechanisms, and communication patterns. How do you implement bound services with AIDL? What are the differences between startService() and bindService()? How do you handle service lifecycle in modern Android (12+)?

## Answer (EN)
Services are fundamental Android components for background operations, with complex lifecycle management and multiple binding patterns for inter-process communication.

#### Service Lifecycle Fundamentals

**1. Started Service Lifecycle**
```kotlin
class DataSyncService : Service() {

    private var isRunning = false
    private val syncJob = Job()
    private val scope = CoroutineScope(Dispatchers.IO + syncJob)

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "onCreate() - Service created")
        // Initialize resources
        // Called only once when service is first created
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "onStartCommand() - startId: $startId")

        when (intent?.action) {
            ACTION_START_SYNC -> startSync(startId)
            ACTION_STOP_SYNC -> stopSync()
            ACTION_PAUSE_SYNC -> pauseSync()
        }

        // Return values:
        // START_STICKY - Restart service if killed, with null intent
        // START_NOT_STICKY - Don't restart if killed
        // START_REDELIVER_INTENT - Restart with last intent redelivered
        return START_STICKY
    }

    private fun startSync(startId: Int) {
        if (isRunning) return

        isRunning = true
        scope.launch {
            try {
                performSync()
            } finally {
                // Stop service when work is complete
                stopSelf(startId) // Stops only this specific start request
                // or stopSelf() to stop all pending requests
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy() - Service destroyed")

        isRunning = false
        syncJob.cancel()

        // Clean up resources
        // Called when service is no longer needed
    }

    override fun onBind(intent: Intent?): IBinder? {
        // Return null for started-only services
        return null
    }

    companion object {
        private const val TAG = "DataSyncService"
        private const val ACTION_START_SYNC = "START_SYNC"
        private const val ACTION_STOP_SYNC = "STOP_SYNC"
        private const val ACTION_PAUSE_SYNC = "PAUSE_SYNC"
    }
}
```

**2. Bound Service Lifecycle**
```kotlin
class MusicPlayerService : Service() {

    private val binder = MusicBinder()
    private var mediaPlayer: MediaPlayer? = null
    private val callbacks = mutableListOf<PlayerCallback>()
    private var bindCount = 0

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "onCreate()")
        mediaPlayer = MediaPlayer()
    }

    override fun onBind(intent: Intent?): IBinder {
        bindCount++
        Log.d(TAG, "onBind() - bind count: $bindCount")
        return binder
    }

    override fun onUnbind(intent: Intent?): Boolean {
        bindCount--
        Log.d(TAG, "onUnbind() - bind count: $bindCount")

        // Return true to receive onRebind() when new clients bind
        // Return false (default) to receive onBind() instead
        return true
    }

    override fun onRebind(intent: Intent?) {
        bindCount++
        Log.d(TAG, "onRebind() - bind count: $bindCount")
        super.onRebind(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy()")
        mediaPlayer?.release()
        mediaPlayer = null
    }

    inner class MusicBinder : Binder() {
        fun getService(): MusicPlayerService = this@MusicPlayerService
    }

    // Public API for bound clients
    fun play(uri: Uri) {
        mediaPlayer?.apply {
            reset()
            setDataSource(applicationContext, uri)
            prepare()
            start()
            notifyPlaybackStateChanged(PlaybackState.PLAYING)
        }
    }

    fun pause() {
        mediaPlayer?.pause()
        notifyPlaybackStateChanged(PlaybackState.PAUSED)
    }

    fun registerCallback(callback: PlayerCallback) {
        callbacks.add(callback)
    }

    fun unregisterCallback(callback: PlayerCallback) {
        callbacks.remove(callback)
    }

    private fun notifyPlaybackStateChanged(state: PlaybackState) {
        callbacks.forEach { it.onPlaybackStateChanged(state) }
    }

    interface PlayerCallback {
        fun onPlaybackStateChanged(state: PlaybackState)
    }

    enum class PlaybackState {
        PLAYING, PAUSED, STOPPED
    }

    companion object {
        private const val TAG = "MusicPlayerService"
    }
}
```

#### Binding to Services

**1. Simple Service Binding**
```kotlin
class MusicPlayerActivity : ComponentActivity() {

    private var musicService: MusicPlayerService? = null
    private var isBound = false

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            Log.d(TAG, "onServiceConnected()")
            val musicBinder = binder as MusicPlayerService.MusicBinder
            musicService = musicBinder.getService()
            isBound = true

            // Register callback
            musicService?.registerCallback(playerCallback)

            // Service is now ready to use
            updateUI()
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            Log.d(TAG, "onServiceDisconnected() - unexpected disconnect")
            musicService = null
            isBound = false
            updateUI()
        }

        override fun onBindingDied(name: ComponentName?) {
            Log.e(TAG, "onBindingDied() - binding died")
            // Connection lost, rebind if needed
            unbindService()
            bindService()
        }

        override fun onNullBinding(name: ComponentName?) {
            Log.e(TAG, "onNullBinding() - service returned null binder")
        }
    }

    private val playerCallback = object : MusicPlayerService.PlayerCallback {
        override fun onPlaybackStateChanged(state: MusicPlayerService.PlaybackState) {
            runOnUiThread {
                updatePlaybackUI(state)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MusicPlayerScreen(
                onPlayClick = { uri -> musicService?.play(uri) },
                onPauseClick = { musicService?.pause() }
            )
        }
    }

    override fun onStart() {
        super.onStart()
        bindService()
    }

    override fun onStop() {
        super.onStop()
        unbindService()
    }

    private fun bindService() {
        if (!isBound) {
            val intent = Intent(this, MusicPlayerService::class.java)
            bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
        }
    }

    private fun unbindService() {
        if (isBound) {
            musicService?.unregisterCallback(playerCallback)
            unbindService(serviceConnection)
            isBound = false
            musicService = null
        }
    }

    companion object {
        private const val TAG = "MusicPlayerActivity"
    }
}
```

**2. Bind Flags**
```kotlin
// BIND_AUTO_CREATE - Automatically create service if not exists
bindService(intent, connection, Context.BIND_AUTO_CREATE)

// BIND_DEBUG_UNBIND - Track unbind call sites for debugging
bindService(intent, connection, Context.BIND_DEBUG_UNBIND)

// BIND_NOT_FOREGROUND - Service won't be promoted to foreground priority
bindService(intent, connection, Context.BIND_NOT_FOREGROUND)

// BIND_ABOVE_CLIENT - Service importance will be at least as high as client
bindService(intent, connection, Context.BIND_ABOVE_CLIENT)

// BIND_WAIVE_PRIORITY - Don't impact service's priority
bindService(intent, connection, Context.BIND_WAIVE_PRIORITY)

// BIND_IMPORTANT - Service is important to the client
bindService(intent, connection, Context.BIND_IMPORTANT)

// BIND_ADJUST_WITH_ACTIVITY - Adjust service based on client activity state
bindService(intent, connection, Context.BIND_ADJUST_WITH_ACTIVITY)
```

#### AIDL-Based Communication

**1. Define AIDL Interface**
```aidl
// IMusicPlayerService.aidl
package com.example.musicapp

import com.example.musicapp.IPlayerCallback

interface IMusicPlayerService {
    void play(String uri)
    void pause()
    void stop()
    void seekTo(int position)

    int getCurrentPosition()
    int getDuration()
    boolean isPlaying()

    void registerCallback(IPlayerCallback callback)
    void unregisterCallback(IPlayerCallback callback)
}

// IPlayerCallback.aidl
package com.example.musicapp

interface IPlayerCallback {
    void onPlaybackStateChanged(int state)
    void onProgressChanged(int position)
    void onError(String errorMessage)
}
```

**2. Implement AIDL Service**
```kotlin
class MusicPlayerAidlService : Service() {

    private var mediaPlayer: MediaPlayer? = null
    private val callbacks = RemoteCallbackList<IPlayerCallback>()
    private var currentUri: Uri? = null

    private val updateHandler = Handler(Looper.getMainLooper())
    private val updateRunnable = object : Runnable {
        override fun run() {
            mediaPlayer?.let { player ->
                if (player.isPlaying) {
                    broadcastProgress(player.currentPosition)
                    updateHandler.postDelayed(this, 1000)
                }
            }
        }
    }

    private val binder = object : IMusicPlayerService.Stub() {
        override fun play(uri: String?) {
            uri ?: return

            try {
                mediaPlayer?.apply {
                    reset()
                    setDataSource(this@MusicPlayerAidlService, Uri.parse(uri))
                    prepareAsync()
                    setOnPreparedListener {
                        start()
                        currentUri = Uri.parse(uri)
                        broadcastStateChange(STATE_PLAYING)
                        startProgressUpdates()
                    }
                    setOnErrorListener { _, what, extra ->
                        broadcastError("Playback error: $what, $extra")
                        true
                    }
                }
            } catch (e: Exception) {
                broadcastError("Failed to play: ${e.message}")
            }
        }

        override fun pause() {
            mediaPlayer?.pause()
            stopProgressUpdates()
            broadcastStateChange(STATE_PAUSED)
        }

        override fun stop() {
            mediaPlayer?.stop()
            stopProgressUpdates()
            broadcastStateChange(STATE_STOPPED)
        }

        override fun seekTo(position: Int) {
            mediaPlayer?.seekTo(position)
            broadcastProgress(position)
        }

        override fun getCurrentPosition(): Int {
            return mediaPlayer?.currentPosition ?: 0
        }

        override fun getDuration(): Int {
            return mediaPlayer?.duration ?: 0
        }

        override fun isPlaying(): Boolean {
            return mediaPlayer?.isPlaying ?: false
        }

        override fun registerCallback(callback: IPlayerCallback?) {
            callback?.let { callbacks.register(it) }
        }

        override fun unregisterCallback(callback: IPlayerCallback?) {
            callback?.let { callbacks.unregister(it) }
        }
    }

    override fun onCreate() {
        super.onCreate()
        mediaPlayer = MediaPlayer()
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }

    override fun onDestroy() {
        super.onDestroy()
        stopProgressUpdates()
        mediaPlayer?.release()
        mediaPlayer = null
        callbacks.kill()
    }

    private fun broadcastStateChange(state: Int) {
        val count = callbacks.beginBroadcast()
        for (i in 0 until count) {
            try {
                callbacks.getBroadcastItem(i).onPlaybackStateChanged(state)
            } catch (e: RemoteException) {
                // Client process died, will be removed automatically
            }
        }
        callbacks.finishBroadcast()
    }

    private fun broadcastProgress(position: Int) {
        val count = callbacks.beginBroadcast()
        for (i in 0 until count) {
            try {
                callbacks.getBroadcastItem(i).onProgressChanged(position)
            } catch (e: RemoteException) {
                // Ignore
            }
        }
        callbacks.finishBroadcast()
    }

    private fun broadcastError(message: String) {
        val count = callbacks.beginBroadcast()
        for (i in 0 until count) {
            try {
                callbacks.getBroadcastItem(i).onError(message)
            } catch (e: RemoteException) {
                // Ignore
            }
        }
        callbacks.finishBroadcast()
    }

    private fun startProgressUpdates() {
        updateHandler.post(updateRunnable)
    }

    private fun stopProgressUpdates() {
        updateHandler.removeCallbacks(updateRunnable)
    }

    companion object {
        const val STATE_PLAYING = 1
        const val STATE_PAUSED = 2
        const val STATE_STOPPED = 3
    }
}
```

**3. Client Implementation**
```kotlin
class MusicPlayerClient : ComponentActivity() {

    private var musicService: IMusicPlayerService? = null
    private var isBound = false

    private val playerCallback = object : IPlayerCallback.Stub() {
        override fun onPlaybackStateChanged(state: Int) {
            runOnUiThread {
                updateStateUI(state)
            }
        }

        override fun onProgressChanged(position: Int) {
            runOnUiThread {
                updateProgressUI(position)
            }
        }

        override fun onError(errorMessage: String?) {
            runOnUiThread {
                showError(errorMessage ?: "Unknown error")
            }
        }
    }

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            musicService = IMusicPlayerService.Stub.asInterface(binder)
            isBound = true

            try {
                musicService?.registerCallback(playerCallback)
            } catch (e: RemoteException) {
                Log.e(TAG, "Failed to register callback", e)
            }
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            musicService = null
            isBound = false
        }
    }

    override fun onStart() {
        super.onStart()
        val intent = Intent(this, MusicPlayerAidlService::class.java)
        bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
    }

    override fun onStop() {
        super.onStop()
        if (isBound) {
            try {
                musicService?.unregisterCallback(playerCallback)
            } catch (e: RemoteException) {
                Log.e(TAG, "Failed to unregister callback", e)
            }
            unbindService(serviceConnection)
            isBound = false
        }
    }

    private fun playMusic(uri: String) {
        try {
            musicService?.play(uri)
        } catch (e: RemoteException) {
            Log.e(TAG, "Failed to play music", e)
        }
    }

    companion object {
        private const val TAG = "MusicPlayerClient"
    }
}
```

#### Messenger-Based Communication

**Lighter alternative to AIDL for simple IPC**
```kotlin
class MessengerService : Service() {

    private val messenger = Messenger(IncomingHandler(this))

    class IncomingHandler(
        private val service: MessengerService
    ) : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_REGISTER_CLIENT -> {
                    service.registerClient(msg.replyTo)
                }
                MSG_UNREGISTER_CLIENT -> {
                    service.unregisterClient(msg.replyTo)
                }
                MSG_START_TASK -> {
                    val taskId = msg.arg1
                    service.startTask(taskId, msg.replyTo)
                }
                else -> super.handleMessage(msg)
            }
        }
    }

    private val clients = mutableListOf<Messenger>()

    override fun onBind(intent: Intent?): IBinder {
        return messenger.binder
    }

    private fun registerClient(client: Messenger) {
        clients.add(client)
    }

    private fun unregisterClient(client: Messenger) {
        clients.remove(client)
    }

    private fun startTask(taskId: Int, replyTo: Messenger) {
        // Perform task
        Thread {
            // Simulate work
            Thread.sleep(2000)

            // Send result back
            try {
                val resultMsg = Message.obtain(null, MSG_TASK_COMPLETE).apply {
                    arg1 = taskId
                    obj = "Task completed successfully"
                }
                replyTo.send(resultMsg)
            } catch (e: RemoteException) {
                // Client is dead
            }
        }.start()
    }

    private fun broadcastToAllClients(what: Int, data: Any? = null) {
        clients.forEach { client ->
            try {
                val msg = Message.obtain(null, what).apply {
                    obj = data
                }
                client.send(msg)
            } catch (e: RemoteException) {
                // Client died
            }
        }
    }

    companion object {
        const val MSG_REGISTER_CLIENT = 1
        const val MSG_UNREGISTER_CLIENT = 2
        const val MSG_START_TASK = 3
        const val MSG_TASK_COMPLETE = 4
    }
}

// Client side
class MessengerClient : ComponentActivity() {

    private var service: Messenger? = null
    private var isBound = false

    private val responseHandler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MessengerService.MSG_TASK_COMPLETE -> {
                    val taskId = msg.arg1
                    val result = msg.obj as? String
                    handleTaskComplete(taskId, result)
                }
            }
        }
    }

    private val messenger = Messenger(responseHandler)

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            service = Messenger(binder)
            isBound = true

            // Register with service
            try {
                val msg = Message.obtain(null, MessengerService.MSG_REGISTER_CLIENT)
                msg.replyTo = messenger
                service?.send(msg)
            } catch (e: RemoteException) {
                // Service crashed
            }
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            service = null
            isBound = false
        }
    }

    private fun startTask(taskId: Int) {
        try {
            val msg = Message.obtain(null, MessengerService.MSG_START_TASK).apply {
                arg1 = taskId
                replyTo = messenger
            }
            service?.send(msg)
        } catch (e: RemoteException) {
            // Service crashed
        }
    }
}
```

#### Foreground Service Lifecycle (Android 12+)

```kotlin
class DownloadForegroundService : Service() {

    private val notificationManager by lazy {
        getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_DOWNLOAD -> {
                // Android 12+ requires startForeground within 5 seconds
                startForeground(NOTIFICATION_ID, createNotification())
                startDownload(intent.getStringExtra(EXTRA_URL))
            }
            ACTION_STOP_DOWNLOAD -> {
                stopDownload()
                stopSelf()
            }
        }

        return START_NOT_STICKY
    }

    private fun startDownload(url: String?) {
        url ?: return

        CoroutineScope(Dispatchers.IO).launch {
            try {
                downloadFile(url) { progress ->
                    updateNotification(progress)
                }

                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            } catch (e: Exception) {
                showErrorNotification(e.message)
                stopSelf()
            }
        }
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Downloads",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "File download progress"
            setShowBadge(false)
        }
        notificationManager.createNotificationChannel(channel)
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Downloading")
            .setContentText("Download in progress")
            .setSmallIcon(R.drawable.ic_download)
            .setProgress(100, 0, false)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(progress: Int) {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Downloading")
            .setContentText("$progress%")
            .setSmallIcon(R.drawable.ic_download)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()

        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val CHANNEL_ID = "download_channel"
        private const val NOTIFICATION_ID = 1
        private const val ACTION_START_DOWNLOAD = "START_DOWNLOAD"
        private const val ACTION_STOP_DOWNLOAD = "STOP_DOWNLOAD"
        private const val EXTRA_URL = "url"
    }
}
```

#### Best Practices

1. **Lifecycle Management**:
   - Always match bind/unbind calls
   - Handle service death gracefully
   - Use proper return values in onStartCommand
   - Clean up resources in onDestroy

2. **Foreground Services (Android 12+)**:
   - Call startForeground within 5 seconds
   - Declare foreground service type in manifest
   - Request appropriate permissions
   - Use ForegroundServiceStartNotAllowedException handling

3. **AIDL Communication**:
   - Use RemoteCallbackList for callbacks
   - Handle RemoteException
   - Consider process death
   - Keep interface simple

4. **Performance**:
   - Don't block binder threads
   - Use async operations
   - Limit callback frequency
   - Consider memory leaks

5. **Testing**:
   - Test service lifecycle transitions
   - Test binding/unbinding
   - Test process death scenarios
   - Use ServiceTestRule

#### Common Pitfalls

1. **Memory Leaks**: Forgetting to unbind or unregister callbacks
2. **ANR**: Blocking operations on binder thread
3. **Lifecycle Mismatches**: Binding in onCreate but unbinding in onStop
4. **No Foreground Notification**: Service killed immediately on Android 12+
5. **Missing Null Checks**: Service can be null after unbind

### Summary

Service lifecycle and binding require careful management:
- **Started Services**: Use for long-running background tasks
- **Bound Services**: Use for client-service interaction
- **AIDL**: For complex cross-process communication
- **Messenger**: For simple message-based IPC
- **Foreground Services**: Mandatory for user-visible work on Android 12+

Key considerations: proper lifecycle management, foreground service compliance, robust error handling, and efficient IPC design.

---

# Вопрос (RU)
>
Объясните жизненный цикл Service, механизмы binding и паттерны коммуникации. Как реализовать bound services с AIDL? В чем разница между startService() и bindService()? Как управлять жизненным циклом сервисов в современном Android (12+)?

## Ответ (RU)
Services — фундаментальные Android-компоненты для фоновых операций со сложным управлением жизненным циклом и множественными паттернами binding для межпроцессной коммуникации.

#### Основы Жизненного Цикла

**Started Service**:
- `onCreate()` → `onStartCommand()` → ... → `onDestroy()`
- Запускается через `startService()`
- Работает независимо от клиента
- Должен сам себя остановить через `stopSelf()`

**Bound Service**:
- `onCreate()` → `onBind()` → `onUnbind()` → `onDestroy()`
- Запускается через `bindService()`
- Живет пока есть привязанные клиенты
- Предоставляет API через IBinder

**Hybrid Service**:
- Может быть запущен И привязан одновременно
- Останавливается только когда вызван `stopSelf()` И нет клиентов

#### AIDL-коммуникация

**Когда использовать**:
- Межпроцессное взаимодействие (IPC)
- Сложные типы данных
- Двусторонняя коммуникация
- Множественные клиенты

**Альтернатива - Messenger**:
- Проще чем AIDL
- Message-based коммуникация
- Один Handler для всех запросов
- Подходит для простых случаев

#### Android 12+ Ограничения

**Foreground Service**:
- Обязательно вызвать `startForeground()` в течение 5 секунд
- Объявить `foregroundServiceType` в манифесте
- Запросить соответствующие разрешения
- Обработать `ForegroundServiceStartNotAllowedException`

**Background Restrictions**:
- Нельзя запустить foreground service из background
- Исключения: WorkManager, Firebase FCM, Exact Alarms

#### Лучшие Практики

1. **Управление жизненным циклом**:
   - Всегда сопоставляйте bind/unbind вызовы
   - Обрабатывайте смерть сервиса gracefully
   - Используйте правильные return values в onStartCommand
   - Очищайте ресурсы в onDestroy

2. **IPC**:
   - Используйте RemoteCallbackList для коллбеков
   - Обрабатывайте RemoteException
   - Учитывайте смерть процесса
   - Держите интерфейс простым

3. **Производительность**:
   - Не блокируйте binder-потоки
   - Используйте async операции
   - Ограничивайте частоту callback'ов

4. **Тестирование**:
   - Тестируйте переходы жизненного цикла
   - Тестируйте binding/unbinding
   - Тестируйте сценарии смерти процесса
   - Используйте ServiceTestRule

### Резюме

Жизненный цикл и binding сервисов требуют тщательного управления:
- **Started Services**: для долгоживущих фоновых задач
- **Bound Services**: для клиент-сервис взаимодействия
- **AIDL**: для сложной межпроцессной коммуникации
- **Messenger**: для простой message-based IPC
- **Foreground Services**: обязательны для видимой пользователю работы на Android 12+

Ключевые моменты: правильное управление жизненным циклом, соответствие требованиям foreground service, надежная обработка ошибок, эффективный дизайн IPC.

---


## Follow-ups

- Follow-up questions to be populated

## References

- References to be populated
## Related Questions

### Prerequisites (Easier)
- [[q-service-component--android--medium]] - Service
- [[q-testing-viewmodels-turbine--android--medium]] - Lifecycle
- [[q-what-is-viewmodel--android--medium]] - Lifecycle
