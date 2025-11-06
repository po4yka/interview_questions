---
id: android-429
title: "Stable Annotation Compose / Аннотация Stable в Compose"
aliases: ["Stable Annotation Compose", "Аннотация Stable в Compose"]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [android/performance-rendering, android/ui-compose, difficulty/hard, jetpack-compose, recomposition, stable-annotation]
---

# Вопрос (RU)

Что известно про `@Stable` в Jetpack Compose?

# Question (EN)

What is known about `@Stable` in Jetpack Compose?

---

## Ответ (RU)

**`@Stable`** — аннотация в Compose, которая сообщает компилятору, что объект **стабилен** и его свойства **не меняются спонтанно**. Это позволяет Compose **эффективно определять**, когда нужна перерисовка UI, сокращая ненужные рекомпозиции.

### Контракт Стабильности

Тип **стабилен**, если гарантирует:

1. **Консистентность equals()** — если `a.equals(b)` возвращает `true`, это будет всегда `true` для тех же экземпляров.
2. **Нет спонтанных изменений** — свойства не мутируют неожиданно. Изменения происходят только через **явные API** (например, `copy()`).
3. **Уведомления при мутациях** — если тип допускает изменения, он должен **уведомлять Compose** через observable механизмы (MutableState, Flow).

```kotlin
// ✅ Стабильный класс с консистентным equals()
@Stable
data class User(val id: String, val name: String)

// ✅ Стабильный класс с observable состоянием
@Stable
class Counter {
    var count by mutableStateOf(0)  // Уведомляет Compose
        private set

    fun increment() { count++ }
}

// ❌ Не стабильный — мутабельное состояние без уведомлений
class UnstableCounter {
    var count: Int = 0  // Compose не узнает об изменениях
}
```

### Когда Использовать @Stable

**Case 1**: Compose не может вывести стабильность автоматически (интерфейсы, внешние классы).

```kotlin
@Stable
interface Repository {
    val data: String
}

@Composable
fun DataDisplay(repository: Repository) {
    Text(repository.data)  // Compose может пропустить рекомпозицию
}
```

**Case 2**: Обёртка для внешних классов третьих сторон.

```kotlin
@Stable
class StableThirdPartyData(private val data: ThirdPartyData) {
    val value: String get() = data.value

    override fun equals(other: Any?) =
        other is StableThirdPartyData && other.value == value
    override fun hashCode() = value.hashCode()
}
```

### @Stable Vs @Immutable

| Аспект | @Immutable | @Stable |
|--------|-----------|---------|
| Изменения после создания | Никогда | Возможны (но observable) |
| equals() консистентна | Да | Да |
| Уведомления Compose | N/A | Обязательны при изменении |
| Типичное применение | Чистые data class | ViewModel, observable state |

### Влияние На Производительность

```kotlin
@Stable
data class Product(val id: String, val name: String, val price: Double)

@Composable
fun ProductCard(product: Product) {
    Text(product.name)
    Text("$${product.price}")
}

val product = Product("1", "Laptop", 999.99)

ProductCard(product)  // Композиция
ProductCard(product)  // ✅ Пропущена (тот же экземпляр)
ProductCard(Product("1", "Laptop", 999.99))  // ✅ Пропущена (equals() true)

// ❌ Без @Stable — рекомпозиция каждый раз, даже с тем же экземпляром
```

### Частые Ошибки

```kotlin
// ❌ @Stable без правильного equals()
@Stable
class User(val id: String, val name: String)
// Использует referential equality — Compose не пропустит рекомпозицию

// ✅ Правильно — data class предоставляет structural equals()
@Stable
data class User(val id: String, val name: String)
```

### Проверка Стабильности

Включите метрики компилятора Compose в `build.gradle.kts`:

```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics"
    )
}
```

Вывод покажет, какие классы считаются стабильными:

```
stable class User {
  stable val id: String
  stable val name: String
}
```

---

## Answer (EN)

**`@Stable`** is an annotation in Compose that tells the compiler an object is **stable** and its properties **don't change spontaneously**. This allows Compose to **efficiently determine** when UI needs redrawing, reducing unnecessary recompositions.

### Stability Contract

A type is **stable** if it guarantees:

1. **equals() Consistency** — if `a.equals(b)` returns `true`, it will **always** return `true` for those same instances.
2. **No Spontaneous Changes** — properties don't mutate unexpectedly. Changes happen only through **explicit APIs** (e.g., `copy()`).
3. **Notifications on Mutations** — if the type allows mutations, it must **notify Compose** via observable mechanisms (MutableState, Flow).

```kotlin
// ✅ Stable class with consistent equals()
@Stable
data class User(val id: String, val name: String)

// ✅ Stable class with observable state
@Stable
class Counter {
    var count by mutableStateOf(0)  // Notifies Compose
        private set

    fun increment() { count++ }
}

// ❌ Not stable — mutable state without notifications
class UnstableCounter {
    var count: Int = 0  // Compose doesn't know about changes
}
```

### When to Use @Stable

**Case 1**: Compose can't infer stability automatically (interfaces, external classes).

```kotlin
@Stable
interface Repository {
    val data: String
}

@Composable
fun DataDisplay(repository: Repository) {
    Text(repository.data)  // Compose can skip recomposition
}
```

**Case 2**: Wrapping third-party external classes.

```kotlin
@Stable
class StableThirdPartyData(private val data: ThirdPartyData) {
    val value: String get() = data.value

    override fun equals(other: Any?) =
        other is StableThirdPartyData && other.value == value
    override fun hashCode() = value.hashCode()
}
```

### @Stable Vs @Immutable

| Aspect | @Immutable | @Stable |
|--------|-----------|---------|
| Change after creation | Never | Possibly (but observable) |
| equals() consistency | Always | Always |
| Compose notification | N/A | Required on change |
| Typical use case | Pure data classes | ViewModels, observable state |

### Performance Impact

```kotlin
@Stable
data class Product(val id: String, val name: String, val price: Double)

@Composable
fun ProductCard(product: Product) {
    Text(product.name)
    Text("$${product.price}")
}

val product = Product("1", "Laptop", 999.99)

ProductCard(product)  // Composes
ProductCard(product)  // ✅ Skipped (same instance)
ProductCard(Product("1", "Laptop", 999.99))  // ✅ Skipped (equals() true)

// ❌ Without @Stable — recomposes every time, even with same instance
```

### Common Mistakes

```kotlin
// ❌ @Stable without proper equals()
@Stable
class User(val id: String, val name: String)
// Uses referential equality — Compose won't skip recomposition

// ✅ Correct — data class provides structural equals()
@Stable
data class User(val id: String, val name: String)
```

### Verifying Stability

Enable Compose compiler metrics in `build.gradle.kts`:

```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics"
    )
}
```

Output shows which classes are considered stable:

```
stable class User {
  stable val id: String
  stable val name: String
}
```

---

## Follow-ups

- What happens if you mark an unstable class as `@Stable` incorrectly?
- How does `@Stable` differ from `@Immutable` in practical scenarios?
- Can `@Stable` be applied to function types and lambdas?
- How do compiler metrics help debug stability issues?
- What are the performance implications of having many unstable types in a Compose hierarchy?

---

## References

- [[c-compose-recomposition]] - Understanding recomposition in Compose
- [[c-compose-state]] - State management in Compose
- https://developer.android.com/develop/ui/compose/performance/stability
- https://developer.android.com/develop/ui/compose/performance/stability/fix

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
- [[q-compose-derived-state--android--hard]] - Derived state optimization
