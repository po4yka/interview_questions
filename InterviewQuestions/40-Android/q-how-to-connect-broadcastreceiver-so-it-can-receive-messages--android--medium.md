---
id: "20251015082237448"
title: "How To Connect Broadcastreceiver So It Can Receive Messages / Как подключить BroadcastReceiver для получения сообщений"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
---
# How to connect BroadcastReceiver so it can receive messages?

## Answer (EN)
BroadcastReceiver can be registered in two ways: statically in AndroidManifest.xml or dynamically in code. Each method has different use cases and lifecycle behaviors.

### Method 1: Static Registration (Manifest)

Register receiver in AndroidManifest.xml - survives app lifecycle:

```kotlin
// Step 1: Create BroadcastReceiver class
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                Log.d("BootReceiver", "Device booted")
                // Start service or schedule work
                context.startService(Intent(context, MyService::class.java))
            }
        }
    }
}
```

```xml
<!-- Step 2: Declare in AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Required permissions -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

    <application>
        <!-- Register BroadcastReceiver -->
        <receiver
            android:name=".BootReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
```

**Characteristics**:
-  Receives broadcasts even when app is not running
-  Survives app restarts
-  Limited in Android 8.0+ (background execution limits)
-  Cannot be enabled/disabled at runtime easily

### Method 2: Dynamic Registration (Code)

Register receiver in code - lifecycle tied to component:

```kotlin
class MainActivity : AppCompatActivity() {

    // Step 1: Create BroadcastReceiver
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            val batteryPct = level / scale.toFloat() * 100

            Log.d("Battery", "Battery level: $batteryPct%")
            updateBatteryUI(batteryPct)
        }
    }

    override fun onStart() {
        super.onStart()

        // Step 2: Create IntentFilter
        val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)

        // Step 3: Register receiver
        registerReceiver(batteryReceiver, filter)
    }

    override fun onStop() {
        super.onStop()

        // Step 4: Unregister receiver (IMPORTANT!)
        unregisterReceiver(batteryReceiver)
    }

    private fun updateBatteryUI(percentage: Float) {
        // Update UI with battery level
    }
}
```

**Characteristics**:
-  Works in Android 8.0+ without restrictions
-  Can be enabled/disabled dynamically
-  Only receives broadcasts while registered
-  Must manually unregister to avoid leaks

### Method 3: Context-Registered Receiver (ContextCompat)

Modern approach with automatic unregistration:

```kotlin
class MainActivity : AppCompatActivity() {

    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val connectivityManager = context.getSystemService(ConnectivityManager::class.java)
            val network = connectivityManager.activeNetwork
            val isConnected = network != null

            Log.d("Network", "Connected: $isConnected")
            updateNetworkUI(isConnected)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Register with lifecycle awareness
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
            registerReceiver(networkReceiver, filter)
        } else {
            // Use WorkManager or other alternatives for older APIs
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(networkReceiver)
        } catch (e: IllegalArgumentException) {
            // Receiver was not registered
        }
    }

    private fun updateNetworkUI(isConnected: Boolean) {
        // Update UI
    }
}
```

### Method 4: LocalBroadcastManager (Deprecated)

For internal app broadcasts only:

```kotlin
// WARNING: Deprecated - use LiveData or Flow instead
class SenderActivity : AppCompatActivity() {

    fun sendLocalBroadcast() {
        val intent = Intent("com.example.CUSTOM_ACTION")
        intent.putExtra("data", "Hello")
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
    }
}

class ReceiverActivity : AppCompatActivity() {

    private val localReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val data = intent.getStringExtra("data")
            Log.d("Receiver", "Received: $data")
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter("com.example.CUSTOM_ACTION")
        LocalBroadcastManager.getInstance(this)
            .registerReceiver(localReceiver, filter)
    }

    override fun onStop() {
        super.onStop()
        LocalBroadcastManager.getInstance(this)
            .unregisterReceiver(localReceiver)
    }
}
```

### Common System Broadcasts

```kotlin
class SystemBroadcastReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            // Device events
            Intent.ACTION_BOOT_COMPLETED -> handleBootCompleted()
            Intent.ACTION_POWER_CONNECTED -> handlePowerConnected()
            Intent.ACTION_POWER_DISCONNECTED -> handlePowerDisconnected()

            // Connectivity
            ConnectivityManager.CONNECTIVITY_ACTION -> handleConnectivityChange(context)
            WifiManager.WIFI_STATE_CHANGED_ACTION -> handleWifiStateChange()

            // Battery
            Intent.ACTION_BATTERY_LOW -> handleBatteryLow()
            Intent.ACTION_BATTERY_OKAY -> handleBatteryOkay()

            // Screen
            Intent.ACTION_SCREEN_ON -> handleScreenOn()
            Intent.ACTION_SCREEN_OFF -> handleScreenOff()

            // Time
            Intent.ACTION_TIME_TICK -> handleTimeTick()
            Intent.ACTION_TIMEZONE_CHANGED -> handleTimezoneChange()

            // Package
            Intent.ACTION_PACKAGE_ADDED -> handlePackageAdded(intent)
            Intent.ACTION_PACKAGE_REMOVED -> handlePackageRemoved(intent)
        }
    }

    private fun handleBootCompleted() {
        // Device finished booting
    }

    private fun handleConnectivityChange(context: Context) {
        val cm = context.getSystemService(ConnectivityManager::class.java)
        val network = cm.activeNetwork
        // Check network status
    }
}
```

### Multiple Intent Filters

```xml
<!-- Manifest registration with multiple actions -->
<receiver
    android:name=".MultiActionReceiver"
    android:enabled="true"
    android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.POWER_CONNECTED" />
        <action android:name="android.intent.action.POWER_DISCONNECTED" />
        <action android:name="android.intent.action.BATTERY_LOW" />
    </intent-filter>
</receiver>
```

```kotlin
// Dynamic registration with multiple actions
override fun onStart() {
    super.onStart()

    val filter = IntentFilter().apply {
        addAction(Intent.ACTION_POWER_CONNECTED)
        addAction(Intent.ACTION_POWER_DISCONNECTED)
        addAction(Intent.ACTION_BATTERY_LOW)
    }

    registerReceiver(powerReceiver, filter)
}
```

### Ordered Broadcasts

Receivers process broadcast in priority order:

```xml
<!-- Higher priority processes first -->
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="com.example.CUSTOM_ACTION" />
    </intent-filter>
</receiver>

<receiver android:name=".LowPriorityReceiver">
    <intent-filter android:priority="1">
        <action android:name="com.example.CUSTOM_ACTION" />
    </intent-filter>
</receiver>
```

```kotlin
class HighPriorityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Process first
        val result = processData(intent)

        // Optionally abort broadcast (lower priority won't receive)
        if (result.shouldAbort) {
            abortBroadcast()
        }

        // Or modify and pass along
        setResultData("Modified data")
    }
}

// Sending ordered broadcast
fun sendOrderedBroadcast() {
    val intent = Intent("com.example.CUSTOM_ACTION")
    sendOrderedBroadcast(
        intent,
        null, // Permission
        null, // Result receiver
        null, // Scheduler
        Activity.RESULT_OK,
        null, // Initial data
        null  // Initial extras
    )
}
```

### Exported vs Not Exported

```xml
<!-- Receives broadcasts from other apps -->
<receiver
    android:name=".PublicReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.PUBLIC_ACTION" />
    </intent-filter>
</receiver>

<!-- Only receives broadcasts from this app -->
<receiver
    android:name=".PrivateReceiver"
    android:exported="false">
    <intent-filter>
        <action android:name="com.example.PRIVATE_ACTION" />
    </intent-filter>
</receiver>
```

### Permission-Protected Broadcasts

```xml
<!-- Define custom permission -->
<permission
    android:name="com.example.app.SEND_CUSTOM_BROADCAST"
    android:protectionLevel="signature" />

<!-- Receiver requires permission to receive -->
<receiver
    android:name=".ProtectedReceiver"
    android:permission="com.example.app.SEND_CUSTOM_BROADCAST">
    <intent-filter>
        <action android:name="com.example.PROTECTED_ACTION" />
    </intent-filter>
</receiver>
```

```kotlin
// Sending app must have permission
fun sendProtectedBroadcast() {
    val intent = Intent("com.example.PROTECTED_ACTION")
    sendBroadcast(intent, "com.example.app.SEND_CUSTOM_BROADCAST")
}
```

### Best Practices

```kotlin
class BestPracticesActivity : AppCompatActivity() {

    private var isReceiverRegistered = false

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Handle broadcast
        }
    }

    override fun onStart() {
        super.onStart()
        registerReceiverSafely()
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiverSafely()
    }

    private fun registerReceiverSafely() {
        if (!isReceiverRegistered) {
            val filter = IntentFilter("com.example.ACTION")
            registerReceiver(receiver, filter)
            isReceiverRegistered = true
        }
    }

    private fun unregisterReceiverSafely() {
        if (isReceiverRegistered) {
            try {
                unregisterReceiver(receiver)
                isReceiverRegistered = false
            } catch (e: IllegalArgumentException) {
                Log.e("Receiver", "Receiver was not registered", e)
            }
        }
    }
}
```

### Comparison Table

| Method | When Receives | Lifecycle | Use Case |
|--------|--------------|-----------|----------|
| Manifest | Always (even app closed) | App lifetime | System events |
| Dynamic | Only when registered | Component lifetime | UI updates |
| LocalBroadcastManager | Only when registered | Component lifetime | Internal communication (deprecated) |
| WorkManager | Scheduled | Flexible | Background work (preferred) |

### Modern Alternatives

For new code, consider these instead of BroadcastReceiver:

```kotlin
// Alternative 1: LiveData for internal communication
class DataRepository {
    private val _updates = MutableLiveData<Data>()
    val updates: LiveData<Data> = _updates

    fun updateData(data: Data) {
        _updates.postValue(data)
    }
}

// Alternative 2: WorkManager for background tasks
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()
WorkManager.getInstance(context).enqueue(workRequest)

// Alternative 3: Flow for reactive streams
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}
```

## Ответ (RU)
Подключение BroadcastReceiver в Android состоит из двух основных шагов: создание самого ресивера и его регистрация. Ресивер можно зарегистрировать как статически в манифесте, так и динамически в коде. Создание BroadcastReceiver: создайте класс, который наследуется от BroadcastReceiver и переопределите метод onReceive. Регистрация ресивера: статическая регистрация в манифесте - добавьте элемент <receiver> с соответствующим intent-filter. Динамическая регистрация в коде - используйте registerReceiver и unregisterReceiver в соответствующих жизненных циклах активности.

## Related Topics
- Intent and IntentFilter
- AndroidManifest.xml
- System broadcasts
- WorkManager (modern alternative)
- LocalBroadcastManager

---

## Related Questions

### Prerequisites (Easier)
- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Related (Medium)
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast

### Advanced (Harder)
- [[q-kotlin-context-receivers--kotlin--hard]] - Broadcast
