---
id: 20251016-172637
title: "Foreground Service Types / Типы Foreground Service"
aliases: ["Foreground Service Types", "Типы Foreground Service"]
topic: android
subtopics: [background-processing, services]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-foreground-services, q-android-service-types--android--easy, q-workmanager-vs-alternatives--android--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [android-14, android/background-processing, android/services, background-processing, difficulty/medium, foreground-service, notifications]
sources: [https://developer.android.com/guide/components/foreground-services]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:48:40 pm
---

# Вопрос (RU)
> Что такое типы Foreground Service в Android? Как правильно реализовать foreground services?

# Question (EN)
> What are Foreground Service types in Android? How do you implement foreground services correctly?

---

## Ответ (RU)

**Теория Foreground Services:**
Foreground Services выполняются с видимым уведомлением, позволяя длительным операциям продолжаться даже когда приложение находится в фоне. Начиная с Android 10 (API 29), необходимо объявлять типы сервисов, а Android 14 (API 34) ввел более строгие ограничения.

**Основные концепции:**
- Должны показывать постоянное уведомление
- Могут работать в фоне неограниченное время
- Требуют объявления типа в манифесте (Android 10+)
- Должны вызывать startForeground() в течение 5 секунд
- Android 14 ограничил запуск из фона

**Типы Foreground Service (Android 10+):**
```kotlin
// Доступные типы с Android 10:
ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA
ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE
ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
ServiceInfo.FOREGROUND_SERVICE_TYPE_PHONE_CALL
ServiceInfo.FOREGROUND_SERVICE_TYPE_REMOTE_MESSAGING // Android 11+
ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE // Android 12+
ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE // Android 14+
```

**Объявление в манифесте:**
```xml
<manifest>
    <!-- Обязательные разрешения для конкретных типов -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".MusicService"
            android:foregroundServiceType="mediaPlayback"
            android:exported="false" />
    </application>
</manifest>
```

**Базовая реализация:**
```kotlin
class MusicService : Service() {

    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stop()
        }
        return START_STICKY
    }

    private fun play() {
        // Создаём уведомление
        val notification = createNotification()

        // Запускаем как foreground сервис
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        // Начинаем воспроизведение
        mediaPlayer?.start()
    }

    private fun createNotification(): Notification {
        // Создаём канал уведомлений (Android 8+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Music Playback",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Music player controls"
                setShowBadge(false)
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        // Строим уведомление
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .setContentText(currentSong?.title ?: "Music")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .setOngoing(true)
            .addAction(R.drawable.ic_pause, "Pause", pausePendingIntent)
            .addAction(R.drawable.ic_stop, "Stop", stopPendingIntent)
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    private fun stop() {
        mediaPlayer?.stop()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val NOTIFICATION_ID = 1
        const val CHANNEL_ID = "music_playback"
        const val ACTION_PLAY = "ACTION_PLAY"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_STOP = "ACTION_STOP"
    }
}
```

**Location Tracking Service:**
```kotlin
class LocationTrackingService : Service() {

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private var locationCallback: LocationCallback? = null

    override fun onCreate() {
        super.onCreate()
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        startLocationUpdates()
        return START_STICKY
    }

    private fun startForegroundService() {
        val notification = createNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_location)
            .setContentTitle("Location Tracking")
            .setContentText("Tracking your location...")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    private fun startLocationUpdates() {
        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            10000 // 10 секунд
        ).build()

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                locationResult.locations.forEach { location ->
                    // Обрабатываем местоположение
                    saveLocation(location)
                }
            }
        }

        try {
            fusedLocationClient.requestLocationUpdates(
                locationRequest,
                locationCallback!!,
                Looper.getMainLooper()
            )
        } catch (e: SecurityException) {
            // Обрабатываем отсутствие разрешений
            stopSelf()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        locationCallback?.let {
            fusedLocationClient.removeLocationUpdates(it)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Android 14 ограничения:**
```kotlin
// Новые ограничения Android 14:
// 1. Требование действий пользователя - большинство foreground сервисов можно запускать только когда приложение на переднем плане
// 2. Short Service тип - для быстрых операций (< 3 минут)
// 3. Special Use тип - требует обоснования в Play Console

// Исключения (можно запускать из фона):
- FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK (если активная медиа-сессия)
- FOREGROUND_SERVICE_TYPE_PHONE_CALL (во время активного звонка)
- FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE (Bluetooth/USB подключен)
- Сервисы, запущенные высокоприоритетным FCM сообщением
- Сервисы, запущенные из действия уведомления
- Сервисы, запущенные с точного будильника
```

**Short Service (Android 12+):**
```kotlin
class QuickUploadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        uploadFile()
        return START_NOT_STICKY
    }

    private fun startForegroundService() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            startForeground(
                NOTIFICATION_ID,
                createNotification(),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE or
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, createNotification())
        }
    }

    private fun uploadFile() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Быстрая операция загрузки
                uploadRepository.uploadFile()
            } finally {
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
    }

    // Обработка таймаута
    override fun onTimeout(startId: Int) {
        // Вызывается когда сервис превышает таймаут (Android 12+)
        cleanup()
        stopSelf(startId)
    }
}
```

## Answer (EN)

**Foreground Services Theory:**
Foreground Services run with a visible notification, allowing long-running operations to continue even when the app is in the background. Starting Android 10 (API 29), you must declare service types, and Android 14 (API 34) introduced stricter restrictions.

**Main concepts:**
- Must show persistent notification
- Can run in background indefinitely
- Require service type declaration in manifest (Android 10+)
- Must call startForeground() within 5 seconds
- Android 14 restricted background startup

**Foreground Service Types (Android 10+):**
```kotlin
// Available types since Android 10:
ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA
ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE
ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
ServiceInfo.FOREGROUND_SERVICE_TYPE_PHONE_CALL
ServiceInfo.FOREGROUND_SERVICE_TYPE_REMOTE_MESSAGING // Android 11+
ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE // Android 12+
ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE // Android 14+
```

**Manifest declaration:**
```xml
<manifest>
    <!-- Required permissions for specific types -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".MusicService"
            android:foregroundServiceType="mediaPlayback"
            android:exported="false" />
    </application>
