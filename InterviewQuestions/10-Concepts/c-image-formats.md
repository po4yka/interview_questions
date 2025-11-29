---
id: "20251110-161337"
title: "Image Formats / Image Formats"
aliases: ["Image Formats"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-vector-graphics, c-drawable, c-android-resources]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Image formats define how pixel data, color information, metadata, and compression are encoded and stored in an image file. Understanding common formats (such as JPEG, PNG, GIF, WebP, SVG) is essential for choosing the right trade-off between quality, size, transparency support, and animation in web and mobile applications. In interviews, this concept often appears when discussing performance optimization, asset pipelines, multimedia handling, or cross-platform rendering.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Форматы изображений определяют способ кодирования и хранения пиксельных данных, цветовой информации, метаданных и сжатия в файловом представлении изображения. Понимание распространённых форматов (JPEG, PNG, GIF, WebP, SVG и др.) важно для выбора баланса между качеством, размером файла, поддержкой прозрачности и анимации в веб- и мобильных приложениях. На собеседованиях тема часто возникает при обсуждении оптимизации производительности, работы с медиа-ресурсами и кроссплатформенного рендеринга.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Lossy vs lossless: JPEG and WebP (lossy mode) use lossy compression for smaller files; PNG, GIF, and WebP (lossless mode) preserve exact pixel data at the cost of larger sizes.
- Transparency and alpha: PNG and WebP support full alpha channels; GIF supports 1-bit transparency; classic JPEG does not support transparency.
- Animation support: GIF, WebP, and some modern formats (e.g., APNG) can store animations; PNG and JPEG are traditionally static.
- Vector vs raster: SVG is a vector format (resolution-independent, ideal for icons/logos), while JPEG/PNG/GIF/WebP are raster formats defined by a fixed pixel grid.
- Performance and compatibility: JPEG/PNG/GIF are universally supported; modern formats like WebP/AVIF provide better compression but require checking platform and browser support.

## Ключевые Моменты (RU)

- Потерянное vs. без потерь: JPEG и WebP (в режиме lossy) используют сжатие с потерями ради меньшего размера; PNG, GIF и WebP (lossless) сохраняют точные пиксели ценой большего файла.
- Прозрачность и альфа-канал: PNG и WebP поддерживают полноценный альфа-канал; GIF поддерживает 1-битную прозрачность; классический JPEG не поддерживает прозрачность.
- Поддержка анимации: GIF, WebP и некоторые современные расширения (например, APNG) могут содержать анимации; PNG и JPEG традиционно статичны.
- Вектор vs. растр: SVG — векторный формат (масштабируется без потери качества, подходит для иконок и логотипов), тогда как JPEG/PNG/GIF/WebP — растровые форматы с фиксированной сеткой пикселей.
- Производительность и совместимость: JPEG/PNG/GIF поддерживаются практически везде; современные форматы (WebP, AVIF) дают лучшее сжатие, но требуют проверки поддержки платформ и браузеров.

## References

- PNG (Portable Network Graphics) Specification — https://www.w3.org/TR/PNG/
- JPEG (Joint Photographic Experts Group) overview — https://jpeg.org/jpeg/index.html
- WebP documentation — https://developers.google.com/speed/webp
- SVG (Scalable Vector Graphics) specification — https://www.w3.org/TR/SVG2/
