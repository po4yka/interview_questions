---\
id: android-014
title: "ViewCompositionStrategy in Compose / ViewCompositionStrategy в Compose"
aliases: ["ViewCompositionStrategy in Compose", "ViewCompositionStrategy в Compose"]
topic: android
subtopics: [ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-compose-ui-basics, q-compose-performance-optimization--android--hard, q-custom-view-lifecycle--android--medium]
created: 2025-10-05
updated: 2025-11-10
tags: [android/lifecycle, android/ui-compose, difficulty/medium, interop, lifecycle, viewcompositionstrategy]
sources: ["https://developer.android.com/jetpack/compose/interop/view-composition-strategy"]

---\
# Вопрос (RU)
> Что такое ViewCompositionStrategy и когда её использовать?

# Question (EN)
> What is ViewCompositionStrategy and when to use it?

---

## Ответ (RU)

**Концепция:**
ViewCompositionStrategy управляет тем, когда освобождается Composition, связанная с конкретным ComposeView, при интеграции Compose в `View`-иерархию. Это важно для корректного управления ресурсами и предотвращения утечек памяти (см. [[c-android]], [[c-compose-ui-basics]]).

**Основные стратегии:**

1. **DisposeOnDetachedFromWindowOrReleasedFromPool** (по умолчанию)
   - Освобождает Composition при detach от окна или при release из `RecyclerView` pool
   - Подходит для большинства случаев, особенно для ComposeView, создаваемых и управляемых как обычные `View` (включая в `RecyclerView`)

```kotlin
// ✅ По умолчанию, работает для RecyclerView
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

1. **DisposeOnLifecycleDestroyed**
   - Привязывает Composition к заданному `Lifecycle` (например, `Fragment` или `Activity`)
   - Composition освобождается только при onDestroy этого `Lifecycle`
   - Полезно, когда нужно, чтобы Composition переживал пересоздание `View` (например, при работе с viewLifecycleOwner или полевым ComposeView)

```kotlin
// ✅ Для Fragment, когда хотите, чтобы Composition жила до уничтожения viewLifecycleOwner.lifecycle
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
)
```

1. **DisposeOnViewTreeLifecycleDestroyed**
   - Использует `Lifecycle` из ViewTreeLifecycleOwner
   - Удобно, когда `Lifecycle` явно недоступен, но установлен через ViewTreeLifecycleOwner

```kotlin
// ✅ Когда lifecycle доступен только через ViewTree
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
)
```

**Частые ошибки:**

```kotlin
// ❌ Потенциальная утечка: ComposeView хранится как поле Fragment
class MyFragment : Fragment() {
    private lateinit var composeView: ComposeView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        composeView = ComposeView(requireContext()).apply {
            // При стратегии только "detach от окна" Composition может
            // остаться привязана к Fragment, если View пересоздаётся
            setContent { /* ... */ }
        }
        return composeView
    }
}

// ✅ Правильно: привязать Composition к жизненному циклу viewLifecycleOwner
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setViewCompositionStrategy(
                ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
            )
            setContent { /* ... */ }
        }
    }
}
```

**Выбор стратегии (обобщённо):**
- **`Fragment`**:
  - Если ComposeView создаётся программно и может переживать пересоздание `View` / быть полем: используйте `DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)` или `DisposeOnViewTreeLifecycleDestroyed`.
  - Если ComposeView создаётся и уничтожается вместе с `View` (например, через XML или в onCreateView без хранения в полях), дефолтная стратегия обычно безопасна.
- **`RecyclerView`**: `DisposeOnDetachedFromWindowOrReleasedFromPool` (по умолчанию)
- **Dialog/BottomSheet**: `DisposeOnDetachedFromWindowOrReleasedFromPool` обычно достаточно, так как жизненный цикл привязан к окну
- **Custom `View`**: оцените срок жизни; дефолтная стратегия подходит, если `View` корректно отделяется от окна при уничтожении

## Answer (EN)

**Concept:**
ViewCompositionStrategy defines when the Composition associated with a specific ComposeView is disposed when integrating Compose into a `View` hierarchy. It is important for proper resource management and avoiding memory leaks (see [[c-android]], [[c-compose-ui-basics]]).

**Main Strategies:**

1. **DisposeOnDetachedFromWindowOrReleasedFromPool** (default)
   - Disposes the Composition when the view is detached from window or released from a `RecyclerView` pool
   - Suitable for most cases, especially when ComposeView is managed like a regular `View` (including in `RecyclerView`)

```kotlin
// ✅ Default, works well for RecyclerView
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

