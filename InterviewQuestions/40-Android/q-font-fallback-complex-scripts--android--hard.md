---
id: android-643
title: Font Fallback for Complex Scripts / Резерв шрифтов для сложных скриптов
aliases:
- Font Fallback for Complex Scripts
- Резерв шрифтов для сложных скриптов
topic: android
subtopics:
- i18n-l10n
- ui-theming
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- c-android-components
- q-compose-core-components--android--medium
- q-dagger-build-time-optimization--android--medium
- q-data-sync-unstable-network--android--hard
created: 2025-11-02
updated: 2025-11-10
tags:
- android/i18n-l10n
- android/ui-theming
- difficulty/hard
anki_cards:
- slug: android-643-0-en
  language: en
  anki_id: 1768367153855
  synced_at: '2026-01-14T09:17:53.072686'
- slug: android-643-0-ru
  language: ru
  anki_id: 1768367153880
  synced_at: '2026-01-14T09:17:53.075065'
sources:
- https://developer.android.com/guide/topics/resources/font-resource
- https://developer.android.com/guide/topics/text/downloadable-fonts
- https://material.io/design/typography/international-typography.html
---
# Вопрос (RU)

> Как обеспечить корректное отображение сложных скриптов (CJK, арабский, индийские письменности) в Android: настройте font fallback цепочки с Noto шрифтами, используйте downloadable fonts для динамической загрузки, корректно учитывайте ligatures и complex shaping. Тестируйте на реальных устройствах с accessibility scaling.

# Question (EN)

> How to ensure proper rendering of complex scripts (CJK, Arabic, Indic) in Android: configure font fallback chains with Noto fonts, use downloadable fonts for dynamic loading, correctly handle ligatures and complex shaping. Test on real devices with accessibility scaling enabled.

## Ответ (RU)

### Краткая Версия
Используйте системные шрифты и Noto как надёжную основу, на бренд-шрифт опирайтесь только там, где подтверждено покрытие glyph и корректное shaping. Для сложных скриптов держитесь системных семейств (`sans-serif`, `serif`) и/или `FontFamily` с Noto для соответствующих скриптов. Добавляйте downloadable fonts через `FontsContractCompat`/`FontRequest`. Обязательно тестируйте CJK, арабский, индийские скрипты, RTL и масштабирование шрифта на реальных устройствах.

### Подробная Версия
### Теоретические Основы

**Сложные скрипты** — письменности, требующие advanced text shaping: CJK (Chinese/Japanese/Korean), Arabic с contextual forms, Indic скрипты с combining marks, Thai/Lao с complex clusters.

**Проблемы отображения:**
- **Glyph coverage** — многие брендовые шрифты поддерживают только Latin glyphs.
- **Text shaping** — complex scripts требуют ligatures, contextual forms, reordering.
- **Baseline alignment** — разные скрипты имеют разные baseline requirements.
- **Line breaking** — script-specific правила переноса слов.

**Android font system:**
- **System fonts** — Roboto (Latin), Noto (international) как часть системного набора и fallback-цепочек.
- **Downloadable fonts** — Google Fonts API / `FontsContract` для dynamic loading.
- **Font resources** — XML-конфигурация семейств шрифтов и расширение generic-семейств через `android:fallbackFor` (поведение и порядок зависят от реализации OEM).
- **Font synthesis** — fake bold/italic для unsupported styles.

### Требования

**Функциональные:**
- Корректное отображение CJK, арабских и индийских письменностей, включая ligatures и contextual forms.
- Поддержка смешанного контента (латиница + сложные скрипты + emoji).
- Работа с user-generated content, где скрипты заранее не известны.

**Нефункциональные:**
- Минимальное влияние на размер APK/`Bundle`.
- Корректная работа offline при недоступности downloadable fonts.
- Поддержка accessibility: масштабирование текста, RTL, screen readers.
- Стабильная производительность при загрузке и рендеринге шрифтов.

### Архитектура

- **Слой шрифтов и ресурсов:**
  - Определение базовых семейств (`sans-serif`, `serif`) и расширенных `font-family` с Noto для целевых скриптов.
  - Использование ресурсных XML и `FontFamily` в Compose для единообразной конфигурации.
