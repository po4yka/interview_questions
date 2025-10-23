---
id: 20251016-161705
title: "How To Register Broadcastreceiver To Receive Messages / Как зарегистрировать BroadcastReceiver для получения сообщений"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-what-does-the-lifecycle-library-do--android--medium, q-how-animations-work-in-recyclerview--android--medium, q-why-was-the-lifecycle-library-created--android--hard]
created: 2025-10-15
tags:
  - android
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

1. **Динамическая регистрация в коде** (Runtime registration) - Рекомендуется для большинства случаев
2. **Статическая регистрация в AndroidManifest.xml** - Ограниченное использование из-за ограничений фоновой работы

### 1. Динамическая регистрация (Рекомендуется)

Регистрация BroadcastReceiver программно в Activity, Fragment или Service.

#### Базовая динамическая регистрация

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

        // Регистрация receiver
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        super.onStop()

        // ВАЖНО: Отмена регистрации для предотвращения утечек
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

#### Множественные Broadcast действия

```kotlin
class BatteryActivity : AppCompatActivity() {

    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                Intent.ACTION_BATTERY_LOW -> {
                    showNotification("Батарея разряжена!")
                }
                Intent.ACTION_BATTERY_OKAY -> {
                    showNotification("Уровень батареи в норме")
                }
                Intent.ACTION_POWER_CONNECTED -> {
                    showNotification("Подключено питание")
                }
                Intent.ACTION_POWER_DISCONNECTED -> {
                    showNotification("Питание отключено")
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_battery)

        // Регистрация для нескольких действий
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

#### Пользовательские Broadcasts

```kotlin
// Отправитель
class SenderActivity : AppCompatActivity() {

    fun sendCustomBroadcast() {
        val intent = Intent("com.example.CUSTOM_ACTION").apply {
            putExtra("message", "Привет от отправителя!")
            putExtra("timestamp", System.currentTimeMillis())
        }
        sendBroadcast(intent)
    }
}

// Получатель
class ReceiverActivity : AppCompatActivity() {

    private val customReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val message = intent?.getStringExtra("message")
            val timestamp = intent?.getLongExtra("timestamp", 0L)

            Log.d("ReceiverActivity", "Получено: $message в $timestamp")
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

#### Локальные Broadcasts (Устаревшее, но показано для справки)

```kotlin
// Старый способ - LocalBroadcastManager (Устарел в AndroidX)
class OldLocalBroadcastExample : AppCompatActivity() {

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // Обработка локального broadcast
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

// Современный способ - Используйте LiveData, Flow или EventBus
class ModernLocalEventExample : AppCompatActivity() {

    private val eventBus = MutableSharedFlow<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            eventBus.collect { message ->
                // Обработка сообщения
            }
        }
    }

    fun sendEvent() {
        lifecycleScope.launch {
            eventBus.emit("Привет")
        }
    }
}
```

### 2. Статическая регистрация (Manifest)

Регистрация в AndroidManifest.xml - receiver существует даже когда приложение не запущено.

**Примечание:** Сильно ограничено с Android 8.0 (API 26) для неявных broadcasts.

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application>

        <!-- Статический BroadcastReceiver -->
        <receiver
            android:name=".BootReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- SMS Receiver (требует разрешения) -->
        <receiver
            android:name=".SmsReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.provider.Telephony.SMS_RECEIVED" />
            </intent-filter>
        </receiver>

    </application>

    <!-- Разрешения -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.RECEIVE_SMS" />
</manifest>
```

**Реализация BroadcastReceiver:**

```kotlin
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d("BootReceiver", "Устройство загружено!")

            // Запуск сервиса или планирование работы
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

                Log.d("SmsReceiver", "От: $sender, Сообщение: $body")
                showNotification(context, sender, body)
            }
        }
    }
}
```

### Динамическая vs Статическая регистрация

| Аспект | Динамическая регистрация | Статическая регистрация |
|--------|-------------------------|------------------------|
| **Когда активна** | Только когда компонент жив | Всегда (даже если приложение не запущено) |
| **Регистрация** | В коде (onCreate/onResume) | AndroidManifest.xml |
| **Отмена регистрации** | Требуется (onDestroy/onPause) | Автоматическая |
| **Память** | Более эффективно (регистрируется только при необходимости) | Всегда в памяти |
| **Ограничения Android 8+** | Нет ограничений | Много неявных broadcasts заблокировано |
| **Случаи использования** | Обновления UI, временные слушатели | BOOT_COMPLETED, SMS, будильники |

### Разрешения для BroadcastReceivers

Некоторые broadcasts требуют разрешений:

```xml
<!-- AndroidManifest.xml -->

<!-- Для получения boot completed -->
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- Для получения SMS -->
<uses-permission android:name="android.permission.RECEIVE_SMS" />

<!-- Для проверки состояния сети -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- Для получения состояния батареи -->
<!-- Разрешение не требуется - публичный broadcast -->
```

### Современные альтернативы BroadcastReceiver

#### 1. WorkManager (для фоновой работы)

```kotlin
// Вместо прослушивания BOOT_COMPLETED или изменений сети
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

#### 2. Flow/LiveData (для событий внутри приложения)

```kotlin
// Вместо LocalBroadcastManager
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
                // Обработка события
            }
        }
    }
}
```

#### 3. NetworkCallback (для изменений сети)

```kotlin
val networkCallback = object : ConnectivityManager.NetworkCallback() {
    override fun onAvailable(network: Network) {
        // Сеть доступна
    }

    override fun onLost(network: Network) {
        // Сеть потеряна
    }
}

val connectivityManager = getSystemService(ConnectivityManager::class.java)
val request = NetworkRequest.Builder()
    .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    .build()

connectivityManager.registerNetworkCallback(request, networkCallback)

// Не забудьте отменить регистрацию
connectivityManager.unregisterNetworkCallback(networkCallback)
```

### Лучшие практики

**1. Всегда отменяйте регистрацию динамических receivers**

```kotlin
class MyActivity : AppCompatActivity() {
    private val receiver = MyReceiver()

    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter("ACTION"))
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver) // Предотвращает утечки памяти
    }
}
```

**2. Аккуратно используйте Context-зарегистрированные receivers**

```kotlin
// Используйте viewLifecycleOwner во Fragment
class MyFragment : Fragment() {
    private val receiver = MyReceiver()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Регистрация
        requireContext().registerReceiver(receiver, IntentFilter("ACTION"))
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Отмена регистрации в onDestroyView (не onDestroy)
        requireContext().unregisterReceiver(receiver)
    }
}
```

**3. Обрабатывайте безопасность с разрешениями**

```kotlin
// Отправка broadcast с разрешением
sendBroadcast(
    Intent("com.example.CUSTOM_ACTION"),
    "com.example.permission.CUSTOM_PERMISSION"
)

// Только receivers с этим разрешением получат broadcast
```

**4. Предпочитайте упорядоченные broadcasts для приоритетной обработки**

```kotlin
// Отправка упорядоченного broadcast
sendOrderedBroadcast(
    Intent("ACTION"),
    null, // разрешение
    null, // resultReceiver
    null, // scheduler
    Activity.RESULT_OK,
    null, // initialData
    null  // initialExtras
)

// Receiver с приоритетом в manifest
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="ACTION" />
    </intent-filter>
</receiver>
```

### Резюме

**Динамическая регистрация (Рекомендуется):**
```kotlin
// Регистрация
val filter = IntentFilter("ACTION")
registerReceiver(receiver, filter)

// Отмена регистрации
unregisterReceiver(receiver)
```

**Статическая регистрация:**
```xml
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="ACTION" />
    </intent-filter>
</receiver>
```

**Ключевые моменты:**
- Динамическая регистрация: Регистрируйте в onCreate/onStart, отменяйте регистрацию в onDestroy/onStop
- Статическая регистрация: Ограничена с Android 8.0, используйте для конкретных broadcasts как BOOT_COMPLETED
- Всегда отменяйте регистрацию динамических receivers для предотвращения утечек памяти
- Рассмотрите современные альтернативы: WorkManager, Flow, NetworkCallback
- Используйте соответствующие разрешения для конфиденциальных broadcasts

---

## Related Questions

### Prerequisites (Easier)
- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Related (Medium)
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast

### Advanced (Harder)
- [[q-kotlin-context-receivers--kotlin--hard]] - Broadcast
