---
id: android-172
title: "How To Display SVG String As A Vector File / Как отобразить SVG строку как векторный файл"
aliases: ["Display SVG String", "Отображение SVG строки"]
topic: android
subtopics: [ui-compose, ui-graphics, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, c-jetpack-compose, c-viewmodel]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/ui-compose, android/ui-graphics, android/ui-views, difficulty/medium, ui]
---

# Вопрос (RU)

Как отобразить SVG-строку в виде векторного изображения в Android?

# Question (EN)

How to display an SVG string as a vector image in Android?

---

## Ответ (RU)

Android не имеет встроенной поддержки SVG, поэтому требуются сторонние библиотеки. Основные подходы:

### 1. AndroidSVG (Рекомендуется Для Простых случаев)

Легковесная библиотека для прямой работы с SVG-строками:

```kotlin
// ✅ Простой и прямой подход
private fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        // ❌ Отсутствие обработки ошибок может привести к краху приложения
        Log.e("SVG", "Parse error", e)
    }
}

// ✅ С контролем размеров
private fun displaySvgWithSize(
    svgString: String,
    imageView: ImageView,
    width: Int,
    height: Int
) {
    val svg = SVG.getFromString(svgString)
    svg.documentWidth = width.toFloat()
    svg.documentHeight = height.toFloat()

    val drawable = PictureDrawable(svg.renderToPicture(width, height))
    imageView.setImageDrawable(drawable)
}
```

### 2. Coil С SVG Декодером (Современный подход)

Интеграция с популярной библиотекой загрузки изображений:

```kotlin
// ✅ Настройка ImageLoader с поддержкой SVG
val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

// ✅ Загрузка SVG из байтов
val request = ImageRequest.Builder(context)
    .data(svgString.toByteArray())
    .target(imageView)
    .build()

imageLoader.enqueue(request)
```

### 3. Jetpack Compose

```kotlin
@Composable
fun SvgImage(svgString: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current

    // ✅ Создание ImageLoader в remember для избежания пересоздания
    val imageLoader = remember {
        ImageLoader.Builder(context)
            .components { add(SvgDecoder.Factory()) }
            .build()
    }

    AsyncImage(
        model = ImageRequest.Builder(context)
            .data(svgString.toByteArray())
            .build(),
        contentDescription = null,
        imageLoader = imageLoader,
        modifier = modifier
    )
}
```

### 4. Пользовательский `Drawable`