- **Runtime-логика выбора шрифта:**
  - Определение скрипта текста (через `UnicodeScript`) и выбор подходящего `Typeface`/`FontFamily` для конкретного текста или его подстрок.
  - Использование системных fallbacks, если кастомный шрифт не покрывает символ.
- **Downloadable fonts сервис:**
  - Обёртка над `FontsContractCompat` с кешированием в памяти/на диске.
  - Асинхронная доставка шрифтов для специфичных скриптов по требованию.
- **Тестирование и наблюдаемость:**
  - Набор тестовых строк по скриптам.
  - Screenshot-тесты и ручная проверка на реальных устройствах с разными локалями и масштабированием.

### 1. Анализ Требований И Аудит

**Выявление целевых скриптов:**
- Анализируйте market requirements: CJK для Asian markets, Arabic для Middle East, Indic для South Asia.
- Проверяйте app content: user-generated text, translations, proper names.
- Оценивайте scope: UI labels vs user content vs mixed text.

**Аудит бренд-шрифта (упрощённая проверка покрытия):**
```kotlin
fun hasGlyph(font: Typeface, ch: Char): Boolean {
    val paint = Paint().apply { typeface = font }
    // Важно: hasGlyph на новых API даёт более надёжный результат;
    // measureText — лишь эвристика и может считать tofu-глиф валидным.
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        paint.hasGlyph(ch.toString())
    } else {
        paint.measureText(ch.toString()) > 0f
    }
}

val testCases = mapOf("CJK" to "中文", "Arabic" to "العربية", "Devanagari" to "हिन्दी")

testCases.forEach { (script, text) ->
    val ok = text.all { hasGlyph(brandFont, it) }
    Log.d("FontAudit", "$script: $ok")
}
```

**Приоритизация:**
- **UI chrome** (buttons, navigation) — critical, может требовать custom fonts и строгий контроль покрытия.
- **Content text** (articles, messages) — flexible, системные fallback допустимы.
- **User-generated content** — unpredictable, необходимы надёжные системные fallbacks / downloadable fonts.

### 2. Font Fallback Цепочки

Ключевая идея: вы не «вкручиваете» произвольную fallback-цепочку внутрь одного кастомного семейства; вы комбинируете бренд-шрифт с системными семействами и Noto так, чтобы движок мог применять свои fallbacks.

**Simple XML font-family:**
```xml
<font-family xmlns:android="http://schemas.android.com/apk/res/android">
    <font
        android:font="@font/brand_regular"
        android:fontStyle="normal"
        android:fontWeight="400" />
</font-family>
```

Используйте это семейство для элементов UI, а для контента оставляйте системные sans-serif / serif, чтобы работали встроенные системные fallbacks (включая Noto на современных устройствах).

**Declarative fallback for a generic family (API 26+):**
```xml
<font-family
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:fallbackFor="sans-serif">

    <font
        android:font="@font/noto_sans_cjk_jp"
        android:fontStyle="normal"
        android:fontWeight="400" />

    <font
        android:font="@font/noto_sans_arabic"
        android:fontStyle="normal"
        android:fontWeight="400" />
</font-family>
```

Эта конфигурация добавляет шрифты в fallback-набор для `sans-serif`, но точный порядок и использование остаются за реализацией системы/OEM — это не строгая, полностью контролируемая цепочка.

**Programmatic combo (API 28+):**
```kotlin
val brand = ResourcesCompat.getFont(context, R.font.brand_regular)
val cjk = ResourcesCompat.getFont(context, R.font.noto_sans_cjk_jp)
val arabic = ResourcesCompat.getFont(context, R.font.noto_sans_arabic)

// Пример: выбираем шрифт для доминирующего скрипта текста.
// Для строк с несколькими скриптами лучше разбивать на подстроки и применять разные Typeface.
val typefaceForText = when {
    text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.ARABIC } -> arabic
    text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.HAN } -> cjk
    else -> brand
}

textView.typeface = typefaceForText
```

Обратите внимание: публичного API вида `Typeface.Builder.setFallback(…)` для произвольного задания цепочки нет; вы опираетесь на системные generic-семейства, XML-ресурсы и выбор typeface в коде.

