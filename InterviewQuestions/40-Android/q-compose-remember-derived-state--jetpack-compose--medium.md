---
id: 20251012-1227107
title: Compose remember/derivedStateOf / remember и derivedStateOf в Compose
aliases: [Compose remember and derivedStateOf, remember и derivedStateOf]
topic: android
subtopics: [ui-compose, state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/develop/ui/compose/state
source_note: Official Compose state docs
status: draft
moc: moc-android
related: [q-remember-vs-remembersaveable-compose--android--medium, q-compose-performance-optimization--android--hard, q-compose-compiler-plugin--jetpack-compose--hard]
created: 2025-10-15
updated: 2025-10-20
tags: [android/ui-compose, compose/state, performance, difficulty/medium]
---
# Question (EN)
> What are `remember`, `rememberSaveable`, and `derivedStateOf` in Compose? When to use each to optimize recomposition and handle process death?

# Вопрос (RU)
> Что такое `remember`, `rememberSaveable` и `derivedStateOf` в Compose? Когда использовать каждую, чтобы оптимизировать рекомпозицию и переживать завершение процесса?

---

## Answer (EN)

### Concepts
- remember: caches values in composition; survives recomposition only.
- rememberSaveable: persists across config changes and process death (uses Bundle/Saver).
- derivedStateOf: computes a value that only invalidates when RESULT changes.

### Minimal patterns

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

## Ответ (RU)

### Концепции
- remember: кэширует значения в composition; переживает только рекомпозиции.
- rememberSaveable: сохраняет через изменение конфигурации и завершение процесса (Bundle/Saver).
- derivedStateOf: вычисляет значение, которое инвалидируется только при ИЗМЕНЕНИИ РЕЗУЛЬТАТА.

### Минимальные паттерны

remember (в рамках composition)
- Для временного UI‑состояния или кэширования вычислений, зависящих от параметров.
```kotlin
@Composable
fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button({ count++ }) { Text("Count: $count") }
}
```

remember с ключами
- Сбрасывает кэш при изменении ключей.
```kotlin
val userData by remember(userId) { mutableStateOf<User?>(null) }
```

rememberSaveable (персистентность)
- Для ввода/навигации, которые должны переживать пересоздание; для сложных типов — Saver.
```kotlin
@Composable
fun Login() {
  var email by rememberSaveable { mutableStateOf("") }
  var password by rememberSaveable { mutableStateOf("") }
  TextField(email, { email = it }); TextField(password, { password = it })
}
```

Пользовательский Saver
```kotlin
@Stable data class Form(val email: String, val agree: Boolean)
val FormSaver = mapSaver(
  save = { mapOf("e" to it.email, "a" to it.agree) },
  restore = { Form(it["e"] as String, it["a"] as Boolean) }
)
var form by rememberSaveable(stateSaver = FormSaver) { mutableStateOf(Form("", false)) }
```

derivedStateOf (вычисляемое состояние)
- Уменьшает инвалидации; рекомпозиция только при изменении результата, а не любой зависимости.
```kotlin
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

Сравнение (когда использовать)
- remember: кэш в composition; не для персистентности.
- rememberSaveable: сохранять ввод/навигацию; нужны поддерживаемые типы или Saver.
- derivedStateOf: кэш производного значения; обычно вместе с remember.

---

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
- [[q-compose-compiler-plugin--jetpack-compose--hard]]

### Advanced (Harder)
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]]

