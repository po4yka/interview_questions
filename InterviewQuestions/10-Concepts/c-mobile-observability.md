---\
id: "20260108-110550"
title: "Mobile Observability / Наблюдаемость мобильных приложений"
aliases: ["Android Observability", "Mobile Telemetry"]
summary: "Instrumentation patterns for logs, metrics, traces in mobile apps with OpenTelemetry and gRPC"
topic: "android"
subtopics: ["logging", "observability", "telemetry"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-11-02"
updated: "2025-11-02"
tags: ["android", "concept", "logging", "observability", "telemetry", "difficulty/medium"]
---\

# Summary (EN)

Mobile observability combines structured logging, metrics, and tracing within Android apps. OpenTelemetry SDKs, gRPC interceptors, and background upload pipelines collect telemetry while respecting battery/network budgets.

# Сводка (RU)

Наблюдаемость мобильных приложений сочетает структурированные логи, метрики и трассировки. SDK OpenTelemetry, перехватчики gRPC и фоновые пайплайны загрузки собирают телеметрию, учитывая ограничения батареи и сети.

## Key Components

- Structured logging (`Logcat`, JSON sinks, Timber with formatters)
- Metrics (OpenTelemetry `Meter`, StatsD, custom counters)
- Tracing (OpenTelemetry `Tracer`, Activity/Span hierarchy)
- Exporters (OTLP/gRPC, HTTP batching, offline storage via Proto/DataStore)

## Considerations

- Sampling strategies для экономии батареи.
- Privacy: удаление PII, шифрование, user opt-in.
- Backpressure: очереди, `WorkManager` for uploads.

