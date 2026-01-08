---\
id: android-259
title: What Is Dp / Что такое dp
aliases: [Density-independent Pixels, Dp, Плотность-независимые пиксели]
topic: android
subtopics: [ui-compose, ui-theming, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, q-compose-core-components--android--medium, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-what-are-px-dp-sp--android--easy, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-15
updated: 2025-10-27
sources:
  - https://developer.android.com/training/multiscreen/screendensities
tags: [android/ui-compose, android/ui-theming, android/ui-views, density, difficulty/easy, material-design]
---\
# Вопрос (RU)

> Что такое dp (density-independent pixel, плотность-независимый пиксель)?

# Question (EN)

> What is dp (density-independent pixel)?

---

## Ответ (RU)

### Определение

**dp** (density-independent pixels, плотность-независимые пиксели) — единица измерения в Android для создания адаптивных интерфейсов, которые выглядят одинаково на устройствах с разной плотностью экрана.

### Зачем Нужен Dp

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

### Использование В XML

```xml
<Button
    android:layout_width="200dp"   <!-- ✅ Используем dp -->
    android:layout_height="48dp"   <!-- ✅ Частый рекомендуемый минимальный размер области касания -->
    android:padding="16dp"         <!-- ✅ Стандартный отступ Material -->
    android:text="Submit" />
```

### Использование В Compose

```kotlin
@Composable
fun DpExample() {
    Column(modifier = Modifier.padding(16.dp)) {  // ✅ .dp extension
        Button(
            onClick = { },
            modifier = Modifier
                .width(200.dp)
                .height(48.dp)  // ✅ Частый рекомендуемый минимальный touch target
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

### Конвертация Dp ↔ Px

**`View` System**:
```kotlin
// dp → px (упрощённый пример; в реальных проектах используйте Context-специфичные ресурсы)
val density = resources.displayMetrics.density
val px = (100 * density).toInt()

// Extension (демонстрационный; привязан к системным ресурсам и не учитывает контекст)
val Int.dpToPx: Int
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

### Стандартные Значения Material Design

```kotlin
// Отступы (часто используемые значения)
8.dp   // Малый
16.dp  // Стандартный (самый частый)
24.dp  // Большой

// Touch targets
48.dp  // Исторически рекомендуемый минимум области касания в Android

// Иконки
24.dp  // Стандартная иконка
```

### Dp Vs Px Vs Sp

| Случай использования        | Единица | Пример              |
|-----------------------------|---------|---------------------|
| Размеры layout              | dp      | `width = 100.dp`    |
| Отступы/padding/margin      | dp      | `padding(16.dp)`    |
| Размер текста               | **sp**  | `fontSize = 16.sp`  |
| `Canvas` и низкоуровневый UI  | px      | Операции рисования  |

### Best Practices

1. **Предпочитайте dp** для размеров элементов
2. **Избегайте px** для высокоуровневого UI (кроме случаев, когда API уже возвращает px или для Canvas/кастомного рисования)
3. **Используйте sp** для размера текста (не dp!)
4. **Кратность 4dp или 8dp** для согласованности

### Частые Ошибки

```kotlin
// ❌ ПЛОХО: Жёсткое значение в px
textView.layoutParams.width = 100  // Это px!

// ✅ ХОРОШО: Конвертация dp в px с учётом плотности
val widthPx = (100 * density).toInt()
textView.layoutParams.width = widthPx
```

---

## Answer (EN)

### Definition

**dp** (density-independent pixels) is an Android measurement unit for creating adaptive interfaces that look consistent across devices with different screen densities.

### Why Dp Exists

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
    android:layout_height="48dp"   <!-- ✅ Commonly recommended minimum touch target height -->
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
                .height(48.dp)  // ✅ Commonly recommended minimum touch target
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

### Converting Dp ↔ Px

**`View` System**:
```kotlin
// dp → px (simplified; in real apps prefer Context-specific resources)
val density = resources.displayMetrics.density
val px = (100 * density).toInt()  // ✅ Correct for the given resources

// Extension (demonstration; uses system resources and ignores current configuration)
val Int.dpToPx: Int
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
// Spacing (commonly used values)
8.dp   // Small
16.dp  // Standard (most common)
24.dp  // Large

// Touch targets
48.dp  // Historically recommended minimum touch target size on Android

// Icons
24.dp  // Standard icon size
```

### Dp Vs Px Vs Sp

| Use Case               | Unit   | Example             |
|------------------------|--------|---------------------|
| Layout sizes           | dp     | `width = 100.dp`    |
| Padding/Margins        | dp     | `padding(16.dp)`    |
| Text size              | **sp** | `fontSize = 16.sp`  |
| `Canvas` / low-level UI  | px     | Drawing operations  |

### Best Practices

1. **Prefer dp** for layout dimensions
2. **Avoid px** for high-level UI (except when APIs return px or for Canvas/custom drawing)
3. **Use sp** for text sizes (not dp!)
4. **Use multiples of 4dp or 8dp** for consistency

### Common Mistakes

```kotlin
// ❌ BAD: Hard-coded px
textView.layoutParams.width = 100  // This is px!

// ✅ GOOD: Convert dp to px using density
val widthPx = (100 * density).toInt()
textView.layoutParams.width = widthPx
```

---

## Follow-ups

- Когда использовать sp вместо dp (и в Compose, и во `View`-системе)?
- Как связаны density buckets и папки ресурсов `drawable-*`/`mipmap-*`?
- Какие проблемы возникают при смешении px и dp?

## References

- https://developer.android.com/training/multiscreen/screendensities
- https://developer.android.com/guide/topics/resources/multiscreen-density
- https://m3.material.io/foundations/layout/applying-layout/spacing

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Same Difficulty (Easy)
- [[q-what-are-px-dp-sp--android--easy]]

### Next Steps (Medium)
- [[q-what-are-the-most-important-components-of-compose--android--medium]]
