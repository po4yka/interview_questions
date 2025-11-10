---
id: android-299
title: WebP Image Format Android / Формат изображений WebP в Android
aliases:
- WebP Image Format
- Формат WebP
topic: android
subtopics:
- files-media
- performance-memory
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-what-layout-allows-overlapping-objects--android--easy
- q-android-app-bundles--android--easy
created: 2024-10-15
updated: 2025-11-10
tags:
- android/files-media
- android/performance-memory
- difficulty/easy
- images
- optimization
- webp
---

# Вопрос (RU)
> Формат изображений WebP в Android

# Question (EN)
> WebP Image Format Android

---

## Ответ (RU)
**WebP** — это современный формат изображений, разработанный Google, который обеспечивает лучшее сжатие по сравнению с PNG и JPEG при сохранении высокого визуального качества. WebP является рекомендуемым форматом для оптимизации изображений в Android-приложениях.

### Преимущества WebP

#### 1. Размер файла

WebP обычно обеспечивает меньший размер файла по сравнению с традиционными форматами:

| Формат | Размер | Относительно JPEG |
|--------|--------|--------------------|
| JPEG | 100 KB | Базовая линия |
| PNG | 120 KB | ~20% больше |
| WebP (lossy) | 65-75 KB | ~25-35% меньше |
| WebP (lossless) | 80-90 KB | ~10-20% меньше |

(Цифры примерные, зависят от содержимого изображения и настроек.)

#### 2. Качество

WebP поддерживает как lossy (с потерями), так и lossless (без потерь) сжатие:

```kotlin
// Lossy compression (для фотографий)
// - Меньший размер файла
// - Подходит для фотографий, где небольшая потеря качества незаметна
// - Аналог JPEG

// Lossless compression (для графики)
// - Без потери качества
// - Подходит для логотипов, иконок, диаграмм
// - Аналог PNG
```

#### 3. Прозрачность

WebP поддерживает альфа-канал (прозрачность), как PNG:

```kotlin
// PNG с прозрачностью: 150 KB
// WebP с прозрачностью: 90-100 KB (экономия ~30-40%)
```

#### 4. Анимация

WebP поддерживает анимацию (animated WebP), как GIF, но обычно с гораздо меньшим размером:

```kotlin
// GIF анимация: 2 MB
// WebP анимация: 500 KB - 1 MB (экономия ~50-75%)
```

### Поддержка в Android

| Android версия | Поддержка WebP |
|----------------|----------------|
| Android 4.0+ (API 14) | WebP lossy (без потерь поддержки с ограничениями) |
| Android 4.3+ (API 18) | WebP lossless + transparency в платформенном декодере |
| Android 9.0+ (API 28) | Animated WebP |

(Библиотеки вроде Glide/Coil могут обеспечивать более широкую поддержку за счет собственных декодеров.)

### Конвертация изображений в WebP

#### Способ 1: Android Studio (встроенная конвертация)

```
1. Правый клик на изображение в res/drawable
2. Выбрать "Convert to WebP..."
3. Настроить параметры:
   - Lossy/Lossless
   - Quality (0-100)
   - Skip images with transparency (опционально)
4. Нажать "OK"
```

Android Studio автоматически:
- Конвертирует изображение в WebP
- (Опционально) сохраняет резервную копию оригинала

#### Способ 2: Командная строка (cwebp)

```bash
# Установка cwebp (macOS)
brew install webp

# Конвертация JPEG/PNG в WebP
cwebp input.jpg -o output.webp

# Lossy compression с качеством 80%
cwebp -q 80 input.jpg -o output.webp

# Lossless compression
cwebp -lossless input.png -o output.webp

# Конвертация с прозрачностью
cwebp -q 80 -alpha_q 100 input.png -o output.webp

# Batch конвертация всех изображений
for file in *.jpg; do
    cwebp -q 80 "$file" -o "${file%.jpg}.webp"
done
```

#### Способ 3: Online конвертеры

- https://cloudconvert.com/webp-converter
- https://squoosh.app/
- https://convertio.co/webp-converter/

### Использование WebP в Android-приложении

#### 1. Обычное использование в XML

```xml
<!-- res/layout/activity_main.xml -->
<ImageView
    android:id="@+id/imageView"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:src="@drawable/photo"  <!-- photo.webp -->
    android:contentDescription="@string/photo_description" />
```

#### 2. Программная загрузка

```kotlin
// Из ресурсов
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.photo)
imageView.setImageBitmap(bitmap)

// Из assets
assets.open("photo.webp").use { inputStream ->
    val bitmap = BitmapFactory.decodeStream(inputStream)
    imageView.setImageBitmap(bitmap)
}

// Из файла
val file = File(filesDir, "photo.webp")
val bitmapFromFile = BitmapFactory.decodeFile(file.absolutePath)
imageView.setImageBitmap(bitmapFromFile)
```

#### 3. Загрузка с сервера через Glide

```kotlin
// build.gradle
dependencies {
    implementation "com.github.bumptech.glide:glide:4.16.0"
}

// Код
Glide.with(context)
    .load("https://example.com/image.webp")
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .into(imageView)
```

#### 4. Загрузка с сервера через Coil

```kotlin
// build.gradle
dependencies {
    implementation("io.coil-kt:coil:2.5.0")
}

// Код
imageView.load("https://example.com/image.webp") {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    error(R.drawable.error)
}
```

### Пример: Оптимизация приложения с WebP

#### До оптимизации

```
app/
  src/main/res/
    drawable/
      photo1.jpg  (500 KB)
      photo2.jpg  (450 KB)
      photo3.png  (600 KB)
      logo.png    (80 KB)
      icon.png    (50 KB)

Общий размер: 1680 KB
APK размер: +1680 KB
```

#### После конвертации в WebP

```
app/
  src/main/res/
    drawable/
      photo1.webp  (325 KB) - экономия ~35%
      photo2.webp  (290 KB) - экономия ~36%
      photo3.webp  (400 KB) - экономия ~33%
      logo.webp    (45 KB)  - экономия ~44%
      icon.webp    (28 KB)  - экономия ~44%

Общий размер: 1088 KB
APK размер: +1088 KB
Экономия: 592 KB (~35%)
```

### Сравнение форматов для разных типов изображений

#### 1. Фотографии (lossy)

```
Оригинал (JPEG): 800x600, 150 KB
WebP (q=80):     800x600, 95 KB  (экономия ~37%)
WebP (q=90):     800x600, 110 KB (экономия ~27%)
```

#### 2. Логотипы и иконки (lossless)

```
Оригинал (PNG):  512x512, 120 KB
WebP (lossless): 512x512, 70 KB  (экономия ~42%)
```

#### 3. Прозрачные изображения

```
Оригинал (PNG):  1024x1024 с прозрачностью, 250 KB
WebP (lossless): 1024x1024 с прозрачностью, 140 KB (экономия ~44%)
```

#### 4. Анимация

```
Оригинал (GIF):  320x240, 30 frames, 1.5 MB
WebP (animated): 320x240, 30 frames, 400 KB (экономия ~73%)
```

### Best Practices

#### 1. Выбор типа сжатия

```kotlin
// Для фотографий → lossy (q=75-85)
cwebp -q 80 photo.jpg -o photo.webp

// Для логотипов/иконок → lossless
cwebp -lossless logo.png -o logo.webp

// Для UI-элементов с прозрачностью → lossless
cwebp -lossless -alpha_q 100 button.png -o button.webp
```

#### 2. Настройка качества

```bash
# Низкое качество (q=60-70): для превью, thumbnail
cwebp -q 65 thumbnail.jpg -o thumbnail.webp

# Среднее качество (q=75-85): для обычных фотографий
cwebp -q 80 photo.jpg -o photo.webp

# Высокое качество (q=90-95): для важных изображений
cwebp -q 90 hero_image.jpg -o hero_image.webp

# Максимальное качество (lossless): для логотипов
cwebp -lossless logo.png -o logo.webp
```

