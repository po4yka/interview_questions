---
id: android-428
title: "Почему колбэки Fragment отличаются от колбэков Activity / Why Fragment Callbacks Differ From Activity Callbacks"
aliases: [Fragment Callbacks, Fragment Lifecycle Differences, Колбэки Fragment]
topic: android
subtopics: [activity, fragment, lifecycle]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-fragments, c-lifecycle, q-fragment-vs-activity-lifecycle--android--medium, q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]
created: 2025-10-15
updated: 2025-10-30
tags: [android/activity, android/fragment, android/lifecycle, difficulty/hard, fragments, lifecycle]
---

# Вопрос (RU)

Почему колбэки `Fragment` отличаются от колбэков `Activity`?

# Question (EN)

Why do `Fragment` callbacks differ from `Activity` callbacks?

---

## Ответ (RU)

`Fragment` имеет более сложный lifecycle, чем `Activity`, из-за **фундаментального архитектурного различия**: `Fragment` живет внутри `Activity` и его жизненный цикл зависит от хоста.

### Ключевые Различия

**`Activity`**: автономный компонент с простым жизненным циклом
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**`Fragment`**: вложенный компонент с двумя независимыми циклами
```
Fragment lifecycle: onCreate → ... → onDestroy
View lifecycle:     onCreateView → ... → onDestroyView
Host lifecycle:     onAttach → ... → onDetach
```

### Дополнительные Колбэки `Fragment`

```kotlin
// Присоединение к хосту
onAttach(context: Context)        // Fragment присоединен к Activity
onDetach()                         // Fragment отсоединен от Activity

// Жизненный цикл View (может повторяться)
onCreateView()                     // Создание View
onViewCreated()                    // View готова к использованию
onDestroyView()                    // Уничтожение View (Fragment жив!)

// Жизненный цикл Fragment
onCreate()                         // Fragment создан
onDestroy()                        // Fragment уничтожен
```

### Почему Нужны Дополнительные Колбэки?

**1. `View` может быть уничтожена без уничтожения `Fragment`**

✅ **Правильно**: Разделенные lifecycle
```kotlin
class MyFragment : Fragment() {
    private var _binding: FragmentBinding? = null

    override fun onCreateView(...): View {
        _binding = FragmentBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Освобождаем View, Fragment жив
    }
}
```

**Сценарии**:
- **ViewPager**: `View` уничтожается при свайпе, `Fragment` остается
- **BackStack**: `View` уничтожается при замене, `Fragment` в стеке
- **Configuration change**: `View` пересоздается, `Fragment` сохраняется

**2. `Fragment` зависит от `Activity`**

```kotlin
override fun onAttach(context: Context) {
    super.onAttach(context)
    // Fragment получил доступ к Activity
    val activity = requireActivity()
}

override fun onDetach() {
    super.onDetach()
    // Fragment потерял доступ к Activity
}
```

**`Activity`** не имеет `onAttach/onDetach` - она автономна.

**3. ViewLifecycleOwner отличается от `Fragment` lifecycle**

❌ **Неправильно**: `LiveData` с `Fragment` lifecycle
```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    viewModel.data.observe(this) { // Memory leak!
        binding.textView.text = it
    }
}
```

✅ **Правильно**: `LiveData` с `View` lifecycle
```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    viewModel.data.observe(viewLifecycleOwner) { // Отписка в onDestroyView
        binding.textView.text = it
    }
}
```

### Сравнение Полного `Lifecycle`

**`Activity`**:
```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // View и Activity созданы одновременно
    }

    override fun onDestroy() {
        super.onDestroy()
        // View и Activity уничтожены одновременно
    }
}
```

**`Fragment`**:
```kotlin
class MyFragment : Fragment() {
    // 1. Присоединение к Activity
    override fun onAttach(context: Context) {
        super.onAttach(context)
    }

    // 2. Fragment создан (без View)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Инициализация ViewModel, данных
    }

    // 3. View создана
    override fun onCreateView(...): View {
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    // 4. View готова
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Настройка UI
    }

    // 5. View уничтожена (Fragment жив!)
    override fun onDestroyView() {
        super.onDestroyView()
        // Очистка ссылок на View
    }

    // 6. Fragment уничтожен
    override fun onDestroy() {
        super.onDestroy()
    }

    // 7. Отсоединение от Activity
    override fun onDetach() {
        super.onDetach()
    }
}
```

### Архитектурные Причины

`Fragment` был создан для **модульности UI** и должен:
1. Существовать в разных `Activity` (переиспользование)
2. Управляться динамически (add/remove/replace)
3. Выживать в BackStack без `View` (память)
4. Поддерживать headless режим (без UI)
5. Координироваться с хостом (жизненный цикл `Activity`)

`Activity` - это **автономная точка входа**, ее lifecycle проще потому что:
1. Создается системой (`Intent`)
2. Управляется Task Manager
3. `View` всегда существует вместе с `Activity`
4. Не зависит от другого компонента

---

## Answer (EN)

`Fragment` has a more complex lifecycle than `Activity` due to a **fundamental architectural difference**: `Fragment` lives inside an `Activity` and its lifecycle depends on the host.

### Key Differences

**`Activity`**: autonomous component with simple lifecycle
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**`Fragment`**: nested component with two independent cycles
```
Fragment lifecycle: onCreate → ... → onDestroy
View lifecycle:     onCreateView → ... → onDestroyView
Host lifecycle:     onAttach → ... → onDetach
```

### Additional `Fragment` Callbacks

```kotlin
// Host attachment
onAttach(context: Context)        // Fragment attached to Activity
onDetach()                         // Fragment detached from Activity

// View lifecycle (can repeat)
onCreateView()                     // View creation
onViewCreated()                    // View ready to use
onDestroyView()                    // View destroyed (Fragment alive!)

// Fragment lifecycle
onCreate()                         // Fragment created
onDestroy()                        // Fragment destroyed
```

### Why Additional Callbacks Are Needed

**1. `View` can be destroyed without destroying `Fragment`**

✅ **Correct**: Separated lifecycles
```kotlin
class MyFragment : Fragment() {
    private var _binding: FragmentBinding? = null

    override fun onCreateView(...): View {
        _binding = FragmentBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Release View, Fragment alive
    }
}
```

**Scenarios**:
- **ViewPager**: `View` destroyed on swipe, `Fragment` remains
- **BackStack**: `View` destroyed on replacement, `Fragment` in stack
- **Configuration change**: `View` recreated, `Fragment` preserved

**2. `Fragment` depends on `Activity`**

```kotlin
override fun onAttach(context: Context) {
    super.onAttach(context)
    // Fragment gained access to Activity
    val activity = requireActivity()
}

override fun onDetach() {
    super.onDetach()
    // Fragment lost access to Activity
}
```

**`Activity`** has no `onAttach/onDetach` - it's autonomous.

**3. ViewLifecycleOwner differs from `Fragment` lifecycle**

❌ **Wrong**: `LiveData` with `Fragment` lifecycle
```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    viewModel.data.observe(this) { // Memory leak!
        binding.textView.text = it
    }
}
```

✅ **Correct**: `LiveData` with `View` lifecycle
```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    viewModel.data.observe(viewLifecycleOwner) { // Unsubscribes in onDestroyView
        binding.textView.text = it
    }
}
```

### Full `Lifecycle` Comparison

**`Activity`**:
```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // View and Activity created together
    }

    override fun onDestroy() {
        super.onDestroy()
        // View and Activity destroyed together
    }
}
```

**`Fragment`**:
```kotlin
class MyFragment : Fragment() {
    // 1. Attached to Activity
    override fun onAttach(context: Context) {
        super.onAttach(context)
    }

    // 2. Fragment created (no View)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Initialize ViewModel, data
    }

    // 3. View created
    override fun onCreateView(...): View {
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    // 4. View ready
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Setup UI
    }

    // 5. View destroyed (Fragment alive!)
    override fun onDestroyView() {
        super.onDestroyView()
        // Clean up View references
    }

    // 6. Fragment destroyed
    override fun onDestroy() {
        super.onDestroy()
    }

    // 7. Detached from Activity
    override fun onDetach() {
        super.onDetach()
    }
}
```

