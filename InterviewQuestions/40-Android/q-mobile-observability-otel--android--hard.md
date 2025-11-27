---
id: android-627
title: Mobile Observability with OpenTelemetry / Наблюдаемость на Android с OpenTelemetry
aliases: [Mobile Observability with OpenTelemetry, Наблюдаемость на Android с OpenTelemetry]
topic: android
subtopics:
  - logging-tracing
  - monitoring-slo
  - performance-battery
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - moc-android
  - q-android-lint-tool--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-main-thread-android--android--medium
  - q-parsing-optimization-android--android--medium
created: 2025-11-02
updated: 2025-11-11
tags: [android/logging-tracing, android/monitoring-slo, android/performance-battery, difficulty/hard, opentelemetry]
sources:
  - "https://developer.android.com/topic/performance/monitoring"
  - "https://opentelemetry.io/docs/instrumentation/android/"
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)
> Как построить наблюдаемость в Android-приложении с OpenTelemetry: структурированные логи, метрики, трассировки, фоновая отправка данных и ограничения батареи/приватности?

# Question (EN)
> How do you implement observability in an Android app using OpenTelemetry, covering structured logs, metrics, traces, background exporting, and power/privacy constraints?

---

## Ответ (RU)

## Краткая Версия
- Используем OpenTelemetry SDK на Android для трёх сигналов: логи, метрики, трассы.
- Централизованная инициализация провайдеров/экспортеров, буферизация и batching.
- Экспорт через `WorkManager`/фоновые задачи с `Constraints`, sampling и privacy-фильтрами.
- Учитываем батарею, сеть, офлайн-режим и требования приватности.

## Подробная Версия
### Требования

- Функциональные:
  - Собор структурированных логов, метрик и трассировок.
  - Корреляция сигналов (trace/span id, user/session id без PII).
  - Надёжная доставка: буферизация, retry, offline-режим.
- Нефункциональные:
  - Минимальное влияние на батарею, сеть и производительность.
  - Соблюдение приватности и законодательных требований.
  - Конфигурируемость (sampling, feature flags, opt-in/opt-out).

### Архитектура

- **SDK слой**: OpenTelemetry API (`Meter`, `Tracer`, `Logger`), включая провайдеры и экспортеры для всех трёх сигналов.
- **Transport слой**: OTLP exporter (gRPC/HTTP) с batching.
- **Storage**: Disk buffer (например, Proto/DataStore или SQLite) для offline и сглаживания пиков.
- **Governance**: sampling, privacy-фильтры, opt-in/opt-out UI и developer toggles.

### Инициализация

```kotlin
val resource = Resource.getDefault()
    .merge(
        Resource.create(
            Attributes.of(
                AttributeKey.stringKey("service.name"), "android-app",
            )
        )
    )

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

val loggerProvider = SdkLoggerProvider.builder()
    .setResource(resource)
    .addLogRecordProcessor(BatchLogRecordProcessor.builder(otlpLogExporter).build())
    .build()

OpenTelemetrySdk.builder()
    .setMeterProvider(meterProvider)
    .setTracerProvider(tracerProvider)
    .setLoggerProvider(loggerProvider)
    .buildAndRegisterGlobal()
```

- Используйте lazy init и DI (Singleton scope) для провайдеров/экспортеров.
- Для OTLP/gRPC используйте TLS и по возможности компрессию.
- Инициализацию выполняйте в `Application` или через startup/DI, избегая тяжёлых операций на UI-потоке.

### Инструментирование

- **Логи**: `Logger.logRecordBuilder()` с структурированными ключами (`event`, `screen`, `userJourneyId` и др.), без PII.
- **Метрики**: `LongCounter` для событий, `Histogram` для latency и размеров payload, `ObservableGauge` для state-based метрик.
- **Трейсы**: `Tracer.spanBuilder("login.request")` + атрибуты (network type, feature flag/experiment, result). Пропагируйте контекст через слои.
- Интегрируйте с gRPC/OkHttp interceptors, WorkManager listeners, ключевыми use-cases и критичными UI-флоу.

### Сбор И Отправка

- Используйте `BatchSpanProcessor` / `BatchLogRecordProcessor` (max queue size, export interval) для снижения накладных расходов.
- Offline storage: буферизация (например, через DataStore/SQLite/файлы) с eviction-политикой (drop oldest) для ограничения диска.
- Экспорт через `WorkManager` или собственный фоновый сервис c использованием `Constraints` (например, `requiredNetworkType = UNMETERED` при необходимости, `requiresCharging = true` для тяжёлых экспортов).
- Обрабатывайте backpressure: ограничивайте размер очереди и при переполнении сбрасывайте самые старые элементы или менее критичные сигналы.

### Оптимизация

- Sampling (например, `TraceIdRatioBasedSampler(0.05)`) для снижения нагрузки на сеть и бекенд, особенно для трассировок.
- Battery-aware: передавайте ограничения в `WorkManager` через `Constraints` и учитывайте системные сигналы (Doze, background restrictions), а не поллинг `BatteryManager` в рантайме.
- Privacy: удаляйте/маскируйте PII, хэшируйте идентификаторы, уважайте настройки пользователя (opt-out из аналитики/треккинга) и требования Google Play/OS.

### Наблюдение И Отладка

- Локально используйте `InMemorySpanExporter` / консольные экспортеры для отладки.
- Добавьте переключатели в developer settings для verbose-телеметрии и включения детализированных трасс.
- Интегрируйте с Crashlytics/Sentry: используйте OpenTelemetry-данные как breadcrumbs и для корреляции с трассами/метриками.
- См. также [[c-android]].

---

## Answer (EN)

## Short Version
- Use OpenTelemetry SDK on Android for logs, metrics, and traces.
- Centralized initialization of providers/exporters with buffering and batching.
- Export via `WorkManager`/background jobs with `Constraints`, plus sampling and privacy filters.
- Respect battery, network, offline behavior, and privacy requirements.

## Detailed Version
### Requirements

- Functional:
  - Collect structured logs, metrics, and traces.
  - Correlate signals (trace/span id, user/session id without PII).
  - Reliable delivery with buffering, retries, and offline support.
- Non-functional:
  - Minimal impact on battery, data usage, and performance.
  - Strong privacy and regulatory compliance.
  - Configurability (sampling, feature flags, opt-in/opt-out).

### Architecture

- SDK layer: OpenTelemetry API (`Meter`, `Tracer`, `Logger`) with providers and exporters for all three signals.
- Transport layer: OTLP exporter (gRPC/HTTP) with batching.
- Storage: disk buffer (e.g., Proto/DataStore or SQLite) for offline and smoothing peaks.
- Governance: sampling, privacy filters, opt-in/opt-out UI, and developer toggles.

### Initialization

```kotlin
val resource = Resource.getDefault()
    .merge(
        Resource.create(
            Attributes.of(
                AttributeKey.stringKey("service.name"), "android-app",
            )
        )
    )

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

val loggerProvider = SdkLoggerProvider.builder()
    .setResource(resource)
    .addLogRecordProcessor(BatchLogRecordProcessor.builder(otlpLogExporter).build())
    .build()

OpenTelemetrySdk.builder()
    .setMeterProvider(meterProvider)
    .setTracerProvider(tracerProvider)
    .setLoggerProvider(loggerProvider)
    .buildAndRegisterGlobal()
```

- Use lazy initialization and DI (singleton scope) for providers/exporters.
- Use TLS (and compression when appropriate) for OTLP/gRPC.
- Initialize in `Application` or via a startup/DI mechanism, avoiding heavy work on the main thread.

### Instrumentation

- Logs: use `Logger.logRecordBuilder()` with structured keys (e.g., `event`, `screen`, `userJourneyId`), no PII.
- Metrics: use `LongCounter` for events, `Histogram` for latency and payload sizes, `ObservableGauge` for state-based metrics.
- Traces: use `Tracer.spanBuilder("login.request")` with attributes (network type, feature flag/experiment, result). Propagate context across layers.
- Integrate instrumentation with gRPC/OkHttp interceptors, WorkManager listeners, and critical UI flows.

### Collection and Export

- Use `BatchSpanProcessor` / `BatchLogRecordProcessor` (configure max queue size and export interval) to reduce overhead.
- Offline storage: buffer data (e.g., using DataStore/SQLite/files) with an eviction policy (drop oldest) to cap disk usage.
- Export via `WorkManager` or a background component with appropriate `Constraints` (e.g., `requiredNetworkType = UNMETERED` when needed, `requiresCharging = true` for heavy exports).
- Handle backpressure: cap queue sizes and on overflow drop oldest or less critical telemetry.

### Optimization

- Sampling (e.g., `TraceIdRatioBasedSampler(0.05)`) to limit trace volume and backend load.
- Battery-aware behavior: rely on `WorkManager` constraints and respect system features (Doze, background restrictions) instead of manual `BatteryManager` polling loops.
- Privacy: redact/mask PII, hash identifiers, respect user analytics/tracking opt-out settings and Google Play/OS policies.

### Observability and Debugging

- For local debugging, use `InMemorySpanExporter` / console exporters.
- Provide developer settings toggles for verbose telemetry and detailed traces.
- Integrate with Crashlytics/Sentry and use OpenTelemetry signals as breadcrumbs and for correlating with traces/metrics.
- See also [[c-android]].

---

## Follow-ups (RU)
- Как объединить мобильные трассы с серверными (context propagation end-to-end)?
- Какие стратегии применять для differential privacy при сборе метрик?
- Как контролировать бюджет телеметрии (квоты на передачу данных и размер хранилища)?

## Follow-ups (EN)
- How to link mobile traces with backend traces (end-to-end context propagation)?
- What strategies can be used for differential privacy in telemetry collection?
- How to manage a telemetry budget (data transfer quotas and storage limits)?

## References (RU)
- [[moc-android]]
- "https://opentelemetry.io/docs/instrumentation/android/"
- "https://developer.android.com/topic/performance/monitoring"

## References (EN)
- [[moc-android]]
- "https://opentelemetry.io/docs/instrumentation/android/"
- "https://developer.android.com/topic/performance/monitoring"

## Related Questions

- [[q-android-performance-measurement-tools--android--medium]]
