---
tags:
  - extension-functions
  - extensions
  - kotlin
  - programming-languages
difficulty: easy
status: reviewed
---

# Что такое Extensions?

**English**: What are Extensions?

## Answer

**Extensions** in Kotlin allow you to **add new functionality to existing classes** without modifying their source code or using inheritance.

### Extension Functions

**Add functions to existing types:**

```kotlin
// Extend String class with new function
fun String.addExclamation(): String {
    return this + "!"
}

// Usage
val greeting = "Hello"
println(greeting.addExclamation())  // "Hello!"

// Can also use directly
println("Kotlin".addExclamation())  // "Kotlin!"
```

### Extension Properties

**Add properties to existing types:**

```kotlin
// Add property to Int
val Int.isEven: Boolean
    get() = this % 2 == 0

// Usage
println(4.isEven)   // true
println(5.isEven)   // false
```

### Real-World Examples

**1. String utilities:**
```kotlin
fun String.isEmailValid(): Boolean {
    return this.contains("@") && this.contains(".")
}

val email = "user@example.com"
if (email.isEmailValid()) {
    println("Valid email")
}
```

**2. Collection utilities:**
```kotlin
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}

val list = listOf(1, 2, 3)
println(list.secondOrNull())  // 2
```

**3. Context extensions:**
```kotlin
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        showToast("Welcome!")  // Clean syntax
    }
}
```

### How Extensions Work

**Under the hood:**
```kotlin
// Kotlin extension
fun String.reverse(): String {
    return this.reversed()
}

// Compiles to static method in Java
public static String reverse(String receiver) {
    return new StringBuilder(receiver).reverse().toString();
}

// Usage: StringExtensionsKt.reverse("hello")
```

**Key points:**
- Not actually modifying the class
- Static functions in bytecode
- `this` refers to receiver object
- Resolved statically (not polymorphic)

### Benefits

**1. No inheritance needed:**
```kotlin
// Can't modify String class or inherit from it
// But can add functionality via extension
fun String.isPalindrome() = this == this.reversed()
```

**2. Clean API:**
```kotlin
// Before: Utility class
StringUtils.capitalize(text)

// After: Extension
text.capitalize()
```

**3. Scope control:**
```kotlin
// Can limit extensions to specific scope
class MyClass {
    // Only available in MyClass
    private fun String.myExtension() = this.uppercase()
}
```

### Nullable Receiver Extensions

**Can extend nullable types:**

```kotlin
fun String?.orDefault(default: String = ""): String {
    return this ?: default
}

val text: String? = null
println(text.orDefault("N/A"))  // "N/A"

val text2: String? = "Hello"
println(text2.orDefault("N/A"))  // "Hello"
```

### Member vs Extension

**Member functions take precedence:**

```kotlin
class MyClass {
    fun foo() {
        println("Member")
    }
}

fun MyClass.foo() {  // Extension
    println("Extension")
}

MyClass().foo()  // Prints: "Member"
```

### Common Use Cases

**1. Android View extensions:**
```kotlin
fun View.visible() {
    visibility = View.VISIBLE
}

fun View.gone() {
    visibility = View.GONE
}

// Usage
textView.visible()
progressBar.gone()
```

**2. Type conversions:**
```kotlin
fun String.toIntOrDefault(default: Int = 0): Int {
    return this.toIntOrNull() ?: default
}

val number = "123".toIntOrDefault()  // 123
val invalid = "abc".toIntOrDefault() // 0
```

**3. Validation:**
```kotlin
fun String.isValidPassword(): Boolean {
    return this.length >= 8 &&
           this.any { it.isDigit() } &&
           this.any { it.isUpperCase() }
}
```

### Limitations

**Cannot:**
- Access private members of the class
- Override member functions
- Be virtual/polymorphic
- Change class structure

```kotlin
class MyClass {
    private val secret = "hidden"
}

fun MyClass.tryAccess() {
    // println(secret)  // Error: Cannot access private member
}
```

## Ответ

Термин 'Extensions' используется для обозначения функциональности, которая позволяет добавлять новые возможности к существующим классам без изменения их исходного кода.

