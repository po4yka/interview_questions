---
id: android-268
title: "What Are Px Dp Sp / Что такое px dp и sp"
aliases: ["What Are Px Dp Sp", "Что такое px dp и sp"]

# Classification
topic: android
subtopics: [ui-theming, ui-views]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [c-density-independent-pixels, c-dimension-units]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags (EN only; no leading #)
tags: [accessibility, android/ui-theming, android/ui-views, difficulty/easy, dp, measurement-units, sp]
---

# Вопрос (RU)

> Что такое px, dp и sp в Android?

# Question (EN)

> What are px, dp, and sp in Android?

---

## Ответ (RU)

Android использует три основные единицы измерения для UI:

**px (pixels)** — физические пиксели экрана. Не рекомендуется для UI, так как одинаковое количество пикселей выглядит по-разному на экранах с разной плотностью.

**dp (density-independent pixels)** — абстрактная единица, которая автоматически масштабируется под плотность экрана. Используется для всех размеров UI элементов (кроме текста). 1dp = 1px на mdpi экране (160dpi).

**sp (scale-independent pixels)** — масштабируемые пиксели для текста. Как dp, но также учитывает настройки размера шрифта пользователя. Используется **только для текста**.

### Основные Правила

| Единица | Использовать для | Не использовать для |
|---------|------------------|---------------------|
| **dp** | Размеры view, отступы, иконки | Размер текста |
| **sp** | Размер текста | Размеры view |
| **px** | Редкие случаи (canvas) | Любые UI элементы |

### Таблица Конверсии Плотности

| Плотность | Множитель | Пример |
|-----------|-----------|--------|
| ldpi | 0.75x | 1dp = 0.75px |
| mdpi (базовая) | 1.0x | 1dp = 1px |
| hdpi | 1.5x | 1dp = 1.5px |
| xhdpi | 2.0x | 1dp = 2px |
| xxhdpi | 3.0x | 1dp = 3px |
| xxxhdpi | 4.0x | 1dp = 4px |

### Примеры Кода

#### XML (правильное использование)

```xml
<!-- ✅ Правильно: dp для layout, sp для текста -->
<TextView
    android:layout_width="200dp"
    android:layout_height="50dp"
    android:padding="16dp"
    android:textSize="16sp" />

<!-- ❌ Неправильно: px для UI -->
<TextView
    android:layout_width="200px"
    android:textSize="16px" />

<!-- ❌ Неправильно: dp для текста -->
<TextView
    android:textSize="16dp" />
```

#### Kotlin (конверсия единиц)

```kotlin
// ✅ Extension функции для удобной конверсии
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()

val Int.sp: Float
    get() = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_SP,
        this.toFloat(),
        Resources.getSystem().displayMetrics
    )

// Использование
view.layoutParams = LinearLayout.LayoutParams(
    100.dp,  // ✅ 100dp width
    50.dp    // ✅ 50dp height
)
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f) // ✅ 16sp
```

#### Jetpack Compose

```kotlin
@Composable
fun ProperDimensions() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp) // ✅ dp для отступов
    ) {
        Text(
            text = "Title",
            fontSize = 24.sp, // ✅ sp для текста
            modifier = Modifier.padding(bottom = 8.dp)
        )

        Button(
            onClick = { },
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp) // ✅ dp для размеров
        ) {
            Text(
                text = "Click Me",
                fontSize = 16.sp // ✅ sp для текста
            )
        }
    }
}
```

#### Утилиты Для Конверсии

```kotlin
class DimensionUtils(private val context: Context) {
    private val displayMetrics = context.resources.displayMetrics

    fun dpToPx(dp: Int): Int =
        (dp * displayMetrics.density).toInt()

    fun spToPx(sp: Float): Float =
        TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_SP,
            sp,
            displayMetrics
        )

    // ✅ Получение информации о плотности экрана
    fun getDensityInfo(): String = """
        Density: ${displayMetrics.density}
        DPI: ${displayMetrics.densityDpi}
        Scaled Density: ${displayMetrics.scaledDensity}
    """.trimIndent()
}
```

### Почему Sp Для Текста Критично Важно

```kotlin
// ❌ Плохо: игнорирует настройки пользователя
textView.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16f)

// ✅ Хорошо: адаптируется под настройки доступности
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
// Если пользователь установил "Большой шрифт" в настройках,
// текст автоматически увеличится
```

## Answer (EN)

Android uses three main measurement units for UI:

**px (pixels)** — physical screen points. Not recommended for UI as the same pixel count looks different on screens with varying densities.

**dp (density-independent pixels)** — abstract unit that automatically scales with screen density. Used for all UI element sizes (except text). 1dp = 1px on mdpi screens (160dpi).

**sp (scale-independent pixels)** — scalable pixels for text. Like dp, but also respects user's font size preferences. Used **only for text**.

### Core Rules

| Unit | Use For | Don't Use For |
|------|---------|---------------|
| **dp** | `View` dimensions, margins, icons | Text size |
| **sp** | Text size only | `View` dimensions |
| **px** | Rare cases (canvas) | Any UI elements |

### Density Conversion Table

| Density | Scale | Example |
|---------|-------|---------|
| ldpi | 0.75x | 1dp = 0.75px |
| mdpi (baseline) | 1.0x | 1dp = 1px |
| hdpi | 1.5x | 1dp = 1.5px |
| xhdpi | 2.0x | 1dp = 2px |
| xxhdpi | 3.0x | 1dp = 3px |
| xxxhdpi | 4.0x | 1dp = 4px |

### Code Examples

#### XML (correct usage)

```xml
<!-- ✅ Correct: dp for layout, sp for text -->
<TextView
    android:layout_width="200dp"
    android:layout_height="50dp"
    android:padding="16dp"
    android:textSize="16sp" />

<!-- ❌ Wrong: px for UI -->
<TextView
    android:layout_width="200px"
    android:textSize="16px" />

<!-- ❌ Wrong: dp for text size -->
<TextView
    android:textSize="16dp" />
```

#### Kotlin (unit conversion)

```kotlin
// ✅ Extension functions for easy conversion
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()

val Int.sp: Float
    get() = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_SP,
        this.toFloat(),
        Resources.getSystem().displayMetrics
    )

// Usage
view.layoutParams = LinearLayout.LayoutParams(
    100.dp,  // ✅ 100dp width
    50.dp    // ✅ 50dp height
)
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f) // ✅ 16sp
```

#### Jetpack Compose

```kotlin
@Composable
fun ProperDimensions() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp) // ✅ dp for padding
    ) {
        Text(
            text = "Title",
            fontSize = 24.sp, // ✅ sp for text
            modifier = Modifier.padding(bottom = 8.dp)
        )

        Button(
            onClick = { },
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp) // ✅ dp for dimensions
        ) {
            Text(
                text = "Click Me",
                fontSize = 16.sp // ✅ sp for text
            )
        }
    }
}
```

#### Conversion Utilities

```kotlin
class DimensionUtils(private val context: Context) {
    private val displayMetrics = context.resources.displayMetrics

    fun dpToPx(dp: Int): Int =
        (dp * displayMetrics.density).toInt()

    fun spToPx(sp: Float): Float =
        TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_SP,
            sp,
            displayMetrics
        )

    // ✅ Get screen density info
    fun getDensityInfo(): String = """
        Density: ${displayMetrics.density}
        DPI: ${displayMetrics.densityDpi}
        Scaled Density: ${displayMetrics.scaledDensity}
    """.trimIndent()
}
```

### Why Sp for Text is Critical

```kotlin
// ❌ Bad: ignores user preferences
textView.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16f)

// ✅ Good: adapts to accessibility settings
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
// If user sets "Large font" in system settings,
// text automatically scales up
```

---

## Follow-ups

- How do you handle dp/sp conversions in custom views?
- What happens to dp values when device configuration changes (rotation, fold)?
- How do you test UI with different density buckets and font scales?
- Why can't you use dp for text and sp for view dimensions?
- How does Jetpack Compose handle dp/sp differently from `View` system?

## References

- [[c-density-independent-pixels]] — Concept note on dp/sp system
- [[c-accessibility]] — Accessibility and sp scaling
- https://developer.android.com/training/multiscreen/screendensities — Screen densities guide
- https://developer.android.com/guide/practices/screens_support — Supporting different screens
- https://m3.material.io/foundations/layout/applying-layout/spacing — Material Design spacing

## Related Questions

### Prerequisites (Easier)
- [[q-view-basics--android--easy]] — Understanding views first
- [[q-layout-basics--android--easy]] — Layout fundamentals

### Related (Same Level)
- [[q-how-to-add-custom-attributes-to-custom-view--android--medium]] — Custom attributes in views
- [[q-resources-qualifiers--android--easy]] — Screen density qualifiers

### Advanced (Harder)
- [[q-custom-view-animation--android--medium]] — Drawing with px on canvas
- [[q-accessibility-testing--android--medium]] — Testing font scale changes
