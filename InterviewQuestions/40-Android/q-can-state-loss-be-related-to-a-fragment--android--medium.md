---
id: android-174
title: Can Fragment State Loss Occur? / Бывает ли потеря состояния у Fragment
aliases:
- Can Fragment State Loss Occur?
- Бывает ли потеря состояния у Fragment
topic: android
subtopics:
- fragment
- processes
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-fragments
- c-lifecycle
- q-activity-lifecycle-methods--android--medium
sources: []
created: 2024-10-15
updated: 2025-11-10
tags:
- android/fragment
- android/processes
- difficulty/medium

---

# Вопрос (RU)
> Бывает ли потеря состояния у `Fragment`?

# Question (EN)
> Can `Fragment` State Loss Occur?

---

## Ответ (RU)

**Определение**
Потеря состояния фрагмента происходит, когда `FragmentTransaction` выполняется после вызова `onSaveInstanceState()` у `Activity` и изменения не попадают в сохранённое состояние `FragmentManager`. При последующем пересоздании процесса такие транзакции не будут восстановлены, и UI-изменения (добавление/замена фрагментов) теряются.

**Основные причины**

1. **Транзакции после сохранения состояния**
   - Асинхронные коллбэки (сеть, база данных)
   - Обработчики событий, сработавшие в background

2. **Смерть процесса**
   - System kill при нехватке памяти
   - Отсутствие персистентного хранения для критичных данных (`ViewModel` и in-memory данные не восстанавливаются после убийства процесса без сохранения состояния)

3. **Пересоздание `Activity`**
   - Configuration changes (поворот экрана)
   - Возвращение из back stack без корректно сохранённого UI-состояния

**Примеры**

```kotlin
// ❌ Небезопасно - может привести к IllegalStateException или потере состояния
fun loadData() {
    repository.fetchData { result ->
        // Коллбэк может выполниться после onSaveInstanceState,
        // когда FragmentManager уже сохранил своё состояние
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ResultFragment())
            .commit() // требует, чтобы состояние ещё не было сохранено
    }
}

// ✅ Безопасная транзакция: учитываем жизненный цикл и состояние FragmentManager
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

// ✅ ViewModel сохраняет данные при пересоздании Activity (но не заменяет сохранение FragmentTransaction)
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Данные переживают configuration changes, пока процесс жив или состояние восстановлено
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

**Защита от потери состояния**

```kotlin
// Проверка перед транзакцией: выполняем commit() только если состояние ещё не сохранено
if (!fragmentManager.isStateSaved) {
    fragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commit()
}

// Использование commitAllowingStateLoss для некритичных UI-изменений:
// транзакция выполнится даже если состояние уже сохранено, но не будет восстановлена после пересоздания
fragmentManager.beginTransaction()
    .replace(R.id.container, TransientDialogFragment())
    .commitAllowingStateLoss()
```

**Best Practices**

- `ViewModel` для бизнес-логики и долгоживущих данных; не полагаться на фрагменты как источник данных
- `onSaveInstanceState` только для временного UI-состояния (scroll position, input text)
- `viewLifecycleOwner` для подписок во фрагментах
- `commitAllowingStateLoss()` только для некритичных UI изменений, когда потеря транзакции при восстановлении допустима

## Answer (EN)

**Definition**
`Fragment` state loss occurs when a `FragmentTransaction` is executed after the host `Activity`'s `onSaveInstanceState()` has been called and the changes are not recorded into the `FragmentManager`'s saved state. On subsequent process recreation, such transactions will not be restored, so UI changes (adding/replacing fragments) are lost.

**Common Causes**

1. **Transactions After State Saved**
   - Asynchronous callbacks (network, database)
   - Event handlers triggered in background

2. **Process Death**
   - System kill due to memory pressure
   - Missing persistent storage for critical data (`ViewModel` and in-memory data are not restored after process death without saved state)

3. **`Activity` Recreation**
   - Configuration changes (screen rotation)
   - Returning from back stack without correctly saved UI state

**Examples**

```kotlin
// ❌ Unsafe - may lead to IllegalStateException or state loss
fun loadData() {
    repository.fetchData { result ->
        // Callback may execute after onSaveInstanceState,
        // when FragmentManager has already saved its state
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ResultFragment())
            .commit() // requires that state has not been saved yet
    }
}

