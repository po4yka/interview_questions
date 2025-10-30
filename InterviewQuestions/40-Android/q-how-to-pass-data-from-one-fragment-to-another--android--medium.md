---
id: 20251012-1227189
title: How To Pass Data From One Fragment To Another / Как передать данные из одного Fragment в другой
aliases: [Pass Data Between Fragments, Fragment Communication, Передача данных между фрагментами]
topic: android
subtopics: [fragment, lifecycle, architecture-mvvm]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-fragment-basics--android--easy
  - q-save-data-outside-fragment--android--medium
  - q-fragment-vs-activity-lifecycle--android--medium
created: 2025-10-15
updated: 2025-10-30
tags: [android/fragment, android/lifecycle, android/architecture-mvvm, difficulty/medium]
sources: []
date created: Thursday, October 30th 2025, 12:51:22 pm
date modified: Thursday, October 30th 2025, 12:53:12 pm
---

# Вопрос (RU)
> Как передавать данные из одного фрагмента в другой?

# Question (EN)
> How to pass data from one fragment to another?

## Ответ (RU)

Передача данных между фрагментами может быть реализована несколькими способами. Важно помнить, что фрагменты не должны напрямую обмениваться данными друг с другом — они должны общаться через родительскую Activity или использовать общий [[c-viewmodel]].

### Основные Подходы

**1. Shared ViewModel (Рекомендуется)**

Современный подход через [[c-viewmodel]], доступный обоим фрагментам через `activityViewModels()`:

```kotlin
// ✅ Shared ViewModel для обмена данными
class SharedViewModel : ViewModel() {
    private val _selectedData = MutableLiveData<String>()
    val selectedData: LiveData<String> = _selectedData

    fun setData(data: String) {
        _selectedData.value = data
    }
}

// Fragment A — отправляет данные
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun sendData() {
        sharedViewModel.setData("Data from Fragment A")  // ✅ Устанавливаем данные
    }
}

// Fragment B — получает данные
class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.selectedData.observe(viewLifecycleOwner) { data ->
            // ✅ Реагируем на изменения данных
        }
    }
}
```

**2. Bundle и Arguments**

Передача данных при создании фрагмента:

```kotlin
// ✅ Создание фрагмента с данными
fun createFragmentWithData(data: String): FragmentB {
    return FragmentB().apply {
        arguments = Bundle().apply {
            putString("KEY_DATA", data)
        }
    }
}

// FragmentB — получение данных
class FragmentB : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val data = arguments?.getString("KEY_DATA")  // ✅ Извлекаем данные
    }
}
```

**3. Activity как посредник (Устаревший)**

```kotlin
// ❌ Устаревший подход — создаёт связанность
interface OnDataPassListener {
    fun onDataPass(data: String)
}

class MainActivity : AppCompatActivity(), OnDataPassListener {
    override fun onDataPass(data: String) {
        val fragmentB = supportFragmentManager.findFragmentByTag("B") as? FragmentB
        fragmentB?.receiveData(data)  // ❌ Прямая связь Activity → Fragment
    }
}
```

### Когда Использовать

| Подход | Когда использовать |
|--------|-------------------|
| **Shared ViewModel** | Динамический обмен данными между фрагментами |
| **Bundle Arguments** | Передача данных при создании фрагмента |
| **Activity посредник** | Устаревший подход, избегать |

## Answer (EN)

Passing data between fragments can be implemented in several ways. It's important to remember that fragments should not directly exchange data with each other — they should communicate through their parent Activity or use a shared [[c-viewmodel]].

### Main Approaches

**1. Shared ViewModel (Recommended)**

Modern approach using [[c-viewmodel]] accessible to both fragments via `activityViewModels()`:

```kotlin
// ✅ Shared ViewModel for data exchange
class SharedViewModel : ViewModel() {
    private val _selectedData = MutableLiveData<String>()
    val selectedData: LiveData<String> = _selectedData

    fun setData(data: String) {
        _selectedData.value = data
    }
}

// Fragment A - sends data
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun sendData() {
        sharedViewModel.setData("Data from Fragment A")  // ✅ Set data
    }
}

// Fragment B - receives data
class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.selectedData.observe(viewLifecycleOwner) { data ->
            // ✅ React to data changes
        }
    }
}
```

**2. Bundle and Arguments**

Passing data when creating a fragment:

```kotlin
// ✅ Create fragment with data
fun createFragmentWithData(data: String): FragmentB {
    return FragmentB().apply {
        arguments = Bundle().apply {
            putString("KEY_DATA", data)
        }
    }
}

// FragmentB - receive data
class FragmentB : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val data = arguments?.getString("KEY_DATA")  // ✅ Extract data
    }
}
```

**3. Activity as Intermediary (Deprecated)**

```kotlin
// ❌ Deprecated approach - creates tight coupling
interface OnDataPassListener {
    fun onDataPass(data: String)
}

class MainActivity : AppCompatActivity(), OnDataPassListener {
    override fun onDataPass(data: String) {
        val fragmentB = supportFragmentManager.findFragmentByTag("B") as? FragmentB
        fragmentB?.receiveData(data)  // ❌ Direct coupling Activity → Fragment
    }
}
```

### When to Use

| Approach | When to use |
|----------|-------------|
| **Shared ViewModel** | Dynamic data exchange between fragments |
| **Bundle Arguments** | Passing data when creating fragment |
| **Activity intermediary** | Deprecated, avoid |

## Follow-ups

- How does shared ViewModel lifecycle differ from fragment lifecycle?
- What happens if you pass large data via Bundle arguments?
- How to handle fragment-to-fragment communication in Navigation Component?
- When should you use FragmentResult API instead of shared ViewModel?
- How to test fragment communication with shared ViewModel?

## References

- [[c-viewmodel]]
- [[c-fragments]]
- [[c-activity-lifecycle]]
- https://developer.android.com/topic/libraries/architecture/viewmodel

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment
- [[q-fragment-basics--android--easy]] - Fragment

### Related (Medium)
- [[q-save-data-outside-fragment--android--medium]] - Fragment
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment
- [[q-how-to-pass-parameters-to-a-fragment--android--easy]] - Fragment

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment
