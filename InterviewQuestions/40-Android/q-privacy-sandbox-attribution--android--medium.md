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

Attribution Reporting API обеспечивает измерение конверсий без cross-app отслеживания через два комплементарных механизма атрибуции: event-level и aggregate отчёты. В Android Privacy Sandbox это реализовано с учётом on-device обработки, задержек и шума, без использования идентификаторов для cross-app трекинга. См. также [[c-android]].

Ниже примеры ориентированы на web-to-app/web сценарии с использованием MeasurementManager и показывают концепции формата отчётов. Формат JSON приведён упрощённо/концептуально (не как точный wire-format для всех реализаций).

**Event-Level Reports:**
- Детальная информация об источнике (например, campaign ID, creative), но ограниченная по количеству бит.
- Ограниченные данные конверсии (типичный пример — до 3 бит для trigger data, т.е. значения 0-7; точные лимиты зависят от конфигурации и могут эволюционировать).
- Задержка отправки с добавлением шума и батчированием.
- Использование: оптимизация кампаний, A/B тестирование, оценка эффективности creatives.

**Aggregate Reports:**
- Сводная статистика по множеству конверсий.
- Возможность кодировать более детальные значения (revenue, quantity и др.) в рамках агрегируемых payload'ов.
- Шум и защита приватности на стороне aggregation service / агрегирующей инфраструктуры.
- Использование: измерение revenue, конверсий по сегментам, более детальная аналитика в агрегированном виде.

**Основные концепции:**
- Source events (показы/клики) регистрируются с attribution destination и параметрами окна атрибуции.
- Trigger events (конверсии) сопоставляются с source в пределах attribution window по правилам приоритезации и дедупликации.
- Отчёты отправляются на reporting endpoint с задержкой, батчированием и добавлением шума для предотвращения идентификации пользователей.
- Rate limits ограничивают количество источников/триггеров и предотвращают злоупотребления.

### Регистрация Source И Trigger (web-to-app пример)

```kotlin
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionManager(context: Context) {
    private val measurementManager =
        context.getSystemService(MeasurementManager::class.java)

    // ✅ Регистрация показа/клика рекламы (web-to-app / web атрибуция, упрощённый пример)
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
            OutcomeReceiver { _, error ->
                if (error == null) cont.resume(Unit) else cont.resumeWithException(error)
            }
        )
    }

    // ✅ Регистрация конверсии (web trigger, упрощённый пример)
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
                OutcomeReceiver { _, error ->
                    if (error == null) cont.resume(Unit) else cont.resumeWithException(error)
                }
            )
        }
}
```

### Event-Level Attribution

```kotlin
// Упрощённый/концептуальный пример Source registration JSON (server endpoint)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "expiry": "2592000",  // 30 days in seconds
  "priority": "100",
  "event_report_window": "2592000"
}

// Упрощённый/концептуальный пример Trigger registration JSON
{
  "event_trigger_data": [
    {
      "trigger_data": "3",  // пример: 0-7 (3 бита) для event-level отчёта
      "priority": "100",
      "deduplication_key": "conversion_456"
    }
  ]
}

// ❌ НЕПРАВИЛЬНО: Попытка передать значение, не укладывающееся в доступные биты
val conversionValue = 150  // Слишком большое значение

// ✅ ПРАВИЛЬНО: Маппинг бизнес-событий в допустимый диапазон бит (пример)
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
// Упрощённый/концептуальный пример Source с aggregation keys
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "aggregation_keys": {
    "campaign_counter": "0x1",
    "geo_value": "0x2",
    "purchase_value": "0x3"
  }
}

// Упрощённый/концептуальный пример Trigger с aggregate values
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

class AggregateTracking(private val attributionManager: AttributionManager) {
    // ✅ Детальные значения для aggregate (упрощённый / псевдокод-паттерн)
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

    private fun buildAggregateTriggerUrl(purchaseValue: Int, quantity: Int): Uri {
        // Псевдореализация построения URL с нужными параметрами для aggregate trigger
        return Uri.parse("https://advertiser.example/trigger?value=$purchaseValue&qty=$quantity")
    }

    // ❌ НЕПРАВИЛЬНО: Хранение user ID вместе с attribution сигналами
    // Нарушает цели Privacy Sandbox и повышает риск деанонимизации
    data class Attribution(
        val userId: String,  // ЗАПРЕЩЕНО
        val conversionValue: Int
    )
}
```

