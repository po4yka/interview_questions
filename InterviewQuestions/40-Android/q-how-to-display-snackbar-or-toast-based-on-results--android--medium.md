---
id: android-426
title: "How To Display Snackbar Or Toast Based On Results / Как отобразить Snackbar или Toast в зависимости от результатов"
aliases: ["How To Display Snackbar Or Toast", "Как отобразить Snackbar или Toast"]
topic: android
subtopics: [architecture-mvvm, ui-compose, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-how-animations-work-in-recyclerview--android--medium, q-navigation-methods-in-kotlin--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android, android/architecture-mvvm, android/ui-compose, android/ui-views, difficulty/medium, notifications, snackbar, toast]
---

# Вопрос (RU)

Как правильно отображать Toast и Snackbar в зависимости от результатов операций в Android-приложении?

# Question (EN)

How to properly display Toast and Snackbar based on operation results in Android applications?

## Ответ (RU)

### Основные Различия

**Toast** — простое временное уведомление без взаимодействия:
- Не требует действий пользователя
- Исчезает автоматически
- Не может быть закрыто вручную
- Использует только Context

**Snackbar** — продвинутое уведомление с возможностями:
- Может содержать кнопку действия
- Закрывается свайпом
- Привязывается к конкретному View
- Появляется внизу экрана

### Базовое Использование

```kotlin
// ✅ Toast для простых уведомлений
Toast.makeText(context, "Данные сохранены", Toast.LENGTH_SHORT).show()

// ✅ Snackbar с действием
Snackbar.make(view, "Элемент удален", Snackbar.LENGTH_LONG)
    .setAction("Отменить") {
        // Восстановить элемент
    }
    .show()
```

### Архитектурный Подход С ViewModel

```kotlin
// Модель UI-событий
sealed class UiMessage {
    data class Success(val text: String) : UiMessage()
    data class Error(val text: String, val canRetry: Boolean = false) : UiMessage()
}

class MyViewModel : ViewModel() {
    private val _messages = MutableSharedFlow<UiMessage>()
    val messages: SharedFlow<UiMessage> = _messages.asSharedFlow()

    suspend fun performAction() {
        try {
            val result = repository.doWork()
            _messages.emit(UiMessage.Success("Готово!"))
        } catch (e: Exception) {
            _messages.emit(UiMessage.Error(e.message ?: "Ошибка", canRetry = true))
        }
    }
}

// ✅ В Activity/Fragment
lifecycleScope.launch {
    viewModel.messages.collect { message ->
        when (message) {
            is UiMessage.Success -> Toast.makeText(this@MyActivity, message.text, Toast.LENGTH_SHORT).show()
            is UiMessage.Error -> {
                Snackbar.make(binding.root, message.text, Snackbar.LENGTH_LONG).apply {
                    if (message.canRetry) {
                        setAction("Повтор") { viewModel.performAction() }
                    }
                }.show()
            }
        }
    }
}
```

