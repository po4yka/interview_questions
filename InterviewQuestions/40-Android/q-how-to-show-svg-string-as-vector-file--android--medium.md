---
id: android-294
title: How To Show SVG String As Vector File / Как показать SVG строку как векторный файл
aliases: [SVG String Display, SVG Vector Rendering, Отображение SVG строки]
topic: android
subtopics:
  - ui-compose
  - ui-graphics
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-compose-state
  - c-jetpack-compose
  - q-api-file-upload-server--android--medium
  - q-how-to-display-svg-string-as-a-vector-file--android--medium
  - q-large-file-upload--android--medium
  - q-vector-graphics-animations--android--medium
  - q-what-is-known-about-view-lifecycles--android--medium
  - q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard
created: 2025-10-15
updated: 2025-11-10
sources:
  - "https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources"
tags: [android/ui-compose, android/ui-graphics, android/ui-views, difficulty/medium, image-loading, svg, vector-graphics]

date created: Saturday, November 1st 2025, 12:46:54 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---

# Вопрос (RU)

> Как отобразить SVG строку в виде векторного изображения в Android?

# Question (EN)

> How to display an SVG string as a vector image in Android?

---

## Ответ (RU)

Android не поддерживает SVG нативно, и строку SVG нельзя напрямую интерпретировать как `VectorDrawable` ресурс. Но существует несколько проверенных подходов для рендеринга SVG-строк как векторной (масштабируемой) графики во время выполнения: библиотека AndroidSVG, Coil с SVG декодером (для URL/файлов), конвертация в `Bitmap` или `Custom Drawable`.

Важно: строку SVG в рантайме нельзя «превратить» в настоящий ресурс `VectorDrawable` без оффлайн-конвертации в формát VectorDrawable XML.

### 1. AndroidSVG Библиотека — Прямая Работа Со Строками

Один из самых распространенных подходов для работы именно со строками SVG.

```kotlin
// implementation 'com.caverock:androidsvg-aar:1.4'

fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)

        // ВАЖНО: для PictureDrawable возможны артефакты с аппаратным ускорением.
        // При проблемах можно отключить аппаратное ускорение ТОЛЬКО для этого ImageView.
        imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}

// С явным указанием размеров (масштабируем рендеринг под нужный размер)
fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
    try {
        val svg = SVG.getFromString(svgString)
        svg.documentWidth = width.toFloat()
        svg.documentHeight = height.toFloat()

        val picture = svg.renderToPicture(width, height)
        val drawable = PictureDrawable(picture)

        imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}
```

Преимущества: легковесность, простота, хорошая производительность.
Недостатки: нет кэширования из коробки, ручное управление, возможна необходимость управления `LayerType`.

### 2. Coil С SVG Декодером — Современный Подход

Хороший выбор для приложений с загрузкой из сети или при использовании унифицированного image loader.

Важно: Coil ожидает корректный источник данных (URL, файл, Content URI или кастомный fetcher), чтобы применить `SvgDecoder`. Для произвольной SVG строки рекомендуется либо:
- использовать AndroidSVG напрямую (см. п.1);
- либо написать кастомный `Fetcher`/`Decoder`, который будет передавать строку как SVG-контент в Coil.

Пример базовой настройки для URL/файлов:

```kotlin
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

fun loadSvgFromUrl(url: String, imageView: ImageView) {
    val request = ImageRequest.Builder(context)
        .data(url)
        .target(imageView)
        .build()

    imageLoader.enqueue(request)
}
```

Преимущества: кэширование, поддержка coroutines, современный API.
Недостатки: дополнительная зависимость; для «сырой» строки требуется дополнительная интеграция (кастомный `Fetcher`/`Decoder`), а не просто передача `ByteArray`.

### 3. Custom Drawable — Полный Контроль

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private val svg: SVG = SVG.getFromString(svgString)

    override fun draw(canvas: Canvas) {
        // Масштабируем содержимое под bounds Drawable с учетом исходного viewBox
        val viewBox = svg.documentViewBox
        if (viewBox != null) {
            val scaleX = bounds.width() / viewBox.width()
            val scaleY = bounds.height() / viewBox.height()
            val saveCount = canvas.save()
            canvas.translate(bounds.left.toFloat(), bounds.top.toFloat())
            canvas.scale(scaleX, scaleY)
            svg.renderToCanvas(canvas)
            canvas.restoreToCount(saveCount)
        } else {
            svg.documentWidth = bounds.width().toFloat()
            svg.documentHeight = bounds.height().toFloat()
            svg.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) { /* NOP: управляется самим SVG или краской */ }
    override fun setColorFilter(colorFilter: ColorFilter?) { /* Реализовать при необходимости */ }
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// Использование
imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
imageView.setImageDrawable(SvgDrawable(svgString))
```

### 4. Jetpack Compose Реализация

```kotlin
@Composable
fun SvgFromString(svgString: String, modifier: Modifier = Modifier) {
    var drawable by remember { mutableStateOf<Drawable?>(null) }

    LaunchedEffect(svgString) {
        // Парсинг SVG выносим из главного потока
        val parsed = withContext(Dispatchers.Default) {
            try {
                val svg = SVG.getFromString(svgString)
                PictureDrawable(svg.renderToPicture())
            } catch (e: SVGParseException) {
                Log.e("SVG", "Parse error", e)
                null
            }
        }
        drawable = parsed
    }

    Canvas(modifier = modifier) {
        val d = drawable ?: return@Canvas
        d.setBounds(0, 0, size.width.toInt(), size.height.toInt())
        drawIntoCanvas { canvas ->
            // При использовании PictureDrawable возможны проблемы с аппаратным ускорением.
            // При артефактах рассмотрите отрисовку Picture напрямую или отключение HW для host view.
            d.draw(canvas.nativeCanvas)
        }
    }
}
```

### 5. Конвертация В Bitmap

Как основной подход для векторной графики нежелательна — теряется масштабируемость и увеличивается расход памяти. Может быть уместна для кэширования или когда требуется именно `Bitmap` API.

```kotlin
fun svgToBitmap(svgString: String, width: Int, height: Int): Bitmap? {
    return try {
        val svg = SVG.getFromString(svgString)
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        svg.documentWidth = width.toFloat()
        svg.documentHeight = height.toFloat()
        svg.renderToCanvas(canvas)

        bitmap
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        null
    }
}
```

### Лучшие Практики

Обработка ошибок:

```kotlin
fun safeSvgLoad(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parsing failed", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}
```

Кэширование:

```kotlin
class OptimizedSvgLoader {
    private val cache = LruCache<String, PictureDrawable>(10)

    fun loadSvg(svgString: String, imageView: ImageView) {
        val key = svgString.hashCode().toString()

        cache.get(key)?.let { cached ->
            imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
            imageView.setImageDrawable(cached)
            return
        }

        try {
            val svg = SVG.getFromString(svgString)
            val drawable = PictureDrawable(svg.renderToPicture())
            cache.put(key, drawable)
            imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            Log.e("SVG", "Parsing failed", e)
            imageView.setImageResource(R.drawable.placeholder)
        }
    }
}
```

Интеграция с `ViewModel`:

```kotlin
class SvgViewModel : ViewModel() {
    private val _svgDrawable = MutableLiveData<PictureDrawable?>()
    val svgDrawable: LiveData<PictureDrawable?> = _svgDrawable

    fun loadSvg(svgString: String) {
        viewModelScope.launch(Dispatchers.Default) {
            try {
                val svg = SVG.getFromString(svgString)
                val drawable = PictureDrawable(svg.renderToPicture())
                _svgDrawable.postValue(drawable)
            } catch (e: SVGParseException) {
                Log.e("SVG", "Parsing failed", e)
                _svgDrawable.postValue(null)
            }
        }
    }
}
```

### Сравнение Подходов

| Подход | Производительность | Кэширование | Сложность | Сценарий |
|--------|-------------------|-------------|-----------|----------|
| AndroidSVG | Высокая | Ручное | Низкая | Простые случаи, прямой рендеринг из строки |
| Coil | Высокая | Автоматическое | Средняя | Сеть, кэш, унифицированная загрузка (URL/файлы) |
| Custom Drawable | Высокая | Ручное | Средняя | Особые требования, кастомный рендеринг |
| Bitmap | Ниже | Ручное | Низкая | Спец. случаи, когда нужен Bitmap (не как основной способ) |

Рекомендации по выбору:
- Прямой рендер из SVG строки → AndroidSVG или Custom Drawable.
- Сетевые или кэшируемые SVG → Coil с SVG декодером (для URL/файлов или с кастомным fetcher/decoder для строк).
- Compose UI → рендер через Canvas/Drawable + парсинг вне главного потока.
- Особая логика отрисовки → Custom Drawable.

---

## Answer (EN)

Android doesn't support SVG natively, and an SVG string cannot be directly used as a `VectorDrawable` resource. However, there are several proven approaches to render SVG strings as scalable vector graphics at runtime: AndroidSVG library, Coil with SVG decoder (for URLs/files), Bitmap conversion, or a custom `Drawable`.

Important: you cannot "convert" an in-memory SVG string into a real `VectorDrawable` resource at runtime without offline conversion to VectorDrawable XML.

### 1. AndroidSVG Library — Direct `String` Handling

A common and practical approach for working directly with SVG strings.

```kotlin
// implementation 'com.caverock:androidsvg-aar:1.4'

fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)

        // IMPORTANT: PictureDrawable may have issues with hardware acceleration.
        // If you see artifacts, disable HW only for this ImageView.
        imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}

