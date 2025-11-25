---
id: "20251110-200828"
title: "Drawable / Drawable"
aliases: ["Drawable"]
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

In UI frameworks like Android, a Drawable is an abstraction for something that can be drawn on the screen, such as bitmaps, shapes, vectors, or state-based graphics. It encapsulates the drawing instructions and visual properties (colors, borders, gradients, etc.) independent of the underlying View, enabling reusable, declarative, and theme-aware graphics. Drawables are commonly used for icons, backgrounds, selectors, and custom UI elements.

*This concept file was auto-generated and has been enriched with technical context for interview preparation.*

# Краткое Описание (RU)

В UI-фреймворках (например, Android) Drawable — это абстракция для любого объекта, который можно отрисовать на экране: битмапы, фигуры, векторные изображения или графика в зависимости от состояния. Он инкапсулирует инструкции отрисовки и визуальные свойства (цвета, границы, градиенты и т.п.) независимо от View, что позволяет переиспользовать, декларировать и темизировать графику. Часто используется для иконок, фонов, селекторов и кастомных элементов интерфейса.

*Этот файл концепции был создан автоматически и дополнен техническим контекстом для подготовки к собеседованиям.*

## Key Points (EN)

- Abstraction layer: Drawable defines how to render visual content (via its draw method) without tying it to a specific widget or layout.
- Multiple types: Includes bitmap drawables, shape drawables, vector drawables, layer lists, selectors (state-list drawables), and more.
- Resource-based: Typically defined as XML or image resources, enabling easy reuse, theming, and configuration for different densities and states.
- State-aware UI: Selectors and stateful drawables change appearance based on view states (pressed, focused, disabled), centralizing UI behavior.
- Customization: Developers can subclass Drawable or use XML-defined shapes/vectors to create lightweight, highly customizable graphics without extra image assets.

## Ключевые Моменты (RU)

- Слой абстракции: Drawable определяет, как отрисовать визуальное содержимое (через метод draw), не привязываясь к конкретному виджету или разметке.
- Разные типы: Включает bitmap-drawable, shape-drawable, vector-drawable, layer-list, selector (state-list drawable) и другие варианты.
- Ресурсно-ориентированный подход: Обычно задаётся как XML или графический ресурс, что упрощает переиспользование, темизацию и поддержку разных плотностей экранов.
- Зависимость от состояния: Селекторы и stateful-drawable меняют внешний вид в зависимости от состояний View (нажат, выбран, отключён), концентрируя логику UI в ресурсах.
- Кастомизация: Разработчик может наследоваться от Drawable или использовать XML-описания фигур/векторов для лёгких и гибко настраиваемых графических элементов без лишних изображений.

## References

- Android Developers: "Drawable" API guide and reference (developer.android.com)

