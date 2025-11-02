---
id: android-432
title: "Vector Graphics Animations / Анимации векторной графики"
aliases: ["Vector Graphics Animations", "Анимации векторной графики"]
topic: android
subtopics: [ui-graphics, ui-animation, performance-rendering]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-graphics, c-animation-framework, q-canvas-custom-views--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/ui-graphics, android/ui-animation, android/performance-rendering, vector-graphics, animated-vector-drawable, difficulty/medium]
---

# Вопрос (RU)

Как работать с векторной графикой и AnimatedVectorDrawable в Android? Каковы лучшие практики для импорта SVG, морфинга путей и оптимизации производительности?

# Question (EN)

How do you work with vector graphics and AnimatedVectorDrawable in Android? What are the best practices for SVG import, path morphing, and performance optimization?

---

## Ответ (RU)

### Основные концепции

**VectorDrawable** — это XML-представление векторной графики на основе SVG path синтаксиса. Обеспечивает независимость от разрешения экрана и минимальный размер APK без bitmap ресурсов для разных плотностей.

**AnimatedVectorDrawable** позволяет анимировать свойства VectorDrawable:
- **Path morphing** — трансформация путей (требует совместимых путей с одинаковым количеством команд)
- **Rotation, scale, translation** — трансформация групп
- **Trim path** — эффект рисования линии
- **Fill/stroke alpha** — анимация прозрачности

**Ключевые преимущества**:
- Масштабируются без потери качества
- Малый размер файла (~1-5 КБ vs. 10-50 КБ для PNG hdpi/xhdpi/xxhdpi)
- Поддержка tinting и theme attributes
- Плавные анимации без промежуточных кадров

### Основные примеры

**1. VectorDrawable с тематизацией:**

```xml
<!-- res/drawable/ic_heart.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal"> <!-- ✅ Theme-aware tinting -->

    <path
        android:name="heart_path"
        android:pathData="M12,21.35l-1.45,-1.32C5.4,15.36 2,12.28 2,8.5..."
        android:fillColor="@android:color/white"/>
</vector>
```

**2. AnimatedVectorDrawable с path morphing:**

```xml
<!-- res/drawable/avd_play_to_pause.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_play_pause">
    <target
        android:name="play_pause_path"
        android:animation="@animator/morph_animation" />
</animated-vector>

<!-- res/animator/morph_animation.xml -->
<objectAnimator xmlns:android="http://schemas.android.com/apk/res/android"
    android:propertyName="pathData"
    android:duration="300"
    android:valueFrom="M16,12L16,36L32,24Z"
    android:valueTo="M14,14L14,34L18,34L18,14ZM30,14L30,34L34,34L34,14Z"
    android:valueType="pathType"
    android:interpolator="@android:interpolator/fast_out_slow_in" />
```

**3. Управление анимацией в коде:**

```kotlin
class AnimatedVectorManager {
    fun playAnimation(imageView: ImageView, @DrawableRes resId: Int) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)
        avd?.start()
    }

    // ✅ Proper cleanup with callbacks
    fun playWithCallback(
        imageView: ImageView,
        @DrawableRes resId: Int,
        onEnd: () -> Unit
    ) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            (avd as? AnimatedVectorDrawable)?.registerAnimationCallback(
                object : Animatable2.AnimationCallback() {
                    override fun onAnimationEnd(drawable: Drawable?) {
                        onEnd()
                    }
                }
            )
        }
        avd?.start()
    }
}
```

**4. Path morphing совместимость:**

```kotlin
// ❌ Incompatible paths - different command counts
val path1 = "M10,10L20,20"           // 2 commands
val path2 = "M10,10L15,15L20,20"     // 3 commands

// ✅ Compatible paths - same command structure
val path1 = "M10,10L20,20L30,10Z"
val path2 = "M10,15L20,25L30,15Z"
```

### Оптимизация производительности

**1. Кеширование для повторного использования:**

```kotlin
class VectorDrawableCache {
    private val cache = LruCache<Int, Drawable>(50)

    fun get(context: Context, @DrawableRes resId: Int): Drawable? {
        return cache.get(resId) ?: run {
            val drawable = ContextCompat.getDrawable(context, resId)
            drawable?.let { cache.put(resId, it.mutate()) }
            drawable
        }
    }
}
```

**2. Растеризация для сложных векторов в списках:**

```kotlin
// ✅ Rasterize complex vectors in RecyclerView
fun rasterizeIfComplex(drawable: Drawable, size: Int): Drawable {
    val complexity = measureComplexity(drawable)

    return if (complexity > 100) {  // Many path commands
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, size, size)
        drawable.draw(canvas)
        BitmapDrawable(null, bitmap)
    } else {
        drawable
    }
}

fun measureComplexity(drawable: Drawable): Int {
    // Count path commands from XML
    // M, L, C, Z commands = complexity
    return 0 // Simplified
}
```

