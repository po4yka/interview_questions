---
title: "How is Fragment lifecycle connected with Activity?"
topic: android
tags:
  - android
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# How is Fragment lifecycle connected with Activity?

# Вопрос (RU)
Как жизненный цикл фрагмента связан с активностью?

## Answer (EN)
Fragment lifecycle is **tightly coupled** with Activity lifecycle. When Activity lifecycle changes, it triggers corresponding Fragment lifecycle callbacks. However, Fragment has **additional lifecycle states** that Activity doesn't have.

### Lifecycle Dependency Diagram

```
Activity State          Fragment State

onCreate()
                    onAttach()
                    onCreate()
                    onCreateView()
                    onViewCreated()
                    onStart()

onStart()           [Fragment onStart already called]

onResume()          onResume()

[Activity running, Fragment active]

onPause()           onPause()

onStop()            onStop()

onDestroy()         onDestroyView()
                    onDestroy()
                    onDetach()
```

### Key Lifecycle Rules

**1. Fragment lifecycle never exceeds Activity lifecycle:**
```kotlin
// Fragment can only be STARTED when Activity is STARTED
// Fragment can only be RESUMED when Activity is RESUMED
```

**2. Fragment callbacks happen AFTER Activity callbacks on the way up:**
```
Activity.onCreate() → Fragment.onCreate()
Activity.onStart() → Fragment.onStart()
Activity.onResume() → Fragment.onResume()
```

**3. Fragment callbacks happen BEFORE Activity callbacks on the way down:**
```
Fragment.onPause() → Activity.onPause()
Fragment.onStop() → Activity.onStop()
Fragment.onDestroy() → Activity.onDestroy()
```

### Complete Lifecycle Flow

```kotlin
// Activity starts → Fragment attaches
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        Log.d("Lifecycle", "Activity.onCreate()")

        // Fragment lifecycle begins here
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Activity.onStart()")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Activity.onResume()")
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Activity.onPause()")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Activity.onStop()")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Activity.onDestroy()")
    }
}

class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "  Fragment.onAttach()")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "  Fragment.onCreate()")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Lifecycle", "  Fragment.onCreateView()")
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "  Fragment.onViewCreated()")
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "  Fragment.onStart()")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "  Fragment.onResume()")
    }

    override fun onPause() {
        Log.d("Lifecycle", "  Fragment.onPause()")
        super.onPause()
    }

    override fun onStop() {
        Log.d("Lifecycle", "  Fragment.onStop()")
        super.onStop()
    }

    override fun onDestroyView() {
        Log.d("Lifecycle", "  Fragment.onDestroyView()")
        super.onDestroyView()
    }

    override fun onDestroy() {
        Log.d("Lifecycle", "  Fragment.onDestroy()")
        super.onDestroy()
    }

    override fun onDetach() {
        Log.d("Lifecycle", "  Fragment.onDetach()")
        super.onDetach()
    }
}
```

**Log Output:**
```
Activity.onCreate()
  Fragment.onAttach()
  Fragment.onCreate()
  Fragment.onCreateView()
  Fragment.onViewCreated()
  Fragment.onStart()
Activity.onStart()
  Fragment.onResume()
Activity.onResume()
[App running]
  Fragment.onPause()
Activity.onPause()
  Fragment.onStop()
Activity.onStop()
  Fragment.onDestroyView()
  Fragment.onDestroy()
  Fragment.onDetach()
Activity.onDestroy()
```

### Fragment-Specific Lifecycle States

Fragment has **view lifecycle** separate from Fragment lifecycle:

```kotlin
class MyFragment : Fragment() {
    // Fragment lifecycle
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fragment created, but no View yet
    }

    // View lifecycle starts
    override fun onCreateView(...): View? {
        // View is being created
        return inflater.inflate(R.layout.fragment, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // View created, safe to access UI
        view.findViewById<TextView>(R.id.textView).text = "Hello"
    }

    // View lifecycle ends
    override fun onDestroyView() {
        super.onDestroyView()
        // View destroyed, but Fragment still alive
        // Must null out view references!
    }

    // Fragment lifecycle ends
    override fun onDestroy() {
        super.onDestroy()
        // Fragment destroyed
    }
}
```

