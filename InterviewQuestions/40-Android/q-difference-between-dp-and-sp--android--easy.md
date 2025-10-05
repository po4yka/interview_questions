---
id: 202510031415
title: What is the difference between measurement units like dp and sp / Чем отличаются единицы измерения например dp от sp
aliases: []

# Classification
topic: android
subtopics: [android, ui, units]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/615
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-units
  - c-android-accessibility

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [dp, sp, units, difficulty/easy, easy_kotlin, lang/ru, android/units, android/ui]
---

# Question (EN)
> What is the difference between measurement units like dp and sp

# Вопрос (RU)
> Чем отличаются единицы измерения например dp от sp

---

## Answer (EN)

**dp** (Density-independent Pixels) depends only on screen density and is used for UI element dimensions. **sp** (Scale-independent Pixels) additionally takes into account user font size settings, making it the preferred unit for text elements.

### Key Differences

| Feature | dp | sp |
|---------|----|----|
| Scales with screen density | ✅ | ✅ |
| Scales with font size setting | ❌ | ✅ |
| Use for | Layouts, dimensions | Text sizes |
| Respects accessibility | No | Yes |

### dp - For Dimensions

```xml
<Button
    android:layout_width="200dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:layout_margin="8dp" />

<ImageView
    android:layout_width="24dp"
    android:layout_height="24dp" />
```

### sp - For Text

```xml
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="16sp"
    android:padding="12dp" />
```

### Why Use sp for Text

```kotlin
// User can change font size in system settings
// sp adjusts automatically, dp does not

// Small font (0.85x)
16sp → ~13.6sp actual

// Normal font (1.0x)
16sp → 16sp actual

// Large font (1.15x)
16sp → ~18.4sp actual

// Huge font (1.3x)
16sp → ~20.8sp actual
```

### Best Practices

```xml
<!-- ✅ CORRECT -->
<TextView
    android:textSize="16sp"
    android:padding="8dp" />

<!-- ❌ WRONG - Don't use sp for dimensions -->
<View
    android:layout_width="100sp"
    android:layout_height="100sp" />

<!-- ❌ WRONG - Don't use dp for text -->
<TextView
    android:textSize="16dp" />
```

## Ответ (RU)

dp зависит только от плотности экрана и используется для размеров интерфейса sp Scale-independent Pixels дополнительно учитывает пользовательские настройки размера шрифта что делает его предпочтительным для текстовых элементов

---

## Follow-ups
- How do you handle layouts when users set very large font sizes?
- What's the impact of sp on accessibility?
- Should you ever use dp for text sizes?

## References
- [[c-android-units]]
- [[c-android-accessibility]]
- [[c-android-typography]]
- [[moc-android]]

## Related Questions
- [[q-what-is-dp-unit--android--easy]]
