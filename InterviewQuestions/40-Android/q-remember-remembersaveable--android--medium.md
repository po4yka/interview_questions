---
id: 20251006-010
title: "remember vs rememberSaveable in Compose"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, state, remember, remembersaveable]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/jetpack-compose, android/state, android/remember, android/remembersaveable, difficulty/medium]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/jetpack-compose, android/state, android/remember, android/remembersaveable, difficulty/medium]
---
# Question (EN)
> What is the difference between remember and rememberSaveable in Jetpack Compose?
# Вопрос (RU)
> В чем разница между remember и rememberSaveable в Jetpack Compose?

---

## Answer (EN)

**remember** stores value across recompositions. **rememberSaveable** stores value across configuration changes (rotation, process death).

### remember - Survives Recomposition Only

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

### rememberSaveable - Survives Configuration Changes

```kotlin
@Composable
fun Counter() {
    var count by rememberSaveable { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Survives: Recomposition, rotation, process death
// Saved to Bundle automatically
```

### Comparison Table

| Feature | remember | rememberSaveable |
|---------|----------|------------------|
| **Recomposition** | - Survives | - Survives |
| **Config change** | - Lost | - Survives |
| **Process death** | - Lost | - Survives |
| **Types supported** | Any | Parcelable/Serializable/primitives |
| **Performance** | Faster | Slightly slower (serialization) |

### When to Use Each

**Use remember for:**
- Temporary UI state (expanded/collapsed)
- Animation state
- Focus state
- Scroll state (handled by rememberScrollState)
- Large objects that shouldn't persist

```kotlin
@Composable
fun ExpandableCard() {
    var isExpanded by remember { mutableStateOf(false) }  // OK - UI-only state

    Card(
        modifier = Modifier.clickable { isExpanded = !isExpanded }
    ) {
        if (isExpanded) { ExpandedContent() }
    }
}
```

**Use rememberSaveable for:**
- User input (text fields, selections)
- Filter/search queries
- Selected tab index
- Form data
- Any state that should survive rotation

```kotlin
@Composable
fun SearchScreen() {
    var searchQuery by rememberSaveable { mutableStateOf("") }  // Survives rotation

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
    restore = { map -> User(map["id"]!!, map["name"]!!) }
)

@Composable
fun UserProfile() {
    var user by rememberSaveable(stateSaver = UserSaver) {
        mutableStateOf(User("1", "Alice"))
    }
}
```

**English Summary**: `remember` stores value across recompositions only (lost on rotation). `rememberSaveable` stores across config changes and process death (uses Bundle). Use `remember` for: temporary UI state, animations, focus. Use `rememberSaveable` for: user input, form data, selections. Custom Saver for complex objects.

## Ответ (RU)

**remember** хранит значение между рекомпозициями. **rememberSaveable** хранит значение при изменениях конфигурации (поворот, смерть процесса).

### remember - Переживает только рекомпозицию

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Переживает: Рекомпозицию
// - Теряется при: Изменении конфигурации, смерти процесса
```

### rememberSaveable - Переживает изменения конфигурации

```kotlin
@Composable
fun Counter() {
    var count by rememberSaveable { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// - Переживает: Рекомпозицию, поворот, смерть процесса
// Сохраняется в Bundle автоматически
```

### Когда использовать каждый

**Используйте remember для:**
- Временное UI состояние (развернуто/свернуто)
- Состояние анимации
- Состояние фокуса
- Большие объекты которые не должны сохраняться

**Используйте rememberSaveable для:**
- Пользовательский ввод (текстовые поля, выбор)
- Запросы фильтрации/поиска
- Индекс выбранной вкладки
- Данные формы
- Любое состояние которое должно пережить поворот

**Краткое содержание**: `remember` хранит значение только между рекомпозициями (теряется при повороте). `rememberSaveable` хранит при изменениях конфигурации и смерти процесса (использует Bundle). Используйте `remember` для: временного UI состояния, анимаций. Используйте `rememberSaveable` для: пользовательского ввода, данных формы.

---

## References
- [State in Compose](https://developer.android.com/jetpack/compose/state)

## Related Questions

### Related (Medium)
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-jetpack-compose-basics--android--medium]] - Jetpack Compose
- [[q-compose-modifier-system--android--medium]] - Jetpack Compose
- [[q-compose-semantics--android--medium]] - Jetpack Compose

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
### Related (Medium)
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-jetpack-compose-basics--android--medium]] - Jetpack Compose
- [[q-compose-modifier-system--android--medium]] - Jetpack Compose
- [[q-compose-semantics--android--medium]] - Jetpack Compose

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
### Related (Medium)
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-jetpack-compose-basics--android--medium]] - Jetpack Compose
- [[q-compose-modifier-system--android--medium]] - Jetpack Compose
- [[q-compose-semantics--android--medium]] - Jetpack Compose

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose