---
id: 20251012-1227111101
title: "Why User Data May Disappear On Screen Rotation / Почему данные пользователя могут пропасть при повороте экрана"
aliases: ["Why User Data May Disappear On Screen Rotation", "Почему данные пользователя могут пропасть при повороте экрана"]
topic: android
subtopics: [lifecycle, activity, architecture-mvvm]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-lifecycle, c-viewmodel, c-mvvm, q-compose-side-effects-advanced--jetpack-compose--hard]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags:
  - android/lifecycle
  - android/activity
  - android/architecture-mvvm
  - configuration-change
  - state-preservation
  - difficulty/hard
date created: Wednesday, October 29th 2025, 1:00:44 pm
date modified: Thursday, October 30th 2025, 3:16:50 pm
---

# Вопрос (RU)

Почему пользовательские данные могут исчезнуть при повороте экрана?

# Question (EN)

Why does user data disappear on screen rotation?

---

## Ответ (RU)

При повороте экрана Android **уничтожает и пересоздаёт Activity** как часть обработки изменения конфигурации. Если состояние не сохранено должным образом, все временные данные теряются.

### Почему Activity пересоздаётся

Поворот экрана = изменение конфигурации. Android:
1. Вызывает `onDestroy()` для текущей Activity
2. Создаёт новый экземпляр Activity через `onCreate()`
3. Загружает layout для новой ориентации

**Последствия:**
- Все переменные экземпляра сбрасываются
- UI состояние может быть потеряно
- Асинхронные операции прерываются

### Основные причины потери данных

**1. Переменные не сохранены**
```kotlin
class LoginActivity : AppCompatActivity() {
    private var username = "" // ❌ Потеряется при повороте
    private var isLoggingIn = false // ❌ Сбросится в false
}
```

**2. EditText без android:id**
```xml
<!-- ❌ Состояние не сохраняется -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- ✅ Автоматическое сохранение -->
<EditText
    android:id="@+id/nameField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**3. Не используется ViewModel**
```kotlin
// ❌ Данные теряются
class BadActivity : AppCompatActivity() {
    private var users: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            users = repository.getUsers() // Повторный запрос при каждом повороте
        }
    }
}

// ✅ Данные сохраняются
class GoodActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users -> // Запрос один раз
            displayUsers(users)
        }
    }
}
```

**4. onSaveInstanceState() не реализован**
```kotlin
class GameActivity : AppCompatActivity() {
    private var score = 0

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("SCORE", score) // ✅ Сохраняем
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        score = savedInstanceState?.getInt("SCORE") ?: 0 // ✅ Восстанавливаем
    }
}
```

### Решения

**1. ViewModel для UI данных**
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
    // ✅ Переживает поворот автоматически
}
```

**2. SavedStateHandle для критического состояния**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var counter: Int
        get() = savedStateHandle["counter"] ?: 0
        set(value) = savedStateHandle.set("counter", value)
    // ✅ Переживает поворот И смерть процесса
}
```

**3. android:id для Views**
```xml
<EditText android:id="@+id/inputField" />
<!-- ✅ Автоматическое сохранение/восстановление -->
```

### Жизненный цикл при изменении конфигурации

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
onRestoreInstanceState() ← ВОССТАНОВИТЬ ДАННЫЕ
    ↓
onResume()
```

### Лучшие практики

1. ✅ Используйте **ViewModel** для всех UI данных
2. ✅ Добавляйте **SavedStateHandle** для критического состояния
3. ✅ Добавляйте **android:id** ко всем Views с пользовательским вводом
4. ✅ Используйте **DataStore/Room** для долгосрочного хранения
5. ✅ Тестируйте с включенным "Don't keep activities"
6. ❌ Не полагайтесь на переменные экземпляра Activity
7. ❌ Не делайте повторные сетевые запросы после поворота

