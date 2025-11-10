---
id: android-263
title: "Stable Classes Compose / Stable Классы Compose"
aliases: ["Stable Classes Compose", "Stable Классы Compose"]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, q-compose-stability-skippability--android--hard]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-rendering, android/ui-compose, difficulty/hard, immutability, jetpack-compose, recomposition, stability]

---

# Вопрос (RU)

> Какие классы будут автоматически выводиться как stable в Jetpack Compose?

# Question (EN)

> Which classes are automatically inferred as stable in Jetpack Compose?

---

## Ответ (RU)

### Краткий вариант

Тип автоматически считается stable в Jetpack Compose, когда компилятор может формально доказать, что:
- он относится к известным стабильным типам (примитивы, `String` и некоторые платформенные типы);
- это `data class` или класс с корректной реализацией `equals()`/`hashCode()`;
- все публичные свойства имеют stable-типы;
- он не содержит произвольного изменяемого состояния, которое компилятор не может отследить.

Такие типы позволяют Compose безопасно пропускать рекомпозиции при неизменных параметрах.

### Подробный вариант

В Jetpack Compose тип может быть выведен как **stable**, если для него компилятор Compose может формально доказать стабильность:
- он относится к известным компилятору стабильным типам (примитивы, `String` и др. платформенные типы);
- это `data class` или класс с корректно реализованным `equals()`/`hashCode()`;
- все его публичные свойства имеют **stable типы**;
- он не содержит свойств с "произвольной" изменяемостью, которую компилятор не может отследить.

При этом:
- Наличие только `val`-свойств — сильный сигнал, но само по себе не гарантирует стабильность, если их типы нестабильны.
- Интерфейс `List`/`Map` выглядит неизменяемым, но не делает тип автоматически stable, если реализация или элементы нестабильны.

### Что Такое Stability?

**Stability** определяет, может ли Compose **пропустить рекомпозицию** при передаче значения в Composable, если, по мнению компилятора, это значение:
- не меняется "спонтанно" без наблюдаемого сигнала;
- даёт предсказуемый `equals()` (для сравнения параметров);
- имеет либо неизменяемое состояние, либо изменяемое состояние с корректной наблюдаемостью (через `mutableStateOf` и т.п. для `@Stable` классов).

Если тип признан stable, Compose может безопасно использовать сравнение значений и локальную информацию, чтобы **пропускать рекомпозицию** вызовов с теми же параметрами.

### Автоматически Stable Типы

Компилятор Compose считает stable (упрощённо):

- **Примитивы и `String`**: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `String` и другие базовые значения, которые не меняются скрытно.
- **Классы с выведенной стабильностью**, например:
```kotlin
// ✅ Может быть выведен как stable:
// - data class
// - только stable-поля
// - корректный equals/hashCode генерируется автоматически

data class User(
    val id: String,
    val name: String,
    val age: Int
)

@Composable
fun UserCard(user: User) {
    // Compose может пропустить рекомпозицию, если ссылка на user не изменилась
    // или если при сравнении equals() объекты равны
    Text("${user.name}, ${user.age}")
}
```

Важно: stable определяется анализом типов и контракта, а не только тем, что это "data class с val".

### Когда Классы НЕ Stable

**1. Изменяемые свойства (var) без наблюдаемости:**
```kotlin
// ❌ Обычно НЕ stable для Compose
// var-свойство может измениться без сигнала системе рекомпозиции

data class User(
    val id: String,
    var name: String
)
```

**2. Изменяемые коллекции или нестабильные контейнеры:**
```kotlin
// ❌ НЕ stable: MutableList может меняться без наблюдаемости

data class Team(
    val members: MutableList<User>
)

// ⚠️ Интерфейс List выглядит лучше, но стабильность зависит от реализации и типов элементов
// Компилятор рассматривает стабильность всего типа, включая элементы.

data class Team(
    val members: List<User>
)
```

В общем случае тип считается нестабильным, если:
- содержит `var` с нестабильным/ненаблюдаемым состоянием;
- содержит поля типов, помеченных как unstable, или типов, для которых компилятор не может вывести стабильность.

### Как Сделать Класс Stable

**Вариант 1: Data классы с stable-полями:**
```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
)
```
(при условии, что все поля — stable типы.)

**Вариант 2: Аннотация @Stable:**
```kotlin
@Stable
class Settings(private val _darkMode: Boolean) {
    val darkMode: Boolean get() = _darkMode

    override fun equals(other: Any?): Boolean =
        other is Settings && other._darkMode == _darkMode

    override fun hashCode(): Int = _darkMode.hashCode()
}
```

Здесь `@Stable` избыточен, так как класс уже фактически неизменяем и с корректным equals/hashCode, но пример показывает:
- `@Stable` обещает компилятору, что:
  - все публичные свойства stable;
  - любые изменяемые свойства (если есть) будут изменяться через наблюдаемые механизмы (например, `mutableStateOf`).
- Аннотация должна соответствовать реальному поведению, иначе возможны некорректные пропуски рекомпозиции.

### Влияние На Производительность

```kotlin
// Stable параметр (предполагая, что User выведен stable)
@Composable
fun UserCard(user: User) {
    Text(user.name)
}
// ✅ Compose может безопасно использовать стабильность user для сокращения числа рекомпозиций

// Unstable параметр
@Composable
fun UserCard(user: UnstableUser) {
    Text(user.name)
}
// ⚠️ Compose не может полагаться на простое сравнение параметров и
// обязан быть более консервативным: меньше возможностей пропустить рекомпозицию.
```

Стабильные типы особенно важны в глубоко вложенных деревьях: они уменьшают количество участков, которые нужно пересчитывать при изменениях.

### Проверка Stability

Можно включить отчёты компилятора Compose в `build.gradle.kts`:
```kotlin
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics",
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${project.buildDir}/compose_reports"
        )
    }
}
```

Отчёты покажут, какие классы и свойства помечены как `stable` или `unstable`, например:
```
stable class User {
  stable val id: String
  stable val name: String
}

unstable class UserProfile {
  unstable var name: String  // ← Проблема!
}
```

---

## Answer (EN)

### Short Version

A type is automatically inferred as stable in Jetpack Compose when the compiler can formally prove that:
- it belongs to known stable types (primitives, `String`, some platform types);
- it is a `data class` or a class with a correct `equals()`/`hashCode()` implementation;
- all its public properties are of stable types;
- it does not expose arbitrary mutable state that the compiler cannot track.

Such types allow Compose to safely skip recompositions when parameters are equal/unchanged.

### Detailed Version

In Jetpack Compose, a type can be inferred as **stable** when the Compose compiler can formally prove that it is stable. Roughly, this happens when:
- it belongs to known stable types (primitive types, `String`, some platform types);
- it is a `data class` or a class with a correct `equals()`/`hashCode()` implementation;
- all of its public properties are of **stable types**;
- it does not expose arbitrary mutable state that the compiler cannot track.

Notes:
- Having only `val` properties is a strong indicator, but does not by itself guarantee stability if their types are unstable.
- Using `List`/`Map` interfaces does not automatically make a class stable if the implementation or element types are unstable.

### What is Stability?

**Stability** determines whether Compose can **safely skip recomposition** for a Composable call based on its parameters. A stable type:
- does not change "spontaneously" without observable notifications;
- has predictable `equals()` behavior for comparing instances;
- has either immutable state or mutable state whose changes are observable to Compose (for `@Stable` types).

If a parameter type is stable, the compiler/runtime can rely more on equality checks and local information to decide when recomposition can be skipped.

### Automatically Stable Types

The Compose compiler treats as stable (simplified):

- **Primitives and `String`**: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `String`, etc.
- **Types with inferred stability**, such as:
```kotlin
// ✅ Can be inferred as stable when:
// - data class
// - all properties are stable types
// - equals/hashCode are correctly generated

data class User(
    val id: String,
    val name: String,
    val age: Int
)

@Composable
fun UserCard(user: User) {
    // Compose may skip recomposition when the user parameter is equal / unchanged
    Text("${user.name}, ${user.age}")
}
```

Important: "stable" is the result of the compiler's stability analysis, not just "data class + val".

### When Classes Are NOT Stable

**1. Mutable properties (var) without proper observability:**
```kotlin
// ❌ Usually NOT stable for Compose
// var can change without notifying the recomposition system

data class User(
    val id: String,
    var name: String
)
```

**2. Mutable collections or unstable containers:**
```kotlin
// ❌ NOT stable: MutableList can change without Compose being aware

data class Team(
    val members: MutableList<User>
)

// ⚠️ Using List is better at the API level, but stability depends
// on the concrete implementation and element types

data class Team(
    val members: List<User>
)
```

In general, a type is considered unstable if it:
- contains `var` properties with non-observable mutations;
- contains fields of types that are themselves unstable or unknown to the analysis.

### Making Classes Stable

**Option 1: Data classes with stable properties:**
```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
)
```
(assuming all fields are stable types.)

**Option 2: `@Stable` annotation:**
```kotlin
@Stable
class Settings(private val _darkMode: Boolean) {
    val darkMode: Boolean get() = _darkMode

    override fun equals(other: Any?): Boolean =
        other is Settings && other._darkMode == _darkMode

    override fun hashCode(): Int = _darkMode.hashCode()
}
```

`@Stable` is redundant for this strictly immutable example, but illustrates that:
- `@Stable` is a promise to the compiler that:
  - all public properties are stable;
  - any mutable properties (if present) change in an observable way (e.g., via `mutableStateOf`).
- Misusing `@Stable` (lying about behavior) can lead to incorrect recomposition skipping.

### Performance Impact

```kotlin
// Stable parameter (assuming User is inferred stable)
@Composable
fun UserCard(user: User) {
    Text(user.name)
}
// ✅ Compose can leverage stability information to reduce recompositions

// Unstable parameter
@Composable
fun UserCard(user: UnstableUser) {
    Text(user.name)
}
// ⚠️ Compose cannot safely treat this parameter as skippable based solely on equality,
// so it must be more conservative about recomposition.
```

Stable parameters are especially valuable in deep Composable trees, as they minimize how far changes propagate.

### Checking Stability

You can enable Compose compiler metrics/reports in `build.gradle.kts`:
```kotlin
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics",
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${project.buildDir}/compose_reports"
        )
    }
}
```

The output will show which classes and properties are marked as `stable` or `unstable`, e.g.:
```
stable class User {
  stable val id: String
  stable val name: String
}

unstable class UserProfile {
  unstable var name: String  // ← Problem!
}
```

---

## Follow-ups

1. What happens to recomposition if a class contains stable properties wrapped inside an unstable container type?
2. How does `@Immutable` differ from the `@Stable` annotation in terms of guarantees and usage?
3. Can you make a class with private `var` properties stable using `@Stable`, and what conditions must hold?
4. How do `kotlinx.collections.immutable` types affect stability and performance compared to standard `List`?
5. How would you detect and fix stability issues using Compose compiler reports in a real project?

## References

- [[c-compose-recomposition]] - Compose recomposition fundamentals
- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)
- [Compose Compiler Metrics](https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md)

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals

### Related
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability
- [[q-stable-annotation-compose--android--hard]] - @Stable annotation details
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

### Advanced
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table internals
- [[q-compose-compiler-plugin--android--hard]] - Analyzing compiler reports
