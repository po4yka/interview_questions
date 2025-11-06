---
id: android-395
title: "BroadcastReceiver / Компонент BroadcastReceiver"
aliases: [BroadcastReceiver, Компонент BroadcastReceiver]
topic: android
subtopics: [service]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-broadcast-receiver, c-intent, q-what-each-android-component-represents--android--easy, q-what-is-activity-and-what-is-it-used-for--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/service, broadcast-receiver, components, difficulty/easy, intent, system-events]
date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Question (EN)

> What is BroadcastReceiver?

# Вопрос (RU)

> Что такое BroadcastReceiver?

---

## Answer (EN)

**BroadcastReceiver** is one of the fundamental Android components that allows applications to **receive and respond to system-wide or app-specific broadcast messages**. It acts as a listener for Intent broadcasts sent by the Android system or other applications.

### Core Concept

BroadcastReceivers enable communication between different parts of an app or between different apps using a publish-subscribe pattern.

```kotlin
class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Handle the broadcast
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // Battery is low
                Toast.makeText(context, "Battery is low!", Toast.LENGTH_SHORT).show()
            }
            Intent.ACTION_POWER_CONNECTED -> {
                // Device plugged in
                Log.d("Receiver", "Power connected")
            }
        }
    }
}
```

### Types of Broadcasts

#### 1. System Broadcasts

Android system sends broadcasts for various events:

```kotlin
class SystemBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                // Device finished booting
                startBackgroundService(context)
            }
            Intent.ACTION_AIRPLANE_MODE_CHANGED -> {
                val isAirplaneModeOn = intent.getBooleanExtra("state", false)
                Log.d("Receiver", "Airplane mode: $isAirplaneModeOn")
            }
            Intent.ACTION_TIMEZONE_CHANGED -> {
                // Time zone changed
                updateTimeZone(context)
            }
            Intent.ACTION_LOCALE_CHANGED -> {
                // Locale/language changed
                updateLocale(context)
            }
        }
    }
}
```

**Common system broadcasts:**

-   `ACTION_BATTERY_LOW` / `ACTION_BATTERY_OKAY` - Battery status
-   `ACTION_POWER_CONNECTED` / `ACTION_POWER_DISCONNECTED` - Charging status
-   `ACTION_BOOT_COMPLETED` - Device finished booting
-   `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF` - Screen state
-   `ACTION_AIRPLANE_MODE_CHANGED` - Airplane mode toggled
-   `ACTION_TIMEZONE_CHANGED` - Time zone changed
-   `ACTION_DATE_CHANGED` - Date changed

#### 2. Custom Broadcasts

Apps can send custom broadcasts:

```kotlin
// Sending custom broadcast
class MainActivity : AppCompatActivity() {
    fun sendCustomBroadcast() {
        val intent = Intent("com.example.MY_CUSTOM_ACTION")
        intent.putExtra("message", "Hello from sender!")
        sendBroadcast(intent)
    }

    fun sendOrderedBroadcast() {
        val intent = Intent("com.example.ORDERED_ACTION")
        sendOrderedBroadcast(intent, null)
    }

    fun sendLocalBroadcast() {
        val intent = Intent("com.example.LOCAL_ACTION")
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
    }
}

// Receiving custom broadcast
class CustomBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val message = intent?.getStringExtra("message")
        Log.d("Receiver", "Received: $message")
    }
}
```

### Registration Methods

#### 1. Static Registration (Manifest)

Declared in AndroidManifest.xml. Receiver works even if app is not running.

```xml
<manifest>
    <application>
        <receiver
            android:name=".MyBroadcastReceiver"
            android:enabled="true"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.AIRPLANE_MODE_CHANGED" />
            </intent-filter>
        </receiver>
    </application>

    <!-- Required permissions -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
</manifest>
```

#### 2. Dynamic Registration (Runtime)

Registered programmatically in code. Receiver only works while component is alive.

