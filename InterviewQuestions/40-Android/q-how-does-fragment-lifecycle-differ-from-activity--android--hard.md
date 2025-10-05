---
id: 202510031417002
title: "How does Fragment lifecycle differ from Activity"
question_ru: "Чем жизненный цикл фрагмента отличается от Activity"
question_en: "How does Fragment lifecycle differ from Activity"
topic: android
moc: moc-android
status: draft
difficulty: hard
tags:
  - lifecycle
  - fragment
  - android/activity
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/17
---

# How does Fragment lifecycle differ from Activity

## English Answer

Fragment lifecycle is similar to Activity lifecycle but has additional states and events reflecting its unique ability to be added, removed, replaced, or restored within an Activity. Fragments provide greater flexibility in managing user interfaces, especially on larger screens or for implementing multi-panel interfaces, and their lifecycle allows fine-grained control over these capabilities.

### Key Differences

#### 1. Nested Within Activity
- **Fragments exist inside Activities** and depend on their lifecycle
- Fragments can be added, removed, and replaced during Activity runtime
- Fragments have additional lifecycle events:
  - **`onAttach()`**: When Fragment is associated with Activity
  - **`onDetach()`**: When Fragment is detached from Activity

```kotlin
override fun onAttach(context: Context) {
    super.onAttach(context)
    // Fragment is now attached to Activity
}

override fun onDetach() {
    super.onDetach()
    // Fragment is being detached from Activity
}
```

#### 2. View Management
Fragments have an additional lifecycle for managing their view:
- **`onCreateView()`**: Creates the Fragment's view
- **`onViewCreated()`**: Called after view is created
- **`onDestroyView()`**: When view is removed from view hierarchy

This reflects the Fragment's ability to be removed from UI and then re-added without destroying the Fragment itself.

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View? {
    return inflater.inflate(R.layout.fragment_example, container, false)
}

override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    // Initialize UI components
}

override fun onDestroyView() {
    super.onDestroyView()
    // Clean up view-related resources
}
```

#### 3. More Granular State Control
Fragments provide more detailed state management:
- Saving and restoring local Fragment state through `onSaveInstanceState()`
- Back stack support allows returning to previous states
- Multiple Fragments can exist simultaneously in one Activity

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putString("data_key", myData)
}
```

#### 4. Interaction with Other Fragments
- Fragments can interact with each other through parent Activity
- Allows creating complex UIs with dynamic component interaction
- Shared ViewModels enable communication between Fragments

```kotlin
// Shared ViewModel between Fragments
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun select(item: Item) {
        _selectedItem.value = item
    }
}

// In Fragment
val viewModel: SharedViewModel by activityViewModels()
```

#### 5. Reusability and Multiple Embedding
- Unlike Activity (which represents a separate screen), Fragments are designed to be:
  - Reusable across different Activities
  - Embeddable in other Fragments
  - Modular UI components with reusable logic

### Complete Fragment Lifecycle Diagram

```
onAttach()
    ↓
onCreate()
    ↓
onCreateView()
    ↓
onViewCreated()
    ↓
onStart()
    ↓
onResume() → [Running]
    ↓
onPause()
    ↓
onStop()
    ↓
onDestroyView()
    ↓
onDestroy()
    ↓
onDetach()
```

### Fragment vs Activity Lifecycle Comparison

| Event | Activity | Fragment | Notes |
|-------|----------|----------|-------|
| Attachment | N/A | `onAttach()` | Fragment attaches to Activity |
| Creation | `onCreate()` | `onCreate()` | Both initialize non-UI components |
| View Creation | `onCreate()` | `onCreateView()` | Fragments separate view creation |
| View Ready | N/A | `onViewCreated()` | Fragment-specific |
| Visible | `onStart()` | `onStart()` | Both become visible |
| Interactive | `onResume()` | `onResume()` | Both start user interaction |
| Paused | `onPause()` | `onPause()` | Both lose focus |
| Stopped | `onStop()` | `onStop()` | Both no longer visible |
| View Destroyed | N/A | `onDestroyView()` | Fragment view can be recreated |
| Destroyed | `onDestroy()` | `onDestroy()` | Both release resources |
| Detachment | N/A | `onDetach()` | Fragment detaches from Activity |

### Practical Example

```kotlin
class ExampleFragment : Fragment() {

    private var _binding: FragmentExampleBinding? = null
    private val binding get() = _binding!!

    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "Fragment attached to Activity")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Fragment onCreate")
        // Initialize non-UI components
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentExampleBinding.inflate(inflater, container, false)
        Log.d("Lifecycle", "Fragment onCreateView")
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "Fragment onViewCreated")
        // Initialize UI components
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Fragment visible")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Fragment interactive")
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Fragment paused")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Fragment stopped")
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
        Log.d("Lifecycle", "Fragment view destroyed")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Fragment destroyed")
    }

    override fun onDetach() {
        super.onDetach()
        Log.d("Lifecycle", "Fragment detached")
    }
}
```

## Russian Answer

Жизненный цикл фрагмента похож на жизненный цикл активити, но имеет дополнительные состояния и события, отражающие его уникальную способность быть добавленным, удалённым, заменённым или восстановленным в рамках активити. Фрагменты предоставляют большую гибкость в управлении пользовательским интерфейсом, особенно на больших экранах или для реализации многопанельных интерфейсов, и их жизненный цикл позволяет тонко управлять этими возможностями.

### Основные отличия

**Вложенность в активити**: Фрагменты существуют внутри активити и зависят от её жизненного цикла. Это означает, что фрагменты могут быть добавлены, удалены и заменены во время выполнения активити. В результате фрагменты имеют дополнительные события жизненного цикла, такие как `onAttach`, когда фрагмент связывается с активити, и `onDetach`, когда фрагмент отсоединяется от активити.

**Управление представлением**: Фрагменты имеют дополнительный жизненный цикл для управления своим представлением (view), включая события `onCreateView` для создания представления фрагмента и `onDestroyView`, когда представление удаляется из иерархии представлений. Это отражает возможность фрагмента быть удалённым из пользовательского интерфейса и затем вновь добавленным без уничтожения самого фрагмента.

**Более гранулярное управление состоянием**: Фрагменты предоставляют более детальное управление состоянием, включая сохранение и восстановление локального состояния фрагмента через `onSaveInstanceState` и возможность возвращения на предыдущие состояния с помощью системы back stack, что не характерно для активити.

**Взаимодействие с другими фрагментами**: Фрагменты могут взаимодействовать друг с другом через родительскую активити, что позволяет создавать более сложные пользовательские интерфейсы с динамическим взаимодействием между компонентами интерфейса.

**Множественное использование и повторное встраивание**: В отличие от активити, которая представляет собой отдельный экран или задачу, фрагменты разработаны для того, чтобы быть многократно встраиваемыми в различные активити или даже в другие фрагменты, обеспечивая повторное использование компонентов интерфейса и логики.

Хотя фрагменты и активити разделяют многие аспекты жизненного цикла, связанные с созданием, паузой, возобновлением и уничтожением, фрагменты имеют уникальные состояния и события, отражающие их более гибкое и динамичное использование в приложении. Это делает их мощным инструментом для разработки модульных, адаптивных и многопанельных пользовательских интерфейсов в Android приложениях.
