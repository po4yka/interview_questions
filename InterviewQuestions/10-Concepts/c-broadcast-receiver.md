---\
id: "20251025-110313"
title: "Broadcast Receiver / Широковещательный Приемник"
aliases: ["Broadcast Receiver", "BroadcastReceiver", "Приемник Трансляций", "Широковещательный Приемник"]
summary: "Android component that responds to system-wide or app-specific broadcast messages"
topic: "android"
subtopics: ["broadcast", "components", "system-events"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-android-ipc", "c-service", "c-android-components", "c-intent", "c-android-manifest"]
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "broadcast", "components", "concept", "difficulty/medium", "system-events"]
---\

# Broadcast Receiver / Широковещательный Приемник

## Summary (EN)

`BroadcastReceiver` is one of Android's four fundamental components that allows applications to receive and respond to broadcast messages from the Android system or other applications. Broadcasts are asynchronous messages sent system-wide or to specific apps, enabling loose coupling between components. Receivers can listen for system events (battery low, connectivity changes) or custom app events.

## Краткое Описание (RU)

`BroadcastReceiver` - это один из четырех фундаментальных компонентов Android, который позволяет приложениям получать и обрабатывать широковещательные сообщения от системы Android или других приложений. Трансляции - это асинхронные сообщения, отправляемые системно или конкретным приложениям, обеспечивающие слабую связанность между компонентами. Приемники могут прослушивать системные события (низкий заряд батареи, изменения подключения) или пользовательские события приложения.

## Key Points (EN)

- **System broadcasts**: Sent by Android system (connectivity, battery, boot)
- **Custom broadcasts**: Sent by your app or other apps
- **Registration types**: Manifest-declared (static) or context-registered (dynamic)
- **Ordered broadcasts**: Delivered to receivers sequentially with priority
- **Local broadcasts**: Delivered only within the app (deprecated, use LiveData/Flow)
- **Background limitations**: Android 8.0+ restricts implicit broadcasts
- **`Lifecycle`**: `Short`-lived, cannot perform long-running operations

## Ключевые Моменты (RU)

- **Системные трансляции**: Отправляются системой Android (подключение, батарея, загрузка)
- **Пользовательские трансляции**: Отправляются вашим приложением или другими приложениями
- **Типы регистрации**: Объявленные в манифесте (статические) или зарегистрированные в контексте (динамические)
- **Упорядоченные трансляции**: Доставляются приемникам последовательно с приоритетом
- **Локальные трансляции**: Доставляются только внутри приложения (устарели, используйте LiveData/Flow)
- **Ограничения фона**: Android 8.0+ ограничивает неявные трансляции
- **Жизненный цикл**: Краткосрочные, не могут выполнять длительные операции

## Creating a Broadcast Receiver

### Basic Receiver Implementation

```kotlin
class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // This method is called when the BroadcastReceiver receives an Intent broadcast
        // WARNING: onReceive() runs on the main thread - keep it short!

        when (intent.action) {
            Intent.ACTION_BATTERY_LOW -> {
                Log.d("Battery", "Battery is low")
                // Handle low battery
            }
            Intent.ACTION_POWER_CONNECTED -> {
                Log.d("Power", "Power connected")
                // Handle power connected
            }
            "com.example.CUSTOM_ACTION" -> {
                val data = intent.getStringExtra("data")
                Log.d("Custom", "Received: $data")
            }
        }
    }
}
```

### Manifest-Declared Receiver (Static)

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application>
        <receiver
            android:name=".MyBroadcastReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <!-- System broadcasts -->
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.AIRPLANE_MODE" />

                <!-- Custom broadcasts -->
                <action android:name="com.example.CUSTOM_ACTION" />
            </intent-filter>
        </receiver>
    </application>

    <!-- Required permissions -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
</manifest>
```

**Characteristics**:
- Receiver exists even when app is not running
- Responds to broadcasts at any time
- Can wake up the app
- Android 8.0+ restrictions on implicit broadcasts

### Context-Registered Receiver (Dynamic)

```kotlin
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            when (intent.action) {
                Intent.ACTION_SCREEN_ON -> {
                    Log.d("Screen", "Screen turned on")
                }
                Intent.ACTION_SCREEN_OFF -> {
                    Log.d("Screen", "Screen turned off")
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Register receiver
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_ON)
            addAction(Intent.ACTION_SCREEN_OFF)
        }
        registerReceiver(receiver, filter)
    }

    override fun onDestroy() {
        // IMPORTANT: Always unregister to prevent memory leaks
        unregisterReceiver(receiver)
        super.onDestroy()
    }
}
```

**Characteristics**:
- Only receives broadcasts while registered
- Must manually register/unregister
- Tied to component lifecycle
- No manifest entry needed
- Preferred for context-dependent broadcasts

## Sending Broadcasts

### Standard Broadcast

```kotlin
// Send broadcast to all registered receivers
fun sendBroadcast(context: Context) {
    val intent = Intent("com.example.CUSTOM_ACTION").apply {
        putExtra("data", "Hello from broadcast")
    }
    context.sendBroadcast(intent)
}

// Send broadcast with permission requirement
fun sendBroadcastWithPermission(context: Context) {
    val intent = Intent("com.example.SECURE_ACTION")
    context.sendBroadcast(
        intent,
        "com.example.permission.RECEIVE_CUSTOM_BROADCAST"
    )
}
```

### Ordered Broadcast

```kotlin
// Receivers process broadcast sequentially based on priority
fun sendOrderedBroadcast(context: Context) {
    val intent = Intent("com.example.ORDERED_ACTION")

    context.sendOrderedBroadcast(
        intent,
        null,  // receiverPermission
        null,  // resultReceiver (final receiver)
        null,  // scheduler
        Activity.RESULT_OK,  // initialCode
        null,  // initialData
        null   // initialExtras
    )
}

// Receiver with priority
class HighPriorityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Process first
        val result = "Processed by high priority"

        // Modify result for next receiver
        resultData = result

        // Or abort broadcast to prevent further receivers
        // abortBroadcast()
    }
}
```

```xml
<!-- Set priority in manifest -->
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="100">
        <action android:name="com.example.ORDERED_ACTION" />
    </intent-filter>
</receiver>
```

### Local Broadcast (Deprecated)

```kotlin
// DEPRECATED: Use LiveData, Flow, or EventBus instead

// Old way (don't use in new code):
val localBroadcastManager = LocalBroadcastManager.getInstance(context)
localBroadcastManager.sendBroadcast(intent)

// Modern alternative with LiveData:
class EventBus {
    private val _events = MutableLiveData<Event>()
    val events: LiveData<Event> = _events

    fun post(event: Event) {
        _events.value = event
    }
}

// Modern alternative with Flow:
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun post(event: Event) {
        _events.emit(event)
    }
}
```

## Common System Broadcasts

### Connectivity Changes

```kotlin
class ConnectivityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val networkInfo = connectivityManager.activeNetworkInfo

        if (networkInfo?.isConnected == true) {
            Log.d("Network", "Connected to ${networkInfo.typeName}")
        } else {
            Log.d("Network", "Disconnected")
        }
    }
}
```

```xml
<receiver android:name=".ConnectivityReceiver">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    </intent-filter>
</receiver>

<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Boot Completed

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Start service or schedule work
            WorkManager.getInstance(context).enqueue(
                OneTimeWorkRequestBuilder<MyWorker>().build()
            )
        }
    }
}
```

```xml
<receiver android:name=".BootReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

### Battery Status

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // Reduce app activity to save battery
            }
            Intent.ACTION_BATTERY_OKAY -> {
                // Resume normal operation
            }
            Intent.ACTION_POWER_CONNECTED -> {
                // Device is charging
            }
            Intent.ACTION_POWER_DISCONNECTED -> {
                // Device unplugged
            }
        }
    }
}
```

## Background Execution Limitations

### Android 8.0 (API 26) Changes

```kotlin
// IMPLICIT broadcasts are restricted in manifest for apps targeting API 26+
// These WON'T work in manifest for API 26+:
// - CONNECTIVITY_CHANGE
// - ACTION_NEW_PICTURE
// - ACTION_NEW_VIDEO

// Solutions:

// 1. Use context-registered receivers
class MyActivity : AppCompatActivity() {
    private val receiver = MyReceiver()

    override fun onResume() {
        super.onResume()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_SCREEN_ON))
    }

    override fun onPause() {
        unregisterReceiver(receiver)
        super.onPause()
    }
}

// 2. Use JobScheduler or WorkManager
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)

// 3. Use explicit broadcasts (these still work)
val intent = Intent(context, MyReceiver::class.java).apply {
    action = "com.example.EXPLICIT_ACTION"
}
context.sendBroadcast(intent)
```

## Long-Running Operations

```kotlin
// DON'T: Long operation in onReceive (will cause ANR)
class BadReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // BAD: Network call on main thread
        val data = makeNetworkCall()  // Will crash or ANR
    }
}

// DO: Use goAsync() for short async work (< 10 seconds)
class GoodReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Perform async work
                val data = fetchData()
                // Process data
            } finally {
                // IMPORTANT: Signal completion
                pendingResult.finish()
            }
        }
    }
}

// BETTER: Delegate to WorkManager for longer operations
class BestReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
            .setInputData(
                workDataOf("data" to intent.getStringExtra("data"))
            )
            .build()

        WorkManager.getInstance(context).enqueue(workRequest)
    }
}

class MyWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        // Perform long-running work here
        return Result.success()
    }
}
```

## Use Cases

### When to Use Broadcast Receivers

- **System event monitoring**: Battery, connectivity, screen state
- **Boot initialization**: Start services on device boot
- **Cross-app communication**: Receive events from other apps
- **Custom in-app events**: Notify components of app-wide changes
- **Time-based events**: Alarm notifications
- **SMS/Call interception**: Monitor incoming messages/calls

### When to Avoid

- **In-app communication**: Use `LiveData`, `Flow`, or EventBus instead
- **`Long`-running tasks**: Use `WorkManager` or Services
- **Frequent updates**: Use direct method calls or reactive patterns
- **Tight coupling**: Consider dependency injection instead

## Trade-offs

**Pros**:
- **Loose coupling**: Components don't need direct references
- **System integration**: Easy to respond to system events
- **Flexibility**: Can enable/disable receivers at runtime
- **Cross-app communication**: Standardized messaging between apps

**Cons**:
- **Security concerns**: Broadcasts can be intercepted or spoofed
- **Performance**: Broadcasting has overhead
- **Background restrictions**: Limited in recent Android versions
- **Memory leaks**: Must unregister dynamic receivers
- **Debugging difficulty**: Hard to trace broadcast flow

## Security Considerations

### Protecting Broadcasts

```kotlin
// 1. Use permissions
context.sendBroadcast(intent, "com.example.permission.RECEIVE_BROADCAST")

// 2. Use explicit intents
val intent = Intent(context, MyReceiver::class.java)
context.sendBroadcast(intent)

// 3. Set package name
val intent = Intent("com.example.ACTION").apply {
    setPackage(context.packageName)  // Only deliver to this app
}

// 4. Use signature-level permissions in manifest
```

```xml
<!-- Define custom permission -->
<permission
    android:name="com.example.permission.RECEIVE_BROADCAST"
    android:protectionLevel="signature" />

<!-- Receiver requires permission -->
<receiver
    android:name=".MyReceiver"
    android:permission="com.example.permission.RECEIVE_BROADCAST">
    <intent-filter>
        <action android:name="com.example.SECURE_ACTION" />
    </intent-filter>
</receiver>
```

## Best Practices

1. **Unregister dynamic receivers**: Always call `unregisterReceiver()` to prevent leaks
2. **Keep onReceive() short**: Under 10 seconds, preferably instant
3. **Use `WorkManager`**: For background work triggered by broadcasts
4. **Prefer explicit intents**: More secure and efficient
5. **Check Android version**: Handle API level differences
6. **Use appropriate registration**: Manifest for always-on, dynamic for context-dependent
7. **Handle null cases**: `Intent` extras may be null
8. **Add permissions**: Declare required permissions in manifest

## Related Concepts

- [[c-lifecycle]]
- [[c-permissions]]
- [[c-memory-management]]
- [[c-coroutines]]

## References

- [BroadcastReceiver Documentation](https://developer.android.com/reference/android/content/BroadcastReceiver)
- [Broadcasts Overview](https://developer.android.com/guide/components/broadcasts)
- [Background Execution Limits](https://developer.android.com/about/versions/oreo/background)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Security with Broadcasts](https://developer.android.com/guide/components/broadcasts#security)
