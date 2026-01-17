---
id: android-029
title: remember vs rememberSaveable in Compose / remember vs rememberSaveable в Compose
aliases: [remember vs rememberSaveable in Compose, remember vs rememberSaveable в Compose]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, c-recomposition, q-compose-core-components--android--medium, q-compose-remember-derived-state--android--medium, q-how-animations-work-in-recyclerview--android--medium, q-remember-vs-remembersaveable-compose--android--medium, q-transaction-too-large-exception--android--medium]
created: 2025-10-06
updated: 2025-11-11
tags: [android/ui-compose, android/ui-state, difficulty/medium, en, ru]
anki_cards:
  - slug: android-029-0-en
    front: "What is the difference between remember and rememberSaveable in Compose?"
    back: |
      **remember** - survives recomposition only
      ```kotlin
      var count by remember { mutableStateOf(0) }
      // Lost on: config change, process death
      ```

      **rememberSaveable** - survives config changes + process death
      ```kotlin
      var count by rememberSaveable { mutableStateOf(0) }
      // Uses Bundle via SavedStateRegistry
      ```

      **Use rememberSaveable for:**
      - User input (text fields)
      - Scroll position
      - UI state that should survive rotation

      **Limitation:** Only `Bundle`-compatible types or custom `Saver`.
    tags:
      - android_compose
      - difficulty::medium
  - slug: android-029-0-ru
    front: "В чём разница между remember и rememberSaveable в Compose?"
    back: |
      **remember** - переживает только рекомпозицию
      ```kotlin
      var count by remember { mutableStateOf(0) }
      // Теряется при: config change, process death
      ```

      **rememberSaveable** - переживает config changes + process death
      ```kotlin
      var count by rememberSaveable { mutableStateOf(0) }
      // Использует Bundle через SavedStateRegistry
      ```

      **Использовать rememberSaveable для:**
      - Пользовательский ввод (текстовые поля)
      - Позиция скролла
      - UI state, который должен пережить поворот

      **Ограничение:** Только `Bundle`-совместимые типы или кастомный `Saver`.
    tags:
      - android_compose
      - difficulty::medium
---
# Вопрос (RU)
> В чем разница между `remember` и `rememberSaveable` в Jetpack Compose?

# Question (EN)
> What is the difference between `remember` and `rememberSaveable` in Jetpack Compose?

---

## Ответ (RU)

`remember` хранит значение только между рекомпозициями. `rememberSaveable` хранит значение между рекомпозициями и при изменениях конфигурации, используя `Bundle` через `SavedStateRegistry` (что позволяет восстановить состояние после пересоздания процесса при использовании в корректном хосте, например `Activity`/`NavBackStackEntry`).

