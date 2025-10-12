---
topic: kotlin
tags:
  - kotlin
  - contracts
  - smart-casts
  - type-system
  - advanced
  - compiler
difficulty: hard
status: draft
---

# Kotlin Contracts and Smart Casts

# Question (EN)
> What are Kotlin contracts? How do they enable smart casts? Implement a custom contract for a validation function.

# Вопрос (RU)
> Что такое контракты Kotlin? Как они обеспечивают умные приведения типов (smart casts)? Реализуйте пользовательский контракт для функции валидации.

---

## Answer (EN)

**Kotlin Contracts** are an experimental feature that allows functions to declare guarantees about their behavior to the compiler, enabling better smart casts, null-safety, and optimization.

---

### What are Smart Casts?

Smart casts automatically cast types when the compiler can prove type safety:

```kotlin
fun printLength(obj: Any) {
    if (obj is String) {
        // Smart cast to String
        println(obj.length) // No need for (obj as String).length
    }
}

fun printUser(user: User?) {
    if (user != null) {
        // Smart cast to User (non-null)
        println(user.name) // No need for user?.name
    }
}
```

---

### Problem Without Contracts

Custom validation functions don't enable smart casts:

```kotlin
fun isNotNull(value: Any?): Boolean {
    return value != null
}

fun example(name: String?) {
    if (isNotNull(name)) {
        // ❌ Smart cast is impossible!
        // Compiler doesn't know isNotNull guarantees non-null
        println(name.length) // Error: Only safe calls are allowed
    }
}
```

---

### Solution: Contracts

Contracts tell the compiler about guarantees:

```kotlin
import kotlin.contracts.*

@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null
}

fun example(name: String?) {
    if (isNotNull(name)) {
        // ✅ Smart cast works!
        println(name.length) // name is smart-cast to String
    }
}
```

---

### Contract Types

**1. returns(value) implies (condition)**

Guarantees condition is true when function returns specific value:

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValid(user: User?): Boolean {
    contract {
        returns(true) implies (user != null)
    }
    return user != null && user.isActive
}

fun process(user: User?) {
    if (isValid(user)) {
        // user is smart-cast to User (non-null)
        println(user.name)
    }
}
```

**2. returns() implies (condition)**

Guarantees condition when function returns normally (doesn't throw):

```kotlin
@OptIn(ExperimentalContracts::class)
fun requireNotNull(value: Any?) {
    contract {
        returns() implies (value != null)
    }
    if (value == null) {
        throw IllegalArgumentException("Value must not be null")
    }
}

fun example(name: String?) {
    requireNotNull(name)
    // After this point, name is smart-cast to String
    println(name.length)
}
```

**3. returnsNotNull() implies (condition)**

Guarantees return value is not null when condition is true:

```kotlin
@OptIn(ExperimentalContracts::class)
fun String?.ifNotEmpty(): String? {
    contract {
        returnsNotNull() implies (this@ifNotEmpty != null)
    }
    return if (this != null && this.isNotEmpty()) this else null
}

fun example(text: String?) {
    val result = text.ifNotEmpty()
    if (result != null) {
        // result is smart-cast to String
        println(result.length)
    }
}
```

**4. callsInPlace(lambda, InvocationKind)**

Guarantees lambda is called specific number of times:

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T> myRun(block: () -> T): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}

fun example() {
    val name: String

    myRun {
        name = "John" // ✅ Compiler knows name is initialized
    }

    println(name) // ✅ No need for lateinit or nullable
}
```

---

### InvocationKind Options

```kotlin
// Called exactly once
callsInPlace(block, InvocationKind.EXACTLY_ONCE)

// Called at most once (0 or 1 times)
callsInPlace(block, InvocationKind.AT_MOST_ONCE)

// Called at least once (1 or more times)
callsInPlace(block, InvocationKind.AT_LEAST_ONCE)

// Unknown number of times
callsInPlace(block, InvocationKind.UNKNOWN)
```

---

### Standard Library Contracts

