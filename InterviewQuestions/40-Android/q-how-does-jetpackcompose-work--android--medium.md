---\
id: android-119
title: How Does Jetpack Compose Work / Как работает Jetpack Compose
aliases: [How Does Jetpack Compose Work, Как работает Jetpack Compose]
topic: android
subtopics: [architecture-mvvm, ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, c-mvvm, q-cache-implementation-strategies--android--medium, q-how-does-activity-lifecycle-work--android--medium, q-how-does-jetpack-compose-work--android--medium, q-how-does-the-main-thread-work--android--medium, q-how-jetpack-compose-works--android--medium, q-jetpack-compose-basics--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/architecture-mvvm, android/ui-compose, android/ui-state, difficulty/medium]
anki_cards:
  - slug: android-119-0-en
    front: "What are the key principles of Jetpack Compose?"
    back: |
      **Declarative** - describe what UI should look like, not how to build it

      **Reactive** - UI updates automatically when state changes

      **Composition** - builds UI tree via @Composable functions using slot table

      **Recomposition** - only invalidated parts re-execute:
      1. State changes (`count++`)
      2. Affected scopes marked invalid
      3. Only those scopes recompose

      **State hoisting** - lift state up for reusability:
      ```kotlin
      fun Counter(count: Int, onIncrement: () -> Unit)
      ```
    tags:
      - android_compose
      - difficulty::medium
  - slug: android-119-0-ru
    front: "Каковы ключевые принципы Jetpack Compose?"
    back: |
      **Декларативный** - описывайте как UI должен выглядеть, а не как его строить

      **Реактивный** - UI обновляется автоматически при изменении состояния

      **Composition** - строит дерево UI через @Composable функции используя slot table

      **Рекомпозиция** - перевыполняются только невалидные части:
      1. Состояние меняется (`count++`)
      2. Затронутые scope помечаются невалидными
      3. Только эти scope рекомпозируются

      **State hoisting** - поднимайте состояние для переиспользуемости:
      ```kotlin
      fun Counter(count: Int, onIncrement: () -> Unit)
      ```
    tags:
      - android_compose
      - difficulty::medium

---\
# Вопрос (RU)

> Как работает Jetpack Compose?

# Question (EN)

> How does Jetpack Compose work?

## Ответ (RU)

**Jetpack Compose** — декларативный UI-фреймворк от Google для Android. Вместо XML и императивного управления `View` используется подход, где UI описывается Kotlin-функциями.

### Основные Принципы

**Declarative UI**: описываете, что должно быть, а не как по шагам построить UI
**Reactive**: UI автоматически обновляется при изменении наблюдаемого состояния
**`Component`-based**: UI собирается из переиспользуемых composable-функций
**Kotlin-first**: тесная интеграция с Kotlin (включая корутины и `Flow` через специализированные API)

### Как Работает Composition

Compose создаёт дерево вызовов composable-функций — **Composition**. Внутри используется структура данных **slot table**, которая отслеживает группы (composable-блоки), их позиции, состояния (включая `remember`) и ключи, необходимые для корректной перекомпозиции. Во время композиции Compose отслеживает чтения состояния и знает, какие группы зависят от каких значений.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ Локальное состояние, привязанное к Composition

    Column {
        Text("Count: $count") // ✅ Перекомпонуется при изменении count
        Button(onClick = { count++ }) {
            Text("Increment") // ✅ Участвует в перекомпозиции; стабильные части могут быть пропущены при повторном выполнении
        }
    }
}
```

### Recomposition - Сердце Compose

При изменении данных Compose интеллектуально повторно выполняет только затронутые части UI:

1. Меняется состояние (`count++`).
2. Compose помечает связанные с этим состоянием группы (composable, которые читали это состояние) как невалидные.
3. При следующем проходе выполняются только невалидные участки Composition; стабильные/неизменившиеся участки могут быть пропущены или переиспользованы.
4. Результат сопоставляется с существующей структурой, и обновляются только изменённые части UI.

### State Hoisting (Поднятие Состояния)

Поднимайте состояние выше по иерархии для переиспользуемости и тестируемости:

```kotlin
// ✅ Stateless composable (переиспользуемый, легко тестировать)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("+") }
    }
}

