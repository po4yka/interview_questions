---
id: 20251016-172637
title: "Foreground Service Types / Типы Foreground Service"
topic: android
difficulty: medium
status: draft
moc: moc-android
created: 2025-10-12
tags: [foreground-service, background-processing, notifications, android-14, difficulty/medium]
related: [q-material3-dynamic-color-theming--material-design--medium, q-mlkit-custom-models--ml--hard, q-compose-gesture-detection--jetpack-compose--medium]
  - q-workmanager-advanced--background--medium
  - q-workmanager-vs-alternatives--background--medium
---
# Question (EN)
What are Foreground Service types in Android? How do you implement foreground services correctly, handle service types (Android 10+), and what are the restrictions in Android 14?

## Answer (EN)
### Overview

**Foreground Services** run with a visible notification, allowing long-running operations to continue even when the app is in the background. Starting Android 10 (API 29), you must declare service types, and Android 14 (API 34) introduced stricter restrictions.

### Foreground Service Types (Android 10+)

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
ServiceInfo.FOREGROUND_SERVICE_TYPE_SYSTEM_EXEMPTED // Android 14+
```

### Declaring Service Types

**AndroidManifest.xml:**

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

**Permission mapping:**

```xml
<!-- Media Playback -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />

<!-- Location -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

<!-- Camera -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA" />
<uses-permission android:name="android.permission.CAMERA" />

<!-- Microphone -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />

<!-- Data Sync -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />

<!-- Health (Android 14+) -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_HEALTH" />

<!-- Remote Messaging -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_REMOTE_MESSAGING" />

<!-- Special Use -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
```

### Basic Foreground Service Implementation

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

    private fun pause() {
        mediaPlayer?.pause()
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

// Start service
fun startMusicPlayback(context: Context) {
    val intent = Intent(context, MusicService::class.java).apply {
        action = MusicService.ACTION_PLAY
    }

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        context.startForegroundService(intent)
    } else {
        context.startService(intent)
    }
}
```

