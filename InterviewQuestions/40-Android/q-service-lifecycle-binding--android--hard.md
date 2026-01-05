---
id: android-325
title: Service Lifecycle and Binding / Жизненный цикл и привязка Service
aliases: [Service Lifecycle and Binding, Жизненный цикл и привязка Service]
topic: android
subtopics: [service]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-foreground-service-types--android--medium, q-how-to-add-custom-attributes-to-custom-view--android--medium, q-migration-to-compose--android--medium, q-viewmodel-pattern--android--easy, q-what-is-data-binding--android--easy, q-when-can-the-system-restart-a-service--android--medium]
created: 2025-10-10
updated: 2025-11-11
tags: [android/service, difficulty/hard]

---
# Вопрос (RU)
>
Объясните жизненный цикл `Service`, механизмы binding и паттерны коммуникации. Как реализовать bound services с AIDL? В чем разница между `startService()` и `bindService()`? Как управлять жизненным циклом сервисов в современном Android (12+)?

# Question (EN)
>
Explain the `Service` lifecycle, binding mechanisms, and communication patterns. How do you implement bound services with AIDL? What are the differences between `startService()` and `bindService()`? How do you handle service lifecycle in modern Android (12+)?

## Ответ (RU)
`Service` — фундаментальный Android-компонент для фоновых операций со сложным управлением жизненным циклом и несколькими паттернами binding для IPC.

Ключевое различие (по сути вопроса):
- `startService()` / `Context.startService()`: запускает started service. Он работает независимо от клиента и должен сам себя остановить через `stopSelf()` / `stopService()`. В современных версиях Android сильно ограничен для фоновых задач — предпочтительнее foreground service, WorkManager, JobScheduler.
- `bindService()`: устанавливает привязку к bound service. Жизненный цикл сервиса привязан к клиентам: создается при первой привязке (с `BIND_AUTO_CREATE`), уничтожается, когда все клиенты отвязались (если сервис не был также запущен).

Гибридный сервис может быть и started, и bound: он уничтожается только когда вызван `stopSelf()` / `stopService()` И нет привязанных клиентов.

#### Основы Жизненного Цикла

**1. Started `Service` (пример реализации)**
```kotlin
class DataSyncService : Service() {

    private var isRunning = false
    private val syncJob = Job()
    private val scope = CoroutineScope(Dispatchers.IO + syncJob)

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "onCreate() - Service created")
        // Инициализация ресурсов; вызывается один раз при первом создании сервиса
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "onStartCommand() - startId: $startId")

        when (intent?.action) {
            ACTION_START_SYNC -> startSync(startId)
            ACTION_STOP_SYNC -> stopSelf(startId)
            ACTION_PAUSE_SYNC -> pauseSync()
        }

        // Семантика возвращаемых значений:
        // START_STICKY - перезапустить сервис при убийстве, Intent будет null (для долгоживущих задач)
        // START_NOT_STICKY - не перезапускать (для некритичных задач или одноразовой работы)
        // START_REDELIVER_INTENT - перезапустить и повторно доставить последний Intent
        // Для задач синхронизации часто логичен START_NOT_STICKY или START_REDELIVER_INTENT.
        return START_STICKY
    }

    private fun startSync(startId: Int) {
        if (isRunning) return

        isRunning = true
        scope.launch {
            try {
                performSync() // псевдокод: длительная операция синхронизации
            } finally {
                // Останавливаем только конкретный запуск после завершения работы
                stopSelf(startId)
                isRunning = false
            }
        }
    }

    private fun pauseSync() {
        // псевдокод: логика паузы при необходимости
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy() - Service destroyed")

        isRunning = false
        syncJob.cancel()
        // Освобождение ресурсов; вызывается, когда сервис окончательно не нужен
    }

    override fun onBind(intent: Intent?): IBinder? {
        // Для чисто started-сервисов возвращаем null
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

**2. Bound `Service` (локальный биндер, один процесс)**
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

        // true -> при новом клиенте будет вызван onRebind()
        // false (по умолчанию) -> будет снова вызван onBind()
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

    // Публичное API для клиентов
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

#### Привязка К Сервису (binding)

**1. Простой пример binding из `Activity`/`ComponentActivity`**
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

            // Регистрируем callback
            musicService?.registerCallback(playerCallback)

            // Сервис готов к использованию
            updateUI()
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            Log.d(TAG, "onServiceDisconnected() - неожиданный разрыв")
            musicService = null
            isBound = false
            updateUI()
        }

        override fun onBindingDied(name: ComponentName?) {
            Log.e(TAG, "onBindingDied() - binding умер")
            // Потеря соединения, пробуем перепривязаться
            if (isBound) {
                unbindFromService()
            }
            bindToService()
        }

        override fun onNullBinding(name: ComponentName?) {
            Log.e(TAG, "onNullBinding() - сервис вернул null binder")
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
        bindToService()
    }

    override fun onStop() {
        super.onStop()
        unbindFromService()
    }

    private fun bindToService() {
        if (!isBound) {
            val intent = Intent(this, MusicPlayerService::class.java)
            bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
        }
    }

    private fun unbindFromService() {
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

**2. Флаги bindService (Bind Flags)**
```kotlin
// BIND_AUTO_CREATE - автоматически создать сервис, если он ещё не запущен
bindService(intent, connection, Context.BIND_AUTO_CREATE)

