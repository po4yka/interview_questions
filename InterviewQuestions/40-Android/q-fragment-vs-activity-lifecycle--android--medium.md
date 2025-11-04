---
id: android-244
title: Чем Жизненный Цикл Fragment Отличается От Activity / Fragment vs Activity Lifecycle
aliases: [Fragment vs Activity Lifecycle, Чем отличается жизненный цикл Fragment от Activity]
topic: android
subtopics:
  - activity
  - fragment
  - lifecycle
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-activity-lifecycle-methods--android--medium
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-what-are-fragments-for-if-there-is-activity--android--medium
created: 2025-10-15
updated: 2025-11-03
sources:
  - https://developer.android.com/guide/fragments/lifecycle
  - https://developer.android.com/topic/libraries/architecture/lifecycle
tags: [android/activity, android/fragment, android/lifecycle, difficulty/medium, fragments, lifecycle]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Tuesday, November 4th 2025, 12:46:34 pm
---

# Вопрос (RU)
> Чем жизненный цикл Fragment отличается от жизненного цикла Activity?

# Question (EN)
> How does the Fragment lifecycle differ from the Activity lifecycle?

---

## Ответ (RU)

### Теоретические Основы

**Fragment** — это переиспользуемый компонент UI, который может быть добавлен в Activity для создания более гибкого интерфейса. В отличие от Activity, Fragment имеет более сложный жизненный цикл, адаптированный для повторного использования и вложенности.

**Почему Fragment нужен сложный lifecycle:**
- **Переиспользование UI** — Fragment может быть использован в разных Activity
- **Независимое управление View** — View может быть уничтожено без уничтожения Fragment
- **Вложенность** — Fragment может содержать другие Fragment'ы
- **Программная навигация** — собственный back stack для навигации

**Взаимосвязь с Activity:**
- Fragment всегда привязан к Activity (кроме retained fragments)
- Lifecycle Fragment зависит от lifecycle Activity, но имеет дополнительные состояния
- Fragment получает события от Activity, но может реагировать по-своему

**Ключевые отличия от Activity:**
- Fragment имеет 11 состояний вместо 6 у Activity
- Отдельный View lifecycle (`onCreateView`/`onDestroyView`)
- Состояния привязки (`onAttach`/`onDetach`)
- `viewLifecycleOwner` для безопасного наблюдения данных

### Ключевые Отличия

**1. Дополнительные состояния привязки**

Fragment имеет состояния `onAttach()` и `onDetach()` для привязки к Activity:

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment привязан к Activity
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment отвязан от Activity
    }
}
```

**2. Отдельный жизненный цикл View**

Fragment отделяет свой lifecycle от View lifecycle, позволяя пересоздавать View без уничтожения Fragment:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?) =
        inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // View уничтожен, но Fragment может быть восстановлен
    }
}
```

**3. Порядок состояний**

**Activity** (6 состояний):
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**Fragment** (11 состояний):
```
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```

**4. ViewLifecycleOwner**

Fragment предоставляет `viewLifecycleOwner` для безопасного наблюдения данных только пока View существует:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Подписка автоматически отменится при onDestroyView
        }
    }
}
```

**5. Программный back stack**

Fragment поддерживает собственный back stack независимо от системного:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

### Сравнительная Таблица

| Аспект | Activity | Fragment |
|--------|----------|----------|
| Количество состояний | 6 | 11 |
| View lifecycle | Совпадает с Activity | Отдельный (`onCreateView`/`onDestroyView`) |
| Привязка к родителю | — | `onAttach`/`onDetach` |
| Back stack | Системный | Программный (`addToBackStack`) |
| Вложенность | — | Поддерживает child fragments |
| LifecycleOwner | Activity сама по себе | Fragment + ViewLifecycleOwner |
| Повторное использование | Ограничено | Высокая переиспользуемость |
| Управление состоянием | `onSaveInstanceState` | Bundle + ViewModel |

---

## Answer (EN)

### Theoretical Foundations

**Fragment** is a reusable UI component that can be added to an Activity to create more flexible interfaces. Unlike Activity, Fragment has a more complex lifecycle adapted for reusability and nesting.

**Why Fragment needs complex lifecycle:**
- **UI reusability** — Fragment can be used in different Activities
- **Independent View management** — View can be destroyed without destroying Fragment
- **Nesting** — Fragment can contain other Fragments
- **Programmatic navigation** — own back stack for navigation

**Relationship with Activity:**
- Fragment is always attached to Activity (except retained fragments)
- Fragment lifecycle depends on Activity lifecycle but has additional states
- Fragment receives events from Activity but can respond differently

**Key differences from Activity:**
- Fragment has 11 states instead of 6 in Activity
- Separate View lifecycle (`onCreateView`/`onDestroyView`)
- Attachment states (`onAttach`/`onDetach`)
- `viewLifecycleOwner` for safe data observation

### Key Differences

**1. Additional Attachment States**

Fragment has `onAttach()` and `onDetach()` states for binding to Activity:

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment attached to Activity
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment detached from Activity
    }
}
```

