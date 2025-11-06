---
id: android-311
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
status: reviewed
moc: moc-android
related:
  - q-compose-compiler-plugin--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-slot-table-recomposition--android--hard
  - q-remember-vs-remembersaveable-compose--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-02
tags: [android/ui-compose, android/ui-state, difficulty/medium]
---

# Вопрос (RU)
> Что такое remember и derivedStateOf в Jetpack Compose? Когда и как их использовать?

# Question (EN)
> What are remember and derivedStateOf in Jetpack Compose? When and how to use them?

---

## Ответ (RU)

### Основные Концепции

**`remember`** — кеширует значения в композиции; переживает рекомпозицию, но не пересоздание активити.

**`rememberSaveable`** — сохраняет значения через изменения конфигурации и смерть процесса (использует `Bundle`/`Saver`).

**`derivedStateOf`** — вычисляет производное состояние, которое инвалидируется только при изменении результата, а не зависимостей.

### Паттерны Использования

#### Remember (область композиции)

Используйте для временного UI-состояния или кешированных вычислений, привязанных к параметрам.

```kotlin
// ✅ Простой счетчик в UI
@Composable
fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button({ count++ }) { Text("Count: $count") }
}
```

#### Remember С Ключами

Сбрасывает кешированное значение при изменении ключа.

```kotlin
// ✅ Пересоздание состояния при смене userId
val userData by remember(userId) {
  mutableStateOf<User?>(null)
}
```

#### `rememberSaveable` (персистентность)

Используйте для input-полей и навигационного состояния, которое должно пережить пересоздание.

```kotlin
// ✅ Форма логина переживает поворот экрана
@Composable
fun Login() {
  var email by rememberSaveable { mutableStateOf("") }
  var password by rememberSaveable { mutableStateOf("") }
  TextField(email, { email = it })
  TextField(password, { password = it })
}
```

#### Custom `Saver` Для Сложных Типов

```kotlin
data class Form(val email: String, val agree: Boolean)

val FormSaver = mapSaver(
  save = { mapOf("e" to it.email, "a" to it.agree) },
  restore = { Form(it["e"] as String, it["a"] as Boolean) }
)

var form by rememberSaveable(stateSaver = FormSaver) {
  mutableStateOf(Form("", false))
}
```

#### `derivedStateOf` (вычисляемое состояние)

Уменьшает количество рекомпозиций: перерисовка происходит только когда меняется вычисленное значение, а не зависимости.

```kotlin
// ✅ FAB показывается только когда прокрутили вниз
val listState = rememberLazyListState()
val showFab by remember {
  derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

// ❌ Без `derivedStateOf` — рекомпозиция при каждом скролле
val showFabWrong = listState.firstVisibleItemIndex > 0
```

### Когда Что Использовать

| Функция | Область видимости | Персистентность | Применение |
|---------|-------------------|-----------------|------------|
| **remember** | Композиция | Нет | Временное UI-состояние, кеш |
| **rememberSaveable** | Процесс + Bundle | Да | Формы, input, навигация |
| **derivedStateOf** | С remember | Как remember | Вычисляемые значения |

## Answer (EN)

### Core Concepts

**`remember`** — caches values in composition; survives recomposition but not activity recreation.

**`rememberSaveable`** — persists across config changes and process death (uses `Bundle`/`Saver`).

**`derivedStateOf`** — computes derived state that invalidates only when result changes, not dependencies.

### Usage Patterns

#### Remember (composition-scoped)

Use for temporary UI state or cached computations tied to parameters.

```kotlin
// ✅ Simple counter in UI
@Composable
fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button({ count++ }) { Text("Count: $count") }
}
```

#### Remember with Keys

Resets cached value when key changes.

```kotlin
// ✅ Recreate state when userId changes
val userData by remember(userId) {
  mutableStateOf<User?>(null)
}
```

#### `rememberSaveable` (persistence)

Use for input fields and navigation state that must survive recreation.

```kotlin
// ✅ Login form survives screen rotation
@Composable
fun Login() {
  var email by rememberSaveable { mutableStateOf("") }
  var password by rememberSaveable { mutableStateOf("") }
  TextField(email, { email = it })
  TextField(password, { password = it })
}
```

#### Custom `Saver` for Complex Types

```kotlin
data class Form(val email: String, val agree: Boolean)

val FormSaver = mapSaver(
  save = { mapOf("e" to it.email, "a" to it.agree) },
  restore = { Form(it["e"] as String, it["a"] as Boolean) }
)

var form by rememberSaveable(stateSaver = FormSaver) {
  mutableStateOf(Form("", false))
}
```

#### `derivedStateOf` (computed state)

Reduces recompositions: redraws only when computed value changes, not dependencies.

```kotlin
// ✅ FAB shows only when scrolled down
val listState = rememberLazyListState()
val showFab by remember {
  derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

// ❌ Without `derivedStateOf` — recomposition on every scroll
val showFabWrong = listState.firstVisibleItemIndex > 0
```

### When to Use What

| Function | Scope | Persistence | Use Case |
|----------|-------|-------------|----------|
| **remember** | Composition | No | Temporary UI state, cache |
| **rememberSaveable** | Process + Bundle | Yes | Forms, inputs, navigation |
| **derivedStateOf** | With remember | Like remember | Computed values |

---

## Follow-ups

- How does `derivedStateOf` affect performance when used with fast-changing state?
- What are the `Bundle` size limitations for `rememberSaveable` and how to handle large objects?
- Can you nest `derivedStateOf` calls, and what are the implications?
- How does `remember` with keys compare to `LaunchedEffect` for triggering side effects on parameter changes?
- What happens if you use `derivedStateOf` without wrapping it in `remember`?

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [Compose State Documentation](https://developer.android.com/develop/ui/compose/state)
- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)

## Related Questions

### Prerequisites (Easier)
- [[q-remember-vs-remembersaveable-compose--android--medium]] — Basic difference between remember variants

### Related (Same Level)
- State management patterns in Compose
- Recomposition optimization techniques

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] — Advanced performance optimization techniques
- [[q-compose-compiler-plugin--android--hard]] — How Compose compiler optimizes state
- [[q-compose-slot-table-recomposition--android--hard]] — Deep dive into recomposition mechanics
