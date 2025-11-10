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
updated: 2025-11-10
sources: []
tags: [android, android/ui-compose, android/ui-graphics, android/ui-views, difficulty/medium, ui]

---

# Вопрос (RU)

> Как отобразить SVG-строку в виде векторного изображения в Android?

# Question (EN)

> How to display an SVG string as a vector image in Android?

## Ответ (RU)

На Android нет нативной поддержки произвольных SVG-файлов во время выполнения (runtime) напрямую из строки. VectorDrawable поддерживает лишь ограниченное подмножество SVG и обычно генерируется на этапе сборки. Поэтому для работы с полной SVG-строкой на рантайме обычно используют сторонние библиотеки. Основные подходы:

### 1. AndroidSVG (Рекомендуется для простых случаев)

Легковесная библиотека для прямой работы с SVG-строками:

```kotlin
// ✅ Простой и прямой подход
private fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)

        // ✅ Для корректного отображения PictureDrawable
        imageView.setLayerType(View.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        // ❌ Отсутствие обработки ошибок может привести к краху приложения
        Log.e("SVG", "Parse error", e)
    }
}

// ✅ С контролем размеров (осторожно с аспект-ратио)
private fun displaySvgWithSize(
    svgString: String,
    imageView: ImageView,
    width: Int,
    height: Int
) {
    val svg = SVG.getFromString(svgString)

    // Если в SVG нет размеров, можно задать явно.
    // Следите за сохранением пропорций, если это важно для дизайна.
    svg.documentWidth = width.toFloat()
    svg.documentHeight = height.toFloat()

    val picture = svg.renderToPicture(width, height)
    val drawable = PictureDrawable(picture)

    imageView.setLayerType(View.LAYER_TYPE_SOFTWARE, null)
    imageView.setImageDrawable(drawable)
}
```

### 2. Coil с SVG декодером (современный подход)

Интеграция с популярной библиотекой загрузки изображений:

```kotlin
// ✅ Настройка ImageLoader с поддержкой SVG
val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

// ✅ Загрузка SVG из строки через ByteArray
// Можно передавать bytes напрямую как источник данных.
val request = ImageRequest.Builder(context)
    .data(svgString.toByteArray(Charsets.UTF_8))
    .target(imageView)
    .build()

imageLoader.enqueue(request)
```

Примечание: при передаче "сырых" байтов кеширование будет ограниченным. Для лучшего кеширования используйте стабильный data (например, URL или file/uri), либо собственный ключ.

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
            .data(svgString.toByteArray(Charsets.UTF_8))
            .build(),
        contentDescription = null,
        imageLoader = imageLoader,
        modifier = modifier
    )
}
```

Замечание: при использовании ByteArray в качестве model кеширование будет ограниченным; при частом переиспользовании имеет смысл задать стабильный ключ (memory/disk cache key) или использовать источник с постоянным идентификатором.

### 4. Пользовательский Drawable

Для полного контроля рендеринга (например, кастомное масштабирование, пост-обработка):

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
        val svg = this.svg ?: return

        // ⚠ Важно: установка documentWidth/documentHeight равными bounds
        // может исказить исходные пропорции. Лучше учитывать viewBox
        // и масштабировать с сохранением аспект-ратио при необходимости.
        svg.documentViewBox?.let { viewBox ->
            val scale = minOf(
                bounds.width() / viewBox.width,
                bounds.height() / viewBox.height
            )
            canvas.save()
            canvas.translate(bounds.left.toFloat(), bounds.top.toFloat())
            canvas.scale(scale, scale)
            svg.renderToCanvas(canvas)
            canvas.restore()
        } ?: run {
            svg.documentWidth = bounds.width().toFloat()
            svg.documentHeight = bounds.height().toFloat()
            svg.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {
        // При необходимости можно реализовать поддержку прозрачности через Paint.
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        // При необходимости можно реализовать применение цветового фильтра.
    }

    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

Замечание: пустые реализации setAlpha/setColorFilter означают, что системные эффекты прозрачности/тоновки к этому Drawable применяться не будут, если явно не добавить поддержку.

### Сравнение подходов

| Подход | Преимущества | Недостатки | Использовать когда |
|--------|--------------|------------|-------------------|
| AndroidSVG | Простота, прямой парсинг строки, контроль | Нет поддержки всех SVG-фич, требуется ручная настройка `View` | Простые случаи, локальные SVG-строки |
| Coil + SVG | Кеширование, современный API, интеграция с сетью | Доп. зависимость, нюансы с model/кешем для сырой строки | Загрузка из сети, повторное использование и кеширование |
| Custom Drawable | Полный контроль рендеринга | Больше кода, нужно самому учитывать размеры/аспект-ратио | Специфичные требования, сложные UIs |
| Compose | Декларативный UI, единый подход с Coil | Требуется Compose, те же нюансы с моделью/кешем | Приложения на Compose UI |

### Важные моменты

**Поддержка формата**:
- AndroidSVG и SVG-декодеры не поддерживают все возможности SVG (скрипты, фильтры, сложные анимации и т.п.).
- Для сложных SVG-файлов поведение может отличаться от браузеров.

**Память**:
- Преобразование больших SVG в Bitmap может вызвать OutOfMemoryError.
- Используйте PictureDrawable или векторный рендеринг, когда это возможно.

**Обработка ошибок**:
- Всегда оборачивайте парсинг в try-catch.
- SVG может содержать невалидный XML или неподдерживаемые элементы — логируйте и подставляйте fallback.

**Производительность**:
- Кешируйте результат парсинга при повторном использовании (например, храните SVG-объект).
- Для сетевых SVG используйте библиотеки с встроенным кешированием (Coil, Glide и т.п.).

**Размеры и масштабирование**:
- Многие SVG используют viewBox и не задают явные размеры — задавайте или вычисляйте размеры осознанно.
- Следите за сохранением аспект-ратио при масштабировании.
- Для ImageView используйте подходящий scaleType в соответствии с дизайном.

## Answer (EN)

Android does not natively support rendering arbitrary SVG files from a runtime string. VectorDrawable supports only a constrained subset of SVG and is usually generated at build time. To render a full SVG string at runtime you typically rely on third-party libraries. Main approaches:

### 1. AndroidSVG (Recommended for simple cases)

Lightweight library for direct SVG string handling:

```kotlin
// ✅ Simple and direct approach
private fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)

        // ✅ Ensure correct rendering with PictureDrawable
        imageView.setLayerType(View.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        // ❌ Missing error handling can crash the app
        Log.e("SVG", "Parse error", e)
    }
}

