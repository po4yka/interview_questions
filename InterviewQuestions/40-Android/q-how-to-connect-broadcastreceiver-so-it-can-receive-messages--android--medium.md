---
id: android-280
title: How To Connect BroadcastReceiver So It Can Receive Messages / Как подключить
  BroadcastReceiver для получения сообщений
aliases:
- How To Connect BroadcastReceiver So It Can Receive Messages
- Как подключить BroadcastReceiver для получения сообщений
topic: android
subtopics:
- broadcast-receiver
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-broadcast-receiver
- q-how-to-register-broadcastreceiver-to-receive-messages--android--medium
- q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium
- q-what-can-be-done-through-composer--android--medium
- q-what-is-broadcastreceiver--android--easy
created: 2024-10-15
updated: 2025-11-10
tags:
- android/broadcast-receiver
- difficulty/medium
anki_cards:
- slug: android-280-0-en
  language: en
  anki_id: 1768378890449
  synced_at: '2026-01-23T16:45:06.007287'
- slug: android-280-0-ru
  language: ru
  anki_id: 1768378890470
  synced_at: '2026-01-23T16:45:06.008979'
---
# Вопрос (RU)
> Как подключить `BroadcastReceiver` для получения сообщений

# Question (EN)
> How To Connect `BroadcastReceiver` So It Can Receive Messages

---

## Ответ (RU)
`BroadcastReceiver` можно подключить двумя основными способами: статически через `AndroidManifest.xml` и динамически в коде. В ряде сценариев также используются упорядоченные (ordered) рассылки, разрешения и (исторически) `LocalBroadcastManager`. Конкретное поведение зависит от версии Android (ограничения фонового выполнения, ограничения на implicit broadcasts, требования к `android:exported`). Важно учитывать, что динамическая регистрация не "отменяет" платформенные ограничения — некоторые broadcast'ы могут быть недоступны или изменены. Ниже приведены подробные примеры для каждого подхода.

### Метод 1: Статическая Регистрация (Manifest)

Регистрируем ресивер в `AndroidManifest.xml`, чтобы система могла запускать процесс приложения для доставки подходящих broadcast-сообщений.

```kotlin
// Шаг 1: Создайте класс BroadcastReceiver
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                Log.d("BootReceiver", "Device booted")
                // На современных Android лучше планировать отложенную работу,
                // а не запускать фоновые сервисы напрямую
                // Например, WorkManager или foreground service при реальной необходимости
                enqueueBootCompletedWork(context)
            }
        }
    }
}
```

```xml
<!-- Шаг 2: Объявите ресивер в AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Необходимое разрешение -->
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

    <application>
        <!-- Регистрация BroadcastReceiver -->
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

Характеристики:
- Может получать некоторые системные broadcast'ы даже когда приложение не запущено: система поднимает процесс при совпадении `Intent`.
- Работает между перезапусками приложения, пока описание в манифесте актуально.
- Подчиняется ограничениям Android 8.0+: многие implicit broadcasts недоступны для сторонних приложений через манифест.
- Можно включать/отключать через `PackageManager`, но это менее гибко, чем динамическая регистрация.

### Метод 2: Динамическая Регистрация (в коде)

Регистрируем ресивер в коде так, чтобы его жизнь была связана с компонентом (`Activity`, `Service` и т.п.). Это основной способ получения многих implicit broadcasts на современных Android (там, где они ещё поддерживаются).

```kotlin
class MainActivity : AppCompatActivity() {

    // Шаг 1: Создаём BroadcastReceiver
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            if (level >= 0 && scale > 0) {
                val batteryPct = level / scale.toFloat() * 100
                Log.d("Battery", "Battery level: $batteryPct%")
                updateBatteryUI(batteryPct)
            }
        }
    }

    override fun onStart() {
        super.onStart()

        // Шаг 2: Создаём IntentFilter
        val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)

        // Шаг 3: Регистрируем ресивер
        registerReceiver(batteryReceiver, filter)
    }

    override fun onStop() {
        super.onStop()

        // Шаг 4: Обязательно отписываемся
        unregisterReceiver(batteryReceiver)
    }

    private fun updateBatteryUI(percentage: Float) {
        // Обновление UI уровнем заряда батареи
    }
}
```

Характеристики:
- Ресивер активен только пока зарегистрирован; обычно привязан к жизненному циклу `Activity`/`Fragment`/`Service`.
- Позволяет гибко включать/отключать обработку во время выполнения.
- Помогает корректно использовать оставшиеся implicit broadcasts без manifest-регистрации (но сами отправляемые системой broadcast'ы всё равно ограничены политиками платформы).
- Требует корректного `unregisterReceiver` для предотвращения утечек и `IllegalArgumentException`.

### Метод 3: Ресивер С Областью Жизни Компонента (Component-Scoped Receiver)

Пример, когда ресивер живёт столько же, сколько конкретная `Activity`.

```kotlin
class MainActivity : AppCompatActivity() {

    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val connectivityManager = context.getSystemService(ConnectivityManager::class.java)
            val network = connectivityManager?.activeNetwork
            val isConnected = network != null

