---
id: android-268
title: "What Are Px Dp Sp / Что такое px dp и sp"
aliases: ["What Are Px Dp Sp", "Что такое px dp и sp"]
topic: android
subtopics: [ui-theming, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [q-accessibility-text-scaling--android--medium, q-android-app-components--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [accessibility, android/ui-theming, android/ui-views, difficulty/easy, dp, measurement-units, sp]

---
# Вопрос (RU)

> Что такое px, dp и sp в Android?

# Question (EN)

> What are px, dp, and sp in Android?

---

## Ответ (RU)

Android использует три основные единицы измерения для UI:

**px (pixels)** — физические пиксели экрана. Для адаптивного UI обычно не рекомендуется, так как одинаковое количество пикселей выглядит по-разному на экранах с разной плотностью.

**dp (density-independent pixels)** — абстрактная единица, которая автоматически масштабируется под плотность экрана. Используется по умолчанию для всех размеров UI-элементов (кроме текста). 1dp = 1px на mdpi экране (160dpi).

**sp (scale-independent pixels)** — масштабируемые пиксели для текста. Как dp, но также учитывает настройки размера шрифта пользователя (scaledDensity). Рекомендуется использовать для текста и элементов, размер которых должен следовать настройкам шрифта пользователя.

### Основные Правила

| Единица | Использовать для | Не использовать для |
|---------|------------------|---------------------|
| **dp** | Размеры view, отступы, иконки | Размер текста |
| **sp** | Размер текста, элементов зависящих от размера шрифта | Фиксированные размеры layout |
| **px** | Редкие случаи (Canvas, низкоуровневый drawing) | Обычные UI-элементы |

### Таблица Конверсии Плотности

| Плотность | Множитель | Пример |
|-----------|-----------|--------|
| ldpi | 0.75x | 1dp = 0.75px |
| mdpi (базовая) | 1.0x | 1dp = 1px |
| hdpi | 1.5x | 1dp = 1.5px |
| xhdpi | 2.0x | 1dp = 2px |
| xxhdpi | 3.0x | 3.0x | 1dp = 3px |
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

<!-- ❌ Неправильно: px для обычного UI -->
<TextView
    android:layout_width="200px"
    android:textSize="16px" />

<!-- ❌ Неправильно: dp для текста (игнорирует настройки пользователя) -->
<TextView
    android:textSize="16dp" />
```

#### Kotlin (конверсия единиц)

```kotlin
// ✅ Extension-функции для конверсии (лучше использовать context.resources, а не Resources.getSystem())
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt() // Для простых примеров; в production учитывайте context

val Int.sp: Float
    get() = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_SP,
        this.toFloat(),
        Resources.getSystem().displayMetrics // В production используйте context.resources.displayMetrics
    )

// Использование
view.layoutParams = LinearLayout.LayoutParams(
    100.dp,  // ✅ 100dp ширина
    50.dp    // ✅ 50dp высота
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

### Дополнительные Вопросы (RU)

- Как вы обрабатываете конверсии dp/sp в кастомных view?
- Что происходит с значениями dp при изменении конфигурации устройства (ротация, fold)?
- Как тестировать UI с разными плотностями и масштабом шрифта?
- Почему нельзя использовать dp для текста и sp для размеров view?
- Как Jetpack Compose обрабатывает dp/sp по сравнению с системой `View`?

### Ссылки (RU)

- https://developer.android.com/training/multiscreen/screendensities — руководство по плотностям экранов
- https://developer.android.com/guide/practices/screens_support — поддержка разных экранов
- https://m3.material.io/foundations/layout/applying-layout/spacing — отступы в Material Design

### Связанные Вопросы (RU)

#### Предпосылки (проще)
- [[q-android-app-components--android--easy]] — сначала разберите базовые компоненты и view

#### Связанные (тот Же уровень)
- [[q-how-to-add-custom-attributes-to-custom-view--android--medium]] — кастомные атрибуты во view

#### Продвинутые (сложнее)
- [[q-custom-view-animation--android--medium]] — рисование с использованием px на canvas
- [[q-accessibility-testing--android--medium]] — тестирование изменений масштаба шрифта

## Answer (EN)

Android uses three main measurement units for UI:

**px (pixels)** — physical pixels of the screen. Typically not recommended for general UI layout because the same pixel count appears differently on screens with different densities.

**dp (density-independent pixels)** — an abstract unit that scales with screen density. Used by default for all UI element sizes (except text). 1dp = 1px on mdpi screens (160dpi).

**sp (scale-independent pixels)** — scalable pixels for text. Similar to dp, but also respects the user's font size preference (scaledDensity). Recommended for text and elements that should follow the user's font size settings.

### Core Rules

| Unit | Use For | Don't Use For |
|------|---------|---------------|
| **dp** | `View` dimensions, margins, icons | Text size |
| **sp** | Text size, font-dependent elements | Fixed layout dimensions |
| **px** | Rare cases (Canvas, low-level drawing) | Regular UI elements |

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

<!-- ❌ Wrong: px for regular UI -->
<TextView
    android:layout_width="200px"
    android:textSize="16px" />

<!-- ❌ Wrong: dp for text size (ignores user settings) -->
<TextView
    android:textSize="16dp" />
```

#### Kotlin (unit conversion)

```kotlin
// ✅ Extension functions for easy conversion (prefer using context.resources instead of Resources.getSystem() in production)
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt() // For simple examples; in production use context-aware metrics

val Int.sp: Float
    get() = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_SP,
        this.toFloat(),
        Resources.getSystem().displayMetrics // In production, use context.resources.displayMetrics
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

- https://developer.android.com/training/multiscreen/screendensities — Screen densities guide
- https://developer.android.com/guide/practices/screens_support — Supporting different screens
- https://m3.material.io/foundations/layout/applying-layout/spacing — Material Design spacing

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — Understanding views and components first

### Related (Same Level)
- [[q-how-to-add-custom-attributes-to-custom-view--android--medium]] — Custom attributes in views

### Advanced (Harder)
- [[q-custom-view-animation--android--medium]] — Drawing with px on canvas
- [[q-accessibility-testing--android--medium]] — Testing font scale changes
