---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# How to register BroadcastReceiver to receive messages?

## Answer (EN)
There are **two ways** to register a BroadcastReceiver in Android:

1. **Dynamically in code** (Runtime registration) - Recommended for most cases
2. **Statically in AndroidManifest.xml** - Limited use due to background execution limits

### 1. Dynamic Registration (Recommended)

Register BroadcastReceiver programmatically in Activity, Fragment, or Service.

#### Basic Dynamic Registration

```kotlin
class MainActivity : AppCompatActivity() {

    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val action = intent?.action
            if (action == ConnectivityManager.CONNECTIVITY_ACTION) {
                val isConnected = isNetworkAvailable(context)
                Toast.makeText(context, "Network: $isConnected", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onStart() {
        super.onStart()

        // Register receiver
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        super.onStop()

        // IMPORTANT: Unregister to prevent leaks
        unregisterReceiver(networkReceiver)
    }

    private fun isNetworkAvailable(context: Context?): Boolean {
        val cm = context?.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
        val network = cm?.activeNetwork
        val capabilities = cm?.getNetworkCapabilities(network)
        return capabilities != null
    }
}
```

#### Multiple Broadcast Actions

```kotlin
class BatteryActivity : AppCompatActivity() {

    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                Intent.ACTION_BATTERY_LOW -> {
                    showNotification("Battery is low!")
                }
                Intent.ACTION_BATTERY_OKAY -> {
                    showNotification("Battery level is okay")
                }
                Intent.ACTION_POWER_CONNECTED -> {
                    showNotification("Power connected")
                }
                Intent.ACTION_POWER_DISCONNECTED -> {
                    showNotification("Power disconnected")
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_battery)

        // Register for multiple actions
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_LOW)
            addAction(Intent.ACTION_BATTERY_OKAY)
            addAction(Intent.ACTION_POWER_CONNECTED)
            addAction(Intent.ACTION_POWER_DISCONNECTED)
        }

        registerReceiver(batteryReceiver, filter)
    }

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(batteryReceiver)
    }
}
```

#### Custom Broadcasts

```kotlin
// Sender
class SenderActivity : AppCompatActivity() {

    fun sendCustomBroadcast() {
        val intent = Intent("com.example.CUSTOM_ACTION").apply {
            putExtra("message", "Hello from sender!")
            putExtra("timestamp", System.currentTimeMillis())
        }
        sendBroadcast(intent)
    }
}

// Receiver
class ReceiverActivity : AppCompatActivity() {

    private val customReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val message = intent?.getStringExtra("message")
            val timestamp = intent?.getLongExtra("timestamp", 0L)

            Log.d("ReceiverActivity", "Received: $message at $timestamp")
            updateUI(message)
        }
    }

    override fun onResume() {
        super.onResume()

        val filter = IntentFilter("com.example.CUSTOM_ACTION")
        registerReceiver(customReceiver, filter)
    }

    override fun onPause() {
        super.onPause()
        unregisterReceiver(customReceiver)
    }
}
```

#### Local Broadcasts (Deprecated but shown for reference)

```kotlin
// Old way - LocalBroadcastManager (Deprecated in AndroidX)
class OldLocalBroadcastExample : AppCompatActivity() {

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // Handle local broadcast
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        LocalBroadcastManager.getInstance(this)
            .registerReceiver(receiver, IntentFilter("local_action"))
    }

    override fun onDestroy() {
        super.onDestroy()
        LocalBroadcastManager.getInstance(this).unregisterReceiver(receiver)
    }
}

// Modern way - Use LiveData, Flow, or EventBus instead
class ModernLocalEventExample : AppCompatActivity() {

    private val eventBus = MutableSharedFlow<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            eventBus.collect { message ->
                // Handle message
            }
        }
    }

    fun sendEvent() {
        lifecycleScope.launch {
            eventBus.emit("Hello")
        }
    }
}
```

### 2. Static Registration (Manifest)

Register in AndroidManifest.xml - receiver exists even when app is not running.

**Note:** Heavily restricted since Android 8.0 (API 26) for implicit broadcasts.

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application>

        <!-- Static BroadcastReceiver -->
        <receiver
            android:name=".BootReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- SMS Receiver (requires permission) -->
        <receiver
            android:name=".SmsReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.provider.Telephony.SMS_RECEIVED" />
            </intent-filter>
        </receiver>

    </application>

    <!-- Permissions -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.RECEIVE_SMS" />
</manifest>
```

**BroadcastReceiver Implementation:**

```kotlin
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d("BootReceiver", "Device booted!")

            // Start a service or schedule work
            val serviceIntent = Intent(context, MyService::class.java)
            context?.startService(serviceIntent)
        }
    }
}

class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == "android.provider.Telephony.SMS_RECEIVED") {
            val bundle = intent.extras
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)

            messages.forEach { message ->
                val sender = message.displayOriginatingAddress
                val body = message.messageBody

                Log.d("SmsReceiver", "From: $sender, Message: $body")
                showNotification(context, sender, body)
            }
        }
    }
}
```

### Dynamic vs Static Registration

| Aspect | Dynamic Registration | Static Registration |
|--------|---------------------|---------------------|
| **When active** | Only when component is alive | Always (even app not running) |
| **Registration** | In code (onCreate/onResume) | AndroidManifest.xml |
| **Unregistration** | Required (onDestroy/onPause) | Automatic |
| **Memory** | More efficient (registered only when needed) | Always in memory |
| **Android 8+ restrictions** | No restrictions | Many implicit broadcasts blocked |
| **Use cases** | UI updates, temporary listeners | BOOT_COMPLETED, SMS, alarms |

### Permissions for BroadcastReceivers

Some broadcasts require permissions:

```xml
<!-- AndroidManifest.xml -->

<!-- To receive boot completed -->
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- To receive SMS -->
<uses-permission android:name="android.permission.RECEIVE_SMS" />

<!-- To check network state -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- To receive battery state -->
<!-- No permission needed - public broadcast -->
```

### Modern Alternatives to BroadcastReceiver

#### 1. WorkManager (for background work)

```kotlin
// Instead of listening for BOOT_COMPLETED or network changes
val workRequest = PeriodicWorkRequestBuilder<MyWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()
).build()

WorkManager.getInstance(context).enqueue(workRequest)
```

#### 2. Flow/LiveData (for in-app events)

```kotlin
// Instead of LocalBroadcastManager
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}

// ViewModel
class MyViewModel(private val eventBus: EventBus) : ViewModel() {
    init {
        viewModelScope.launch {
            eventBus.events.collect { event ->
                // Handle event
            }
        }
    }
}
```

#### 3. NetworkCallback (for network changes)

```kotlin
val networkCallback = object : ConnectivityManager.NetworkCallback() {
    override fun onAvailable(network: Network) {
        // Network available
    }

    override fun onLost(network: Network) {
        // Network lost
    }
}

val connectivityManager = getSystemService(ConnectivityManager::class.java)
val request = NetworkRequest.Builder()
    .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    .build()

connectivityManager.registerNetworkCallback(request, networkCallback)

// Don't forget to unregister
connectivityManager.unregisterNetworkCallback(networkCallback)
```

### Best Practices

**1. Always unregister dynamic receivers**

```kotlin
class MyActivity : AppCompatActivity() {
    private val receiver = MyReceiver()

    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter("ACTION"))
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver) // Prevent memory leaks
    }
}
```

**2. Use Context-registered receivers carefully**

```kotlin
// Use viewLifecycleOwner in Fragments
class MyFragment : Fragment() {
    private val receiver = MyReceiver()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Register
        requireContext().registerReceiver(receiver, IntentFilter("ACTION"))
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Unregister in onDestroyView (not onDestroy)
        requireContext().unregisterReceiver(receiver)
    }
}
```

**3. Handle security with permissions**

```kotlin
// Send broadcast with permission
sendBroadcast(
    Intent("com.example.CUSTOM_ACTION"),
    "com.example.permission.CUSTOM_PERMISSION"
)

// Only receivers with this permission will receive it
```

**4. Prefer ordered broadcasts for priority handling**

```kotlin
// Send ordered broadcast
sendOrderedBroadcast(
    Intent("ACTION"),
    null, // permission
    null, // resultReceiver
    null, // scheduler
    Activity.RESULT_OK,
    null, // initialData
    null  // initialExtras
)

// Receiver with priority in manifest
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="ACTION" />
    </intent-filter>
</receiver>
```

### Summary

**Dynamic Registration (Recommended):**
```kotlin
// Register
val filter = IntentFilter("ACTION")
registerReceiver(receiver, filter)

// Unregister
unregisterReceiver(receiver)
```

**Static Registration:**
```xml
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="ACTION" />
    </intent-filter>
</receiver>
```

**Key Points:**
- Dynamic registration: Register in onCreate/onStart, unregister in onDestroy/onStop
- Static registration: Limited since Android 8.0, use for specific broadcasts like BOOT_COMPLETED
- Always unregister dynamic receivers to prevent memory leaks
- Consider modern alternatives: WorkManager, Flow, NetworkCallback
- Use appropriate permissions for sensitive broadcasts

## Ответ (RU)
Существует **два способа** регистрации BroadcastReceiver в Android:

### 1. Динамическая регистрация (Рекомендуется)

Регистрация в коде программно:

```kotlin
class MainActivity : AppCompatActivity() {

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // Обработка broadcast
        }
    }

    override fun onStart() {
        super.onStart()

        // Регистрация
        val filter = IntentFilter("com.example.ACTION")
        registerReceiver(receiver, filter)
    }

    override fun onStop() {
        super.onStop()

        // ВАЖНО: Отмена регистрации для предотвращения утечек
        unregisterReceiver(receiver)
    }
}
```

### 2. Статическая регистрация (Manifest)

Регистрация в AndroidManifest.xml:

```xml
<receiver
    android:name=".MyReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Обработка broadcast
    }
}
```

### Сравнение

| Динамическая | Статическая |
|-------------|-------------|
| Активна только когда компонент жив | Всегда активна |
| Регистрация в коде | Регистрация в Manifest |
| Требуется отмена регистрации | Автоматическая |
| Нет ограничений Android 8+ | Много ограничений |
| Для UI обновлений | Для BOOT_COMPLETED, SMS |

### Лучшие практики

1. **Всегда отменяйте регистрацию динамических receivers**
2. **Используйте viewLifecycleOwner во Fragment**
3. **Для фоновой работы используйте WorkManager вместо BroadcastReceiver**
4. **Для событий внутри приложения используйте Flow/LiveData**

### Современные альтернативы

- **WorkManager** - для фоновой работы
- **Flow/LiveData** - для событий внутри приложения
- **NetworkCallback** - для изменений сети

---

## Related Questions

### Prerequisites (Easier)
- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Related (Medium)
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast

### Advanced (Harder)
- [[q-kotlin-context-receivers--kotlin--hard]] - Broadcast
