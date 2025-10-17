---
id: 20251016-161632
title: "When Is It Better To Use Png And Webp And When Svg / When Is It Better To Use Png и Webp и When Svg"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [image-formats, ui, difficulty/easy]
---
# Когда лучше использовать png и webp, а когда svg?

**English**: When is it better to use png and webp, and when svg?

## Answer (EN)
Choosing the right image format is important for app performance, file size, and visual quality. Here's when to use each format:

### PNG (Portable Network Graphics)

**Best for:**
- Simple images with transparency and high detail
- Screenshots and UI mockups
- Images requiring lossless compression
- Small icons with transparency

**Advantages:**
- Lossless compression (no quality loss)
- Excellent transparency support (alpha channel)
- Wide compatibility across all Android versions
- Good for images with sharp edges and text

**Disadvantages:**
- Larger file sizes compared to WebP
- Not ideal for photographs
- No animation support

**Use cases:**

```xml
<!-- PNG for app launcher icon with transparency -->
<ImageView
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:src="@drawable/app_logo"
    android:contentDescription="App logo" />
```

**File structure:**
```
res/
  drawable-mdpi/
    icon.png (48x48)
  drawable-hdpi/
    icon.png (72x72)
  drawable-xhdpi/
    icon.png (96x96)
  drawable-xxhdpi/
    icon.png (144x144)
```

### WebP

**Best for:**
- Photographs and complex images
- Images requiring compression with minimal quality loss
- Reducing app size
- Both lossy and lossless compression needs

**Advantages:**
- 25-35% smaller file size than PNG (lossless)
- 25-34% smaller than JPEG (lossy)
- Supports transparency (like PNG)
- Supports animation (like GIF)
- Excellent compression algorithms

**Disadvantages:**
- Requires Android 4.0+ (API 14+) for basic support
- Full feature support from Android 4.3+ (API 18+)
- Slightly more CPU intensive to decode

**Use cases:**

```xml
<!-- WebP for photo backgrounds -->
<ImageView
    android:layout_width="match_parent"
    android:layout_height="200dp"
    android:src="@drawable/background_photo"
    android:scaleType="centerCrop" />
```

**Conversion command:**
```bash

# Convert PNG to WebP (lossless)
cwebp -lossless input.png -o output.webp

# Convert PNG to WebP (lossy with quality 80)
cwebp -q 80 input.png -o output.webp
```

**Gradle configuration:**
```kotlin
// build.gradle
android {
    defaultConfig {
        // Enable WebP conversion
        vectorDrawables.useSupportLibrary = true
    }

    buildTypes {
        release {
            // Automatically convert PNG to WebP
            crunchPngs = false
        }
    }
}
```

### SVG / Vector Drawables (VectorDrawable)

**Best for:**
- Vector images requiring scaling without quality loss
- Icons and simple graphics
- UI elements that need to scale to different screen sizes
- Images with solid colors and simple shapes

**Advantages:**
- Scalable to any size without quality loss
- Single file for all screen densities
- Smaller file size for simple graphics
- Can be animated with AnimatedVectorDrawable
- Can be tinted programmatically

**Disadvantages:**
- Not suitable for complex images or photographs
- Higher CPU usage for complex paths
- Rendering performance can be slower for very complex vectors

**Use cases:**

```xml
<!-- res/drawable/ic_home.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M10,20v-6h4v6h5v-8h3L12,3 2,12h3v8z"/>
</vector>

<!-- Using in layout -->
<ImageView
    android:layout_width="24dp"
    android:layout_height="24dp"
    android:src="@drawable/ic_home"
    app:tint="@color/primary" />
```

**Programmatic tinting:**

```kotlin
// Tint vector drawable
val drawable = AppCompatResources.getDrawable(context, R.drawable.ic_home)
DrawableCompat.setTint(drawable!!, ContextCompat.getColor(context, R.color.primary))
imageView.setImageDrawable(drawable)
```

**Animated vector drawable:**

```xml
<!-- res/drawable/animated_check.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_check">
    <target
        android:name="check_path"
        android:animation="@animator/check_animation" />
</animated-vector>
```

### Comparison Table

| Feature | PNG | WebP | SVG/Vector |
|---------|-----|------|------------|
| **File Size** | Large | Small | Very Small (simple) |
| **Scalability** | No | No | Yes |
| **Transparency** | Yes | Yes | Yes |
| **Animation** | No | Yes | Yes (AnimatedVectorDrawable) |
| **Compression** | Lossless | Both | N/A |
| **Best For** | UI assets, logos | Photos, complex images | Icons, simple graphics |
| **CPU Usage** | Low | Medium | Medium-High (complex) |
| **Android Support** | All versions | 4.0+ | 5.0+ (full support) |

### Decision Flow Chart

```
Is it a photograph or complex raster image?
 Yes → Use WebP (lossy compression)
 No → Is it a simple icon or geometric shape?
     Yes → Use Vector Drawable (SVG)
     No → Does it need transparency?
         Yes → Use WebP (lossless) or PNG
         No → Use WebP (lossy)
```

### Best Practices

#### 1. Use Vector Drawables for Icons

```kotlin
// Enable vector drawable support in older Android versions
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true
    }
}
```

```xml
<!-- In layout, use app:srcCompat for vectors -->
<ImageView
    android:layout_width="24dp"
    android:layout_height="24dp"
    app:srcCompat="@drawable/ic_star"
    app:tint="@color/yellow" />
```

#### 2. Use WebP for Photos and Backgrounds

```xml
<ImageView
    android:layout_width="match_parent"
    android:layout_height="300dp"
    android:src="@drawable/hero_image"
    android:scaleType="centerCrop" />
```

#### 3. Optimize Image Loading

```kotlin
// Use Glide or Coil for efficient image loading
Glide.with(context)
    .load(R.drawable.large_webp_image)
    .placeholder(R.drawable.placeholder)
    .into(imageView)
```

#### 4. Convert PNG to WebP for Release

```bash

# Find and convert all PNGs to WebP
find ./res -name "*.png" -exec cwebp -q 90 {} -o {}.webp \;
```

### Summary

- **PNG**: Simple images with transparency, UI assets
- **WebP**: Photographs, complex images, backgrounds (best compression)
- **SVG/Vector**: Icons, logos, simple scalable graphics

For modern Android apps, the recommended approach is:
1. **Vector Drawables** for all icons and simple graphics
2. **WebP** for all photographic content and complex images
3. **PNG** only when WebP is not supported or for legacy compatibility

## Ответ (RU)
Выбор правильного формата изображения важен для производительности приложения, размера файла и визуального качества. Вот когда использовать каждый формат:

### PNG (Portable Network Graphics)

**Лучше всего для:**
- Простых изображений с прозрачностью и высокой детализацией
- Скриншотов и UI-макетов
- Изображений, требующих сжатия без потерь
- Небольших иконок с прозрачностью

**Преимущества:**
- Сжатие без потерь (без потери качества)
- Отличная поддержка прозрачности (альфа-канал)
- Широкая совместимость со всеми версиями Android
- Хорошо для изображений с четкими краями и текстом

**Недостатки:**
- Большие размеры файлов по сравнению с WebP
- Не идеально для фотографий
- Нет поддержки анимации

### WebP

**Лучше всего для:**
- Фотографий и сложных изображений
- Изображений, требующих сжатия с минимальной потерей качества
- Уменьшения размера приложения
- Потребностей в сжатии с потерями и без потерь

**Преимущества:**
- На 25-35% меньше размер файла, чем PNG (без потерь)
- На 25-34% меньше, чем JPEG (с потерями)
- Поддерживает прозрачность (как PNG)
- Поддерживает анимацию (как GIF)
- Отличные алгоритмы сжатия

**Недостатки:**
- Требуется Android 4.0+ (API 14+) для базовой поддержки
- Полная функциональность от Android 4.3+ (API 18+)
- Немного более интенсивна для CPU при декодировании

**Конфигурация Gradle:**
```kotlin
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true
    }

    buildTypes {
        release {
            crunchPngs = false
        }
    }
}
```

### SVG / Vector Drawables (VectorDrawable)

**Лучше всего для:**
- Векторных изображений, требующих масштабирования без потери качества
- Иконок и простой графики
- UI-элементов, которые должны масштабироваться для разных размеров экрана
- Изображений со сплошными цветами и простыми формами

**Преимущества:**
- Масштабируется до любого размера без потери качества
- Один файл для всех плотностей экрана
- Меньший размер файла для простой графики
- Может быть анимирован с помощью AnimatedVectorDrawable
- Может быть окрашен программно

**Недостатки:**
- Не подходит для сложных изображений или фотографий
- Более высокое использование CPU для сложных путей
- Производительность рендеринга может быть медленнее для очень сложных векторов

**Программное окрашивание:**
```kotlin
val drawable = AppCompatResources.getDrawable(context, R.drawable.ic_home)
DrawableCompat.setTint(drawable!!, ContextCompat.getColor(context, R.color.primary))
imageView.setImageDrawable(drawable)
```

### Таблица сравнения

| Функция | PNG | WebP | SVG/Vector |
|---------|-----|------|------------|
| **Размер файла** | Большой | Малый | Очень малый (простой) |
| **Масштабируемость** | Нет | Нет | Да |
| **Прозрачность** | Да | Да | Да |
| **Анимация** | Нет | Да | Да (AnimatedVectorDrawable) |
| **Сжатие** | Без потерь | Оба варианта | Н/Д |
| **Лучше всего для** | UI-ресурсы, логотипы | Фото, сложные изображения | Иконки, простая графика |
| **Использование CPU** | Низкое | Среднее | Среднее-Высокое (сложные) |
| **Поддержка Android** | Все версии | 4.0+ | 5.0+ (полная поддержка) |

### Блок-схема принятия решения

```
Это фотография или сложное растровое изображение?
 Да → Используйте WebP (сжатие с потерями)
 Нет → Это простая иконка или геометрическая фигура?
     Да → Используйте Vector Drawable (SVG)
     Нет → Нужна прозрачность?
         Да → Используйте WebP (без потерь) или PNG
         Нет → Используйте WebP (с потерями)
```

### Лучшие практики

#### 1. Использовать Vector Drawables для иконок

```kotlin
android {
    defaultConfig {
        vectorDrawables.useSupportLibrary = true
    }
}
```

#### 2. Использовать WebP для фотографий и фонов

```xml
<ImageView
    android:layout_width="match_parent"
    android:layout_height="300dp"
    android:src="@drawable/hero_image"
    android:scaleType="centerCrop" />
```

#### 3. Оптимизировать загрузку изображений

```kotlin
Glide.with(context)
    .load(R.drawable.large_webp_image)
    .placeholder(R.drawable.placeholder)
    .into(imageView)
```

### Резюме

- **PNG**: Простые изображения с прозрачностью, UI-ресурсы
- **WebP**: Фотографии, сложные изображения, фоны (лучшее сжатие)
- **SVG/Vector**: Иконки, логотипы, простая масштабируемая графика

Для современных Android-приложений рекомендуемый подход:
1. **Vector Drawables** для всех иконок и простой графики
2. **WebP** для всего фотографического контента и сложных изображений
3. **PNG** только когда WebP не поддерживается или для совместимости с устаревшими версиями

