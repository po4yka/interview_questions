---
id: "20251110-200721"
title: "Android Graphics / Android Graphics"
aliases: ["Android Graphics"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Android Graphics is the Android framework stack responsible for rendering UI and visual content onto the device screen, combining high-level view rendering with low-level drawing APIs and hardware acceleration. It covers components like Canvas, Paint, Drawable, Bitmap, shaders, and the rendering pipeline built on top of Skia, OpenGL ES, and Vulkan. Understanding Android Graphics is essential for building custom views, efficient animations, image processing, and smooth, performant user interfaces.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Android Graphics — это стек фреймворка Android, отвечающий за отрисовку UI и визуального контента на экране устройства, объединяющий высокоуровневый рендеринг View с низкоуровневыми API рисования и аппаратным ускорением. Он включает компоненты Canvas, Paint, Drawable, Bitmap, шейдеры и пайплайн отрисовки на базе Skia, OpenGL ES и Vulkan. Понимание Android Graphics важно для создания кастомных View, эффективных анимаций, обработки изображений и плавных, производительных интерфейсов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Rendering pipeline: Android uses a multi-stage pipeline (measure/layout/draw) for Views, backed by Skia and hardware-accelerated compositing (GPU, SurfaceFlinger) to draw pixels efficiently.
- Canvas and Paint: Canvas provides the 2D drawing surface (shapes, text, bitmaps), while Paint defines style (color, stroke, shader, anti-aliasing); together they are core to custom drawing.
- Bitmaps and Drawables: Bitmaps hold pixel data; Drawables are an abstraction used by Views and resources (e.g., vector, shape, bitmap, StateList) to render scalable and themeable graphics.
- Hardware acceleration: By default, most UI rendering is GPU-accelerated, improving performance but imposing constraints (e.g., some unsupported operations, increased memory usage) that developers must consider.
- Performance considerations: Efficient invalidation (invalidate()/postInvalidate()), clipping, caching (e.g., Bitmap/Layer), and avoiding overdraw and unnecessary allocations are critical for smooth 60+ FPS rendering.

## Ключевые Моменты (RU)

- Конвейер отрисовки: Android использует многоэтапный пайплайн (measure/layout/draw) для View, опирающийся на Skia и GPU-акселерацию (SurfaceFlinger) для эффективного вывода пикселей.
- Canvas и Paint: Canvas предоставляет 2D-поверхность для рисования (фигуры, текст, битмапы), а Paint задаёт стиль (цвет, обводка, шейдер, сглаживание); вместе составляют основу кастомной отрисовки.
- Bitmap и Drawable: Bitmap хранит пиксельные данные; Drawable — абстракция для рендеринга ресурсов (vector, shape, bitmap, StateList и др.), обеспечивающая масштабируемость и поддержку тем.
- Аппаратное ускорение: По умолчанию рендеринг UI выполняется с использованием GPU, что повышает производительность, но накладывает ограничения (часть операций не поддерживается, рост потребления памяти), которые нужно учитывать.
- Производительность: Грамотное использование invalidation (invalidate()/postInvalidate()), клиппинга, кеширования (Bitmap/Layer), а также снижение overdraw и лишних аллокаций критично для стабильных 60+ FPS.

## References

- Android Developers: Graphics Overview — https://developer.android.com/guide/topics/graphics/overview
- Android Developers: Canvas and Drawables — https://developer.android.com/guide/topics/graphics
- Android Developers: Hardware Acceleration — https://developer.android.com/guide/topics/graphics/hardware-accel

