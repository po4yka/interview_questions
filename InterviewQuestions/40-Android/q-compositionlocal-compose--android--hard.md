---
id: 20251021-120500
title: CompositionLocal in Compose / CompositionLocal в Compose
aliases: [CompositionLocal in Compose, CompositionLocal в Compose]
topic: android
subtopics:
  - ui-compose
  - ui-state
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-compose-performance-optimization--android--hard
  - q-compose-remember-derived-state--android--medium
  - q-compositionlocal-advanced--android--medium
created: 2025-10-15
updated: 2025-10-21
tags: [android/ui-compose, android/ui-state, difficulty/hard]
source: https://developer.android.com/jetpack/compose/compositionlocal
source_note: Official docs on CompositionLocal
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:27 pm
---

# Вопрос (RU)
> CompositionLocal в Compose?

# Question (EN)
> CompositionLocal in Compose?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Purpose
- Local "context" for a subtree: theme, locale, density, haptics, UI‑level DI objects
- Avoids over‑plumbing parameters when the dependency is environmental
- Not a replacement for parameters: do not hide business data/state in Locals

Based on concepts from [[c-dependency-injection]] and c-compose-state.

### Parameters Vs CompositionLocal
- Parameters: local dependency, changes frequently, API clarity
- Local: cross‑cutting, rarely changing, environmental (theme, locale, imageLoader)

### Dynamic Vs Static
- `compositionLocalOf` (dynamic)
  - Read tracking: only actual `.current` readers recompose
  - Fits frequently changing values (scroll position, runtime flags)
  - Small per‑read overhead
- `staticCompositionLocalOf` (static)
  - No read tracking: update invalidates entire provider subtree
  - Fits rarely changing, widely read values (theme, locale)
  - Cheaper reads, more expensive updates (wide invalidation)

Rule of thumb: changes often + narrow recomposition → `compositionLocalOf`; rarely changes + wide readership → `staticCompositionLocalOf`.

### Invalidation Boundaries
- Boundary is `CompositionLocalProvider`
- Dynamic: invalidates only readers; static: whole subtree
- Place providers close to consumers if updates are wide/frequent

### Safe Defaults
- Avoid silent valid defaults; prefer throwing in factory or explicit noop

### Immutability & Stability
- Prefer immutable or explicitly stable values
- Update the reference (copy) vs mutating internals invisibly to Compose

### Pitfalls
- Reading Local outside composition (long‑lived lambdas)
- Using Local for business logic/repos instead of DI
- Provider too high for frequently changing value → extra recomposition

### Patterns
- Thin provider over only the necessary subtree
- Combine rare static values under one provider
- Override Locals in tests within the scene

### Minimal Examples

Create & provide (static context):
```kotlin
// Rarely changing global context
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> { error("No AppEnv provided") }

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) { content() }
}
```

Dynamic Local with narrow recomposition:
```kotlin
val LocalScrollY = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollY provides scrollY) {
        Header()              // does not read → no recomposition
        StickyToolbar()       // reads Local → recomposes on change
    }
}
```

---

## Follow-ups
- How to scope providers across feature modules?
- When are parameters still preferable despite deep trees?
- How to profile invalidation caused by Local updates?
- Strategies for testing and overriding chains of providers?

## References
- [CompositionLocal (Docs)](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)
- [[q-compose-semantics--android--medium]]

### Related (Same Level)
- [[q-compositionlocal-advanced--android--medium]]
- [[q-compose-remember-derived-state--android--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]
