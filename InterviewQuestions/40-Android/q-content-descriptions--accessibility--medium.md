---
id: android-accessibility-001
title: Content Descriptions / Описания контента для доступности
aliases:
- Content Descriptions
- contentDescription
- importantForAccessibility
- Описания контента
topic: android
subtopics:
- accessibility
- ui
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-accessibility
- q-accessibility-compose--android--medium
- q-accessibility-talkback--android--medium
- q-custom-view-accessibility--android--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/guide/topics/ui/accessibility/apps
- https://developer.android.com/jetpack/compose/accessibility
tags:
- accessibility
- android/ui-accessibility
- difficulty/medium
- talkback
- contentDescription
---
# Vopros (RU)
> Kak pravilno ispolzovat contentDescription i importantForAccessibility dlya dostupnosti v Android?

# Question (EN)
> How to properly use contentDescription and importantForAccessibility for accessibility in Android?

---

## Otvet (RU)

**`contentDescription`** - tekstovoe opisanie elementa dlya sluzhb dostupnosti (TalkBack), **`importantForAccessibility`** - opredelyaet, dolzhen li element byt viden sluzhbam dostupnosti.

### Kogda Ispolzovat contentDescription

**1. Ikonki bez podpisi (View system)**

```kotlin
// Ikonka bez teksta - nuzhno opisanie
<ImageButton
    android:id="@+id/delete_button"
    android:src="@drawable/ic_delete"
    android:contentDescription="@string/delete_item" />

// Ikonka s tekstom ryadom - opisanie ne nuzhno
<ImageView
    android:src="@drawable/ic_star"
    android:contentDescription="@null"
    android:importantForAccessibility="no" />
<TextView android:text="Favorites" />
```

**2. Compose**

```kotlin
// Znachimoe izobrazhenie
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "Foto profilya polzovatelya"  // Opisyvaet naznachenie
)

// Dekorativnyy element
Image(
    painter = painterResource(R.drawable.background_pattern),
    contentDescription = null  // null = ignoriruetsya TalkBack
)

// Ikonka s tekstom - ikonka dekorativnaya
Row(
    modifier = Modifier
        .clickable { }
        .semantics(mergeDescendants = true) { }
) {
    Icon(
        Icons.Default.Favorite,
        contentDescription = null  // Tekst ryadom opisyvaet
    )
    Text("Izbrannoe")  // TalkBack: "Izbrannoe, knopka"
}
```

### importantForAccessibility

**Znacheniya:**

| Znachenie | Opisanie | Primer |
|-----------|----------|--------|
| `auto` (default) | Sistema reshaet | Bolshinstvo elementov |
| `yes` | Vsegda vidim | Custom interaktivnye elementy |
| `no` | Ignoriruetsya | Dekorativnye elementy |
| `noHideDescendants` | Ignoriruetsya vmeste s potomkami | Konteyner dekorativnogo kontenta |

```kotlin
// View system
<ImageView
    android:importantForAccessibility="no"
    android:src="@drawable/decorative_divider" />

// Skryt konteyner i vsekh potomkov
<LinearLayout
    android:importantForAccessibility="noHideDescendants">
    <!-- Dekorativnyy konteyner -->
</LinearLayout>

// Compose
Divider(
    modifier = Modifier.semantics {
        invisibleToUser()  // Analog importantForAccessibility="no"
    }
)
```

### Luchshie Praktiki

**1. Opisyvat naznachenie, a ne vneshnost:**

```kotlin
// Pravilno
contentDescription = "Otpravit soobshchenie"
contentDescription = "Zakryt dialog"
contentDescription = "Udalit element"

// Nepravilno
contentDescription = "Sinyaya knopka"
contentDescription = "Ikonka krestik"
contentDescription = "Kartinka"
```

**2. Izbegat dublirovanie:**

```kotlin
// Nepravilno - TalkBack dobavit "knopka" avtomaticheski
Button(onClick = { }) {
    Text("Otpravit")
}
// Pri etom ne nuzhno: contentDescription = "Knopka Otpravit"

// Pravilno dlya IconButton bez teksta
IconButton(onClick = { onDelete() }) {
    Icon(
        Icons.Default.Delete,
        contentDescription = "Udalit"  // Nuzhno, tak kak net teksta
    )
}
```

**3. Korotkie opisaniya (3-5 slov):**

```kotlin
// Pravilno
contentDescription = "Nastraivanie uvedomleniy"

// Slishkom dlinno
contentDescription = "Nazhmite chtoby otkryt ekran nastroyki uvedomleniy gde mozhno upravlyat vsemi tipami uvedomleniy"
```

### Tipichnye Oshibki

```kotlin
// 1. Otsutstvie opisaniya u znachimoy ikonki
IconButton(onClick = { }) {
    Icon(Icons.Default.Settings, contentDescription = null)  // TalkBack: nichego
}

// 2. Opisanie "Image" ili "Icon"
Image(
    painter = painterResource(R.drawable.product),
    contentDescription = "Image"  // Bespolezno
)

// 3. Dublirovanie vidimogo teksta
Row {
    Icon(Icons.Default.Star, contentDescription = "Star icon")
    Text("Favorites")
}
// TalkBack: "Star icon Favorites" - izbytochno

// Pravilno
Row(modifier = Modifier.semantics(mergeDescendants = true) { }) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Favorites")
}
// TalkBack: "Favorites"
```

