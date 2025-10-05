---
id: 202510031417020
title: "Why Fragment callbacks differ from Activity callbacks"
question_ru: "Почему колбеки фрагмента отличаются от колбеков Activity ?"
question_en: "Почему колбеки фрагмента отличаются от колбеков Activity ?"
topic: android
moc: moc-android
status: draft
difficulty: hard
tags:
  - lifecycle
  - fragments
  - android/activity
  - android/fragments
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/538
---

# Why Fragment callbacks differ from Activity callbacks

## English Answer

Fragment callbacks differ from Activity callbacks because Fragments manage separate parts of the user interface, can be dynamically added or removed, and have their own specific methods (onCreateView(), onAttach(), etc.), while Activity manages the lifecycle of the entire screen.

### Key Differences

#### 1. Lifecycle Stages

**Activity**: Basic lifecycle stages
```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Activity: onCreate")
        // Main lifecycle methods:
        // onCreate → onStart → onResume → onPause → onStop → onDestroy
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Activity: onStart")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Activity: onResume")
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Activity: onPause")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Activity: onStop")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Activity: onDestroy")
    }
}
```

**Fragment**: Additional lifecycle stages
```kotlin
class MyFragment : Fragment() {

    // Additional Fragment-specific callbacks
    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "Fragment: onAttach - attached to Activity")
        // Fragment is attached to its host Activity
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Fragment: onCreate")
        // Initialize non-UI components
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Lifecycle", "Fragment: onCreateView")
        // Create and return the view hierarchy
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "Fragment: onViewCreated")
        // Initialize UI components
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        Log.d("Lifecycle", "Fragment: onActivityCreated [DEPRECATED]")
        // Activity onCreate() completed
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Fragment: onStart")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Fragment: onResume")
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Fragment: onPause")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Fragment: onStop")
    }

    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Lifecycle", "Fragment: onDestroyView")
        // View hierarchy is destroyed, Fragment instance may remain
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Fragment: onDestroy")
        // Fragment is being destroyed
    }

    override fun onDetach() {
        super.onDetach()
        Log.d("Lifecycle", "Fragment: onDetach")
        // Fragment is detached from Activity
    }
}
```

#### 2. Nested Nature

**Activity**: Independent unit
```kotlin
class MainActivity : AppCompatActivity() {
    // Activity is an independent entry point
    // Declared in AndroidManifest.xml
    // Can exist on its own
}
```

**Fragment**: Modular part within Activity
```kotlin
class MyFragment : Fragment() {
    // Fragment MUST be hosted by an Activity or another Fragment
    // Cannot exist independently
    // Requires host for lifecycle management
}

// Fragment requires host
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Fragment needs to be added to Activity
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    }
}
```

#### 3. View Management

**Activity**: Single view hierarchy
```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Set content view ONCE
        setContentView(R.layout.activity_main)

        // View hierarchy created in onCreate
        // Destroyed in onDestroy
    }

    // No separate view lifecycle callbacks
}
```

**Fragment**: Separate view lifecycle
```kotlin
class MyFragment : Fragment() {

    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fragment instance created
        // NO VIEW YET
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // CREATE VIEW
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // VIEW EXISTS - can initialize UI
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // DESTROY VIEW - but Fragment instance remains!
        _binding = null
    }

    override fun onDestroy() {
        super.onDestroy()
        // Fragment instance destroyed
    }
}
```

### Complete Lifecycle Comparison

```
Activity Lifecycle:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
onCreate()
    ↓
onStart()
    ↓
onResume()
    ↓
[Running]
    ↓
onPause()
    ↓
onStop()
    ↓
onDestroy()

Fragment Lifecycle:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
onAttach(context)      ← Fragment-specific
    ↓
onCreate()
    ↓
onCreateView()         ← Fragment-specific
    ↓
onViewCreated()        ← Fragment-specific
    ↓
onActivityCreated()    ← Fragment-specific [DEPRECATED]
    ↓
onStart()
    ↓
onResume()
    ↓
[Running]
    ↓
onPause()
    ↓
onStop()
    ↓
onDestroyView()        ← Fragment-specific
    ↓
onDestroy()
    ↓
onDetach()             ← Fragment-specific
```

### Fragment-Specific Use Cases

#### 1. Attachment to Host

```kotlin
interface OnDataPassListener {
    fun onDataPassed(data: String)
}

class MyFragment : Fragment() {

    private var listener: OnDataPassListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Access to host Activity
        // Only Fragments have this callback
        if (context is OnDataPassListener) {
            listener = context
        } else {
            throw RuntimeException("$context must implement OnDataPassListener")
        }
    }

    override fun onDetach() {
        super.onDetach()
        // Clean up references to prevent leaks
        listener = null
    }

    fun sendDataToActivity(data: String) {
        listener?.onDataPassed(data)
    }
}

class MainActivity : AppCompatActivity(), OnDataPassListener {
    override fun onDataPassed(data: String) {
        Log.d("Activity", "Received: $data")
    }
}
```

#### 2. View Recreation Without Instance Recreation