```kotlin
class MainActivity : AppCompatActivity() {
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val level = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
            val scale = intent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
            val batteryPct = level * 100 / scale.toFloat()

            Log.d("Battery", "Battery level: $batteryPct%")
        }
    }

    override fun onResume() {
        super.onResume()

        // Register receiver
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_CHANGED)
            addAction(Intent.ACTION_POWER_CONNECTED)
            addAction(Intent.ACTION_POWER_DISCONNECTED)
        }
        registerReceiver(batteryReceiver, filter)
    }

    override fun onPause() {
        super.onPause()
        // Unregister to avoid memory leaks
        unregisterReceiver(batteryReceiver)
    }
}
```

**Key difference:**

-   Static: Works even when app is closed (limited on Android 8.0+)
-   Dynamic: Only works when component is active, must unregister

### Broadcast Types

#### Normal Broadcasts

Asynchronous, all receivers get broadcast simultaneously.

```kotlin
// Send normal broadcast
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)
```

#### Ordered Broadcasts

Delivered to receivers one at a time, in priority order. Receivers can abort broadcast.

```kotlin
// Send ordered broadcast
sendOrderedBroadcast(intent, null)

// Receiver with priority
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="com.example.ACTION" />
    </intent-filter>
</receiver>

// Abort broadcast
class HighPriorityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Process broadcast
        abortBroadcast() // Stop propagation to lower priority receivers
    }
}
```

#### Local Broadcasts

Only within the app, more efficient and secure.

```kotlin
// Send
LocalBroadcastManager.getInstance(context).sendBroadcast(intent)

// Register
LocalBroadcastManager.getInstance(context)
    .registerReceiver(receiver, IntentFilter("ACTION"))

// Unregister
LocalBroadcastManager.getInstance(context)
    .unregisterReceiver(receiver)
```

### Complete Example

```kotlin
// 1. Define receiver
class NetworkChangeReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            val connectivityManager = context?.getSystemService(Context.CONNECTIVITY_SERVICE)
                as ConnectivityManager

            val activeNetwork = connectivityManager.activeNetworkInfo
            val isConnected = activeNetwork?.isConnectedOrConnecting == true

            if (isConnected) {
                Toast.makeText(context, "Internet connected", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(context, "No internet", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

// 2. Register in Activity
class MainActivity : AppCompatActivity() {
    private val networkReceiver = NetworkChangeReceiver()

    override fun onStart() {
        super.onStart()

        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(networkReceiver)
    }
}

// 3. Add permission in manifest
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Background Execution Limits (Android 8.0+)

Starting from Android 8.0 (API 26), there are restrictions on implicit broadcasts registered in manifest.

**Affected broadcasts:**

Most implicit system broadcasts cannot be received by manifest-declared receivers.

**Exceptions (still work):**

-   `ACTION_BOOT_COMPLETED`
-   `ACTION_LOCALE_CHANGED`
-   `ACTION_TIME_SET`

**Solutions:**

1. Register receiver dynamically instead
2. Use JobScheduler or WorkManager for background tasks
3. Use foreground services

```kotlin
// Instead of manifest-registered receiver for network changes:
// Use WorkManager with network constraint
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()

val work = OneTimeWorkRequestBuilder<NetworkWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(work)
```

### Best Practices

**1. Keep onReceive() short:**

```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Process quickly (< 10 seconds)
        // For long operations, use WorkManager or Service

        val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
        WorkManager.getInstance(context!!).enqueue(workRequest)
    }
}
```

**2. Always unregister dynamic receivers:**

```kotlin
override fun onDestroy() {
    super.onDestroy()
    try {
        unregisterReceiver(myReceiver)
    } catch (e: IllegalArgumentException) {
        // Receiver not registered
    }
}
```

**3. Use LocalBroadcastManager for internal communication:**

```kotlin
// More efficient and secure than global broadcasts
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("com.example.ACTION"))
```

**4. Set receiver exported correctly:**

```xml
<!-- Not accessible by other apps -->
<receiver
    android:name=".MyReceiver"
    android:exported="false">
</receiver>

<!-- Accessible by other apps (requires explicit permission) -->
<receiver
    android:name=".PublicReceiver"
    android:exported="true"
    android:permission="com.example.MY_PERMISSION">
