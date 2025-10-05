---
id: 202510031417004
title: "How application priority is determined by the system"
question_ru: "Как определяется приоритет приложений перед системой"
question_en: "Как определяется приоритет приложений перед системой"
topic: android
moc: moc-android
status: draft
difficulty: hard
tags:
  - lifecycle
  - priority
  - android/activity
  - android/service
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/36
---

# How application priority is determined by the system

## English Answer

Application priority in Android is determined by several factors, including the lifecycle state of application components (Activities, Services), system resource usage, and user interaction with the application. These factors help the system determine which applications should continue running, which should be paused, and which should be terminated to free up resources.

### Process Priority Hierarchy

Android categorizes processes into five priority levels, from highest to lowest:

#### 1. Foreground Process (Highest Priority)
Applications with active components that the user is currently interacting with have the highest priority. The system strives to ensure their optimal performance for smooth user experience.

**Criteria for foreground process:**
- Activity that user is interacting with (`onResume()` has been called)
- BroadcastReceiver currently running (`onReceive()` is executing)
- Service executing a callback (`onCreate()`, `onStart()`, `onDestroy()`)

```kotlin
// Foreground Activity example
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // This Activity is now in foreground
        // Process has highest priority
    }
}
```

#### 2. Visible Process (High Priority)
Applications containing Activities that are not in the foreground but are still visible (e.g., when a dialog is displayed) also have high priority, though lower than foreground processes.

**Criteria:**
- Activity that is visible but not in foreground (e.g., partially covered by dialog)
- Service bound to a visible Activity

```kotlin
// Visible but not focused Activity
class DialogActivity : AppCompatActivity() {
    override fun onPause() {
        super.onPause()
        // Activity still visible but not interactive
        // Process has visible priority
    }
}
```

#### 3. Service Process (Medium Priority)
Services running in the background have lower priority compared to foreground Activities. The system may stop background services to free resources, especially when device is low on memory.

**Important distinction:**

```kotlin
// Regular background service - medium priority
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Service running in background
        return START_STICKY
    }
}

// Foreground service - high priority (close to foreground process)
class ForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        // Service has high priority due to notification
        return START_STICKY
    }
}
```

#### 4. Cached Process (Low Priority)
Applications that have been used but are currently inactive and cached for quick restoration have the lowest priority. These processes are the first to be terminated when system needs to free resources.

**Characteristics:**
- No active components
- Process kept for quick restart
- Multiple cached processes may exist
- Terminated in LRU (Least Recently Used) order

```kotlin
// Activity moved to background
class CachedActivity : AppCompatActivity() {
    override fun onStop() {
        super.onStop()
        // If app has no other active components,
        // process becomes cached
    }
}
```

#### 5. Empty Process (Lowest Priority)
Processes that don't host any active application components are kept only for caching purposes and can be killed at any time.

### Process Priority Diagram

```
┌─────────────────────────────────────────┐
│ Foreground Process                      │ ← Highest Priority
│ - Active Activity (onResume)            │   Almost never killed
│ - Running BroadcastReceiver             │
│ - Service callback executing            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Visible Process                         │
│ - Visible Activity (onPause)            │
│ - Service bound to visible Activity     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Service Process                         │
│ - Background Service running            │
│ - Foreground Service with notification  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Cached Process                          │
│ - No active components                  │
│ - Ready for quick restart               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Empty Process                           │ ← Lowest Priority
│ - No active components                  │   First to be killed
│ - Kept only for caching                 │
└─────────────────────────────────────────┘
```

### Foreground Services (Special Case)

Starting with Android 8.0 (API 26), foreground services must display a notification:

```kotlin
class MusicPlayerService : Service() {

    private fun startForegroundService() {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Music Player")
            .setContentText("Playing: Song Title")
            .setSmallIcon(R.drawable.ic_music)
            .build()

        // Service gains high priority
        startForeground(NOTIFICATION_ID, notification)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForegroundService()
        // Now service has priority similar to foreground Activity
        return START_STICKY
    }
}
```

### Background Execution Limits

Starting with Android Oreo (API 26), new restrictions on background execution:

```kotlin
// ❌ BAD - Background service limitations
// Starting from API 26, this is restricted
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startService(Intent(this, BackgroundService::class.java))
    // May throw IllegalStateException if app is in background
}

// ✅ GOOD - Use foreground service or WorkManager
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(Intent(this, ForegroundService::class.java))
} else {
    startService(Intent(this, ForegroundService::class.java))
}

// ✅ BETTER - Use WorkManager for deferrable tasks
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()
WorkManager.getInstance(context).enqueue(workRequest)
```

### Factors Affecting Process Priority

1. **Component State**: Active vs inactive components
2. **User Interaction**: Recent user interaction increases priority
3. **Service Type**: Foreground vs background services
4. **Bound Services**: Services bound to higher-priority components
5. **System Resources**: Memory pressure affects kill decisions

### Best Practices

```kotlin
class OptimizedActivity : AppCompatActivity() {

    private var wakeLock: PowerManager.WakeLock? = null

    override fun onResume() {
        super.onResume()
        // High priority - start critical operations
        startCriticalUpdates()
    }

    override fun onPause() {
        super.onPause()
        // Priority lowering - pause non-critical operations
        pauseNonCriticalUpdates()
        saveState() // Save important state
    }

    override fun onStop() {
        super.onStop()
        // May become cached - release resources
        releaseResources()
        wakeLock?.release()
    }
}
```

## Russian Answer

Приоритет приложений определяется на основе нескольких факторов, включая состояние жизненного цикла компонентов приложения (таких как Activity, Services), использование системных ресурсов и взаимодействие пользователя с приложением. Эти факторы помогают системе определить, какие приложения следует оставить работающими, какие приостановить, и какие закрыть для освобождения ресурсов.

### Ключевые аспекты, влияющие на определение приоритета приложений перед системой

1. **Foreground Activity**: Приложения, имеющие активные компоненты (например, Activity), с которыми пользователь взаимодействует в данный момент, обладают наивысшим приоритетом. Система стремится максимально обеспечить их работоспособность, чтобы пользовательский опыт был максимально плавным и без задержек.

2. **Visible Activity**: Приложения, содержащие Activity, которые не находятся на переднем плане, но всё ещё видимы пользователю (например, когда отображается диалоговое окно), также имеют высокий приоритет, хотя и ниже, чем у приложений на переднем плане.

3. **Background Services**: Сервисы, работающие в фоне, имеют более низкий приоритет по сравнению с активностями на переднем плане. Система может решить остановить фоновые сервисы для освобождения ресурсов, особенно если устройство испытывает нехватку памяти.

4. **Broadcast Receivers**: Компоненты, ожидающие широковещательные сообщения, не занимают много ресурсов, пока не получат сигнал к активации. Приоритет этих компонентов повышается в момент получения и обработки сообщения.

5. **Cached Processes**: Приложения, которые были использованы, но в данный момент не активны и сохранены в кэше для быстрого восстановления, имеют самый низкий приоритет. Эти процессы первыми подлежат завершению при необходимости освободить системные ресурсы.

### Исключения и специальные случаи

**Foreground Services**: Сервисы, объявленные как работающие на переднем плане с использованием уведомления, имеют высокий приоритет, схожий с приоритетом активных Activity.

**Ограничения для фоновой работы**: Начиная с Android Oreo (API уровень 26), введены новые ограничения на фоновую работу приложений для улучшения производительности системы и увеличения времени работы от батареи. Это влияет на способы, которыми приложения могут выполнять фоновые задачи и службы.

Приоритет приложений перед системой Android определяется на основе их взаимодействия с пользователем и использования системных ресурсов. Активные и видимые для пользователя приложения имеют высокий приоритет, в то время как фоновые задачи и кэшированные процессы могут быть ограничены в ресурсах или завершены системой для оптимизации производительности и экономии энергии.
