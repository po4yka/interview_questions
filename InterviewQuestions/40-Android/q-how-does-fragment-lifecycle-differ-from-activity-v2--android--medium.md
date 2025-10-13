---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# How does Fragment lifecycle differ from Activity?

## Answer (EN)
Fragment lifecycle is more complex than Activity lifecycle because **Fragments have additional lifecycle states related to their View and their attachment to an Activity**. Fragments have 11 lifecycle callbacks compared to Activity's 7.

### Key Differences

1. **Fragment depends on Activity** - Fragment cannot exist without an Activity host
2. **Separate View lifecycle** - Fragment has distinct View creation/destruction callbacks
3. **Attachment/Detachment** - Fragment can be attached/detached from Activity
4. **Retention** - Fragment can be retained across configuration changes (deprecated but shows lifecycle difference)

### Side-by-Side Lifecycle Comparison

```
Activity Lifecycle          Fragment Lifecycle
=================          ==================
                          → onAttach()          [NEW: Attached to Activity]
onCreate()                → onCreate()          [Same: Initial creation]
                          → onCreateView()      [NEW: View creation]
                          → onViewCreated()     [NEW: View created]
onStart()                 → onStart()           [Same: Becoming visible]
onResume()                → onResume()          [Same: Interactive]
onPause()                 → onPause()           [Same: Losing focus]
onStop()                  → onStop()            [Same: No longer visible]
                          → onDestroyView()     [NEW: View destroyed]
onDestroy()               → onDestroy()         [Same: Fragment destroyed]
                          → onDetach()          [NEW: Detached from Activity]
```

### Complete Fragment Lifecycle with Activity

```kotlin
class MyFragment : Fragment() {

    // 1. ATTACHMENT PHASE (doesn't exist in Activity)
    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.d("Lifecycle", "Fragment: onAttach - Fragment attached to Activity")
        // Fragment is now attached to Activity
        // Can access requireActivity() and requireContext()
    }

    // 2. CREATION PHASE
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "Fragment: onCreate - Fragment created")
        // Similar to Activity onCreate
        // Initialize non-view components
        // Retrieve arguments
        val userId = arguments?.getInt("user_id")
    }

    // 3. VIEW CREATION PHASE (doesn't exist in Activity)
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.d("Lifecycle", "Fragment: onCreateView - Creating view")
        // Return the Fragment's root view
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    // 4. VIEW CREATED PHASE (doesn't exist in Activity)
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("Lifecycle", "Fragment: onViewCreated - View created and ready")
        // Initialize views, set click listeners
        // This is where you typically set up UI
        view.findViewById<Button>(R.id.button).setOnClickListener {
            // Handle click
        }
    }

    // 5. START PHASE
    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "Fragment: onStart - Fragment visible")
        // Fragment is visible
    }

    // 6. RESUME PHASE
    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "Fragment: onResume - Fragment interactive")
        // Fragment is in foreground and interactive
    }

    // 7. PAUSE PHASE
    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "Fragment: onPause - Losing focus")
        // Fragment losing focus
    }

    // 8. STOP PHASE
    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "Fragment: onStop - No longer visible")
        // Fragment no longer visible
    }

    // 9. VIEW DESTRUCTION PHASE (doesn't exist in Activity)
    override fun onDestroyView() {
        super.onDestroyView()
        Log.d("Lifecycle", "Fragment: onDestroyView - View destroyed")
        // View hierarchy being removed
        // Clean up view references to prevent memory leaks
        _binding = null
    }

    // 10. DESTRUCTION PHASE
    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "Fragment: onDestroy - Fragment destroyed")
        // Fragment being destroyed
        // Clean up resources
    }

    // 11. DETACHMENT PHASE (doesn't exist in Activity)
    override fun onDetach() {
        super.onDetach()
        Log.d("Lifecycle", "Fragment: onDetach - Detached from Activity")
        // Fragment detached from Activity
        // Cannot access requireActivity() anymore
    }
}
```

### Visual Lifecycle Flow

```

         Activity onCreate()              

               ↓

      Fragment onAttach(context)          
      Fragment onCreate(bundle)           
      Fragment onCreateView()             
      Fragment onViewCreated()            

               ↓

         Activity onStart()               
         Fragment onStart()               

               ↓

         Activity onResume()              
         Fragment onResume()              

               ↓
         [RUNNING STATE]
               ↓

         Fragment onPause()               
         Activity onPause()               

               ↓

         Fragment onStop()                
         Activity onStop()                

               ↓

      Fragment onDestroyView()            
      Fragment onDestroy()                
      Fragment onDetach()                 

               ↓

         Activity onDestroy()             

```

