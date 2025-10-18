---
id: 20251012-122791
title: "Can State Loss Be Related To A Fragment / Может ли потеря состояния быть связана с Fragment"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-save-markdown-structure-database--android--medium, q-canvas-optimization--graphics--medium, q-workmanager-advanced--background--medium]
created: 2025-10-15
tags:
  - android
---
# Can state loss be related to a fragment

# Question (EN)
> Can state loss be related to a fragment?

# Вопрос (RU)
> Может ли потеря состояния быть связана с фрагментом?

---

## Answer (EN)

Yes, Fragment state loss is a common issue in Android development. It can occur in several scenarios related to Fragment lifecycle, transactions, and parent Activity state management.

---

## Ответ (RU)

Да, потеря состояния Fragment - это распространенная проблема в Android разработке. Она может возникать при коммите транзакции после вызова onSaveInstanceState(), при изменении конфигурации, при использовании commit() вместо commitAllowingStateLoss(), и при неправильной работе с backstack.

### When Fragment State Loss Occurs

#### 1. Transaction After onSaveInstanceState

The most common cause - committing Fragment transaction after Activity has saved its state:

```kotlin
class MainActivity : AppCompatActivity() {

    fun replaceFragment() {
        // This can throw IllegalStateException if called after onSaveInstanceState()
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, MyFragment())
            .commit()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // After this point, commit() will throw exception
        // State already saved, new transactions not allowed
    }
}
```

**Error**:
```
java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState
```

**Solutions**:

```kotlin
// Solution 1: Use commitAllowingStateLoss() - risky
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commitAllowingStateLoss() // Fragment might be lost on process death

// Solution 2: Check if state saved
if (!isStateSaved) {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, MyFragment())
        .commit()
}

// Solution 3: Use commitNow() in safe locations
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState == null) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, MyFragment())
            .commitNow() // Synchronous, safer
    }
}

// Solution 4: Post transaction to run when safe
lifecycleScope.launchWhenResumed {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, MyFragment())
        .commit()
}
```

#### 2. Process Death Without State Saving

Fragment state lost when process is killed:

```kotlin
class MyFragment : Fragment() {

    private var userName: String = ""
    private var userAge: Int = 0

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // These won't survive process death
        userName = "John"
        userAge = 25
    }
}

// After process death: userName and userAge reset to defaults
```

**Solution**: Implement onSaveInstanceState

```kotlin
class MyFragment : Fragment() {

    private var userName: String = ""
    private var userAge: Int = 0

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Restore state
        savedInstanceState?.let {
            userName = it.getString(KEY_USER_NAME, "")
            userAge = it.getInt(KEY_USER_AGE, 0)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save state
        outState.putString(KEY_USER_NAME, userName)
        outState.putInt(KEY_USER_AGE, userAge)
    }

    companion object {
        private const val KEY_USER_NAME = "user_name"
        private const val KEY_USER_AGE = "user_age"
    }
}
```

#### 3. Fragment Removed from Back Stack

Fragment recreated when popped from back stack:

```kotlin
class MainActivity : AppCompatActivity() {

    fun addFragment() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, FragmentA())
            .addToBackStack("fragmentA")
            .commit()

        // Later, add another fragment
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, FragmentB())
            .addToBackStack("fragmentB")
            .commit()
    }

    // When user presses back:
    // FragmentB destroyed
    // FragmentA RECREATED (not restored)
    // State lost unless saved in onSaveInstanceState
}
```

**Solution**: Use ViewModel or onSaveInstanceState

```kotlin
class FragmentA : Fragment() {

    // Survives back stack recreation
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.userData.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }
}
```

#### 4. Parent Activity Destroyed

Fragment state lost when parent Activity is destroyed:

```kotlin
// Configuration change (rotation)
// Activity destroyed → Fragment destroyed
// Activity recreated → Fragment recreated
// Fragment state lost unless properly saved

class MyFragment : Fragment() {

    private lateinit var expensiveData: LargeDataSet

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Lost on configuration change
        expensiveData = loadLargeDataSet()
    }
}
```

**Solutions**:

```kotlin
// Solution 1: ViewModel (recommended)
class MyFragment : Fragment() {
    private val viewModel: DataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ViewModel survives configuration changes
        viewModel.loadDataIfNeeded()
    }
}

// Solution 2: retainInstance (deprecated)
class MyFragment : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        retainInstance = true // Deprecated, use ViewModel
    }
}
```

#### 5. View State Loss

Fragment's view destroyed but Fragment instance retained:

```kotlin
class MyFragment : Fragment() {

    private var binding: FragmentMyBinding? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding!!.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding?.editText?.setText("Some text")
        // View can be destroyed while Fragment lives (back stack)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        binding = null // Must null out binding
    }
}
```

**Solution**: Observe LiveData with viewLifecycleOwner

```kotlin
class MyFragment : Fragment() {

    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Use viewLifecycleOwner, not this (Fragment lifecycle)
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }
    }
}
```

### Fragment Manager State Loss Scenarios

```kotlin
// Scenario 1: Asynchronous callback after state saved
class MyFragment : Fragment() {

    fun loadData() {
        viewLifecycleOwner.lifecycleScope.launch {
            val data = repository.getData()

            // Fragment might be in saved state by now
            // This can cause IllegalStateException
            childFragmentManager.beginTransaction()
                .replace(R.id.child_container, ChildFragment())
                .commit() // Can crash
        }
    }
}

// Solution: Check lifecycle state
class MyFragment : Fragment() {

    fun loadData() {
        viewLifecycleOwner.lifecycleScope.launch {
            val data = repository.getData()

            if (viewLifecycleOwner.lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                childFragmentManager.beginTransaction()
                    .replace(R.id.child_container, ChildFragment())
                    .commit() // Safe
            }
        }
    }
}
```

### Using commitAllowingStateLoss Safely

```kotlin
class MyFragment : Fragment() {

    fun showDialog() {
        // When to use commitAllowingStateLoss:
        // 1. UI update not critical if lost
        // 2. User-triggered action in async callback
        // 3. Fragment can be safely recreated

        DialogFragment().show(
            childFragmentManager.beginTransaction()
                .commitAllowingStateLoss(), // Acceptable for dialogs
            "dialog"
        )
    }

    fun criticalTransaction() {
        // Don't use for critical state changes
        childFragmentManager.beginTransaction()
            .replace(R.id.container, ImportantFragment())
            .commit() // Use regular commit for critical operations
    }
}
```

### Complete State Management Example

```kotlin
class UserFragment : Fragment() {

    private var _binding: FragmentUserBinding? = null
    private val binding get() = _binding!!

    // Survives configuration changes
    private val viewModel: UserViewModel by viewModels()

    // Transient UI state
    private var scrollPosition: Int = 0

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentUserBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Restore UI state
        savedInstanceState?.let {
            scrollPosition = it.getInt(KEY_SCROLL_POSITION, 0)
            binding.recyclerView.scrollToPosition(scrollPosition)
        }

        // Observe ViewModel (survives config changes)
        viewModel.users.observe(viewLifecycleOwner) { users ->
            updateUserList(users)
        }

        // Setup listeners
        binding.button.setOnClickListener {
            // Safe transaction - in click listener
            showDetailFragment()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save UI state
        scrollPosition = (binding.recyclerView.layoutManager as LinearLayoutManager)
            .findFirstVisibleItemPosition()
        outState.putInt(KEY_SCROLL_POSITION, scrollPosition)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun showDetailFragment() {
        parentFragmentManager.beginTransaction()
            .replace(R.id.container, DetailFragment())
            .addToBackStack(null)
            .commit()
    }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
    }
}
```

### Best Practices

1. **Use ViewModel**: For data that survives configuration changes
2. **Implement onSaveInstanceState**: For UI state
3. **Check lifecycle state**: Before Fragment transactions
4. **Use viewLifecycleOwner**: When observing LiveData
5. **Null binding in onDestroyView**: Prevent memory leaks
6. **Avoid commitAllowingStateLoss**: Unless state loss is acceptable
7. **Test process death**: Use "Don't keep activities" developer option

## Ответ (RU)
Да, потеря состояния может быть связана с фрагментами в Android. Это связано со сложным жизненным циклом фрагмента, удалением View системой, проблемами с менеджером фрагментов и неправильным использованием savedInstanceState. Для предотвращения потери состояния рекомендуется использовать onSaveInstanceState, ViewModel и правильно работать с FragmentManager.

## Related Topics
- Fragment lifecycle
- onSaveInstanceState
- ViewModel
- commitAllowingStateLoss
- viewLifecycleOwner

---

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment
- [[q-fragment-basics--android--easy]] - Fragment

### Related (Medium)
- [[q-save-data-outside-fragment--android--medium]] - Fragment
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]] - Fragment
- [[q-how-to-pass-parameters-to-a-fragment--android--easy]] - Fragment

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment
