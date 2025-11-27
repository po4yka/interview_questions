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
status: draft
moc: moc-android
related:
  - c-activity
  - q-activity-lifecycle-methods--android--medium
  - q-how-does-activity-lifecycle-work--android--medium
  - q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-what-are-fragments-for-if-there-is-activity--android--medium
created: 2025-10-15
updated: 2025-11-10
sources:
  - "https://developer.android.com/guide/fragments/lifecycle"
  - "https://developer.android.com/topic/libraries/architecture/lifecycle"
tags: [android/activity, android/fragment, android/lifecycle, difficulty/medium, fragments, lifecycle]

date created: Saturday, November 1st 2025, 12:46:50 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)
> Чем жизненный цикл `Fragment` отличается от жизненного цикла `Activity`?

# Question (EN)
> How does the `Fragment` lifecycle differ from the `Activity` lifecycle?

---

## Ответ (RU)

### Теоретические Основы

**`Fragment`** — это переиспользуемый компонент UI, который может быть добавлен в `Activity` для создания более гибкого интерфейса. В отличие от `Activity`, `Fragment` имеет более детализированный жизненный цикл, адаптированный для повторного использования, вложенности и тесной интеграции с lifecycle хоста.

**Почему `Fragment` нужен более сложный lifecycle:**
- **Переиспользование UI** — `Fragment` может быть использован в разных `Activity`.
- **Независимое управление `View`** — `View` может быть уничтожена без уничтожения экземпляра `Fragment`.
- **Вложенность** — `Fragment` может содержать другие `Fragment`'ы.
- **Программная навигация** — back stack на уровне `FragmentManager`.

**Взаимосвязь с `Activity`:**
- `Fragment` всегда существует внутри контекста хоста (обычно `Activity` или другого `Fragment` через `childFragmentManager`) и не может пережить его lifecycle.
- Lifecycle `Fragment` зависит от lifecycle хоста и синхронизируется с ним, но имеет дополнительные промежуточные состояния и коллбеки.
- `Fragment` получает события от `Activity`, но может реагировать по-своему.

**Ключевые отличия от `Activity`:**
- `Fragment` описывается более подробным набором коллбеков (часто перечисляют около 10–11 основных этапов) по сравнению с базовыми коллбеками `Activity` — это иллюстративное, а не строго фиксированное количество.
- Отдельный `View` lifecycle (`onCreateView`/`onDestroyView`).
- Состояния привязки (`onAttach`/`onDetach`).
- `viewLifecycleOwner` для безопасного наблюдения данных, связанных с `View`.

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

`Fragment` отделяет свой lifecycle от lifecycle его `View`, позволяя пересоздавать `View` без уничтожения самого `Fragment`:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?) =
        inflater.inflate(R.layout.fragment_my, container, false)

    override fun onDestroyView() {
        super.onDestroyView()
        // View уничтожен, но Fragment остается и может пересоздать View
    }
}
```

**3. Порядок состояний**

**`Activity`** (базовая последовательность ключевых коллбеков):
```text
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**`Fragment`** (расширенная последовательность ключевых коллбеков):
```text
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```
(Фактический порядок учитывает, что вызовы `Fragment` синхронизированы с состояниями хоста.)

**4. ViewLifecycleOwner**

