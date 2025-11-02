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

В текущем хранилище уже закрыты крупные пробелы (CameraX, Media3, Wear Compose, Billing, Auto/TV, MDM), однако остаются новые высокоприоритетные темы. Ниже перечислены области, которые всё ещё требуют освещения в формате concept + Q&A заметок.

### 1. Безопасность и соответствие требованиям
- **Android Data Safety & Safety Labels**: процессы заполнения форм Play Console, автоматизация деклараций, связка с внутренней политикой privacy.
- **Сетевые защиты**: certificate pinning, `Network Security Config`, key attestation, mutual TLS.
- **Sensitive data lifecycle**: шифрование файлов, безопасное кеширование, интеграция с Safety Center/privileged APIs.

### 2. Продвинутые коммуникационные поверхности
- **Conversation notifications & Bubbles**: API уровни, UX best practices, ограничения Android 13+.
- **CallStyle/Foreground Service specials**: emergency access, mic/camera indicators, privacy chips.
- **ShareSheet & cross-app collaboration**: `ChooserTarget`, `ShortcutInfo` interop, predictive back.

### 3. Maps & геопространственные сервисы
- **Compose for Maps / Maps SDK v4**: управляемые камеры, marker clusters, theming.
- **Geospatial anchors & AR navigation**: интеграция Maps + ARCore Geospatial.
- **Offline/Hybrid навигация**: синхронизация карт, storage budgeting, разрешения.

### 4. Release engineering & качество
- **Play Console automation**: Play Vitals, ANR/Rollback dashboards, pre-launch reports triage.
- **App Bundles advanced**: Play Asset Delivery (install-time/fast-follow), dynamic features migration.
- **Continuous delivery**: internal app sharing, staged rollouts, automated compliance checks.

### 5. Accessibility & инклюзивность на продвинутом уровне
- **Switch Access / универсальный доступ**: паттерны UI, semantics, тестирование.
- **Text-to-speech & multimodal UX**: captions, live transcription, audio descriptions.
- **Globalization**: bi-directional layouts, number/date localization, font fallback (CJK).

### План действий
1. Подготовить концепт + Q&A по каждой секции (начать с Security и Conversation surfaces).
2. Добавить новые `tags` (`android/security-hardening`, `android/bubbles`, `android/maps-compose`, `android/release`) в `TAXONOMY.md`.
3. Обновить `moc-android`, добавив секции Security, Communication Surfaces, Release Engineering.
4. Настроить Dataview-виджет для отслеживания прогресса по новым направлениям (draft → ready).

---

## Answer (EN)

### Quick Summary

The vault now covers recent additions (CameraX, Media3, Wear Compose, Billing, Auto/TV, MDM), yet several senior-level gaps remain. These are the next priorities for concept + Q&A coverage.

### 1. Advanced communication surfaces
- **Conversation notifications & Bubbles**: APIs across Android 11–14, UX caveats, background limits.
- **CallStyle/Foreground service compliance**: emergency affordances, mic/camera indicators, privacy chips.
- **ShareSheet collaboration**: `ChooserTarget`, dynamic shortcuts, predictive back support.

### 2. Maps & geospatial experiences
- **Compose for Maps / Maps SDK v4**: managing camera state, clustering, theming.
- **Geospatial anchors & AR navigation**: combining Maps + ARCore Geospatial.
- **Offline/hybrid navigation**: map syncing, storage budgeting, runtime permissions.

### 3. Release engineering & quality operations
- **Play Console automation**: Play Vitals dashboards, ANR debugging, rollback workflows, pre-launch report triage.
- **App Bundles advanced**: Play Asset Delivery (install/fast-follow/on-demand), feature modularization.
- **Continuous delivery**: internal app sharing, staged rollouts, automated compliance checks.

### 4. Accessibility & inclusion at scale
- **Switch Access / universal access**: semantics, focus management, testing strategies.
- **Text-to-speech & multimodal UX**: live captions, audio descriptions, spoken feedback integration.
- **Globalization**: RTL layouts, localized formatting, font fallback for complex scripts.

### Next steps
1. Prioritize Communication surfaces for the next round of notes (concept + Q&A each).
2. Add taxonomy tags (`android/bubbles`, `android/maps-compose`, `android/release`) to track new work.
3. Extend `moc-android` with Communication Surfaces and Release Engineering sections.
4. Build a Dataview tracker monitoring draft → reviewed → ready for these focus areas.

---

## Follow-ups
- Какие конкретные ресурсы (документация, codelabs) использовать для каждого добавления?
- Нужен ли отдельный roadmap-файл с дедлайнами по закрытию пробелов?
- Как интегрировать проверки на пробелы в автоматизированные отчёты (`Link Health`, `Dataview`)?

## References
- [[moc-android]]
- [[c-dependency-injection]]
- [[q-koin-vs-dagger-philosophy--android--hard]]
