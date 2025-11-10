---
id: android-430
title: Privacy Sandbox SDK Runtime / Privacy Sandbox SDK Runtime
aliases:
- Privacy Sandbox
- Privacy Sandbox SDK Runtime
- SDK Runtime
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
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android/permissions
- android/privacy-sdks
- difficulty/hard
- security/privacy
- android
---

# Вопрос (RU)

> Что такое SDK Runtime в Privacy Sandbox? Как он изолирует сторонние SDK? Какие вызовы возникают при миграции SDK в sandbox-окружение и как обрабатывать cross-sandbox коммуникацию?

---

# Question (EN)

> What is the SDK Runtime in Privacy Sandbox? How does it isolate third-party SDKs? What are the challenges of migrating SDKs to the runtime environment and how do you handle cross-sandbox communication?

---

## Ответ (RU)

**SDK Runtime** — компонент Privacy Sandbox (Android 13+ и совместимых билдах), запускающий сторонние SDK в изолированных процессах (SDK sandbox), чтобы ограничить их доступ к данным приложения и пользователя. SDK получает доступ только к разрешённому подмножеству платформенных API и данным, явно предоставленным приложением. Коммуникация с хост-приложением и другими компонентами идёт через Binder IPC с ограниченными возможностями.

### Архитектура SDK Runtime

**Ключевые концепции:**
- **Process Isolation** — каждый SDK (или группа SDK) работает в отдельном sandbox-процессе, логически отделённом от процесса приложения.
- **Limited Access** — прямого доступа к внутренним данным приложения (SharedPreferences, internal storage), его runtime permissions и device identifiers нет; SDK оперирует тем, что предоставляет хост и разрешённые системные API.
- **Binder IPC** — вся коммуникация SDK с приложением и обратно идёт через Binder-интерфейсы, предоставленные SDK Runtime.
- **Resource Quotas** — ограничения на CPU, память, сеть и др. для снижения влияния SDK на приложение и систему.
- **Privacy Protection** — SDK не видит стабильные device IDs и чувствительные данные, если их явно не проксирует приложение в допустимой форме.

```
App Process <-> SDK Runtime Process <-> Network/Services
     |                 |
  App Code        SDK Code (isolated)
```

**Ограничения SDK (упрощённо):**
- Нет прямого доступа к хранилищу приложения (SharedPreferences, internal files) — данные должны приходить от хост-приложения или использовать разрешённые механизмы.
- Нет доступа к device identifiers и сигналы обрабатываются в соответствии с Privacy Sandbox (ID ограничены / проксируются).
- Нет доступа к runtime permissions приложения и их результатам напрямую — права проверяет приложение и при необходимости передаёт данные SDK.
- Нельзя напрямую управлять компонентами приложения (activities/services/broadcast receivers) из sandbox без участия хоста; взаимодействие делается через согласованные IPC-протоколы.
- Нет произвольного доступа к другим приложениям.

### Загрузка SDK В Sandbox

```kotlin
class SdkRuntimeManager(private val context: Context) {
    private val sdkSandboxManager: SdkSandboxManager? =
        context.getSystemService(SdkSandboxManager::class.java)

    private val executor: Executor = ContextCompat.getMainExecutor(context)

    suspend fun loadSdk(sdkName: String, params: Bundle): Result<SandboxedSdk> {
        val manager = sdkSandboxManager
            ?: return Result.failure(IllegalStateException("SdkSandboxManager not available"))

        return try {
            val sandboxedSdk = suspendCancellableCoroutine<SandboxedSdk> { cont ->
                manager.loadSdk(
                    sdkName,
                    params,
                    executor,
                    object : OutcomeReceiver<SandboxedSdk, LoadSdkException> {
                        override fun onResult(result: SandboxedSdk) {
                            if (cont.isActive) cont.resume(result)
                        }

                        override fun onError(error: LoadSdkException) {
                            if (cont.isActive) cont.resumeWithException(error)
                        }
                    }
                )

                cont.invokeOnCancellation {
                    // Здесь при необходимости можно отменять операции загрузки,
                    // если используется соответствующая поддержка.
                }
            }
            Result.success(sandboxedSdk)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getSdkInterface(sdk: SandboxedSdk): IBinder? = sdk.getInterface()
}
```

Асинхронная загрузка через coroutines (поверх async API `loadSdk`)
Корректное использование `Executor` и проверка доступности `SdkSandboxManager`
`IBinder` как точка входа для IPC с SDK

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

