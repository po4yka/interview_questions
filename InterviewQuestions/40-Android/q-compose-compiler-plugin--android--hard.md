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
  - c-compose-state
  - c-compose-recomposition
  - q-compose-state--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-compose-performance-benchmarking--android--hard
sources: []
created: 2025-10-11
updated: 2025-10-29
tags:
  - android/performance-memory
  - android/ui-compose
  - compose
  - compiler
  - performance
  - difficulty/hard
date created: Thursday, October 30th 2025, 11:17:58 am
date modified: Thursday, October 30th 2025, 12:43:40 pm
---

# Вопрос (RU)
> Как работает плагин компилятора Compose и как он оптимизирует перекомпозицию?

# Question (EN)
> How does the Compose Compiler Plugin work and how does it optimize recomposition?

---

## Ответ (RU)

### Трансформация @Composable функций

Компилятор преобразует `@Composable` функции в машины состояний:
- Вставляет параметр `Composer` для управления slot table
- Генерирует группы и ключи для отслеживания изменений UI
- Анализирует стабильность параметров через data flow analysis
- Помечает функции как restartable/skippable для оптимизации

### Механизм стабильности

**Стабильные типы** → функция пропускается при одинаковых параметрах:
- Примитивы (Int, String, Boolean)
- Типы с `@Immutable` / `@Stable`
- Referentially equal объекты

**Нестабильные типы** → всегда перекомпозируются:
- Изменяемые коллекции (MutableList, MutableMap)
- Классы без явных маркеров стабильности
- Типы с var полями

### Примеры оптимизации

✅ **Стабильная модель**:
```kotlin
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Перекомпозиция только при изменении user
}
```

❌ **Нестабильная модель**:
```kotlin
data class User(val id: String, var name: String) // var делает тип нестабильным

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Перекомпозируется при каждом изменении родителя
}
```

✅ **Неизменяемые интерфейсы**:
```kotlin
@Composable
fun ItemList(items: List<Item>) { // List вместо MutableList
    LazyColumn {
        items(items) { ItemRow(it) }
    }
}
```

### Диагностика компилятора

Включите отчеты для анализа решений компилятора:

```kotlin
// gradle.properties
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
```

Отчеты показывают:
- Какие функции restartable/skippable
- Причины нестабильности типов
- Количество групп и сложность композиций

### Рекомендации по оптимизации

1. **Используйте @Immutable/@Stable** для доменных моделей
2. **Передавайте ID вместо объектов** для снижения нагрузки
3. **Выносите вычисления** в `remember` и `derivedStateOf`
4. **Декомпозируйте UI** на мелкие composable функции
5. **Используйте key()** для контроля области перекомпозиции

## Answer (EN)

### @Composable Function Transformation

The compiler transforms `@Composable` functions into state machines:
- Injects `Composer` parameter for slot table management
- Generates groups and keys for UI change tracking
- Analyzes parameter stability through data flow analysis
- Marks functions as restartable/skippable for optimization

### Stability Mechanism

**Stable types** → function skips when parameters are equal:
- Primitives (Int, String, Boolean)
- Types annotated with `@Immutable` / `@Stable`
- Referentially equal objects

**Unstable types** → always recompose:
- Mutable collections (MutableList, MutableMap)
- Classes without explicit stability markers
- Types with var fields

### Optimization Examples

✅ **Stable model**:
```kotlin
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Recomposes only when user changes
}
```

❌ **Unstable model**:
```kotlin
data class User(val id: String, var name: String) // var makes type unstable

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Recomposes on every parent change
}
```

✅ **Immutable interfaces**:
```kotlin
@Composable
fun ItemList(items: List<Item>) { // List instead of MutableList
    LazyColumn {
        items(items) { ItemRow(it) }
    }
}
```

### Compiler Diagnostics

Enable reports to analyze compiler decisions:

```kotlin
// gradle.properties
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
```

Reports show:
- Which functions are restartable/skippable
- Reasons for type instability
- Group counts and composition complexity

### Optimization Recommendations

1. **Use @Immutable/@Stable** for domain models when semantics apply
2. **Pass IDs instead of objects** to reduce payload
3. **Move calculations** to `remember` and `derivedStateOf`
4. **Decompose UI** into small composable functions
5. **Use key()** to control recomposition scope

---

## Follow-ups

- How to interpret compiler stability reports and fix unstable types?
- What are the trade-offs of @Stable vs @Immutable annotations?
- How does derivedStateOf prevent unnecessary recompositions?
- When should you use key() to control recomposition scope?
- How to measure recomposition counts in production using tracing?

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model
- https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md

## Related Questions

### Prerequisites (Easier)
- [[q-compose-state--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-compose-performance-benchmarking--android--hard]]
- [[q-android-runtime-art--android--medium]]
