---\
id: "20251110-200847"
title: "Vector Graphics / Vector Graphics"
aliases: ["Vector Graphics"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-drawable", "c-image-formats", "c-android-graphics", "c-canvas-drawing", "c-custom-views"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

Vector graphics represent images using mathematical descriptions of geometric primitives (points, lines, curves, shapes) instead of fixed pixels. They scale infinitely without losing quality, making them ideal for icons, logos, diagrams, UI assets, and rendering in different resolutions and densities. In programming, vector graphics are manipulated via APIs (e.g., SVG, `Canvas` with paths, PDF, Android VectorDrawable) and rendered by rasterization at display time.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Векторная графика представляет изображения с помощью математических описаний геометрических примитивов (точки, линии, кривые, фигуры), а не фиксированного набора пикселей. Такие изображения масштабируются без потери качества, что делает их идеальными для иконок, логотипов, диаграмм, UI-ресурсов и отображения на разных разрешениях и плотностях экранов. В программировании векторная графика задаётся через API (например, SVG, `Canvas` с путями, PDF, Android VectorDrawable) и растеризуется при выводе на экран.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Resolution independence: Quality does not degrade when scaling; one asset can target multiple screen densities (useful for responsive UI and mobile apps).
- Representation: Uses paths, Bézier curves, strokes, fills, and transformations defined mathematically, which are compact and easy to manipulate programmatically.
- Rendering pipeline: Vector descriptions are eventually rasterized by the graphics engine into pixels at render time, which may be more CPU/GPU intensive for complex scenes.
- Typical formats/APIs: Commonly implemented via SVG, PDF vector content, PostScript, font outlines, and platform APIs like Android VectorDrawable, HTML5 `Canvas` paths, and graphics libraries (e.g., Skia, Core Graphics).
- Use vs raster: Preferred for icons, logos, text, and scalable UI; raster images remain better for detailed photos or textures.

## Ключевые Моменты (RU)

- Независимость от разрешения: Качество не ухудшается при масштабировании; один ресурс подходит для разных плотностей экранов (актуально для адаптивного UI и мобильных приложений).
- Представление: Используются пути, кривые Безье, обводки, заливки и трансформации, заданные математически; такие данные компактны и легко изменяются программно.
- Конвейер отрисовки: Векторное описание в итоге растеризуется графическим движком в пиксели при выводе, что может быть ресурсоёмко для сложных сцен.
- Типичные форматы/API: На практике реализуется через SVG, векторное содержимое PDF, PostScript, контуры шрифтов, а также платформенные API вроде Android VectorDrawable, HTML5 `Canvas` (пути) и графические библиотеки (например, Skia, Core Graphics).
- Выбор против растров: Предпочтительна для иконок, логотипов, текста и масштабируемых элементов UI; растровая графика лучше подходит для детализированных фотографий и текстур.

## References

- SVG Specification (W3C): https://www.w3.org/Graphics/SVG/
- Android VectorDrawable overview: https://developer.android.com/guide/topics/graphics/vector-drawable
- Skia Graphics Library: https://skia.org/
