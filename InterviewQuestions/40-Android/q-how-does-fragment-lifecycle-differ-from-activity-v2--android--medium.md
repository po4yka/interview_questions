---
id: android-339
title: "How Does Fragment Lifecycle Differ From Activity V2 / Чем жизненный цикл Fragment отличается от Activity v2"
aliases: ["How Does Fragment Lifecycle Differ From Activity V2", "Чем жизненный цикл Fragment отличается от Activity v2"]
topic: android
subtopics: [activity, fragment, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-project-parts--android--easy, q-how-to-add-custom-attributes-to-custom-view--android--medium, q-workmanager-return-result--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android, android/activity, android/fragment, android/lifecycle, difficulty/medium]
date created: Tuesday, October 28th 2025, 9:35:33 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Чем жизненный цикл Fragment отличается от жизненного цикла Activity?

# Question (EN)

How does Fragment lifecycle differ from Activity lifecycle?

---

## Ответ (RU)

Жизненный цикл Fragment сложнее, чем у Activity, потому что **Fragment имеет дополнительные состояния, связанные с View и прикреплением к Activity**. У Fragment 11 коллбэков против 7 у Activity.

### Ключевые Отличия

1. **Fragment зависит от Activity** — не может существовать самостоятельно
2. **Отдельный жизненный цикл View** — есть коллбэки для создания/уничтожения View
3. **Прикрепление/открепление** — Fragment может прикрепляться/открепляться от Activity
4. **Back stack** — Fragment может оставаться в памяти с уничтоженной View

### Сравнение Коллбэков

```text
Activity                   Fragment
=========                  =========
                          → onAttach()
onCreate()                → onCreate()
                          → onCreateView()
                          → onViewCreated()
onStart()                 → onStart()
onResume()                → onResume()
onPause()                 → onPause()
onStop()                  → onStop()
                          → onDestroyView()
onDestroy()               → onDestroy()
                          → onDetach()
```

### Основной Жизненный Цикл Fragment

```kotlin
class MyFragment : Fragment() {

    // ✅ Прикрепление к Activity
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Доступны requireActivity() и requireContext()
    }

    // ✅ Инициализация без View
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = arguments?.getInt("user_id")
    }

    // ✅ Создание View
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    // ✅ View создана и готова
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        view.findViewById<Button>(R.id.button).setOnClickListener {
            // Handle click
        }
    }

    // ✅ Уничтожение View
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Предотвращение утечек памяти
    }

    // ✅ Открепление от Activity
    override fun onDetach() {
        super.onDetach()
        // requireActivity() недоступен
    }
}
```

### View Binding С Правильной Очисткой

```kotlin
class SafeFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Создание binding
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.textView.text = "Hello"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ✅ ВАЖНО: очистка binding
        _binding = null
    }
}
```

### ViewLifecycleOwner Для Наблюдений

```kotlin
class ModernFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ Использование viewLifecycleOwner
        viewModel.userData.observe(viewLifecycleOwner) { user ->
            binding.nameText.text = user.name
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { updateUI(it) }
        }
    }
}
```

### Back Stack Navigation

```kotlin
// При replace с addToBackStack:
// OldFragment: onPause → onStop → onDestroyView
// NewFragment: onAttach → onCreate → onCreateView → onViewCreated → onStart → onResume

// При нажатии Back:
// NewFragment: onPause → onStop → onDestroyView → onDestroy → onDetach
// OldFragment: onCreateView → onViewCreated → onStart → onResume
// (View пересоздана!)
```

### Распространенные Ошибки

```kotlin
// ❌ НЕПРАВИЛЬНО: доступ к View в onCreate
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    view?.findViewById<TextView>(R.id.text)  // view == null!
}

// ✅ ПРАВИЛЬНО: доступ к View в onViewCreated
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    view.findViewById<TextView>(R.id.text).text = "Hello"
}

// ❌ НЕПРАВИЛЬНО: не очищен binding
override fun onDestroyView() {
    super.onDestroyView()
    // Утечка памяти!
}

// ✅ ПРАВИЛЬНО: очистка binding
override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

## Answer (EN)

Fragment lifecycle is more complex than Activity lifecycle because **Fragments have additional lifecycle states related to their View and their attachment to an Activity**. Fragments have 11 lifecycle callbacks compared to Activity's 7.

### Key Differences

1. **Fragment depends on Activity** — cannot exist without an Activity host
2. **Separate View lifecycle** — Fragment has distinct View creation/destruction callbacks
3. **Attachment/Detachment** — Fragment can be attached/detached from Activity
4. **Back stack** — Fragment can remain in memory with destroyed views

### Lifecycle Callbacks Comparison

```text
Activity                   Fragment
=========                  =========
                          → onAttach()
onCreate()                → onCreate()
                          → onCreateView()
                          → onViewCreated()
onStart()                 → onStart()
onResume()                → onResume()
onPause()                 → onPause()
onStop()                  → onStop()
                          → onDestroyView()
onDestroy()               → onDestroy()
                          → onDetach()
```

### Basic Fragment Lifecycle

```kotlin
class MyFragment : Fragment() {

    // ✅ Attached to Activity
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // requireActivity() and requireContext() available
    }

    // ✅ Initialize non-view components
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = arguments?.getInt("user_id")
    }

    // ✅ Create View
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    // ✅ View created and ready
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        view.findViewById<Button>(R.id.button).setOnClickListener {
            // Handle click
        }
    }

    // ✅ View destruction
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Prevent memory leaks
    }

    // ✅ Detached from Activity
    override fun onDetach() {
        super.onDetach()
        // requireActivity() no longer available
    }
}
```

### View Binding with Proper Cleanup

```kotlin
class SafeFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Create binding
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.textView.text = "Hello"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ✅ IMPORTANT: Clear binding
        _binding = null
    }
}
```

### ViewLifecycleOwner for Observations

```kotlin
class ModernFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ Use viewLifecycleOwner
        viewModel.userData.observe(viewLifecycleOwner) { user ->
            binding.nameText.text = user.name
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { updateUI(it) }
        }
    }
}
```

### Back Stack Navigation

```kotlin
// During replace with addToBackStack:
// OldFragment: onPause → onStop → onDestroyView
// NewFragment: onAttach → onCreate → onCreateView → onViewCreated → onStart → onResume

// When pressing Back:
// NewFragment: onPause → onStop → onDestroyView → onDestroy → onDetach
// OldFragment: onCreateView → onViewCreated → onStart → onResume
// (View recreated!)
```

### Common Mistakes

```kotlin
// ❌ WRONG: Accessing view in onCreate
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    view?.findViewById<TextView>(R.id.text)  // view is null!
}

// ✅ CORRECT: Access view in onViewCreated
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    view.findViewById<TextView>(R.id.text).text = "Hello"
}

// ❌ WRONG: Not clearing binding
override fun onDestroyView() {
    super.onDestroyView()
    // Memory leak!
}

// ✅ CORRECT: Clear binding
override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

---

## Follow-ups

- What happens to Fragment lifecycle when Activity goes to background?
- How does setMaxLifecycle() affect Fragment lifecycle?
- When should you use viewLifecycleOwner vs Fragment's lifecycle?
- What lifecycle callbacks are called during configuration changes?
- How do DialogFragment and BottomSheetFragment lifecycles differ?

## References

- [Android Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Fragment Lifecycle API](https://developer.android.com/reference/androidx/fragment/app/Fragment)
- [ViewLifecycleOwner](https://developer.android.com/reference/androidx/lifecycle/ViewLifecycleOwner)

## Related Questions

### Prerequisites
- [[q-android-project-parts--android--easy]] - Basic Android components

### Related
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment-Activity relationship
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle details
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Fragment use cases

### Advanced
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Fragment architecture
- [[q-fragments-and-activity-relationship--android--hard]] - Deep dive into relationship
