---
id: android-388
title: "Privacy Sandbox Topics API / Privacy Sandbox Topics API"
aliases: ["Privacy Sandbox Topics API", "Topics API"]
topic: android
subtopics: [privacy-sdks]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-app-permissions-runtime--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [advertising, android/privacy-sdks, difficulty/medium, privacy, privacy-sandbox, topics-api, user-privacy]
---

# Вопрос (RU)

Что такое Topics API в Privacy Sandbox для Android? Как он обеспечивает рекламу на основе интересов с сохранением приватности?

# Question (EN)

What is the Privacy Sandbox Topics API in Android? How does it provide privacy-preserving interest-based advertising?

---

## Ответ (RU)

Topics API — это механизм Privacy Sandbox, который обеспечивает рекламу на основе интересов без кросс-приложенского отслеживания. Темы интересов вычисляются на устройстве на основе использования приложений за последние 3 недели и хранятся локально.

### Ключевые Принципы

**Как работает:**
- Система определяет 3-5 тем из таксономии (~350 категорий: Спорт, Путешествия, Технологии)
- Темы обновляются еженедельно на основе использования приложений
- Каждый вызов API возвращает одну тему за эпоху (неделю)
- В 5% случаев возвращается случайная тема (plausible deniability)
- Темы доступны только приложениям, которые их "наблюдали"

**Privacy гарантии:**
- Вычисления только на устройстве
- Нет persistent идентификаторов
- Нет передачи истории просмотров
- Пользовательский контроль и прозрачность

### Базовая Реализация

```kotlin
import android.adservices.topics.TopicsManager
import android.adservices.topics.GetTopicsRequest
import android.content.Context
import android.os.Build
import androidx.annotation.RequiresApi

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class TopicsApiManager(private val context: Context) {

    private val topicsManager: TopicsManager? =
        context.getSystemService(TopicsManager::class.java)

    // ✅ Корректно: проверка доступности API перед использованием
    suspend fun getTopics(): Result<List<Int>> {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            return Result.failure(UnsupportedOperationException("Topics API requires Android 13+"))
        }

        return try {
            val request = GetTopicsRequest.Builder()
                .setAdsSdkName("com.example.ads")
                .setShouldRecordObservation(true)  // ✅ Записываем observation
                .build()

            val response = topicsManager?.getTopics(request, Executors.newSingleThreadExecutor()) { result ->
                result.onSuccess { it.topics }
                result.onFailure { e -> throw e }
            }

            Result.success(response?.topics?.map { it.topicId } ?: emptyList())
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
            // ✅ Используем темы для таргетинга без user ID
            requestAdsWithTopics(topicsResult.getOrThrow())
        } else {
            // ✅ Fallback на контекстную рекламу
            requestContextualAds()
        }
    }

    private suspend fun requestAdsWithTopics(topics: List<Int>): Result<List<Ad>> {
        // ❌ НИКОГДА: не комбинируем с идентификаторами пользователя
        // val userId = getUserId()  // FORBIDDEN

        // ✅ Отправляем только темы на сервер
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

    // ✅ Явный запрос согласия с понятным объяснением
    suspend fun requestTopicsConsent(activity: Activity): Boolean {
        return showConsentDialog(
            activity,
            title = "Персонализированная реклама",
            message = """
                Приложение использует Topics API для показа релевантной рекламы:
                • Темы определяются на вашем устройстве
                • Данные не покидают устройство
                • Вы можете отключить в любой момент
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

1. **Проверка доступности**: всегда проверяйте Android 13+ перед вызовом
2. **Fallback механизм**: используйте контекстную рекламу, если Topics недоступен
3. **Запись observation**: устанавливайте `setShouldRecordObservation(true)` для корректной работы
4. **Изоляция от идентификаторов**: никогда не комбинируйте Topics с user ID или advertising ID
5. **Прозрачность**: объясняйте пользователям механизм работы
6. **Уважение выбора**: немедленно прекращайте использование при opt-out

### Распространённые Ошибки

```kotlin
// ❌ Не проверяется доступность API
val topics = topicsManager.getTopics()  // Crash на Android < 13

// ❌ Комбинируется с user ID
requestAds(userId = "123", topics = topics)  // Нарушение privacy

// ❌ Нет fallback механизма
if (topics.isEmpty()) return emptyList()  // Нет рекламы

// ✅ Корректная реализация
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    val topics = topicsManager.getTopics().getOrNull()
    if (topics != null) {
        requestAdsWithTopics(topics)
    } else {
        requestContextualAds()  // Fallback
    }
}
```

---

## Answer (EN)

Topics API is a Privacy Sandbox mechanism that enables interest-based advertising without cross-app tracking. Interest topics are computed on-device based on app usage over the last 3 weeks and stored locally.

### Core Principles

**How it works:**
- System determines 3-5 topics from taxonomy (~350 categories: Sports, Travel, Technology)
- Topics update weekly based on app usage
- Each API call returns one topic per epoch (week)
- 5% of the time returns random topic (plausible deniability)
- Topics only available to apps that "observed" them

**Privacy guarantees:**
- On-device computation only
- No persistent identifiers
- No browsing history transmission
- User control and transparency

### Basic Implementation

```kotlin
import android.adservices.topics.TopicsManager
import android.adservices.topics.GetTopicsRequest
import android.content.Context
import android.os.Build
import androidx.annotation.RequiresApi

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class TopicsApiManager(private val context: Context) {

    private val topicsManager: TopicsManager? =
        context.getSystemService(TopicsManager::class.java)

    // ✅ Correct: check API availability before use
    suspend fun getTopics(): Result<List<Int>> {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            return Result.failure(UnsupportedOperationException("Topics API requires Android 13+"))
        }

        return try {
            val request = GetTopicsRequest.Builder()
                .setAdsSdkName("com.example.ads")
                .setShouldRecordObservation(true)  // ✅ Record observation
                .build()

            val response = topicsManager?.getTopics(request, Executors.newSingleThreadExecutor()) { result ->
                result.onSuccess { it.topics }
                result.onFailure { e -> throw e }
            }

            Result.success(response?.topics?.map { it.topicId } ?: emptyList())
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
            // ✅ Use topics for targeting without user ID
            requestAdsWithTopics(topicsResult.getOrThrow())
        } else {
            // ✅ Fallback to contextual ads
            requestContextualAds()
        }
    }

    private suspend fun requestAdsWithTopics(topics: List<Int>): Result<List<Ad>> {
        // ❌ NEVER: don't combine with user identifiers
        // val userId = getUserId()  // FORBIDDEN

        // ✅ Send only topics to server
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

    // ✅ Explicit consent request with clear explanation
    suspend fun requestTopicsConsent(activity: Activity): Boolean {
        return showConsentDialog(
            activity,
            title = "Personalized Ads",
            message = """
                App uses Topics API to show relevant ads:
                • Topics determined on your device
                • Data doesn't leave your device
                • You can disable anytime
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

1. **Availability check**: always verify Android 13+ before calling
2. **Fallback mechanism**: use contextual ads if Topics unavailable
3. **Record observation**: set `setShouldRecordObservation(true)` for correct operation
4. **Isolation from identifiers**: never combine Topics with user ID or advertising ID
5. **Transparency**: explain the mechanism to users
6. **Respect choice**: immediately stop using on opt-out

### Common Mistakes

```kotlin
// ❌ API availability not checked
val topics = topicsManager.getTopics()  // Crash on Android < 13

// ❌ Combined with user ID
requestAds(userId = "123", topics = topics)  // Privacy violation

// ❌ No fallback mechanism
if (topics.isEmpty()) return emptyList()  // No ads shown

// ✅ Correct implementation
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    val topics = topicsManager.getTopics().getOrNull()
    if (topics != null) {
        requestAdsWithTopics(topics)
    } else {
        requestContextualAds()  // Fallback
    }
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

- [[c-privacy-by-design]] - Privacy design patterns
- [[c-gdpr-compliance]] - GDPR requirements
- Android Privacy Sandbox documentation: https://developer.android.com/design-for-safety/privacy-sandbox/topics

## Related Questions

### Prerequisites
- [[q-app-permissions-runtime--android--medium]] - Runtime permissions
- [[q-gdpr-compliance-android--android--medium]] - GDPR compliance basics

### Related
- [[q-data-storage-security--android--medium]] - Secure data storage
- [[q-advertising-id-best-practices--android--medium]] - Advertising ID handling

### Advanced
- [[q-fledge-protected-audience-api--android--hard]] - FLEDGE API
- [[q-attribution-reporting-api--android--hard]] - Attribution API
