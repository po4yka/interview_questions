---
topic: android
tags:
  - android
  - android/jetpack-compose
  - android/performance
  - immutability
  - jetpack-compose
  - performance
  - recomposition
  - stability
  - stable-annotation
difficulty: hard
status: draft
---

# Какие классы будут автоматически выводиться как stable?

**English**: Which classes are automatically inferred as stable in Jetpack Compose?

## Answer

Classes in Jetpack Compose are automatically considered **stable** if they are:
- **Data classes**
- **Immutable** (all properties are `val`)
- **All properties are stable types** (e.g., String, Int, Float)
- **Do not use mutable reference types**

---

## Stability in Compose

### What is Stability?

**Stability** determines whether Compose can **skip recomposition** of a Composable when parameters haven't changed.

**Stable** means:
- The value **doesn't change spontaneously**
- **`equals()`** always returns the same result for the same values
- Compose can **safely skip recomposition** if parameters are equal

---

## Automatically Stable Types

### 1. Primitive Types

```kotlin
// ✅ Automatically stable
Int, Long, Short, Byte
Float, Double
Boolean
Char
String
```

### 2. Immutable Data Classes with Stable Properties

```kotlin
// ✅ Automatically stable
data class User(
    val id: String,      // Stable (String)
    val name: String,    // Stable (String)
    val age: Int         // Stable (Int)
)

@Composable
fun UserCard(user: User) {  // user parameter is stable
    Text("${user.name}, ${user.age}")
}
```

**Why stable:**
- All properties are `val` (immutable)
- All property types are stable (String, Int)
- Data class (structural equality)

---

## When Classes Are NOT Stable

### 1. Mutable Properties (var)

```kotlin
// ❌ NOT stable - has var
data class User(
    val id: String,
    var name: String,    // ❌ Mutable!
    var age: Int         // ❌ Mutable!
)

@Composable
fun UserCard(user: User) {
    // Compose can't skip recomposition
    // (name/age might change without creating new User instance)
    Text("${user.name}, ${user.age}")
}
```

### 2. Mutable Collections

```kotlin
// ❌ NOT stable - MutableList is mutable
data class UserList(
    val users: MutableList<User>  // ❌ Mutable collection!
)

// ✅ Stable - List is immutable interface
data class UserList(
    val users: List<User>  // ✅ Immutable collection
)
```

### 3. Non-Stable Property Types

```kotlin
// ❌ NOT stable - contains unstable type
data class UserProfile(
    val user: User,
    val settings: MutableSettings  // ❌ MutableSettings is unstable
)

class MutableSettings {
    var darkMode: Boolean = false  // ❌ Mutable property
}
```

---

## Stability Inference Rules

### Rule 1: All Properties Must Be Stable

```kotlin
// ✅ Stable - all properties stable
data class Point(
    val x: Int,      // Stable
    val y: Int       // Stable
)

// ❌ NOT stable - contains unstable property
data class Screen(
    val title: String,           // Stable
    val users: MutableList<User> // ❌ Unstable!
)
```

### Rule 2: Immutability Required

```kotlin
// ✅ Stable - all val
data class Config(
    val timeout: Int,
    val retryCount: Int
)

// ❌ NOT stable - has var
data class Config(
    var timeout: Int,     // ❌ Mutable
    val retryCount: Int
)
```

### Rule 3: Structural Equality

```kotlin
// ✅ Stable - data class has structural equals()
data class User(val id: String, val name: String)

// ❌ NOT stable - regular class uses referential equals()
class User(val id: String, val name: String)
// Need to override equals() and hashCode()
```

---

## Checking Stability

### Compose Compiler Metrics

Enable compiler metrics to see stability inference:

```gradle
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics"
        )
    }
}
```

**Output file shows:**
```
stable class User {
  stable val id: String
  stable val name: String
  stable val age: Int
}

unstable class UserProfile {
  stable val id: String
  unstable var name: String  // ← Problem!
}
```

---

## Performance Impact

### Stable vs Unstable Parameters

```kotlin
// Stable parameter
@Composable
fun UserCard(user: User) {  // User is stable
    Text("${user.name}, ${user.age}")
}

// If same user instance passed:
UserCard(user)  // Compose SKIPS recomposition ✅
```

```kotlin
// Unstable parameter
@Composable
fun UserCard(user: UnstableUser) {  // UnstableUser is unstable
    Text("${user.name}, ${user.age}")
}

// Even if same user instance passed:
UserCard(user)  // Compose CANNOT skip recomposition ❌
                // Must recompose every time
```

---

## Making Classes Stable

### Option 1: Use Data Classes with val

```kotlin
// ❌ Unstable
class User(
    var name: String,
    var age: Int
)

// ✅ Stable
data class User(
    val name: String,
    val age: Int
)
```

### Option 2: Use Immutable Collections

```kotlin
// ❌ Unstable - MutableList
data class Team(
    val name: String,
    val members: MutableList<User>
)

// ✅ Stable - List (immutable interface)
data class Team(
    val name: String,
    val members: List<User>
)

// ✅ Also stable - ImmutableList from kotlinx.collections.immutable
data class Team(
    val name: String,
    val members: ImmutableList<User>
)
```

### Option 3: Use @Stable Annotation

```kotlin
// When Compose can't infer stability, annotate manually
@Stable
class Settings(
    private val _darkMode: Boolean  // Private mutable state
) {
    val darkMode: Boolean get() = _darkMode

    // Override equals/hashCode to prove stability
    override fun equals(other: Any?): Boolean {
        return other is Settings && other._darkMode == _darkMode
    }

    override fun hashCode(): Int = _darkMode.hashCode()
}
```

**Use `@Stable` when:**
- Compose can't infer stability
- You **guarantee** the class behaves stably
- You implement proper `equals()` and `hashCode()`

---

## Common Patterns

### Pattern 1: Immutable Data Classes

```kotlin
// ✅ Stable pattern
data class Product(
    val id: String,
    val name: String,
    val price: Double,
    val inStock: Boolean
)

@Composable
fun ProductCard(product: Product) {
    // Compose can skip recomposition if product hasn't changed
    Column {
        Text(product.name)
        Text("$${product.price}")
    }
}
```

### Pattern 2: Collections

```kotlin
// ✅ Stable - using List (immutable interface)
data class ShoppingCart(
    val items: List<Product>
)

// Update by creating new instance
val newCart = cart.copy(items = cart.items + newProduct)

// ✅ Better - using ImmutableList
import kotlinx.collections.immutable.ImmutableList
import kotlinx.collections.immutable.persistentListOf

data class ShoppingCart(
    val items: ImmutableList<Product>
)

// Efficient updates
val newCart = cart.copy(items = cart.items.add(newProduct))
```

### Pattern 3: State Management

```kotlin
// ❌ Unstable - mutable state
class UserViewModel : ViewModel() {
    var user = User("", "", 0)  // ❌ Mutable
}

// ✅ Stable - immutable with StateFlow
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow(User("", "", 0))
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateUser(newUser: User) {
        _user.value = newUser  // Immutable replacement
    }
}
```

---

## Advanced Example

### Nested Stable Classes

```kotlin
// ✅ All stable
data class Address(
    val street: String,
    val city: String,
    val zipCode: String
)

data class User(
    val id: String,
    val name: String,
    val address: Address  // ✅ Address is stable
)

data class Company(
    val name: String,
    val employees: List<User>  // ✅ List of stable Users
)

@Composable
fun CompanyCard(company: Company) {
    // Compose can skip recomposition efficiently
    Column {
        Text(company.name)
        company.employees.forEach { user ->
            Text(user.name)
        }
    }
}
```

---

## Unstable Class Example

```kotlin
// ❌ Unstable - has var
data class Counter(
    var count: Int  // ❌ Mutable property
)

@Composable
fun CounterDisplay(counter: Counter) {
    // Compose CANNOT skip recomposition
    // Even if counter instance hasn't changed,
    // counter.count might have changed
    Text("Count: ${counter.count}")
}

// Problem demonstration
val counter = Counter(0)
CounterDisplay(counter)  // Displays "Count: 0"

counter.count = 5  // Modified in place
CounterDisplay(counter)  // ❌ Compose doesn't know it changed!
                         // Might still show "Count: 0"
```

**Fix:**
```kotlin
// ✅ Stable - use val and create new instances
data class Counter(
    val count: Int
)

@Composable
fun CounterDisplay(counter: Counter) {
    // Compose CAN skip recomposition
    Text("Count: ${counter.count}")
}

// Usage
var counter by remember { mutableStateOf(Counter(0)) }
CounterDisplay(counter)

// Update by creating new instance
counter = Counter(counter.count + 1)  // ✅ New instance
CounterDisplay(counter)  // Updates correctly
```

---

## Summary

**Automatically stable classes:**
- ✅ **Data classes** with only `val` properties
- ✅ **All properties are stable types** (String, Int, etc.)
- ✅ **Immutable collections** (List, not MutableList)
- ✅ **No mutable state**

**NOT stable:**
- ❌ Classes with `var` properties
- ❌ MutableList, MutableSet, MutableMap
- ❌ Non-data classes without proper equals()
- ❌ Classes containing unstable types

**Benefits of stability:**
- **Skip recomposition** when parameters unchanged
- **Better performance** - fewer recompositions
- **Predictable behavior** - no spontaneous changes

**Best practices:**
1. Use **data classes** with **val** properties
2. Use **immutable collections** (List, ImmutableList)
3. **Create new instances** instead of mutating
4. Use **@Stable** annotation when Compose can't infer
5. Enable **compiler metrics** to check stability

---

## Ответ

Классы в Jetpack Compose автоматически считаются **stable**, если они:
- **Data классы**
- **Неизменяемые (immutable)** - все свойства `val`
- **Все их свойства состоят из stable типов** (например, String, Int, Float)
- **Не используют ссылочные типы с изменяемым состоянием**

**Преимущества stable классов:**
- Compose может **пропустить рекомпозицию**, если параметры не изменились
- **Лучшая производительность** - меньше перерисовок
- **Предсказуемое поведение**

**Как сделать класс stable:**
1. Используйте data class с val
2. Используйте неизменяемые коллекции (List, не MutableList)
3. Создавайте новые экземпляры вместо мутации
4. При необходимости используйте @Stable аннотацию

