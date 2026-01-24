---
id: android-acc-003
title: Minimum Touch Target Size / Minimal'nyj razmer oblasti kasaniya
aliases: [Touch Target Size, 48dp minimum, Razmer oblasti kasaniya]
topic: android
subtopics: [accessibility, ui-views, ui-compose]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-what-is-dp--android--easy, q-content-descriptions--accessibility--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/accessibility, android/ui-views, android/ui-compose, difficulty/easy, accessibility, touch-target]

---
# Vopros (RU)
> Kakoj minimal'nyj razmer oblasti kasaniya rekomendovan dlya dostupnosti v Android?

# Question (EN)
> What is the minimum recommended touch target size for accessibility in Android?

---

## Otvet (RU)

**Minimal'nyj razmer oblasti kasaniya** - **48x48 dp** (density-independent pixels). Eto rekomendatsiya Material Design i trebovanie WCAG dlya obespecheniya dostupnosti pol'zovatelyam s ogranichennymi motornymi vozmozhnostyami.

### Pochemu 48dp?

- **Fizicheskij razmer**: 48dp ~ 9mm na ekrane - udobno dlya kasaniya pal'tsem
- **Motor coordination**: Lyudi s tremor ili ogranichennojmotorikoj mogut tochno popast' po tseli
- **WCAG 2.1**: Sootvetstvuet standartu dostupnosti (minimum 44x44 CSS px v vebe)
- **Material Design**: Oficial'naya rekomendatsiya Google

### Realizatsiya v Jetpack Compose

```kotlin
// Komponenty Material 3 avtomaticheski soblyudayut 48dp
IconButton(onClick = { /* ... */ }) { // Touch target >= 48dp
    Icon(
        imageVector = Icons.Default.Favorite,
        contentDescription = "Dobavit' v izbrannoe",
        modifier = Modifier.size(24.dp) // Ikonka men'she, no oblast' kasaniya 48dp
    )
}

// Ruchnoe uvelichenie touch target
Icon(
    imageVector = Icons.Default.Close,
    contentDescription = "Zakryt'",
    modifier = Modifier
        .size(16.dp) // Malen'kaya ikonka
        .clickable { /* ... */ }
        .sizeIn(minWidth = 48.dp, minHeight = 48.dp) // Touch target 48dp
)

// S ispol'zovaniem minimumInteractiveComponentSize
Icon(
    imageVector = Icons.Default.Add,
    contentDescription = "Dobavit'",
    modifier = Modifier
        .clickable { /* ... */ }
        .minimumInteractiveComponentSize() // Garantiruet 48dp
)
```

### Realizatsiya v Views (XML)

```xml
<!-- Uvelichenie oblasti kasaniya cherez padding -->
<ImageButton
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:padding="12dp"
    android:src="@drawable/ic_small_icon"
    android:contentDescription="@string/action_description" />

<!-- TouchDelegate dlya rasshireniya oblasti -->
<FrameLayout
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:minWidth="48dp"
    android:minHeight="48dp">

    <ImageView
        android:id="@+id/smallIcon"
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="center" />
</FrameLayout>
```

### TouchDelegate dlya rasshireniya oblasti (Views)

```kotlin
// Rasshirenie oblasti kasaniya programno
val parent = iconView.parent as View
parent.post {
    val rect = Rect()
    iconView.getHitRect(rect)

    // Rasshiryaem na 24dp s kazhdoj storony
    val extraPadding = (24 * resources.displayMetrics.density).toInt()
    rect.inset(-extraPadding, -extraPadding)

    parent.touchDelegate = TouchDelegate(rect, iconView)
}
```

### Pravilnyj spacing mezhdu elementami

```kotlin
// Compose - dostatochnyj otstup mezhdu knopkami
Row(
    horizontalArrangement = Arrangement.spacedBy(8.dp) // Minimum 8dp mezhdu 48dp targetami
) {
    IconButton(onClick = { /* ... */ }) {
        Icon(Icons.Default.Edit, contentDescription = "Redaktirovat'")
    }
    IconButton(onClick = { /* ... */ }) {
        Icon(Icons.Default.Delete, contentDescription = "Udalit'")
    }
}
```

### Proverka touch target razmerov

```kotlin
// Compose UI Test
composeTestRule
    .onNodeWithContentDescription("Dobavit' v izbrannoe")
    .assertTouchHeightIsAtLeast(48.dp)
    .assertTouchWidthIsAtLeast(48.dp)

// Accessibility Scanner avtomaticheski proverit razmery
```

### Tipichnye problemy i resheniya

| Problema | Reshenie |
|----------|----------|
| Ikonka 24dp bez paddinga | Ispol'zujte IconButton ili dobav'te padding |
| Checkbox/Radio slishkom malen'kie | Material komponenty imeyut pravilnyj razmer po umolchaniyu |
| Tekst-ssylka slishkom malen'kaya | Dobav'te vertikalnye otstapy ili ispol'zujte TextButton |
| Elementy slishkom blizko | Dobav'te spacing mezhdu interaktivnymi elementami |

### Rekomendatsii Material Design

| Komponent | Minimalnyj touch target |
|-----------|------------------------|
| Button | 48dp vysota |
| IconButton | 48x48dp |
| Checkbox | 48x48dp (vklyuchaya padding) |
| Radio button | 48x48dp (vklyuchaya padding) |
| Switch | 48dp vysota |
| TextField | 56dp vysota (rekomendovano) |
| List item | 48dp vysota minimum |

