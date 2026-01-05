---
id: android-388
title: "Topics API в Privacy Sandbox / Privacy Sandbox Topics API"
aliases: ["Privacy Sandbox Topics API", "Topics API"]
topic: android
subtopics: [privacy-sdks]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-android-security-best-practices--android--medium]
sources: []
created: 2024-10-10
updated: 2025-11-10
tags: [advertising, android/privacy-sdks, difficulty/medium, privacy, privacy-sandbox, topics-api, user-privacy]
---
# Вопрос (RU)

> Что такое Topics API в Privacy Sandbox для Android? Как он обеспечивает рекламу на основе интересов с сохранением приватности?

# Question (EN)

> What is the Privacy Sandbox Topics API in Android? How does it provide privacy-preserving interest-based advertising?

---

## Ответ (RU)

Topics API — это механизм Privacy Sandbox, который обеспечивает рекламу на основе интересов без кросс-приложенческого отслеживания с использованием стабильных идентификаторов. Темы интересов определяются на устройстве на основе активности пользователя в приложениях и наблюдений со стороны интегрированных рекламных SDK за последние несколько недель и хранятся локально; приложения и зарегистрированные ad tech SDK получают доступ только к итоговым темам (в соответствии с политикой и регистрацией).

См. также: [[c-android]], [[moc-android]]

### Ключевые Принципы

**Как работает (упрощённо):**
- Система определяет до 3 наиболее релевантных тем за каждую эпоху (неделю) из таксономии (сотни обобщённых категорий, например: Спорт, Путешествия, Технологии).
- Темы пересчитываются еженедельно на основе использования приложений и SDK-наблюдений.
- При запросе Topics API конкретное приложение или интегрированный/зарегистрированный ad tech SDK получает ограниченное подмножество тем; доступны только темы, которые были "наблюдаемы" и соответствуют установленным правилам доступа.
- В части вызовов может возвращаться случайная тема для повышения приватности и правдоподобного отрицания (точные параметры и проценты зависят от реализации и могут меняться).

**Гарантии приватности (упрощённо):**
- Вычисления выполняются на устройстве, темы формируются локально.
- Нет использования стабильных кросс-приложенческих идентификаторов наподобие Advertising ID внутри Topics API.
- Доступен только ограниченный набор грубых (coarse-grained) тем, а не подробная история активности.
- Пользователь получает контроль и прозрачность (системные настройки Privacy Sandbox, возможность отключить Topics).

### Базовая Реализация (упрощённый пример)

Ниже — концептуальный пример для Android 13+ с использованием `TopicsManager`. Фактические сигнатуры, требования к регистрации ad tech, способы получения клиента и доступность отличаются в зависимости от версии Android, SDK Extensions и библиотек `adservices` / `adservices-ext`; всегда сверяйтесь с официальной документацией.

```kotlin
import android.adservices.topics.GetTopicsRequest
import android.adservices.topics.GetTopicsResponse
import android.adservices.topics.TopicsManager
import android.content.Context
import android.os.Build
import androidx.annotation.RequiresApi
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class TopicsApiManager(private val context: Context) {

    private val topicsManager: TopicsManager? =
        context.getSystemService(TopicsManager::class.java)

    private val executor: Executor = Executors.newSingleThreadExecutor()

    // ✅ Проверяем доступность API и оборачиваем callback в suspend-функцию (псевдокод)
    suspend fun getTopics(): Result<List<Int>> {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU || topicsManager == null) {
            return Result.failure(UnsupportedOperationException("Topics API требует Android 13+ и доступного TopicsManager/adservices клиента"))
        }

        return try {
            val request = GetTopicsRequest.Builder()
                // Должно совпадать с зарегистрированным именем ad tech SDK (пример)
                .setAdsSdkName("com.example.ads")
                .setShouldRecordObservation(true)
                .build()

            val topics = suspendCoroutine<List<Int>> { cont ->
                topicsManager.getTopics(request, executor) { response: GetTopicsResponse? ->
                    if (response != null) {
                        cont.resume(response.topics.map { it.topicId })
                    } else {
                        cont.resumeWithException(IllegalStateException("Empty Topics response"))
                    }
                }
            }

            Result.success(topics)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Использование Для Таргетинга Рекламы

```kotlin
class PrivacyPreservingAdManager(
    private val topicsManager: TopicsApiManager
) {

    suspend fun requestAds(): Result<List<Ad>> {
        val topicsResult = topicsManager.getTopics()

        return if (topicsResult.isSuccess) {
            // ✅ Используем темы как один из сигналов, без создания устойчивого кросс-приложенческого профиля
            requestAdsWithTopics(topicsResult.getOrThrow())
        } else {
            // ✅ Fallback на контекстную рекламу
            requestContextualAds()
        }
    }

    private suspend fun requestAdsWithTopics(topics: List<Int>): Result<List<Ad>> {
        // ⚠ Рекомендуется НЕ комбинировать Topics с устойчивыми user ID / Advertising ID
        // и соблюдать требования политики и локального законодательства.

        // ✅ Отправляем на сервер только ограниченные сигналы (topics + контекст)
        return adServerClient.requestAds(
            AdRequest(
                topics = topics,
                contextualSignals = getContextualSignals()
            )
        )
    }
}
```

### Пользовательский Контроль

```kotlin
class PrivacySandboxControls(private val context: Context) {

    private val prefs = context.getSharedPreferences("privacy_sandbox", Context.MODE_PRIVATE)

    // ✅ Явный запрос согласия с понятным объяснением (если требуется вашей юридической моделью)
    suspend fun requestTopicsConsent(activity: Activity): Boolean {
        return showConsentDialog(
            activity,
            title = "Персонализированная реклама",
            message = """
                Приложение использует Topics API для показа более релевантной рекламы:
                • Темы определяются на вашем устройстве
                • Серверам передаются только обобщённые тематики, а не подробная история активности
                • Вы можете отключить использование таких тем в любое время
            """.trimIndent()
        )
    }

    fun hasTopicsConsent(): Boolean =
        prefs.getBoolean("topics_consent", false)

    fun optOutOfTopics() {
        prefs.edit().putBoolean("topics_consent", false).apply()
    }
}
```

### Best Practices

1. **Проверка доступности**: всегда проверяйте Android 13+, наличие `TopicsManager`/совместимого клиента (adservices SDK, SDK Extensions) и корректную регистрацию ad tech перед вызовом.
2. **Fallback механизм**: используйте контекстную рекламу, если Topics недоступен или запрос завершился с ошибкой.
3. **Запись observation**: устанавливайте `setShouldRecordObservation(true)` там, где это уместно, чтобы система могла учитывать взаимодействия.
4. **Минимизация идентификаторов**: не используйте Topics для построения долгоживущих персональных профилей; избегайте связывания с устойчивыми ID.
5. **Прозрачность**: объясняйте пользователям механизм работы и дайте ссылку на соответствующие настройки.
6. **Уважение выбора**: немедленно прекращайте использование при opt-out на уровне приложения или системных настроек.

### Распространённые Ошибки

```kotlin
// ❌ Нет проверки доступности API / версии
val topics = topicsManager.getTopics()  // Риск краша или некорректной работы на устройствах без поддержки

// ❌ Игнорируется отказ / ошибки API
// Нет fallback → потеря дохода и ухудшение UX

// ✅ Корректный паттерн (упрощённо)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && topicsApiManager != null) {
    val topics = topicsApiManager.getTopics().getOrNull()
    if (!topics.isNullOrEmpty()) {
        requestAdsWithTopics(topics)
    } else {
        requestContextualAds()  // Fallback
    }
} else {
    requestContextualAds()  // Fallback для старых устройств
}
```

---

## Answer (EN)

The Topics API is a Privacy Sandbox mechanism that enables interest-based advertising without using stable cross-app identifiers. Interest topics are determined on-device based on user activity in apps and observations from integrated ad tech SDKs over recent weeks and stored locally; apps and registered ad tech SDKs can access only the resulting topics subject to policy and registration, not raw history.

See also: [[c-android]], [[moc-android]]

### Core Principles

**How it works (simplified):**
- The system selects up to 3 top topics per epoch (week) from a taxonomy (hundreds of coarse categories such as Sports, Travel, Technology).
- Topics are recomputed weekly based on app usage and SDK observations.
- When calling the Topics API, a given app or integrated/registered ad tech SDK receives a limited subset of topics; only topics that are observable and eligible for that caller under the rules are returned.
- In some calls, a random topic may be returned to improve privacy and provide plausible deniability (exact parameters/percentages are implementation-dependent and may change).

**Privacy guarantees (high-level):**
- Topics are computed on-device; classification happens locally.
- No stable cross-app identifiers like Advertising ID are used within the Topics API.
- Only a small set of coarse topics is exposed instead of detailed activity history.
- Users have control and transparency via system Privacy Sandbox settings, including the ability to turn off Topics.

### Basic Implementation (simplified)

Below is a conceptual example for Android 13+ using `TopicsManager`. Actual method signatures, ad tech registration requirements, how to obtain the client, and availability depend on Android version, SDK Extensions, and `adservices` / `adservices-ext` libraries; always check the official documentation.

```kotlin
import android.adservices.topics.GetTopicsRequest
import android.adservices.topics.GetTopicsResponse
import android.adservices.topics.TopicsManager
import android.content.Context
import android.os.Build
import androidx.annotation.RequiresApi
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class TopicsApiManager(private val context: Context) {

    private val topicsManager: TopicsManager? =
        context.getSystemService(TopicsManager::class.java)

    private val executor: Executor = Executors.newSingleThreadExecutor()

    // ✅ Check API availability and wrap callback into a suspend function (pseudo-code)
    suspend fun getTopics(): Result<List<Int>> {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU || topicsManager == null) {
            return Result.failure(UnsupportedOperationException("Topics API requires Android 13+ and available TopicsManager/adservices client"))
        }

        return try {
            val request = GetTopicsRequest.Builder()
                // Must match the registered ad tech SDK name (example)
                .setAdsSdkName("com.example.ads")
                .setShouldRecordObservation(true)
                .build()

            val topics = suspendCoroutine<List<Int>> { cont ->
                topicsManager.getTopics(request, executor) { response: GetTopicsResponse? ->
                    if (response != null) {
                        cont.resume(response.topics.map { it.topicId })
                    } else {
                        cont.resumeWithException(IllegalStateException("Empty Topics response"))
                    }
                }
            }

            Result.success(topics)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Using for Ad Targeting

```kotlin
class PrivacyPreservingAdManager(
    private val topicsManager: TopicsApiManager
) {

    suspend fun requestAds(): Result<List<Ad>> {
        val topicsResult = topicsManager.getTopics()

        return if (topicsResult.isSuccess) {
            // ✅ Use topics as one of the signals without creating a stable cross-app profile
            requestAdsWithTopics(topicsResult.getOrThrow())
        } else {
            // ✅ Fallback to contextual ads
            requestContextualAds()
        }
    }

    private suspend fun requestAdsWithTopics(topics: List<Int>): Result<List<Ad>> {
        // ⚠ Recommended: do NOT combine Topics with long-lived user identifiers / Advertising ID;
        // comply with platform policies and applicable regulations.

        // ✅ Send only limited signals (topics + contextual data) to your ad server
        return adServerClient.requestAds(
            AdRequest(
                topics = topics,
                contextualSignals = getContextualSignals()
            )
        )
    }
}
```

### User Control

```kotlin
class PrivacySandboxControls(private val context: Context) {

    private val prefs = context.getSharedPreferences("privacy_sandbox", Context.MODE_PRIVATE)

    // ✅ Explicit consent with clear explanation (if required by your legal/compliance model)
    suspend fun requestTopicsConsent(activity: Activity): Boolean {
        return showConsentDialog(
            activity,
            title = "Personalized Ads",
            message = """
                This app uses the Topics API to show more relevant ads:
                • Topics are determined on your device
                • Only coarse topics, not detailed activity history, are shared
                • You can disable this at any time
            """.trimIndent()
        )
    }

    fun hasTopicsConsent(): Boolean =
        prefs.getBoolean("topics_consent", false)

    fun optOutOfTopics() {
        prefs.edit().putBoolean("topics_consent", false).apply()
    }
}
```

### Best Practices

1. **Availability check**: always verify Android 13+, `TopicsManager`/compatible client (adservices SDK, SDK Extensions), and proper ad tech registration before calling.
2. **Fallback mechanism**: use contextual ads if Topics is unavailable or fails.
3. **Record observation**: set `setShouldRecordObservation(true)` where appropriate so the system can consider interactions.
4. **Minimize identifiers**: avoid using Topics to build long-lived personal profiles; avoid combining with stable identifiers.
5. **Transparency**: clearly explain to users how Topics is used and link to relevant settings.
6. **Respect choice**: immediately stop using Topics when users opt out in-app or via system settings.

### Common Mistakes

```kotlin
// ❌ API availability not checked / wrong environment assumptions
val topics = topicsManager.getTopics()  // Risk of crash or unsupported behavior

// ❌ Ignoring API failures / no fallback
// Leads to revenue loss and poor UX

// ✅ Correct pattern (simplified)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && topicsApiManager != null) {
    val topics = topicsApiManager.getTopics().getOrNull()
    if (!topics.isNullOrEmpty()) {
        requestAdsWithTopics(topics)
    } else {
        requestContextualAds()  // Fallback
    }
} else {
    requestContextualAds()  // Fallback on older devices
}
```

---

## Follow-ups

- How does Topics API differ from FLEDGE (Protected Audience API)?
- What happens when user clears app data?
- How to test Topics API in development?
- What are the taxonomy version update implications?
- How to handle users who disable Topics API across all apps?

## References

- Android Privacy Sandbox documentation: https://developer.android.com/design-for-safety/privacy-sandbox/topics

## Related Questions

### Prerequisites

_None_

### Related

_None_

### Advanced

_None_
