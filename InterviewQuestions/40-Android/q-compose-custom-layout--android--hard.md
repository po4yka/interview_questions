---\
id: android-054
title: Compose Custom Layout / Кастомный layout в Compose
aliases: [Compose Custom Layout, Custom Layout Jetpack Compose, Кастомная разметка Compose, Кастомный layout в Compose]
topic: android
subtopics: [ui-compose, ui-graphics]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, q-compose-canvas-graphics--android--hard, q-compose-compiler-plugin--android--hard, q-compose-custom-animations--android--medium, q-compose-lazy-layout-optimization--android--hard, q-custom-viewgroup-layout--android--hard]
sources: []
created: 2023-10-11
updated: 2025-11-10
tags: [android/ui-compose, android/ui-graphics, difficulty/hard]

---\
# Вопрос (RU)
> Как создать кастомный layout в Compose? Объясните механизм measurement и placement.

# Question (EN)
> How to create a custom layout in Compose? Explain the measurement and placement mechanism.

---

## Ответ (RU)

### Краткий Вариант

Создать кастомный layout в Compose можно через `Layout` или собственный `MeasurePolicy`:
- На этапе измерения передаем детям `Constraints` и получаем `Placeable`.
- На этапе вычисления определяем размер layout на основе результатов измерения и своих `Constraints`.
- На этапе размещения вызываем `place`/`placeRelative` для `Placeable` с нужными координатами, учитывая RTL.

### Подробный Вариант

#### Основные Концепции

`Layout` в Compose использует `MeasurePolicy` — контракт из трех шагов:
1. Measurement — каждый дочерний элемент измеряется с переданными `Constraints` (min/max width/height).
2. Calculation — layout вычисляет собственный размер на основе измеренных дочерних элементов и своих `Constraints`.
3. Placement — размещение дочерних элементов в координатах layout.

Ключевые правила:
- Каждый `Measurable` должен измеряться детерминированно и с валидными ограничениями; повторные измерения допустимы и иногда необходимы, но могут быть дорогими, поэтому их стоит минимизировать.
- Минимизируйте аллокации в `measure`/`place` (горячий путь, влияет на производительность).
- Используйте `placeRelative` для корректной RTL-поддержки: он интерпретирует горизонтальные координаты относительно "начала" (`start`), а не фиксированного `left`.

#### Архитектура (пример Кастомного layout)

Высокоуровневая схема для кастомного layout на примере `TwoColumn`:
- Компонент-обертка `@Composable` → вызывает `Layout`.
- В лямбде `measurePolicy`:
  - Делим список детей на логические группы (левая/правая колонка).
  - Измеряем детей с подходящими `Constraints`.
  - Вычисляем итоговую ширину/высоту layout.
  - Размещаем `Placeable` в нужных координатах.

#### Минимальный Пример: TwoColumn

```kotlin
@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    gap: Dp = 8.dp,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        val gapPx = gap.roundToPx().coerceAtLeast(0)

        // Делим список детей на две колонки
        val mid = (measurables.size + 1) / 2
        val leftMeasurables = measurables.subList(0, mid)
        val rightMeasurables = measurables.subList(mid, measurables.size)

        // Распределяем доступную ширину между колонками с учетом gap
        // Упрощение: считаем, что maxWidth задает полезную доступную ширину.
        val totalMaxWidth = constraints.maxWidth
        val availableForColumns = (totalMaxWidth - gapPx).coerceAtLeast(0)
        val leftMaxWidth = availableForColumns / 2
        val rightMaxWidth = availableForColumns - leftMaxWidth

        val leftColumnConstraints = constraints.copy(
            maxWidth = leftMaxWidth,
            minWidth = 0
        )
        val rightColumnConstraints = constraints.copy(
            maxWidth = rightMaxWidth,
            minWidth = 0
        )

        // Измеряем детей
        val leftPlaceables = leftMeasurables.map { it.measure(leftColumnConstraints) }
        val rightPlaceables = rightMeasurables.map { it.measure(rightColumnConstraints) }

        // Фактические ширины колонок по измеренным детям
        val leftColumnWidth = leftPlaceables.maxOfOrNull { it.width } ?: 0
        val rightColumnWidth = rightPlaceables.maxOfOrNull { it.width } ?: 0

        // Высоты колонок (вертикальное стекание)
        val leftColumnHeight = leftPlaceables.sumOf { it.height }
        val rightColumnHeight = rightPlaceables.sumOf { it.height }

        val layoutWidth = (leftColumnWidth + gapPx + rightColumnWidth)
            .coerceIn(constraints.minWidth, constraints.maxWidth)
        val layoutHeight = maxOf(leftColumnHeight, rightColumnHeight)
            .coerceIn(constraints.minHeight, constraints.maxHeight)

        layout(layoutWidth, layoutHeight) {
            var yLeft = 0
            leftPlaceables.forEach { placeable ->
                placeable.placeRelative(0, yLeft)
                yLeft += placeable.height
            }

            var yRight = 0
            val rightX = (leftColumnWidth + gapPx).coerceAtMost(layoutWidth)
            rightPlaceables.forEach { placeable ->
                placeable.placeRelative(rightX, yRight)
                yRight += placeable.height
            }
        }
    }
}
```

(Это обучающий пример: для production-кода нужно тщательнее учитывать `Constraints` (в т.ч. ненулевой `minWidth`) и следить за количеством аллокаций в `measure`.)

#### Переиспользуемый MeasurePolicy

Для оптимизации можно вынести реализацию `MeasurePolicy` отдельно, если она не захватывает состояние композиции:

```kotlin
private val twoColumnMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Логика измерения и размещения, аналогичная выше, без захвата State
}

@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier, twoColumnMeasurePolicy)
}
```

Уточнение: top-level `MeasurePolicy` не должен напрямую захватывать `State`/`remember`. Если layout зависит от параметров (`gap`, `spacing`), `MeasurePolicy` обычно создают внутри composable, чтобы он корректно отражал параметры.

#### Intrinsics

Intrinsics позволяют родителю узнать желательные размеры до реального `measure`.

```kotlin
val policy = object : MeasurePolicy {
    override fun MeasureScope.measure(
        measurables: List<Measurable>,
        constraints: Constraints
    ): MeasureResult {
        // ... реализация кастомного измерения и размещения ...
    }

    override fun IntrinsicMeasureScope.minIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ): Int = measurables.sumOf { it.minIntrinsicHeight(width) }
}
```

Здесь переопределен только один intrinsic-метод; остальные используют реализации по умолчанию. Если кастомный `Layout` участвует в вычислениях intrinsic-типов у родителя, имеет смысл реализовать все четыре intrinsic-метода.

#### Рекомендации По Производительности

- Использовать стабильные параметры и иммутабельные типы.
- Минимизировать временные аллокации в `measure`/`place`.
- Не читать изменяемое состояние напрямую в `measure`/`place`; все значения передавать как параметры.

### Требования

#### Функциональные

- Поддержка измерения детей с учетом `Constraints`.
- Гибкая схема размещения элементов через `MeasurePolicy`.
- Возможность разделения контента на несколько зон (например, две колонки).
- Поддержка RTL через `placeRelative`.

#### Нефункциональные

- Высокая производительность: минимум аллокаций и лишних измерений.
- Предсказуемое поведение при сложных деревьях layout.
- Масштабируемость до большого количества элементов без драматической деградации.

---

## Answer (EN)

### Short Version

Create a custom layout in Compose using `Layout` or a custom `MeasurePolicy`:
- In measurement, pass `Constraints` to children and obtain `Placeable`s.
- In size calculation, compute the layout size from children and its own `Constraints`.
- In placement, call `place`/`placeRelative` on `Placeable`s with proper coordinates, respecting RTL.

### Detailed Version

#### Core Concepts

`Layout` in Compose uses a `MeasurePolicy` — a three-step contract:
1. Measurement — measure each child with provided `Constraints` (min/max width/height).
2. Calculation — compute the layout size based on measured children and its own `Constraints`.
3. Placement — place children in the layout's coordinate space.

Key rules:
- Each `Measurable` must be measured deterministically with valid constraints; re-measurement is allowed and sometimes necessary but can be expensive, so keep it under control.
- Minimize allocations in `measure`/`place` (they are hot paths and affect performance).
- Use `placeRelative` for correct RTL support: it interprets horizontal coordinates relative to "start" instead of always using left.

#### Architecture (example Custom layout)

High-level structure for a custom layout like `TwoColumn`:
- Wrapper `@Composable` → calls `Layout`.
- Inside the `measurePolicy` lambda:
  - Split children into logical groups (left/right column).
  - Measure them with appropriate `Constraints`.
  - Compute final width/height.
  - Place `Placeable`s at required coordinates.

#### Minimal Example: TwoColumn

