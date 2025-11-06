---
id: android-430
title: Privacy Sandbox SDK Runtime / Privacy Sandbox SDK Runtime
aliases:
- Privacy Sandbox
- Privacy Sandbox SDK Runtime
- SDK Runtime
- Изоляция SDK
topic: android
subtopics:
- permissions
- privacy-sdks
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-permissions
- q-content-provider-security--android--hard
- q-custom-sandbox-implementation--android--hard
sources: []
created: 2025-10-15
updated: 2025-10-31
tags:
- android/permissions
- android/privacy-sdks
- difficulty/hard
- privacy
- sandboxing
date created: Saturday, November 1st 2025, 1:03:51 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Что такое SDK Runtime в Privacy Sandbox? Как он изолирует сторонние SDK? Какие вызовы возникают при миграции SDK в sandbox-окружение и как обрабатывать cross-sandbox коммуникацию?

---

# Question (EN)

> What is the SDK Runtime in Privacy Sandbox? How does it isolate third-party SDKs? What are the challenges of migrating SDKs to the runtime environment and how do you handle cross-sandbox communication?

---

## Ответ (RU)

**SDK Runtime** — компонент Privacy Sandbox, запускающий сторонние SDK в изолированных процессах, предотвращая доступ к данным приложения и пользователя. Коммуникация через Binder IPC с ограниченными возможностями.

### Архитектура SDK Runtime

**Ключевые концепции:**
- **Process Isolation** — SDK в отдельном процессе
- **Limited Access** — нет доступа к app data, storage, permissions
- **Binder IPC** — cross-process коммуникация
- **Resource Quotas** — лимиты CPU, памяти, сети
- **Privacy Protection** — нет user data, device IDs

```
App Process <-> SDK Runtime Process <-> Network/Services
     |                 |
  App Code        SDK Code (isolated)
```

**Ограничения SDK:**
- ❌ Нет storage/SharedPreferences
- ❌ Нет device identifiers
- ❌ Нет permissions приложения
- ❌ Не могут запускать activities/services
- ❌ Нет доступа к другим приложениям

### Загрузка SDK В Sandbox

```kotlin
class SdkRuntimeManager(private val context: Context) {
    private val sdkSandboxManager: SdkSandboxManager? =
        context.getSystemService(SdkSandboxManager::class.java)

    suspend fun loadSdk(sdkName: String, params: Bundle): Result<SandboxedSdk> {
        return try {
            val sandboxedSdk = suspendCancellableCoroutine<SandboxedSdk> { cont ->
                sdkSandboxManager?.loadSdk(
                    sdkName, params, executor,
                    object : OutcomeReceiver<SandboxedSdk, LoadSdkException> {
                        override fun onResult(result: SandboxedSdk) = cont.resume(result)
                        override fun onError(error: LoadSdkException) =
                            cont.resumeWithException(error)
                    }
                )
            }
            Result.success(sandboxedSdk)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getSdkInterface(sdk: SandboxedSdk): IBinder? = sdk.getInterface()
}
```

✅ **Асинхронная загрузка** с coroutines
✅ **Error handling** через Result
✅ **IBinder** для коммуникации

### SDK Provider Implementation

```kotlin
// Sandbox SDK должен наследовать SandboxedSdkProvider
abstract class BaseSandboxedSdkProvider : SandboxedSdkProvider() {

    override fun onLoadSdk(params: Bundle): SandboxedSdk {
        initializeSdk(params)
        return SandboxedSdk(SdkInterface())
    }

    override fun beforeUnloadSdk() {
        cleanupSdk()
    }

    inner class SdkInterface : ISdkApi.Stub() {
        override fun performAction(action: String, params: Bundle): Bundle {
            return when (action) {
                "loadAd" -> loadAd(params)
                "trackEvent" -> trackEvent(params)
                else -> Bundle().apply { putString("error", "Unknown action") }
            }
        }
    }
}
```

✅ **Entry point** — `onLoadSdk()`
✅ **IBinder interface** для IPC
✅ **Cleanup** в `beforeUnloadSdk()`

### App-Side Integration

```kotlin
class SandboxedAdClient(
    private val runtimeManager: SdkRuntimeManager
) {
    private var sdkInterface: ISdkApi? = null

    suspend fun initialize(apiKey: String): Result<Unit> {
        val params = Bundle().apply { putString("apiKey", apiKey) }
        val sandboxedSdk = runtimeManager.loadSdk("com.example.adsdk", params)
            .getOrThrow()

        val binder = sandboxedSdk.getInterface()
        sdkInterface = ISdkApi.Stub.asInterface(binder)

        val result = sdkInterface?.initialize(Bundle.EMPTY)
        return if (result?.getBoolean("success") == true) {
            Result.success(Unit)
        } else {
            Result.failure(Exception(result?.getString("error")))
        }
    }

    suspend fun loadAd(adType: String): Result<String> {
        val params = Bundle().apply { putString("adType", adType) }
        val result = sdkInterface?.performAction("loadAd", params)
            ?: return Result.failure(Exception("SDK not initialized"))

        return if (result.getBoolean("success")) {
            Result.success(result.getString("adId") ?: "")
        } else {
            Result.failure(Exception(result.getString("error")))
        }
    }
}
```

✅ **AIDL interface** через `Stub.asInterface()`
✅ **Bundle** для передачи данных
✅ **Result type** для error handling

### Вызовы Миграции SDK

**1. Архитектурные изменения:**
- Переход на Binder IPC (вместо прямых вызовов)
- Сериализация данных через Bundle
- Асинхронные операции обязательны

**2. Функциональные ограничения:**
- ❌ Persistent storage — приложение должно передавать config через Bundle
- ❌ Background execution — только в рамках жизненного цикла
- ❌ Direct permissions — app проверяет permissions, передаёт данные

**3. Обход ограничений:**

```kotlin
class SdkMigrationManager(private val context: Context) {

    fun shouldUseSandboxedSdk(): Boolean =
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
        context.packageManager.hasSystemFeature("android.software.sdk_sandbox")

    suspend fun initializeSdk(apiKey: String): SdkClient {
        return if (shouldUseSandboxedSdk()) {
            val runtimeManager = SdkRuntimeManager(context)
            SandboxedAdClient(runtimeManager).apply { initialize(apiKey) }
        } else {
            TraditionalAdClient(context).apply { initialize(apiKey) }
        }
    }
}
```

✅ **Feature detection** перед использованием
✅ **Fallback** к традиционному SDK
✅ **Adapter pattern** для унификации

### Лучшие Практики

**Миграция:**
- Постепенная стратегия с fallback
- Поддержка обеих версий SDK
- Тестирование на разных Android версиях

**Коммуникация:**
- ✅ Лёгкие Binder calls
- ✅ Efficient Bundles (избегать больших данных)
- ✅ Timeouts для IPC
- ❌ Избегать частых синхронных вызовов

**Приватность:**
- ✅ Передавать только необходимые данные
- ✅ Анонимизировать user IDs
- ❌ Не передавать device identifiers
- ❌ Не передавать personal information

**Ресурсы:**
- Мониторинг использования CPU/memory/network
- Release resources в `beforeUnloadSdk()`
- Тестирование на low-end устройствах

### Распространённые Ошибки

1. **Передача sensitive data** → нарушения приватности
   - Решение: только анонимизированные данные

2. **Игнорирование load failures** → краши
   - Решение: Result type, fallback mechanisms

3. **Сложные Binder calls** → performance issues
   - Решение: async operations, lightweight data

4. **Нет fallback** → сломанное приложение на старых версиях
   - Решение: feature detection, традиционный SDK

5. **Предположение о permissions** → SDK сбои
   - Решение: app проверяет permissions, передаёт результаты

---

## Answer (EN)

**SDK Runtime** is a Privacy Sandbox component that runs third-party SDKs in isolated processes, preventing access to app data and user information. Communication occurs through Binder IPC with limited capabilities.

### SDK Runtime Architecture

**Key Concepts:**
- **Process Isolation** — SDKs run in separate process
- **Limited Access** — no app data, storage, permissions
- **Binder IPC** — cross-process communication
- **Resource Quotas** — CPU, memory, network limits
- **Privacy Protection** — no user data, device IDs

```
App Process <-> SDK Runtime Process <-> Network/Services
     |                 |
  App Code        SDK Code (isolated)
```

**SDK Limitations:**
- ❌ No storage/SharedPreferences access
- ❌ No device identifiers
- ❌ No app permissions
- ❌ Cannot start activities/services
- ❌ No access to other apps

### Loading SDK in Sandbox

```kotlin
class SdkRuntimeManager(private val context: Context) {
    private val sdkSandboxManager: SdkSandboxManager? =
        context.getSystemService(SdkSandboxManager::class.java)

    suspend fun loadSdk(sdkName: String, params: Bundle): Result<SandboxedSdk> {
        return try {
            val sandboxedSdk = suspendCancellableCoroutine<SandboxedSdk> { cont ->
                sdkSandboxManager?.loadSdk(
                    sdkName, params, executor,
                    object : OutcomeReceiver<SandboxedSdk, LoadSdkException> {
                        override fun onResult(result: SandboxedSdk) = cont.resume(result)
                        override fun onError(error: LoadSdkException) =
                            cont.resumeWithException(error)
                    }
                )
            }
            Result.success(sandboxedSdk)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getSdkInterface(sdk: SandboxedSdk): IBinder? = sdk.getInterface()
}
```

✅ **Async loading** with coroutines
✅ **Error handling** via Result
✅ **IBinder** for communication

### SDK Provider Implementation

```kotlin
// Sandbox SDK must extend SandboxedSdkProvider
abstract class BaseSandboxedSdkProvider : SandboxedSdkProvider() {

    override fun onLoadSdk(params: Bundle): SandboxedSdk {
        initializeSdk(params)
        return SandboxedSdk(SdkInterface())
    }

    override fun beforeUnloadSdk() {
        cleanupSdk()
    }

    inner class SdkInterface : ISdkApi.Stub() {
        override fun performAction(action: String, params: Bundle): Bundle {
            return when (action) {
                "loadAd" -> loadAd(params)
                "trackEvent" -> trackEvent(params)
                else -> Bundle().apply { putString("error", "Unknown action") }
            }
        }
    }
}
```

✅ **Entry point** — `onLoadSdk()`
✅ **IBinder interface** for IPC
✅ **Cleanup** in `beforeUnloadSdk()`

### App-Side Integration

```kotlin
class SandboxedAdClient(
    private val runtimeManager: SdkRuntimeManager
) {
    private var sdkInterface: ISdkApi? = null

    suspend fun initialize(apiKey: String): Result<Unit> {
        val params = Bundle().apply { putString("apiKey", apiKey) }
        val sandboxedSdk = runtimeManager.loadSdk("com.example.adsdk", params)
            .getOrThrow()

        val binder = sandboxedSdk.getInterface()
        sdkInterface = ISdkApi.Stub.asInterface(binder)

        val result = sdkInterface?.initialize(Bundle.EMPTY)
        return if (result?.getBoolean("success") == true) {
            Result.success(Unit)
        } else {
            Result.failure(Exception(result?.getString("error")))
        }
    }

    suspend fun loadAd(adType: String): Result<String> {
        val params = Bundle().apply { putString("adType", adType) }
        val result = sdkInterface?.performAction("loadAd", params)
            ?: return Result.failure(Exception("SDK not initialized"))

        return if (result.getBoolean("success")) {
            Result.success(result.getString("adId") ?: "")
        } else {
            Result.failure(Exception(result.getString("error")))
        }
    }
}
```

✅ **AIDL interface** via `Stub.asInterface()`
✅ **Bundle** for data transfer
✅ **Result type** for error handling

### SDK Migration Challenges

**1. Architectural Changes:**
- Switch to Binder IPC (instead of direct calls)
- Data serialization via Bundle
- Async operations mandatory

**2. Functional Limitations:**
- ❌ Persistent storage — app must pass config via Bundle
- ❌ Background execution — only within lifecycle
- ❌ Direct permissions — app checks permissions, passes data

**3. Workarounds:**

```kotlin
class SdkMigrationManager(private val context: Context) {

    fun shouldUseSandboxedSdk(): Boolean =
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
        context.packageManager.hasSystemFeature("android.software.sdk_sandbox")

    suspend fun initializeSdk(apiKey: String): SdkClient {
        return if (shouldUseSandboxedSdk()) {
            val runtimeManager = SdkRuntimeManager(context)
            SandboxedAdClient(runtimeManager).apply { initialize(apiKey) }
        } else {
            TraditionalAdClient(context).apply { initialize(apiKey) }
        }
    }
}
```

✅ **Feature detection** before use
✅ **Fallback** to traditional SDK
✅ **Adapter pattern** for unification

### Best Practices

**Migration:**
- Gradual strategy with fallback
- Support both SDK versions
- Test on different Android versions

**Communication:**
- ✅ Lightweight Binder calls
- ✅ Efficient Bundles (avoid large data)
- ✅ Timeouts for IPC
- ❌ Avoid frequent synchronous calls

**Privacy:**
- ✅ Pass only necessary data
- ✅ Anonymize user IDs
- ❌ Don't pass device identifiers
- ❌ Don't pass personal information

**Resources:**
- Monitor CPU/memory/network usage
- Release resources in `beforeUnloadSdk()`
- Test on low-end devices

### Common Pitfalls

1. **Passing sensitive data** → privacy violations
   - Solution: only anonymized data

2. **Ignoring load failures** → crashes
   - Solution: Result type, fallback mechanisms

3. **Complex Binder calls** → performance issues
   - Solution: async operations, lightweight data

4. **No fallback** → broken app on older versions
   - Solution: feature detection, traditional SDK

5. **Assuming permissions** → SDK failures
   - Solution: app checks permissions, passes results

---

## Follow-ups

- What happens if SDK exceeds resource quotas?
- How to handle SDK crashes in sandbox?
- Can multiple SDKs share data in sandbox?
- What APIs are available in SDK Runtime?
- How to debug sandboxed SDKs?
- What's the performance overhead of process isolation?

## References

- [Android Privacy Sandbox](https://developer.android.com/design-for-safety/privacy-sandbox)
- [SDK Runtime Overview](https://developer.android.com/design-for-safety/privacy-sandbox/sdk-runtime)
- [SdkSandboxManager API](https://developer.android.com/reference/android/app/sdksandbox/SdkSandboxManager)

## Related Questions

### Prerequisites / Concepts

- [[c-permissions]]


### Prerequisites (Easier)
- [[q-service-thread--android--medium]] - Process/thread fundamentals
- [[q-process-isolation--android--medium]] - Android process isolation

### Related (Same Level)
- [[q-binder-ipc--android--hard]] - Binder IPC mechanisms
- [[q-content-provider-security--android--hard]] - Cross-process security

### Advanced (Harder)
- [[q-custom-sandbox-implementation--android--hard]] - Custom sandboxing strategies
