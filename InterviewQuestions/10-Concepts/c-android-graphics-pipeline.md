---\
id: "20251110-184526"
title: "Android Graphics Pipeline / Android Graphics Pipeline"
aliases: ["Android Graphics Pipeline"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-android-graphics", "c-choreographer", "c-android-frame-budget", "c-gpu-rendering", "c-android-surfaces"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [android, concept, difficulty/medium]
---\

# Summary (EN)

Android Graphics Pipeline is the sequence of stages Android uses to transform application drawing commands into pixels displayed on the screen. It covers how Views/Compose UI issue draw calls, how the system records them into display lists, how the GPU renders via OpenGL ES/Vulkan, and how frames are composed and presented by SurfaceFlinger. Understanding the pipeline is critical for diagnosing jank, optimizing rendering performance, and meeting the 16ms-per-frame (60fps) budget in modern Android apps.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Android Graphics Pipeline — это последовательность этапов, через которые Android преобразует команды отрисовки приложения в пиксели на экране. Она включает генерацию команд UI (Views/Compose), формирование display lists, рендеринг на GPU через OpenGL ES/Vulkan и композицию кадров системой SurfaceFlinger. Понимание этого конвейера критично для поиска причин лагов (jank), оптимизации производительности и укладывания в бюджет ~16 мс на кадр (60fps) в современных Android-приложениях.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- UI rendering path: `Application` code (Views or Jetpack Compose) runs on the main thread, measures/layouts views, and issues drawing operations to `Canvas` or the Compose rendering layer.
- Hardware acceleration: With hardware-accelerated rendering, Android records drawing operations into display lists and renders them via GPU backends (OpenGL ES or Vulkan) instead of CPU rasterization.
- Choreographer and vsync: The Choreographer coordinates frame callbacks with the display's vsync signal; the app must complete input handling, layout, and draw within a frame interval (e.g., ~16.67ms for 60Hz) to avoid jank.
- `Surface`, BufferQueue, SurfaceFlinger: UI is rendered into a `Surface` backed by buffers; BufferQueue passes these to SurfaceFlinger, which composes layers (app windows, system UI) into the final framebuffer.
- Performance implications: Overdraw, heavy overuse of alpha, complex layouts, or expensive work on the main thread can cause missed frames; profiling tools (Layout Inspector, GPU Profiler, Frame Timeline, Perfetto) help analyze pipeline bottlenecks.

## Ключевые Моменты (RU)

- Путь отрисовки UI: Код приложения (Views или Jetpack Compose) на главном потоке выполняет measure/layout, затем формирует операции рисования для `Canvas` или рендеринг-слоя Compose.
- Аппаратное ускорение: При включённом hardware acceleration Android записывает операции отрисовки в display lists и рендерит их через GPU (OpenGL ES или Vulkan), а не полностью на CPU.
- Choreographer и vsync: Choreographer синхронизирует callbacks кадра с сигналом vsync; обработка ввода, layout и draw должны уложиться в интервал кадра (≈16,67 мс при 60 Гц), чтобы избегать рывков (jank).
- `Surface`, BufferQueue, SurfaceFlinger: UI рендерится в `Surface`, связанный с буферами; BufferQueue передаёт буферы в SurfaceFlinger, который композитит слои (окна приложений, системный UI) в финальный framebuffer.
- Влияние на производительность: Overdraw, тяжёлые прозрачности, сложные иерархии layout'ов и дорогие операции на главном потоке приводят к пропуску кадров; инструменты профилирования (Layout Inspector, GPU Profiler, Frame Timeline, Perfetto) помогают находить узкие места конвейера.

## References

- Android Developers: "Hardware Acceleration" (developer.android.com)
- Android Developers: "Graphics Architecture" / "SurfaceFlinger" (source.android.com, developer.android.com)
- Android Developers: "Profile your layout" and "Inspect GPU rendering performance" (developer.android.com)