#### 3. Fallback для старых версий Android

Если minSdk < 14 (очень старые устройства), можно хранить альтернативы в PNG/JPEG и использовать совместимые библиотеки/логики выбора ресурсов. В современных проектах (minSdk ≥ 21) отдельный fallback для WebP обычно не требуется.

```kotlin
// Стандартный выбор ресурсов по квалификаторам
imageView.setImageResource(R.drawable.image)
```

### Мониторинг размера APK

#### Анализ APK в Android Studio

```
Build → Analyze APK → выбрать APK

Смотрим:
- res/drawable: размер всех изображений
- сравниваем до и после конвертации
```

#### Gradle-отчет

```gradle
// build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
        }
    }
}
```

### Пример: динамическая загрузка WebP

```kotlin
class ImageLoader {
    suspend fun loadImage(url: String): Bitmap? {
        return withContext(Dispatchers.IO) {
            try {
                val connection = URL(url).openConnection()
                connection.connect()
                connection.getInputStream().use { input ->
                    BitmapFactory.decodeStream(input)
                }
            } catch (e: Exception) {
                Log.e("ImageLoader", "Failed to load WebP image", e)
                null
            }
        }
    }
}

// Использование
lifecycleScope.launch {
    val bitmap = ImageLoader().loadImage("https://example.com/image.webp")
    bitmap?.let {
        imageView.setImageBitmap(it)
    }
}
```

### Альтернативы WebP

| Формат | Размер | Поддержка | Когда использовать |
|--------|--------|-----------|-------------------|
| JPEG | Средний | Везде | Для совместимости и простых фотографий |
| PNG | Большой | Везде | Когда нужна строгая без потерь графика |
| WebP | Маленький | Android 4.0+ (поддержка зависит от типа WebP и API) | Рекомендуется для большинства кейсов |
| AVIF | Очень маленький | Android 12+ (статичные изображения) | Перспективный формат, поддержка растет |
| HEIF | Маленький | Android 9+ | Альтернатива для фотографий |

### Вывод

WebP — это оптимальный выбор для Android-приложений благодаря:

1. Размеру: обычно на 25-45% меньше по сравнению с JPEG/PNG
2. Качеству: поддержка lossy и lossless
3. Функциональности: прозрачность + анимация (animated WebP)
4. Поддержке: базовая поддержка с Android 4.0+ (детали зависят от типа WebP)
5. Простоте: встроенные инструменты конвертации и поддержка в популярных библиотеке изображений

**Рекомендации:**
- Конвертируйте JPEG/PNG в WebP там, где это визуально приемлемо
- Используйте lossy (q≈80) для фотографий
- Используйте lossless для логотипов и иконок
- Проверяйте качество визуально перед релизом
- Мониторьте размер APK до и после конвертации

## Answer (EN)

WebP is a modern image format developed by Google that provides better compression than PNG and JPEG while maintaining high visual quality. It is a recommended default for image optimization in Android apps.

### Advantages of WebP

#### 1. File size

WebP usually gives smaller file sizes compared to traditional formats:

| Format | Size | Relative to JPEG |
|--------|------|------------------|
| JPEG | 100 KB | Baseline |
| PNG | 120 KB | ~20% larger |
| WebP (lossy) | 65-75 KB | ~25-35% smaller |
| WebP (lossless) | 80-90 KB | ~10-20% smaller |

(Values are approximate and depend on content and settings.)

#### 2. Quality

WebP supports both lossy and lossless compression:

```kotlin
// Lossy compression (for photos)
// - Smaller file size
// - Good for photos where slight loss is acceptable
// - Similar to JPEG

// Lossless compression (for graphics)
// - No quality loss
// - Good for logos, icons, diagrams
// - Similar to PNG
```

#### 3. Transparency

WebP supports alpha channel (transparency), like PNG:

```kotlin
// PNG with transparency: 150 KB
// WebP with transparency: 90-100 KB (~30-40% savings)
```

#### 4. Animation

WebP supports animated images (animated WebP), similar to GIF but usually with much smaller size:

```kotlin
// GIF animation: 2 MB
// WebP animation: 500 KB - 1 MB (~50-75% savings)
```

### Support in Android

| Android version | WebP support |
|-----------------|--------------|
| Android 4.0+ (API 14) | WebP lossy (limited lossless support) |
| Android 4.3+ (API 18) | WebP lossless + transparency in platform decoder |
| Android 9.0+ (API 28) | Animated WebP |

(Libraries like Glide/Coil may offer broader support via their own decoders.)

### Conversion to WebP

#### Method 1: Android Studio (built-in)

```
1. Right-click on image in res/drawable
2. Select "Convert to WebP..."
3. Configure:
   - Lossy/Lossless
   - Quality (0-100)
   - Skip images with transparency (optional)
4. Click "OK"
```

Android Studio will:
- Convert the image to WebP
- Optionally keep a backup of the original

#### Method 2: Command line (cwebp)

```bash
# Install cwebp (macOS)
brew install webp

# Convert JPEG/PNG to WebP
cwebp input.jpg -o output.webp

# Lossy compression with quality 80
cwebp -q 80 input.jpg -o output.webp

# Lossless compression
cwebp -lossless input.png -o output.webp

# With transparency
cwebp -q 80 -alpha_q 100 input.png -o output.webp

# Batch convert all images
for file in *.jpg; do
    cwebp -q 80 "$file" -o "${file%.jpg}.webp"
done
```

#### Method 3: Online converters

- https://cloudconvert.com/webp-converter
- https://squoosh.app/
- https://convertio.co/webp-converter/

### Using WebP in an Android app

#### 1. XML usage

```xml
<!-- res/layout/activity_main.xml -->
<ImageView
    android:id="@+id/imageView"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:src="@drawable/photo"  <!-- photo.webp in drawable -->
    android:contentDescription="@string/photo_description" />
```

#### 2. Programmatic loading

```kotlin
// From resources
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.photo)
imageView.setImageBitmap(bitmap)

// From assets
assets.open("photo.webp").use { inputStream ->
    val bitmap = BitmapFactory.decodeStream(inputStream)
    imageView.setImageBitmap(bitmap)
}

// From file
val file = File(filesDir, "photo.webp")
val bitmapFromFile = BitmapFactory.decodeFile(file.absolutePath)
imageView.setImageBitmap(bitmapFromFile)
```

#### 3. Loading from server with Glide

```kotlin
// build.gradle
dependencies {
    implementation "com.github.bumptech.glide:glide:4.16.0"
}

Glide.with(context)
    .load("https://example.com/image.webp")
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .into(imageView)
```

#### 4. Loading from server with Coil

```kotlin
// build.gradle
dependencies {
    implementation("io.coil-kt:coil:2.5.0")
}

imageView.load("https://example.com/image.webp") {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    error(R.drawable.error)
}
```

### Example: App optimization with WebP

#### Before

```
app/
  src/main/res/
    drawable/
      photo1.jpg  (500 KB)
      photo2.jpg  (450 KB)
      photo3.png  (600 KB)
      logo.png    (80 KB)
      icon.png    (50 KB)

Total images: 1680 KB
APK size contribution: +1680 KB
```

#### After converting to WebP

```
app/
  src/main/res/
    drawable/
      photo1.webp  (325 KB) ~35% saved
      photo2.webp  (290 KB) ~36% saved
      photo3.webp  (400 KB) ~33% saved
      logo.webp    (45 KB)  ~44% saved
      icon.webp    (28 KB)  ~44% saved

Total images: 1088 KB
APK size contribution: +1088 KB
Saving: 592 KB (~35%)
```

### Format comparison for different image types

#### 1. Photos (lossy)

```
Original (JPEG): 800x600, 150 KB
WebP (q=80):     800x600, 95 KB  (~37% saved)
WebP (q=90):     800x600, 110 KB (~27% saved)
```

#### 2. Logos and icons (lossless)

```
Original (PNG):  512x512, 120 KB
WebP (lossless): 512x512, 70 KB  (~42% saved)
```

#### 3. Transparent images

```
Original (PNG):  1024x1024 with alpha, 250 KB
WebP (lossless): 1024x1024 with alpha, 140 KB (~44% saved)
```

#### 4. Animation

```
Original (GIF):  320x240, 30 frames, 1.5 MB
WebP (animated): 320x240, 30 frames, 400 KB (~73% saved)
```

### Best practices

#### 1. Compression type choice

```bash
# Photos → lossy (q=75-85)
cwebp -q 80 photo.jpg -o photo.webp

# Logos/icons → lossless
cwebp -lossless logo.png -o logo.webp

# UI elements with transparency → lossless
cwebp -lossless -alpha_q 100 button.png -o button.webp
```

#### 2. Quality tuning

```bash
# Low quality (q=60-70): previews, thumbnails
cwebp -q 65 thumbnail.jpg -o thumbnail.webp

# Medium (q=75-85): regular photos
cwebp -q 80 photo.jpg -o photo.webp

# High (q=90-95): critical visuals
cwebp -q 90 hero_image.jpg -o hero_image.webp

# Max (lossless): logos
cwebp -lossless logo.png -o logo.webp
```

#### 3. Fallback for old Android versions

If minSdk < 14 (very old devices), provide PNG/JPEG alternatives and select resources accordingly. For modern projects (minSdk ≥ 21) explicit WebP fallback is usually not needed.

```kotlin
imageView.setImageResource(R.drawable.image)
```

### APK size monitoring

#### Analyze APK in Android Studio

```
Build → Analyze APK → select APK

Check:
- res/drawable: total image size
- compare before vs after conversion
```

#### Gradle config

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
        }
    }
}
```

### Example: dynamic WebP loading

```kotlin
class ImageLoader {
    suspend fun loadImage(url: String): Bitmap? {
        return withContext(Dispatchers.IO) {
            try {
                val connection = URL(url).openConnection()
                connection.connect()
                connection.getInputStream().use { input ->
                    BitmapFactory.decodeStream(input)
                }
            } catch (e: Exception) {
                Log.e("ImageLoader", "Failed to load WebP image", e)
                null
            }
        }
    }
}

lifecycleScope.launch {
    val bitmap = ImageLoader().loadImage("https://example.com/image.webp")
    bitmap?.let { imageView.setImageBitmap(it) }
}
```

### Alternatives to WebP

| Format | Size | Support | When to use |
|--------|------|---------|-------------|
| JPEG | Medium | Everywhere | Simple photos, compatibility |
| PNG | Large | Everywhere | Strict lossless graphics |
| WebP | Small | Android 4.0+ (type/API dependent) | Recommended default in most cases |
| AVIF | Very small | Android 12+ (static) | Future-proof, growing support |
| HEIF | Small | Android 9+ | Photo alternative |

### Summary

WebP is an excellent choice for Android apps because it:

1. Reduces size by about 25–45% vs JPEG/PNG.
2. Offers both lossy and lossless modes.
3. Supports transparency and animation.
4. Has broad Android support (4.0+; details depend on WebP type).
5. Is easy to integrate via Android Studio tools and popular image libraries.

Recommendations:
- Convert JPEG/PNG to WebP where visually acceptable.
- Use lossy (q≈80) for photos.
- Use lossless for logos/icons and important UI.
- Always visually review results.
- Track APK size before/after conversion.

## Follow-ups

- [[q-what-layout-allows-overlapping-objects--android--easy]]
- How would you compare using WebP vs AVIF for modern Android apps in terms of support and tooling?
- When might you still choose PNG or JPEG over WebP in an Android project?
- How does using WebP impact memory usage and decoding performance on low-end devices?
- How would you organize drawables and densities when migrating a large project to WebP?

## References

- [WebP support in Android](https://developer.android.com/studio/write/convert-webp)

## Related Questions

- [[q-what-are-services-for--android--easy]]
- [[q-view-fundamentals--android--easy]]
- [[q-sparsearray-optimization--android--medium]]
