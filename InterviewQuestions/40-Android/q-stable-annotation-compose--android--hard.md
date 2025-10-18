---
id: 20251012-122711109
title: "Stable Annotation Compose / Аннотация Stable в Compose"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-multithreading-tools-android--android--medium, q-push-notification-navigation--android--medium, q-save-data-outside-fragment--android--medium]
created: 2025-10-15
tags: [android/jetpack-compose, android/performance, annotations, jetpack-compose, optimization, performance, recomposition, stability, stable-annotation, difficulty/hard]
---
# Что известно про stable?

**English**: What is known about @Stable?

## Answer (EN)
**`@Stable`** is an annotation in Compose that indicates an **object is stable** and its **properties don't change spontaneously**. This helps Compose **efficiently determine when UI needs to be redrawn**, reducing unnecessary recompositions.

---

## @Stable Annotation

### Definition

```kotlin
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION, AnnotationTarget.PROPERTY)
@Retention(AnnotationRetention.BINARY)
annotation class Stable
```

**Purpose:** Tell Compose compiler that a type is **stable** even if it can't automatically infer stability.

---

## Stability Contract

A type is **stable** if it guarantees:

### 1. Result of equals() is Consistent

```kotlin
@Stable
class User(private val name: String) {
    override fun equals(other: Any?): Boolean {
        return other is User && other.name == name
    }

    override fun hashCode(): Int = name.hashCode()
}

val user1 = User("Alice")
val user2 = User("Alice")

user1 == user2  // - Always true (consistent equals)
```

**Contract:** If `a.equals(b)` returns `true`, it will **always** return `true` for those same instances.

### 2. Properties Don't Change Spontaneously

```kotlin
@Stable
class Configuration(
    val timeout: Int,
    val retryCount: Int
) {
    // Properties are val - can't change
}

val config = Configuration(30, 3)
// config.timeout will ALWAYS be 30
// config.retryCount will ALWAYS be 3
```

**Contract:** Properties **don't mutate** unexpectedly. Changes only happen through **explicit API calls** (like `copy()`).

### 3. Notifications on Mutations

If a stable type **does** allow mutations, it must **notify Compose**:

```kotlin
@Stable
class MutableCounter {
    private val _count = mutableStateOf(0)
    val count: State<Int> = _count  // Notifies Compose on change

    fun increment() {
        _count.value++  // Compose is notified automatically
    }
}
```

**Contract:** If state changes, Compose is **notified** via observable mechanisms (MutableState, Flow, etc.).

---

## When to Use @Stable

### Case 1: Class Compose Can't Infer

```kotlin
// - Compose can't infer stability (interface)
interface Repository {
    val data: String
}

// - Annotate to help Compose
@Stable
interface Repository {
    val data: String
}

@Composable
fun DataDisplay(repository: Repository) {
    // Compose can now skip recomposition if repository hasn't changed
    Text(repository.data)
}
```

### Case 2: External Classes

```kotlin
// - Third-party class, Compose can't infer
class ThirdPartyData(val value: String)

// - Wrap and annotate
@Stable
class StableThirdPartyData(private val data: ThirdPartyData) {
    val value: String get() = data.value

    override fun equals(other: Any?): Boolean {
        return other is StableThirdPartyData && other.value == value
    }

    override fun hashCode(): Int = value.hashCode()
}
```

### Case 3: Complex Stable Behavior

```kotlin
@Stable
class ComputedValue(
    private val source: String
) {
    // Computed on-demand, but result is stable for same source
    val hash: String by lazy {
        source.hashCode().toString()
    }

    override fun equals(other: Any?): Boolean {
        return other is ComputedValue && other.source == source
    }

    override fun hashCode(): Int = source.hashCode()
}
```

---

## @Stable vs @Immutable

### @Immutable

**Stronger guarantee:** Properties **never change** after construction.

```kotlin
@Immutable
data class User(
    val id: String,
    val name: String
)

// After construction, id and name NEVER change
val user = User("1", "Alice")
// user.id will ALWAYS be "1"
// user.name will ALWAYS be "Alice"
```

### @Stable

**Weaker guarantee:** Properties **might change**, but in a **controlled, observable** way.

```kotlin
@Stable
class UserViewModel {
    private val _user = MutableStateFlow(User("1", "Alice"))
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateUser(newUser: User) {
        _user.value = newUser  // - Change is observable
    }
}
```

### Comparison

| Aspect | @Immutable | @Stable |
|--------|-----------|---------|
| **Change after creation** | Never | Possibly (but observable) |
| **equals() consistency** | Always | Always |
| **Compose notification** | N/A (never changes) | Required (on change) |
| **Use case** | Pure data classes | ViewModels, observable state |

---

## Performance Impact

### With @Stable

```kotlin
@Stable
data class Product(
    val id: String,
    val name: String,
    val price: Double
)

@Composable
fun ProductCard(product: Product) {
    Column {
        Text(product.name)
        Text("$${product.price}")
    }
}

// Usage
val product = Product("1", "Laptop", 999.99)

// First call
ProductCard(product)  // Composes

// Second call with SAME instance
ProductCard(product)  // - SKIPPED (product stable and unchanged)

// Third call with EQUAL instance
ProductCard(Product("1", "Laptop", 999.99))  // - SKIPPED (equals() returns true)
```

### Without @Stable

```kotlin
// - No @Stable annotation
class UnstableProduct(
    val id: String,
    val name: String,
    val price: Double
)

@Composable
fun ProductCard(product: UnstableProduct) {
    Column {
        Text(product.name)
        Text("$${product.price}")
    }
}

val product = UnstableProduct("1", "Laptop", 999.99)

ProductCard(product)  // Composes
ProductCard(product)  // - RECOMPOSES (Compose can't trust stability)
```

