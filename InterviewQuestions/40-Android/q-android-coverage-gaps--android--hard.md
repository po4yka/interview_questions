---
id: android-613
title: Android Coverage Gaps / Пробелы в покрытии Android
aliases:
  - Android Coverage Gaps
  - Пробелы в покрытии Android
  - Missing Android Topics
topic: android
subtopics:
  - roadmap
  - coverage
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-dependency-injection
  - q-koin-vs-dagger-philosophy--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/coverage
  - knowledge-gap
  - backlog
  - difficulty/hard
sources: []
---

# Вопрос (RU)
> Какие важные области Android ещё не покрыты в хранилище? Сформируйте исчерпывающий список пробелов и вероятность их востребованности на собеседованиях.

# Question (EN)
> Which Android topic areas are still missing from the vault? Provide a comprehensive gap list and note why each matters for interviews.

---

## Ответ (RU)

### Краткое резюме

В текущем хранилище 494 заметки по Android, но остаются критичные пробелы. Ниже — приоритетные области, которые регулярно всплывают на собеседованиях (Senior/Staff) и требуют пополнения базы. Для каждой области указаны ключевые подтемы и формат будущих заметок.

### 1. Современная работа с камерой и мультимедиа
- **CameraX Advanced**: pipeline, `ImageAnalysis`, `Camera2Interop`, настройка экспозиции/фокуса, обработка кадров в реальном времени.
- **Media3 / ExoPlayer 2 → Media3 миграция**: architecture components, customizable `PlayerView`, DRM, offline playback, streaming ABR.
- **Видео-захват и редакторы**: стабилизация, `MediaCodec`, `MediaMuxer`, фоновые задачи (WorkManager + ForegroundService).

### 2. Большие экраны, foldables и адаптивная верстка
- **Jetpack Window Manager**: `WindowSizeClass`, posture API, handling hinge/folding states.
- **Responsive UI patterns**: master-detail, adaptive navigation, Compose adaptive layouts.
- **ChromeOS/Tablet адаптация**: input modes, multi-window quirks, performance tuning.

### 3. Wearables, Health и окружающая экосистема
- **Wear OS Compose**: scaling lazy lists, complications, navigation на часах.
- **Health Services / Health Connect**: permission model, data sync, privacy constraints.
- **Sensor APIs и low-power**: batching, significant motion, background delivery limits.

### 4. Монетизация и комплаенс
- **Google Play Billing v5/v6**: subscriptions, offers, server-side APIs, pending transactions.
- **Play Integrity / SafetyNet миграция**: attestation workflows, device integrity checks.
- **Regional compliance**: GDPR/CPA hooks, age verification, parental controls (в контексте Android SDK).

### 5. Расширенные каналы взаимодействия
- **NFC / UWB / Nearby**: tap-to-pay flows, background tag reading, ranging, handshake protocols.
- **App Links & Deferred Deep Links**: verification, testing, analytics attribution.
- **Glance / App Widgets (Compose)**: update cadence, limitations, interoperability с LiveData/Flow.

### 6. Платформенные особенности и интеграции
- **Android Auto / Automotive OS**: templated UI, messaging/media requirements, driver distraction rules.
- **Android TV / Google TV**: Leanback/Compose for TV, remote input patterns, certification checklists.
- **Enterprise/MDM**: Work profile APIs, device policy management, zero-touch enrollment.

### 7. Observability & Performance beyond basics
- **Perfetto / Frame Timeline**: trace analysis, jank classification.
- **Power profiling**: Battery Historian, Android Studio Energy Profiler, wake-lock audits.
- **Client observability**: gRPC/OpenTelemetry instrumentation on Android clients.

### Предлагаемый план пополнения
1. Сначала подготовить концепт заметку + 1 Q&A по каждой секции (начать с CameraX и Billing).
2. Добавить соответствующие `tags` (`android/camerax`, `android/billing`, `android/foldable` и т.п.) в `TAXONOMY.md`.
3. Расширить `moc-android` отдельными подразделами для новых направлений.
4. Настроить Dataview-отчёт по прогрессу закрытия пробелов (draft → ready).

---

## Answer (EN)

### Quick Summary

The vault holds 494 Android notes, yet several interview-critical gaps remain. The list below groups the highest-priority areas for senior-level discussions, with subtopics and suggested note types to add.

### 1. Modern camera & media pipeline
- **CameraX advanced usage**: pipeline control, `ImageAnalysis`, `Camera2Interop`, manual exposure/focus, real-time frame processing.
- **Media3 / ExoPlayer migration**: player architecture, DRM, offline downloads, adaptive bitrate streaming, custom UI components.
- **Video capture & editors**: stabilization, `MediaCodec` + `MediaMuxer`, background constraints (WorkManager + ForegroundService).

### 2. Large screens, foldables, adaptive layouts
- **Jetpack Window Manager**: `WindowSizeClass`, posture APIs, hinge/fold state handling.
- **Responsive patterns**: master-detail, adaptive navigation, Compose adaptive layout patterns.
- **ChromeOS/tablet readiness**: input modes, multi-window behavior, performance tuning.

### 3. Wearables, Health, ecosystem surfaces
- **Wear OS with Compose**: lazy list scaling, complications, navigation.
- **Health Services / Health Connect**: permission model, data sync, privacy boundaries.
- **Sensor APIs & low power**: batching, significant motion, background delivery caps.

### 4. Monetization & compliance
- **Google Play Billing v5/v6**: subscriptions, pricing phases, server verification, pending purchases.
- **Play Integrity / SafetyNet migration**: attestation flows, device integrity policy.
- **Regional compliance hooks**: GDPR/CPA, age gates, parental controls in the Android SDK context.

### 5. Extended connectivity & surfaces
- **NFC / UWB / Nearby**: tap-to-pay, background tag reading, ranging accuracy, handshake design.
- **App Links & deferred deep links**: asset verification, QA strategies, analytics integration.
- **Glance / Compose widgets**: update cadence, limitations, state management with LiveData/Flow.

### 6. Platform specialties & integrations
- **Android Auto / Automotive OS**: templated UI limitations, media/messaging guidelines, driver distraction rules.
- **Android TV / Google TV**: Leanback/Compose for TV, remote input, certification checklist.
- **Enterprise/MDM**: Work profile APIs, Device Policy Manager, zero-touch enrollment lifecycle.

### 7. Observability & performance beyond basics
- **Perfetto / Frame timeline**: trace reading, jank categorization, regression tracking.
- **Power profiling**: Battery Historian, Energy Profiler, wake-lock audits and mitigations.
- **Client observability**: gRPC/OpenTelemetry instrumentation on Android clients, sampling strategies.

### Recommended next steps
1. Seed each section with one concept note plus a focused Q&A (start with CameraX and Play Billing).
2. Extend the tag taxonomy with dedicated namespaces (`android/camerax`, `android/billing`, `android/foldable`, etc.).
3. Update `moc-android` with new subsections mirroring the gap list.
4. Add a Dataview tracker to monitor gap closure (draft → reviewed → ready).

---

## Follow-ups
- Какие конкретные ресурсы (документация, codelabs) использовать для каждого добавления?
- Нужен ли отдельный roadmap-файл с дедлайнами по закрытию пробелов?
- Как интегрировать проверки на пробелы в автоматизированные отчёты (`Link Health`, `Dataview`)?

## References
- [[moc-android]]
- [[c-dependency-injection]]
- [[q-koin-vs-dagger-philosophy--android--hard]]
