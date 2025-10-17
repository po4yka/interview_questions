---
id: "20251015082238618"
title: "Workmanager Vs Alternatives / Workmanager против Alternatives"
topic: android
difficulty: medium
status: draft
created: 2025-10-12
tags: - android
  - workmanager
  - alarmmanager
  - jobscheduler
  - background-processing
date_updated: 2025-10-13
moc: moc-android
related_questions:   - q-workmanager-advanced--background--medium
  - q-foreground-service-types--background--medium
subtopics: [background-execution, workmanager]
---
# Question (EN)
When should you use WorkManager vs AlarmManager vs JobScheduler vs Foreground Service? What are the trade-offs and use cases for each?

## Answer (EN)
### Overview

Android provides multiple APIs for background work, each with different capabilities and constraints:

| API | Best For | Guarantees | Survives | Timing | Constraints |
|-----|----------|------------|----------|---------|-------------|
| **WorkManager** | Deferrable guaranteed work |  Guaranteed | Reboots, app updates | Flexible | Network, battery, storage |
| **AlarmManager** | Time-critical tasks |  Exact timing | Reboots | Exact or window | None |
| **JobScheduler** | Scheduled background work |  Guaranteed | Reboots | Flexible | Network, charging, idle |
| **Foreground Service** | User-visible ongoing work |  User can stop | While running | Immediate | None |
| **Coroutines** | Short async tasks |  Not guaranteed | Only while app alive | Immediate | None |

### WorkManager

**Use when:**
-  Work must eventually complete (guaranteed)
-  Work can be deferred (flexible timing)
-  Need to respect constraints (network, battery)
-  Work should survive app restart/update

**Don't use when:**
-  Need exact timing (use AlarmManager)
-  User must see it running (use Foreground Service)
-  Very time-sensitive (use AlarmManager)

**Example: Photo backup**

```kotlin
fun schedulePhotoBackup() {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
        .setRequiresBatteryNotLow(true)
        .build()

    val backupRequest = PeriodicWorkRequestBuilder<PhotoBackupWorker>(
        24, TimeUnit.HOURS
    )
        .setConstraints(constraints)
        .build()

    WorkManager.getInstance(context)
        .enqueueUniquePeriodicWork(
            "photo_backup",
            ExistingPeriodicWorkPolicy.KEEP,
            backupRequest
        )
}

@HiltWorker
class PhotoBackupWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val photoRepository: PhotoRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val photos = photoRepository.getUnsyncedPhotos()
            photos.forEach { photo ->
                photoRepository.uploadPhoto(photo)
            }
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

**Characteristics:**
- Minimum periodic interval: 15 minutes
- Runs when constraints met (flexible)
- Survives app updates and reboots
- Automatic retry with backoff
- Good for: Sync, backup, cleanup, upload

### AlarmManager

**Use when:**
-  Need exact timing (within seconds)
-  Time-critical operations
-  Alarm clock, reminders, scheduled tasks

**Don't use when:**
-  Can be deferred (use WorkManager)
-  Need network/battery constraints (use WorkManager)
-  Just need periodic sync (use WorkManager)

**Example: Medication reminder**

```kotlin
fun scheduleMedicationReminder(reminderTime: Long) {
    val alarmManager = context.getSystemService(AlarmManager::class.java)

    val intent = Intent(context, MedicationReminderReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        MEDICATION_REQUEST_CODE,
        intent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )

    // Exact alarm (requires SCHEDULE_EXACT_ALARM permission on Android 12+)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        if (alarmManager.canScheduleExactAlarms()) {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                reminderTime,
                pendingIntent
            )
        } else {
            // Fallback to inexact alarm
            alarmManager.setAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                reminderTime,
                pendingIntent
            )
        }
    } else {
        alarmManager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP,
            reminderTime,
            pendingIntent
        )
    }
}

class MedicationReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Show notification
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_medication)
            .setContentTitle("Medication Reminder")
            .setContentText("Time to take your medication")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .build()

        NotificationManagerCompat.from(context)
            .notify(MEDICATION_NOTIFICATION_ID, notification)

        // Schedule next reminder (e.g., next day same time)
        val nextReminder = reminderTime + TimeUnit.DAYS.toMillis(1)
        scheduleMedicationReminder(nextReminder)
    }
}
```

**Alarm types:**

```kotlin
// RTC - Real Time Clock (wall clock time)
AlarmManager.RTC // Doesn't wake device
AlarmManager.RTC_WAKEUP // Wakes device

// ELAPSED_REALTIME - Time since boot
AlarmManager.ELAPSED_REALTIME // Doesn't wake device
AlarmManager.ELAPSED_REALTIME_WAKEUP // Wakes device

// Examples:
// Exact alarm at specific time
alarmManager.setExact(
    AlarmManager.RTC_WAKEUP,
    triggerAtMillis,
    pendingIntent
)

// Repeating alarm
alarmManager.setRepeating(
    AlarmManager.RTC_WAKEUP,
    firstTriggerMillis,
    intervalMillis,
    pendingIntent
)

// Inexact alarm (more battery friendly)
alarmManager.set(
    AlarmManager.RTC_WAKEUP,
    triggerAtMillis,
    pendingIntent
)

// Window alarm (between two times)
alarmManager.setWindow(
    AlarmManager.RTC_WAKEUP,
    windowStartMillis,
    windowLengthMillis,
    pendingIntent
)
```

**Android 12+ restrictions:**

```xml
<!-- Manifest permission for exact alarms -->
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />

<!-- Or use this for user-facing alarms (clocks, calendars) -->
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
```

**Characteristics:**
- Can trigger at exact times (seconds precision)
- Wakes device from sleep
- Limited by battery optimization
- Good for: Alarms, reminders, time-sensitive tasks

### JobScheduler

**Use when:**
-  API 21+ only (no backward compatibility needed)
-  Need constraints (network, charging, idle)
-  Can be deferred

**Don't use when:**
-  Need to support older Android versions (use WorkManager)
-  WorkManager provides everything you need

**Note:** WorkManager uses JobScheduler internally on API 23+, so prefer WorkManager for better API and backward compatibility.

**Example: Database cleanup**

```kotlin
fun scheduleCleanup(context: Context) {
    val jobScheduler = context.getSystemService(JobScheduler::class.java)

    val jobInfo = JobInfo.Builder(
        CLEANUP_JOB_ID,
        ComponentName(context, CleanupJobService::class.java)
    )
        .setRequiresDeviceIdle(true) // Only when device idle
        .setRequiresCharging(true) // Only when charging
        .setPersisted(true) // Survive reboot
        .setPeriodic(TimeUnit.DAYS.toMillis(1)) // Daily
        .build()

    jobScheduler.schedule(jobInfo)
}

class CleanupJobService : JobService() {
    private var job: Job? = null

    override fun onStartJob(params: JobParameters): Boolean {
        job = CoroutineScope(Dispatchers.IO).launch {
            try {
                // Clean old data
                database.cleanOldRecords()

                // Job completed successfully
                jobFinished(params, false)
            } catch (e: Exception) {
                // Job failed, reschedule
                jobFinished(params, true)
            }
        }

        return true // Work is ongoing
    }

    override fun onStopJob(params: JobParameters): Boolean {
        job?.cancel()
        return true // Reschedule
    }
}
```

**Characteristics:**
- API 21+ only
- Good constraint support
- Survives reboots
- WorkManager is better alternative

### Foreground Service

**Use when:**
-  User must know work is happening
-  Work cannot be interrupted
-  Long-running operations (minutes to hours)
-  Music playback, navigation, file download

**Don't use when:**
-  Work can be deferred (use WorkManager)
-  Quick background task (use Coroutines)
-  Don't need to show notification

**Example: Music player**

```kotlin
class MusicPlayerService : Service() {

