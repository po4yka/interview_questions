---
id: android-434
title: "Until What Point Does ViewModel Guarantee State Preservation / До какого момента ViewModel гарантирует сохранение состояния"
aliases: ["Until What Point Does ViewModel Guarantee State Preservation", "До какого момента ViewModel гарантирует сохранение состояния"]
topic: android
subtopics: [architecture-mvvm, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-mvvm-pattern--android--medium, q-viewmodel-vs-onsavedinstancestate--android--medium, q-what-is-viewmodel--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android, android/architecture-mvvm, android/lifecycle, difficulty/medium, lifecycle, savedstatehandle, viewmodel]
---

# Вопрос (RU)

До какого момента `ViewModel` гарантирует сохранение состояния?

# Question (EN)

Until what point does `ViewModel` guarantee state preservation?

---

## Ответ (RU)

`ViewModel` гарантирует сохранение состояния до момента полного завершения `Activity` или уничтожения процесса. Она переживает изменения конфигурации (поворот экрана), но не переживает смерть процесса.

### Когда Данные Сохраняются

**Изменения конфигурации**:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()
    // ✅ ViewModel переживает: поворот экрана, смену языка, темную тему
}
```

**`Fragment` транзакции**: замена `Fragment` в той же `Activity`, добавление в back stack.

**`Activity` в фоне**: `Activity` в onStop(), процесс жив.

### Когда Данные Теряются

**`Activity`.finish()**:
```kotlin
fun closeActivity() {
    finish() // ❌ ViewModel.onCleared() будет вызван
}
```

**Смерть процесса**: система убивает приложение из-за нехватки памяти, принудительная остановка, crash.

**Back навигация**: нажатие back на корневой `Activity`.

### Обработка Смерти Процесса

Используйте SavedStateHandle для критичных данных:

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ Переживает смерть процесса
    var userName: String
        get() = savedStateHandle["user_name"] ?: ""
        set(value) { savedStateHandle["user_name"] = value }

    // ❌ Теряется при смерти процесса
    var temporaryData: String = ""
}
```

### `Fragment`-scoped `ViewModel`

```kotlin
class MyFragment : Fragment() {
    // Привязан к Fragment
    private val fragmentViewModel: MyViewModel by viewModels()
    // Привязан к Activity - переживает пересоздание Fragment
    private val activityViewModel: SharedViewModel by activityViewModels()
}
```

**`Fragment` `ViewModel` очищается**: при окончательном удалении `Fragment` (не в back stack) или завершении родительской `Activity`.

### Лучшие Практики

1. **Критичные данные**: SavedStateHandle
2. **Большие данные**: Repository/Database
3. **Временное UI состояние**: обычные свойства `ViewModel`
4. **Очистка**: реализуйте onCleared()

```kotlin
class MyViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Освободите ресурсы
        disposables.clear()
    }
}
```

## Answer (EN)

`ViewModel` guarantees state preservation until `Activity` finishes or process is killed. It survives configuration changes (screen rotation) but not process death.

### When Data Survives

**Configuration Changes**:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()
    // ✅ ViewModel survives: rotation, language change, dark mode
}
```

**`Fragment` Transactions**: `Fragment` replacement in same `Activity`, back stack additions.

**Background `Activity`**: `Activity` in onStop(), process alive.

### When Data Is Lost

**`Activity`.finish()**:
```kotlin
fun closeActivity() {
    finish() // ❌ ViewModel.onCleared() will be called
}
```

**Process Death**: System kills app due to memory pressure, force-stop, crash.

**Back Navigation**: Back press on root `Activity`.

### Handling Process Death

Use SavedStateHandle for critical data:

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ Survives process death
    var userName: String
        get() = savedStateHandle["user_name"] ?: ""
        set(value) { savedStateHandle["user_name"] = value }

    // ❌ Lost on process death
    var temporaryData: String = ""
}
```

### `Fragment`-Scoped `ViewModel`

```kotlin
class MyFragment : Fragment() {
    // Scoped to Fragment
    private val fragmentViewModel: MyViewModel by viewModels()
    // Scoped to Activity - survives Fragment recreation
    private val activityViewModel: SharedViewModel by activityViewModels()
}
```

**`Fragment` `ViewModel` cleared**: When `Fragment` permanently removed (not in back stack) or parent `Activity` finishes.

### Best Practices

1. **Critical data**: SavedStateHandle
2. **Large data**: Repository/Database
3. **Temporary UI state**: Regular `ViewModel` properties
4. **Cleanup**: Implement onCleared()

```kotlin
class MyViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Release resources
        disposables.clear()
    }
}
```

---

## Follow-ups

1. What happens to `ViewModel` when the app is killed from recent apps?
2. How does SavedStateHandle differ from onSaveInstanceState?
3. What are the size limitations of SavedStateHandle?
4. How can you test `ViewModel` survival during process death?
5. What's the lifecycle difference between `Activity`-scoped and `Fragment`-scoped ViewModels in a multi-fragment setup?

## References

- [[c-viewmodel]] - `ViewModel` concept and architecture
- [[c-savedstatehandle]] - SavedStateHandle for process death handling
- [[c-mvvm-pattern]] - MVVM architectural pattern
- [[c-lifecycle]] - Android lifecycle components
- [Android Developer Guide: `ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Android Developer Guide: Saved State](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate)

## Related Questions

### Prerequisites
- [[q-what-is-viewmodel--android--medium]] - What is `ViewModel` and why is it needed
- [[q-mvvm-pattern--android--medium]] - MVVM architecture pattern basics

### Related
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - `ViewModel` vs onSavedInstanceState comparison
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - `ViewModel` internals and purpose
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP architectural comparison

### Advanced
- [[q-clean-architecture-android--android--hard]] - Clean Architecture with `ViewModel`
- [[q-mvi-architecture--android--hard]] - MVI pattern and state management
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture patterns