### Configuration Change Behavior

**During rotation (Activity recreated):**

```
Fragment.onPause()
Activity.onPause()
Fragment.onStop()
Activity.onStop()
Fragment.onDestroyView()
Fragment.onDestroy()
Fragment.onDetach()
Activity.onDestroy()

[Activity recreated]

Activity.onCreate()
Fragment.onAttach()
Fragment.onCreate()
Fragment.onCreateView()
Fragment.onViewCreated()
Fragment.onStart()
Activity.onStart()
Fragment.onResume()
Activity.onResume()
```

**Using ViewModel (state preserved):**
```kotlin
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ViewModel survives configuration change
        viewModel.loadData() // Only called once
    }
}
```

### Fragment Transaction Impact

**Adding Fragment:**
```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()

// Lifecycle:
// Fragment.onAttach()
// Fragment.onCreate()
// Fragment.onCreateView()
// Fragment.onViewCreated()
// Fragment.onStart()  (if Activity is STARTED)
// Fragment.onResume() (if Activity is RESUMED)
```

**Replacing Fragment:**
```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, NewFragment())
    .commit()

// Old Fragment:
// Fragment.onPause()
// Fragment.onStop()
// Fragment.onDestroyView()
// Fragment.onDestroy()
// Fragment.onDetach()

// New Fragment:
// Fragment.onAttach()
// Fragment.onCreate()
// Fragment.onCreateView()
// Fragment.onViewCreated()
// Fragment.onStart()
// Fragment.onResume()
```

**Replacing with BackStack:**
```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, NewFragment())
    .addToBackStack(null)
    .commit()

// Old Fragment:
// Fragment.onPause()
// Fragment.onStop()
// Fragment.onDestroyView()
// [Fragment and its state retained in memory]
// [NO onDestroy(), NO onDetach()]

// New Fragment:
// Fragment.onAttach()
// Fragment.onCreate()
// Fragment.onCreateView()
// Fragment.onViewCreated()
// Fragment.onStart()
// Fragment.onResume()
```

### ViewLifecycleOwner

Fragment has **two lifecycle owners:**

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // DON'T observe with Fragment lifecycle
        viewModel.data.observe(this) { data ->
            // This observer stays active even after onDestroyView()!
            textView.text = data // CRASH if textView is null
        }

        // DO observe with viewLifecycleOwner
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Automatically unsubscribed in onDestroyView()
            textView.text = data
        }
    }
}
```

**Lifecycle comparison:**
```
Fragment Lifecycle:        onCreate → onDestroy
View Lifecycle:           onCreateView → onDestroyView

With BackStack:
Fragment:                 [Stays alive]
View:                     [Destroyed and recreated]
```

### Practical Scenarios

#### Scenario 1: Activity Paused (Phone call)

```
Fragment.onPause() → Activity.onPause()
[Phone call ends]
Activity.onResume() → Fragment.onResume()
```

#### Scenario 2: Activity Stopped (Home pressed)

```
Fragment.onPause() → Activity.onPause()
Fragment.onStop() → Activity.onStop()
[User returns]
Activity.onRestart() → Activity.onStart() → Fragment.onStart()
Activity.onResume() → Fragment.onResume()
```

#### Scenario 3: Fragment Replaced with BackStack

```
// User navigates to Fragment B
FragmentA.onPause()
FragmentA.onStop()
FragmentA.onDestroyView()
[FragmentA retained in memory]

FragmentB.onAttach()
FragmentB.onCreate()
FragmentB.onCreateView()
FragmentB.onViewCreated()
FragmentB.onStart()
FragmentB.onResume()

// User presses Back
FragmentB.onPause()
FragmentB.onStop()
FragmentB.onDestroyView()
FragmentB.onDestroy()
FragmentB.onDetach()

FragmentA.onCreateView()  // View recreated
FragmentA.onViewCreated()
FragmentA.onStart()
FragmentA.onResume()
```

### Best Practices

**1. Use viewLifecycleOwner for View-related operations:**
```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)

    viewModel.data.observe(viewLifecycleOwner) { data ->
        // Safe - auto-cleaned in onDestroyView()
    }

    lifecycleScope.launch {
        viewModel.uiState.collect { state ->
            // Cancelled in onDestroy()
        }
    }

    viewLifecycleOwner.lifecycleScope.launch {
        // Cancelled in onDestroyView()
    }
}
```

**2. Clear view references in onDestroyView():**
```kotlin
class MyFragment : Fragment() {
    private var binding: FragmentBinding? = null

    override fun onCreateView(...): View {
        binding = FragmentBinding.inflate(inflater, container, false)
        return binding!!.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        binding = null  // Prevent memory leak!
    }
}
```

**3. Initialize in appropriate callbacks:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Initialize non-UI components (ViewModel, etc.)
    viewModel.loadInitialData()
}

override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    // Initialize UI components
    setupRecyclerView()
    observeViewModel()
}
```

### Summary

**Fragment lifecycle connection to Activity:**
- Fragment lifecycle **depends on** Activity lifecycle
- Fragment **never exceeds** Activity lifecycle state
- Fragment has **additional states** (onAttach, onCreateView, onViewCreated, onDestroyView, onDetach)
- Fragment callbacks occur **after** Activity callbacks (up) and **before** Activity callbacks (down)
- Fragment has **separate view lifecycle** (viewLifecycleOwner)
- Use **viewLifecycleOwner** for view-related observations
- Always **null view references** in onDestroyView()

**English Summary**: Fragment lifecycle is synchronized with Activity lifecycle but has additional states. Fragment callbacks occur after Activity callbacks when starting up (onCreate → onStart → onResume) and before Activity callbacks when shutting down (onPause → onStop → onDestroy). Fragment has separate view lifecycle (onCreateView → onDestroyView) independent of Fragment lifecycle. Use viewLifecycleOwner for view-related LiveData/Flow observations to prevent memory leaks. Fragment lifecycle never exceeds Activity lifecycle - if Activity is PAUSED, Fragment is also PAUSED.

## Ответ (RU)
Жизненный цикл фрагмента **тесно связан** с жизненным циклом активности. Когда изменяется жизненный цикл активности, это вызывает соответствующие обратные вызовы жизненного цикла фрагмента. Однако у фрагмента есть **дополнительные состояния жизненного цикла**, которых нет у активности.

### Ключевые правила жизненного цикла

**1. Жизненный цикл фрагмента никогда не превышает жизненный цикл активности:**
```kotlin
// Фрагмент может быть в состоянии STARTED, только когда активность в состоянии STARTED
// Фрагмент может быть в состоянии RESUMED, только когда активность в состоянии RESUMED
```

**2. Обратные вызовы фрагмента происходят ПОСЛЕ обратных вызовов активности при запуске:**
```
Activity.onCreate() → Fragment.onCreate()
Activity.onStart() → Fragment.onStart()
Activity.onResume() → Fragment.onResume()
```

**3. Обратные вызовы фрагмента происходят ПЕРЕД обратными вызовами активности при остановке:**
```
Fragment.onPause() → Activity.onPause()
Fragment.onStop() → Activity.onStop()
Fragment.onDestroy() → Activity.onDestroy()
```

### Раздельный жизненный цикл View

У фрагмента есть **отдельный жизненный цикл для его View**:

```kotlin
// Жизненный цикл фрагмента:        onCreate → onDestroy
// Жизненный цикл View:           onCreateView → onDestroyView
```

### ViewLifecycleOwner

У фрагмента **два владельца жизненного цикла:**

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // НЕПРАВИЛЬНО: наблюдать с жизненным циклом фрагмента
        viewModel.data.observe(this) { /* ... */ }

        // ПРАВИЛЬНО: наблюдать с viewLifecycleOwner
        viewModel.data.observe(viewLifecycleOwner) { /* ... */ }
    }
}
```

### Лучшие практики

**1. Используйте `viewLifecycleOwner` для операций, связанных с View.**
**2. Обнуляйте ссылки на View в `onDestroyView()`.**
**3. Инициализируйте в соответствующих обратных вызовах.**

---

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, Activity
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, Activity
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Lifecycle, Activity
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle, Activity
