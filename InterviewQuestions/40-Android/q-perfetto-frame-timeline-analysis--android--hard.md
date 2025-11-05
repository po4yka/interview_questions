---
id: android-625
title: Perfetto Frame Timeline Analysis / Анализ Frame Timeline в Perfetto
aliases:
  - Perfetto Frame Timeline Analysis
  - Анализ Frame Timeline в Perfetto
topic: android
subtopics:
  - performance
  - perfetto
  - tracing
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-perfetto
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/performance
  - android/perfetto
  - tracing
  - difficulty/hard
sources:
  - url: https://perfetto.dev/docs/concepts/frame-timeline
    note: Frame timeline documentation
  - url: https://developer.android.com/topic/performance/tracing/perfetto
    note: Perfetto guide
---

# Вопрос (RU)
> Как использовать Perfetto и Frame Timeline для анализа лагов: настройка трассировки, интерпретация DisplayFrame/AppFrame, корреляция с потоками и автоматизация метрик?

# Question (EN)
> How do you leverage Perfetto and the frame timeline to analyze jank, configure tracing, interpret DisplayFrame/AppFrame data, correlate threads, and automate metrics?

---

## Ответ (RU)

### 1. Сбор трассы

```bash
adb shell perfetto -o /data/misc/perfetto-traces/app.perfetto-trace -c - <<'EOF'
buffers: {
  size_kb: 10240
  fill_policy: RING_BUFFER
}
data_sources: {
  config {
    name: "android.surfaceflinger.frame"
  }
}
data_sources: {
  config {
    name: "android.gpu.memory"
  }
}
data_sources: {
  config {
    name: "android.java_hprof"
  }
}
duration_ms: 10000
EOF
adb pull /data/misc/perfetto-traces/app.perfetto-trace
```

- Включите `android.surfaceflinger.frame`, `android.gpu`, `android.packages.list`.
- Для Compose добавьте `android.latency` + `traceEvents`.

### 2. Интерпретация Frame Timeline

- **DisplayFrame**: когда кадр попал на дисплей.
- **AppFrame**: когда приложение завершило отрисовку.
- Цветовая кодировка: зелёный (успех), жёлтый (jank, deadline miss), красный (dropped).
- Свяжите с `Choreographer#doFrame`, RenderThread, GPU queue.

### 3. Корреляция потоков

- Используйте `Slice` view, фильтруйте по `Choreographer#doFrame`.
- Сопоставьте `Main Thread` → `RenderThread` → `GPU completion`.
- Просматривайте `Binder` вызовы (SurfaceFlinger, ViewRootImpl).

### 4. Автоматизация

- `trace_processor_shell`:

```bash
trace_processor_shell trace.perfetto-trace <<'SQL'
SELECT ts, dur, jank_type FROM frame_timeline_slice WHERE jank_type != 0;
SQL
```

- Метрика `android.frame_timeline` выдаёт FPS, missed frames, prediction accuracy.
- В CI храните базовые значения, сравнивайте с threshold, отправляйте отчёты.

### 5. Практические советы

- Собирайте трассы на релизном билде (debounce instrumentation).
- Совмещайте с `macrobenchmark` (`FrameTimingMetric`) для автоматизированных тестов.
- Анализируйте GPU memory peaks (`gpu.memory`).

---

## Answer (EN)

- Capture traces with Perfetto enabling SurfaceFlinger frame data and relevant schedulers; pull the trace and open in Perfetto UI.
- Inspect frame timeline slices to determine where frames miss deadlines; correlate with main/render/GPU threads.
- Use `trace_processor` to extract jank metrics programmatically and integrate with CI (FrameTimelineMetric).
- Combine with Macrobenchmark frame timing to catch regressions and monitor GPU/memory tracks for supporting evidence.

---

## Follow-ups
- Как интерпретировать prediction error и present latency?
- Как комбинировать Perfetto и Systrace для старых устройств?
- Какие thresholds для dropped frames использовать в SLA?

## References
- [[c-perfetto]]
- [[q-android-coverage-gaps--android--hard]]
- https://perfetto.dev/docs/concepts/frame-timeline
- https://developer.android.com/topic/performance/tracing/perfetto

## Related Questions

- [[c-perfetto]]
- [[q-android-coverage-gaps--android--hard]]
