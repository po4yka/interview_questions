---
id: android-386
title: "Fragments And Activity Relationship / Взаимосвязь Фрагментов И Activity"
aliases: ["Fragment Lifecycle Dependency", "Fragments And Activity Relationship", "Взаимосвязь Фрагментов И Activity", "Зависимость жизненного цикла фрагмента"]
topic: android
subtopics: [architecture-mvvm, fragment, lifecycle]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-can-a-service-communicate-with-the-user--android--medium, q-how-did-fragments-appear-and-why-were-they-started-to-be-used--android--hard, q-sharedpreferences-commit-vs-apply--android--easy]
created: 2025-10-15
updated: 2025-10-28
tags: [android, android/architecture-mvvm, android/fragment, android/lifecycle, difficulty/hard, fragments, ui]
date created: Tuesday, October 28th 2025, 7:39:14 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Как существуют и к чему привязаны фрагменты в Activity?

# Question (EN)

How do fragments exist and what are they attached to in Activity?

---

## Ответ (RU)

Фрагменты в Android существуют как модульные компоненты, привязанные к Activity через **FragmentManager**. Они размещаются в **ViewGroup контейнерах** и имеют собственный жизненный цикл, синхронизированный с Activity.

### Механизм Привязки

Фрагменты зависят от Activity для:
- **Контекста**: доступ через `requireContext()`, `requireActivity()`
- **Ресурсов**: строки, drawable, системные сервисы
- **Жизненного цикла**: синхронизация с Activity
- **ViewGroup**: физическая точка размещения в UI

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Фрагмент добавляется в ViewGroup контейнер
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, MyFragment())
            .commit()
    }
}

class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // ✅ Доступ к Activity context после привязки
    }

    override fun onDetach() {
        super.onDetach()
        // ❌ После этого контекст Activity недоступен
    }
}
```

### Динамическое Управление

Фрагменты можно добавлять, заменять и удалять во время выполнения:

```kotlin
// Замена с поддержкой back stack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, SecondFragment())
    .addToBackStack(null)  // ✅ Добавляет в историю навигации
    .commit()

// ❌ Неправильно - без проверки существования
supportFragmentManager.findFragmentByTag("TAG")?.let {
    // Может быть null
}
```

### Коммуникация Через Activity

Фрагменты взаимодействуют через родительскую Activity:

```kotlin
// ✅ Современный подход - ViewModel
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<String>()
    val selectedItem: LiveData<String> = _selectedItem
}

// Fragment A
class ListFragment : Fragment() {
    private val viewModel: SharedViewModel by activityViewModels()

    fun selectItem(item: String) {
        viewModel.setItem(item)
    }
}

// Fragment B
class DetailFragment : Fragment() {
    private val viewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            updateContent(item)
        }
    }
}
```

### Ключевые Характеристики

1. **Модульность**: переиспользуются в разных activities
2. **Зависимость от контекста**: требуют Activity для ресурсов
3. **Динамичность**: управляются во время выполнения
4. **Back stack**: поддержка навигации

## Answer (EN)

Fragments in Android exist as modular components attached to an Activity via **FragmentManager**. They reside in **ViewGroup containers** and have their own lifecycle synchronized with the Activity.

### Attachment Mechanism

Fragments depend on Activity for:
- **Context**: accessed via `requireContext()`, `requireActivity()`
- **Resources**: strings, drawables, system services
- **Lifecycle**: synchronized with Activity
- **ViewGroup**: physical placement point in UI

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Fragment added to ViewGroup container
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, MyFragment())
            .commit()
    }
}

class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // ✅ Access to Activity context after attachment
    }

    override fun onDetach() {
        super.onDetach()
        // ❌ After this, Activity context is unavailable
    }
}
```

### Dynamic Management

Fragments can be added, replaced, and removed at runtime:

```kotlin
// Replace with back stack support
supportFragmentManager.beginTransaction()
    .replace(R.id.container, SecondFragment())
    .addToBackStack(null)  // ✅ Adds to navigation history
    .commit()

// ❌ Incorrect - without existence check
supportFragmentManager.findFragmentByTag("TAG")?.let {
    // May be null
}
```

### Communication Through Activity

Fragments communicate via the parent Activity:

```kotlin
// ✅ Modern approach - ViewModel
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<String>()
    val selectedItem: LiveData<String> = _selectedItem
}

// Fragment A
class ListFragment : Fragment() {
    private val viewModel: SharedViewModel by activityViewModels()

    fun selectItem(item: String) {
        viewModel.setItem(item)
    }
}

// Fragment B
class DetailFragment : Fragment() {
    private val viewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            updateContent(item)
        }
    }
}
```

### Key Characteristics

1. **Modular**: reusable across different activities
2. **Context-dependent**: require Activity for resources
3. **Dynamic**: managed at runtime
4. **Back stack**: navigation history support

---

## Follow-ups

- What happens to Fragment state when Activity is destroyed due to configuration change?
- How does FragmentManager handle back stack when Activity is killed by the system?
- What are the differences between `add()`, `replace()`, and `show()/hide()` for fragment transactions?
- How do you handle fragment communication in a multi-module architecture?
- What are the lifecycle differences between Fragment's View and Fragment itself?

## References

- [Android Developer Guide - Fragments](https://developer.android.com/guide/fragments)
- [Android Developer Guide - Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Android Developer Guide - FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)

---

## Related Questions

### Prerequisites
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment lifecycle basics
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle comparison
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Fragment purpose

### Related
- [[q-how-did-fragments-appear-and-why-were-they-started-to-be-used--android--hard]] - Fragment history and rationale
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Lifecycle callbacks differences

### Advanced
- Fragment state management across configuration changes
- Fragment transaction animations and transitions
- Nested fragments and child FragmentManager patterns