### Location Tracking Service

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

    private fun saveLocation(location: Location) {
        // Save to database or send to server
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

**AndroidManifest.xml:**

```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

<service
    android:name=".LocationTrackingService"
    android:foregroundServiceType="location"
    android:exported="false" />
```

### Data Sync Service

```kotlin
class DataSyncService : Service() {

    private var syncJob: Job? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        startSync()
        return START_NOT_STICKY
    }

    private fun startForegroundService() {
        val notification = createNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_sync)
            .setContentTitle("Syncing Data")
            .setContentText("Synchronizing your data...")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setProgress(0, 0, true) // Indeterminate progress
            .build()
    }

    private fun startSync() {
        syncJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                // Perform sync
                syncRepository.syncData()

                // Update notification
                updateNotification("Sync complete")

                delay(2000) // Show completion message
            } catch (e: Exception) {
                updateNotification("Sync failed: ${e.message}")
            } finally {
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
    }

    private fun updateNotification(text: String) {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_sync)
            .setContentTitle("Data Sync")
            .setContentText(text)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()

        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        syncJob?.cancel()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Android 14 Restrictions

**New in Android 14:**

1. **User-initiated actions required** - Most foreground services can only be started while app is in foreground

2. **Short Service type** - For quick operations (< 3 minutes)

3. **Special Use type** - Requires justification in Play Console

**Exemptions (can start from background):**

```kotlin
// These can still start from background:
- FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK (if active media session)
- FOREGROUND_SERVICE_TYPE_PHONE_CALL (during active call)
- FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE (Bluetooth/USB connected)
- Services started by high-priority FCM message
- Services started from notification action
- Services started from exact alarm
```

**Short Service (Android 12+):**

```xml
<!-- For short operations (< 3 minutes) -->
<service
    android:name=".QuickUploadService"
    android:foregroundServiceType="shortService|dataSync"
    android:exported="false" />
```

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
}
```

**Timeout handling:**

```kotlin
// Short service automatically stopped after timeout
override fun onTimeout(startId: Int) {
    // Called when service times out (Android 12+)
    // Clean up and stop
    cleanup()
    stopSelf(startId)
}
```

### Multiple Service Types

```kotlin
// Combine multiple types
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
    startForeground(
        NOTIFICATION_ID,
        notification,
        ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION or
        ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA
    )
}
```

**Manifest:**

```xml
<service
    android:name=".FitnessTrackingService"
    android:foregroundServiceType="location|camera"
    android:exported="false" />

<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA" />
```

### Service Lifecycle

```kotlin
class ExampleService : Service() {

    override fun onCreate() {
        super.onCreate()
        // Service created (called once)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Service started
        // Return value determines restart behavior:
        // START_STICKY - restart with null intent
        // START_NOT_STICKY - don't restart
        // START_REDELIVER_INTENT - restart with same intent

        startForeground(NOTIFICATION_ID, createNotification())

        return START_STICKY
    }

    override fun onDestroy() {
        // Service destroyed
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? {
        // For bound services
        return null
    }
}
```

### Best Practices

1. **Start foreground ASAP**

```kotlin
//  GOOD - Start foreground immediately
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, createNotification())
    doWork()
    return START_STICKY
}

//  BAD - Delay before startForeground
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    doWork() // If this takes > 5 seconds, ANR!
    startForeground(NOTIFICATION_ID, createNotification())
    return START_STICKY
}
```

2. **Use appropriate service type**

```kotlin
//  GOOD - Correct type for use case
startForeground(
    id,
    notification,
    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK // Music player
)

//  BAD - Wrong type
startForeground(
    id,
    notification,
    ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION // Music player using location type
)
```

3. **Stop when done**

```kotlin
//  GOOD - Stop when work complete
private fun finishWork() {
    stopForeground(STOP_FOREGROUND_REMOVE)
    stopSelf()
}

//  BAD - Never stop
// Service runs forever
```

4. **Handle cancellation**

```kotlin
//  GOOD - Handle task cancellation
override fun onDestroy() {
    super.onDestroy()
    job?.cancel() // Cancel ongoing work
    cleanup()
}

//  BAD - No cleanup
override fun onDestroy() {
    super.onDestroy()
    // Work continues after service destroyed!
}
```

5. **Request permissions at runtime**

```kotlin
//  GOOD - Check permissions before starting
private fun startLocationService() {
    if (hasLocationPermission()) {
        startForegroundService(Intent(this, LocationService::class.java))
    } else {
        requestLocationPermission()
    }
}

//  BAD - Start without checking
private fun startLocationService() {
    startForegroundService(Intent(this, LocationService::class.java))
    // Crashes if permission not granted!
}
```

### Testing Foreground Services

```kotlin
@RunWith(AndroidJUnit4::class)
class MusicServiceTest {

    @get:Rule
    val serviceRule = ServiceTestRule()

    @Test
    fun testServiceStartsForeground() {
        val serviceIntent = Intent(
            ApplicationProvider.getApplicationContext(),
            MusicService::class.java
        ).apply {
            action = MusicService.ACTION_PLAY
        }

        serviceRule.startService(serviceIntent)

        // Verify service is running
        val binder = serviceRule.bindService(serviceIntent)
        assertNotNull(binder)
    }

    @Test
    fun testNotificationShown() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val serviceIntent = Intent(context, MusicService::class.java).apply {
            action = MusicService.ACTION_PLAY
        }

        context.startForegroundService(serviceIntent)

        // Verify notification
        val notificationManager = context.getSystemService(NotificationManager::class.java)
        val notifications = notificationManager.activeNotifications

        assertTrue(notifications.any { it.id == MusicService.NOTIFICATION_ID })
    }
}
```

### Common Issues and Solutions

**Issue 1: ANR after 5 seconds**

```kotlin
//  BAD - Long initialization before startForeground
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    initializeHeavyResources() // Takes 10 seconds - ANR!
    startForeground(NOTIFICATION_ID, notification)
    return START_STICKY
}

//  GOOD - startForeground immediately
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    startForeground(NOTIFICATION_ID, notification)
    CoroutineScope(Dispatchers.IO).launch {
        initializeHeavyResources() // Background thread
    }
    return START_STICKY
}
```

**Issue 2: ForegroundServiceStartNotAllowedException (Android 12+)**

```kotlin
//  BAD - Start from background without exemption
fun startServiceFromBackground() {
    context.startForegroundService(Intent(context, MyService::class.java))
    // Throws ForegroundServiceStartNotAllowedException on Android 12+
}

//  GOOD - Check if can start
fun startServiceSafely() {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        // Use WorkManager instead
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
            .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
            .build()
        WorkManager.getInstance(context).enqueue(workRequest)
    } else {
        context.startForegroundService(Intent(context, MyService::class.java))
    }
}
```

**Issue 3: Missing permission crash**

```kotlin
//  BAD - Missing manifest permission
// Crashes on Android 14+

//  GOOD - Add permission to manifest
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
```

### Summary

**Foreground service types (Android 10+):**
- Must declare in manifest
- Must specify when calling startForeground()
- Required permissions for each type

**Android 14 restrictions:**
- Most services need user-initiated action
- Short service type for < 3 minute tasks
- Special use requires justification

**Key requirements:**
- Must show notification (PRIORITY_LOW or higher)
- Call startForeground() within 5 seconds
- Declare service type in manifest (Android 10+)
- Request runtime permissions
- Stop service when done

**Best practices:**
- Start foreground immediately in onStartCommand()
- Use correct service type for use case
- Stop service when work complete
- Handle cancellation and cleanup
- Consider WorkManager as alternative

**Common types:**
- `mediaPlayback` - Music, podcasts
- `location` - GPS tracking, navigation
- `dataSync` - File sync, backup
- `camera` - Video recording
- `microphone` - Audio recording
- `phoneCall` - VoIP calls
- `shortService` - Quick tasks < 3 min

---

# Вопрос (RU)
Что такое типы Foreground Service в Android? Как правильно реализовать foreground services, работать с типами сервисов (Android 10+), и какие ограничения в Android 14?

## Ответ (RU)

### Обзор

**Foreground Services** (сервисы переднего плана) выполняются с видимым уведомлением, позволяя длительным операциям продолжаться даже когда приложение находится в фоне. Начиная с Android 10 (API 29), необходимо объявлять типы сервисов, а Android 14 (API 34) ввел более строгие ограничения.

### Типы Foreground Service (Android 10+)

Android предоставляет несколько типов foreground сервисов, каждый для конкретного случая использования:

- **CAMERA** - для работы с камерой (запись видео)
- **CONNECTED_DEVICE** - для подключенных устройств (Bluetooth, USB)
- **DATA_SYNC** - для синхронизации данных
- **LOCATION** - для отслеживания местоположения
- **MEDIA_PLAYBACK** - для воспроизведения медиа (музыка, подкасты)
- **MEDIA_PROJECTION** - для захвата экрана
- **MICROPHONE** - для записи аудио
- **PHONE_CALL** - для VoIP звонков
- **REMOTE_MESSAGING** - для обмена сообщениями (Android 11+)
- **SHORT_SERVICE** - для коротких задач до 3 минут (Android 12+)
- **SPECIAL_USE** - для специальных случаев (Android 14+)
- **HEALTH** - для фитнес-трекинга (Android 14+)

### Объявление типов сервисов

Для каждого типа сервиса необходимо объявить соответствующие разрешения в AndroidManifest.xml. Начиная с Android 10, требуется указывать атрибут `android:foregroundServiceType` в декларации сервиса.

Например, для сервиса воспроизведения музыки необходимы разрешения:
- `FOREGROUND_SERVICE` - базовое разрешение для всех foreground сервисов
- `FOREGROUND_SERVICE_MEDIA_PLAYBACK` - специфичное разрешение для медиа
- `POST_NOTIFICATIONS` - для показа уведомлений (Android 13+)

### Базовая реализация

При реализации foreground сервиса критически важно вызвать `startForeground()` в течение 5 секунд после запуска сервиса. Иначе система выбросит исключение ANR (Application Not Responding).

Метод `startForeground()` принимает три параметра:
1. ID уведомления (должен быть уникальным в приложении)
2. Notification объект (должен иметь приоритет LOW или выше)
3. Тип сервиса (для Android 10+)

### Ограничения Android 14

Android 14 ввел значительные изменения в работу foreground сервисов:

**1. Требование действий пользователя** - Большинство foreground сервисов теперь можно запускать только когда приложение находится на переднем плане или в результате действий пользователя (нажатие на уведомление, запуск с точного будильника и т.д.).

**2. Short Service** - Новый тип для быстрых операций продолжительностью до 3 минут. Система автоматически останавливает такие сервисы по истечении таймаута.

**3. Special Use** - Для нестандартных случаев использования, требует обоснования в Play Console.

**Исключения**, позволяющие запуск из фона:
- Сервисы MEDIA_PLAYBACK с активной медиа-сессией
- Сервисы PHONE_CALL во время активного звонка
- Сервисы CONNECTED_DEVICE при подключенном Bluetooth/USB устройстве
- Сервисы, запущенные высокоприоритетным FCM сообщением
- Сервисы, запущенные из действия уведомления
- Сервисы, запущенные с точного будильника (exact alarm)

### Жизненный цикл сервиса

Foreground сервис проходит через следующие этапы:

1. **onCreate()** - вызывается один раз при создании сервиса
2. **onStartCommand()** - вызывается каждый раз при запуске сервиса через startService() или startForegroundService()
3. **onDestroy()** - вызывается при уничтожении сервиса

Возвращаемое значение `onStartCommand()` определяет поведение при перезапуске:
- **START_STICKY** - система перезапустит сервис с null intent после завершения ресурсов
- **START_NOT_STICKY** - система не будет перезапускать сервис
- **START_REDELIVER_INTENT** - система перезапустит с тем же intent

### Комбинирование типов сервисов

Можно комбинировать несколько типов сервисов, используя побитовое ИЛИ. Например, для фитнес-приложения, которое отслеживает местоположение и записывает видео, можно использовать `LOCATION | CAMERA`. При этом в манифесте нужно указать оба типа через вертикальную черту и добавить соответствующие разрешения.

### Лучшие практики

**1. Немедленный запуск foreground** - Вызывайте startForeground() сразу в начале onStartCommand(), до выполнения любой тяжелой работы.

**2. Правильный выбор типа** - Используйте тип, соответствующий реальной функциональности сервиса. Неправильный выбор может привести к отклонению приложения в Play Store.

**3. Остановка сервиса** - Всегда останавливайте сервис вызовом stopForeground() и stopSelf() когда работа завершена.

**4. Обработка отмены** - В onDestroy() отменяйте все корутины и освобождайте ресурсы.

**5. Проверка разрешений** - Проверяйте наличие runtime разрешений перед запуском сервиса.

### Альтернативы

Для многих случаев использования рекомендуется рассмотреть **WorkManager** вместо foreground сервисов:
- Expedited Work для срочных задач
- Periodic Work для периодических задач
- Автоматическая обработка ограничений Android 12+
- Лучшая совместимость с Doze режимом

### Резюме

**Типы foreground service (Android 10+):**
- Должны быть объявлены в манифесте
- Должны указываться при вызове startForeground()
- Требуются разрешения для каждого типа

**Ограничения Android 14:**
- Большинству сервисов нужно действие, инициированное пользователем
- Short service тип для задач < 3 минут
- Special use требует обоснования

**Ключевые требования:**
- Должен показывать notification (PRIORITY_LOW или выше)
- Вызвать startForeground() в течение 5 секунд
- Объявить тип сервиса в манифесте (Android 10+)
- Запросить runtime-разрешения
- Остановить сервис по завершении

**Лучшие практики:**
- Запускать foreground немедленно в onStartCommand()
- Использовать правильный тип для случая применения
- Останавливать сервис при завершении работы
- Обрабатывать отмену и очистку
- Рассмотреть WorkManager как альтернативу

**Распространённые типы:**
- `mediaPlayback` — Музыка, подкасты
- `location` — GPS-трекинг, навигация
- `dataSync` — Синхронизация файлов, резервное копирование
- `camera` — Запись видео
- `microphone` — Запись аудио
- `phoneCall` — VoIP-звонки
- `shortService` — Быстрые задачи < 3 мин

---

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Service

### Related (Medium)
- [[q-service-component--android--medium]] - Service
- [[q-when-can-the-system-restart-a-service--android--medium]] - Service
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Service
- [[q-keep-service-running-background--android--medium]] - Service
- [[q-background-vs-foreground-service--android--medium]] - Service

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Service
