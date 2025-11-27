---
id: android-264
title: "Measurement Units: dp vs sp / Единицы измерения: dp vs sp"
aliases: ["Measurement Units: dp vs sp", "Единицы измерения: dp vs sp"]
topic: android
subtopics: [ui-accessibility, ui-widgets]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-accessibility]
created: 2025-10-15
updated: 2025-11-10
tags: [accessibility, android/ui-accessibility, android/ui-widgets, difficulty/easy, dp, sp, ui]
sources: ["https://developer.android.com/guide/topics/resources/more-resources#Dimension"]
date created: Saturday, November 1st 2025, 1:25:40 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)
> В чем разница между единицами измерения dp и sp?

# Question (EN)
> What is the difference between measurement units dp and sp?

---

## Ответ (RU)

Android использует две масштабируемые логические единицы измерения: **dp** (density-independent pixels) для размеров UI-элементов и **sp** (scale-independent pixels) в первую очередь для текста. Обе единицы зависят от плотности экрана, но **sp** дополнительно учитывает пользовательские настройки масштаба/размера шрифта (font scale).

**Основные различия:**
- **dp**: масштабируется только с плотностью экрана (dpi)
- **sp**: масштабируется с плотностью экрана + пользовательским масштабом текста
- **dp**: рекомендуется для размеров, отступов, границ и других параметров макета UI-элементов
- **sp**: рекомендуется для размеров текста (включая текст в Button и других текстовых компонентах), чтобы уважать настройки доступности

**Примеры:**

```xml
<!-- ✅ Правильно: dp для размеров элементов, sp для текста -->
<Button
    android:layout_width="120dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:textSize="16sp" /> <!-- ✅ sp для текста (учитывает масштаб шрифта пользователя) -->

<!-- ❌ Неправильно: sp для размеров элемента -->
<ImageView
    android:layout_width="64sp"
    android:layout_height="64sp" /> <!-- Размер иконки начнет зависеть от настроек шрифта, что ломает предсказуемый макет -->
```

**Compose:**

```kotlin
// ✅ Правильно
Text(
    text = "Hello",
    fontSize = 16.sp,  // sp для текста (учитывает font scale)
    modifier = Modifier.padding(16.dp)  // dp для отступов и размеров макета
)

// ❌ Неправильно
Box(
    modifier = Modifier.size(48.sp)  // sp не подходит для размеров контейнеров; привязка к font scale может сломать layout
)
```

## Answer (EN)

Android uses two scalable logical units: **dp** (density-independent pixels) for UI element dimensions and **sp** (scale-independent pixels) primarily for text. Both are based on screen density, but **sp** additionally respects the user font scale / text size preferences.

**Key Differences:**
- **dp**: scales only with screen density (dpi)
- **sp**: scales with screen density + user font scale
- **dp**: recommended for view dimensions, spacing, padding, margins, and borders
- **sp**: recommended for text sizes (including text in Buttons and other text components) to respect accessibility settings

**Examples:**

```xml
<!-- ✅ Correct: dp for element dimensions, sp for text -->
<Button
    android:layout_width="120dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:textSize="16sp" /> <!-- ✅ sp for text (respects user's font scale) -->

<!-- ❌ Wrong: sp for element dimensions -->
<ImageView
    android:layout_width="64sp"
    android:layout_height="64sp" /> <!-- Icon size will depend on font scale, breaking predictable layout -->
```

**Compose:**

```kotlin
// ✅ Correct
Text(
    text = "Hello",
    fontSize = 16.sp,  // sp for text (respects font scale)
    modifier = Modifier.padding(16.dp)  // dp for layout spacing and dimensions
)

// ❌ Wrong
Box(
    modifier = Modifier.size(48.sp)  // sp is not appropriate for container size; tying it to font scale can break the layout
)
```

---

## Последующие Вопросы (RU)

- Как dp и sp конвертируются в физические пиксели на экранах с разной плотностью (mdpi, hdpi, xxhdpi)?
- Что происходит с макетом UI, когда пользователь меняет размер шрифта в настройках системы?
- Следует ли использовать dp или sp для размеров иконок? Почему?
- Как Compose обрабатывает единицы dp/sp по сравнению с XML Views?
- Каковы последствия для доступности при использовании dp для текста вместо sp?

## Follow-ups

- How do dp and sp convert to physical pixels on different screen densities (mdpi, hdpi, xxhdpi)?
- What happens to UI layout when users change system font size from Settings?
- Should you use dp or sp for icon sizes? Why?
- How does Compose handle dp/sp units differently from XML Views?
- What are the accessibility implications of using dp for text instead of sp?

## Ссылки (RU)

- [Android Dimensions Guide](https://developer.android.com/guide/topics/resources/more-resources#Dimension) — Официальная документация
- [Material Design Metrics](https://m2.material.io/design/layout/spacing-methods.html) — Метрики и ключевые линии макета
- [Compose Units](https://developer.android.com/jetpack/compose/designsystems/custom#unit-types) — Dp и Sp в Compose

## References

- [Android Dimensions Guide](https://developer.android.com/guide/topics/resources/more-resources#Dimension) - Official documentation
- [Material Design Metrics](https://m2.material.io/design/layout/spacing-methods.html) - Layout metrics and keylines
- [Compose Units](https://developer.android.com/jetpack/compose/designsystems/custom#unit-types) - Dp and Sp in Compose

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-app-components--android--easy]] - Понимание компонентов Android

### Похожие (того Же уровня)
- [[q-accessibility-color-contrast--android--medium]] - Практики доступности
- [[q-compose-navigation-advanced--android--medium]] - Паттерны навигации в Compose

### Продвинутые (сложнее)
- [[q-compose-custom-layout--android--hard]] - Реализация пользовательских Layout-ов в Compose
- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство платформы

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Understanding Android components

### Related (Same Level)
- [[q-accessibility-color-contrast--android--medium]] - Accessibility best practices
- [[q-compose-navigation-advanced--android--medium]] - Navigation patterns

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation
- [[q-android-runtime-internals--android--hard]] - Platform internals