    private val mediaPlayer = MediaPlayer()
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicPlayerService = this@MusicPlayerService
    }

    override fun onBind(intent: Intent): IBinder = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stop()
        }
        return START_STICKY
    }

    private fun play() {
        val notification = createNotification()

        // Start as foreground service (required for Android 8+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        mediaPlayer.start()
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .setContentText(currentSong.title)
            .addAction(R.drawable.ic_pause, "Pause", pausePendingIntent)
            .addAction(R.drawable.ic_stop, "Stop", stopPendingIntent)
            .setStyle(
                MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    private fun pause() {
        mediaPlayer.pause()
    }

    private fun stop() {
        mediaPlayer.stop()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
}

// Start service
fun startMusicPlayback() {
    val intent = Intent(context, MusicPlayerService::class.java).apply {
        action = ACTION_PLAY
    }

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        context.startForegroundService(intent)
    } else {
        context.startService(intent)
    }
}
```

**Foreground service types (Android 10+):**

```xml
<service
    android:name=".MusicPlayerService"
    android:foregroundServiceType="mediaPlayback" />

<!-- Available types: -->
<!-- camera, connectedDevice, dataSync, location, mediaPlayback,
     mediaProjection, microphone, phoneCall, remoteMessaging,
     shortService, specialUse, systemExempted -->
```

**Characteristics:**
- Must show notification
- User is aware work is happening
- Not killed by system (unless low memory)
- Battery intensive
- Good for: Media playback, navigation, file transfers

### Coroutines (No Guarantee)

**Use when:**
-  Quick async operations
-  App is in foreground
-  OK if work doesn't complete

**Don't use when:**
-  Work must complete (use WorkManager)
-  App might be killed (use WorkManager)

**Example: Quick API call**

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: HomeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            try {
                val data = repository.fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

**Characteristics:**
- No guarantee of completion
- Canceled when scope canceled
- Good for: UI updates, quick API calls
- Not good for: Background sync, uploads

### Decision Tree

```
Need to show notification to user?
 YES → Foreground Service
 NO
     Must happen at exact time?
        YES → AlarmManager
        NO
            Must complete even if app killed?
               YES → WorkManager
               NO → Coroutines
            Need constraints (WiFi, battery)?
                YES → WorkManager
```

### Comparison Table

| Feature | WorkManager | AlarmManager | JobScheduler | Foreground Service | Coroutines |
|---------|-------------|--------------|--------------|-------------------|------------|
| **Guaranteed execution** |  |  |  |  |  |
| **Exact timing** |  |  |  |  |  |
| **Survives reboot** |  |  |  |  |  |
| **Survives app kill** |  |  |  |  |  |
| **Network constraint** |  |  |  |  |  |
| **Battery constraint** |  |  |  |  |  |
| **Backward compatibility** |  API 14+ |  |  API 21+ |  |  |
| **User visibility** |  |  |  |  Required |  |
| **Min interval** | 15 min | None | 15 min | N/A | N/A |
| **Battery friendly** |  |  |  |  |  |

### Real-World Use Cases

**WorkManager:**
```
 Sync app data when WiFi available
 Backup photos overnight
 Upload logs to server
 Clean old cache files
 Process images for upload
 Send analytics events in batch
```

**AlarmManager:**
```
 Alarm clock app
 Medication reminders
 Calendar event notifications
 Recurring bill reminders
 Scheduled report generation
```

**Foreground Service:**
```
 Music/podcast playback
 GPS navigation
 File downloads (user-initiated)
 Video call
 Fitness tracking
 Live location sharing
```

**Coroutines:**
```
 Load data for UI
 Quick API calls
 Image loading
 Form validation
 Database queries (while app active)
```

### Best Practices

1. **Prefer WorkManager for Background Work**
   ```kotlin
   //  GOOD - WorkManager for sync
   WorkManager.getInstance(context)
       .enqueueUniquePeriodicWork(...)

   //  BAD - AlarmManager for periodic sync
   alarmManager.setRepeating(...)
   ```

2. **Use AlarmManager Only for Exact Timing**
   ```kotlin
   //  GOOD - Alarm clock
   alarmManager.setExact(...)

   //  BAD - Data sync (use WorkManager)
   alarmManager.setRepeating(...)
   ```

3. **Foreground Service Only When Visible**
   ```kotlin
   //  GOOD - Music playback
   startForeground(notification)

   //  BAD - Silent data sync
   startForeground(notification) // User sees notification!
   ```

4. **Coroutines for UI-Related Work**
   ```kotlin
   //  GOOD - Load data for screen
   viewModelScope.launch { loadData() }

   //  BAD - Upload file (use WorkManager)
   viewModelScope.launch { uploadFile() } // Might be killed!
   ```

### Summary

**Use WorkManager when:**
- Work must complete (guaranteed)
- Work can be deferred
- Need constraints (network, battery, storage)
- Work survives app updates/reboots

**Use AlarmManager when:**
- Need exact timing (alarm clock, reminders)
- Time-critical operations

**Use Foreground Service when:**
- User must see work happening (notification required)
- Long-running operations (music, navigation)

**Use Coroutines when:**
- Quick async work
- App is in foreground
- OK if work doesn't complete

**General rule:** Start with WorkManager for background work. Only use alternatives if WorkManager doesn't fit your use case.

---

# Вопрос (RU)
Когда использовать WorkManager vs AlarmManager vs JobScheduler vs Foreground Service? Какие компромиссы и применения для каждого?

## Ответ (RU)

### Обзор

Android предоставляет несколько API для фоновой работы, каждый с разными возможностями и ограничениями:

| API | Лучше всего для | Гарантии | Переживает | Тайминг | Constraints |
|-----|----------|------------|----------|---------|-------------|
| **WorkManager** | Отложенная гарантированная работа | Гарантированная | Перезагрузки, обновления приложения | Гибкий | Сеть, батарея, хранилище |
| **AlarmManager** | Критичные по времени задачи | Точный тайминг | Перезагрузки | Точный или окно | Нет |
| **JobScheduler** | Запланированная фоновая работа | Гарантированная | Перезагрузки | Гибкий | Сеть, зарядка, idle |
| **Foreground Service** | Видимая для пользователя работа | Пользователь может остановить | Пока работает | Немедленный | Нет |
| **Coroutines** | Короткие асинхронные задачи | Не гарантировано | Только пока приложение живо | Немедленный | Нет |

### WorkManager

**Используйте когда:**
- Работа должна в итоге завершиться (гарантированно)
- Работу можно отложить (гибкий тайминг)
- Нужно уважать ограничения (сеть, батарея)
- Работа должна пережить перезапуск/обновление приложения

**Не используйте когда:**
- Нужен точный тайминг (используйте AlarmManager)
- Пользователь должен видеть что работа выполняется (используйте Foreground Service)
- Очень чувствительно к времени (используйте AlarmManager)

**Пример: Резервное копирование фотографий**

```kotlin
fun schedulePhotoBackup() {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.UNMETERED) // Только WiFi
        .setRequiresBatteryNotLow(true)
        .build()

    val backupRequest = PeriodicWorkRequestBuilder<PhotoBackupWorker>(
        24, TimeUnit.HOURS
    )
        .setConstraints(constraints)
        .build()

    WorkManager.getInstance(context)
        .enqueueUniquePeriodicWork(
            "photo_backup",
            ExistingPeriodicWorkPolicy.KEEP,
            backupRequest
        )
}