### Isklyucheniya

- **Inline tekst**: Ssylki vnutri paragrafa mogut byt' men'she
- **Plotnye spiski**: V spiskah mozhno ispol'zovat' 40dp pri neobhodimosti
- **Klavier'a**: Klavishi klaviatury imeyut sobstvennye standarty

---

## Answer (EN)

**Minimum touch target size** is **48x48 dp** (density-independent pixels). This is a Material Design recommendation and WCAG requirement to ensure accessibility for users with limited motor abilities.

### Why 48dp?

- **Physical size**: 48dp ~ 9mm on screen - comfortable for finger taps
- **Motor coordination**: People with tremors or limited motor skills can accurately hit targets
- **WCAG 2.1**: Meets accessibility standard (minimum 44x44 CSS px on web)
- **Material Design**: Official Google recommendation

### Implementation in Jetpack Compose

```kotlin
// Material 3 components automatically comply with 48dp
IconButton(onClick = { /* ... */ }) { // Touch target >= 48dp
    Icon(
        imageVector = Icons.Default.Favorite,
        contentDescription = "Add to favorites",
        modifier = Modifier.size(24.dp) // Icon is smaller, but touch area is 48dp
    )
}

// Manually increasing touch target
Icon(
    imageVector = Icons.Default.Close,
    contentDescription = "Close",
    modifier = Modifier
        .size(16.dp) // Small icon
        .clickable { /* ... */ }
        .sizeIn(minWidth = 48.dp, minHeight = 48.dp) // Touch target 48dp
)

// Using minimumInteractiveComponentSize
Icon(
    imageVector = Icons.Default.Add,
    contentDescription = "Add",
    modifier = Modifier
        .clickable { /* ... */ }
        .minimumInteractiveComponentSize() // Guarantees 48dp
)
```

### Implementation in Views (XML)

```xml
<!-- Increasing touch area via padding -->
<ImageButton
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:padding="12dp"
    android:src="@drawable/ic_small_icon"
    android:contentDescription="@string/action_description" />

<!-- TouchDelegate for expanding area -->
<FrameLayout
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:minWidth="48dp"
    android:minHeight="48dp">

    <ImageView
        android:id="@+id/smallIcon"
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="center" />
</FrameLayout>
```

### TouchDelegate for Expanding Area (Views)

```kotlin
// Programmatically expanding touch area
val parent = iconView.parent as View
parent.post {
    val rect = Rect()
    iconView.getHitRect(rect)

    // Expand by 24dp on each side
    val extraPadding = (24 * resources.displayMetrics.density).toInt()
    rect.inset(-extraPadding, -extraPadding)

    parent.touchDelegate = TouchDelegate(rect, iconView)
}
```

### Proper Spacing Between Elements

```kotlin
// Compose - adequate spacing between buttons
Row(
    horizontalArrangement = Arrangement.spacedBy(8.dp) // Minimum 8dp between 48dp targets
) {
    IconButton(onClick = { /* ... */ }) {
        Icon(Icons.Default.Edit, contentDescription = "Edit")
    }
    IconButton(onClick = { /* ... */ }) {
        Icon(Icons.Default.Delete, contentDescription = "Delete")
    }
}
```

### Verifying Touch Target Sizes

```kotlin
// Compose UI Test
composeTestRule
    .onNodeWithContentDescription("Add to favorites")
    .assertTouchHeightIsAtLeast(48.dp)
    .assertTouchWidthIsAtLeast(48.dp)

// Accessibility Scanner automatically checks sizes
```

### Common Problems and Solutions

| Problem | Solution |
|---------|----------|
| 24dp icon without padding | Use IconButton or add padding |
| Checkbox/Radio too small | Material components have correct default size |
| Text link too small | Add vertical padding or use TextButton |
| Elements too close | Add spacing between interactive elements |

### Material Design Recommendations

| Component | Minimum touch target |
|-----------|---------------------|
| Button | 48dp height |
| IconButton | 48x48dp |
| Checkbox | 48x48dp (including padding) |
| Radio button | 48x48dp (including padding) |
| Switch | 48dp height |
| TextField | 56dp height (recommended) |
| List item | 48dp height minimum |

### Exceptions

- **Inline text**: Links within paragraphs can be smaller
- **Dense lists**: Lists can use 40dp when necessary
- **Keyboard**: Keyboard keys have their own standards

---

## Follow-ups

- How does touch target size interact with padding and margins?
- What happens when touch targets overlap?
- How to handle touch targets in RecyclerView/LazyColumn items?
- How does screen density affect actual touch target physical size?

## References

- Material Design Touch Targets: https://m3.material.io/foundations/accessible-design/accessibility-basics
- WCAG Target Size: https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
- Android Accessibility: https://developer.android.com/guide/topics/ui/accessibility

## Related Questions

### Prerequisites
- [[q-what-is-dp--android--easy]] - Understanding dp units
- [[q-view-fundamentals--android--easy]] - View basics

### Related
- [[q-content-descriptions--accessibility--medium]] - Content descriptions
- [[q-talkback-support--accessibility--medium]] - TalkBack support
- [[q-accessibility-testing--accessibility--medium]] - Accessibility testing
