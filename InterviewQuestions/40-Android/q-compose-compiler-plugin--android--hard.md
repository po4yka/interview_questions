---
id: 20251012-122803
title: Compose Compiler Plugin / Плагин компилятора Compose
aliases: [Compose Compiler Plugin, Плагин компилятора Compose]
topic: android
subtopics:
  - performance-memory
  - ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-animated-visibility-vs-content--android--medium
  - q-compose-canvas-graphics--android--hard
created: 2025-10-11
updated: 2025-10-20
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:41 pm
---

# Вопрос (RU)
> Плагин компилятора Compose?

# Question (EN)
> Compose Compiler Plugin?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### What the Plugin Does (high level)
- Lowers `@Composable` functions to state machines; inserts composer parameters, keys, groups
- Infers parameter stability (Stable/Unstable) to decide if recomposition can be skipped
- Marks calls restartable/skippable; generates slot table read/write operations
- Transforms code using compiler plugin and [[c-algorithms]] for optimization decisions

### Stability & Skipping (theory)
- Stable params that are referentially equal → call is skippable
- Unstable params or changed identity/content → recomposition executes
- Collections/MutableState wrappers impact stability; prefer stable immutable models

### Minimal Examples
Stable model → fewer recompositions:
```kotlin
@Immutable data class User(val id: String, val name: String)
@Composable fun UserRow(user: User) { /* draw using stable fields */ }
```

Avoid unstable mutable props in parameters:
```kotlin
// BAD: passing mutable list triggers recomposition often
@Composable fun ListScreen(items: MutableList<Item>) { /* ... */ }

// GOOD: expose SnapshotStateList via stable facade or pass immutable List
@Composable fun ListScreen(items: List<Item>) { /* ... */ }
```

Hoist state and keep parameters stable:
```kotlin
@Composable fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button(onClick = { count++ }) { Text("$count") } // only Text recomposes
}
```

### Diagnostics (reports)
- Enable compiler metrics/reports to inspect stability/skipping decisions and call graphs
- Review: which calls are restartable/skippable; which types are unstable; large group counts

Minimal Gradle flags (no versions):
```bash
# gradle.properties or CI flags
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
compose.compiler.metricsDestination=build/compose-metrics
```

### Performance Practices
- Prefer @Immutable/@Stable for domain models when semantics apply
- Keep large objects out of parameters; pass keys/ids instead
- Move heavy work off composition; use remember + derivedStateOf
- Avoid recomposition cascades: break trees with subcomposables, remember

## Follow-ups
- How to interpret compiler stability reports and fix unstable types?
- What are trade‑offs of @Stable/@Immutable annotations vs real immutability?
- How to validate recomposition counts (Macrobenchmark tracing)?

## References
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