### Jetpack Compose

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current

    // ✅ Обработка UI-событий
    LaunchedEffect(Unit) {
        viewModel.messages.collect { message ->
            when (message) {
                is UiMessage.Success ->
                    Toast.makeText(context, message.text, Toast.LENGTH_SHORT).show()
                is UiMessage.Error -> {
                    val result = snackbarHostState.showSnackbar(
                        message = message.text,
                        actionLabel = if (message.canRetry) "Повтор" else null,
                        duration = SnackbarDuration.Long
                    )
                    if (result == SnackbarResult.ActionPerformed) {
                        // Выполнить повторную попытку
                    }
                }
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Content(modifier = Modifier.padding(padding))
    }
}
```

### Best Practices

- ✅ **Snackbar для действий**: Используйте когда нужно взаимодействие (Undo, Retry)
- ✅ **Toast для информации**: Простые уведомления без действий
- ✅ **SharedFlow для событий**: Избегайте повторной отправки при пересоздании UI
- ✅ **Lifecycle-aware**: Собирайте Flow в `lifecycleScope` или `repeatOnLifecycle`
- ❌ **Не используйте Toast из фоновых потоков**: Только из главного потока
- ❌ **Не злоупотребляйте**: Критичные ошибки лучше показывать через Dialog

## Answer (EN)

### Key Differences

**Toast** — simple temporary notification without interaction:
- Requires no user action
- Disappears automatically
- Cannot be dismissed manually
- Requires only Context

**Snackbar** — advanced notification with capabilities:
- Can contain action button
- Dismissed by swiping
- Anchored to specific View
- Appears at bottom of screen

### Basic Usage

```kotlin
// ✅ Toast for simple notifications
Toast.makeText(context, "Data saved", Toast.LENGTH_SHORT).show()

// ✅ Snackbar with action
Snackbar.make(view, "Item deleted", Snackbar.LENGTH_LONG)
    .setAction("Undo") {
        // Restore item
    }
    .show()
```

### Architectural Approach with ViewModel

```kotlin
// UI events model
sealed class UiMessage {
    data class Success(val text: String) : UiMessage()
    data class Error(val text: String, val canRetry: Boolean = false) : UiMessage()
}

class MyViewModel : ViewModel() {
    private val _messages = MutableSharedFlow<UiMessage>()
    val messages: SharedFlow<UiMessage> = _messages.asSharedFlow()

    suspend fun performAction() {
        try {
            val result = repository.doWork()
            _messages.emit(UiMessage.Success("Done!"))
        } catch (e: Exception) {
            _messages.emit(UiMessage.Error(e.message ?: "Error", canRetry = true))
        }
    }
}

// ✅ In Activity/Fragment
lifecycleScope.launch {
    viewModel.messages.collect { message ->
        when (message) {
            is UiMessage.Success -> Toast.makeText(this@MyActivity, message.text, Toast.LENGTH_SHORT).show()
            is UiMessage.Error -> {
                Snackbar.make(binding.root, message.text, Snackbar.LENGTH_LONG).apply {
                    if (message.canRetry) {
                        setAction("Retry") { viewModel.performAction() }
                    }
                }.show()
            }
        }
    }
}
```

### Jetpack Compose

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current

    // ✅ Handle UI events
    LaunchedEffect(Unit) {
        viewModel.messages.collect { message ->
            when (message) {
                is UiMessage.Success ->
                    Toast.makeText(context, message.text, Toast.LENGTH_SHORT).show()
                is UiMessage.Error -> {
                    val result = snackbarHostState.showSnackbar(
                        message = message.text,
                        actionLabel = if (message.canRetry) "Retry" else null,
                        duration = SnackbarDuration.Long
                    )
                    if (result == SnackbarResult.ActionPerformed) {
                        // Execute retry
                    }
                }
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Content(modifier = Modifier.padding(padding))
    }
}
```

### Best Practices

- ✅ **Snackbar for actions**: Use when interaction needed (Undo, Retry)
- ✅ **Toast for information**: Simple notifications without actions
- ✅ **SharedFlow for events**: Avoid re-emission on UI recreation
- ✅ **Lifecycle-aware**: Collect Flow in `lifecycleScope` or `repeatOnLifecycle`
- ❌ **Don't use Toast from background threads**: Main thread only
- ❌ **Don't overuse**: Critical errors better shown via Dialog

## Follow-ups

- How to handle multiple simultaneous Snackbar messages in a queue?
- What are the accessibility considerations for Toast and Snackbar?
- How to test Snackbar and Toast interactions in UI tests?
- When should you use Dialog instead of Snackbar for error handling?

## References

- [[c-viewmodel]]
- [[c-coroutines]]

## Related Questions

### Prerequisites
- [[q-android-architectural-patterns--android--medium]] - Understanding MVVM architecture
- [[q-navigation-methods-in-kotlin--android--medium]] - Navigation basics for UI flow

### Related
- [[q-how-animations-work-in-recyclerview--android--medium]] - UI interactions in Android

### Advanced
- Implementing custom Snackbar with Material Design 3
- Building a centralized notification system with priority queues
- Accessibility testing for transient UI elements