</receiver>
```

### Common Use Cases

**1. Network Monitoring:**

```kotlin
class NetworkMonitor(private val context: Context) {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            checkNetworkStatus()
        }
    }

    fun start() {
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        context.registerReceiver(receiver, filter)
    }

    fun stop() {
        context.unregisterReceiver(receiver)
    }
}
```

**2. Battery Monitoring:**

```kotlin
class BatteryMonitor : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // Enable power saving mode
                enablePowerSaving(context)
            }
            Intent.ACTION_BATTERY_OKAY -> {
                // Disable power saving mode
                disablePowerSaving(context)
            }
        }
    }
}
```

**3. App Update Detection:**

```kotlin
class AppUpdateReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_MY_PACKAGE_REPLACED) {
            // App was updated
            performMigration(context)
        }
    }
}
```

### Summary

**BroadcastReceiver is an Android component that:**

-   Listens for system-wide or app-specific broadcast messages
-   Can be registered statically (manifest) or dynamically (runtime)
-   Receives Intent broadcasts from system or other apps
-   Executes in main thread (keep onReceive() fast)
-   Has restrictions on Android 8.0+ for background execution

**Use cases:**

-   Monitoring system events (battery, network, screen)
-   App-to-app communication
-   Responding to device state changes
-   Scheduling tasks based on system conditions

**Best practices:**

-   Keep onReceive() short (< 10 seconds)
-   Always unregister dynamic receivers
-   Use LocalBroadcastManager for internal broadcasts
-   Consider WorkManager for background tasks on Android 8.0+


# Question (EN)

> What is BroadcastReceiver?

# Вопрос (RU)

> Что такое BroadcastReceiver?

---


---


## Answer (EN)

**BroadcastReceiver** is one of the fundamental Android components that allows applications to **receive and respond to system-wide or app-specific broadcast messages**. It acts as a listener for Intent broadcasts sent by the Android system or other applications.

### Core Concept

BroadcastReceivers enable communication between different parts of an app or between different apps using a publish-subscribe pattern.

```kotlin
class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Handle the broadcast
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // Battery is low
                Toast.makeText(context, "Battery is low!", Toast.LENGTH_SHORT).show()
            }
            Intent.ACTION_POWER_CONNECTED -> {
                // Device plugged in
                Log.d("Receiver", "Power connected")
            }
        }
    }
}
```

### Types of Broadcasts

#### 1. System Broadcasts

Android system sends broadcasts for various events:

```kotlin
class SystemBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                // Device finished booting
                startBackgroundService(context)
            }
            Intent.ACTION_AIRPLANE_MODE_CHANGED -> {
                val isAirplaneModeOn = intent.getBooleanExtra("state", false)
                Log.d("Receiver", "Airplane mode: $isAirplaneModeOn")
            }
            Intent.ACTION_TIMEZONE_CHANGED -> {
                // Time zone changed
                updateTimeZone(context)
            }
            Intent.ACTION_LOCALE_CHANGED -> {
                // Locale/language changed
                updateLocale(context)
            }
        }
    }
}
```

**Common system broadcasts:**

-   `ACTION_BATTERY_LOW` / `ACTION_BATTERY_OKAY` - Battery status
-   `ACTION_POWER_CONNECTED` / `ACTION_POWER_DISCONNECTED` - Charging status
-   `ACTION_BOOT_COMPLETED` - Device finished booting
-   `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF` - Screen state
-   `ACTION_AIRPLANE_MODE_CHANGED` - Airplane mode toggled
-   `ACTION_TIMEZONE_CHANGED` - Time zone changed
-   `ACTION_DATE_CHANGED` - Date changed

#### 2. Custom Broadcasts

Apps can send custom broadcasts:

```kotlin
// Sending custom broadcast
class MainActivity : AppCompatActivity() {
    fun sendCustomBroadcast() {
        val intent = Intent("com.example.MY_CUSTOM_ACTION")
        intent.putExtra("message", "Hello from sender!")
        sendBroadcast(intent)
    }

    fun sendOrderedBroadcast() {
        val intent = Intent("com.example.ORDERED_ACTION")
        sendOrderedBroadcast(intent, null)
    }

    fun sendLocalBroadcast() {
        val intent = Intent("com.example.LOCAL_ACTION")
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
    }
}

