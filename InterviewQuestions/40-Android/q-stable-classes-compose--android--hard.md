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

date created: Saturday, November 1st 2025, 1:24:29 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)

> Какие классы будут автоматически выводиться как stable в Jetpack Compose?

# Question (EN)

> Which classes are automatically inferred as stable in Jetpack Compose?

---

## Ответ (RU)

### Краткий Вариант

Тип автоматически считается stable в Jetpack Compose, когда компилятор может формально доказать, что:
- он относится к известным стабильным типам (примитивы Kotlin, `String` и часть стандартных value-типов/платформенных типов, которые не меняют состояние скрытно);
- его структура и контракт позволяют корректно определять, изменилось ли его «наблюдаемое» состояние (например, неизменяемый `data class` с валидной семантикой равенства);
- все публичные свойства имеют stable-типы или типы, для которых может быть выведена стабильность;
- он не содержит произвольного изменяемого состояния, которое компилятор не может отследить (например, `var` или изменяемые коллекции без наблюдаемости).

Такие типы позволяют Compose безопасно сокращать количество рекомпозиций при неизменных параметрах.

### Подробный Вариант

В Jetpack Compose тип может быть выведен как **stable**, если для него компилятор Compose может формально доказать стабильность. Упрощённо это означает, что:
- он относится к известным компилятору стабильным типам (примитивные типы Kotlin, `String`, `Boolean`, беззнаковые типы `U*` и т.п. — значения, которые не меняются скрытно);
- его публичный API не позволяет «тихо» менять значимое состояние без участия Compose (например, через небезопасные `var` или мутируемые коллекции);
- все его публичные свойства имеют **stable типы** либо типы, чья стабильность выведена компилятором;
- если определены `equals()`/`hashCode()`, они согласованы с тем, какие изменения состояния считаются значимыми.

Важные уточнения:
- Наличие только `val`-свойств — сильный сигнал, но само по себе НЕ гарантирует стабильность, если типы этих свойств нестабильны.
- `data class` сам по себе не гарантирует стабильность. Он будет выведен как stable только если все его публичные свойства stable и он не содержит скрытого нестабильного состояния.
- Интерфейсы `List`/`Map` в сигнатуре выглядят лучше, чем мутируемые типы, но стабильность всё равно зависит от конкретной реализации коллекции и стабильности элементов. Сам факт использования `List` не делает класс автоматически stable.

### Что Такое Stability?

**Stability** определяет, может ли Compose **пропустить рекомпозицию** при передаче значения в Composable, исходя из гарантий типа. Для stable-типа верно, что его значимое состояние:
- не меняется "спонтанно" без механизма наблюдаемости (например, без `mutableStateOf` и т.п.);
- имеет предсказуемую семантику равенства (если равенство участвует в контракте стабильности типа);
- либо неизменно, либо его изменяемое состояние обновляется через наблюдаемые Compose-механизмы (актуально для `@Stable` классов).

Если тип признан stable, Compose-компилятор может безопаснее оптимизировать пропуск рекомпозиций. При этом важно понимать: для ссылочных (class) типов Compose по умолчанию опирается прежде всего на стабильность контракта и анализ кода; использование `equals()` для решения о пропуске рекомпозиции — это не универсальное правило для всех стабильных типов, а часть более общего контракта стабильности.

### Автоматически Stable Типы

Компилятор Compose (упрощённо) считает stable:

- **Базовые value-типы**: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `String`, беззнаковые типы `UByte`, `UShort`, `UInt`, `ULong` и другие стандартные неизменяемые value-типы, которые не изменяют состояние скрытно.
- **Типы с выведенной стабильностью**, например:
```kotlin
// ✅ Может быть выведен как stable, если:
// - data class
// - все публичные свойства имеют stable-типы
// - нет скрытого нестабильного/мутируемого состояния

data class User(
    val id: String,
    val name: String,
    val age: Int
)

@Composable
fun UserCard(user: User) {
    // Compose может безопасно использовать стабильность user для оптимизации рекомпозиций,
    // если контракт stability для User соблюдён
    Text("${user.name}, ${user.age}")
}
```

Важно: stable — это результат анализа компилятора и соблюдаемого контракта (не только «data class с val-полями»).

### Когда Классы НЕ Stable

**1. Изменяемые свойства (var) без наблюдаемости:**
```kotlin
// ❌ Как правило, НЕ stable для Compose
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

// ⚠️ Интерфейс List выглядит лучше, но стабильность зависит от реализации и от того,
// stable ли элементы. Компилятор анализирует весь тип целиком.

data class Team(
    val members: List<User>
)
```

В общем случае тип считается нестабильным, если:
- содержит `var` с нестабильным/ненаблюдаемым состоянием;
- содержит поля типов, помеченных как unstable, либо типов, для которых компилятор не может вывести стабильность.

### Как Сделать Класс Stable

**Вариант 1: Data классы с stable-полями:**
```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
)
```
(при условии, что все свойства — stable-типы и нет скрытого нестабильного состояния.)

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

Здесь `@Stable` избыточен, так как класс уже фактически неизменяем и с корректным `equals`/`hashCode`, но пример показывает, что:
- `@Stable` — это обещание компилятору, что:
  - все публичные свойства stable;
  - любые изменяемые свойства (если есть) меняются только через наблюдаемые Compose-механизмы.
- Аннотация не «чинит» неправильную реализацию. Нарушение этого контракта может привести к некорректным пропускам рекомпозиции.

### Влияние На Производительность

```kotlin
// Stable-параметр (предполагая, что User выведен stable)
@Composable
fun UserCard(user: User) {
    Text(user.name)
}
// ✅ Компилятор и рантайм Compose могут воспользоваться стабильностью user
// для уменьшения числа рекомпозиций

// Unstable-параметр
@Composable
fun UserCard(user: UnstableUser) {
    Text(user.name)
}
// ⚠️ Compose не может безопасно считать такие параметры пропускаемыми только по равенству,
// поэтому будет действовать консервативно и реже пропускать рекомпозицию.
```

Стабильные типы особенно важны в глубоко вложенных деревьях, так как уменьшают объём кода, который требуется пересчитывать при изменениях.

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

Эти флаги включают генерацию метрик и отчётов (а не изменяют поведение компилятора). В отчётах видно, какие классы и свойства помечены как `stable` или `unstable`, например:
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
- it belongs to known stable types (Kotlin primitives, `String`, and some standard/pure value or platform types that do not mutate state invisibly);
- its structure and contract make it possible to decide when its observable state has changed (e.g., an immutable `data class` with valid equality semantics);
- all of its public properties are of stable types or types whose stability can be inferred;
- it does not expose arbitrary mutable state that the compiler cannot track (e.g., raw `var` fields or mutable collections without observability).

Such types allow Compose to safely reduce recompositions when parameters are known not to have meaningfully changed.

### Detailed Version

In Jetpack Compose, a type can be inferred as **stable** when the Compose compiler can formally prove it is stable. Roughly, that means:
- it is one of the compiler's known stable types (Kotlin primitive types, `String`, `Boolean`, unsigned value types, etc. — values that cannot change behind the scenes);
- its public API does not allow silently mutating significant state without going through observable channels;
- all of its public properties are of **stable types** or types whose stability has been inferred;
- if `equals()`/`hashCode()` are provided, they are consistent with the state that matters for its contract.

Notes:
- Having only `val` properties is a strong signal but does NOT by itself guarantee stability if their types are unstable.
- A `data class` is not automatically stable. It is inferred stable only if all its public properties are stable and there is no hidden unstable state.
- Using `List`/`Map` interfaces in the API is preferable to mutable types, but stability still depends on the concrete implementation and the stability of element types. Using `List` alone does not automatically make a class stable.

### What is Stability?

**Stability** determines whether Compose can **safely skip recomposition** for a Composable call based on its parameters and the guarantees of their types. For a stable type, its relevant state:
- does not change "spontaneously" without observable notifications (e.g., via Compose state APIs);
- has predictable equality semantics (when equality is part of the stability contract for that type);
- is either immutable, or its mutable state is updated through mechanisms observable to Compose (relevant for `@Stable` classes).

When a parameter type is stable, the compiler/runtime can apply more aggressive optimizations to skip recomposition. Note: for general reference types, Compose primarily relies on the stability contract and compiler analysis; it is not a blanket rule that `equals()` is always directly used for deciding skippability for all stable types.

### Automatically Stable Types

The Compose compiler (simplified) treats as stable:

- **Basic value types**: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `String`, unsigned `U*` types, and other standard immutable value-like types without hidden mutable state.
- **Types with inferred stability**, such as:
```kotlin
// ✅ Can be inferred as stable if:
// - data class
// - all public properties are stable types
// - there is no hidden unstable/mutable state

data class User(
    val id: String,
    val name: String,
    val age: Int
)

@Composable
fun UserCard(user: User) {
    // Compose can safely leverage User's stability to optimize recompositions
    Text("${user.name}, ${user.age}")
}
```

Important: "stable" is the result of the compiler's stability analysis and honored contracts, not merely "data class + val".

### When Classes Are NOT Stable

**1. Mutable properties (`var`) without proper observability:**
```kotlin
// ❌ Typically NOT stable for Compose
// `var` can change without notifying the recomposition system

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

// ⚠️ Using List in the API is better, but stability depends on the
// concrete implementation and element types. The compiler evaluates the full type.

data class Team(
    val members: List<User>
)
```

In general, a type is considered unstable if it:
- contains `var` properties with non-observable mutations;
- contains fields of types that are unstable or whose stability cannot be inferred.

### Making Classes Stable

**Option 1: Data classes with stable properties:**
```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
)
```
(assuming all properties are stable types and there is no hidden unstable state.)

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

`@Stable` is redundant here because the class is already strictly immutable with correct equality, but it demonstrates that:
- `@Stable` is a promise to the compiler that:
  - all public properties are stable;
  - any mutable properties (if present) change only via Compose-observable state mechanisms.
- The annotation does not fix incorrect implementations. Violating its contract can cause incorrect recomposition skipping.

### Performance Impact

```kotlin
// Stable parameter (assuming User is inferred stable)
@Composable
fun UserCard(user: User) {
    Text(user.name)
}
// ✅ The Compose compiler/runtime can leverage the stability of `user`
// to reduce unnecessary recompositions

// Unstable parameter
@Composable
fun UserCard(user: UnstableUser) {
    Text(user.name)
}
// ⚠️ Compose cannot safely treat such parameters as skippable based solely on equality,
// so it behaves more conservatively and skips recomposition less often.
```

Stable parameters are especially valuable in deep Composable trees, as they limit how far changes need to propagate.

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

These flags enable generation of metrics and reports (they do not, by themselves, change behavior). The output will show which classes and properties are marked as `stable` or `unstable`, e.g.:
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
