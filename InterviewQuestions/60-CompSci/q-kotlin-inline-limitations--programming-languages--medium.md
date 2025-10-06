---
tags:
  - inline
  - kotlin
  - lambdas
  - optimization
  - performance
  - programming-languages
  - recursion
difficulty: medium
---

# Бывают ли случаи, когда нельзя использовать inline?

**English**: Are there cases when inline cannot be used?

## Answer

Yes, **inline cannot be used** if the function contains **large blocks of code** or **recursion**, as this will increase the size of compiled code. Also, **inline functions are not suitable** for passing or returning lambdas that capture variables from the context. This can lead to errors or significant increase in memory consumption.

## When Inline Should NOT Be Used

### 1. Large Function Bodies

**Problem:** Inlining copies function code to every call site.

```kotlin
// ❌ BAD - Large function body
inline fun processLargeData(data: List<Int>) {
    // 100+ lines of complex logic
    val step1 = data.map { it * 2 }
    val step2 = step1.filter { it > 10 }
    val step3 = step2.groupBy { it % 3 }
    val step4 = step3.map { (key, values) -> key to values.sum() }
    // ... many more lines
    // This code is copied to EVERY call site!
}

// Called 10 times = code bloat (100+ lines × 10 = 1000+ lines)
repeat(10) {
    processLargeData(listOf(1, 2, 3))
}

// ✅ GOOD - Regular function
fun processLargeData(data: List<Int>) {
    // Large code, called once
}
```

**Result of inlining large functions:**
- Increased compiled code size (.dex/.class files)
- Slower compilation
- Potential instruction cache misses
- Minimal performance benefit

---

### 2. Recursive Functions

**Problem:** Inlining creates infinite copy loop.

```kotlin
// ❌ COMPILATION ERROR - Cannot inline recursive function
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)  // ❌ Error: Cannot inline recursive call
}
```

**Why it fails:**

```
Attempt to inline factorial(5):

factorial(5) = 5 * factorial(4)
             = 5 * (4 * factorial(3))
             = 5 * (4 * (3 * factorial(2)))
             = ... infinite inlining!
```

**Compiler error:**
```
Error: Inline function 'factorial' cannot be recursive
```

**Solution:** Don't use `inline` for recursive functions:

```kotlin
// ✅ GOOD - Regular function
fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)
}
```

---

### 3. Passing or Storing Lambdas (Non-Inlined)

**Problem:** Lambdas passed to non-inline functions or stored create objects.

```kotlin
// ❌ BAD - Lambda cannot be inlined
inline fun processData(data: List<Int>, action: (Int) -> Unit) {
    // Passing lambda to non-inline function
    data.forEach(action)  // forEach is inline, OK

    // Storing lambda - creates object!
    val storedAction = action  // ❌ Capturing creates object
    someList.add(storedAction)  // ❌ Cannot inline
}
```

**Compiler error:**
```
Error: Illegal usage of inline-parameter 'action'
```

**Workaround:** Use `noinline`:

```kotlin
// ✅ GOOD - Mark lambda as noinline
inline fun processData(
    data: List<Int>,
    noinline action: (Int) -> Unit  // Won't be inlined
) {
    val storedAction = action  // OK now
    someList.add(storedAction)
}
```

---

### 4. Lambdas Capturing Variables (with caution)

**Problem:** Captured variables in lambdas can cause issues.

```kotlin
// ⚠️ CAREFUL - Capturing variables
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Fine
    }
}

fun test() {
    var count = 0
    repeat(5) {
        count++  // Captures 'count' - creates boxing overhead
    }
}
```

**What happens:**

Without inline:
```kotlin
// Lambda creates object with 'count' reference
class Lambda : Function0<Unit> {
    var count: Ref<Int>  // Wrapped in reference
    override fun invoke() {
        count.element++
    }
}
```

With inline:
```kotlin
// Lambda body inlined - direct variable access
for (i in 0 until 5) {
    count++  // Direct access, no wrapping
}
```

**When it becomes a problem:**

```kotlin
// ❌ PROBLEM - Returns lambda that captures variables
inline fun createCounter(): () -> Int {
    var count = 0
    return { count++ }  // ❌ Cannot inline returned lambda
}
```

**Compiler error:**
```
Error: Inline function cannot contain reified type parameters
```

---

### 5. Virtual/Abstract Functions

**Problem:** Inline requires compile-time knowledge of function body.

```kotlin
abstract class Base {
    // ❌ COMPILATION ERROR - Abstract cannot be inline
    abstract inline fun process()  // ❌ No body to inline
}

open class Parent {
    // ❌ COMPILATION ERROR - Open cannot be inline
    open inline fun calculate() {  // ❌ Can be overridden
        // ...
    }
}
```

**Why:** Inlining requires knowing exact implementation at compile time.

**Solution:** Don't use inline with virtual/abstract functions:

```kotlin
abstract class Base {
    abstract fun process()  // ✅ OK
}
```

---

### 6. Functions with Reified Type Parameters (partially)

**Correct usage:**

```kotlin
// ✅ OK - inline with reified
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T
}
```

**Problematic usage:**

```kotlin
// ❌ PROBLEM - Returning lambda with reified type
inline fun <reified T> createChecker(): (Any) -> Boolean {
    return { it is T }  // ❌ Cannot return lambda using reified type
}
```

---

### 7. Functions Called from Java

**Problem:** Java doesn't understand Kotlin's inline.

```kotlin
// Kotlin
inline fun process(action: () -> Unit) {
    action()
}

// Called from Java - inline is ignored!
```

**Java sees:**

```java
public static final void process(@NotNull Function0 action) {
    action.invoke();  // Regular call, not inlined
}
```

**Result:** Performance benefit lost when called from Java.

---

## Code Size Impact

### Example: Inline vs Regular

```kotlin
// Inline function
inline fun log(message: String) {
    println("[LOG] $message")
}

// Called 100 times
fun main() {
    repeat(100) {
        log("Message $it")
    }
}
```

**After inlining:**

```kotlin
fun main() {
    repeat(100) {
        // Code copied 100 times!
        println("[LOG] Message $it")
    }
}
```

**Bytecode impact:**
- Regular function: ~10 lines of bytecode (1 function definition + 100 calls)
- Inlined function: ~200 lines of bytecode (println copied 100 times)

---

## When to Avoid Inline

| Case | Problem | Solution |
|------|---------|----------|
| **Large functions** | Code bloat | Regular function |
| **Recursive functions** | Infinite inlining | Regular function |
| **Stored lambdas** | Cannot inline | `noinline` modifier |
| **Returned lambdas** | Escaping lambda | `noinline` or regular function |
| **Virtual/abstract** | No body at compile time | Regular function |
| **Called from Java** | Inline ignored | Consider regular function |

---

## When TO Use Inline

✅ **Good use cases:**

1. **Higher-order functions with lambdas:**

```kotlin
inline fun <T> measureTime(block: () -> T): T {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    println("Took ${duration}ms")
    return result
}
```

2. **Functions with reified type parameters:**

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}
```

3. **Small utility functions:**

```kotlin
inline fun Int.isEven() = this % 2 == 0
inline fun String.isEmail() = contains("@")
```

4. **Performance-critical lambdas:**

```kotlin
inline fun List<Int>.sumByCustom(selector: (Int) -> Int): Int {
    var sum = 0
    for (element in this) {
        sum += selector(element)  // Inlined, no lambda object
    }
    return sum
}
```

---

## Summary

**Cannot use inline when:**

1. ❌ **Large function bodies** - causes code bloat
2. ❌ **Recursive functions** - infinite inlining
3. ❌ **Storing lambdas** - lambda must be invoked inline
4. ❌ **Returning lambdas** - escaping context
5. ❌ **Virtual/abstract functions** - no body to inline
6. ❌ **Called primarily from Java** - inline ignored

**Should use inline when:**

1. ✅ Small higher-order functions with lambdas
2. ✅ Functions with reified type parameters
3. ✅ Performance-critical small utilities
4. ✅ Eliminating lambda object allocation

**Key principle:** Only inline **small functions** with **lambda parameters** where **eliminating lambda objects** provides meaningful performance benefit.

**Memory impact:** Captured variables in non-inlined lambdas cause boxing and increased memory usage.

## Ответ

Да, inline нельзя использовать, если функция содержит большие блоки кода или рекурсию, так как это увеличит размер скомпилированного кода. Также inline-функции не подходят для передачи или возврата лямбд, которые захватывают переменные из контекста. Это может привести к ошибкам или значительному увеличению потребления памяти.

