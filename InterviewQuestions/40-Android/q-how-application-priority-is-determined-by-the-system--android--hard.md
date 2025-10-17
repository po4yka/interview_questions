---
id: "20251015082237254"
title: "How Application Priority Is Determined By The System / Как система определяет приоритет приложения"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [process-management, memory-management, lifecycle, difficulty/hard]
---

# Question (EN)

> How application priority is determined by the system?

# Вопрос (RU)

> Как система определяет приоритет приложения?

---

## Answer (EN)

Android determines application priority based on the **importance hierarchy** of processes, which affects **Low Memory Killer (LMK)** decisions and CPU/resource allocation. The system classifies processes into five main priority levels.

### Process Priority Hierarchy

From highest to lowest priority:

1. **Foreground Process** (highest priority)
2. **Visible Process**
3. **Service Process**
4. **Cached Process** (Background/Empty)
5. **Empty Process** (lowest priority)

### 1. Foreground Process

**Definition:** Process the user is currently interacting with.

**Conditions:**

-   Has an Activity in **resumed state** (onResume called, user seeing it)
-   Has a Service bound to foreground Activity
-   Has a Service running in foreground (via startForeground with notification)
-   Has a BroadcastReceiver executing onReceive()
-   Has a ContentProvider executing onCreate()

**Example:**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // App is now FOREGROUND PROCESS
        // Highest priority - will NOT be killed
    }
}

// Foreground Service
class MusicPlayerService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        // Service is now FOREGROUND PROCESS
        return START_STICKY
    }
}
```

**Priority:** **Critical** - System will only kill as last resort

**OOM adj value:** 0 (lowest oom_adj = highest priority)

### 2. Visible Process

**Definition:** Process doing something user is aware of, but not in foreground.

**Conditions:**

-   Has an Activity in **paused state** (onPause called, partially visible)
-   Activity covered by non-fullscreen Activity (dialog, transparent Activity)
-   Has a Service bound to visible Activity

**Example:**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onPause() {
        super.onPause()
        // If Activity still partially visible:
        // App is now VISIBLE PROCESS
    }
}

// Example: Dialog on top of Activity
fun showDialog() {
    AlertDialog.Builder(this)
        .setTitle("Dialog")
        .setMessage("Activity behind this dialog is VISIBLE PROCESS")
        .show()
    // MainActivity is paused but visible → VISIBLE PROCESS
}
```

**Priority:** **High** - Rarely killed, only if needed for foreground processes

**OOM adj value:** 100-200

### 3. Service Process

**Definition:** Process running a Service started with startService().

**Conditions:**

-   Has a Service running (not foreground service)
-   Service performing long-running operation

**Example:**

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background download
        startDownload()
        // Service is SERVICE PROCESS (not foreground)
        return START_STICKY
    }

    private fun startDownload() {
        CoroutineScope(Dispatchers.IO).launch {
            // Long-running download
            downloadFile()
        }
    }
}

// Starting the service
startService(Intent(this, DownloadService::class.java))
// DownloadService process is now SERVICE PROCESS
```

**Priority:** **Medium** - Killed when memory needed for higher priority processes

**OOM adj value:** 300-400

**Note:** Services running for 30+ minutes may be demoted to lower priority.

### 4. Cached Process (Background)

**Definition:** Process not currently needed, kept in cache for faster restart.

**Conditions:**

-   Has an Activity in **stopped state** (onStop called, not visible)
-   No active components (Service, BroadcastReceiver, etc.)
-   User navigated away from app

**Example:**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onStop() {
        super.onStop()
        // Activity no longer visible
        // App is now CACHED PROCESS
    }
}

// User scenario:
// 1. User opens App A → FOREGROUND
// 2. User presses Home → App A becomes CACHED
// 3. User opens App B → App B is FOREGROUND, App A still CACHED
// 4. User returns to App A → CACHED → FOREGROUND (fast restart)
```

**Priority:** **Low** - First to be killed when memory is low

**OOM adj value:** 900-999

**LRU list:** Android maintains Least Recently Used list of cached processes. Oldest unused processes killed first.

### 5. Empty Process

**Definition:** Process with no active components, kept only for caching.

**Conditions:**

-   No Activity, Service, or any component
-   Process kept alive for faster cold start

**Priority:** **Lowest** - Killed immediately when memory needed

**OOM adj value:** 1000

### Priority Determination Logic

```kotlin
// Simplified Android system logic
fun determineProcessPriority(process: Process): Int {
    return when {
        // Foreground: User is interacting
        process.hasResumedActivity() -> IMPORTANCE_FOREGROUND
        process.hasForegroundService() -> IMPORTANCE_FOREGROUND
        process.hasExecutingBroadcastReceiver() -> IMPORTANCE_FOREGROUND

        // Visible: User can see it
        process.hasPausedActivity() -> IMPORTANCE_VISIBLE
        process.isBoundToVisibleActivity() -> IMPORTANCE_VISIBLE

        // Service: Doing work in background
        process.hasRunningService() -> IMPORTANCE_SERVICE

        // Cached: Stopped but kept for quick restart
        process.hasStoppedActivity() -> IMPORTANCE_CACHED

        // Empty: No components
        else -> IMPORTANCE_EMPTY
    }
}
```

### Low Memory Killer (LMK)

Android's Low Memory Killer uses **oom_adj** (Out-Of-Memory adjustment) scores:

```
Priority         oom_adj     When killed

Foreground       0           Last resort (critical)
Visible          100-200     Rarely
Perceptible      200-250     If needed for foreground
Service          300-400     When memory low
Cached           900-999     First (LRU order)
Empty            1000        Immediately
```

**Process:**

1. System detects **low memory**
2. LMK kills processes starting from **highest oom_adj**
3. Continues until **enough memory freed**

### Factors Affecting Priority

#### 1. Component State

```kotlin
// High priority - Foreground Activity
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // Priority: FOREGROUND (0)
    }

    override fun onPause() {
        super.onPause()
        // Priority: VISIBLE (100) if still partially visible
    }

    override fun onStop() {
        super.onStop()
        // Priority: CACHED (900)
    }
}
```

#### 2. Service Type

```kotlin
// High priority - Foreground Service
class LocationService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(1, notification)
        // Priority: FOREGROUND (0)
        return START_STICKY
    }
}

// Medium priority - Background Service
class SyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performSync()
        // Priority: SERVICE (300)
        return START_STICKY
    }
}
```

#### 3. Bound Services

```kotlin
// Service bound to foreground Activity inherits its priority
class DataService : Service() {
    override fun onBind(intent: Intent?): IBinder {
        return binder
    }
}

class MainActivity : AppCompatActivity() {
    override fun onStart() {
        super.onStart()
        // Bind to service
        bindService(
            Intent(this, DataService::class.java),
            connection,
            Context.BIND_AUTO_CREATE
        )
        // DataService now has FOREGROUND priority (same as MainActivity)
    }
}
```

#### 4. Process Dependency

If **Process A** depends on **Process B**, B inherits A's priority (if higher).

```kotlin
// Process A (foreground) binds to Process B (background)
// → Process B elevated to foreground priority
```

### Checking Process Priority

```kotlin
class PriorityChecker {
    fun getCurrentPriority(context: Context): Int {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val runningAppProcesses = activityManager.runningAppProcesses ?: return -1

        val myPid = android.os.Process.myPid()
        for (processInfo in runningAppProcesses) {
            if (processInfo.pid == myPid) {
                return processInfo.importance
            }
        }
        return -1
    }

    fun logPriority(context: Context) {
        val importance = getCurrentPriority(context)
        val priorityName = when (importance) {
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND -> "FOREGROUND"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_VISIBLE -> "VISIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_SERVICE -> "SERVICE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_CACHED -> "CACHED"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_GONE -> "GONE"
            else -> "UNKNOWN"
        }
        Log.d("Priority", "Current priority: $priorityName ($importance)")
    }
}

// Usage
class MainActivity : AppCompatActivity() {
    private val priorityChecker = PriorityChecker()

    override fun onResume() {
        super.onResume()
        priorityChecker.logPriority(this)
        // Output: "Current priority: FOREGROUND (100)"
    }

    override fun onStop() {
        super.onStop()
        priorityChecker.logPriority(this)
        // Output: "Current priority: CACHED (400)"
    }
}
```

### Priority Transitions Example