### Architectural Reasons

`Fragment` was created for **UI modularity** and must:
1. Exist in different Activities (reusability)
2. Be managed dynamically (add/remove/replace)
3. Survive in BackStack without `View` (memory)
4. Support headless mode (no UI)
5. Coordinate with host (`Activity` lifecycle)

`Activity` is an **autonomous entry point**, its lifecycle is simpler because:
1. Created by system (`Intent`)
2. Managed by Task Manager
3. `View` always exists with `Activity`
4. Independent of other components

### Real-World Scenarios

**ViewPager `Fragment` `Lifecycle`**:
```kotlin
// Page 0 visible
FragmentA: onCreate() → onCreateView() → onViewCreated()

// Swipe to Page 1
FragmentA: onDestroyView() // View destroyed, Fragment alive

// Swipe back to Page 0
FragmentA: onCreateView() → onViewCreated() // Same Fragment, new View
```

**BackStack Navigation**:
```kotlin
// FragmentA visible
FragmentA: onCreate() → onCreateView()

// Replace with FragmentB
FragmentA: onDestroyView() // In BackStack
FragmentB: onCreate() → onCreateView()

// Press Back
FragmentB: onDestroyView() → onDestroy() → onDetach()
FragmentA: onCreateView() // Restored from BackStack
```

**Configuration Change**:
```kotlin
// Before rotation
FragmentA: onCreate() → onCreateView()

// Rotate device
FragmentA: onDestroyView() → onCreateView()
// onCreate() NOT called - Fragment survives
```

### Memory Management Benefits

```kotlin
class OptimizedFragment : Fragment() {
    // Heavy data survives View destruction
    private lateinit var cachedData: List<String>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        cachedData = loadFromDatabase() // Expensive operation
    }

    override fun onCreateView(...): View {
        return createView() // Lightweight
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // View released, cachedData kept
    }
}
```

**Benefit**: When `Fragment` in BackStack:
- `View` destroyed → freed memory
- Data kept → no reload needed
- Fast restoration when user navigates back

---

## Follow-ups

1. Why does `Fragment` have both `onCreate()` and `onCreateView()` when `Activity` only has `onCreate()`?
2. What happens if you observe `LiveData` with `this` instead of `viewLifecycleOwner` in `Fragment`?
3. How does `retainInstance = true` affect `Fragment` lifecycle (deprecated pattern)?
4. What is the lifecycle of a `Fragment` in ViewPager vs BackStack?
5. Why can't `Fragment` access `requireActivity()` after `onDetach()`?

---

## References

- [[c-fragments]] - `Fragment` fundamentals
- [[c-lifecycle]] - Android lifecycle concepts
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - onCreateView separation
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Lifecycle` comparison
- [`Fragment` `Lifecycle` | Android Developers](https://developer.android.com/guide/fragments/lifecycle)
- [ViewLifecycleOwner | Android Developers](https://developer.android.com/reference/androidx/fragment/app/`Fragment`#getViewLifecycleOwner())

---

## Related Questions

### Prerequisites (Easier)
- [[q-fragment-basics--android--easy]] - `Fragment` fundamentals
- [[q-how-does-activity-lifecycle-work--android--medium]] - `Activity` lifecycle
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment`-`Activity` relationship

### Related (Same Level)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - `View` lifecycle separation
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Fragment` purpose
- [[q-fragments-and-activity-relationship--android--hard]] - Architectural patterns

### Advanced (Harder)
- [[q-in-what-cases-might-you-need-to-call-commitallowingstateloss--android--hard]] - `Fragment` state loss
- [[q-shared-element-transitions--android--hard]] - `Fragment` transitions
