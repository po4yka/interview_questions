---\
id: android-041
title: Compose Compiler Plugin / Плагин компилятора Compose
aliases: [Compose Compiler, Compose Compiler Plugin, Компилятор Compose, Плагин компилятора Compose]
topic: android
subtopics: [performance-memory, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, q-android-performance-measurement-tools--android--medium, q-compose-multiplatform--android--hard, q-compose-performance-optimization--android--hard, q-compose-stability-skippability--android--hard]
sources: []
created: 2025-10-11
updated: 2025-11-10
tags: [android/performance-memory, android/ui-compose, compiler, difficulty/hard, performance]

---\
# Вопрос (RU)
> Как работает плагин компилятора Compose и как он оптимизирует перекомпозицию?

# Question (EN)
> How does the Compose Compiler Plugin work and how does it optimize recomposition?

---

## Ответ (RU)

### Трансформация @Composable Функций

Компилятор преобразует `@Composable` функции в машины состояний:
- Вставляет параметр `Composer` для управления slot table
- Генерирует группы и ключи для отслеживания изменений UI
- Анализирует стабильность параметров через data flow analysis
- Помечает функции как restartable/skippable для оптимизации (если сигнатура и стабильность аргументов позволяют)

### Механизм Стабильности

**Стабильные типы** → позволяют компилятору безопасно пропускать выполнение функции при отсутствии изменений входных данных:
- Примитивы (`Int`, `String`, `Boolean`) и другие типы, известные компилятору как неизменяемые
- Типы с `@Immutable` / `@Stable` (при корректной семантике неизменяемости/стабильности)
- Объекты, для которых композиционный анализ может опираться на сравнение по ссылке (referential equality), если они считаются стабильными

**Нестабильные типы** → не позволяют использовать автоматический skip, основанный только на стабильности аргументов; такие функции не считаются skippable по критерию стабильности и чаще будут выполняться при перекомпозиции соответствующей области:
- Изменяемые коллекции (`MutableList`, `MutableMap`, и т.п.)
- Классы без явных маркеров стабильности и/или с семантикой мутабельности
- Типы с `var` полями, нарушающими гарантию стабильности

Важно: "нестабильный" не означает, что функция гарантированно перекомпозируется при любом изменении родителя. Это означает, что компилятор не может безопасно пропустить ее выполнение, опираясь на информацию о стабильности, и поэтому при триггере перекомпозиции соответствующей области она, как правило, будет вызвана.

### Примеры Оптимизации

✅ **Стабильная модель**:
```kotlin
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Перекомпозиция только при изменении user или соответствующих входов в пределах ее области перекомпозиции
}
```

❌ **Нестабильная модель**:
```kotlin
data class User(val id: String, var name: String) // var делает тип нестабильным

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Не может быть эффективно пропущена по стабильности; при перекомпозиции родительского scope, как правило, будет выполняться снова
}
```

✅ **Неизменяемые интерфейсы**:
```kotlin
@Composable
fun ItemList(items: List<Item>) { // List вместо MutableList; важно соблюдать неизменяемый контракт использования
    LazyColumn {
        items(items) { ItemRow(it) }
    }
}
```

(Список будет считаться стабильным только при эффективной неизменяемости: если реализация и контракт гарантируют отсутствие мутаций "за кадром".)

### Диагностика Компилятора

Включите отчеты для анализа решений компилятора. Конкретные флаги зависят от версии плагина Compose и Gradle. Один из распространенных вариантов конфигурации (Kotlin DSL):

```kotlin
// build.gradle.kts (пример, актуальный для новых версий Compose Compiler)
composeCompiler {
    reportsDestination.set(layout.buildDirectory.dir("compose-reports"))
    metricsDestination.set(layout.buildDirectory.dir("compose-metrics"))
}
```

Либо через аргументы компилятора Kotlin (для соответствующих версий):

```kotlin
kotlin {
    compilerOptions {
        freeCompilerArgs.addAll(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${buildDir}/compose-reports",
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${buildDir}/compose-metrics"
        )
    }
}
```

Отчеты показывают:
- Какие функции restartable/skippable
- Причины нестабильности типов
- Количество групп и сложность композиций

### Рекомендации По Оптимизации

