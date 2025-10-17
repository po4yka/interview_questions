---
id: "20251015082237508"
title: "Vector Graphics Animations / Анимации векторной графики"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [vector-graphics, animated-vector-drawable, svg, animations, graphics, difficulty/medium]
---
# Vector Graphics and Animated Vector Drawables

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How do you work with vector graphics and animated vector drawables in Android? What are the best practices for SVG import, path morphing, and complex animations? How do you optimize vector drawable performance?

## Answer (EN)
Vector graphics provide resolution-independent images that scale perfectly across different screen densities. Android's VectorDrawable and AnimatedVectorDrawable enable complex animations and transformations without bitmap resources.

#### 1. VectorDrawable Basics

**Creating Vector Drawable XML:**
```xml
<!-- res/drawable/ic_heart.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal">

    <path
        android:name="heart_path"
        android:pathData="M12,21.35l-1.45,-1.32C5.4,15.36 2,12.28 2,8.5 2,5.42 4.42,3 7.5,3c1.74,0 3.41,0.81 4.5,2.09C13.09,3.81 14.76,3 16.5,3 19.58,3 22,5.42 22,8.5c0,3.78 -3.4,6.86 -8.55,11.54L12,21.35z"
        android:fillColor="@android:color/white"/>
</vector>
```

**Loading Vector Drawable in Code:**
```kotlin
class VectorDrawableManager {

    /**
     * Load vector drawable programmatically
     */
    fun loadVectorDrawable(context: Context, @DrawableRes resId: Int): Drawable? {
        return ContextCompat.getDrawable(context, resId)
    }

    /**
     * Tint vector drawable
     */
    fun tintVectorDrawable(
        context: Context,
        @DrawableRes resId: Int,
        @ColorInt color: Int
    ): Drawable? {
        val drawable = ContextCompat.getDrawable(context, resId)
        drawable?.let {
            DrawableCompat.setTint(it, color)
        }
        return drawable
    }

    /**
     * Create vector drawable programmatically
     */
    fun createVectorDrawable(
        context: Context,
        width: Int,
        height: Int,
        viewportWidth: Float,
        viewportHeight: Float,
        pathData: String,
        @ColorInt fillColor: Int
    ): VectorDrawableCompat {
        return VectorDrawableCompat.create(
            context.resources,
            createVectorXml(width, height, viewportWidth, viewportHeight, pathData, fillColor),
            context.theme
        )!!
    }

    private fun createVectorXml(
        width: Int,
        height: Int,
        viewportWidth: Float,
        viewportHeight: Float,
        pathData: String,
        fillColor: Int
    ): Int {
        // This would require runtime XML generation or using VectorDrawableCompat.create
        // with pre-created resources
        return 0
    }

    /**
     * Convert SVG path data to Android path
     */
    fun parseSVGPath(svgPath: String): Path {
        val path = Path()
        try {
            PathParser.createPathFromPathData(svgPath)?.let {
                path.set(it)
            }
        } catch (e: Exception) {
            Log.e("VectorDrawable", "Failed to parse SVG path", e)
        }
        return path
    }

    /**
     * Scale vector drawable to specific size
     */
    fun scaleVectorDrawable(
        drawable: Drawable,
        width: Int,
        height: Int
    ): Bitmap {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        drawable.setBounds(0, 0, canvas.width, canvas.height)
        drawable.draw(canvas)

        return bitmap
    }
}
```

#### 2. AnimatedVectorDrawable

**Defining Animated Vector Drawable:**
```xml
<!-- res/drawable/avd_heart_fill.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_heart">

    <target
        android:name="heart_path"
        android:animation="@animator/heart_fill_animation" />

</animated-vector>

<!-- res/animator/heart_fill_animation.xml -->
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <objectAnimator
        android:propertyName="fillAlpha"
        android:duration="300"
        android:valueFrom="0.0"
        android:valueTo="1.0"
        android:interpolator="@android:interpolator/fast_out_slow_in" />

    <objectAnimator
        android:propertyName="strokeWidth"
        android:duration="300"
        android:valueFrom="2"
        android:valueTo="0"
        android:interpolator="@android:interpolator/fast_out_slow_in" />
</set>
```