            Log.d("Network", "Connected: $isConnected")
            updateNetworkUI(isConnected)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Для приложений с target N+ CONNECTIVITY_ACTION помечен deprecated.
        // Динамическая регистрация возможна, но для отслеживания сети рекомендуется
        // использовать NetworkCallback API (registerDefaultNetworkCallback и др.).
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(networkReceiver)
        } catch (e: IllegalArgumentException) {
            // Ресивер не был зарегистрирован или уже отписан
        }
    }

    private fun updateNetworkUI(isConnected: Boolean) {
        // Обновление UI
    }
}
```

Характеристики:
- Использует стандартные `registerReceiver`/`unregisterReceiver` с явной привязкой к жизненному циклу компонента.
- Для современных сценариев работы с сетью предпочтительнее `ConnectivityManager.registerDefaultNetworkCallback` и аналогичные API.

### Метод 4: LocalBroadcastManager (устаревший)

Использовался только для внутренних (внутри приложения) broadcast'ов. Сейчас помечен как deprecated; рекомендуется использовать другие механизмы.

```kotlin
// ВНИМАНИЕ: LocalBroadcastManager устарел.
// Для внутрипроцессного взаимодействия используйте Shared ViewModel, Flow, LiveData и т.п.
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

### Примеры Системных Broadcast'ов

```kotlin
class SystemBroadcastReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            // События устройства
            Intent.ACTION_BOOT_COMPLETED -> handleBootCompleted()
            Intent.ACTION_POWER_CONNECTED -> handlePowerConnected()
            Intent.ACTION_POWER_DISCONNECTED -> handlePowerDisconnected()

            // Подключение (CONNECTIVITY_ACTION deprecated, используйте NetworkCallback, где возможно)
            ConnectivityManager.CONNECTIVITY_ACTION -> handleConnectivityChange(context)
            WifiManager.WIFI_STATE_CHANGED_ACTION -> handleWifiStateChange()

            // Батарея
            Intent.ACTION_BATTERY_LOW -> handleBatteryLow()
            Intent.ACTION_BATTERY_OKAY -> handleBatteryOkay()

            // Экран
            Intent.ACTION_SCREEN_ON -> handleScreenOn()
            Intent.ACTION_SCREEN_OFF -> handleScreenOff()

            // Время
            // Начиная с Android 12, ACTION_TIME_TICK больше не доставляется манифестным ресиверам сторонних приложений
            Intent.ACTION_TIME_TICK -> handleTimeTick()
            Intent.ACTION_TIMEZONE_CHANGED -> handleTimezoneChange()

            // Пакеты (требуют указания data scheme="package" в intent-filter манифеста)
            Intent.ACTION_PACKAGE_ADDED -> handlePackageAdded(intent)
            Intent.ACTION_PACKAGE_REMOVED -> handlePackageRemoved(intent)
        }
    }

    private fun handleBootCompleted() { /* ... */ }
    private fun handlePowerConnected() { /* ... */ }
    private fun handlePowerDisconnected() { /* ... */ }
    private fun handleWifiStateChange() { /* ... */ }
    private fun handleBatteryLow() { /* ... */ }
    private fun handleBatteryOkay() { /* ... */ }
    private fun handleScreenOn() { /* ... */ }
    private fun handleScreenOff() { /* ... */ }
    private fun handleTimeTick() { /* ... */ }
    private fun handleTimezoneChange() { /* ... */ }
    private fun handlePackageAdded(intent: Intent) { /* ... */ }
    private fun handlePackageRemoved(intent: Intent) { /* ... */ }

    private fun handleConnectivityChange(context: Context) {
        val cm = context.getSystemService(ConnectivityManager::class.java)
        val network = cm?.activeNetwork
        // Проверка статуса сети через NetworkCapabilities и т.п.
    }
}
```

