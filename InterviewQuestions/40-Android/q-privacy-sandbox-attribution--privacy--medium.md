---
id: 20251012-12271169
title: "Privacy Sandbox Attribution"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [privacy-sandbox, attribution-reporting, conversion-tracking, privacy, advertising, difficulty/medium]
---
# Privacy Sandbox: Attribution Reporting API

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How does the Attribution Reporting API work in Privacy Sandbox? How do you measure ad conversions without tracking users? What are the differences between event-level and aggregate reports?

## Answer (EN)
The Attribution Reporting API enables conversion measurement and attribution without cross-app tracking. It provides two types of reports: event-level (limited detailed data) and aggregated (summary statistics with differential privacy), allowing advertisers to measure campaign effectiveness while preserving user privacy.

#### 1. Attribution Reporting Overview

**Understanding Attribution Reporting:**
```kotlin
/**
 * Attribution Reporting API enables conversion tracking without user tracking
 *
 * Key Concepts:
 * - Source Events: Ad impressions or clicks
 * - Trigger Events: Conversions (purchases, sign-ups, etc.)
 * - Event-Level Reports: Limited conversion data (3 bits)
 * - Aggregate Reports: Summary statistics with differential privacy
 * - Attribution Windows: Time limits for attributing conversions
 * - Rate Limits: Prevent abuse and cross-site tracking
 *
 * Report Types:
 * 1. Event-Level: Detailed source info + limited conversion data
 * 2. Aggregate: Summary metrics with privacy guarantees
 */

import android.adservices.measurement.MeasurementManager
import android.adservices.measurement.WebSourceParams
import android.adservices.measurement.WebSourceRegistrationRequest
import android.adservices.measurement.WebTriggerParams
import android.adservices.measurement.WebTriggerRegistrationRequest
import android.content.Context
import android.net.Uri
import android.os.Build
import android.view.InputEvent
import androidx.annotation.RequiresApi

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionReportingManager(private val context: Context) {

    private val measurementManager: MeasurementManager? =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.getSystemService(MeasurementManager::class.java)
        } else null

    /**
     * Register ad source (impression or click)
     */
    suspend fun registerAdSource(
        sourceUrl: String,
        destinationUrl: String,
        sourceType: SourceType,
        priority: Long = 0,
        expiry: Long = 2592000000, // 30 days in milliseconds
        inputEvent: InputEvent? = null
    ): Result<Unit> {
        if (measurementManager == null) {
            return Result.failure(UnsupportedOperationException("Measurement API not available"))
        }

        return try {
            val sourceParams = WebSourceParams.Builder(Uri.parse(sourceUrl))
                .setDebugKeyAllowed(false)
                .build()

            val request = WebSourceRegistrationRequest.Builder(
                listOf(sourceParams),
                Uri.parse(destinationUrl)
            )
                .setInputEvent(inputEvent)
                .setAppDestination(Uri.parse(destinationUrl))
                .setWebDestination(Uri.parse(destinationUrl))
                .build()

            suspendCancellableCoroutine<Unit> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                measurementManager.registerWebSource(
                    request,
                    executor,
                    OutcomeReceiver.create(
                        { continuation.resume(Unit) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Register conversion trigger
     */
    suspend fun registerConversion(
        triggerUrl: String,
        conversionData: ConversionData
    ): Result<Unit> {
        if (measurementManager == null) {
            return Result.failure(UnsupportedOperationException("Measurement API not available"))
        }

        return try {
            val triggerParams = WebTriggerParams.Builder(Uri.parse(triggerUrl))
                .setDebugKeyAllowed(false)
                .build()

            val request = WebTriggerRegistrationRequest.Builder(
                listOf(triggerParams),
                Uri.parse("https://advertiser.example")
            ).build()

            suspendCancellableCoroutine<Unit> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                measurementManager.registerWebTrigger(
                    request,
                    executor,
                    OutcomeReceiver.create(
                        { continuation.resume(Unit) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Delete registrations (for user privacy control)
     */
    suspend fun deleteRegistrations(): Result<Unit> {
        if (measurementManager == null) {
            return Result.failure(UnsupportedOperationException("Measurement API not available"))
        }

        return try {
            suspendCancellableCoroutine<Unit> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                measurementManager.deleteRegistrations(
                    executor,
                    OutcomeReceiver.create(
                        { continuation.resume(Unit) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun isApiAvailable(): Boolean {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
               measurementManager != null
    }
}

enum class SourceType {
    IMPRESSION,
    CLICK
}

data class ConversionData(
    val eventType: String,
    val value: Int, // Limited to 3 bits (0-7) for event-level reports
    val priority: Long = 0
)
```

#### 2. Event-Level Attribution

**Event-Level Report Configuration:**
```kotlin
class EventLevelAttribution(
    private val attributionManager: AttributionReportingManager
) {

    /**
     * Register ad impression with event-level attribution
     */
    suspend fun trackAdImpression(
        campaignId: String,
        adId: String,
        destinationUrl: String
    ) {
        // Source registration URL with event-level configuration
        val sourceUrl = buildSourceUrl(
            campaignId = campaignId,
            adId = adId,
            reportingEndpoint = "https://adtech.example/attribution"
        )

        attributionManager.registerAdSource(
            sourceUrl = sourceUrl,
            destinationUrl = destinationUrl,
            sourceType = SourceType.IMPRESSION,
            priority = 100,
            expiry = 2592000000 // 30 days
        )
    }

    /**
     * Register ad click with event-level attribution
     */
    suspend fun trackAdClick(
        campaignId: String,
        adId: String,
        destinationUrl: String,
        inputEvent: InputEvent
    ) {
        val sourceUrl = buildSourceUrl(
            campaignId = campaignId,
            adId = adId,
            reportingEndpoint = "https://adtech.example/attribution"
        )

        // Clicks have higher priority than impressions
        attributionManager.registerAdSource(
            sourceUrl = sourceUrl,
            destinationUrl = destinationUrl,
            sourceType = SourceType.CLICK,
            priority = 200,
            expiry = 604800000, // 7 days
            inputEvent = inputEvent
        )
    }

    /**
     * Track conversion with limited data (3 bits = 0-7)
     */
    suspend fun trackConversion(
        conversionType: ConversionType,
        conversionValue: Int
    ) {
        // Conversion data limited to 3 bits for privacy
        val limitedValue = conversionValue.coerceIn(0, 7)

        val triggerUrl = buildTriggerUrl(
            conversionType = conversionType,
            conversionData = limitedValue,
            reportingEndpoint = "https://adtech.example/attribution"
        )

        attributionManager.registerConversion(
            triggerUrl = triggerUrl,
            conversionData = ConversionData(
                eventType = conversionType.name,
                value = limitedValue,
                priority = conversionType.priority
            )
        )
    }

    /**
     * Build source registration URL with JSON configuration
     */
    private fun buildSourceUrl(
        campaignId: String,
        adId: String,
        reportingEndpoint: String
    ): String {
        val config = """
            {
              "source_event_id": "$campaignId",
              "destination": "https://advertiser.example",
              "expiry": "2592000",
              "priority": "100",
              "event_report_window": "2592000",
              "aggregatable_report_window": "2592000"
            }
        """.trimIndent()

        return "$reportingEndpoint/register-source?config=${Uri.encode(config)}"
    }

    /**
     * Build trigger registration URL
     */
    private fun buildTriggerUrl(
        conversionType: ConversionType,
        conversionData: Int,
        reportingEndpoint: String
    ): String {
        val config = """
            {
              "event_trigger_data": [
                {
                  "trigger_data": "$conversionData",
                  "priority": "${conversionType.priority}",
                  "deduplication_key": "${System.currentTimeMillis()}"
                }
              ]
            }
        """.trimIndent()

        return "$reportingEndpoint/register-trigger?config=${Uri.encode(config)}"
    }
}

enum class ConversionType(val priority: Long) {
    PAGE_VIEW(10),
    ADD_TO_CART(50),
    INITIATE_CHECKOUT(75),
    PURCHASE(100),
    SIGN_UP(80),
    LEAD(60)
}
```