**Compose FontFamily:**
```kotlin
val ComplexFontFamily = FontFamily(
    Font(R.font.brand_regular),
    Font(R.font.noto_sans_cjk_jp),
    Font(R.font.noto_sans_arabic)
)

Text(
    text = text,
    fontFamily = ComplexFontFamily
)
```

Важно: `Font(...)` принимает ресурсы или Typeface, а не строковые имена семейств. Наличие нескольких `Font` в `FontFamily` задаёт варианты по весу/стилю и даёт системе пространство для fallback внутри этого семейства, но не реализует «умный» выбор по скрипту — для сложных сценариев смешанных скриптов всё равно учитывайте системные fallbacks или деление текста на части.

### 3. Downloadable Fonts

**Font request (classic):**
```kotlin
val request = FontRequest(
    "com.google.android.gms.fonts",
    "com.google.android.gms",
    "Noto Sans CJK JP",
    R.array.com_google_android_gms_fonts_certs
)

FontsContractCompat.requestFont(context, request, callback, Handler(Looper.getMainLooper()))
```

**Compose integration (упрощённый пример):**
```kotlin
@Composable
fun DownloadableFontText(text: String) {
    val context = LocalContext.current
    var typeface by remember { mutableStateOf<Typeface?>(null) }

    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            // Обёртка над FontsContractCompat.requestFont с callback -> suspend
            typeface = downloadTypeface(context, "Noto Sans Arabic")
        }
    }

    val family = typeface?.let { FontFamily(Font(it)) } ?: FontFamily.Default

    Text(text = text, fontFamily = family)
}
```

Реализация `downloadTypeface` опускается, но должна корректно оборачивать `FontsContractCompat`; прямого `await()` в SDK нет.

**Font caching (идея):**
```kotlin
class FontCache {
    private val memory = mutableMapOf<String, Typeface>()

    fun get(name: String): Typeface? = memory[name]

    fun put(name: String, typeface: Typeface) {
        memory[name] = typeface
    }
}
```

Подробнее: кешируйте в памяти и (при необходимости) на диске, корректно обрабатывая ошибки и отсутствие сети.

### 4. Rendering Настройки

**`TextView` optimization:**
```kotlin
class OptimizedTextView(context: Context, attrs: AttributeSet? = null) : AppCompatTextView(context, attrs) {
    init {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            breakStrategy = Layout.BREAK_STRATEGY_HIGH_QUALITY
            hyphenationFrequency = Layout.HYPHENATION_FREQUENCY_NORMAL
        }
        // OpenType features вроде 'liga' и 'kern' обычно включены по умолчанию;
        // включайте fontFeatureSettings только при необходимости специфических фич.
    }
}
```

**Compose rendering (упрощённый выбор семейства по скрипту):**
```kotlin
@Composable
fun ComplexScriptText(text: String) {
    val fontFamily = when {
        text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.HAN } ->
            FontFamily(Font(R.font.noto_sans_cjk_jp))
        text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.ARABIC } ->
            FontFamily(Font(R.font.noto_sans_arabic))
        text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.DEVANAGARI } ->
            FontFamily(Font(R.font.noto_sans_devanagari))
        else -> FontFamily.Default
    }

    // Для строк, содержащих несколько скриптов, при необходимости делите на подстроки
    // с отдельными Text-компонентами; иначе полагайтесь на системные fallbacks.
    Text(
        text = text,
        fontFamily = fontFamily
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
            fontFamily = FontFamily(Font(R.font.noto_sans_arabic))
            // Не полагайтесь на ручное управление 'isol/init/medi/fina' — это задача шейпера.
        )
    }
}
```

### 5. Тестирование

**Glyph coverage test (диагностический пример):**
```kotlin
@Test
fun testComplexScriptCoverage() {
    val tests = mapOf(
        "Arabic" to "العربية",
        "Devanagari" to "हिन्दी",
        "CJK" to "中文日韓"
    )

    tests.forEach { (script, text) ->
        val ok = text.all { hasGlyph(brandFont, it) }
        // Это приблизительная проверка; результат зависит от ограничений hasGlyph/measureText.
        println("$script coverage (approx): $ok")
    }
}

private fun hasGlyph(font: Typeface, ch: Char): Boolean {
    val paint = Paint().apply { typeface = font }
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        paint.hasGlyph(ch.toString())
    } else {
        paint.measureText(ch.toString()) > 0f
    }
}
```

