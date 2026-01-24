---
id: android-lc-017
title: LiveData Lifecycle Awareness / Lifecycle-Awareness LiveData
aliases: []
topic: android
subtopics:
- lifecycle
- livedata
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-livedata
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/livedata
- difficulty/medium
anki_cards:
- slug: android-lc-017-0-en
  language: en
  anki_id: 1769172299732
  synced_at: '2026-01-23T16:45:06.379962'
- slug: android-lc-017-0-ru
  language: ru
  anki_id: 1769172299757
  synced_at: '2026-01-23T16:45:06.381091'
---
# Question (EN)
> How does LiveData respect lifecycle and prevent memory leaks?

# Vopros (RU)
> Как LiveData учитывает lifecycle и предотвращает утечки памяти?

---

## Answer (EN)

**LiveData** is lifecycle-aware: it only updates observers in **active** state (STARTED or RESUMED) and automatically removes observers when owner is DESTROYED.

**Lifecycle states mapping:**
```
INITIALIZED -> CREATED -> STARTED -> RESUMED
                 |           |
              inactive    active (receives updates)
                 |           |
              DESTROYED   (auto-removed)
```

**How it works:**
```kotlin
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Observer registered
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Only called when Fragment is STARTED or RESUMED
            updateUI(data)
        }
    }

    // No need to manually remove observer!
    // LiveData auto-removes when viewLifecycleOwner is DESTROYED
}
```

**Internal mechanism:**
```kotlin
// Simplified LiveData.observe() logic:
fun observe(owner: LifecycleOwner, observer: Observer<T>) {
    // 1. Check if already destroyed
    if (owner.lifecycle.currentState == DESTROYED) return

    // 2. Wrap observer with lifecycle awareness
    val wrapper = LifecycleBoundObserver(owner, observer)

    // 3. Register lifecycle observer
    owner.lifecycle.addObserver(wrapper)

    // 4. wrapper.onStateChanged() called on lifecycle events:
    //    - STARTED/RESUMED: mark active, dispatch pending value
    //    - DESTROYED: remove observer
}
```

**Why no memory leaks:**
1. Observer holds reference to Activity/Fragment
2. LiveData observes LifecycleOwner
3. When owner DESTROYED, LiveData removes observer
4. Observer reference released, no leak

**Active vs inactive:**
```kotlin
// Value set while inactive
viewModel.setValue("new value")

// When Fragment becomes STARTED:
// -> Observer receives "new value" immediately

// Value changes while active:
viewModel.setValue("another value")
// -> Observer receives immediately
```

**observeForever (dangerous):**
```kotlin
// NO lifecycle awareness - must manually remove!
liveData.observeForever { value ->
    // Called regardless of lifecycle state
}

// Must remove manually or will leak
override fun onDestroy() {
    liveData.removeObserver(foreverObserver)
}
```

**Common mistakes:**
```kotlin
// BAD: Using this instead of viewLifecycleOwner in Fragment
// Leaks when Fragment's view destroyed but Fragment on back stack
liveData.observe(this) { } // Fragment scope

// GOOD: View scope, removed when view destroyed
liveData.observe(viewLifecycleOwner) { }

// BAD: Registering observer in onResume
// Creates multiple observers, called multiple times
override fun onResume() {
    viewModel.data.observe(viewLifecycleOwner) { } // Don't!
}

// GOOD: Register once in onViewCreated
override fun onViewCreated(...) {
    viewModel.data.observe(viewLifecycleOwner) { }
}
```

## Otvet (RU)

**LiveData** учитывает lifecycle: обновляет observers только в **активном** состоянии (STARTED или RESUMED) и автоматически удаляет observers когда owner DESTROYED.

**Маппинг состояний lifecycle:**
```
INITIALIZED -> CREATED -> STARTED -> RESUMED
                 |           |
              inactive    active (получает обновления)
                 |           |
              DESTROYED   (авто-удалён)
```

**Как это работает:**
```kotlin
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Observer зарегистрирован
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Вызывается только когда Fragment STARTED или RESUMED
            updateUI(data)
        }
    }

    // Не нужно вручную удалять observer!
    // LiveData авто-удаляет когда viewLifecycleOwner DESTROYED
}
```

**Внутренний механизм:**
```kotlin
// Упрощённая логика LiveData.observe():
fun observe(owner: LifecycleOwner, observer: Observer<T>) {
    // 1. Проверить уже ли destroyed
    if (owner.lifecycle.currentState == DESTROYED) return

    // 2. Обернуть observer с lifecycle-awareness
    val wrapper = LifecycleBoundObserver(owner, observer)

    // 3. Зарегистрировать lifecycle observer
    owner.lifecycle.addObserver(wrapper)

    // 4. wrapper.onStateChanged() вызывается на события lifecycle:
    //    - STARTED/RESUMED: пометить активным, отправить ожидающее значение
    //    - DESTROYED: удалить observer
}
```

**Почему нет утечек памяти:**
1. Observer держит ссылку на Activity/Fragment
2. LiveData наблюдает за LifecycleOwner
3. Когда owner DESTROYED, LiveData удаляет observer
4. Ссылка observer освобождена, нет утечки

**Active vs inactive:**
```kotlin
// Значение установлено пока inactive
viewModel.setValue("new value")

// Когда Fragment становится STARTED:
// -> Observer получает "new value" немедленно

// Значение меняется пока active:
viewModel.setValue("another value")
// -> Observer получает немедленно
```

**observeForever (опасно):**
```kotlin
// НЕТ lifecycle awareness - нужно удалять вручную!
liveData.observeForever { value ->
    // Вызывается независимо от состояния lifecycle
}

// Нужно удалять вручную или будет утечка
override fun onDestroy() {
    liveData.removeObserver(foreverObserver)
}
```

**Частые ошибки:**
```kotlin
// ПЛОХО: Использование this вместо viewLifecycleOwner во Fragment
// Утечка когда view Fragment уничтожен но Fragment на back stack
liveData.observe(this) { } // Область Fragment

// ХОРОШО: Область view, удаляется когда view уничтожен
liveData.observe(viewLifecycleOwner) { }

// ПЛОХО: Регистрация observer в onResume
// Создаёт множество observers, вызывается множество раз
override fun onResume() {
    viewModel.data.observe(viewLifecycleOwner) { } // Не делайте!
}

// ХОРОШО: Регистрировать один раз в onViewCreated
override fun onViewCreated(...) {
    viewModel.data.observe(viewLifecycleOwner) { }
}
```

---

## Follow-ups
- What is the difference between LiveData and StateFlow for lifecycle?
- When to use observeForever?
- How does MediatorLiveData handle multiple sources?

## References
- [[c-lifecycle]]
- [[c-livedata]]
- [[moc-android]]
