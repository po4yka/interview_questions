---
id: android-102
title: Fragment & Activity Lifecycle Connection / Связь жизненных циклов Fragment и Activity
aliases: [Fragment Lifecycle Connection, Связь жизненных циклов Fragment и Activity]
topic: android
subtopics:
  - activity
  - fragment
  - lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
created: 2025-10-13
updated: 2025-11-10
tags: [android, android/activity, android/fragment, android/lifecycle, difficulty/medium]
moc: moc-android
related:
  - c-activity
  - q-android-runtime-art--android--medium
  - q-fragment-vs-activity-lifecycle--android--medium
  - q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-view-composition-strategy-compose--android--medium
sources: []

date created: Saturday, November 1st 2025, 1:31:34 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)

> Как жизненный цикл `Fragment` связан с `Activity`?

# Question (EN)

> How is `Fragment` lifecycle connected with `Activity`?

---

## Ответ (RU)

Жизненный цикл `Fragment` **тесно связан** с жизненным циклом `Activity`. `Fragment` не может находиться в состоянии жизненного цикла **выше**, чем состояние его хост-`Activity` (в терминах AndroidX Lifecycle), но имеет **дополнительные колбэки** (`onAttach`, `onCreateView`, `onViewCreated`, `onDestroyView`, `onDetach`). Переходы состояний `Fragment` инициируются через `FragmentManager` и синхронизируются с состоянием `Activity`.

### Ключевые Правила Зависимости

**1. `Fragment` не превышает состояние `Activity`:**
```kotlin
// Fragment может быть STARTED только когда Activity как минимум STARTED
// Fragment может быть RESUMED только когда Activity RESUMED
// FragmentManager следит за тем, чтобы lifecycle-состояние Fragment
// не превысило lifecycle-состояние Activity-хоста
```

**2. При запуске — упрощённая последовательность колбэков `Fragment` относительно `Activity`:**

(Упрощено для иллюстрации, фактическая последовательность может включать дополнительные колбэки и зависеть от конкретных операций `FragmentManager`.)
```text
Activity.onCreate()
  → Fragment.onAttach()
  → Fragment.onCreate()
  → Fragment.onCreateView()
  → Fragment.onViewCreated()

Activity.onStart()
  → Fragment.onStart()

Activity.onResume()
  → Fragment.onResume()
```

**3. При остановке — упрощённый порядок:**

(Точный порядок зависит от того, как удаляется/заменяется `Fragment` и как завершается `Activity`, но инвариант сохраняется: `Fragment` не остаётся в более "высоком" состоянии, чем `Activity`.)
```text
Activity.onPause()
  → Fragment.onPause()

Activity.onStop()
  → Fragment.onStop()

Activity.onDestroy()
  → Fragment.onDestroyView()
  → Fragment.onDestroy()
  → Fragment.onDetach()
```

### Диаграмма Полного Цикла (Упрощённая)

```text
Activity              Fragment

onCreate()
                      onAttach()
                      onCreate()
                      onCreateView()
                      onViewCreated()
                      onStart()
onStart()
onResume()            onResume()

[работает приложение]

onPause()
                      onPause()
onStop()
                      onStop()
                      onDestroyView()
                      onDestroy()
                      onDetach()
onDestroy()
```

(Это иллюстрация. При уничтожении `Activity` связанные `Fragment` уничтожаются как часть этого процесса; точный порядок отдельных колбэков может отличаться, но `Fragment` не переходит в состояние выше, чем `Activity`.)

### Раздельный Жизненный Цикл `View`

`Fragment` имеет **два владельца жизненного цикла**:
- сам `Fragment` (состояние instance),
- `viewLifecycleOwner` (для `View`-иерархии внутри `Fragment`).

```kotlin
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels() // пример корректного скоупа

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ❌ НЕПРАВИЛЬНО — наблюдатель переживёт onDestroyView()
        // и может удерживать View, вызывая утечки и крэши
        viewModel.data.observe(this) { data ->
            textView.text = data // Возможен CRASH, если View уже уничтожен
        }

        // ✅ ПРАВИЛЬНО — привязан к viewLifecycleOwner и автоматически
        // отписывается при onDestroyView()
        viewModel.data.observe(viewLifecycleOwner) { data ->
            textView.text = data
        }
    }
}
```

**Жизненные циклы (схематично):**
```text
Fragment:     onCreate ————————————————→ onDestroy
View:              onCreateView ——→ onDestroyView
```

