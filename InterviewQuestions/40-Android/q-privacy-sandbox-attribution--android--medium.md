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
related: [c-android, q-privacy-sandbox-topics-api--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [advertising, android/privacy-sdks, attribution-reporting, difficulty/medium, privacy, privacy-sandbox]
---

# Вопрос (RU)

> Как работает Attribution Reporting API в Privacy Sandbox? Как измерять конверсии рекламы без отслеживания пользователей? В чём разница между event-level и aggregate отчётами?

# Question (EN)

> How does the Attribution Reporting API work in Privacy Sandbox? How do you measure ad conversions without tracking users? What are the differences between event-level and aggregate reports?

---

## Ответ (RU)

Attribution Reporting API обеспечивает измерение конверсий без cross-app отслеживания через два комплементарных механизма. См. также [[c-android]].

**Event-Level Reports:**
- Детальная информация об источнике (campaign ID, creative)
- Ограниченные данные конверсии (3 бита = значения 0-7)
- Задержка отправки с добавлением шума
- Использование: оптимизация кампаний, A/B тестирование

**Aggregate Reports:**
- Сводная статистика по множеству конверсий
- Детальные значения (revenue, quantity)
- Шум и защита приватности на стороне aggregation service
- Использование: измерение revenue, детальная аналитика

**Основные концепции:**
- Source events (показы/клики) регистрируются с attribution destination
- Trigger events (конверсии) сопоставляются с source в пределах attribution window
- Отчёты отправляются на reporting endpoint с задержкой и с учётом privacy-защит
- Rate limits предотвращают злоупотребления

### Регистрация Source И Trigger

```kotlin
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionManager(context: Context) {
    private val measurementManager =
        context.getSystemService(MeasurementManager::class.java)

    // ✅ Регистрация показа/клика рекламы (web-to-app / web attribution пример)
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

    // ✅ Регистрация конверсии (web trigger пример)
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
// Упрощённый пример Source registration JSON (server endpoint)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "expiry": "2592000",  // 30 days in seconds
  "priority": "100",
  "event_report_window": "2592000"
}

// Упрощённый пример Trigger registration JSON
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
// Упрощённый пример Source с aggregation keys
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "aggregation_keys": {
    "campaign_counter": "0x1",
    "geo_value": "0x2",
    "purchase_value": "0x3"
  }
}

// Упрощённый пример Trigger с aggregate values
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
    // ✅ Детальные значения для aggregate (упрощённый паттерн)
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
    // Нарушает privacy и цели API
    data class Attribution(
        val userId: String,  // ЗАПРЕЩЕНО
        val conversionValue: Int
    )
}
```

### Privacy Protections

**Event-Level:**
- Ограничение 3 бита для trigger data
- Randomized reporting delay (периодическая отправка с задержкой, минимизирует отслеживание по времени)
- Rate limits на количество источников и триггеров

**Aggregate:**
- Шум и анонимизация на уровне агрегированных сумм
- Использование aggregation service и зашифрованных payloads для обработки

```kotlin
// Deduplication на стороне приложения для предотвращения двойного подсчёта
class ConversionTracker(private val prefs: SharedPreferences) {

    // ✅ Проверка дубликатов перед регистрацией (app-level guard, не часть протокола)
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
- Комбинировать оба для более полной картины в рамках ограничений API

**2. Attribution windows:**
- Для кликов обычно используются более короткие окна, чем для показов
- Конкретные окна и тайминги определяются спецификацией API и конфигурацией источников

**3. Deduplication:**
- Использовать deduplication keys, поддерживаемые API
- При необходимости дополнять app-level проверками
- Критично для purchase events

**4. Privacy budget / queries:**
- Планировать aggregation queries заранее и минимизировать количество различных срезов
- Мониторить эффекты шума и ограничений на точность
- Приоритизировать важные метрики, учитывая ограничения приватности

---

## Answer (EN)

Attribution Reporting API enables conversion measurement without cross-app tracking through two complementary mechanisms. See also [[c-android]].

**Event-Level Reports:**
- Detailed source information (campaign ID, creative)
- Limited conversion data (3 bits = values 0-7)
- Delayed delivery with added noise
- Use case: campaign optimization, A/B testing

**Aggregate Reports:**
- Summary statistics across multiple conversions
- Detailed values (revenue, quantity)
- Privacy protection and noise applied by the aggregation service
- Use case: revenue measurement, detailed analytics

**Core concepts:**
- Source events (impressions/clicks) registered with an attribution destination
- Trigger events (conversions) matched to sources within an attribution window
- Reports sent to reporting endpoint with delay and built-in privacy protections
- Rate limits prevent abuse

### Source and Trigger Registration

```kotlin
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionManager(context: Context) {
    private val measurementManager =
        context.getSystemService(MeasurementManager::class.java)

    // ✅ Register ad impression/click (web-to-app / web attribution example)
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

    // ✅ Register conversion (web trigger example)
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
// Simplified example of Source registration JSON (server endpoint)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "expiry": "2592000",  // 30 days in seconds
  "priority": "100",
  "event_report_window": "2592000"
}

// Simplified example of Trigger registration JSON
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
// Simplified example: Source with aggregation keys
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "aggregation_keys": {
    "campaign_counter": "0x1",
    "geo_value": "0x2",
    "purchase_value": "0x3"
  }
}

