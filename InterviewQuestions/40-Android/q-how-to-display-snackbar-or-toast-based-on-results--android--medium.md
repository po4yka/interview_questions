---
id: "20251015082238645"
title: "How To Display Snackbar Or Toast Based On Results / Как отобразить Snackbar или Toast в зависимости от результатов"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
---
# How to display Snackbar or Toast based on results?

## EN (expanded)

### Toast

Toast is used for brief, non-intrusive notifications that appear temporarily and then disappear automatically. They don't require any user interaction and cannot be dismissed manually.

**Basic Usage:**
```kotlin
Toast.makeText(context, "Message", Toast.LENGTH_SHORT).show()
// or
Toast.makeText(context, "Message", Toast.LENGTH_LONG).show()
```

**When to use Toast:**
- Simple notifications that don't require action
- Confirmation messages (e.g., "Item saved")
- Brief status updates
- Background operation completions

### Snackbar

Snackbar is a more advanced notification mechanism that appears at the bottom of the screen. It can include an action button and can be dismissed by swiping.

**Basic Usage:**
```kotlin
Snackbar.make(view, "Message", Snackbar.LENGTH_SHORT).show()
// or
Snackbar.make(view, "Message", Snackbar.LENGTH_LONG).show()
```

**With Action Button:**
```kotlin
Snackbar.make(view, "Item deleted", Snackbar.LENGTH_LONG)
    .setAction("Undo") {
        // Restore the deleted item
    }
    .show()
```

**When to use Snackbar:**
- When you need to provide an action (e.g., "Undo")
- More prominent notifications
- Messages that need to be associated with a specific UI component
- When you want the user to have the option to dismiss the message

### Key Differences

1. **User Interaction**: Snackbar can have action buttons, Toast cannot
2. **Dismissal**: Snackbar can be swiped away, Toast disappears automatically
3. **View Binding**: Snackbar requires a view to anchor to, Toast only needs context
4. **Positioning**: Toast appears centered (by default), Snackbar appears at the bottom

### In Jetpack Compose

For Compose, you would use `Snackbar` through `SnackbarHost`:

```kotlin
@Composable
fun MyScreen() {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) {
        Button(onClick = {
            scope.launch {
                snackbarHostState.showSnackbar(
                    message = "Item deleted",
                    actionLabel = "Undo"
                )
            }
        }) {
            Text("Show Snackbar")
        }
    }
}
```

For Toast in Compose, you still use the traditional API:
```kotlin
val context = LocalContext.current
Button(onClick = {
    Toast.makeText(context, "Message", Toast.LENGTH_SHORT).show()
}) {
    Text("Show Toast")
}
```

---

## RU (original)

По результатам нужно отобразить Snackbar или Toast, как это сделаешь?

Для отображения Toast можно использовать Toast.makeText(context, "Message", LENGTH).show(), а для Snackbar – Snackbar.make(view, "Message", LENGTH).show(). Toast чаще используется для кратких уведомлений, а Snackbar – для сообщений с действиями, например, кнопкой "Отменить". Snackbar также требует привязки к определённому view.
