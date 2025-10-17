---
id: 20251012-1227108
title: "Semantics in Jetpack Compose"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, semantics, accessibility, testing]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/jetpack-compose, android/semantics, android/accessibility, android/testing, difficulty/medium]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/jetpack-compose, android/semantics, android/accessibility, android/testing, difficulty/medium]
---
# Question (EN)
> What are Semantics in Jetpack Compose? How are they used for accessibility and testing?
# Вопрос (RU)
> Что такое Semantics в Jetpack Compose? Как они используются для доступности и тестирования?

---

## Answer (EN)

**Semantics** describe the UI structure and meaning for accessibility services and testing frameworks.

### Basic Usage

```kotlin
@Composable
fun CustomButton(onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clickable(onClick = onClick)
            .semantics {
                contentDescription = "Submit button"
                role = Role.Button
            }
    ) {
        Text("Submit")
    }
}
```

### Accessibility Properties

```kotlin
@Composable
fun ProfileImage(imageUrl: String) {
    Image(
        painter = rememberImagePainter(imageUrl),
        contentDescription = "User profile picture",  // For screen readers
        modifier = Modifier
            .semantics {
                // Additional semantic properties
                role = Role.Image
                contentDescription = "Profile photo of John Doe"
            }
    )
}
```

### Testing with Semantics

```kotlin
@Test
fun testButton() {
    composeTestRule.setContent {
        Button(
            onClick = {},
            modifier = Modifier.testTag("submit_button")  // Test tag
        ) {
            Text("Submit")
        }
    }

    // Find by test tag
    composeTestRule
        .onNodeWithTag("submit_button")
        .assertIsEnabled()
        .performClick()

    // Find by text
    composeTestRule
        .onNodeWithText("Submit")
        .assertExists()

    // Find by content description
    composeTestRule
        .onNodeWithContentDescription("Submit button")
        .assertIsDisplayed()
}
```

### Custom Semantics

```kotlin
@Composable
fun ProgressBar(progress: Float) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(8.dp)
            .semantics {
                // Custom semantic property
                progressBarRangeInfo = ProgressBarRangeInfo(
                    current = progress,
                    range = 0f..1f
                )
                stateDescription = "${(progress * 100).toInt()}% complete"
            }
    ) {
        // Progress bar UI
    }
}
```

### Merge Semantics

```kotlin
// BAD - Each text has separate semantics
@Composable
fun UserInfo(user: User) {
    Row {
        Text(user.firstName)
        Text(user.lastName)
    }
    // Screen reader announces separately: "John" "Doe"
}

// GOOD - Merged semantics
@Composable
fun UserInfo(user: User) {
    Row(
        modifier = Modifier.semantics(mergeDescendants = true) {
            contentDescription = "${user.firstName} ${user.lastName}"
        }
    ) {
        Text(user.firstName)
        Text(user.lastName)
    }
    // Screen reader announces once: "John Doe"
}
```

**English Summary**: Semantics describe UI for accessibility and testing. Properties: `contentDescription` (screen readers), `role` (Button/Image/etc), `stateDescription` (current state). Use `testTag` for testing, `mergeDescendants` for combining child semantics. Essential for accessibility and UI testing.

## Ответ (RU)

**Semantics** описывают структуру и смысл UI для служб доступности и фреймворков тестирования.

### Базовое использование

```kotlin
@Composable
fun CustomButton(onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clickable(onClick = onClick)
            .semantics {
                contentDescription = "Submit button"
                role = Role.Button
            }
    ) {
        Text("Submit")
    }
}
```

### Свойства доступности

```kotlin
@Composable
fun ProfileImage(imageUrl: String) {
    Image(
        painter = rememberImagePainter(imageUrl),
        contentDescription = "User profile picture",  // Для screen readers
        modifier = Modifier.semantics {
            role = Role.Image
        }
    )
}
```

### Тестирование с Semantics

```kotlin
@Test
fun testButton() {
    composeTestRule
        .onNodeWithTag("submit_button")
        .assertIsEnabled()
        .performClick()

    composeTestRule
        .onNodeWithText("Submit")
        .assertExists()
}
```

**Краткое содержание**: Semantics описывают UI для доступности и тестирования. Свойства: `contentDescription` (screen readers), `role` (Button/Image/etc), `stateDescription` (текущее состояние). Используйте `testTag` для тестирования, `mergeDescendants` для объединения семантики детей. Важно для доступности и UI тестирования.

---

## References
- [Compose Semantics](https://developer.android.com/jetpack/compose/semantics)

## Related Questions

### Related (Medium)
- [[q-compose-testing--android--medium]] - Jetpack Compose
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-compose-modifier-system--android--medium]] - Jetpack Compose
- [[q-jetpack-compose-basics--android--medium]] - Jetpack Compose

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