### Real-World Example: Fragment Transaction Lifecycle

```kotlin
class HostActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_host)

        // Add fragment
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, MyFragment())
            .commit()
    }
}

// Lifecycle output when fragment is added:
// Activity: onCreate
// Fragment: onAttach
// Fragment: onCreate
// Fragment: onCreateView
// Fragment: onViewCreated
// Activity: onStart
// Fragment: onStart
// Activity: onResume
// Fragment: onResume
```

### Fragment Replace Transaction

```kotlin
fun replaceFragment() {
    supportFragmentManager.beginTransaction()
        .replace(R.id.fragment_container, NewFragment())
        .addToBackStack(null)
        .commit()
}

// Lifecycle when replacing:
// OldFragment: onPause
// OldFragment: onStop
// OldFragment: onDestroyView
// NewFragment: onAttach
// NewFragment: onCreate
// NewFragment: onCreateView
// NewFragment: onViewCreated
// NewFragment: onStart
// NewFragment: onResume

// Note: OldFragment's onDestroy/onDetach NOT called
// because it's added to back stack
```

### Back Stack Navigation

```kotlin
// When pressing back from NewFragment:
// NewFragment: onPause
// NewFragment: onStop
// NewFragment: onDestroyView
// NewFragment: onDestroy
// NewFragment: onDetach

// OldFragment: onCreateView     (View recreated!)
// OldFragment: onViewCreated
// OldFragment: onStart
// OldFragment: onResume
```

### Configuration Change (Rotation)

```kotlin
// Activity configuration change with Fragment:

// Old Activity & Fragment destruction:
// Fragment: onPause
// Activity: onPause
// Fragment: onStop
// Activity: onStop
// Fragment: onDestroyView
// Fragment: onDestroy
// Fragment: onDetach
// Activity: onDestroy

// New Activity & Fragment creation:
// Activity: onCreate
// Fragment: onAttach
// Fragment: onCreate
// Fragment: onCreateView
// Fragment: onViewCreated
// Activity: onStart
// Fragment: onStart
// Activity: onResume
// Fragment: onResume
```

### View Binding Lifecycle Management

```kotlin
class MyFragment : Fragment() {
    // Use backing property to avoid memory leaks
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Create binding
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Safe to use binding
        binding.textView.text = "Hello"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // IMPORTANT: Clear binding to prevent memory leak
        _binding = null
    }
}
```

### Fragment Lifecycle with ViewLifecycleOwner

```kotlin
class ModernFragment : Fragment() {
    private var _binding: FragmentModernBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Use viewLifecycleOwner for LiveData/Flow observation
        viewModel.userData.observe(viewLifecycleOwner) { user ->
            binding.nameText.text = user.name
        }

        // Coroutines tied to view lifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUI(state)
            }
        }
    }
}

// Why viewLifecycleOwner?
// Fragment's lifecycle ≠ Fragment's View lifecycle
// viewLifecycleOwner lifecycle matches the View
// Prevents leaks when Fragment is on back stack
```

### Comparison Table

| Aspect | Activity | Fragment |
|--------|----------|----------|
| **Lifecycle callbacks** | 7 main callbacks | 11 callbacks |
| **View creation** | `setContentView()` in `onCreate()` | Separate `onCreateView()` |
| **Can exist alone** | Yes | No, requires Activity |
| **Attachment** | N/A | `onAttach()`, `onDetach()` |
| **View lifecycle** | Same as Activity | Separate: `onCreateView()`, `onDestroyView()` |
| **Back stack** | System back stack | FragmentManager back stack |
| **Retains state** | Via `onSaveInstanceState()` | Via `onSaveInstanceState()` + arguments |
| **Multiple instances** | One per screen | Multiple per Activity |

### Fragment-Specific Lifecycle Scenarios

#### 1. Fragment in ViewPager

```kotlin
class MyPagerAdapter : FragmentStateAdapter(activity) {
    override fun createFragment(position: Int): Fragment {
        return MyFragment.newInstance(position)
    }
}

// Lifecycle for off-screen fragments:
// Position 0 (visible): Full lifecycle to onResume
// Position 1 (off-screen): onCreate → onDestroyView (View destroyed but Fragment kept)
// Position -1 (destroyed): Full destruction
```

#### 2. DialogFragment Lifecycle

