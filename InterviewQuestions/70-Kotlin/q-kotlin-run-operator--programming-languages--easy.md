---
id: 20251016-123551
title: "Kotlin Run Operator / Оператор run в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - also
  - apply
  - kotlin
  - let
  - programming-languages
  - run
  - scope-functions
  - with
---
# Какой оператор в Kotlin исполняет блок кода и возвращает его значение?

# Question (EN)
> Which operator in Kotlin executes a block of code and returns its value?

# Вопрос (RU)
> Какой оператор в Kotlin исполняет блок кода и возвращает его значение?

---

## Answer (EN)

The **`run`** operator (scope function) in Kotlin executes a block of code and returns its result value.

## Run Function

`run` is one of Kotlin's **scope functions** that:
- Executes a lambda block
- Returns the **result of the lambda** (last expression)
- Can be called on an object (`obj.run`) or standalone (`run`)

### Basic Syntax

```kotlin
// Extension function form
val result = obj.run {
    // this refers to obj
    // do something with obj
    someValue  // returned
}

// Standalone form
val result = run {
    // no implicit receiver
    val x = 10
    val y = 20
    x + y  // returned (30)
}
```

---

## Run Variants

### 1. Object.run (Extension Function)

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
- Context object: `this`
- Returns: Lambda result
- Use: Transform object and return result

### 2. run (Standalone Function)

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
- Use: Execute block and return result

---

## Comparison with Other Scope Functions

| Function | Object Reference | Return Value | Use Case |
|----------|-----------------|--------------|----------|
| **run** | `this` | Lambda result | Transform and return |
| **let** | `it` | Lambda result | Null checks, transform |
| **apply** | `this` | Context object | Configure object |
| **also** | `it` | Context object | Side effects |
| **with** | `this` | Lambda result | Multiple calls on object |

---

## Run Use Cases

### 1. Compute and Return Result

```kotlin
val result = user.run {
    val fullName = "$firstName $lastName"
    val age = calculateAge(birthDate)
    "$fullName ($age years old)"  // Returned
}
```

### 2. Null Safety with run

```kotlin
val length = str?.run {
    trim()
    uppercase()
    length  // Returned if str is not null
} ?: 0  // Default if str is null
```

### 3. Initialize and Configure

```kotlin
val db = Database().run {
    connect()
    migrate()
    this  // Return configured database
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

## Run vs Other Scope Functions

### run vs let

```kotlin
// run - uses 'this'
val result1 = user.run {
    println(name)  // Direct access
    age
}

// let - uses 'it'
val result2 = user.let {
    println(it.name)  // Must use 'it'
    it.age
}
```

**Use `run`** when:
- You want `this` instead of `it`
- Multiple property access without repeating `it`

**Use `let`** when:
- Null safety with `?.let`
- Want explicit parameter name

### run vs apply

```kotlin
// run - returns lambda result
val length = StringBuilder().run {
    append("Hello")
    append(" World")
    length  // Returns Int (length)
}

// apply - returns object itself
val builder = StringBuilder().apply {
    append("Hello")
    append(" World")
}  // Returns StringBuilder
```

**Use `run`** when:
- You want to return a computed value

**Use `apply`** when:
- You want to return the configured object

### run vs with

```kotlin
// run - extension function
val result1 = user.run {
    "$name is $age years old"
}

