---
id: android-300
title: How To Pass Data From One Fragment To Another / Как передавать данные из одного фрагмента в другой
aliases: [Fragment Communication, Pass Data Between Fragments]
topic: android
subtopics: [architecture-mvvm, fragment, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-fragments
  - q-fragment-basics--android--easy
  - q-fragment-vs-activity-lifecycle--android--medium
  - q-how-can-data-be-saved-beyond-the-fragment-scope--android--medium
  - q-save-data-outside-fragment--android--medium
  - q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-mvvm, android/fragment, android/lifecycle, difficulty/medium]
sources: []

date created: Saturday, November 1st 2025, 12:46:54 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---
# Вопрос (RU)
> Как передавать данные из одного фрагмента в другой?

# Question (EN)
> How to pass data from one fragment to another?

## Ответ (RU)

Передача данных между фрагментами может быть реализована несколькими способами. Важно помнить, что фрагменты не должны напрямую обмениваться данными друг с другом — они должны общаться через родительскую `Activity`, общий [[c-viewmodel]] или использовать API навигации (arguments, FragmentResult).

### Основные Подходы

**1. Shared `ViewModel` (Рекомендуется)**

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

**2. `Bundle` и Arguments (включая Safe Args / Navigation)**

Передача данных при создании фрагмента (базовый способ, также используется внутри Navigation Component через arguments/Safe Args):

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

**3. FragmentResult API (Рекомендуется для одноразовой передачи результата)**

Подходит для передачи результата от одного фрагмента другому без shared `ViewModel` и без жёсткой связанности. Работает между фрагментами, которые используют один и тот же `FragmentManager`.

```kotlin
// Fragment A — отправляет результат
class FragmentA : Fragment() {
    fun sendResult() {
        parentFragmentManager.setFragmentResult(
            "requestKey",
            bundleOf("KEY_DATA" to "Data from Fragment A")
        )
    }
}

// Fragment B — подписывается на результат
class FragmentB : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        parentFragmentManager.setFragmentResultListener(
            "requestKey",
            this
        ) { _, bundle ->
            val data = bundle.getString("KEY_DATA")
            // ✅ Обрабатываем результат
        }
    }
}
```

**4. `Activity` как посредник (Не рекомендуется)**

Этот подход работает, но создаёт жёсткую связанность между `Activity` и конкретными фрагментами. Его лучше избегать, если есть возможность использовать Shared `ViewModel`, FragmentResult API или arguments.

```kotlin
// ⚠️ Не рекомендуется — создаёт связанность
interface OnDataPassListener {
    fun onDataPass(data: String)
}

class MainActivity : AppCompatActivity(), OnDataPassListener {
    override fun onDataPass(data: String) {
        val fragmentB = supportFragmentManager.findFragmentByTag("B") as? FragmentB
        fragmentB?.receiveData(data)  // ⚠️ Прямая связь Activity → Fragment
    }
}

class FragmentB : Fragment() {
    fun receiveData(data: String) {
        // ✅ Обработка полученных данных
    }
}
```

### Когда Использовать

| Подход | Когда использовать |
|--------|-------------------|
| **Shared `ViewModel`** | Динамический обмен данными между фрагментами, совместно используемое состояние |
| **`Bundle` Arguments** | Передача данных при создании фрагмента или при навигации (в т.ч. через Navigation Component / Safe Args) |
| **FragmentResult API** | Одноразовые результаты между фрагментами без shared `ViewModel` |
| **`Activity` посредник** | Работает, но не рекомендуется из-за сильной связанности |

## Дополнительные Вопросы (RU)

- Как отличается жизненный цикл общего `ViewModel` от жизненного цикла фрагмента?
- Что произойдет, если передавать большой объём данных через `Bundle` arguments?
- Как обрабатывать коммуникацию фрагмент-фрагмент в Navigation Component?
- Когда лучше использовать FragmentResult API вместо shared `ViewModel`?
- Как тестировать коммуникацию фрагментов с использованием shared `ViewModel`?

## Ссылки (RU)

- [[c-viewmodel]]
- [[c-fragments]]
- [[c-activity-lifecycle]]
- [`ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)

## Связанные Вопросы (RU)

### База (Проще)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - `Fragment`
- [[q-fragment-basics--android--easy]] - `Fragment`

### Похожие (Средней сложности)
- [[q-save-data-outside-fragment--android--medium]] - `Fragment`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment`
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - `Fragment`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Fragment`
- [[q-how-to-pass-parameters-to-a-fragment--android--easy]] - `Fragment`

### Продвинутое (Сложнее)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - `Fragment`

## Answer (EN)

Passing data between fragments can be implemented in several ways. It's important to remember that fragments should not directly exchange data with each other — they should communicate via their parent `Activity`, a shared [[c-viewmodel]], or navigation APIs (arguments, FragmentResult).

### Main Approaches

**1. Shared `ViewModel` (Recommended)**

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

**2. `Bundle` and Arguments (including Safe Args / Navigation)**

Passing data when creating a fragment (basic approach, also used internally by Navigation Component via arguments/Safe Args):

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

**3. FragmentResult API (Recommended for one-time results)**

Good for passing a result from one fragment to another without a shared `ViewModel` and without tight coupling. Works between fragments that use the same `FragmentManager`.

```kotlin
// Fragment A - send result
class FragmentA : Fragment() {
    fun sendResult() {
        parentFragmentManager.setFragmentResult(
            "requestKey",
            bundleOf("KEY_DATA" to "Data from Fragment A")
        )
    }
}

// Fragment B - listen for result
class FragmentB : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        parentFragmentManager.setFragmentResultListener(
            "requestKey",
            this
        ) { _, bundle ->
            val data = bundle.getString("KEY_DATA")
            // ✅ Handle result
        }
    }
}
```

**4. `Activity` as Intermediary (Not recommended)**

This approach works but introduces tight coupling between the `Activity` and specific fragments. Prefer Shared `ViewModel`, FragmentResult API, or arguments when possible.

```kotlin
// ⚠️ Not recommended - creates tight coupling
interface OnDataPassListener {
    fun onDataPass(data: String)
}

class MainActivity : AppCompatActivity(), OnDataPassListener {
    override fun onDataPass(data: String) {
        val fragmentB = supportFragmentManager.findFragmentByTag("B") as? FragmentB
        fragmentB?.receiveData(data)  // ⚠️ Direct coupling Activity → Fragment
    }
}

class FragmentB : Fragment() {
    fun receiveData(data: String) {
        // ✅ Handle received data
    }
}
```

### When to Use

| Approach | When to use |
|----------|-------------|
| **Shared `ViewModel`** | Dynamic data exchange between fragments, shared state |
| **`Bundle` Arguments** | Passing data on fragment creation or navigation (incl. Navigation Component / Safe Args) |
| **FragmentResult API** | One-time results between fragments without shared `ViewModel` |
| **`Activity` intermediary** | Works but not recommended due to tight coupling |

## Follow-ups

- How does shared `ViewModel` lifecycle differ from fragment lifecycle?
- What happens if you pass large data via `Bundle` arguments?
- How to handle fragment-to-fragment communication in Navigation Component?
- When should you use FragmentResult API instead of shared `ViewModel`?
- How to test fragment communication with shared `ViewModel`?

## References

- [[c-viewmodel]]
- [[c-fragments]]
- [[c-activity-lifecycle]]
- [`ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - `Fragment`
- [[q-fragment-basics--android--easy]] - `Fragment`

### Related (Medium)
- [[q-save-data-outside-fragment--android--medium]] - `Fragment`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment`
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - `Fragment`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Fragment`
- [[q-how-to-pass-parameters-to-a-fragment--android--easy]] - `Fragment`

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - `Fragment`