**require() and check():**

```kotlin
// Standard library implementation
@OptIn(ExperimentalContracts::class)
public inline fun require(value: Boolean) {
    contract {
        returns() implies value
    }
    if (!value) {
        throw IllegalArgumentException("Failed requirement.")
    }
}

// Usage
fun divide(a: Int, b: Int): Int {
    require(b != 0) // Compiler knows b != 0 after this

    return a / b // No warning about division by zero
}
```

**isNullOrEmpty():**

```kotlin
@OptIn(ExperimentalContracts::class)
public inline fun CharSequence?.isNullOrEmpty(): Boolean {
    contract {
        returns(false) implies (this@isNullOrEmpty != null)
    }
    return this == null || this.length == 0
}

// Usage
fun example(text: String?) {
    if (!text.isNullOrEmpty()) {
        // text is smart-cast to String
        println(text.length)
    }
}
```

**let, run, with, apply, also:**

```kotlin
@OptIn(ExperimentalContracts::class)
public inline fun <T, R> T.let(block: (T) -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block(this)
}

// Usage
fun example() {
    val name: String

    "John".let {
        name = it // ✅ Compiler knows it's initialized
    }

    println(name) // ✅ Definite initialization
}
```

---

### Custom Validation Contracts

**Email validation:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValidEmail(email: String?): Boolean {
    contract {
        returns(true) implies (email != null)
    }
    return email != null && email.matches(Regex("^[A-Za-z0-9+_.-]+@(.+)$"))
}

fun sendEmail(email: String?) {
    if (isValidEmail(email)) {
        // email is smart-cast to String
        println("Sending to ${email.lowercase()}")
    }
}
```

**Range validation:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun isInRange(value: Int?, min: Int, max: Int): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value in min..max
}

fun processAge(age: Int?) {
    if (isInRange(age, 0, 120)) {
        // age is smart-cast to Int
        println("Valid age: $age")
    }
}
```

**Collection validation:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun <T> isNotNullOrEmpty(collection: Collection<T>?): Boolean {
    contract {
        returns(true) implies (collection != null)
    }
    return collection != null && collection.isNotEmpty()
}

fun processItems(items: List<String>?) {
    if (isNotNullOrEmpty(items)) {
        // items is smart-cast to List<String>
        items.forEach { println(it) }
    }
}
```

---

### Advanced: Multiple Implications

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValidUser(user: User?, requireActive: Boolean): Boolean {
    contract {
        returns(true) implies (user != null)
        returns(true) implies (requireActive implies user.isActive)
    }
    return user != null && (!requireActive || user.isActive)
}
```

---

### Real-World Example: Form Validation

```kotlin
data class RegistrationForm(
    val email: String?,
    val password: String?,
    val age: Int?,
    val terms: Boolean
)

@OptIn(ExperimentalContracts::class)
fun isValidEmail(email: String?): Boolean {
    contract {
        returns(true) implies (email != null)
    }
    return email != null && email.contains("@")
}

@OptIn(ExperimentalContracts::class)
fun isValidPassword(password: String?): Boolean {
    contract {
        returns(true) implies (password != null)
    }
    return password != null && password.length >= 8
}

@OptIn(ExperimentalContracts::class)
fun isValidAge(age: Int?): Boolean {
    contract {
        returns(true) implies (age != null)
    }
    return age != null && age in 13..120
}

@OptIn(ExperimentalContracts::class)
fun isValidForm(form: RegistrationForm): Boolean {
    contract {
        returns(true) implies (form.email != null)
        returns(true) implies (form.password != null)
        returns(true) implies (form.age != null)
    }

    return isValidEmail(form.email) &&
        isValidPassword(form.password) &&
        isValidAge(form.age) &&
        form.terms
}

fun register(form: RegistrationForm) {
    if (isValidForm(form)) {
        // All fields are smart-cast to non-null
        val user = User(
            email = form.email,      // String (smart-cast)
            password = form.password, // String (smart-cast)
            age = form.age           // Int (smart-cast)
        )

        saveUser(user)
    } else {
        showError("Invalid form")
    }
}
```

---

### Contract with callsInPlace

**Safe resource management:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T : AutoCloseable, R> T.safeUse(block: (T) -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return try {
        block(this)
    } finally {
        close()
    }
}

fun example() {
    val data: String

    FileInputStream("file.txt").safeUse { stream ->
        data = stream.readBytes().decodeToString()
        // Compiler knows data is initialized
    }

    println(data) // ✅ No error
}
```

**Initialization guarantee:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun initialize(block: () -> Unit) {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    block()
}

fun example() {
    val name: String

    initialize {
        name = "John"
    }

    // Compiler knows name is definitely initialized
    println(name)
}
```

---

### Limitations

**1. Contracts must be first statement:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract { // ✅ Must be first
        returns(true) implies (value != null)
    }
    println("Checking...") // Other code after
    return value != null
}
```

**2. Contract cannot depend on runtime values:**

```kotlin
// ❌ INVALID: Cannot use runtime value
@OptIn(ExperimentalContracts::class)
fun isValid(value: Int?, threshold: Int): Boolean {
    contract {
        returns(true) implies (value != null)
        // ❌ Cannot reference threshold
    }
    return value != null && value > threshold
}
```

**3. Contracts are not verified:**

```kotlin
// ⚠️ WARNING: Contract lies!
@OptIn(ExperimentalContracts::class)
fun alwaysFalse(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null) // Lie!
    }
    return false // Never returns true!
}

// This will cause bugs!
fun example(name: String?) {
    if (alwaysFalse(name)) {
        // Compiler thinks name is non-null, but it's not!
        println(name.length) // Potential NPE!
    }
}
```

---

### Best Practices

**1. Only use contracts when necessary:**

```kotlin
// ✅ DO: Contract needed for smart cast
@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null
}

// ❌ DON'T: Contract not needed
@OptIn(ExperimentalContracts::class)
fun add(a: Int, b: Int): Int {
    contract { } // Pointless
    return a + b
}
```

**2. Ensure contracts are truthful:**

```kotlin
// ✅ DO: Honest contract
@OptIn(ExperimentalContracts::class)
fun isPositive(value: Int?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value > 0 // Guarantees non-null
}

// ❌ DON'T: Lying contract
@OptIn(ExperimentalContracts::class)
fun isPositive(value: Int?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return true // LIES! Doesn't guarantee non-null
}
```

**3. Use for validation functions:**

```kotlin
// ✅ GOOD use cases
- isNotNull(value)
- isValidEmail(email)
- isInRange(value, min, max)
- require/check conditions
```

---

## Ответ (RU)

**Контракты Kotlin** — это экспериментальная функция, которая позволяет функциям объявлять гарантии о своем поведении компилятору, обеспечивая лучшие умные приведения типов, null-безопасность и оптимизацию.

### Что такое умные приведения типов?

Умные приведения автоматически преобразуют типы, когда компилятор может доказать безопасность типов.

### Проблема без контрактов

Пользовательские функции валидации не обеспечивают умные приведения. Компилятор не знает гарантий функции.

### Решение: Контракты

Контракты сообщают компилятору о гарантиях функции, используя синтаксис `contract { }`.

### Типы контрактов

1. **returns(value) implies (condition)** - гарантирует условие при возврате значения
2. **returns() implies (condition)** - гарантирует условие при нормальном возврате
3. **returnsNotNull()** - гарантирует не-null возврат
4. **callsInPlace(lambda, InvocationKind)** - гарантирует количество вызовов лямбды

### Ограничения

1. Контракты должны быть первым оператором
2. Контракт не может зависеть от runtime значений
3. Контракты не проверяются компилятором

### Лучшие практики

1. Используйте контракты только когда необходимо
2. Убедитесь, что контракты правдивы
3. Используйте для функций валидации

Контракты — мощный инструмент для улучшения безопасности типов и умных приведений в Kotlin.