// ✅ Stateful-родитель управляет состоянием
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Counter(count = count, onIncrement = { count++ })
}
```

### Effect Handlers

Для побочных эффектов (side effects):

```kotlin
@Composable
fun EffectsExample(userId: String, locationManager: LocationManager) {
    // ✅ LaunchedEffect: для запуска suspend-функций, перезапускается при изменении ключа
    LaunchedEffect(userId) {
        val user = loadUser(userId) // loadUser — условная suspend-функция загрузки данных
        // используйте user для обновления состояния
    }

    // ✅ DisposableEffect: для инициализации и освобождения ресурсов
    DisposableEffect(Unit) {
        val listener = LocationListener() // иллюстративный пример; конкретное API зависит от реализации
        locationManager.addListener(listener)
        onDispose { locationManager.removeListener(listener) }
    }
}
```

### Modifiers - Стилизация И Поведение

Модификаторы настраивают внешний вид и поведение. **Порядок важен**:

```kotlin
// ✅ padding перед background — фон включает внутренние отступы
Box(Modifier.padding(16.dp).background(Color.Blue))

// ❌ background перед padding — отступы оказываются за пределами фона
Box(Modifier.background(Color.Blue).padding(16.dp))
```

### Производительность

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // ✅ LazyColumn для больших списков: элементы создаются лениво и удаляются при уходе с экрана (по концепции похоже на эффективную работу RecyclerView, но без прямого переиспользования view)
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}

@Composable
fun ItemRow(item: Item) {
    // ✅ derivedStateOf: вычисляет значение только при изменении зависимостей
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }
    // ✅ remember: кэширует дорогостоящие объекты по ключу на время жизни соответствующей части Composition
    val obj = remember(item.id) { createExpensiveObject(item) }

    // используйте isExpensive и obj в UI
}
```

### Как Работает Внутри

**Три фазы**:
1. **Composition**: построение дерева UI из @Composable-функций и запись структуры в slot table.
2. **Layout**: измерение и позиционирование элементов.
3. **Drawing**: отрисовка элементов на экран.

**Slot Table**: компактная индексированная структура, которую Compose использует для эффективного отслеживания групп composable, их состояний, значений `remember` и ключей. Это позволяет находить и обновлять только нужные части дерева при перекомпозиции без полного пересоздания UI.

### Резюме

Compose работает через:
- Описание UI с помощью @Composable-функций
- Построение дерева Composition
- Автоматическое отслеживание и использование состояния
- Умную перекомпозицию только затронутых частей
- Эффективные фазы layout и отрисовки

"Магия" — в механизме перекомпозиции: повторно выполняются только те функции и группы, которые зависят от изменённого состояния, при возможности переиспользуя остальные.

## Answer (EN)

**Jetpack Compose** is Google's declarative UI toolkit for Android. Instead of XML and imperative `View` manipulation, it uses Kotlin functions to describe UI.

### Core Principles

**Declarative UI**: describe what the UI should be, not step-by-step how to mutate it
**Reactive**: UI automatically updates when observable state changes
**`Component`-based**: build UIs from reusable composable functions
**Kotlin-first**: designed for Kotlin, with coroutine/`Flow`-aware APIs and seamless Kotlin integration

### How Composition Works

Compose builds a tree of composable function calls called the **Composition**. Internally, it uses a **slot table** data structure that tracks groups (composable regions), their positions, state (including `remember`), and keys required for correct recomposition. During composition, Compose tracks state reads to know which groups depend on which state values.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ Local state tied to this Composition

    Column {
        Text("Count: $count") // ✅ Re-executes / updates when count changes
        Button(onClick = { count++ }) {
            Text("Increment") // ✅ Participates in recomposition; stable parts may be skipped when re-running
        }
    }
}
```

### Recomposition - The Heart of Compose

When data changes, Compose intelligently re-executes only affected parts of the UI:

1. State changes (`count++`).
2. Compose marks the corresponding groups (composables that read that state) as invalid.
3. On the next pass, only invalid regions of the Composition are re-executed; stable/unchanged regions may be skipped or reused.
4. The result is reconciled with the existing structure, and only the changed parts of the UI get updated.

### State Hoisting

Move state up the tree to make components reusable and testable:

```kotlin
// ✅ Stateless composable (reusable, easy to test)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("+") }
    }
}

// ✅ Stateful parent owns and manages state
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Counter(count = count, onIncrement = { count++ })
}
```

### Effect Handlers

For side effects:

```kotlin
@Composable
fun EffectsExample(userId: String, locationManager: LocationManager) {
    // ✅ LaunchedEffect: run suspend functions; restarts when key changes
    LaunchedEffect(userId) {
        val user = loadUser(userId) // loadUser is a placeholder suspend function
        // use user to update some state
    }

    // ✅ DisposableEffect: acquire and clean up resources
    DisposableEffect(Unit) {
        val listener = LocationListener() // illustrative; concrete API depends on your implementation
        locationManager.addListener(listener)
        onDispose { locationManager.removeListener(listener) }
    }
}
```

### Modifiers - Styling and Behavior

Modifiers customize appearance and behavior. **Order matters**:

```kotlin
// ✅ Padding before background - background covers padded area
Box(Modifier.padding(16.dp).background(Color.Blue))

// ❌ Background before padding - padding is applied outside the background
Box(Modifier.background(Color.Blue).padding(16.dp))
```

### Performance Optimization

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // ✅ Use LazyColumn for large lists: items are composed lazily and disposed when off-screen (conceptually similar to efficient lists like RecyclerView, but without direct view recycling)
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}

@Composable
fun ItemRow(item: Item) {
    // ✅ derivedStateOf: recompute only when dependencies change
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }
    // ✅ remember: cache expensive objects by key for the lifetime of the corresponding composition scope
    val obj = remember(item.id) { createExpensiveObject(item) }

    // use isExpensive and obj in the UI
}
```

### How It Works Under the Hood

**Three phases**:
1. **Composition**: execute @Composable functions to build the UI tree and record it into the slot table.
2. **Layout**: measure and position elements.
3. **Drawing**: draw elements to the screen.

**Slot Table**: a compact indexed data structure that Compose uses to efficiently track composable groups, their state objects, `remember` values, and keys. This enables updating only the necessary parts of the tree during recomposition without rebuilding the entire UI.

### Summary

Compose works by:
- Declaring UI with @Composable functions
- Building a composition tree
- Automatically tracking and observing state usage
- Performing smart recomposition of only affected parts
- Running efficient layout and drawing phases

The "magic" is in its recomposition model: only functions and groups that depend on changed state are re-executed, while others can be efficiently reused or skipped.

## Дополнительные Вопросы (RU)

- Как Compose обрабатывает изменения конфигурации по сравнению с традиционной `View`-системой?
- Каковы последствия глубокой вложенности composable-функций для производительности?
- Как работает `remember` при смерти процесса и восстановлении состояния?
- Когда следует использовать `derivedStateOf` вместо обычного состояния?
- Как интероп между Compose и `View` влияет на производительность гибридных приложений?

## Follow-ups

- How does Compose handle configuration changes compared to traditional Views?
- What are the performance implications of deep nesting in Compose?
- How does remember work across process death and restoration?
- When should you use derivedStateOf vs regular state?
- How does Compose interop affect performance in hybrid apps?

## Ссылки (RU)

- Официальная документация по Jetpack Compose
- Руководство "Thinking in Compose"
- Рекомендации по управлению состоянием в Compose

## References

- Official Jetpack Compose documentation
- Thinking in Compose guide
- State management in Compose best practices

## Связанные Вопросы И Материалы (RU)

### Предварительные Знания / Концепции

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-mvvm]]

### Предварительные Требования

- Базовые знания Kotlin (лямбды, делегаты)
- Понимание основ `View`-системы Android

### Связанные Вопросы

- [[q-cache-implementation-strategies--android--medium]]
- [[q-how-does-the-main-thread-work--android--medium]]
- [[q-how-does-activity-lifecycle-work--android--medium]]

### Продвинутое

- Продвинутая оптимизация производительности в Compose
- Реализация кастомных layout-ов в Compose
- Внутреннее устройство Compose Compiler и генерация кода

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-mvvm]]

### Prerequisites

- Basic Kotlin knowledge with lambdas and delegates
- Understanding of Android `View` system basics

### Related

- [[q-cache-implementation-strategies--android--medium]]
- [[q-how-does-the-main-thread-work--android--medium]]
- [[q-how-does-activity-lifecycle-work--android--medium]]

### Advanced

- Advanced Compose performance optimization techniques
- Custom layout implementation in Compose
- Compose compiler internals and code generation