**Event-Level Report Structure:**
```kotlin
/**
 * Event-level attribution report (sent to reporting endpoint)
 */
data class EventLevelReport(
    // Source information (detailed)
    val sourceEventId: String,        // Campaign/ad identifier
    val sourceType: String,           // "navigation" or "event"
    val attributionDestination: String,

    // Trigger information (limited to 3 bits)
    val triggerData: Int,             // 0-7 only (privacy protection)

    // Metadata
    val reportId: String,
    val sourceDebugKey: String? = null,
    val triggerDebugKey: String? = null,
    val randomizedTriggerRate: Double,

    // Timing (with noise for privacy)
    val scheduledReportTime: Long,
    val reportingOrigin: String
)

/**
 * Example: Parse event-level report received at endpoint
 */
class EventLevelReportProcessor {

    fun processReport(report: EventLevelReport): AttributionInsight {
        // Decode 3-bit trigger data
        val conversionType = when (report.triggerData) {
            0 -> "page_view"
            1 -> "add_to_cart"
            2 -> "checkout"
            3 -> "purchase"
            4 -> "sign_up"
            5, 6, 7 -> "other" // Limited vocabulary due to 3-bit constraint
            else -> "unknown"
        }

        return AttributionInsight(
            campaignId = report.sourceEventId,
            conversionType = conversionType,
            timestamp = report.scheduledReportTime,
            sourceType = report.sourceType
        )
    }

    /**
     * Aggregate multiple event-level reports
     */
    fun aggregateReports(reports: List<EventLevelReport>): CampaignPerformance {
        val byCampaign = reports.groupBy { it.sourceEventId }

        return CampaignPerformance(
            campaigns = byCampaign.map { (campaignId, campaignReports) ->
                CampaignMetrics(
                    id = campaignId,
                    totalConversions = campaignReports.size,
                    conversionsByType = campaignReports
                        .groupBy { it.triggerData }
                        .mapValues { it.value.size },
                    clickConversions = campaignReports.count { it.sourceType == "navigation" },
                    impressionConversions = campaignReports.count { it.sourceType == "event" }
                )
            }
        )
    }
}

data class AttributionInsight(
    val campaignId: String,
    val conversionType: String,
    val timestamp: Long,
    val sourceType: String
)

data class CampaignPerformance(
    val campaigns: List<CampaignMetrics>
)

data class CampaignMetrics(
    val id: String,
    val totalConversions: Int,
    val conversionsByType: Map<Int, Int>,
    val clickConversions: Int,
    val impressionConversions: Int
)
```

#### 3. Aggregate Attribution

