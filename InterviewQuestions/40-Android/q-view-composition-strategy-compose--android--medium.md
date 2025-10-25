---
id: 20251012-122711126
title: "ViewCompositionStrategy in Compose / ViewCompositionStrategy в Compose"
aliases:
  - "ViewCompositionStrategy in Compose"
  - "ViewCompositionStrategy в Compose"
topic: android
subtopics: [ui-compose, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-viewcompositionstrategy, q-compose-lifecycle--android--medium, q-compose-performance-optimization--android--hard]
created: 2025-10-05
updated: 2025-01-25
tags: [android/ui-compose, android/lifecycle, compose, viewcompositionstrategy, lifecycle, interop, difficulty/medium]
sources: [https://developer.android.com/jetpack/compose/interop/view-composition-strategy]
---

# Вопрос (RU)
> Что такое ViewCompositionStrategy и когда ее использовать?

# Question (EN)
> What is ViewCompositionStrategy and when to use it?

---

## Ответ (RU)

**Теория ViewCompositionStrategy:**
ViewCompositionStrategy определяет, когда Composition должна быть уничтожена. Это критично для управления жизненным циклом Compose в смешанных View/Compose приложениях и предотвращения утечек памяти.

**Основные стратегии:**
ViewCompositionStrategy предоставляет четыре стратегии для управления жизненным циклом Composition.

```kotlin
// Стратегия по умолчанию - для большинства случаев
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)

// Для Fragment - привязка к жизненному циклу
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(lifecycle)
)
```

**DisposeOnDetachedFromWindowOrReleasedFromPool (по умолчанию):**
Уничтожает Composition при отсоединении от окна или освобождении из пула (RecyclerView).

```kotlin
// Автоматически обрабатывает RecyclerView pooling
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

**DisposeOnLifecycleDestroyed:**
Уничтожает Composition при уничтожении предоставленного Lifecycle.

```kotlin
// Для Fragment - привязка к жизненному циклу Fragment
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(fragment.lifecycle)
)
```

**DisposeOnViewTreeLifecycleDestroyed:**
Уничтожает Composition при уничтожении Lifecycle из ViewTree.

```kotlin
// Когда Lifecycle еще не известен
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
)
```

**Выбор стратегии:**
- По умолчанию: для большинства случаев, включая RecyclerView
- LifecycleDestroyed: для Fragment
- ViewTreeLifecycleDestroyed: когда Lifecycle неизвестен

## Answer (EN)

**ViewCompositionStrategy Theory:**
ViewCompositionStrategy defines when Composition should be disposed. This is critical for managing Compose lifecycle in mixed View/Compose apps and preventing memory leaks.

**Main Strategies:**
ViewCompositionStrategy provides four strategies for managing Composition lifecycle.

```kotlin
// Default strategy - for most cases
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)

// For Fragment - bind to lifecycle
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(lifecycle)
)
```

**DisposeOnDetachedFromWindowOrReleasedFromPool (default):**
Disposes Composition when detached from window or released from pool (RecyclerView).

```kotlin
// Automatically handles RecyclerView pooling
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

**DisposeOnLifecycleDestroyed:**
Disposes Composition when provided Lifecycle is destroyed.

```kotlin
// For Fragment - bind to Fragment lifecycle
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(fragment.lifecycle)
)
```

**DisposeOnViewTreeLifecycleDestroyed:**
Disposes Composition when ViewTree Lifecycle is destroyed.

```kotlin
// When Lifecycle is not yet known
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
)
```

**Strategy Selection:**
- Default: for most cases, including RecyclerView
- LifecycleDestroyed: for Fragment
- ViewTreeLifecycleDestroyed: when Lifecycle unknown

---

## Follow-ups

- How does ViewCompositionStrategy affect memory management?
- What happens if you use the wrong strategy?
- How do you handle ViewCompositionStrategy in RecyclerView?

## Related Questions

### Prerequisites (Easier)
- [[q-compose-basics--android--easy]] - Compose basics
- [[q-android-lifecycle--android--easy]] - Lifecycle management

### Related (Same Level)
- [[q-compose-lifecycle--android--medium]] - Compose lifecycle
- [[q-compose-performance-optimization--android--hard]] - Performance optimization
- [[q-compose-modifier-order-performance--android--medium]] - Modifier performance

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts
- [[q-android-runtime-internals--android--hard]] - Runtime internals
