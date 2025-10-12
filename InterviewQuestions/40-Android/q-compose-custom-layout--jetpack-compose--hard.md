---
topic: jetpack-compose
tags:
  - jetpack-compose
  - custom-layout
  - measure
  - layout
difficulty: hard
status: draft
---

# Custom Layout Composables

**English**: Implement a custom Layout composable. Explain measure policy, intrinsic measurements, and multi-pass layout.

**Russian**: Реализуйте кастомный Layout composable. Объясните measure policy, intrinsic measurements и multi-pass layout.

## Answer (EN)

Creating custom layouts in Jetpack Compose allows you to implement complex layout logic that goes beyond standard layouts like Column, Row, or Box.

### Layout Basics

The `Layout` composable is the foundation for all layouts in Compose:

```kotlin
@Composable
fun CustomLayout(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(
        modifier = modifier,
        content = content
    ) { measurables, constraints ->
        // 1. Measure children
        val placeables = measurables.map { measurable ->
            measurable.measure(constraints)
        }

        // 2. Calculate layout size
        val width = placeables.maxOfOrNull { it.width } ?: 0
        val height = placeables.sumOf { it.height }

        // 3. Position children
        layout(width, height) {
            var yPosition = 0
            placeables.forEach { placeable ->
                placeable.place(x = 0, y = yPosition)
                yPosition += placeable.height
            }
        }
    }
}
```

### Measure Policy

The measure policy defines how children are measured and positioned:

```kotlin
val customMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Custom measurement logic
    val placeables = measurables.map { it.measure(constraints) }

    layout(constraints.maxWidth, constraints.maxHeight) {
        // Custom placement logic
    }
}

@Composable
fun CustomLayoutWithPolicy(modifier: Modifier = Modifier) {
    Layout(
        content = { /* children */ },
        measurePolicy = customMeasurePolicy,
        modifier = modifier
    )
}
```

### Constraints System

Constraints define the min/max width and height for a child:

```kotlin
data class Constraints(
    val minWidth: Int,
    val maxWidth: Int,
    val minHeight: Int,
    val maxHeight: Int
)

// Create specific constraints
val fixedConstraints = Constraints.fixed(width = 100, height = 100)
val looseConstraints = Constraints(maxWidth = 500, maxHeight = 500)
val tightConstraints = Constraints(
    minWidth = 200,
    maxWidth = 200,
    minHeight = 100,
    maxHeight = 100
)
```

### Custom FlowLayout Implementation

FlowLayout arranges children in rows, wrapping to next row when needed:

```kotlin
@Composable
fun FlowLayout(
    modifier: Modifier = Modifier,
    horizontalSpacing: Dp = 0.dp,
    verticalSpacing: Dp = 0.dp,
    content: @Composable () -> Unit
) {
    Layout(
        modifier = modifier,
        content = content
    ) { measurables, constraints ->
        val horizontalSpacingPx = horizontalSpacing.roundToPx()
        val verticalSpacingPx = verticalSpacing.roundToPx()

        // Measure all children with loose constraints
        val placeables = measurables.map { measurable ->
            measurable.measure(constraints.copy(minWidth = 0, minHeight = 0))
        }

        // Calculate rows
        val rows = mutableListOf<List<Placeable>>()
        var currentRow = mutableListOf<Placeable>()
        var currentRowWidth = 0

        placeables.forEach { placeable ->
            val placeableWidth = placeable.width + horizontalSpacingPx

            if (currentRowWidth + placeableWidth <= constraints.maxWidth || currentRow.isEmpty()) {
                currentRow.add(placeable)
                currentRowWidth += placeableWidth
            } else {
                rows.add(currentRow)
                currentRow = mutableListOf(placeable)
                currentRowWidth = placeableWidth
            }
        }
        if (currentRow.isNotEmpty()) {
            rows.add(currentRow)
        }

        // Calculate layout dimensions
        val width = constraints.maxWidth
        val height = rows.sumOf { row ->
            row.maxOfOrNull { it.height } ?: 0
        } + (rows.size - 1) * verticalSpacingPx

        // Place children
        layout(width, height) {
            var yPosition = 0
            rows.forEach { row ->
                var xPosition = 0
                val rowHeight = row.maxOfOrNull { it.height } ?: 0

                row.forEach { placeable ->
                    placeable.place(xPosition, yPosition)
                    xPosition += placeable.width + horizontalSpacingPx
                }

                yPosition += rowHeight + verticalSpacingPx
            }
        }
    }
}

// Usage
@Composable
fun FlowLayoutExample() {
    FlowLayout(
        horizontalSpacing = 8.dp,
        verticalSpacing = 8.dp,
        modifier = Modifier.fillMaxWidth()
    ) {
        repeat(10) { index ->
            Chip(text = "Item $index")
        }
    }
}
```

