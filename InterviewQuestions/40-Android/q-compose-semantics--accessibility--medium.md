---
id: android-acc-004
title: Semantics in Jetpack Compose / Semantika v Jetpack Compose
aliases:
- Compose Semantics
- Modifier.semantics
- Semantika Compose
topic: android
subtopics:
- accessibility
- ui-compose
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-jetpack-compose
- q-content-descriptions--accessibility--medium
- q-talkback-support--accessibility--medium
- q-testing-compose-ui--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/accessibility
- android/ui-compose
- difficulty/medium
- accessibility
- semantics
- compose
anki_cards:
- slug: android-acc-004-0-en
  language: en
- slug: android-acc-004-0-ru
  language: ru
---
# Vopros (RU)
> Chto takoe Semantics v Jetpack Compose i kak ispol'zovat' Modifier.semantics dlya dostupnosti?

# Question (EN)
> What is Semantics in Jetpack Compose and how do you use Modifier.semantics for accessibility?

---

## Otvet (RU)

**Semantics** v Compose - sistema opisaniya znacheniya UI-elementov dlya sluzhb dostupnosti (TalkBack), avtomatizatsii testov i instrumentov (Accessibility Scanner). Semantiki opisyvayut ne vneshnij vid, a smysl i povedenie elementov.

### Semanticheskoe derevo

```
Compose UI Tree          Semantics Tree
     |                        |
  Column               [Merged Node]
   /   \                     |
 Icon  Text     ->     "John Smith, 5 messages"
```

Semanticheskoe derevo - uproschennoye predstavlenie UI dlya programm chteniya ekrana.

### Bazovoe ispol'zovanie Modifier.semantics

```kotlin
// Dobavlenie contentDescription
Image(
    painter = painterResource(R.drawable.logo),
    contentDescription = null, // Vizualnoe opisanie
    modifier = Modifier.semantics {
        contentDescription = "Logotip kompanii ABC"
    }
)

// Opisanie sostoyaniya
Switch(
    checked = isEnabled,
    onCheckedChange = { /* ... */ },
    modifier = Modifier.semantics {
        stateDescription = if (isEnabled) "Vklyucheno" else "Vyklyucheno"
    }
)

// Ukazanie roli elementa
Box(
    modifier = Modifier
        .clickable { onItemClick() }
        .semantics {
            role = Role.Button
        }
) {
    Text("Nazhmi menya")
}
```

### Ob"edinenie semantik (mergeDescendants)

```kotlin
// Bez ob"edineniya - TalkBack chitat kazhdyj element otdel'no
Row {
    Icon(Icons.Default.Person, contentDescription = "Pol'zovatel'")
    Column {
        Text("Ivan Petrov")           // Otdel'nyj fokus
        Text("5 novykh soobschenij")  // Otdel'nyj fokus
    }
}

// S ob"edineniem - chitat kak edinoe tseloe
Row(
    modifier = Modifier.semantics(mergeDescendants = true) { }
) {
    Icon(Icons.Default.Person, contentDescription = null)
    Column {
        Text("Ivan Petrov")
        Text("5 novykh soobschenij")
    }
}
// TalkBack skazhet: "Ivan Petrov, 5 novykh soobschenij"
```

### clearAndSetSemantics

```kotlin
// Polnaya zamena semantik potomkov
Row(
    modifier = Modifier
        .clickable { onProfileClick() }
        .clearAndSetSemantics {
            contentDescription = "Profil' Ivana Petrova, 5 neprochinannykh soobschenij. Nazhmi dlya otkrytiya"
            role = Role.Button
        }
) {
    Icon(Icons.Default.Person, contentDescription = null)
    Column {
        Text("Ivan Petrov")
        Text("5 novykh soobschenij")
    }
}
```

### Osnovnye svojstva semantik

```kotlin
Modifier.semantics {
    // Opisaniya
    contentDescription = "Opisanie elementa"
    stateDescription = "Tekuschee sostoyanie"
    text = AnnotatedString("Tekstovoe soderzhimoe")

    // Roli
    role = Role.Button      // Button, Checkbox, Switch, RadioButton,
                            // Tab, Image, DropdownList, etc.

    // Navigatsiya
    heading()                // Otmechaet kak zagolovok (dlya navigatsii)
    traversalIndex = 1f      // Poryadok navigatsii

    // Dejstviya
    onClick(label = "Aktivirovat'") { true }
    onLongClick(label = "Pokazat' menyu") { true }

    // Dinamicheskie obnovleniya
    liveRegion = LiveRegionMode.Polite  // Polite ili Assertive

    // Testirovanie
    testTag = "profile_card"

    // Skrytie
    invisibleToUser()        // Polnoe skrytie ot accessibility services
}
```

### Kastomnyye dejstviya

