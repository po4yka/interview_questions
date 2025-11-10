---
id: android-395
title: BroadcastReceiver / Компонент BroadcastReceiver
aliases:
- BroadcastReceiver
- Компонент BroadcastReceiver
topic: android
subtopics:
- broadcast-receiver
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-broadcast-receiver
- c-intent
- q-what-each-android-component-represents--android--easy
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/broadcast-receiver
- difficulty/easy
- intent
- system-events

---

# Вопрос (RU)

> Что такое `BroadcastReceiver`?

# Question (EN)

> What is `BroadcastReceiver`?

---

## Ответ (RU)

**`BroadcastReceiver`** — один из базовых компонентов Android, позволяющий приложениям **получать и обрабатывать широковещательные сообщения (broadcast `Intent`s)** от системы или других приложений, а также собственные (внутри приложения).

Ключевые моменты:

- `BroadcastReceiver` выступает как слушатель `Intent`-ов.
- `BroadcastReceiver` обрабатывает только те `Intent`-ы, чьи `action`/`data`/`category` соответствуют его `intent-filter`.
- `onReceive()` вызывается в главном потоке — обработка должна быть быстрой.

### Основная концепция

`BroadcastReceiver` реализует шаблон publish-subscribe:

- отправитель посылает `Intent` (broadcast);
- каждый `BroadcastReceiver` с подходящим `intent-filter` получает этот `Intent`.

```kotlin
class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                Toast.makeText(context, "Низкий заряд батареи", Toast.LENGTH_SHORT).show()
            }
            Intent.ACTION_POWER_CONNECTED -> {
                Log.d("Receiver", "Питание подключено")
            }
        }
    }
}
```

### Типы широковещательных сообщений по источнику

#### 1. Системные broadcast-ы

Android отправляет broadcast-ы при различных системных событиях. Пример ресивера:

```kotlin
class SystemBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BOOT_COMPLETED -> {
                // Устройство завершило загрузку
                startBackgroundService(context)
            }
            Intent.ACTION_AIRPLANE_MODE_CHANGED -> {
                val isAirplaneModeOn = intent.getBooleanExtra("state", false)
                Log.d("Receiver", "Режим полета: $isAirplaneModeOn")
            }
            Intent.ACTION_TIMEZONE_CHANGED -> {
                updateTimeZone(context)
            }
            Intent.ACTION_LOCALE_CHANGED -> {
                updateLocale(context)
            }
        }
    }
}
```

Типичные системные broadcast-ы (многие ограничены на современных версиях Android):

- `ACTION_BATTERY_LOW` / `ACTION_BATTERY_OKAY` — состояние батареи
- `ACTION_POWER_CONNECTED` / `ACTION_POWER_DISCONNECTED` — состояние зарядки
- `ACTION_BOOT_COMPLETED` — устройство завершило загрузку
- `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF` — состояние экрана (ограничены в новых версиях)
- `ACTION_AIRPLANE_MODE_CHANGED` — переключение режима полета
- `ACTION_TIMEZONE_CHANGED` / `ACTION_DATE_CHANGED` — изменения времени и даты

Всегда проверяйте актуальную документацию, чтобы убедиться, что нужный `action` можно получать (особенно из манифеста).

#### 2. Пользовательские (кастомные) broadcast-ы

Приложение может отправлять собственные broadcast-ы, в том числе обычные и упорядоченные:

```kotlin
class MainActivity : AppCompatActivity() {
    fun sendCustomBroadcast() {
        val intent = Intent("com.example.MY_CUSTOM_ACTION").apply {
            putExtra("message", "Hello from sender!")
        }
        // Глобальный broadcast (может быть виден другим приложениям, если ресивер экспортирован)
        sendBroadcast(intent)
    }

    fun sendOrderedBroadcast() {
        val intent = Intent("com.example.ORDERED_ACTION")
        sendOrderedBroadcast(intent, null)
    }
}

class CustomBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val message = intent?.getStringExtra("message")
        Log.d("Receiver", "Получено: $message")
    }
}
```

Для внутренней коммуникации в рамках одного приложения на современных проектах чаще используют другие механизмы (колбэки, `LiveData`, `Flow`, shared `ViewModel` и т.п.). `LocalBroadcastManager` в AndroidX помечен как deprecated и актуален только для легаси-кода.