// BIND_DEBUG_UNBIND - помогает отлаживать корректность вызовов unbindService
bindService(intent, connection, Context.BIND_DEBUG_UNBIND)

// BIND_NOT_FOREGROUND - это связывание само по себе не поднимает приоритет сервиса до foreground
bindService(intent, connection, Context.BIND_NOT_FOREGROUND)

// BIND_ABOVE_CLIENT - важность сервиса будет не ниже важности клиента
bindService(intent, connection, Context.BIND_ABOVE_CLIENT)

// BIND_WAIVE_PRIORITY - это связывание не повышает приоритет сервиса
bindService(intent, connection, Context.BIND_WAIVE_PRIORITY)

// BIND_IMPORTANT - помечает связывание как важное для клиента
bindService(intent, connection, Context.BIND_IMPORTANT)

// BIND_ADJUST_WITH_ACTIVITY - важность сервиса будет следовать за состоянием Activity клиента
bindService(intent, connection, Context.BIND_ADJUST_WITH_ACTIVITY)
```

#### AIDL-основанный Bound Service (IPC)

**1. Определение AIDL-интерфейсов**
```aidl
// IMusicPlayerService.aidl
package com.example.musicapp;

import com.example.musicapp.IPlayerCallback;

interface IMusicPlayerService {
    void play(String uri);
    void pause();
    void stop();
    void seekTo(int position);

    int getCurrentPosition();
    int getDuration();
    boolean isPlaying();

    void registerCallback(IPlayerCallback callback);
    void unregisterCallback(IPlayerCallback callback);
}

// IPlayerCallback.aidl
package com.example.musicapp;

interface IPlayerCallback {
    void onPlaybackStateChanged(int state);
    void onProgressChanged(int position);
    void onError(String errorMessage);
}
```

**2. Реализация AIDL `Service`**
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
                val parsed = Uri.parse(uri)
                val player = mediaPlayer ?: MediaPlayer().also { mediaPlayer = it }

                player.reset()
                player.setDataSource(this@MusicPlayerAidlService, parsed)
                player.setOnPreparedListener {
                    it.start()
                    currentUri = parsed
                    broadcastStateChange(STATE_PLAYING)
                    startProgressUpdates()
                }
                player.setOnErrorListener { _, what, extra ->
                    broadcastError("Playback error: $what, $extra")
                    true
                }
                player.prepareAsync()
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
        // IPC-bound-only сервис (bound-only IPC service), возвращаем AIDL Stub
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
                // Клиентский процесс умер; игнорируем
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
                // Игнорируем
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
                // Игнорируем
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

**3. Клиент для AIDL-сервиса**
```kotlin
class MusicPlayerClient : ComponentActivity() {

    private var musicService: IMusicPlayerService? = null
    private var isBound = false

    private val playerCallback = object : IPlayerCallback.Stub() {
        override fun onPlaybackStateChanged(state: Int) {
            runOnUiThread { updateStateUI(state) }
        }

        override fun onProgressChanged(position: Int) {
            runOnUiThread { updateProgressUI(position) }
        }

        override fun onError(errorMessage: String?) {
            runOnUiThread { showError(errorMessage ?: "Unknown error") }
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

#### Messenger-основанная Коммуникация

Упрощенная альтернатива AIDL для простого IPC на основе сообщений.

```kotlin
class MessengerService : Service() {

    private val messenger = Messenger(IncomingHandler(this))

    class IncomingHandler(
        private val service: MessengerService
    ) : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_REGISTER_CLIENT -> service.registerClient(msg.replyTo)
                MSG_UNREGISTER_CLIENT -> service.unregisterClient(msg.replyTo)
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
        // Демонстрационный фоновой поток; на практике используйте корутины/исполнители
        Thread {
            Thread.sleep(2000)
            try {
                val resultMsg = Message.obtain(null, MSG_TASK_COMPLETE).apply {
                    arg1 = taskId
                    obj = "Task completed successfully"
                }
                replyTo.send(resultMsg)
            } catch (e: RemoteException) {
                // Клиент умер
            }
        }.start()
    }

    private fun broadcastToAllClients(what: Int, data: Any? = null) {
        clients.forEach { client ->
            try {
                val msg = Message.obtain(null, what).apply { obj = data }
                client.send(msg)
            } catch (e: RemoteException) {
                // Клиент умер
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

// Клиент
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

            // Регистрируемся в сервисе
            try {
                val msg = Message.obtain(null, MessengerService.MSG_REGISTER_CLIENT)
                msg.replyTo = messenger
                service?.send(msg)
            } catch (e: RemoteException) {
                // Сервис упал
            }
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            service = null
            isBound = false
        }
    }

    private fun startTask(taskId: Int) {
        if (!isBound) return
        try {
            val msg = Message.obtain(null, MessengerService.MSG_START_TASK).apply {
                arg1 = taskId
                replyTo = messenger
            }
            service?.send(msg)
        } catch (e: RemoteException) {
            // Сервис упал
        }
    }
}
```

#### Foreground `Service` (Android 12+) — Пример Жизненного Цикла

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
                // Android 12+: startForeground() нужно вызвать в течение 5 секунд
                // после startForegroundService(), объявить foregroundServiceType и
                // учитывать ограничения на запуск foreground service из background.
                startForeground(NOTIFICATION_ID, createNotification())
                startDownload(intent.getStringExtra(EXTRA_URL))
            }
            ACTION_STOP_DOWNLOAD -> {
                stopDownload() // псевдокод: отмена работы
                stopSelf()
            }
        }

