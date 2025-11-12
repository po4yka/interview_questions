---
id: lang-039
title: "Kotlin Sam Conversions / SAM конверсии в Kotlin"
aliases: [Kotlin Sam Conversions, SAM конверсии в Kotlin]
topic: kotlin
subtopics: [functional-programming, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-infix-functions--kotlin--medium, q-kotlin-extensions-overview--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, lambda, lambda-functions, programming-languages, sam]
---
# Как Работают SAM (Single Abstract Method)?

# Вопрос (RU)
> Как работают SAM (Single Abstract Method)?

---

# Question (EN)
> How do SAM (Single Abstract Method) conversions work?

## Ответ (RU)

SAM (Single Abstract Method) конверсии позволяют использовать Kotlin-лямбды в тех местах, где ожидаются функциональные интерфейсы (Java функциональные интерфейсы или Kotlin `fun interface`). Компилятор при этом генерирует анонимную реализацию интерфейса.

### Java Функциональный Интерфейс
```java
// Java
public interface Clickable {
    void onClick(Object view);
}

public void setListener(Clickable listener) {
    // ...
}
```

### Kotlin SAM Конверсия
```kotlin
// Вместо:
setListener(object : Clickable {
    override fun onClick(view: Any?) {
        // Обработать клик
    }
})

// SAM-конверсия позволяет записать короче:
setListener { view ->
    // Обработать клик
}
```

### Требования Для SAM Конверсии

1. **Функциональный интерфейс** с ровно одним абстрактным методом:
   - Java интерфейс с одним абстрактным методом (фактический SAM/functional interface)
   - либо Kotlin `fun interface` (с одним абстрактным методом)
2. **Параметры метода соответствуют параметрам лямбды** (типы должны быть совместимы)
3. **Должен быть известен целевой тип (target type)**: контекст (тип параметра функции, типа переменной, generic-аргумента) должен однозначно указывать на функциональный интерфейс, чтобы компилятор мог применить SAM-конверсию.
4. SAM-конверсия — это синтаксический сахар: создаётся анонимная реализация интерфейса, а не «чистая» функция.

### Примеры

**1. Event Listeners (Java SAM)**
```kotlin
button.setOnClickListener { view ->
    Toast.makeText(context, "Clicked", Toast.LENGTH_SHORT).show()
}
```

**2. Runnable (Java SAM)**
```kotlin
// Java: Thread(Runnable target)
Thread {
    println("Running in thread")
}.start()
// Здесь лямбда конвертируется в Runnable, так как конструктор ожидает Runnable.
```

**3. Comparator (Java SAM / лямбда-форма)**
```kotlin
val sorted = list.sortedWith { a, b ->
    a.length.compareTo(b.length)
}
// Используется перегрузка sortedWith, принимающая (T, T) -> Int,
// которая затем реализуется через Comparator.
```

### Kotlin Fun Interfaces

Начиная с Kotlin 1.4 поддерживаются `fun interface`, для которых также работает SAM-конверсия:
```kotlin
fun interface Transformer {
    fun transform(input: String): String
}

// SAM-конверсия работает:
fun process(transformer: Transformer) {
    // ...
}

process { it.uppercase() }
```

### Когда SAM Не Работает
```kotlin
// Обычный Kotlin-интерфейс (НЕ fun interface) - нет SAM-конверсии
interface KotlinListener {
    fun onEvent()
}

// Нужно использовать object expression:
setListener(object : KotlinListener {
    override fun onEvent() { }
})
```

---

## Answer (EN)

SAM (Single Abstract Method) conversions allow Kotlin lambdas to be used where functional interfaces are expected (Java functional interfaces or Kotlin `fun interface`). The compiler generates an anonymous implementation of that interface behind the scenes.

### Java Functional Interface
```java
// Java
public interface Clickable {
    void onClick(Object view);
}

public void setListener(Clickable listener) {
    // ...
}
```

### Kotlin SAM Conversion
```kotlin
// Instead of:
setListener(object : Clickable {
    override fun onClick(view: Any?) {
        // Handle click
    }
})

// SAM conversion allows a shorter form:
setListener { view ->
    // Handle click
}
```

### Requirements for SAM Conversion

1. **Functional interface** with exactly one abstract method:
   - Java interface with a single abstract method (a SAM / functional interface)
   - or a Kotlin `fun interface` (with a single abstract method)
2. **Method parameters must be compatible with lambda parameters** (types must be compatible)
3. **Target type must be known**: the context (function parameter type, variable type, or generic argument) must clearly expect that functional interface so the compiler can apply SAM conversion.
4. SAM conversion is compile-time sugar that creates an anonymous implementation of the interface (not a raw function type at runtime).

### Examples

**1. Event Listeners (Java SAM)**
```kotlin
button.setOnClickListener { view ->
    Toast.makeText(context, "Clicked", Toast.LENGTH_SHORT).show()
}
```

**2. Runnable (Java SAM)**
```kotlin
// Java: Thread(Runnable target)
Thread {
    println("Running in thread")
}.start()
// Here the lambda is converted to Runnable because the constructor expects a Runnable.
```

**3. Comparator (Java SAM / lambda form)**
```kotlin
val sorted = list.sortedWith { a, b ->
    a.length.compareTo(b.length)
}
// Uses the sortedWith overload taking (T, T) -> Int,
// which is implemented via a Comparator under the hood.
```

### Kotlin Fun Interfaces

Since Kotlin 1.4, `fun interface` is supported and SAM conversion applies to them:
```kotlin
fun interface Transformer {
    fun transform(input: String): String
}

// SAM conversion works:
fun process(transformer: Transformer) {
    // ...
}

process { it.uppercase() }
```

### When SAM Doesn't Work
```kotlin
// Plain Kotlin interface (NOT a fun interface) - no SAM conversion
interface KotlinListener {
    fun onEvent()
}

// Must use object expression:
setListener(object : KotlinListener {
    override fun onEvent() { }
})
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-extensions-overview--programming-languages--medium]]
- [[q-infix-functions--kotlin--medium]]
- [[q-kotlin-override-keyword--programming-languages--easy]]
- [[c-kotlin]]
