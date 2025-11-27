---
id: android-386
title: Fragments And Activity Relationship / Взаимосвязь Фрагментов И Activity
aliases: [Fragment Lifecycle Dependency, Fragments And Activity Relationship, Взаимосвязь Фрагментов И Activity, Зависимость жизненного цикла фрагмента]
topic: android
subtopics:
  - fragment
  - lifecycle
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-components
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-what-are-fragments-for-if-there-is-activity--android--medium
  - q-why-are-fragments-needed-if-there-is-activity--android--hard
  - q-why-use-fragments-when-we-have-activities--android--medium
created: 2025-10-15
updated: 2025-11-10
sources:
  - "https://developer.android.com/guide/fragments"
  - "https://developer.android.com/guide/fragments/fragmentmanager"
  - "https://developer.android.com/guide/fragments/lifecycle"
tags: [android/fragment, android/lifecycle, difficulty/hard]

date created: Saturday, November 1st 2025, 12:46:50 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)
> Как существуют и к чему привязаны фрагменты в `Activity`?

# Question (EN)
> How do fragments exist and what are they attached to in `Activity`?

---

## Ответ (RU)

Фрагменты в Android существуют как модульные компоненты, обычно хостящиеся внутри `FragmentActivity`/`AppCompatActivity` и управляемые через **`FragmentManager`**. Они размещаются в **`ViewGroup`** контейнерах и имеют собственный жизненный цикл, связанный с жизненным циклом хост-`Activity` (или другого владельца, например NavHost), но не полностью автономный.

### Краткий Вариант

Фрагмент:
- всегда привязан к host-`Activity` (или другому владельцу), не может жить дольше него;
- управляется через `FragmentManager` и размещается в `ViewGroup` контейнере;
- использует контекст, ресурсы и lifecycle host-а;
- общается с другими фрагментами через `Activity` или общую `ViewModel`.

### Подробный Вариант

### Механизм Привязки

Фрагменты зависят от `Activity` (или другого host-а) для:
- **Контекста**: доступ через `requireContext()`, `requireActivity()` (или `context`/`activity` с проверкой на null)
- **Ресурсов**: строки, drawable, системные сервисы
- **Жизненного цикла**: верхняя граница — жизненный цикл хост-`Activity`; фрагмент не может жить дольше своей `Activity`
- **`ViewGroup`**: физическая точка размещения в UI (для UI-фрагментов)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Фрагмент добавляется в ViewGroup контейнер через FragmentManager
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, MyFragment())
            .commit()
    }
}

class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // ✅ Доступ к контексту host-а после onAttach
    }

    override fun onDetach() {
        super.onDetach()
        // ❌ После этого Activity/host больше не гарантированно доступен, ссылки должны быть обнулены
    }
}
```

### Динамическое Управление

Фрагменты можно добавлять, заменять и удалять во время выполнения:

```kotlin
// ✅ Замена с добавлением в back stack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, SecondFragment())
    .addToBackStack(null)  // Добавляет транзакцию в историю навигации
    .commit()

// ✅ Поиск по тэгу — результат может быть null, это нормально
val fragment = supportFragmentManager.findFragmentByTag("TAG")
if (fragment != null) {
    // Безопасная работа с найденным фрагментом
}
```

### Коммуникация Через `Activity` / Общую `ViewModel`

Фрагменты не должны напрямую жёстко зависеть друг от друга. Типичные подходы:
- через интерфейсы/коллбеки к `Activity`;
- через общую `ViewModel`, скоупленную к `Activity`.

```kotlin
// ✅ Современный подход — Shared ViewModel, скоупленная к Activity
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<String>()
    val selectedItem: LiveData<String> = _selectedItem

    fun setItem(item: String) {
        _selectedItem.value = item
    }
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

1. **Модульность**: могут переиспользоваться в разных Activities/контекстах
2. **Привязка к host-у**: требуют host (обычно `Activity`) для контекста и ресурсов; не существуют автономно
3. **Динамичность**: управляются во время выполнения через `FragmentManager`
4. **Back stack**: транзакции могут быть добавлены в back stack `FragmentManager` для навигации