        return START_NOT_STICKY
    }

    private fun startDownload(url: String?) {
        url ?: return

        CoroutineScope(Dispatchers.IO).launch {
            try {
                downloadFile(url) { progress -> // псевдокод: загрузка файла
                    updateNotification(progress)
                }

                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            } catch (e: Exception) {
                showErrorNotification(e.message ?: "Download failed") // псевдокод
                stopForeground(STOP_FOREGROUND_REMOVE)
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

#### Лучшие Практики И Типичные Ошибки

1. Управление жизненным циклом:
   - Строго парные `bindService()` / `unbindService()`.
   - Обрабатывать смерть сервиса и binder'а: `onServiceDisconnected()`, `onBindingDied()`.
   - Корректно выбирать значение из `onStartCommand()` под нужное поведение перезапуска.
   - Освобождать ресурсы в `onDestroy()`.
   - Bound-only сервис завершается, когда все клиенты отвязались; started-only должен сам вызвать `stopSelf()` / `stopService()`.

2. Foreground services (Android 12+):
   - Вызывать `startForeground()` в отведенное время после `startForegroundService()`.
   - Объявлять `foregroundServiceType` и запрашивать соответствующие разрешения.
   - Не стартовать foreground service из background без допустимых исключений; обрабатывать `ForegroundServiceStartNotAllowedException` и использовать WorkManager/JobScheduler, когда нужно.

3. IPC (AIDL/Messenger):
   - Использовать `RemoteCallbackList` для удаленных колбеков.
   - Оборачивать IPC-вызовы в обработку `RemoteException`.
   - Проектировать простой протокол, учитывать смерть клиента и сервиса.

4. Производительность:
   - Не блокировать main и binder потоки, выносить тяжелые операции в фоновые потоки/корутины.
   - Не спамить слишком частыми callback'ами.
   - Не утекать `Activity`/`Context` из сервисов.

5. Тестирование и надежность:
   - Тестировать переходы start/stop, bind/unbind и гибридные сценарии.
   - Тестировать поведение при убийстве процесса, переподключение binder'а.
   - Использовать `ServiceTestRule` и интеграционные/UI-тесты.

Типичные ошибки:
- Утечки памяти из-за забытых `unbindService()` или неотписанных callback'ов.
- ANR из-за тяжелых задач в main/binder потоках.
- Неправильное связывание с жизненным циклом `Activity`/`Fragment`.
- Ошибки с foreground notification/манифестом, приводящие к убийству сервиса.
- Использование `Service` для задач, где лучше подходят WorkManager/JobScheduler.

---

## Answer (EN)
Services are fundamental Android components for background operations, with complex lifecycle management and multiple binding patterns for inter-process communication.

Key distinction (core to the question):
- `startService()` / `Context.startService()`: start a started service. It runs independently of the caller; the system keeps it alive until it calls `stopSelf()` / `stopService()` or is killed. On modern Android it is heavily restricted/obsolete for most background work; use foreground services, WorkManager, or job APIs instead.
- `bindService()`: establish a bound service connection. The service lifecycle is tied to bound clients. It is created on first bind (with `BIND_AUTO_CREATE`) and destroyed when no clients remain (unless also started).

Hybrid services may be both started and bound; they are destroyed only when `stopSelf()` / `stopService()` has been called AND no clients remain.

#### `Service` Lifecycle Fundamentals

**1. Started `Service` Lifecycle**
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
            ACTION_STOP_SYNC -> stopSelf(startId)
            ACTION_PAUSE_SYNC -> pauseSync()
        }

        // Return values semantics:
        // START_STICKY - Restart service if killed, with null intent (for ongoing work)
        // START_NOT_STICKY - Don't restart if killed (for non-critical or one-off work)
        // START_REDELIVER_INTENT - Restart and redeliver last Intent(s)
        // For sync-style tasks, START_NOT_STICKY or START_REDELIVER_INTENT is often preferable.
        return START_STICKY
    }

    private fun startSync(startId: Int) {
        if (isRunning) return

        isRunning = true
        scope.launch {
            try {
                performSync() // pseudo-code: your long-running sync logic
            } finally {
                // Stop only this specific start request when work completes
                stopSelf(startId)
                isRunning = false
            }
        }
    }

    private fun pauseSync() {
        // pseudo-code: implement pause logic if needed
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy() - Service destroyed")

        isRunning = false
        syncJob.cancel()
        // Clean up resources; called when service is no longer needed
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

**2. Bound `Service` Lifecycle (local binder, same process)**
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

        // Return true to receive onRebind() when new clients bind.
        // Return false (default) to receive onBind() instead.
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

**1. Simple `Service` Binding (local bound service)**
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
            // Connection lost, attempt to rebind if appropriate
            if (isBound) {
                unbindFromService()
            }
            bindToService()
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
        bindToService()
    }

    override fun onStop() {
        super.onStop()
        unbindFromService()
    }

    private fun bindToService() {
        if (!isBound) {
            val intent = Intent(this, MusicPlayerService::class.java)
            bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
        }
    }

    private fun unbindFromService() {
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

// BIND_NOT_FOREGROUND - Service won't be raised to foreground priority for this binding alone
bindService(intent, connection, Context.BIND_NOT_FOREGROUND)

// BIND_ABOVE_CLIENT - Service importance will be at least as high as client
bindService(intent, connection, Context.BIND_ABOVE_CLIENT)

// BIND_WAIVE_PRIORITY - Don't have this binding raise the service's priority
bindService(intent, connection, Context.BIND_WAIVE_PRIORITY)

// BIND_IMPORTANT - Mark this binding as important to the client
bindService(intent, connection, Context.BIND_IMPORTANT)

// BIND_ADJUST_WITH_ACTIVITY - Adjust service importance with client activity state
bindService(intent, connection, Context.BIND_ADJUST_WITH_ACTIVITY)
```

#### AIDL-Based Communication (bound IPC service)

**1. Define AIDL Interface**
```aidl
// IMusicPlayerService.aidl
package com.example.musicapp;

import com.example.musicapp.IPlayerCallback;

interface IMusicPlayerService {
    void play(String uri);
    void pause();
    void stop();
    void seekTo(int position);

    int getCurrentPosition();
    int getDuration();
    boolean isPlaying();

    void registerCallback(IPlayerCallback callback);
    void unregisterCallback(IPlayerCallback callback);
}

// IPlayerCallback.aidl
package com.example.musicapp;

interface IPlayerCallback {
    void onPlaybackStateChanged(int state);
    void onProgressChanged(int position);
    void onError(String errorMessage);
}
```

**2. Implement AIDL `Service`**
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
                val parsed = Uri.parse(uri)
                val player = mediaPlayer ?: MediaPlayer().also { mediaPlayer = it }

                player.reset()
                player.setDataSource(this@MusicPlayerAidlService, parsed)
                player.setOnPreparedListener {
                    it.start()
                    currentUri = parsed
                    broadcastStateChange(STATE_PLAYING)
                    startProgressUpdates()
                }
                player.setOnErrorListener { _, what, extra ->
                    broadcastError("Playback error: $what, $extra")
                    true
                }
                player.prepareAsync()
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
        // Bound-only IPC service
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
                // Client process died; ignored
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

**3. Client Implementation (AIDL bound service)**
```kotlin
class MusicPlayerClient : ComponentActivity() {

    private var musicService: IMusicPlayerService? = null
    private var isBound = false

    private val playerCallback = object : IPlayerCallback.Stub() {
        override fun onPlaybackStateChanged(state: Int) {
            runOnUiThread { updateStateUI(state) }
        }

        override fun onProgressChanged(position: Int) {
            runOnUiThread { updateProgressUI(position) }
        }

        override fun onError(errorMessage: String?) {
            runOnUiThread { showError(errorMessage ?: "Unknown error") }
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

Lighter alternative to AIDL for simple IPC.

```kotlin
class MessengerService : Service() {

    private val messenger = Messenger(IncomingHandler(this))

    class IncomingHandler(
        private val service: MessengerService
    ) : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_REGISTER_CLIENT -> service.registerClient(msg.replyTo)
                MSG_UNREGISTER_CLIENT -> service.unregisterClient(msg.replyTo)
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
        // Perform task (demo: use background thread; in production prefer coroutines/executors)
        Thread {
            Thread.sleep(2000)
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
                val msg = Message.obtain(null, what).apply { obj = data }
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
        if (!isBound) return
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

#### Foreground `Service` Lifecycle (Android 12+)

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
                // Android 12+ requires startForeground within 5 seconds of startForegroundService(),
                // declare foregroundServiceType, and respect background start restrictions.
                startForeground(NOTIFICATION_ID, createNotification())
                startDownload(intent.getStringExtra(EXTRA_URL))
            }
            ACTION_STOP_DOWNLOAD -> {
                stopDownload() // pseudo-code: cancel work if running
                stopSelf()
            }
        }

        return START_NOT_STICKY
    }

    private fun startDownload(url: String?) {
        url ?: return

        CoroutineScope(Dispatchers.IO).launch {
            try {
                downloadFile(url) { progress -> // pseudo-code: implement download
                    updateNotification(progress)
                }

                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            } catch (e: Exception) {
                showErrorNotification(e.message ?: "Download failed") // pseudo-code
                stopForeground(STOP_FOREGROUND_REMOVE)
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

1. Lifecycle Management:
   - Always match bind/unbind calls.
   - Handle service death and binder death (`onServiceDisconnected` / `onBindingDied`).
   - Use appropriate `onStartCommand` return values based on desired restart behavior.
   - Clean up resources in `onDestroy`.
   - Remember: bound-only services are destroyed when all clients unbind; started-only must call `stopSelf`/`stopService`.

2. Foreground Services (Android 12+):
   - Call `startForeground` within 5 seconds after `startForegroundService`.
   - Declare `foregroundServiceType` in manifest and request appropriate permissions.
   - You generally cannot start foreground services from the background on Android 12+; handle `ForegroundServiceStartNotAllowedException` and use alternatives (e.g., WorkManager) where required.

3. AIDL Communication:
   - Use `RemoteCallbackList` for managing remote callbacks.
   - Handle `RemoteException` on every IPC call.
   - Consider client and service process death; keep protocol robust and simple.

4. Performance:
   - Don't block binder threads or the main thread: offload work to background executors/coroutines.
   - Limit callback frequency to avoid overhead.
   - Avoid leaking `Context`/`Activity` references from services.

5. Testing:
   - Test service lifecycle transitions (start/stop, bind/unbind, hybrid).
   - Test binder reconnection, process death, and configuration changes.
   - Use `ServiceTestRule` and integration/UI tests where applicable.

#### Common Pitfalls

1. Memory Leaks: forgetting to unbind or unregister callbacks.
2. ANR: running heavy work on binder or main threads.
3. Lifecycle Mismatches: binding in `onCreate` but unbinding late or not at all; leaking connections.
4. Foreground Notification Issues: not calling `startForeground` in time or missing required notification/manifest declarations, causing kill on Android 8+ and 12+.
5. Missing Null Checks: accessing service or binder after unbind.

### Summary

`Service` lifecycle and binding require careful management:
- Started Services: for ongoing work not tied to a specific client (but avoid improper background use on modern Android).
- Bound Services: for client-service interaction with lifecycle coupled to clients.
- Hybrid: for services that must continue even if no clients are bound.
- AIDL: for complex cross-process communication.
- Messenger: for simple message-based IPC.
- Foreground Services: required for most user-visible long-running work on Android 12+.

Key considerations: correct started vs bound semantics, modern foreground service restrictions, robust error handling, and efficient IPC design.

---

## Follow-ups

- [[q-how-to-add-custom-attributes-to-custom-view--android--medium]]
- [[q-migration-to-compose--android--medium]]
- [[q-viewmodel-pattern--android--easy]]

## References

- [Services](https://developer.android.com/develop/background-work/services)

## Related Questions

### Prerequisites / Concepts

- [[c-android]]

### Prerequisites (Easier)

- [[q-service-component--android--medium]] - `Service`
- [[q-testing-viewmodels-turbine--android--medium]] - Lifecycle
- [[q-what-is-viewmodel--android--medium]] - Lifecycle
