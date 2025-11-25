---
id: android-429
title: "Stable Annotation Compose / Stable Compose"
aliases: ["Stable Annotation Compose", "Stable Compose"]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, q-compose-stability-skippability--android--hard]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-rendering, android/ui-compose, difficulty/hard, jetpack-compose, recomposition, stable-annotation]

date created: Saturday, November 1st 2025, 1:24:29 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)

> Что известно о `@Stable` в Jetpack Compose?

# Question (EN)

> What is known about `@Stable` in Jetpack Compose?

---

## Ответ (RU)

**`@Stable`** — это аннотация в Compose, которая сообщает компилятору, что тип соблюдает контракт стабильности. Стабильный объект не меняется "за спиной" Compose так, чтобы это влияло на данные, которые читают composable-функции, поэтому компилятор/рантайм могут безопасно оптимизировать и пропускать лишние рекомпозиции при отсутствии значимых изменений.

Ключевая идея: `@Stable` — это обещание разработчика компилятору. Если вы нарушаете контракт, поведение не определено: вы можете получить устаревший UI или пропущенные рекомпозиции.

### Контракт Стабильности

Тип считается стабильным, если выполняются условия:

1. Его публичные свойства, влияющие на UI, либо:
   - неизменяемые примитивы/строки/другие стабильные или immutable-типы, либо
   - отдаются через observable-state (например, `MutableState<T>`), чтобы Compose был уведомлен об изменениях.
2. Он не изменяется способами, невидимыми для Compose:
   - нет "спонтанных" мутаций значений, которые читаются composable-функциями в обход observable-state.
3. Если тип изменяемый, все изменения, влияющие на то, что видят composable-функции, должны быть наблюдаемыми для Compose.

```kotlin
// ✅ Stable-подобный holder: неизменяемые поля примитивных / String типов
@Stable
data class User(val id: String, val name: String)

// ✅ Stable-класс с observable-состоянием: мутации видны Compose
@Stable
class Counter {
    var count by mutableStateOf(0)
        private set

    fun increment() { count++ }
}

// ❌ Не стабильный для Compose: изменяемое поле без наблюдаемости
class UnstableCounter {
    var count: Int = 0  // Compose не уведомляется автоматически
}
```

Важный нюанс: `@Stable` НЕ означает, что решения о рекомпозиции принимаются только по `equals()`. Аннотация говорит компилятору, что он может:
- считать тип стабильным,
- отслеживать, какие поля читаются,
- и пропускать рекомпозицию, когда известно, что прочитанные стабильные поля не менялись между вызовами.

### Когда Использовать @Stable

Используйте `@Stable` в основном тогда, когда компилятор не может вывести стабильность автоматически, но вы можете строго гарантировать контракт:

- Интерфейсы или абстрактные типы, реализации которых стабильны.
- Обёртки над сторонними или платформенными типами, где вы контролируете видимость и мутации.

```kotlin
@Stable
interface Repository {
    val data: String
}

@Composable
fun DataDisplay(repository: Repository) {
    Text(repository.data)
}
```

```kotlin
@Stable
class StableThirdPartyData(private val data: ThirdPartyData) {
    val value: String get() = data.value

    override fun equals(other: Any?) =
        other is StableThirdPartyData && other.value == value
    override fun hashCode(): Int = value.hashCode()
}
```

Не помечайте произвольные классы `ViewModel` и вообще сложные, активно изменяемые объекты как `@Stable`, если вы не можете строго выполнить контракт. Вместо этого экспонируйте из них стабильное/immutable/observable-состояние.

### @Stable Vs @Immutable

- `@Immutable`:
  - Более строгий контракт.
  - Все публичные свойства должны быть неизменяемыми и сами стабильными/примитивными/immutable.
  - Состояние объекта, влияющее на UI, не меняется после создания.
  - Нарушение контракта ведёт к неопределённому поведению.

- `@Stable`:
  - Более общий и мягкий контракт.
  - Тип может быть изменяемым, но все значимые изменения должны быть наблюдаемы для Compose (через `MutableState`, `SnapshotState` и т.п.).
  - Компилятор использует это, чтобы, зная, что прочитанные стабильные поля не менялись, безопасно пропускать рекомпозицию.

Типичные случаи:
- `@Immutable`: чистые value-объекты / DTO / state-холдеры, которые не мутируют.
- `@Stable`: контролируемые изменяемые state-холдеры / обёртки, где вы гарантируете наблюдаемые изменения.

### Влияние На Производительность (уточнение)

