---
id: 20251003141217
title: Regular vs extension method / Обычный и extension метод
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, extension-functions, functions]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1435
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-extensions

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, extension-functions, functions, static-methods, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between a regular method and an extension method in Kotlin

# Вопрос (RU)
> В чём отличие обычного метода от extension метода в Kotlin

---

## Answer (EN)

### Regular Method (Member Function)

**Defined inside class**, has direct access to private members:

```kotlin
class User(val name: String, private val password: String) {
    // Regular method (member function)
    fun validatePassword(input: String): Boolean {
        return password == input  // Can access private password
    }

    fun greet() {
        println("Hello, $name!")
    }
}

val user = User("John", "secret123")
user.greet()  // Calls member function
user.validatePassword("secret123")  // true
```

**Characteristics:**
- Part of class definition
- Can access private/protected members
- Can be overridden in subclasses
- Dispatched virtually (polymorphic)
- Modifies class bytecode

### Extension Function

**Defined outside class**, looks like member but is actually static:

```kotlin
// Extension function (defined outside class)
fun User.displayInfo() {
    println("User: $name")
    // println(password)  // ERROR: Cannot access private members!
}

// Can extend classes you don't own
fun String.addQuotes(): String {
    return "\"$this\""
}

val user = User("John", "secret123")
user.displayInfo()  // Looks like member call

val text = "Hello"
val quoted = text.addQuotes()  // "Hello"
```

**Characteristics:**
- Defined outside class
- Cannot access private/protected members
- Cannot be overridden (not virtual)
- Resolved statically
- Does NOT modify class bytecode

### How Extension Functions Work

**Under the hood:**

```kotlin
// Kotlin extension
fun String.reverse(): String {
    return this.reversed()
}

"hello".reverse()

// Compiles to static method in Java:
public static String reverse(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Called as:
StringExtensionsKt.reverse("hello")
```

**Key point:** Extension is **syntactic sugar** for static method calls!

### Comparison

| Aspect | Regular Method | Extension Function |
|--------|---------------|-------------------|
| **Location** | Inside class | Outside class |
| **Access** | Private members | Public members only |
| **Virtual** | Yes (polymorphic) | No (static) |
| **Override** | Can override | Cannot override |
| **Modifies class** | Yes | No |
| **Bytecode** | Method in class | Static method |
| **Syntax** | `obj.method()` | `obj.extension()` (but static) |

### Access to Members

```kotlin
class User(val name: String, private val age: Int) {
    // Regular method - can access private
    fun isAdult(): Boolean {
        return age >= 18  // OK
    }
}

// Extension - cannot access private
fun User.printAge() {
    println(name)  // OK (public)
    // println(age)  // ERROR: age is private!
}
```

### Polymorphism

**Member functions are virtual:**

```kotlin
open class Animal {
    open fun sound() = "Some sound"
}

class Dog : Animal() {
    override fun sound() = "Woof"  // Override
}

val animal: Animal = Dog()
animal.sound()  // "Woof" (polymorphic call)
```

**Extension functions are NOT virtual:**

```kotlin
open class Animal

class Dog : Animal()

fun Animal.sound() = "Some sound"
fun Dog.sound() = "Woof"

val animal: Animal = Dog()
animal.sound()  // "Some sound" (NOT "Woof"!)
// Resolved based on declared type (Animal), not actual type (Dog)
```

### Member Takes Precedence

**If both exist, member wins:**

```kotlin
class MyClass {
    fun foo() {
        println("Member")
    }
}

fun MyClass.foo() {  // Extension with same name
    println("Extension")
}

MyClass().foo()  // Prints: "Member" (not "Extension")
```

### Use Cases

**Regular methods when:**
- Need access to private state
- Want polymorphism/overriding
- Core functionality of the class
- You control the class

**Extension functions when:**
- Extending classes you don't own (String, List, etc.)
- Utility functions that don't need private access
- Keeping class focused (separate concerns)
- Creating DSLs

### Real-World Examples

**Regular methods (core functionality):**
```kotlin
class BankAccount(private var balance: Double) {
    // Core operations need private access
    fun deposit(amount: Double) {
        balance += amount
    }

    fun withdraw(amount: Double): Boolean {
        return if (balance >= amount) {
            balance -= amount
            true
        } else {
            false
        }
    }
}
```

**Extension functions (utilities):**
```kotlin
// Extending String (don't own this class)
fun String.isValidEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

// Extending Context (Android)
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// Extending List
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}
```

### Benefits of Extensions

**1. No class modification:**
```kotlin
// Can't modify String class, but can add functionality
fun String.camelToSnakeCase(): String {
    return this.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
}

"camelCase".camelToSnakeCase()  // "camel_case"
```

**2. Cleaner API:**
```kotlin
// Before: static utility
StringUtils.capitalize(text)
StringUtils.reverse(text)

// After: extensions
text.capitalize()
text.reverse()
```

**3. Scope control:**
```kotlin
// Extension only available in specific context
class Config {
    fun String.parseConfig(): Map<String, String> {
        // Only available inside Config class
    }
}
```

### Summary

**Extension function:**
- Looks like it's added to the class
- Actually a static function
- Provides syntactic sugar
- Doesn't modify class bytecode
- Cannot access private members
- Not virtual/polymorphic

**Regular method:**
- Actual member of class
- Can access private state
- Virtual/polymorphic
- Can be overridden
- Part of class bytecode

## Ответ (RU)

Extension-функция выглядит как будто добавлена в класс, но на самом деле это статическая функция, которой не требуется менять сам класс. Она даёт синтаксический сахар, не добавляя нового в байткод класса

---

## Follow-ups
- Can extensions be overridden?
- How to call extension from Java?
- What are extension properties?

## References
- [[c-kotlin-extensions]]
- [[moc-kotlin]]

## Related Questions
- [[q-extensions-concept--programming-languages--easy]]
- [[q-kotlin-extensions-basics--programming-languages--easy]]
