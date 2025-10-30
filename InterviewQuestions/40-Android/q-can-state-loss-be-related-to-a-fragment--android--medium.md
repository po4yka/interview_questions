---
id: 20251012-122791
title: Can Fragment State Loss Occur? / Бывает ли потеря состояния у Fragment
aliases: ["Can Fragment State Loss Occur?", "Бывает ли потеря состояния у Fragment"]
topic: android
subtopics: [fragment, lifecycle, processes]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, c-viewmodel, c-memory-leaks]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/fragment, android/lifecycle, android/processes, difficulty/medium]
date created: Thursday, October 30th 2025, 11:10:50 am
date modified: Thursday, October 30th 2025, 12:43:30 pm
---

# Вопрос (RU)
> Бывает ли потеря состояния у Fragment?

# Question (EN)
> Can Fragment State Loss Occur?

---

## Ответ (RU)

**Определение**
Потеря состояния фрагмента происходит, когда `FragmentTransaction` выполняется после вызова `onSaveInstanceState()` у Activity. Такая транзакция не сохранится при пересоздании процесса, и изменения UI теряются.

**Основные причины**

1. **Транзакции после сохранения состояния**
   - Асинхронные коллбэки (сеть, база данных)
   - Обработчики событий, сработавшие в background

2. **Смерть процесса**
   - System kill при нехватке памяти
   - Отсутствие персистентного хранения для критичных данных

3. **Пересоздание Activity**
   - Configuration changes (поворот экрана)
   - Возвращение из back stack без сохраненного UI-состояния

**Примеры**

```kotlin
// ❌ Небезопасно - может вызвать IllegalStateException
fun loadData() {
    repository.fetchData { result ->
        // Коллбэк может выполниться после onSaveInstanceState
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ResultFragment())
            .commit()
    }
}

// ✅ Безопасная транзакция
fun loadDataSafely() {
    lifecycleScope.launch {
        val result = repository.fetchData()
        lifecycle.whenResumed {
            if (!supportFragmentManager.isStateSaved) {
                supportFragmentManager.beginTransaction()
                    .replace(R.id.container, ResultFragment())
                    .commit()
            }
        }
    }
}

// ✅ ViewModel сохраняет данные при пересоздании
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Данные переживают configuration changes
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

**Защита от потери состояния**

```kotlin
// Проверка перед транзакцией
if (!fragmentManager.isStateSaved) {
    fragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commit()
}

// Использование commitAllowingStateLoss для некритичных UI
fragmentManager.beginTransaction()
    .replace(R.id.container, TransientDialogFragment())
    .commitAllowingStateLoss()
```

**Best Practices**

- [[c-viewmodel]] для бизнес-логики и данных
- `onSaveInstanceState` только для временного UI-состояния (scroll position, input text)
- `viewLifecycleOwner` для подписок во фрагментах
- `commitAllowingStateLoss()` только для некритичных UI изменений

## Answer (EN)

**Definition**
Fragment state loss occurs when a `FragmentTransaction` is executed after the host Activity's `onSaveInstanceState()` has been called. Such transactions won't be saved during process recreation, causing UI changes to be lost.

**Common Causes**

1. **Transactions After State Saved**
   - Asynchronous callbacks (network, database)
   - Event handlers triggered in background

2. **Process Death**
   - System kill due to memory pressure
   - Missing persistent storage for critical data

3. **Activity Recreation**
   - Configuration changes (screen rotation)
   - Returning from back stack without saved UI state

**Examples**

```kotlin
// ❌ Unsafe - may throw IllegalStateException
fun loadData() {
    repository.fetchData { result ->
        // Callback may execute after onSaveInstanceState
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ResultFragment())
            .commit()
    }
}

// ✅ Safe transaction
fun loadDataSafely() {
    lifecycleScope.launch {
        val result = repository.fetchData()
        lifecycle.whenResumed {
            if (!supportFragmentManager.isStateSaved) {
                supportFragmentManager.beginTransaction()
                    .replace(R.id.container, ResultFragment())
                    .commit()
            }
        }
    }
}

// ✅ ViewModel preserves data across recreation
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Data survives configuration changes
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

**State Loss Prevention**

```kotlin
// Check before transaction
if (!fragmentManager.isStateSaved) {
    fragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commit()
}

// Use commitAllowingStateLoss for non-critical UI
fragmentManager.beginTransaction()
    .replace(R.id.container, TransientDialogFragment())
    .commitAllowingStateLoss()
```

**Best Practices**

- Use [[c-viewmodel]] for business logic and data
- Use `onSaveInstanceState` only for transient UI state (scroll position, input text)
- Use `viewLifecycleOwner` for subscriptions in fragments
- Use `commitAllowingStateLoss()` only for non-critical UI changes

## Follow-ups

1. What's the difference between `commit()`, `commitNow()`, and `commitAllowingStateLoss()` in terms of execution timing and state safety?
2. How does `isStateSaved()` work internally and when exactly does it return true?
3. How do you handle fragment transactions triggered by asynchronous operations (network, database) safely?
4. What data should live in ViewModel vs savedInstanceState vs persistent storage (Room, DataStore)?
5. How does Navigation Component prevent state loss compared to manual FragmentManager usage?

## References

- [[c-viewmodel]]
- [[c-memory-leaks]]
- [[q-activity-lifecycle-methods--android--medium]]
- https://developer.android.com/guide/fragments/lifecycle
- https://developer.android.com/guide/fragments/transactions

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - Understanding Activity lifecycle is essential for Fragment state management

### Related (Same Level)
- Questions about Fragment lifecycle and state restoration mechanisms
- Questions about ViewModel and saved state handling
- Questions about FragmentTransaction commit methods

### Advanced (Harder)
- Questions about Navigation Component and Jetpack Navigation architecture
- Questions about process death handling and state restoration strategies
- Questions about multi-module navigation and deep linking with fragments
