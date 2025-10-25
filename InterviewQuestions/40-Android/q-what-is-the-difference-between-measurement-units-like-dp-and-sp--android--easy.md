---
id: 20251012-122711166
title: "Measurement Units: dp vs sp / Единицы измерения: dp vs sp"
aliases:
  - "Measurement Units: dp vs sp"
  - "Единицы измерения: dp vs sp"
topic: android
subtopics: [ui-units]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dp-sp-units, q-accessibility-color-contrast--android--medium, q-compose-navigation-advanced--android--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android/ui-units, dp, sp, ui, accessibility, difficulty/easy]
sources: [https://developer.android.com/guide/topics/resources/more-resources#Dimension]
---

# Вопрос (RU)
> В чем разница между единицами измерения dp и sp?

# Question (EN)
> What is the difference between measurement units dp and sp?

---

## Ответ (RU)

**Теория единиц измерения:**
Android использует две основные единицы измерения: dp для размеров UI элементов и sp для размеров текста. Обе масштабируются с плотностью экрана, но sp дополнительно учитывает пользовательские настройки масштабирования текста.

**dp (Density-Independent Pixels):**
Используется для размеров макета и UI элементов, обеспечивая одинаковый физический размер на всех устройствах.

```xml
<!-- dp для размеров элементов -->
<Button
    android:layout_width="100dp"
    android:layout_height="48dp"
    android:padding="16dp" />

<ImageView
    android:layout_width="64dp"
    android:layout_height="64dp" />
```

**sp (Scale-Independent Pixels):**
Используется для размеров текста и масштабируется с пользовательскими настройками доступности.

```xml
<!-- sp для размеров текста -->
<TextView
    android:textSize="16sp"
    android:text="Обычный текст" />

<TextView
    android:textSize="24sp"
    android:text="Заголовок"
    android:textStyle="bold" />
```

**Ключевые различия:**
- dp: масштабируется только с плотностью экрана
- sp: масштабируется с плотностью экрана + настройки пользователя
- dp: для всех UI элементов кроме текста
- sp: только для размеров текста

**Правильное использование:**
```xml
<LinearLayout
    android:padding="16dp"> <!-- dp для отступов -->

    <TextView
        android:textSize="14sp" <!-- sp для текста -->
        android:text="Текст" />

    <Button
        android:layout_width="120dp" <!-- dp для размеров -->
        android:layout_height="48dp"
        android:textSize="16sp" /> <!-- sp для текста кнопки -->
</LinearLayout>
```

## Answer (EN)

**Measurement Units Theory:**
Android uses two main measurement units: dp for UI element sizes and sp for text sizes. Both scale with screen density, but sp additionally respects user text scaling preferences.

**dp (Density-Independent Pixels):**
Used for layout and UI element sizes, ensuring consistent physical size across all devices.

```xml
<!-- dp for element dimensions -->
<Button
    android:layout_width="100dp"
    android:layout_height="48dp"
    android:padding="16dp" />

<ImageView
    android:layout_width="64dp"
    android:layout_height="64dp" />
```

**sp (Scale-Independent Pixels):**
Used for text sizes and scales with user accessibility settings.

```xml
<!-- sp for text sizes -->
<TextView
    android:textSize="16sp"
    android:text="Normal text" />

<TextView
    android:textSize="24sp"
    android:text="Heading"
    android:textStyle="bold" />
```

**Key Differences:**
- dp: scales only with screen density
- sp: scales with screen density + user settings
- dp: for all UI elements except text
- sp: only for text sizes

**Correct Usage:**
```xml
<LinearLayout
    android:padding="16dp"> <!-- dp for spacing -->

    <TextView
        android:textSize="14sp" <!-- sp for text -->
        android:text="Text" />

    <Button
        android:layout_width="120dp" <!-- dp for dimensions -->
        android:layout_height="48dp"
        android:textSize="16sp" /> <!-- sp for button text -->
</LinearLayout>
```

---

## Follow-ups

- How do dp and sp behave on different screen densities?
- What happens when users change system font size settings?
- How do you handle measurement units in Compose?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-compose-basics--android--easy]] - Compose basics

### Related (Same Level)
- [[q-accessibility-color-contrast--android--medium]] - Accessibility
- [[q-compose-navigation-advanced--android--medium]] - Compose navigation
- [[q-android-ui-fundamentals--android--easy]] - UI fundamentals

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts
- [[q-android-runtime-internals--android--hard]] - Runtime internals
