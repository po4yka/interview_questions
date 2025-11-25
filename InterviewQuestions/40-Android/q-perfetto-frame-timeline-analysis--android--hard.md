---
id: android-625
title: Perfetto Frame Timeline Analysis / Анализ Frame Timeline в Perfetto
aliases: [Perfetto Frame Timeline Analysis, Анализ Frame Timeline в Perfetto]
topic: android
subtopics:
  - logging-tracing
  - monitoring-slo
  - performance-rendering
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-profiling
  - q-android-performance-measurement-tools--android--medium
  - q-frame-time-120ms-meaning--android--easy
  - q-jank-detection-frame-metrics--android--medium
  - q-leakcanary-heap-dump-analysis--android--medium
created: 2025-10-02
updated: 2025-11-10
tags: [android/logging-tracing, android/monitoring-slo, android/performance-rendering, difficulty/hard]
sources:
  - "https://developer.android.com/topic/performance/tracing/perfetto"
  - "https://perfetto.dev/docs/concepts/frame-timeline"

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)
> Как использовать Perfetto и Frame Timeline для анализа лагов: настройка трассировки, интерпретация DisplayFrame/AppFrame, корреляция с потоками и автоматизация метрик?

# Question (EN)
> How do you leverage Perfetto and the frame timeline to analyze jank, configure tracing, interpret DisplayFrame/AppFrame data, correlate threads, and automate metrics?

---

## Ответ (RU)

### 1. Сбор Трассы

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

- Обязательно включите источники Frame Timeline: `android.app_frame_timeline` и `android.surfaceflinger.frame_timeline` (конкретные названия и доступность зависят от версии Android/Perfetto; сверяйтесь с документацией и `perfetto --query`).
- Добавьте `android.packages_list`, чтобы связывать фреймы с нужным пакетом.
- По необходимости добавляйте дополнительные источники (CPU scheduler, Binder, GPU), но помните, что они дополняют Frame Timeline, а не заменяют её.
- Для Jetpack Compose и современных приложений опирайтесь на Frame Timeline как на основной источник правды о кадрах; дополнительные источники (`traceEvents`, latency/CPU/GPU треки) используйте для детализации.

### 2. Интерпретация Frame Timeline

- **AppFrame**: фрейм на стороне приложения — момент, когда приложение завершило подготовку кадра (рендеринг на `RenderThread` / запись в Surface) и передало результат системе.
- **DisplayFrame**: фрейм на стороне SurfaceFlinger/дисплея — момент, когда системный композитор выбрал и показал кадр на экране.
- Jank определяется по тому, успевает ли AppFrame попасть в соответствующий DisplayFrame (до дедлайна VSync) и по полям `jank_type` / причинам jank в таблицах Frame Timeline.
- В Perfetto UI используется цветовая подсветка состояний фреймов (успешные, с задержкой, дропнутые и др.); воспринимайте зелёный/жёлтый/красный как концептуальное обозначение нормальных, пограничных и проблемных кадров, а за точной семантикой цветов и легендой обращайтесь к конкретной версии UI.
- Свяжите события Frame Timeline с `Choreographer#doFrame`, работой `RenderThread`, GPU queue и SurfaceFlinger, используя идентификаторы App/Display фреймов, чтобы точно понять, на каком этапе возникает задержка.

### 3. Корреляция Потоков

- Используйте `Slice`/`Tracks` view и специализированные Frame Timeline треки в Perfetto, чтобы находить `AppFrame`/`DisplayFrame` и соответствующие им срезы.
- Фильтруйте по `Choreographer#doFrame` и смежным событиям, сопоставляйте:
  - `Main Thread` → обработка input/measure/layout.
  - `RenderThread` → генерация команд для GPU.
  - GPU/композитор → фактическая отрисовка и композиция кадра.
- Анализируйте `Binder` вызовы (например, к SurfaceFlinger) и взаимодействие с `ViewRootImpl` для понимания задержек между приложением и системным compositor.

### 4. Автоматизация

- Используйте `trace_processor_shell` для изучения доступных таблиц и извлечения метрик. Обратите внимание, что структура таблиц зависит от версии Perfetto/Android; используйте `.tables` и `.schema` для проверки.

```bash
trace_processor_shell app.perfetto-trace <<'SQL'
SELECT ts, dur, jank_type
FROM frame_timeline_slice -- используйте актуальное имя таблицы/представления для вашей версии
WHERE jank_type != 0;
SQL
```

- Таблицы, связанные с Frame Timeline (например, `frame_timeline`, `actual_frame_timeline` или их аналоги в вашей версии), содержат информацию по App/Display фреймам, длительности и типам jank. Уточняйте точные имена по актуальной схеме trace processor.
- Встроенные метрики Perfetto (например, метрики на основе Frame Timeline в trace processor metrics) позволяют получать агрегаты: количество дропнутых кадров, долю janky-фреймов, FPS и т.п. Уточняйте точные имена метрик по актуальной версии Perfetto.
- В CI:
  - фиксируйте baseline по ключевым метрикам (например, доля janky-фреймов, p95/p99 времени подготовки фрейма);
  - сравнивайте с порогами (thresholds) и фейлите сборку или отправляйте отчёты при регрессии;
  - интегрируйте с Macrobenchmark/Benchmark для автоматического снятия трасс.

### 5. Практические Советы

- Снимайте трассы максимально близко к релизному окружению (release build / minified / без лишней отладочной инструментализации), чтобы не искажать тайминги.
- Совмещайте Perfetto с `Macrobenchmark` (`FrameTimingMetric` / FrameTimelineMetric) для автоматизированных тестов производительности.
- Анализируйте GPU и память (соответствующие data sources Perfetto) как дополнительный контекст при поиске причин jank.

См. также: [[c-android-profiling]]

---

## Answer (EN)

### 1. Trace Capture

- Capture a Perfetto trace including frame timeline data sources, e.g. `android.app_frame_timeline` and `android.surfaceflinger.frame_timeline`, plus `android.packages_list` and, if needed, CPU/Binder/GPU sources (exact names and availability depend on your Android/Perfetto version; confirm via docs and `perfetto --query`).
- Use an `adb shell perfetto` command similar to the RU example, then `adb pull` and open the trace in the Perfetto UI.

### 2. Frame Timeline Interpretation

- AppFrame: the application-side frame — when the app has finished producing the frame (RenderThread/GPU command submission / writing into its Surface) and hands it off to the system.
- DisplayFrame: the system compositor/SurfaceFlinger-side frame — when the compositor selects and presents a frame on screen.
- Jank is detected by checking whether AppFrames meet the deadlines for their corresponding DisplayFrames (vsync deadline) and by inspecting `jank_type` / jank reasons in frame timeline tables.
- Treat green/yellow/red in the Perfetto UI as conceptual shorthand for good/borderline/bad frames; rely on the legend of your Perfetto UI version for exact semantics.
- Correlate AppFrame/DisplayFrame slices with `Choreographer#doFrame`, RenderThread, GPU/compositor tracks and frame ids/tokens to locate where time is spent and where delays appear.

### 3. Thread Correlation

- In Perfetto, use the Slice/Tracks views and dedicated Frame Timeline tracks to:
  - Filter for `Choreographer#doFrame` and frame-related slices.
  - Map Main thread → RenderThread → GPU/compositor work.
  - Inspect Binder calls to SurfaceFlinger/ViewRootImpl to see where delays occur between the app and the system compositor.

### 4. Automation

- Use `trace_processor_shell` to inspect available tables and query frame timeline-related data. Note that exact table names depend on the Perfetto/Android version; use `.tables` and `.schema` for discovery.

```bash
trace_processor_shell app.perfetto-trace <<'SQL'
SELECT ts, dur, jank_type
FROM frame_timeline_slice -- replace with the actual frame timeline table/view name for your version
WHERE jank_type != 0;
SQL
```

- Use Perfetto's built-in metrics (for example, frame-timeline-based metrics like `android_frame_timeline` or version-specific equivalents) to compute aggregates such as dropped/janky frame counts and FPS; always confirm exact metric names against the current Perfetto docs and `trace_processor_shell --run-metrics` output.
- Integrate this into CI:
  - collect traces via Macrobenchmark or scripted runs;
  - compute frame-timeline-based metrics;
  - compare against stored baselines/thresholds and fail or report on regression.

### 5. Practical Tips

- Capture traces on builds close to production (release-like, minimal extra instrumentation).
- Combine Perfetto with Macrobenchmark FrameTiming/FrameTimeline metrics to detect regressions.
- Use GPU and memory tracks as supporting context for diagnosing jank rather than as primary frame correctness signals.

See also: [[c-android-profiling]]

---

## Дополнительные Вопросы (RU)
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