### Несколько `IntentFilter`

```xml
<!-- Manifest-регистрация с несколькими действиями -->
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
// Динамическая регистрация с несколькими действиями
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

### Упорядоченные (Ordered) Broadcast'ы

Упорядоченные broadcast'ы доставляются ресиверам в порядке приоритета.

```xml
<!-- Более высокий приоритет обрабатывает первым (для данного ordered broadcast) -->
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
        val result = processData(intent)

        // abortBroadcast() имеет эффект только для ordered broadcast'ов
        if (result.shouldAbort) {
            abortBroadcast()
        }

        // Можно модифицировать и передать далее
        setResultData("Modified data")
    }
}

// Отправка ordered broadcast (внутренний пример)
fun Context.sendCustomOrderedBroadcast() {
    val intent = Intent("com.example.CUSTOM_ACTION")
    sendOrderedBroadcast(
        intent,
        null, // Разрешение
        null, // Ресивер результата
        null, // Scheduler
        Activity.RESULT_OK,
        null, // Начальные данные
        null  // Начальные extras
    )
}
```

### Exported Vs Not Exported

```xml
<!-- Получает broadcast'ы из других приложений -->
<receiver
    android:name=".PublicReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.PUBLIC_ACTION" />
    </intent-filter>
</receiver>

<!-- Получает broadcast'ы только внутри данного приложения -->
<receiver
    android:name=".PrivateReceiver"
    android:exported="false">
    <intent-filter>
        <action android:name="com.example.PRIVATE_ACTION" />
    </intent-filter>
</receiver>
```

Примечание:
- Начиная с Android 12 (API 31), явное указание `android:exported` обязательно для компонентов с `intent-filter`.

### Broadcast'ы, Защищённые Разрешениями (Permission-Protected)

```xml
<!-- Объявляем собственное разрешение -->
<permission
    android:name="com.example.app.SEND_CUSTOM_BROADCAST"
    android:protectionLevel="signature" />

<!-- Ресивер требует разрешение для получения -->
<receiver
    android:name=".ProtectedReceiver"
    android:permission="com.example.app.SEND_CUSTOM_BROADCAST">
    <intent-filter>
        <action android:name="com.example.PROTECTED_ACTION" />
    </intent-filter>
</receiver>
```

```kotlin
// Приложение-отправитель должно иметь это разрешение
fun Context.sendProtectedBroadcast() {
    val intent = Intent("com.example.PROTECTED_ACTION")
    sendBroadcast(intent, "com.example.app.SEND_CUSTOM_BROADCAST")
}
```

### Лучшие Практики

```kotlin
class BestPracticesActivity : AppCompatActivity() {

