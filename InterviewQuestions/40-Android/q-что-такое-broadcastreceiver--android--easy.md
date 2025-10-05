---
id: 202510031417005
title: "What is BroadcastReceiver"
question_ru: "Что такое BroadcastReceiver"
question_en: "Что такое BroadcastReceiver"
topic: android
moc: moc-android
status: draft
difficulty: easy
tags:
  - BroadcastReceiver
  - Android Components
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/44
---

# What is BroadcastReceiver

## English Answer

**BroadcastReceiver** is an application component that allows you to listen to and react to broadcast messages from other applications or from the system itself. These messages can notify about various events, such as network state changes, low battery level, language changes on the device, etc.

### Key Concepts

#### What is a Broadcast?
A broadcast is a message sent system-wide that any app can receive if it registers to listen for that particular broadcast.

```kotlin
// Sending a broadcast
val intent = Intent("com.example.CUSTOM_ACTION")
intent.putExtra("data", "some_value")
sendBroadcast(intent)
```

### Types of Broadcasts

#### 1. System Broadcasts
Built-in broadcasts from the Android system:

```kotlin
// Common system broadcasts
Intent.ACTION_BOOT_COMPLETED    // Device finished booting
Intent.ACTION_BATTERY_LOW       // Battery is low
Intent.ACTION_POWER_CONNECTED   // Power connected
Intent.ACTION_AIRPLANE_MODE_CHANGED  // Airplane mode changed
Intent.ACTION_TIME_TICK         // Every minute time change
```

#### 2. Custom Broadcasts
Application-defined broadcasts:

```kotlin
// Sending custom broadcast
val intent = Intent("com.example.myapp.DATA_UPDATED")
intent.putExtra("timestamp", System.currentTimeMillis())
sendBroadcast(intent)
```

### Creating a BroadcastReceiver

#### Basic Implementation

```kotlin
class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                Log.d("Receiver", "Battery is low!")
                // Handle low battery
            }
            Intent.ACTION_POWER_CONNECTED -> {
                Log.d("Receiver", "Power connected!")
                // Handle power connected
            }
            "com.example.CUSTOM_ACTION" -> {
                val data = intent.getStringExtra("data")
                Log.d("Receiver", "Received: $data")
            }
        }
    }
}
```

### Registration Methods

#### 1. Static Registration (Manifest)
Register in AndroidManifest.xml - receiver is always active:

```xml
<receiver
    android:name=".MyBroadcastReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
        <action android:name="android.intent.action.BATTERY_LOW"/>
    </intent-filter>
</receiver>
```

**Note**: Starting from Android 8.0 (API 26), most implicit broadcasts cannot be declared in manifest. Use dynamic registration instead.

#### 2. Dynamic Registration (Code)
Register programmatically - receiver is active only when registered:

```kotlin
class MainActivity : AppCompatActivity() {

    private val receiver = MyBroadcastReceiver()

    override fun onStart() {
        super.onStart()
        // Register receiver
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_LOW)
            addAction(Intent.ACTION_POWER_CONNECTED)
        }
        registerReceiver(receiver, filter)
    }

    override fun onStop() {
        super.onStop()
        // Unregister receiver to avoid memory leaks
        unregisterReceiver(receiver)
    }
}
```

### Broadcast Types

#### 1. Normal Broadcasts
Delivered to all registered receivers asynchronously:

```kotlin
// Send normal broadcast
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)
```

#### 2. Ordered Broadcasts
Delivered to receivers one at a time, in priority order:

```kotlin
// Send ordered broadcast
val intent = Intent("com.example.ACTION")
sendOrderedBroadcast(intent, null)

// Receiver with priority
val filter = IntentFilter("com.example.ACTION")
filter.priority = 100  // Higher priority
registerReceiver(receiver, filter)
```

#### 3. Local Broadcasts
Only within the same application (deprecated, use LiveData or event bus instead):

```kotlin
// Using LocalBroadcastManager (deprecated)
LocalBroadcastManager.getInstance(this).sendBroadcast(intent)

// Modern alternative: LiveData
class DataRepository {
    private val _dataUpdated = MutableLiveData<String>()
    val dataUpdated: LiveData<String> = _dataUpdated

    fun updateData(data: String) {
        _dataUpdated.postValue(data)
    }
}
```

### Practical Examples

#### Battery Monitor Example

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // Show notification about low battery
                showNotification(context, "Battery Low", "Please charge your device")
            }
            Intent.ACTION_BATTERY_OKAY -> {
                // Battery level is okay now
                Log.d("Battery", "Battery level is okay")
            }
        }
    }

    private fun showNotification(context: Context?, title: String, message: String) {
        // Create and show notification
    }
}

// In Activity
class MainActivity : AppCompatActivity() {
    private val batteryReceiver = BatteryReceiver()

    override fun onResume() {
        super.onResume()
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_LOW)
            addAction(Intent.ACTION_BATTERY_OKAY)
        }
        registerReceiver(batteryReceiver, filter)
    }

    override fun onPause() {
        super.onPause()
        unregisterReceiver(batteryReceiver)
    }
}
```

#### Network Change Example

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            val connectivityManager = context?.getSystemService(Context.CONNECTIVITY_SERVICE)
                as ConnectivityManager
            val networkInfo = connectivityManager.activeNetworkInfo

            if (networkInfo?.isConnected == true) {
                Log.d("Network", "Connected to ${networkInfo.typeName}")
            } else {
                Log.d("Network", "No internet connection")
            }
        }
    }
}
```

### Important Considerations

#### 1. Lifecycle
```kotlin
// BroadcastReceiver lifecycle is very short
class QuickReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // ⚠️ This method must complete quickly (< 10 seconds)
        // ❌ Don't perform long operations here
        // ✅ Use WorkManager or Service for long tasks

        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Perform background work
                performWork()
            } finally {
                pendingResult.finish()
            }
        }
    }
}
```

#### 2. Security

```kotlin
// Secure broadcast - only your app can receive
val intent = Intent("com.example.SECURE_ACTION")
intent.setPackage(packageName)  // Limit to your app
sendBroadcast(intent)

// Require permission to receive
sendBroadcast(intent, "com.example.permission.CUSTOM")
```

#### 3. Modern Alternatives

- **WorkManager**: For deferrable background tasks
- **LiveData/StateFlow**: For in-app event communication
- **JobScheduler**: For scheduled tasks
- **Foreground Services**: For user-visible background work

### Best Practices

1. **Always unregister dynamic receivers** to avoid memory leaks
2. **Keep onReceive() fast** (< 10 seconds)
3. **Use goAsync()** for slightly longer operations
4. **Prefer context-registered receivers** over manifest for most cases
5. **Use WorkManager** instead of broadcasts for background work
6. **Be aware of battery impact** when listening to frequent broadcasts

## Russian Answer

**BroadcastReceiver** — это компонент приложения, который позволяет вам слушать и реагировать на широковещательные сообщения из других приложений или из самой системы. Эти сообщения могут сообщать о различных событиях, таких как:

- Изменение состояния сети
- Низкий уровень заряда батареи
- Смена языка в устройстве
- Завершение загрузки устройства
- Изменение режима полета
- Получение SMS-сообщения
- Подключение зарядного устройства

BroadcastReceiver позволяет вашему приложению реагировать на эти системные события и выполнять соответствующие действия, даже если приложение не запущено.