```kotlin
// Dobavlenie kastomnyh dejstvij dlya TalkBack menyu
Card(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction(label = "Udalit'") {
                onDelete()
                true
            },
            CustomAccessibilityAction(label = "Peredat'") {
                onShare()
                true
            },
            CustomAccessibilityAction(label = "V izbrannoe") {
                onFavorite()
                true
            }
        )
    }
) {
    // Soderzhimoe kartochki
    ListItem(
        headlineContent = { Text("Dokument.pdf") },
        supportingContent = { Text("2.5 MB") }
    )
}
```

### Rabota s progress i range

```kotlin
// Progress bar
LinearProgressIndicator(
    progress = { 0.7f },
    modifier = Modifier.semantics {
        progressBarRangeInfo = ProgressBarRangeInfo(
            current = 0.7f,
            range = 0f..1f
        )
    }
)

// Slider
Slider(
    value = volume,
    onValueChange = { volume = it },
    valueRange = 0f..100f,
    modifier = Modifier.semantics {
        stateDescription = "Gromkost': ${volume.toInt()}%"
    }
)
```

### Uslovnoe izmenenie semantik

```kotlin
@Composable
fun ToggleButton(
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.semantics {
            // Dinamicheskoe sostoyanie
            stateDescription = if (isSelected) "Vybrano" else "Ne vybrano"

            // Dinamicheskaya rol'
            role = Role.Checkbox

            // Opisanie dejstviya
            onClick(label = if (isSelected) "Otmenit' vybor" else "Vybrat'") {
                onClick()
                true
            }
        }
    ) {
        Text(if (isSelected) "Vybrano" else "Vybrat'")
    }
}
```

### Semantiki dlya testirovaniya

```kotlin
// Dobavlenie testTag
Text(
    text = "Privet",
    modifier = Modifier.testTag("greeting_text")
)

// Ispol'zovanie v testah
composeTestRule
    .onNodeWithTag("greeting_text")
    .assertTextEquals("Privet")

// Proverka semantik
composeTestRule
    .onNode(hasContentDescription("Logotip"))
    .assertExists()

composeTestRule
    .onNode(hasStateDescription("Vklyucheno"))
    .assertExists()

// Proverka roli
composeTestRule
    .onNode(
        hasContentDescription("Otpravit'") and
        hasRole(Role.Button)
    )
    .performClick()
```

### Luchshie praktiki

| Praktika | Primer |
|----------|--------|
| Ob"edinyajte svyazannye elementy | `mergeDescendants = true` dlya list item |
| Ispol'zujte pravilnye roli | `Role.Button`, `Role.Checkbox` i td |
| Dobavlyajte stateDescription | Dlya toggle, checkbox, switch |
| Ispol'zujte heading() | Dlya zagolovkov sekcij |
| Skryvajte dekorativnye | `contentDescription = null` |
| Predostavlyajte custom actions | Dlya elementov so slozhnym povedeniem |

### Chastye oshibki

| Oshibka | Reshenie |
|---------|----------|
| Lishnie fokusiruemye elementy | Ispol'zujte mergeDescendants |
| Otsutstvie opisaniya sostoyaniya | Dobav'te stateDescription |
| Nepravil'nyj poryadok chteniya | Ispol'zujte traversalIndex |
| Dekorativnye elementy chitayutsya | Ustanovite contentDescription = null |
| Otsutstvie roli dlya custom controls | Dobav'te role v semantics |

---

## Answer (EN)

**Semantics** in Compose is a system for describing the meaning of UI elements for accessibility services (TalkBack), test automation, and tools (Accessibility Scanner). Semantics describe not appearance but meaning and behavior.

### Semantics Tree

```
Compose UI Tree          Semantics Tree
     |                        |
  Column               [Merged Node]
   /   \                     |
 Icon  Text     ->     "John Smith, 5 messages"
```

The semantics tree is a simplified UI representation for screen readers.

### Basic Modifier.semantics Usage

```kotlin
// Adding contentDescription
Image(
    painter = painterResource(R.drawable.logo),
    contentDescription = null, // Visual description
    modifier = Modifier.semantics {
        contentDescription = "ABC Company logo"
    }
)

// State description
Switch(
    checked = isEnabled,
    onCheckedChange = { /* ... */ },
    modifier = Modifier.semantics {
        stateDescription = if (isEnabled) "On" else "Off"
    }
)

// Specifying element role
Box(
    modifier = Modifier
        .clickable { onItemClick() }
        .semantics {
            role = Role.Button
        }
) {
    Text("Click me")
}
```

### Merging Semantics (mergeDescendants)

```kotlin
// Without merging - TalkBack reads each element separately
Row {
    Icon(Icons.Default.Person, contentDescription = "User")
    Column {
        Text("John Smith")           // Separate focus
        Text("5 new messages")       // Separate focus
    }
}

// With merging - reads as single unit
Row(
    modifier = Modifier.semantics(mergeDescendants = true) { }
) {
    Icon(Icons.Default.Person, contentDescription = null)
    Column {
        Text("John Smith")
        Text("5 new messages")
    }
}
// TalkBack says: "John Smith, 5 new messages"
```

### clearAndSetSemantics

