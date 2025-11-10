---
id: android-625
title: Perfetto Frame Timeline Analysis / Анализ Frame Timeline в Perfetto
aliases:
- Perfetto Frame Timeline Analysis
- Анализ Frame Timeline в Perfetto
topic: android
subtopics:
- logging-tracing
- performance-rendering
- monitoring-slo
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-android-performance-measurement-tools--android--medium
created: 2025-10-02
updated: 2025-11-10
tags:
- android/logging-tracing
- android/performance-rendering
- android/monitoring-slo
- difficulty/hard
sources:
- "https://perfetto.dev/docs/concepts/frame-timeline"
- "https://developer.android.com/topic/performance/tracing/perfetto"

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
    name: "android.app_frame_timeline"
  }
}
data_sources: {
  config {
    name: "android.surfaceflinger.frame_timeline"
  }
}
data_sources: {
  config {
    name: "android.packages_list"
  }
}
duration_ms: 10000
EOF
adb pull /data/misc/perfetto-traces/app.perfetto-trace
```

- Обязательно включите источники Frame Timeline: `android.app_frame_timeline` и `android.surfaceflinger.frame_timeline` (названия могут отличаться в зависимости от версии, сверяйтесь с документацией Perfetto/Android).
- Добавьте `android.packages_list`, чтобы связывать фреймы с нужным пакетом.
- По необходимости добавляйте дополнительные источники (CPU scheduler, Binder, GPU), но помните, что они не заменяют frame timeline.
- Для Jetpack Compose и современных приложений опирайтесь на Frame Timeline; дополнительные источники (`traceEvents`, latency/CPU/GPU треки) используйте для детализации, а не вместо Frame Timeline.

### 2. Интерпретация Frame Timeline

- **AppFrame**: фрейм на стороне приложения (когда приложение завершило подготовку/отрисовку кадра).
- **DisplayFrame**: фрейм на стороне SurfaceFlinger/дисплея (когда кадр был представлен на дисплей).
- Jank определяется по тому, успевает ли AppFrame попасть в соответствующий DisplayFrame (deadline) и по полям `jank_type` / причинам jank в таблицах Frame Timeline.
- В Perfetto UI используется цветовая подсветка состояний фреймов (успешные, с задержкой, дропнутые и др.); воспринимайте зелёный/жёлтый/красный как концептуальное обозначение нормальных, пограничных и проблемных кадров, а за точной семантикой цветов и легендой обращайтесь к конкретной версии UI.
- Свяжите события Frame Timeline с `Choreographer#doFrame`, работой `RenderThread`, GPU queue и SurfaceFlinger, чтобы понять, на каком этапе возникает задержка.

### 3. Корреляция потоков

- Используйте `Slice`/`Tracks` view в Perfetto, чтобы находить `AppFrame`/`DisplayFrame` и соответствующие им срезы.
- Фильтруйте по `Choreographer#doFrame` и смежным событиям, сопоставляйте:
  - `Main Thread` → обработка input/measure/layout.
  - `RenderThread` → генерация команд для GPU.
  - GPU/композитор → фактическая отрисовка и композиция кадра.
- Анализируйте `Binder` вызовы (например, к SurfaceFlinger) и взаимодействие с `ViewRootImpl` для понимания задержек между приложением и системным compositor.

### 4. Автоматизация

- Используйте `trace_processor_shell` для извлечения метрик:

```bash
trace_processor_shell app.perfetto-trace <<'SQL'
SELECT ts, dur, jank_type
FROM frame_timeline_slice
WHERE jank_type != 0;
SQL
```

