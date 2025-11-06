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
related: [c-accessibility, c-dimension-units]
created: 2025-10-15
updated: 2025-10-29
tags: [accessibility, android/ui-accessibility, android/ui-widgets, difficulty/easy, dp, sp, ui]
sources: [https://developer.android.com/guide/topics/resources/more-resources#Dimension]
---

# Вопрос (RU)
> В чем разница между единицами измерения dp и sp?

# Question (EN)
> What is the difference between measurement units dp and sp?

---

## Ответ (RU)

Android использует две масштабируемые единицы измерения: **dp** (density-independent pixels) для размеров UI элементов и **sp** (scale-independent pixels) для текста. Обе адаптируются к плотности экрана, но sp дополнительно учитывает пользовательские настройки размера шрифта.

**Основные различия:**
- **dp**: масштабируется только с плотностью экрана (dpi)
- **sp**: масштабируется с плотностью экрана + пользовательские настройки текста
- **dp**: для размеров, отступов, границ UI элементов
- **sp**: только для размеров текста (включая text в Button)

**Примеры:**

```xml
<!-- ✅ Правильно: dp для размеров элементов -->
<Button
    android:layout_width="120dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:textSize="16sp" /> <!-- ✅ sp для текста -->

<!-- ❌ Неправильно: sp для размеров элемента -->
<ImageView
    android:layout_width="64sp"
    android:layout_height="64sp" /> <!-- Игнорирует настройки пользователя -->
```

**Compose:**

```kotlin
// ✅ Правильно
Text(
    text = "Hello",
    fontSize = 16.sp,  // sp для текста
    modifier = Modifier.padding(16.dp)  // dp для отступов
)

// ❌ Неправильно
Box(
    modifier = Modifier.size(48.sp)  // sp не для размеров контейнера
)
```

## Answer (EN)

Android uses two scalable measurement units: **dp** (density-independent pixels) for UI element sizes and **sp** (scale-independent pixels) for text. Both adapt to screen density, but sp additionally respects user font size preferences.

**Key Differences:**
- **dp**: scales only with screen density (dpi)
- **sp**: scales with screen density + user text preferences
- **dp**: for dimensions, spacing, borders of UI elements
- **sp**: only for text sizes (including text in Button)

**Examples:**

```xml
<!-- ✅ Correct: dp for element dimensions -->
<Button
    android:layout_width="120dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:textSize="16sp" /> <!-- ✅ sp for text -->

<!-- ❌ Wrong: sp for element dimensions -->
<ImageView
    android:layout_width="64sp"
    android:layout_height="64sp" /> <!-- Ignores user preferences -->
```

**Compose:**

```kotlin
// ✅ Correct
Text(
    text = "Hello",
    fontSize = 16.sp,  // sp for text
    modifier = Modifier.padding(16.dp)  // dp for spacing
)

// ❌ Wrong
Box(
    modifier = Modifier.size(48.sp)  // sp not for container size
)
```

---

## Follow-ups

- How do dp and sp convert to physical pixels on different screen densities (mdpi, hdpi, xxhdpi)?
- What happens to UI layout when users change system font size from Settings?
- Should you use dp or sp for icon sizes? Why?
- How does Compose handle dp/sp units differently from XML Views?
- What are the accessibility implications of using dp for text instead of sp?

## References

- [[c-dp-sp-units]] - Understanding density-independent units
- [Android Dimensions Guide](https://developer.android.com/guide/topics/resources/more-resources#Dimension) - Official documentation
- [Material Design Metrics](https://m2.material.io/design/layout/spacing-methods.html) - Layout metrics and keylines
- [Compose Units](https://developer.android.com/jetpack/compose/designsystems/custom#unit-types) - Dp and Sp in Compose

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Understanding Android components
- [[q-compose-basics--android--easy]] - Jetpack Compose fundamentals

### Related (Same Level)
- [[q-accessibility-color-contrast--android--medium]] - Accessibility best practices
- [[q-compose-navigation-advanced--android--medium]] - Navigation patterns
- [[q-android-ui-fundamentals--android--easy]] - UI design principles

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation
- [[q-android-runtime-internals--android--hard]] - Platform internals
