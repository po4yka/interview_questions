---
id: android-417
title: "Why User Data May Disappear On Screen Rotation / Почему данные пользователя могут пропасть при повороте экрана"
aliases: ["Why User Data May Disappear On Screen Rotation", "Почему данные пользователя могут пропасть при повороте экрана"]
topic: android
subtopics: [activity, architecture-mvvm, lifecycle]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, c-viewmodel]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/activity, android/architecture-mvvm, android/lifecycle, configuration-change, difficulty/hard, state-preservation]

---

# Вопрос (RU)

> Почему пользовательские данные могут исчезнуть при повороте экрана?

# Question (EN)

> Why does user data disappear on screen rotation?

---

## Ответ (RU)

При повороте экрана Android **уничтожает и пересоздаёт `Activity`** как часть обработки изменения конфигурации. Если состояние не сохранено должным образом, все временные данные теряются.

### Почему `Activity` Пересоздаётся

Поворот экрана = изменение конфигурации. Android:
1. Вызывает `onDestroy()` для текущей `Activity`
2. Создаёт новый экземпляр `Activity` через `onCreate()`
3. Загружает layout для новой ориентации

**Последствия:**
- Все переменные экземпляра сбрасываются
- UI состояние может быть потеряно
- Асинхронные операции, привязанные к `Activity`, могут быть отменены

### Основные Причины Потери Данных

**1. Переменные не сохранены**
```kotlin
class LoginActivity : AppCompatActivity() {
    private var username = "" // ❌ Потеряется при повороте, если явно не сохранить
    private var isLoggingIn = false // ❌ Сбросится в false
}
```

**2. EditText без android:id**
```xml
<!-- ❌ Состояние не сохраняется (нет ID, системе не к чему привязать состояние) -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- ✅ Автоматическое сохранение (если view saveEnabled и поддерживается контейнером) -->
<EditText
    android:id="@+id/nameField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**3. Не используется `ViewModel`**
```kotlin
// ❌ Данные теряются между пересозданиями Activity
class BadActivity : AppCompatActivity() {
    private var users: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            users = repository.getUsers() // Повторный запрос при каждом повороте
        }
    }
}

// ✅ ViewModel переживает поворот и позволяет избежать лишних запросов
class GoodActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users ->
            // Запрос не должен повторяться на каждый поворот,
            // если внутри ViewModel данные кэшируются/загружаются один раз
            displayUsers(users)
        }
    }
}
```

**4. `onSaveInstanceState()` не реализован**
```kotlin
class GameActivity : AppCompatActivity() {
    private var score = 0

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("SCORE", score) // ✅ Сохраняем
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Восстанавливаем, если есть сохранённое состояние, иначе значение по умолчанию
        score = savedInstanceState?.getInt("SCORE") ?: 0
    }
}
```

### Решения

**1. `ViewModel` для UI данных**
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
    // ✅ Экземпляр ViewModel переживает изменение конфигурации
}
```

**2. `SavedStateHandle` для критического состояния**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var counter: Int
        get() = savedStateHandle["counter"] ?: 0
        set(value) = savedStateHandle.set("counter", value)
    // ✅ Помогает восстановить важное состояние при повороте и возможной смерти процесса,
    // при условии корректной интеграции через SavedStateViewModelFactory/ViewModelProvider
}
```

**3. `android:id` для Views**
```xml
<EditText
    android:id="@+id/inputField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
<!-- ✅ Позволяет системе автоматически сохранить/восстановить состояние, если saveEnabled=true -->
```

### Жизненный Цикл При Изменении Конфигурации

```
Поворот экрана
    ↓
onPause()
    ↓
onSaveInstanceState() ← СОХРАНИТЬ ДАННЫЕ
    ↓
onStop()
    ↓
onDestroy() ← Activity УНИЧТОЖЕНА
    ↓
onCreate(savedInstanceState) ← НОВАЯ Activity
    ↓
onRestoreInstanceState() ← ВОССТАНОВИТЬ ДАННЫЕ (дополнительно к onCreate)
    ↓
onResume()
```

### Лучшие Практики

1. ✅ Используйте **`ViewModel`** для большинства UI-данных, которые должны переживать изменение конфигурации
2. ✅ Добавляйте **`SavedStateHandle`** для критического/минимального состояния, которое важно сохранить даже при смерти процесса
3. ✅ Добавляйте **`android:id`** ко всем Views с пользовательским вводом (и не отключайте `saveEnabled` без причины)
4. ✅ Используйте **DataStore/Room** для долгосрочного и важного пользовательского состояния/данных
5. ✅ Тестируйте поведение с включенным "Don't keep activities" и эмуляцией изменения конфигураций
6. ❌ Не полагайтесь на переменные экземпляра `Activity` для данных, которые должны пережить пересоздание
7. ❌ Не делайте ненужные повторные сетевые запросы после поворота — кэшируйте данные (например, во `ViewModel` или репозитории)

### Современное Решение

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var uiState: UiState
        get() = savedStateHandle["state"] ?: UiState.default()
        set(value) = savedStateHandle.set("state", value)
}
```

Это обеспечивает сохранение важного UI-состояния при изменении конфигурации и упрощает восстановление после смерти процесса (для сериализуемых и достаточно компактных данных).

---

## Answer (EN)

On screen rotation, Android **destroys and recreates the `Activity`** as part of configuration change handling. If state isn't properly saved, transient UI data is lost.

### Why `Activity` is Recreated

Screen rotation = configuration change. Android:
1. Calls `onDestroy()` on the current `Activity`
2. Creates a new `Activity` instance via `onCreate()`
3. Loads the layout for the new orientation

**Consequences:**
- All instance variables reset
- UI state may be lost
- Async operations tied to the `Activity` lifecycle/scope may be cancelled

