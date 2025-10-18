---
id: 20251012-1227111196
title: Anonymous Class in Inline Function / Анонимный класс в inline функции
aliases: []

# Classification
topic: kotlin
subtopics: [inline, anonymous-classes, lambdas, performance, optimization]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: ""
source_note: ""

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-structured-concurrency-kotlin--kotlin--medium, q-delegates-compilation--kotlin--hard, q-coroutine-timeout-withtimeout--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, inline, anonymous-classes, lambdas, object-expressions, performance, difficulty/medium]
---
# Question (EN)
> Can you create an anonymous class inside an inline function in Kotlin?

# Вопрос (RU)
> Можно ли создать анонимный класс внутри inline функции в Kotlin?

## Answer (EN)
**No**, **inline functions cannot contain object expressions** (anonymous classes). If you need to use inline, you can pass a **lambda instead of an anonymous class**.

However, there are nuances: while you can technically write an object expression in an inline function, it **defeats the purpose** of inlining and can cause **performance issues** because the object expression creates an actual object allocation.

## The Problem

### Why Anonymous Classes Don't Work Well with Inline

**Inline functions** are designed to eliminate lambda object allocation by copying lambda code directly to the call site.

**Anonymous classes** (object expressions) always create object instances, which contradicts the performance goal of inlining.

---

## Compilation Error Case

```kotlin
// - COMPILATION ERROR in some contexts
inline fun process(value: Int, action: (Int) -> Unit) {
    // Trying to create anonymous class
    val handler = object : EventHandler {
        override fun handle() {
            action(value)  // - Cannot capture inline parameter
        }
    }
    handler.handle()
}
```

**Compiler error:**
```
Error: Inline lambda parameter 'action' captured in non-inline lambda
```

**Why:** The `action` lambda parameter is meant to be inlined, but capturing it in an object expression would require creating an actual object, which defeats inlining.

---

## Cases Where It Compiles But Defeats Purpose

### Example 1: Object Expression Without Capturing

```kotlin
// WARNING: COMPILES but defeats inline purpose
inline fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun handle() {
            println("Handling event")
        }
    }
}
```

**What happens:**
- Creates an anonymous class instance (object allocation)
- Inlining doesn't help performance
- Defeats the purpose of using `inline`

**Better approach:**

```kotlin
// - BETTER - Regular function
fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun handle() {
            println("Handling event")
        }
    }
}
```

---

### Example 2: Object Expression with Captured Variables

```kotlin
// WARNING: PROBLEMATIC
inline fun processWithHandler(value: Int) {
    val handler = object : EventHandler {
        override fun handle() {
            println("Value: $value")  // Captures 'value'
        }
    }
    handler.handle()
}
```

**Issues:**
1. Creates object instance (not inlined)
2. Captured variables lose inline benefit
3. Increased memory allocation

---

## The Correct Approach: Use Lambdas

### Replace Anonymous Class with Lambda

```kotlin
// - Anonymous class (creates object)
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            action(value)  // - Error!
        }
    }
    handler.handle(42)
}

// - Lambda (no object allocation with inline)
inline fun process(action: (Int) -> Unit) {
    action(42)  // Inlined directly
}
```

**Result after inlining:**

```kotlin
// Call site
process { value ->
    println(value)
}

// After inlining
println(42)  // No object, no lambda object!
```

---

## Comparison: Anonymous Class vs Lambda

### Anonymous Class

```kotlin
interface Callback {
    fun onComplete(result: String)
}

// Regular function (not inline)
fun execute(callback: Callback) {
    callback.onComplete("Done")
}

// Usage
execute(object : Callback {
    override fun onComplete(result: String) {
        println(result)
    }
})
```

**Memory:** Creates anonymous class instance.

---

### Lambda with Inline

```kotlin
// Inline function
inline fun execute(callback: (String) -> Unit) {
    callback("Done")
}

// Usage
execute { result ->
    println(result)
}
```

**After inlining:**

```kotlin
println("Done")  // No object allocation!
```

**Memory:** Zero allocation (lambda code inlined).

---

## When Anonymous Classes Are Necessary

Sometimes you **must** use anonymous classes (e.g., when implementing interfaces with multiple methods):

```kotlin
interface EventHandler {
    fun onStart()
    fun onComplete(result: String)
    fun onError(error: Throwable)
}

// - Use regular function (not inline)
fun registerHandler(): EventHandler {
    return object : EventHandler {
        override fun onStart() {
            println("Started")
        }

        override fun onComplete(result: String) {
            println("Complete: $result")
        }

        override fun onError(error: Throwable) {
            println("Error: ${error.message}")
        }
    }
}
```

**Why not inline:** Multiple methods cannot be represented as a single lambda.

---

## Workaround: noinline

If you need to use object expressions with an inline function:

```kotlin
inline fun process(
    value: Int,
    noinline complexHandler: (Int) -> Unit  // Mark as noinline
) {
    // Now can be used in object expression
    val handler = object : Handler {
        override fun handle() {
            complexHandler(value)  // OK now
        }
    }
    handler.handle()
}
```

**Tradeoff:** `complexHandler` parameter loses inline benefit.

---

## Performance Impact

### Scenario 1: Inline with Lambda (Best)

```kotlin
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Inlined
    }
}

repeat(1000) {
    println("Hello")
}
```

**After inlining:**

```kotlin
for (i in 0 until 1000) {
    println("Hello")  // No lambda object
}
```

**Allocations:** 0

---

### Scenario 2: Inline with Object Expression (Worst)

```kotlin
inline fun repeat(times: Int, action: () -> Unit) {
    val wrapper = object : Runnable {
        override fun run() {
            action()  // - If this compiles, defeats inline
        }
    }
    for (i in 0 until times) {
        wrapper.run()
    }
}
```

**Allocations:** 1 Runnable object + lambda captures

**Performance:** Worse than regular function!

---

### Scenario 3: Regular Function with Object Expression (OK)

```kotlin
fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Lambda object created
    }
}
```

**Allocations:** 1 lambda object

**Performance:** Acceptable, honest about allocation.

---

## Best Practices

### - DO

1. **Use lambdas with inline functions:**

```kotlin
inline fun <T> measureTime(block: () -> T): T {
    val start = System.currentTimeMillis()
    val result = block()  // Lambda inlined
    println("Took ${System.currentTimeMillis() - start}ms")
    return result
}
```

2. **Use regular functions for anonymous classes:**

```kotlin
fun createClickListener(onClick: () -> Unit): View.OnClickListener {
    return object : View.OnClickListener {
        override fun onClick(v: View?) {
            onClick()
        }
    }
}
```

3. **Use noinline when necessary:**

```kotlin
inline fun process(
    inlinedAction: () -> Unit,
    noinline storedAction: () -> Unit  // For storage/passing
) {
    inlinedAction()  // Inlined
    someList.add(storedAction)  // Stored as object
}
```

---

### - DON'T

1. **Don't mix inline with anonymous classes:**

```kotlin
// - BAD
inline fun process() {
    val obj = object : Handler { ... }  // Defeats purpose
}
```

2. **Don't use inline for functions that must create objects:**

```kotlin
// - BAD
inline fun createHandler(): Handler {
    return object : Handler { ... }  // No benefit from inline
}

// - GOOD
fun createHandler(): Handler {
    return object : Handler { ... }
}
```

---

## Summary

**Can you create anonymous classes in inline functions?**

- **Technically:** Sometimes yes (compiles)
- **Practically:** No, defeats the purpose
- **Compiler:** Often produces errors when capturing inline parameters

**Problems:**
1. Creates object allocation (defeats inline)
2. Cannot capture inline lambda parameters
3. Hurts performance instead of helping

**Solution:**
- Use **lambdas** for single-method interfaces (SAM)
- Use **regular functions** when anonymous classes are needed
- Use **noinline** modifier if you must mix them

**Key principle:** Inline is for **eliminating** object allocation. Anonymous classes **create** objects. They are fundamentally incompatible.

**Best practice:**
- Inline → Use lambdas
- Anonymous classes → Use regular functions

## Ответ (RU)

**Нет**, **inline функции не должны содержать object expressions** (анонимные классы). Если нужно использовать inline, используйте **лямбду вместо анонимного класса**.

Однако есть нюансы: технически можно написать object expression в inline функции, но это **сводит на нет смысл инлайна** и может вызвать **проблемы с производительностью**, так как object expression всегда создает объект.

### Проблема

**Inline функции** предназначены для устранения создания объектов лямбд путем копирования кода лямбды непосредственно в место вызова.

**Анонимные классы** (object expressions) всегда создают экземпляры объектов, что противоречит цели инлайна.

### Ключевые проблемы

1. **Создает объект** (сводит на нет inline)
2. **Не может захватывать inline лямбда-параметры**
3. **Ухудшает производительность** вместо улучшения

### Правильный подход: используйте лямбды

```kotlin
// - Анонимный класс (создает объект)
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            action(value)  // - Ошибка!
        }
    }
    handler.handle(42)
}

// - Лямбда (без создания объекта с inline)
inline fun process(action: (Int) -> Unit) {
    action(42)  // Инлайнится напрямую
}
```

### Когда нужны анонимные классы

Используйте **обычные функции** (не inline) для анонимных классов:

```kotlin
// - Обычная функция для анонимного класса
fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun onStart() { println("Started") }
        override fun onComplete(result: String) { println("Complete: $result") }
        override fun onError(error: Throwable) { println("Error: ${error.message}") }
    }
}
```

### Обходной путь: noinline

Если необходимо смешать:

```kotlin
inline fun process(
    value: Int,
    noinline complexHandler: (Int) -> Unit  // Помечаем как noinline
) {
    val handler = object : Handler {
        override fun handle() {
            complexHandler(value)  // Теперь OK
        }
    }
    handler.handle()
}
```

**Компромисс:** параметр `complexHandler` теряет преимущество inline.

### Резюме

**Можно ли создавать анонимные классы в inline функциях?**

- **Технически:** Иногда да (компилируется)
- **Практически:** Нет, сводит на нет смысл
- **Компилятор:** Часто выдает ошибки при захвате inline параметров

**Решение:**
- Используйте **лямбды** для single-method интерфейсов (SAM)
- Используйте **обычные функции**, когда нужны анонимные классы
- Используйте **noinline** модификатор, если нужно их смешать

**Ключевой принцип:** Inline для **устранения** создания объектов. Анонимные классы **создают** объекты. Они фундаментально несовместимы.

**Best practice:**
- Inline → Используйте лямбды
- Анонимные классы → Используйте обычные функции


---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-inline-classes-value-classes--kotlin--medium]] - Inline Class
- [[q-kotlin-inline-functions--kotlin--medium]] - Inline Functions
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-app-startup-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
