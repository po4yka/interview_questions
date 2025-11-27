---
id: android-171
title: Single Activity Pros Cons / Преимущества и недостатки Single Activity
aliases: [Single Activity Pros Cons, Преимущества и недостатки Single Activity]
topic: android
subtopics:
  - activity
  - ui-navigation
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-activity
  - c-compose-navigation
  - q-activity-lifecycle-methods--android--medium
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-single-activity-approach--android--medium
  - q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium
  - q-what-is-activity-and-what-is-it-used-for--android--medium
  - q-why-are-fragments-needed-if-there-is-activity--android--hard
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/activity, android/ui-navigation, difficulty/medium, navigation, single-activity, viewmodel]

date created: Saturday, November 1st 2025, 12:47:04 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)

> Какие у подхода Single `Activity` этого подхода плюсы и минусы?

# Question (EN)

> What are the pros and cons of the Single `Activity` approach?

## Ответ (RU)

**Подход Single `Activity`** — использование **одной `Activity`** (как корневой контейнер) для всего приложения, где большинство/все экраны представлены как **`Fragment`** и/или destinations навигации. Это противоположность традиционному подходу с множеством `Activity`, где каждый экран — отдельная `Activity`.

### Плюсы (Advantages)

1. **Упрощенная навигация** — можно использовать `NavController` и навигационные графы вместо ручного управления `Intent` и `FragmentTransaction` для большинства кейсов.
2. **Общий `ViewModel`** — легко делиться данными между связанными экранами через `activityViewModels()` или scoped `ViewModel` в `NavGraph`, без сериализации данных в `Intent`.
3. **Общие UI элементы** — общий `Toolbar`, `BottomNavigationView` и другие контейнеры живут в `Activity` и не пересоздаются при переходах между фрагментами.
4. **Лучшие анимации** — проще делать плавные переходы и shared element transitions между фрагментами внутри одной `Activity`.
5. **Менее затратные переходы** — нет накладных расходов полного создания новой `Activity` (новый `Window`, тема, дополнительные lifecycle callbacks) при каждом переходе; переходы чаще ограничиваются операциями с фрагментами.
6. **Deep links** — с Navigation Component проще конфигурировать и обрабатывать deep links в рамках одной `Activity` (но требуется корректная настройка графа и `intent-filter`).
7. **Централизованный подход к состоянию** — проще проектировать согласованный state management (например, через общие `ViewModel` и `SavedStateHandle` для конкретных destination), чем при разбросе по множеству `Activity`.

**Пример навигации:**
```kotlin
// ✅ Single Activity - навигация через NavController
navController.navigate(R.id.profileFragment, bundleOf("userId" to userId))

// ➜ Multi-Activity - через Intent (не обязательно "сложнее", но более многословно)
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("userId", userId)
startActivity(intent)
```

**Общий `ViewModel`:**
```kotlin
// ✅ Легко делиться данными между фрагментами
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun updateUser(user: User) {
        sharedViewModel.userData.value = user // FragmentB сможет наблюдать изменения
    }
}

class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels() // тот же instance
}
```

### Минусы (Disadvantages)

1. **Сложный lifecycle фрагментов** — больше callback-методов (`onCreateView`, `onViewCreated`, `onDestroyView`, `onDetach`), два уровня lifecycle (`Fragment` и его `View`), легко ошибиться.
2. **Риск утечек памяти** — при использовании ViewBinding/DataBinding во фрагментах нужно очищать ссылки в `onDestroyView()`, иначе возможны утечки.
3. **Сложность FragmentManager** — ручное управление back stack'ом и транзакциями может быть запутанным (особенно без Navigation Component).
4. **State loss проблемы** — `IllegalStateException` при commit после `onSaveInstanceState()` остаётся типичной проблемой для транзакций фрагментов; это особенно критично в Single `Activity`, где весь UI завязан на фрагменты.
5. **Вложенные фрагменты** — различия между `childFragmentManager` и `parentFragmentManager` усложняют архитектуру и могут приводить к ошибкам.
6. **Сложность тестирования** — UI-тесты фрагментов требуют дополнительного setup (`FragmentScenario`, `launchFragmentInContainer`), по сравнению с прямым тестированием одной отдельной `Activity`.
7. **Обработка кнопки "Назад"** — требуется аккуратная работа с `OnBackPressedDispatcher` и навигационным стеком, особенно при сложных графах.

