---
id: android-acc-002
title: TalkBack Support / Poderzhka TalkBack
aliases: [TalkBack Support, Screen Reader, Poderzhka TalkBack, Programma chteniya ekrana]
topic: android
subtopics: [accessibility, ui-views, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-content-descriptions--accessibility--medium, q-compose-semantics--accessibility--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/accessibility, android/ui-views, android/ui-compose, difficulty/medium, accessibility, talkback]

---
# Vopros (RU)
> Chto takoe TalkBack i kak obespechit' podderzhku programmy chteniya ekrana v Android-prilozhenii?

# Question (EN)
> What is TalkBack and how do you ensure screen reader support in an Android application?

---

## Otvet (RU)

**TalkBack** - vstroennaya programma chteniya ekrana Android, ozvochivaet UI-elementy i pozvolyaet upravlyat' prilozheniem s pomoshch'yu zhestov. Eto osnovnoj instrument dostupnosti dlya pol'zovatelej s narusheniami zrenia.

### Kak rabotaet TalkBack

1. **Navigatsiya** - provodyat pal'tsem po ekranu, TalkBack ozvuchivaet elementy
2. **Aktivatsiya** - dvojnoj tap dlya nazhatiia na element v fokuse
3. **Prokrutka** - zhesty dvumya pal'tsami
4. **Kontekstnoye menyu** - tap tremya pal'tsami

### Osnovnye printsipy podderzhki TalkBack

```kotlin
// 1. Vse interaktivnye elementy dolzhny imet' opisanie
IconButton(
    onClick = { /* ... */ }
) {
    Icon(
        imageVector = Icons.Default.Share,
        contentDescription = stringResource(R.string.share) // Obyazatel'no!
    )
}

// 2. Logicheskaya gruppirovka elementov
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {
        // Ozvuchitsya kak edinoe tseloe
    }
) {
    Icon(Icons.Default.Email, contentDescription = null)
    Text("user@example.com")
}

// 3. Pravilnye roli i dejstviya
Box(
    modifier = Modifier
        .clickable { /* ... */ }
        .semantics {
            role = Role.Button
            onClick(label = "Otkryt' nastrojki") { true }
        }
)
```

### Poryadok fokusa i navigatsii

```kotlin
// Upravlenie poryadkom fokusa v Compose
Column {
    // Elementy chitayutsya sverkhu vniz
    Text("Zagolovok", modifier = Modifier.semantics { heading() })
    Text("Opisanie")

    // Prinuditel'noe izmenenie poryadka
    Row {
        Text(
            "Vtoroy",
            modifier = Modifier.semantics { traversalIndex = 2f }
        )
        Text(
            "Pervyy",
            modifier = Modifier.semantics { traversalIndex = 1f }
        )
    }
}

// V Views - XML
<LinearLayout
    android:accessibilityTraversalBefore="@id/nextElement"
    android:accessibilityTraversalAfter="@id/previousElement">
```

### Ob"yavlenie ob izmeneniyakh (Live Regions)

```kotlin
// Compose - ob"yavlenie dinamicheskikh izmenenij
var statusMessage by remember { mutableStateOf("") }

Text(
    text = statusMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // ili Assertive
    }
)

// Pri izmenenii statusMessage TalkBack ozvuchit novoe znachenie

// Views
textView.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
```

| Rezhim | Kogda ispol'zovat' |
|--------|-------------------|
| Polite | Nespeshnye obnovleniya (status zagruzki) |
| Assertive | Vazhnye soobscheniya (oshibki) |

### Kastomnyj accessibility-dejstviya

```kotlin
// Dobavlenie kastomnyh dejstvij
Card(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Udalit'") {
                deleteItem()
                true
            },
            CustomAccessibilityAction("Redaktirovat'") {
                editItem()
                true
            }
        )
    }
) {
    // Soderzhimoe kartochki
}

// Views
ViewCompat.addAccessibilityAction(
    view,
    "Udalit'"
) { _, _ ->
    deleteItem()
    true
}
```

### Skrytie elementov ot TalkBack

