---
id: kotlin-047
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
related: [c-kotlin, q-coroutine-timeout-withtimeout--kotlin--medium, q-delegates-compilation--kotlin--hard, q-structured-concurrency-kotlin--kotlin--medium]

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
- **Если object expression захватывает inline lambda-параметр (по умолчанию inline)** — компилятор выдаст ошибку, потому что такой параметр подставляется на место вызова и не может быть сохранён в поле/замыкании.
- **Если object expression не захватывает inline параметры**, он компилируется нормально, но **создаёт объект**, т.е. не даёт преимуществ inline и может ухудшать производительность.

При этом знание базовых концепций [[c-kotlin]] помогает лучше понимать поведение inline функций и анонимных классов.

### Проблема

**Inline функции** в основном используются для устранения накладных расходов на создание объектов лямбд и вызовов функций: тело лямбды подставляется в место вызова.

**Анонимные классы** (object expressions) всегда создают экземпляры объектов. Поэтому:
- Они **не запрещены**, но
- Они **противоречат основной мотивации inline**, если используются для тех же целей, что и лямбды.

### Ключевые моменты

1. **Object expression всегда создаёт объект** → не даёт выигрыш от inline.
2. **Нельзя захватывать inline lambda-параметры** внутри object expression/лямбды, если они помечены как inline (по умолчанию) и должны быть сохранены.
3. **Возможна потеря производительности**, если ожидался выигрыш от inline, но добавлены анонимные классы.

### Пример с ограничением захвата

```kotlin
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            // НЕЛЬЗЯ захватывать inline-параметр таким образом:
            // action(value) // Ошибка компиляции: inline-параметр нельзя сохранять
        }
    }
    handler.handle(42)
}
```

Здесь проблема не в том, что "inline нельзя содержать object expressions", а в том, что **inline-параметр `action` нельзя сохранять и вызывать позже через созданный объект**.

### Правильный подход: используйте лямбды, когда нужна инлайнизация

```kotlin
inline fun process(action: (Int) -> Unit) {
    // Лямбда будет инлайнена в место вызова
    action(42)
}
```

Когда мы не создаём анонимный класс и не сохраняем `action`, inline может дать ожидаемый выигрыш.

### Когда нужны анонимные классы

Если вам действительно нужен анонимный класс/`object` (например, реализация интерфейса с несколькими методами или хранение состояния), вы можете:
- использовать **обычную функцию** (не inline), или
- использовать inline, но так, чтобы не захватывать inline-параметры в сохраняемые объекты.

```kotlin
fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun onStart() { println("Started") }
        override fun onComplete(result: String) { println("Complete: $result") }
        override fun onError(error: Throwable) { println("Error: ${error.message}") }
    }
}
```

### Обходной путь: `noinline`

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
- **Ограничения:** Нельзя сохранять и вызывать inline lambda-параметры (по умолчанию inline) из таких объектов; для этого используйте `noinline` или перепишите дизайн.
- **Практически:** Часто нет смысла, так как создание анонимного класса нивелирует выигрыш от inline.

**Рекомендации:**
- Для single-method интерфейсов и простых колбэков используйте **лямбды + inline**.
- Для сложных анонимных реализаций используйте **обычные функции** или `noinline`-параметры.
- Помните: inline оптимален, когда **избегает создания лишних объектов**, а object expressions эти объекты создают.

---

## Answer (EN)

**Technically yes**, **you can create object expressions (anonymous classes) inside inline functions** in Kotlin.

But there are important constraints and trade-offs:
- **If the object expression captures an inline lambda parameter (default behavior)**, the compiler will report an error, because such parameters are inlined at call sites and cannot be stored in fields/closures.
- **If the object expression does not capture inline parameters**, it compiles fine, but it **allocates an object**, so you do not get the intended inline performance benefits and may even regress performance.

### Key points

1. An object expression always creates an object → no allocation savings from inlining.
2. You cannot capture inline lambda parameters in objects or lambdas that outlive the call; to do that, you must mark them as `noinline`.
3. Using anonymous classes inside an inline function is allowed, but often contradicts the usual goal of using inline for allocation and call overhead reduction.

### Example with capture restriction

```kotlin
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            // You CANNOT capture the inline parameter like this:
            // action(value) // Compilation error: cannot store inline parameter
        }
    }
    handler.handle(42)
}
```

The issue is not that "inline functions cannot contain object expressions", but that **the inline parameter `action` cannot be stored and invoked later through the created object**.

### Preferred usage: lambdas for inlining benefits

```kotlin
inline fun process(action: (Int) -> Unit) {
    // Lambda body will be inlined at the call site
    action(42)
}
```

If you avoid creating anonymous classes and do not store the lambda, the inline function can deliver its benefits.

### When to use anonymous classes

If you truly need an anonymous class/object (e.g., multi-method interface implementation or stateful handler), you can:
- use a **regular (non-inline) function**, or
- use an inline function but design it so that it does not capture inline parameters into stored objects.

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

**Trade-off:** `complexHandler` is no longer inlined, so you lose the inline benefits for that parameter, but it becomes safe to capture.

### Summary

- You **can** declare anonymous classes inside inline functions.
- The main restriction: **do not capture inline lambda parameters in objects that outlive the call**; use `noinline` (or redesign) when you need to store them.
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