### Common Causes of Data Loss

**1. Instance Variables Not Saved**
```kotlin
class LoginActivity : AppCompatActivity() {
    private var username = "" // ❌ Lost on rotation if not explicitly saved
    private var isLoggingIn = false // ❌ Resets to false
}
```

**2. EditText Without `android:id`**
```xml
<!-- ❌ State not preserved (no ID, nothing to associate state with) -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- ✅ Automatic state saving (provided the view is saveEnabled and supported by its parent) -->
<EditText
    android:id="@+id/nameField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**3. Not Using `ViewModel`**
```kotlin
// ❌ Data lost between Activity recreations
class BadActivity : AppCompatActivity() {
    private var users: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            users = repository.getUsers() // Re-fetched on every rotation
        }
    }
}

// ✅ ViewModel survives rotation and can prevent redundant fetches
class GoodActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users ->
            // Fetch should not happen on every rotation if ViewModel caches/loads once internally
            displayUsers(users)
        }
    }
}
```

**4. `onSaveInstanceState()` Not Implemented**
```kotlin
class GameActivity : AppCompatActivity() {
    private var score = 0

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("SCORE", score) // ✅ Save
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Restore if savedInstanceState is not null, otherwise use default
        score = savedInstanceState?.getInt("SCORE") ?: 0
    }
}
```

### Solutions

**1. `ViewModel` for UI Data**
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
    // ✅ ViewModel instance survives configuration changes
}
```

**2. `SavedStateHandle` for Critical State**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var counter: Int
        get() = savedStateHandle["counter"] ?: 0
        set(value) = savedStateHandle.set("counter", value)
    // ✅ Helps restore important state across rotation and potential process death,
    // assuming proper integration via SavedStateViewModelFactory/ViewModelProvider
}
```

**3. `android:id` for Views**
```xml
<EditText
    android:id="@+id/inputField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
<!-- ✅ Allows framework to automatically save/restore state when saveEnabled=true -->
```

### Configuration Change Lifecycle

```
Screen rotation
    ↓
onPause()
    ↓
onSaveInstanceState() ← SAVE DATA
    ↓
onStop()
    ↓
onDestroy() ← Activity DESTROYED
    ↓
onCreate(savedInstanceState) ← NEW Activity
    ↓
onRestoreInstanceState() ← RESTORE DATA (in addition to onCreate)
    ↓
onResume()
```

### Best Practices

1. ✅ Use **`ViewModel`** for most UI-related data that should survive configuration changes
2. ✅ Use **`SavedStateHandle`** for critical/minimal state that must be restorable even after process death
3. ✅ Add **`android:id`** to all Views with user input (and avoid disabling `saveEnabled` without a good reason)
4. ✅ Use **DataStore/Room** for long-term and important user data/state
5. ✅ Test with "Don't keep activities" and configuration change emulation tools
6. ❌ Don't rely on `Activity` instance variables for data that must survive recreation
7. ❌ Don't perform unnecessary duplicate network calls after rotation—cache results (e.g., in `ViewModel` or repository)

### Modern Solution

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var uiState: UiState
        get() = savedStateHandle["state"] ?: UiState.default()
        set(value) = savedStateHandle.set("state", value)
}
```

This helps persist important UI state across configuration changes and simplifies restoring after process death for serializable and reasonably small pieces of state.

---

## Дополнительные вопросы (RU)

1. В чем практическая разница между использованием `onSaveInstanceState()` и `ViewModel` для сохранения состояния в реальных проектах?
2. Как `SavedStateHandle` ведет себя при смерти процесса по сравнению с обычными полями `ViewModel`?
3. В каких случаях (если вообще) уместно использовать `android:configChanges` для ручной обработки поворота вместо пересоздания `Activity` системой?
4. Чем отличается стратегия обработки состояния для `Fragment` и для `Activity` при изменении конфигурации?
5. Как обеспечить корректную отмену или продолжение корутин/Job и другой асинхронной работы при изменении конфигурации?

## Follow-ups

1. What's the difference between `onSaveInstanceState()` and `ViewModel` for state preservation in real projects?
2. How does `SavedStateHandle` interact with process death compared to regular `ViewModel` fields?
3. When (if ever) is it appropriate to use `android:configChanges` to handle rotations manually instead of letting the system recreate the `Activity`?
4. How would you design state handling differently for `Fragment` vs `Activity` when dealing with configuration changes?
5. How can you ensure coroutines/Jobs and other async work are cancelled or resumed correctly across configuration changes?

## Ссылки (RU)

- [[c-activity-lifecycle]] — основы жизненного цикла `Activity`
- [[c-viewmodel]] — архитектурный компонент `ViewModel`
- https://developer.android.com/guide/components/activities/activity-lifecycle
- https://developer.android.com/topic/libraries/architecture/viewmodel-savedstate

## References

- [[c-activity-lifecycle]] - Android `Activity` lifecycle fundamentals
- [[c-viewmodel]] - `ViewModel` architecture component
- https://developer.android.com/guide/components/activities/activity-lifecycle
- https://developer.android.com/topic/libraries/architecture/viewmodel-savedstate

## Связанные вопросы (RU)

### Предпосылки
- [[q-activity-lifecycle-methods--android--medium]] — основы жизненного цикла `Activity`

### Похожие
- [[q-compose-side-effects-advanced--android--hard]] — продвинутые сайд-эффекты в Compose

### Продвинутое
<!-- Оставляем заголовок без ссылок, чтобы избежать битых ссылок. -->

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle basics

### Related
- [[q-compose-side-effects-advanced--android--hard]] - Side effects in Compose

### Advanced
<!-- The following referenced notes are not available; keeping section header only to avoid broken links. -->
