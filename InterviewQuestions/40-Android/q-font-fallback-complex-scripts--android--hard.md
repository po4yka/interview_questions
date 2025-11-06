---
id: android-643
title: Font Fallback for Complex Scripts / Резерв шрифтов для сложных скриптов
aliases: [Font Fallback for Complex Scripts, Резерв шрифтов для сложных скриптов]
topic: android
subtopics:
  - globalization
  - typography
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-globalization
created: 2025-11-02
updated: 2025-11-02
tags: [accessibility, android/globalization, difficulty/hard, typography]
sources:
  - https://developer.android.com/guide/topics/resources/font-resource
  - https://developer.android.com/guide/topics/text/downloadable-fonts
  - https://material.io/design/typography/international-typography.html
---

# Вопрос (RU)

> Как обеспечить корректное отображение сложных скриптов (CJK, арабский, индийские письменности) в Android: настройте font fallback цепочки с Noto шрифтами, downloadable fonts для dynamic loading, специальные настройки rendering для ligatures и complex shaping. Тестируйте на real устройствах с accessibility scaling.

# Question (EN)

> How to ensure proper rendering of complex scripts (CJK, Arabic, Indic) in Android: configure font fallback chains with Noto fonts, use downloadable fonts for dynamic loading, apply special rendering settings for ligatures and complex shaping. Test on real devices with accessibility scaling enabled.

---

## Ответ (RU)

### Теоретические Основы

**Сложные скрипты** — письменности требующие advanced text shaping: CJK (Chinese/Japanese/Korean), Arabic с contextual forms, Indic скрипты с combining marks, Thai/Lao с complex clusters.

**Проблемы отображения:**
- **Glyph coverage** — большинство шрифтов поддерживают только Latin glyphs
- **Text shaping** — complex scripts требуют ligatures, contextual forms, reordering
- **Baseline alignment** — разные скрипты имеют разные baseline requirements
- **Line breaking** — script-specific правила переноса слов

**Android font system:**
- **System fonts** — Roboto (Latin), Noto (international) как fallbacks
- **Downloadable fonts** — Google Fonts API для dynamic loading
- **Font resources** — XML конфигурация fallback цепочек
- **Font synthesis** — fake bold/italic для unsupported styles

### 1. Анализ Требований И Аудит

**Выявление целевых скриптов:**
- Анализируйте market requirements: CJK для Asian markets, Arabic для Middle East, Indic для South Asia
- Проверяйте app content: user-generated text, translations, proper names
- Оценивайте scope: UI labels vs user content vs mixed text

**Аудит бренд-шрифта:**
```kotlin
fun hasGlyph(font: Typeface, text: String): Boolean {
    val paint = Paint().apply { typeface = font }
    return paint.measureText(text) > 0f
}

val testCases = mapOf("CJK" to "中文", "Arabic" to "العربية", "Devanagari" to "हिन्दी")
testCases.forEach { (script, text) ->
    Log.d("FontAudit", "$script: ${hasGlyph(brandFont, text)}")
}
```

**Приоритизация:**
- **UI chrome** (buttons, navigation) — critical, может требовать custom fonts
- **Content text** (articles, messages) — flexible, fallback acceptable
- **User-generated content** — unpredictable, robust fallback essential

### 2. Font Fallback Цепочки

**XML fallback цепочка:**
```xml
<font-family xmlns:android="http://schemas.android.com/apk/res/android">
    <font android:font="@font/brand_regular" />
    <font android:fallbackFor="sans-serif" android:font="@font/noto_cjk" />
    <font android:fallbackFor="sans-serif" android:font="@font/noto_arabic" />
</font-family>
```

**Программное создание:**
```kotlin
val fontFamily = Typeface.Builder(assets, "fonts/brand.ttf")
    .setFallback("Noto Sans CJK JP", "Noto Sans Arabic")
    .build()
textView.typeface = fontFamily
```

**Compose FontFamily:**
```kotlin
val fontFamily = FontFamily(
    Font(R.font.brand_regular),
    Font("Noto Sans CJK JP"), // CJK fallback
    Font("Noto Sans Arabic")  // Arabic fallback
)

Text(text, fontFamily = fontFamily)
```