`Fragment` предоставляет `viewLifecycleOwner` для безопасного наблюдения данных только пока существует `View`:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Подписка автоматически будет деактивирована при onDestroyView
        }
    }
}
```

Использование `viewLifecycleOwner` предотвращает ситуацию, когда наблюдатель переживает уничтожение `View` и продолжает обновлять неактуальные ссылки.

**5. Back stack на уровне FragmentManager**

`Fragment`-транзакции могут быть добавлены во внутренний back stack `FragmentManager` внутри `Activity` или другого хоста:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

Этот back stack:
- управляется программно через `FragmentManager`;
- логически отделен от системного back stack `Activity`, но привязан к lifecycle хоста.

### Сравнительная Таблица

| Аспект | `Activity` | `Fragment` |
|--------|----------|----------|
| Количество состояний | Набор базовых коллбеков (`onCreate`–`onDestroy`) | Более детализированный набор коллбеков (привязка, создание `View`, уничтожение `View` и т.д.) |
| `View` lifecycle | Совпадает с lifecycle `Activity` | Отдельный (`onCreateView`/`onDestroyView`) |
| Привязка к родителю | — | `onAttach`/`onDetach` |
| Back stack | Системный back stack `Activity` | Внутренний back stack `FragmentManager` внутри хоста |
| Вложенность | — | Поддерживает child fragments |
| LifecycleOwner | `Activity` сама по себе | `Fragment` как `LifecycleOwner` + `viewLifecycleOwner` для `View` |
| Повторное использование | Более ограничено | Высокая переиспользуемость |
| Управление состоянием | `onSaveInstanceState` + `ViewModel` | `onSaveInstanceState` + `ViewModel` (часто для долгоживущих / общих данных между фрагментами и `Activity`) |

### Лучшие Практики (RU)

- **Используйте `viewLifecycleOwner`** для подписок на `LiveData`/`Flow`, связанных с `View`, чтобы избежать обновления уже уничтоженных `View`.
- **Избегайте утечек памяти** — очищайте/отменяйте ссылки на `View` и подписки в `onDestroyView`.
- **Правильно сохраняйте состояние** — используйте `Bundle` для сериализуемого UI-состояния, `ViewModel` для бизнес-логики и долгоживущих данных.
- **Тестируйте lifecycle** — проверяйте поведение при configuration changes и навигации (back stack).
- **Используйте child fragments осознанно** — для сложных вложенных UI-компонентов, контролируя их lifecycle.

### Типичные Ошибки (RU)

- **Неправильный `LifecycleOwner`** — использование `Fragment` вместо `viewLifecycleOwner` для `View`-связанных наблюдателей: в этом случае наблюдатель будет жить дольше, чем `View`, и может пытаться обновлять уничтоженный UI.
- **Утечка подписок** — неотмененные коллбеки/подписки, которые продолжают держать ссылку на `View` после `onDestroyView`.
- **Неправильное сохранение состояния** — попытка сохранить несериализуемые или тяжелые объекты напрямую в `Bundle`.
- **Игнорирование `onAttach`/`onDetach`** — отсутствие проверки доступности host/context.
- **Блокирующие операции** — выполнение тяжелых задач в lifecycle-коллбеках на главном потоке.

---

## Answer (EN)

### Theoretical Foundations

A **`Fragment`** is a reusable UI component that can be added to an `Activity` to create more flexible interfaces. Unlike an `Activity`, a `Fragment` has a more granular lifecycle, adapted for reuse, nesting, and tight integration with its host's lifecycle.

**Why `Fragment` needs a more complex lifecycle:**
- **UI reusability** — A `Fragment` can be used in different `Activities`.
- **Independent `View` management** — The `View` can be destroyed without destroying the `Fragment` instance.
- **Nesting** — A `Fragment` can contain other fragments.
- **Programmatic navigation** — Back stack at the `FragmentManager` level.

**Relationship with `Activity`:**
- A `Fragment` always exists within a hosting context (typically an `Activity` or another `Fragment` via `childFragmentManager`) and cannot outlive its host.
- The `Fragment` lifecycle depends on and is synchronized with the host `Activity` lifecycle but introduces additional intermediate states and callbacks.
- A `Fragment` receives events from the `Activity` but can handle them independently.

**Key differences from `Activity`:**
- A `Fragment` is described with a more detailed set of callbacks (people often list around 10–11 key stages) compared to the basic `Activity` callbacks — this is illustrative, not a strict canonical count.
- Separate `View` lifecycle (`onCreateView`/`onDestroyView`).
- Attachment states (`onAttach`/`onDetach`).
- `viewLifecycleOwner` for safe observation of view-bound data.

### Key Differences

**1. Additional Attachment States**

A `Fragment` has `onAttach()` and `onDetach()` callbacks for binding to its host:

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

A `Fragment` separates its own lifecycle from the `View` lifecycle, allowing `View` recreation without destroying the `Fragment` instance itself:

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

**`Activity`** (basic sequence of key callbacks):
```text
onCreate → onStart → onResume → onPause → onStop → onDestroy
```

**`Fragment`** (extended sequence of key callbacks):
```text
onAttach → onCreate → onCreateView → onViewCreated →
onStart → onResume → onPause → onStop →
onDestroyView → onDestroy → onDetach
```
(Actual dispatch is aligned with the host lifecycle states.)

**4. ViewLifecycleOwner**

A `Fragment` provides `viewLifecycleOwner` for safe data observation only while the `View` exists:

```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.data.observe(viewLifecycleOwner) { data ->
            // Subscription will be automatically stopped when onDestroyView is called
        }
    }
}
```

Using `viewLifecycleOwner` prevents observers from outliving the view and updating a destroyed UI.

**5. FragmentManager Back Stack**

`Fragment` transactions can be added to the `FragmentManager`'s internal back stack inside the hosting `Activity` or fragment container:

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

This back stack:
- is controlled programmatically via `FragmentManager`;
- is logically separate from the system `Activity` back stack, but scoped to the host's lifecycle.

### Comparison Table

| Aspect | `Activity` | `Fragment` |
|--------|----------|----------|
| Number of states | Basic callbacks (`onCreate`–`onDestroy`) | More granular callbacks (attachment, view creation, view destruction, etc.) |
| `View` lifecycle | Same as `Activity` lifecycle | Separate (`onCreateView`/`onDestroyView`) |
| Parent binding | — | `onAttach`/`onDetach` |
| Back stack | System back stack of `Activities` | Internal `FragmentManager` back stack within the host |
| Nesting | — | Supports child fragments |
| LifecycleOwner | `Activity` itself | `Fragment` as `LifecycleOwner` + `viewLifecycleOwner` for the `View` |
| Reusability | More limited | High reusability |
| State management | `onSaveInstanceState` + `ViewModel` | `onSaveInstanceState` + `ViewModel` (commonly for longer-lived / shared data between fragments and `Activity`) |

### Best Practices (EN)

- **Use `viewLifecycleOwner`** for `LiveData`/`Flow` observers tied to the `View`, to avoid updating destroyed views.
- **Avoid memory leaks** — clear/cancel `View` references and subscriptions in `onDestroyView`.
- **Save state correctly** — use `Bundle` for serializable UI state, `ViewModel` for business logic and long-lived data.
- **Test lifecycle behavior** — verify behavior during configuration changes and navigation (back stack).
- **Use child fragments judiciously** — for complex nested UI components while respecting their lifecycle.

### Common Pitfalls (EN)

- **Wrong `LifecycleOwner`** — using `Fragment` instead of `viewLifecycleOwner` for view-bound observers: the observer outlives the view and may try to update a destroyed UI.
- **Subscription leaks** — not cancelling callbacks/subscriptions that keep references to the view after `onDestroyView`.
- **Improper state saving** — trying to store non-serializable or heavy objects directly in `Bundle`.
- **Ignoring `onAttach`/`onDetach`** — not checking host/context availability.
- **Blocking operations** — running heavy work in lifecycle callbacks on the main thread.

---

## Дополнительные Вопросы (RU)

- Что произойдет, если наблюдать `LiveData`, используя `Fragment` вместо `viewLifecycleOwner`?
- Как вложенные фрагменты влияют на порядок вызовов lifecycle?
- Когда и почему исторически использовался `setRetainInstance(true)` и почему сейчас вместо него рекомендуется `ViewModel` (метод помечен как устаревший в современных версиях `Fragment`)?
- Как конфигурационные изменения по-разному влияют на lifecycle `Fragment` и `Activity`?

## Follow-ups (EN)

- What happens if you observe `LiveData` with `Fragment` instead of `viewLifecycleOwner`?
- How do nested fragments affect the lifecycle order?
- When and why was `setRetainInstance(true)` used historically, and why is `ViewModel` recommended instead (the method is deprecated in modern `Fragment` versions)?
- How does configuration change affect `Fragment` lifecycle differently from `Activity`?

---

## Ссылки (RU)

- [Документация по жизненному циклу `Fragment`](https://developer.android.com/guide/fragments/lifecycle)
- [Руководство по `ViewLifecycleOwner` и архитектурным компонентам](https://developer.android.com/topic/libraries/architecture/lifecycle)

## References (EN)

- [Android `Fragment` Lifecycle Documentation](https://developer.android.com/guide/fragments/lifecycle)
- [ViewLifecycleOwner Best Practices](https://developer.android.com/topic/libraries/architecture/lifecycle)

---

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-activity]]

### Базовые Вопросы

- [[q-activity-lifecycle-methods--android--medium]] — основы жизненного цикла `Activity`
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — назначение `Fragment`

### Связанные

- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — зависимость lifecycle

## Related Questions (EN)

### Prerequisites / Concepts

- [[c-activity]]

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] — `Activity` lifecycle basics
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — `Fragment` purpose

### Related
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — Lifecycle dependency