// Receiving custom broadcast
class CustomBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val message = intent?.getStringExtra("message")
        Log.d("Receiver", "Received: $message")
    }
}
```

### Registration Methods

#### 1. Static Registration (Manifest)

Declared in AndroidManifest.xml. Receiver works even if app is not running.

```xml
<manifest>
    <application>
        <receiver
            android:name=".MyBroadcastReceiver"
            android:enabled="true"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.AIRPLANE_MODE_CHANGED" />
            </intent-filter>
        </receiver>
    </application>

    <!-- Required permissions -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
</manifest>
```

#### 2. Dynamic Registration (Runtime)

Registered programmatically in code. Receiver only works while component is alive.

```kotlin
class MainActivity : AppCompatActivity() {
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val level = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
            val scale = intent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
            val batteryPct = level * 100 / scale.toFloat()

            Log.d("Battery", "Battery level: $batteryPct%")
        }
    }

    override fun onResume() {
        super.onResume()

        // Register receiver
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_CHANGED)
            addAction(Intent.ACTION_POWER_CONNECTED)
            addAction(Intent.ACTION_POWER_DISCONNECTED)
        }
        registerReceiver(batteryReceiver, filter)
    }

    override fun onPause() {
        super.onPause()
        // Unregister to avoid memory leaks
        unregisterReceiver(batteryReceiver)
    }
}
```

**Key difference:**

-   Static: Works even when app is closed (limited on Android 8.0+)
-   Dynamic: Only works when component is active, must unregister

### Broadcast Types

#### Normal Broadcasts

Asynchronous, all receivers get broadcast simultaneously.

```kotlin
// Send normal broadcast
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)
```

#### Ordered Broadcasts

Delivered to receivers one at a time, in priority order. Receivers can abort broadcast.

```kotlin
// Send ordered broadcast
sendOrderedBroadcast(intent, null)

// Receiver with priority
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="com.example.ACTION" />
    </intent-filter>
</receiver>

// Abort broadcast
class HighPriorityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Process broadcast
        abortBroadcast() // Stop propagation to lower priority receivers
    }
}
```

#### Local Broadcasts

Only within the app, more efficient and secure.

```kotlin
// Send
LocalBroadcastManager.getInstance(context).sendBroadcast(intent)

// Register
LocalBroadcastManager.getInstance(context)
    .registerReceiver(receiver, IntentFilter("ACTION"))

// Unregister
LocalBroadcastManager.getInstance(context)
    .unregisterReceiver(receiver)
