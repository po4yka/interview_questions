---
id: 20251029-170210
title: Design Offline Maps & Navigation / Проектирование офлайн карт и навигации
aliases:
    [
        Design Offline Maps & Navigation,
        Проектирование офлайн карт и навигации,
        Offline Maps Architecture,
        Архитектура офлайн карт,
    ]
topic: android
subtopics: [location, files-media, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-design-uber-app--android--hard, c-lifecycle, c-workmanager]
sources: []
created: 2025-10-29
updated: 2025-10-29
tags:
    [
        android/location,
        android/files-media,
        android/service,
        difficulty/hard,
        platform/android,
        lang/kotlin,
        maps,
        navigation,
        offline,
    ]
date created: Wednesday, October 29th 2025, 5:02:58 pm
date modified: Thursday, October 30th 2025, 3:15:12 pm
---

# Вопрос (RU)

> Как спроектировать офлайн карты и пошаговую навигацию для Android?

# Question (EN)

> How to design offline maps & turn-by-turn navigation for Android?

---

### Upgraded Interview Prompt (RU)

Спроектируйте офлайн‑first карты и навигацию. Требования: работа без сети 24ч, обработка GPS drift, голосовые подсказки, батарея <2%/ч во время навигации. Включите хранение/эвикцию тайлов, вычисление маршрута (серверная помощь при онлайне), латентность reroute <1.5с, download manager для регионов, доступность (крупный текст, цветовой контраст), наблюдаемость.

### Upgraded Interview Prompt (EN)

Build offline‑first maps & navigation. Requirements: no network for 24h, GPS drift handling, voice guidance, and battery <2%/hr while navigating. Include tile storage/eviction, route computation (server‑assisted when online), reroute latency <1.5s, download manager for regions, accessibility (large text, color contrast), and observability.

## Ответ (RU)

Офлайн карты и навигация требуют векторных тайлов, локального графа маршрутизации, обработки GPS и голосовых подсказок.

### Архитектура

Модули: maps-core, tiles-store, nav-engine, voice, download-manager, location-core, analytics, flags.

### Тайлы и Хранилище

Векторные тайлы (protobuf); региональные пакеты с манифестом; LRU эвикция по редкости региона + размер; лимит 2–4GB. Дельта-обновления при онлайне.

### Локация

Fused provider где возможно; fallback на raw GNSS + sensor fusion. Семплинг 1 Гц при движении; 0.2 Гц при остановке. Kalman filter для сглаживания; snap к графу дорог.

### Маршрутизация

Локальный граф для основных дорог; серверная помощь при онлайне для трафика; reroute цель <1.5с через incremental Dijkstra/A\* на локальном графе. Голосовые подсказки планируются заранее по расстоянию; TTS через TextToSpeech или pre‑baked prompts.

### Батарея

Duty‑cycle GPS; significant‑motion для перехода на низкий семплинг; coalesce записи; foreground service с persistent notification.

### Загрузки

WorkManager; pause/resume; checksum verification; пользовательские настройки хранилища.

### Наблюдаемость

GPS accuracy hist, reroute latency, crash/ANR, battery/100км, tile cache hit%.

### Тестирование

Симулированные трейсы, туннель/no‑GNSS, переключение региона, смерть процесса mid‑route.

### Последовательность

MVP (базовые тайлы + локальная маршрутизация) → Голос → Reroute → Серверная помощь по трафику → Умные загрузки.

### Tradeoffs

Большие локальные графы снижают время reroute, но стоят хранилища; настраиваем по популярности региона и свободному месту на устройстве.

## Answer (EN)

Offline maps and navigation require vector tiles, local routing graph, GPS handling, and voice guidance.

### Architecture

maps-core, tiles-store, nav-engine, voice, download-manager, location-core, analytics, flags.

### Tiles & Storage

Vector tiles (protobuf); region packs with manifest; LRU eviction by region recency + size; cap e.g. 2–4GB. Delta updates when online.

### Location

Fused provider where possible; fallback to raw GNSS + sensor fusion. Sampling 1 Hz while moving; 0.2 Hz when stationary. Kalman filter for smoothing; snap to road graph.

### Routing

On‑device graph for primary roads; server‑assisted when online for traffic; reroute target <1.5s using incremental Dijkstra/A\* on local graph. Voice prompts scheduled ahead by distance; TTS via TextToSpeech or pre‑baked prompts.

### Battery

Duty‑cycle GPS; significant‑motion to drop to low sampling; coalesce writes; foreground service with persistent notification.

### Downloads

WorkManager; pause/resume; checksum verification; user controls for storage.

### Observability

GPS accuracy hist, reroute latency, crash/ANR, battery/100km, tile cache hit%.

### Testing

Simulated traces, tunnel/no‑GNSS, region switch, process‑death mid‑route.

### Sequencing

MVP (basic tiles + on‑device routing) → voice → reroute → server traffic assist → smart downloads.

### Tradeoffs

Larger local graphs reduce reroute time but cost storage; tune by region popularity and device free space.

---

## Follow-ups

-   How to handle GPS drift in tunnels and urban canyons?
-   What compression strategy minimizes tile storage while preserving quality?
-   How to optimize battery for continuous navigation?
-   How to handle map updates with active navigation sessions?

## References

-   [[c-lifecycle]]
-   [[c-workmanager]]
-   https://developer.android.com/training/location
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites (Easier)

-   [[q-design-uber-app--android--hard]]

### Related (Same Level)

-   [[q-design-uber-app--android--hard]]
-   [[q-data-sync-unstable-network--android--hard]]

### Advanced (Harder)

-   Design a global tile distribution system at Google Maps scale