@HiltWorker
class PhotoBackupWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val photoRepository: PhotoRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val photos = photoRepository.getUnsyncedPhotos()
            photos.forEach { photo ->
                photoRepository.uploadPhoto(photo)
            }
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

**Характеристики:**
- Минимальный периодический интервал: 15 минут
- Запускается когда ограничения выполнены (гибко)
- Переживает обновления приложения и перезагрузки
- Автоматический retry с backoff
- Хорошо для: синхронизация, резервное копирование, очистка, загрузка

### AlarmManager

**Используйте когда:**
- Нужен точный тайминг (в пределах секунд)
- Критичные по времени операции
- Будильник, напоминания, запланированные задачи

**Не используйте когда:**
- Можно отложить (используйте WorkManager)
- Нужны ограничения сети/батареи (используйте WorkManager)
- Просто нужна периодическая синхронизация (используйте WorkManager)

**Пример: Напоминание о лекарстве**

```kotlin
fun scheduleMedicationReminder(reminderTime: Long) {
    val alarmManager = context.getSystemService(AlarmManager::class.java)

    val intent = Intent(context, MedicationReminderReceiver::class.java)
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        MEDICATION_REQUEST_CODE,
        intent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )

    // Точный alarm (требует разрешения SCHEDULE_EXACT_ALARM на Android 12+)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        if (alarmManager.canScheduleExactAlarms()) {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                reminderTime,
                pendingIntent
            )
        } else {
            // Fallback на неточный alarm
            alarmManager.setAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                reminderTime,
                pendingIntent
            )
        }
    } else {
        alarmManager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP,
            reminderTime,
            pendingIntent
        )
    }
}

class MedicationReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Показать уведомление
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_medication)
            .setContentTitle("Напоминание о лекарстве")
            .setContentText("Время принять лекарство")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .build()

        NotificationManagerCompat.from(context)
            .notify(MEDICATION_NOTIFICATION_ID, notification)

        // Запланировать следующее напоминание
        val nextReminder = reminderTime + TimeUnit.DAYS.toMillis(1)
        scheduleMedicationReminder(nextReminder)
    }
}
```

