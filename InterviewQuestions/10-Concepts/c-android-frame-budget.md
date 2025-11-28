---
id: "20251110-173048"
title: "Android Frame Budget / Android Frame Budget"
aliases: ["Android Frame Budget"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: [c-choreographer, c-android-graphics-pipeline, c-performance-optimization, c-android-profiling, c-gpu-rendering]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:43 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Android Frame Budget is the fixed time window (typically 16.67 ms at 60 Hz, 8.33 ms at 120 Hz, etc.) in which the system must measure input, run app logic, perform layout and draw, and submit a frame to the display. Staying within this budget ensures smooth animations and scrolling; exceeding it leads to jank, dropped frames, and poor UX. Understanding and optimizing against the frame budget is critical when building performant Android UIs, especially for animation-heavy screens.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Android Frame Budget — это фиксированное временное окно (обычно 16,67 мс при 60 Гц, 8,33 мс при 120 Гц и т.п.), в которое система должна уложиться, чтобы обработать ввод, выполнить логику приложения, разметку, отрисовку и отправить кадр на дисплей. Соблюдение этого бюджета обеспечивает плавные анимации и прокрутку; превышение приводит к фризам, пропущенным кадрам и ухудшению UX. Понимание и оптимизация под frame budget критичны при разработке производительных UI в Android, особенно для экранов с интенсивной анимацией.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Fixed per refresh rate: The frame budget is determined by the device refresh rate (e.g., 60/90/120 Hz), defining how many milliseconds your entire frame pipeline has.
- End-to-end pipeline: Input handling, measure/layout, drawing (View or Compose), GPU work, and SurfaceFlinger composition must all complete within this window.
- Jank and dropped frames: If the app or GPU misses the deadline, the previous frame is shown again, causing visible stutter (jank).
- Performance focus: Heavy work on the main thread, excessive overdraw, complex layouts, or inefficient Compose recompositions frequently cause frame budget violations.
- Tooling: Use tools like Android Studio Profiler, Layout Inspector, Perfetto, and Macrobenchmark to detect slow frames and optimize rendering.

## Ключевые Моменты (RU)

- Зависимость от частоты обновления: Frame budget определяется частотой обновления экрана (60/90/120 Гц и др.), задавая количество миллисекунд на полный цикл отрисовки кадра.
- Конвейер от ввода до дисплея: Обработка ввода, measure/layout, рисование (View или Compose), работа GPU и композиция SurfaceFlinger должны уложиться в этот интервал.
- Джанк и пропуски кадров: При превышении дедлайна показывается старый кадр, что визуально проявляется как подёргивания и рывки интерфейса (jank).
- Фокус на производительности: Тяжёлые операции на main thread, избыточная вложенность и перерисовка layout, неэффективные recomposition в Compose часто приводят к выходу за frame budget.
- Инструменты анализа: Для поиска и устранения проблем используйте Android Studio Profiler, Layout Inspector, Perfetto и Macrobenchmark.

## References

- Android Developers: Performance Profiling and Optimizing Rendering
- Android Developers: JankStats and UI jank detection