### Лучшие Практики

- **Используйте `viewLifecycleOwner` для подписок, завязанных на `View`** — наблюдение `LiveData`/`Flow`, которое управляет UI.
- **Используйте `requireActivity()`/`requireContext()` только когда фрагмент гарантированно присоединён** (например, после `onAttach` и до `onDetach`); вне этого диапазона — проверяйте `isAdded` или используйте безопасные ссылки.
- **Используйте Shared `ViewModel` или чёткие интерфейсы** — для коммуникации между фрагментами без жёстких зависимостей.
- **Грамотно управляйте back stack** — осознанно решайте, какие транзакции добавлять, и используйте теги для идентификации фрагментов при необходимости.
- **Избегайте утечек памяти** — не храните ссылки на `View`/Binding/`Activity`/`Context` после `onDestroyView()`/`onDetach()`.

### Типичные Ошибки

- **Неправильный LifecycleOwner** — использование `this` (фрагмента) вместо `viewLifecycleOwner` для UI-наблюдений, что переживают пересоздание `View`.
- **Неверный scope `ViewModel`** — использование `activityViewModels()` там, где нужен `viewModels()` (или наоборот), что приводит к неожиданному времени жизни и разделению состояния, а не прямой "утечке" памяти.
- **Потеря состояния навигации** — некорректное использование `add()`/`replace()` и `addToBackStack()` (например, ожидание back-навигации без добавления в back stack).
- **Проблемы с контекстом** — доступ к `Activity`/`Context` после `onDetach()` или удержание ссылок на него.
- **Неправильное управление транзакциями** — конкурентные транзакции, игнорирование `commitNow`/`commitAllowingStateLoss` и возможной потери состояния.

## Answer (EN)

Fragments in Android exist as modular components typically hosted inside a `FragmentActivity`/`AppCompatActivity` and managed via the **`FragmentManager`**. They reside in **`ViewGroup`** containers and have their own lifecycle that is bound to the lifecycle of their host `Activity` (or another host such as a NavHost), i.e., they cannot outlive it.

### Short Version

A `Fragment`:
- is always attached to a host `Activity` (or another lifecycle owner) and cannot outlive it;
- is managed through `FragmentManager` and placed into a `ViewGroup` container;
- uses the host's context, resources, and lifecycle;
- communicates with other Fragments via the `Activity` or a shared `ViewModel`.

### Detailed Version

### Attachment Mechanism

Fragments depend on their host (usually an `Activity`) for:
- **`Context`**: accessed via `requireContext()`, `requireActivity()` (or nullable `context`/`activity` with checks)
- **Resources**: strings, drawables, system services
- **Lifecycle**: the host `Activity` lifecycle defines the upper bound; a `Fragment` cannot live longer than its host
- **`ViewGroup`**: the physical placement point in the UI (for UI fragments)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Fragment is added into a ViewGroup container via FragmentManager
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, MyFragment())
            .commit()
    }
}

class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // ✅ Access to host context is available after onAttach
    }

    override fun onDetach() {
        super.onDetach()
        // ❌ After this, the Activity/host is no longer guaranteed; clear references
    }
}
```

### Dynamic Management

Fragments can be added, replaced, and removed at runtime:

```kotlin
// ✅ Replace with back stack support
supportFragmentManager.beginTransaction()
    .replace(R.id.container, SecondFragment())
    .addToBackStack(null)  // Adds the transaction to navigation history
    .commit()

// ✅ Lookup by tag — result may be null, which is expected
val fragment = supportFragmentManager.findFragmentByTag("TAG")
if (fragment != null) {
    // Safely work with the found fragment
}
```

### Communication Through `Activity` / Shared `ViewModel`

Fragments should not be tightly coupled to each other. Typical strategies:
- using interfaces/callbacks to the parent `Activity`;
- using a shared `ViewModel` scoped to the `Activity`.

```kotlin
// ✅ Modern approach — Shared ViewModel scoped to Activity
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<String>()
    val selectedItem: LiveData<String> = _selectedItem

    fun setItem(item: String) {
        _selectedItem.value = item
    }
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

