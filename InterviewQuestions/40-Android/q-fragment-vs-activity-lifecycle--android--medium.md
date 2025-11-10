---
id: android-244
title: Чем Жизненный Цикл Fragment Отличается От Activity / Fragment vs Activity Lifecycle
aliases:
- Fragment vs Activity Lifecycle
- Чем отличается жизненный цикл Fragment от Activity
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
status: draft
moc: moc-android
related:
- c-activity
- c-fragments
- c-lifecycle
- q-activity-lifecycle-methods--android--medium
- q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
- q-what-are-fragments-for-if-there-is-activity--android--medium
created: 2025-10-15
updated: 2025-11-10
sources:
- "https://developer.android.com/guide/fragments/lifecycle"
- "https://developer.android.com/topic/libraries/architecture/lifecycle"
tags:
- android/activity
- android/fragment
- android/lifecycle
- difficulty/medium
- fragments
- lifecycle

---

# Вопрос (RU)
> Чем жизненный цикл `Fragment` отличается от жизненного цикла `Activity`?

# Question (EN)
> How does the `Fragment` lifecycle differ from the `Activity` lifecycle?

---

## Ответ (RU)

### Теоретические Основы

**`Fragment`** — это переиспользуемый компонент UI, который может быть добавлен в `Activity` для создания более гибкого интерфейса. В отличие от `Activity`, `Fragment` имеет более сложный жизненный цикл, адаптированный для повторного использования и вложенности.

**Почему `Fragment` нужен сложный lifecycle:**
- **Переиспользование UI** — `Fragment` может быть использован в разных `Activity`
- **Независимое управление `View`** — `View` может быть уничтожено без уничтожения `Fragment`
- **Вложенность** — `Fragment` может содержать другие `Fragment`'ы
- **Программная навигация** — back stack на уровне FragmentManager

**Взаимосвязь с `Activity`:**
- `Fragment` всегда существует внутри контекста хоста (обычно `Activity` или другого `Fragment` через `childFragmentManager`)
- Lifecycle `Fragment` зависит от lifecycle `Activity`, но имеет дополнительные состояния
- `Fragment` получает события от `Activity`, но может реагировать по-своему

**Ключевые отличия от `Activity`:**
- `Fragment` часто описывают через более детализированный набор коллбеков (например, 11 основных шагов) против 6 базовых у `Activity`
- Отдельный `View` lifecycle (`onCreateView`/`onDestroyView`)
- Состояния привязки (`onAttach`/`onDetach`)
- `viewLifecycleOwner` для безопасного наблюдения данных

### Ключевые Отличия

**1. Дополнительные состояния привязки**

`Fragment` имеет состояния `onAttach()` и `onDetach()` для привязки к `Activity` или другому хосту:

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment привязан к host (обычно Activity)
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment отвязан от host
    }
}
```

**2. Отдельный жизненный цикл `View`**

`Fragment` отделяет свой lifecycle от `View` lifecycle, позволяя пересоздавать `View` без уничтожения самого `Fragment`:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?) =
        inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // View уничтожен, но Fragment остается в памяти и может пересоздать View
    }
}
```

**3. Порядок состояний**

**`Activity`** (базовая последовательность коллбеков):
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**`Fragment`** (расширенная последовательность ключевых коллбеков):
```
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```

**4. ViewLifecycleOwner**

