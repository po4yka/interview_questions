---
id: android-115
title: Fragments History And Purpose / История и назначение фрагментов
aliases:
- Fragments History And Purpose
- История и назначение фрагментов
topic: android
subtopics:
- fragment
- lifecycle
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-fragments
- c-lifecycle
- q-save-data-outside-fragment--android--medium
- q-what-are-fragments-for-if-there-is-activity--android--medium
created: 2025-10-15
updated: 2025-11-10
sources:
- "https://developer.android.com/guide/fragments"
- "https://developer.android.com/guide/fragments/lifecycle"
tags:
- android/fragment
- android/lifecycle
- difficulty/hard
---

# Вопрос (RU)

> Как появились фрагменты и для чего их начали использовать?

# Question (EN)

> How did fragments appear and why were they started to be used?

---

## Ответ (RU)

Фрагменты появились в **Android 3.0 (Honeycomb) в 2011 году** для решения проблемы поддержки планшетов с большими экранами (10 дюймов). Google нужно было решение для адаптивного UI: планшеты могли показывать несколько панелей одновременно (master-detail), а телефоны — по одной.

### Основные Причины Появления

**1. Multi-Pane Layouts (Master-Detail Pattern)**

До фрагментов на телефонах использовалось две `Activity` (список → детали). На планшетах это выглядело неэффективно. Фрагменты позволили показывать обе панели одновременно:

```kotlin
// ✅ Телефон: один контейнер, фрагменты заменяют друг друга
class PhoneActivity : AppCompatActivity() {
    fun showDetails(itemId: Int) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, DetailFragment.newInstance(itemId))
            .addToBackStack(null) // ✅ Навигация назад работает
            .commit()
    }
}

// ✅ Планшет: два контейнера, оба фрагмента видны
class TabletActivity : AppCompatActivity() {
    fun showDetails(itemId: Int) {
        // Только детали обновляются, список остается
        supportFragmentManager.beginTransaction()
            .replace(R.id.detail_pane, DetailFragment.newInstance(itemId))
            .commit()
    }
}
```

**2. Переиспользование Кода**

Один фрагмент может использоваться в разных `Activity`:

```kotlin
class UserListFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_user_list, container, false)
    }
}

// ✅ Используется в MainActivity, SettingsActivity, AdminActivity
```

**3. Независимый Lifecycle**

Фрагменты имеют собственный жизненный цикл, отдельный от `Activity`. Это позволяет управлять состоянием UI компонентов независимо:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // ✅ View готово для работы
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // ✅ Очищаем ссылки, избегаем утечек
    }
}
```

**4. Back `Stack` Management**

```kotlin
// ✅ Навигация: Fragment3 → Fragment2 → Fragment1 → Exit
supportFragmentManager.beginTransaction()
    .replace(R.id.container, Fragment1())
    .addToBackStack("fragment1")
    .commit()
```

### Эволюция

- **2011** — Android 3.0 (Honeycomb): первый релиз для планшетов
- **2013** — `Support Library`: обратная совместимость
- **2018** — AndroidX migration
- **2019-2020** — современные API: `by viewModels()`, `Fragment Result API`
- **2021+** — интеграция с `Jetpack Navigation`

### Современные Практики

```kotlin
class ModernFragment : Fragment(R.layout.fragment_modern) {
    private val viewModel: MyViewModel by viewModels()

    private var _binding: FragmentModernBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentModernBinding.bind(view)

        // ✅ viewLifecycleOwner предотвращает утечки
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // ✅ Fragment Result API (замена setTargetFragment)
        setFragmentResultListener("requestKey") { _, bundle ->
            handleResult(bundle.getString("result"))
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // ✅ Обязательно очищаем
    }
}
```

### Какие Проблемы Решили

- Адаптивные макеты для разных размеров экранов
- Переиспользование UI компонентов
- Модульная архитектура
- Встроенная навигация с back stack
- Независимый lifecycle от `Activity`

### Основные Вызовы

- Сложный lifecycle (много методов)
- Configuration changes требуют управления состоянием
- `IllegalStateException` при неправильном тайминге транзакций
- Необходимость очистки view references (утечки памяти)
- Сложность при вложенных фрагментах

### Альтернативы

Jetpack Compose снижает необходимость фрагментов в новых проектах, но они остаются важной частью Android-разработки в существующих приложениях.

### Лучшие Практики

- Используйте современные API: `viewModels()`, `viewLifecycleOwner`, `Fragment Result API`
- Правильно управляйте binding: очищайте ссылки в `onDestroyView()` для предотвращения утечек
- Избегайте глубокого вложения фрагментов
- Используйте общую `ViewModel` для коммуникации между sibling-фрагментами
- Тестируйте configuration changes: проверяйте сохранение состояния при повороте экрана

### Типичные Ошибки

- Утечки памяти из-за неправильного использования lifecycle для подписок
- `IllegalStateException` из-за транзакций после `onSaveInstanceState()`
- Ошибки с back stack из-за пропуска `addToBackStack()`
- Неправильная коммуникация через устаревший `setTargetFragment()`
- Переусложнение там, где достаточно простого `View`

## Answer (EN)

Fragments were introduced in **Android 3.0 (Honeycomb) in 2011** to support tablets with large screens (10 inches). Google needed a solution for adaptive UI: tablets could show multiple panes simultaneously (master-detail), while phones would show one pane at a time.

### Main Reasons for Creation

**1. Multi-Pane Layouts (Master-Detail Pattern)**

Before fragments, phones used two Activities (list → details). This looked inefficient on tablets. Fragments enabled showing both panes simultaneously:

```kotlin
// ✅ Phone: single container, fragments replace each other
class PhoneActivity : AppCompatActivity() {
    fun showDetails(itemId: Int) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, DetailFragment.newInstance(itemId))
            .addToBackStack(null) // ✅ Back navigation works
            .commit()
    }
}