**Aggregate Attribution Setup:**
```kotlin
class AggregateAttribution(
    private val attributionManager: AttributionReportingManager
) {

    /**
     * Register source with aggregate keys
     */
    suspend fun trackAdWithAggregation(
        campaignId: String,
        adGroupId: String,
        creativeId: String,
        destinationUrl: String
    ) {
        val sourceUrl = buildAggregateSourceUrl(
            campaignId = campaignId,
            adGroupId = adGroupId,
            creativeId = creativeId
        )

        attributionManager.registerAdSource(
            sourceUrl = sourceUrl,
            destinationUrl = destinationUrl,
            sourceType = SourceType.IMPRESSION
        )
    }

    /**
     * Track conversion with aggregate contribution
     */
    suspend fun trackConversionWithValue(
        conversionType: String,
        purchaseValue: Double,
        quantity: Int
    ) {
        val triggerUrl = buildAggregateTriggerUrl(
            conversionType = conversionType,
            purchaseValue = purchaseValue,
            quantity = quantity
        )

        attributionManager.registerConversion(
            triggerUrl = triggerUrl,
            conversionData = ConversionData(
                eventType = conversionType,
                value = 0 // Not used for aggregate reports
            )
        )
    }

    /**
     * Build source URL with aggregate keys
     */
    private fun buildAggregateSourceUrl(
        campaignId: String,
        adGroupId: String,
        creativeId: String
    ): String {
        // Define aggregation keys (128-bit identifiers)
        val aggregationKeys = """
            {
              "campaign_counter": "0x${campaignId.hashCode().toString(16).padStart(32, '0')}",
              "geo_value": "0x${getGeoKey().toString(16).padStart(32, '0')}",
              "creative_value": "0x${creativeId.hashCode().toString(16).padStart(32, '0')}"
            }
        """.trimIndent()

        val config = """
            {
              "source_event_id": "$campaignId",
              "destination": "https://advertiser.example",
              "aggregation_keys": $aggregationKeys,
              "aggregatable_report_window": "2592000"
            }
        """.trimIndent()

        return "https://adtech.example/register-source?config=${Uri.encode(config)}"
    }

    /**
     * Build trigger URL with aggregate values
     */
    private fun buildAggregateTriggerUrl(
        conversionType: String,
        purchaseValue: Double,
        quantity: Int
    ): String {
        // Aggregate contributions (with privacy budget)
        val aggregatableValues = """
            [
              {
                "key_piece": "0x1",
                "source_keys": ["campaign_counter"],
                "value": 1
              },
              {
                "key_piece": "0x2",
                "source_keys": ["geo_value"],
                "value": ${(purchaseValue * 100).toInt()}
              },
              {
                "key_piece": "0x3",
                "source_keys": ["creative_value"],
                "value": $quantity
              }
            ]
        """.trimIndent()

        val config = """
            {
              "aggregatable_trigger_data": $aggregatableValues,
              "aggregatable_values": {
                "campaign_counter": 1,
                "geo_value": ${(purchaseValue * 100).toInt()},
                "creative_value": $quantity
              }
            }
        """.trimIndent()

        return "https://adtech.example/register-trigger?config=${Uri.encode(config)}"
    }

    private fun getGeoKey(): Int {
        // Get geo-based key
        return 1 // Placeholder
    }
}

/**
 * Aggregate attribution report (encrypted)
 */
data class AggregateReport(
    val aggregationServicePayloads: List<EncryptedPayload>,
    val sharedInfo: String,
    val reportingOrigin: String
)

data class EncryptedPayload(
    val payload: String, // Encrypted aggregate contributions
    val keyId: String
)

/**
 * Process aggregate reports (requires aggregation service)
 */
class AggregateReportProcessor {

    /**
     * Aggregate reports are processed by aggregation service
     * which adds differential privacy noise
     */
    fun requestAggregation(
        reports: List<AggregateReport>,
        aggregationKeys: List<String>
    ): AggregationRequest {
        return AggregationRequest(
            reports = reports.map { it.toPayload() },
            keys = aggregationKeys,
            privacyBudget = 65536 // Total privacy budget
        )
    }

    /**
     * Parse aggregated results (with noise)
     */
    fun parseAggregatedResults(results: AggregationResponse): AggregatedMetrics {
        return AggregatedMetrics(
            metrics = results.data.map { entry ->
                AggregateMetric(
                    key = entry.key,
                    value = entry.value,
                    // Values have differential privacy noise added
                    noiseApplied = true
                )
            }
        )
    }

    private fun AggregateReport.toPayload(): String {
        // Convert to aggregation service format
        return ""
    }
}

data class AggregationRequest(
    val reports: List<String>,
    val keys: List<String>,
    val privacyBudget: Int
)

data class AggregationResponse(
    val data: List<KeyValue>
)

data class KeyValue(
    val key: String,
    val value: Long
)

data class AggregatedMetrics(
    val metrics: List<AggregateMetric>
)

data class AggregateMetric(
    val key: String,
    val value: Long,
    val noiseApplied: Boolean
)
```

#### 4. Conversion Tracking Implementation

**E-commerce Conversion Tracking:**
```kotlin
class EcommerceAttributionTracker(
    private val context: Context,
    private val eventLevel: EventLevelAttribution,
    private val aggregate: AggregateAttribution
) {

    /**
     * Track product page view
     */
    suspend fun trackProductView(productId: String, fromAd: Boolean) {
        if (fromAd) {
            eventLevel.trackConversion(
                conversionType = ConversionType.PAGE_VIEW,
                conversionValue = 0
            )
        }
    }

    /**
     * Track add to cart
     */
    suspend fun trackAddToCart(
        productId: String,
        price: Double,
        quantity: Int
    ) {
        // Event-level: Limited data (3 bits)
        eventLevel.trackConversion(
            conversionType = ConversionType.ADD_TO_CART,
            conversionValue = 1
        )

        // Aggregate: Detailed value data
        aggregate.trackConversionWithValue(
            conversionType = "add_to_cart",
            purchaseValue = price * quantity,
            quantity = quantity
        )
    }

    /**
     * Track purchase
     */
    suspend fun trackPurchase(
        orderId: String,
        orderValue: Double,
        itemCount: Int,
        items: List<PurchaseItem>
    ) {
        // Event-level: Conversion signal (3 for purchase)
        eventLevel.trackConversion(
            conversionType = ConversionType.PURCHASE,
            conversionValue = 3
        )

        // Aggregate: Detailed revenue data
        aggregate.trackConversionWithValue(
            conversionType = "purchase",
            purchaseValue = orderValue,
            quantity = itemCount
        )

        // Store locally for deduplication
        saveConversion(orderId, orderValue)
    }

    /**
     * Track sign-up conversion
     */
    suspend fun trackSignUp(userId: String) {
        eventLevel.trackConversion(
            conversionType = ConversionType.SIGN_UP,
            conversionValue = 4
        )

        aggregate.trackConversionWithValue(
            conversionType = "sign_up",
            purchaseValue = 0.0,
            quantity = 1
        )
    }

    private fun saveConversion(orderId: String, value: Double) {
        val prefs = context.getSharedPreferences("conversions", Context.MODE_PRIVATE)
        prefs.edit()
            .putFloat(orderId, value.toFloat())
            .putLong("${orderId}_time", System.currentTimeMillis())
            .apply()
    }

    /**
     * Check if conversion was already tracked (deduplication)
     */
    fun wasConversionTracked(orderId: String): Boolean {
        val prefs = context.getSharedPreferences("conversions", Context.MODE_PRIVATE)
        return prefs.contains(orderId)
    }
}

data class PurchaseItem(
    val productId: String,
    val name: String,
    val price: Double,
    val quantity: Int
)
```

**Attribution Report Visualization:**
```kotlin
@Composable
fun AttributionDashboard(
    viewModel: AttributionViewModel = viewModel()
) {
    val eventLevelMetrics by viewModel.eventLevelMetrics.collectAsState()
    val aggregateMetrics by viewModel.aggregateMetrics.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "Attribution Reports",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Event-Level Metrics
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "Event-Level Attribution",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Detailed source info, limited conversion data (3 bits)",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(16.dp))

                eventLevelMetrics.campaigns.forEach { campaign ->
                    MetricRow(
                        label = "Campaign ${campaign.id}",
                        value = "${campaign.totalConversions} conversions"
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Aggregate Metrics
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "Aggregate Attribution",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Summary metrics with differential privacy",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(16.dp))

                aggregateMetrics.metrics.forEach { metric ->
                    MetricRow(
                        label = metric.key,
                        value = "${metric.value} (with noise)"
                    )
                }
            }
        }
    }
}

@Composable
fun MetricRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium)
        Text(value, style = MaterialTheme.typography.bodyMedium)
    }
}
```

### Best Practices

1. **Report Type Selection:**
   - Event-level: Campaign optimization, A/B testing
   - Aggregate: Revenue measurement, detailed analytics
   - Use both for comprehensive measurement

