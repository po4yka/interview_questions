---
id: 202510031417008
title: "How is Fragment lifecycle connected with Activity"
question_ru: "Как связан жизненный цикл фрагментов с Activity ?"
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
source: https://t.me/easy_kotlin/104
---

# How is Fragment lifecycle connected with Activity

## English Answer

Fragment lifecycle is closely tied to the lifecycle of its parent Activity, as Fragments are embedded within Activities and depend on them. This means that changes in the Activity's lifecycle directly affect the lifecycle of embedded Fragments.

### Fragment-Activity Lifecycle Connection

When an Activity is created (onCreate() is called), it can start a Fragment transaction to add, remove, or replace Fragments in its container. Each Fragment goes through its own lifecycle stages (such as onAttach(), onCreate(), onCreateView(), onActivityCreated(), onStart(), onResume(), etc.), which are synchronized with the Activity's lifecycle.

### Synchronized Lifecycle Events

```kotlin
// Activity lifecycle
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // Activity created

        // Add fragment
        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, MyFragment())
                .commit()
        }
        // Fragment lifecycle: onAttach() → onCreate() → onCreateView() → onViewCreated()
    }

    override fun onStart() {
        super.onStart()
        // Activity starting
        // Fragment onStart() will be called
    }

    override fun onResume() {
        super.onResume()
        // Activity resumed
        // Fragment onResume() will be called
    }

    override fun onPause() {
        super.onPause()
        // Activity pausing
        // Fragment onPause() will be called
    }

    override fun onStop() {
        super.onStop()
        // Activity stopping
        // Fragment onStop() will be called
    }

    override fun onDestroy() {
        super.onDestroy()
        // Activity destroying
        // Fragment lifecycle: onDestroyView() → onDestroy() → onDetach()
    }
}
```

### Fragment Lifecycle Within Activity

```kotlin
class MyFragment : Fragment() {

    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "Fragment: onAttach")
        // Fragment attached to Activity
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Fragment: onCreate")
        // Fragment created (Activity.onCreate is running)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Lifecycle", "Fragment: onCreateView")
        // Create Fragment's view
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "Fragment: onViewCreated")
        // View is ready, can initialize UI
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        Log.d("Lifecycle", "Fragment: onActivityCreated")
        // Activity onCreate() completed
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Fragment: onStart")
        // Fragment becoming visible (Activity.onStart called)
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Fragment: onResume")
        // Fragment interactive (Activity.onResume called)
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Fragment: onPause")
        // Fragment losing focus (Activity.onPause called)
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Fragment: onStop")
        // Fragment no longer visible (Activity.onStop called)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Lifecycle", "Fragment: onDestroyView")
        // Fragment's view being destroyed
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Fragment: onDestroy")
        // Fragment being destroyed (Activity.onDestroy called)
    }

    override fun onDetach() {
        super.onDetach()
        Log.d("Lifecycle", "Fragment: onDetach")
        // Fragment detached from Activity
    }
}
```

### Activity-Fragment Lifecycle Coordination

```
Activity onCreate()
    ↓
Fragment onAttach()
Fragment onCreate()
Fragment onCreateView()
Fragment onViewCreated()
Fragment onActivityCreated()  [DEPRECATED - use onViewCreated]
    ↓
Activity onStart()
    ↓
Fragment onStart()
    ↓
Activity onResume()
    ↓
Fragment onResume()
    ↓
[Activity and Fragment are running]
    ↓
Activity onPause()
    ↓
Fragment onPause()
    ↓
Activity onStop()
    ↓
Fragment onStop()
    ↓
Activity onDestroy()
    ↓
Fragment onDestroyView()
Fragment onDestroy()
Fragment onDetach()
```

### Fragment Transactions During Activity Lifecycle

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ SAFE - Activity is being created
        supportFragmentManager.beginTransaction()
            .add(R.id.container, Fragment1())
            .commit()
    }

    override fun onStart() {
        super.onStart()

        // ✅ SAFE - Can add fragments
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .commit()
    }

    override fun onResume() {
        super.onResume()

        // ✅ SAFE - Can modify fragments
        supportFragmentManager.beginTransaction()
            .add(R.id.container, Fragment3())
            .addToBackStack(null)
            .commit()
    }

    override fun onPause() {
        super.onPause()

        // ⚠️ RISKY - Avoid fragment transactions
        // Activity is losing focus
    }

    override fun onStop() {
        super.onStop()

        // ❌ AVOID - Activity is stopping
        // Fragment transactions may cause IllegalStateException
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // ❌ NEVER do fragment transactions here
        // Will cause IllegalStateException: Can not perform this action after onSaveInstanceState
    }
}
```

### Fragment Survives Configuration Changes

```kotlin
class RetainedFragment : Fragment() {

    private lateinit var heavyData: HeavyData

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Retain fragment across configuration changes
        retainInstance = true  // DEPRECATED in newer APIs

        // Modern approach: Use ViewModel instead
        heavyData = loadHeavyData()
    }

    override fun onDestroy() {
        super.onDestroy()

        // With retainInstance = true, onDestroy is NOT called
        // during configuration changes (only when Activity truly finishes)
    }
}

// Modern approach with ViewModel (recommended)
class MyFragment : Fragment() {

    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ViewModel survives configuration changes automatically
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

### ViewLifecycleOwner in Fragments

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

        // ✅ Use viewLifecycleOwner for view-related observations
        // This lifecycle matches the Fragment's view lifecycle
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // Fragment lifecycle continues after onDestroyView
        // But viewLifecycleOwner is destroyed, preventing leaks
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Clean up binding reference
        _binding = null
        // Observers on viewLifecycleOwner are automatically removed
    }
}
```

### BackStack and Fragment Lifecycle

```kotlin
class MainActivity : AppCompatActivity() {

    private fun navigateToFragment2() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .addToBackStack("fragment2")
            .commit()

        // Fragment1: onPause() → onStop() → onDestroyView()
        // Fragment1 instance is retained in back stack
        // Fragment2: onAttach() → ... → onResume()
    }

    private fun popBackStack() {
        supportFragmentManager.popBackStack()

        // Fragment2: onPause() → onStop() → onDestroyView() → onDestroy() → onDetach()
        // Fragment1: onCreateView() → onViewCreated() → onStart() → onResume()
    }
}

class Fragment1 : Fragment() {
    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Fragment1", "View destroyed but Fragment instance retained")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Fragment1", "View recreated when returning from back stack")
        return inflater.inflate(R.layout.fragment1, container, false)
    }
}
```

### Key Takeaways

1. **Fragment lifecycle depends on Activity lifecycle** - When Activity stops, all Fragments stop
2. **Fragments can outlive their views** - onDestroyView() doesn't mean Fragment is destroyed
3. **Use viewLifecycleOwner** for view-related observations to avoid leaks
4. **Fragment transactions** should generally happen before onSaveInstanceState()
5. **ViewModel survives configuration changes** - Better than retainInstance for state preservation

## Russian Answer

Жизненный цикл фрагментов тесно связан с жизненным циклом их родительской активити, поскольку фрагменты встраиваются в активити и зависят от неё. Это значит, что изменения в жизненном цикле активити напрямую влияют на жизненный цикл вложенных в неё фрагментов.

Когда активити создаётся (вызывается onCreate()), она может начать транзакцию фрагментов для добавления, удаления или замены фрагментов в своём контейнере. Каждый фрагмент проходит через свои собственные этапы жизненного цикла (например, onAttach(), onCreate(), onCreateView(), onActivityCreated(), onStart(), onResume(), и так далее), которые синхронизированы с жизненным циклом активити.

Например, когда активити переходит в состояние onPause() (например, при открытии другой активити), все фрагменты внутри неё также переходят в onPause(). Аналогично, когда активити уничтожается (onDestroy()), все её фрагменты также проходят через onDestroy() и onDetach().

Это позволяет фрагментам правильно управлять своими ресурсами и состоянием в соответствии с текущим состоянием родительской активити.
