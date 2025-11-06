---
id: android-487
title: Design Client Observability & Health-Gated Rollouts / Проектирование клиентской
  наблюдаемости и health-gated релизов
aliases:
- Design Client Observability & Health-Gated Rollouts
- Проектирование клиентской наблюдаемости и health-gated релизов
topic: android
subtopics:
- analytics
- logging-tracing
- performance-startup
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-room
- c-workmanager
- q-feature-flags-sdk--android--hard
sources: []
created: 2025-10-29
updated: 2025-10-29
tags:
- difficulty/hard
- android/analytics
- android/logging-tracing
- android/performance-startup
- topic/android
---

# Вопрос (RU)

> Как спроектировать SDK наблюдаемости для Android, который обеспечивает crash/perf метрики и health‑gated staged rollouts?

# Question (EN)

> How to design an observability SDK for Android with crash/perf metrics and health‑gated rollouts?

---

### Upgraded Interview Prompt (RU)

Спроектируйте SDK наблюдаемости для Android, который обеспечивает crash/perf метрики и health‑gated staged rollouts. Требования: SDK init <100мс, overhead батареи <0.3%/день, sampling, PII redaction, захват ANR/crash, metric dashboards, автоматический rollback при падении health ниже порогов.

### Upgraded Interview Prompt (EN)

Build an observability SDK for Android that powers crash/perf metrics and health‑gated staged rollouts. Requirements: SDK init <100ms, battery overhead <0.3%/day, sampling, PII redaction, ANR/crash capture, metric dashboards, and automatic rollback when health dips past thresholds.

## Ответ (RU)

SDK наблюдаемости собирает метрики производительности, crashes и обеспечивает health‑gated rollouts.

### Архитектура

Модули: metrics-core, trace, crash-anr, sampler, store, uploader, gates, flags.

### Data Model

Envelopes с session ID, device/app versions, sampled traces (cold/warm start, frame time percentiles), network timings, custom events.

### ANR/Crash

Signal‑safe handlers; tombstones парсятся на следующем запуске; rate‑limit для избежания upload storms.

### Sampling

Динамические sampling keys per cohort; server‑tunable; обеспечить experiment cells сохраняют статистическую мощность.

### Upload

Backoff при failures; Wi‑Fi preferred; batch. PII redaction и hashing для IDs; GDPR/CCPA toggles.

### Health Gates

Определить SLOs (например, Crash‑free sessions > 99.8%, ANR rate < 0.3%, cold start p95 < 2.5s). Release pipeline автоматически паузит или делает rollback, если пороги нарушены.

### Dashboards/Alerts

Экраны с p95/p99, device breakdowns, regression diff. On‑call playbooks связаны.

### Тестирование

Synthetic crashes, throttled uplinks, time skew, schema migrations.

### Tradeoffs

Богатые traces улучшают диагностику, но повышают privacy/cost; по умолчанию минимальные поля, включать deep traces через server flag во время инцидентов.

## Answer (EN)

Observability SDK collects performance metrics, crashes, and enables health‑gated rollouts.

### Architecture

metrics-core, trace, crash-anr, sampler, store, uploader, gates, flags.

### Data Model

Envelopes with session ID, device/app versions, sampled traces (cold/warm start, frame time percentiles), network timings, custom events.

### ANR/Crash

Signal‑safe handlers; tombstones parsed on next launch; rate‑limit to avoid upload storms.

### Sampling

Dynamic sampling keys per cohort; server‑tunable; ensure experiment cells keep statistical power.

### Upload

Backoff on failures; Wi‑Fi preferred; batch. PII redaction and hashing for IDs; GDPR/CCPA toggles.

### Health Gates

Define SLOs (e.g., Crash‑free sessions > 99.8%, ANR rate < 0.3%, cold start p95 < 2.5s). The release pipeline pauses or rolls back automatically if thresholds breach.

### Dashboards/alerts

Screens with p95/p99, device breakdowns, regression diff. On‑call playbooks linked.

### Testing

Synthetic crashes, throttled uplinks, time skew, schema migrations.

### Tradeoffs

Rich traces improve diagnosis but raise privacy/cost; default to minimal fields, enable deep traces via server flag during incidents.

---

## Follow-ups

-   How to balance telemetry collection with privacy regulations (GDPR/CCPA)?
-   What sampling strategy ensures statistical validity while minimizing data volume?
-   How to handle telemetry in offline scenarios and large backlogs?
-   How to implement automatic rollback triggers without false positives?

## References

-   [[q-feature-flags-sdk--android--hard]]
-   [[c-workmanager]]
-   [[c-room]]
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites (Easier)

-   Understanding of Android app lifecycle and background execution

### Related (Same Level)

-   [[q-feature-flags-sdk--android--hard]]

### Advanced (Harder)

-   Design a global observability platform at Datadog/Firebase scale
