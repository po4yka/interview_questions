---
id: android-311
title: Compose remember/derivedStateOf / remember и derivedStateOf в Compose
aliases:
- Compose remember and derivedStateOf
- remember и derivedStateOf
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
- c-compose-state
- q-compose-compiler-plugin--android--hard
- q-compose-gesture-detection--android--medium
- q-compose-performance-optimization--android--hard
- q-compose-slot-table-recomposition--android--hard
- q-mutable-state-compose--android--medium
- q-recomposition-compose--android--medium
- q-remember-vs-remembersaveable-compose--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-compose
- android/ui-state
- difficulty/medium
anki_cards:
- slug: android-311-0-en
  language: en
  anki_id: 1768366070426
  synced_at: '2026-01-23T16:45:06.106500'
- slug: android-311-0-ru
  language: ru
  anki_id: 1768366070450
  synced_at: '2026-01-23T16:45:06.107388'
---
# Вопрос (RU)
> Что такое remember и derivedStateOf в Jetpack Compose? Когда и как их использовать?

# Question (EN)
> What are remember and derivedStateOf in Jetpack Compose? When and how to use them?

---

## Ответ (RU)

### Основные Концепции

**`remember`** — кеширует значения в композиции; переживает рекомпозицию, но не пересоздание активити/хоста композиции.

**`rememberSaveable`** — сохраняет значения через изменения конфигурации и может быть восстановлен после смерти процесса за счет механизма `SavedInstanceState` (использует `Bundle`/`Saver`), если хост (`Activity` / NavBackStackEntry и т.п.) правильно интегрирован с SavedState и восстанавливает состояние.

**`derivedStateOf`** — описывает производное состояние на основе других состояний. Инвалидируется при изменении зависимостей и сравнивает новое значение с предыдущим: только при фактическом изменении производного значения уведомляются его потребители. Это уменьшает лишние обновления для тех, кто подписан именно на производное состояние.

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

Используйте для input-полей и навигационного состояния, которое должно пережить пересоздание `Activity`/хоста при конфигурационных изменениях и (при наличии SavedState) восстановиться после убийства процесса.

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

Используется для мемоизации производных значений и уменьшения лишних уведомлений/рекомпозиций потребителей этого производного состояния. Когда зависящие состояния меняются, но вычисленное производное значение остается тем же, потребители `derivedStateOf` не будут перерисованы.

```kotlin
// ✅ FAB показывается только когда прокрутили вниз
val listState = rememberLazyListState()
val showFab by remember {
  derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

// ⚠️ Без `derivedStateOf`, если это условие используется в нескольких местах
//     или вычисление более дорогое, оно будет пересчитываться каждый раз отдельно.
//     `derivedStateOf` позволяет централизовать вычисление и уведомлять потребителей
//     только при реальном изменении значения.
val showFabDirect = listState.firstVisibleItemIndex > 0
```

### Когда Что Использовать

| Функция | Область видимости | Персистентность | Применение |
|---------|-------------------|-----------------|------------|
| **remember** | Композиция | Нет | Временное UI-состояние, кеш |
| **rememberSaveable** | Там, где есть SavedState (`Bundle`) | Да, при восстановлении SavedInstanceState | Формы, input, навигация |
| **derivedStateOf** | Обычно вместе с `remember` | Зависит от того, как обернуто (например, в `remember`) | Вычисляемые/производные значения |

## Answer (EN)

### Core Concepts

**`remember`** — caches values in the composition; survives recomposition but not `Activity`/composition host recreation.

**`rememberSaveable`** — persists values across configuration changes and can be restored after process death via the `SavedInstanceState` mechanism (uses `Bundle`/`Saver`), provided the host (`Activity` / NavBackStackEntry, etc.) is properly integrated with SavedState and restores that state.

**`derivedStateOf`** — describes derived state based on other states. It is invalidated when its dependencies change and compares the new value to the previous one; only when the derived value actually changes are its consumers notified. This reduces unnecessary updates for observers of that derived state.

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

Use for input fields and navigation state that must survive `Activity`/host recreation on configuration changes and (with proper SavedState integration) be restored after process death.

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

Use to memoize derived values and reduce unnecessary updates/recompositions of the consumers of that derived state. When dependencies change but the derived value remains the same, those consumers are not recomposed.

```kotlin
// ✅ FAB shows only when scrolled down
val listState = rememberLazyListState()
val showFab by remember {
  derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

// ⚠️ Without `derivedStateOf`, if this condition is used in multiple places
//     or is more expensive, it will be recomputed each time separately.
//     `derivedStateOf` centralizes the computation and notifies consumers
//     only when the value actually changes.
val showFabDirect = listState.firstVisibleItemIndex > 0
```

### When to Use What

| Function | Scope | Persistence | Use Case |
|----------|-------|-------------|----------|
| **remember** | Composition | No | Temporary UI state, cache |
| **rememberSaveable** | Where SavedState (`Bundle`) is available | Yes, when SavedInstanceState is restored | Forms, inputs, navigation |
| **derivedStateOf** | Typically wrapped in `remember` | Depends on how it's wrapped (e.g., in `remember`) | Computed/derived values |

---

## Дополнительные Вопросы (RU)

- Как `derivedStateOf` влияет на производительность при работе с часто изменяющимся состоянием?
- Каковы ограничения размера `Bundle` для `rememberSaveable` и как работать с крупными объектами?
- Можно ли вкладывать вызовы `derivedStateOf` друг в друга и как это влияет на производительность и читаемость?
- Чем `remember` с ключами отличается от `LaunchedEffect` при срабатывании побочных эффектов на изменения параметров?
- Что произойдет, если использовать `derivedStateOf` без обертки в `remember`?

## Follow-ups

- How does `derivedStateOf` affect performance when used with fast-changing state?
- What are the `Bundle` size limitations for `rememberSaveable` and how to handle large objects?
- Can you nest `derivedStateOf` calls, and what are the implications?
- How does `remember` with keys compare to `LaunchedEffect` for triggering side effects on parameter changes?
- What happens if you use `derivedStateOf` without wrapping it in `remember`?

## Ссылки (RU)

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [Документация по состоянию в Compose](https://developer.android.com/develop/ui/compose/state)
- [Руководство по производительности Compose](https://developer.android.com/jetpack/compose/performance)

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [Compose State Documentation](https://developer.android.com/develop/ui/compose/state)
- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-remember-vs-remembersaveable-compose--android--medium]] — Базовые отличия вариантов `remember`

### Связанное (тот Же уровень)
- Паттерны управления состоянием в Compose
- Техники оптимизации рекомпозиции в Compose

### Продвинутое (сложнее)
- [[q-compose-performance-optimization--android--hard]] — Продвинутые техники оптимизации производительности
- [[q-compose-compiler-plugin--android--hard]] — Как компилятор Compose оптимизирует состояние
- [[q-compose-slot-table-recomposition--android--hard]] — Подробный разбор механики рекомпозиции

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
