---
id: kotlin-229
title: "Kotlin Extension Functions Advanced"
aliases: ["Advanced Extension Functions", "Kotlin Extension Functions Advanced"]
topic: kotlin
subtopics: [dsl, extensions, generics]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en]
status: draft
moc: moc-kotlin
related: [q-crossinline-keyword--kotlin--medium, q-kotlin-java-primitives--programming-languages--medium, q-object-singleton-companion--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/hard, dsl, extensions, generics, kotlin, receivers]
date created: Tuesday, November 25th 2025, 12:37:51 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Question (EN)

> Implement extension functions with receivers, generic extensions, and nullable receivers. Understand resolution and scope.

---

## Answer (EN)

Extension functions add functionality to existing classes without modifying them. Advanced usage involves receiver function types, generics, nullability, operator overloads, and DSL-style builders.

### Extension Function Basics

```kotlin
// Basic extension (simplified example, not production-ready email validation)
fun String.isEmail() = contains('@') && contains('.')

// Generic extension using a receiver-lambda
fun <T> T.applyIf(condition: Boolean, block: T.() -> T): T {
    return if (condition) block() else this
}

// Usage
"text".applyIf(true) {
    uppercase()
}
```

### Generic Extensions

```kotlin
// Generic collection extension
// Caller must ensure list has at least 2 elements; otherwise IndexOutOfBoundsException
fun <T> List<T>.second(): T = this[1]

// Generic with constraint
fun <T : Comparable<T>> List<T>.isSorted(): Boolean {
    return zipWithNext().all { (a, b) -> a <= b }
}

// Multiple type parameters
fun <K, V> Map<K, V>.getOrThrow(key: K): V {
    return this[key] ?: throw NoSuchElementException("Key $key not found")
}

// Reified type parameters
inline fun <reified T> Any?.asOrNull(): T? {
    return this as? T
}

// Reified example using a different name to avoid shadowing stdlib filterIsInstance
inline fun <reified T> List<*>.filterAsType(): List<T> {
    return this.filterIsInstance<T>()
}
```

### Nullable Receivers

```kotlin
// Extension on nullable type
fun String?.orEmpty(): String = this ?: ""

fun <T> T?.orDefault(default: T): T = this ?: default

// Safe call on nullable
fun CharSequence?.isNullOrBlank(): Boolean {
    return this == null || this.isBlank()
}

// Usage
val text: String? = null
println(text.orEmpty())  // "" instead of null
```

### Extension Functions with Receivers

```kotlin
// Function with receiver and fluent API
fun StringBuilder.appendLine(value: String): StringBuilder = apply {
    append(value)
    append("\n")
}

// Generic configure pattern using receiver-lambda
fun <T> T.configure(block: T.() -> Unit): T {
    block()
    return this
}

// Usage
class Config {
    var host: String = ""
    var port: Int = 0
}

val config = Config().configure {
    host = "localhost"
    port = 8080
}
```

### Extension Properties

```kotlin
val String.lastChar: Char
    get() = this[length - 1]

val <T> List<T>.secondToLast: T
    get() = this[size - 2]

// Mutable extension property backed by the underlying list
var <T> MutableList<T>.lastItem: T
    get() = last()
    set(value) {
        if (isNotEmpty()) this[lastIndex] = value
    }
```

Note: Extension properties do not introduce real backing fields; they are syntax sugar for functions.

### Resolution and Scope

```kotlin
// Member extension defined inside Example
class Example {
    fun String.memberExtension() = "member"
}

// Top-level extension with the same name but without additional receiver
fun String.memberExtension() = "top-level"

fun main() {
    val example = Example()
    with(example) {
        // Here the implicit receiver is Example, and the extension receiver is String.
        // The member extension inside Example is in scope and is chosen over the top-level.
        "".memberExtension()  // "member"
    }
}
```

If both a member function and an extension are applicable, the member always wins. When multiple extensions are in scope, normal overload resolution and import priority rules apply.

### Operator Extensions

```kotlin
// Arithmetic operators
operator fun Int.times(str: String): String = str.repeat(this)

// Usage: 3 * "abc" == "abcabcabc"

// Comparison
class Version(val number: Int)

operator fun Version.compareTo(other: Version): Int {
    return this.number.compareTo(other.number)
}

// Indexed access for ranges (caller must ensure indices are valid)
operator fun <T> List<T>.get(range: IntRange): List<T> {
    return subList(range.first, range.last + 1)
}

// Usage: list[0..2]
```

### DSL-Style Extensions

```kotlin
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun tag(name: String, block: HtmlBuilder.() -> Unit) {
        elements.add("<$name>")
        this.block()
        elements.add("</$name>")
    }

    fun text(value: String) {
        elements.add(value)
    }

    fun build(): String = elements.joinToString("")
}

fun html(block: HtmlBuilder.() -> Unit): String {
    return HtmlBuilder().apply(block).build()
}

// Usage
val page = html {
    tag("body") {
        tag("h1") {
            text("Title")
        }
    }
}
```

This is a minimal example of a DSL-style builder using extension function receivers; production implementations typically use nested builders for proper DOM structure.

### Context Receivers (Experimental)

```kotlin
// Requires Kotlin with context receivers enabled (e.g., Kotlin 2.x with proper language flags)

interface Logger {
    fun log(message: String)
}

interface Transaction {
    fun save(order: Order)
    fun commit()
}

class Order(val id: String)

context(Logger, Transaction)
fun processOrder(order: Order) {
    log("Processing order ${order.id}")
    save(order)
    commit()
}
```

Context receivers generalize the idea of multiple receivers for extensions/DSLs.

### Best Practices

1. Keep extensions focused: single responsibility per function.
2. Name clearly to avoid ambiguity with existing members and stdlib extensions.
3. Use generics and reified parameters for reusable, type-safe patterns.
4. Handle nullable receivers when it meaningfully improves call-site safety.
5. Understand and document resolution behavior when overloading or shadowing.
6. Prefer member functions for core, domain behavior you control.
7. Use extension properties sparingly; remember they do not add state.
8. Group related extensions in the same file or package for discoverability.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-crossinline-keyword--kotlin--medium]]
- [[q-object-singleton-companion--kotlin--medium]]
- [[q-kotlin-java-primitives--kotlin--medium]]
