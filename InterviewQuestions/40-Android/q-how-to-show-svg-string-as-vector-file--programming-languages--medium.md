---
id: 20251017-105349
title: "How To Show Svg String As Vector File / Как показать SVG строку как векторный файл"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [languages, difficulty/medium]
---
# Как SVG-строку показать в виде векторного файла?

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

---

# Как SVG-строку показать в виде векторного файла

## Ответ (RU)

Существует несколько способов отображения SVG-строки как векторного изображения в Android, от использования специализированных библиотек до конвертации в нативные Android vector drawable.

### Основные подходы

1. **AndroidSVG библиотека** - прямая работа с SVG строками
2. **Coil с SVG декодером** - современная загрузка изображений
3. **Glide с SVG модулем** - интеграция с популярной библиотекой
4. **Сохранение в файл** - классический подход
5. **Конвертация в Bitmap** - совместимость везде
6. **Custom Drawable** - полный контроль
7. **Jetpack Compose** - декларативный UI

### 1. AndroidSVG библиотека

Самый прямой подход для работы с SVG строками.

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

    // Альтернатива: указание размеров
    private fun displaySvgWithSize(svgString: String, imageView: ImageView, width: Int, height: Int) {
        try {
            val svg = SVG.getFromString(svgString)

            // Установка размеров SVG документа
            svg.documentWidth = width.toFloat()
            svg.documentHeight = height.toFloat()

            val picture = svg.renderToPicture(width, height)
            val drawable = PictureDrawable(picture)
            imageView.setImageDrawable(drawable)
        } catch (e: SVGParseException) {
            e.printStackTrace()
        }
    }

    // Пример использования
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

**Преимущества:**
- Прямая работа со строками
- Легкая интеграция
- Хорошая производительность

**Недостатки:**
- Дополнительная библиотека
- Ручное управление

### 2. Coil с SVG декодером

Современная библиотека загрузки изображений с поддержкой SVG.

```kotlin
// Добавить зависимости
// implementation "io.coil-kt:coil:2.5.0"
// implementation "io.coil-kt:coil-svg:2.5.0"

class CoilSvgActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Настройка ImageLoader с поддержкой SVG
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

        // Конвертация строки в ByteArray
        val svgBytes = svgString.toByteArray()

        // Загрузка SVG из байтов
        val request = ImageRequest.Builder(this)
            .data(svgBytes)
            .target(imageView)
            .build()

        imageLoader.enqueue(request)
    }

    // Загрузка SVG из URL
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

**Преимущества:**
- Современный API
- Кэширование из коробки
- Coroutines поддержка

### 3. Конвертация в Bitmap

Универсальный подход для совместимости.

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

### 4. Custom Drawable из SVG строки

Полный контроль над отрисовкой.

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
        // Реализовать при необходимости
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        // Реализовать при необходимости
    }

    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}

// Использование
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

### 5. Jetpack Compose реализация

Для современного декларативного UI.

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

// Использование
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

### 6. Загрузка SVG из сети

Работа с удаленными SVG файлами.

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

// Использование с корутинами
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

### Сравнение подходов

| Подход | Плюсы | Минусы | Лучше для |
|----------|------|------|----------|
| AndroidSVG | Простота, легковесность | Ручная настройка | Прямые SVG строки |
| Coil + SVG | Современный, кэширование | Доп. зависимость | Сетевые SVG |
| Glide + SVG | Надежный, знакомый | Больше настройки | Существующие Glide проекты |
| Файловый | Стандартный подход | Overhead I/O | Большие SVG |
| Bitmap конвертация | Совместимость везде | Затраты памяти | Статические изображения |
| Custom Drawable | Полный контроль | Больше кода | Специфичные требования |
| Compose | Декларативный | Требует Compose | Современные UI |

### Лучшие практики

**1. Выбор библиотеки:**
```kotlin
// Для простых случаев - AndroidSVG
fun simple(svgString: String, view: ImageView) {
    val svg = SVG.getFromString(svgString)
    view.setImageDrawable(PictureDrawable(svg.renderToPicture()))
}

// Для современных приложений - Coil
fun modern(svgUrl: String, view: ImageView) {
    view.load(svgUrl) {
        decoder(SvgDecoder.Factory())
    }
}
```

**2. Обработка ошибок:**
```kotlin
fun safeSvgLoad(svgString: String, imageView: ImageView) {
    try {
        val svg = SVG.getFromString(svgString)
        val drawable = PictureDrawable(svg.renderToPicture())
        imageView.setImageDrawable(drawable)
    } catch (e: SVGParseException) {
        Log.e("SVG", "Parsing error: ${e.message}")
        // Показать placeholder
        imageView.setImageResource(R.drawable.placeholder)
    } catch (e: Exception) {
        Log.e("SVG", "Unknown error: ${e.message}")
        imageView.setImageResource(R.drawable.error)
    }
}
```

**3. Оптимизация памяти:**
```kotlin
class OptimizedSvgLoader {
    // Кэширование загруженных SVG
    private val cache = LruCache<String, PictureDrawable>(10)

    fun loadSvg(svgString: String, imageView: ImageView) {
        val cacheKey = svgString.hashCode().toString()

        val cached = cache.get(cacheKey)
        if (cached != null) {
            imageView.setImageDrawable(cached)
            return
        }

        try {
            val svg = SVG.getFromString(svgString)
            val drawable = PictureDrawable(svg.renderToPicture())
            cache.put(cacheKey, drawable)
            imageView.setImageDrawable(drawable)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
```

**4. Размеры и масштабирование:**
```kotlin
fun loadSvgWithProperSize(
    svgString: String,
    imageView: ImageView,
    targetWidth: Int,
    targetHeight: Int
) {
    try {
        val svg = SVG.getFromString(svgString)

        // Установка целевых размеров
        svg.documentWidth = targetWidth.toFloat()
        svg.documentHeight = targetHeight.toFloat()

        // Создание Picture с указанными размерами
        val picture = svg.renderToPicture(targetWidth, targetHeight)
        val drawable = PictureDrawable(picture)

        imageView.setImageDrawable(drawable)
    } catch (e: Exception) {
        e.printStackTrace()
    }
}
```

**5. ViewModel интеграция:**
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
            } catch (e: Exception) {
                _svgDrawable.postValue(null)
            }
        }
    }
}

// Использование в Activity
class SvgActivity : AppCompatActivity() {
    private val viewModel: SvgViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val imageView = findViewById<ImageView>(R.id.imageView)

        viewModel.svgDrawable.observe(this) { drawable ->
            imageView.setImageDrawable(drawable)
        }

        viewModel.loadSvg(svgString)
    }
}
```

### Резюме

**Рекомендации по выбору:**

1. **AndroidSVG** - для прямой работы с SVG строками, простая интеграция
2. **Coil** - для современных приложений с сетевыми SVG, отличное кэширование
3. **Кэшируйте** преобразованные изображения для лучшей производительности
4. **Обрабатывайте ошибки** - парсинг SVG может завершиться неудачей
5. **Учитывайте память** при конвертации в bitmap
6. **Используйте соответствующие размеры** для избежания проблем масштабирования
7. **Для Compose** используйте Coil или custom Canvas решение

**Зависимости для Gradle:**
```gradle
// AndroidSVG
implementation 'com.caverock:androidsvg-aar:1.4'

// Coil с SVG
implementation "io.coil-kt:coil:2.5.0"
implementation "io.coil-kt:coil-svg:2.5.0"

// Glide (если используется)
implementation 'com.github.bumptech.glide:glide:4.16.0'
```