**ViewBinding: пример утечки и правильного подхода:**
```kotlin
// ❌ Потенциальная утечка памяти - binding хранится как lateinit и не очищается
class MyFragment : Fragment() {
    private lateinit var binding: FragmentMyBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    // Если не обнулить binding в onDestroyView(), View может утекать
}

// ✅ Правильный подход
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // очищаем ссылку на View
    }
}
```

### Сравнение

| Аспект | Single `Activity` | Multi-`Activity` |
|--------|----------------|----------------|
| Навигация | Единый граф, `NavController`, фрагменты; меньше явных `Intent` | Переходы через `Intent`, каждый экран в своей `Activity` |
| Обмен данными | Shared `ViewModel`, NavGraph-scoped `ViewModel`, аргументы destination | `Intent` extras, `startActivityForResult` (устаревший), `ActivityResultAPI` |
| Память | Нет накладных расходов множества Activities; но важно контролировать количество активных фрагментов и их `View` | `Activity` изолированы; общий overhead на несколько Activities, но управление проще |
| Кривая обучения | Более сложный lifecycle фрагментов и навигации | Проще понять lifecycle `Activity` |
| Утечки памяти | Выше риск при неправильной работе с ViewBinding/фрагментами | Обычно меньше точек для утечек UI через binding |
| Тестирование | Может требовать больше конфигурации для фрагментов и навигатора | Тесты отдельных `Activity` относительно прямолинейны |

### Когда Использовать

**Хорошо для:**
- Приложений с общими UI элементами (toolbar, bottom nav, общий layout-каркас).
- Сложной иерархической навигации с общим состоянием между несколькими экранами.
- Приложений, использующих Jetpack Navigation и фрагменты, где единый контейнер упрощает управление стеком.

**Не идеально для:**
- Простых приложений с малым количеством экранов, где одна-две `Activity` проще и прозрачнее.
- Крупных legacy-кодовых баз, где миграция на Single `Activity` слишком затратна.
- Команд, незнакомых с `Fragment` lifecycle и Navigation Component (высокий риск ошибок).

**Вердикт:**
Single `Activity` — рекомендованный и распространённый подход для современных фрагмент-ориентированных Android-приложений (особенно в связке с Navigation Component), но он не является единственно "правильным" стандартом. Важно понимать сложность lifecycle фрагментов, избегать утечек памяти и выбирать архитектуру исходя из размера приложения и опыта команды.

## Answer (EN)

The **Single `Activity` approach** uses **one `Activity`** (as the root container) for the entire application, with most/all screens implemented as **Fragments** and/or navigation destinations. This contrasts with the traditional multi-`Activity` approach where each major screen is a separate `Activity`.

### Advantages (Pros)

1. **Simplified navigation** — you can use `NavController` and navigation graphs instead of manually wiring `Intent` and `FragmentTransaction` for most navigation flows.
2. **Shared `ViewModel`** — easy data sharing between related screens via `activityViewModels()` or NavGraph-scoped ViewModels, without passing everything through `Intent` extras.
3. **Shared UI elements** — common `Toolbar`, `BottomNavigationView`, and other containers live in the `Activity` and are not recreated when switching between fragments.
4. **Better animations** — smoother transitions and shared element transitions are easier to implement between fragments within one `Activity`.
5. **Lower transition overhead** — no full `Activity` creation (`Window`, theme inflation, additional lifecycle callbacks) on every navigation step; many transitions are just fragment operations.
6. **Deep links** — with Navigation Component, configuring and handling deep links into specific destinations in a single host `Activity` becomes easier (assuming proper graph and `intent-filter` setup).
7. **Centralized state patterns** — it’s easier to design consistent state management (e.g., shared ViewModels and `SavedStateHandle` per destination) than when logic is scattered across many Activities.

**Navigation example:**
```kotlin
// ✅ Single Activity - navigation via NavController
navController.navigate(R.id.profileFragment, bundleOf("userId" to userId))

// ➜ Multi-Activity - via Intent (not inherently "worse", but more verbose)
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("userId", userId)
startActivity(intent)
```

**Shared `ViewModel`:**
```kotlin
// ✅ Easy data sharing between fragments
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun updateUser(user: User) {
        sharedViewModel.userData.value = user // FragmentB can observe the update
    }
}

class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels() // same instance
}
```

### Disadvantages (Cons)

1. **`Fragment` lifecycle complexity** — more callbacks (`onCreateView`, `onViewCreated`, `onDestroyView`, `onDetach`), two lifecycles (`Fragment` and its `View`); easier to make mistakes.
2. **Memory leak risk** — with ViewBinding/DataBinding in Fragments you must clear references in `onDestroyView()`, otherwise you can leak Views and `Context`.
3. **FragmentManager complexity** — manual back stack and transaction management can be tricky (especially without Navigation Component).
4. **State loss issues** — committing fragment transactions after `onSaveInstanceState()` can cause `IllegalStateException`; this is a general fragment/navigation concern and becomes more visible when all navigation relies on a single host `Activity`.
5. **Nested fragments** — differences between `childFragmentManager` and `parentFragmentManager` make architecture more complex and error-prone.
6. **Testing complexity** — fragment UI tests often need extra setup (`FragmentScenario`, `launchFragmentInContainer`) compared to straightforward single-`Activity` tests.
7. **Back button handling** — requires careful use of `OnBackPressedDispatcher` and correct integration with the navigation stack for complex graphs.

**ViewBinding leak example and correct pattern:**
```kotlin
// ❌ Potential memory leak - binding kept as lateinit and never cleared
class MyFragment : Fragment() {
    private lateinit var binding: FragmentMyBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    // If binding is not cleared in onDestroyView(), the View can leak
}

// ✅ Correct approach
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // clear reference to the View hierarchy
    }
}
```

### Comparison

| Aspect | Single `Activity` | Multi-`Activity` |
|--------|----------------|----------------|
| Navigation | Centralized graph, `NavController`, fragment-based; fewer explicit `Intents` | Navigation via `Intent` between Activities |
| Data sharing | Shared / NavGraph-scoped ViewModels, destination arguments | `Intent` extras, `ActivityResult` APIs |
| Memory | No repeated `Activity` setup; must manage number of active Fragments/Views | Separate Activities; some extra overhead per `Activity` but simpler isolation |
| Learning curve | Steeper: `Fragment` + Navigation lifecycles | Simpler: `Activity` lifecycle only |
| Memory leaks | Higher risk if `Fragment`/ViewBinding handled incorrectly | Fewer common UI-binding leak patterns |
| Testing | `Fragment` + navigation tests may need more setup | `Activity`-based tests are relatively straightforward |

### When to Use

**Good fit for:**
- Apps with shared UI elements (toolbar, bottom navigation, shared layout shell).
- Complex, hierarchical navigation flows with shared state between multiple screens.
- Apps using Jetpack Navigation with Fragments, where a single host `Activity` simplifies stack handling.

**Not ideal for:**
- Simple apps with few screens where one or a couple of Activities is clearer and sufficient.
- Large legacy codebases where migrating to a Single `Activity` architecture is too costly.
- Teams unfamiliar with `Fragment` lifecycle and Navigation Component (higher risk of bugs).

**Verdict:**
Single `Activity` is a widely recommended approach for modern `Fragment`-based Android apps (especially together with Navigation Component), but it is not the only valid architecture. Choose it when it matches your app’s complexity and your team’s expertise, and be mindful of `Fragment` lifecycle and memory management pitfalls.

---

## Follow-ups

- How to handle configuration changes in Single `Activity` with Fragments?
- What are the memory implications of keeping Fragments in back stack?
- How does Navigation Component handle deep links and conditional navigation?
- What are best practices for ViewBinding cleanup in Fragments?
- How to implement nested navigation graphs in Single `Activity`?

## References

- Official Android documentation: Navigation Component
- Official Android documentation: `Fragment` best practices
- Official Android documentation: Single `Activity` architecture guide

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-activity]]

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] — `Activity` lifecycle understanding needed

### Related
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]] — `Activity` fundamentals

### Advanced
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] — Deep dive into `Fragment` architecture
