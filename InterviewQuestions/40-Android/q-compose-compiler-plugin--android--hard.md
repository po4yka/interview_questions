---
id: 20251012-122803
title: Compose Compiler Plugin / Плагин компилятора Compose
aliases:
  - Compose Compiler Plugin
  - Плагин компилятора Compose
  - Compose Compiler
  - Компилятор Compose
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
sources: []
created: 2025-10-11
updated: 2025-10-28
tags:
  - android/performance-memory
  - android/ui-compose
  - compose
  - compiler
  - performance
  - difficulty/hard
---
# Вопрос (RU)
> Как работает плагин компилятора Compose и как он оптимизирует перекомпозицию?

# Question (EN)
> How does the Compose Compiler Plugin work and how does it optimize recomposition?

---

## Ответ (RU)

### Что делает плагин

Плагин компилятора Compose преобразует `@Composable` функции в машины состояний:
- Добавляет параметры `Composer`, генерирует группы и ключи для отслеживания изменений
- Анализирует стабильность параметров (Stable/Unstable) для пропуска ненужных перекомпозиций
- Отмечает вызовы как restartable/skippable и генерирует операции чтения/записи slot table
- Использует анализ потока данных для определения оптимизаций

### Стабильность и пропуск перекомпозиций

**Стабильные параметры** → функция может быть пропущена при перекомпозиции:
- Примитивы (Int, String, Boolean)
- Типы с `@Immutable` / `@Stable`
- Referentially equal объекты

**Нестабильные параметры** → всегда выполняется перекомпозиция:
- Изменяемые коллекции (MutableList, MutableMap)
- Классы без явной стабильности
- Типы с изменяемыми полями

### Примеры стабильности

✅ **Стабильная модель** — минимум перекомпозиций:
```kotlin
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserRow(user: User) {
    // Перекомпозиция только при изменении user
    Text(text = user.name)
}
```

❌ **Нестабильная модель** — избыточные перекомпозиции:
```kotlin
// Без @Immutable компилятор не может гарантировать стабильность
data class User(val id: String, var name: String)

@Composable
fun UserRow(user: User) {
    // Перекомпозиция при каждом изменении родителя
    Text(text = user.name)
}
```

✅ **Подъем состояния и стабильные параметры**:
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    // ✅ Только Text перекомпозируется
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

❌ **Передача изменяемых коллекций**:
```kotlin
// ❌ Каждое изменение MutableList вызывает перекомпозицию
@Composable
fun ItemList(items: MutableList<Item>) {
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}
```

✅ **Использование неизменяемых интерфейсов**:
```kotlin
// ✅ Передаем List вместо MutableList
@Composable
fun ItemList(items: List<Item>) {
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}
```

### Диагностика компилятора

Включите метрики и отчеты для анализа решений компилятора:

```kotlin
// gradle.properties
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
compose.compiler.metricsDestination=build/compose-metrics
```

Отчеты показывают:
- Какие функции restartable/skippable
- Какие типы нестабильны и почему
- Количество групп и сложность композиций

### Практики оптимизации

1. **Используйте @Immutable/@Stable** для доменных моделей
2. **Избегайте больших объектов в параметрах** — передавайте ID или ключи
3. **Выносите тяжелые вычисления** — используйте `remember` и `derivedStateOf`
4. **Разбивайте композиции** — декомпозируйте сложные UI на подкомпоненты
5. **Контролируйте каскады** — используйте `key()` и локальное состояние

## Answer (EN)

### What the Plugin Does

The Compose Compiler Plugin transforms `@Composable` functions into state machines:
- Inserts `Composer` parameters, generates groups and keys for change tracking
- Infers parameter stability (Stable/Unstable) to decide if recomposition can be skipped
- Marks calls as restartable/skippable and generates slot table read/write operations
- Uses data flow analysis to determine optimization decisions

### Stability and Skipping

**Stable parameters** → function can be skipped during recomposition:
- Primitives (Int, String, Boolean)
- Types annotated with `@Immutable` / `@Stable`
- Referentially equal objects

**Unstable parameters** → recomposition always executes:
- Mutable collections (MutableList, MutableMap)
- Classes without explicit stability markers
- Types with mutable fields

### Stability Examples

✅ **Stable model** — minimal recompositions:
```kotlin
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserRow(user: User) {
    // Recomposes only when user changes
    Text(text = user.name)
}
```

❌ **Unstable model** — excessive recompositions:
```kotlin
// Without @Immutable compiler cannot guarantee stability
data class User(val id: String, var name: String)

@Composable
fun UserRow(user: User) {
    // Recomposes on every parent change
    Text(text = user.name)
}
```

✅ **State hoisting with stable parameters**:
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    // ✅ Only Text recomposes
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

❌ **Passing mutable collections**:
```kotlin
// ❌ Every MutableList change triggers recomposition
@Composable
fun ItemList(items: MutableList<Item>) {
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}
```

✅ **Using immutable interfaces**:
```kotlin
// ✅ Pass List instead of MutableList
@Composable
fun ItemList(items: List<Item>) {
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}
```

### Compiler Diagnostics

Enable metrics and reports to analyze compiler decisions:

```kotlin
// gradle.properties
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
compose.compiler.metricsDestination=build/compose-metrics
```

Reports show:
- Which functions are restartable/skippable
- Which types are unstable and why
- Group counts and composition complexity

### Optimization Practices

1. **Use @Immutable/@Stable** for domain models when semantics apply
2. **Avoid large objects in parameters** — pass IDs or keys instead
3. **Move heavy work off composition** — use `remember` and `derivedStateOf`
4. **Break down compositions** — decompose complex UI into subcomposables
5. **Control cascades** — use `key()` and local state management

---

## Follow-ups

- How to interpret compiler stability reports and fix unstable types?
- What are trade-offs of @Stable/@Immutable annotations vs real immutability?
- How to measure recomposition counts in production (Macrobenchmark, tracing)?
- When should you use `key()` to control recomposition scope?
- How does `derivedStateOf` prevent unnecessary recompositions?

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model
- https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-compose-state--android--medium]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
- [[q-compose-performance-benchmarking--android--hard]]
