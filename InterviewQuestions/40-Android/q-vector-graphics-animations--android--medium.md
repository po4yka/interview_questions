---
id: android-432
title: "Vector Graphics Animations / Анимации векторной графики"
aliases: ["Vector Graphics Animations", "Анимации векторной графики"]
topic: android
subtopics: [performance-rendering, ui-animation, ui-graphics]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-graphics, c-animation-framework, q-animated-visibility-vs-content--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-rendering, android/ui-animation, android/ui-graphics, animated-vector-drawable, difficulty/medium, vector-graphics]

date created: Saturday, November 1st 2025, 1:24:44 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)

> Как работать с векторной графикой и `AnimatedVectorDrawable` в Android? Каковы лучшие практики для импорта SVG, морфинга путей и оптимизации производительности?

# Question (EN)

> How do you work with vector graphics and `AnimatedVectorDrawable` in Android? What are the best practices for SVG import, path morphing, and performance optimization?

---

## Ответ (RU)

### Основные Концепции

**VectorDrawable** — это XML-представление векторной графики на основе синтаксиса SVG path. Обеспечивает независимость от разрешения экрана и уменьшает размер APK за счёт отсутствия отдельных bitmap-ресурсов для разных плотностей.

**AnimatedVectorDrawable** позволяет анимировать свойства VectorDrawable:
- **Path morphing** — трансформация путей (требует совместимых путей: одинаковый набор, порядок и типы команд и сегментов, а не только количество или длина строки)
- **Rotation, scale, translation** — трансформация групп
- **Trim path** — эффект рисования линии
- **Fill/stroke alpha** — анимация прозрачности

**Ключевые преимущества**:
- Масштабируются без потери качества
- Малый размер файлов (~1–5 КБ vs. 10–50 КБ для PNG hdpi/xhdpi/xxhdpi)
- Поддержка tinting и theme attributes
- Процедурные, разрешение-независимые анимации без необходимости хранить промежуточные кадры

См. также: [[c-android-graphics]], [[c-animation-framework]].

### Основные Примеры

**1. VectorDrawable с тематизацией:**

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
        android:pathData="M12,21.35l-1.45,-1.32C5.4,15.36 2,12.28 2,8.5..."
        android:fillColor="@android:color/white"/>
</vector>
```

**2. AnimatedVectorDrawable с path morphing:**

```xml
<!-- res/drawable/ic_play_to_pause.xml: VectorDrawable с path @name/play_pause_path -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="48"
    android:viewportHeight="48">

    <path
        android:name="play_pause_path"
        android:fillColor="@android:color/white"
        android:pathData="M16,12L16,36L32,24Z"/>
</vector>

<!-- res/drawable/avd_play_to_pause.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_play_to_pause">
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

(Обратите внимание: `valueFrom` и `valueTo` должны описывать совместимые пути; пример иллюстративный.)

**3. Управление анимацией в коде:**

```kotlin
class AnimatedVectorManager {
    fun playAnimation(imageView: ImageView, @DrawableRes resId: Int) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)
        avd?.start()
    }

    fun playWithCallback(
        imageView: ImageView,
        @DrawableRes resId: Int,
        onEnd: () -> Unit
    ) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)

        if (avd is Animatable2Compat) {
            avd.registerAnimationCallback(object : Animatable2Compat.AnimationCallback() {
                override fun onAnimationEnd(drawable: Drawable?) {
                    onEnd()
                    avd.unregisterAnimationCallback(this)
                }
            })
        }

        avd?.start()
    }
}
```

**4. Path morphing совместимость:**

```kotlin
// Несовместимые пути — разное количество/структура команд
val path1 = "M10,10L20,20"           // 2 команды
val path2 = "M10,10L15,15L20,20"     // 3 команды

// Совместимые пути — одинаковая структура команд и сегментов
val path3 = "M10,10L20,20L30,10Z"
val path4 = "M10,15L20,25L30,15Z"
```

### Оптимизация Производительности

**1. Кеширование для повторного использования (упрощённый пример):**

```kotlin
class VectorDrawableCache {
    private val cache = LruCache<Int, Drawable.ConstantState>(50)

    fun get(context: Context, @DrawableRes resId: Int): Drawable? {
        val cachedState = cache.get(resId)
        if (cachedState != null) {
            return cachedState.newDrawable(context.resources).mutate()
        }

        val drawable = ContextCompat.getDrawable(context, resId) ?: return null
        drawable.constantState?.let { cache.put(resId, it) }
        return drawable.mutate()
    }
}
```

**2. Растеризация для сложных векторов в списках (пример паттерна):**

```kotlin
fun rasterizeIfComplex(drawable: Drawable, size: Int): Drawable {
    val complexity = measureComplexity(drawable)

    return if (complexity > 100) {
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, size, size)
        drawable.draw(canvas)
        BitmapDrawable(null, bitmap)
    } else {
        drawable
    }
}

// Заглушка: на практике сложность оценивается по числу путей, сегментов и т.п.
fun measureComplexity(drawable: Drawable): Int {
    return 0
}
```

**3. Аппаратный слой для анимаций (по ситуации):**

```kotlin
fun animateWithHardwareLayer(imageView: ImageView, avd: AnimatedVectorDrawableCompat) {
    val previousLayerType = imageView.layerType

    imageView.setLayerType(View.LAYER_TYPE_HARDWARE, null)

    avd.registerAnimationCallback(object : Animatable2Compat.AnimationCallback() {
        override fun onAnimationEnd(drawable: Drawable?) {
            imageView.setLayerType(previousLayerType, null)
            avd.unregisterAnimationCallback(this)
        }
    })

    avd.start()
}
```

(Используйте аппаратные слои только после профилирования: для некоторых векторов выгоды может не быть.)

### Compose Интеграция

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
            drawable?.stop()
        }
    }

    Image(
        painter = rememberDrawablePainter(drawable),
        contentDescription = contentDescription,
        modifier = modifier
    )
}
```

(В реальных проектах также можно использовать специализированные вспомогательные API из Compose для работы с AnimatedVectorDrawable.)

### Лучшие Практики

1. **Path morphing**: используйте инструменты для нормализации путей (Vector Asset Studio, svg-path-morph); обеспечивайте идентичную структуру команд.
2. **Производительность**: кешируйте `Drawable` (или их `ConstantState`), при необходимости растеризуйте особо сложные векторы для RecyclerView, выборочно используйте аппаратные слои на основе профилирования.
3. **Импорт SVG**: импортируйте через Vector Asset Studio, упрощайте пути, оптимизируйте viewport и удаляйте неподдерживаемые эффекты.
4. **Анимации**: длительность 200–400 мс для большинства UI-кейсов, используйте FastOutSlowInInterpolator, избегайте избыточного количества одновременно анимируемых путей.
5. **Совместимость**: используйте VectorDrawableCompat / AnimatedVectorDrawableCompat для поддержки старых версий, при этом на новых API можно использовать нативные классы; тестируйте на API 21+.

### Распространённые Ошибки

1. Несовместимые пути приводят к некорректному морфингу.
2. Отсутствие кеширования вызывает лишние inflate-операции.
3. Сложные векторы в списках вызывают лаги при скролле.
4. Незакрытые анимации и колбэки ведут к утечкам.
5. Избыточно большие и сложные векторы увеличивают нагрузку.

---

## Answer (EN)

### Core Concepts

**VectorDrawable** is an XML representation of vector graphics based on SVG path syntax. It provides resolution independence and helps reduce APK size by avoiding separate bitmap resources for each density.

**AnimatedVectorDrawable** enables animating VectorDrawable properties:
- **Path morphing** — shape transitions (requires compatible paths: same set, order, and types of commands/segments, not just equal string length)
- **Rotation, scale, translation** — group transformations
- **Trim path** — line drawing effects
- **Fill/stroke alpha** — opacity animations

**Key advantages**:
- Scale without quality loss
- Small file size (~1–5 KB vs. 10–50 KB for PNG hdpi/xhdpi/xxhdpi)
- Support for tinting and theme attributes
- Procedural, resolution-independent animations without storing raster keyframes

See also: [[c-android-graphics]], [[c-animation-framework]].

### Essential Examples

**1. VectorDrawable with theming:**

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
        android:pathData="M12,21.35l-1.45,-1.32C5.4,15.36 2,12.28 2,8.5..."
        android:fillColor="@android:color/white"/>
</vector>
```

**2. AnimatedVectorDrawable with path morphing:**

```xml
<!-- res/drawable/ic_play_to_pause.xml: VectorDrawable with path @name/play_pause_path -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="48"
    android:viewportHeight="48">

    <path
        android:name="play_pause_path"
        android:fillColor="@android:color/white"
        android:pathData="M16,12L16,36L32,24Z"/>
</vector>

<!-- res/drawable/avd_play_to_pause.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_play_to_pause">
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

(Note: `valueFrom` and `valueTo` must describe compatible paths; the snippet is illustrative.)

**3. Animation control in code:**

```kotlin
class AnimatedVectorManager {
    fun playAnimation(imageView: ImageView, @DrawableRes resId: Int) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)
        avd?.start()
    }

    fun playWithCallback(
        imageView: ImageView,
        @DrawableRes resId: Int,
        onEnd: () -> Unit
    ) {
        val avd = AnimatedVectorDrawableCompat.create(imageView.context, resId)
        imageView.setImageDrawable(avd)

        if (avd is Animatable2Compat) {
            avd.registerAnimationCallback(object : Animatable2Compat.AnimationCallback() {
                override fun onAnimationEnd(drawable: Drawable?) {
                    onEnd()
                    avd.unregisterAnimationCallback(this)
                }
            })
        }

        avd?.start()
    }
}
```

**4. Path morphing compatibility:**

```kotlin
// Incompatible paths - different number/structure of commands
val path1 = "M10,10L20,20"           // 2 commands
val path2 = "M10,10L15,15L20,20"     // 3 commands

// Compatible paths - same command structure and segments
val path3 = "M10,10L20,20L30,10Z"
val path4 = "M10,15L20,25L30,15Z"
```

### Performance Optimization

**1. Caching for reuse (simplified pattern):**

```kotlin
class VectorDrawableCache {
    private val cache = LruCache<Int, Drawable.ConstantState>(50)

    fun get(context: Context, @DrawableRes resId: Int): Drawable? {
        val cachedState = cache.get(resId)
        if (cachedState != null) {
            return cachedState.newDrawable(context.resources).mutate()
        }

        val drawable = ContextCompat.getDrawable(context, resId) ?: return null
        drawable.constantState?.let { cache.put(resId, it) }
        return drawable.mutate()
    }
}
```

**2. Rasterization for complex vectors in lists (pattern example):**

```kotlin
fun rasterizeIfComplex(drawable: Drawable, size: Int): Drawable {
    val complexity = measureComplexity(drawable)

    return if (complexity > 100) {
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, size, size)
        drawable.draw(canvas)
        BitmapDrawable(null, bitmap)
    } else {
        drawable
    }
}

// Stub: in real code, base this on number of paths, segments, etc.
fun measureComplexity(drawable: Drawable): Int {
    return 0
}
```

**3. Hardware layer for animations (situational):**

```kotlin
fun animateWithHardwareLayer(imageView: ImageView, avd: AnimatedVectorDrawableCompat) {
    val previousLayerType = imageView.layerType

    imageView.setLayerType(View.LAYER_TYPE_HARDWARE, null)

    avd.registerAnimationCallback(object : Animatable2Compat.AnimationCallback() {
        override fun onAnimationEnd(drawable: Drawable?) {
            imageView.setLayerType(previousLayerType, null)
            avd.unregisterAnimationCallback(this)
        }
    })

    avd.start()
}
```

(Use hardware layers only after profiling; they may not always improve performance for vector animations.)

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
            drawable?.stop()
        }
    }

    Image(
        painter = rememberDrawablePainter(drawable),
        contentDescription = contentDescription,
        modifier = modifier
    )
}
```

(In production, you can also use dedicated Compose helpers for AnimatedVectorDrawable.)

### Best Practices

1. Path morphing: use tools to normalize paths; ensure identical command structure.
2. Performance: cache drawables (or their ConstantState), rasterize very complex vectors for RecyclerView when needed, and apply hardware layers based on profiling.
3. SVG import: import via Vector Asset Studio, simplify paths, optimize viewport, and remove unsupported effects.
4. Animation: use 200–400 ms for most UI cases, prefer FastOutSlowInInterpolator, avoid animating too many paths at once.
5. Compatibility: use VectorDrawableCompat / AnimatedVectorDrawableCompat to support old APIs; on newer APIs native classes are fine. Test on API 21+.

### Common Pitfalls

1. Incompatible paths cause broken morphing.
2. No caching leads to repeated inflation overhead.
3. Complex vectors in lists cause scrolling jank.
4. Unreleased animations/callbacks lead to leaks.
5. Overly large/complex vectors increase rendering cost.

---

## Дополнительные Вопросы (RU)

1. Как реализовать кастомные path-интерполяторы для нелинейного морфинга фигур?
2. Какие подходы используются для конвертации сложных SVG (градиенты, фильтры) в поддерживаемые VectorDrawable-ресурсы?
3. Как измерять и профилировать производительность отрисовки VectorDrawable на разных устройствах?
4. В каких случаях следует выбирать `AnimatedVectorDrawable` вместо Lottie-анимаций и наоборот?
5. Как реализовать возможность "прокрутки" (`scrubbing`) анимации `AnimatedVectorDrawable` по времени?

## Follow-ups

1. How do you implement custom path interpolators for non-linear morphing?
2. What strategies exist for converting complex SVG files with gradients and filters to VectorDrawable?
3. How do you measure and profile VectorDrawable rendering performance on different devices?
4. When should you choose `AnimatedVectorDrawable` vs. Lottie animations?
5. How do you implement seekable `AnimatedVectorDrawable` (scrubbing)?

## Ссылки (RU)

- [Material Design Motion](https://m3.material.io/styles/motion/overview)
- [Android Vector Drawables Guide](https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources)

## References

- [Material Design Motion](https://m3.material.io/styles/motion/overview)
- [Android Vector Drawables Guide](https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources)

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-android-app-components--android--easy]] — Базовые компоненты Android-приложения
- [[q-android-app-bundles--android--easy]] — Основы Android App `Bundle`

### Связанные (средний уровень)
- [[q-android-app-lag-analysis--android--medium]] — Диагностика лагов и jank в UI
- [[q-android-performance-measurement-tools--android--medium]] — Обзор инструментов измерения производительности

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] — Внутреннее устройство Android Runtime
- [[q-android-keystore-system--security--medium]] — Безопасное управление ключами в Android

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] — Basic Android app components
- [[q-android-app-bundles--android--easy]] — Android App `Bundle` basics

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] — Diagnosing UI jank
- [[q-android-performance-measurement-tools--android--medium]] — Performance tooling overview

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Android runtime internals
- [[q-android-keystore-system--security--medium]] — Secure key management on Android
