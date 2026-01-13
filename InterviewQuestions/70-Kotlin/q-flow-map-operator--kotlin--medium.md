---
---
---\
id: lang-065
title: "Flow map operator / Оператор map для Flow"
aliases: [Flow Map Operator, Оператор map для Flow]
topic: kotlin
subtopics: [coroutines, flow, operators]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, flow, kotlin, operators, reactive]
---\
# Вопрос (RU)
> Чем воспользоваться чтобы преобразовать внутри одного потока данных данные из одного типа в другой?

---

# Question (EN)
> What to use to transform data from one type to another within a single data stream?

## Ответ (RU)

Используйте оператор `map`. Он преобразует каждый элемент исходного потока в новый элемент другого типа.

Оператор `map` — один из наиболее часто используемых операторов трансформации в Kotlin `Flow`. Он применяет функцию трансформации к каждому элементу, эмитируемому upstream `Flow`, и эмитирует трансформированный результат downstream, сохраняя порядок элементов.

### Ключевые Характеристики

1. **Трансформация типов**: Преобразует элементы из типа A в тип B
2. **Последовательная обработка**: Для одного коллектора элементы обрабатываются по мере поступления, в порядке upstream
3. **Поддержка suspend**: Лямбда трансформации может быть suspend-функцией
4. **Cold Stream**: Сохраняет cold-природу `Flow`, не изменяет контекст выполнения сам по себе

### Базовый Синтаксис

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

### Пример Преобразования Типа

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

### Suspend Функция В Map

```kotlin
suspend fun fetchUserDetails(id: Int): UserDetails {
    delay(100)  // Имитация сетевого вызова
    return UserDetails(id, "Details for $id")
}

flowOf(1, 2, 3)
    .map { id ->
        fetchUserDetails(id)  // Можно вызывать suspend-функции
    }
    .collect { details ->
        println(details)
    }
```

### Цепочка Нескольких Map

```kotlin
flowOf("1", "2", "3")
    .map { it.toInt() }            // String -> Int
    .map { it * 2 }                // Int -> Int
    .map { "Result: $it" }        // Int -> String
    .collect { println(it) }       // Выводит: Result: 2, Result: 4, Result: 6
```

### Реальный Пример: Трансформация Ответа API

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

### Map Vs mapLatest Vs mapNotNull

```kotlin
// map: Обрабатывает все элементы по порядку
flowOf(1, 2, 3)
    .map { it * 2 }
    .collect { println(it) }  // 2, 4, 6

// mapLatest: Отменяет предыдущую suspend-трансформацию,
// если приходит новый элемент до её завершения
flowOf(1, 2, 3)
    .onEach { delay(100) }
    .mapLatest { value ->
        delay(100)
        value * 2
    }
    .collect { println(it) }
// В этом примере будут обработаны только "актуальные" значения;
// для синхронного flowOf(1, 2, 3) без задержек обычно будет напечатано только 6.

// mapNotNull: Фильтрует null результаты
flowOf(1, 2, 3, 4)
    .mapNotNull { if (it % 2 == 0) it * 2 else null }
    .collect { println(it) }  // 4, 8
```

### Распространенные Случаи Использования

1. **Преобразование DTO в Domain Model**
2. **Форматирование данных** (например, timestamp в читаемые даты)
3. **Трансформация `Entity` в UI Model**
4. **Применение бизнес-логики** к каждому элементу
5. **Преобразования типов** (`String` в `Int`, и т.д.)

### Соображения Производительности

- `map` — **легковесный** оператор
- Каждый элемент обрабатывается **независимо**, в порядке поступления
- Сам по себе не добавляет буферизацию или батчинг
- Не изменяет диспетчер/контекст; используйте `flowOn` для смены контекста
- Используйте `mapLatest`, если важен только последний актуальный результат для длительных операций

## Answer (EN)

Use the `map` operator. It transforms each element of the source stream into a new element of another type.

The `map` operator is one of the most commonly used transformation operators in Kotlin `Flow`. It applies a transformation function to each element emitted by the upstream `Flow` and emits the transformed result downstream while preserving element order.

### Key Characteristics

1. **Type Transformation**: Converts elements from type A to type B
2. **Sequential Processing**: For a single collector, elements are processed as they arrive, in upstream order
3. **Suspension Support**: The transformation lambda can be a suspend function
4. **Cold Stream**: Maintains the cold nature of `Flow` and does not change the execution context by itself

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
    .map { it.toInt() }            // String -> Int
    .map { it * 2 }                // Int -> Int
    .map { "Result: $it" }        // Int -> String
    .collect { println(it) }       // Prints: Result: 2, Result: 4, Result: 6
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

### Map Vs mapLatest Vs mapNotNull

```kotlin
// map: Processes all elements in order
flowOf(1, 2, 3)
    .map { it * 2 }
    .collect { println(it) }  // 2, 4, 6

// mapLatest: Cancels the previous suspend transformation
// if a new element arrives before it completes
flowOf(1, 2, 3)
    .onEach { delay(100) }
    .mapLatest { value ->
        delay(100)
        value * 2
    }
    .collect { println(it) }
// In this pattern, only the "latest" values finish;
// with a synchronous flowOf(1, 2, 3) without delays, you'll typically see only 6 printed.

// mapNotNull: Filters out null results
flowOf(1, 2, 3, 4)
    .mapNotNull { if (it % 2 == 0) it * 2 else null }
    .collect { println(it) }  // 4, 8
```

### Common Use Cases

1. **DTO to Domain Model Conversion**
2. **Data Formatting** (e.g., timestamps to readable dates)
3. **`Entity` to UI Model Transformation**
4. **Applying Business Logic** to each element
5. **Type Conversions** (`String` to `Int`, etc.)

### Performance Considerations

- `map` is a **lightweight** operator
- Each element is processed **independently**, in order
- It does not introduce buffering or batching by itself
- It does not change dispatcher/context; use `flowOn` to change context when needed
- Use `mapLatest` when only the latest relevant result matters for long-running transformations

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-flow]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-flow]]

## Связанные Вопросы (RU)

- [[q-how-gc-knows-object-can-be-destroyed--kotlin--easy]]
- [[q-suspend-functions-under-the-hood--kotlin--hard]]

## Related Questions

- [[q-how-gc-knows-object-can-be-destroyed--kotlin--easy]]
- [[q-suspend-functions-under-the-hood--kotlin--hard]]
