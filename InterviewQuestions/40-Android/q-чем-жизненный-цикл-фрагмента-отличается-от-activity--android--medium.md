---
id: 202510031417021
title: "How does Fragment lifecycle differ from Activity (v2)"
question_ru: "Чем жизненный цикл фрагмента отличается от Activity?"
question_en: "How does Fragment lifecycle differ from Activity"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - lifecycle
  - fragment
  - activity
  - android/activity
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/546
---

# How does Fragment lifecycle differ from Activity

## English Answer

Fragments exist inside Activities and depend on their lifecycle. Fragments have their own stages, such as onAttach, onCreateView, and onDetach, which are absent in Activities. Activity manages all Fragments, providing context and capabilities for interaction between them.

### Key Differences

#### 1. Dependency on Activity

Fragments cannot exist without a host Activity:

```kotlin
// Fragment MUST be hosted by Activity
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Fragment needs Activity as host
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    }
}

class MyFragment : Fragment() {
    // Fragment depends on Activity lifecycle
    // Cannot exist independently
}
```

#### 2. Additional Lifecycle Stages

**Activity lifecycle**:
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**Fragment lifecycle** (has additional stages):
```
onAttach → onCreate → onCreateView → onViewCreated → onStart → onResume
    ↓
onPause → onStop → onDestroyView → onDestroy → onDetach
```

```kotlin
class MyFragment : Fragment() {

    // ✅ Fragment-specific callbacks

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment attached to Activity
        // Access to Activity context
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Create Fragment's view hierarchy
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // View is created and ready
        // Initialize UI components here
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // View is destroyed
        // But Fragment instance may still exist
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment detached from Activity
    }
}
```

#### 3. View Lifecycle Separation

Fragments have a separate view lifecycle that can outlive the view itself:

```kotlin
class MyFragment : Fragment() {

    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fragment instance created
        Log.d("Fragment", "Instance created")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // View created
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        Log.d("Fragment", "View created")
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // View destroyed, but Fragment instance STILL EXISTS
        _binding = null
        Log.d("Fragment", "View destroyed, Fragment alive")
    }

    override fun onDestroy() {
        super.onDestroy()
        // Fragment instance destroyed
        Log.d("Fragment", "Instance destroyed")
    }
}
```

#### 4. Back Stack Behavior

Fragments can be retained in the back stack:

```kotlin
class MainActivity : AppCompatActivity() {

    fun navigateToFragment2() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .addToBackStack("fragment2")  // Add to back stack
            .commit()

        // Fragment1 lifecycle:
        // onPause() → onStop() → onDestroyView()
        // ⚠️ onDestroy() and onDetach() NOT called
        // Fragment1 instance is RETAINED
    }

    fun goBack() {
        supportFragmentManager.popBackStack()

        // Fragment1 lifecycle:
        // onCreateView() → onViewCreated() → onStart() → onResume()
        // ⚠️ onAttach() and onCreate() NOT called
        // Same Fragment instance is reused
    }
}
```

### Synchronized Lifecycle Events

Fragments and Activity lifecycles are synchronized:

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Activity onCreate")

        // Fragment will be created
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Activity onStart")
        // Fragment onStart() will be called
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Activity onResume")
        // Fragment onResume() will be called
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Activity onPause")
        // Fragment onPause() called BEFORE this
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Activity onStop")
        // Fragment onStop() called BEFORE this
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Activity onDestroy")
        // Fragments destroyed before Activity
    }
}
```

### viewLifecycleOwner

Fragments have viewLifecycleOwner for safe view observations:

```kotlin
class MyFragment : Fragment() {

    private val viewModel: MyViewModel by viewModels()
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ CORRECT - Use viewLifecycleOwner
        // Automatically cleaned up when view is destroyed
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // ❌ WRONG - Using Fragment lifecycle owner
        // Can cause memory leaks!
        // viewModel.data.observe(this) { ... }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
        // viewLifecycleOwner is destroyed
        // All observers automatically removed
    }
}
```

### Complete Lifecycle Flow

```kotlin
// App launch with Fragment
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    }
}

class MyFragment : Fragment() {

    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "1. Fragment onAttach")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "2. Fragment onCreate")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Lifecycle", "3. Fragment onCreateView")
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "4. Fragment onViewCreated")
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "5. Fragment onStart")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "6. Fragment onResume - Running")
    }

    // User presses Home button
    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "7. Fragment onPause")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "8. Fragment onStop")
    }

    // Activity finished
    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Lifecycle", "9. Fragment onDestroyView")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "10. Fragment onDestroy")
    }

    override fun onDetach() {
        super.onDetach()
        Log.d("Lifecycle", "11. Fragment onDetach")
    }
}
```

### Fragment Management by Activity

Activity provides context and manages all Fragments:

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Activity manages multiple Fragments
        supportFragmentManager.beginTransaction()
            .add(R.id.container_top, HeaderFragment())
            .add(R.id.container_middle, ContentFragment())
            .add(R.id.container_bottom, FooterFragment())
            .commit()

        // All Fragments share same Activity context
        // All Fragments' lifecycles synchronized with Activity
    }

    // Fragment interaction through Activity
    fun onFragmentInteraction(data: String) {
        // Activity coordinates between Fragments
        val contentFragment = supportFragmentManager
            .findFragmentById(R.id.container_middle) as? ContentFragment
        contentFragment?.updateContent(data)
    }
}
```

### Summary Table

| Aspect | Activity | Fragment |
|--------|----------|----------|
| **Existence** | Independent | Depends on Activity |
| **Lifecycle methods** | 6 basic methods | 11+ methods |
| **View lifecycle** | Same as Activity | Separate viewLifecycleOwner |
| **Back stack** | System managed | Can be retained |
| **Context** | Self-contained | Provided by Activity |
| **Multiple instances** | One per screen | Multiple per Activity |
| **Attachment** | To system | To Activity |

### Best Practices

1. **Use viewLifecycleOwner** for observing LiveData/Flow in Fragments
2. **Clean up view references** in onDestroyView()
3. **Initialize non-UI** in onCreate()
4. **Initialize UI** in onViewCreated()
5. **Communicate through Activity** or shared ViewModel

## Russian Answer

Фрагменты существуют внутри Activity и зависят от её жизненного цикла. У фрагментов есть свои стадии, такие как `onAttach`, `onCreateView` и `onDetach`, которые отсутствуют у Activity. Activity управляет всеми фрагментами, предоставляя контекст и возможности для взаимодействия между ними.

### Основные отличия

1. **Зависимость**: Фрагмент не может существовать без Activity-хоста

2. **Дополнительные стадии**: Фрагмент имеет уникальные методы жизненного цикла:
   - `onAttach()` - присоединение к Activity
   - `onCreateView()` - создание view
   - `onViewCreated()` - view создано и готово
   - `onDestroyView()` - уничтожение view (фрагмент может остаться)
   - `onDetach()` - отсоединение от Activity

3. **Отдельный жизненный цикл view**: View фрагмента может быть уничтожено и пересоздано, пока экземпляр фрагмента остается живым (в back stack)

4. **viewLifecycleOwner**: Фрагменты имеют отдельный lifecycle owner для view, что предотвращает утечки памяти

5. **Back stack**: Фрагменты могут быть сохранены в back stack, где их view уничтожается, но экземпляр остается

6. **Синхронизация**: Методы onStart(), onResume(), onPause(), onStop() фрагмента синхронизированы с Activity, но фрагмент имеет дополнительные этапы до и после них

Эта архитектура позволяет фрагментам быть модульными, переиспользуемыми компонентами UI, которые могут динамически добавляться, удаляться и заменяться во время работы приложения.
