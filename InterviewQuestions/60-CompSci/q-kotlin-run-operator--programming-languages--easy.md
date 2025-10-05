---
tags:
  - kotlin
  - scope-functions
  - run
  - let
  - also
  - apply
  - with
  - easy_kotlin
  - programming-languages
difficulty: easy
---

# Какой оператор в Kotlin исполняет блок кода и возвращает его значение?

**English**: Which operator in Kotlin executes a block of code and returns its value?

## Answer

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

✅ **Use `run` when:**
- You need to execute a block and return result
- Working with `this` context (not `it`)
- Performing transformations
- Null safety with `?.run`
- Scoping intermediate variables

❌ **Avoid `run` when:**
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

## Ответ

run

