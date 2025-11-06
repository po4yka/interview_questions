---
id: android-127
title: "How Dialog Differs From Other Navigation / Чем Dialog отличается от другой навигации"
aliases: ["How Dialog Differs From Other Navigation", "Чем Dialog отличается от другой навигации"]
topic: android
subtopics: [ui-compose, ui-navigation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-main-thread-android--android--medium, q-what-is-layout-performance-measured-in--android--medium]
created: 2025-10-15
updated: 2025-01-27
tags: [android, android/ui-compose, android/ui-navigation, dialog, difficulty/medium, navigation]
sources: []
---

# Вопрос (RU)

> Чем dialog отличается от остальной навигации?

# Question (EN)

> How does dialog differ from other navigation?

---

## Ответ (RU)

Dialog - это UI-компонент, который отображается поверх текущего экрана и фундаментально отличается от стандартной навигации:

**Ключевые отличия:**

1. **Overlay vs Replacement** - Dialog отображается поверх экрана, обычная навигация заменяет экран
2. **Back Stack** - Dialog не добавляется в back stack, навигация добавляет записи
3. **State Preservation** - Под dialog сохраняется состояние экрана, при навигации может теряться
4. **Scope** - Dialog для кратких взаимодействий (подтверждения, выбор), навигация для полноценных экранов
5. **Lifecycle** - Dialog имеет независимый lifecycle, привязанный к родительскому экрану

**Использование:** подтверждения действий, простые формы, выбор опций (date/time picker), индикаторы прогресса.

### Jetpack Compose

```kotlin
@Composable
fun MyScreen() {
    var showDialog by remember { mutableStateOf(false) } // ✅ State hoisting

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false }, // ✅ Handle dismissal
            title = { Text("Confirm") },
            text = { Text("Delete item?") },
            confirmButton = {
                TextButton(onClick = {
                    // ✅ Handle action then dismiss
                    showDialog = false
                }) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

// ❌ Bad: Dialog state not managed properly
@Composable
fun BadExample() {
    AlertDialog(
        onDismissRequest = { /* no state update */ }, // ❌ Dialog won't close
        // ...
    )
}
```

### Traditional Android (Views)

```kotlin
// ✅ Good: DialogFragment with lifecycle awareness
class ConfirmDialogFragment : DialogFragment() {
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        return AlertDialog.Builder(requireContext())
            .setMessage("Confirm action?")
            .setPositiveButton("OK") { _, _ -> /* action */ }
            .setNegativeButton("Cancel", null)
            .create()
    }
}

// ❌ Bad: Direct AlertDialog (loses state on config changes)
AlertDialog.Builder(context)
    .setMessage("Confirm?")
    .show() // ❌ Lost on rotation
```

**Связь с [[c-compose-navigation]]:** Dialog не влияет на NavController, в отличие от обычной навигации между composables.

---

## Answer (EN)

A dialog is a UI component displayed on top of the current screen, fundamentally different from standard navigation:

**Key Differences:**

1. **Overlay vs Replacement** - Dialog appears on top, navigation replaces the screen
2. **Back Stack** - Dialog doesn't add to back stack, navigation does
3. **State Preservation** - Screen state preserved under dialog, may be lost with navigation
4. **Scope** - Dialog for brief interactions (confirmations, selections), navigation for full screens
5. **Lifecycle** - Dialog has independent lifecycle tied to parent screen

**Use Cases:** Action confirmations, simple forms, option selection (date/time pickers), progress indicators.

### Jetpack Compose

```kotlin
@Composable
fun MyScreen() {
    var showDialog by remember { mutableStateOf(false) } // ✅ State hoisting

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false }, // ✅ Handle dismissal
            title = { Text("Confirm") },
            text = { Text("Delete item?") },
            confirmButton = {
                TextButton(onClick = {
                    // ✅ Handle action then dismiss
                    showDialog = false
                }) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

// ❌ Bad: Dialog state not managed properly
@Composable
fun BadExample() {
    AlertDialog(
        onDismissRequest = { /* no state update */ }, // ❌ Dialog won't close
        // ...
    )
}
```

### Traditional Android (Views)

```kotlin
// ✅ Good: DialogFragment with lifecycle awareness
class ConfirmDialogFragment : DialogFragment() {
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        return AlertDialog.Builder(requireContext())
            .setMessage("Confirm action?")
            .setPositiveButton("OK") { _, _ -> /* action */ }
            .setNegativeButton("Cancel", null)
            .create()
    }
}

// ❌ Bad: Direct AlertDialog (loses state on config changes)
AlertDialog.Builder(context)
    .setMessage("Confirm?")
    .show() // ❌ Lost on rotation
```

**Related to [[c-compose-navigation]]:** Dialog doesn't affect NavController, unlike standard navigation between composables.

---

## Follow-ups

- How does dialog state survive configuration changes in Compose vs Views?
- What happens to dialog when parent activity/composable is destroyed?
- How to implement nested navigation with dialogs in Navigation Component?
- What are the performance implications of showing dialogs frequently?

## References

- [[c-compose-navigation]] - Navigation in Jetpack Compose
- [[c-compose-state]] - State management in Compose
- [[c-lifecycle]] - Android lifecycle concepts

## Related Questions

### Prerequisites (Easier)

### Related (Medium)
- [[q-main-thread-android--android--medium]] - Main thread and UI operations
- [[q-what-is-layout-performance-measured-in--android--medium]] - Performance considerations

### Advanced (Harder)
- Implementing custom dialog destinations in Navigation Component
- Managing dialog state across process death
- Building reusable dialog systems with Compose
