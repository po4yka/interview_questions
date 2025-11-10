---
id: android-294
title: How To Show SVG String As Vector File / Как показать SVG строку как векторный файл
aliases:
- SVG String Display
- SVG Vector Rendering
- Отображение SVG строки
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
- q-vector-graphics-animations--android--medium
- q-what-is-known-about-view-lifecycles--android--medium
- q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard
created: 2025-10-15
updated: 2025-11-10
sources:
- "https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources"
tags:
- android/ui-compose
- android/ui-graphics
- android/ui-views
- difficulty/medium
- image-loading
- svg
- vector-graphics

---

# Вопрос (RU)

> Как отобразить SVG строку в виде векторного изображения в Android?

# Question (EN)

> How to display an SVG string as a vector image in Android?

---

## Ответ (RU)

Android не поддерживает SVG нативно, и строку SVG нельзя напрямую интерпретировать как `VectorDrawable` ресурс. Но существует несколько проверенных подходов для рендеринга SVG-строк как векторной (масштабируемой) графики во время выполнения: библиотека AndroidSVG, Coil с SVG декодером, конвертация в `Bitmap` или `Custom Drawable`.

### 1. AndroidSVG Библиотека — Прямая Работа Со Строками

Один из самых распространенных подходов для работы именно со строками SVG.

```kotlin
// implementation 'com.caverock:androidsvg-aar:1.4'

fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)

        // ВАЖНО: отключаем аппаратное ускорение для корректного рендеринга PictureDrawable
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
Недостатки: нет кэширования из коробки, ручное управление, нужен контроль `LayerType`.

### 2. Coil С SVG Декодером — Современный Подход

Хороший выбор для приложений с загрузкой из сети или при использовании унифицированного image loader.

Важно: Coil ожидает указание типа данных, чтобы применить `SvgDecoder`. При работе со строкой SVG нужно использовать `data` с `Decoder.Factory` и при необходимости установить MIME-тип.

```kotlin
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

fun loadSvgString(svgString: String, imageView: ImageView) {
    val request = ImageRequest.Builder(context)
        // Передаем SVG как ByteArray с явным MIME-типом
        .data(svgString.toByteArray())
        .mimeType("image/svg+xml")
        .target(imageView)
        .build()

    imageLoader.enqueue(request)
}
```

Альтернатива: если SVG доступен по URL/файлу, достаточно передать URI/URL, и `SvgDecoder` будет выбран автоматически.

Преимущества: кэширование, поддержка coroutines, современный API.
Недостатки: дополнительная зависимость, для "сырой" строки нужна аккуратная настройка `data`/`mimeType`.

### 3. Custom Drawable — Полный Контроль

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private val svg: SVG = SVG.getFromString(svgString)

    override fun draw(canvas: Canvas) {
        // Подгоняем содержимое под bounds Drawable
        svg.documentWidth = bounds.width().toFloat()
        svg.documentHeight = bounds.height().toFloat()
        svg.renderToCanvas(canvas)
    }

    override fun setAlpha(alpha: Int) { /* NOP: управляется самим SVG */ }
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
| Coil | Высокая | Автоматическое | Средняя | Сеть, кэш, унифицированная загрузка |
| Custom Drawable | Высокая | Ручное | Средняя | Особые требования, кастомный рендеринг |
| Bitmap | Ниже | Ручное | Низкая | Спец. случаи, когда нужен Bitmap (не как основной способ) |

Рекомендации по выбору:
- Прямой рендер из SVG строки → AndroidSVG или Custom Drawable.
- Сетевые или кэшируемые SVG → Coil с SVG декодером.
- Compose UI → рендер через Canvas/Drawable + парсинг вне главного потока.
- Особая логика отрисовки → Custom Drawable.

---

## Answer (EN)

Android doesn't support SVG natively, and an SVG string cannot be directly used as a `VectorDrawable` resource. However, there are several proven approaches to render SVG strings as scalable vector graphics at runtime: AndroidSVG library, Coil with SVG decoder, Bitmap conversion, or a custom `Drawable`.

### 1. AndroidSVG Library — Direct `String` Handling

A common and practical approach for working directly with SVG strings.

```kotlin
// implementation 'com.caverock:androidsvg-aar:1.4'

fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)

        // IMPORTANT: disable hardware acceleration for proper PictureDrawable rendering
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
Cons: no built-in caching, manual management, must handle layer type.

### 2. Coil with SVG Decoder — Modern Approach

A solid choice for apps loading images from the network or using a common image loader.

Important: Coil needs to know it's dealing with SVG to apply `SvgDecoder`. With an in-memory SVG string, configure `data` and MIME type appropriately.

```kotlin
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

val imageLoader = ImageLoader.Builder(context)
    .components {
        add(SvgDecoder.Factory())
    }
    .build()

fun loadSvgString(svgString: String, imageView: ImageView) {
    val request = ImageRequest.Builder(context)
        // Pass raw SVG bytes with explicit MIME type so SvgDecoder is used
        .data(svgString.toByteArray())
        .mimeType("image/svg+xml")
        .target(imageView)
        .build()

    imageLoader.enqueue(request)
}
```

Alternatively, when SVG is available via URL/file, simply pass the URI/URL and `SvgDecoder` will be picked automatically.

Pros: caching, coroutines support, modern API.
Cons: extra dependency, raw string input requires correct configuration.

### 3. Custom Drawable — Full Control

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private val svg: SVG = SVG.getFromString(svgString)

    override fun draw(canvas: Canvas) {
        // Fit SVG content into this drawable's bounds
        svg.documentWidth = bounds.width().toFloat()
        svg.documentHeight = bounds.height().toFloat()
        svg.renderToCanvas(canvas)
    }

    override fun setAlpha(alpha: Int) { /* NOP: let SVG define alpha */ }
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
| Coil | High | Automatic | Medium | Network + cache, unified loading |
| Custom Drawable | High | Manual | Medium | Special requirements, custom rendering |
| Bitmap | Lower | Manual | Low | Special cases requiring Bitmap (not primary) |

Selection recommendations:
- Direct rendering from SVG string → AndroidSVG or Custom Drawable.
- Network / cached SVG → Coil with SVG decoder.
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
