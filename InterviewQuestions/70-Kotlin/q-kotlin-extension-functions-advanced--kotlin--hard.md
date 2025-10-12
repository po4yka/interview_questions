---
topic: kotlin
tags:
  - kotlin
  - extensions
  - receivers
  - generics
  - dsl
difficulty: hard
status: draft
---

# Advanced Extension Functions

**English**: Implement extension functions with receivers, generic extensions, and nullable receivers. Understand resolution and scope.

**Russian**: Реализуйте extension functions с receivers, generic extensions и nullable receivers. Понимайте resolution и scope.

## Answer (EN)

Extension functions add functionality to existing classes without modifying them. Advanced usage involves receivers, generics, and DSL patterns.

### Extension Function Basics

```kotlin
// Basic extension
fun String.isEmail() = contains('@') && contains('.')

// With receiver type
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
fun <T> List<T>.second(): T = this[1]

// Generic with constraint
fun <T : Comparable<T>> List<T>.isSorted(): Boolean {
    return this.zipWithNext().all { (a, b) -> a <= b }
}

// Multiple type parameters
fun <K, V> Map<K, V>.getOrThrow(key: K): V {
    return this[key] ?: throw NoSuchElementException("Key $key not found")
}

// Reified type parameters
inline fun <reified T> Any?.asOrNull(): T? {
    return this as? T
}

inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    return filterIsInstance<T>()
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
// Function with receiver
fun StringBuilder.appendLine(value: String) = apply {
    append(value)
    append("\n")
}

// DSL-style extension
fun <T> T.configure(block: T.() -> Unit): T {
    block()
    return this
}

// Usage
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

// Mutable extension property (with backing)
var <T> MutableList<T>.lastItem: T
    get() = last()
    set(value) {
        if (isNotEmpty()) this[lastIndex] = value
    }
```

### Resolution and Scope

```kotlin
class Example {
    // Member function
    fun String.memberExtension() = "member"
}

// Top-level extension
fun String.memberExtension() = "top-level"

fun main() {
    val example = Example()
    // Member wins over extension
    with(example) {
        "".memberExtension()  // "member"
    }
}
```

### Operator Extensions

```kotlin
// Arithmetic operators
operator fun Int.times(str: String) = str.repeat(this)

// Usage: 3 * "abc" = "abcabcabc"

// Comparison
operator fun Version.compareTo(other: Version): Int {
    return this.number.compareTo(other.number)
}

// Indexed access
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
        block()
        elements.add("</$name>")
    }

    fun text(value: String) {
        elements.add(value)
    }

    fun build() = elements.joinToString("")
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

### Context Receivers (Experimental)

```kotlin
context(Logger, Transaction)
fun processOrder(order: Order) {
    log("Processing order ${order.id}")
    save(order)
    commit()
}
```

### Best Practices

1. **Keep extensions focused** - single responsibility
2. **Name clearly** - avoid ambiguity with members
3. **Use generics** for reusable patterns
4. **Handle null receivers** when appropriate
5. **Document resolution behavior**
6. **Prefer member functions** for core functionality
7. **Use extension properties** sparingly
8. **Group related extensions** in same file

## Ответ (RU)

Extension functions добавляют функциональность существующим классам без их модификации.

[Полные примеры generic extensions, nullable receivers, DSL patterns и operator extensions приведены в английском разделе]

### Лучшие практики

1. **Держите extensions сфокусированными**
2. **Именуйте четко** - избегайте двусмысленности с members
3. **Используйте generics** для переиспользуемых паттернов
4. **Обрабатывайте null receivers** когда уместно
5. **Документируйте поведение resolution**
6. **Предпочитайте member functions** для основной функциональности
7. **Используйте extension properties осторожно**
8. **Группируйте связанные extensions** в одном файле
