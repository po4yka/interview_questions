---
id: 202510031411308
title: How do fragments exist and what are they attached to in Activity / Как существуют и к чему привязаны фрагменты в Activity
aliases: []

# Classification
topic: android
subtopics: [android, ui, fragments]
question_kind: practical
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/142
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-fragments
  - c-android-activity
  - c-android-fragmentmanager

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [fragments, activity, difficulty/hard, easy_kotlin, lang/ru, android/fragments]
---

# Question (EN)
> How do fragments exist and what are they attached to in Activity

# Вопрос (RU)
> Как существуют и к чему привязаны фрагменты в Activity

---

## Answer (EN)

Fragments are modular UI sections that are attached to Activities. They exist in the context of an activity and cannot exist independently without one.

### Fragment Attachment to Activity

#### 1. Container-Based Attachment

Fragments are added to **containers**, which are part of the activity's layout. These containers are typically `FrameLayout` or other `ViewGroup` elements.

```xml
<!-- activity_main.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Add fragment to container
        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, HomeFragment())
                .commit()
        }
    }
}
```

#### 2. FragmentManager

Fragments are managed by the **FragmentManager**, which handles:
- Adding, removing, and replacing fragments
- Fragment transactions
- Back stack management
- Fragment lifecycle

```kotlin
// Access FragmentManager
val fragmentManager = supportFragmentManager

// Fragment transaction
fragmentManager.beginTransaction()
    .replace(R.id.fragment_container, DetailFragment())
    .addToBackStack("detail")
    .commit()

// Find existing fragment
val fragment = fragmentManager.findFragmentById(R.id.fragment_container)
val fragmentByTag = fragmentManager.findFragmentByTag("myTag")
```

### Fragment Lifecycle Relationship with Activity

The fragment's lifecycle is **closely tied** to the activity's lifecycle:

```kotlin
class MyFragment : Fragment() {
    // Fragment lifecycle methods closely follow Activity lifecycle

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment is attached to activity
        // Activity is available via requireActivity()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Called after onAttach, before onCreateView
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Create fragment's view hierarchy
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // View is created, safe to initialize UI
    }

    override fun onStart() {
        super.onStart()
        // Fragment visible but not interactive
    }

    override fun onResume() {
        super.onResume()
        // Fragment visible and interactive
    }

    override fun onPause() {
        super.onPause()
        // Fragment losing focus
    }

    override fun onStop() {
        super.onStop()
        // Fragment no longer visible
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Clean up view-related resources
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up fragment resources
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment detached from activity
    }
}
```

### Fragment-Activity Interaction

#### 1. Accessing Activity from Fragment

```kotlin
class MyFragment : Fragment() {
    fun interactWithActivity() {
        // Get activity reference
        val activity = requireActivity()

        // Access activity resources
        val string = requireActivity().getString(R.string.app_name)

        // Call activity methods
        (activity as? MainActivity)?.someActivityMethod()
    }
}
```

#### 2. Communicating Through Interfaces

```kotlin
// Define interface
interface OnFragmentInteractionListener {
    fun onItemSelected(item: String)
}

// Implement in fragment
class ListFragment : Fragment() {
    private var listener: OnFragmentInteractionListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)
        listener = context as? OnFragmentInteractionListener
            ?: throw RuntimeException("$context must implement OnFragmentInteractionListener")
    }

    fun selectItem(item: String) {
        listener?.onItemSelected(item)
    }

    override fun onDetach() {
        super.onDetach()
        listener = null
    }
}

// Implement in activity
class MainActivity : AppCompatActivity(), OnFragmentInteractionListener {
    override fun onItemSelected(item: String) {
        // Handle item selection
    }
}
```

#### 3. Accessing Activity Context

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Access context safely
        val context = requireContext()

        // Use activity context
        Toast.makeText(requireContext(), "Message", Toast.LENGTH_SHORT).show()

        // Get system services
        val inflater = requireContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
    }
}
```

### Fragment Dependency on Activity

Key points about fragment existence:

1. **Cannot exist independently** - Fragment must be attached to an Activity or another Fragment
2. **Shares activity lifecycle** - When activity is destroyed, all fragments are destroyed
3. **Requires container** - Fragment's view must be placed in a ViewGroup container in the activity's layout
4. **Managed by FragmentManager** - Activity's FragmentManager controls fragment lifecycle
5. **Context dependency** - Fragment uses activity's context for resources and system services

```kotlin
// Fragment cannot exist without activity
class MyFragment : Fragment() {
    fun demonstrateDependency() {
        // All these require activity context
        val activity = requireActivity()  // Throws if no activity
        val context = requireContext()    // Throws if no context

        // Fragment's view is placed in activity's view hierarchy
        val parent = view?.parent  // Parent is activity's container
    }
}
```

### Summary

Fragments are **modular UI components** that:
- Exist within the context of an Activity
- Are added to ViewGroup containers in the activity's layout
- Have a lifecycle closely tied to the activity's lifecycle
- Cannot exist independently without an activity
- Interact with the activity through context, interfaces, or direct references
- Are managed by the activity's FragmentManager

## Ответ (RU)

Фрагменты представляют собой модульные секции пользовательского интерфейса, привязанные к активити. Они существуют в контексте активити и привязаны к ней, не могут существовать самостоятельно без активити. Фрагменты добавляются в контейнеры, которые являются частью макета активити. Жизненный цикл фрагмента тесно связан с жизненным циклом активити. Фрагменты могут взаимодействовать с активити через интерфейсы или обращение к Context активити.

---

## Follow-ups
- What happens to fragments when the activity is destroyed and recreated due to configuration changes?
- How do child fragments work and how are they attached to parent fragments?
- What is the difference between add() and replace() in fragment transactions?

## References
- [[c-android-fragments]]
- [[c-android-activity]]
- [[c-android-fragmentmanager]]
- [[c-android-lifecycle]]
- [[moc-android]]

## Related Questions
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]]