**3. Hardware layer для анимаций:**

```kotlin
fun animateWithHardwareLayer(imageView: ImageView, avd: AnimatedVectorDrawableCompat) {
    imageView.setLayerType(View.LAYER_TYPE_HARDWARE, null)  // ✅ Enable

    avd.registerAnimationCallback(object : Animatable2Compat.AnimationCallback() {
        override fun onAnimationEnd(drawable: Drawable?) {
            imageView.setLayerType(View.LAYER_TYPE_NONE, null)  // ✅ Disable after
        }
    })

    avd.start()
}
```

### Compose интеграция

```kotlin
@Composable
fun AnimatedVectorIcon(
    @DrawableRes resId: Int,
    contentDescription: String?,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val drawable = remember(resId) {
        AnimatedVectorDrawableCompat.create(context, resId)
    }

    DisposableEffect(drawable) {
        drawable?.start()
        onDispose {
            drawable?.stop()  // ✅ Cleanup
        }
    }

    Image(
        painter = rememberDrawablePainter(drawable),
        contentDescription = contentDescription,
        modifier = modifier
    )
}
```

### Лучшие практики

1. **Path morphing**: используйте инструменты для нормализации путей (Android Studio Vector Asset Studio, svg-path-morph)
2. **Performance**: кешируйте inflated drawable, растеризуйте сложные векторы для RecyclerView, используйте hardware layers
3. **SVG import**: импортируйте через Android Studio → Vector Asset → упростите пути → оптимизируйте viewport
4. **Animation**: длительность 200-400мс, используйте FastOutSlowInInterpolator, избегайте одновременной анимации >3 путей
5. **Compatibility**: VectorDrawableCompat для backward compatibility, тестируйте на API 21+

### Распространённые ошибки

1. **Несовместимые пути** → сломанный морфинг (нормализуйте структуру команд)
2. **Отсутствие кеширования** → repeated inflation overhead (используйте LruCache)
3. **Сложные векторы в списках** → scrolling jank (растеризуйте)
4. **Незакрытые анимации** → memory leaks (cleanup в onDispose/onDestroy)
5. **Большие viewport** → memory issues (используйте 24x24 для иконок)

---

## Answer (EN)

### Core Concepts

**VectorDrawable** is an XML representation of vector graphics based on SVG path syntax. It provides resolution independence and minimal APK size without bitmap resources for different densities.

**AnimatedVectorDrawable** enables animating VectorDrawable properties:
- **Path morphing** — shape transitions (requires compatible paths with same command count)
- **Rotation, scale, translation** — group transformations
- **Trim path** — line drawing effects
- **Fill/stroke alpha** — opacity animations

**Key advantages**:
- Scale without quality loss
- Small file size (~1-5 KB vs. 10-50 KB for PNG hdpi/xhdpi/xxhdpi)
- Support for tinting and theme attributes
- Smooth animations without intermediate frames

### Essential Examples

**1. VectorDrawable with theming:**

```xml
<!-- res/drawable/ic_heart.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal"> <!-- ✅ Theme-aware tinting -->

    <path
        android:name="heart_path"
        android:pathData="M12,21.35l-1.45,-1.32C5.4,15.36 2,12.28 2,8.5..."
        android:fillColor="@android:color/white"/>
</vector>
```

**2. AnimatedVectorDrawable with path morphing:**

```xml
<!-- res/drawable/avd_play_to_pause.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_play_pause">
    <target
        android:name="play_pause_path"
        android:animation="@animator/morph_animation" />
</animated-vector>

<!-- res/animator/morph_animation.xml -->
<objectAnimator xmlns:android="http://schemas.android.com/apk/res/android"
    android:propertyName="pathData"
    android:duration="300"
    android:valueFrom="M16,12L16,36L32,24Z"
    android:valueTo="M14,14L14,34L18,34L18,14ZM30,14L30,34L34,34L34,14Z"
    android:valueType="pathType"
    android:interpolator="@android:interpolator/fast_out_slow_in" />
```

**3. Animation control in code:**

```kotlin
class AnimatedVectorManager {
    fun playAnimation(imageView: ImageView, @DrawableRes resId: Int) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)
        avd?.start()
    }

    // ✅ Proper cleanup with callbacks
    fun playWithCallback(
        imageView: ImageView,
        @DrawableRes resId: Int,
        onEnd: () -> Unit
    ) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            (avd as? AnimatedVectorDrawable)?.registerAnimationCallback(
                object : Animatable2.AnimationCallback() {
                    override fun onAnimationEnd(drawable: Drawable?) {
                        onEnd()
                    }
                }
            )
        }
        avd?.start()
    }
}
```

**4. Path morphing compatibility:**

```kotlin
// ❌ Incompatible paths - different command counts
val path1 = "M10,10L20,20"           // 2 commands
val path2 = "M10,10L15,15L20,20"     // 3 commands

// ✅ Compatible paths - same command structure
val path1 = "M10,10L20,20L30,10Z"
val path2 = "M10,15L20,25L30,15Z"
```

### Performance Optimization

**1. Caching for reuse:**

```kotlin
class VectorDrawableCache {
    private val cache = LruCache<Int, Drawable>(50)

    fun get(context: Context, @DrawableRes resId: Int): Drawable? {
        return cache.get(resId) ?: run {
            val drawable = ContextCompat.getDrawable(context, resId)
            drawable?.let { cache.put(resId, it.mutate()) }
            drawable
        }
    }
}
```

**2. Rasterization for complex vectors in lists:**

```kotlin
// ✅ Rasterize complex vectors in RecyclerView
fun rasterizeIfComplex(drawable: Drawable, size: Int): Drawable {
    val complexity = measureComplexity(drawable)

    return if (complexity > 100) {  // Many path commands
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, size, size)
        drawable.draw(canvas)
        BitmapDrawable(null, bitmap)
    } else {
        drawable
    }
}

fun measureComplexity(drawable: Drawable): Int {
    // Count path commands from XML
    // M, L, C, Z commands = complexity
    return 0 // Simplified
}
```

**3. Hardware layer for animations:**

```kotlin
fun animateWithHardwareLayer(imageView: ImageView, avd: AnimatedVectorDrawableCompat) {
    imageView.setLayerType(View.LAYER_TYPE_HARDWARE, null)  // ✅ Enable

    avd.registerAnimationCallback(object : Animatable2Compat.AnimationCallback() {
        override fun onAnimationEnd(drawable: Drawable?) {
            imageView.setLayerType(View.LAYER_TYPE_NONE, null)  // ✅ Disable after
        }
    })

    avd.start()
}
```

### Compose Integration

```kotlin
@Composable
fun AnimatedVectorIcon(
    @DrawableRes resId: Int,
    contentDescription: String?,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val drawable = remember(resId) {
        AnimatedVectorDrawableCompat.create(context, resId)
    }

    DisposableEffect(drawable) {
        drawable?.start()
        onDispose {
            drawable?.stop()  // ✅ Cleanup
        }
    }

    Image(
        painter = rememberDrawablePainter(drawable),
        contentDescription = contentDescription,
        modifier = modifier
    )
}
```

### Best Practices

1. **Path morphing**: use tools to normalize paths (Android Studio Vector Asset Studio, svg-path-morph)
2. **Performance**: cache inflated drawable, rasterize complex vectors for RecyclerView, use hardware layers
3. **SVG import**: import via Android Studio → Vector Asset → simplify paths → optimize viewport
4. **Animation**: duration 200-400ms, use FastOutSlowInInterpolator, avoid animating >3 paths simultaneously
5. **Compatibility**: use VectorDrawableCompat for backward compatibility, test on API 21+

### Common Pitfalls

1. **Incompatible paths** → broken morphing (normalize command structure)
2. **No caching** → repeated inflation overhead (use LruCache)
3. **Complex vectors in lists** → scrolling jank (rasterize)
4. **Unclosed animations** → memory leaks (cleanup in onDispose/onDestroy)
5. **Large viewport** → memory issues (use 24x24 for icons)

---

## Follow-ups

1. How do you implement custom path interpolators for non-linear morphing?
2. What strategies exist for converting complex SVG files with gradients and filters to VectorDrawable?
3. How do you measure and profile VectorDrawable rendering performance on different devices?
4. When should you choose AnimatedVectorDrawable vs. Lottie animations?
5. How do you implement seekable AnimatedVectorDrawable (scrubbing)?

## References

- [[c-android-graphics]] — Graphics rendering fundamentals
- [[c-animation-framework]] — Android animation types
- [Material Design Motion](https://m3.material.io/styles/motion/overview)
- [Android Vector Drawables Guide](https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources)

## Related Questions

### Prerequisites (Easier)
- [[q-drawable-resources--android--easy]] — Basic drawable types
- [[q-animation-types--android--easy]] — Animation framework overview

### Related (Same Level)
- [[q-canvas-custom-views--android--medium]] — Custom drawing with Canvas
- [[q-transition-animations--android--medium]] — View transitions

### Advanced (Harder)
- [[q-opengl-rendering--android--hard]] — Low-level graphics with OpenGL
- [[q-renderscript-compute--android--hard]] — GPU-accelerated computations