---

### Методы регистрации

#### 1. Статическая регистрация (в манифесте)

Объявление в `AndroidManifest.xml` позволяет системе запускать процесс приложения при получении подходящего broadcast-а.

Важно:

- Начиная с Android 8.0, многие неявные системные broadcast-ы больше не доставляются таким ресиверам.
- Явные broadcast-ы (адресованные вашему пакету) и некоторые задокументированные исключения продолжают работать.

```xml
<manifest>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

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
</manifest>
```

Кратко:

- работает даже когда процесс приложения не запущен (для разрешенных действий);
- ограничен для многих неявных broadcast-ов, начиная с API 26.

#### 2. Динамическая регистрация (во время выполнения)

Регистрация в коде через `Context.registerReceiver`. Ресивер активен только пока жив компонент (например, `Activity` или `Service`), который его зарегистрировал.

```kotlin
class MainActivity : AppCompatActivity() {
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val level = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
            val scale = intent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
            if (level >= 0 && scale > 0) {
                val batteryPct = level * 100f / scale
                Log.d("Battery", "Уровень заряда: $batteryPct%")
            }
        }
    }

    override fun onResume() {
        super.onResume()
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_CHANGED)
            addAction(Intent.ACTION_POWER_CONNECTED)
            addAction(Intent.ACTION_POWER_DISCONNECTED)
        }
        registerReceiver(batteryReceiver, filter)
    }

    override fun onPause() {
        super.onPause()
        try {
            unregisterReceiver(batteryReceiver)
        } catch (e: IllegalArgumentException) {
            // Ресивер не был зарегистрирован или уже размонтирован
        }
    }
}
```

Кратко:

- активен только пока зарегистрирован;
- требует явного `unregisterReceiver()` для избежания утечек и исключений.

---

### Типы доставки broadcast-ов

#### Обычные (normal)

Отправляются через `sendBroadcast()`.

```kotlin
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)
```

- доставляются всем подходящим ресиверам;
- порядок доставки не гарантируется;
- нельзя предотвратить доставку другим.

#### Упорядоченные (ordered)

Отправляются через `sendOrderedBroadcast()`.

```kotlin
val intent = Intent("com.example.ORDERED_ACTION")
sendOrderedBroadcast(intent, null)
```

Манифест:

```xml
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="com.example.ORDERED_ACTION" />
    </intent-filter>
</receiver>
```

Ресивер:

```kotlin
class HighPriorityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Обрабатываем broadcast
        abortBroadcast() // Для упорядоченных broadcast-ов может остановить доставку низкоприоритетным ресиверам
    }
}
```

Примечание: упорядоченные broadcast-ы и `abortBroadcast()` существенно ограничены в современных версиях Android; перед использованием проверяйте документацию.

#### Локальные broadcast-ы (legacy)

Ранее использовались через `LocalBroadcastManager`:

```kotlin
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("com.example.LOCAL_ACTION"))
```

Сейчас `LocalBroadcastManager` помечен как deprecated; предпочтительнее прямые колбэки, `LiveData`, `Flow` или другие механизмы внутри приложения.

---

### Пример: отслеживание изменений сети (legacy-подход)

Исторически приложения слушали `ConnectivityManager.CONNECTIVITY_ACTION` через `BroadcastReceiver`:

```kotlin
class NetworkChangeReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            val cm = context?.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val activeNetwork = cm.activeNetworkInfo
            val isConnected = activeNetwork?.isConnectedOrConnecting == true

            Toast.makeText(
                context,
                if (isConnected) "Интернет доступен" else "Нет подключения к интернету",
                Toast.LENGTH_SHORT
            ).show()
        }
    }
}
```

Для современных приложений (таргетирующих новые SDK) рекомендуется использовать `ConnectivityManager.NetworkCallback` вместо этого broadcast-а.

---

### Ограничения фонового выполнения (Android 8.0+)

Начиная с Android 8.0 (API 26), введены ограничения фонового выполнения и implicit broadcast-ов:

