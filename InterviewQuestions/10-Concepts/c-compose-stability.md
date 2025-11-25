---
id: "20251110-124741"
title: "Compose Stability / Compose Stability"
aliases: ["Compose Stability"]
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
date created: Monday, November 10th 2025, 8:37:43 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Compose Stability in Jetpack Compose is a property of values and functions that determines whether they can change across recompositions and therefore whether Compose must re-read or re-execute them. It is central to how the Compose compiler optimizes recomposition, skips unnecessary UI updates, and preserves correctness when state changes. Understanding stability helps you design performant, predictable composables and avoid accidental recomposition storms or stale UI.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Compose Stability в Jetpack Compose — это свойство значений и функций, определяющее, могут ли они изменяться между рекомпозициями и нужно ли Compose заново их читать или выполнять. Это ключ к тому, как компилятор Compose оптимизирует рекомпозицию, пропуская лишние обновления UI и сохраняя корректность при изменении состояния. Понимание стабильности помогает проектировать производительные и предсказуемые composable-функции и избегать лишних рекомпозиций и устаревшего UI.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Stable vs unstable types: A "stable" type guarantees that Compose can detect all changes in its public state; if no tracked fields change, recomposition using that value can be skipped.
- Built-in stable entities: Many primitives (e.g., Int, String), immutable data classes with stable fields, and key Compose types (e.g., Modifier) are treated as stable by the compiler.
- Compiler analysis: The Compose compiler performs stability analysis and uses it to generate equality checks and decide when to skip or re-run composables.
- API and design impact: Marking types as immutable/stable (e.g., with @Immutable/@Stable) and preferring immutable state holders reduces unnecessary recompositions and improves performance.
- Common pitfalls: Passing mutable collections, lambdas capturing changing state, or large unstable objects into composables can mark parameters as unstable and trigger excessive recomposition.

## Ключевые Моменты (RU)

- Stable vs unstable типы: "Стабильный" тип гарантирует, что Compose может отследить все изменения его публичного состояния; если отслеживаемые поля не изменились, рекомпозицию с таким значением можно пропустить.
- Встроенные стабильные сущности: Многие примитивы (например, Int, String), неизменяемые data-классы со стабильными полями и ключевые типы Compose (например, Modifier) рассматриваются компилятором как стабильные.
- Анализ компилятора: Компилятор Compose выполняет анализ стабильности и на его основе генерирует проверки равенства и решает, когда можно пропустить или заново выполнить composable-функции.
- Влияние на дизайн API: Отмечание типов как immutable/stable (например, через @Immutable/@Stable) и использование неизменяемых контейнеров состояния уменьшают количество лишних рекомпозиций и улучшают производительность.
- Типичные ошибки: Передача изменяемых коллекций, лямбд с захватом меняющегося состояния или крупных нестабильных объектов в composable делает параметры нестабильными и приводит к избыточным рекомпозициям.

## References

- Official Jetpack Compose docs: https://developer.android.com/jetpack/compose
- Jetpack Compose Compiler and stability annotations: https://developer.android.com/jetpack/compose/performance/stability