```kotlin
@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    gap: Dp = 8.dp,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        val gapPx = gap.roundToPx().coerceAtLeast(0)

        // Split children into two columns
        val mid = (measurables.size + 1) / 2
        val leftMeasurables = measurables.subList(0, mid)
        val rightMeasurables = measurables.subList(mid, measurables.size)

        // Distribute available width between columns accounting for the gap
        // Simplification: treat maxWidth as the effective available width.
        val totalMaxWidth = constraints.maxWidth
        val availableForColumns = (totalMaxWidth - gapPx).coerceAtLeast(0)
        val leftMaxWidth = availableForColumns / 2
        val rightMaxWidth = availableForColumns - leftMaxWidth

        val leftColumnConstraints = constraints.copy(
            maxWidth = leftMaxWidth,
            minWidth = 0
        )
        val rightColumnConstraints = constraints.copy(
            maxWidth = rightMaxWidth,
            minWidth = 0
        )

        // Measure children
        val leftPlaceables = leftMeasurables.map { it.measure(leftColumnConstraints) }
        val rightPlaceables = rightMeasurables.map { it.measure(rightColumnConstraints) }

        // Actual column widths from measured children
        val leftColumnWidth = leftPlaceables.maxOfOrNull { it.width } ?: 0
        val rightColumnWidth = rightPlaceables.maxOfOrNull { it.width } ?: 0

        // Column heights (vertical stacking)
        val leftColumnHeight = leftPlaceables.sumOf { it.height }
        val rightColumnHeight = rightPlaceables.sumOf { it.height }

        val layoutWidth = (leftColumnWidth + gapPx + rightColumnWidth)
            .coerceIn(constraints.minWidth, constraints.maxWidth)
        val layoutHeight = maxOf(leftColumnHeight, rightColumnHeight)
            .coerceIn(constraints.minHeight, constraints.maxHeight)

        layout(layoutWidth, layoutHeight) {
            var yLeft = 0
            leftPlaceables.forEach { placeable ->
                placeable.placeRelative(0, yLeft)
                yLeft += placeable.height
            }

            var yRight = 0
            val rightX = (leftColumnWidth + gapPx).coerceAtMost(layoutWidth)
            rightPlaceables.forEach { placeable ->
                placeable.placeRelative(rightX, yRight)
                yRight += placeable.height
            }
        }
    }
}
```

(This is a didactic example: in production you should handle `Constraints` more thoroughly (including non-zero `minWidth`) and carefully watch allocations inside `measure`.)

#### Reusable MeasurePolicy

You can extract a `MeasurePolicy` if it does not capture composition state:

```kotlin
private val twoColumnMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Measurement and placement logic using only parameters
}

@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier, twoColumnMeasurePolicy)
}
```

Clarification: a top-level `MeasurePolicy` must not capture `State`/`remember`. If the layout depends on parameters (`gap`, `spacing`), construct the `MeasurePolicy` inside the composable so it correctly reflects those parameters.

#### Intrinsics

Intrinsics let a parent query desired sizes before actual measurement:

```kotlin
val policy = object : MeasurePolicy {
    override fun MeasureScope.measure(
        measurables: List<Measurable>,
        constraints: Constraints
    ): MeasureResult {
        // ... custom measurement & placement implementation ...
    }

    override fun IntrinsicMeasureScope.minIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ): Int = measurables.sumOf { it.minIntrinsicHeight(width) }
}
```

Here only one intrinsic method is overridden; others use defaults. If your custom `Layout` is used inside components that rely on intrinsic sizes, consider implementing all four intrinsic methods (`min/max width/height`).

#### Performance Tips

- Prefer stable and immutable parameters where possible.
- Minimize temporary allocations in `measure`/`place`.
- Avoid reading mutable state directly in `measure`/`place`; pass the required values as parameters.

### Requirements

#### Functional

- Support measuring children according to `Constraints`.
- Provide flexible placement via `MeasurePolicy`.
- Allow splitting content into multiple zones (e.g., two columns).
- Support RTL via `placeRelative`.

#### Non-functional

- High performance: minimal allocations and redundant measurements.
- Predictable behavior in complex layout trees.
- Ability to scale to many children without severe degradation.

---

## Follow-ups (RU)

- Как обрабатывать случаи, когда дочерние элементы не помещаются в `constraints`?
- В чем разница между `placeRelative` и `place`?
- Когда нужно реализовывать все 4 intrinsic-метода (`minWidth`, `maxWidth`, `minHeight`, `maxHeight`)?
- Как протестировать кастомный layout с разными `constraints` и RTL?
- Какие проблемы производительности возникают при многократном remeasure и как их избежать?

## Follow-ups (EN)

- How to handle cases when children do not fit into the given `constraints`?
- What is the difference between `placeRelative` and `place`?
- When should you implement all 4 intrinsic methods (`minWidth`, `maxWidth`, `minHeight`, `maxHeight`)?
- How to test a custom layout with different `constraints` and RTL?
- What performance issues arise from frequent remeasurement, and how to avoid them?

## References

- [Custom layouts in Compose](https://developer.android.com/develop/ui/compose/layouts/custom)
- [Layout basics - `Constraints` and measurement](https://developer.android.com/develop/ui/compose/layouts/basics)
- [Compose performance best practices](https://developer.android.com/develop/ui/compose/performance)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]

### Related (Same Level)

- [[q-compose-canvas-graphics--android--hard]] — `Canvas` for custom drawing, Layout for custom measurement
- [[q-compose-compiler-plugin--android--hard]] — How Compose compiler optimizes layouts

### Advanced (Harder)

- Custom layouts with complex intrinsic calculations and nested `Constraints`
- Building layout modifiers that affect measurement behavior
- Optimizing layout performance in deep hierarchies with thousands of nodes
