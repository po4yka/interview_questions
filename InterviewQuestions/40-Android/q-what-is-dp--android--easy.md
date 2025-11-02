---
id: android-259
title: "What Is Dp / Что такое dp"
aliases: [Dp, Density-independent Pixels, Плотность-независимые пиксели]
topic: android
subtopics: [ui-compose, ui-views, ui-theming]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-are-px-dp-sp--android--easy, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-15
updated: 2025-10-27
sources: [https://developer.android.com/training/multiscreen/screendensities]
tags:
  - android/ui-compose
  - android/ui-views
  - android/ui-theming
  - density
  - material-design
  - difficulty/easy
---
# Вопрос (RU)

> Что такое dp (density-independent pixel, плотность-независимый пиксель)?

# Question (EN)

> What is dp (density-independent pixel)?

---

## Ответ (RU)

### Определение

**dp** (density-independent pixels, плотность-независимые пиксели) — единица измерения в Android для создания адаптивных интерфейсов, которые выглядят одинаково на устройствах с разной плотностью экрана.

### Зачем нужен dp

**Проблема**: При использовании пикселей (px) элементы UI имеют разный физический размер на разных устройствах.

**Решение**: dp автоматически масштабируется в зависимости от плотности экрана.

**Формула конвертации**:
```text
pixels = dp × (device dpi / 160)
```

**Пример**: 100dp на разных устройствах
- mdpi (160dpi): 100dp = 100px
- hdpi (240dpi): 100dp = 150px
- xhdpi (320dpi): 100dp = 200px
- xxhdpi (480dpi): 100dp = 300px

### Density Buckets

| Плотность | DPI     | Коэффициент | Папка            |
|-----------|---------|-------------|------------------|
| mdpi      | ~160dpi | 1.0         | drawable-mdpi    |
| hdpi      | ~240dpi | 1.5         | drawable-hdpi    |
| xhdpi     | ~320dpi | 2.0         | drawable-xhdpi   |
| xxhdpi    | ~480dpi | 3.0         | drawable-xxhdpi  |
| xxxhdpi   | ~640dpi | 4.0         | drawable-xxxhdpi |

### Использование в XML

```xml
<Button
    android:layout_width="200dp"   <!-- ✅ Используем dp -->
    android:layout_height="48dp"   <!-- ✅ Минимальный размер touch target -->
    android:padding="16dp"         <!-- ✅ Стандартный отступ Material -->
    android:text="Submit" />
```

### Использование в Compose

```kotlin
@Composable
fun DpExample() {
    Column(modifier = Modifier.padding(16.dp)) {  // ✅ .dp extension
        Button(
            onClick = { },
            modifier = Modifier
                .width(200.dp)
                .height(48.dp)  // ✅ Минимальный touch target
        ) {
            Text("Submit")
        }

        Icon(
            imageVector = Icons.Default.Star,
            modifier = Modifier.size(24.dp)  // ✅ Стандартный размер иконки
        )
    }
}
```

### Конвертация dp ↔ px

**View System**:
```kotlin
// dp → px
val density = resources.displayMetrics.density
val px = (100 * density).toInt()  // ✅ Правильно

// Extension
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()
```

**Compose**:
```kotlin
@Composable
fun DpConversion() {
    val density = LocalDensity.current
    val widthPx = with(density) { 100.dp.toPx() }  // ✅ dp → px
}
```

### Стандартные значения Material Design

```kotlin
// Отступы
8.dp   // Малый
16.dp  // Стандартный (самый частый)
24.dp  // Большой

// Touch targets
48.dp  // Минимальный размер для касания

// Иконки
24.dp  // Стандартная иконка
```

### dp vs px vs sp

| Случай использования | Единица | Пример              |
|---------------------|---------|---------------------|
| Размеры layout      | dp      | `width = 100.dp`    |
| Отступы/padding     | dp      | `padding(16.dp)`    |
| Размер текста       | **sp**  | `fontSize = 16.sp`  |
| Canvas (редко)      | px      | Операции рисования  |

### Best Practices

1. **Всегда используйте dp** для размеров элементов
2. **Никогда не используйте px** для UI (кроме Canvas)
3. **Используйте sp** для размера текста (не dp!)
4. **Кратность 4dp или 8dp** для согласованности

### Частые ошибки

```kotlin
// ❌ ПЛОХО: Использование px
textView.layoutParams.width = 100  // Это px!

// ✅ ХОРОШО: Конвертация dp в px
val widthPx = (100 * density).toInt()
textView.layoutParams.width = widthPx
```

---

## Answer (EN)

### Definition

**dp** (density-independent pixels) is an Android measurement unit for creating adaptive interfaces that look consistent across devices with different screen densities.

### Why dp Exists

**Problem**: Using pixels (px) results in different physical sizes on different devices.

**Solution**: dp automatically scales based on screen density.

**Conversion formula**:
```text
pixels = dp × (device dpi / 160)
```

**Example**: 100dp on different devices
- mdpi (160dpi): 100dp = 100px
- hdpi (240dpi): 100dp = 150px
- xhdpi (320dpi): 100dp = 200px
- xxhdpi (480dpi): 100dp = 300px

### Density Buckets

| Density | DPI     | Scale | Folder           |
|---------|---------|-------|------------------|
| mdpi    | ~160dpi | 1.0   | drawable-mdpi    |
| hdpi    | ~240dpi | 1.5   | drawable-hdpi    |
| xhdpi   | ~320dpi | 2.0   | drawable-xhdpi   |
| xxhdpi  | ~480dpi | 3.0   | drawable-xxhdpi  |
| xxxhdpi | ~640dpi | 4.0   | drawable-xxxhdpi |

### XML Usage

```xml
<Button
    android:layout_width="200dp"   <!-- ✅ Use dp -->
    android:layout_height="48dp"   <!-- ✅ Minimum touch target -->
    android:padding="16dp"         <!-- ✅ Standard Material padding -->
    android:text="Submit" />
```

### Compose Usage

```kotlin
@Composable
fun DpExample() {
    Column(modifier = Modifier.padding(16.dp)) {  // ✅ .dp extension
        Button(
            onClick = { },
            modifier = Modifier
                .width(200.dp)
                .height(48.dp)  // ✅ Minimum touch target
        ) {
            Text("Submit")
        }

        Icon(
            imageVector = Icons.Default.Star,
            modifier = Modifier.size(24.dp)  // ✅ Standard icon size
        )
    }
}
```

### Converting dp ↔ px

**View System**:
```kotlin
// dp → px
val density = resources.displayMetrics.density
val px = (100 * density).toInt()  // ✅ Correct

// Extension
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()
```

**Compose**:
```kotlin
@Composable
fun DpConversion() {
    val density = LocalDensity.current
    val widthPx = with(density) { 100.dp.toPx() }  // ✅ dp → px
}
```

### Material Design Standard Values

```kotlin
// Spacing
8.dp   // Small
16.dp  // Standard (most common)
24.dp  // Large

// Touch targets
48.dp  // Minimum touch target size

// Icons
24.dp  // Standard icon
```

### dp vs px vs sp

| Use Case         | Unit   | Example             |
|-----------------|--------|---------------------|
| Layout sizes    | dp     | `width = 100.dp`    |
| Padding/Margins | dp     | `padding(16.dp)`    |
| Text size       | **sp** | `fontSize = 16.sp`  |
| Canvas (rare)   | px     | Drawing operations  |

### Best Practices

1. **Always use dp** for layout dimensions
2. **Never use px** for UI (except Canvas)
3. **Use sp** for text sizes (not dp!)
4. **Use multiples of 4dp or 8dp** for consistency

### Common Mistakes

```kotlin
// ❌ BAD: Using px
textView.layoutParams.width = 100  // This is px!

// ✅ GOOD: Convert dp to px
val widthPx = (100 * density).toInt()
textView.layoutParams.width = widthPx
```

---

## Follow-ups

- Когда использовать sp вместо dp (и в Compose, и во View-системе)?
- Как связаны density buckets и папки ресурсов `drawable-*`/`mipmap-*`?
- Какие проблемы возникают при смешении px и dp?

## References

- https://developer.android.com/training/multiscreen/screendensities
- https://developer.android.com/guide/topics/resources/multiscreen-density
- https://m3.material.io/foundations/layout/applying-layout/spacing

## Related Questions

### Same Difficulty (Easy)
- [[q-what-are-px-dp-sp--android--easy]]

### Next Steps (Medium)
- [[q-what-are-the-most-important-components-of-compose--android--medium]]