Используйте такие проверки как помощник в аудите и сопровождать их визуальной валидацией, а не как строгие unit-тесты с `assertTrue`.

**Screenshot testing:**
```kotlin
@RunWith(AndroidJUnit4::class)
class TypographyScreenshotTest {
    // Пример c Paparazzi / Shot / и т.п. — конкретная интеграция зависит от используемого инструмента.

    @Test
    fun complexScripts() {
        val texts = listOf("English + العربية", "English + हिन्दी", "Mixed: Hello 世界")
        // Захват и сравнение скриншотов для разных конфигураций шрифта и scale.
    }
}
```

### 6. Performance Optimization

**`Bundle` size analysis (пример оценки):**
```kotlin
fun analyzeFontImpact() {
    val fontsMb = listOf(2.1f, 2.0f, 18.5f, 0.8f) // sizes in MB
    val compressedTotal = fontsMb.sum() * 0.7f
    println("Font impact (approx compressed): ${compressedTotal}MB")
}
```

**Selective inclusion (концепт):**

Избегайте включения полноразмерных CJK-шрифтов, если это не критично; опирайтесь на встроенные системные Noto, downloadable fonts или split APK / on-demand modules.

**On-demand delivery (концепт):**
```kotlin
suspend fun loadScriptFont(script: String): Typeface {
    val fontName = when (script) {
        "arabic" -> "Noto Sans Arabic"
        "cjk" -> "Noto Sans CJK JP"
        else -> "Noto Sans"
    }

    // Реализуйте downloadFont через FontsContractCompat или Play Feature Delivery.
    return fontCache.get(fontName) ?: downloadFont(fontName).also { fontCache.put(fontName, it) }
}
```

### 7. UX Considerations

**Line height для разных скриптов (эвристика):**
```kotlin
val lineHeight = when (script) {
    "devanagari" -> 1.4f
    "arabic" -> 1.3f
    "cjk" -> 1.5f
    else -> 1.2f
}
```

**Mixed script alignment (концептуальный пример):**
```kotlin
val baselineOffset = when (script) {
    "devanagari" -> (-2).dp
    "arabic" -> 0.dp
    "cjk" -> (-1).dp
    else -> 0.dp
}
```

Подбирайте значения экспериментально — разные шрифты дают разные метрики.

**Emoji compatibility (пример):**
```kotlin
val config = BundledEmojiCompatConfig(context)
val emojiCompat = EmojiCompat.init(config)
```

Для downloadable emoji используйте официальные EmojiCompat FontRequest-примеры вместо произвольных имен; опирайтесь на документацию AndroidX Emoji2.

### Лучшие Практики

- **Комплексный аудит** — проверяйте бренд-шрифты на всех целевых скриптах (`hasGlyph`/аналоги + визуальная проверка).
- **Прогрессивное улучшение** — начинайте с системных шрифтов и встроенных fallbacks, добавляйте кастомные и downloadable fonts по необходимости.
- **Мониторинг производительности** — измеряйте время загрузки шрифтов и влияние на размер бандла / модулей.
- **Доступность прежде всего** — проверяйте complex scripts при увеличенном шрифте, high contrast, RTL и с экранными дикторами.
- **Оффлайн устойчивость** — кешируйте скачанные шрифты и всегда предоставляйте системные fallback'ы.

### Типичные Ошибки

- **Предположение, что Latin coverage = universal** — большинство шрифтов не имеют CJK/Arabic/Indic glyphs.
- **Игнорирование text shaping** — complex scripts требуют автоматического применения contextual forms и ligatures.
- **Плохое выравнивание mixed scripts** — разные скрипты имеют разные baseline.
- **Отсутствие тестирования доступности** — крупные размеры шрифта и RTL могут ломать верстку без корректных fallbacks.
- **Невнимание к размеру бандла** — CJK шрифты могут добавить 20+ MB к APK, используйте downloadable/модули.

## Answer (EN)

### Short Version
Use system fonts and Noto as the reliable base; only apply the brand font where glyph coverage and shaping are verified. For complex scripts keep text on system families (`sans-serif`, `serif`) and/or `FontFamily` configured with Noto for relevant scripts. Add downloadable fonts via `FontsContractCompat`/`FontRequest`. Always test CJK, Arabic, Indic, RTL, and font scaling on real devices.

### Detailed Version
### Theoretical Foundations

**Complex scripts** — writing systems requiring advanced text shaping: CJK (Chinese/Japanese/Korean), Arabic with contextual forms, Indic scripts with combining marks, Thai/Lao with complex clusters.

**Rendering challenges:**
- **Glyph coverage** — many brand fonts support only Latin glyphs.
- **Text shaping** — complex scripts require ligatures, contextual forms, reordering.
- **Baseline alignment** — different scripts have different baseline requirements.
- **Line breaking** — script-specific word wrapping rules.

**Android font system:**
- **System fonts** — Roboto (Latin), Noto (international) as part of the system set and fallback chains.
- **Downloadable fonts** — Google Fonts API / `FontsContract` for dynamic loading.
- **Font resources** — XML configuration of font families and extension of generic families via `android:fallbackFor` (behavior and ordering are OEM-dependent).
- **Font synthesis** — fake bold/italic for unsupported styles.

### Requirements

**Functional:**
- Proper rendering of CJK, Arabic, and Indic scripts including ligatures and contextual forms.
- Support for mixed content (Latin + complex scripts + emoji).
- Robust handling of user-generated content where scripts are unknown upfront.

**Non-functional:**
- Minimal APK/`Bundle` size impact.
- Correct offline behavior when downloadable fonts are unavailable.
- Accessibility support: font scaling, RTL, screen readers.
- Stable performance for font loading and rendering.

### Architecture

- **Font/resources layer:**
  - Define base families (`sans-serif`, `serif`) and extended `font-family` configs with Noto for target scripts.
  - Use XML font resources and Compose `FontFamily` for consistent configuration.
- **Runtime font selection:**
  - Detect script via `UnicodeScript` and choose the appropriate `Typeface`/`FontFamily` for a specific text or substrings.
  - Fall back to system fonts when the brand font lacks coverage.
- **Downloadable fonts service:**
  - Wrapper over `FontsContractCompat` with in-memory/disk caching.
  - Async, on-demand delivery for specific scripts.
- **Testing/observability:**
  - Curated test strings per script.
  - Screenshot tests and manual checks on real devices across locales and font scales.

### 1. Requirements Analysis and Audit

**Identifying target scripts:**
- Analyze market requirements: CJK for Asian markets, Arabic for Middle East, Indic for South Asia.
- Check app content: user-generated text, translations, proper names.
- Evaluate scope: UI labels vs user content vs mixed text.

**Brand font audit (approximate coverage check):**
```kotlin
fun hasGlyph(font: Typeface, ch: Char): Boolean {
    val paint = Paint().apply { typeface = font }
    // Note: hasGlyph is more reliable on newer API; measureText is only a heuristic
    // and may treat tofu as a valid glyph.
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        paint.hasGlyph(ch.toString())
    } else {
        paint.measureText(ch.toString()) > 0f
    }
}

val testCases = mapOf("CJK" to "中文", "Arabic" to "العربية", "Devanagari" to "हिन्दी")

testCases.forEach { (script, text) ->
    val ok = text.all { hasGlyph(brandFont, it) }
    Log.d("FontAudit", "$script: $ok")
}
```

**Prioritization:**
- **UI chrome** (buttons, navigation) — critical, may require custom fonts with verified coverage.
- **Content text** (articles, messages) — flexible, system fallbacks acceptable.
- **User-generated content** — unpredictable, robust fallbacks/downloadable fonts essential.

### 2. Font Fallback Chains

Key idea: you typically do not hard-wire a fully custom fallback chain into a single family; instead, you combine brand fonts with system families and Noto in ways that let the engine apply its built-in fallbacks.

**Simple XML font-family:**
```xml
<font-family xmlns:android="http://schemas.android.com/apk/res/android">
    <font
        android:font="@font/brand_regular"
        android:fontStyle="normal"
        android:fontWeight="400" />
</font-family>
```

Use this for branded UI; keep content on `sans-serif`/system families so built-in fallbacks (including Noto on many devices) handle complex scripts.

**Declarative fallback for a generic family (API 26+):**
```xml
<font-family
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:fallbackFor="sans-serif">

    <font
        android:font="@font/noto_sans_cjk_jp"
        android:fontStyle="normal"
        android:fontWeight="400" />

    <font
        android:font="@font/noto_sans_arabic"
        android:fontStyle="normal"
        android:fontWeight="400" />
</font-family>
```

This configuration adds these fonts into the fallback set for the generic `sans-serif` family, but exact ordering/usage is up to the system/OEM; it is not a fully deterministic chain you control.

**Programmatic combo (API 28+):**
```kotlin
val brand = ResourcesCompat.getFont(context, R.font.brand_regular)
val cjk = ResourcesCompat.getFont(context, R.font.noto_sans_cjk_jp)
val arabic = ResourcesCompat.getFont(context, R.font.noto_sans_arabic)

// Example: choose font for the dominant script of this text.
// For mixed-script strings, consider splitting into substrings with different typefaces
// instead of forcing one typeface for all characters.
val typefaceForText = when {
    text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.ARABIC } -> arabic
    text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.HAN } -> cjk
    else -> brand
}

textView.typeface = typefaceForText
```

Note: there is no public API like `Typeface.Builder.setFallback(...)` to define an arbitrary ordered fallback chain. Use system generic families, XML resources, and runtime selection.

**Compose FontFamily:**
```kotlin
val ComplexFontFamily = FontFamily(
    Font(R.font.brand_regular),
    Font(R.font.noto_sans_cjk_jp),
    Font(R.font.noto_sans_arabic)
)

Text(
    text = text,
    fontFamily = ComplexFontFamily
)
```

Important: `Font(...)` takes resource IDs or a Typeface, not raw family name strings. Multiple Font entries primarily express variants (weight/style/etc.) and allow Compose/runtime to fall back within this family; they do not create a magical script-aware chain. For truly fine-grained control with mixed scripts, split text into runs or rely on system-level fallbacks.

### 3. Downloadable Fonts

**Font request (classic):**
```kotlin
val request = FontRequest(
    "com.google.android.gms.fonts",
    "com.google.android.gms",
    "Noto Sans CJK JP",
    R.array.com_google_android_gms_fonts_certs
)

FontsContractCompat.requestFont(context, request, callback, Handler(Looper.getMainLooper()))
```

**Compose integration (simplified):**
```kotlin
@Composable
fun DownloadableFontText(text: String) {
    val context = LocalContext.current
    var typeface by remember { mutableStateOf<Typeface?>(null) }

    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            typeface = downloadTypeface(context, "Noto Sans Arabic")
        }
    }

    val family = typeface?.let { FontFamily(Font(it)) } ?: FontFamily.Default

    Text(text = text, fontFamily = family)
}
```

`downloadTypeface` should wrap `FontsContractCompat` and callbacks into a suspend function; there is no built-in `await()` helper.

**Font caching (idea):**
```kotlin
class FontCache {
    private val memory = mutableMapOf<String, Typeface>()

    fun get(name: String): Typeface? = memory[name]

    fun put(name: String, typeface: Typeface) {
        memory[name] = typeface
    }
}
```

### 4. Rendering Settings

**`TextView` optimization:**
```kotlin
class OptimizedTextView(context: Context, attrs: AttributeSet? = null) : AppCompatTextView(context, attrs) {
    init {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            breakStrategy = Layout.BREAK_STRATEGY_HIGH_QUALITY
            hyphenationFrequency = Layout.HYPHENATION_FREQUENCY_NORMAL
        }
        // OpenType features like 'liga' and 'kern' are usually enabled by default;
        // set fontFeatureSettings only when you need specific optional features.
    }
}
```

**Compose rendering (simplified family selection by script):**
```kotlin
@Composable
fun ComplexScriptText(text: String) {
    val fontFamily = when {
        text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.HAN } ->
            FontFamily(Font(R.font.noto_sans_cjk_jp))
        text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.ARABIC } ->
            FontFamily(Font(R.font.noto_sans_arabic))
        text.any { Character.UnicodeScript.of(it.code) == Character.UnicodeScript.DEVANAGARI } ->
            FontFamily(Font(R.font.noto_sans_devanagari))
        else -> FontFamily.Default
    }

    // For strings containing multiple scripts, consider splitting into multiple Text
    // composables; otherwise rely on system fallbacks.
    Text(
        text = text,
        fontFamily = fontFamily
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
            fontFamily = FontFamily(Font(R.font.noto_sans_arabic))
            // Let the shaping engine handle joining; don't manually manage 'isol/init/medi/fina'.
        )
    }
}
```

