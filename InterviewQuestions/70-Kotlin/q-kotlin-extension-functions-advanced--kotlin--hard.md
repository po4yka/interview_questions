---
id: kotlin-229
title: "Kotlin Extension Functions Advanced / 1f403e3432383d43424b35 Extension Functions 32 Kotlin"
aliases: [Kotlin Extension Functions Advanced, 1f403e3432383d43424b35 Extension Functions 32 Kotlin]
topic: kotlin
subtopics: [dsl, extensions, generics]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-crossinline-keyword--kotlin--medium, q-kotlin-java-primitives--programming-languages--medium, q-object-singleton-companion--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/hard, dsl, extensions, generics, kotlin, receivers]
---

# Advanced Extension Functions

**English**: Implement extension functions with receivers, generic extensions, and nullable receivers. Understand resolution and scope.

**Russian**: 2035303b383743394235 extension functions 41 receivers, generic extensions 38 nullable receivers. 1f3e3d383c30394235 rules of resolution 38 scope.

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

## 1e42323542 (RU)

Extension functions (44433d3a463838-403041483840353d384f) 343e3130323b4f4e42 44433d3a46383e3d303b4c3d3e41424c 41434935414232434e49383c 3a3b304141303c 313537 3845 38373c353d353d384f. 1f403e3432383d43423e35 38413f3e3b4c373e32303d3835 323a3b4e47303542 receiver-lambda, generics, nullable-receivers, operator overloads 38 DSL-4142383b4c 3f3e4142403e353d384f.

1a3b4e4735324b35 38343538 38 3f40383c35404b:

- 1130373e324b35 extension-44433d3a463838:
  - `fun String.isEmail() = contains('@') && contains('.')` (433f403e49353d3d4b39 3f40383c3540).
  - Generic extension 41 receiver-lambda: `fun <T> T.applyIf(condition: Boolean, block: T.() -> T): T`.

- Generic extensions:
  - `fun <T> List<T>.second(): T = this[1]` 3f4035343f3e3b3033303542, 47423e 4d3b353c353d423e32 3d35 3c353d3535 2.
  - `fun <T : Comparable<T>> List<T>.isSorted(): Boolean = zipWithNext().all { (a, b) -> a <= b }`.
  - `fun <K, V> Map<K, V>.getOrThrow(key: K): V` 31403e41303542 `NoSuchElementException`, 35413b38 3a3b4e47 3d35 3d303934353d.
  - Reified: `inline fun <reified T> Any?.asOrNull(): T? = this as? T` 38 `inline fun <reified T> List<*>.filterAsType(): List<T> = filterIsInstance<T>()`.

- Nullable receivers:
  - `fun String?.orEmpty(): String = this ?: ""`.
  - `fun <T> T?.orDefault(default: T): T = this ?: default`.
  - `fun CharSequence?.isNullOrBlank(): Boolean = this == null || this.isBlank()`.

- Extension-44433d3a463838 41 receiver:
  - Fluent API: `fun StringBuilder.appendLine(value: String): StringBuilder = apply { ... }`.
  - `fun <T> T.configure(block: T.() -> Unit): T` 343b4f 3d304142403e393a38 `Config` 38 3f3e343e313d4b45 3e314a353a423e32.

- Extension properties:
  - `val String.lastChar: Char get() = this[length - 1]`.
  - `val <T> List<T>.secondToLast: T get() = this[size - 2]`.
  - `var <T> MutableList<T>.lastItem: T` (473842303542/ 37303f38414b32303542 3f3e413b35343d3839 4d3b353c353d42; 3d35 343e3130323b4f3542 3d3e324b45 3f3e3b3539).

- Resolution & scope:
  - 15413b38 343e4142433f3d4b 38 member-44433d3a46384f, 38 extension 41 413e323c354142383c3e39 4138333d304243403e39, 324b313840303542414f member.
  - 123b3e36353d3d4b35 receivers (`with`, `apply`, context receivers) 323b384f4e42 3d30 324b313e40 extension.

- Operator extensions:
  - `operator fun Int.times(str: String): String = str.repeat(this)`.
  - `class Version(val number: Int)` + `operator fun Version.compareTo(other: Version): Int` 343b4f 414030323d353d384f.
  - `operator fun <T> List<T>.get(range: IntRange): List<T> = subList(range.first, range.last + 1)` (3e363834303542 3a3e4040353a423d4b35 383d34353a414b).

- DSL-4142383b4c:
  - `HtmlBuilder` 41 `fun html(block: HtmlBuilder.() -> Unit): String` 38 `tag("body") { ... }` 383b3b4e4142403840433542 DSL 3d30 31303735 receiver-lambda.

- Context receivers (experimental / Kotlin 2.x):
  - `context(Logger, Transaction) fun processOrder(order: Order)` 3f3e3a30374b32303542, 3a303a 3d35413a3e3b4c3a3e receivers 3c3e334342 314b424c 343e4142433f3d4b 323d43424038 44433d3a463838.

### 1b4347483835 1f40303a42383a38

1. 14354036384235 extension-44433d3a463838 41443e3a434138403e32303d3d4b3c38 (3e343d30 3e42323542414232353d3d3e41424c).
2. 2735423a3e 383c353d43394235, 47423e314b 3d35 323d3e4138424c 3f4342303d384643 41 member-3c35423e34303c38 38 stdlib.
3. 18413f3e3b4c3743394235 generics 38 reified-3f3040303c3542404b 343b4f 433d3832354041303b4c3d4b45 4830313b3e3d3e32.
4. 1e3140303130424b3230394235 nullable-receivers, 3a3e333430 4d423e 433b434748303542 47384230353c3e41424c 38 3135373e3f30413d3e41424c.
5. 1f3e3d383c30394235 resolution rules (3a423e 324b3833404b32303542: member vs extension, 3a303a 4030313e42304e42 imports).
6. 18413f3e3b4c3743394235 member-44433d3a463838 343b4f 3130373e323e333e 343e3c353d3d3e333e API, 30 extensions 343b4f sugar 38 3a3e3d3a4035423d4b45 3a3539413e32.
7. 213e373d303d3d3e 38413f3e3b4c3743394235 extension properties: 3e3d38 3d35 343e3130323b4f4e42 413e41423e4f3d384f.
8. 1340433f3f384043394235 403e34414232353d3d4b35 extensions 32 3e343d3845 38 423545 3635 4430393b3045/3f303a35423045.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-crossinline-keyword--kotlin--medium]]
- [[q-object-singleton-companion--kotlin--medium]]
- [[q-kotlin-java-primitives--programming-languages--medium]]
