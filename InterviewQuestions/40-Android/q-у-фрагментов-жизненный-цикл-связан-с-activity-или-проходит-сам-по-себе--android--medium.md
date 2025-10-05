---
id: 202510031417015
title: "Is Fragment lifecycle connected to Activity or independent"
question_ru: "У фрагментов жизненный цикл связан с Activity или проходит сам по себе?"
question_en: "How does Activity lifecycle work"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - lifecycle
  - fragments
  - android/activity
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/458
---

# Is Fragment lifecycle connected to Activity or independent

## English Answer

Fragment lifecycle is directly connected to the lifecycle of the Activity in which it resides. When an Activity is created, started, or destroyed, its Fragments go through the same lifecycle stages. Fragments can have their own unique lifecycle methods, such as `onCreateView()` or `onDestroyView()`, but they are always synchronized with the Activity's lifecycle. This ensures proper resource management and user interface state.

### Fragment Lifecycle Dependency on Activity

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Activity: onCreate")
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MyFragment())
                .commit()
        }
        // Fragment lifecycle: onAttach → onCreate → onCreateView → onViewCreated
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Activity: onStart")
        // Fragment onStart() will be called
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Activity: onResume")
        // Fragment onResume() will be called
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Activity: onPause")
        // Fragment onPause() will be called FIRST
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Activity: onStop")
        // Fragment onStop() will be called FIRST
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Activity: onDestroy")
        // Fragment: onDestroyView → onDestroy → onDetach
    }
}

class MyFragment : Fragment() {

    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "Fragment: onAttach - attached to Activity")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Fragment: onCreate - Activity.onCreate is running")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Lifecycle", "Fragment: onCreateView")
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "Fragment: onViewCreated")
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Fragment: onStart - Activity.onStart called")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Fragment: onResume - Activity.onResume called")
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Fragment: onPause - BEFORE Activity.onPause")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Fragment: onStop - BEFORE Activity.onStop")
    }

    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Lifecycle", "Fragment: onDestroyView")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Fragment: onDestroy - Activity.onDestroy is running")
    }

    override fun onDetach() {
        super.onDetach()
        Log.d("Lifecycle", "Fragment: onDetach - detached from Activity")
    }
}
```

### Activity-Fragment Lifecycle Coordination

```
App Launch:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Activity.onCreate()
    ↓
Fragment.onAttach(context)
Fragment.onCreate(savedInstanceState)
Fragment.onCreateView(...)
Fragment.onViewCreated(...)
    ↓
Activity.onStart()
    ↓
Fragment.onStart()
    ↓
Activity.onResume()
    ↓
Fragment.onResume()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

App Goes to Background:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fragment.onPause()     ← Fragment pauses FIRST
    ↓
Activity.onPause()
    ↓
Fragment.onStop()      ← Fragment stops FIRST
    ↓
Activity.onStop()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

App Destroyed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fragment.onPause()
Activity.onPause()
Fragment.onStop()
Activity.onStop()
Fragment.onDestroyView()
Fragment.onDestroy()
Fragment.onDetach()
    ↓
Activity.onDestroy()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fragment Cannot Exist Without Activity

```kotlin
// ❌ This is IMPOSSIBLE - Fragment must be attached to Activity
val fragment = MyFragment()
// fragment exists but is NOT functional
// fragment.requireActivity() → throws IllegalStateException

// ✅ Fragment must be added to Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
        // Now fragment is attached and functional
    }
}
```

### Fragment Lifecycle Depends on Transaction Type

```kotlin
class MainActivity : AppCompatActivity() {

    fun replaceFragment() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .commit()

        // Fragment1 lifecycle:
        // onPause() → onStop() → onDestroyView() → onDestroy() → onDetach()

        // Fragment2 lifecycle:
        // onAttach() → onCreate() → onCreateView() → ... → onResume()
    }

    fun addToBackStack() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .addToBackStack(null)  // Add to back stack
            .commit()

        // Fragment1 lifecycle (DIFFERENT - kept in back stack):
        // onPause() → onStop() → onDestroyView()
        // Fragment1 instance is RETAINED (onCreate not called again)

        // Fragment2 lifecycle:
        // onAttach() → onCreate() → onCreateView() → ... → onResume()
    }

    fun popBackStack() {
        supportFragmentManager.popBackStack()

        // Fragment2 lifecycle (removed):
        // onPause() → onStop() → onDestroyView() → onDestroy() → onDetach()

        // Fragment1 lifecycle (restored from back stack):
        // onCreateView() → onViewCreated() → onStart() → onResume()
        // onCreate() is NOT called - instance was retained
    }
}
```

### Configuration Changes

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // On screen rotation:
        // Both Activity AND Fragment are destroyed and recreated
    }
}

class MyFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Fragment recreated along with Activity
        Log.d("Fragment", "Fragment onCreate after rotation")
    }
}

// Modern approach: Use ViewModel to survive configuration changes
class MyFragment : Fragment() {

    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ViewModel survives rotation
        // Same ViewModel instance after rotation
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

### viewLifecycleOwner vs Fragment Lifecycle

```kotlin
class ModernFragment : Fragment() {

    private var _binding: FragmentModernBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MyViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentModernBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ CORRECT - Use viewLifecycleOwner for view observations
        // viewLifecycleOwner lifecycle:
        // - Created: onCreateView()
        // - Destroyed: onDestroyView()
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // ❌ WRONG - Don't use 'this' (Fragment lifecycle)
        // Fragment lifecycle continues after onDestroyView()
        // This can cause memory leaks!
        // viewModel.data.observe(this) { data -> ... }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
        // viewLifecycleOwner is destroyed here
        // All observers on viewLifecycleOwner are automatically removed
    }

    override fun onDestroy() {
        super.onDestroy()
        // Fragment lifecycle ends here
    }
}
```

### Fragment in Back Stack

```kotlin
class Fragment1 : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Fragment1", "onCreate - Fragment instance created")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Fragment1", "onCreateView - View created")
        return inflater.inflate(R.layout.fragment1, container, false)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Fragment1", "onDestroyView - View destroyed but Fragment alive")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Fragment1", "onDestroy - Fragment destroyed")
    }
}

// Navigation scenario
class MainActivity : AppCompatActivity() {

    fun navigateToFragment2() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .addToBackStack("fragment2")
            .commit()

        // Fragment1 lifecycle:
        // onPause() → onStop() → onDestroyView()
        // ⚠️ onCreate() and onDestroy() are NOT called
        // Fragment1 instance is kept alive in back stack
    }

    fun goBack() {
        supportFragmentManager.popBackStack()

        // Fragment1 lifecycle:
        // onCreateView() → onViewCreated() → onStart() → onResume()
        // ⚠️ onCreate() is NOT called - same instance
    }
}
```

### Practical Example: Parent-Child Communication

```kotlin
interface OnDataPassListener {
    fun onDataPassed(data: String)
}

class ChildFragment : Fragment() {

    private var listener: OnDataPassListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)

        // Fragment is attached to Activity
        // This is where you can get Activity reference
        if (context is OnDataPassListener) {
            listener = context
        } else {
            throw RuntimeException("$context must implement OnDataPassListener")
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        button.setOnClickListener {
            // Communicate with Activity
            listener?.onDataPassed("Data from Fragment")
        }
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment is detached from Activity
        // Clean up references to prevent leaks
        listener = null
    }
}

class MainActivity : AppCompatActivity(), OnDataPassListener {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        supportFragmentManager.beginTransaction()
            .add(R.id.container, ChildFragment())
            .commit()
    }

    override fun onDataPassed(data: String) {
        Toast.makeText(this, "Received: $data", Toast.LENGTH_SHORT).show()
    }
}
```

### Key Points

1. **Fragment lifecycle is bound to Activity lifecycle**
2. **Fragments pause/stop BEFORE Activity**
3. **Fragment can outlive its view** (in back stack)
4. **Use viewLifecycleOwner** for view-related observations
5. **Configuration changes** destroy both Activity and Fragment
6. **ViewModel survives** configuration changes

## Russian Answer

Жизненный цикл фрагментов напрямую связан с жизненным циклом Activity, в которой они находятся. Когда Activity создаётся, запускается или уничтожается, её фрагменты проходят те же стадии жизненного цикла.

### Ключевые моменты

1. **Синхронизация**: Фрагменты могут иметь свои уникальные методы жизненного цикла, такие как `onCreateView()` или `onDestroyView()`, но они всегда синхронизированы с жизненным циклом Activity.

2. **Зависимость**: Фрагмент не может существовать без Activity. Когда Activity уничтожается, все её фрагменты также уничтожаются.

3. **Порядок вызова**: При паузе приложения сначала вызывается `onPause()` фрагмента, затем Activity. При возобновлении - наоборот.

4. **Управление ресурсами**: Это гарантирует правильное управление ресурсами и состоянием интерфейса пользователя.

### Жизненный цикл при навигации

- При замене фрагмента без back stack: фрагмент полностью уничтожается
- При добавлении в back stack: вызывается `onDestroyView()`, но фрагмент остаётся в памяти
- При возврате из back stack: вызывается `onCreateView()` заново, но не `onCreate()`