---

## Answer (EN)

**`contentDescription`** - textual description of an element for accessibility services (TalkBack), **`importantForAccessibility`** - determines whether an element should be visible to accessibility services.

### When to Use contentDescription

**1. Unlabeled icons (View system)**

```kotlin
// Icon without text - needs description
<ImageButton
    android:id="@+id/delete_button"
    android:src="@drawable/ic_delete"
    android:contentDescription="@string/delete_item" />

// Icon with adjacent text - no description needed
<ImageView
    android:src="@drawable/ic_star"
    android:contentDescription="@null"
    android:importantForAccessibility="no" />
<TextView android:text="Favorites" />
```

**2. Compose**

```kotlin
// Meaningful image
Image(
    painter = painterResource(R.drawable.profile),
    contentDescription = "User profile photo"  // Describes purpose
)

// Decorative element
Image(
    painter = painterResource(R.drawable.background_pattern),
    contentDescription = null  // null = ignored by TalkBack
)

// Icon with text - icon is decorative
Row(
    modifier = Modifier
        .clickable { }
        .semantics(mergeDescendants = true) { }
) {
    Icon(
        Icons.Default.Favorite,
        contentDescription = null  // Adjacent text describes it
    )
    Text("Favorites")  // TalkBack: "Favorites, button"
}
```

### importantForAccessibility

**Values:**

| Value | Description | Example |
|-------|-------------|---------|
| `auto` (default) | System decides | Most elements |
| `yes` | Always visible | Custom interactive elements |
| `no` | Ignored | Decorative elements |
| `noHideDescendants` | Ignored with all descendants | Container of decorative content |

```kotlin
// View system
<ImageView
    android:importantForAccessibility="no"
    android:src="@drawable/decorative_divider" />

// Hide container and all children
<LinearLayout
    android:importantForAccessibility="noHideDescendants">
    <!-- Decorative container -->
</LinearLayout>

// Compose
Divider(
    modifier = Modifier.semantics {
        invisibleToUser()  // Equivalent to importantForAccessibility="no"
    }
)
```

### Best Practices

**1. Describe purpose, not appearance:**

```kotlin
// Correct
contentDescription = "Send message"
contentDescription = "Close dialog"
contentDescription = "Delete item"

// Wrong
contentDescription = "Blue button"
contentDescription = "X icon"
contentDescription = "Picture"
```

**2. Avoid duplication:**

```kotlin
// Wrong - TalkBack adds "button" automatically
Button(onClick = { }) {
    Text("Submit")
}
// Don't add: contentDescription = "Submit button"

// Correct for IconButton without text
IconButton(onClick = { onDelete() }) {
    Icon(
        Icons.Default.Delete,
        contentDescription = "Delete"  // Needed since no text
    )
}
```

**3. Keep descriptions short (3-5 words):**

```kotlin
// Correct
contentDescription = "Notification settings"

// Too long
contentDescription = "Click to open the notification settings screen where you can manage all notification types"
```

### Common Mistakes

```kotlin
// 1. Missing description for meaningful icon
IconButton(onClick = { }) {
    Icon(Icons.Default.Settings, contentDescription = null)  // TalkBack: nothing
}

// 2. Generic "Image" or "Icon" description
Image(
    painter = painterResource(R.drawable.product),
    contentDescription = "Image"  // Useless
)

// 3. Duplicating visible text
Row {
    Icon(Icons.Default.Star, contentDescription = "Star icon")
    Text("Favorites")
}
// TalkBack: "Star icon Favorites" - redundant

// Correct
Row(modifier = Modifier.semantics(mergeDescendants = true) { }) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Favorites")
}
// TalkBack: "Favorites"
```

---

## Dopolnitelnye Voprosy (RU)

- Kak opredelit, nuzhno li opisanie dlya elementa?
- Kogda ispolzovat `noHideDescendants` vmesto `no`?
- Kak lokalizovat contentDescription?
- V chem raznitsa mezhdu `contentDescription` i `stateDescription`?
- Kak testirovat pravilnost opisaniy?

## Follow-ups (EN)

- How to determine if an element needs a description?
- When to use `noHideDescendants` vs `no`?
- How to localize contentDescription?
- What's the difference between `contentDescription` and `stateDescription`?
- How to test description correctness?

## Ssylki (RU)

- [[c-accessibility]] - Osnovy dostupnosti
- https://developer.android.com/guide/topics/ui/accessibility/apps
- https://developer.android.com/jetpack/compose/accessibility

## References (EN)

- [[c-accessibility]] - Accessibility basics
- https://developer.android.com/guide/topics/ui/accessibility/apps
- https://developer.android.com/jetpack/compose/accessibility

## Related Questions

### Prerequisites (Easier)
- [[c-accessibility]] - Accessibility concepts

### Related (Same Level)
- [[q-accessibility-compose--android--medium]] - Accessibility in Compose
- [[q-accessibility-talkback--android--medium]] - TalkBack integration

### Advanced (Harder)
- [[q-custom-view-accessibility--android--medium]] - Custom view accessibility
- [[q-accessibility-services--accessibility--hard]] - Accessibility services