### BackStack Поведение

**При replace с addToBackStack():**
```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, NewFragment())
    .addToBackStack(null)
    .commit()

// Старый Fragment:
// onPause() → onStop() → onDestroyView()
// ⚠️ Экземпляр Fragment и его не-view-состояние могут быть сохранены FragmentManager'ом
// для восстановления; onDestroy()/onDetach() обычно не вызываются до окончательного
// удаления из BackStack. При нехватке ресурсов система может пересоздать экземпляр.

// При возврате назад (упрощённо):
// onCreateView() → onViewCreated() → onStart() → onResume()
```

### Управление Ресурсами `View`

```kotlin
class MyFragment : Fragment() {
    private var binding: FragmentBinding? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentBinding.inflate(inflater, container, false)
        return binding!!.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ✅ ВАЖНО для view-based binding-паттерна — обнуляем ссылку на View,
        // чтобы не удерживать уничтоженную View-иерархию и избежать утечек памяти
        binding = null
    }
}
```

### Лучшие Практики

**1. Используйте `viewLifecycleOwner` для UI-событий, подписок и корутин, завязанных на `View`:**
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.uiState.collect { state ->
        // Коррутина будет отменена при onDestroyView()
    }
}
```

**2. Инициализация в правильных колбэках:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Инициализация без UI (ViewModel, данные)
    viewModel.loadData()
}

override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    // Инициализация UI компонентов, зависящих от View
    setupRecyclerView()
}
```

## Answer (EN)

`Fragment` lifecycle is **tightly coupled** with `Activity` lifecycle. A `Fragment` cannot be in a lifecycle state **higher** than its host `Activity` (in AndroidX Lifecycle terms), but it has **additional callbacks** (`onAttach`, `onCreateView`, `onViewCreated`, `onDestroyView`, `onDetach`). `Fragment` state transitions are driven by the `FragmentManager` and synchronized with the `Activity` state.

### Key Dependency Rules

**1. `Fragment` never exceeds `Activity` state:**
```kotlin
// Fragment can be STARTED only when Activity is at least STARTED
// Fragment can be RESUMED only when Activity is RESUMED
// FragmentManager ensures that the Fragment's lifecycle state
// does not exceed the host Activity's lifecycle state
```

**2. On startup — simplified `Fragment` callbacks relative to `Activity`:**

(Simplified for illustration; the real sequence includes more callbacks and depends on `FragmentManager` operations.)
```text
Activity.onCreate()
  → Fragment.onAttach()
  → Fragment.onCreate()
  → Fragment.onCreateView()
  → Fragment.onViewCreated()

Activity.onStart()
  → Fragment.onStart()

Activity.onResume()
  → Fragment.onResume()
```

**3. On shutdown — simplified order:**

(Exact order depends on how the `Fragment` is removed/replaced and how the `Activity` finishes, but the invariant holds: a `Fragment` will not remain in a "higher" state than its `Activity`.)
```text
Activity.onPause()
  → Fragment.onPause()

Activity.onStop()
  → Fragment.onStop()

Activity.onDestroy()
  → Fragment.onDestroyView()
  → Fragment.onDestroy()
  → Fragment.onDetach()
```

### Complete Lifecycle Diagram (Simplified)

```text
Activity              Fragment

onCreate()
                      onAttach()
                      onCreate()
                      onCreateView()
                      onViewCreated()
                      onStart()
onStart()
onResume()            onResume()

[app running]

onPause()
                      onPause()
onStop()
                      onStop()
                      onDestroyView()
                      onDestroy()
                      onDetach()
onDestroy()
```

(This is an illustration. When an `Activity` is destroyed, its `Fragments` are destroyed as part of that process; individual callback ordering may vary, but a `Fragment` will not advance beyond the `Activity` state.)

### Separate `View` Lifecycle