**2. Separate View Lifecycle**

Fragment separates its lifecycle from View lifecycle, allowing View recreation without destroying Fragment:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?) =
        inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // View destroyed, but Fragment can be restored
    }
}
```

**3. State Order**

**Activity** (6 states):
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**Fragment** (11 states):
```
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```

**4. ViewLifecycleOwner**

Fragment provides `viewLifecycleOwner` for safe data observation only while View exists:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Subscription automatically cancelled on onDestroyView
        }
    }
}
```

**5. Programmatic Back Stack**

Fragment supports its own back stack independent of the system back stack:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

### Comparison Table

| Aspect | Activity | Fragment |
|--------|----------|----------|
| Number of states | 6 | 11 |
| View lifecycle | Same as Activity | Separate (`onCreateView`/`onDestroyView`) |
| Parent binding | — | `onAttach`/`onDetach` |
| Back stack | System | Programmatic (`addToBackStack`) |
| Nesting | — | Supports child fragments |
| LifecycleOwner | Activity itself | Fragment + ViewLifecycleOwner |
| Reusability | Limited | High reusability |
| State management | `onSaveInstanceState` | Bundle + ViewModel |

### Best Practices

- **Always use viewLifecycleOwner** — for LiveData/Flow subscriptions in Fragment
- **Avoid memory leaks** — cancel subscriptions in `onDestroyView`
- **Save state properly** — use Bundle for UI state, ViewModel for business data
- **Test lifecycle** — verify behavior during configuration changes
- **Use child fragments** — for complex nested UI components

### Common Pitfalls

- **Wrong LifecycleOwner** — using Fragment instead of viewLifecycleOwner causes leaks
- **Subscription leaks** — forgotten LiveData subscriptions after onDestroyView
- **Improper state saving** — trying to save complex objects in Bundle
- **Ignoring onAttach/onDetach** — not checking Activity availability
- **Blocking operations** — performing heavy tasks in lifecycle methods

### Лучшие Практики

- **Всегда используйте viewLifecycleOwner** — для подписок на LiveData/Flow в Fragment
- **Избегайте утечек памяти** — отменяйте подписки в `onDestroyView`
- **Правильно сохраняйте состояние** — используйте Bundle для UI состояния, ViewModel для бизнес-данных
- **Тестируйте lifecycle** — проверяйте поведение при configuration changes
- **Используйте child fragments** — для сложных вложенных UI компонентов

### Типичные Ошибки

- **Неправильный LifecycleOwner** — использование Fragment вместо viewLifecycleOwner приводит к утечкам
- **Утечка подписок** — забытые подписки на LiveData после onDestroyView
- **Неправильное сохранение состояния** — попытка сохранить сложные объекты в Bundle
- **Игнорирование onAttach/onDetach** — отсутствие проверки доступности Activity
- **Блокирующие операции** — выполнение тяжелых задач в lifecycle методах

---

## Follow-ups

- What happens if you observe LiveData with Fragment instead of viewLifecycleOwner?
- How do nested fragments affect the lifecycle order?
- When should you use `setRetainInstance(true)` and is it still recommended?
- How does configuration change affect Fragment lifecycle differently from Activity?

## References

- [Android Fragment Lifecycle Documentation](https://developer.android.com/guide/fragments/lifecycle)
- [ViewLifecycleOwner Best Practices](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] — Activity lifecycle basics
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — Fragment purpose

### Related
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — Lifecycle dependency
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] — Alternative perspective

### Advanced
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] — Fragment design rationale
- [[q-fragments-and-activity-relationship--android--hard]] — Deep dive into relationship
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] — Callback differences
