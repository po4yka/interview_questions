---
id: android-241
title: When to Use PNG, WebP, or SVG / Когда использовать PNG, WebP или SVG
aliases: [Image Formats Android, PNG vs WebP vs SVG, Форматы изображений Android]

# Classification
topic: android
subtopics: [gradle, performance-rendering, ui-graphics]
question_kind: android
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-compose-ui-testing-advanced--android--hard, q-dagger-build-time-optimization--android--medium, q-dagger-purpose--android--easy]

# Timestamps
created: 2025-10-15
updated: 2025-10-29

# Tags (EN only; no leading #)
tags: [android/gradle, android/performance-rendering, android/ui-graphics, difficulty/easy, image-formats, ui]

---

# Вопрос (RU)
> Когда лучше использовать PNG и WebP, а когда SVG?

# Question (EN)
> When is it better to use PNG, WebP, and when SVG?

---

## Ответ (RU)

Выбор формата изображения влияет на производительность приложения, размер APK и визуальное качество. Правильный выбор зависит от типа контента.

### Когда Использовать Vector Drawables (SVG)

**Лучший выбор для:**
- Иконки и UI-элементы
- Простая графика с геометрическими формами
- Элементы, требующие масштабирования

**Преимущества:**
- Масштабируется без потери качества
- Один файл для всех плотностей экрана
- Малый размер для простой графики
- Программная раскраска через tint

**Пример:**
```xml
<!-- res/drawable/ic_home.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M10,20v-6h4v6h5v-8h3L12,3 2,12h3v8z"/> <!-- ✅ Простые пути -->
</vector>

<!-- Использование с динамической раскраской -->
<ImageView
    android:src="@drawable/ic_home"
    app:tint="@color/primary" /> <!-- ✅ Раскраска без новых файлов -->
```

**Ограничения:**
- Не подходит для фотографий или сложной графики
- Сложные векторы нагружают CPU при рендеринге

### Когда Использовать WebP

**Лучший выбор для:**
- Фотографии и сложные изображения
- Фоны и декоративная графика
- Уменьшение размера APK

**Преимущества:**
- На 25-35% меньше PNG при том же качестве
- Поддержка прозрачности и анимации
- Lossy и lossless сжатие

**Пример:**
```xml
<!-- WebP для фона -->
<ImageView
    android:src="@drawable/background_photo" <!-- ✅ .webp формат -->
    android:scaleType="centerCrop" />
```

**Конвертация:**
```bash
# PNG → WebP (lossy, качество 80)
cwebp -q 80 input.png -o output.webp
```

**Ограничения:**
- Требуется Android 4.0+ (базовая поддержка)
- Немного больше нагрузка на CPU при декодировании

### Когда Использовать PNG

**Лучший выбор для:**
- Легаси-совместимость
- Изображения с прозрачностью, где WebP не подходит
- Скриншоты и UI-макеты

**Преимущества:**
- Сжатие без потерь
- Полная поддержка на всех версиях Android
- Отличная прозрачность (альфа-канал)

**Недостатки:**
- Больший размер по сравнению с WebP
- Требует разных файлов для разных плотностей

```
res/drawable-mdpi/icon.png    <!-- ❌ Много файлов -->
res/drawable-hdpi/icon.png
res/drawable-xhdpi/icon.png
```

### Сравнение Форматов

| Критерий | Vector | WebP | PNG |
|----------|--------|------|-----|
| **Размер** | Малый | Средний | Большой |
| **Масштабируемость** | ✅ Да | ❌ Нет | ❌ Нет |
| **Фото** | ❌ Нет | ✅ Да | ⚠️ Да (большой размер) |
| **Иконки** | ✅ Да | ⚠️ Да (больше) | ⚠️ Да (больше) |
| **Прозрачность** | ✅ Да | ✅ Да | ✅ Да |
| **Раскраска** | ✅ tint | ❌ Нет | ❌ Нет |

### Рекомендации