1. **DisposeOnLifecycleDestroyed**
   - Binds the Composition to a given `Lifecycle` (e.g., `Fragment` or `Activity`)
   - Composition is disposed only when that `Lifecycle` reaches onDestroy
   - Useful when you want the Composition to outlive a single `View` instance (e.g., tied to viewLifecycleOwner or a field-held ComposeView)

```kotlin
// ✅ For Fragment when you want Composition bound to viewLifecycleOwner.lifecycle
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
)
```

1. **DisposeOnViewTreeLifecycleDestroyed**
   - Uses the `Lifecycle` from ViewTreeLifecycleOwner
   - Handy when `Lifecycle` isn't passed directly but is provided via ViewTreeLifecycleOwner

```kotlin
// ✅ When lifecycle is available only from ViewTree
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
)
```

**Common Mistakes:**

```kotlin
// ❌ Potential leak: ComposeView kept as a Fragment field
class MyFragment : Fragment() {
    private lateinit var composeView: ComposeView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        composeView = ComposeView(requireContext()).apply {
            // With only "detach from window" behavior, Composition may remain
            // tied to the Fragment if views are recreated
            setContent { /* ... */ }
        }
        return composeView
    }
}

// ✅ Correct: bind Composition to viewLifecycleOwner's lifecycle
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setViewCompositionStrategy(
                ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
            )
            setContent { /* ... */ }
        }
    }
}
```

**Strategy Selection (general):**
- **`Fragment`**:
  - If ComposeView is created programmatically and may outlive a single `View` instance / stored as a field: use `DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)` or `DisposeOnViewTreeLifecycleDestroyed`.
  - If ComposeView is created and destroyed together with the `View` (e.g., via XML or local in onCreateView), the default strategy is typically safe.
- **`RecyclerView`**: `DisposeOnDetachedFromWindowOrReleasedFromPool` (default)
- **Dialog/BottomSheet**: `DisposeOnDetachedFromWindowOrReleasedFromPool` is usually sufficient since lifetime is tied to the window
- **Custom `View`**: evaluate lifetime; default works when the `View` is correctly detached on destruction

---

## Дополнительные Вопросы (RU)

- Что произойдет при повороте `Fragment` с неверно выбранной ViewCompositionStrategy?
- Как DisposeOnDetachedFromWindowOrReleasedFromPool по-разному обрабатывает `RecyclerView` pooling и detach?
- В каких случаях DisposeOnViewTreeLifecycleDestroyed предпочтительна по сравнению с DisposeOnLifecycleDestroyed?
- Как диагностировать утечки памяти, вызванные некорректной ViewCompositionStrategy?
- Можно ли вручную инициировать освобождение Composition без detach `ComposeView`?

## Follow-ups (EN)

- What happens if `Fragment` rotates with the wrong ViewCompositionStrategy?
- How does DisposeOnDetachedFromWindowOrReleasedFromPool handle `RecyclerView` pooling differently from detach?
- When would DisposeOnViewTreeLifecycleDestroyed be preferred over DisposeOnLifecycleDestroyed?
- How do you diagnose memory leaks caused by incorrect ViewCompositionStrategy?
- Can you manually trigger Composition disposal without detaching ComposeView?

## Ссылки (RU)

- Официальная документация: https://developer.android.com/jetpack/compose/interop/view-composition-strategy

## References (EN)

- Official docs: https://developer.android.com/jetpack/compose/interop/view-composition-strategy

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-custom-view-lifecycle--android--medium]] - детали жизненного цикла ComposeView

### Связанные (такой Же уровень)
- [[q-custom-view-lifecycle--android--medium]] - детали жизненного цикла ComposeView
- [[q-compose-performance-optimization--android--hard]] - оптимизация производительности

### Продвинутые (сложнее)
- [[q-compose-performance-optimization--android--hard]] - оптимизация производительности

## Related Questions (EN)

### Prerequisites (Easier)
- [[q-custom-view-lifecycle--android--medium]] - ComposeView lifecycle details

### Related (Same Level)
- [[q-custom-view-lifecycle--android--medium]] - ComposeView lifecycle details
- [[q-compose-performance-optimization--android--hard]] - Performance optimization strategies

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance optimization strategies
