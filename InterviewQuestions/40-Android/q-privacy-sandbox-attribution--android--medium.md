---
id: android-238
title: "Privacy Sandbox Attribution / Attribution Reporting API в Privacy Sandbox"
aliases: ["Attribution Reporting API в Privacy Sandbox", "Attribution Reporting API", "Privacy Sandbox Attribution"]
topic: android
subtopics: [privacy-sdks]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-privacy-sandbox-topics-api--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [advertising, android/privacy-sdks, attribution-reporting, difficulty/medium, privacy, privacy-sandbox]

---

# Вопрос (RU)

> Как работает Attribution Reporting API в Privacy Sandbox? Как измерять конверсии рекламы без отслеживания пользователей? В чём разница между event-level и aggregate отчётами?

# Question (EN)

> How does the Attribution Reporting API work in Privacy Sandbox? How do you measure ad conversions without tracking users? What are the differences between event-level and aggregate reports?

---

## Ответ (RU)

Attribution Reporting API обеспечивает измерение конверсий без cross-app отслеживания через два комплементарных механизма:

**Event-Level Reports:**
- Детальная информация об источнике (campaign ID, creative)
- Ограниченные данные конверсии (3 бита = значения 0-7)
- Задержка отправки с добавлением шума
- Использование: оптимизация кампаний, A/B тестирование

**Aggregate Reports:**
- Сводная статистика по множеству конверсий
- Детальные значения (revenue, quantity)
- Differential privacy (добавление шума к агрегированным данным)
- Использование: измерение revenue, детальная аналитика

**Основные концепции:**
- Source events (показы/клики) регистрируются с attribution destination
- Trigger events (конверсии) сопоставляются с source в пределах attribution window
- Отчёты отправляются на reporting endpoint с задержкой
- Rate limits предотвращают злоупотребления

### Регистрация Source И Trigger

```kotlin
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionManager(context: Context) {
    private val measurementManager =
        context.getSystemService(MeasurementManager::class.java)

    // ✅ Регистрация показа/клика рекламы
    suspend fun registerAdSource(
        sourceUrl: Uri,
        destination: Uri,
        inputEvent: InputEvent? = null
    ) = suspendCancellableCoroutine { cont ->
        val params = WebSourceParams.Builder(sourceUrl)
            .setDebugKeyAllowed(false)
            .build()

        val request = WebSourceRegistrationRequest.Builder(
            listOf(params),
            destination
        ).apply {
            inputEvent?.let { setInputEvent(it) }
        }.build()

        measurementManager?.registerWebSource(
            request,
            Executors.newSingleThreadExecutor(),
            OutcomeReceiver.create(
                { cont.resume(Unit) },
                { error -> cont.resumeWithException(error) }
            )
        )
    }

    // ✅ Регистрация конверсии
    suspend fun registerTrigger(triggerUrl: Uri) =
        suspendCancellableCoroutine { cont ->
        val params = WebTriggerParams.Builder(triggerUrl)
            .setDebugKeyAllowed(false)
            .build()

        val request = WebTriggerRegistrationRequest.Builder(
            listOf(params),
            Uri.parse("https://advertiser.example")
        ).build()

        measurementManager?.registerWebTrigger(
            request,
            Executors.newSingleThreadExecutor(),
            OutcomeReceiver.create(
                { cont.resume(Unit) },
                { error -> cont.resumeWithException(error) }
            )
        )
    }
}
```

### Event-Level Attribution

```kotlin
// Source registration JSON (server endpoint)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "expiry": "2592000",  // 30 days in seconds
  "priority": "100",
  "event_report_window": "2592000"
}

// Trigger registration JSON
{
  "event_trigger_data": [
    {
      "trigger_data": "3",  // 0-7 только (3 бита)
      "priority": "100",
      "deduplication_key": "conversion_456"
    }
  ]
}

// ❌ НЕПРАВИЛЬНО: Попытка передать >3 бит
val conversionValue = 150  // Слишком большое значение

// ✅ ПРАВИЛЬНО: Маппинг на 3-битное значение
val triggerData = when (conversionType) {
    ConversionType.PAGE_VIEW -> 0
    ConversionType.ADD_TO_CART -> 1
    ConversionType.CHECKOUT -> 2
    ConversionType.PURCHASE -> 3
    ConversionType.SIGN_UP -> 4
    else -> 7  // "other"
}
```

### Aggregate Attribution

```kotlin
// Source с aggregation keys (128-bit идентификаторы)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "aggregation_keys": {
    "campaign_counter": "0x1",
    "geo_value": "0x2",
    "purchase_value": "0x3"
  }
}

// Trigger с aggregate values
{
  "aggregatable_trigger_data": [
    {
      "key_piece": "0x1",
      "source_keys": ["campaign_counter"],
      "value": 1
    }
  ],
  "aggregatable_values": {
    "campaign_counter": 1,
    "purchase_value": 5000  // Детальное значение (cents)
  }
}

class AggregateTracking {
    // ✅ Детальные значения для aggregate
    suspend fun trackPurchase(
        orderId: String,
        totalValue: Double,
        itemCount: Int
    ) {
        val triggerUrl = buildAggregateTriggerUrl(
            purchaseValue = (totalValue * 100).toInt(),  // cents
            quantity = itemCount
        )
        attributionManager.registerTrigger(triggerUrl)
    }

    // ❌ НЕПРАВИЛЬНО: Хранение user ID вместе с attribution
    // Нарушает privacy
    data class Attribution(
        val userId: String,  // ЗАПРЕЩЕНО
        val conversionValue: Int
    )
}
```

### Privacy Protections

**Event-Level:**
- Ограничение 3 бита для trigger data
- Randomized reporting delay (2-30 дней)
- Rate limits на количество источников

**Aggregate:**
- Differential privacy noise добавляется к суммам
- Privacy budget (65536) распределяется между отчётами
- Encrypted payloads обрабатываются aggregation service

```kotlin
// Deduplication для предотвращения двойного подсчёта
class ConversionTracker(private val prefs: SharedPreferences) {

    // ✅ Проверка дубликатов перед регистрацией
    suspend fun trackIfNew(orderId: String, trigger: Uri) {
        val key = "conversion_$orderId"
        if (!prefs.contains(key)) {
            attributionManager.registerTrigger(trigger)
            prefs.edit().putLong(key, System.currentTimeMillis()).apply()
        }
    }
}
```

### Best Practices

**1. Выбор типа отчёта:**
- Event-level для оптимизации кампаний (какие ads работают)
- Aggregate для revenue measurement (сколько заработали)
- Комбинировать оба для полной картины

**2. Attribution windows:**
- Clicks: 7 дней (shorter journey)
- Impressions: 30 дней (longer journey)
- Настроить под customer journey вашего продукта

**3. Deduplication:**
- Использовать уникальные deduplication keys
- Хранить локально для проверки
- Критично для purchase events

**4. Privacy budget management:**
- Планировать aggregation queries заранее
- Мониторить потребление budget
- Приоритизировать важные метрики

---

## Answer (EN)

Attribution Reporting API enables conversion measurement without cross-app tracking through two complementary mechanisms:

**Event-Level Reports:**
- Detailed source information (campaign ID, creative)
- Limited conversion data (3 bits = values 0-7)
- Delayed delivery with added noise
- Use case: campaign optimization, A/B testing

**Aggregate Reports:**
- Summary statistics across multiple conversions
- Detailed values (revenue, quantity)
- Differential privacy (noise added to aggregated data)
- Use case: revenue measurement, detailed analytics

**Core concepts:**
- Source events (impressions/clicks) registered with attribution destination
- Trigger events (conversions) matched to sources within attribution window
- Reports sent to reporting endpoint with delay
- Rate limits prevent abuse

### Source and Trigger Registration

```kotlin
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionManager(context: Context) {
    private val measurementManager =
        context.getSystemService(MeasurementManager::class.java)

    // ✅ Register ad impression/click
    suspend fun registerAdSource(
        sourceUrl: Uri,
        destination: Uri,
        inputEvent: InputEvent? = null
    ) = suspendCancellableCoroutine { cont ->
        val params = WebSourceParams.Builder(sourceUrl)
            .setDebugKeyAllowed(false)
            .build()

        val request = WebSourceRegistrationRequest.Builder(
            listOf(params),
            destination
        ).apply {
            inputEvent?.let { setInputEvent(it) }
        }.build()

        measurementManager?.registerWebSource(
            request,
            Executors.newSingleThreadExecutor(),
            OutcomeReceiver.create(
                { cont.resume(Unit) },
                { error -> cont.resumeWithException(error) }
            )
        )
    }

    // ✅ Register conversion
    suspend fun registerTrigger(triggerUrl: Uri) =
        suspendCancellableCoroutine { cont ->
        val params = WebTriggerParams.Builder(triggerUrl)
            .setDebugKeyAllowed(false)
            .build()

        val request = WebTriggerRegistrationRequest.Builder(
            listOf(params),
            Uri.parse("https://advertiser.example")
        ).build()

        measurementManager?.registerWebTrigger(
            request,
            Executors.newSingleThreadExecutor(),
            OutcomeReceiver.create(
                { cont.resume(Unit) },
                { error -> cont.resumeWithException(error) }
            )
        )
    }
}
```

