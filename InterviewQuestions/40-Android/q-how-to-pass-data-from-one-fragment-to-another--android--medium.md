---
id: "20251015082237468"
title: "How To Pass Data From One Fragment To Another / Как передать данные из одного Fragment в другой"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - android/fragments
  - android/views
  - communication
  - fragments
  - ui
  - viewmodel
  - views
---
# Как передавать данные из одного фрагмента в другой?

**English**: How to pass data from one fragment to another?

## Answer (EN)
Passing data between fragments can be implemented in several ways. It's important to remember that fragments should not directly exchange data with each other. Instead, they should communicate through their parent activity or use a shared ViewModel.

### Main Approaches to Passing Data Between Fragments

#### 1. Using Parent Activity as Intermediary

Fragments communicate through the parent activity using interfaces or activity methods.

```kotlin
// Define interface in fragment
interface OnDataPassListener {
    fun onDataPass(data: String)
}

// Fragment A
class FragmentA : Fragment() {
    private var listener: OnDataPassListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)
        listener = context as? OnDataPassListener
    }

    fun sendData() {
        listener?.onDataPass("Data from Fragment A")
    }
}

// Activity implements interface
class MainActivity : AppCompatActivity(), OnDataPassListener {
    override fun onDataPass(data: String) {
        val fragmentB = supportFragmentManager.findFragmentByTag("FragmentB") as? FragmentB
        fragmentB?.receiveData(data)
    }
}

// Fragment B receives data
class FragmentB : Fragment() {
    fun receiveData(data: String) {
        // Use the data
    }
}
```

#### 2. Using Shared ViewModel (Recommended)

Create a ViewModel containing LiveData or other observables for data storage. Access this ViewModel from both fragments through their parent activity.

```kotlin
// Shared ViewModel
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
        sharedViewModel.setData("Data from Fragment A")
    }
}

// Fragment B - receives data
class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.selectedData.observe(viewLifecycleOwner) { data ->
            // Use the data
        }
    }
}
```

#### 3. Using Bundle and Fragment Arguments

Create a Bundle and place data in it, use setArguments() to pass the Bundle to a new fragment instance. In the target fragment, extract data from the received Bundle using getArguments().

```kotlin
// Creating fragment with arguments
fun createFragmentWithData(data: String): FragmentB {
    val fragment = FragmentB()
    val bundle = Bundle().apply {
        putString("KEY_DATA", data)
    }
    fragment.arguments = bundle
    return fragment
}

// Receiving data in target fragment
class FragmentB : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val data = arguments?.getString("KEY_DATA")
        // Use the data
    }
}

// Usage
val fragmentB = createFragmentWithData("My data")
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragmentB)
    .commit()
```

### Best Practice

The choice of method depends on the specific use case. Modern development often recommends using **ViewModel** for data exchange between fragments, as it promotes creating a reliable and testable application architecture.

## Ответ (RU)
Передача данных между фрагментами может быть реализована несколькими способами. Важно помнить что фрагменты не должны напрямую обмениваться данными друг с другом. Вместо этого они должны общаться через свою родительскую активность или использовать общий ViewModel. Основные подходы к передаче данных между фрагментами: использование родительской активности как посредника через интерфейс или методы активности. Использование ViewModel для общения между фрагментами. Создайте ViewModel содержащую LiveData или другие обсерваблы для хранения данных. Доступ к этой ViewModel должен быть получен из обоих фрагментов через их родительскую активность. Использование Bundle и аргументов фрагмента для передачи данных при создании нового экземпляра фрагмента. Создайте Bundle и поместите в него данные используйте setArguments для передачи Bundle новому экземпляру фрагмента. В целевом фрагменте извлеките данные из полученного Bundle с помощью метода getArguments. Выбор метода зависит от конкретного случая использования в современной разработке часто рекомендуется использовать ViewModel для обмена данными между фрагментами так как это способствует созданию надежной и тестируемой архитектуры приложения


---

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