// With explicit dimensions (scale rendering to the desired size)
fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
    try {
        val svg = SVG.getFromString(svgString)
        svg.documentWidth = width.toFloat()
        svg.documentHeight = height.toFloat()

        val picture = svg.renderToPicture(width, height)
        val drawable = PictureDrawable(picture)

        imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}
```

Pros: lightweight, simple, good performance.
Cons: no built-in caching, manual management, may require layer type adjustments.

### 2. Coil with SVG Decoder — Modern Approach

A solid choice for apps loading images from the network or using a common image loader.

Important: Coil selects `SvgDecoder` based on the data source (URL/file/URI, etc.) and content; for an arbitrary in-memory SVG string you should either:
- use AndroidSVG directly (see #1), or
- implement a custom `Fetcher`/`Decoder` that provides SVG content to Coil correctly.

Basic setup for URL/file sources:

```kotlin
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

fun loadSvgFromUrl(url: String, imageView: ImageView) {
    val request = ImageRequest.Builder(context)
        .data(url)
        .target(imageView)
        .build()

    imageLoader.enqueue(request)
}
```

Pros: caching, coroutines support, modern API.
Cons: extra dependency; raw SVG strings require custom integration (not just `ByteArray`).

### 3. Custom Drawable — Full Control

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private val svg: SVG = SVG.getFromString(svgString)

    override fun draw(canvas: Canvas) {
        // Fit SVG content into this drawable's bounds while respecting the original viewBox
        val viewBox = svg.documentViewBox
        if (viewBox != null) {
            val scaleX = bounds.width() / viewBox.width()
            val scaleY = bounds.height() / viewBox.height()
            val saveCount = canvas.save()
            canvas.translate(bounds.left.toFloat(), bounds.top.toFloat())
            canvas.scale(scaleX, scaleY)
            svg.renderToCanvas(canvas)
            canvas.restoreToCount(saveCount)
        } else {
            svg.documentWidth = bounds.width().toFloat()
            svg.documentHeight = bounds.height().toFloat()
            svg.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) { /* NOP: let SVG or paint handle alpha */ }
    override fun setColorFilter(colorFilter: ColorFilter?) { /* Implement if needed */ }
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// Usage
imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
imageView.setImageDrawable(SvgDrawable(svgString))
```

### 4. Jetpack Compose Implementation

```kotlin
@Composable
fun SvgFromString(svgString: String, modifier: Modifier = Modifier) {
    var drawable by remember { mutableStateOf<Drawable?>(null) }

    LaunchedEffect(svgString) {
        // Parse off the main thread
        val parsed = withContext(Dispatchers.Default) {
            try {
                val svg = SVG.getFromString(svgString)
                PictureDrawable(svg.renderToPicture())
            } catch (e: SVGParseException) {
                Log.e("SVG", "Parse error", e)
                null
            }
        }
        drawable = parsed
    }

    Canvas(modifier = modifier) {
        val d = drawable ?: return@Canvas
        d.setBounds(0, 0, size.width.toInt(), size.height.toInt())
        drawIntoCanvas { canvas ->
            // When using PictureDrawable with HW acceleration there may be artifacts.
            // If that happens, consider drawing the Picture directly or disabling HW for the host view.
            d.draw(canvas.nativeCanvas)
        }
    }
}
```

### 5. Bitmap Conversion

Not recommended as the primary approach for vector graphics, since it loses scalability and increases memory usage. Can be acceptable when a real `Bitmap` is required.

```kotlin
fun svgToBitmap(svgString: String, width: Int, height: Int): Bitmap? {
    return try {
        val svg = SVG.getFromString(svgString)
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        svg.documentWidth = width.toFloat()
        svg.documentHeight = height.toFloat()
        svg.renderToCanvas(canvas)

        bitmap
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        null
    }
}
```

### Best Practices

Error handling:

```kotlin
fun safeSvgLoad(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parsing failed", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}
```

Caching:

```kotlin
class OptimizedSvgLoader {
    private val cache = LruCache<String, PictureDrawable>(10)

    fun loadSvg(svgString: String, imageView: ImageView) {
        val key = svgString.hashCode().toString()

        cache.get(key)?.let { cached ->
            imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
            imageView.setImageDrawable(cached)
            return
        }

        try {
            val svg = SVG.getFromString(svgString)
            val drawable = PictureDrawable(svg.renderToPicture())
            cache.put(key, drawable)
            imageView.setLayerType(ImageView.LAYER_TYPE_SOFTWARE, null)
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            Log.e("SVG", "Parsing failed", e)
            imageView.setImageResource(R.drawable.placeholder)
        }
    }
}
```

`ViewModel` integration:

```kotlin
class SvgViewModel : ViewModel() {
    private val _svgDrawable = MutableLiveData<PictureDrawable?>()
    val svgDrawable: LiveData<PictureDrawable?> = _svgDrawable

    fun loadSvg(svgString: String) {
        viewModelScope.launch(Dispatchers.Default) {
            try {
                val svg = SVG.getFromString(svgString)
                val drawable = PictureDrawable(svg.renderToPicture())
                _svgDrawable.postValue(drawable)
            } catch (e: SVGParseException) {
                Log.e("SVG", "Parsing failed", e)
                _svgDrawable.postValue(null)
            }
        }
    }
}
```

### Approach Comparison

| Approach | Performance | Caching | Complexity | Scenario |
|----------|------------|---------|------------|----------|
| AndroidSVG | High | Manual | Low | Simple cases, direct rendering from string |
| Coil | High | Automatic | Medium | Network + cache, unified loading (URLs/files; strings via custom integration) |
| Custom Drawable | High | Manual | Medium | Special requirements, custom rendering |
| Bitmap | Lower | Manual | Low | Special cases requiring Bitmap (not primary) |

Selection recommendations:
- Direct rendering from SVG string → AndroidSVG or Custom Drawable.
- Network / cached SVG → Coil with SVG decoder (for URLs/files or via custom fetcher/decoder for strings).
- Compose UI → Canvas/Drawable rendering with off-main-thread parsing.
- Custom rendering logic → Custom Drawable.

---

## Follow-ups

1. How to handle SVG parsing failures gracefully with fallback images?
2. What memory optimizations are needed when caching multiple SVG drawables?
3. How to implement SVG color tinting at runtime?
4. What are the performance implications of SVG vs VectorDrawable in Android?
5. How to batch-load multiple SVG strings efficiently in RecyclerView?

## References

- [[q-vector-graphics-animations--android--medium]]
- [[q-what-is-known-about-view-lifecycles--android--medium]]
- https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources
- https://github.com/coil-kt/coil
- https://github.com/BigBadaboom/androidsvg

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Same Level (Medium)

- [[q-vector-graphics-animations--android--medium]]
- [[q-what-is-known-about-view-lifecycles--android--medium]]

### Advanced (Hard)

- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]]