### 5. Testing

**Glyph coverage test (diagnostic example):**
```kotlin
@Test
fun testComplexScriptCoverage() {
    val tests = mapOf(
        "Arabic" to "العربية",
        "Devanagari" to "हिन्दी",
        "CJK" to "中文日韓"
    )

    tests.forEach { (script, text) ->
        val ok = text.all { hasGlyph(brandFont, it) }
        // Approximate check; interpret as diagnostic signal, not a strict pass/fail.
        println("$script coverage (approx): $ok")
    }
}

private fun hasGlyph(font: Typeface, ch: Char): Boolean {
    val paint = Paint().apply { typeface = font }
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        paint.hasGlyph(ch.toString())
    } else {
        paint.measureText(ch.toString()) > 0f
    }
}
```

**Screenshot testing:**
```kotlin
@RunWith(AndroidJUnit4::class)
class TypographyScreenshotTest {
    @Test
    fun complexScripts() {
        val texts = listOf("English + العربية", "English + हिन्दी", "Mixed: Hello 世界")
        // Capture and compare screenshots at different font scales and locales.
    }
}
```

### 6. Performance Optimization

**`Bundle` size analysis (example):**
```kotlin
fun analyzeFontImpact() {
    val fontsMb = listOf(2.1f, 2.0f, 18.5f, 0.8f)
    val compressedTotal = fontsMb.sum() * 0.7f
    println("Font impact (approx compressed): ${compressedTotal}MB")
}
```

**Selective inclusion (concept):**

Avoid bundling full CJK fonts unless absolutely necessary; rely on system Noto fonts, downloadable fonts, and/or Play Feature Delivery / split APKs.

**On-demand delivery (concept):**
```kotlin
suspend fun loadScriptFont(script: String): Typeface {
    val fontName = when (script) {
        "arabic" -> "Noto Sans Arabic"
        "cjk" -> "Noto Sans CJK JP"
        else -> "Noto Sans"
    }

    // Implement downloadFont via FontsContractCompat or Play Feature Delivery.
    return fontCache.get(fontName) ?: downloadFont(fontName).also { fontCache.put(fontName, it) }
}
```

### Best Practices

- **Comprehensive audit** — validate brand fonts for all target scripts (`hasGlyph`-like APIs plus visual review).
- **Progressive enhancement** — start with system fonts and built-in fallbacks; add custom and downloadable fonts as needed.
- **Performance monitoring** — measure font loading times and bundle/module size impact.
- **Accessibility first** — test complex scripts with large font scales, high contrast, RTL, and screen readers.
- **Offline resilience** — cache downloaded fonts and always provide system fallbacks.

### Common Pitfalls

- **Assuming Latin coverage is universal** — most fonts lack CJK/Arabic/Indic glyphs.
- **Ignoring text shaping** — complex scripts rely on automatic contextual forms and ligatures.
- **Poor mixed-script alignment** — different scripts have different baselines.
- **No accessibility testing** — large font sizes and RTL can break layout without proper fallbacks.
- **Ignoring bundle size** — CJK fonts can add 20+ MB; prefer downloadable fonts or modularization.

## Follow-ups (RU)
- Как комбинировать латинский бренд-шрифт и Noto для контента без визуальных конфликтов?
- Как управлять загрузкой шрифтов при старте приложения (splash screen)?
- Какие инструменты использовать для автоматической проверки покрытия glyph?

## Follow-ups (EN)
- How can you combine a Latin brand font and Noto fonts for content without visual conflicts?
- How should you manage font loading during app startup (splash screen)?
- Which tools can be used to automatically verify glyph coverage?

## References (RU)
- [[c-android]]
- https://developer.android.com/guide/topics/text/downloadable-fonts

## References (EN)
- [[c-android]]
- https://developer.android.com/guide/topics/text/downloadable-fonts

## Related Questions

- [[c-android]]
- [[c-android-components]]
