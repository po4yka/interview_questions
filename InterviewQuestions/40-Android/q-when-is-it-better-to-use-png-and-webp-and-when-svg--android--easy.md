---
id: android-241
title: When to Use PNG, WebP, or SVG / Когда использовать PNG, WebP или SVG
aliases: [Image Formats Android, PNG vs WebP vs SVG, Форматы изображений Android]

# Classification
topic: android
subtopics: [performance-rendering, ui-graphics]
question_kind: android
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: ["https://developer.android.com/develop/ui/views/graphics/drawables"]

# Workflow & relations
status: draft
moc: moc-android
related: [q-compose-ui-testing-advanced--android--hard, q-dagger-build-time-optimization--android--medium, q-dagger-purpose--android--easy]

# Timestamps
created: 2025-10-15
updated: 2025-11-10

# Tags (EN only; no leading #)
tags: [android/performance-rendering, android/ui-graphics, difficulty/easy, image-formats, ui]
---

# Вопрос (RU)
> Когда лучше использовать PNG и WebP, а когда SVG?

# Question (EN)
> When is it better to use PNG, WebP, and when SVG?

---

## Ответ (RU)

Выбор формата изображения влияет на производительность приложения, размер APK и визуальное качество. Правильный выбор зависит от типа контента. На Android обычно используют:
- растровые форматы (PNG, WebP)
- векторные ресурсы (VectorDrawable), которые часто импортируются из SVG.

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
- Не подходит для фотографий или очень сложной/детальной графики
- Сложные векторы нагружают CPU при рендеринге, особенно на старых устройствах

### Когда Использовать WebP

**Лучший выбор для:**
- Фотографии и сложные изображения
- Фоны и декоративная графика
- Уменьшение размера APK / AAB

**Преимущества:**
- Обычно на 25-35% меньше PNG при сопоставимом визуальном качестве
- Поддержка прозрачности (включая lossless) и анимации (на современных версиях Android)
- Поддерживает lossy и lossless сжатие

**Пример:**
```xml
<!-- WebP для фона -->
<ImageView
    android:src="@drawable/background_photo" <!-- ✅ файл в формате .webp -->
    android:scaleType="centerCrop" />
```

**Конвертация:**
```bash
# PNG → WebP (lossy, качество 80)
cwebp -q 80 input.png -o output.webp
```

**Ограничения:**
- Базовая поддержка WebP есть с Android 4.0; расширенные возможности (альфа-канал для lossy, анимация) полноценно доступны на более новых версиях. В современных проектах с minSdk ≥ 21 ограничения обычно не критичны.
- Немного больше нагрузка на CPU при декодировании по сравнению с простыми PNG, но в большинстве случаев это окупается уменьшением размера.

### Когда Использовать PNG

**Лучший выбор для:**
- Легаси-совместимость с очень старыми устройствами или нестандартными ограничениями
- Случаи, когда по процессу/платформе WebP недоступен
- Скриншоты и UI-макеты, где нужен строгий lossless и не критичен размер

**Преимущества:**
- Сжатие без потерь
- Полная поддержка на всех версиях Android
- Корректная поддержка прозрачности (альфа-канал)

**Недостатки:**
- Обычно больший размер по сравнению с WebP при сопоставимом качестве
- Для растровых иконок требуются разные файлы для разных плотностей

```text
res/drawable-mdpi/icon.png    <!-- ❌ Много файлов для плотностей -->
res/drawable-hdpi/icon.png
res/drawable-xhdpi/icon.png
```

### Сравнение Форматов

| Критерий | Vector | WebP | PNG |
|----------|--------|------|-----|
| **Размер** | Малый для простой графики | Обычно меньше PNG | Обычно больше |
| **Масштабируемость** | ✅ Да (вектор) | ❌ Растровый (нужны подходящие размеры/density) | ❌ Растровый (нужны подходящие размеры/density) |
| **Фото** | ❌ Нет | ✅ Да | ⚠️ Да (но крупные файлы) |
| **Иконки** | ✅ Да | ⚠️ Да (чаще больше, чем вектор) | ⚠️ Да (много density-ресурсов) |
| **Прозрачность** | ✅ Да | ✅ Да (lossless и современные реализации) | ✅ Да |
| **Раскраска** | ✅ tint | ⚠️ Ограничено (через ColorFilter / tint для bitmap) | ⚠️ Ограничено (через ColorFilter / tint для bitmap) |

