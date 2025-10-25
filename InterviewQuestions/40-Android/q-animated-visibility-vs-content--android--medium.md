---
id: 20251012-122777
title: AnimatedVisibility vs AnimatedContent vs Crossfade / AnimatedVisibility против
aliases:
- AnimatedVisibility vs AnimatedContent vs Crossfade
- AnimatedVisibility против AnimatedContent против Crossfade
topic: android
subtopics:
- ui-animation
- ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-testing-strategies--android--medium
- q-android-architectural-patterns--android--medium
- q-android-performance-measurement-tools--android--medium
created: 2025-10-13
updated: 2025-10-15
tags:
- android/ui-animation
- android/ui-compose
- difficulty/medium
---

# Вопрос (RU)
> Что такое AnimatedVisibility против?

---

# Question (EN)
> What is the difference between animatedvisibility vs animatedcontent vs crossfade?

## Answer (EN)
**Compose Animation APIs** provide three main approaches for content transitions: AnimatedVisibility, AnimatedContent, and Crossfade, each optimized for different use cases.

**Animation APIs Theory:**
Jetpack Compose offers specialized animation APIs for different scenarios. AnimatedVisibility handles show/hide transitions, AnimatedContent manages state-based content changes, and Crossfade provides simple fade transitions between content.

**1. AnimatedVisibility:**
Show/hide content with enter/exit animations for visibility toggles.

```kotlin
// Basic AnimatedVisibility
@Composable
fun AnimatedVisibilityExample() {
    var visible by remember { mutableStateOf(false) }

    Column {
        Button(onClick = { visible = !visible }) {
            Text(if (visible) "Hide" else "Show")
        }

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn() + slideInVertically(),
            exit = fadeOut() + slideOutVertically()
        ) {
            Text("Hello, I'm animated!")
        }
    }
}

// Expandable Card
@Composable
fun ExpandableCard() {
    var expanded by remember { mutableStateOf(false) }

    Card(modifier = Modifier.clickable { expanded = !expanded }) {
        Column {
            Text("Card Header")
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Text("Expanded content")
            }
        }
    }
}
```

**2. AnimatedContent:**
Animate between different content based on target state changes.

```kotlin
// State-based Content Animation
@Composable
fun AnimatedContentExample() {
    var count by remember { mutableStateOf(0) }

    AnimatedContent(
        targetState = count,
        transitionSpec = {
            if (targetState > initialState) {
                slideInVertically { it } + fadeIn() togetherWith
                    slideOutVertically { -it } + fadeOut()
            } else {
                slideInVertically { -it } + fadeIn() togetherWith
                    slideOutVertically { it } + fadeOut()
            }
        }
    ) { targetCount ->
        Text("Count: $targetCount")
    }
}

// Loading States
@Composable
fun LoadingStates() {
    var state by remember { mutableStateOf(LoadingState.Loading) }

    AnimatedContent(targetState = state) { currentState ->
        when (currentState) {
            LoadingState.Loading -> CircularProgressIndicator()
            LoadingState.Success -> Text("Success!")
            LoadingState.Error -> Text("Error occurred")
        }
    }
}
```

**3. Crossfade:**
Simple fade transition between different content states.

```kotlin
// Simple Crossfade
@Composable
fun CrossfadeExample() {
    var currentScreen by remember { mutableStateOf("Home") }

    Crossfade(targetState = currentScreen) { screen ->
        when (screen) {
            "Home" -> HomeScreen()
            "Profile" -> ProfileScreen()
            "Settings" -> SettingsScreen()
        }
    }
}
```

**API Comparison:**

| Feature | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| **Primary Use** | Show/hide content | State-based content | Simple switching |
| **Animations** | Enter/exit transitions | Custom transitions | Fade only |
| **Direction Control** | Yes | Yes | No |
| **Size Animation** | Yes | Yes | No |
| **API Complexity** | Medium | High | Low |
| **Flexibility** | High | Highest | Low |

**When to Use Each:**

**AnimatedVisibility:**
- Toggle visibility on/off
- Show/hide optional UI elements
- Expand/collapse sections
- Modal dialogs, tooltips

**AnimatedContent:**
- Switching between screens/views
- State changes (loading → success → error)
- Carousel/pager transitions
- Form wizard steps

**Crossfade:**
- Simple content switching
- Minimal animation needs
- Quick prototyping
- Basic state transitions

**Best Practices:**
- Choose based on use case requirements
- Consider performance implications
- Use appropriate animation specifications
- Account for content size changes
- Test on different screen sizes

## Follow-ups

- How do you handle performance with complex animations?
- What's the difference between animateEnterExit and AnimatedVisibility?
- How do you create custom transition specifications?
- When should you avoid animations in Compose?

## References

- c-animations
- [Compose Animation Guide](https://developer.android.com/jetpack/compose/animation)
- [Animation Best Practices](https://developer.android.com/jetpack/compose/animation/best-practices)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]