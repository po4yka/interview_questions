---
id: "20251110-151504"
title: "Dp Sp Units / Dp Sp Units"
aliases: ["Dp Sp Units"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Dp and sp are density-aware units used mainly in Android and Jetpack Compose UI to create screens that scale correctly across devices with different pixel densities and user font settings. `dp` (density-independent pixel) is used for layout dimensions and spacing so that physical size appears consistent, while `sp` (scale-independent pixel) is used for text size and respects the user’s font scale preferences. Choosing the correct unit is essential for responsive, accessible, and visually consistent interfaces.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Dp и sp — это единицы измерения, учитывающие плотность пикселей и используемые в основном в Android и Jetpack Compose для масштабируемых интерфейсов на устройствах с разным разрешением экрана. `dp` (density-independent pixel) применяют для размеров элементов и отступов, чтобы физический размер оставался визуально одинаковым, а `sp` (scale-independent pixel) используют для размеров текста с учетом пользовательских настроек масштаба шрифта. Правильный выбор единиц критичен для адаптивности, доступности и визуальной согласованности UI.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- `dp` abstracts from raw pixels: 1 dp is defined relative to a baseline density (160 dpi), so UI elements maintain consistent physical size on different screens.
- `sp` builds on `dp` but also scales with the user’s font size/accessibility settings, making it the correct choice for text and typographic elements.
- Use `dp` for layout metrics: widths, heights, padding, margins, corner radii, elevation, and icon sizes.
- Use `sp` for any user-visible text to ensure readability and accessibility; avoid using `dp` for text sizes.
- Mixing raw `px` with `dp`/`sp` can cause inconsistent layouts; prefer density-independent units for all UI where possible.

## Ключевые Моменты (RU)

- `dp` абстрагируется от физических пикселей: 1 dp определяется относительно базовой плотности (160 dpi), поэтому элементы сохраняют близкий физический размер на разных экранах.
- `sp` основан на `dp`, но дополнительно масштабируется в соответствии с пользовательскими настройками размера шрифта, поэтому используется для текста и типографики.
- Используйте `dp` для метрик разметки: ширина, высота, отступы, поля, радиусы скругления, тени/поднятие, размеры иконок.
- Используйте `sp` для всего пользовательского текста, чтобы обеспечить читаемость и поддержку настроек доступности; избегайте `dp` для размеров шрифта.
- Смешивание «чистых» `px` с `dp`/`sp` приводит к неконсистентным интерфейсам; по возможности используйте плотностно-независимые единицы.

## References

- Android Developers: "Support different pixel densities" (developer.android.com)
- Android Developers: "Material Design typographic scale" (material.io)