### Рекомендации

**Современный Android-проект:**
1. **Vector Drawables** — иконки и UI-элементы, где это возможно.
2. **WebP** — фотографии, сложная графика, фоны (особенно при minSdk ≥ 21).
3. **PNG** — только для особых случаев и легаси-совместимости.

**Gradle конфигурация:**
```kotlin
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true // ✅ Поддержка VectorDrawable на старых версиях через AppCompat
    }
    buildTypes {
        release {
            crunchPngs = false // ✅ Отключить PNG crunching aapt'ом; не конвертирует в WebP, но избегает лишней переработки PNG
        }
    }
}
```

## Answer (EN)

Image format choice affects app performance, APK size, and visual quality. The right format depends on content type. On Android you typically use:
- raster formats (PNG, WebP)
- vector resources (VectorDrawable), often imported from SVG.

### When to Use Vector Drawables (SVG)

**Best for:**
- Icons and UI elements
- Simple graphics with geometric shapes
- Elements that must scale across densities

**Advantages:**
- Scales without quality loss
- Single resource for all screen densities
- Very small for simple graphics
- Programmatic tinting via the tint attribute / ImageView tint

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
- Not suitable for photos or very complex/detailed artwork
- Complex vectors can be expensive to render on CPU, especially on older devices

### When to Use WebP

**Best for:**
- Photographs and complex images
- Backgrounds and decorative graphics
- Reducing APK/AAB size

**Advantages:**
- Typically 25-35% smaller than PNG for similar perceived quality
- Supports transparency (including lossless) and animation (on modern Android versions)
- Offers both lossy and lossless compression

**Example:**
```xml
<!-- WebP for background -->
<ImageView
    android:src="@drawable/background_photo" <!-- ✅ file in .webp format -->
    android:scaleType="centerCrop" />
```

**Conversion:**
```bash
# PNG → WebP (lossy, quality 80)
cwebp -q 80 input.png -o output.webp
```

**Limitations:**
- Basic WebP support exists since Android 4.0; advanced features (e.g., lossy with alpha, animated WebP) became fully available only in later versions. For typical modern minSdk (≥ 21), these limitations are usually irrelevant.
- Slightly higher CPU cost for decoding compared to simple PNG, usually offset by smaller transfer/storage size.

### When to Use PNG

**Best for:**
- Legacy compatibility with very old devices or specific environments
- Cases where WebP cannot be used in the pipeline/tooling
- Screenshots and UI mockups where strict lossless quality is required and size is acceptable

**Advantages:**
- Lossless compression
- Fully supported on all Android versions
- Proper alpha transparency support

**Disadvantages:**
- Generally larger file size than WebP for similar quality
- For bitmap icons, requires multiple density-specific files

```text
res/drawable-mdpi/icon.png    <!-- ❌ Many density-specific files -->
res/drawable-hdpi/icon.png
res/drawable-xhdpi/icon.png
```

### Format Comparison

| Criteria | Vector | WebP | PNG |
|----------|--------|------|-----|
| **Size** | Small for simple graphics | Typically smaller than PNG | Typically larger |
| **Scalability** | ✅ Yes (vector) | ❌ Bitmap (needs proper sizes/densities) | ❌ Bitmap (needs proper sizes/densities) |
| **Photos** | ❌ No | ✅ Yes | ⚠️ Yes (large) |
| **Icons** | ✅ Yes | ⚠️ Yes (often larger than vector) | ⚠️ Yes (requires multiple densities) |
| **Transparency** | ✅ Yes | ✅ Yes (lossless and modern support) | ✅ Yes |
| **Tinting** | ✅ Native tint support | ⚠️ Possible via ColorFilter/tint on bitmaps | ⚠️ Possible via ColorFilter/tint on bitmaps |

### Recommendations

**Modern Android project:**
1. **Vector Drawables** — default for icons and UI elements where feasible.
2. **WebP** — for photos, complex graphics, and backgrounds (especially with minSdk ≥ 21).
3. **PNG** — only for special cases and legacy compatibility.

**Gradle configuration:**
```kotlin
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true // ✅ Enable VectorDrawable support on older Android via AppCompat
    }
    buildTypes {
        release {
            crunchPngs = false // ✅ Disable aapt PNG crunching; does NOT auto-convert to WebP, just skips extra PNG processing
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
