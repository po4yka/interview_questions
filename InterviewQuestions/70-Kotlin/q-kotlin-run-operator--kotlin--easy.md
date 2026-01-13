---
anki_cards:
- slug: q-kotlin-run-operator--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-run-operator--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: lang-017
title: "Kotlin Run Operator / Оператор run в Kotlin"
aliases: [Kotlin Run Operator, Оператор run в Kotlin]
topic: kotlin
subtopics: [functions, scope-functions]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-compose-side-effects-coroutines--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [also, apply, difficulty/easy, kotlin, let, run, scope-functions, with]
---\
# Вопрос (RU)
> Какой оператор в Kotlin исполняет блок кода и возвращает его значение?

---

# Question (EN)
> Which operator in Kotlin executes a block of code and returns its value?

## Ответ (RU)

Функция `run` — это scope-функция, которая выполняет блок кода и возвращает результат. Она полезна для выполнения нескольких операций над объектом или в ограниченной области видимости с возвратом итогового значения. См. также [[c-kotlin]] и [[c-kotlin-features]].

### Базовое Использование
```kotlin
val result = "Hello".run {
    println(length)  // Доступ к свойствам через 'this'
    uppercase()       // Возвращает трансформацию
}
println(result)  // "HELLO"
```

### Распространенные Паттерны

**1. Конфигурация объекта**
```kotlin
val person = Person().run {
    name = "Alice"
    age = 25
    address = "123 Main St"
    this  // Вернуть сконфигурированный объект
}
```

**2. Null безопасность**
```kotlin
val result = value?.run {
    transform()
} ?: defaultValue
```

**3. Вычисления в scope**
```kotlin
val formatted = run {
    val first = getName()
    val last = getLastName()
    "$first $last"
}
```

**vs `let`, `apply`, `also`:**
- `run`: Имеет `this`, возвращает результат лямбды
- `let`: Имеет `it`, возвращает результат лямбды
- `apply`: Имеет `this`, возвращает receiver
- `also`: Имеет `it`, возвращает receiver

---

## Answer (EN)

The `run` function is a scope function that executes a block of code and returns the result. It is useful for performing multiple operations on an object or within a limited scope while returning a final value. See also [[c-kotlin]] and [[c-kotlin-features]].

### Basic Usage
```kotlin
val result = "Hello".run {
    println(length)  // Access properties via 'this'
    uppercase()       // Returns transformation
}
println(result)  // "HELLO"
```

### Common Patterns

**1. Object Configuration**
```kotlin
val person = Person().run {
    name = "Alice"
    age = 25
    address = "123 Main St"
    this  // Return configured object
}
```

**2. Null Safety**
```kotlin
val result = value?.run {
    transform()
} ?: defaultValue
```

**3. Scoped Computation**
```kotlin
val formatted = run {
    val first = getName()
    val last = getLastName()
    "$first $last"
}
```

**vs `let`, `apply`, `also`:**
- `run`: Has `this`, returns lambda result
- `let`: Has `it`, returns lambda result
- `apply`: Has `this`, returns receiver
- `also`: Has `it`, returns receiver

---

## Варианты Использования Run

### 1. Object.run (Extension-функция)

```kotlin
data class User(var name: String, var age: Int)

val user = User("Alice", 25)

val greeting = user.run {
    // 'this' ссылается на user
    age += 1  // Изменяем user
    "Hello, $name! You are now $age years old."  // Возвращаемое значение
}

println(greeting)  // "Hello, Alice! You are now 26 years old."
println(user.age)  // 26 (изменен)
```

**Характеристики:**
- Контекстный объект: `this`
- Возвращает: Результат лямбды
- Применение: Трансформация объекта с возвратом результата

### 2. Run (Автономная функция)

```kotlin
val result = run {
    val x = 10
    val y = 20
    val z = x + y
    z * 2  // Возвращает 60
}

println(result)  // 60
```

**Характеристики:**
- Нет контекстного объекта
- Возвращает: Результат лямбды
- Применение: Выполнение блока с возвратом результата

---

## Usage Variants of Run

### 1. Object.run (Extension function)

```kotlin
data class User(var name: String, var age: Int)

val user = User("Alice", 25)

val greeting = user.run {
    // 'this' refers to user
    age += 1  // Modify user
    "Hello, $name! You are now $age years old."  // Return value
}

println(greeting)  // "Hello, Alice! You are now 26 years old."
println(user.age)  // 26 (modified)
```

**Characteristics:**
- `Context` object: `this`
- Returns: Lambda result
- Usage: Transform object and return a value

### 2. Top-level Run (Standalone function)

```kotlin
val result = run {
    val x = 10
    val y = 20
    val z = x + y
    z * 2  // Returns 60
}

println(result)  // 60
```

**Characteristics:**
- No context object
- Returns: Lambda result
- Usage: Execute a block and return its result

---

## Сравнение С Другими Scope-функциями

| Функция | Ссылка на объект | Возвращаемое значение | Применение |
|---------|------------------|-----------------------|------------|
| **run** | `this`           | Результат лямбды      | Трансформация и возврат |
| **let** | `it`             | Результат лямбды      | Проверка null, трансформация |
| **apply** | `this`         | Контекстный объект    | Конфигурация объекта |
| **also** | `it`            | Контекстный объект    | Побочные эффекты |
| **with** | `this`          | Результат лямбды      | Множественные вызовы на объекте |

---

## Comparison with Other Scope Functions

| Function | Object reference | Return value        | Usage                     |
|----------|------------------|---------------------|---------------------------|
| **run**  | `this`           | Lambda result       | Transformation + return   |
| **let**  | `it`             | Lambda result       | Null check, transformation|
| **apply**| `this`           | Receiver object     | Object configuration      |
| **also** | `it`             | Receiver object     | Side effects              |
| **with** | `this`           | Lambda result       | Multiple calls on object  |

---

## Примеры Использования Run

### 1. Вычисление И Возврат Результата

```kotlin
val result = user.run {
    val fullName = "$firstName $lastName"
    val age = calculateAge(birthDate)
    "$fullName ($age years old)"  // Возвращается
}
```

### 2. Null-безопасность С Run

```kotlin
val length = str?.run {
    trim()
    uppercase()
    length  // Возвращается, если str не null
} ?: 0  // Значение по умолчанию, если str null
```

### 3. Инициализация И Конфигурация

```kotlin
val db = Database().run {
    connect()
    migrate()
    this  // Возвращаем сконфигурированную БД
}
```

### 4. Сложные Вычисления

```kotlin
val price = product.run {
    val basePrice = this.basePrice
    val discount = this.discount
    val tax = (basePrice - discount) * 0.2
    basePrice - discount + tax  // Финальная цена
}
```

---

## Examples of Using Run

### 1. Compute and Return a Result

```kotlin
val result = user.run {
    val fullName = "$firstName $lastName"
    val age = calculateAge(birthDate)
    "$fullName ($age years old)"  // Returned
}
```

### 2. Null Safety with Run

```kotlin
val length = str?.run {
    trim()
    uppercase()
    length  // Returned if str is not null
} ?: 0  // Default if str is null
```

### 3. Initialization and Configuration

```kotlin
val db = Database().run {
    connect()
    migrate()
    this  // Return configured DB
}
```

### 4. Complex Calculations

```kotlin
val price = product.run {
    val basePrice = this.basePrice
    val discount = this.discount
    val tax = (basePrice - discount) * 0.2
    basePrice - discount + tax  // Final price
}
```

---

## Run Vs Другие Scope-функции

### Run Vs Let

```kotlin
// run - использует 'this'
val result1 = user.run {
    println(name)  // Прямой доступ
    age
}

// let - использует 'it'
val result2 = user.let {
    println(it.name)  // Нужно использовать 'it'
    it.age
}
```

**Используйте `run` когда:**
- Нужен `this` вместо `it`
- Множественный доступ к свойствам без повторения `it`

**Используйте `let` когда:**
- Null-безопасность с `?.let`
- Нужно явное имя параметра

### Run Vs Apply

```kotlin
// run - возвращает результат лямбды
val length = StringBuilder().run {
    append("Hello")
    append(" World")
    length  // Возвращает Int (длину)
}

// apply - возвращает сам объект
val builder = StringBuilder().apply {
    append("Hello")
    append(" World")
}  // Возвращает StringBuilder
```

