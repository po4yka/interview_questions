---
id: lang-039
title: "Kotlin Sam Conversions / SAM конверсии в Kotlin"
aliases: [Kotlin Sam Conversions, SAM конверсии в Kotlin]
topic: programming-languages
subtopics: [functional-programming, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-infix-functions--kotlin--medium, q-kotlin-extensions-overview--programming-languages--medium, q-kotlin-override-keyword--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, lambda, lambda-functions, programming-languages, sam]
---
# Как Работают SAM (Single Abstract Method)?

# Вопрос (RU)
> Как работают SAM (Single Abstract Method)?

---

# Question (EN)
> How do SAM (Single Abstract Method) conversions work?

## Ответ (RU)


SAM (Single Abstract Method) конверсии позволяют использовать Kotlin лямбды там где ожидаются Java функциональные интерфейсы.

### Java Функциональный Интерфейс
```java
// Java
public interface Clickable {
    void onClick(View view);
}

public void setListener(Clickable listener) {
    // ...
}
```

### Kotlin SAM Конверсия
```kotlin
// Вместо:
setListener(object : Clickable {
    override fun onClick(view: View) {
        // Обработать клик
    }
})

// SAM конверсия позволяет:
setListener { view ->
    // Обработать клик
}
```

### Требования Для SAM Конверсии

1. **Java интерфейс** (не Kotlin интерфейс)
2. **Ровно один абстрактный метод**
3. **Параметры метода соответствуют параметрам лямбды**

### Примеры

**1. Event Listeners**
```kotlin
button.setOnClickListener { view ->
    Toast.makeText(context, "Clicked", Toast.LENGTH_SHORT).show()
}
```

**2. Runnable**
```kotlin
// Java: Runnable interface
Thread {
    println("Running in thread")
}.start()
```

**3. Comparator**
```kotlin
val sorted = list.sortedWith { a, b ->
    a.length - b.length
}
```

### Kotlin Fun Interfaces

Kotlin 1.4+ поддерживает `fun interface`:
```kotlin
fun interface Transformer {
    fun transform(input: String): String
}

// SAM конверсия работает:
fun process(transformer: Transformer) {
    // ...
}

process { it.uppercase() }
```

### Когда SAM Не Работает
```kotlin
// Kotlin интерфейс - Нет SAM конверсии
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


SAM (Single Abstract Method) conversions allow Kotlin lambdas to be used where Java functional interfaces are expected.

### Java Functional Interface
```java
// Java
public interface Clickable {
    void onClick(View view);
}

public void setListener(Clickable listener) {
    // ...
}
```

### Kotlin SAM Conversion
```kotlin
// Instead of:
setListener(object : Clickable {
    override fun onClick(view: View) {
        // Handle click
    }
})

// SAM conversion allows:
setListener { view ->
    // Handle click
}
```

### Requirements for SAM Conversion

1. **Java interface** (not Kotlin interface)
2. **Exactly one abstract method**
3. **Method parameters match lambda parameters**

### Examples

**1. Event Listeners**
```kotlin
button.setOnClickListener { view ->
    Toast.makeText(context, "Clicked", Toast.LENGTH_SHORT).show()
}
```

**2. Runnable**
```kotlin
// Java: Runnable interface
Thread {
    println("Running in thread")
}.start()
```

**3. Comparator**
```kotlin
val sorted = list.sortedWith { a, b ->
    a.length - b.length
}
```

### Kotlin Fun Interfaces

Kotlin 1.4+ supports `fun interface`:
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
// Kotlin interface - No SAM conversion
interface KotlinListener {
    fun onEvent()
}

// Must use object expression:
setListener(object : KotlinListener {
    override fun onEvent() { }
})
```

---
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

