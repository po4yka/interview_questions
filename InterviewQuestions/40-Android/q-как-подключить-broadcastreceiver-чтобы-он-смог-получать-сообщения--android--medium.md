---
id: 202510031417011
title: "How to register BroadcastReceiver to receive messages"
question_ru: "Как подключить BroadcastReceiver чтобы он смог получать сообщения"
question_en: "Как подключить BroadcastReceiver чтобы он смог получать сообщения"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - BroadcastReceiver
  - AndroidManifest.xml
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/262
---

# How to register BroadcastReceiver to receive messages

## English Answer

Connecting a BroadcastReceiver in Android consists of two main steps: creating the receiver itself and registering it. The receiver can be registered either statically in the manifest or dynamically in code.

### Step 1: Create BroadcastReceiver

First, create a simple BroadcastReceiver that will react to specific events (e.g., receiving SMS):

```kotlin
class SmsReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            "android.provider.Telephony.SMS_RECEIVED" -> {
                Log.d("SmsReceiver", "SMS received!")
                // Handle SMS
                handleSmsReceived(intent)
            }
            "com.example.CUSTOM_ACTION" -> {
                val data = intent.getStringExtra("data")
                Log.d("SmsReceiver", "Custom action received: $data")
            }
        }
    }

    private fun handleSmsReceived(intent: Intent) {
        // Process SMS data
        val bundle = intent.extras
        // Extract SMS details...
    }
}
```

### Step 2: Register the Receiver

There are two ways to register a BroadcastReceiver:

## Method 1: Static Registration (Manifest)

Register the receiver in `AndroidManifest.xml`. This is convenient when you want the receiver to always be active and listen for specific system events (e.g., device reboot or SMS reception).

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <!-- Declare required permissions -->
    <uses-permission android:name="android.permission.RECEIVE_SMS"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>

    <application>
        <!-- Register BroadcastReceiver -->
        <receiver
            android:name=".SmsReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <!-- Listen for SMS -->
                <action android:name="android.provider.Telephony.SMS_RECEIVED"/>
                <!-- Listen for boot complete -->
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>
```

### Important Notes for Manifest Registration

**Starting from Android 8.0 (API 26)**, most implicit broadcasts cannot be declared in the manifest. Exceptions include:

```xml
<!-- These broadcasts still work in manifest (Android 8.0+) -->
<receiver android:name=".BootReceiver" android:exported="true">
    <intent-filter>
        <!-- Boot completed - still allowed -->
        <action android:name="android.intent.action.BOOT_COMPLETED"/>

        <!-- Timezone changed - still allowed -->
        <action android:name="android.intent.action.TIMEZONE_CHANGED"/>

        <!-- Locale changed - still allowed -->
        <action android:name="android.intent.action.LOCALE_CHANGED"/>
    </intent-filter>
</receiver>

<!-- Most other broadcasts require dynamic registration -->
```

## Method 2: Dynamic Registration (Code)

Sometimes you need to register the receiver only during the execution of a specific Activity or Service. In this case, use dynamic registration.

```kotlin
class MainActivity : AppCompatActivity() {

    private val customReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                Intent.ACTION_BATTERY_LOW -> {
                    Toast.makeText(context, "Battery Low!", Toast.LENGTH_SHORT).show()
                }
                Intent.ACTION_POWER_CONNECTED -> {
                    Toast.makeText(context, "Power Connected!", Toast.LENGTH_SHORT).show()
                }
                "com.example.CUSTOM_ACTION" -> {
                    val data = intent.getStringExtra("data")
                    updateUI(data)
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()

        // Create IntentFilter for actions we want to receive
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_LOW)
            addAction(Intent.ACTION_POWER_CONNECTED)
            addAction("com.example.CUSTOM_ACTION")
        }

        // Register receiver
        registerReceiver(customReceiver, filter)

        Log.d("MainActivity", "Receiver registered")
    }

    override fun onStop() {
        super.onStop()

        // IMPORTANT: Unregister to avoid memory leaks
        unregisterReceiver(customReceiver)

        Log.d("MainActivity", "Receiver unregistered")
    }

    private fun updateUI(data: String?) {
        // Update UI with received data
    }
}
```

### Dynamic Registration with Context Registered Receiver (Android 13+)

```kotlin
class ModernActivity : AppCompatActivity() {

    private val batteryReceiver = BatteryReceiver()

    override fun onResume() {
        super.onResume()

        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_CHANGED)
        }

        // Modern approach for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(
                batteryReceiver,
                filter,
                Context.RECEIVER_NOT_EXPORTED  // Security flag
            )
        } else {
            registerReceiver(batteryReceiver, filter)
        }
    }

    override fun onPause() {
        super.onPause()
        unregisterReceiver(batteryReceiver)
    }
}

class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val level = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = intent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryPct = level / scale.toFloat() * 100
        Log.d("Battery", "Battery level: $batteryPct%")
    }
}
```

### Complete Example: Network Change Receiver

```kotlin
// 1. Create Receiver
class NetworkChangeReceiver : BroadcastReceiver() {

    interface NetworkStateListener {
        fun onNetworkAvailable()
        fun onNetworkLost()
    }

    var listener: NetworkStateListener? = null

    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            val connectivityManager = context?.getSystemService(Context.CONNECTIVITY_SERVICE)
                as? ConnectivityManager

            val isConnected = connectivityManager?.activeNetworkInfo?.isConnected == true

            if (isConnected) {
                listener?.onNetworkAvailable()
            } else {
                listener?.onNetworkLost()
            }
        }
    }
}

// 2. Use in Activity
class MainActivity : AppCompatActivity(), NetworkChangeReceiver.NetworkStateListener {

    private val networkReceiver = NetworkChangeReceiver()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Set listener
        networkReceiver.listener = this
    }

    override fun onStart() {
        super.onStart()

        // Register receiver
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        super.onStop()

        // Unregister receiver
        try {
            unregisterReceiver(networkReceiver)
        } catch (e: IllegalArgumentException) {
            // Receiver was already unregistered
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        networkReceiver.listener = null
    }

    // NetworkStateListener implementation
    override fun onNetworkAvailable() {
        runOnUiThread {
            Toast.makeText(this, "Network Available", Toast.LENGTH_SHORT).show()
            statusTextView.text = "Online"
        }
    }

    override fun onNetworkLost() {
        runOnUiThread {
            Toast.makeText(this, "Network Lost", Toast.LENGTH_SHORT).show()
            statusTextView.text = "Offline"
        }
    }
}
```

### Sending Custom Broadcasts

```kotlin
class DataUpdateService : Service() {

    fun notifyDataUpdated(data: String) {
        // Create intent with custom action
        val intent = Intent("com.example.DATA_UPDATED").apply {
            putExtra("data", data)
            putExtra("timestamp", System.currentTimeMillis())
        }

        // Send broadcast
        sendBroadcast(intent)

        Log.d("Service", "Broadcast sent")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// Receive in Activity
class MainActivity : AppCompatActivity() {

    private val dataReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val data = intent?.getStringExtra("data")
            val timestamp = intent?.getLongExtra("timestamp", 0L)

            Log.d("MainActivity", "Received: $data at $timestamp")
            updateUI(data)
        }
    }

    override fun onStart() {
        super.onStart()

        val filter = IntentFilter("com.example.DATA_UPDATED")
        registerReceiver(dataReceiver, filter)
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(dataReceiver)
    }
}
```

### Permissions for BroadcastReceiver

```xml
<!-- AndroidManifest.xml -->

<!-- Receive SMS -->
<uses-permission android:name="android.permission.RECEIVE_SMS"/>

<!-- Receive boot completed -->
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>

<!-- Access network state -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>

<!-- For custom broadcasts, can define custom permission -->
<permission
    android:name="com.example.permission.RECEIVE_CUSTOM_BROADCAST"
    android:protectionLevel="signature"/>

<!-- Require permission to receive -->
<receiver
    android:name=".SecureReceiver"
    android:permission="com.example.permission.RECEIVE_CUSTOM_BROADCAST">
    <intent-filter>
        <action android:name="com.example.SECURE_ACTION"/>
    </intent-filter>
</receiver>
```

### Static vs Dynamic Registration Comparison

| Aspect | Static (Manifest) | Dynamic (Code) |
|--------|-------------------|----------------|
| **Lifetime** | Always active | Active only when registered |
| **Registration** | AndroidManifest.xml | `registerReceiver()` |
| **Unregistration** | Not needed | **Must** unregister |
| **API 26+ limitations** | Most implicit broadcasts blocked | No limitations |
| **Memory** | No leaks | Can leak if not unregistered |
| **Use case** | System events, boot | Activity/Service specific |

### Best Practices

1. **Always unregister dynamic receivers** to prevent memory leaks
2. **Use dynamic registration** for most cases (especially API 26+)
3. **Handle unregister exceptions** when receiver might not be registered
4. **Set null listeners** in onDestroy to prevent leaks
5. **Use context-specific registration** (Activity, Service, Application)
6. **Consider WorkManager or JobScheduler** for background tasks instead of receivers

## Russian Answer

Подключение BroadcastReceiver в Android состоит из двух основных шагов: создание самого ресивера и его регистрация. Ресивер можно зарегистрировать как статически в манифесте, так и динамически в коде.

### Создание BroadcastReceiver

Создадим простой BroadcastReceiver, который будет реагировать на определённое событие, например, на получение SMS.

### Регистрация ресивера

**Статическая регистрация в манифесте**: Можно зарегистрировать ресивер в файле `AndroidManifest.xml`. Это удобно, когда вы хотите, чтобы ресивер всегда был активен и слушал определённые системные события, например, перезагрузку устройства или получение SMS.

**Динамическая регистрация в коде**: Иногда нужно регистрировать ресивер только на время выполнения определённой активности или службы. В этом случае лучше использовать динамическую регистрацию.

В методе `onStart()` регистрируется ресивер, а в `onStop()` отписывается. Это позволяет ресиверу быть активным только тогда, когда активность видима.

**Важно**: Всегда отменяйте регистрацию ресивера в соответствующем методе жизненного цикла (`onStop()` или `onDestroy()`), чтобы избежать утечек памяти.
