---\
id: "20251110-133119"
title: "Itemdecoration / Itemdecoration"
aliases: ["Itemdecoration"]
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
related: ["c-recyclerview", "c-viewholder", "c-custom-views", "c-canvas-drawing"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

ItemDecoration in Android's `RecyclerView` is an extension mechanism that allows developers to draw custom visual elements (such as dividers, margins, backgrounds, or section headers) around or behind individual list/grid items without modifying the item view layout itself. It centralizes decoration logic, keeps adapters and view holders clean, and enables consistent, reusable styling across multiple RecyclerViews.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

ItemDecoration в `RecyclerView` (Android) — это расширяемый механизм, позволяющий рисовать пользовательские декоративные элементы (например, разделители, отступы, фоны, секционные заголовки) вокруг или под элементами списка/сетки без изменения разметки самих item-view. Он выносит логику оформления в отдельный слой, упрощая адаптеры и обеспечивая единообразный, переиспользуемый стиль для нескольких `RecyclerView`.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Separation of concerns: Decoration (dividers, spacing, background) is handled outside adapter/view holder logic by subclassing `RecyclerView.ItemDecoration`.
- Flexible drawing: `Provides` `onDraw` and `onDrawOver` callbacks to draw below or above item views using the `Canvas` API.
- Layout offsets: `getItemOffsets` lets you add spacing/padding around items without changing item layouts, ideal for grids and complex lists.
- Reusability: One ItemDecoration implementation can be attached to multiple RecyclerViews to enforce consistent UI behavior.
- Non-interfering behavior: Decorations do not affect item click handling or data binding, focusing purely on visual presentation.

## Ключевые Моменты (RU)

- Разделение ответственности: Декор (разделители, отступы, фон) выносится из адаптера и `ViewHolder` в отдельный класс, наследующий `RecyclerView.ItemDecoration`.
- Гибкая отрисовка: Методы `onDraw` и `onDrawOver` позволяют рисовать под или поверх item-view, используя `Canvas`.
- Управление отступами: `getItemOffsets` добавляет пространство вокруг элементов без изменения их разметки — удобно для сеток и сложных списков.
- Переиспользуемость: Один ItemDecoration можно подключать к разным `RecyclerView` для единообразного оформления.
- Отсутствие влияния на логику: Декорации не вмешиваются в обработку кликов и биндинг данных, отвечая только за визуальную часть.

## References

- Android Developers: `RecyclerView`.ItemDecoration (developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.ItemDecoration)
