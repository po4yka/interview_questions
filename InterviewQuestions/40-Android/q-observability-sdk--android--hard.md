---
id: android-487
title: Design Client Observability & Health-Gated Rollouts / Проектирование клиентской
  наблюдаемости и health-gated релизов
aliases: [Design Client Observability & Health-Gated Rollouts, Проектирование клиентской наблюдаемости и health-gated релизов]
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
  - q-design-instagram-stories--android--hard
  - q-design-uber-app--android--hard
  - q-feature-flags-sdk--android--hard
  - q-wearos-health-connect-integration--android--hard
sources: []
created: 2025-10-29
updated: 2025-10-29
tags: [android/analytics, android/logging-tracing, android/performance-startup, difficulty/hard, topic/android]
date created: Saturday, November 1st 2025, 12:46:59 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
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

SDK наблюдаемости собирает метрики производительности, crash/ANR и обеспечивает health‑gated rollouts.

### Архитектура

Модули: metrics-core, trace, crash-anr, sampler, store, uploader (WorkManager/JobScheduler‑based), gates, flags.

SDK должен учитывать ограничения background execution и использовать надёжный, battery‑friendly механизм планирования задач (например, WorkManager) для отправки телеметрии.

### Data Model

Envelopes с session ID, device/app versions, sampled traces (cold/warm start, frame time percentiles), network timings, custom events. PII‑поля не включаются или редактируются/хэшируются до записи на диск и отправки.

### ANR/Crash

- Java/Kotlin: глобальный UncaughtExceptionHandler для перехвата и сериализации crash‑стеков.
- NDK: signal‑safe handlers для native crash, запись минимально необходимой информации.
- ANR: обнаружение через watchdog/Looper‑monitoring и/или разбор system traces (например, traces.txt) после ANR.
- Разбор crash/ANR артефактов на следующем запуске.
- Rate‑limit для избежания upload storms при массовых сбоях.

### Sampling

Динамические sampling keys per cohort; server‑tunable; обеспечить, чтобы экспериментальные и rollout‑кохонты сохраняли статистическую мощность.

### Upload

Backoff при failures, batching, учёт зарядки/сети; Wi‑Fi preferred, но возможность конфигурации (например, отправка по сотовой сети при небольших объёмах или длительной оффлайнности), чтобы избежать бесконечного откладывания.

Использовать надёжные фоновые механизмы (WorkManager/JobScheduler) и соблюдать ограничения Android на фоновую активность.

PII redaction и (ключевое) hashing для стабильных IDs выполняются на устройстве до сохранения и upload; поддержка режимов под GDPR/CCPA (opt‑out, ограничения по регионам, rotation идентификаторов).

### Health Gates

Определить SLOs (например, Crash‑free sessions > 99.8%, ANR rate < 0.3%, cold start p95 < 2.5s). SDK публикует агрегированные health‑метрики и экспонирует gates/conditions для клиента и backend.

Release pipeline/feature‑flag система использует эти метрики для автоматического приостановления rollout или rollback, если пороги нарушены (с порогами, гистерезисом и минимальными объёмами данных, чтобы снизить ложные срабатывания).

### Dashboards/Alerts

Экраны с p95/p99, device/OS/app version breakdowns, regression diff. Alerts и on‑call playbooks привязаны к этим метрикам.

### Тестирование

Synthetic crashes, эмуляция ANR, throttled uplinks, offline/large backlog сценарии, time skew, schema migrations, нагрузочные тесты на overhead.

### Tradeoffs

Богатые traces улучшают диагностику, но повышают privacy/cost/overhead; по умолчанию минимальные поля, включать deep traces и повышенный sampling через server flag во время инцидентов.

## Answer (EN)

Observability SDK collects performance metrics, crash/ANR data, and enables health‑gated rollouts.

### Architecture

Modules: metrics-core, trace, crash-anr, sampler, store, uploader (WorkManager/JobScheduler‑based), gates, flags.

The SDK must respect Android background execution limits and use reliable, battery‑friendly scheduling (e.g., WorkManager) for telemetry uploads.

### Data Model

Envelopes with session ID, device/app versions, sampled traces (cold/warm start, frame time percentiles), network timings, custom events. PII fields are excluded or redacted/hashed on-device before persistence and upload.

### ANR/Crash

- Java/Kotlin: global UncaughtExceptionHandler to capture and serialize crash stacks.
- NDK: signal‑safe handlers for native crashes, writing minimal safe state.
- ANR: detect via watchdog/Looper monitoring and/or parsing system traces (e.g., traces.txt) generated for ANRs.
- Parse crash/ANR artifacts on next launch.
- Apply rate‑limiting to avoid upload storms under mass failures.

### Sampling

Dynamic sampling keys per cohort; server‑tunable; ensure experiment and rollout cohorts maintain statistical power.

### Upload

Use backoff on failures, batching, and network/charging awareness. Prefer Wi‑Fi when possible but keep behavior configurable (e.g., allow cellular uploads for small payloads or long offline periods) to avoid indefinite deferral.

Use robust background mechanisms (WorkManager/JobScheduler) and follow Android background execution rules.

PII redaction and keyed hashing for stable identifiers happen on-device before storage/upload; support GDPR/CCPA modes (opt‑out, regional restrictions, identifier rotation).

### Health Gates

Define SLOs (e.g., Crash‑free sessions > 99.8%, ANR rate < 0.3%, cold start p95 < 2.5s). The SDK publishes aggregated health metrics and exposes gate conditions to the client and backend.

The release pipeline/feature‑flag system consumes these metrics to automatically pause rollout or roll back when thresholds are breached (with thresholds, hysteresis, and minimum sample sizes to reduce false positives).

### Dashboards/alerts

Screens with p95/p99, device/OS/app version breakdowns, regression diffs. Alerts and on‑call playbooks are tied to these metrics.

### Testing

Synthetic crashes, ANR emulation, throttled uplinks, offline/large backlog handling, time skew, schema migrations, and load tests to validate overhead.

### Tradeoffs

Rich traces improve diagnosis but increase privacy/cost/overhead; default to minimal fields and enable deep traces and higher sampling via server flags during incidents.

---

## Follow-ups

- How to balance telemetry collection with privacy regulations (GDPR/CCPA)?
- What sampling strategy ensures statistical validity while minimizing data volume?
- How to handle telemetry in offline scenarios and large backlogs?
- How to implement automatic rollback triggers without false positives?

## References

- [[q-feature-flags-sdk--android--hard]]
- [[c-workmanager]]
- [[c-room]]
- [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
- [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites (Easier)

- Understanding of Android app lifecycle and background execution

### Related (Same Level)

- [[q-feature-flags-sdk--android--hard]]

### Advanced (Harder)

- Design a global observability platform at Datadog/Firebase scale