- Таблица `frame_timeline_slice` (или её аналог в вашей версии) содержит информацию по App/Display фреймам, длительности и типам jank.
- Встроенные метрики Perfetto (например, `android_frame_timeline` в trace processor metrics) позволяют получать агрегаты: количество дропнутых кадров, долю janky-фреймов, FPS и т.п. Уточняйте точные имена метрик по актуальной версии Perfetto.
- В CI:
  - фиксируйте baseline по ключевым метрикам (например, доля janky-фреймов, p95/p99 времени подготовки фрейма);
  - сравнивайте с порогами (thresholds) и фейлите сборку или отправляйте отчёты при регрессии;
  - интегрируйте с Macrobenchmark/Benchmark для автоматического снятия трасс.

### 5. Практические советы

- Снимайте трассы максимально близко к релизному окружению (release build / minified / без лишней отладочной инструментализации), чтобы не искажать тайминги.
- Совмещайте Perfetto с `Macrobenchmark` (`FrameTimingMetric` / FrameTimelineMetric) для автоматизированных тестов производительности.
- Анализируйте GPU и память (соответствующие data sources Perfetto) как дополнительный контекст при поиске причин jank.

---

## Answer (EN)

### 1. Trace capture

- Capture a Perfetto trace including frame timeline data sources, e.g. `android.app_frame_timeline` and `android.surfaceflinger.frame_timeline`, plus `android.packages_list` and, if needed, CPU/Binder/GPU sources.
- Use an `adb shell perfetto` command similar to the RU example, then `adb pull` and open the trace in the Perfetto UI.

### 2. Frame timeline interpretation

- AppFrame: when the app finishes producing a frame.
- DisplayFrame: when SurfaceFlinger/compositor presents a frame to the display.
- Jank is detected by checking whether AppFrames make their deadlines for the corresponding DisplayFrames and by inspecting `jank_type` / jank reasons in frame timeline tables.
- Treat green/yellow/red as a conceptual shorthand for good/borderline/bad frames; rely on the actual Perfetto UI legend for the precise color semantics in your version.
- Correlate AppFrame/DisplayFrame slices with `Choreographer#doFrame`, RenderThread, GPU/compositor tracks to locate where time is spent.

### 3. Thread correlation

- In Perfetto, use Slice/Tracks views to:
  - Filter for `Choreographer#doFrame` and frame-related slices.
  - Map Main thread → RenderThread → GPU/compositor work.
  - Inspect Binder calls to SurfaceFlinger/ViewRootImpl to see where delays occur between the app and system compositor.

### 4. Automation

- Use `trace_processor_shell` to query frame timeline data, for example:

```bash
trace_processor_shell app.perfetto-trace <<'SQL'
SELECT ts, dur, jank_type
FROM frame_timeline_slice
WHERE jank_type != 0;
SQL
```

- Use Perfetto's built-in metrics (e.g. `android_frame_timeline` metric proto, depending on your version) to compute aggregates such as dropped/janky frame counts and FPS; always confirm exact metric names against the current Perfetto docs.
- Integrate this into CI:
  - collect traces via Macrobenchmark or scripted runs;
  - compute frame-timeline-based metrics;
  - compare against stored baselines/thresholds and fail or report on regression.

### 5. Practical tips

- Capture traces on builds close to production (release-like, minimal extra instrumentation).
- Combine Perfetto with Macrobenchmark FrameTiming/FrameTimeline metrics to detect regressions.
- Use GPU and memory tracks as supporting context for diagnosing jank rather than as primary frame correctness signals.

---

## Дополнительные вопросы (RU)
- Как интерпретировать prediction error и present latency?
- Как комбинировать Perfetto и Systrace для старых устройств?
- Какие thresholds для dropped frames использовать в SLA?

## Follow-ups
- How to interpret prediction error and present latency?
- How to combine Perfetto and Systrace for legacy devices?
- What thresholds for dropped frames should be used in SLAs?

## Ссылки (RU)
- https://perfetto.dev/docs/concepts/frame-timeline
- https://developer.android.com/topic/performance/tracing/perfetto

## References
- https://perfetto.dev/docs/concepts/frame-timeline
- https://developer.android.com/topic/performance/tracing/perfetto

## Related Questions

- [[q-android-performance-measurement-tools--android--medium]]
