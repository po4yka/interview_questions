---
id: ivc-20251102-012
title: Perfetto & Frame Timeline / Perfetto и Frame Timeline
aliases:
  - Perfetto
  - Frame Timeline
  - Android Performance Tracing
kind: concept
summary: Perfetto-based tracing framework and frame timeline metrics for jank analysis on Android
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - performance
  - perfetto
  - tracing
---

# Summary (EN)

**Perfetto** is Android's system tracing platform capturing CPU, GPU, input, and app events. Frame timeline metrics align choreographer, render thread, and GPU completion to measure jank precisely.

# Сводка (RU)

**Perfetto** — системная платформа трассировки Android, собирающая события CPU, GPU, ввода и приложений. Frame Timeline синхронизирует Choreographer, RenderThread и GPU, позволяя точно анализировать лаги.

## Key Components

- Trace configs (`perfetto -c config.pbtxt -o trace.perfetto-trace`)
- Android Studio profiler integration
- Frame timeline tracks (DisplayFrame, AppFrame)
- `FrameTimelineMetric` в Perfetto UI

## Considerations

- Требует `WRITE_APN_SETTINGS`? (нет) — запускается через `adb shell perfetto`.
- Большие трассы → используйте ring buffer.
- Для CI можно применять `perfetto_cmd` и `trace_processor` для метрик.