`Fragment` effectively exposes **two lifecycle owners**:
- the `Fragment` itself (its instance and logical state),
- the `viewLifecycleOwner` (for the `Fragment`'s `View` hierarchy).

```kotlin
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels() // example of proper scope

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ❌ WRONG — observer outlives onDestroyView() and may hold onto
        // the destroyed View, causing leaks and crashes
        viewModel.data.observe(this) { data ->
            textView.text = data // Potential CRASH if View is already destroyed
        }

        // ✅ CORRECT — bound to viewLifecycleOwner and automatically
        // removed at onDestroyView()
        viewModel.data.observe(viewLifecycleOwner) { data ->
            textView.text = data
        }
    }
}
```

**Lifecycles (schematic):**
```text
Fragment:     onCreate ————————————————→ onDestroy
View:              onCreateView ——→ onDestroyView
```

### BackStack Behavior

**On replace with addToBackStack():**
```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, NewFragment())
    .addToBackStack(null)
    .commit()

// Old Fragment:
// onPause() → onStop() → onDestroyView()
// ⚠️ The Fragment instance and its non-view state may be retained by FragmentManager
// for restoration; onDestroy()/onDetach() are typically not called until it is
// finally removed from the BackStack. If needed, the system/FragmentManager may
// recreate the instance later.

// On back press (simplified):
// onCreateView() → onViewCreated() → onStart() → onResume()
```

### `View` Resource Management

```kotlin
class MyFragment : Fragment() {
    private var binding: FragmentBinding? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentBinding.inflate(inflater, container, false)
        return binding!!.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ✅ IMPORTANT for this nullable binding pattern — clear the reference
        // to the destroyed View hierarchy to avoid memory leaks
        binding = null
    }
}
```

### Best Practices

**1. Use `viewLifecycleOwner` for UI-bound observers and coroutines tied to the `View`:**
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.uiState.collect { state ->
        // Cancelled automatically in onDestroyView()
    }
}
```

**2. Initialize in appropriate callbacks:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Initialize non-UI components (ViewModel, data loading)
    viewModel.loadData()
}

override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    // Initialize UI components that depend on the created View
    setupRecyclerView()
}
```

---

## Дополнительные Вопросы (RU)

- Что происходит с `Fragment`, когда `Activity` уничтожается из-за изменения конфигурации?
- Как `ViewModel` сохраняется при пересоздании `Fragment` в сценариях с BackStack?
- Когда следует использовать жизненный цикл `Fragment` против `viewLifecycleOwner` для корутин?
- В чем разница между транзакциями `Fragment` `replace()`, `add()` и `show()/hide()`?
- Как `setRetainInstance(true)` влияет на жизненный цикл `Fragment` (deprecated)?

## Ссылки (RU)

- Официальная документация Android: жизненный цикл `Fragment` — https://developer.android.com/guide/fragments/lifecycle
- Официальная документация Android: `ViewLifecycleOwner` — https://developer.android.com/reference/androidx/fragment/app/Fragment#getViewLifecycleOwner()

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-activity]]

### Предпосылки (проще)

- Основы жизненного цикла `Activity` — сначала понять состояния `Activity`
- Основы `Fragment` — что такое `Fragment` и зачем он нужен

### Связанные (такой Же уровень)

- [[q-android-runtime-art--android--medium]] — Понимание Android runtime
- [[q-view-composition-strategy-compose--android--medium]] — Современный жизненный цикл UI

### Продвинутые (сложнее)

- Управление состоянием BackStack `Fragment` — сложные сценарии навигации
- Shared element-переходы в `Fragment` — координация жизненного цикла с анимациями

## Follow-ups

- What happens to `Fragment` when `Activity` is destroyed due to configuration change?
- How does `ViewModel` survive `Fragment` recreation in BackStack scenarios?
- When should you use `Fragment` lifecycle vs `viewLifecycleOwner` for coroutines?
- What are the differences between `replace()`, `add()`, and `show()/hide()` `Fragment` transactions?
- How does `setRetainInstance(true)` affect `Fragment` lifecycle (deprecated)?

## References

- Android Official: `Fragment` Lifecycle — https://developer.android.com/guide/fragments/lifecycle
- Android Official: `ViewLifecycleOwner` — https://developer.android.com/reference/androidx/fragment/app/Fragment#getViewLifecycleOwner()

## Related Questions

### Prerequisites / Concepts

- [[c-activity]]

### Prerequisites (Easier)
- `Activity` lifecycle basics — understand `Activity` states first
- `Fragment` basics — what is `Fragment` and why use it

### Related (Same Level)
- [[q-android-runtime-art--android--medium]] — Understanding Android runtime
- [[q-view-composition-strategy-compose--android--medium]] — Modern UI lifecycle

### Advanced (Harder)
- `Fragment` BackStack state management — complex navigation scenarios
- `Fragment` shared element transitions — coordinating lifecycle with animations