Для полного контроля рендеринга:

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private var svg: SVG? = null

    init {
        try {
            svg = SVG.getFromString(svgString)
        } catch (e: SVGParseException) {
            Log.e("SvgDrawable", "Parse error", e)
        }
    }

    override fun draw(canvas: Canvas) {
        svg?.let {
            // ✅ Адаптация к bounds контейнера
            it.documentWidth = bounds.width().toFloat()
            it.documentHeight = bounds.height().toFloat()
            it.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {}
    override fun setColorFilter(colorFilter: ColorFilter?) {}
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

### Сравнение Подходов

| Подход | Преимущества | Недостатки | Использовать когда |
|--------|--------------|------------|-------------------|
| AndroidSVG | Простота, контроль | Ручная настройка | Простые случаи, прямая работа со строками |
| Coil + SVG | Кеширование, современный API | Доп. зависимость | Загрузка из сети, кеширование |
| Custom `Drawable` | Полный контроль | Больше кода | Специфичные требования к рендерингу |
| Compose | Декларативность | Требует Compose | Compose UI |

### Важные Моменты

**Память**:
- Преобразование в `Bitmap` для больших SVG может вызвать OutOfMemoryError
- Используйте PictureDrawable для эффективного рендеринга векторов

**Обработка ошибок**:
- Всегда оборачивайте парсинг в try-catch
- SVG может содержать невалидный XML или неподдерживаемые элементы

**Производительность**:
- Кешируйте результат парсинга при повторном использовании
- Для сетевых SVG используйте библиотеки с встроенным кешированием (Coil, Glide)

**Размеры**:
- SVG может не иметь явных размеров - устанавливайте их программно
- Используйте scaleType для `ImageView` согласно требованиям дизайна

## Answer (EN)

Android has no built-in SVG support, requiring third-party libraries. Main approaches:

### 1. AndroidSVG (Recommended for Simple cases)

Lightweight library for direct SVG string handling:

```kotlin
// ✅ Simple and direct approach
private fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        // ❌ Missing error handling can crash the app
        Log.e("SVG", "Parse error", e)
    }
}

// ✅ With size control
private fun displaySvgWithSize(
    svgString: String,
    imageView: ImageView,
    width: Int,
    height: Int
) {
    val svg = SVG.getFromString(svgString)
    svg.documentWidth = width.toFloat()
    svg.documentHeight = height.toFloat()

    val drawable = PictureDrawable(svg.renderToPicture(width, height))
    imageView.setImageDrawable(drawable)
}
```

### 2. Coil with SVG Decoder (Modern approach)

Integration with popular image loading library:

```kotlin
// ✅ Configure ImageLoader with SVG support
val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

// ✅ Load SVG from bytes
val request = ImageRequest.Builder(context)
    .data(svgString.toByteArray())
    .target(imageView)
    .build()

imageLoader.enqueue(request)
```

### 3. Jetpack Compose

```kotlin
@Composable
fun SvgImage(svgString: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current

    // ✅ Create ImageLoader in remember to avoid recreation
    val imageLoader = remember {
        ImageLoader.Builder(context)
            .components { add(SvgDecoder.Factory()) }
            .build()
    }

    AsyncImage(
        model = ImageRequest.Builder(context)
            .data(svgString.toByteArray())
            .build(),
        contentDescription = null,
        imageLoader = imageLoader,
        modifier = modifier
    )
}
```

### 4. Custom `Drawable`

For full rendering control:

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private var svg: SVG? = null

    init {
        try {
            svg = SVG.getFromString(svgString)
        } catch (e: SVGParseException) {
            Log.e("SvgDrawable", "Parse error", e)
        }
    }

    override fun draw(canvas: Canvas) {
        svg?.let {
            // ✅ Adapt to container bounds
            it.documentWidth = bounds.width().toFloat()
            it.documentHeight = bounds.height().toFloat()
            it.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {}
    override fun setColorFilter(colorFilter: ColorFilter?) {}
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

### Approach Comparison

| Approach | Advantages | Disadvantages | Use when |
|----------|-----------|---------------|----------|
| AndroidSVG | Simplicity, control | Manual setup | Simple cases, direct string handling |
| Coil + SVG | Caching, modern API | Extra dependency | Network loading, caching needed |
| Custom `Drawable` | Full control | More code | Specific rendering requirements |
| Compose | Declarative | Requires Compose | Compose UI |

### Key Considerations

**Memory**:
- Converting large SVGs to `Bitmap` can cause OutOfMemoryError
- Use PictureDrawable for efficient vector rendering

**Error handling**:
- Always wrap parsing in try-catch
- SVG may contain invalid XML or unsupported elements

**Performance**:
- Cache parsing result when reusing
- For network SVGs, use libraries with built-in caching (Coil, Glide)

**Sizing**:
- SVG may lack explicit dimensions - set them programmatically
- Use appropriate `ImageView` scaleType per design requirements

---

## Follow-ups

- How to handle SVG animations in Android?
- What SVG features are not supported by AndroidSVG library?
- How to optimize SVG loading performance for lists/`RecyclerView`?
- How to apply color filters or tinting to programmatically loaded SVGs?
- What are the differences between VectorDrawable and SVG in Android?

## References

- [[c-jetpack-compose]]
- [[c-custom-views]]
- [[c-viewmodel]]
- AndroidSVG documentation
- Coil SVG decoder implementation

## Related Questions

### Prerequisites
- [[c-custom-views]] - Understanding Android drawables and custom views
- [[c-jetpack-compose]] - Jetpack Compose basics

### Related
- How to load images efficiently in `RecyclerView`
- Vector drawables vs raster images in Android

### Advanced
- Custom drawable implementation patterns
- Image caching strategies in Android
