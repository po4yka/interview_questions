---
id: 20251012-1227178
title: "How To Display Snackbar Or Toast Based On Results / Как отобразить Snackbar или Toast в зависимости от результатов"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-how-animations-work-in-recyclerview--android--medium, q-navigation-methods-in-kotlin--android--medium]
created: 2025-10-15
tags: [android]
date created: Saturday, October 25th 2025, 1:26:31 pm
date modified: Saturday, October 25th 2025, 4:39:51 pm
---

# How to Display Snackbar or Toast Based on Results?

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
Отображение Snackbar или Toast на основе результатов операций - распространенный паттерн в Android.

**Toast - простое сообщение:**

```kotlin
class MyActivity : AppCompatActivity() {

    fun showResult(result: Result<Data>) {
        when (result) {
            is Result.Success -> {
                Toast.makeText(
                    this,
                    "Success: \${result.data}",
                    Toast.LENGTH_SHORT
                ).show()
            }
            is Result.Error -> {
                Toast.makeText(
                    this,
                    "Error: \${result.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}
```

**Snackbar - с действием:**

```kotlin
fun showSnackbar(result: Result<Data>) {
    when (result) {
        is Result.Success -> {
            Snackbar.make(
                binding.root,
                "Success!",
                Snackbar.LENGTH_SHORT
            ).show()
        }
        is Result.Error -> {
            Snackbar.make(
                binding.root,
                "Error occurred",
                Snackbar.LENGTH_LONG
            ).setAction("Retry") {
                retryOperation()
            }.show()
        }
    }
}
```

**В ViewModel с Flow:**

```kotlin
class MyViewModel : ViewModel() {
    private val _messages = MutableSharedFlow<UiMessage>()
    val messages: SharedFlow<UiMessage> = _messages.asSharedFlow()

    suspend fun performAction() {
        try {
            val result = repository.doWork()
            _messages.emit(UiMessage.Success("Done!"))
        } catch (e: Exception) {
            _messages.emit(UiMessage.Error(e.message))
        }
    }
}

// В Activity
lifecycleScope.launch {
    viewModel.messages.collect { message ->
        when (message) {
            is UiMessage.Success -> showToast(message.text)
            is UiMessage.Error -> showSnackbar(message.text)
        }
    }
}
```

**В Compose:**

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.messages.collect { message ->
            snackbarHostState.showSnackbar(
                message = message.text,
                duration = SnackbarDuration.Short
            )
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) {
        Content()
    }
}
```

**Одноразовые события с Event wrapper:**

```kotlin
data class Event<out T>(private val content: T) {
    private var hasBeenHandled = false

    fun getContentIfNotHandled(): T? {
        return if (hasBeenHandled) {
            null
        } else {
            hasBeenHandled = true
            content
        }
    }
}

class MyViewModel : ViewModel() {
    private val _toastMessage = MutableLiveData<Event<String>>()
    val toastMessage: LiveData<Event<String>> = _toastMessage

    fun doWork() {
        _toastMessage.value = Event("Work completed")
    }
}

// Наблюдение
viewModel.toastMessage.observe(this) { event ->
    event.getContentIfNotHandled()?.let { message ->
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
```

**Best Practices:**

1. ✅ Snackbar для действий требующих взаимодействия
2. ✅ Toast для простых информационных сообщений
3. ✅ Используйте SharedFlow для one-time events
4. ✅ В Compose используйте SnackbarHost
5. ❌ Не показывайте Toast из фоновых потоков

## Related Questions

- [[q-navigation-methods-in-kotlin--android--medium]]
- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-android-architectural-patterns--android--medium]]
