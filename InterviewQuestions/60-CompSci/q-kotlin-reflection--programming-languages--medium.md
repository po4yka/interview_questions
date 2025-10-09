---
tags:
  - kotlin
  - kotlin-reflect
  - metaprogramming
  - programming-languages
  - reflection
  - runtime
difficulty: medium
status: reviewed
---

# Что такое рефлексия?

**English**: What is reflection?

## Answer

**Reflection** is a mechanism that allows a program to **inspect and modify its own structure** (classes, methods, fields) at runtime.

It allows you to:
- Call private methods
- Create class instances by name
- Access/modify private fields
- Inspect annotations

This is a powerful but **unsafe and performance-heavy** tool.

**Setup:**

```kotlin
// build.gradle.kts
dependencies {
    implementation(kotlin("reflect"))
}
```

**Key Uses:**

**1. Get Class Information:**

```kotlin
class Person(val name: String, var age: Int) {
    private fun secret() = "Secret method"
}

val person = Person("Alice", 30)

// Get class
val kClass = person::class
println(kClass.simpleName)  // "Person"
println(kClass.qualifiedName)  // "com.example.Person"

// Get properties
kClass.memberProperties.forEach { prop ->
    println("${prop.name}: ${prop.get(person)}")
}
// Output:
// name: Alice
// age: 30
```

**2. Create Instances Dynamically:**

```kotlin
// Get class by name
val kClass = Class.forName("com.example.Person").kotlin

// Get constructor
val constructor = kClass.constructors.first()

// Create instance
val person = constructor.call("Bob", 25)
```

**3. Access Private Members:**

```kotlin
class User(private val password: String) {
    private fun getSecret() = "Secret: $password"
}

val user = User("12345")

// Access private property
val passwordProp = User::class.memberProperties
    .find { it.name == "password" }
passwordProp?.isAccessible = true
val password = passwordProp?.get(user)
println(password)  // "12345"

// Call private method
val secretMethod = User::class.memberFunctions
    .find { it.name == "getSecret" }
secretMethod?.isAccessible = true
val secret = secretMethod?.call(user)
println(secret)  // "Secret: 12345"
```

**4. Inspect Annotations:**

```kotlin
@Target(AnnotationTarget.CLASS)
annotation class Entity(val tableName: String)

@Target(AnnotationTarget.PROPERTY)
annotation class Column(val name: String)

@Entity("users")
data class User(
    @Column("user_id") val id: Int,
    @Column("user_name") val name: String
)

// Get class annotation
val entity = User::class.annotations
    .filterIsInstance<Entity>()
    .firstOrNull()
println(entity?.tableName)  // "users"

// Get property annotations
User::class.memberProperties.forEach { prop ->
    val column = prop.annotations
        .filterIsInstance<Column>()
        .firstOrNull()
    println("${prop.name} -> ${column?.name}")
}
// Output:
// id -> user_id
// name -> user_name
```

**5. Invoke Functions Dynamically:**

```kotlin
class Calculator {
    fun add(a: Int, b: Int) = a + b
    fun multiply(a: Int, b: Int) = a * b
}

val calc = Calculator()

// Find function by name
val addFunc = Calculator::class.memberFunctions
    .find { it.name == "add" }

// Call it
val result = addFunc?.call(calc, 5, 3)
println(result)  // 8
```

**6. Modify Properties:**

```kotlin
class Settings {
    var theme: String = "light"
}

val settings = Settings()

// Get property reference
val themeProp = Settings::class.memberProperties
    .find { it.name == "theme" } as? KMutableProperty<*>

// Modify it
themeProp?.setter?.call(settings, "dark")
println(settings.theme)  // "dark"
```

**Common Use Cases:**

**Serialization/Deserialization:**
```kotlin
fun <T : Any> toJson(obj: T): String {
    val kClass = obj::class
    val props = kClass.memberProperties

    val json = props.joinToString(", ") { prop ->
        """"${prop.name}": "${prop.get(obj)}""""
    }

    return "{$json}"
}

data class User(val name: String, val age: Int)

val user = User("Alice", 30)
println(toJson(user))  // {"name": "Alice", "age": "30"}
```

**Dependency Injection:**
```kotlin
class UserService
class UserRepository

fun <T : Any> inject(kClass: KClass<T>): T {
    // Find constructor
    val constructor = kClass.primaryConstructor!!

    // Get parameter types
    val params = constructor.parameters.map { param ->
        inject(param.type.classifier as KClass<*>)
    }

    // Create instance
    return constructor.call(*params.toTypedArray())
}

// Usage
val service = inject(UserService::class)
```

**Testing - Access Private Members:**
```kotlin
class ViewModel {
    private val repository = UserRepository()

    private fun loadData() {
        // Load data
    }
}

// In test
@Test
fun testLoadData() {
    val viewModel = ViewModel()

    val loadMethod = ViewModel::class.memberFunctions
        .find { it.name == "loadData" }
    loadMethod?.isAccessible = true
    loadMethod?.call(viewModel)

    // Assert results
}
```

**Performance Impact:**

```kotlin
// Direct access - FAST
val name = person.name

// Reflection - SLOW (10-100x slower)
val nameProp = Person::class.memberProperties.find { it.name == "name" }
val name = nameProp?.get(person)
```

**Pros & Cons:**

| Pros - | Cons - |
|---------|---------|
| Dynamic behavior | Performance overhead |
| Generic frameworks | Type safety lost |
| Powerful | Complex code |
| Flexibility | Security risks |

**When to Use:**

- **Use reflection for:**
- Serialization libraries (Gson, Jackson)
- Dependency injection (Dagger, Koin)
- Testing frameworks
- ORM libraries
- Generic utilities

- **Avoid reflection for:**
- Performance-critical code
- Simple tasks (use direct access)
- Production code (use compile-time alternatives)
- Security-sensitive operations

**Summary:**

- **Reflection**: Inspect/modify code at runtime
- **Powerful**: Access private members, create instances dynamically
- **Costly**: Performance overhead, type safety loss
- **Use cases**: Serialization, DI, testing, ORMs
- **Dependency**: `kotlin-reflect` library required

## Ответ

Рефлексия — это механизм, позволяющий программе исследовать и изменять свою структуру (классы, методы, поля) во время выполнения. Он позволяет вызывать приватные методы, создавать экземпляры классов по имени и т.д. Это мощный, но небезопасный и затратный по производительности инструмент.

