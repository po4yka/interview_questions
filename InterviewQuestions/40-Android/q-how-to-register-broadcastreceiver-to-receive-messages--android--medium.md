---
id: android-163
title: "How To Register Broadcastreceiver To Receive Messages / Как зарегистрировать BroadcastReceiver для получения сообщений"
aliases: ["How To Register BroadcastReceiver", "Как зарегистрировать BroadcastReceiver"]
topic: android
subtopics: [broadcast-receiver, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-broadcast-receiver, q-what-is-broadcastreceiver--android--easy]
created: 2025-10-15
updated: 2025-01-27
tags: [android, android/broadcast-receiver, android/lifecycle, difficulty/medium]
sources: []
---

# Вопрос (RU)

Как зарегистрировать BroadcastReceiver для получения сообщений?

# Question (EN)

How to register BroadcastReceiver to receive messages?

## Ответ (RU)

Существует **два способа** регистрации [[c-broadcast-receiver|BroadcastReceiver]]:

### 1. Динамическая Регистрация (Runtime)

Регистрируется программно через IntentFilter:

```kotlin
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // ✅ Обработка broadcast
            when (intent?.action) {
                ConnectivityManager.CONNECTIVITY_ACTION -> {
                    // Проверка сети
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(receiver, filter)  // ✅ Регистрация
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)  // ✅ Обязательно отменить регистрацию
    }
}
```

**Преимущества:**
- Работает только когда компонент активен
- Нет ограничений на implicit broadcasts
- Более эффективно по памяти

**Недостатки:**
- Требует явной отмены регистрации
- Не работает когда приложение закрыто

### 2. Статическая Регистрация (Manifest)

Регистрируется в AndroidManifest.xml:

```xml
<receiver
    android:name=".BootReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            // ✅ Запуск сервиса после перезагрузки
            val serviceIntent = Intent(context, MyService::class.java)
            context?.startService(serviceIntent)
        }
    }
}
```

**Преимущества:**
- Работает даже когда приложение закрыто
- Автоматическая отмена регистрации

**Недостатки:**
- Ограничения с Android 8+ для implicit broadcasts
- Всегда в памяти

### Современные Альтернативы

```kotlin
// ❌ Устарело: LocalBroadcastManager
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("action"))

// ✅ Используйте Flow
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events = _events.asSharedFlow()

    suspend fun emit(event: Event) = _events.emit(event)
}
```

**Когда использовать:**
- **Dynamic:** UI обновления, временные слушатели
- **Static:** BOOT_COMPLETED, SMS (требует разрешений)
- **WorkManager:** Фоновые задачи с ограничениями
- **Flow/LiveData:** Внутриприложенческие события

## Answer (EN)

There are **two ways** to register a [[c-broadcast-receiver|BroadcastReceiver]]:

### 1. Dynamic Registration (Runtime)

Register programmatically using IntentFilter:

```kotlin
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // ✅ Handle broadcast
            when (intent?.action) {
                ConnectivityManager.CONNECTIVITY_ACTION -> {
                    // Check network
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(receiver, filter)  // ✅ Register
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)  // ✅ Must unregister
    }
}
```

**Advantages:**
- Active only when component is alive
- No restrictions on implicit broadcasts
- More memory efficient

**Disadvantages:**
- Requires explicit unregistration
- Doesn't work when app is closed

### 2. Static Registration (Manifest)

Declare in AndroidManifest.xml:

```xml
<receiver
    android:name=".BootReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            // ✅ Start service after reboot
            val serviceIntent = Intent(context, MyService::class.java)
            context?.startService(serviceIntent)
        }
    }
}
```

**Advantages:**
- Works even when app is closed
- Automatic unregistration

**Disadvantages:**
- Restrictions from Android 8+ for implicit broadcasts
- Always in memory

### Modern Alternatives

```kotlin
// ❌ Deprecated: LocalBroadcastManager
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("action"))

// ✅ Use Flow instead
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events = _events.asSharedFlow()

    suspend fun emit(event: Event) = _events.emit(event)
}
```

**When to use:**
- **Dynamic:** UI updates, temporary listeners
- **Static:** BOOT_COMPLETED, SMS (requires permissions)
- **WorkManager:** Background tasks with constraints
- **Flow/LiveData:** In-app events

## Follow-ups

- What happens if you forget to unregister a dynamically registered receiver?
- How does Android handle priority in ordered broadcasts?
- What are the security implications of using exported receivers?
- When should you prefer WorkManager over BroadcastReceiver?
- How do you test BroadcastReceiver implementations?

## References

- [[c-broadcast-receiver]] - BroadcastReceiver concept
- Android Developers: BroadcastReceiver guide
- Android Developers: Implicit broadcast limitations

---

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-broadcastreceiver--android--easy]] - What is BroadcastReceiver

### Related (Medium)
- [[q-what-does-the-lifecycle-library-do--android--medium]] - Lifecycle management
- [[q-how-animations-work-in-recyclerview--android--medium]] - Component lifecycle

### Advanced (Harder)
- [[q-why-was-the-lifecycle-library-created--android--hard]] - Advanced lifecycle concepts