```kotlin
// Compose - dekorativnye elementy
Image(
    painter = painterResource(R.drawable.decorative),
    contentDescription = null, // Ne ozvuchitsya
    modifier = Modifier.semantics {
        invisibleToUser() // Polnoe skrytie
    }
)

// Skrytie konteinera, no ne detej
Box(
    modifier = Modifier.clearAndSetSemantics { }
) {
    // Deti budut dostupny
}

// Views
android:importantForAccessibility="no"
// ili
ViewCompat.setImportantForAccessibility(view, ViewCompat.IMPORTANT_FOR_ACCESSIBILITY_NO)
```

### Testirovanie s TalkBack

```kotlin
// 1. Ruchnoe testirovanie
// - Vklyuchit' TalkBack: Nastrojki > Spetsdostup > TalkBack
// - Projti vse ekrany prilozheniia
// - Proverit' poryadok chteniya i opisaniya

// 2. Accessibility Scanner (Google)
// - Avtomaticheskij analiz UI
// - Predlozheniya po uluchsheniyu

// 3. Espresso accessibility checks
@Test
fun checkAccessibility() {
    AccessibilityChecks.enable()
    onView(withId(R.id.myButton)).perform(click())
}

// 4. Compose accessibility checks
composeTestRule
    .onNodeWithContentDescription("Otpravit'")
    .assertIsDisplayed()
    .assertHasClickAction()
```

### Chek-list podderzhki TalkBack

| Trebovanie | Proverka |
|------------|----------|
| contentDescription dlya ikonok | Vse interaktivnye ikonki imeyut opisanie |
| Logicheskaya gruppirovka | Svyazannye elementy ob"edineny |
| Poryadok fokusa | Sootvetstvuet vizualnomy poryadku |
| Dinamicheskij kontent | Live regions dlya obnovlenij |
| Touch targets | Minimum 48dp |
| Kastomnye kontroly | Pravilnye roli i dejstviya |
| Dekorativnye elementy | Skryty ot TalkBack |

### Chastye oshibki

| Oshibka | Reshenie |
|---------|----------|
| Otsutstvie contentDescription | Dobav'te opisanie dlya kazhdogo interaktivnogo elementa |
| "Image" ili "Button" v opisanii | Opisyvajte dejstvie, ne tip elementa |
| Nelogichnyj poryadok chteniya | Ispol'zujte semantics { traversalIndex } |
| Fokus uhodit za ekran | Ogranich'te navigatsiyu modal'nym oknom |
| Dialog ne ob"yavlyaetsya | Ispol'zujte AlertDialog s pravilnymi semantikami |

---

## Answer (EN)

**TalkBack** is Android's built-in screen reader that announces UI elements and allows controlling the app through gestures. It is the primary accessibility tool for users with visual impairments.

### How TalkBack Works

1. **Navigation** - swipe to explore, TalkBack announces elements
2. **Activation** - double-tap to activate focused element
3. **Scrolling** - two-finger gestures
4. **Context menu** - three-finger tap

### Core Principles for TalkBack Support

```kotlin
// 1. All interactive elements must have descriptions
IconButton(
    onClick = { /* ... */ }
) {
    Icon(
        imageVector = Icons.Default.Share,
        contentDescription = stringResource(R.string.share) // Required!
    )
}

// 2. Logical grouping of elements
Row(
    modifier = Modifier.semantics(mergeDescendants = true) {
        // Will be announced as a single unit
    }
) {
    Icon(Icons.Default.Email, contentDescription = null)
    Text("user@example.com")
}

// 3. Proper roles and actions
Box(
    modifier = Modifier
        .clickable { /* ... */ }
        .semantics {
            role = Role.Button
            onClick(label = "Open settings") { true }
        }
)
```

### Focus Order and Navigation

```kotlin
// Managing focus order in Compose
Column {
    // Elements read top to bottom
    Text("Title", modifier = Modifier.semantics { heading() })
    Text("Description")

    // Force reorder
    Row {
        Text(
            "Second",
            modifier = Modifier.semantics { traversalIndex = 2f }
        )
        Text(
            "First",
            modifier = Modifier.semantics { traversalIndex = 1f }
        )
    }
}

// In Views - XML
<LinearLayout
    android:accessibilityTraversalBefore="@id/nextElement"
    android:accessibilityTraversalAfter="@id/previousElement">
```

### Announcing Changes (Live Regions)

```kotlin
// Compose - announcing dynamic changes
var statusMessage by remember { mutableStateOf("") }

Text(
    text = statusMessage,
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite // or Assertive
    }
)

// When statusMessage changes, TalkBack announces the new value

// Views
textView.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
```

| Mode | When to Use |
|------|-------------|
| Polite | Non-urgent updates (loading status) |
| Assertive | Important messages (errors) |

### Custom Accessibility Actions

```kotlin
// Adding custom actions
Card(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction("Delete") {
                deleteItem()
                true
            },
            CustomAccessibilityAction("Edit") {
                editItem()
                true
            }
        )
    }
) {
    // Card content
}

// Views
ViewCompat.addAccessibilityAction(
    view,
    "Delete"
) { _, _ ->
    deleteItem()
    true
}
```

### Hiding Elements from TalkBack

```kotlin
// Compose - decorative elements
Image(
    painter = painterResource(R.drawable.decorative),
    contentDescription = null, // Won't be announced
    modifier = Modifier.semantics {
        invisibleToUser() // Completely hidden
    }
)

// Hide container but not children
Box(
    modifier = Modifier.clearAndSetSemantics { }
) {
    // Children remain accessible
}

// Views
android:importantForAccessibility="no"
// or
ViewCompat.setImportantForAccessibility(view, ViewCompat.IMPORTANT_FOR_ACCESSIBILITY_NO)
```

### Testing with TalkBack

```kotlin
// 1. Manual testing
// - Enable TalkBack: Settings > Accessibility > TalkBack
// - Navigate through all app screens
// - Verify reading order and descriptions

// 2. Accessibility Scanner (Google)
// - Automatic UI analysis
// - Improvement suggestions

// 3. Espresso accessibility checks
@Test
fun checkAccessibility() {
    AccessibilityChecks.enable()
    onView(withId(R.id.myButton)).perform(click())
}

// 4. Compose accessibility checks
composeTestRule
    .onNodeWithContentDescription("Send")
    .assertIsDisplayed()
    .assertHasClickAction()
```

### TalkBack Support Checklist

| Requirement | Verification |
|-------------|--------------|
| contentDescription for icons | All interactive icons have descriptions |
| Logical grouping | Related elements merged |
| Focus order | Matches visual order |
| Dynamic content | Live regions for updates |
| Touch targets | Minimum 48dp |
| Custom controls | Proper roles and actions |
| Decorative elements | Hidden from TalkBack |

### Common Mistakes

| Mistake | Solution |
|---------|----------|
| Missing contentDescription | Add description for every interactive element |
| "Image" or "Button" in description | Describe the action, not element type |
| Illogical reading order | Use semantics { traversalIndex } |
| Focus escapes screen | Constrain navigation to modal |
| Dialog not announced | Use AlertDialog with proper semantics |

---

## Follow-ups

- How to handle TalkBack with bottom sheets and dialogs?
- What gestures does TalkBack intercept and how to handle them?
- How to implement accessibility for drag-and-drop interactions?
- How to test TalkBack support in automated tests?

## References

- TalkBack Guide: https://support.google.com/accessibility/android/answer/6283677
- Android Accessibility: https://developer.android.com/guide/topics/ui/accessibility
- Testing Accessibility: https://developer.android.com/guide/topics/ui/accessibility/testing

## Related Questions

### Prerequisites
- [[q-content-descriptions--accessibility--medium]] - Content descriptions
- [[q-view-fundamentals--android--easy]] - View basics

### Related
- [[q-compose-semantics--accessibility--medium]] - Semantics in Compose
- [[q-accessibility-testing--accessibility--medium]] - Accessibility testing
- [[q-touch-target-size--accessibility--easy]] - Touch target size
