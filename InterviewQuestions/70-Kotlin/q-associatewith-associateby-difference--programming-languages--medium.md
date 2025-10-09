---
tags:
  - associateBy
  - associateWith
  - collections
  - kotlin
  - programming-languages
difficulty: medium
status: reviewed
---

# В чём разница между функциями коллекций associateWith() и associateBy()

**English**: What is the difference between collection functions associateWith() and associateBy()?

## Answer

`associateBy` and `associateWith` are Kotlin collection functions that create Maps, but they work in opposite ways.

### associateBy

Creates a Map where:
- **Keys** are computed from elements using a lambda
- **Values** are the original collection elements

**Syntax**: `collection.associateBy { keySelector }`

```kotlin
data class User(val id: Int, val name: String)

val users = listOf(
    User(1, "Alice"),
    User(2, "Bob"),
    User(3, "Charlie")
)

// Keys from id, values are User objects
val usersById = users.associateBy { it.id }
// Result: {1=User(1, Alice), 2=User(2, Bob), 3=User(3, Charlie)}

println(usersById[1])  // User(1, Alice)
println(usersById[2]?.name)  // Bob
```

**With value transform** (optional second lambda):
```kotlin
val nameById = users.associateBy({ it.id }, { it.name })
// Result: {1=Alice, 2=Bob, 3=Charlie}

println(nameById[1])  // Alice
```

### associateWith

Creates a Map where:
- **Keys** are the original collection elements
- **Values** are computed using a lambda

**Syntax**: `collection.associateWith { valueSelector }`

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// Keys are numbers, values are their squares
val squares = numbers.associateWith { it * it }
// Result: {1=1, 2=4, 3=9, 4=16, 5=25}

println(squares[3])  // 9
println(squares[5])  // 25
```

**More examples**:
```kotlin
val words = listOf("apple", "banana", "cherry")

// Keys are words, values are lengths
val wordLengths = words.associateWith { it.length }
// Result: {apple=5, banana=6, cherry=6}

// Keys are words, values are uppercase versions
val uppercase = words.associateWith { it.uppercase() }
// Result: {apple=APPLE, banana=BANANA, cherry=CHERRY}
```

### Comparison

| Function | Keys | Values | Use Case |
|----------|------|--------|----------|
| **associateBy** | Computed from elements | Original elements | Index elements by property |
| **associateWith** | Original elements | Computed from elements | Add computed data to elements |

### Visual Representation

```kotlin
// associateBy: element → (key from element, element)
[User(1, "Alice"), User(2, "Bob")]
  ↓ associateBy { it.id }
{1 → User(1, "Alice"), 2 → User(2, "Bob")}
//  ↑ key from element    ↑ original element

// associateWith: element → (element, value from element)
["apple", "banana"]
  ↓ associateWith { it.length }
{"apple" → 5, "banana" → 6}
//   ↑ original element  ↑ computed value
```

### Practical Examples

**associateBy - Create lookup tables**:
```kotlin
data class Product(val id: String, val name: String, val price: Double)

val products = listOf(
    Product("A1", "Laptop", 999.99),
    Product("B2", "Mouse", 29.99),
    Product("C3", "Keyboard", 79.99)
)

// Quick lookup by ID
val productsById = products.associateBy { it.id }
val laptop = productsById["A1"]  // Product(A1, Laptop, 999.99)

// Lookup by name
val productsByName = products.associateBy { it.name }
val mouse = productsByName["Mouse"]  // Product(B2, Mouse, 29.99)

// Custom transform
val priceById = products.associateBy({ it.id }, { it.price })
// {A1=999.99, B2=29.99, C3=79.99}
```

**associateWith - Add metadata to elements**:
```kotlin
val files = listOf("document.pdf", "image.png", "video.mp4")

// File → Extension
val extensions = files.associateWith {
    it.substringAfterLast('.')
}
// {document.pdf=pdf, image.png=png, video.mp4=mp4}

// File → File size (simulated)
val fileSizes = files.associateWith {
    (Math.random() * 1000).toInt()
}
// {document.pdf=532, image.png=847, video.mp4=123}

// User IDs → Permissions
val userIds = listOf(1, 2, 3, 4, 5)
val permissions = userIds.associateWith { userId ->
    if (userId == 1) "admin" else "user"
}
// {1=admin, 2=user, 3=user, 4=user, 5=user}
```

### Common Use Cases

**associateBy**:
- ✅ Creating ID → Entity maps
- ✅ Indexing collections for fast lookup
- ✅ Converting lists to dictionaries
- ✅ Grouping by unique key

**associateWith**:
- ✅ Adding computed properties to elements
- ✅ Creating element → metadata maps
- ✅ Caching calculated values
- ✅ Enriching data with additional info

### Important Notes

**Duplicate keys**: Last element wins
```kotlin
val list = listOf("a", "b", "a", "c")

// associateBy
val countBy = list.associateBy { it }
// Result: {a=a, b=b, c=c}  // Only one "a" - last one kept

// associateWith
val indexed = list.associateWith { list.indexOf(it) }
// Result: {a=2, b=1, c=3}  // indexOf returns last occurrence
```

**Use groupBy for multiple values per key**:
```kotlin
val list = listOf("apple", "apricot", "banana", "blueberry")

// If you need multiple values per key, use groupBy
val byFirstLetter = list.groupBy { it.first() }
// {a=[apple, apricot], b=[banana, blueberry]}
```

### Summary

```kotlin
// associate BY property → lookup table
users.associateBy { it.id }      // ID → User
users.associateBy { it.name }    // Name → User

// associate WITH computed value → enrichment
ids.associateWith { fetchData(it) }     // ID → Data
keys.associateWith { computeValue(it) } // Key → Computed Value
```

**Memory aid**:
- `associateBy` = "index BY this property" → element becomes value
- `associateWith` = "associate WITH this value" → element becomes key

## Ответ

`associateBy` создаёт Map, где ключи вычисляются из элементов (например, по ID), а значениями становятся сами элементы коллекции. Используется для создания lookup-таблиц.

`associateWith` создаёт Map, где ключами становятся элементы коллекции, а значения вычисляются из них. Используется для обогащения элементов вычисленными данными.

Пример:
```kotlin
users.associateBy { it.id }       // {1=User(1), 2=User(2)}  - ключ из элемента
numbers.associateWith { it * it }  // {1=1, 2=4, 3=9}        - элемент как ключ
```

