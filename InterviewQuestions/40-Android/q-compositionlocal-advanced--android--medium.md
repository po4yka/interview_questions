---
id: 20251020-211200
title: CompositionLocal Advanced / CompositionLocal — продвинутый уровень
aliases:
- CompositionLocal Advanced
- CompositionLocal — продвинутый уровень
topic: android
subtopics:
- ui-compose
- architecture-mvvm
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-compose-remember-derived-state--android--medium
- q-compose-semantics--android--medium
- q-compose-performance-optimization--android--hard
created: 2025-10-20
updated: 2025-10-20
tags:
- android/ui-compose
- android/architecture-mvvm
- difficulty/medium
---

# Вопрос (RU)
> CompositionLocal — продвинутый уровень?

# Question (EN)
> CompositionLocal Advanced?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Why CompositionLocal
- Context for a subtree: theme, locale, density, DI objects
- Removes over‑plumbing through many layers when explicit params hurt readability
- Not a replacement for parameters: use when the dependency is truly environmental

See also [[c-dependency-injection]] and c-compose-state for understanding dependency management in Compose.

### Parameters vs Local
- Parameters — when the dependency is local, frequently changing, and API clarity matters
- CompositionLocal — when the dependency is cross‑cutting, rarely changing, and environmental (theme, haptics, logger, imageLoader)

### staticCompositionLocalOf vs compositionLocalOf
- `compositionLocalOf` (dynamic)
  - Read tracking: only readers of `.current` recompose
  - Fits frequently changing values (scroll position, dynamic flags)
  - Small per‑read overhead
- `staticCompositionLocalOf` (static)
  - No read tracking: updating value invalidates the entire provider subtree
  - Fits rarely changing, widely read values (theme, locale)
  - Cheaper reads, more expensive updates (wide invalidation)

Guideline: if it changes often and you need narrow recomposition — use `compositionLocalOf`; if it rarely changes and is read widely — use `staticCompositionLocalOf`.

### Invalidation boundaries & performance
- Boundary is the `CompositionLocalProvider` block
- Dynamic Local: invalidation propagates only to actual readers
- Static Local: the entire provider subtree is invalidated
- Place providers close to consumers if updates are wide

### Safe defaults
- Risk: silent valid default hides missing provider
- Prefer `error("No Foo provided")` or an explicit noop with clear semantics

### Immutability & stability
- Values should be immutable or explicitly stable
- Update the reference (copy) rather than mutating internals invisibly to Compose
- Improves predictability and skippability

### Common pitfalls
- Reading Local outside composition (in lambdas outliving a frame)
- Using Local as hidden global for business logic
- Provider too high for frequently changing values (excess recomposition)
- Too many tiny providers in hot paths (overhead)

### Patterns
- Thin provider: wrap only the subtree that actually needs the value
- Combined provider: group rarely changing values into a single static Local
- Testability: override Local in tests inside the scene

### Minimal examples

Create and provide:
```kotlin
// Rarely changing global context
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> { error("No AppEnv provided") }

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        content()
    }
}
```

Dynamic Local with narrow recomposition:
```kotlin
val LocalScrollInfo = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        Header()              // does not read Local → no recomposition
        StickyToolbar()       // reads Local → recomposes on change
    }
}
```

---

## Follow-ups
- How to scope providers in multi-module apps?
- When to prefer parameters even if many layers are involved?
- Can CompositionLocal carry mutable state safely?
- How to test provider chains and overrides?

## References
- [CompositionLocal (Docs)](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)
- [[q-compose-semantics--android--medium]]

### Related (Same Level)
- [[q-compose-remember-derived-state--android--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]
