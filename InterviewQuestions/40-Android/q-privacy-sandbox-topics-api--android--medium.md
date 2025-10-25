---
id: 20251012-12271172
title: "Privacy Sandbox Topics Api"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-what-is-the-difference-between-fragmentmanager-and-fragmenttransaction--android--medium, q-touch-event-handling-custom-views--custom-views--medium, q-hilt-entry-points--di--medium]
created: 2025-10-15
tags: [privacy-sandbox, topics-api, privacy, advertising, user-privacy, difficulty/medium]
---
# Privacy Sandbox: Topics API and Privacy-Preserving Advertising

---

## Answer (EN)
# Question (EN)
What is the Privacy Sandbox Topics API in Android? How does it provide privacy-preserving interest-based advertising? How do you implement Topics API in your app and what are the privacy considerations?

## Answer (EN)
Privacy Sandbox for Android is Google's initiative to improve user privacy while supporting advertising-based business models. The Topics API enables interest-based advertising without cross-app tracking by inferring topics of interest from app usage.

#### 1. Topics API Overview

**How Topics API Works:**
```kotlin
/**
 * Topics API provides interest-based topics without tracking individual users
 *
 * Key Concepts:
 * - Topics are derived from app usage over 3-week periods
 * - Taxonomy of ~350 topics (Sports, Travel, etc.)
 * - Topics are stored on-device
 * - Random topic (5% of the time) for plausible deniability
 * - Only recent topics (last 3 weeks) are available
 * - Topics are shared only with apps that observed the topic
 */

import android.adservices.topics.TopicsManager
import android.adservices.topics.GetTopicsRequest
import android.adservices.topics.GetTopicsResponse
import android.adservices.topics.Topic
import android.content.Context
import android.os.Build
import androidx.annotation.RequiresApi

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class TopicsApiManager(private val context: Context) {

    private val topicsManager: TopicsManager? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        context.getSystemService(TopicsManager::class.java)
    } else {
        null
    }

    /**
     * Get topics of interest for the user
     * Topics are computed on-device based on app usage
     */
    suspend fun getTopics(): Result<List<Topic>> {
        if (topicsManager == null) {
            return Result.failure(UnsupportedOperationException("Topics API not available"))
        }

        return try {
            val request = GetTopicsRequest.Builder()
                .setAdsSdkName("com.example.ads.sdk")
                .setShouldRecordObservation(true) // Record this call for future topic calculation
                .build()

            val response = suspendCancellableCoroutine<GetTopicsResponse> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                topicsManager.getTopics(
                    request,
                    executor,
                    OutcomeReceiver.create(
                        { response -> continuation.resume(response) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(response.topics)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get topics without recording observation
     * Useful for analytics/debugging
     */
    suspend fun getTopicsWithoutRecording(): Result<List<Topic>> {
        if (topicsManager == null) {
            return Result.failure(UnsupportedOperationException("Topics API not available"))
        }

        return try {
            val request = GetTopicsRequest.Builder()
                .setAdsSdkName("com.example.ads.sdk")
                .setShouldRecordObservation(false)
                .build()

            val response = suspendCancellableCoroutine<GetTopicsResponse> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                topicsManager.getTopics(
                    request,
                    executor,
                    OutcomeReceiver.create(
                        { response -> continuation.resume(response) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(response.topics)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Parse topic information
     */
    fun parseTopicInfo(topic: Topic): TopicInfo {
        return TopicInfo(
            id = topic.topicId,
            taxonomyVersion = topic.taxonomyVersion,
            modelVersion = topic.modelVersion,
            displayName = getTopicDisplayName(topic.topicId)
        )
    }

    /**
     * Map topic ID to human-readable name
     * (Simplified - actual taxonomy has ~350 topics)
     */
    private fun getTopicDisplayName(topicId: Int): String {
        return when (topicId) {
            1 -> "Arts & Entertainment"
            2 -> "Autos & Vehicles"
            3 -> "Beauty & Fitness"
            4 -> "Books & Literature"
            5 -> "Business & Industrial"
            6 -> "Computers & Electronics"
            7 -> "Finance"
            8 -> "Food & Drink"
            9 -> "Games"
            10 -> "Health"
            11 -> "Hobbies & Leisure"
            12 -> "Home & Garden"
            13 -> "Internet & Telecom"
            14 -> "Jobs & Education"
            15 -> "Law & Government"
            16 -> "News"
            17 -> "Online Communities"
            18 -> "People & Society"
            19 -> "Pets & Animals"
            20 -> "Real Estate"
            21 -> "Reference"
            22 -> "Science"
            23 -> "Shopping"
            24 -> "Sports"
            25 -> "Travel"
            else -> "Unknown Topic"
        }
    }

    /**
     * Check if Topics API is available
     */
    fun isTopicsApiAvailable(): Boolean {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
               topicsManager != null
    }
}

data class TopicInfo(
    val id: Int,
    val taxonomyVersion: Long,
    val modelVersion: Long,
    val displayName: String
)
```

#### 2. Privacy-Preserving Ad Targeting

**Using Topics for Ad Selection:**
```kotlin
class PrivacyPreservingAdManager(
    private val context: Context,
    private val topicsManager: TopicsApiManager
) {

    /**
     * Request ads based on topics without tracking
     */
    suspend fun requestAds(adFormat: AdFormat): Result<List<Ad>> {
        // Get topics
        val topicsResult = topicsManager.getTopics()

        if (topicsResult.isFailure) {
            // Fall back to contextual ads (based on current content)
            return requestContextualAds(adFormat)
        }

        val topics = topicsResult.getOrThrow()
        val topicIds = topics.map { it.topicId }

        // Request ads from ad server using topics
        return requestAdsFromServer(topicIds, adFormat)
    }

    private suspend fun requestAdsFromServer(
        topicIds: List<Int>,
        adFormat: AdFormat
    ): Result<List<Ad>> {
        return withContext(Dispatchers.IO) {
            try {
                // Send topics to ad server (without user identifiers)
                val request = AdRequest(
                    topics = topicIds,
                    format = adFormat,
                    contextualSignals = getContextualSignals()
                )

                val response = adServerClient.requestAds(request)
                Result.success(response.ads)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    private suspend fun requestContextualAds(adFormat: AdFormat): Result<List<Ad>> {
        // Fallback: contextual ads based on current app content
        return withContext(Dispatchers.IO) {
            try {
                val request = AdRequest(
                    topics = emptyList(),
                    format = adFormat,
                    contextualSignals = getContextualSignals()
                )

                val response = adServerClient.requestAds(request)
                Result.success(response.ads)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    /**
     * Get contextual signals from current content
     * (content-based targeting without tracking)
     */
    private fun getContextualSignals(): ContextualSignals {
        return ContextualSignals(
            contentCategory = getCurrentContentCategory(),
            language = Locale.getDefault().language,
            deviceType = if (isTablet()) "tablet" else "phone"
        )
    }

    private fun getCurrentContentCategory(): String {
        // Determine category of current content being viewed
        return "sports" // Placeholder
    }

    private fun isTablet(): Boolean {
        return (context.resources.configuration.screenLayout
                and Configuration.SCREENLAYOUT_SIZE_MASK) >= Configuration.SCREENLAYOUT_SIZE_LARGE
    }

    /**
     * Record ad impression (for frequency capping, without tracking)
     */
    fun recordImpression(adId: String) {
        // Record impression locally for frequency capping
        // No user identifiers sent to server
        val prefs = context.getSharedPreferences("ad_impressions", Context.MODE_PRIVATE)
        val count = prefs.getInt(adId, 0)
        prefs.edit().putInt(adId, count + 1).apply()
    }

    /**
     * Check if ad should be shown (frequency capping)
     */
    fun shouldShowAd(adId: String, maxImpressions: Int): Boolean {
        val prefs = context.getSharedPreferences("ad_impressions", Context.MODE_PRIVATE)
        val count = prefs.getInt(adId, 0)
        return count < maxImpressions
    }

    private val adServerClient = AdServerClient()
}

data class AdRequest(
    val topics: List<Int>,
    val format: AdFormat,
    val contextualSignals: ContextualSignals
)

data class ContextualSignals(
    val contentCategory: String,
    val language: String,
    val deviceType: String
)

data class Ad(
    val id: String,
    val title: String,
    val description: String,
    val imageUrl: String,
    val targetUrl: String
)

enum class AdFormat {
    BANNER,
    INTERSTITIAL,
    REWARDED,
    NATIVE
}

class AdServerClient {
    suspend fun requestAds(request: AdRequest): AdResponse {
        // Call ad server API
        return AdResponse(emptyList())
    }
}

data class AdResponse(val ads: List<Ad>)
```

#### 3. User Consent and Privacy Controls

**Privacy Controls Implementation:**
```kotlin
class PrivacySandboxControls(private val context: Context) {

    private val prefs = context.getSharedPreferences("privacy_sandbox", Context.MODE_PRIVATE)

    /**
     * Check if user has consented to Topics API
     */
    fun hasTopicsConsent(): Boolean {
        return prefs.getBoolean("topics_consent", false)
    }

    /**
     * Request user consent for Topics API
     */
    suspend fun requestTopicsConsent(activity: Activity): Boolean {
        return withContext(Dispatchers.Main) {
            suspendCancellableCoroutine { continuation ->
                showConsentDialog(
                    activity = activity,
                    title = "Personalized Ads",
                    message = """
                        We use Privacy Sandbox Topics API to show you relevant ads without tracking you across apps.

                        How it works:
                        • Your device determines topics of interest based on apps you use
                        • Topics are stored on your device only
                        • No personal information or browsing history leaves your device
                        • You can change this anytime in Settings
                    """.trimIndent(),
                    onAccept = {
                        prefs.edit().putBoolean("topics_consent", true).apply()
                        continuation.resume(true)
                    },
                    onDecline = {
                        prefs.edit().putBoolean("topics_consent", false).apply()
                        continuation.resume(false)
                    }
                )
            }
        }
    }

    private fun showConsentDialog(
        activity: Activity,
        title: String,
        message: String,
        onAccept: () -> Unit,
        onDecline: () -> Unit
    ) {
        AlertDialog.Builder(activity)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("Accept") { _, _ -> onAccept() }
            .setNegativeButton("Decline") { _, _ -> onDecline() }
            .setCancelable(false)
            .show()
    }

    /**
     * Show privacy settings screen
     */
    fun showPrivacySettings(activity: Activity) {
        val intent = Intent(activity, PrivacySandboxSettingsActivity::class.java)
        activity.startActivity(intent)
    }

    /**
     * Opt out of Topics API
     */
    fun optOutOfTopics() {
        prefs.edit().putBoolean("topics_consent", false).apply()
    }

    /**
     * Clear all privacy sandbox data
     */
    fun clearAllData() {
        prefs.edit().clear().apply()

        // Clear ad impressions
        context.getSharedPreferences("ad_impressions", Context.MODE_PRIVATE)
            .edit().clear().apply()
    }

    /**
     * Export user's privacy sandbox data (GDPR compliance)
     */
    fun exportUserData(): PrivacySandboxData {
        return PrivacySandboxData(
            topicsConsentGiven = hasTopicsConsent(),
            consentTimestamp = prefs.getLong("consent_timestamp", 0),
            settings = PrivacySandboxSettings(
                topicsEnabled = hasTopicsConsent()
            )
        )
    }
}

data class PrivacySandboxData(
    val topicsConsentGiven: Boolean,
    val consentTimestamp: Long,
    val settings: PrivacySandboxSettings
)

data class PrivacySandboxSettings(
    val topicsEnabled: Boolean
)
```

**Privacy Settings UI (Compose):**
```kotlin
@Composable
fun PrivacySandboxSettingsScreen(
    viewModel: PrivacySandboxViewModel = viewModel()
) {
    val settings by viewModel.settings.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Privacy Sandbox Settings") })
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            item {
                Text(
                    "Privacy Sandbox for Android",
                    style = MaterialTheme.typography.headlineSmall
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Privacy Sandbox helps protect your privacy while allowing apps to show you relevant content and ads.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            item {
                Spacer(modifier = Modifier.height(24.dp))
                SettingItem(
                    title = "Topics API",
                    description = "Allow apps to show you ads based on topics of interest without tracking you",
                    enabled = settings.topicsEnabled,
                    onToggle = { viewModel.toggleTopics() }
                )
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            "How Topics Work",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "• Topics are determined on your device based on your app usage\n" +
                            "• Only recent topics (last 3 weeks) are used\n" +
                            "• Topics are stored on your device\n" +
                            "• No personal information leaves your device",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(24.dp))
                OutlinedButton(
                    onClick = { viewModel.clearAllData() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.Delete, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Clear All Privacy Sandbox Data")
                }
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))
                TextButton(
                    onClick = { viewModel.exportData() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.Download, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Export My Data")
                }
            }
        }
    }
}

@Composable
fun SettingItem(
    title: String,
    description: String,
    enabled: Boolean,
    onToggle: (Boolean) -> Unit
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    title,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Switch(
                checked = enabled,
                onCheckedChange = onToggle
            )
        }
    }
}

class PrivacySandboxViewModel : ViewModel() {
    private val _settings = MutableStateFlow(PrivacySandboxSettings(topicsEnabled = false))
    val settings: StateFlow<PrivacySandboxSettings> = _settings.asStateFlow()

    fun toggleTopics() {
        _settings.value = _settings.value.copy(
            topicsEnabled = !_settings.value.topicsEnabled
        )
    }

    fun clearAllData() {
        // Clear all Privacy Sandbox data
    }

    fun exportData() {
        // Export user data
    }
}
```

#### 4. Testing and Debugging

**Topics API Testing:**
```kotlin
class TopicsApiDebugger(
    private val context: Context,
    private val topicsManager: TopicsApiManager
) {

    /**
     * Get current topics with detailed information
     */
    suspend fun debugGetTopics(): TopicsDebugInfo {
        val topics = topicsManager.getTopics().getOrNull() ?: emptyList()

        return TopicsDebugInfo(
            availableTopics = topics.map { topic ->
                TopicDebugDetail(
                    id = topic.topicId,
                    name = getTopicName(topic.topicId),
                    taxonomyVersion = topic.taxonomyVersion,
                    modelVersion = topic.modelVersion
                )
            },
            apiAvailable = topicsManager.isTopicsApiAvailable(),
            consentGiven = hasConsent(),
            timestamp = System.currentTimeMillis()
        )
    }

    /**
     * Simulate topic calculation (for testing)
     */
    fun simulateTopics(packageNames: List<String>): List<Int> {
        // Simulate topic assignment based on app categories
        // In reality, this happens on-device by the system
        return packageNames.mapNotNull { packageName ->
            getAppCategory(packageName)
        }.distinct()
    }

    private fun getAppCategory(packageName: String): Int? {
        // Map app to topic category
        return when {
            packageName.contains("sport") -> 24 // Sports
            packageName.contains("news") -> 16 // News
            packageName.contains("game") -> 9 // Games
            packageName.contains("shopping") -> 23 // Shopping
            else -> null
        }
    }

    private fun getTopicName(topicId: Int): String {
        // Get human-readable topic name
        return "Topic $topicId"
    }

    private fun hasConsent(): Boolean {
        val prefs = context.getSharedPreferences("privacy_sandbox", Context.MODE_PRIVATE)
        return prefs.getBoolean("topics_consent", false)
    }

    /**
     * Log Topics API calls for debugging
     */
    fun logTopicsApiCall(topics: List<Topic>) {
        Log.d("TopicsAPI", "Retrieved ${topics.size} topics:")
        topics.forEach { topic ->
            Log.d("TopicsAPI", "  - Topic ${topic.topicId} (v${topic.taxonomyVersion})")
        }
    }
}

data class TopicsDebugInfo(
    val availableTopics: List<TopicDebugDetail>,
    val apiAvailable: Boolean,
    val consentGiven: Boolean,
    val timestamp: Long
)

data class TopicDebugDetail(
    val id: Int,
    val name: String,
    val taxonomyVersion: Long,
    val modelVersion: Long
)
```

### Best Practices

1. **User Consent:**
   - Request explicit consent before using Topics API
   - Provide clear explanation of how it works
   - Allow users to opt-out anytime
   - Respect user preferences

2. **Privacy-First Design:**
   - Never combine Topics with user identifiers
   - Use contextual signals as fallback
   - Implement frequency capping locally
   - Minimize data collection

3. **Transparency:**
   - Provide privacy settings in app
   - Explain data usage clearly
   - Allow data export (GDPR)
   - Document privacy practices

4. **Testing:**
   - Test with Topics API disabled
   - Verify fallback to contextual ads
   - Test consent flow
   - Monitor API availability

5. **Compliance:**
   - Follow GDPR/CCPA requirements
   - Implement data deletion
   - Provide privacy policy
   - Regular privacy audits

### Common Pitfalls

1. **Not checking API availability** → Crashes on older Android versions
   - Always check Build.VERSION_CODES.TIRAMISU

2. **Combining Topics with user IDs** → Privacy violation
   - Never send Topics with personal identifiers

3. **No fallback mechanism** → No ads when Topics unavailable
   - Implement contextual advertising fallback

4. **Unclear consent flow** → User confusion
   - Provide clear, simple explanations

5. **Not respecting opt-out** → Privacy violation and user distrust
   - Always honor user preferences

6. **Excessive API calls** → Performance issues
   - Cache topics locally with appropriate TTL

### Summary

Privacy Sandbox Topics API enables interest-based advertising without cross-app tracking. Topics are computed on-device, stored locally, and shared only with apps that observed them. Proper implementation requires user consent, clear privacy controls, contextual fallbacks, and strict adherence to privacy principles. This approach balances user privacy with advertising needs in a transparent, user-controlled manner.

---



## Ответ (RU)
# Вопрос (RU)
Что такое Topics API Privacy Sandbox в Android? Как он обеспечивает privacy-preserving рекламу на основе интересов? Как реализовать Topics API в приложении и какие есть соображения приватности?

## Ответ (RU)
Privacy Sandbox для Android — это инициатива Google по улучшению приватности пользователей при поддержке рекламных бизнес-моделей. Topics API обеспечивает рекламу на основе интересов без cross-app отслеживания, определяя темы интересов на основе использования приложений.

#### Как работает Topics API

**Ключевые концепции:**
- Темы выводятся из использования приложений за 3-недельные периоды
- Таксономия из ~350 тем (Спорт, Путешествия и т.д.)
- Темы хранятся на устройстве
- Случайная тема (5% времени) для правдоподобного отрицания
- Доступны только recent темы (последние 3 недели)
- Темы делятся только с приложениями, которые наблюдали тему

**Privacy гарантии:**
- Обработка на устройстве
- Нет кросс-app tracking
- Нет persistent identifiers
- Пользовательский контроль
- Прозрачность

#### Реализация

**Основные шаги:**
1. Проверить доступность API (Android 13+)
2. Запросить согласие пользователя
3. Вызвать getTopics()
4. Использовать темы для выбора рекламы
5. Записать observation (для будущих вычислений)

**Fallback стратегия:**
- Contextual advertising (на основе контента)
- Generic ads без targeting
- Первая сторона данных (в пределах приложения)

### Лучшие практики

1. **Согласие:** Явный запрос, четкое объяснение, opt-out
2. **Privacy-first:** Никогда не комбинировать с user ID
3. **Прозрачность:** Настройки приватности, объяснение использования
4. **Тестирование:** API отключен, fallback, consent flow
5. **Compliance:** GDPR/CCPA, удаление данных, privacy policy

### Распространённые ошибки

1. Не проверять доступность API → краши
2. Комбинировать Topics с user ID → нарушение приватности
3. Нет fallback механизма → нет рекламы
4. Неясный consent flow → confusion
5. Не уважать opt-out → нарушение доверия
6. Избыточные API вызовы → проблемы производительности

### Резюме

Privacy Sandbox Topics API обеспечивает рекламу на основе интересов без cross-app отслеживания. Темы вычисляются на устройстве, хранятся локально и делятся только с приложениями, которые их наблюдали. Правильная реализация требует согласия пользователя, четких privacy контролов, contextual fallback и строгого соблюдения принципов приватности.

---

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-api-file-upload-server--android--medium]] - Networking
- [[q-splash-screen-api-android12--android--medium]] - Networking
- [[q-api-rate-limiting-throttling--android--medium]] - Networking
- [[q-kmm-ktor-networking--android--medium]] - Networking

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