**Custom resolver:**
```kotlin
val resolver = FontFamily.Resolver { family, weight, style ->
    when {
        text.contains(Regex("\\p{IsHan}")) -> Font("Noto Sans CJK JP", weight, style)
        text.contains(Regex("\\p{IsArabic}")) -> Font("Noto Sans Arabic", weight, style)
        else -> Font("sans-serif", weight, style)
    }
}
```

### 3. Downloadable Fonts

**Font request:**
```kotlin
val request = FontRequest(
    "com.google.android.gms.fonts",
    "com.google.android.gms",
    "Noto Sans CJK JP",
    R.array.com_google_android_gms_fonts_certs
)

FontsContractCompat.requestFont(context, request, callback, handler)
```

**Compose integration:**
```kotlin
@Composable
fun DownloadableFontText(text: String) {
    var fontFamily by remember { mutableStateOf<FontFamily?>(null) }
    var loading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        try {
            val typeface = FontsContractCompat.requestFont(context, request).await()
            fontFamily = FontFamily(TypefaceCompat.createFromTypeface(typeface))
        } catch (e: Exception) {
            fontFamily = FontFamily.Default
        }
        loading = false
    }

    if (loading) CircularProgressIndicator() else Text(text, fontFamily = fontFamily)
}
```

**Font caching:**
```kotlin
class FontCache(private val context: Context) {
    private val fontMap = mutableMapOf<String, Typeface>()

    fun getFont(name: String): Typeface? = fontMap[name] ?: loadFromDisk(name)
    fun saveFont(name: String, typeface: Typeface) { fontMap[name] = typeface }

    private fun loadFromDisk(name: String): Typeface? =
        File(context.cacheDir, "fonts/$name.ttf").takeIf { it.exists() }
            ?.let { Typeface.createFromFile(it) }
}
```

### 4. Rendering Настройки

**`TextView` optimization:**
```kotlin
class OptimizedTextView(context: Context) : AppCompatTextView(context) {
    init {
        setBreakStrategy(Layout.BREAK_STRATEGY_HIGH_QUALITY)
        setHyphenationFrequency(Layout.HYPHENATION_FREQUENCY_NORMAL)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            setFontFeatureSettings("'liga' 1, 'kern' 1, 'calt' 1")
        }
    }
}
```

**Compose rendering:**
```kotlin
@Composable
fun ComplexScriptText(text: String) {
    val fontFamily = when {
        text.contains(Regex("\\p{IsHan}")) -> FontFamily(Font("Noto Sans CJK JP"))
        text.contains(Regex("\\p{IsArabic}")) -> FontFamily(Font("Noto Sans Arabic"))
        text.contains(Regex("\\p{IsDevanagari}")) -> FontFamily(Font("Noto Sans Devanagari"))
        else -> FontFamily.Default
    }

    Text(
        text = text,
        fontFamily = fontFamily,
        fontFeatureSettings = when {
            text.contains(Regex("\\p{IsArabic}")) -> "liga 1, calt 1, isol 1"
            text.contains(Regex("\\p{IsDevanagari}")) -> "liga 1, nukt 1"
            else -> "liga 1"
        }
    )
}
```

**Arabic RTL handling:**
```kotlin
@Composable
fun ArabicText(text: String) {
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        Text(
            text = text,
            textAlign = TextAlign.Start,
            fontFamily = FontFamily(Font("Noto Sans Arabic")),
            fontFeatureSettings = "liga 1, calt 1, isol 1, init 1, medi 1, fina 1"
        )
    }
}
```

### 5. Тестирование

**Glyph coverage test:**
```kotlin
@Test
fun testComplexScriptCoverage() {
    val tests = mapOf(
        "Arabic" to "العربيةﷺ",
        "Devanagari" to "हिन्दीक्ष",
        "CJK" to "中文日韓"
    )

    tests.forEach { (script, text) ->
        assertTrue("$script coverage", hasGlyphCoverage(brandFont, text))
    }
}

private fun hasGlyphCoverage(font: Typeface, text: String): Boolean {
    val paint = Paint().apply { typeface = font }
    return text.all { paint.measureText(it.toString()) > 0 }
}
```