```kotlin
class MyDialogFragment : DialogFragment() {

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        // Called BEFORE onCreateView
        return AlertDialog.Builder(requireContext())
            .setTitle("Dialog")
            .setMessage("Message")
            .create()
    }

    override fun onCreateView(...): View? {
        // Called AFTER onCreateDialog
        return super.onCreateView(inflater, container, savedInstanceState)
    }
}

// DialogFragment lifecycle:
// onAttach → onCreate → onCreateDialog → onCreateView → onViewCreated → onStart → onResume
```

#### 3. Detached Fragment (setMaxLifecycle)

```kotlin
// Set fragment to STARTED state (won't call onResume)
fragmentTransaction.setMaxLifecycle(fragment, Lifecycle.State.STARTED)

// Lifecycle stops at onStart:
// onAttach → onCreate → onCreateView → onViewCreated → onStart
// (onResume NOT called)
```

### Common Lifecycle Mistakes

```kotlin
// WRONG: Accessing view in onCreate
class WrongFragment : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // view is null here!
        view?.findViewById<TextView>(R.id.text)
    }
}

// CORRECT: Access view in onViewCreated
class CorrectFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // view is available here
        view.findViewById<TextView>(R.id.text).text = "Hello"
    }
}

// WRONG: Not clearing binding
class LeakyFragment : Fragment() {
    private var _binding: FragmentBinding? = null
    private val binding get() = _binding!!

    override fun onDestroyView() {
        super.onDestroyView()
        // Forgot to clear binding - MEMORY LEAK!
    }
}

// CORRECT: Clear binding
class SafeFragment : Fragment() {
    private var _binding: FragmentBinding? = null
    private val binding get() = _binding!!

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Prevents memory leak
    }
}
```

### Fragment Lifecycle Best Practices

1. **Initialize non-view components in `onCreate()`**
   - Arguments parsing
   - ViewModel initialization
   - Repository setup

2. **Initialize views in `onViewCreated()`**
   - View binding setup
   - Click listeners
   - RecyclerView adapters

3. **Use `viewLifecycleOwner` for observations**
   - Prevents leaks when Fragment is on back stack
   - Automatically unsubscribes when view is destroyed

4. **Clean up in `onDestroyView()`**
   - Clear view bindings
   - Cancel view-related coroutines
   - Remove listeners

5. **Understand back stack behavior**
   - Fragment stays in memory when on back stack
   - View is destroyed (`onDestroyView`) but Fragment exists
   - View recreated (`onCreateView`) when returning from back stack

### Summary

**Main Differences:**
1. Fragment has **extra callbacks** for attachment/detachment and view creation/destruction
2. Fragment lifecycle is **nested within** Activity lifecycle
3. Fragment **View lifecycle** is separate from Fragment lifecycle
4. Fragment can be on **back stack** with destroyed views
5. Fragment requires careful **memory leak prevention** (binding cleanup)

## Ответ (RU)

Жизненный цикл Fragment сложнее, чем у Activity, потому что Fragment имеет дополнительные состояния, связанные с View и прикреплением к Activity. У Fragment 11 коллбэков жизненного цикла против 7 у Activity.

**Основные отличия:**
1. **Fragment зависит от Activity** - не может существовать самостоятельно
2. **Отдельный жизненный цикл View** - есть отдельные коллбэки для создания/уничтожения View (onCreateView, onViewCreated, onDestroyView)
3. **Прикрепление/открепление** - дополнительные коллбэки onAttach и onDetach
4. **Back stack** - Fragment может оставаться в памяти с уничтоженной View

**Уникальные коллбэки Fragment:**
- `onAttach()` - прикрепление к Activity
- `onCreateView()` - создание View
- `onViewCreated()` - View создана и готова
- `onDestroyView()` - уничтожение View
- `onDetach()` - открепление от Activity

**Важно:**
- Инициализировать View нужно в `onViewCreated()`, не в `onCreate()`
- Обязательно очищать binding в `onDestroyView()` во избежание утечек памяти
- Использовать `viewLifecycleOwner` для наблюдения за LiveData/Flow

## Related Topics
- Fragment transactions
- FragmentManager
- Back stack navigation
- ViewLifecycleOwner
- Memory leak prevention
- Fragment communication

---

## Related Questions

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, Activity
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, Activity
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Activity, Fragment
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle, Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Activity, Fragment

---

## Related Questions

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, Activity
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, Activity
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Activity, Fragment
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle, Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Activity, Fragment

---

## Related Questions

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, Activity
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, Activity
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Activity, Fragment
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle, Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Activity, Fragment
