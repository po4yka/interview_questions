---
id: android-014
title: "ViewCompositionStrategy in Compose / ViewCompositionStrategy в Compose"
aliases: ["ViewCompositionStrategy in Compose", "ViewCompositionStrategy в Compose"]
topic: android
subtopics: [lifecycle, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-lifecycle, c-viewcompositionstrategy]
created: 2025-10-05
updated: 2025-10-28
tags: [android/lifecycle, android/ui-compose, compose, difficulty/medium, interop, lifecycle, viewcompositionstrategy]
sources: ["https://developer.android.com/jetpack/compose/interop/view-composition-strategy"]
date created: Saturday, November 1st 2025, 1:24:45 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Вопрос (RU)
> Что такое ViewCompositionStrategy и когда её использовать?

# Question (EN)
> What is ViewCompositionStrategy and when to use it?

---

## Ответ (RU)

**Концепция:**
ViewCompositionStrategy управляет жизненным циклом Composition в ComposeView — определяет, когда освобождать ресурсы. Критично для интеграции Compose в View-based код и предотвращения утечек памяти.

**Основные стратегии:**

1. **DisposeOnDetachedFromWindowOrReleasedFromPool** (по умолчанию)
   - Освобождает Composition при detach от окна или release из RecyclerView pool
   - Подходит для большинства случаев

```kotlin
// ✅ По умолчанию, работает для RecyclerView
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

1. **DisposeOnLifecycleDestroyed**
   - Привязывает Composition к Lifecycle (Fragment, Activity)
   - Освобождается только при onDestroy

```kotlin
// ✅ Для Fragment — избегает преждевременного dispose
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
)
```

1. **DisposeOnViewTreeLifecycleDestroyed**
   - Использует Lifecycle из ViewTreeLifecycleOwner
   - Для случаев, когда Lifecycle недоступен напрямую

```kotlin
// ✅ Когда lifecycle известен только через ViewTree
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
)
```

**Частые ошибки:**

```kotlin
// ❌ Fragment с дефолтной стратегией — утечка после rotate
class MyFragment : Fragment() {
    override fun onCreateView(...) = ComposeView(requireContext()).apply {
        // Composition dispose на onDestroyView, но Fragment жив
        setContent { /* ... */ }
    }
}

// ✅ Правильно для Fragment
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
)
```

**Выбор стратегии:**
- **Fragment**: DisposeOnLifecycleDestroyed (viewLifecycleOwner)
- **RecyclerView**: DisposeOnDetachedFromWindowOrReleasedFromPool (default)
- **Dialog/BottomSheet**: DisposeOnDetachedFromWindow
- **Custom View**: оцените lifetime, обычно default подходит

## Answer (EN)

**Concept:**
ViewCompositionStrategy controls Composition lifecycle in ComposeView — determines when to release resources. Critical for integrating Compose into View-based code and preventing memory leaks.

**Main Strategies:**

1. **DisposeOnDetachedFromWindowOrReleasedFromPool** (default)
   - Releases Composition on detach from window or release from RecyclerView pool
   - Suitable for most cases

```kotlin
// ✅ Default, works for RecyclerView
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

1. **DisposeOnLifecycleDestroyed**
   - Binds Composition to Lifecycle (Fragment, Activity)
   - Releases only on onDestroy

```kotlin
// ✅ For Fragment — avoids premature disposal
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
)
```

1. **DisposeOnViewTreeLifecycleDestroyed**
   - Uses Lifecycle from ViewTreeLifecycleOwner
   - For cases when Lifecycle isn't directly available

```kotlin
// ✅ When lifecycle known only through ViewTree
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
)
```

**Common Mistakes:**

```kotlin
// ❌ Fragment with default strategy — leak after rotation
class MyFragment : Fragment() {
    override fun onCreateView(...) = ComposeView(requireContext()).apply {
        // Composition disposed on onDestroyView, but Fragment alive
        setContent { /* ... */ }
    }
}

// ✅ Correct for Fragment
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(viewLifecycleOwner.lifecycle)
)
```

**Strategy Selection:**
- **Fragment**: DisposeOnLifecycleDestroyed (viewLifecycleOwner)
- **RecyclerView**: DisposeOnDetachedFromWindowOrReleasedFromPool (default)
- **Dialog/BottomSheet**: DisposeOnDetachedFromWindow
- **Custom View**: evaluate lifetime, usually default works

---

## Follow-ups

- What happens if Fragment rotates with the wrong ViewCompositionStrategy?
- How does DisposeOnDetachedFromWindowOrReleasedFromPool handle RecyclerView pooling differently from detach?
- When would DisposeOnViewTreeLifecycleDestroyed be preferred over DisposeOnLifecycleDestroyed?
- How do you diagnose memory leaks caused by incorrect ViewCompositionStrategy?
- Can you manually trigger Composition disposal without detaching ComposeView?

## References

- [[c-compose-lifecycle]] - Compose lifecycle management
- [[c-android-lifecycle]] - Android Lifecycle fundamentals
- Official docs: https://developer.android.com/jetpack/compose/interop/view-composition-strategy

## Related Questions

### Prerequisites (Easier)
- [[q-compose-basics--android--easy]] - Compose fundamentals
- [[q-android-lifecycle--android--easy]] - Lifecycle basics

### Related (Same Level)
- [[q-custom-view-lifecycle--android--medium]] - Compose lifecycle details
- [[q-compose-interop-androidview--android--medium]] - Compose-View interop
- [[q-fragment-lifecycle-viewlifecycle--android--medium]] - Fragment lifecycle nuances

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance optimization strategies
- [[q-memory-leak-detection-android--android--hard]] - Memory leak analysis
