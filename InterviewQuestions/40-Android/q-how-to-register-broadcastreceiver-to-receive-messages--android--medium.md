---\
id: android-163
title: "How To Register Broadcastreceiver To Receive Messages / Как зарегистрировать BroadcastReceiver для получения сообщений"
aliases: ["How To Register BroadcastReceiver", "Как зарегистрировать BroadcastReceiver"]
topic: android
subtopics: [broadcast-receiver]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-broadcast-receiver, q-what-is-broadcastreceiver--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/broadcast-receiver, difficulty/medium]
sources: []
anki_cards:
  - slug: android-163-0-en
    front: "How to register a BroadcastReceiver in Android?"
    back: |
      **Dynamic (runtime):**
      ```kotlin
      registerReceiver(receiver, IntentFilter("action"),
          RECEIVER_NOT_EXPORTED) // API 33+
      unregisterReceiver(receiver) // in onStop
      ```

      **Static (manifest):**
      ```xml
      <receiver android:name=".BootReceiver"
          android:exported="false">
          <intent-filter>
              <action android:name="android.intent.action.BOOT_COMPLETED"/>
          </intent-filter>
      </receiver>
      ```

      **Dynamic:** Lives with component. **Static:** Survives process death
    tags:
      - android_general
      - difficulty::medium
  - slug: android-163-0-ru
    front: "Как зарегистрировать BroadcastReceiver в Android?"
    back: |
      **Динамическая (runtime):**
      ```kotlin
      registerReceiver(receiver, IntentFilter("action"),
          RECEIVER_NOT_EXPORTED) // API 33+
      unregisterReceiver(receiver) // в onStop
      ```

      **Статическая (manifest):**
      ```xml
      <receiver android:name=".BootReceiver"
          android:exported="false">
          <intent-filter>
              <action android:name="android.intent.action.BOOT_COMPLETED"/>
          </intent-filter>
      </receiver>
      ```

      **Динамическая:** Живёт с компонентом. **Статическая:** Переживает смерть процесса
    tags:
      - android_general
      - difficulty::medium

---\
# Вопрос (RU)

> Как зарегистрировать `BroadcastReceiver` для получения сообщений?

# Question (EN)

> How to register `BroadcastReceiver` to receive messages?

## Ответ (RU)

Существует **два основных способа** регистрации [[c-broadcast-receiver|`BroadcastReceiver`]]:

### 1. Динамическая Регистрация (Runtime)

Регистрируется программно через `IntentFilter` внутри компонента (`Activity`, `Service`, др.). На современных версиях Android важно учитывать флаги экспорта и ограничения фонового выполнения.

```kotlin
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // ✅ Обработка broadcast
            when (intent?.action) {
                "com.example.ACTION_CUSTOM" -> {
                    // Обработка своего кастомного события
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter("com.example.ACTION_CUSTOM")
        // На Android 13+ (API 33+) рекомендуется указывать RECEIVER_EXPORTED/NOT_EXPORTED
        registerReceiver(
            receiver,
            filter,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU)
                RECEIVER_NOT_EXPORTED
            else
                0
        ) // ✅ Регистрация во время жизни Activity
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)  // ✅ Обязательно отменить регистрацию
    }
}
```

**Преимущества:**
- Принимает только пока компонент (`Activity`/`Service` и процесс приложения) жив
- Нет привязки к манифесту; удобно для временных слушателей и UI-событий
- Можно регистрировать на runtime с учётом логики, разрешений и флагов экспорта (API 33+)

**Недостатки / ограничения:**
- Требует явной отмены регистрации (иначе риск утечки контекста/исключений)
- Не будет получать сообщения, когда компонент уничтожен и процесс приложения выгружен
- Ограничения фона и implicit broadcasts на новых Android всё равно действуют (некоторые системные широковещательные сообщения доставляются только manifest-receiver'ам)

### 2. Статическая Регистрация (Manifest)

Регистрируется в AndroidManifest.xml (актуально для системных событий, например BOOT_COMPLETED, SMS_RECEIVED и др.):

```xml
<receiver
    android:name=".BootReceiver"
    android:enabled="true"
    android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            // ✅ Запуск фоновой работы после перезагрузки
            // Начиная с Android 8.0 используйте JobIntentService, WorkManager
            // или startForegroundService с последующим переводом сервиса в foreground.
        }
    }
}
```

(Значение `android:exported` должно соответствовать требованиям безопасности: `true`, если ресивер должен быть доступен другим приложениям; `false`, если он предназначен только для внутриприложенческого использования.)

**Преимущества:**
- Может срабатывать даже когда UI не запущен (система поднимает процесс под broadcast)
- Регистрация описана в манифесте и не требует ручного `unregisterReceiver`

**Недостатки / ограничения:**
- С Android 8+ есть серьёзные ограничения на implicit broadcasts и фоновое выполнение
- Нельзя считать, что ресивер "всегда в памяти": он создаётся только на время обработки onReceive; частые системные события могут влиять на ресурсы

### Современные Альтернативы

```kotlin
// DEPRECATED: LocalBroadcastManager устарел в AndroidX и не рекомендован к использованию
// LocalBroadcastManager.getInstance(context)
//     .sendBroadcast(Intent("action"))

// ✅ Предпочитайте Flow/LiveData/EventBus-подходы для внутриприложенческих событий,
// но помните, что они не заменяют системные broadcast'ы и работают только внутри процесса.
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events = _events.asSharedFlow()

    suspend fun emit(event: Event) = _events.emit(event)
}
```

**Когда использовать:**
- **Dynamic:** обновление UI, временные слушатели внутри живого компонента
- **Static (Manifest):** системные события (BOOT_COMPLETED, SMS_RECEIVED и т.п. — с учётом разрешений, `android:exported` и ограничений платформы)
- **WorkManager/JobScheduler:** долговременные фоновые задачи с условиями (сеть, зарядка и др.) вместо прямого запуска сервиса из ресивера
- **`Flow`/`LiveData`:** внутриприложенческие события и коммуникация между компонентами без системных broadcast'ов

## Answer (EN)

There are **two primary ways** to register a [[c-broadcast-receiver|`BroadcastReceiver`]]:

### 1. Dynamic Registration (Runtime)

Register programmatically using an `IntentFilter` inside a component (`Activity`, `Service`, etc.). On modern Android versions you must also consider export flags and background limitations.

```kotlin
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            // ✅ Handle broadcast
            when (intent?.action) {
                "com.example.ACTION_CUSTOM" -> {
                    // Handle your custom event
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter("com.example.ACTION_CUSTOM")
        // On Android 13+ (API 33+), specify RECEIVER_EXPORTED/NOT_EXPORTED when registering
        registerReceiver(
            receiver,
            filter,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU)
                RECEIVER_NOT_EXPORTED
            else
                0
        ) // ✅ Register tied to Activity lifecycle
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)  // ✅ Must unregister to avoid leaks/crashes
    }
}
```

**Advantages:**
- Active only while the component (`Activity`/`Service` and app process) is alive
- Not tied to manifest; convenient for temporary listeners and UI-related events
- Can be registered conditionally at runtime (permissions, feature flags, export flags on API 33+, etc.)

**Disadvantages / limitations:**
- Requires explicit unregistration (risk of leaks or `IllegalArgumentException`)
- Will not receive broadcasts once the component is destroyed and the process is killed
- Background execution and implicit broadcast limitations on modern Android still apply (some system broadcasts only go to manifest-declared receivers)

### 2. Static Registration (Manifest)

Declare in AndroidManifest.xml (suitable for certain system events like BOOT_COMPLETED, SMS_RECEIVED, etc.):

```xml
<receiver
    android:name=".BootReceiver"
    android:enabled="true"
    android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            // ✅ Start background work after reboot
            // From Android 8.0 onward, use JobIntentService, WorkManager,
            // or startForegroundService and move the service to foreground.
        }
    }
}
```

(`android:exported` must reflect your security requirements: `true` if other apps are allowed to send broadcasts to this receiver; `false` if it is only for in-app/system broadcasts targeted at your app.)

**Advantages:**
- Can trigger even when the UI is not running (system starts the process for the broadcast)
- Registration is defined in the manifest; no manual `unregisterReceiver` is needed

**Disadvantages / limitations:**
- From Android 8+ many implicit broadcasts are restricted; background execution limits apply
- The receiver is not "always in memory"; it is created only while handling `onReceive`, and frequent triggers may impact resources

### Modern Alternatives

```kotlin
// DEPRECATED: LocalBroadcastManager is deprecated in AndroidX and not recommended
// LocalBroadcastManager.getInstance(context)
//     .sendBroadcast(Intent("action"))

// ✅ Prefer Flow/LiveData/EventBus-style patterns for in-app events only;
// they do not receive or replace system broadcasts.
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events = _events.asSharedFlow()

    suspend fun emit(event: Event) = _events.emit(event)
}
```

**When to use:**
- **Dynamic:** UI updates, temporary listeners bound to the lifecycle of an `Activity`/`Service`
- **Static (Manifest):** system events (BOOT_COMPLETED, SMS_RECEIVED, etc.), with required permissions, correct `android:exported` value, and platform limits
- **WorkManager/JobScheduler:** reliable deferred/background work with constraints instead of directly starting long-running services from a receiver
- **`Flow`/`LiveData`:** in-app events and communication between components without relying on system broadcasts

## Дополнительные Вопросы (RU)

- Что произойдет, если забыть вызвать `unregisterReceiver` для динамически зарегистрированного ресивера?
- Как Android обрабатывает приоритет в упорядоченных (ordered) broadcast'ах?
- Каковы риски для безопасности при использовании экспортированных ресиверов?
- Когда стоит предпочесть `WorkManager` вместо `BroadcastReceiver`?
- Как тестировать реализации `BroadcastReceiver`?

## Follow-ups

- What happens if you forget to unregister a dynamically registered receiver?
- How does Android handle priority in ordered broadcasts?
- What are the security implications of using exported receivers?
- When should you prefer `WorkManager` over `BroadcastReceiver`?
- How do you test `BroadcastReceiver` implementations?

## Ссылки (RU)

- [[c-broadcast-receiver]] — концепция `BroadcastReceiver`
- Android Developers: руководство по `BroadcastReceiver`
- Android Developers: ограничения implicit broadcast'ов

## References

- [[c-broadcast-receiver]] - `BroadcastReceiver` concept
- Android Developers: `BroadcastReceiver` guide
- Android Developers: Implicit broadcast limitations

---

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-what-is-broadcastreceiver--android--easy]] - Что такое `BroadcastReceiver`

### Похожие (средний уровень)
- [[q-what-does-the-lifecycle-library-do--android--medium]] - Управление жизненным циклом
- [[q-how-animations-work-in-recyclerview--android--medium]] - Жизненный цикл компонента

### Продвинутые (сложнее)
- [[q-why-was-the-lifecycle-library-created--android--hard]] - Продвинутые концепции жизненного цикла

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-broadcastreceiver--android--easy]] - What is `BroadcastReceiver`

### Related (Medium)
- [[q-what-does-the-lifecycle-library-do--android--medium]] - `Lifecycle` management
- [[q-how-animations-work-in-recyclerview--android--medium]] - `Component` lifecycle

### Advanced (Harder)
- [[q-why-was-the-lifecycle-library-created--android--hard]] - Advanced lifecycle concepts
