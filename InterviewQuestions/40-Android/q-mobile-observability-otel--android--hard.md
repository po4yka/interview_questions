---
id: android-627
title: Mobile Observability with OpenTelemetry / Наблюдаемость на Android с OpenTelemetry
aliases:
- Mobile Observability with OpenTelemetry
- Наблюдаемость на Android с OpenTelemetry
topic: android
subtopics:
- logging-tracing
- monitoring-slo
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- c-mobile-observability
created: 2025-11-02
updated: 2025-11-02
tags:
- android/logging-tracing
- android/monitoring-slo
- difficulty/hard
sources:
- url: https://opentelemetry.io/docs/instrumentation/android/
  note: OpenTelemetry Android docs
- url: https://developer.android.com/topic/performance/monitoring
  note: Monitoring best practices
---

# Вопрос (RU)
> Как построить наблюдаемость в Android-приложении с OpenTelemetry: структурированные логи, метрики, трассировки, фоновая отправка данных и ограничения батареи/приватности?

# Question (EN)
> How do you implement observability in an Android app using OpenTelemetry, covering structured logs, metrics, traces, background exporting, and power/privacy constraints?

---

## Ответ (RU)

### 1. Архитектура

- **SDK слой**: OpenTelemetry API (`Meter`, `Tracer`, `Logger`).
- **Transport слой**: OTLP exporter (gRPC/HTTP) с batching.
- **Storage**: Disk buffer (Proto/DataStore) для offline.
- **Governance**: sampling, privacy filters, opt-in UI.

### 2. Инициализация

```kotlin
val resource = Resource.getDefault()
    .merge(Resource.create(Attributes.of(AttributeKey.stringKey("service.name"), "android-app")))

val meterProvider = SdkMeterProvider.builder()
    .setResource(resource)
    .registerMetricReader(
        PeriodicMetricReader.builder(otlpMetricExporter)
            .setInterval(Duration.ofMinutes(1))
            .build()
    )
    .build()

val tracerProvider = SdkTracerProvider.builder()
    .setResource(resource)
    .addSpanProcessor(BatchSpanProcessor.builder(otlpTraceExporter).build())
    .build()

OpenTelemetrySdk.builder()
    .setMeterProvider(meterProvider)
    .setTracerProvider(tracerProvider)
    .setLoggerProvider(loggerProvider)
    .buildAndRegisterGlobal()
```

- Используйте lazy init и DI (Singleton scope).
- Для gRPC используйте компрессию + TLS.

### 3. Инструментирование

- **Логи**: `Logger.logRecordBuilder()` с ключами `event`, `userJourneyId`.
- **Метрики**: `LongCounter` для событий, `Histogram` для latency.
- **Трейсы**: `Tracer.spanBuilder("login.request")` + attributes (network type, experiment).
- Интегрируйте с gRPC/OkHttp interceptors, WorkManager listeners.

### 4. Сбор и отправка

- BatchSpanProcessor (max queue size, export interval).
- Offline storage: Proto DataStore с eviction.
- Upload через WorkManager (constraints: unmetered + charging).
- Обрабатывайте backpressure (drop oldest spans).

### 5. Оптимизация

- Sampling (trace-based, ratio = 0.05) для снижения нагрузки.
- Battery-aware: suspend exports при `BatteryManager.isCharging` false (optional).
- Privacy: redact PII, хэшировать идентификаторы, respect `LIMIT_AD_TRACKING`.

### 6. Наблюдение & Debug

- Локально используйте `InMemorySpanExporter` + debug view.
- Добавьте toggle в developer settings для verbose logs.
- Интегрируйте с Crashlytics/Sentry (breadcrumbs).

---

## Answer (EN)

- Set up OpenTelemetry SDKs with batched exporters, disk buffering, and resource attributes describing the app build.
- Instrument logs, metrics, and traces across networking, WorkManager, and UI flows; propagate context (correlation IDs).
- Export telemetry via WorkManager respecting network/power constraints, with sampling and privacy filters.
- Provide developer toggles for debugging and integrate with backend observability pipelines for correlation.

---

## Follow-ups
- Как объединить Mobile telemetry с серверными трассами (context propagation)?
- Какие стратегии для differential privacy при сборе метрик?
- Как отслеживать бюджет телеметрии (квоты на передачу данных)?

## References
- [[c-mobile-observability]]
- https://opentelemetry.io/docs/instrumentation/android/
- https://developer.android.com/topic/performance/monitoring

## Related Questions

- [[c-mobile-observability]]
