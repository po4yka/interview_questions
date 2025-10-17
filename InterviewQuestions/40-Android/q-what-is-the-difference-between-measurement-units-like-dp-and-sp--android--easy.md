---
id: "20251015082237430"
title: "What Is The Difference Between Measurement Units Like Dp And Sp / What Is The Difference Between Measurement Units Like Dp и Sp"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [android ui, dp, sp, ui, difficulty/easy]
---
# Чем отличаются единицы измерения например dp от sp

**English**: What is the difference between measurement units like dp and sp?

## Answer (EN)
### dp (Density-Independent Pixels)

**dp** is used for layout and UI element sizes, providing the same physical size on all devices regardless of screen density.

```xml
<!-- Using dp for layout dimensions -->
<Button
    android:layout_width="100dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:text="Click Me" />

<ImageView
    android:layout_width="64dp"
    android:layout_height="64dp"
    android:src="@drawable/icon" />
```

**Characteristics:**
- Independent of screen pixel density
- 1dp ≈ 1/160 inch on any screen
- Ensures consistent physical size across devices
- Used for margins, padding, dimensions, and all non-text UI elements

### sp (Scale-Independent Pixels)

**sp** is used for text font sizes and scales with both screen density changes and user text scaling preferences.

```xml
<!-- Using sp for text sizes -->
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="16sp"
    android:text="Normal text" />

<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="24sp"
    android:text="Large heading"
    android:textStyle="bold" />
```

**Characteristics:**
- Scales with screen density (like dp)
- Additionally scales with user's font size preferences in system settings
- Respects accessibility settings
- Used exclusively for text sizes

### Main Difference

The **main difference** is that **sp respects user's text scale preferences** set in system accessibility settings, while **dp does not**.

| Feature | dp | sp |
|---------|----|----|
| Screen density scaling | Yes | Yes |
| User text size preference | No | Yes |
| Primary use case | UI elements, layouts | Text sizes |
| Accessibility support | No | Yes |

### Best Practices

```xml
<!-- Good practice -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="16dp">  <!-- dp for spacing -->

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="14sp"  <!-- sp for text -->
        android:text="@string/label" />

    <Button
        android:layout_width="120dp"  <!-- dp for dimensions -->
        android:layout_height="48dp"
        android:textSize="16sp"  <!-- sp for button text -->
        android:text="@string/button_text" />
</LinearLayout>

<!-- Bad practice - don't do this -->
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="14dp"  <!-- Wrong: using dp for text -->
    android:text="Text" />
```

### Why This Matters

Using **dp** for all UI sizes except text and **sp** for text sizes allows your application to:
1. Look consistent across devices with different screen densities
2. Respect user accessibility preferences for larger text
3. Provide better user experience for users with visual impairments
4. Follow Android design guidelines and best practices

## Ответ (RU)
dp (density-independent pixels) используется для размеров макета и элементов интерфейса, обеспечивая одинаковый физический размер на всех устройствах независимо от плотности экрана. sp (scale-independent pixels) используется для размеров шрифтов текста и масштабируется не только с изменением плотности экрана но и в зависимости от пользовательских настроек масштабирования текста. Основное различие в том что sp учитывает предпочтения пользователя по масштабу текста. dp рекомендуется использовать для всех размеров в пользовательском интерфейсе кроме текста. В XML-разметке Android размер текста указывается в sp а другие размеры в dp. Это позволяет оптимизировать приложение для различных устройств и настроек доступности