**Path Morphing Animation:**
```xml
<!-- res/drawable/ic_play_pause.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="48"
    android:viewportHeight="48">

    <path
        android:name="play_pause_path"
        android:pathData="M16,12L16,36L32,24Z"
        android:fillColor="#FFFFFF"/>
</vector>

<!-- res/drawable/avd_play_to_pause.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_play_pause">

    <target
        android:name="play_pause_path"
        android:animation="@animator/play_to_pause_animation" />

</animated-vector>

<!-- res/animator/play_to_pause_animation.xml -->
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <objectAnimator
        android:propertyName="pathData"
        android:duration="300"
        android:valueFrom="M16,12L16,36L32,24Z"
        android:valueTo="M14,14L14,34L18,34L18,14ZM30,14L30,34L34,34L34,14Z"
        android:valueType="pathType"
        android:interpolator="@android:interpolator/fast_out_slow_in" />
</set>
```

**Playing Animated Vector Drawable:**
```kotlin
class AnimatedVectorManager(private val context: Context) {

    /**
     * Play animated vector drawable
     */
    fun playAnimation(
        imageView: ImageView,
        @DrawableRes animatedVectorRes: Int
    ) {
        val avd = AnimatedVectorDrawableCompat.create(context, animatedVectorRes)
        imageView.setImageDrawable(avd)
        avd?.start()
    }

    /**
     * Play animation with callback
     */
    fun playAnimationWithCallback(
        imageView: ImageView,
        @DrawableRes animatedVectorRes: Int,
        onAnimationEnd: () -> Unit
    ) {
        val avd = AnimatedVectorDrawableCompat.create(context, animatedVectorRes)
        imageView.setImageDrawable(avd)

        // Register animation callback (API 23+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            (avd as? AnimatedVectorDrawable)?.registerAnimationCallback(
                object : Animatable2.AnimationCallback() {
                    override fun onAnimationEnd(drawable: Drawable?) {
                        onAnimationEnd()
                    }
                }
            )
        }

        avd?.start()
    }

    /**
     * Create reversible animation
     */
    fun createReversibleAnimation(
        imageView: ImageView,
        @DrawableRes forwardRes: Int,
        @DrawableRes reverseRes: Int
    ): ReversibleAnimation {
        return ReversibleAnimation(context, imageView, forwardRes, reverseRes)
    }

    /**
     * Seek to specific frame (API 25+)
     */
    @RequiresApi(Build.VERSION_CODES.N)
    fun seekToFrame(
        avd: AnimatedVectorDrawable,
        progress: Float // 0.0 to 1.0
    ) {
        avd.reset()
        val totalDuration = getTotalDuration(avd)
        avd.start()
        // This is simplified - actual implementation would need to calculate frame time
    }

    private fun getTotalDuration(avd: AnimatedVectorDrawable): Long {
        // Calculate total animation duration from XML
        return 1000L // Placeholder
    }
}

class ReversibleAnimation(
    private val context: Context,
    private val imageView: ImageView,
    @DrawableRes private val forwardRes: Int,
    @DrawableRes private val reverseRes: Int
) {
    private var isForward = true

    fun toggle() {
        val res = if (isForward) forwardRes else reverseRes
        val avd = AnimatedVectorDrawableCompat.create(context, res)
        imageView.setImageDrawable(avd)
        avd?.start()
        isForward = !isForward
    }

    fun reset() {
        isForward = true
    }
}
```

#### 3. Complex Path Morphing

**Path Morphing Utilities:**
```kotlin
class PathMorphingUtils {

    /**
     * Check if two paths are compatible for morphing
     * Paths must have same number and type of commands
     */
    fun arePathsCompatible(path1: String, path2: String): Boolean {
        val commands1 = extractPathCommands(path1)
        val commands2 = extractPathCommands(path2)

        if (commands1.size != commands2.size) return false

        return commands1.zip(commands2).all { (cmd1, cmd2) ->
            cmd1.command == cmd2.command
        }
    }

    private fun extractPathCommands(pathData: String): List<PathCommand> {
        val commands = mutableListOf<PathCommand>()
        val regex = Regex("[MLHVCSQTAZmlhvcsqtaz][^MLHVCSQTAZmlhvcsqtaz]*")

        regex.findAll(pathData).forEach { match ->
            val commandStr = match.value
            val command = commandStr[0]
            val numbers = commandStr.substring(1)
                .trim()
                .split(Regex("[,\\s]+"))
                .filter { it.isNotEmpty() }
                .map { it.toFloatOrNull() ?: 0f }

            commands.add(PathCommand(command, numbers))
        }

        return commands
    }

    /**
     * Make paths compatible by adding intermediate points
     */
    fun makePathsCompatible(path1: String, path2: String): Pair<String, String> {
        val commands1 = extractPathCommands(path1)
        val commands2 = extractPathCommands(path2)

        // If already compatible, return as-is
        if (arePathsCompatible(path1, path2)) {
            return Pair(path1, path2)
        }

        // Add intermediate points to make paths compatible
        // This is simplified - full implementation would need sophisticated path analysis
        val normalized1 = normalizePath(commands1, commands2.size)
        val normalized2 = normalizePath(commands2, commands1.size)

        return Pair(
            pathCommandsToString(normalized1),
            pathCommandsToString(normalized2)
        )
    }

    private fun normalizePath(commands: List<PathCommand>, targetSize: Int): List<PathCommand> {
        // Normalize path to have target number of commands
        // This would involve subdividing or merging path segments
        return commands
    }

    private fun pathCommandsToString(commands: List<PathCommand>): String {
        return commands.joinToString(" ") { cmd ->
            "${cmd.command}${cmd.numbers.joinToString(",")}"
        }
    }

    /**
     * Interpolate between two paths
     */
    fun interpolatePaths(
        path1: String,
        path2: String,
        fraction: Float
    ): String {
        val commands1 = extractPathCommands(path1)
        val commands2 = extractPathCommands(path2)

        require(arePathsCompatible(path1, path2)) {
            "Paths must be compatible for interpolation"
        }

        val interpolated = commands1.zip(commands2).map { (cmd1, cmd2) ->
            val interpolatedNumbers = cmd1.numbers.zip(cmd2.numbers).map { (n1, n2) ->
                n1 + (n2 - n1) * fraction
            }
            PathCommand(cmd1.command, interpolatedNumbers)
        }

        return pathCommandsToString(interpolated)
    }

    data class PathCommand(
        val command: Char,
        val numbers: List<Float>
    )
}
```

**Programmatic Animation Creation:**
```kotlin
class ProgrammaticAnimatedVector(
    private val context: Context
) {

    /**
     * Create animated vector drawable programmatically
     */
    fun createMorphAnimation(
        width: Int,
        height: Int,
        startPath: String,
        endPath: String,
        duration: Long
    ): AnimatedVectorDrawableCompat {
        // Create base vector drawable
        val vectorXml = """
            <vector xmlns:android="http://schemas.android.com/apk/res/android"
                android:width="${width}dp"
                android:height="${height}dp"
                android:viewportWidth="$width"
                android:viewportHeight="$height">
                <path
                    android:name="morph_path"
                    android:pathData="$startPath"
                    android:fillColor="#FFFFFF"/>
            </vector>
        """.trimIndent()

        // Create animator
        val animatorXml = """
            <objectAnimator xmlns:android="http://schemas.android.com/apk/res/android"
                android:propertyName="pathData"
                android:duration="$duration"
                android:valueFrom="$startPath"
                android:valueTo="$endPath"
                android:valueType="pathType"
                android:interpolator="@android:interpolator/fast_out_slow_in" />
        """.trimIndent()

        // Create animated vector
        val avdXml = """
            <animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
                android:drawable="@drawable/vector">
                <target
                    android:name="morph_path"
                    android:animation="@animator/morph_animation" />
            </animated-vector>
        """.trimIndent()

        // Note: Actual implementation would need to create resources dynamically
        // or use VectorDrawableCompat API

        return createFromXml(avdXml)
    }

    private fun createFromXml(xml: String): AnimatedVectorDrawableCompat {
        // Parse XML and create AnimatedVectorDrawableCompat
        // This is simplified - actual implementation would use XmlPullParser
        return AnimatedVectorDrawableCompat.create(context, R.drawable.avd_placeholder)!!
    }

    /**
     * Create rotation animation
     */
    fun createRotationAnimation(
        vectorDrawable: VectorDrawableCompat,
        groupName: String,
        fromDegrees: Float,
        toDegrees: Float,
        duration: Long
    ): ObjectAnimator {
        return ObjectAnimator.ofFloat(
            vectorDrawable,
            "rotation",
            fromDegrees,
            toDegrees
        ).apply {
            this.duration = duration
            interpolator = LinearInterpolator()
            repeatCount = ObjectAnimator.INFINITE
        }
    }

    /**
     * Create trim path animation (drawing effect)
     */
    fun createTrimPathAnimation(
        duration: Long
    ): AnimatorSet {
        val trimStart = ObjectAnimator.ofFloat(0f, 0f).apply {
            this.duration = duration
        }

        val trimEnd = ObjectAnimator.ofFloat(0f, 1f).apply {
            this.duration = duration
        }

        return AnimatorSet().apply {
            playTogether(trimStart, trimEnd)
        }
    }
}
```

