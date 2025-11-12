---
id: android-434
title: "Until What Point Does ViewModel Guarantee State Preservation / До какого момента ViewModel гарантирует сохранение состояния"
aliases: ["Until What Point Does ViewModel Guarantee State Preservation", "До какого момента ViewModel гарантирует сохранение состояния"]
topic: android
subtopics: [lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-lifecycle, q-mvvm-pattern--android--medium, q-viewmodel-vs-onsavedinstancestate--android--medium, q-what-is-viewmodel--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/lifecycle, difficulty/medium, savedstatehandle, viewmodel]

---

# Вопрос (RU)

> До какого момента `ViewModel` гарантирует сохранение состояния?

# Question (EN)

> Until what point does `ViewModel` guarantee state preservation?

## Ответ (RU)

`ViewModel` сохраняет свое состояние (то есть свой инстанс и данные в нем) до тех пор, пока жива ее область видимости (`Activity`, `Fragment` или NavBackStackEntry) и процесс приложения не был уничтожен. Она переживает изменения конфигурации (например, поворот экрана), но не переживает смерть процесса или окончательное уничтожение связанного владельца (`Activity`/`Fragment`). См. также [[c-android-lifecycle]].

### Когда Данные Сохраняются (инстанс `ViewModel` жив)

**Изменения конфигурации**:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()
    // ✅ ViewModel переживает: поворот экрана, смену языка, темную тему
}
```

**`Fragment`-транзакции**: замена `Fragment` в той же `Activity`, добавление в back stack, когда область видимости `ViewModel` (`Activity` или конкретный `Fragment`) остается живой.

**`Activity` в фоне**: `Activity` в onStop(), процесс жив, область видимости не уничтожена.

### Когда Данные Теряются (`ViewModel` очищается)

**`Activity`.finish()**:
```kotlin
fun closeActivity() {
    finish() // ❌ ViewModel.onCleared() будет вызван, так как область видимости уничтожена
}
```

**Навигация Back**: нажатие Back, приводящее к уничтожению корневой `Activity` или окончательному удалению `Fragment`, уничтожает соответствующую `ViewModel`.

**Смерть процесса**: система убивает приложение из-за нехватки памяти, принудительная остановка, crash — инстансы `ViewModel` теряются.

### Обработка Смерти Процесса

Для восстановления критичных данных после смерти процесса используйте `SavedStateHandle` (через SavedStateViewModelFactory или соответствующие API), который сохраняет значения в механизме saved instance state и позволяет создать новый `ViewModel` с восстановленными данными.

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ Значение может быть восстановлено при пересоздании ViewModel после смерти процесса
    var userName: String
        get() = savedStateHandle["user_name"] ?: ""
        set(value) { savedStateHandle["user_name"] = value }

    // ❌ Теряется при смерти процесса (часть только in-memory состояния ViewModel)
    var temporaryData: String = ""
}
```

Важно: `SavedStateHandle` не делает сам `ViewModel` бессмертным — при смерти процесса `ViewModel` уничтожается, но при новом создании может получить сохраненные значения.

### `Fragment`-scoped `ViewModel`

```kotlin
class MyFragment : Fragment() {
    // Привязан к Fragment
    private val fragmentViewModel: MyViewModel by viewModels()
    // Привязан к Activity - переживает пересоздание Fragment в той же Activity
    private val activityViewModel: SharedViewModel by activityViewModels()
}
```

**`Fragment` `ViewModel` очищается**: при окончательном удалении `Fragment` (когда он не находится в back stack) или при завершении родительской `Activity` / уничтожении соответствующей области видимости.

### Лучшие Практики

1. **Критичные данные**: используйте `SavedStateHandle` или `onSaveInstanceState` для данных, которые должны пережить смерть процесса.
2. **Большие данные**: храните в Repository/Database и восстанавливайте во `ViewModel` по необходимости.
3. **Временное UI-состояние**: храните как обычные свойства `ViewModel` (они живут, пока жива `ViewModel`).
4. **Очистка**: реализуйте `onCleared()` для освобождения ресурсов.

```kotlin
class MyViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Освободите ресурсы (отписки, закрытие соединений и т.п.)
        disposables.clear()
    }
}
```

## Answer (EN)

A `ViewModel` instance (and its in-memory state) is retained as long as its scope (`Activity`, `Fragment`, or NavBackStackEntry) is alive and the app process is not killed. It survives configuration changes (e.g., rotation) but does not survive process death or final destruction of its owner (`Activity`/`Fragment`). See also [[c-android-lifecycle]].

