---
id: 20251016-162242
title: "Flow Map Operator / Оператор map для Flow"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - programming-languages
---
# Flow Map Operator for Type Transformation

# Question (EN)
> What to use to transform data from one type to another within a single data stream?

# Вопрос (RU)
> Чем воспользоваться чтобы преобразовать внутри одного потока данных данные из одного типа в другой?

---

## Answer (EN)

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

## Ответ (RU)

Используйте оператор **map**. Он преобразует каждый элемент исходного потока в новый элемент другого типа.

Оператор `map` — один из наиболее часто используемых операторов трансформации в Kotlin Flow. Он применяет функцию трансформации к каждому элементу, эмитируемому upstream Flow, и эмитирует трансформированный результат downstream.

### Ключевые характеристики

1. **Трансформация типов**: Преобразует элементы из типа A в тип B
2. **Последовательная обработка**: Обрабатывает элементы один за другим
3. **Поддержка suspend**: Лямбда трансформации может быть suspend функцией
4. **Cold Stream**: Сохраняет cold природу Flow

### Базовый синтаксис

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { value ->
    value * 2  // Трансформация Int в Int
}.collect { transformed ->
    println(transformed)  // Выводит: 2, 4, 6
}
```

### Пример преобразования типа

```kotlin
data class User(val id: Int, val name: String)
data class UserDto(val userId: Int, val userName: String)

fun getUserFlow(): Flow<User> = flow {
    emit(User(1, "Alice"))
    emit(User(2, "Bob"))
}

// Трансформация User в UserDto
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

### Suspend функция в map

```kotlin
suspend fun fetchUserDetails(id: Int): UserDetails {
    delay(100)  // Имитация сетевого вызова
    return UserDetails(id, "Details for $id")
}

flowOf(1, 2, 3)
    .map { id ->
        fetchUserDetails(id)  // Можно вызывать suspend функции
    }
    .collect { details ->
        println(details)
    }
```

### Цепочка нескольких map

```kotlin
flowOf("1", "2", "3")
    .map { it.toInt() }           // String -> Int
    .map { it * 2 }                // Int -> Int
    .map { "Result: $it" }         // Int -> String
    .collect { println(it) }        // Выводит: Result: 2, Result: 4, Result: 6
```

### Реальный пример: Трансформация ответа API

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
// map: Обрабатывает все элементы
flowOf(1, 2, 3)
    .map { it * 2 }
    .collect { println(it) }  // 2, 4, 6

// mapLatest: Отменяет предыдущую трансформацию если приходит новый элемент
flowOf(1, 2, 3)
    .mapLatest { value ->
        delay(100)
        value * 2
    }
    .collect { println(it) }  // Может вывести только 6

// mapNotNull: Фильтрует null результаты
flowOf(1, 2, 3, 4)
    .mapNotNull { if (it % 2 == 0) it * 2 else null }
    .collect { println(it) }  // 4, 8
```

### Распространенные случаи использования

1. **Преобразование DTO в Domain Model**
2. **Форматирование данных** (например, timestamp в читаемые даты)
3. **Трансформация Entity в UI Model**
4. **Применение бизнес-логики** к каждому элементу
5. **Преобразования типов** (String в Int, и т.д.)

### Соображения производительности

- Map — это **легковесный** оператор
- Каждый элемент обрабатывается **независимо**
- Нет буферизации или батчинга
- Используйте `mapLatest` если важен только последний результат