#### 4. SVG Import and Optimization

**SVG to VectorDrawable Conversion:**
```kotlin
class SVGImporter {

    /**
     * Import SVG file and convert to VectorDrawable XML
     */
    fun importSVG(svgContent: String): String {
        // Parse SVG
        val parser = SVGParser()
        val svg = parser.parse(svgContent)

        // Extract viewBox
        val viewBox = svg.viewBox ?: "0 0 24 24"
        val parts = viewBox.split(" ")
        val viewportWidth = parts[2].toFloatOrNull() ?: 24f
        val viewportHeight = parts[3].toFloatOrNull() ?: 24f

        // Convert SVG paths to Android path data
        val paths = svg.paths.map { svgPath ->
            convertSVGPath(svgPath)
        }

        // Generate VectorDrawable XML
        return generateVectorXML(
            width = 24,
            height = 24,
            viewportWidth = viewportWidth,
            viewportHeight = viewportHeight,
            paths = paths
        )
    }

    private fun convertSVGPath(svgPath: SVGPath): VectorPath {
        return VectorPath(
            name = svgPath.id ?: "path",
            pathData = svgPath.d,
            fillColor = svgPath.fill ?: "#000000",
            strokeColor = svgPath.stroke,
            strokeWidth = svgPath.strokeWidth ?: 0f,
            fillAlpha = svgPath.fillOpacity ?: 1f,
            strokeAlpha = svgPath.strokeOpacity ?: 1f
        )
    }

    private fun generateVectorXML(
        width: Int,
        height: Int,
        viewportWidth: Float,
        viewportHeight: Float,
        paths: List<VectorPath>
    ): String {
        val pathsXml = paths.joinToString("\n") { path ->
            """
                <path
                    android:name="${path.name}"
                    android:pathData="${path.pathData}"
                    android:fillColor="${path.fillColor}"
                    ${if (path.strokeColor != null) "android:strokeColor=\"${path.strokeColor}\"" else ""}
                    ${if (path.strokeWidth > 0) "android:strokeWidth=\"${path.strokeWidth}\"" else ""}
                    android:fillAlpha="${path.fillAlpha}"
                    android:strokeAlpha="${path.strokeAlpha}"/>
            """.trimIndent()
        }

        return """
            <vector xmlns:android="http://schemas.android.com/apk/res/android"
                android:width="${width}dp"
                android:height="${height}dp"
                android:viewportWidth="$viewportWidth"
                android:viewportHeight="$viewportHeight">
                $pathsXml
            </vector>
        """.trimIndent()
    }

    /**
     * Optimize vector drawable by simplifying paths
     */
    fun optimizeVectorDrawable(pathData: String, tolerance: Float = 1f): String {
        // Simplify path by removing unnecessary points
        val commands = PathMorphingUtils().extractPathCommands(pathData)

        val optimized = mutableListOf<PathMorphingUtils.PathCommand>()
        var lastPoint: PointF? = null

        commands.forEach { command ->
            when (command.command) {
                'M', 'm' -> {
                    optimized.add(command)
                    lastPoint = PointF(command.numbers[0], command.numbers[1])
                }
                'L', 'l' -> {
                    val point = PointF(command.numbers[0], command.numbers[1])
                    if (lastPoint == null || distance(lastPoint!!, point) > tolerance) {
                        optimized.add(command)
                        lastPoint = point
                    }
                }
                else -> optimized.add(command)
            }
        }

        return PathMorphingUtils().pathCommandsToString(optimized)
    }

    private fun distance(p1: PointF, p2: PointF): Float {
        val dx = p2.x - p1.x
        val dy = p2.y - p1.y
        return sqrt(dx * dx + dy * dy)
    }

    // Placeholder classes for SVG parsing
    data class SVG(val viewBox: String?, val paths: List<SVGPath>)
    data class SVGPath(
        val id: String?,
        val d: String,
        val fill: String?,
        val stroke: String?,
        val strokeWidth: Float?,
        val fillOpacity: Float?,
        val strokeOpacity: Float?
    )

    data class VectorPath(
        val name: String,
        val pathData: String,
        val fillColor: String,
        val strokeColor: String?,
        val strokeWidth: Float,
        val fillAlpha: Float,
        val strokeAlpha: Float
    )

    class SVGParser {
        fun parse(svgContent: String): SVG {
            // Parse SVG XML content
            // This is placeholder - actual implementation would use XmlPullParser
            return SVG(null, emptyList())
        }
    }
}
```

