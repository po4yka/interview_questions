---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# Flow Map Operator for Type Transformation

## Answer

Use the **map** operator. It transforms each element of the source stream into a new element of another type.

The `map` operator is one of the most commonly used transformation operators in Kotlin Flow. It applies a transformation function to each element emitted by the upstream Flow and emits the transformed result downstream.

### Key Characteristics

1. **Type Transformation**: Converts elements from type A to type B
2. **Sequential Processing**: Processes elements one by one
3. **Suspension Support**: The transformation lambda can be a suspend function
4. **Cold Stream**: Maintains the cold nature of Flow

### Basic Syntax

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { value ->
    value * 2  // Transform Int to Int
}.collect { transformed ->
    println(transformed)  // Prints: 2, 4, 6
}
```

### Type Conversion Example

```kotlin
data class User(val id: Int, val name: String)
data class UserDto(val userId: Int, val userName: String)

fun getUserFlow(): Flow<User> = flow {
    emit(User(1, "Alice"))
    emit(User(2, "Bob"))
}

// Transform User to UserDto
getUserFlow()
    .map { user ->
        UserDto(
            userId = user.id,
            userName = user.name
        )
    }
    .collect { dto ->
        println("DTO: ${dto.userName}")
    }
```

### Suspend Function in Map

```kotlin
suspend fun fetchUserDetails(id: Int): UserDetails {
    delay(100)  // Simulate network call
    return UserDetails(id, "Details for $id")
}

flowOf(1, 2, 3)
    .map { id ->
        fetchUserDetails(id)  // Can call suspend functions
    }
    .collect { details ->
        println(details)
    }
```

### Chaining Multiple Maps

```kotlin
flowOf("1", "2", "3")
    .map { it.toInt() }           // String -> Int
    .map { it * 2 }                // Int -> Int
    .map { "Result: $it" }         // Int -> String
    .collect { println(it) }        // Prints: Result: 2, Result: 4, Result: 6
```

### Real-World Example: API Response Transformation

```kotlin
data class ApiResponse(val data: String, val timestamp: Long)
data class DomainModel(val content: String, val formattedDate: String)

fun fetchData(): Flow<ApiResponse> = flow {
    emit(ApiResponse("Hello", System.currentTimeMillis()))
    delay(1000)
    emit(ApiResponse("World", System.currentTimeMillis()))
}

fetchData()
    .map { response ->
        DomainModel(
            content = response.data,
            formattedDate = SimpleDateFormat("HH:mm:ss").format(Date(response.timestamp))
        )
    }
    .collect { model ->
        println("${model.content} at ${model.formattedDate}")
    }
```

### Map vs MapLatest vs MapNotNull

```kotlin
// map: Processes all elements
flowOf(1, 2, 3)
    .map { it * 2 }
    .collect { println(it) }  // 2, 4, 6

// mapLatest: Cancels previous transformation if new element arrives
flowOf(1, 2, 3)
    .mapLatest { value ->
        delay(100)
        value * 2
    }
    .collect { println(it) }  // May only print 6

// mapNotNull: Filters out null results
flowOf(1, 2, 3, 4)
    .mapNotNull { if (it % 2 == 0) it * 2 else null }
    .collect { println(it) }  // 4, 8
```

### Common Use Cases

1. **DTO to Domain Model Conversion**
2. **Data Formatting** (e.g., timestamps to readable dates)
3. **Entity to UI Model Transformation**
4. **Applying Business Logic** to each element
5. **Type Conversions** (String to Int, etc.)

### Performance Considerations

- Map is a **lightweight** operator
- Each element is processed **independently**
- No buffering or batching occurs
- Use `mapLatest` if only the latest result matters

---
## Вопрос (RU)

Чем воспользоваться чтобы преобразовать внутри одного потока данных данные из одного типа в другой

## Ответ

Используйте оператор map. Преобразует каждый элемент исходного потока в новый элемент другого типа.