    private var isReceiverRegistered = false

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Обработка broadcast'а
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

Ключевые моменты:
- Всегда согласовывайте регистрацию и отписку с жизненным циклом компонента.
- Не выполняйте долгие операции в `onReceive()`; переносите их в `WorkManager`, foreground service или другие асинхронные механизмы.
- Для новых задач по возможности используйте современные API (`NetworkCallback`, `WorkManager`, внутриприложечные event bus'ы и реактивные потоки), а не глобальные broadcast'ы.

### Сравнение Подходов

| Метод                | Когда получает                             | Жизненный цикл           | Типичные случаи использования                |
|----------------------|--------------------------------------------|--------------------------|----------------------------------------------|
| Manifest             | Некоторые системные broadcast'ы; может запускать приложение | Между перезапусками     | Системные события, `BOOT_COMPLETED` и т.п.   |
| Dynamic              | Только пока зарегистрирован                | Жизнь компонента         | Обновление UI, implicit broadcasts           |
| LocalBroadcastManager| Только пока зарегистрирован (deprecated)   | Жизнь компонента         | Устаревшая внутренняя коммуникация           |
| `WorkManager`          | При выполнении условий/расписания          | Управляется системой     | Отложенная фоновая работа (предпочтительно)  |

### Современные Альтернативы

Во многих сценариях внутреннего взаимодействия или фоновой работы вместо глобальных broadcast'ов используйте:

```kotlin
// Альтернатива 1: LiveData для внутренней коммуникации
class DataRepository {
    private val _updates = MutableLiveData<Data>()
    val updates: LiveData<Data> = _updates

    fun updateData(data: Data) {
        _updates.postValue(data)
    }
}

// Альтернатива 2: WorkManager для фоновых задач
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()
WorkManager.getInstance(context).enqueue(workRequest)

// Альтернатива 3: Flow для реактивных событий
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}
```

В итоге, чтобы `BroadcastReceiver` получал сообщения, нужно: (1) объявить или реализовать ресивер, (2) корректно зарегистрировать его (в манифесте или динамически), (3) учитывать экспорт/разрешения и (4) следовать лучшим практикам и современным альтернативам.

## Answer (EN)
`BroadcastReceiver` can be registered in two main ways: statically in AndroidManifest.xml or dynamically in code. For some use cases, you can also use ordered broadcasts, permission-protected broadcasts, and (historically) LocalBroadcastManager. Exact behavior depends on Android version (background execution limits, implicit broadcast restrictions, exported flag requirements). Dynamic registration does not "override" platform policies: some broadcasts may still be limited or no longer sent.

### Method 1: Static Registration (Manifest)

Register receiver in AndroidManifest.xml so the system can start your app process to deliver matching broadcasts.

```kotlin
// Step 1: Create BroadcastReceiver class
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                Log.d("BootReceiver", "Device booted")
                // On modern Android, prefer scheduling deferrable work
                // instead of starting a background service directly
                // e.g. WorkManager or a foreground service if truly necessary
                enqueueBootCompletedWork(context)
            }
        }
    }
}
```

```xml
<!-- Step 2: Declare in AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Required permission -->
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

Characteristics:
- Can receive certain system broadcasts even when the app is not running: the system may start your app process to deliver them.
- Works across app restarts as long as the manifest entry remains.
- Subject to Android 8.0+ background execution limits and implicit broadcast restrictions: many implicit broadcasts can no longer be received via manifest registration by third-party apps.
- Can be enabled/disabled at runtime via PackageManager (less flexible than dynamic registration).

### Method 2: Dynamic Registration (Code)

Register receiver in code so its lifetime is tied to a component (e.g., `Activity`, `Service`). This is the primary way to receive many implicit broadcasts on modern Android where they are still supported.

```kotlin
class MainActivity : AppCompatActivity() {

    // Step 1: Create BroadcastReceiver
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            if (level >= 0 && scale > 0) {
                val batteryPct = level / scale.toFloat() * 100
                Log.d("Battery", "Battery level: $batteryPct%")
                updateBatteryUI(batteryPct)
            }
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

Characteristics:
- Receiver is active only while registered; typically tied to `Activity`/`Fragment`/`Service` lifecycle.
- Allows flexible enable/disable behavior at runtime.
- Helps correctly use remaining implicit broadcasts without manifest registration (but the underlying broadcasts are still governed by platform policies).
- Must be unregistered in the corresponding lifecycle callback to avoid leaks or IllegalArgumentException.

### Method 3: Component-Scoped Receiver Example

```kotlin
class MainActivity : AppCompatActivity() {

    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val connectivityManager = context.getSystemService(ConnectivityManager::class.java)
            val network = connectivityManager?.activeNetwork
            val isConnected = network != null

            Log.d("Network", "Connected: $isConnected")
            updateNetworkUI(isConnected)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // For apps targeting N+, CONNECTIVITY_ACTION is deprecated.
        // Dynamic registration is possible, but prefer NetworkCallback APIs
        // (e.g., registerDefaultNetworkCallback) for production code.
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(networkReceiver)
        } catch (e: IllegalArgumentException) {
            // Receiver was not registered or already unregistered
        }
    }

    private fun updateNetworkUI(isConnected: Boolean) {
        // Update UI
    }
}
```

Characteristics:
- Uses standard registerReceiver/unregisterReceiver with explicit lifecycle tie-in.
- For modern networking scenarios, use `ConnectivityManager.registerDefaultNetworkCallback` or related APIs instead of relying on `CONNECTIVITY_ACTION`.

### Method 4: LocalBroadcastManager (Deprecated)

Previously used for in-app broadcasts only. Now deprecated; use other mechanisms.

```kotlin
// WARNING: LocalBroadcastManager is deprecated.
// Prefer in-app mechanisms like shared ViewModel, Flow, LiveData, etc.
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

            // Connectivity (CONNECTIVITY_ACTION deprecated; prefer NetworkCallback where possible)
            ConnectivityManager.CONNECTIVITY_ACTION -> handleConnectivityChange(context)
            WifiManager.WIFI_STATE_CHANGED_ACTION -> handleWifiStateChange()

            // Battery
            Intent.ACTION_BATTERY_LOW -> handleBatteryLow()
            Intent.ACTION_BATTERY_OKAY -> handleBatteryOkay()

            // Screen
            Intent.ACTION_SCREEN_ON -> handleScreenOn()
            Intent.ACTION_SCREEN_OFF -> handleScreenOff()

            // Time
            // Starting with Android 12, ACTION_TIME_TICK is no longer delivered
            // to manifest-declared receivers in third-party apps
            Intent.ACTION_TIME_TICK -> handleTimeTick()
            Intent.ACTION_TIMEZONE_CHANGED -> handleTimezoneChange()

            // Package (require data scheme="package" in manifest intent-filters)
            Intent.ACTION_PACKAGE_ADDED -> handlePackageAdded(intent)
            Intent.ACTION_PACKAGE_REMOVED -> handlePackageRemoved(intent)
        }
    }

    private fun handleBootCompleted() { /* ... */ }
    private fun handlePowerConnected() { /* ... */ }
    private fun handlePowerDisconnected() { /* ... */ }
    private fun handleWifiStateChange() { /* ... */ }
    private fun handleBatteryLow() { /* ... */ }
    private fun handleBatteryOkay() { /* ... */ }
    private fun handleScreenOn() { /* ... */ }
    private fun handleScreenOff() { /* ... */ }
    private fun handleTimeTick() { /* ... */ }
    private fun handleTimezoneChange() { /* ... */ }
    private fun handlePackageAdded(intent: Intent) { /* ... */ }
    private fun handlePackageRemoved(intent: Intent) { /* ... */ }

    private fun handleConnectivityChange(context: Context) {
        val cm = context.getSystemService(ConnectivityManager::class.java)
        val network = cm?.activeNetwork
        // Check network status using NetworkCapabilities, etc.
    }
}
```

### Multiple `Intent` Filters

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

Receivers of an ordered broadcast are invoked according to their priority.

```xml
<!-- Higher priority processes first (for this ordered broadcast) -->
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
        val result = processData(intent)

        // abortBroadcast() only has effect for ordered broadcasts
        if (result.shouldAbort) {
            abortBroadcast()
        }

        // Or modify and pass along
        setResultData("Modified data")
    }
}

// Sending ordered broadcast (internal example)
fun Context.sendCustomOrderedBroadcast() {
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

### Exported Vs Not Exported

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

Note:
- Starting with Android 12 (API 31), specifying `android:exported` explicitly is mandatory for components with intent filters.

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
// Sending app must hold the permission
fun Context.sendProtectedBroadcast() {
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

Key points:
- Always match registration and unregistration to the appropriate lifecycle callbacks.
- Avoid long-running work in `onReceive()`; offload to `WorkManager`, a foreground service, or other async mechanisms.
- For new code, prefer modern APIs (`NetworkCallback`, `WorkManager`, in-app event buses, reactive streams) over global broadcasts where appropriate.

### Comparison Table

| Method               | When Receives                              | `Lifecycle`              | Use Case                               |
|----------------------|--------------------------------------------|------------------------|-----------------------------------------|
| Manifest             | Certain system broadcasts; app may be started | Across app restarts | System events, BOOT_COMPLETED, etc.    |
| Dynamic              | Only when registered                      | `Component` lifetime     | UI updates, implicit broadcasts        |
| LocalBroadcastManager| Only when registered (deprecated)         | `Component` lifetime     | Legacy internal communication          |
| `WorkManager`          | When constraints met / scheduled          | Managed by OS          | Deferrable background work (preferred) |

### Modern Alternatives

For many internal or background tasks, use these instead of global broadcasts:

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

---

## Related Topics
- `Intent` and IntentFilter
- AndroidManifest.xml
- System broadcasts
- `WorkManager` (modern alternative)
- LocalBroadcastManager

---

## Follow-ups

- [[q-memory-leak-vs-oom-android--android--medium]]
- [[q-state-hoisting-compose--android--medium]]
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]

## References

- [Services](https://developer.android.com/develop/background-work/services)

## Related Questions

### Prerequisites / Concepts

- [[c-broadcast-receiver]]

### Prerequisites (Easier)
- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Related (Medium)
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast

### Advanced (Harder)
- [[q-kotlin-context-receivers--android--hard]] - Broadcast
