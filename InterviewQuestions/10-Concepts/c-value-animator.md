---\
id: "20251110-175129"
title: "Value Animator / Value Animator"
aliases: ["Value Animator"]
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
related: ["c-animation", "c-animation-framework", "c-interpolator", "c-custom-views", "c-android-graphics"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

ValueAnimator is an Android animation utility class that calculates animated values over time and delivers them via callbacks, without directly knowing how those values are rendered. It is used to interpolate between start and end values (numbers, colors, etc.) based on a specified duration and interpolator, enabling smooth, time-based UI animations and transitions. Unlike ViewPropertyAnimator or ObjectAnimator, ValueAnimator focuses solely on value computation, giving developers full control over how those values are applied.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

ValueAnimator — это вспомогательный класс анимации в Android, который вычисляет анимируемые значения во времени и передаёт их через колбэки, не зная напрямую, как эти значения будут отрисованы. Он интерполирует между начальными и конечными значениями (числа, цвета и т.п.) за заданную длительность с использованием интерполятора, обеспечивая плавные анимации и переходы в UI. В отличие от ViewPropertyAnimator или ObjectAnimator, ValueAnimator отвечает только за расчёт значений, предоставляя разработчику полный контроль над их применением.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Core behavior: `Provides` a timing engine that runs over a set duration and repeatedly calls `onAnimationUpdate` with the current animated value.
- Value types: Supports primitive types (int, float), ARGB colors, and custom types via `TypeEvaluator`, making it flexible for various animation scenarios.
- Separation of concerns: Does not modify views directly; you manually apply computed values (e.g., translation, alpha, height) inside the update listener.
- Control options: Allows configuration of duration, start delay, repeat count/mode, interpolators, and play states (start, pause, resume, cancel).
- Use cases: Ideal when animating non-standard properties (layout params, custom views, drawing properties, numbers in counters) that are not directly supported by property animators.

## Ключевые Моменты (RU)

- Основное поведение: Предоставляет тайминг-движок, который за заданную длительность вызывает `onAnimationUpdate` с текущим анимированным значением.
- Типы значений: Поддерживает примитивные типы (int, float), ARGB-цвета и пользовательские типы через `TypeEvaluator`, что делает его гибким для разных сценариев.
- Разделение обязанностей: Не изменяет `View` напрямую; вы сами применяете вычисленные значения (например, translation, alpha, высота) внутри слушателя обновления.
- Управление анимацией: Позволяет настраивать длительность, стартовую задержку, количество и режим повторений, интерполяторы и состояние (start, pause, resume, cancel).
- Типичные случаи: Подходит для анимации нестандартных свойств (layout-параметры, кастомные view, свойства отрисовки, числовые счётчики), которые не поддерживаются property-аниматорами напрямую.

## References

- Android Developers: ValueAnimator (developer.android.com)