```kotlin
@Stable
data class Product(val id: String, val name: String, val price: Double)

@Composable
fun ProductCard(product: Product) {
    Text(product.name)
    Text("$${product.price}")
}

val product = Product("1", "Laptop", 999.99)

ProductCard(product)      // Первая композиция
ProductCard(product)      // Может быть пропущена: тот же стабильный экземпляр, поля не менялись

// Новый экземпляр с теми же значениями:
ProductCard(Product("1", "Laptop", 999.99))
// Пропуск здесь не гарантирован только по equals().
// Для стабильных параметров компилятор опирается на модель стабильности и фактические изменения;
// если он не может доказать отсутствие изменений, рекомпозиция произойдёт.
```

Ключевое уточнение:
- `@Stable` улучшает способность компилятора пропускать рекомпозиции, когда стабильные параметры не меняются в релевантных частях.
- Это НЕ означает "`equals()` вернул true ⇒ рекомпозиция всегда будет пропущена"; решение принимается по модели стабильности, отслеживанию чтений и известным изменениям.

### Частые Ошибки

```kotlin
// ❌ Потенциальная ошибка: @Stable на типе, чьё наблюдаемое поведение
// может меняться без уведомления Compose (например, через внутренние мутации, не завязанные на SnapshotState)
@Stable
class UserHolder(val user: MutableUser)

// ✅ Лучше: immutable/value-like data class или тип, где изменения делаются через observable state
@Immutable
data class User(val id: String, val name: String)
```

Рекомендации:
- Помечайте тип `@Stable` / `@Immutable` только если вы полностью понимаете и соблюдаете контракт.
- Неверная аннотация может привести к пропущенным рекомпозициям и "застывшему" UI.

### Проверка Стабильности

Включите метрики/отчёты компилятора Compose в `build.gradle.kts`:

```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics",
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${project.buildDir}/compose_reports"
    )
}
```

Отчёты покажут, какие классы компилятор считает stable/immutable и как он выводит стабильность, например:

```
stable class User {
  stable val id: String
  stable val name: String
}
```

---

## Answer (EN)

**`@Stable`** is an annotation in Compose that tells the compiler that a type obeys the stability contract. A stable object won't change "behind Compose's back" in a way that affects what composables read from it, so the compiler/runtime can make safe optimizations and skip recompositions when inputs are unchanged according to that contract.

Key idea: `@Stable` is a promise from you to the compiler. If you break it, behavior is undefined (you may get stale UI or missed recompositions).

### Stability Contract

A type is considered stable if it guarantees:

1. Its public properties that affect UI are either:
   - immutable primitives/strings/other stable or immutable types, or
   - exposed via observable state (e.g. `MutableState<T>`), so Compose is notified on change.
2. It does not change in ways that are invisible to Compose:
   - No "spontaneous" mutations of values that composables read without going through observable state.
3. If it is mutable, mutations that affect what composables see are observable to Compose.

```kotlin
// ✅ Stable-like holder: immutable fields of primitive / String types
@Stable
data class User(val id: String, val name: String)

// ✅ Stable class with observable state: mutations are visible to Compose
@Stable
class Counter {
    var count by mutableStateOf(0)
        private set

    fun increment() { count++ }
}

// ❌ Not stable for Compose: mutable field with no observation
class UnstableCounter {
    var count: Int = 0  // Compose is not automatically notified
}
```

Important nuance: `@Stable` does NOT automatically make recomposition decisions based on `equals()` alone. It tells the compiler it may:
- treat the type as stable,
- track which fields are read,
- and skip recomposition when those read stable fields are known not to have changed between calls.

### When to Use @Stable

Use `@Stable` mainly when the compiler cannot infer stability but you know the contract is satisfied:

- Interfaces or abstract types whose implementations are stable.
- Wrappers around third-party or platform types where you control visibility and mutation.

```kotlin
@Stable
interface Repository {
    val data: String
}

@Composable
fun DataDisplay(repository: Repository) {
    Text(repository.data)
}
```

```kotlin
@Stable
class StableThirdPartyData(private val data: ThirdPartyData) {
    val value: String get() = data.value

    override fun equals(other: Any?) =
        other is StableThirdPartyData && other.value == value
    override fun hashCode(): Int = value.hashCode()
}
```

Do NOT annotate arbitrary `ViewModel` classes or generally mutable, complex objects with `@Stable` unless you can strictly uphold the contract. Instead, expose stable/immutable/observable state from them.

### @Stable Vs @Immutable

- `@Immutable`:
  - Stronger contract.
  - All public properties must be immutable and themselves stable/primitive/immutable.
  - Instances never change in a way that affects UI after construction.
  - If you break this contract, behavior is undefined.