---

## Real-World Examples

### Example 1: ViewModel

```kotlin
@Stable
class ProductViewModel : ViewModel() {
    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products: StateFlow<List<Product>> = _products.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun loadProducts() {
        viewModelScope.launch {
            _isLoading.value = true
            _products.value = repository.getProducts()
            _isLoading.value = false
        }
    }
}

@Composable
fun ProductScreen(viewModel: ProductViewModel = viewModel()) {
    val products by viewModel.products.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    // Efficient recomposition: only when products/isLoading change
    if (isLoading) {
        CircularProgressIndicator()
    } else {
        ProductList(products)
    }
}
```

### Example 2: Custom State Holder

```kotlin
@Stable
class SearchState(
    initialQuery: String = ""
) {
    var query by mutableStateOf(initialQuery)
        private set

    var results by mutableStateOf<List<SearchResult>>(emptyList())
        private set

    fun updateQuery(newQuery: String) {
        query = newQuery
    }

    fun updateResults(newResults: List<SearchResult>) {
        results = newResults
    }
}

@Composable
fun SearchScreen() {
    val searchState = remember { SearchState() }

    Column {
        SearchBar(
            query = searchState.query,
            onQueryChange = { searchState.updateQuery(it) }
        )

        SearchResults(results = searchState.results)
    }
}
```

### Example 3: Wrapper for External Library

```kotlin
// Third-party library class
class ExternalConfig(val timeout: Int, val retries: Int)

// - Wrap and annotate
@Stable
class AppConfig(
    private val external: ExternalConfig
) {
    val timeout: Int get() = external.timeout
    val retries: Int get() = external.retries

    override fun equals(other: Any?): Boolean {
        return other is AppConfig &&
               other.timeout == timeout &&
               other.retries == retries
    }

    override fun hashCode(): Int {
        return 31 * timeout + retries
    }
}

@Composable
fun ConfigDisplay(config: AppConfig) {
    // Compose can skip recomposition efficiently
    Column {
        Text("Timeout: ${config.timeout}")
        Text("Retries: ${config.retries}")
    }
}
```

---

## Common Mistakes

### Mistake 1: @Stable Without equals()

```kotlin
// - BAD: @Stable but no proper equals()
@Stable
class User(val id: String, val name: String)
// Uses default equals() (referential equality)

val user1 = User("1", "Alice")
val user2 = User("1", "Alice")

user1 == user2  // false (different instances)

// Compose won't skip recomposition for equal users!
```

**Fix:**
```kotlin
// - GOOD: @Stable with proper equals()
@Stable
data class User(val id: String, val name: String)
// data class provides structural equals()

val user1 = User("1", "Alice")
val user2 = User("1", "Alice")

user1 == user2  // true (same values)
```

### Mistake 2: @Stable with Mutable State

```kotlin
// - BAD: @Stable but mutable without notification
@Stable
class Counter {
    var count: Int = 0  // - Mutable but doesn't notify Compose!

    fun increment() {
        count++  // Compose doesn't know about this change!
    }
}
```

**Fix:**
```kotlin
// - GOOD: @Stable with observable mutable state
@Stable
class Counter {
    var count by mutableStateOf(0)  // - Notifies Compose
        private set

    fun increment() {
        count++  // Compose is notified automatically
    }
}
```

---

## Verifying Stability

### Compose Compiler Metrics

```gradle
// build.gradle.kts
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

**Check output:**
```
stable class User {
  stable val id: String
  stable val name: String
}

stable class ProductViewModel {
  stable val products: StateFlow<List<Product>>
  stable val isLoading: StateFlow<Boolean>
}
```

---

## Summary

**`@Stable` annotation:**
- Tells Compose a type is **stable** (predictable behavior)
- Helps Compose **skip unnecessary recompositions**
- Requires **consistent equals()** and **controlled mutations**

**Use @Stable when:**
- Compose can't infer stability automatically
- Wrapping external classes
- ViewModels with observable state
- Complex stable behaviors

**Stability contract:**
1. **equals() is consistent** (same values → same result)
2. **No spontaneous changes** (mutations are explicit)
3. **Notifications on mutations** (via MutableState, Flow, etc.)

**Performance benefit:**
- Compose can **skip recomposition** when parameters haven't changed
- Fewer UI updates = better performance

**Comparison:**
- **@Immutable** - Stronger (never changes)
- **@Stable** - Weaker (might change, but observably)

**Best practices:**
1. Use `data class` when possible (automatic equals())
2. Implement proper `equals()` and `hashCode()`
3. Use observable state (MutableState, StateFlow)
4. Verify with compiler metrics

---

## Ответ (RU)
**`@Stable`** - это аннотация в Compose, которая указывает, что объект **стабилен** и его свойства **не изменяются спонтанно**. Это помогает Compose эффективно определять, когда нужно перерисовывать UI, уменьшая количество лишних перерисовок.

**Контракт стабильности:**
1. **equals() консистентна** - одинаковые значения всегда дают одинаковый результат
2. **Нет спонтанных изменений** - свойства не меняются неожиданно
3. **Уведомления при мутациях** - если состояние меняется, Compose уведомляется (через MutableState, Flow)

**Когда использовать:**
- Compose не может автоматически вывести стабильность
- Оборачивание внешних классов
- ViewModel с наблюдаемым состоянием

**Преимущество:**
- Compose может **пропустить рекомпозицию**, если параметры не изменились
- Меньше перерисовок = лучшая производительность



---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table internals
- [[q-compose-performance-optimization--android--hard]] - Performance optimization
- [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts

