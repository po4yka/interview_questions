---\
id: android-430
title: Privacy Sandbox SDK Runtime / SDK Runtime в Privacy Sandbox
aliases: [Privacy Sandbox, Privacy Sandbox SDK Runtime, SDK Runtime]
topic: android
subtopics: [permissions, privacy-sdks]
question_kind: system-design
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-permissions, q-android-security-best-practices--android--medium, q-privacy-sandbox-attribution--android--medium, q-privacy-sandbox-fledge--android--hard, q-privacy-sandbox-topics-api--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-11
tags: [android, android/permissions, android/privacy-sdks, difficulty/hard, security/privacy]
anki_cards:
  - slug: android-430-0-en
    front: "What is SDK Runtime in Privacy Sandbox and how does it isolate SDKs?"
    back: |
      **SDK Runtime** - runs third-party SDKs in isolated sandbox process (Android 13+).

      **Key features:**
      - **Process Isolation** - separate sandbox process per app
      - **Limited Access** - no SharedPrefs, internal storage, device IDs
      - **Binder IPC** - all communication via `SdkSandboxManager`
      - **Resource Quotas** - CPU, memory, network limits

      **Migration challenges:**
      - Convert to IPC contracts
      - Handle storage/permission restrictions
      - Support fallback for older devices
    tags:
      - android_general
      - difficulty::hard
  - slug: android-430-0-ru
    front: "Что такое SDK Runtime в Privacy Sandbox и как он изолирует SDK?"
    back: |
      **SDK Runtime** - запускает сторонние SDK в изолированном sandbox-процессе (Android 13+).

      **Ключевые особенности:**
      - **Process Isolation** - отдельный sandbox-процесс на приложение
      - **Limited Access** - нет SharedPrefs, internal storage, device IDs
      - **Binder IPC** - коммуникация через `SdkSandboxManager`
      - **Resource Quotas** - лимиты CPU, памяти, сети

      **Сложности миграции:**
      - Переход на IPC-контракты
      - Учёт ограничений storage/permissions
      - Fallback для старых устройств
    tags:
      - android_general
      - difficulty::hard

---\
# Вопрос (RU)

> Что такое SDK Runtime в Privacy Sandbox? Как он изолирует сторонние SDK? Какие вызовы возникают при миграции SDK в sandbox-окружение и как обрабатывать cross-sandbox коммуникацию?

---

# Question (EN)

> What is the SDK Runtime in Privacy Sandbox? How does it isolate third-party SDKs? What are the challenges of migrating SDKs to the runtime environment and how do you handle cross-sandbox communication?

---

## Ответ (RU)

**SDK Runtime** — компонент Privacy Sandbox (Android 13+ и совместимых билдах), запускающий сторонние SDK в отдельном sandbox-процессе, который управляется системой и логически отделён от процесса приложения. В этом процессе SDK выполняются изолированно и получают доступ только к разрешённому подмножеству платформенных API и данным, явно предоставленным приложением. Коммуникация с хост-приложением и другими компонентами идёт через Binder IPC с ограниченными возможностями.

## Краткая Версия
- Изоляция сторонних SDK в выделенном sandbox-процессе.
- Ограниченный доступ к данным и API: только явно предоставленные данные и Privacy Sandbox API.
- Взаимодействие через контролируемый Binder IPC.
- Жёсткие гарантии приватности и квоты ресурсов.
- При миграции: переход на IPC-контракты, учёт ограничений storage/permissions и поддержка fallback.

## Подробная Версия
### Архитектура SDK Runtime