`Fragment` предоставляет `viewLifecycleOwner` для безопасного наблюдения данных только пока `View` существует:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Подписка автоматически отменится при onDestroyView
        }
    }
}
```

**5. Back stack на уровне FragmentManager**

`Fragment`-транзакции могут быть добавлены во внутренний back stack FragmentManager внутри `Activity` или другого хоста:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

Этот back stack:
- управляется программно через `FragmentManager`
- логически отделен от системного back stack `Activity`, но живет внутри жизненного цикла хоста

### Сравнительная Таблица

| Аспект | `Activity` | `Fragment` |
|--------|----------|----------|
| Количество состояний | 6 базовых коллбеков | Более детализированный набор (например, 11 ключевых коллбеков) |
| `View` lifecycle | Совпадает с `Activity` | Отдельный (`onCreateView`/`onDestroyView`) |
| Привязка к родителю | — | `onAttach`/`onDetach` |
| Back stack | Системный back stack `Activity` | Внутренний back stack `FragmentManager` внутри `Activity` |
| Вложенность | — | Поддерживает child fragments |
| LifecycleOwner | `Activity` сама по себе | `Fragment` + `viewLifecycleOwner` |
| Повторное использование | Ограничено | Высокая переиспользуемость |
| Управление состоянием | `onSaveInstanceState` | `onSaveInstanceState` + `ViewModel` (для долгоживущих данных) |

### Лучшие Практики (RU)

- **Всегда используйте `viewLifecycleOwner`** — для подписок на `LiveData`/`Flow` в `Fragment`
- **Избегайте утечек памяти** — очищайте/отменяйте подписки и ссылки в `onDestroyView`
- **Правильно сохраняйте состояние** — используйте `Bundle` для UI-состояния, `ViewModel` для бизнес-/долгоживущих данных
- **Тестируйте lifecycle** — проверяйте поведение при configuration changes
- **Используйте child fragments** — для сложных вложенных UI компонентов

### Типичные Ошибки (RU)

- **Неправильный `LifecycleOwner`** — использование `Fragment` вместо `viewLifecycleOwner` для `View`-связанных наблюдателей
- **Утечка подписок** — забытые подписки на `LiveData` после `onDestroyView`
- **Неправильное сохранение состояния** — попытка сохранить сложные объекты напрямую в `Bundle`
- **Игнорирование `onAttach`/`onDetach`** — отсутствие проверки доступности host/context
- **Блокирующие операции** — выполнение тяжелых задач в lifecycle-коллбеках на главном потоке

---

## Answer (EN)

### Theoretical Foundations

A **`Fragment`** is a reusable UI component that can be added to an `Activity` to create more flexible interfaces. Unlike an `Activity`, a `Fragment` has a more complex lifecycle adapted for reusability and nesting.

**Why `Fragment` needs a complex lifecycle:**
- **UI reusability** — `Fragment` can be used in different Activities
- **Independent `View` management** — `View` can be destroyed without destroying the `Fragment` instance
- **Nesting** — `Fragment` can contain other Fragments
- **Programmatic navigation** — back stack at the FragmentManager level

**Relationship with `Activity`:**
- A `Fragment` always exists within a hosting context (typically an `Activity` or another `Fragment` via `childFragmentManager`)
- `Fragment` lifecycle depends on the host `Activity` lifecycle but adds its own states
- `Fragment` receives events from the `Activity` but can handle them independently

**Key differences from `Activity`:**
- `Fragment` is often described with a more detailed set of callbacks (e.g., 11 key steps) vs 6 basic `Activity` callbacks
- Separate `View` lifecycle (`onCreateView`/`onDestroyView`)
- Attachment states (`onAttach`/`onDetach`)
- `viewLifecycleOwner` for safe data observation

### Key Differences

**1. Additional Attachment States**

`Fragment` has `onAttach()` and `onDetach()` callbacks for binding to its host:

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Fragment attached to host (typically Activity)
    }

    override fun onDetach() {
        super.onDetach()
        // Fragment detached from host
    }
}
```

**2. Separate `View` Lifecycle**

`Fragment` separates its own lifecycle from the `View` lifecycle, allowing `View` recreation without destroying the `Fragment` instance itself:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?) =
        inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // View destroyed, but Fragment remains and can recreate its View
    }
}
```

**3. State Order**

**`Activity`** (basic callback sequence):
```
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**`Fragment`** (extended sequence of key callbacks):
```
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```

**4. ViewLifecycleOwner**