### When Data Survives (`ViewModel` instance is kept)

**Configuration Changes**:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()
    // ✅ ViewModel survives: rotation, language change, dark mode
}
```

**`Fragment` Transactions**: `Fragment` replacement within the same `Activity` or back stack operations where the `ViewModel`'s scope (`Activity` or specific `Fragment`) remains alive.

**Background `Activity`**: `Activity` in onStop() with process still alive and its scope not destroyed.

### When Data Is Lost (`ViewModel` is cleared)

**`Activity`.finish()**:
```kotlin
fun closeActivity() {
    finish() // ❌ ViewModel.onCleared() will be called because the scope is destroyed
}
```

**Back Navigation**: A back press that destroys the root `Activity` or permanently removes a `Fragment` will clear the corresponding `ViewModel`.

**Process Death**: When the system kills the app due to memory pressure, force-stop, or crash, `ViewModel` instances are lost.

### Handling Process Death

To restore critical data after process death, use `SavedStateHandle` (via the proper SavedState-enabled `ViewModel` factory / APIs). It persists values via the saved instance state mechanism so that a new `ViewModel` instance can be created with restored data.

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ Value can be restored when a new ViewModel is created after process death
    var userName: String
        get() = savedStateHandle["user_name"] ?: ""
        set(value) { savedStateHandle["user_name"] = value }

    // ❌ Lost on process death (pure in-memory ViewModel state)
    var temporaryData: String = ""
}
```

Important: `SavedStateHandle` does not make the `ViewModel` itself survive process death — the instance is destroyed, but its selected data can be restored into a new instance.

### `Fragment`-Scoped `ViewModel`

```kotlin
class MyFragment : Fragment() {
    // Scoped to Fragment
    private val fragmentViewModel: MyViewModel by viewModels()
    // Scoped to Activity - survives Fragment recreation within the same Activity
    private val activityViewModel: SharedViewModel by activityViewModels()
}
```

**`Fragment` `ViewModel` cleared**: When the `Fragment` is permanently removed (not in the back stack) or when the parent `Activity` finishes / its scope is destroyed.

### Best Practices

1. **Critical data**: Use `SavedStateHandle` or `onSaveInstanceState` for data that must survive process death.
2. **Large data**: Store in a Repository/Database and reload into `ViewModel` as needed.
3. **Temporary UI state**: Store as regular `ViewModel` properties (valid while `ViewModel` is alive).
4. **Cleanup**: Override `onCleared()` to release resources.

```kotlin
class MyViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Release resources (disposables, coroutines, etc.)
        disposables.clear()
    }
}
```

## Дополнительные вопросы (RU)

1. Что произойдет с `ViewModel`, если приложение завершить из списка недавних?
2. Чем `SavedStateHandle` отличается от `onSaveInstanceState`?
3. Каковы ограничения по размеру данных для `SavedStateHandle`?
4. Как протестировать поведение `ViewModel` при смерти процесса?
5. В чем разница жизненного цикла `Activity`-scoped и `Fragment`-scoped `ViewModel` в мульти-фрагментной архитектуре?

## Follow-ups

1. What happens to `ViewModel` when the app is killed from recent apps?
2. How does `SavedStateHandle` differ from `onSaveInstanceState`?
3. What are the size limitations of `SavedStateHandle`?
4. How can you test `ViewModel` survival during process death?
5. What's the lifecycle difference between `Activity`-scoped and `Fragment`-scoped ViewModels in a multi-fragment setup?

## Ссылки (RU)

- [Android Developer Guide: `ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Android Developer Guide: Saved State](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate)

## References

- [Android Developer Guide: `ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Android Developer Guide: Saved State](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate)

## Связанные вопросы (RU)

### Предпосылки
- [[q-what-is-viewmodel--android--medium]] - Что такое `ViewModel` и зачем он нужен
- [[q-mvvm-pattern--android--medium]] - Основы архитектуры MVVM

### Связанные
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - Сравнение `ViewModel` и `onSavedInstanceState`
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - Назначение и внутренняя работа `ViewModel`
- [[q-mvvm-vs-mvp-differences--android--medium]] - Сравнение архитектур MVVM и MVP

### Продвинутые
- [[q-clean-architecture-android--android--hard]] - Чистая архитектура с использованием `ViewModel`
- [[q-mvi-architecture--android--hard]] - MVI и управление состоянием
- [[q-offline-first-architecture--android--hard]] - Offline-first архитектурные подходы

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