</manifest>
```

**Basic implementation:**
```kotlin
class MusicService : Service() {

    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stop()
        }
        return START_STICKY
    }

    private fun play() {
        // Create notification
        val notification = createNotification()

        // Start as foreground service
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        // Start playback
        mediaPlayer?.start()
    }

    private fun createNotification(): Notification {
        // Create notification channel (Android 8+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Music Playback",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Music player controls"
                setShowBadge(false)
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        // Build notification
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .setContentText(currentSong?.title ?: "Music")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .setOngoing(true)
            .addAction(R.drawable.ic_pause, "Pause", pausePendingIntent)
            .addAction(R.drawable.ic_stop, "Stop", stopPendingIntent)
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    private fun stop() {
        mediaPlayer?.stop()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val NOTIFICATION_ID = 1
        const val CHANNEL_ID = "music_playback"
        const val ACTION_PLAY = "ACTION_PLAY"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_STOP = "ACTION_STOP"
    }
}
```

**Location Tracking Service:**
```kotlin
class LocationTrackingService : Service() {

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private var locationCallback: LocationCallback? = null

    override fun onCreate() {
        super.onCreate()
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        startLocationUpdates()
        return START_STICKY
    }

    private fun startForegroundService() {
        val notification = createNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_location)
            .setContentTitle("Location Tracking")
            .setContentText("Tracking your location...")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    private fun startLocationUpdates() {
        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            10000 // 10 seconds
        ).build()

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                locationResult.locations.forEach { location ->
                    // Process location
                    saveLocation(location)
                }
            }
        }

        try {
            fusedLocationClient.requestLocationUpdates(
                locationRequest,
                locationCallback!!,
                Looper.getMainLooper()
            )
        } catch (e: SecurityException) {
            // Handle missing permissions
            stopSelf()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        locationCallback?.let {
            fusedLocationClient.removeLocationUpdates(it)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Android 14 restrictions:**
```kotlin
// New Android 14 restrictions:
// 1. User-initiated actions required - most foreground services can only be started while app is in foreground
// 2. Short Service type - for quick operations (< 3 minutes)
// 3. Special Use type - requires justification in Play Console

// Exemptions (can start from background):
- FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK (if active media session)
- FOREGROUND_SERVICE_TYPE_PHONE_CALL (during active call)
- FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE (Bluetooth/USB connected)
- Services started by high-priority FCM message
- Services started from notification action
- Services started from exact alarm
```

**Short Service (Android 12+):**
```kotlin
class QuickUploadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        uploadFile()
        return START_NOT_STICKY
    }

    private fun startForegroundService() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            startForeground(
                NOTIFICATION_ID,
                createNotification(),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE or
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, createNotification())
        }
    }

    private fun uploadFile() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Quick upload operation
                uploadRepository.uploadFile()
            } finally {
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
    }

    // Handle timeout
    override fun onTimeout(startId: Int) {
        // Called when service times out (Android 12+)
        cleanup()
        stopSelf(startId)
    }
}
```

---

## Follow-ups

- How do Android 14 restrictions affect app architecture?
- When should you use WorkManager instead of foreground services?
- What are the performance implications of foreground services?

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Service types
- [[q-workmanager-basics--android--easy]] - WorkManager basics

### Related (Same Level)
- [[q-workmanager-vs-alternatives--android--medium]] - Background alternatives
- [[q-background-vs-foreground-service--android--medium]] - Service comparison
- [[q-service-lifecycle--android--medium]] - Service lifecycle

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Service binding
- [[q-workmanager-advanced--android--hard]] - Advanced WorkManager
