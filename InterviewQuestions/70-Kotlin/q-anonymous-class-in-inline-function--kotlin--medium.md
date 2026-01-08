---id: kotlin-047
title: Anonymous Class in Inline Function / Анонимный класс в inline функции
aliases: [Anonymous Class in Inline Function, Анонимный класс в inline функции]

# Classification
topic: kotlin
subtopics: [anonymous-classes, inline, lambdas]
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
related: [c-compose-recomposition, c-kotlin, c-perfetto, c-power-profiling, q-coroutine-timeout-withtimeout--kotlin--medium, q-delegates-compilation--kotlin--hard, q-structured-concurrency-kotlin--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-11-10

tags: [anonymous-classes, difficulty/medium, inline, kotlin, lambdas, object-expressions, performance]
---
# Вопрос (RU)
> Можно ли создать анонимный класс внутри inline функции в Kotlin?

# Question (EN)
> Can you create an anonymous class inside an inline function in Kotlin?

## Ответ (RU)

**Технически — да**, **можно создавать object expressions (анонимные классы) внутри inline функций**.

Но важно понимать ограничения и последствия:
- **Если object expression пытается сохранять или использовать inline lambda-параметр (по умолчанию inline) вне его непосредственного вызова**, компилятор выдаст ошибку. Такой параметр подставляется на место вызова и не может быть сохранён в поле/долгоживущем замыкании.
- **Если object expression не захватывает inline-параметры, которые должны пережить вызов**, он компилируется нормально, но **создаёт объект во время выполнения**, т.е. не даёт преимуществ inline и может ухудшать производительность.

При этом знание базовых концепций [[c-kotlin]] помогает лучше понимать поведение inline функций и анонимных классов.

### Проблема

**Inline функции** в основном используются для устранения накладных расходов на создание объектов лямбд и вызовов функций: тело лямбды подставляется в место вызова.

**Анонимные классы** (object expressions) при обычной семантике всегда приводят к созданию экземпляра объекта. Поэтому:
- Они **не запрещены**, но
- Они **часто противоречат основной мотивации inline**, если используются как обёртка вокруг колбэков и добавляют лишние аллокации.

### Ключевые Моменты

1. **Object expression приводит к созданию объекта во время выполнения** → не даёт выигрыша от inline по аллокациям (если только компилятор не применит дополнительные оптимизации, на которые не стоит полагаться).
2. **Нельзя сохранять inline lambda-параметры** в полях, долгоживущих объектах или замыканиях, которые могут пережить вызов inline функции (включая object expressions, которые выходят за её пределы). Для таких случаев параметр нужно пометить `noinline`.
3. **Возможна потеря производительности**, если ожидался выигрыш от inline, но добавлены анонимные классы и дополнительные аллокации.

### Пример С Ограничением Захвата

```kotlin
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            // НЕЛЬЗЯ сохранять inline-параметр таким образом в долгоживущем объекте:
            // action(value) // Ошибка компиляции: inline-параметр нельзя сохранять в поле/объекте, переживающем вызов
        }
    }
    handler.handle(42)
}
```

Здесь проблема не в том, что «inline функции не могут содержать object expressions», а в том, что **inline-параметр `action` нельзя сохранять и вызывать позже через созданный объект**, если этот объект или ссылка на параметр потенциально переживают сам вызов inline функции.

### Правильный Подход: Используйте Лямбды, Когда Нужна Инлайнизация

```kotlin
inline fun process(action: (Int) -> Unit) {
    // Лямбда будет инлайнена в месте вызова
    action(42)
}
```

Когда мы не создаём анонимный класс и не сохраняем `action` за пределами контекста вызова, inline может дать ожидаемый выигрыш.

### Когда Нужны Анонимные Классы

Если вам действительно нужен анонимный класс/`object` (например, реализация интерфейса с несколькими методами или хранение состояния), вы можете:
- использовать **обычную функцию** (не inline), или
- использовать inline так, чтобы не сохранять inline-параметры в объекты, которые переживают вызов.

```kotlin
fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun onStart() { println("Started") }
        override fun onComplete(result: String) { println("Complete: $result") }
        override fun onError(error: Throwable) { println("Error: ${error.message}") }
    }
}
```

### Обходной Путь: `noinline`

Если нужно передать лямбду в анонимный класс внутри inline-функции, пометьте её как `noinline`:

```kotlin
inline fun process(
    value: Int,
    noinline complexHandler: (Int) -> Unit // не будет инлайнен, можно сохранять
) {
    val handler = object : Handler {
        override fun handle() {
            complexHandler(value) // OK: noinline-параметр можно вызывать из сохранённого контекста
        }
    }
    handler.handle()
}
```

**Компромисс:** параметр `complexHandler` теряет преимущества inline, но его можно безопасно захватывать в object expression.

### Резюме

**Можно ли создавать анонимные классы в inline функциях?**

- **Технически:** Да, это разрешено.
- **Ограничения:** Нельзя сохранять и вызывать inline lambda-параметры (по умолчанию inline) из объектов или замыканий, которые переживают вызов; для этого используйте `noinline` или перепишите дизайн.
- **Практически:** Часто нет смысла, так как создание анонимного класса нивелирует выигрыш от inline.

**Рекомендации:**
- Для single-method интерфейсов и простых колбэков используйте **лямбды + inline**.
- Для сложных анонимных реализаций используйте **обычные функции** или `noinline`-параметры.
- Помните: inline оптимален, когда **избегает создания лишних объектов**, а object expressions эти объекты добавляют.

---

## Answer (EN)

**Technically yes**, **you can create object expressions (anonymous classes) inside inline functions** in Kotlin.

But there are important constraints and trade-offs:
- **If the object expression attempts to store or use an inline lambda parameter (default inline) beyond its immediate call**, the compiler will report an error. Such parameters are inlined at the call site and cannot be safely stored in fields or long-lived closures.
- **If the object expression does not capture inline parameters that need to escape the call**, it compiles fine, but it **allocates an object at runtime**, so you do not get the intended inline performance benefits and might even regress performance.

### Key Points

1. An object expression, under its usual semantics, results in a runtime allocation → no allocation savings from inlining (unless additional compiler optimizations apply; you should not rely on those here).
2. You cannot store inline function parameters (including inline lambdas) in fields or objects that may outlive the inline call (including object expressions that escape); to do that safely, those parameters must be marked `noinline`.
3. Using anonymous classes inside an inline function is allowed, but if they capture/stash parameters they often defeat the usual goal of using inline for allocation and call overhead reduction.

### Example with Capture Restriction

```kotlin
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            // You CANNOT store the inline parameter like this in a long-lived object:
            // action(value) // Compilation error: cannot store an inline parameter in a field/object that outlives the call
        }
    }
    handler.handle(42)
}
```

The issue is not that "inline functions cannot contain object expressions", but that **the inline parameter `action` cannot be stored and invoked later through the created object** if that object or reference may outlive the inline function call.

### Preferred Usage: Lambdas for Inlining Benefits

```kotlin
inline fun process(action: (Int) -> Unit) {
    // Lambda body will be inlined at the call site
    action(42)
}
```

If you avoid creating anonymous classes and do not store `action` beyond the call context, the inline function can deliver its intended benefits.

### When to Use Anonymous Classes

If you truly need an anonymous class/object (e.g., multi-method interface implementation or a stateful handler), you can:
- use a **regular (non-inline) function**, or
- use an inline function but design it so that it does not store inline parameters into objects that outlive the call.

```kotlin
fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun onStart() { println("Started") }
        override fun onComplete(result: String) { println("Complete: $result") }
        override fun onError(error: Throwable) { println("Error: ${error.message}") }
    }
}
```

### Workaround: `noinline`

If you need to pass a lambda into an anonymous class inside an inline function, mark it as `noinline`:

```kotlin
inline fun process(
    value: Int,
    noinline complexHandler: (Int) -> Unit
) {
    val handler = object : Handler {
        override fun handle() {
            complexHandler(value) // OK: noinline parameter can be stored and called
        }
    }
    handler.handle()
}
```

**Trade-off:** `complexHandler` is no longer inlined, so you lose inline benefits for that parameter, but it becomes safe to capture in an object expression.

### Summary

- You **can** declare anonymous classes inside inline functions.
- The main restriction: **do not store inline lambda parameters (or other inline parameters) in objects/closures that can outlive the inline call**; use `noinline` or redesign when you need to store them.
- In practice, prefer lambdas plus inline when you want performance benefits, and use anonymous classes where their semantics are needed, understanding that they allocate objects.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-inline-classes-value-classes--kotlin--medium]] - Inline Class
- [[q-kotlin-inline-functions--kotlin--medium]] - Inline Functions
- [[q-macrobenchmark-startup--android--medium]] - Performance
- [[q-app-startup-optimization--android--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