### Custom StaggeredGrid Implementation

```kotlin
@Composable
fun StaggeredGrid(
    modifier: Modifier = Modifier,
    columns: Int = 2,
    spacing: Dp = 8.dp,
    content: @Composable () -> Unit
) {
    Layout(
        modifier = modifier,
        content = content
    ) { measurables, constraints ->
        val spacingPx = spacing.roundToPx()
        val columnWidth = (constraints.maxWidth - (columns - 1) * spacingPx) / columns

        // Create constraints for children
        val itemConstraints = constraints.copy(
            minWidth = 0,
            maxWidth = columnWidth,
            minHeight = 0
        )

        // Measure all children
        val placeables = measurables.map { it.measure(itemConstraints) }

        // Track column heights
        val columnHeights = IntArray(columns) { 0 }

        // Assign items to columns
        val columnItems = List(columns) { mutableListOf<Pair<Placeable, Int>>() }

        placeables.forEach { placeable ->
            // Find shortest column
            val shortestColumn = columnHeights.indices.minByOrNull { columnHeights[it] } ?: 0
            val yPosition = columnHeights[shortestColumn]

            columnItems[shortestColumn].add(placeable to yPosition)
            columnHeights[shortestColumn] += placeable.height + spacingPx
        }

        // Calculate total height
        val height = columnHeights.maxOrNull() ?: 0

        // Place items
        layout(constraints.maxWidth, height) {
            columnItems.forEachIndexed { columnIndex, items ->
                val xPosition = columnIndex * (columnWidth + spacingPx)

                items.forEach { (placeable, yPosition) ->
                    placeable.place(xPosition, yPosition)
                }
            }
        }
    }
}
```

### Intrinsic Measurements

Intrinsic measurements allow parents to query child size preferences before actual measurement:

```kotlin
@Composable
fun IntrinsicLayout(modifier: Modifier = Modifier) {
    Layout(
        modifier = modifier,
        content = {
            Text("Short")
            Text("Very long text here")
        }
    ) { measurables, constraints ->
        // Query intrinsic width of all children
        val maxIntrinsicWidth = measurables.maxOfOrNull {
            it.maxIntrinsicWidth(constraints.maxHeight)
        } ?: 0

        // Measure all children with the same width
        val placeables = measurables.map { measurable ->
            measurable.measure(
                constraints.copy(
                    minWidth = maxIntrinsicWidth,
                    maxWidth = maxIntrinsicWidth
                )
            )
        }

        val height = placeables.sumOf { it.height }

        layout(maxIntrinsicWidth, height) {
            var yPosition = 0
            placeables.forEach { placeable ->
                placeable.place(0, yPosition)
                yPosition += placeable.height
            }
        }
    }
}
```

**Intrinsic measurement methods**:
- `minIntrinsicWidth(height: Int)`: Minimum width needed given height
- `maxIntrinsicWidth(height: Int)`: Maximum useful width given height
- `minIntrinsicHeight(width: Int)`: Minimum height needed given width
- `maxIntrinsicHeight(width: Int)`: Maximum useful height given width

### Multi-Pass Layout

Compose layouts should be single-pass for performance, but intrinsics enable multi-pass patterns:

```kotlin
@Composable
fun TwoPassLayout(modifier: Modifier = Modifier) {
    Layout(
        modifier = modifier,
        content = {
            Box(Modifier.background(Color.Red))
            Box(Modifier.background(Color.Blue))
        }
    ) { measurables, constraints ->
        // First pass: measure with intrinsics
        val intrinsicSizes = measurables.map { measurable ->
            measurable.maxIntrinsicWidth(constraints.maxHeight)
        }

        val averageWidth = intrinsicSizes.average().toInt()

        // Second pass: measure with calculated constraints
        val placeables = measurables.map { measurable ->
            measurable.measure(
                constraints.copy(
                    minWidth = averageWidth,
                    maxWidth = averageWidth
                )
            )
        }

        layout(constraints.maxWidth, placeables.sumOf { it.height }) {
            var yPosition = 0
            placeables.forEach { placeable ->
                placeable.place(0, yPosition)
                yPosition += placeable.height
            }
        }
    }
}
```

### ParentDataModifier for Child Configuration

```kotlin
data class GridScope(val row: Int, val column: Int)

fun Modifier.gridItem(row: Int, column: Int) = this.then(
    object : ParentDataModifier {
        override fun Density.modifyParentData(parentData: Any?) =
            GridScope(row, column)
    }
)

@Composable
fun GridLayout(
    rows: Int,
    columns: Int,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(
        modifier = modifier,
        content = content
    ) { measurables, constraints ->
        val cellWidth = constraints.maxWidth / columns
        val cellHeight = constraints.maxHeight / rows

        val placeables = measurables.map { measurable ->
            val gridScope = measurable.parentData as? GridScope
            measurable.measure(
                constraints.copy(
                    minWidth = 0,
                    maxWidth = cellWidth,
                    minHeight = 0,
                    maxHeight = cellHeight
                )
            ) to gridScope
        }

        layout(constraints.maxWidth, constraints.maxHeight) {
            placeables.forEach { (placeable, scope) ->
                if (scope != null) {
                    placeable.place(
                        x = scope.column * cellWidth,
                        y = scope.row * cellHeight
                    )
                }
            }
        }
    }
}

// Usage
@Composable
fun GridExample() {
    GridLayout(rows = 3, columns = 3) {
        Box(Modifier.gridItem(0, 0).background(Color.Red))
        Box(Modifier.gridItem(1, 1).background(Color.Blue))
        Box(Modifier.gridItem(2, 2).background(Color.Green))
    }
}
```

### Advanced: Custom LayoutModifier

```kotlin
fun Modifier.customPosition(
    x: Dp = 0.dp,
    y: Dp = 0.dp
) = this.layout { measurable, constraints ->
    val placeable = measurable.measure(constraints)

    layout(placeable.width, placeable.height) {
        placeable.place(
            x = x.roundToPx(),
            y = y.roundToPx()
        )
    }
}

fun Modifier.aspectRatio(ratio: Float) = this.layout { measurable, constraints ->
    val width = if (constraints.hasBoundedWidth) {
        constraints.maxWidth
    } else {
        constraints.maxHeight * ratio.toInt()
    }

    val height = (width / ratio).toInt()

    val placeable = measurable.measure(
        Constraints.fixed(width, height)
    )

    layout(placeable.width, placeable.height) {
        placeable.place(0, 0)
    }
}
```

### Complete Example: Custom Carousel Layout

```kotlin
@Composable
fun CarouselLayout(
    modifier: Modifier = Modifier,
    itemSpacing: Dp = 16.dp,
    content: @Composable () -> Unit
) {
    Layout(
        modifier = modifier,
        content = content
    ) { measurables, constraints ->
        val spacingPx = itemSpacing.roundToPx()

        // Calculate item width (showing 1.5 items)
        val itemWidth = ((constraints.maxWidth - spacingPx) * 2 / 3)

        val itemConstraints = constraints.copy(
            minWidth = itemWidth,
            maxWidth = itemWidth,
            minHeight = 0
        )

        // Measure all items
        val placeables = measurables.map { measurable ->
            measurable.measure(itemConstraints)
        }

        val height = placeables.maxOfOrNull { it.height } ?: 0

        layout(constraints.maxWidth, height) {
            var xPosition = 0

            placeables.forEach { placeable ->
                placeable.place(xPosition, 0)
                xPosition += itemWidth + spacingPx
            }
        }
    }
}
```

### Performance Considerations

**1. Measure once rule**:
```kotlin
// WRONG: Multiple measurements
val placeable1 = measurable.measure(constraints1)
val placeable2 = measurable.measure(constraints2)  // ❌ Second measurement!

// CORRECT: Single measurement
val placeable = measurable.measure(constraints)
```

**2. Constraint optimization**:
```kotlin
// Prefer tight constraints when possible
val tightConstraints = Constraints.fixed(width, height)

// Use copy for constraint modifications
val relaxedConstraints = constraints.copy(minWidth = 0, minHeight = 0)
```

**3. Avoid allocations in layout**:
```kotlin
// WRONG: Creating list in layout
layout(width, height) {
    val positions = mutableListOf<Int>()  // ❌ Allocation
    // ...
}

// CORRECT: Calculate positions directly
layout(width, height) {
    var yPosition = 0
    placeables.forEach { placeable ->
        placeable.place(0, yPosition)
        yPosition += placeable.height
    }
}
```

### Common Pitfalls

**1. Not handling empty measurables**:
```kotlin
// WRONG: Assumes measurables exist
val width = placeables.maxOf { it.width }  // Crashes if empty!

// CORRECT: Handle empty case
val width = placeables.maxOfOrNull { it.width } ?: 0
```

**2. Ignoring constraints**:
```kotlin
// WRONG: Fixed size ignoring constraints
layout(fixedWidth, fixedHeight) { ... }

// CORRECT: Respect constraints
val width = constraints.constrainWidth(desiredWidth)
val height = constraints.constrainHeight(desiredHeight)
layout(width, height) { ... }
```

**3. Placing outside bounds**:
```kotlin
// WRONG: Can place outside parent
placeable.place(x = -100, y = -100)

// CORRECT: Clamp to valid positions
placeable.place(
    x = x.coerceIn(0, width - placeable.width),
    y = y.coerceIn(0, height - placeable.height)
)
```

### Best Practices

1. **Measure each child exactly once**
2. **Respect parent constraints**
3. **Handle empty measurables list**
4. **Use intrinsics for multi-pass layouts**
5. **Avoid allocations in layout lambda**
6. **Test with various constraint scenarios**
7. **Consider RTL support** with `place(x, y)` vs `placeRelative(x, y)`
8. **Document custom layout behavior**
9. **Profile performance** with Layout Inspector

## Ответ (RU)

Создание кастомных layouts в Jetpack Compose позволяет реализовать сложную логику компоновки.

### Основы Layout

Composable `Layout` - это основа для всех layouts в Compose. Он принимает:
- `content`: дочерние composables
- `measurePolicy` или лямбду с логикой измерения/размещения

### Measure Policy

Определяет как дети измеряются и позиционируются.

[Полные примеры реализаций FlowLayout, StaggeredGrid и Carousel приведены в английском разделе]

### Лучшие практики

1. **Измеряйте каждого ребенка ровно один раз**
2. **Уважайте ограничения родителя**
3. **Обрабатывайте пустой список measurables**
4. **Используйте intrinsics для multi-pass layouts**
5. **Избегайте аллокаций в layout лямбде**
6. **Тестируйте с различными сценариями ограничений**
7. **Учитывайте поддержку RTL**
8. **Документируйте поведение**
9. **Профилируйте производительность**


---

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - compose modifier order performance 
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - compose navigation advanced   jetpack
- [[q-compose-remember-derived-state--jetpack-compose--medium]] - compose remember derived state 

### Related (Hard)
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - compose side effects advanced 
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]] - compose lazy layout optimization 
### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - compose modifier order performance 
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - compose navigation advanced   jetpack
- [[q-compose-remember-derived-state--jetpack-compose--medium]] - compose remember derived state 

### Related (Hard)
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - compose side effects advanced 
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]] - compose lazy layout optimization 
### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table internals
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