// ✅ Safe transaction: lifecycle-aware and checks FragmentManager state
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

// ✅ ViewModel preserves data across Activity recreation (but does not replace saving FragmentTransactions)
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Data survives configuration changes while the process is alive or state is restored
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

**State Loss Prevention**

```kotlin
// Check before transaction: call commit() only if state is not yet saved
if (!fragmentManager.isStateSaved) {
    fragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commit()
}

// Use commitAllowingStateLoss for non-critical UI changes:
// the transaction will run even if state is already saved, but it won't be restored after recreation
fragmentManager.beginTransaction()
    .replace(R.id.container, TransientDialogFragment())
    .commitAllowingStateLoss()
```

**Best Practices**

- Use `ViewModel` for business logic and longer-lived data; do not treat Fragments as the single source of truth
- Use `onSaveInstanceState` only for transient UI state (scroll position, input text)
- Use `viewLifecycleOwner` for subscriptions in fragments
- Use `commitAllowingStateLoss()` only for non-critical UI changes where losing the transaction on restore is acceptable

## Дополнительные вопросы (RU)

1. В чём разница между `commit()`, `commitNow()` и `commitAllowingStateLoss()` с точки зрения времени выполнения и безопасности состояния?
2. Как работает `isStateSaved()` внутренне и когда именно он возвращает `true`?
3. Как безопасно обрабатывать транзакции фрагментов, запускаемые асинхронными операциями (сеть, база данных)?
4. Какие данные должны храниться в `ViewModel`, какие — в `savedInstanceState`, а какие — в персистентном хранилище (Room, DataStore)?
5. Как Navigation Component помогает снизить риск потери состояния фрагментов по сравнению с ручным использованием `FragmentManager`?

## Follow-ups

1. What's the difference between `commit()`, `commitNow()`, and `commitAllowingStateLoss()` in terms of execution timing and state safety?
2. How does `isStateSaved()` work internally and when exactly does it return true?
3. How do you handle fragment transactions triggered by asynchronous operations (network, database) safely?
4. What data should live in `ViewModel` vs `savedInstanceState` vs persistent storage (Room, DataStore)?
5. How does Navigation Component help mitigate fragment state loss compared to manual `FragmentManager` usage?

## Ссылки (RU)

- [[c-fragments]]
- Официальная документация по жизненному циклу фрагментов: https://developer.android.com/guide/fragments/lifecycle
- Документация по транзакциям фрагментов: https://developer.android.com/guide/fragments/transactions

## References

- [[c-fragments]]
- Official fragment lifecycle documentation: https://developer.android.com/guide/fragments/lifecycle
- Fragment transactions documentation: https://developer.android.com/guide/fragments/transactions

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-activity-lifecycle-methods--android--medium]] — Понимание жизненного цикла `Activity` важно для управления состоянием `Fragment`.

### Смежные (тот же уровень)
- Вопросы о жизненном цикле `Fragment` и механизмах восстановления состояния
- Вопросы о `ViewModel` и работе с сохранённым состоянием
- Вопросы о методах коммита `FragmentTransaction`

### Продвинутые (сложнее)
- Вопросы о Navigation Component и архитектуре Jetpack Navigation
- Вопросы об обработке смерти процесса и стратегиях восстановления состояния
- Вопросы о мультимодульной навигации и deeplink-ах с использованием фрагментов

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - Understanding `Activity` lifecycle is essential for `Fragment` state management

### Related (Same Level)
- Questions about `Fragment` lifecycle and state restoration mechanisms
- Questions about `ViewModel` and saved state handling
- Questions about `FragmentTransaction` commit methods

### Advanced (Harder)
- Questions about Navigation Component and Jetpack Navigation architecture
- Questions about process death handling and state restoration strategies
- Questions about multi-module navigation and deep linking with fragments
