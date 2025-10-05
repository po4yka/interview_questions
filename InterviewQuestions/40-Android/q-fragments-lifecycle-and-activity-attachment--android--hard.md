---
id: 202510031403
title: How do fragments exist and what are they attached to in Activity / Расскажи как существуют и к чему привязаны фрагменты в Activity
aliases: []

# Classification
topic: android
subtopics: [android, ui, fragments]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/474
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-fragments
  - c-android-activity
  - c-android-fragment-lifecycle

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [fragments, activity, lifecycle, difficulty/hard, easy_kotlin, lang/ru, android/fragments, android/ui]
---

# Question (EN)
> How do fragments exist and what are they attached to in Activity

# Вопрос (RU)
> Расскажи как существуют и к чему привязаны фрагменты в Activity

---

## Answer (EN)

Fragments in Android are modular, reusable UI components that exist as sub-components within an Activity. Understanding their attachment mechanism and lifecycle is crucial for proper Android development.

### Fragment Attachment to Activity

#### 1. FragmentManager Relationship

Fragments are managed by **FragmentManager**, which maintains the fragment lifecycle and back stack.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Add fragment using FragmentManager
        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, MyFragment())
                .commit()
        }
    }
}
```

#### 2. Context Dependency

Fragments depend on their host Activity for:
- **Context access**: Through `requireContext()` or `requireActivity()`
- **Resources**: String, drawable, and other resources
- **System services**: Getting system-level services
- **Lifecycle coordination**: Fragment lifecycle tied to Activity lifecycle

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment is now attached to Activity context
        val activity = requireActivity()
        val appContext = context.applicationContext
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment is detaching from Activity
    }
}
```

### Fragment Lifecycle Synchronization

Fragments have their own lifecycle that is closely synchronized with the Activity lifecycle:

```kotlin
Activity                    Fragment
onCreate() ─────────────────> onAttach()
                              onCreate()
                              onCreateView()
                              onViewCreated()
                              onActivityCreated()
onStart() ──────────────────> onStart()
onResume() ─────────────────> onResume()

onPause() ──────────────────> onPause()
onStop() ───────────────────> onStop()
                              onDestroyView()
onDestroy() ────────────────> onDestroy()
                              onDetach()
```

### Fragment Attachment Points

#### Static Attachment (XML)

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <fragment
        android:id="@+id/my_fragment"
        android:name="com.example.MyFragment"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</FrameLayout>
```

#### Dynamic Attachment (Code)

```kotlin
// Add fragment
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment(), "MY_FRAGMENT_TAG")
    .commit()

// Replace fragment
supportFragmentManager.beginTransaction()
    .replace(R.id.container, AnotherFragment())
    .addToBackStack(null)
    .commit()

// Remove fragment
supportFragmentManager.beginTransaction()
    .remove(fragment)
    .commit()
```

### Fragment Container

Fragments must be attached to a **container ViewGroup** in the Activity's layout:

```xml
<FrameLayout
    android:id="@+id/fragment_container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

### Multiple Fragment Scenarios

#### Master-Detail Pattern

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (isTablet()) {
            // Show both fragments
            supportFragmentManager.beginTransaction()
                .add(R.id.master_container, MasterFragment())
                .add(R.id.detail_container, DetailFragment())
                .commit()
        } else {
            // Show only master
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MasterFragment())
                .commit()
        }
    }
}
```

### Fragment Back Stack

Fragments can be added to the back stack for navigation:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, SecondFragment())
    .addToBackStack("second_fragment")
    .commit()

// Pop back stack
supportFragmentManager.popBackStack()
```

### Key Characteristics

1. **Modular**: Can be reused across multiple activities
2. **Lifecycle-aware**: Respond to Activity lifecycle changes
3. **Dynamic**: Can be added, removed, or replaced at runtime
4. **Back stack support**: Enable navigation history
5. **Context-dependent**: Require Activity for resources and context
6. **ViewLifecycle separate**: View can be created/destroyed independently

### Best Practices

1. **Always check attachment** before accessing Activity
2. **Use ViewLifecycleOwner** for observers in fragments
3. **Avoid retaining Activity references** after onDetach()
4. **Handle configuration changes** properly
5. **Use Navigation Component** for complex navigation flows

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Use viewLifecycleOwner for LiveData observation
        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateUI(data)
        }
    }

    private fun safelyAccessActivity() {
        // Check if fragment is attached
        if (isAdded && activity != null) {
            requireActivity().supportActionBar?.title = "My Title"
        }
    }
}
```

## Ответ (RU)

Фрагменты в Android — это компоненты приложения, которые могут быть добавлены в Activity для создания модульного интерфейса. Фрагменты жизненно привязаны к Activity, которая выступает как хост для них. Они имеют собственный жизненный цикл, который тесно связан с жизненным циклом своей родительской Activity. Фрагменты можно добавлять, удалять и заменять во время выполнения приложения, что делает их идеальными для адаптивных и динамических пользовательских интерфейсов.

---

## Follow-ups
- How does the Fragment ViewLifecycleOwner differ from the Fragment lifecycle?
- What happens to fragments during configuration changes?
- How do you handle retained fragments and what are their use cases?

## References
- [[c-android-fragments]]
- [[c-android-activity]]
- [[c-android-fragment-lifecycle]]
- [[c-android-fragmentmanager]]
- [[moc-android]]

## Related Questions
- [[q-how-did-fragments-appear-and-why-were-they-started-to-be-used--android--hard]]
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]
- [[q-pass-data-between-fragments--android--medium]]