**Screenshot testing:**
```kotlin
@RunWith(AndroidJUnit4::class)
class TypographyScreenshotTest {
    @get:Rule val paparazzi = Paparazzi()

    @Test
    fun complexScripts() {
        val texts = listOf("English + العربية", "English + हिन्दी", "Mixed: Hello 世界")
        texts.forEach { text ->
            paparazzi.snapshot { Text(text, modifier = Modifier.padding(16.dp)) }
        }
    }
}
```

### 6. Performance Optimization

**`Bundle` size analysis:**
```kotlin
fun analyzeFontImpact() {
    val fonts = listOf(2.1f, 2.0f, 18.5f, 0.8f) // MB sizes
    val total = fonts.sum() * 0.7f // Compressed
    println("Font impact: ${total}MB")
}
```

**Selective inclusion:**
```kotlin
android {
    bundle {
        font {
            include "Noto Sans", "latin", "arabic", "devanagari"
        }
    }
}
```

**On-demand delivery:**
```kotlin
suspend fun loadScriptFont(script: String): Typeface {
    val fontName = when(script) {
        "arabic" -> "Noto Sans Arabic"
        "cjk" -> "Noto Sans CJK JP"
        else -> "Noto Sans"
    }

    return fontCache[fontName] ?: downloadFont(fontName).also { fontCache[fontName] = it }
}
```

### 7. UX Considerations

**Line height for scripts:**
```kotlin
val lineHeight = when (script) {
    "devanagari" -> 1.4f
    "arabic" -> 1.3f
    "cjk" -> 1.5f
    else -> 1.2f
}
```

**Mixed script alignment:**
```kotlin
val baselineOffset = when (script) {
    "devanagari" -> (-2).dp
    "arabic" -> 0.dp
    "cjk" -> (-1).dp
    else -> 0.dp
}
```

**Emoji compatibility:**
```kotlin
val emojiCompat = EmojiCompat.init(FontRequest(
    "com.google.android.gms.fonts",
    "com.google.android.gms",
    "Noto Color Emoji Compat",
    certs
))
```

### Лучшие Практики

- **Комплексный аудит** — тестируйте бренд-шрифты на всех целевых скриптах перед внедрением
- **Прогрессивное улучшение** — начинайте с системных шрифтов, добавляйте кастомные по необходимости
- **Мониторинг производительности** — отслеживайте время загрузки шрифтов и влияние на размер бандла
- **Доступность прежде всего** — обеспечивайте работу complex scripts с крупными размерами шрифта и скринридерами
- **Оффлайн устойчивость** — кешируйте скачанные шрифты и предоставляйте системные fallback'ы

### Типичные Ошибки

- **Предположение что Latin coverage = universal** — большинство шрифтов не имеют CJK/Arabic glyphs
- **Игнорирование text shaping** — complex scripts требуют contextual forms и ligatures
- **Плохое выравнивание mixed scripts** — разные скрипты имеют разные baseline
- **Отсутствие тестирования доступности** — крупные размеры шрифта ломают рендеринг complex scripts
- **Невнимание к размеру бандла** — CJK шрифты могут добавить 20+ MB к APK

---

## Answer (EN)

### Theoretical Foundations

**Complex scripts** — writing systems requiring advanced text shaping: CJK (Chinese/Japanese/Korean), Arabic with contextual forms, Indic scripts with combining marks, Thai/Lao with complex clusters.

**Rendering challenges:**
- **Glyph coverage** — most fonts support only Latin glyphs
- **Text shaping** — complex scripts require ligatures, contextual forms, reordering
- **Baseline alignment** — different scripts have different baseline requirements
- **Line breaking** — script-specific word wrapping rules

**Android font system:**
- **System fonts** — Roboto (Latin), Noto (international) as fallbacks
- **Downloadable fonts** — Google Fonts API for dynamic loading
- **Font resources** — XML configuration of fallback chains
- **Font synthesis** — fake bold/italic for unsupported styles

### 1. Requirements Analysis and Audit

**Identifying target scripts:**
- Analyze market requirements: CJK for Asian markets, Arabic for Middle East, Indic for South Asia
- Check app content: user-generated text, translations, proper names
- Evaluate scope: UI labels vs user content vs mixed text