### Современное решение

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var uiState: UiState
        get() = savedStateHandle["state"] ?: UiState.default()
        set(value) = savedStateHandle.set("state", value)
}
```

Это обеспечивает сохранение данных при изменении конфигурации **и** при смерти процесса.

---

## Answer (EN)

On screen rotation, Android **destroys and recreates the Activity** as part of configuration change handling. If state isn't properly saved, all transient data is lost.

### Why Activity is Recreated

Screen rotation = configuration change. Android:
1. Calls `onDestroy()` on current Activity
2. Creates new Activity instance via `onCreate()`
3. Loads appropriate layout for new orientation

**Consequences:**
- All instance variables reset
- UI state may be lost
- Async operations interrupted

### Common Causes of Data Loss

**1. Instance Variables Not Saved**
```kotlin
class LoginActivity : AppCompatActivity() {
    private var username = "" // ❌ Lost on rotation
    private var isLoggingIn = false // ❌ Resets to false
}
```

**2. EditText Without android:id**
```xml
<!-- ❌ State not preserved -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- ✅ Automatic preservation -->
<EditText
    android:id="@+id/nameField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**3. Not Using ViewModel**
```kotlin
// ❌ Data lost
class BadActivity : AppCompatActivity() {
    private var users: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            users = repository.getUsers() // Re-fetched every rotation
        }
    }
}

// ✅ Data preserved
class GoodActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users -> // Fetched once
            displayUsers(users)
        }
    }
}
```

**4. onSaveInstanceState() Not Implemented**
```kotlin
class GameActivity : AppCompatActivity() {
    private var score = 0

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("SCORE", score) // ✅ Save
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        score = savedInstanceState?.getInt("SCORE") ?: 0 // ✅ Restore
    }
}
```

### Solutions

**1. ViewModel for UI Data**
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
    // ✅ Survives rotation automatically
}
```

**2. SavedStateHandle for Critical State**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var counter: Int
        get() = savedStateHandle["counter"] ?: 0
        set(value) = savedStateHandle.set("counter", value)
    // ✅ Survives rotation AND process death
}
```

**3. android:id for Views**
```xml
<EditText android:id="@+id/inputField" />
<!-- ✅ Automatic save/restore -->
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
onRestoreInstanceState() ← RESTORE DATA
    ↓
onResume()
```

### Best Practices

1. ✅ Use **ViewModel** for all UI-related data
2. ✅ Add **SavedStateHandle** for critical state
3. ✅ Add **android:id** to all Views with user input
4. ✅ Use **DataStore/Room** for long-term storage
5. ✅ Test with "Don't keep activities" enabled
6. ❌ Don't rely on Activity instance variables
7. ❌ Don't make redundant network calls after rotation

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

This ensures data survives both configuration changes **and** process death.

---

## Follow-ups

1. What's the difference between `onSaveInstanceState()` and ViewModel for state preservation?
2. How does SavedStateHandle differ from regular ViewModel properties?
3. When should you use `android:configChanges` to prevent Activity recreation?
4. How can you test configuration changes without physically rotating the device?
5. What happens to ongoing coroutines/Jobs when Activity is destroyed on rotation?

## References

- [[c-lifecycle]] - Android lifecycle fundamentals
- [[c-viewmodel]] - ViewModel architecture component
- [[c-mvvm]] - MVVM pattern implementation
- https://developer.android.com/guide/components/activities/activity-lifecycle
- https://developer.android.com/topic/libraries/architecture/viewmodel-savedstate

## Related Questions

### Prerequisites
- [[q-activity-lifecycle--android--medium]] - Activity lifecycle basics
- [[q-viewmodel-basics--android--easy]] - Introduction to ViewModel

### Related
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - Side effects in Compose
- [[q-savedstatehandle-vs-viewmodel--android--medium]] - State preservation strategies

### Advanced
- [[q-process-death-handling--android--hard]] - Handling process death scenarios
- [[q-configuration-changes-custom-handling--android--hard]] - Custom configuration change handling
