---
id: 20251012-122710
title: Compose remember/derivedStateOf / remember и derivedStateOf в Compose
aliases: [Compose remember and derivedStateOf, remember и derivedStateOf]
topic: android
subtopics:
  - ui-compose
  - ui-state
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-compose-compiler-plugin--android--hard
  - q-compose-performance-optimization--android--hard
  - q-remember-vs-remembersaveable-compose--android--medium
created: 2025-10-15
updated: 2025-10-20
tags: [android/ui-compose, android/ui-state, difficulty/medium]
source: https://developer.android.com/develop/ui/compose/state
source_note: Official Compose state docs
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:37 pm
---

# Вопрос (RU)
> remember и derivedStateOf в Compose?

# Question (EN)
> Compose remember/derivedStateOf?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Concepts
- remember: caches values in composition; survives recomposition only.
- rememberSaveable: persists across config changes and process death (uses Bundle/Saver).
- derivedStateOf: computes a value that only invalidates when RESULT changes.
- Builds on [[c-data-structures]] for efficient state caching and [[c-algorithms]] for change detection.

### Minimal Patterns

remember (composition‑scoped)
- Use for temporary UI state or cached computations tied to parameters.
```kotlin
@Composable
fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button({ count++ }) { Text("Count: $count") }
}
```

remember with keys
- Resets cached value when key(s) change.
```kotlin
val userData by remember(userId) { mutableStateOf<User?>(null) }
```

rememberSaveable (persists)
- Use for inputs/navigation state that must survive recreation; provide Saver for complex types.
```kotlin
@Composable
fun Login() {
  var email by rememberSaveable { mutableStateOf("") }
  var password by rememberSaveable { mutableStateOf("") }
  TextField(email, { email = it }); TextField(password, { password = it })
}
```

Custom Saver
```kotlin
@Stable data class Form(val email: String, val agree: Boolean)
val FormSaver = mapSaver(
  save = { mapOf("e" to it.email, "a" to it.agree) },
  restore = { Form(it["e"] as String, it["a"] as Boolean) }
)
var form by rememberSaveable(stateSaver = FormSaver) { mutableStateOf(Form("", false)) }
```

derivedStateOf (computed state)
- Reduces invalidations; recomposes only when computed value changes, not every dependency change.
```kotlin
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

Comparison (when to use)
- remember: cache within composition; not for persistence.
- rememberSaveable: persist user input/navigation; requires supported types or Saver.
- derivedStateOf: cache computed value that changes infrequently; pair with remember.

## Follow-ups
- When does derivedStateOf hurt performance (overuse on fast‑changing inputs)?
- How to design Savers for nested immutable models?
- How to test process‑death resilience of forms and wizards?

## References
- https://developer.android.com/develop/ui/compose/state
- https://developer.android.com/jetpack/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-remember-vs-remembersaveable-compose--android--medium]]

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]]
- [[q-compose-compiler-plugin--android--hard]]

### Advanced (Harder)
- [[q-compose-slot-table-recomposition--android--hard]]