**Brand font audit:**
```kotlin
fun hasGlyph(font: Typeface, text: String): Boolean {
    val paint = Paint().apply { typeface = font }
    return paint.measureText(text) > 0f
}

val testCases = mapOf("CJK" to "中文", "Arabic" to "العربية", "Devanagari" to "हिन्दी")
testCases.forEach { (script, text) ->
    Log.d("FontAudit", "$script: ${hasGlyph(brandFont, text)}")
}
```

**Prioritization:**
- **UI chrome** (buttons, navigation) — critical, may require custom fonts
- **Content text** (articles, messages) — flexible, fallback acceptable
- **User-generated content** — unpredictable, robust fallback essential

### 2. Font Fallback Chains

**XML fallback:**
```xml
<font-family xmlns:android="http://schemas.android.com/apk/res/android">
    <font android:font="@font/brand_regular" />
    <font android:fallbackFor="sans-serif" android:font="@font/noto_cjk" />
    <font android:fallbackFor="sans-serif" android:font="@font/noto_arabic" />
</font-family>
```

**Programmatic creation:**
```kotlin
val fontFamily = Typeface.Builder(assets, "fonts/brand.ttf")
    .setFallback("Noto Sans CJK JP", "Noto Sans Arabic")
    .build()
textView.typeface = fontFamily
```

**Compose FontFamily:**
```kotlin
val fontFamily = FontFamily(
    Font(R.font.brand_regular),
    Font("Noto Sans CJK JP"), // CJK fallback
    Font("Noto Sans Arabic")  // Arabic fallback
)

Text(text, fontFamily = fontFamily)
```

**Custom resolver:**
```kotlin
val resolver = FontFamily.Resolver { family, weight, style ->
    when {
        text.contains(Regex("\\p{IsHan}")) -> Font("Noto Sans CJK JP", weight, style)
        text.contains(Regex("\\p{IsArabic}")) -> Font("Noto Sans Arabic", weight, style)
        else -> Font("sans-serif", weight, style)
    }
}
```

### 3. Downloadable Fonts

**Font request:**
```kotlin
val request = FontRequest(
    "com.google.android.gms.fonts",
    "com.google.android.gms",
    "Noto Sans CJK JP",
    R.array.com_google_android_gms_fonts_certs
)

FontsContractCompat.requestFont(context, request, callback, handler)
```

**Compose integration:**
```kotlin
@Composable
fun DownloadableFontText(text: String) {
    var fontFamily by remember { mutableStateOf<FontFamily?>(null) }
    var loading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        try {
            val typeface = FontsContractCompat.requestFont(context, request).await()
            fontFamily = FontFamily(TypefaceCompat.createFromTypeface(typeface))
        } catch (e: Exception) {
            fontFamily = FontFamily.Default
        }
        loading = false
    }

    if (loading) CircularProgressIndicator() else Text(text, fontFamily = fontFamily)
}
```

**Font caching:**
```kotlin
class FontCache(private val context: Context) {
    private val fontMap = mutableMapOf<String, Typeface>()

    fun getFont(name: String): Typeface? = fontMap[name] ?: loadFromDisk(name)
    fun saveFont(name: String, typeface: Typeface) { fontMap[name] = typeface }

    private fun loadFromDisk(name: String): Typeface? =
        File(context.cacheDir, "fonts/$name.ttf").takeIf { it.exists() }
            ?.let { Typeface.createFromFile(it) }
}
```

### 4. Rendering Settings

**`TextView` optimization:**
```kotlin
class OptimizedTextView(context: Context) : AppCompatTextView(context) {
    init {
        setBreakStrategy(Layout.BREAK_STRATEGY_HIGH_QUALITY)
        setHyphenationFrequency(Layout.HYPHENATION_FREQUENCY_NORMAL)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            setFontFeatureSettings("'liga' 1, 'kern' 1, 'calt' 1")
        }
    }
}
```

**Compose rendering:**
```kotlin
@Composable
fun ComplexScriptText(text: String) {
    val fontFamily = when {
        text.contains(Regex("\\p{IsHan}")) -> FontFamily(Font("Noto Sans CJK JP"))
        text.contains(Regex("\\p{IsArabic}")) -> FontFamily(Font("Noto Sans Arabic"))
        text.contains(Regex("\\p{IsDevanagari}")) -> FontFamily(Font("Noto Sans Devanagari"))
        else -> FontFamily.Default
    }

    Text(
        text = text,
        fontFamily = fontFamily,
        fontFeatureSettings = when {
            text.contains(Regex("\\p{IsArabic}")) -> "liga 1, calt 1, isol 1"
            text.contains(Regex("\\p{IsDevanagari}")) -> "liga 1, nukt 1"
            else -> "liga 1"
        }
    )
}
```

**Arabic RTL handling:**
```kotlin
@Composable
fun ArabicText(text: String) {
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        Text(
            text = text,
            textAlign = TextAlign.Start,
            fontFamily = FontFamily(Font("Noto Sans Arabic")),
            fontFeatureSettings = "liga 1, calt 1, isol 1, init 1, medi 1, fina 1"
        )
    }
}
```

### 5. Testing

**Glyph coverage test:**
```kotlin
@Test
fun testComplexScriptCoverage() {
    val tests = mapOf(
        "Arabic" to "العربيةﷺ",
        "Devanagari" to "हिन्दीक्ष",
        "CJK" to "中文日韓"
    )

    tests.forEach { (script, text) ->
        assertTrue("$script coverage", hasGlyphCoverage(brandFont, text))
    }
}

private fun hasGlyphCoverage(font: Typeface, text: String): Boolean {
    val paint = Paint().apply { typeface = font }
    return text.all { paint.measureText(it.toString()) > 0 }
}
```

**Screenshot testing:**
```kotlin
@RunWith(AndroidJUnit4::class)
class TypographyScreenshotTest {
    @get:Rule val paparazzi = Paparazzi()

    @Test
    fun complexScripts() {
        val texts = listOf("English + العربية", "English + हिन्दी", "Mixed: Hello 世界")
        texts.forEach { text ->
            paparazzi.snapshot { Text(text, modifier = Modifier.padding(16.dp)) }
        }
    }
}
```

### 6. Performance Optimization

**`Bundle` size analysis:**
```kotlin
fun analyzeFontImpact() {
    val fonts = listOf(2.1f, 2.0f, 18.5f, 0.8f) // MB sizes
    val total = fonts.sum() * 0.7f // Compressed
    println("Font impact: ${total}MB")
}
```

**Selective inclusion:**
```kotlin
android {
    bundle {
        font {
            include "Noto Sans", "latin", "arabic", "devanagari"
        }
    }
}
```

**On-demand delivery:**
```kotlin
suspend fun loadScriptFont(script: String): Typeface {
    val fontName = when(script) {
        "arabic" -> "Noto Sans Arabic"
        "cjk" -> "Noto Sans CJK JP"
        else -> "Noto Sans"
    }

    return fontCache[fontName] ?: downloadFont(fontName).also { fontCache[fontName] = it }
}
```

### Best Practices

- **Comprehensive audit** — test brand fonts against all target scripts before implementation
- **Progressive enhancement** — start with system fonts, add custom fonts as needed
- **Performance monitoring** — track font loading times and bundle size impact
- **Accessibility first** — ensure complex scripts work with large font sizes and screen readers
- **Offline resilience** — cache downloaded fonts and provide system font fallbacks

### Common Pitfalls

- **Assuming Latin coverage equals universal** — most fonts lack CJK/Arabic glyphs
- **Ignoring text shaping** — complex scripts require contextual forms and ligatures
- **Poor mixed script alignment** — different scripts have different baselines
- **No accessibility testing** — large font sizes break complex script rendering
- **`Bundle` size neglect** — CJK fonts can add 20+ MB to APK size

---

## Follow-ups
- Как комбинировать латинский бренд-шрифт и Noto для контента без визуальных конфликтов?
- Как управлять загрузкой шрифтов при старте приложения (splash screen)?
- Какие инструменты использовать для автоматической проверки покрытия glyph?

## References
- [[c-globalization]]
- https://developer.android.com/guide/topics/text/downloadable-fonts

## Related Questions

- [[c-globalization]]