### Privacy Protections

**Event-Level:**
- Ограничение доступных бит для trigger data (примерно несколько бит, для снижения возможности кодирования идентификатора пользователя).
- Randomized reporting delay: отчёты отправляются с задержкой и батчированием, чтобы усложнить отслеживание по времени.
- Rate limits на количество источников и триггеров.

**Aggregate:**
- Добавление шума и анонимизация на уровне агрегированных сумм.
- Использование зашифрованных payloads и aggregation service для обработки данных.

```kotlin
// Deduplication на стороне приложения для предотвращения двойного подсчёта
// (app-level guard, дополняет, но не заменяет механизмы API)
class ConversionTracker(
    private val prefs: SharedPreferences,
    private val attributionManager: AttributionManager
) {
    // ✅ Проверка дубликатов перед регистрацией (упрощённый пример)
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
- Event-level для оптимизации кампаний (какие объявления работают).
- Aggregate для измерения дохода и агрегированной аналитики.
- Комбинировать оба типа, соблюдая ограничения API и приватности.

**2. Attribution windows:**
- Для кликов обычно используются более короткие окна, чем для показов.
- Конкретные окна и тайминги определяются спецификацией Privacy Sandbox и конфигурацией источников.

**3. Deduplication:**
- Использовать deduplication keys, поддерживаемые API.
- При необходимости дополнять app-level проверками для критичных событий (например, покупок).

**4. Aggregation и privacy ограничения:**
- Планировать aggregation queries / breakdowns заранее и минимизировать количество различных срезов.
- Учитывать влияние шума и ограничений на точность метрик.
- Приоритизировать ключевые метрики с учётом privacy-бюджета и лимитов API.

---

## Answer (EN)

The Attribution Reporting API enables conversion measurement without cross-app tracking through two complementary attribution mechanisms: event-level and aggregate reports. In the Android Privacy Sandbox this is implemented with on-device processing, delays, and noise, without user-identifying cross-app IDs. See also [[c-android]].

The examples below focus on web-to-app/web scenarios using MeasurementManager and illustrate reporting concepts. JSON formats are simplified/conceptual and not the exact wire format for all Android implementations.

**Event-Level Reports:**
- Include detailed source information (e.g., campaign ID, creative), but with a limited number of bits.
- Contain restricted conversion data (a typical example is up to 3 bits for trigger data, i.e., 0-7; exact limits depend on configuration and may evolve).
- Delivered with delays, batching, and added noise.
- Use cases: campaign optimization, A/B testing, creative performance.

**Aggregate Reports:**
- Provide summary statistics across many conversions.
- Allow more detailed values (e.g., revenue, quantity) to be encoded in aggregatable payloads.
- Use noise and privacy protections enforced by the aggregation service / infrastructure.
- Use cases: revenue measurement, segmented performance analysis in aggregate.

**Core concepts:**
- Source events (impressions/clicks) are registered with an attribution destination and attribution window parameters.
- Trigger events (conversions) are matched to sources within the attribution window according to prioritization and deduplication rules.
- Reports are sent to reporting endpoints with delay, batching, and noise to prevent user identification.
- Rate limits constrain numbers of sources/triggers and prevent abuse.

### Source and Trigger Registration (web-to-app example)

```kotlin
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class AttributionManager(context: Context) {
    private val measurementManager =
        context.getSystemService(MeasurementManager::class.java)

    // ✅ Register ad impression/click (web-to-app / web attribution, simplified example)
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
            OutcomeReceiver { _, error ->
                if (error == null) cont.resume(Unit) else cont.resumeWithException(error)
            }
        )
    }

    // ✅ Register conversion (web trigger, simplified example)
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
                OutcomeReceiver { _, error ->
                    if (error == null) cont.resume(Unit) else cont.resumeWithException(error)
                }
            )
        }
}
```

### Event-Level Attribution

```kotlin
// Simplified/conceptual example of Source registration JSON (server endpoint)
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "expiry": "2592000",  // 30 days in seconds
  "priority": "100",
  "event_report_window": "2592000"
}