**Типы Alarm:**

```kotlin
// RTC - Real Time Clock (время по часам)
AlarmManager.RTC // Не будит устройство
AlarmManager.RTC_WAKEUP // Будит устройство

// ELAPSED_REALTIME - Время с момента загрузки
AlarmManager.ELAPSED_REALTIME // Не будит устройство
AlarmManager.ELAPSED_REALTIME_WAKEUP // Будит устройство

// Примеры:
// Точный alarm в определенное время
alarmManager.setExact(
    AlarmManager.RTC_WAKEUP,
    triggerAtMillis,
    pendingIntent
)

// Повторяющийся alarm
alarmManager.setRepeating(
    AlarmManager.RTC_WAKEUP,
    firstTriggerMillis,
    intervalMillis,
    pendingIntent
)

// Неточный alarm (более дружелюбен к батарее)
alarmManager.set(
    AlarmManager.RTC_WAKEUP,
    triggerAtMillis,
    pendingIntent
)

// Alarm с окном (между двумя временами)
alarmManager.setWindow(
    AlarmManager.RTC_WAKEUP,
    windowStartMillis,
    windowLengthMillis,
    pendingIntent
)
```

**Ограничения Android 12+:**

```xml
<!-- Разрешение манифеста для точных alarms -->
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />

<!-- Или используйте это для пользовательских alarms (часы, календари) -->
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
```

**Характеристики:**
- Может срабатывать в точное время (точность в секундах)
- Будит устройство из сна
- Ограничено оптимизацией батареи
- Хорошо для: будильники, напоминания, задачи чувствительные к времени

### JobScheduler

**Используйте когда:**
- Только API 21+ (не нужна обратная совместимость)
- Нужны ограничения (сеть, зарядка, idle)
- Можно отложить

**Не используйте когда:**
- Нужно поддерживать старые версии Android (используйте WorkManager)
- WorkManager предоставляет все что вам нужно

**Примечание:** WorkManager использует JobScheduler внутри на API 23+, поэтому предпочтительнее WorkManager для лучшего API и обратной совместимости.

**Пример: Очистка базы данных**

```kotlin
fun scheduleCleanup(context: Context) {
    val jobScheduler = context.getSystemService(JobScheduler::class.java)

    val jobInfo = JobInfo.Builder(
        CLEANUP_JOB_ID,
        ComponentName(context, CleanupJobService::class.java)
    )
        .setRequiresDeviceIdle(true) // Только когда устройство в idle
        .setRequiresCharging(true) // Только при зарядке
        .setPersisted(true) // Пережить перезагрузку
        .setPeriodic(TimeUnit.DAYS.toMillis(1)) // Ежедневно
        .build()

    jobScheduler.schedule(jobInfo)
}

class CleanupJobService : JobService() {
    private var job: Job? = null

    override fun onStartJob(params: JobParameters): Boolean {
        job = CoroutineScope(Dispatchers.IO).launch {
            try {
                // Очистка старых данных
                database.cleanOldRecords()

                // Задача успешно завершена
                jobFinished(params, false)
            } catch (e: Exception) {
                // Задача провалилась, перепланировать
                jobFinished(params, true)
            }
        }

        return true // Работа продолжается
    }

    override fun onStopJob(params: JobParameters): Boolean {
        job?.cancel()
        return true // Перепланировать
    }
}
```

**Характеристики:**
- Только API 21+
- Хорошая поддержка ограничений
- Переживает перезагрузки
- WorkManager - лучшая альтернатива

### Foreground Service

**Используйте когда:**
- Пользователь должен знать что работа выполняется
- Работу нельзя прерывать
- Долгосрочные операции (минуты - часы)
- Воспроизведение музыки, навигация, загрузка файлов

**Не используйте когда:**
- Работу можно отложить (используйте WorkManager)
- Быстрая фоновая задача (используйте Coroutines)
- Не нужно показывать уведомление

**Пример: Музыкальный плеер**

```kotlin
class MusicPlayerService : Service() {

    private val mediaPlayer = MediaPlayer()
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicPlayerService = this@MusicPlayerService
    }

    override fun onBind(intent: Intent): IBinder = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stop()
        }
        return START_STICKY
    }

    private fun play() {
        val notification = createNotification()

        // Запустить как foreground service (обязательно для Android 8+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        mediaPlayer.start()
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Сейчас играет")
            .setContentText(currentSong.title)
            .addAction(R.drawable.ic_pause, "Пауза", pausePendingIntent)
            .addAction(R.drawable.ic_stop, "Стоп", stopPendingIntent)
            .setStyle(
                MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    private fun pause() {
        mediaPlayer.pause()
    }

    private fun stop() {
        mediaPlayer.stop()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
}

// Запустить сервис
fun startMusicPlayback() {
    val intent = Intent(context, MusicPlayerService::class.java).apply {
        action = ACTION_PLAY
    }

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        context.startForegroundService(intent)
    } else {
        context.startService(intent)
    }
}
```

**Типы Foreground service (Android 10+):**

```xml
<service
    android:name=".MusicPlayerService"
    android:foregroundServiceType="mediaPlayback" />

<!-- Доступные типы: -->
<!-- camera, connectedDevice, dataSync, location, mediaPlayback,
     mediaProjection, microphone, phoneCall, remoteMessaging,
     shortService, specialUse, systemExempted -->
```

**Характеристики:**
- Должен показывать уведомление
- Пользователь знает что работа выполняется
- Не убивается системой (кроме низкой памяти)
- Интенсивно использует батарею
- Хорошо для: воспроизведение медиа, навигация, передача файлов

### Coroutines (Без гарантий)

**Используйте когда:**
- Быстрые асинхронные операции
- Приложение на переднем плане
- OK если работа не завершится

**Не используйте когда:**
- Работа должна завершиться (используйте WorkManager)
- Приложение может быть убито (используйте WorkManager)

**Пример: Быстрый API вызов**

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: HomeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            try {
                val data = repository.fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Неизвестная ошибка")
            }
        }
    }
}
```

**Характеристики:**
- Нет гарантии завершения
- Отменяется при отмене scope
- Хорошо для: обновления UI, быстрые API вызовы
- Не хорошо для: фоновая синхронизация, загрузки

### Дерево решений

```
Нужно показывать уведомление пользователю?
 ДА → Foreground Service
 НЕТ
     Должно произойти в точное время?
        ДА → AlarmManager
        НЕТ
            Должно завершиться даже если приложение убито?
               ДА → WorkManager
               НЕТ → Coroutines
            Нужны ограничения (WiFi, батарея)?
                ДА → WorkManager
```

### Таблица сравнения

| Функция | WorkManager | AlarmManager | JobScheduler | Foreground Service | Coroutines |
|---------|-------------|--------------|--------------|-------------------|------------|
| **Гарантированное выполнение** | Да | Да | Да | Да | Нет |
| **Точный тайминг** | Нет | Да | Нет | Да | Да |
| **Переживает перезагрузку** | Да | Да | Да | Нет | Нет |
| **Переживает убийство приложения** | Да | Да | Да | Нет | Нет |
| **Ограничение сети** | Да | Нет | Да | Нет | Нет |
| **Ограничение батареи** | Да | Нет | Да | Нет | Нет |
| **Обратная совместимость** | API 14+ | Все | API 21+ | Все | Все |
| **Видимость пользователя** | Опционально | Нет | Нет | Обязательно | Нет |
| **Мин. интервал** | 15 мин | Нет | 15 мин | N/A | N/A |
| **Дружелюбен к батарее** | Да | Нет | Да | Нет | Да |

### Реальные случаи использования

**WorkManager:**
```
Синхронизация данных приложения при доступе к WiFi
Резервное копирование фотографий ночью
Загрузка логов на сервер
Очистка старых файлов кеша
Обработка изображений для загрузки
Отправка аналитических событий пакетами
```

**AlarmManager:**
```
Приложение будильника
Напоминания о лекарствах
Уведомления о событиях календаря
Напоминания о регулярных счетах
Запланированная генерация отчетов
```

**Foreground Service:**
```
Воспроизведение музыки/подкастов
GPS навигация
Загрузка файлов (инициированная пользователем)
Видеозвонок
Отслеживание фитнеса
Общий доступ к местоположению в реальном времени
```

**Coroutines:**
```
Загрузка данных для UI
Быстрые API вызовы
Загрузка изображений
Валидация форм
Запросы к базе данных (пока приложение активно)
```

### Лучшие практики

1. **Предпочитайте WorkManager для фоновой работы**
   ```kotlin
   // ХОРОШО - WorkManager для синхронизации
   WorkManager.getInstance(context)
       .enqueueUniquePeriodicWork(...)

   // ПЛОХО - AlarmManager для периодической синхронизации
   alarmManager.setRepeating(...)
   ```

2. **Используйте AlarmManager только для точного тайминга**
   ```kotlin
   // ХОРОШО - Будильник
   alarmManager.setExact(...)

   // ПЛОХО - Синхронизация данных (используйте WorkManager)
   alarmManager.setRepeating(...)
   ```

3. **Foreground Service только когда видимо**
   ```kotlin
   // ХОРОШО - Воспроизведение музыки
   startForeground(notification)

   // ПЛОХО - Тихая синхронизация данных
   startForeground(notification) // Пользователь видит уведомление!
   ```

4. **Coroutines для работы связанной с UI**
   ```kotlin
   // ХОРОШО - Загрузка данных для экрана
   viewModelScope.launch { loadData() }

   // ПЛОХО - Загрузка файла (используйте WorkManager)
   viewModelScope.launch { uploadFile() } // Может быть убито!
   ```

### Резюме

**Используйте WorkManager когда:**
- Работа должна завершиться (гарантированно)
- Работу можно отложить
- Нужны ограничения (сеть, батарея, хранилище)
- Работа переживает обновления приложения/перезагрузки

**Используйте AlarmManager когда:**
- Нужен точный тайминг (будильник, напоминания)
- Критичные по времени операции

**Используйте Foreground Service когда:**
- Пользователь должен видеть что работа выполняется (требуется уведомление)
- Долгосрочные операции (музыка, навигация)

**Используйте Coroutines когда:**
- Быстрая асинхронная работа
- Приложение на переднем плане
- OK если работа не завершится

**Общее правило:** Начинайте с WorkManager для фоновой работы. Используйте альтернативы только если WorkManager не подходит для вашего случая.
