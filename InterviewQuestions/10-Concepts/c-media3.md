---
id: ivc-20251102-002
title: Media3 / Media3
aliases:
  - Media3
  - Android Media3
kind: concept
summary: Unified Jetpack media stack replacing ExoPlayer and legacy media components
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - media
  - exoplayer
  - media3
date created: Sunday, November 2nd 2025, 12:05:00 pm
date modified: Sunday, November 2nd 2025, 12:05:00 pm
---

# Summary (EN)

**Media3** is the evolution of ExoPlayer and Jetpack media APIs, offering a unified set of components for playback, editing, casting, and session management. It modularizes player UI, playback engine, session orchestration, and integrates tightly with Jetpack lifecycle, Compose, and Android Auto/TV surfaces.

**Key Modules**
- `media3-exoplayer`: core playback engine with audio/video renderers
- `media3-ui`: standard player UI components
- `media3-session`: integration with `MediaBrowser`/`MediaController`
- `media3-cast`: Cast support
- `media3-transformer`: media editing and transcoding

# Сводка (RU)

**Media3** — эволюция ExoPlayer и Jetpack media API, объединяющая воспроизведение, редактирование, кастинг и управление сессиями. Платформа модульна, лучше интегрирована с lifecycle/Compose и предназначена для повторного использования в Android Auto, TV и Wear.

**Основные модули**
- `media3-exoplayer`: движок воспроизведения
- `media3-ui`: стандартные UI-компоненты плеера
- `media3-session`: контроллеры, Browsers, интеграция с медиасервисами
- `media3-cast`: поддержка Google Cast
- `media3-transformer`: монтаж, обрезка, транскодирование

## Migration Considerations

- API surface больше не использует `SimpleExoPlayer`; нужно создавать `ExoPlayer.Builder`.
- Media3 поощряет использование `Player.Listener` вместо старых `EventListener`.
- `MediaLibraryService` и `MediaSessionService` облегчены, совместимы с Auto/TV.
- Compose integration через `AndroidView` или специализированные компоненты.

## Trade-offs

- Требует миграции namespace и зависимостей.
- Принуждает к четкой архитектуре сервиса (foreground service + session).
- Дает поддержку новых форматов, DRM, playback qos instrumentation.