// Simplified/conceptual example of Trigger registration JSON
{
  "event_trigger_data": [
    {
      "trigger_data": "3",  // example: 0-7 (3 bits) for event-level report
      "priority": "100",
      "deduplication_key": "conversion_456"
    }
  ]
}

// ❌ WRONG: Trying to use a value that does not fit into available bits
val conversionValue = 150  // Too large

// ✅ CORRECT: Map business events into allowed bit range (example)
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
// Simplified/conceptual example: Source with aggregation keys
{
  "source_event_id": "campaign_123",
  "destination": "https://advertiser.example",
  "aggregation_keys": {
    "campaign_counter": "0x1",
    "geo_value": "0x2",
    "purchase_value": "0x3"
  }
}

// Simplified/conceptual example: Trigger with aggregate values
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

class AggregateTracking(private val attributionManager: AttributionManager) {
    // ✅ Detailed values for aggregate (simplified / pseudo-code pattern)
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

    private fun buildAggregateTriggerUrl(purchaseValue: Int, quantity: Int): Uri {
        // Pseudo implementation of building a URL for an aggregate trigger
        return Uri.parse("https://advertiser.example/trigger?value=$purchaseValue&qty=$quantity")
    }

    // ❌ WRONG: Storing user ID alongside attribution signals
    // Violates Privacy Sandbox goals and increases re-identification risk
    data class Attribution(
        val userId: String,  // FORBIDDEN
        val conversionValue: Int
    )
}
```

### Privacy Protections

**Event-Level:**
- Limited bits for trigger data (only a few bits to prevent encoding a unique identifier).
- Randomized reporting delay: batched/delayed reports to reduce timing-based tracking.
- Rate limits on the number of sources and triggers.

**Aggregate:**
- Noise and anonymization applied to aggregated results.
- Encrypted payloads processed by an aggregation service.

```kotlin
// Deduplication on the app side to prevent double-counting
// (app-level guard that complements, but does not replace, API mechanisms)
class ConversionTracker(
    private val prefs: SharedPreferences,
    private val attributionManager: AttributionManager
) {
    // ✅ Check for duplicates before registration (simplified example)
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
- Use event-level reports for campaign optimization (which ads perform better).
- Use aggregate reports for revenue and aggregate analytics.
- Combine both types within API constraints and privacy guarantees.

**2. Attribution windows:**
- Click-based sources typically use shorter windows than impression-based sources.
- Exact windows and timings are defined by Privacy Sandbox specs and source configuration.

**3. Deduplication:**
- Use deduplication keys supported by the API.
- Optionally complement with app-level checks for critical events (e.g., purchases).

**4. Aggregation and privacy constraints:**
- Plan aggregation queries/breakdowns upfront and minimize distinct slices.
- Account for the impact of noise and constraints on metric accuracy.
- Prioritize key metrics considering privacy budget and API limits.

---

## Дополнительные Вопросы (RU)

- Как работает атрибуция, если пользователь меняет устройство?
- Что происходит, если attribution window истекает до конверсии?
- Как обрабатывать несколько источников атрибуции (клик + показ)?
- Как работает механизм расчёта privacy budget?
- Как шум дифференциальной приватности влияет на маленькие кампании?
- Можно ли комбинировать Attribution Reporting с Topics API?

## Ссылки (RU)

- [Privacy Sandbox Attribution Reporting](https://developer.android.com/design-for-safety/privacy-sandbox/attribution)

## Связанные Вопросы (RU)

### Предварительные Материалы

- [[q-privacy-sandbox-topics-api--android--medium]] - Основы Topics API

### Похожие Вопросы

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
