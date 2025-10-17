---
id: "20251015082237321"
title: "How To Display Svg String As A Vector File / Как отобразить SVG строку как векторный файл"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [image loading, file handling, android, ui, image-loading, difficulty/medium]
---
# How to display SVG string as a vector file?

# Вопрос (RU)

Как SVG-строку показать в виде векторного файла

## Answer (EN)
There are several approaches to display an SVG string as a vector image in Android. The methods range from using specialized libraries to converting the SVG to native Android vector drawables.

### 1. Using AndroidSVG Library

The most straightforward approach for SVG strings.

```kotlin
// Add dependency
// implementation 'com.caverock:androidsvg-aar:1.4'

class SvgActivity : AppCompatActivity() {

    private fun displaySvgFromString(svgString: String, imageView: ImageView) {
        try {
            val svg = SVG.getFromString(svgString)
            val drawable = PictureDrawable(svg.renderToPicture())
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
    }

    // Alternative: Set dimensions
    private fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
        try {
            val svg = SVG.getFromString(svgString)

            // Set SVG document dimensions
            svg.documentWidth = width.toFloat()
            svg.documentHeight = height.toFloat()

            val picture = svg.renderToPicture(width, height)
            val drawable = PictureDrawable(picture)
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
    }

    // Example usage
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_svg)

        val imageView = findViewById<ImageView>(R.id.imageView)
        val svgString = """
            <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="40" fill="blue" />
            </svg>
        """.trimIndent()

        displaySvgFromString(svgString, imageView)
    }
}
```

### 2. Using Coil with SVG Decoder

Modern image loading library with SVG support.

```kotlin
// Add dependencies
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

class CoilSvgActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Setup ImageLoader with SVG support
        val imageLoader = ImageLoader.Builder(this)
            .components {
                add(SvgDecoder.Factory())
            }
            .build()

        val imageView = findViewById<ImageView>(R.id.imageView)
        val svgString = """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="200" height="200" fill="red" />
                <circle cx="100" cy="100" r="50" fill="yellow" />
            </svg>
        """.trimIndent()

        // Convert string to ByteArray
        val svgBytes = svgString.toByteArray()

        // Load SVG from bytes
        val request = ImageRequest.Builder(this)
            .data(svgBytes)
            .target(imageView)
            .build()

        imageLoader.enqueue(request)
    }

    // Load SVG from URL
    private fun loadSvgFromUrl(url: String, imageView: ImageView) {
        val imageLoader = ImageLoader.Builder(this)
            .components {
                add(SvgDecoder.Factory())
            }
            .build()

        val request = ImageRequest.Builder(this)
            .data(url)
            .target(imageView)
            .build()

        imageLoader.enqueue(request)
    }
}
```

### 3. Using Glide with SVG Module

```kotlin
// Add dependencies
// implementation 'com.github.bumptech.glide:glide:4.16.0'
// implementation 'com.caverock:androidsvg-aar:1.4'

// Create SVG Decoder for Glide
class SvgDecoder : ResourceDecoder<InputStream, SVG> {
    override fun handles(source: InputStream, options: Options): Boolean = true

    override fun decode(
        source: InputStream,
        width: Int,
        height: Int,
        options: Options
    ): Resource<SVG>? {
        return try {
            val svg = SVG.getFromInputStream(source)
            SimpleResource(svg)
        } catch (e: SVGParseException) {
            null
        }
    }
}

// SVG to Drawable transcoder
class SvgDrawableTranscoder : ResourceTranscoder<SVG, PictureDrawable> {
    override fun transcode(
        toTranscode: Resource<SVG>,
        options: Options
    ): Resource<PictureDrawable> {
        val svg = toTranscode.get()
        val picture = svg.renderToPicture()
        val drawable = PictureDrawable(picture)
        return SimpleResource(drawable)
    }
}

// Register in AppGlideModule
@GlideModule
class MyAppGlideModule : AppGlideModule() {
    override fun registerComponents(context: Context, glide: Glide, registry: Registry) {
        registry.register(SVG::class.java, PictureDrawable::class.java, SvgDrawableTranscoder())
            .append(InputStream::class.java, SVG::class.java, SvgDecoder())
    }

    override fun isManifestParsingEnabled(): Boolean = false
}

// Usage
class GlideSvgActivity : AppCompatActivity() {

    private fun loadSvgString(svgString: String, imageView: ImageView) {
        val svgBytes = svgString.toByteArray()

        Glide.with(this)
            .`as`(PictureDrawable::class.java)
            .load(svgBytes)
            .into(imageView)
    }
}
```

### 4. Save to File and Load

```kotlin
class SvgFileActivity : AppCompatActivity() {

    private fun saveSvgStringToFile(svgString: String): File {
        val file = File(cacheDir, "temp_svg_${System.currentTimeMillis()}.svg")
        file.writeText(svgString)
        return file
    }

    private fun loadSvgFromFile(file: File, imageView: ImageView) {
        try {
            val svg = SVG.getFromInputStream(file.inputStream())
            val drawable = PictureDrawable(svg.renderToPicture())
            imageView.setImageDrawable(drawable)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    // Complete flow
    private fun displaySvgString(svgString: String, imageView: ImageView) {
        val file = saveSvgStringToFile(svgString)
        loadSvgFromFile(file, imageView)
        file.delete() // Clean up
    }
}
```

### 5. Convert SVG to Bitmap

```kotlin
class SvgToBitmapConverter {

    fun svgStringToBitmap(svgString: String, width: Int, height: Int): Bitmap? {
        return try {
            val svg = SVG.getFromString(svgString)

            val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bitmap)

            svg.documentWidth = width.toFloat()
            svg.documentHeight = height.toFloat()

            svg.renderToCanvas(canvas)
            bitmap
        } catch (e: SVGParseException) {
            e.printStackTrace()
            null
        }
    }

    fun displayAsBitmap(svgString: String, imageView: ImageView) {
        val bitmap = svgStringToBitmap(svgString, 500, 500)
        imageView.setImageBitmap(bitmap)
    }
}
```

### 6. Custom Drawable from SVG String

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {

    private var svg: SVG? = null

    init {
        try {
            svg = SVG.getFromString(svgString)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
    }

    override fun draw(canvas: Canvas) {
        svg?.let {
            it.documentWidth = bounds.width().toFloat()
            it.documentHeight = bounds.height().toFloat()
            it.renderToCanvas(canvas)
        }
    }

    override fun setAlpha(alpha: Int) {
        // Implement if needed
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        // Implement if needed
    }

    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// Usage
class CustomDrawableActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val svgString = """
            <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
                <polygon points="50,10 90,90 10,90" fill="green" />
            </svg>
        """.trimIndent()

        val imageView = findViewById<ImageView>(R.id.imageView)
        imageView.setImageDrawable(SvgDrawable(svgString))
    }
}
```

### 7. Jetpack Compose Implementation

```kotlin
// Using Coil in Compose
@Composable
fun SvgImage(svgString: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current

    val imageLoader = remember {
        ImageLoader.Builder(context)
            .components {
                add(SvgDecoder.Factory())
            }
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

// Using AndroidSVG with Canvas
@Composable
fun SvgFromString(svgString: String, modifier: Modifier = Modifier) {
    var svgDrawable by remember { mutableStateOf<Drawable?>(null) }

    LaunchedEffect(svgString) {
        withContext(Dispatchers.IO) {
            try {
                val svg = SVG.getFromString(svgString)
                val pictureDrawable = PictureDrawable(svg.renderToPicture())
                svgDrawable = pictureDrawable
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    Canvas(modifier = modifier) {
        svgDrawable?.let { drawable ->
            drawable.setBounds(0, 0, size.width.toInt(), size.height.toInt())
            drawIntoCanvas { canvas ->
                drawable.draw(canvas.nativeCanvas)
            }
        }
    }
}

// Usage
@Composable
fun SvgScreen() {
    val svgString = """
        <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="purple" />
        </svg>
    """.trimIndent()

    Column {
        SvgImage(
            svgString = svgString,
            modifier = Modifier.size(200.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))

        SvgFromString(
            svgString = svgString,
            modifier = Modifier.size(200.dp)
        )
    }
}
```

### 8. Network SVG Loading

```kotlin
class NetworkSvgLoader(private val context: Context) {

    suspend fun loadSvgFromUrl(url: String): String? = withContext(Dispatchers.IO) {
        try {
            val connection = URL(url).openConnection() as HttpURLConnection
            connection.inputStream.bufferedReader().use { it.readText() }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    suspend fun displaySvgFromUrl(url: String, imageView: ImageView) {
        val svgString = loadSvgFromUrl(url)
        svgString?.let {
            withContext(Dispatchers.Main) {
                try {
                    val svg = SVG.getFromString(it)
                    val drawable = PictureDrawable(svg.renderToPicture())
                    imageView.setImageDrawable(drawable)
                } catch (e: SVGParseException) {
                    e.printStackTrace()
                }
            }
        }
    }
}

// Usage with coroutines
class SvgNetworkActivity : AppCompatActivity() {
    private val svgLoader = NetworkSvgLoader(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val imageView = findViewById<ImageView>(R.id.imageView)

        lifecycleScope.launch {
            svgLoader.displaySvgFromUrl(
                "https://example.com/image.svg",
                imageView
            )
        }
    }
}
```

### Comparison of Approaches

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| AndroidSVG | Simple, lightweight | Manual setup | Direct SVG strings |
| Coil + SVG | Modern, caching | Additional dependency | Network SVGs |
| Glide + SVG | Robust, familiar | More setup | Existing Glide projects |
| File-based | Standard approach | I/O overhead | Large SVGs |
| Bitmap conversion | Compatible everywhere | Memory intensive | Static images |

### Best Practices

1. **Use AndroidSVG** for simple SVG string display
2. **Use Coil** for modern apps with network SVGs
3. **Cache converted images** for better performance
4. **Handle errors gracefully** - SVG parsing can fail
5. **Consider memory usage** when converting to bitmap
6. **Use appropriate image size** to avoid scaling issues

## Ответ (RU)

Существует несколько подходов к отображению SVG-строки как векторного изображения в Android. Методы варьируются от использования специализированных библиотек до преобразования SVG в нативные Android vector drawables.

### 1. Использование библиотеки AndroidSVG

Наиболее прямой подход для работы с SVG-строками.

```kotlin
// Добавить зависимость
// implementation 'com.caverock:androidsvg-aar:1.4'

class SvgActivity : AppCompatActivity() {

    private fun displaySvgFromString(svgString: String, imageView: ImageView) {
        try {
            val svg = SVG.getFromString(svgString)
            val drawable = PictureDrawable(svg.renderToPicture())
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
    }

    // С установкой размеров
    private fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
        try {
            val svg = SVG.getFromString(svgString)
            svg.documentWidth = width.toFloat()
            svg.documentHeight = height.toFloat()

            val picture = svg.renderToPicture(width, height)
            val drawable = PictureDrawable(picture)
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
    }
}
```

### 2. Использование Coil с SVG декодером

Современная библиотека загрузки изображений с поддержкой SVG.

```kotlin
// Добавить зависимости
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

class CoilSvgActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Настройка ImageLoader с поддержкой SVG
        val imageLoader = ImageLoader.Builder(this)
            .components {
                add(SvgDecoder.Factory())
            }
            .build()

        val svgString = """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="200" height="200" fill="red" />
                <circle cx="100" cy="100" r="50" fill="yellow" />
            </svg>
        """.trimIndent()

        // Преобразовать строку в ByteArray
        val svgBytes = svgString.toByteArray()

        // Загрузить SVG из байтов
        val request = ImageRequest.Builder(this)
            .data(svgBytes)
            .target(imageView)
            .build()

        imageLoader.enqueue(request)
    }
}
```

### 3. Использование Glide с SVG модулем

```kotlin
// Добавить зависимости
// implementation 'com.github.bumptech.glide:glide:4.16.0'
// implementation 'com.caverock:androidsvg-aar:1.4'

// Создать SVG декодер для Glide
class SvgDecoder : ResourceDecoder<InputStream, SVG> {
    override fun handles(source: InputStream, options: Options): Boolean = true

    override fun decode(
        source: InputStream,
        width: Int,
        height: Int,
        options: Options
    ): Resource<SVG>? {
        return try {
            val svg = SVG.getFromInputStream(source)
            SimpleResource(svg)
        } catch (e: SVGParseException) {
            null
        }
    }
}

// Использование
class GlideSvgActivity : AppCompatActivity() {

    private fun loadSvgString(svgString: String, imageView: ImageView) {
        val svgBytes = svgString.toByteArray()

        Glide.with(this)
            .`as`(PictureDrawable::class.java)
            .load(svgBytes)
            .into(imageView)
    }
}
```

### 4. Сохранение в файл и загрузка

```kotlin
class SvgFileActivity : AppCompatActivity() {

    private fun saveSvgStringToFile(svgString: String): File {
        val file = File(cacheDir, "temp_svg_${System.currentTimeMillis()}.svg")
        file.writeText(svgString)
        return file
    }

    private fun loadSvgFromFile(file: File, imageView: ImageView) {
        try {
            val svg = SVG.getFromInputStream(file.inputStream())
            val drawable = PictureDrawable(svg.renderToPicture())
            imageView.setImageDrawable(drawable)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    // Полный процесс
    private fun displaySvgString(svgString: String, imageView: ImageView) {
        val file = saveSvgStringToFile(svgString)
        loadSvgFromFile(file, imageView)
        file.delete() // Очистка
    }
}
```

### 5. Преобразование SVG в Bitmap

```kotlin
class SvgToBitmapConverter {

    fun svgStringToBitmap(svgString: String, width: Int, height: Int): Bitmap? {
        return try {
            val svg = SVG.getFromString(svgString)

            val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bitmap)

            svg.documentWidth = width.toFloat()
            svg.documentHeight = height.toFloat()

            svg.renderToCanvas(canvas)
            bitmap
        } catch (e: SVGParseException) {
            e.printStackTrace()
            null
        }
    }

    fun displayAsBitmap(svgString: String, imageView: ImageView) {
        val bitmap = svgStringToBitmap(svgString, 500, 500)
        imageView.setImageBitmap(bitmap)
    }
}
```

### 6. Пользовательский Drawable из SVG строки

```kotlin
class SvgDrawable(private val svgString: String) : Drawable() {

    private var svg: SVG? = null

    init {
        try {
            svg = SVG.getFromString(svgString)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
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
```

### 7. Jetpack Compose реализация

```kotlin
// Использование Coil в Compose
@Composable
fun SvgImage(svgString: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current

    val imageLoader = remember {
        ImageLoader.Builder(context)
            .components {
                add(SvgDecoder.Factory())
            }
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

// Использование AndroidSVG с Canvas
@Composable
fun SvgFromString(svgString: String, modifier: Modifier = Modifier) {
    var svgDrawable by remember { mutableStateOf<Drawable?>(null) }

    LaunchedEffect(svgString) {
        withContext(Dispatchers.IO) {
            try {
                val svg = SVG.getFromString(svgString)
                val pictureDrawable = PictureDrawable(svg.renderToPicture())
                svgDrawable = pictureDrawable
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    Canvas(modifier = modifier) {
        svgDrawable?.let { drawable ->
            drawable.setBounds(0, 0, size.width.toInt(), size.height.toInt())
            drawIntoCanvas { canvas ->
                drawable.draw(canvas.nativeCanvas)
            }
        }
    }
}
```

### 8. Загрузка SVG из сети

```kotlin
class NetworkSvgLoader(private val context: Context) {

    suspend fun loadSvgFromUrl(url: String): String? = withContext(Dispatchers.IO) {
        try {
            val connection = URL(url).openConnection() as HttpURLConnection
            connection.inputStream.bufferedReader().use { it.readText() }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    suspend fun displaySvgFromUrl(url: String, imageView: ImageView) {
        val svgString = loadSvgFromUrl(url)
        svgString?.let {
            withContext(Dispatchers.Main) {
                try {
                    val svg = SVG.getFromString(it)
                    val drawable = PictureDrawable(svg.renderToPicture())
                    imageView.setImageDrawable(drawable)
                } catch (e: SVGParseException) {
                    e.printStackTrace()
                }
            }
        }
    }
}
```

### Сравнение подходов

| Подход | Преимущества | Недостатки | Лучше всего для |
|--------|--------------|------------|-----------------|
| AndroidSVG | Простой, легковесный | Ручная настройка | Прямые SVG строки |
| Coil + SVG | Современный, кеширование | Дополнительная зависимость | Сетевые SVG |
| Glide + SVG | Надежный, знакомый | Больше настройки | Существующие Glide проекты |
| Файловый подход | Стандартный подход | Накладные расходы на I/O | Большие SVG |
| Преобразование в Bitmap | Совместимо везде | Интенсивное использование памяти | Статические изображения |

### Лучшие практики

1. **Используйте AndroidSVG** для простого отображения SVG строк
2. **Используйте Coil** для современных приложений с сетевыми SVG
3. **Кешируйте преобразованные изображения** для лучшей производительности
4. **Обрабатывайте ошибки корректно** - парсинг SVG может завершиться неудачей
5. **Учитывайте использование памяти** при преобразовании в bitmap
6. **Используйте соответствующий размер изображения** чтобы избежать проблем масштабирования