```

### Complete Example

```kotlin
// 1. Define receiver
class NetworkChangeReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            val connectivityManager = context?.getSystemService(Context.CONNECTIVITY_SERVICE)
                as ConnectivityManager

            val activeNetwork = connectivityManager.activeNetworkInfo
            val isConnected = activeNetwork?.isConnectedOrConnecting == true

            if (isConnected) {
                Toast.makeText(context, "Internet connected", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(context, "No internet", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

// 2. Register in Activity
class MainActivity : AppCompatActivity() {
    private val networkReceiver = NetworkChangeReceiver()

    override fun onStart() {
        super.onStart()

        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(networkReceiver)
    }
}

// 3. Add permission in manifest
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Background Execution Limits (Android 8.0+)

Starting from Android 8.0 (API 26), there are restrictions on implicit broadcasts registered in manifest.

**Affected broadcasts:**

Most implicit system broadcasts cannot be received by manifest-declared receivers.

**Exceptions (still work):**

-   `ACTION_BOOT_COMPLETED`
-   `ACTION_LOCALE_CHANGED`
-   `ACTION_TIME_SET`

**Solutions:**

1. Register receiver dynamically instead
2. Use JobScheduler or WorkManager for background tasks
3. Use foreground services

```kotlin
// Instead of manifest-registered receiver for network changes:
// Use WorkManager with network constraint
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()

val work = OneTimeWorkRequestBuilder<NetworkWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(work)
```

### Best Practices

**1. Keep onReceive() short:**

```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Process quickly (< 10 seconds)
        // For long operations, use WorkManager or Service

        val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
        WorkManager.getInstance(context!!).enqueue(workRequest)
    }
}
```

**2. Always unregister dynamic receivers:**

```kotlin
override fun onDestroy() {
    super.onDestroy()
    try {
        unregisterReceiver(myReceiver)
    } catch (e: IllegalArgumentException) {
        // Receiver not registered
    }
}
```

**3. Use LocalBroadcastManager for internal communication:**

```kotlin
// More efficient and secure than global broadcasts
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("com.example.ACTION"))
```

**4. Set receiver exported correctly:**

```xml
<!-- Not accessible by other apps -->
<receiver
    android:name=".MyReceiver"
    android:exported="false">
</receiver>

<!-- Accessible by other apps (requires explicit permission) -->
<receiver
    android:name=".PublicReceiver"
    android:exported="true"
    android:permission="com.example.MY_PERMISSION">
</receiver>
```

### Common Use Cases

**1. Network Monitoring:**

```kotlin
class NetworkMonitor(private val context: Context) {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            checkNetworkStatus()
        }
    }

    fun start() {
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        context.registerReceiver(receiver, filter)
    }

    fun stop() {
        context.unregisterReceiver(receiver)
    }
}
```

**2. Battery Monitoring:**

```kotlin
class BatteryMonitor : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // Enable power saving mode
                enablePowerSaving(context)
            }
            Intent.ACTION_BATTERY_OKAY -> {
                // Disable power saving mode
                disablePowerSaving(context)
            }
        }
    }
}
```

**3. App Update Detection:**

```kotlin
class AppUpdateReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_MY_PACKAGE_REPLACED) {
            // App was updated
            performMigration(context)
        }
    }
}
```

### Summary

**BroadcastReceiver is an Android component that:**

-   Listens for system-wide or app-specific broadcast messages
-   Can be registered statically (manifest) or dynamically (runtime)
-   Receives Intent broadcasts from system or other apps
-   Executes in main thread (keep onReceive() fast)
-   Has restrictions on Android 8.0+ for background execution

**Use cases:**

-   Monitoring system events (battery, network, screen)
-   App-to-app communication
-   Responding to device state changes
-   Scheduling tasks based on system conditions

**Best practices:**

-   Keep onReceive() short (< 10 seconds)
-   Always unregister dynamic receivers
-   Use LocalBroadcastManager for internal broadcasts
-   Consider WorkManager for background tasks on Android 8.0+

## Ответ (RU)

**BroadcastReceiver** - это один из фундаментальных компонентов Android, который позволяет приложениям **получать и реагировать на широковещательные сообщения** от системы или других приложений.

### Основная Концепция

BroadcastReceiver работает по принципу publish-subscribe (издатель-подписчик), позволяя приложениям подписываться на определенные события.

### Типы Широковещательных Сообщений

**1. Системные broadcasts:**

-   `ACTION_BATTERY_LOW` - низкий заряд батареи
-   `ACTION_BOOT_COMPLETED` - устройство загрузилось
-   `ACTION_AIRPLANE_MODE_CHANGED` - изменен режим полета
-   `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF` - экран включен/выключен

**2. Пользовательские broadcasts:**

Приложения могут отправлять собственные broadcasts для коммуникации между компонентами.

### Методы Регистрации

**Статическая (в манифесте):**

-   Работает даже когда приложение закрыто
-   Ограничения на Android 8.0+

**Динамическая (в коде):**

-   Работает только пока компонент активен
-   Необходимо отменять регистрацию

### Лучшие Практики

1. Держите onReceive() коротким (< 10 секунд)
2. Всегда отменяйте регистрацию динамических receivers
3. Используйте LocalBroadcastManager для внутренней коммуникации
4. На Android 8.0+ используйте WorkManager вместо manifest-registered receivers

---

## Follow-ups

-   How do Android 8.0+ background execution limits affect BroadcastReceiver usage?
-   When should you use LocalBroadcastManager vs global broadcasts?
-   What's the difference between ordered and normal broadcasts?

## References

-   `https://developer.android.com/guide/components/broadcasts` — Broadcasts overview
-   `https://developer.android.com/guide/components/broadcast-exceptions` — Background execution limits

## Related Questions

### Related (Easy)

-   [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast

### Advanced (Harder)

-   [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast
-   [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast
-   [[q-kotlin-context-receivers--android--hard]] - Broadcast