```kotlin
// Complete replacement of descendant semantics
Row(
    modifier = Modifier
        .clickable { onProfileClick() }
        .clearAndSetSemantics {
            contentDescription = "John Smith's profile, 5 unread messages. Tap to open"
            role = Role.Button
        }
) {
    Icon(Icons.Default.Person, contentDescription = null)
    Column {
        Text("John Smith")
        Text("5 new messages")
    }
}
```

### Core Semantics Properties

```kotlin
Modifier.semantics {
    // Descriptions
    contentDescription = "Element description"
    stateDescription = "Current state"
    text = AnnotatedString("Text content")

    // Roles
    role = Role.Button      // Button, Checkbox, Switch, RadioButton,
                            // Tab, Image, DropdownList, etc.

    // Navigation
    heading()                // Marks as heading (for navigation)
    traversalIndex = 1f      // Navigation order

    // Actions
    onClick(label = "Activate") { true }
    onLongClick(label = "Show menu") { true }

    // Dynamic updates
    liveRegion = LiveRegionMode.Polite  // Polite or Assertive

    // Testing
    testTag = "profile_card"

    // Hiding
    invisibleToUser()        // Completely hidden from accessibility services
}
```

### Custom Actions

```kotlin
// Adding custom actions for TalkBack menu
Card(
    modifier = Modifier.semantics {
        customActions = listOf(
            CustomAccessibilityAction(label = "Delete") {
                onDelete()
                true
            },
            CustomAccessibilityAction(label = "Share") {
                onShare()
                true
            },
            CustomAccessibilityAction(label = "Favorite") {
                onFavorite()
                true
            }
        )
    }
) {
    // Card content
    ListItem(
        headlineContent = { Text("Document.pdf") },
        supportingContent = { Text("2.5 MB") }
    )
}
```

### Working with Progress and Range

```kotlin
// Progress bar
LinearProgressIndicator(
    progress = { 0.7f },
    modifier = Modifier.semantics {
        progressBarRangeInfo = ProgressBarRangeInfo(
            current = 0.7f,
            range = 0f..1f
        )
    }
)

// Slider
Slider(
    value = volume,
    onValueChange = { volume = it },
    valueRange = 0f..100f,
    modifier = Modifier.semantics {
        stateDescription = "Volume: ${volume.toInt()}%"
    }
)
```

### Conditional Semantics Changes

```kotlin
@Composable
fun ToggleButton(
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.semantics {
            // Dynamic state
            stateDescription = if (isSelected) "Selected" else "Not selected"

            // Dynamic role
            role = Role.Checkbox

            // Action description
            onClick(label = if (isSelected) "Deselect" else "Select") {
                onClick()
                true
            }
        }
    ) {
        Text(if (isSelected) "Selected" else "Select")
    }
}
```

### Semantics for Testing

```kotlin
// Adding testTag
Text(
    text = "Hello",
    modifier = Modifier.testTag("greeting_text")
)

// Using in tests
composeTestRule
    .onNodeWithTag("greeting_text")
    .assertTextEquals("Hello")

// Checking semantics
composeTestRule
    .onNode(hasContentDescription("Logo"))
    .assertExists()

composeTestRule
    .onNode(hasStateDescription("On"))
    .assertExists()

// Checking role
composeTestRule
    .onNode(
        hasContentDescription("Send") and
        hasRole(Role.Button)
    )
    .performClick()
```

### Best Practices

| Practice | Example |
|----------|---------|
| Merge related elements | `mergeDescendants = true` for list items |
| Use correct roles | `Role.Button`, `Role.Checkbox`, etc. |
| Add stateDescription | For toggles, checkboxes, switches |
| Use heading() | For section headings |
| Hide decorative elements | `contentDescription = null` |
| Provide custom actions | For elements with complex behavior |

### Common Mistakes

| Mistake | Solution |
|---------|----------|
| Too many focusable elements | Use mergeDescendants |
| Missing state description | Add stateDescription |
| Incorrect reading order | Use traversalIndex |
| Decorative elements being read | Set contentDescription = null |
| Missing role for custom controls | Add role in semantics |

---

## Follow-ups

- How does the semantics tree differ from the UI tree?
- How to debug semantics issues in Compose?
- What is the difference between mergeDescendants and clearAndSetSemantics?
- How to handle semantics for animated content?

## References

- Compose Accessibility: https://developer.android.com/develop/ui/compose/accessibility
- Semantics in Compose: https://developer.android.com/develop/ui/compose/semantics
- Testing Semantics: https://developer.android.com/develop/ui/compose/testing

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals
- [[q-what-do-you-know-about-modifiers--android--medium]] - Understanding Modifiers

### Related
- [[q-content-descriptions--accessibility--medium]] - Content descriptions
- [[q-talkback-support--accessibility--medium]] - TalkBack support
- [[q-testing-compose-ui--android--medium]] - Compose UI testing
- [[q-accessibility-testing--accessibility--medium]] - Accessibility testing
