---
id: android-102
title: Fragment & Activity Lifecycle Connection / Связь жизненных циклов Fragment
  и Activity
aliases:
- Fragment Lifecycle Connection
- Связь жизненных циклов Fragment и Activity
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
updated: 2025-10-28
tags:
- android
- android/activity
- android/fragment
- android/lifecycle
- difficulty/medium
moc: moc-android
related:
- c-activity
- c-fragments
- c-lifecycle
- q-android-runtime-art--android--medium
- q-view-composition-strategy-compose--android--medium
sources: []
---

# Вопрос (RU)

> Как жизненный цикл `Fragment` связан с `Activity`?

# Question (EN)

> How is `Fragment` lifecycle connected with `Activity`?

---

## Ответ (RU)

Жизненный цикл `Fragment` **тесно связан** с жизненным циклом `Activity`. `Fragment` никогда не может превысить состояние жизненного цикла `Activity`, но имеет **дополнительные колбэки** (onAttach, onCreateView, onViewCreated, onDestroyView, onDetach).

### Ключевые Правила Зависимости

**1. `Fragment` не превышает состояние `Activity`:**
```kotlin
// Fragment может быть STARTED только когда Activity STARTED
// Fragment может быть RESUMED только когда Activity RESUMED
```

**2. При запуске — `Fragment` колбэки ПОСЛЕ `Activity`:**
```
Activity.onCreate() → Fragment.onCreate()
Activity.onStart() → Fragment.onStart()
Activity.onResume() → Fragment.onResume()
```

**3. При остановке — `Fragment` колбэки ПЕРЕД `Activity`:**
```
Fragment.onPause() → Activity.onPause()
Fragment.onStop() → Activity.onStop()
Fragment.onDestroy() → Activity.onDestroy()
```

### Диаграмма Полного Цикла

```
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

### Раздельный Жизненный Цикл `View`

`Fragment` имеет **два владельца жизненного цикла**:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ❌ НЕПРАВИЛЬНО — наблюдатель останется после onDestroyView()
        viewModel.data.observe(this) { data ->
            textView.text = data // CRASH если View уже уничтожен
        }

        // ✅ ПРАВИЛЬНО — автоматически отписывается в onDestroyView()
        viewModel.data.observe(viewLifecycleOwner) { data ->
            textView.text = data
        }
    }
}
```

**Жизненные циклы:**
```
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
// ⚠️ Fragment остаётся в памяти (НЕ вызывается onDestroy/onDetach)

// При возврате назад:
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
        // ✅ ОБЯЗАТЕЛЬНО — предотвращаем утечку памяти
        binding = null
    }
}
```

### Лучшие Практики

**1. Используйте viewLifecycleOwner для UI:**
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.uiState.collect { state ->
        // Отменяется в onDestroyView()
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
    // Инициализация UI компонентов
    setupRecyclerView()
}
```

## Answer (EN)

`Fragment` lifecycle is **tightly coupled** with `Activity` lifecycle. `Fragment` can never exceed the `Activity`'s lifecycle state but has **additional callbacks** (onAttach, onCreateView, onViewCreated, onDestroyView, onDetach).

### Key Dependency Rules

**1. `Fragment` never exceeds `Activity` state:**
```kotlin
// Fragment can only be STARTED when Activity is STARTED
// Fragment can only be RESUMED when Activity is RESUMED
```

**2. On startup — `Fragment` callbacks AFTER `Activity`:**
```
Activity.onCreate() → Fragment.onCreate()
Activity.onStart() → Fragment.onStart()
Activity.onResume() → Fragment.onResume()
```

**3. On shutdown — `Fragment` callbacks BEFORE `Activity`:**
```
Fragment.onPause() → Activity.onPause()
Fragment.onStop() → Activity.onStop()
Fragment.onDestroy() → Activity.onDestroy()
```

### Complete `Lifecycle` Diagram

```
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

### Separate `View` `Lifecycle`

`Fragment` has **two lifecycle owners**:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ❌ WRONG — observer stays active after onDestroyView()
        viewModel.data.observe(this) { data ->
            textView.text = data // CRASH if View is destroyed
        }

        // ✅ CORRECT — auto-unsubscribed in onDestroyView()
        viewModel.data.observe(viewLifecycleOwner) { data ->
            textView.text = data
        }
    }
}
```

**Lifecycles:**
```
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
// ⚠️ Fragment stays in memory (NO onDestroy/onDetach called)

// On back press:
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
        // ✅ REQUIRED — prevent memory leak
        binding = null
    }
}
```

### Best Practices

**1. Use viewLifecycleOwner for UI:**
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.uiState.collect { state ->
        // Cancelled in onDestroyView()
    }
}
```

**2. Initialize in appropriate callbacks:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Initialize non-UI (ViewModel, data)
    viewModel.loadData()
}

override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    // Initialize UI components
    setupRecyclerView()
}
```

---

## Follow-ups

- What happens to `Fragment` when `Activity` is destroyed due to configuration change?
- How does `ViewModel` survive `Fragment` recreation in BackStack scenarios?
- When should you use `Fragment` lifecycle vs viewLifecycleOwner for coroutines?
- What are the differences between replace(), add(), and show()/hide() `Fragment` transactions?
- How does setRetainInstance(true) affect `Fragment` lifecycle (deprecated)?

## References

- Android Official: [`Fragment` `Lifecycle`](https://developer.android.com/guide/fragments/lifecycle)
- Android Official: [ViewLifecycleOwner](https://developer.android.com/reference/androidx/fragment/app/`Fragment`#getViewLifecycleOwner())

## Related Questions

### Prerequisites / Concepts

- [[c-activity]]
- [[c-fragments]]
- [[c-lifecycle]]


### Prerequisites (Easier)
- `Activity` lifecycle basics — understand `Activity` states first
- `Fragment` basics — what is `Fragment` and why use it

### Related (Same Level)
- [[q-android-runtime-art--android--medium]] — Understanding Android runtime
- [[q-view-composition-strategy-compose--android--medium]] — Modern UI lifecycle

### Advanced (Harder)
- `Fragment` BackStack state management — complex navigation scenarios
- `Fragment` shared element transitions — coordinating lifecycle with animations