// ✅ Tablet: two containers, both fragments visible
class TabletActivity : AppCompatActivity() {
    fun showDetails(itemId: Int) {
        // Only details updated, list remains visible
        supportFragmentManager.beginTransaction()
            .replace(R.id.detail_pane, DetailFragment.newInstance(itemId))
            .commit()
    }
}
```

**2. Code Reusability**

Same fragment can be used in different Activities:

```kotlin
class UserListFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_user_list, container, false)
    }
}

// ✅ Used in MainActivity, SettingsActivity, AdminActivity
```

**3. Independent Lifecycle**

Fragments have their own lifecycle, separate from `Activity`. This allows managing UI component state independently:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // ✅ View ready for work
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // ✅ Clear references, prevent leaks
    }
}
```

**4. Back `Stack` Management**

```kotlin
// ✅ Navigation: Fragment3 → Fragment2 → Fragment1 → Exit
supportFragmentManager.beginTransaction()
    .replace(R.id.container, Fragment1())
    .addToBackStack("fragment1")
    .commit()
```

### Evolution

- **2011** — Android 3.0 (Honeycomb): initial release for tablets
- **2013** — `Support Library`: backward compatibility
- **2018** — AndroidX migration
- **2019-2020** — modern APIs: `by viewModels()`, `Fragment Result API`
- **2021+** — integration with `Jetpack Navigation`

### Modern Best Practices

```kotlin
class ModernFragment : Fragment(R.layout.fragment_modern) {
    private val viewModel: MyViewModel by viewModels()

    private var _binding: FragmentModernBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentModernBinding.bind(view)

        // ✅ viewLifecycleOwner prevents leaks
        viewModel.data.observe(viewLifecycleOwner) { data ->
            binding.textView.text = data
        }

        // ✅ Fragment Result API (replaces setTargetFragment)
        setFragmentResultListener("requestKey") { _, bundle ->
            handleResult(bundle.getString("result"))
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // ✅ Must clear
    }
}
```

### Problems Fragments Solved

- Adaptive layouts for different screen sizes
- UI component reusability
- Modular architecture
- Built-in navigation with back stack
- Independent lifecycle from `Activity`

### Main Challenges

- Complex lifecycle (many methods)
- Configuration changes require state management
- `IllegalStateException` with incorrect transaction timing
- Need to clear view references (memory leaks)
- Complexity with nested fragments

### Alternatives Today

Jetpack Compose reduces the need for fragments in new projects, but they remain an important part of Android development in existing applications.

### Best Practices

- Use modern APIs: `viewModels()`, `viewLifecycleOwner`, `Fragment Result API`
- Manage binding correctly: clear references in `onDestroyView()` to prevent leaks
- Avoid deep nesting of fragments
- Use shared `ViewModel` for communication between sibling fragments
- Test configuration changes: verify state preservation during screen rotation

### Common Pitfalls

- Memory leaks due to incorrect lifecycle usage for subscriptions
- `IllegalStateException` due to transactions after `onSaveInstanceState()`
- Back stack issues due to missing `addToBackStack()` during navigation
- Incorrect communication via deprecated `setTargetFragment()`
- Over-complication where a simple `View` would be enough

---

## Follow-ups

- How does `FragmentManager` handle configuration changes and state restoration?
- What are the performance implications of deeply nested fragment hierarchies?
- How does the `Fragment Result API` improve upon deprecated communication patterns like `setTargetFragment()`?
- When would you choose fragments over Compose in a new project?

## References

- [[c-fragments]]
- [[c-fragment-lifecycle]]

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]
- [[c-lifecycle]]

### Prerequisites (Easier)

- [[q-save-data-outside-fragment--android--medium]] — `Fragment` state management
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — `Fragment` purpose

### Related (Hard)

- [[q-fragments-and-activity-relationship--android--hard]] — `Fragment`-`Activity` lifecycle
- [[q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard]] — `Fragment` benefits