2. **Privacy Budget:**
   - Monitor privacy budget consumption
   - Aggregate reports consume budget
   - Plan measurement strategy carefully

3. **Deduplication:**
   - Use deduplication keys
   - Prevent double-counting conversions
   - Store conversion IDs locally

4. **Attribution Windows:**
   - Set appropriate windows (7-30 days)
   - Clicks: shorter window (7 days)
   - Impressions: longer window (30 days)

5. **Testing:**
   - Test with debug keys in development
   - Validate report structure
   - Monitor report delivery

### Common Pitfalls

1. **Exceeding 3-bit limit** → Data loss in event-level reports
   - Map conversions to 0-7 values carefully

2. **Not implementing deduplication** → Double-counting
   - Always use deduplication keys

3. **Ignoring privacy budget** → Report failures
   - Monitor and manage budget usage

4. **Incorrect attribution windows** → Missed attributions
   - Set windows based on customer journey

5. **Not handling API unavailability** → Missing data
   - Implement fallback measurement

6. **Combining with user IDs** → Privacy violation
   - Keep attribution data separate from user identity

### Summary

Attribution Reporting API enables conversion measurement without user tracking through two complementary approaches: event-level reports provide detailed source information with limited conversion data (3 bits), while aggregate reports offer detailed conversion metrics with differential privacy. This dual approach balances granular campaign optimization with comprehensive revenue measurement, all while preserving user privacy.

---



## Ответ (RU)
# Вопрос (RU)
Как работает Attribution Reporting API в Privacy Sandbox? Как измерять конверсии рекламы без отслеживания пользователей? В чём разница между event-level и aggregate отчётами?

## Ответ (RU)
Attribution Reporting API обеспечивает измерение конверсий и атрибуцию без cross-app отслеживания. Предоставляет два типа отчётов: event-level (ограниченные детальные данные) и aggregated (сводная статистика с differential privacy), позволяя рекламодателям измерять эффективность кампаний с сохранением приватности пользователей.

#### Типы отчётов

**1. Event-Level Reports:**
- Детальная информация об источнике (кампания, creative)
- Ограниченные данные о конверсии (3 бита = 0-7)
- Индивидуальные конверсии
- Для оптимизации кампаний

**2. Aggregate Reports:**
- Сводная статистика
- Детальные данные о конверсиях (revenue, quantity)
- Differential privacy шум
- Для измерения revenue

#### Ключевые концепции

**Source Events:**
- Ad impressions
- Ad clicks
- Priority (клики > impressions)
- Expiration windows

**Trigger Events:**
- Conversions (purchases, sign-ups)
- Trigger data (0-7 для event-level)
- Aggregate values (для aggregate)
- Deduplication keys

**Privacy Protections:**
- 3-bit ограничение (event-level)
- Differential privacy (aggregate)
- Rate limits
- Attribution windows

### Лучшие практики

1. **Выбор типа отчёта:** Event-level для оптимизации, aggregate для revenue
2. **Privacy budget:** Мониторинг, планирование стратегии
3. **Deduplication:** Использование ключей, локальное хранение
4. **Attribution windows:** Подходящие окна (7-30 дней)
5. **Тестирование:** Debug keys, валидация структуры

### Распространённые ошибки

1. Превышение 3-bit лимита → потеря данных
2. Нет deduplication → двойной подсчёт
3. Игнорирование privacy budget → сбои отчётов
4. Неправильные attribution windows → пропущенные атрибуции
5. Не обрабатывать недоступность API → потеря данных
6. Комбинировать с user ID → нарушение приватности

### Резюме

Attribution Reporting API обеспечивает измерение конверсий без отслеживания пользователей через два комплементарных подхода: event-level отчёты предоставляют детальную информацию об источнике с ограниченными данными о конверсии (3 бита), в то время как aggregate отчёты предлагают детальные метрики конверсий с differential privacy. Этот двойной подход балансирует гранулярную оптимизацию кампаний с комплексным измерением revenue, сохраняя приватность пользователей.