// Simplified example: Trigger with aggregate values
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
    // ✅ Detailed values for aggregate (simplified pattern)
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
    // Violates privacy goals of the API
    data class Attribution(
        val userId: String,  // FORBIDDEN
        val conversionValue: Int
    )
}
```

### Privacy Protections

**Event-Level:**
- 3-bit limit for trigger data
- Randomized reporting delay (batched and delayed to reduce timing-based tracking)
- Rate limits on number of sources and triggers

**Aggregate:**
- Noise and anonymization applied to aggregated sums
- Encrypted payloads processed by an aggregation service

```kotlin
// Deduplication on app side to prevent double-counting
class ConversionTracker(private val prefs: SharedPreferences) {

    // ✅ Check for duplicates before registration (app-level guard, not protocol-required)
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
- Combine both for a more complete picture within API constraints

**2. Attribution windows:**
- Click-based sources typically use shorter windows than impression-based sources
- Exact windows and timings are defined by the API specification and source configuration

**3. Deduplication:**
- Use deduplication keys supported by the API
- Optionally complement with app-level checks
- Critical for purchase events

**4. Aggregation and privacy constraints:**
- Plan aggregation queries in advance and minimize the number of distinct breakdowns
- Monitor the impact of noise and constraints on accuracy
- Prioritize key metrics given privacy limitations

---

## Дополнительные вопросы (RU)

- Как работает атрибуция, если пользователь меняет устройство?
- Что происходит, если attribution window истекает до конверсии?
- Как обрабатывать несколько источников атрибуции (клик + показ)?
- Как работает механизм расчёта privacy budget?
- Как шум дифференциальной приватности влияет на маленькие кампании?
- Можно ли комбинировать Attribution Reporting с Topics API?

## Ссылки (RU)

- [Privacy Sandbox Attribution Reporting](https://developer.android.com/design-for-safety/privacy-sandbox/attribution)

## Связанные вопросы (RU)

### Предварительные материалы

- [[q-privacy-sandbox-topics-api--android--medium]] - Основы Topics API

### Похожие вопросы

- [[q-privacy-sandbox-fledge--android--hard]] - FLEDGE API для ремаркетинга
- [[q-privacy-sandbox-sdk-runtime--android--hard]] - Изоляция SDK Runtime

### Продвинутое

- Управление privacy budget в масштабных системах (отдельная заметка отсутствует)

## Follow-ups

- How does attribution work when user switches devices?
- What happens when attribution window expires before conversion?
- How to handle multiple attribution sources (click + impression)?
- What is the privacy budget calculation mechanism?
- How does differential privacy noise affect small campaigns?
- Can you combine Attribution Reporting with Topics API?

## References

- [Privacy Sandbox Attribution Reporting](https://developer.android.com/design-for-safety/privacy-sandbox/attribution)

## Related Questions

### Prerequisites

- [[q-privacy-sandbox-topics-api--android--medium]] - Topics API basics

### Related

- [[q-privacy-sandbox-fledge--android--hard]] - FLEDGE API for remarketing
- [[q-privacy-sandbox-sdk-runtime--android--hard]] - SDK Runtime isolation

### Advanced

- Managing privacy budget at scale (note missing)