#### 5. Performance Optimization

**Vector Drawable Performance:**
```kotlin
class VectorDrawableOptimizer {

    /**
     * Cache vector drawables to avoid repeated inflation
     */
    private val drawableCache = LruCache<Int, Drawable>(50)

    fun getVectorDrawable(
        context: Context,
        @DrawableRes resId: Int
    ): Drawable? {
        return drawableCache.get(resId) ?: run {
            val drawable = ContextCompat.getDrawable(context, resId)
            drawable?.let { drawableCache.put(resId, it.mutate()) }
            drawable
        }
    }

    /**
     * Pre-rasterize complex vector drawables for better performance
     */
    fun rasterizeVectorDrawable(
        drawable: Drawable,
        width: Int,
        height: Int
    ): BitmapDrawable {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        drawable.setBounds(0, 0, width, height)
        drawable.draw(canvas)

        return BitmapDrawable(null, bitmap)
    }

    /**
     * Detect when to use rasterized version vs vector
     */
    fun shouldRasterize(
        drawable: Drawable,
        renderCount: Int,
        complexity: Int
    ): Boolean {
        // Rasterize if:
        // - Rendered frequently (e.g., in RecyclerView)
        // - Complex paths (many points)
        // - Animated frequently

        return renderCount > 10 || complexity > 100
    }

    /**
     * Measure vector drawable complexity
     */
    fun measureComplexity(pathData: String): Int {
        // Count number of commands and points
        return pathData.count { it in "MLHVCSQTAZmlhvcsqtaz" }
    }

    /**
     * Enable/disable hardware acceleration for specific view
     */
    fun optimizeForAnimation(imageView: ImageView, enable: Boolean) {
        if (enable) {
            // Enable hardware layers for smooth animation
            imageView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
        } else {
            // Disable after animation completes
            imageView.setLayerType(View.LAYER_TYPE_NONE, null)
        }
    }
}
```

**Compose Integration:**
```kotlin
@Composable
fun AnimatedVectorIcon(
    @DrawableRes animatedVectorRes: Int,
    contentDescription: String?,
    modifier: Modifier = Modifier,
    autoPlay: Boolean = true
) {
    val context = LocalContext.current
    val drawable = remember(animatedVectorRes) {
        AnimatedVectorDrawableCompat.create(context, animatedVectorRes)
    }

    DisposableEffect(drawable) {
        if (autoPlay) {
            drawable?.start()
        }

        onDispose {
            drawable?.stop()
        }
    }

    Image(
        painter = rememberDrawablePainter(drawable),
        contentDescription = contentDescription,
        modifier = modifier
    )
}

@Composable
fun rememberAnimatedVectorPainter(
    @DrawableRes resId: Int
): Painter {
    val context = LocalContext.current
    return remember(resId) {
        val drawable = AnimatedVectorDrawableCompat.create(context, resId)
        BitmapPainter(drawable?.let { drawableToBitmap(it) } ?: Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888).asImageBitmap())
    }
}

private fun drawableToBitmap(drawable: Drawable): ImageBitmap {
    val bitmap = Bitmap.createBitmap(
        drawable.intrinsicWidth,
        drawable.intrinsicHeight,
        Bitmap.Config.ARGB_8888
    )
    val canvas = Canvas(bitmap)
    drawable.setBounds(0, 0, canvas.width, canvas.height)
    drawable.draw(canvas)
    return bitmap.asImageBitmap()
}
```