1. **Используйте @Immutable/@Stable** для доменных моделей при корректной семантике
2. **По возможности для коллекций и списков передавайте стабильные и эффективно неизменяемые структуры (или идентификаторы элементов)**, если это уменьшает количество изменений с точки зрения компилятора
3. **Выносите вычисления** в `remember` и `derivedStateOf` для предотвращения лишних вычислений при перекомпозиции
4. **Декомпозируйте UI** на мелкие composable функции для локализации областей перекомпозиции
5. **Используйте `key()`** для контроля области и идентичности элементов при перекомпозиции

## Answer (EN)

### @Composable Function Transformation

The compiler transforms `@Composable` functions into state machines:
- Injects a `Composer` parameter for slot table management
- Generates groups and keys for UI change tracking
- Analyzes parameter stability through data flow analysis
- Marks functions as restartable/skippable for optimization (when the signature and parameter stability allow it)

### Stability Mechanism

**Stable types** → enable the compiler to safely skip executing a function when inputs are unchanged:
- Primitives (`Int`, `String`, `Boolean`) and other types known to the compiler as effectively immutable
- Types annotated with `@Immutable` / `@Stable` (assuming semantics are correct)
- Objects where the stability analysis can rely on referential equality when they are classified as stable

**Unstable types** → prevent the compiler from using automatic skipping based solely on stability; such functions are not considered skippable based on stability and are more likely to be re-executed when their recomposition scope is invalidated:
- Mutable collections (`MutableList`, `MutableMap`, etc.)
- Classes without explicit stability markers and/or with mutable semantics
- Types with `var` properties that break stability guarantees

Important: "unstable" does not mean the function will "always recompose" on every parent change. It means the compiler cannot safely skip it based on stability information, so when recomposition is triggered for that scope, it will generally be invoked.

### Optimization Examples

✅ **Stable model**:
```kotlin
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Recomposes only when user or relevant inputs/keys change within its recomposition scope
}
```

❌ **Unstable model**:
```kotlin
data class User(val id: String, var name: String) // var makes the type unstable

@Composable
fun UserRow(user: User) {
    Text(text = user.name) // Cannot be efficiently skipped based on stability; it will generally run whenever its parent scope recomposes
}
```

✅ **Immutable interfaces**:
```kotlin
@Composable
fun ItemList(items: List<Item>) { // List instead of MutableList; relies on an effectively immutable usage contract
    LazyColumn {
        items(items) { ItemRow(it) }
    }
}
```

(A `List` is treated as stable only when the implementation and contract ensure it is not mutated in a way that violates the compiler's assumptions.)

### Compiler Diagnostics

Enable reports to analyze compiler decisions. Exact configuration depends on the Compose Compiler and Android Gradle Plugin versions. A common modern setup (Kotlin DSL) is:

```kotlin
// build.gradle.kts (example for newer Compose Compiler)
composeCompiler {
    reportsDestination.set(layout.buildDirectory.dir("compose-reports"))
    metricsDestination.set(layout.buildDirectory.dir("compose-metrics"))
}
```

Or via Kotlin compiler plugin arguments (for applicable versions):

```kotlin
kotlin {
    compilerOptions {
        freeCompilerArgs.addAll(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${buildDir}/compose-reports",
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${buildDir}/compose-metrics"
        )
    }
}
```

Reports show:
- Which functions are restartable/skippable
- Reasons for type instability
- Group counts and composition complexity

### Optimization Recommendations

1. **Use @Immutable/@Stable** for domain models when semantics are correct
2. **For collections and lists, prefer stable and effectively immutable structures (or item IDs) where it reduces perceived changes for the compiler**
3. **Move expensive calculations** into `remember` and `derivedStateOf` to avoid redundant work during recomposition
4. **Decompose UI** into small composable functions to localize recomposition scopes
5. **Use `key()`** to control identity and recomposition scope for items

---

## Follow-ups

- How to interpret compiler stability reports and fix unstable types?
- What are the trade-offs of @Stable vs @Immutable annotations?
- How does `derivedStateOf` prevent unnecessary recompositions?
- When should you use `key()` to control recomposition scope?
- How to measure recomposition counts in production using tracing?

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model
- https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