```kotlin
class MyFragment : Fragment() {

    private val viewModel: MyViewModel by viewModels()
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Called ONCE when Fragment is created
        Log.d("Fragment", "onCreate - hashCode: ${this.hashCode()}")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Can be called MULTIPLE times
        // (e.g., when returning from back stack)
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        Log.d("Fragment", "onCreateView - Fragment hashCode: ${this.hashCode()}")
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // View destroyed, but Fragment instance ALIVE
        _binding = null
        Log.d("Fragment", "onDestroyView - Fragment still alive: ${this.hashCode()}")
    }
}

// Scenario:
// 1. Fragment added to back stack
// 2. onDestroyView() called
// 3. User presses back
// 4. onCreateView() called again
// 5. onCreate() NOT called - same Fragment instance!
```

#### 3. Multiple Fragments in One Activity

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Activity manages multiple Fragments
        supportFragmentManager.beginTransaction()
            .add(R.id.container_top, Fragment1())
            .add(R.id.container_middle, Fragment2())
            .add(R.id.container_bottom, Fragment3())
            .commit()

        // All Fragments have synchronized lifecycle with Activity
        // But each has its own view lifecycle
    }
}
```

### Lifecycle Method Comparison Table

| Callback | Activity | Fragment | Purpose |
|----------|----------|----------|---------|
| **onAttach()** | ❌ No | ✅ Yes | Attach to host |
| **onCreate()** | ✅ Yes | ✅ Yes | Initialize component |
| **onCreateView()** | ❌ No | ✅ Yes | Create view hierarchy |
| **onViewCreated()** | ❌ No | ✅ Yes | View ready for initialization |
| **onActivityCreated()** | ❌ No | ⚠️ Deprecated | Activity onCreate complete |
| **onStart()** | ✅ Yes | ✅ Yes | Becoming visible |
| **onResume()** | ✅ Yes | ✅ Yes | Interactive |
| **onPause()** | ✅ Yes | ✅ Yes | Losing focus |
| **onStop()** | ✅ Yes | ✅ Yes | No longer visible |
| **onDestroyView()** | ❌ No | ✅ Yes | View destroyed |
| **onDestroy()** | ✅ Yes | ✅ Yes | Component destroyed |
| **onDetach()** | ❌ No | ✅ Yes | Detach from host |

### Practical Example: Why Fragments Need Different Callbacks

```kotlin
// Scenario: Navigation with back stack

class ListFragment : Fragment() {

    private val viewModel: ListViewModel by viewModels()
    private var _binding: FragmentListBinding? = null
    private val binding get() = _binding!!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Load data ONCE
        viewModel.loadData()
        Log.d("ListFragment", "onCreate - Data loaded")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Create view (can happen multiple times)
        _binding = FragmentListBinding.inflate(inflater, container, false)
        Log.d("ListFragment", "onCreateView - View created")
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Setup RecyclerView every time view is created
        binding.recyclerView.adapter = ListAdapter()

        // Observe data (data already loaded in onCreate)
        viewModel.data.observe(viewLifecycleOwner) { data ->
            (binding.recyclerView.adapter as ListAdapter).submitList(data)
        }

        binding.itemView.setOnClickListener {
            navigateToDetail()
        }

        Log.d("ListFragment", "onViewCreated - UI initialized")
    }

    private fun navigateToDetail() {
        parentFragmentManager.beginTransaction()
            .replace(R.id.container, DetailFragment())
            .addToBackStack(null)
            .commit()

        // ListFragment lifecycle:
        // onPause() → onStop() → onDestroyView()
        // Fragment instance RETAINED
        // Data in ViewModel RETAINED
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
        Log.d("ListFragment", "onDestroyView - View destroyed, Fragment alive")
        // View destroyed, but:
        // - Fragment instance still exists
        // - ViewModel still exists with data
        // - onCreate won't be called again when returning
    }
}

// User presses back:
// ListFragment lifecycle:
// onCreateView() → onViewCreated() → onStart() → onResume()
// onCreate() NOT called - data still in ViewModel!
```

### Why This Design?

1. **Modularity**: Fragments are modular UI components within Activity
2. **Reusability**: Can be reused across different Activities
3. **Dynamic UI**: Can be added/removed/replaced at runtime
4. **View lifecycle**: View can be recreated without recreating Fragment
5. **Resource efficiency**: Fragment instance can be retained in back stack
6. **Host communication**: onAttach/onDetach for Activity communication

## Russian Answer

Колбеки фрагмента отличаются от колбеков Activity, так как фрагменты управляют отдельными частями пользовательского интерфейса, могут динамически добавляться или удаляться, и имеют свои специфичные методы (onCreateView(), onAttach(), и т.д.), в то время как Activity управляет жизненным циклом всего экрана.

### Ключевые отличия

**Жизненный цикл**:
- **Activity**: Основные стадии - onCreate(), onStart(), onResume(), onPause(), onStop(), onDestroy()
- **Fragment**: Дополнительные стадии - onAttach(), onCreateView(), onViewCreated(), onDestroyView(), onDetach()

**Вложенность**:
- **Activity**: Независимая единица интерфейса, объявляется в манифесте
- **Fragment**: Модульная часть внутри Activity, требует хоста для существования

**Управление представлениями**:
- **Activity**: Управляет своим представлением через setContentView()
- **Fragment**: Управляет своим представлением внутри Activity через onCreateView()

**Уникальные возможности фрагментов**:
- Могут существовать без view (в back stack)
- View может быть пересоздано без пересоздания фрагмента
- Имеют отдельный viewLifecycleOwner для предотвращения утечек
- Могут взаимодействовать с Activity через onAttach/onDetach

Эти отличия позволяют фрагментам быть более гибкими и модульными компонентами, подходящими для создания сложных, динамических пользовательских интерфейсов.