// with - regular function
val result2 = with(user) {
    "$name is $age years old"
}
```

**Use `run`** when:
- Object might be null (`user?.run`)
- Chaining operations

**Use `with`** when:
- Object is definitely not null
- Prefer function call syntax

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

### Example 5: Resource Management

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

## Common Patterns

### Pattern 1: Scoped Computation

```kotlin
val result = run {
    val a = computeA()
    val b = computeB()
    val c = computeC()
    a + b + c  // Scoped variables, return sum
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

## When to Use run

- **Use `run` when:**
- You need to execute a block and return result
- Working with `this` context (not `it`)
- Performing transformations
- Null safety with `?.run`
- Scoping intermediate variables

- **Avoid `run` when:**
- You want to return the object itself (use `apply`)
- You need explicit parameter (use `let`)
- No transformation needed (use `also` for side effects)

---

## Summary

**`run` operator:**
- Executes a lambda block
- Returns the **lambda result** (last expression)
- Context object available as `this`
- Can be called as extension (`obj.run`) or standalone (`run`)

**Key characteristics:**
- Object reference: `this`
- Return value: Lambda result
- Null-safe: Yes (`?.run`)

**Common use cases:**
- Compute and return value
- Transform object
- Scoped calculations
- Null safety chains

**Comparison:**
- `run`: Returns result, uses `this`
- `let`: Returns result, uses `it`
- `apply`: Returns object, uses `this`
- `also`: Returns object, uses `it`
- `with`: Returns result, uses `this` (not extension)

---

## Ответ (RU)

Оператор **`run`** (scope-функция) в Kotlin исполняет блок кода и возвращает результат его выполнения.

## Функция Run

`run` - одна из **scope-функций** Kotlin, которая:
- Исполняет лямбда-блок
- Возвращает **результат лямбды** (последнее выражение)
- Может вызываться на объекте (`obj.run`) или автономно (`run`)

### Базовый синтаксис

```kotlin
// Форма extension-функции
val result = obj.run {
    // this ссылается на obj
    // выполняем операции с obj
    someValue  // возвращается
}

// Автономная форма
val result = run {
    // нет неявного получателя
    val x = 10
    val y = 20
    x + y  // возвращается (30)
}
```

---

## Варианты использования Run

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

### 2. run (Автономная функция)

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

## Сравнение с другими Scope-функциями

| Функция | Ссылка на объект | Возвращаемое значение | Применение |
|---------|------------------|----------------------|------------|
| **run** | `this` | Результат лямбды | Трансформация и возврат |
| **let** | `it` | Результат лямбды | Проверка null, трансформация |
| **apply** | `this` | Контекстный объект | Конфигурация объекта |
| **also** | `it` | Контекстный объект | Побочные эффекты |
| **with** | `this` | Результат лямбды | Множественные вызовы на объекте |

---

## Примеры использования Run

### 1. Вычисление и возврат результата

```kotlin
val result = user.run {
    val fullName = "$firstName $lastName"
    val age = calculateAge(birthDate)
    "$fullName ($age years old)"  // Возвращается
}
```

### 2. Null-безопасность с run

```kotlin
val length = str?.run {
    trim()
    uppercase()
    length  // Возвращается, если str не null
} ?: 0  // Значение по умолчанию, если str null
```

### 3. Инициализация и конфигурация

```kotlin
val db = Database().run {
    connect()
    migrate()
    this  // Возвращаем сконфигурированную БД
}
```

### 4. Сложные вычисления

```kotlin
val price = product.run {
    val basePrice = this.basePrice
    val discount = this.discount
    val tax = (basePrice - discount) * 0.2
    basePrice - discount + tax  // Финальная цена
}
```

---

## Run vs другие Scope-функции

### run vs let

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

### run vs apply

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

### run vs with

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

## Практические примеры

### Пример 1: Запрос к базе данных

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

### Пример 4: Множественные трансформации

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

### Пример 5: Управление ресурсами

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

## Распространенные паттерны

### Паттерн 1: Ограниченные вычисления

```kotlin
val result = run {
    val a = computeA()
    val b = computeB()
    val c = computeC()
    a + b + c  // Переменные в области видимости, возврат суммы
}
```

### Паттерн 2: Условные операции

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

## Когда использовать run

- **Используйте `run` когда:**
- Нужно выполнить блок и вернуть результат
- Работаете с контекстом `this` (а не `it`)
- Выполняете трансформации
- Null-безопасность с `?.run`
- Ограничиваете область видимости промежуточных переменных

- **Избегайте `run` когда:**
- Хотите вернуть сам объект (используйте `apply`)
- Нужен явный параметр (используйте `let`)
- Трансформация не нужна (используйте `also` для побочных эффектов)

---

## Резюме

**Оператор `run`:**
- Исполняет лямбда-блок
- Возвращает **результат лямбды** (последнее выражение)
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