1. **Modular**: reusable across different Activities/hosts
2. **Host-bound**: require a host (usually an `Activity`) for context/resources; cannot exist fully standalone
3. **Dynamic**: managed at runtime via `FragmentManager`
4. **Back stack**: fragment transactions can be added to the `FragmentManager` back stack for navigation

### Best Practices

- **Use `viewLifecycleOwner` for view-bound subscriptions** — `LiveData`/`Flow` observers that update the UI should use the view lifecycle.
- **Use `requireActivity()`/`requireContext()` only when attached** — call them in lifecycle states where the fragment is guaranteed to be attached; otherwise check `isAdded` or use nullable references.
- **Use Shared `ViewModel` or clear interfaces** — for decoupled communication between Fragments.
- **Manage the back stack intentionally** — decide which transactions go to the back stack; use tags only when you truly need to find a specific fragment.
- **Avoid memory leaks** — do not hold references to Views/Bindings/`Activity`/`Context` beyond `onDestroyView()`/`onDetach()`.

### Common Pitfalls

- **Wrong LifecycleOwner** — using the `Fragment` itself instead of `viewLifecycleOwner` for UI observers that should respect view recreation.
- **Incorrect `ViewModel` scope** — using `activityViewModels()` when a `Fragment`-scoped `viewModels()` is needed (or vice versa), leading to unexpected state sharing or lifetime, rather than a literal memory leak.
- **State loss / navigation bugs** — relying on back navigation without calling `addToBackStack()` where appropriate; misusing `add()` vs `replace()`.
- **`Context` issues** — accessing `Activity`/`Context` after `onDetach()` or keeping hard references to it.
- **Transaction issues** — concurrent transactions, misuse of `commitAllowingStateLoss`, or not accounting for state loss.

---

## Дополнительные Вопросы (RU)

- Что происходит с состоянием `Fragment`, когда `Activity` уничтожается из-за смены конфигурации?
- Как `FragmentManager` обрабатывает back stack, когда `Activity` убита системой?
- В чем разница между `add()`, `replace()` и `show()/hide()` для транзакций фрагментов?
- Как организовать коммуникацию между фрагментами в многомодульной архитектуре?
- В чем различия жизненного цикла `View` фрагмента и самого `Fragment`?

## Follow-ups

- What happens to `Fragment` state when `Activity` is destroyed due to configuration change?
- How does FragmentManager handle back stack when `Activity` is killed by the system?
- What are the differences between `add()`, `replace()`, and `show()/hide()` for fragment transactions?
- How do you handle fragment communication in a multi-module architecture?
- What are the lifecycle differences between `Fragment`'s `View` and `Fragment` itself?

## Ссылки (RU)

- [Руководство разработчика Android - Fragments](https://developer.android.com/guide/fragments)
- [Руководство разработчика Android - Жизненный цикл `Fragment`](https://developer.android.com/guide/fragments/lifecycle)
- [Руководство разработчика Android - FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)

## References

- [Android Developer Guide - Fragments](https://developer.android.com/guide/fragments)
- [Android Developer Guide - `Fragment` Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Android Developer Guide - FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)

---

## Related Questions

### Пререквизиты / Концепции (RU)

- [[c-android-components]]

### Prerequisites / Concepts

- [[c-android-components]]

### Пререквизиты (RU)

- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - основы жизненного цикла `Fragment`
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - назначение `Fragment`

### Prerequisites

- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment` lifecycle basics
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - `Fragment` purpose

### Связанные (RU)

- [[q-how-did-fragments-appear-and-why-were-they-started-to-be-used--android--hard]] - история появления `Fragment`
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - различия коллбеков жизненного цикла

### Related

- [[q-how-did-fragments-appear-and-why-were-they-started-to-be-used--android--hard]] - `Fragment` history and rationale
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Lifecycle callbacks differences

### Advanced

- `Fragment` state management across configuration changes
- `Fragment` transaction animations and transitions
- Nested fragments and child FragmentManager patterns
