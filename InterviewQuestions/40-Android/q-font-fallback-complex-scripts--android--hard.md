---
id: android-643
title: Font Fallback for Complex Scripts / Резерв шрифтов для сложных скриптов
aliases:
  - Font Fallback for Complex Scripts
  - Резерв шрифтов для сложных скриптов
topic: android
subtopics:
  - globalization
  - typography
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-globalization
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/globalization
  - typography
  - accessibility
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/topics/text/downloadable-fonts
    note: Downloadable fonts guide
  - url: https://developer.android.com/guide/topics/resources/font-resource
    note: Font resources
  - url: https://material.io/design/typography/international-typography.html
    note: International typography best practices
---

# Вопрос (RU)
> Как обеспечить корректное отображение сложных скриптов (CJK, арабский, индийские письменности) в Android: fallback цепочки, скачиваемые шрифты, Compose/TextView настройки и тестирование?

# Question (EN)
> How do you guarantee proper rendering for complex scripts (CJK, Arabic, Indic) in Android, covering font fallback chains, downloadable fonts, Compose/TextView configuration, and testing?

---

## Ответ (RU)

### 1. Анализ требований

- Выявите целевые рынки и скрипты (CJK, Thai, Devanagari, Arabic).
- Проверьте бренд-шрифт: поддерживает ли glyphs? Если нет → fallback или отдельные гарнитуры.
- Документируйте приоритет (UI chrome vs content).

### 2. Font fallback цепочка

- Для TextView: используйте `fontFamily` с font resources (`font/my_font.xml`) и `<family>` с `font` + `<font fallbackFor="sans-serif">`.
- Compose: `FontFamily` + `FontFamily.Resolver`; добавьте custom fallback через `FontFamily(listOf(Font(...), Font(...)))`.
- Учитывайте веса/стили; предоставьте `FontWeight` map.

### 3. Downloadable Fonts & dynamic loading

- Применяйте Google Fonts provider:

```kotlin
val request = FontRequest(
    "com.google.android.gms.fonts",
    "com.google.android.gms",
    "Noto Sans Arabic",
    R.array.com_google_android_gms_fonts_certs
)
FontsContractCompat.requestFont(context, request, callback, handler)
```

- Для Compose: `remember { FontFamily(Font(request = ...)) }`.
- Кешируйте результаты, учитывайте оффлайн fallback.

### 4. Rendering настройки

- TextView: включайте `setBreakStrategy(Layout.BREAK_STRATEGY_HIGH_QUALITY)`, `setHyphenationFrequency`.
- Compose: `Text` with `softWrap = true`, `overflow = TextOverflow.Ellipsis`, `lineHeight` адаптирован под script.
- Арабский/Indic: учитывайте ligatures; используйте `FontFeatureSettings`.

### 5. Тестирование

- Псевдо-тексты с сложными скриптами или реальные sample strings.
- Snapshot tests для разных локалей и размеров шрифта (accessibility).
- Device matrix: low-end, OEM с кастомными шрифтами.

### 6. Перфоманс и размер

- Оценивайте размер APK/AAB при включении шрифтов; используйте PAD/on-demand для больших гарнитур.
- Децентрализуйте шрифты (не дублируйте в нескольких модулях).
- Предусмотрите fallback на системные шрифты (Noto) при ошибках загрузки.

### 7. UX и i18n нюансы

- Проверяйте line height, baseline, text alignment (особенно смешанные скрипты).
- Поддержите bold/italic, если script допускает (иначе используйте weight variations).
- Учитывайте Emojis (EmojiCompat) и variation selectors.

---

## Answer (EN)

- Identify target scripts, audit brand fonts for glyph support, and define fallback priorities between UI and content text.
- Configure font families with explicit fallback chains (TextView `fontFamily`, Compose `FontFamily`) that include script-specific fonts.
- Use Downloadable Fonts to pull Noto or other fonts at runtime; cache results and provide offline fallbacks.
- Tweak rendering settings (break strategy, hyphenation, line height) and ensure ligatures and shaping features are enabled.
- Test with real complex-script content across locales, large fonts, and device matrices; include snapshot testing.
- Manage bundle size by sharing fonts, using on-demand packs if needed, and defaulting to system fonts when dynamic fetch fails.
- Watch UX details such as baseline alignment, weight support, and emoji compatibility for multilingual content.

---

## Follow-ups
- Как комбинировать латинский бренд-шрифт и Noto для контента без визуальных конфликтов?
- Как управлять загрузкой шрифтов при старте приложения (splash screen)?
- Какие инструменты использовать для автоматической проверки покрытия glyph?

## References
- [[c-globalization]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/topics/text/downloadable-fonts
