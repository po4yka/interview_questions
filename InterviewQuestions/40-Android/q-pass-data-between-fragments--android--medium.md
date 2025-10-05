---
id: 202510031401
title: How to pass data from one fragment to another / Как передавать данные из одного фрагмента в другой
aliases: []

# Classification
topic: android
subtopics: [android, ui, fragments]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/451
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-fragments
  - c-android-viewmodel
  - c-android-bundle

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [fragments, bundle, viewmodel, difficulty/medium, easy_kotlin, lang/ru, android/fragments, android/ui]
---

# Question (EN)
> How to pass data from one fragment to another

# Вопрос (RU)
> Как передавать данные из одного фрагмента в другой

---

## Answer (EN)

There are several approaches to passing data between fragments in Android. The key principle is that fragments should not communicate directly with each other, but rather through intermediaries or shared state.

### 1. Using Bundle and Fragment Arguments

This is the traditional approach for passing data when creating a new fragment instance.

```kotlin
// Creating fragment with data
companion object {
    private const val ARG_USER_ID = "user_id"
    private const val ARG_USER_NAME = "user_name"

    fun newInstance(userId: Int, userName: String): FragmentB {
        return FragmentB().apply {
            arguments = Bundle().apply {
                putInt(ARG_USER_ID, userId)
                putString(ARG_USER_NAME, userName)
            }
        }
    }
}

// Receiving data in target fragment
class FragmentB : Fragment() {
    private var userId: Int = 0
    private var userName: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            userId = it.getInt(ARG_USER_ID)
            userName = it.getString(ARG_USER_NAME)
        }
    }
}
```

### 2. Using Shared ViewModel (Recommended)

ViewModel provides safe and efficient state management, especially when working with fragment lifecycle.

```kotlin
// Shared ViewModel scoped to Activity
class SharedDataViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun updateUser(user: User) {
        _userData.value = user
    }
}

// Fragment A - sends data
class FragmentA : Fragment() {
    private val sharedViewModel: SharedDataViewModel by activityViewModels()

    private fun sendData() {
        val user = User(id = 1, name = "John")
        sharedViewModel.updateUser(user)
    }
}

// Fragment B - receives data
class FragmentB : Fragment() {
    private val sharedViewModel: SharedDataViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.userData.observe(viewLifecycleOwner) { user ->
            // Update UI with user data
            updateUI(user)
        }
    }
}
```

### 3. Using Fragment Result API

Modern approach introduced in AndroidX Fragment 1.3.0 for one-time data passing.

```kotlin
// Fragment A - sends result
class FragmentA : Fragment() {
    private fun sendResult() {
        val result = Bundle().apply {
            putString("key", "value")
        }
        setFragmentResult("requestKey", result)
    }
}

// Fragment B - receives result
class FragmentB : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setFragmentResultListener("requestKey") { _, bundle ->
            val result = bundle.getString("key")
            // Use the result
        }
    }
}
```

### 4. Using Interfaces (Traditional Pattern)

Communication through parent Activity via interfaces.

```kotlin
// Define interface
interface DataPassListener {
    fun onDataPassed(data: String)
}

// Fragment A
class FragmentA : Fragment() {
    private var listener: DataPassListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)
        listener = context as? DataPassListener
    }

    private fun sendData() {
        listener?.onDataPassed("Some data")
    }
}

// Activity implements interface
class MainActivity : AppCompatActivity(), DataPassListener {
    override fun onDataPassed(data: String) {
        val fragmentB = supportFragmentManager
            .findFragmentByTag("FragmentB") as? FragmentB
        fragmentB?.receiveData(data)
    }
}
```

### Best Practices

1. **Use ViewModel** for shared state between fragments
2. **Use Bundle** for initial fragment configuration
3. **Use Fragment Result API** for one-time events
4. **Avoid direct references** between fragments
5. **Consider Navigation Component** SafeArgs for type-safe argument passing

## Ответ (RU)

Для передачи данных между фрагментами в Android можно использовать Bundle, передавая данные через методы setArguments() и getArguments(). Также можно использовать интерфейсы или ViewModel, чтобы организовать взаимодействие между фрагментами через Activity. ViewModel обеспечивает безопасное и эффективное управление состоянием, особенно при работе с жизненным циклом фрагментов.

---

## Follow-ups
- How does the Fragment Result API differ from ViewModel for data passing?
- What are the lifecycle implications of using activityViewModels() vs viewModels()?
- How do you handle complex object passing with Navigation Component SafeArgs?

## References
- [[c-android-fragments]]
- [[c-android-viewmodel]]
- [[c-android-bundle]]
- [[c-android-livedata]]
- [[moc-android]]

## Related Questions
- [[q-how-do-fragments-exist-and-what-are-they-attached-to-in-activity--android--hard]]
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]
- [[q-viewmodel-pattern--android--easy]]