**Ключевые концепции:**
- **Process Isolation** — SDK выполняются в отдельном sandbox-процессе, управляемом ОС и логически отделённом от процесса приложения. Один sandbox-процесс на приложение может обслуживать несколько SDK, при этом SDK изолированы логически и через предоставленные интерфейсы.
- **Limited Access** — прямого доступа к внутренним данным приложения (`SharedPreferences`, internal storage), его runtime permissions и стабильным идентификаторам устройства нет; SDK оперирует тем, что предоставляет хост и разрешённые системные API/Privacy Sandbox API.
- **Binder IPC** — вся коммуникация SDK с приложением и обратно идёт через Binder-интерфейсы, предоставленные SDK Runtime (например, через `SdkSandboxManager` и `SandboxedSdk` интерфейсы).
- **Resource Quotas** — система ограничивает использование CPU, памяти, сети и др. sandbox-процессом, чтобы снизить влияние SDK на приложение и систему.
- **Privacy Protection** — SDK не видит стабильные device IDs и чувствительные данные, если они не переданы явно и в соответствии с политиками; идентификаторы и сигналы медиируются Privacy Sandbox API.

```text
App Process <-> SDK Runtime (Sandbox Process) <-> Network/Services
     |                      |
  App Code             SDK Code (isolated)
```

**Ограничения SDK (упрощённо):**
- Нет прямого доступа к хранилищу приложения (`SharedPreferences`, internal files) — данные должны приходить от хост-приложения или использовать разрешённые механизмы (например, специфичные API Privacy Sandbox).
- Нет прямого доступа к device identifiers; сигналы и идентификаторы ограничены или проксируются в соответствии с Privacy Sandbox.
- Нет доступа к runtime permissions приложения и их результатам напрямую — права проверяет приложение и при необходимости передаёт данные SDK.
- Нельзя напрямую управлять компонентами приложения (activities/services/broadcast receivers) из sandbox без участия хоста; взаимодействие делается через согласованные IPC-протоколы.
- Нет произвольного доступа к другим приложениям.

### Требования

**Функциональные:**
- Изолировать выполнение сторонних SDK от хост-приложения.
- Обеспечить контролируемое взаимодействие через стандартизированные IPC-интерфейсы.
- Сохранить возможность SDK выполнять ключевые задачи (например, медиация рекламы, аналитика) без прямого доступа к чувствительным данным.
- Поддерживать плавную миграцию существующих SDK с fallback на традиционную модель.

**Нефункциональные:**
- Гарантировать приватность пользователя (минимизация доступа к данным, отсутствие стабильных идентификаторов).
- Обеспечить стабильность и предсказуемость: сбой SDK не должен ломать приложение.
- Ограничить использование ресурсов SDK (CPU, память, сеть).
- Свести к минимуму overhead IPC и влияния изоляции на UX.

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

- Асинхронная загрузка через coroutines поверх async API `loadSdk`.
- Корректное использование `Executor` и проверка доступности `SdkSandboxManager`.
- `IBinder` как точка входа для IPC с SDK.

### Реализация SDK Provider

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

- Точка входа — `onLoadSdk()`.
- `IBinder`-интерфейс (`ISdkApi`) для IPC с приложением (AIDL-интерфейс условный и задаётся SDK-провайдером).
- Освобождение ресурсов в `beforeUnloadSdk()`.

### Интеграция На Стороне Приложения

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

        // Предполагается, что ISdkApi определяет метод initialize(Bundle): Bundle.
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

- Использование AIDL-интерфейса через `Stub.asInterface()`.
- `Bundle` как транспорт для данных через Binder.
- Обработка ошибок и null-случаев через `Result`.
- Пример носит иллюстративный характер; конкретные методы AIDL-интерфейса определяются SDK.

### Вызовы Миграции SDK

**1. Архитектурные изменения:**
- Переход с прямых in-process вызовов на Binder IPC между приложением и SDK.
- Сериализация данных через `Bundle`/`Parcelable` для IPC.
- Асинхронная модель взаимодействия практически обязательна из-за IPC/latency и асинхронных API загрузки SDK.

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
            // Предполагается, что SandboxedAdClient и TraditionalAdClient реализуют общий интерфейс SdkClient.
            SandboxedAdClient(runtimeManager).apply { initialize(apiKey) }
        } else {
            TraditionalAdClient(context).apply { initialize(apiKey) }
        }
    }
}
```

- Проверка наличия SDK Runtime перед использованием.
- Fallback к традиционному in-app SDK при отсутствии Sandbox.
- Единый интерфейс (adapter) для хост-приложения предполагается и должен быть явно определён в реальной реализации.

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
- Понимать, что квоты и ограничения sandbox-процесса контролируются системой; учитывать их при проектировании SDK.
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

**SDK Runtime** is a Privacy Sandbox component (on Android 13+ and supported builds) that runs third-party SDKs inside a dedicated sandbox process managed by the OS and logically separated from the host app process. Within this process, SDKs execute in an isolated environment and can use only a constrained subset of platform APIs and data explicitly provided by the host app. Communication with the host app and other components occurs through Binder IPC under strict controls.

## Short Version
- Isolates third-party SDKs into a dedicated sandbox process.
- Restricts access to app data and device identifiers; SDK sees only host-provided data and Privacy Sandbox APIs.
- All interactions go through controlled Binder IPC.
- `Provides` strong privacy guarantees and resource quotas.
- Migration requires IPC-based contracts, handling storage/permission constraints, and supporting fallbacks.

## Detailed Version
### SDK Runtime Architecture

**Key Concepts:**
- **Process Isolation** — SDKs run in a dedicated sandbox process managed by the system and logically separated from the app process. A single sandbox process per app can host multiple SDKs, with isolation enforced via runtime boundaries and IPC.
- **Limited Access** — no direct access to the host app's internal data (`SharedPreferences`, internal storage), its runtime permissions, or stable device identifiers; the SDK relies on host-provided data, allowed system APIs, and Privacy Sandbox APIs.
- **Binder IPC** — all communication between the SDK and the host app uses Binder interfaces exposed through SDK Runtime (for example via `SdkSandboxManager` and `SandboxedSdk` interfaces).
- **Resource Quotas** — the system constrains CPU, memory, and network usage of the sandbox process to limit the SDKs' impact on the app and system.
- **Privacy Protection** — SDKs do not see stable device IDs or sensitive data unless explicitly (and compliantly) proxied by the host; identifiers and signals are mediated by Privacy Sandbox mechanisms.

```text
App Process <-> SDK Runtime (Sandbox Process) <-> Network/Services
     |                      |
  App Code             SDK Code (isolated)
```

**SDK Limitations (simplified):**
- No direct access to the host app's storage (`SharedPreferences`, internal files); data must come from the host app or approved mechanisms (e.g., Privacy Sandbox APIs).
- No direct access to device identifiers; identifiers and signals are scoped/mediated per Privacy Sandbox policies.
- No direct access to the app's runtime permission state; the app performs checks and passes only necessary derived data.
- Cannot directly control app components (activities/services/broadcast receivers) from the sandbox without host cooperation; interactions are via explicit IPC contracts.
- No arbitrary access to other apps.

### Requirements

**Functional:**
- Isolate third-party SDK execution from the host app.
- Provide standardized IPC interfaces for host-SDK communication.
- Allow SDKs to perform core tasks (e.g., ads, analytics) without direct access to sensitive data.
- Support smooth migration of existing SDKs, including fallback to the legacy in-app model.

**Non-functional:**
- Strong user privacy guarantees (data minimization, scoped identifiers).
- Stability: SDK crashes must not crash the host app.
- Resource control for SDKs (CPU, memory, network).
- Keep IPC overhead and UX impact minimal.

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

- Async loading using coroutines over the async `loadSdk` API.
- Proper `Executor` usage and `SdkSandboxManager` availability check.
- `IBinder` as the IPC entry point to the SDK.

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

- Entry point via `onLoadSdk()`.
- IBinder-based `ISdkApi` interface for IPC with the host app (AIDL is illustrative and defined by the SDK provider).
- Resource cleanup in `beforeUnloadSdk()`.

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

        // Assumes ISdkApi defines initialize(Bundle): Bundle.
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

- Uses an AIDL-generated interface via `Stub.asInterface()`.
- Uses `Bundle` for cross-process data transfer.
- Handles errors and nulls via `Result`.
- Illustrative example; concrete AIDL methods are SDK-specific.

### SDK Migration Challenges

**1. Architectural Changes:**
- Switch from in-process calls to Binder IPC between app and SDK.
- Serialize data via `Bundle`/`Parcelable` for IPC.
- Adopt an asynchronous interaction model due to IPC latency and async `loadSdk` API.

**2. Functional Limitations:**
- Persistent storage — SDK cannot write directly to the app's storage; the host app provides configuration/cache via an explicit protocol.
- Background execution — SDK work is constrained by the sandbox process; long-running/background tasks require coordination with the host app.
- Direct permissions — SDK cannot request/use runtime permissions directly; the host app validates permissions and passes only derived/aggregated data.

**3. Workarounds (via explicit host-SDK contracts):**

```kotlin
class SdkMigrationManager(private val context: Context) {

    fun shouldUseSandboxedSdk(): Boolean =
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            context.packageManager.hasSystemFeature("android.software.sdk_sandbox")

    suspend fun initializeSdk(apiKey: String): SdkClient {
        return if (shouldUseSandboxedSdk()) {
            val runtimeManager = SdkRuntimeManager(context)
            // Assumes SandboxedAdClient and TraditionalAdClient implement a common SdkClient interface.
            SandboxedAdClient(runtimeManager).apply { initialize(apiKey) }
        } else {
            TraditionalAdClient(context).apply { initialize(apiKey) }
        }
    }
}
```

- Feature detection before using SDK Runtime.
- Fallback to a traditional in-app SDK when sandbox is unavailable.
- Unified adapter-style interface for the host app is implied and should be defined in real implementations.

### Best Practices

**Migration:**
- Use a gradual rollout strategy with a fallback to the traditional SDK.
- Support both SDK variants during the transition period.
- Test across Android versions and Privacy Sandbox configurations.

**Communication:**
- Prefer lightweight, batched Binder calls.
- Optimize `Bundle` payloads (avoid large transfers).
- Implement timeouts and robust error handling for IPC.
- Avoid frequent synchronous calls that block the UI thread.

**Privacy:**
- Send only necessary, aggregated data.
- Anonymize or pseudonymize user IDs.
- Do not send stable device identifiers or personal data without strict necessity and policy compliance.

**Resources:**
- Understand that sandbox process quotas and limits are enforced by the system; design SDK behavior with these constraints in mind.
- Release resources in `beforeUnloadSdk()` and on failure paths.
- Test behavior on low-end devices and under constrained network conditions.

### Common Pitfalls

1. Passing sensitive data → privacy/policy violations.
   - Solution: minimize/anonymize data; align with Privacy Sandbox requirements.

2. Ignoring `loadSdk` failures → crashes or silent SDK malfunction.
   - Solution: use `Result`, explicit error handling, and fallbacks.

3. Overly chatty or heavy Binder calls → performance issues.
   - Solution: batching, async patterns, lightweight payloads.

4. No fallback path → broken behavior on devices without SDK Runtime.
   - Solution: feature detection and traditional SDK fallback.

5. Assuming app permissions inside the SDK → logic failures.
   - Solution: rely only on data explicitly supplied by the host app; avoid restricted APIs.

---

## Дополнительные Вопросы (RU)

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

- https://developer.android.com/design-for-safety/privacy-sandbox
- https://developer.android.com/design-for-safety/privacy-sandbox/sdk-runtime
- https://developer.android.com/reference/android/app/sdksandbox/SdkSandboxManager

## References

- https://developer.android.com/design-for-safety/privacy-sandbox
- https://developer.android.com/design-for-safety/privacy-sandbox/sdk-runtime
- https://developer.android.com/reference/android/app/sdksandbox/SdkSandboxManager

## Related Questions

### Prerequisites / Concepts

- [[c-android]]
- [[c-permissions]]