// ✅ With size control (beware aspect ratio)
private fun displaySvgWithSize(
    svgString: String,
    imageView: ImageView,
    width: Int,
    height: Int
) {
    val svg = SVG.getFromString(svgString)

    // If SVG has no explicit size, you can set one.
    // Be careful not to break the original aspect ratio if it matters.
    svg.documentWidth = width.toFloat()
    svg.documentHeight = height.toFloat()

    val picture = svg.renderToPicture(width, height)
    val drawable = PictureDrawable(picture)

    imageView.setLayerType(View.LAYER_TYPE_SOFTWARE, null)
    imageView.setImageDrawable(drawable)
}
```

### 2. Coil with SVG Decoder (modern approach)

Integration with a popular image loading library:

```kotlin
// ✅ Configure ImageLoader with SVG support
val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

// ✅ Load SVG from string via ByteArray
// Passing raw bytes works as a data source.
val request = ImageRequest.Builder(context)
    .data(svgString.toByteArray(Charsets.UTF_8))
    .target(imageView)
    .build()

imageLoader.enqueue(request)
```

Note: when using raw bytes as the model, caching will be limited. For better caching, use a stable data source (e.g., URL or file/uri) or provide a custom cache key.

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
            .data(svgString.toByteArray(Charsets.UTF_8))
            .build(),
        contentDescription = null,
        imageLoader = imageLoader,
        modifier = modifier
    )
}
```

Note: using a ByteArray as model limits cache reuse; for frequent reuse consider providing a stable key or a source with a consistent identifier.

### 4. Custom Drawable

For full rendering control (e.g., custom scaling, post-processing):

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
        val svg = this.svg ?: return

        // ⚠ Setting documentWidth/documentHeight equal to bounds
        // may distort the original aspect ratio.
        // Prefer using the viewBox and scaling while preserving aspect ratio.
        svg.documentViewBox?.let { viewBox ->
            val scale = minOf(
                bounds.width() / viewBox.width,
                bounds.height() / viewBox.height
            )
            canvas.save()
            canvas.translate(bounds.left.toFloat(), bounds.top.toFloat())
            canvas.scale(scale, scale)
            svg.renderToCanvas(canvas)
            canvas.restore()
        } ?: run {
            svg.documentWidth = bounds.width().toFloat()
            svg.documentHeight = bounds.height().toFloat()
            svg.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {
        // Implement alpha support with Paint if needed.
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        // Implement color filter support if needed.
    }

    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

Note: leaving setAlpha/setColorFilter empty means system-driven alpha/tint will not affect this Drawable unless you add explicit support.

### Approach Comparison

| Approach | Advantages | Disadvantages | Use when |
|----------|-----------|---------------|----------|
| AndroidSVG | Simple, direct string parsing, good control | Not all SVG features supported, manual `View` setup | Simple cases, local SVG strings |
| Coil + SVG | Caching, modern API, network integration | Extra dependency, model/cache nuances for raw strings | Network-loaded SVGs, caching and reuse |
| Custom Drawable | Full rendering control | More code, must handle sizing/aspect ratio yourself | Specific rendering requirements, complex UIs |
| Compose | Declarative, integrates well with Coil | Requires Compose, similar model/cache nuances | Compose-based UIs |

### Key Considerations

**Format support**:
- AndroidSVG and SVG decoders do not support the full SVG spec (e.g., scripts, advanced filters, complex animations).
- Complex SVGs may not render identically to browsers.

**Memory**:
- Converting large SVGs to Bitmap may cause OutOfMemoryError.
- Prefer PictureDrawable or vector-style rendering when possible.

**Error handling**:
- Always wrap parsing in try-catch.
- SVGs may contain invalid XML or unsupported elements; log and provide fallbacks.

**Performance**:
- Cache parsed SVG objects when reused.
- For network SVGs, use libraries with built-in caching (Coil, Glide, etc.).

**Sizing and scaling**:
- Many SVGs rely on viewBox without explicit sizes — define or compute sizes deliberately.
- Preserve aspect ratio when scaling unless distortion is acceptable.
- For ImageView, choose an appropriate scaleType per design.

## Follow-ups

- How to handle SVG animations in Android?
- What SVG features are not supported by AndroidSVG library?
- How to optimize SVG loading performance for lists/RecyclerView?
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
- How to load images efficiently in RecyclerView
- Vector drawables vs raster images in Android

### Advanced
- Custom drawable implementation patterns
- Image caching strategies in Android