**Современный Android-проект:**
1. **Vector Drawables** — все иконки и UI-элементы
2. **WebP** — фотографии, сложная графика, фоны
3. **PNG** — только для легаси-совместимости

**Gradle конфигурация:**
```kotlin
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true // ✅ Поддержка векторов
    }
    buildTypes {
        release {
            crunchPngs = false // ✅ Отключить PNG оптимизацию, использовать WebP
        }
    }
}
```

## Answer (EN)

Image format choice affects app performance, APK size, and visual quality. The right format depends on content type.

### When to Use Vector Drawables (SVG)

**Best for:**
- Icons and UI elements
- Simple graphics with geometric shapes
- Scalable elements

**Advantages:**
- Scales without quality loss
- Single file for all screen densities
- Small size for simple graphics
- Programmatic tinting via tint attribute

**Example:**
```xml
<!-- res/drawable/ic_home.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M10,20v-6h4v6h5v-8h3L12,3 2,12h3v8z"/> <!-- ✅ Simple paths -->
</vector>

<!-- Usage with dynamic tinting -->
<ImageView
    android:src="@drawable/ic_home"
    app:tint="@color/primary" /> <!-- ✅ Tint without new files -->
```

**Limitations:**
- Not suitable for photos or complex graphics
- Complex vectors increase CPU rendering load

### When to Use WebP

**Best for:**
- Photographs and complex images
- Backgrounds and decorative graphics
- Reducing APK size

**Advantages:**
- 25-35% smaller than PNG at same quality
- Supports transparency and animation
- Both lossy and lossless compression

**Example:**
```xml
<!-- WebP for background -->
<ImageView
    android:src="@drawable/background_photo" <!-- ✅ .webp format -->
    android:scaleType="centerCrop" />
```

**Conversion:**
```bash
# PNG → WebP (lossy, quality 80)
cwebp -q 80 input.png -o output.webp
```

**Limitations:**
- Requires Android 4.0+ (basic support)
- Slightly higher CPU load for decoding

### When to Use PNG

**Best for:**
- Legacy compatibility
- Transparency where WebP doesn't fit
- Screenshots and UI mockups

**Advantages:**
- Lossless compression
- Full support on all Android versions
- Excellent transparency (alpha channel)

**Disadvantages:**
- Larger size compared to WebP
- Requires separate files for different densities

```
res/drawable-mdpi/icon.png    <!-- ❌ Many files -->
res/drawable-hdpi/icon.png
res/drawable-xhdpi/icon.png
```

### Format Comparison

| Criteria | Vector | WebP | PNG |
|----------|--------|------|-----|
| **Size** | Small | Medium | Large |
| **Scalability** | ✅ Yes | ❌ No | ❌ No |
| **Photos** | ❌ No | ✅ Yes | ⚠️ Yes (large) |
| **Icons** | ✅ Yes | ⚠️ Yes (larger) | ⚠️ Yes (larger) |
| **Transparency** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Tinting** | ✅ tint | ❌ No | ❌ No |

### Recommendations

**Modern Android project:**
1. **Vector Drawables** — all icons and UI elements
2. **WebP** — photos, complex graphics, backgrounds
3. **PNG** — legacy compatibility only

**Gradle configuration:**
```kotlin
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true // ✅ Enable vector support
    }
    buildTypes {
        release {
            crunchPngs = false // ✅ Disable PNG optimization, use WebP
        }
    }
}
```

---

## Follow-ups

- How to convert existing PNG assets to WebP in Android Studio?
- What's the performance impact of complex vector drawables on older devices?
- Can WebP images be used for adaptive icons?
- How to implement runtime tinting for bitmap drawables (PNG/WebP)?
- What are best practices for managing multiple drawable densities vs single vector?

## References

- 
- [[c-performance-optimization]]
- https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources
- https://developer.android.com/develop/ui/views/graphics/drawables
- https://developers.google.com/speed/webp

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-purpose--android--easy]]

### Related (Same Level)
- [[q-compose-ui-testing-advanced--android--hard]]

### Advanced (Harder)
- [[q-dagger-build-time-optimization--android--medium]]