- большинство неявных системных broadcast-ов нельзя получать через ресиверы из манифеста;
- часть задокументированных исключений (например, `ACTION_BOOT_COMPLETED`, `ACTION_LOCALE_CHANGED`, `ACTION_TIMEZONE_CHANGED`, `ACTION_MY_PACKAGE_REPLACED` и др.) по-прежнему поддерживается;
- явные broadcast-ы к вашему приложению, как правило, разрешены.

Рекомендуется:

1. Регистрировать ресиверы динамически, пока приложение на переднем плане.
2. Использовать `JobScheduler` / `WorkManager` для отложенной фоновой работы.
3. Использовать foreground service для долгих операций, инициированных broadcast-ами.

Пример с WorkManager:

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()

val work = OneTimeWorkRequestBuilder<NetworkWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(work)
```

---

### Лучшие практики (RU)

1. Держите `onReceive()` максимально коротким:

```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Только легкая работа
        val safeContext = context ?: return
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
        WorkManager.getInstance(safeContext).enqueue(workRequest)
    }
}
```

2. Всегда корректно снимайте регистрацию динамических ресиверов:

```kotlin
override fun onDestroy() {
    super.onDestroy()
    try {
        unregisterReceiver(myReceiver)
    } catch (e: IllegalArgumentException) {
        // Ресивер не был зарегистрирован или уже размонтирован
    }
}
```

3. По возможности предпочитайте внутриприложечные механизмы (колбэки, shared `ViewModel`, корутины и т.п.) вместо глобальных широковещательных сообщений.

4. Правильно задавайте `android:exported`:

```xml
<!-- Не доступен другим приложениям -->
<receiver
    android:name=".MyReceiver"
    android:exported="false" />

<!-- Доступен другим приложениям (при необходимости защитите разрешением) -->
<receiver
    android:name=".PublicReceiver"
    android:exported="true"
    android:permission="com.example.MY_PERMISSION" />
```

5. Не полагайтесь на устаревшие или ограниченные broadcast-ы без проверки документации для целевой API-версии.

---

## Answer (EN)

**`BroadcastReceiver`** is one of the fundamental Android components that allows applications to **receive and respond to system-wide or app-specific broadcast messages**. It acts as a listener for `Intent` broadcasts sent by the Android system or other applications.

It is usually used for:

- reacting to system events (battery, boot, connectivity, locale, etc.)
- app-internal communication via custom broadcasts

Note: `onReceive()` is called on the main thread, so work must be fast and non-blocking.

### Core Concept

BroadcastReceivers enable communication between different parts of an app or between different apps using a publish-subscribe pattern: senders broadcast `Intent`s, and receivers handle only those `Intent`s whose actions/data/categories match their filters.

```kotlin
class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        when (intent?.action) {
            Intent.ACTION_BATTERY_LOW -> {
                Toast.makeText(context, "Battery is low!", Toast.LENGTH_SHORT).show()
            }
            Intent.ACTION_POWER_CONNECTED -> {
                Log.d("Receiver", "Power connected")
            }
        }
    }
}
```

### Types of Broadcasts by Origin

#### 1. System Broadcasts

The Android system sends broadcasts for various events, for example:

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
                updateTimeZone(context)
            }
            Intent.ACTION_LOCALE_CHANGED -> {
                updateLocale(context)
            }
        }
    }
}
```

Common system broadcasts (many are subject to background limits on modern Android):

- `ACTION_BATTERY_LOW` / `ACTION_BATTERY_OKAY` – battery status
- `ACTION_POWER_CONNECTED` / `ACTION_POWER_DISCONNECTED` – charging status
- `ACTION_BOOT_COMPLETED` – device finished booting
- `ACTION_SCREEN_ON` / `ACTION_SCREEN_OFF` – screen state (restricted in recent versions)
- `ACTION_AIRPLANE_MODE_CHANGED` – airplane mode toggled
- `ACTION_TIMEZONE_CHANGED` / `ACTION_DATE_CHANGED` – time and date changes

Always check current docs to ensure an action can still be received (especially from the manifest).

#### 2. Custom Broadcasts

Apps can send custom broadcasts:

```kotlin
class MainActivity : AppCompatActivity() {
    fun sendCustomBroadcast() {
        val intent = Intent("com.example.MY_CUSTOM_ACTION").apply {
            putExtra("message", "Hello from sender!")
        }
        // Global broadcast (visible to other apps if exported)
        sendBroadcast(intent)
    }

    fun sendOrderedBroadcast() {
        val intent = Intent("com.example.ORDERED_ACTION")
        sendOrderedBroadcast(intent, null)
    }
}

class CustomBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val message = intent?.getStringExtra("message")
        Log.d("Receiver", "Received: $message")
    }
}
```

For app-internal events on modern Android, prefer other patterns (callbacks, `LiveData`, `Flow`, shared `ViewModel`, etc.). `LocalBroadcastManager` is deprecated in AndroidX and kept only for legacy code.

---

### Registration Methods

#### 1. Static Registration (Manifest)

Declared in `AndroidManifest.xml`. A manifest-declared receiver can start the app process when a matching broadcast arrives.

Important:

- On modern Android (8.0+), many implicit system broadcasts can no longer be received this way.
- Explicit broadcasts (targeting your package) and some documented exceptions still work.

```xml
<manifest>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

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
</manifest>
```

Summary:

- works even when your app process is not running (for allowed actions)
- restricted for many implicit broadcasts on API 26+

#### 2. Dynamic Registration (Runtime)

Registered in code with `Context.registerReceiver`. The receiver is active only while the registering component (e.g., `Activity`, `Service`) is alive.

```kotlin
class MainActivity : AppCompatActivity() {
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val level = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
            val scale = intent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
            if (level >= 0 && scale > 0) {
                val batteryPct = level * 100f / scale
                Log.d("Battery", "Battery level: $batteryPct%")
            }
        }
    }

    override fun onResume() {
        super.onResume()
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_CHANGED)
            addAction(Intent.ACTION_POWER_CONNECTED)
            addAction(Intent.ACTION_POWER_DISCONNECTED)
        }
        registerReceiver(batteryReceiver, filter)
    }

    override fun onPause() {
        super.onPause()
        unregisterReceiver(batteryReceiver)
    }
}
```

Summary:

- active only while registered
- must be unregistered to avoid leaks and runtime exceptions

---

### Broadcast Delivery Types

#### Normal Broadcasts

Sent with `sendBroadcast()`. Delivered in an undefined order; receivers cannot prevent others from receiving the `Intent`.

```kotlin
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)
```

#### Ordered Broadcasts

Sent with `sendOrderedBroadcast()`. Delivered one at a time in priority order; each receiver can modify the result and (for some cases) abort further delivery.

```kotlin
val intent = Intent("com.example.ORDERED_ACTION")
sendOrderedBroadcast(intent, null)
```

Manifest example:

```xml
<receiver android:name=".HighPriorityReceiver">
    <intent-filter android:priority="1000">
        <action android:name="com.example.ORDERED_ACTION" />
    </intent-filter>
</receiver>
```

Receiver example:

```kotlin
class HighPriorityReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Process broadcast
        abortBroadcast() // For ordered broadcasts, stops propagation to lower-priority receivers
    }
}
```

Note: ordered broadcasts and `abortBroadcast()` are limited in modern Android; check docs before relying on them.

#### Local Broadcasts (Legacy)

`LocalBroadcastManager` was used for in-app broadcasts:

```kotlin
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("com.example.LOCAL_ACTION"))
```

However, `LocalBroadcastManager` is deprecated in AndroidX; prefer direct callbacks, `LiveData`, `Flow`, or other in-app communication patterns.

---

### Example: Network Change Receiver (Legacy Pattern)

Historically, apps listened for `ConnectivityManager.CONNECTIVITY_ACTION`:

```kotlin
class NetworkChangeReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            val cm = context?.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val activeNetwork = cm.activeNetworkInfo
            val isConnected = activeNetwork?.isConnectedOrConnecting == true

            Toast.makeText(
                context,
                if (isConnected) "Internet connected" else "No internet",
                Toast.LENGTH_SHORT
            ).show()
        }
    }
}
```

For modern apps targeting recent SDKs, prefer `ConnectivityManager.NetworkCallback` instead of this broadcast.

---

### Background Execution Limits (Android 8.0+)

From Android 8.0 (API 26), background execution and implicit broadcasts are restricted:

- Most implicit system broadcasts can no longer be received by manifest-registered receivers.
- Some documented exceptions (e.g. `ACTION_BOOT_COMPLETED`, `ACTION_LOCALE_CHANGED`, `ACTION_TIMEZONE_CHANGED`, `ACTION_MY_PACKAGE_REPLACED`, etc.) still work.
- Explicit broadcasts to your app are generally allowed.

Recommended approaches:

1. Register receivers dynamically while your app is in the foreground.
2. Use `JobScheduler` / `WorkManager` for deferred background work.
3. Use foreground services for long-running work triggered by broadcasts.

Example with WorkManager:

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()

val work = OneTimeWorkRequestBuilder<NetworkWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(work)
```

---

### Best Practices

1. Keep `onReceive()` short:

```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Do only lightweight work here
        val safeContext = context ?: return
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
        WorkManager.getInstance(safeContext).enqueue(workRequest)
    }
}
```

2. Always unregister dynamic receivers:

```kotlin
override fun onDestroy() {
    super.onDestroy()
    try {
        unregisterReceiver(myReceiver)
    } catch (e: IllegalArgumentException) {
        // Receiver was not registered or already unregistered
    }
}
```

3. Use in-app mechanisms (callbacks, shared ViewModels, coroutines, etc.) instead of global broadcasts when possible. Only use broadcasts when you truly need the decoupled, system-level pattern.

4. Set `android:exported` correctly:

```xml
<!-- Not accessible by other apps -->
<receiver
    android:name=".MyReceiver"
    android:exported="false" />

<!-- Accessible by other apps (consider protecting with a permission) -->
<receiver
    android:name=".PublicReceiver"
    android:exported="true"
    android:permission="com.example.MY_PERMISSION" />
```

5. Do not rely on deprecated or restricted broadcasts without checking the documentation for your target API level.

---

### Summary (RU)

`BroadcastReceiver`:

- слушает системные и пользовательские широковещательные `Intent`-ы;
- может регистрироваться статически (манифест) или динамически (в коде);
- выполняет `onReceive()` в главном потоке, поэтому логика должна быть легковесной;
- подчиняется строгим ограничениям фонового выполнения и implicit broadcast-ов на Android 8.0+;
- подходит для реакции на системные события и для слабо связанных уведомлений между компонентами.

---

### Summary (EN)

`BroadcastReceiver` is an Android component that:

- listens for system-wide or app-specific broadcast `Intent`s;
- can be registered in manifest or dynamically at runtime;
- executes `onReceive()` on the main thread (must be quick);
- is subject to significant background and implicit broadcast limits on Android 8.0+.

Use it to:

- react to system events;
- enable decoupled communication via broadcasts;

while following modern best practices and avoiding reliance on deprecated or restricted behaviors.

---

## Дополнительные вопросы (RU)

- Как ограничения фонового выполнения Android 8.0+ влияют на использование `BroadcastReceiver`?
- Когда стоит использовать broadcast вместо внутриприложечных механизмов коммуникации?
- В чем разница между обычными и упорядоченными broadcast-ами?

## Follow-ups

- How do Android 8.0+ background execution limits affect `BroadcastReceiver` usage?
- When should you use a broadcast vs an in-app communication mechanism?
- What's the difference between ordered and normal broadcasts?

---

## Ссылки (RU)

- https://developer.android.com/guide/components/broadcasts
- https://developer.android.com/guide/components/broadcast-exceptions

## References

- https://developer.android.com/guide/components/broadcasts
- https://developer.android.com/guide/components/broadcast-exceptions

---

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-broadcast-receiver]]
- [[c-intent]]

### Связанные (Easy)

- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast

### Продвинутые (Harder)

- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast
- [[q-kotlin-context-receivers--android--hard]] - Broadcast

## Related Questions

### Prerequisites / Concepts

- [[c-broadcast-receiver]]
- [[c-intent]]

### Related (Easy)

- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast

### Advanced (Harder)

- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast
- [[q-kotlin-context-receivers--android--hard]] - Broadcast
