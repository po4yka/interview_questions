---
id: 20251029-170211
title: Design Feature Flags & Experimentation SDK / Проектирование SDK флагов и экспериментов
aliases:
    [
        Design Feature Flags SDK,
        Проектирование SDK флагов функций,
        Feature Flags Architecture,
        Архитектура флагов функций,
    ]
topic: android
subtopics: [architecture-clean, networking-http, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-clean-architecture, c-dependency-injection, c-workmanager]
sources: []
created: 2025-10-29
updated: 2025-10-29
tags:
    [
        android/architecture-clean,
        android/networking-http,
        android/service,
        difficulty/hard,
        platform/android,
        lang/kotlin,
        feature-flags,
        experimentation,
        sdk,
    ]
date created: Wednesday, October 29th 2025, 5:03:10 pm
date modified: Thursday, October 30th 2025, 12:47:49 pm
---

# Вопрос (RU)

> Как спроектировать SDK флагов функций и экспериментов для Android?

# Question (EN)

> How to design a feature flags & experimentation SDK for Android?

---

### Upgraded Interview Prompt (RU)

Спроектируйте клиентский SDK флагов функций для Android. Цели: bootstrap <150мс при холодном старте, sticky assignments, офлайн кеш с TTL, семантика kill‑switch, privacy‑safe exposure logging. Обработайте мульти‑окружения, динамические конфиги, targeting rules, эксперименты. Включите схему/версионирование, безопасность, наблюдаемость, релиз.

### Upgraded Interview Prompt (EN)

Design a client‑side feature flag SDK for Android. Targets: bootstrap <150ms at cold start, sticky assignments, offline cache with TTL, kill‑switch semantics, and privacy‑safe exposure logging. Handle multi‑environment, dynamic configs, targeting rules, and experimentation. Include schema/versioning, security, observability, and rollout.

## Ответ (RU)

SDK флагов функций обеспечивает динамическое включение/выключение функций и A/B тестирование.

### Архитектура

Модули: flags-core, evaluator, store, network, telemetry, flags-ui. Предоставить contract tests для rule evaluation.

### Bootstrap

Загрузка last good config с диска (protobuf/JSON) <150мс; ленивая загрузка обновления post‑init с ETag/If‑None‑Match. Sticky через hashed user/device key.

### Evaluation

Rule tree → детерминированное bucketing (Murmur/xxHash) → variant. Поддержка server overrides и локальных failsafe defaults.

### Cache & TTL

Персист config с TTL; если истёк и офлайн, продолжать с last good + alert. Защита через checksum/signature.

### Kill‑switch

Выделенный remote boolean для мгновенного отключения функций; уважать в течение секунд через FCM nudge + short‑poll fallback.

### Telemetry

Exposure events буферизованы; flush на app foreground или каждые N минут; PII‑redacted; backpressure limits.

### Безопасность

Signed configs; верификация подписи; хранение в EncryptedFile при необходимости. Не отправлять targeting rules, раскрывающие PII.

### Наблюдаемость

Bootstrap latency, cache hit, evaluation errors, exposure rate, disk read/write time. Health‑gated rollout версий SDK.

### Тестирование

Golden vectors для rules, chaos для коррупции config, clock‑skew тесты.

### Tradeoffs

On‑device evaluation снижает latency, но рискует logic drift; митигируем версионированными evaluators и contract tests.

## Answer (EN)

Feature flags SDK enables dynamic feature toggles and A/B testing.

### Architecture

flags-core, evaluator, store, network, telemetry, flags-ui. Provide contract tests for rule evaluation.

### Bootstrap

Load last good config from disk (protobuf/JSON) <150ms; lazy fetch update post‑init with ETag/If‑None‑Match. Stickiness via hashed user/device key.

### Evaluation

Rule tree → deterministic bucketing (Murmur/xxHash) → variant. Support server overrides and local failsafe defaults.

### Cache & TTL

Persist config with TTL; if expired and offline, continue with last good + alert. Protect with checksum/signature.

### Kill‑switch

Dedicated remote boolean to disable features instantly; honor within seconds via FCM nudge + short‑poll fallback.

### Telemetry

Exposure events buffered; flush on app foreground or every N minutes; PII‑redacted; backpressure limits.

### Security

Signed configs; verify signature; store in EncryptedFile if sensitive. Don't ship targeting rules that expose PII.

### Observability

Bootstrap latency, cache hit, evaluation errors, exposure rate, disk read/write time. Health‑gated rollout of SDK versions.

### Testing

Golden vectors for rules, chaos for config corruption, clock‑skew tests.

### Tradeoffs

On‑device evaluation reduces latency but risks logic drift; mitigate with versioned evaluators and contract tests.

---

## Follow-ups

-   How to handle schema migration for flag configurations?
-   What strategy ensures statistical power in A/B experiments?
-   How to prevent feature flag leaks and security issues?
-   How to optimize bootstrap latency while maintaining freshness?

## References

-   [[c-clean-architecture]]
-   [[c-dependency-injection]]
-   [[c-workmanager]]
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites (Easier)

-   Understanding of dependency injection and architecture patterns

### Related (Same Level)

-   [[q-observability-sdk--android--hard]]

### Advanced (Harder)

-   Design a global experimentation platform at Netflix scale