```kotlin
class LifecycleApp : Application() {
    override fun onCreate() {
        super.onCreate()

        // Scenario 1: Normal app usage
        // App launches → FOREGROUND (0)
        // User presses Home → CACHED (900)
        // User returns → FOREGROUND (0)

        // Scenario 2: With background service
        // App launches → FOREGROUND (0)
        // Starts background service → Still FOREGROUND (0)
        // User presses Home → SERVICE (300) due to running service
        // Service finishes → CACHED (900)

        // Scenario 3: With foreground service
        // App launches → FOREGROUND (0)
        // Starts foreground service → Still FOREGROUND (0)
        // User presses Home → Still FOREGROUND (0) due to foreground service!
        // Service stops → CACHED (900)
    }
}
```

### Process Lifetime Management

```kotlin
class ProcessManagement {

    // Keep process alive longer
    fun increaseProcessPriority() {
        // 1. Use foreground service
        startForegroundService()

        // 2. Keep Activity visible (not stopped)
        // Use sticky notifications, Picture-in-Picture, etc.

        // 3. Bind to higher-priority process
        bindToSystemService()
    }

    private fun startForegroundService() {
        val intent = Intent(context, MyForegroundService::class.java)
        context.startForegroundService(intent)
        // Elevates process to FOREGROUND priority
    }

    // DO NOT abuse these techniques!
    // Android will penalize apps that unnecessarily stay in memory
}
```

### Best Practices

1. **Understand priority levels** to predict when your app might be killed
2. **Use foreground services** only when necessary (music, navigation, etc.)
3. **Save state** in onPause/onStop - app can be killed from CACHED state
4. **Use WorkManager** for deferrable background work instead of long-running services
5. **Don't fight the system** - Excessive battery use leads to restrictions
6. **Test with "Don't keep activities"** developer option enabled

### Summary

**Priority hierarchy:**

```
FOREGROUND (0)       → User interacting, foreground service
    ↓
VISIBLE (100-200)    → Partially visible (dialog on top)
    ↓
SERVICE (300-400)    → Background service running
    ↓
CACHED (900-999)     → Stopped, kept for quick restart
    ↓
EMPTY (1000)         → No components, killed first
```

**Key factors:**

-   Activity state (resumed > paused > stopped)
-   Service type (foreground > background)
-   Bound services (inherit bound component's priority)
-   Component execution (BroadcastReceiver, ContentProvider)

**System behavior:**

-   Low Memory Killer (LMK) kills lowest priority first
-   LRU order within same priority level
-   Foreground processes rarely killed

## Ответ (RU)

Android определяет приоритет приложения на основе **иерархии важности процессов**, что влияет на решения **Low Memory Killer (LMK)** и распределение ресурсов.

### Иерархия приоритетов (от высшего к низшему)

1. **Foreground Process** - пользователь взаимодействует (Activity в onResume, foreground service)
2. **Visible Process** - частично виден (Activity в onPause, диалог сверху)
3. **Service Process** - фоновый сервис работает
4. **Cached Process** - остановлен, кешируется для быстрого запуска
5. **Empty Process** - нет компонентов, убивается первым

### Значения oom_adj

```
Приоритет      oom_adj    Когда убивается

Foreground     0          В крайнем случае
Visible        100-200    Редко
Service        300-400    При нехватке памяти
Cached         900-999    Первыми (LRU порядок)
Empty          1000       Немедленно
```

### Ключевые факторы

-   Состояние Activity (resumed > paused > stopped)
-   Тип сервиса (foreground > background)
-   Выполнение компонентов (BroadcastReceiver, ContentProvider)
-   Bound services наследуют приоритет связанного компонента

---

## Follow-ups

-   How does Android's Low Memory Killer (LMK) decide which processes to terminate first?
-   What's the difference between oom_adj and oom_score_adj in Android process management?
-   How can you optimize your app to avoid being killed by the system during low memory conditions?

## References

-   `https://developer.android.com/guide/components/activities/process-lifecycle` — Process lifecycle
-   `https://developer.android.com/guide/components/services` — Services and process priority
-   `https://developer.android.com/topic/performance/memory` — Memory management

## Related Questions

### Related (Hard)

-   [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Process management
-   [[q-android-memory-management--android--hard]] - Memory management
-   [[q-background-execution-limits--android--hard]] - Background execution

### Prerequisites (Easier)

-   [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
-   [[q-anr-application-not-responding--android--medium]] - Fundamentals
-   [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals

### Related (Hard)

-   [[q-kotlin-context-receivers--kotlin--hard]] - Fundamentals
