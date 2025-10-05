---
id: 202510031414
title: What is dp / Что такое dp
aliases: []

# Classification
topic: android
subtopics: [android, ui, units]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/608
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-units
  - c-android-density

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [dp, units, difficulty/easy, easy_kotlin, lang/ru, android/units, android/ui]
---

# Question (EN)
> What is dp

# Вопрос (RU)
> Что такое dp

---

## Answer (EN)

**dp** (Density-independent Pixels) is a measurement unit in Android used to create adaptive interfaces. It scales based on device screen density, ensuring consistent visual size of elements across different screens.

### Basic Concept

- **1 dp = 1 pixel** on a 160 dpi (mdpi) screen
- Automatically scales on other densities
- Physical size remains visually consistent

### Example Usage

```xml
<Button
    android:layout_width="200dp"
    android:layout_height="48dp"
    android:padding="16dp" />
```

```kotlin
// Convert dp to pixels
fun Int.dpToPx(context: Context): Int {
    return (this * context.resources.displayMetrics.density).toInt()
}

val widthInPx = 48.dpToPx(context)
```

## Ответ (RU)

dp (Density-independent Pixels) это единица измерения в Android используемая для создания адаптивных интерфейсов Она масштабируется в зависимости от плотности экрана устройства обеспечивая одинаковый визуальный размер элементов на разных экранах

---

## Follow-ups
- How does the scaling factor work for different screen densities?
- When should you use dp vs sp vs px?
- How do you convert between dp and pixels programmatically?

## References
- [[c-android-units]]
- [[c-android-density]]
- [[moc-android]]

## Related Questions
- [[q-difference-between-dp-and-sp--android--easy]]