### Event-Level Attribution

```kotlin
// Source registration JSON (server endpoint)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "expiry": "2592000",  // 30 days in seconds
  "priority": "100",
  "event_report_window": "2592000"
}

// Trigger registration JSON
{
  "event_trigger_data": [
    {
      "trigger_data": "3",  // 0-7 only (3 bits)
      "priority": "100",
      "deduplication_key": "conversion_456"
    }
  ]
}

// ❌ WRONG: Trying to pass >3 bits
val conversionValue = 150  // Too large

// ✅ CORRECT: Map to 3-bit value
val triggerData = when (conversionType) {
    ConversionType.PAGE_VIEW -> 0
    ConversionType.ADD_TO_CART -> 1
    ConversionType.CHECKOUT -> 2
    ConversionType.PURCHASE -> 3
    ConversionType.SIGN_UP -> 4
    else -> 7  // "other"
}
```

### Aggregate Attribution

```kotlin
// Source with aggregation keys (128-bit identifiers)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "aggregation_keys": {
    "campaign_counter": "0x1",
    "geo_value": "0x2",
    "purchase_value": "0x3"
  }
}

// Trigger with aggregate values
{
  "aggregatable_trigger_data": [
    {
      "key_piece": "0x1",
      "source_keys": ["campaign_counter"],
      "value": 1
    }
  ],
  "aggregatable_values": {
    "campaign_counter": 1,
    "purchase_value": 5000  // Detailed value (cents)
  }
}

class AggregateTracking {
    // ✅ Detailed values for aggregate
    suspend fun trackPurchase(
        orderId: String,
        totalValue: Double,
        itemCount: Int
    ) {
        val triggerUrl = buildAggregateTriggerUrl(
            purchaseValue = (totalValue * 100).toInt(),  // cents
            quantity = itemCount
        )
        attributionManager.registerTrigger(triggerUrl)
    }

    // ❌ WRONG: Storing user ID with attribution
    // Violates privacy
    data class Attribution(
        val userId: String,  // FORBIDDEN
        val conversionValue: Int
    )
}
```

### Privacy Protections

**Event-Level:**
- 3-bit limit for trigger data
- Randomized reporting delay (2-30 days)
- Rate limits on number of sources

**Aggregate:**
- Differential privacy noise added to sums
- Privacy budget (65536) distributed across reports
- Encrypted payloads processed by aggregation service

```kotlin
// Deduplication to prevent double-counting
class ConversionTracker(private val prefs: SharedPreferences) {

    // ✅ Check for duplicates before registration
    suspend fun trackIfNew(orderId: String, trigger: Uri) {
        val key = "conversion_$orderId"
        if (!prefs.contains(key)) {
            attributionManager.registerTrigger(trigger)
            prefs.edit().putLong(key, System.currentTimeMillis()).apply()
        }
    }
}
```

### Best Practices

**1. Report type selection:**
- Event-level for campaign optimization (which ads work)
- Aggregate for revenue measurement (how much earned)
- Combine both for complete picture

**2. Attribution windows:**
- Clicks: 7 days (shorter journey)
- Impressions: 30 days (longer journey)
- Tune to your product's customer journey

**3. Deduplication:**
- Use unique deduplication keys
- Store locally for checking
- Critical for purchase events

**4. Privacy budget management:**
- Plan aggregation queries in advance
- Monitor budget consumption
- Prioritize important metrics

---

## Follow-ups

- How does attribution work when user switches devices?
- What happens when attribution window expires before conversion?
- How to handle multiple attribution sources (click + impression)?
- What is the privacy budget calculation mechanism?
- How does differential privacy noise affect small campaigns?
- Can you combine Attribution Reporting with Topics API?

## References

- 
- 
- [Privacy Sandbox Attribution Reporting](https://developer.android.com/design-for-safety/privacy-sandbox/attribution)

## Related Questions

### Prerequisites
-  - Topics API basics
-  - Differential privacy concepts

### Related
- [[q-privacy-sandbox-fledge--android--hard]] - FLEDGE API for remarketing
- [[q-privacy-sandbox-sdk-runtime--android--hard]] - SDK Runtime isolation

### Advanced
-  - Backend aggregation service
-  - Managing privacy budget at scale