### Remember — Переживает Только Рекомпозицию

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Переживает: Рекомпозицию
// - Теряется при: Изменении конфигурации, пересоздании процесса
```

### rememberSaveable — Переживает Изменения Конфигурации

```kotlin
@Composable
fun Counter() {
    var count by rememberSaveable { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Переживает: Рекомпозицию, изменения конфигурации и может быть восстановлено после пересоздания процесса,
//   если используется в хосте с SavedStateRegistry (например, Activity, NavBackStackEntry).
// - Реализация: Автоматически сохраняет состояние в совместимый с Bundle формат (или через Saver).
```

### Сравнение

| Особенность | remember | rememberSaveable |
|------------|----------|------------------|
| Рекомпозиция | Переживает | Переживает |
| Изменение конфигурации | Теряется | Переживает (через SavedStateRegistry/`Bundle`) |
| Пересоздание процесса | Теряется | Может быть восстановлено при наличии SavedStateRegistry |
| Поддерживаемые типы | Любые типы Kotlin (без требований к сериализации) | Типы, поддерживаемые `Bundle`: примитивы, `String`, массивы, `Parcelable`, `Serializable` и др., либо любые типы через `Saver` |
| Производительность | Без сериализации; обычно дешевле | Возможна (де)сериализация; немного дороже |

### Когда Использовать

Используйте `remember` для:
- Временного UI-состояния (развернуто/свернуто)
- Состояния анимаций
- Состояния фокуса
- Больших/сложных объектов, которые не нужно и неэффективно сериализовать
- Состояния скролла/взаимодействий, если его не нужно сохранять при изменении конфигурации (например, `rememberScrollState`)

```kotlin
@Composable
fun ExpandableCard() {
    var isExpanded by remember { mutableStateOf(false) }  // Только UI-состояние

    Card(
        modifier = Modifier.clickable { isExpanded = !isExpanded }
    ) {
        if (isExpanded) { ExpandedContent() }
    }
}
```

Используйте `rememberSaveable` для:
- Пользовательского ввода (текстовые поля, выборы)
- Запросов фильтрации/поиска
- Индекса выбранной вкладки
- Данных формы
- Любого пользовательского состояния малого/среднего размера, которое должно пережить изменение конфигурации и быть восстановлено после пересоздания процесса

```kotlin
@Composable
fun SearchScreen() {
    var searchQuery by rememberSaveable { mutableStateOf("") }  // Переживает поворот и может быть восстановлен

    TextField(
        value = searchQuery,
        onValueChange = { searchQuery = it }
    )
}
```

### Пользовательский Saver Для Сложных Объектов

```kotlin
data class User(val id: String, val name: String)

val UserSaver = Saver<User, Map<String, String>>(
    save = { user -> mapOf("id" to user.id, "name" to user.name) },
    restore = { map ->
        val id = map["id"]
        val name = map["name"]
        if (id != null && name != null) User(id, name) else null
    }
)

@Composable
fun UserProfile() {
    var user by rememberSaveable(stateSaver = UserSaver) {
        mutableStateOf(User("1", "Alice"))
    }
}
```

Краткое содержание (RU): `remember` хранит состояние только в рамках текущей композиции и теряется при изменении конфигурации и пересоздании процесса. `rememberSaveable` сохраняет состояние в совместимом с `Bundle` виде через `SavedStateRegistry`, благодаря чему оно переживает изменения конфигурации и может быть восстановлено после пересоздания процесса при использовании в соответствующем хосте. Используйте `remember` для эфемерного/UI-состояния; `rememberSaveable` — для пользовательского состояния, важного для UX.

---

## Answer (EN)

`remember` stores value across recompositions only. `rememberSaveable` stores value across recompositions and configuration changes by saving to a `Bundle` via `SavedStateRegistry` (so it can also be restored after process recreation when used in a proper owner, e.g. `Activity`/`NavBackStackEntry`).

### Remember — Survives Recomposition Only

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Survives: Recomposition
// - Lost on: Configuration change, process death
```

### rememberSaveable — Survives Configuration Changes

```kotlin
@Composable
fun Counter() {
    var count by rememberSaveable { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Survives: Recomposition, configuration changes, and can be restored after process recreation
//   when used in a host that provides SavedStateRegistry (e.g., Activity, NavBackStackEntry).
// - Implementation: Saves to Bundle-compatible state automatically (or via Saver).
```

### Comparison Table

| Feature | remember | rememberSaveable |
|---------|----------|------------------|
| **Recomposition** | Survives | Survives |
| **Config change** | Lost | Survives (via SavedStateRegistry/`Bundle`) |
| **Process recreation** | Lost | Can be restored when SavedStateRegistry is available |
| **Types supported** | Any Kotlin type (no persistence requirement) | Types that can be stored in `Bundle`: primitives, `String`, arrays, `Parcelable`, `Serializable`, etc., or any type via `Saver` |
| **Performance** | No serialization; generally cheaper | May involve (de)serialization; slightly higher cost |

### When to Use Each

Use `remember` for:
- Temporary UI-only state (expanded/collapsed)
- Animation state
- Focus state
- Large/complex objects that should not be persisted or serialized
- Scroll/interaction state when it does not need to survive configuration changes (e.g. `rememberScrollState`)

```kotlin
@Composable
fun ExpandableCard() {
    var isExpanded by remember { mutableStateOf(false) }  // UI-only state

    Card(
        modifier = Modifier.clickable { isExpanded = !isExpanded }
    ) {
        if (isExpanded) { ExpandedContent() }
    }
}
```

Use `rememberSaveable` for:
- User input (text fields, selections)
- Filter/search queries
- Selected tab index
- Form data
- Any small/medium UI state that should survive configuration changes and be restorable after process recreation

```kotlin
@Composable
fun SearchScreen() {
    var searchQuery by rememberSaveable { mutableStateOf("") }  // Survives rotation and can be restored

    TextField(
        value = searchQuery,
        onValueChange = { searchQuery = it }
    )
}
```

### Custom Saver for Complex Objects

```kotlin
data class User(val id: String, val name: String)

val UserSaver = Saver<User, Map<String, String>>(
    save = { user -> mapOf("id" to user.id, "name" to user.name) },
    restore = { map ->
        val id = map["id"]
        val name = map["name"]
        if (id != null && name != null) User(id, name) else null
    }
)

@Composable
fun UserProfile() {
    var user by rememberSaveable(stateSaver = UserSaver) {
        mutableStateOf(User("1", "Alice"))
    }
}
```

English Summary: `remember` keeps state only for the current composition lifecycle (lost on config changes/process death). `rememberSaveable` keeps state across recompositions and saves/restores it via `Bundle`/`SavedStateRegistry` so it survives configuration changes and can be restored after process recreation when used with a proper owner. Use `remember` for ephemeral/UI-only/non-persistable state; use `rememberSaveable` for user-visible state that should be preserved.

---

## Follow-ups

- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-transaction-too-large-exception--android--medium]]
- Как вы объясните различия между `remember`/`rememberSaveable` и управлением состоянием на уровне `ViewModel`?
- В каких случаях вы бы отказались от `rememberSaveable` в пользу хранения состояния вне Compose-иерархии?
- Как бы вы реализовали сохранение сложного пользовательского объекта с помощью `Saver` и `rememberSaveable`?

## References
- [State in Compose](https://developer.android.com/jetpack/compose/state)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]

### Related (Medium)
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-jetpack-compose-basics--android--medium]] - Jetpack Compose
- [[q-compose-modifier-system--android--medium]] - Jetpack Compose
- [[q-compose-semantics--android--medium]] - Jetpack Compose

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose