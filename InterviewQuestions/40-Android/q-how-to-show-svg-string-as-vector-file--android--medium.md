---
id: 20251017-105349
title: "How To Show SVG String As Vector File / Как показать SVG строку как векторный файл"
aliases: ["SVG String Display", "Отображение SVG строки", "SVG Vector Rendering"]
topic: android
subtopics: [ui-graphics, ui-views, ui-compose]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-vector-graphics-animations--android--medium, q-what-is-known-about-view-lifecycles--android--medium, q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]
created: 2025-10-15
updated: 2025-10-30
sources: [https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources]
tags: [android/ui-graphics, android/ui-views, android/ui-compose, difficulty/medium, svg, vector-graphics, image-loading]
---

# Вопрос (RU)

> Как отобразить SVG строку в виде векторного изображения в Android?

# Question (EN)

> How to display an SVG string as a vector image in Android?

---

## Ответ (RU)

Android не поддерживает SVG нативно, но существует несколько проверенных подходов для отображения SVG-строк: AndroidSVG библиотека, Coil с SVG декодером, конвертация в Bitmap, или custom Drawable.

### 1. AndroidSVG Библиотека — Прямая Работа со Строками

✅ **Рекомендуемый подход** для большинства сценариев.

```kotlin
// implementation 'com.caverock:androidsvg-aar:1.4'

fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        imageView.setImageDrawable(PictureDrawable(svg.renderToPicture()))
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}

// С явным указанием размеров
fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
    val svg = SVG.getFromString(svgString)
    svg.documentWidth = width.toFloat()
    svg.documentHeight = height.toFloat()

    val picture = svg.renderToPicture(width, height)
    imageView.setImageDrawable(PictureDrawable(picture))
}
```

**Преимущества:** Легковесность, простота, хорошая производительность.
**Недостатки:** Нет кэширования из коробки, ручное управление.

### 2. Coil с SVG Декодером — Современный Подход

✅ **Лучший выбор** для приложений с загрузкой из сети.

```kotlin
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

val imageLoader = ImageLoader.Builder(context)
    .components { add(SvgDecoder.Factory()) }
    .build()

fun loadSvgString(svgString: String, imageView: ImageView) {
    val request = ImageRequest.Builder(context)
        .data(svgString.toByteArray())
        .target(imageView)
        .build()

    imageLoader.enqueue(request)
}
```

**Преимущества:** Кэширование, coroutines поддержка, современный API.
**Недостатки:** Дополнительная зависимость.

### 3. Custom Drawable — Полный Контроль

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private var svg: SVG? = null

    init {
        svg = SVG.getFromString(svgString)
    }

    override fun draw(canvas: Canvas) {
        svg?.let {
            it.documentWidth = bounds.width().toFloat()
            it.documentHeight = bounds.height().toFloat()
            it.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {}
    override fun setColorFilter(colorFilter: ColorFilter?) {}
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// Использование
imageView.setImageDrawable(SvgDrawable(svgString))
```

### 4. Jetpack Compose Реализация

```kotlin
@Composable
fun SvgFromString(svgString: String, modifier: Modifier = Modifier) {
    var drawable by remember { mutableStateOf<Drawable?>(null) }

    LaunchedEffect(svgString) {
        withContext(Dispatchers.IO) {
            val svg = SVG.getFromString(svgString)
            drawable = PictureDrawable(svg.renderToPicture())
        }
    }

    Canvas(modifier = modifier) {
        drawable?.let {
            it.setBounds(0, 0, size.width.toInt(), size.height.toInt())
            drawIntoCanvas { canvas ->
                it.draw(canvas.nativeCanvas)
            }
        }
    }
}
```

### 5. Конвертация в Bitmap

❌ **Избегать** для векторной графики — теряется масштабируемость.

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
        null
    }
}
```

### Лучшие Практики

**Обработка ошибок:**
```kotlin
fun safeSvgLoad(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        imageView.setImageDrawable(PictureDrawable(svg.renderToPicture()))
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parsing failed", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}
```

**Кэширование:**
```kotlin
class OptimizedSvgLoader {
    private val cache = LruCache<String, PictureDrawable>(10)

    fun loadSvg(svgString: String, imageView: ImageView) {
        val key = svgString.hashCode().toString()
        cache.get(key)?.let {
            imageView.setImageDrawable(it)
            return
        }

        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        cache.put(key, drawable)
        imageView.setImageDrawable(drawable)
    }
}
```

**ViewModel интеграция:**
```kotlin
class SvgViewModel : ViewModel() {
    private val _svgDrawable = MutableLiveData<PictureDrawable?>()
    val svgDrawable: LiveData<PictureDrawable?> = _svgDrawable

    fun loadSvg(svgString: String) {
        viewModelScope.launch(Dispatchers.Default) {
            val svg = SVG.getFromString(svgString)
            _svgDrawable.postValue(PictureDrawable(svg.renderToPicture()))
        }
    }
}
```

### Сравнение Подходов

| Подход | Производительность | Кэширование | Сложность | Сценарий |
|--------|-------------------|-------------|-----------|----------|
| AndroidSVG | Высокая | Ручное | Низкая | Простые случаи |
| Coil | Высокая | Автоматическое | Средняя | Сеть, кэш |
| Custom Drawable | Высокая | Ручное | Средняя | Особые требования |
| Bitmap | Низкая | Ручное | Низкая | ❌ Не рекомендуется |

**Рекомендации по выбору:**
- **Простая интеграция** → AndroidSVG
- **Сетевые SVG** → Coil с SVG декодером
- **Compose UI** → Custom Canvas с LaunchedEffect
- **Особая логика отрисовки** → Custom Drawable

---

## Answer (EN)

Android doesn't support SVG natively, but there are several proven approaches to display SVG strings: AndroidSVG library, Coil with SVG decoder, Bitmap conversion, or custom Drawable.

### 1. AndroidSVG Library — Direct String Handling

✅ **Recommended approach** for most scenarios.

```kotlin
// implementation 'com.caverock:androidsvg-aar:1.4'

fun displaySvgFromString(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        imageView.setImageDrawable(PictureDrawable(svg.renderToPicture()))
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parse error", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}

// With explicit dimensions
fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
    val svg = SVG.getFromString(svgString)
    svg.documentWidth = width.toFloat()
    svg.documentHeight = height.toFloat()

    val picture = svg.renderToPicture(width, height)
    imageView.setImageDrawable(PictureDrawable(picture))
}
```

**Pros:** Lightweight, simple, good performance.
**Cons:** No built-in caching, manual management.

### 2. Coil with SVG Decoder — Modern Approach

✅ **Best choice** for apps with network loading.

```kotlin
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

val imageLoader = ImageLoader.Builder(context)
    .components { add(SvgDecoder.Factory()) }
    .build()

fun loadSvgString(svgString: String, imageView: ImageView) {
    val request = ImageRequest.Builder(context)
        .data(svgString.toByteArray())
        .target(imageView)
        .build()

    imageLoader.enqueue(request)
}
```

**Pros:** Caching, coroutines support, modern API.
**Cons:** Additional dependency.

### 3. Custom Drawable — Full Control

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {
    private var svg: SVG? = null

    init {
        svg = SVG.getFromString(svgString)
    }

    override fun draw(canvas: Canvas) {
        svg?.let {
            it.documentWidth = bounds.width().toFloat()
            it.documentHeight = bounds.height().toFloat()
            it.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {}
    override fun setColorFilter(colorFilter: ColorFilter?) {}
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// Usage
imageView.setImageDrawable(SvgDrawable(svgString))
```

### 4. Jetpack Compose Implementation

```kotlin
@Composable
fun SvgFromString(svgString: String, modifier: Modifier = Modifier) {
    var drawable by remember { mutableStateOf<Drawable?>(null) }

    LaunchedEffect(svgString) {
        withContext(Dispatchers.IO) {
            val svg = SVG.getFromString(svgString)
            drawable = PictureDrawable(svg.renderToPicture())
        }
    }

    Canvas(modifier = modifier) {
        drawable?.let {
            it.setBounds(0, 0, size.width.toInt(), size.height.toInt())
            drawIntoCanvas { canvas ->
                it.draw(canvas.nativeCanvas)
            }
        }
    }
}
```

### 5. Bitmap Conversion

❌ **Avoid** for vector graphics — loses scalability.

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
        null
    }
}
```

### Best Practices

**Error Handling:**
```kotlin
fun safeSvgLoad(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        imageView.setImageDrawable(PictureDrawable(svg.renderToPicture()))
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parsing failed", e)
        imageView.setImageResource(R.drawable.placeholder)
    }
}
```

**Caching:**
```kotlin
class OptimizedSvgLoader {
    private val cache = LruCache<String, PictureDrawable>(10)

    fun loadSvg(svgString: String, imageView: ImageView) {
        val key = svgString.hashCode().toString()
        cache.get(key)?.let {
            imageView.setImageDrawable(it)
            return
        }

        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        cache.put(key, drawable)
        imageView.setImageDrawable(drawable)
    }
}
```

**ViewModel Integration:**
```kotlin
class SvgViewModel : ViewModel() {
    private val _svgDrawable = MutableLiveData<PictureDrawable?>()
    val svgDrawable: LiveData<PictureDrawable?> = _svgDrawable

    fun loadSvg(svgString: String) {
        viewModelScope.launch(Dispatchers.Default) {
            val svg = SVG.getFromString(svgString)
            _svgDrawable.postValue(PictureDrawable(svg.renderToPicture()))
        }
    }
}
```

### Approach Comparison

| Approach | Performance | Caching | Complexity | Scenario |
|----------|------------|---------|------------|----------|
| AndroidSVG | High | Manual | Low | Simple cases |
| Coil | High | Automatic | Medium | Network, cache |
| Custom Drawable | High | Manual | Medium | Special requirements |
| Bitmap | Low | Manual | Low | ❌ Not recommended |

**Selection Recommendations:**
- **Simple integration** → AndroidSVG
- **Network SVG** → Coil with SVG decoder
- **Compose UI** → Custom Canvas with LaunchedEffect
- **Custom rendering logic** → Custom Drawable

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

### Same Level (Medium)
- [[q-vector-graphics-animations--android--medium]]
- [[q-what-is-known-about-view-lifecycles--android--medium]]

### Advanced (Hard)
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]]