**Используйте `run` когда:**
- Нужно вернуть вычисленное значение

**Используйте `apply` когда:**
- Нужно вернуть сконфигурированный объект

### Run Vs with

```kotlin
// run - extension-функция
val result1 = user.run {
    "$name is $age years old"
}

// with - обычная функция
val result2 = with(user) {
    "$name is $age years old"
}
```

**Используйте `run` когда:**
- Объект может быть null (`user?.run`)
- Цепочка операций

**Используйте `with` когда:**
- Объект точно не null
- Предпочитаете синтаксис вызова функции

---

## Run Vs Other Scope Functions

### Run Vs Let

```kotlin
val result1 = user.run {
    println(name)
    age
}

val result2 = user.let {
    println(it.name)
    it.age
}
```

Use `run` when:
- You prefer `this` over `it`.
- You want concise access to members without repeating `it`.

Use `let` when:
- You use null-safe chains with `?.let`.
- You want an explicit lambda parameter.

### Run Vs Apply

```kotlin
val length = StringBuilder().run {
    append("Hello")
    append(" World")
    length  // Returns Int length
}

val builder = StringBuilder().apply {
    append("Hello")
    append(" World")
}  // Returns StringBuilder
```

Use `run` when:
- You need a computed result.

Use `apply` when:
- You need the configured object itself.

### Run Vs with

```kotlin
val result1 = user.run {
    "$name is $age years old"
}

val result2 = with(user) {
    "$name is $age years old"
}
```

Use `run` when:
- The receiver might be null (`user?.run`).
- You chain operations.

Use `with` when:
- Receiver is non-null and you prefer function style.

---

## Практические Примеры

### Пример 1: Запрос К Базе Данных

```kotlin
val users = database.run {
    connect()
    val query = "SELECT * FROM users WHERE active = true"
    executeQuery(query)
    mapToUsers(resultSet)  // Возвращается
}
```

### Пример 2: Конфигурация

```kotlin
val config = Config().run {
    setHost("localhost")
    setPort(8080)
    setTimeout(30)
    validate()  // Возвращает Boolean
}

if (config) {
    startServer()
}
```

### Пример 3: Null-безопасность

```kotlin
val userInfo = user?.run {
    "Name: $name\nAge: $age\nEmail: $email"
} ?: "User not found"
```

### Пример 4: Множественные Трансформации

```kotlin
val processed = data
    .filter { it.isValid }
    .run {
        // 'this' - отфильтрованный список
        if (isEmpty()) {
            emptyList()
        } else {
            map { it.process() }
        }
    }
```

### Пример 5: Управление Ресурсами

```kotlin
val content = File("data.txt").run {
    if (exists()) {
        readText()
    } else {
        createNewFile()
        ""
    }
}
```

---

## Practical Examples

### Example 1: Database Query

```kotlin
val users = database.run {
    connect()
    val query = "SELECT * FROM users WHERE active = true"
    executeQuery(query)
    mapToUsers(resultSet)  // Returned
}
```

### Example 2: Configuration

```kotlin
val config = Config().run {
    setHost("localhost")
    setPort(8080)
    setTimeout(30)
    validate()  // Returns Boolean
}

if (config) {
    startServer()
}
```

### Example 3: Null Safety

```kotlin
val userInfo = user?.run {
    "Name: $name\nAge: $age\nEmail: $email"
} ?: "User not found"
```

### Example 4: Multiple Transformations

```kotlin
val processed = data
    .filter { it.isValid }
    .run {
        // 'this' is the filtered list
        if (isEmpty()) {
            emptyList()
        } else {
            map { it.process() }
        }
    }
```

### Example 5: Resource Handling

```kotlin
val content = File("data.txt").run {
    if (exists()) {
        readText()
    } else {
        createNewFile()
        ""
    }
}
```

---

## Распространенные Паттерны

### Паттерн 1: Ограниченные Вычисления

```kotlin
val result = run {
    val a = computeA()
    val b = computeB()
    val c = computeC()
    a + b + c  // Переменные в области видимости, возврат суммы
}
```

### Паттерн 2: Условные Операции

```kotlin
val value = obj.run {
    when (type) {
        Type.A -> processAsA()
        Type.B -> processAsB()
        else -> processDefault()
    }
}
```

### Паттерн 3: Паттерн Builder

```kotlin
val request = HttpRequest().run {
    url = "https://api.example.com"
    method = "POST"
    headers["Content-Type"] = "application/json"
    body = jsonBody
    build()  // Возвращает собранный запрос
}
```

---

## Common Patterns

### Pattern 1: Scoped Computations

```kotlin
val result = run {
    val a = computeA()
    val b = computeB()
    val c = computeC()
    a + b + c  // Variables are scoped, return sum
}
```

### Pattern 2: Conditional Operations

```kotlin
val value = obj.run {
    when (type) {
        Type.A -> processAsA()
        Type.B -> processAsB()
        else -> processDefault()
    }
}
```

### Pattern 3: Builder Pattern

```kotlin
val request = HttpRequest().run {
    url = "https://api.example.com"
    method = "POST"
    headers["Content-Type"] = "application/json"
    body = jsonBody
    build()  // Returns built request
}
```

---

## Когда Использовать Run

**Используйте `run` когда:**
- Нужно выполнить блок и вернуть результат
- Работаете с контекстом `this` (а не `it`)
- Выполняете трансформации
- Нужна null-безопасность с `?.run`
- Нужно ограничить область видимости промежуточных переменных

**Избегайте `run` когда:**
- Хотите вернуть сам объект (используйте `apply`)
- Нужен явный параметр (используйте `let`)
- Трансформация не нужна (используйте `also` для побочных эффектов)

---

## When to Use Run

Use `run` when:
- You need to execute a block and return its result.
- You work with `this` as the context.
- You perform transformations and want the computed value.
- You need null-safety with `?.run`.
- You want to limit the scope of temporary variables.

Avoid `run` when:
- You want to return the receiver object itself (`apply`).
- You want an explicit parameter (`let`).
- You only need side effects (`also`).

---

## Резюме

**Оператор `run`:**
- Исполняет лямбда-блок
- Возвращает результат лямбды (последнее выражение)
- Контекстный объект доступен как `this`
- Может вызываться как extension (`obj.run`) или автономно (`run`)

**Ключевые характеристики:**
- Ссылка на объект: `this`
- Возвращаемое значение: Результат лямбды
- Null-безопасность: Да (`?.run`)

**Основные сценарии применения:**
- Вычисление и возврат значения
- Трансформация объекта
- Ограниченные вычисления
- Цепочки с null-безопасностью

**Сравнение:**
- `run`: Возвращает результат, использует `this`
- `let`: Возвращает результат, использует `it`
- `apply`: Возвращает объект, использует `this`
- `also`: Возвращает объект, использует `it`
- `with`: Возвращает результат, использует `this` (не extension)

---

## Summary

The `run` function:
- Executes a lambda block.
- Returns the lambda result (last expression).
- Uses `this` as the context object.
- Can be called as an extension (`obj.run`) or as a top-level `run`.

Key properties:
- Object reference: `this`.
- Return value: lambda result.
- Null-safety: supported via `?.run`.

Typical use cases:
- Compute and return values.
- Transform objects.
- Scoped computations.
- Null-safe chains.

Compared to other scope functions:
- `run`: returns result, uses `this`.
- `let`: returns result, uses `it`.
- `apply`: returns receiver, uses `this`.
- `also`: returns receiver, uses `it`.
- `with`: returns result, uses `this` (not an extension).

---

## Дополнительные Вопросы (RU)

- В чем разница между `run` и другими scope-функциями (`let`, `apply`, `also`, `with`)?
- Когда вы бы использовали `run` на практике?
- Какие распространенные ошибки при использовании `run`?

## Follow-ups

- What are the key differences between `run` and other scope functions (`let`, `apply`, `also`, `with`)?
- When would you use `run` in practice?
- What are common pitfalls when using `run`?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-sealed-when-exhaustive--kotlin--medium]]
- [[q-compose-side-effects-coroutines--kotlin--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]