- `@Stable`:
  - Weaker, more general contract.
  - Type may be mutable, but all meaningful mutations must be observable to Compose (e.g. via `MutableState`, `SnapshotState`, etc.).
  - Compiler uses this to determine that if none of the observed stable fields change, recomposition can be safely skipped.

Typical use:
- `@Immutable`: pure value objects / DTOs / state holders that never mutate.
- `@Stable`: controlled mutable state holders / wrappers where you guarantee observable changes.

### Performance Impact (Clarified)

```kotlin
@Stable
data class Product(val id: String, val name: String, val price: Double)

@Composable
fun ProductCard(product: Product) {
    Text(product.name)
    Text("$${product.price}")
}

val product = Product("1", "Laptop", 999.99)

ProductCard(product)      // Composes
ProductCard(product)      // May be skipped: same stable instance, fields unchanged

// New instance with same values:
ProductCard(Product("1", "Laptop", 999.99))
// Skipping here is not guaranteed purely by equals().
// For stable parameters, the compiler relies on the stability model and actual changes;
// if it cannot prove that nothing relevant changed, it will recompose.
```

Key clarification:
- `@Stable` improves the compiler's ability to skip recomposition when stable parameters did not change in relevant ways.
- It does NOT mean "equals() true ⇒ recomposition always skipped"; skippability is based on the stability model, tracked reads, and known changes.

### Common Mistakes

```kotlin
// ❌ Potential misuse: @Stable on a type whose observable behavior
// can change without notifying Compose (e.g. internal mutations not based on SnapshotState)
@Stable
class UserHolder(val user: MutableUser)

// ✅ Safer: immutable/value-like data class or a type whose changes are driven via observable state
@Immutable
data class User(val id: String, val name: String)
```

Guidelines:
- Only mark a type `@Stable` / `@Immutable` if you fully understand and uphold the contract.
- Mislabeling can cause missed recompositions and stale UI.

### Verifying Stability

Enable Compose compiler metrics/reports in `build.gradle.kts`:

```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics",
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${project.buildDir}/compose_reports"
    )
}
```

The reports will show which classes the compiler treats as stable/immutable and how stability is inferred, for example:

```
stable class User {
  stable val id: String
  stable val name: String
}
```

---

## Дополнительные Вопросы (RU)

- Что произойдет, если пометить нестабильный класс как `@Stable`?
- Чем `@Stable` отличается от `@Immutable` в практических сценариях?
- Можно ли применять `@Stable` к функциям и лямбдам? (подсказка: аннотация сама по себе не сделает лямбду стабильной для Compose)
- Как метрики компилятора помогают разбирать проблемы со стабильностью?
- Каковы последствия для производительности, если в иерархии Compose много нестабильных типов?

---

## Follow-ups

- What happens if you mark an unstable class as `@Stable` incorrectly?
- How does `@Stable` differ from `@Immutable` in practical scenarios?
- Can `@Stable` be applied to function types and lambdas? (hint: the annotation alone does not make a lambda stable for Compose)
- How do compiler metrics help debug stability issues?
- What are the performance implications of having many unstable types in a Compose hierarchy?

---

## Ссылки (RU)

- [[c-compose-recomposition]] — Понимание рекомпозиции в Compose
- [[c-compose-state]] — Управление состоянием в Compose
- https://developer.android.com/develop/ui/compose/performance/stability
- https://developer.android.com/develop/ui/compose/performance/stability/fix

---

## References

- [[c-compose-recomposition]] - Understanding recomposition in Compose
- [[c-compose-state]] - State management in Compose
- https://developer.android.com/develop/ui/compose/performance/stability
- https://developer.android.com/develop/ui/compose/performance/stability/fix

---

## Связанные Вопросы (RU)

### Предпосылки (Medium)
- [[q-compose-testing--android--medium]] - Понимание рекомпозиции в тестах
- [[q-jetpack-compose-basics--android--medium]] - Основы Compose

### Связанные (Hard)
- [[q-compose-stability-skippability--android--hard]] - Концепции стабильности и skippability
- [[q-compose-performance-optimization--android--hard]] - Стратегии оптимизации производительности
- [[q-compose-slot-table-recomposition--android--hard]] - Внутренние механизмы рекомпозиции

### Продвинутые (Hard)
- [[q-compose-custom-layout--android--hard]] - Производительность кастомных layout-ов

---

## Related Questions

### Prerequisites (Medium)
- [[q-compose-testing--android--medium]] - Understand how recomposition works
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals

### Related (Hard)
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability concepts
- [[q-compose-performance-optimization--android--hard]] - Performance optimization strategies
- [[q-compose-slot-table-recomposition--android--hard]] - Internal recomposition mechanisms

### Advanced (Hard)
- [[q-compose-custom-layout--android--hard]] - Custom layout performance