Точка входа — `onLoadSdk()`
IBinder-интерфейс (`ISdkApi`) для IPC с приложением
Освобождение ресурсов в `beforeUnloadSdk()`

### App-Side Integration

```kotlin
class SandboxedAdClient(
    private val runtimeManager: SdkRuntimeManager
) {
    private var sdkInterface: ISdkApi? = null

    suspend fun initialize(apiKey: String): Result<Unit> {
        val params = Bundle().apply { putString("apiKey", apiKey) }
        val sandboxedSdk = runtimeManager.loadSdk("com.example.adsdk", params)
            .getOrElse { return Result.failure(it) }

        val binder = sandboxedSdk.getInterface()
            ?: return Result.failure(IllegalStateException("SDK interface is null"))

        sdkInterface = ISdkApi.Stub.asInterface(binder)

        val result = sdkInterface?.initialize(Bundle.EMPTY)
            ?: return Result.failure(IllegalStateException("SDK initialization failed"))

        return if (result.getBoolean("success")) {
            Result.success(Unit)
        } else {
            Result.failure(Exception(result.getString("error")))
        }
    }

    suspend fun loadAd(adType: String): Result<String> {
        val api = sdkInterface ?: return Result.failure(Exception("SDK not initialized"))

        val params = Bundle().apply { putString("adType", adType) }
        val result = api.performAction("loadAd", params)

        return if (result.getBoolean("success")) {
            Result.success(result.getString("adId") ?: "")
        } else {
            Result.failure(Exception(result.getString("error")))
        }
    }
}
```

Использование AIDL-интерфейса через `Stub.asInterface()`
`Bundle` как транспорт для данных через Binder
Обработка ошибок и null-случаев через `Result`

### Вызовы Миграции SDK

**1. Архитектурные изменения:**
- Переход на Binder IPC (вместо прямых in-process вызовов).
- Сериализация данных через `Bundle`/parcelables.
- Асинхронная модель взаимодействия практически обязательна на практике из-за IPC/latency и асинхронных API загрузки SDK.

**2. Функциональные ограничения:**
- Persistent storage — SDK не может самостоятельно писать в хранилище приложения; хост-приложение передаёт конфигурацию/кеш по согласованному протоколу.
- Background execution — SDK работает в рамках ограничений sandbox-процесса; долгоживущие задачи требуют координации с приложением.
- Direct permissions — SDK не запрашивает и не использует runtime permissions напрямую; приложение проверяет права и предоставляет агрегированные данные/сигналы.

**3. Обход ограничений (через явный контракт с приложением):**

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

Проверка наличия SDK Runtime перед использованием
Fallback к традиционному in-app SDK при отсутствии Sandbox
Единый интерфейс (adapter) для хост-приложения

### Лучшие Практики

**Миграция:**
- Постепенная стратегия с fallback на традиционный SDK.
- Поддержка обеих версий SDK на переходный период.
- Тщательное тестирование на разных версиях Android и разных конфигурациях Privacy Sandbox.

**Коммуникация:**
- Предпочитать лёгкие, агрегированные Binder-вызовы.
- Эффективно формировать `Bundle` (избегать больших payload-ов).
- Закладывать таймауты и обработку ошибок для IPC.
- Избегать частых синхронных вызовов, блокирующих UI.

**Приватность:**
- Передавать только необходимые агрегированные данные.
- Анонимизировать или псевдонимизировать user IDs.
- Не передавать стабильные device identifiers и персональные данные без строгой необходимости и соответствия политике.

**Ресурсы:**
- Мониторинг использования CPU/memory/network SDK в sandbox (по доступным метрикам).
- Освобождение ресурсов в `beforeUnloadSdk()` и при ошибках.
- Тестирование на low-end устройствах и при ограничениях сети.

### Распространённые Ошибки

1. Передача чувствительных данных → нарушения приватности и политик.
   - Решение: минимизация и анонимизация данных, проверка против требований Privacy Sandbox.

2. Игнорирование ошибок `loadSdk` → краши/"тихий" отказ SDK.
   - Решение: использовать `Result`, fallback-механизмы и явную обработку ошибок.

3. Сложные и частые Binder-вызовы → проблемы с производительностью.
   - Решение: батчинг, асинхронность, лёгкие объёмы данных.

4. Отсутствие fallback → сломанное приложение на устройствах без SDK Runtime.
   - Решение: feature detection + традиционный SDK.

5. Предположение о permissions приложения внутри SDK → сбои логики.
   - Решение: полагаться на данные, которые передаёт приложение, и не вызывать запрещённые API напрямую.

---

## Answer (EN)

**SDK Runtime** is a Privacy Sandbox component (on Android 13+ and supported builds) that runs third-party SDKs in an isolated SDK sandbox process to restrict their access to app and user data. The SDK can use only a constrained subset of platform APIs and data explicitly provided by the host app. Communication with the host app and other components occurs through Binder IPC under strict controls.

### SDK Runtime Architecture

**Key Concepts:**
- **Process Isolation** — each SDK (or group of SDKs) runs in a separate sandbox process, logically separated from the app process.
- **Limited Access** — no direct access to the host app's internal data (SharedPreferences, internal storage), its runtime permissions, or stable device identifiers; the SDK relies on host-provided data and allowed system APIs.
- **Binder IPC** — all communication between the SDK and the app uses Binder interfaces exposed through the SDK Runtime.
- **Resource Quotas** — CPU, memory, and network usage are constrained to limit the SDK's impact on the app and system.
- **Privacy Protection** — SDKs do not see stable device IDs or sensitive data unless explicitly (and compliantly) proxied by the host.

```
App Process <-> SDK Runtime Process <-> Network/Services
     |                 |
  App Code        SDK Code (isolated)
```

**SDK Limitations (simplified):**
- No direct access to the host app's storage (SharedPreferences, internal files); data must come from the host app or allowed mechanisms.
- No direct access to device identifiers; signals and identifiers are mediated/limited under Privacy Sandbox policies.
- No direct access to the app's runtime permissions state; the app performs checks and passes only necessary data.
- Cannot directly control app components (activities/services/broadcast receivers) from the sandbox without cooperation from the host; interactions are via explicit IPC contracts.
- No arbitrary access to other apps.

### Loading SDK in Sandbox

```kotlin
class SdkRuntimeManager(private val context: Context) {
    private val sdkSandboxManager: SdkSandboxManager? =
        context.getSystemService(SdkSandboxManager::class.java)

    private val executor: Executor = ContextCompat.getMainExecutor(context)

    suspend fun loadSdk(sdkName: String, params: Bundle): Result<SandboxedSdk> {
        val manager = sdkSandboxManager
            ?: return Result.failure(IllegalStateException("SdkSandboxManager not available"))

        return try {
            val sandboxedSdk = suspendCancellableCoroutine<SandboxedSdk> { cont ->
                manager.loadSdk(
                    sdkName,
                    params,
                    executor,
                    object : OutcomeReceiver<SandboxedSdk, LoadSdkException> {
                        override fun onResult(result: SandboxedSdk) {
                            if (cont.isActive) cont.resume(result)
                        }

                        override fun onError(error: LoadSdkException) {
                            if (cont.isActive) cont.resumeWithException(error)
                        }
                    }
                )

                cont.invokeOnCancellation {
                    // Optionally cancel outstanding work if supported.
                }
            }
            Result.success(sandboxedSdk)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getSdkInterface(sdk: SandboxedSdk): IBinder? = sdk.getInterface()
}
```

Async loading using coroutines over the async `loadSdk` API
Proper `Executor` usage and `SdkSandboxManager` availability check
`IBinder` as the IPC entry point to the SDK

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

Entry point via `onLoadSdk()`
IBinder-based `ISdkApi` interface for IPC with the host app
Cleanup in `beforeUnloadSdk()`

### App-Side Integration

```kotlin
class SandboxedAdClient(
    private val runtimeManager: SdkRuntimeManager
) {
    private var sdkInterface: ISdkApi? = null

    suspend fun initialize(apiKey: String): Result<Unit> {
        val params = Bundle().apply { putString("apiKey", apiKey) }
        val sandboxedSdk = runtimeManager.loadSdk("com.example.adsdk", params)
            .getOrElse { return Result.failure(it) }

        val binder = sandboxedSdk.getInterface()
            ?: return Result.failure(IllegalStateException("SDK interface is null"))

        sdkInterface = ISdkApi.Stub.asInterface(binder)

        val result = sdkInterface?.initialize(Bundle.EMPTY)
            ?: return Result.failure(IllegalStateException("SDK initialization failed"))

        return if (result.getBoolean("success")) {
            Result.success(Unit)
        } else {
            Result.failure(Exception(result.getString("error")))
        }
    }

    suspend fun loadAd(adType: String): Result<String> {
        val api = sdkInterface ?: return Result.failure(Exception("SDK not initialized"))

        val params = Bundle().apply { putString("adType", adType) }
        val result = api.performAction("loadAd", params)

        return if (result.getBoolean("success")) {
            Result.success(result.getString("adId") ?: "")
        } else {
            Result.failure(Exception(result.getString("error")))
        }
    }
}
```

Uses AIDL-generated interface via `Stub.asInterface()`
Uses `Bundle` for cross-process data transfer
Handles errors and nulls via `Result`

### SDK Migration Challenges

**1. Architectural Changes:**
- Switch from in-process calls to Binder IPC between app and SDK.
- Serialize data via `Bundle`/parcelables for IPC.
- Adopt an asynchronous interaction model in practice due to IPC latency and async `loadSdk`.

**2. Functional Limitations:**
- Persistent storage — SDK cannot write directly to the app's storage; the app provides configuration/cache via agreed protocol.
- Background execution — SDK work is constrained by the sandbox process; long-running/background tasks require coordination with the host app.
- Direct permissions — SDK cannot request/use runtime permissions directly; the host app validates permissions and passes derived data only.

**3. Workarounds (via explicit host-SDK contracts):**

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

Feature detection before using SDK Runtime
Fallback to traditional SDK when sandbox is unavailable
Adapter-style unified interface for the app

### Best Practices

**Migration:**
- Use a gradual rollout strategy with a fallback to the traditional SDK.
- Support both SDK variants during transition.
- Test across Android versions and Privacy Sandbox configurations.

**Communication:**
- Prefer lightweight, batched Binder calls.
- Use efficient `Bundle` payloads (avoid large data transfers).
- Implement timeouts and robust error handling for IPC.
- Avoid frequent synchronous calls that block the UI.

**Privacy:**
- Send only necessary, aggregated data.
- Anonymize or pseudonymize user IDs.
- Do not send stable device identifiers or personal data without strict necessity and policy compliance.

**Resources:**
- Monitor SDK CPU/memory/network usage where possible.
- Release resources in `beforeUnloadSdk()` and on failure paths.
- Test behavior on low-end devices and under constrained conditions.

### Common Pitfalls

1. Passing sensitive data → privacy/policy violations.
   - Solution: minimize/anonymize data; align with Privacy Sandbox requirements.

2. Ignoring `loadSdk` failures → crashes or silent SDK breakage.
   - Solution: use `Result`, explicit error handling, and fallbacks.

3. Overly chatty or heavy Binder calls → performance issues.
   - Solution: async patterns, batching, lightweight payloads.

4. No fallback path → broken behavior on devices without SDK Runtime.
   - Solution: feature detection and traditional SDK fallback.

5. Assuming app permissions inside the SDK → logic failures.
   - Solution: rely only on data explicitly supplied by the host app; avoid restricted APIs.

---

## Дополнительные вопросы (RU)

- Что происходит, если SDK превышает квоты ресурсов?
- Как обрабатывать падения SDK в sandbox?
- Могут ли несколько SDK безопасно шарить данные внутри sandbox?
- Какие API доступны в SDK Runtime?
- Как отлаживать sandboxed SDK?
- Каков overhead по производительности из-за изоляции процесса?

## Follow-ups

- What happens if SDK exceeds resource quotas?
- How to handle SDK crashes in sandbox?
- Can multiple SDKs share data in sandbox?
- What APIs are available in SDK Runtime?
- How to debug sandboxed SDKs?
- What's the performance overhead of process isolation?

## Ссылки (RU)

- [Android Privacy Sandbox](https://developer.android.com/design-for-safety/privacy-sandbox)
- [SDK Runtime Overview](https://developer.android.com/design-for-safety/privacy-sandbox/sdk-runtime)
- [SdkSandboxManager API](https://developer.android.com/reference/android/app/sdksandbox/SdkSandboxManager)

## References

- [Android Privacy Sandbox](https://developer.android.com/design-for-safety/privacy-sandbox)
- [SDK Runtime Overview](https://developer.android.com/design-for-safety/privacy-sandbox/sdk-runtime)
- [SdkSandboxManager API](https://developer.android.com/reference/android/app/sdksandbox/SdkSandboxManager)

## Related Questions

### Prerequisites / Concepts

- [[c-permissions]]