### Best Practices

1. **Path Compatibility:**
   - Ensure paths have same number of commands for morphing
   - Use tools to normalize paths
   - Test morphing animations thoroughly

2. **Performance:**
   - Cache inflated drawables
   - Rasterize complex vectors for repeated use
   - Use hardware layers during animations
   - Measure complexity before deciding vector vs bitmap

3. **SVG Import:**
   - Use Android Studio's Vector Asset tool
   - Simplify paths before import
   - Remove unnecessary groups and transforms
   - Optimize path data

4. **Animation:**
   - Keep animations under 300-500ms
   - Use appropriate interpolators
   - Avoid animating too many paths simultaneously
   - Clean up animation callbacks

5. **Compatibility:**
   - Use VectorDrawableCompat for backward compatibility
   - Test on different API levels
   - Provide bitmap fallbacks for very old devices

### Common Pitfalls

1. **Incompatible paths for morphing** → Animation fails or looks broken
   - Normalize paths to have same structure

2. **Not caching vector drawables** → Repeated inflation overhead
   - Use LruCache for frequently used vectors

3. **Complex vectors in lists** → Scrolling jank
   - Rasterize complex vectors for RecyclerView items

4. **Forgetting to stop animations** → Memory leaks
   - Clean up in onPause/onDestroy

5. **Large viewport dimensions** → Memory issues
   - Keep viewport dimensions reasonable (24x24 for icons)

6. **Not using hardware layers** → Slow animations
   - Enable hardware layer during animation

### Summary

Vector graphics and AnimatedVectorDrawable provide scalable, animatable graphics for Android. Key features include path morphing for shape transitions, programmatic animation control, and SVG import capabilities. Proper optimization through caching, selective rasterization, and hardware acceleration ensures smooth performance even with complex vector graphics.

---



## Ответ (RU)
# Вопрос (RU)
Как работать с векторной графикой и анимированными векторными drawable в Android? Каковы лучшие практики для импорта SVG, морфинга путей и сложных анимаций? Как оптимизировать производительность векторных drawable?

## Ответ (RU)
Векторная графика обеспечивает независимые от разрешения изображения, которые идеально масштабируются для разных плотностей экрана. VectorDrawable и AnimatedVectorDrawable Android позволяют создавать сложные анимации и трансформации без bitmap ресурсов.

#### Основные концепции

**1. VectorDrawable:**
- Основан на SVG path синтаксисе
- Определяется в XML
- Поддерживает tint и theme attributes
- Масштабируется без потери качества

**2. AnimatedVectorDrawable:**
- Анимация свойств VectorDrawable
- Path morphing (трансформация путей)
- Rotation, scale, translation анимации
- Trim path для эффекта рисования

**3. Path Morphing:**
- Требует совместимых путей (одинаковое количество команд)
- Interpolation между start и end path
- Нормализация путей для совместимости

**4. Оптимизация:**
- Кеширование inflated drawable
- Растеризация для частого использования
- Hardware layers для анимаций
- Упрощение сложных путей

### Лучшие практики

1. **Совместимость путей:** Нормализация, одинаковая структура
2. **Производительность:** Кеширование, растеризация, hardware layers
3. **Импорт SVG:** Упрощение, оптимизация, Android Studio tools
4. **Анимации:** 300-500мс длительность, правильные интерполяторы
5. **Совместимость:** VectorDrawableCompat, тестирование на разных API

### Распространённые ошибки

1. Несовместимые пути для морфинга → сломанная анимация
2. Не кешировать векторы → накладные расходы на inflation
3. Сложные векторы в списках → лаги при скролле
4. Не останавливать анимации → утечки памяти
5. Большие viewport размеры → проблемы с памятью
6. Не использовать hardware layers → медленные анимации

### Резюме

Векторная графика и AnimatedVectorDrawable обеспечивают масштабируемую, анимируемую графику для Android. Ключевые возможности включают морфинг путей для переходов форм, программный контроль анимаций и возможности импорта SVG. Правильная оптимизация через кеширование, селективную растеризацию и аппаратное ускорение обеспечивает плавную производительность даже со сложной векторной графикой.