`Fragment` provides `viewLifecycleOwner` for safe data observation only while the `View` exists:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Subscription is automatically cleared on onDestroyView
        }
    }
}
```

**5. FragmentManager Back Stack**

`Fragment` transactions can be added to the FragmentManager's internal back stack inside the hosting `Activity` or fragment container:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

This back stack:
- is controlled programmatically via `FragmentManager`
- is logically separate from the system `Activity` back stack, but scoped to the host's lifecycle

### Comparison Table

| Aspect | `Activity` | `Fragment` |
|--------|----------|----------|
| Number of states | 6 basic callbacks | More granular set (e.g., 11 key callbacks) |
| `View` lifecycle | Same as `Activity` | Separate (`onCreateView`/`onDestroyView`) |
| Parent binding | — | `onAttach`/`onDetach` |
| Back stack | System back stack of Activities | Internal `FragmentManager` back stack within `Activity` |
| Nesting | — | Supports child fragments |
| LifecycleOwner | `Activity` itself | `Fragment` + `viewLifecycleOwner` |
| Reusability | Limited | High reusability |
| State management | `onSaveInstanceState` | `onSaveInstanceState` + `ViewModel` (for long-lived data) |

### Best Practices (EN)

- **Always use `viewLifecycleOwner`** for `LiveData`/`Flow` subscriptions in a `Fragment`
- **Avoid memory leaks** — clear/cancel subscriptions and references in `onDestroyView`
- **Save state properly** — use `Bundle` for UI state, `ViewModel` for business/long-lived data
- **Test lifecycle behavior** — verify behavior during configuration changes
- **Use child fragments when appropriate** — for complex nested UI components

### Common Pitfalls (EN)

- **Wrong `LifecycleOwner`** — using `Fragment` instead of `viewLifecycleOwner` for view-bound observers
- **Subscription leaks** — forgotten `LiveData` subscriptions after `onDestroyView`
- **Improper state saving** — trying to store complex objects directly in `Bundle`
- **Ignoring `onAttach`/`onDetach`** — not checking host availability or context
- **Blocking operations** — running heavy work in lifecycle callbacks on the main thread

---

## Дополнительные вопросы (RU)

- Что произойдет, если наблюдать `LiveData`, используя `Fragment` вместо `viewLifecycleOwner`?
- Как вложенные фрагменты влияют на порядок вызовов lifecycle?
- Когда стоит использовать `setRetainInstance(true)` и актуально ли это сейчас?
- Как конфигурационные изменения по-разному влияют на lifecycle `Fragment` и `Activity`?

## Follow-ups (EN)

- What happens if you observe `LiveData` with `Fragment` instead of `viewLifecycleOwner`?
- How do nested fragments affect the lifecycle order?
- When should you use `setRetainInstance(true)` and is it still recommended?
- How does configuration change affect `Fragment` lifecycle differently from `Activity`?

---

## Ссылки (RU)

- [Документация по жизненному циклу `Fragment`](https://developer.android.com/guide/fragments/lifecycle)
- [Руководство по `ViewLifecycleOwner` и архитектурным компонентам](https://developer.android.com/topic/libraries/architecture/lifecycle)

## References (EN)

- [Android `Fragment` Lifecycle Documentation](https://developer.android.com/guide/fragments/lifecycle)
- [ViewLifecycleOwner Best Practices](https://developer.android.com/topic/libraries/architecture/lifecycle)

---

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-activity]]
- [[c-fragments]]
- [[c-lifecycle]]

### Базовые вопросы

- [[q-activity-lifecycle-methods--android--medium]] — основы жизненного цикла `Activity`
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — назначение `Fragment`

### Связанные

- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — зависимость lifecycle

## Related Questions (EN)

### Prerequisites / Concepts

- [[c-activity]]
- [[c-fragments]]
- [[c-lifecycle]]

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] — `Activity` lifecycle basics
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — `Fragment` purpose

### Related
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — Lifecycle dependency

