---
id: kotlin-024
title: "lazy vs lateinit / lazy против lateinit"
aliases: ["lazy vs lateinit, lazy против lateinit"]

# Classification
topic: kotlin
subtopics: [delegation, initialization, lateinit]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-lateinit--kotlin--medium, q-property-delegates--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [delegation, difficulty/medium, initialization, kotlin, lateinit, lazy]
date created: Friday, October 17th 2025, 9:48:25 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Вопрос (RU)
> В чем разница между lazy и lateinit в Kotlin?

---

# Question (EN)
> What is the difference between lazy and lateinit in Kotlin?
## Ответ (RU)

### lazy()

Функция, которая принимает лямбду и возвращает экземпляр `Lazy<T>` для реализации ленивых свойств. Первый вызов выполняет лямбду и запоминает результат. Последующие вызовы возвращают запомненный результат.

```kotlin
val lazyValue: String by lazy {
    println("computed!")
    "Hello"
}

fun main() {
    println(lazyValue)  // Печатает: computed! \n Hello
    println(lazyValue)  // Печатает: Hello (кешировано)
}
```

### Lateinit

Ключевое слово, которое позволяет объявлять ненулевые свойства без немедленной инициализации. Должно быть инициализировано перед доступом, иначе выбрасывает `UninitializedPropertyAccessException`.

```kotlin
class DemoClass {
    lateinit var userAge: UserAge

    fun init() {
        userAge = UserAge(27)
    }

    fun printAge() {
        if (::userAge.isInitialized) {
            println("Age is : ${userAge.age}")
        } else {
            println("Age not initialized")
        }
    }
}
```

### Ключевые Отличия

| Функция | lazy | lateinit |
|---------|------|----------|
| **Тип свойства** | Только `val` | Только `var` |
| **Примитивные типы** | - Можно использовать | - Нельзя использовать |
| **Nullable** | - Можно использовать | - Нельзя использовать |
| **Потокобезопасность** | - Потокобезопасен по умолчанию | - Не потокобезопасен |
| **Инициализация** | Только из лямбды-инициализатора | Откуда угодно |
| **Проверка инициализации** | N/A (всегда инициализирован) | `::property.isInitialized` |
| **Когда инициализируется** | При первом доступе | Вручную перед использованием |

### Потокобезопасность

```kotlin
// lazy - потокобезопасен по умолчанию
val threadSafeValue by lazy {
    // Гарантированно выполнится только один раз
    expensiveComputation()
}

// lateinit - нужна ручная синхронизация
lateinit var threadUnsafeValue: String

fun initialize() {
    synchronized(this) {
        threadUnsafeValue = computeValue()
    }
}
```

### Случаи Использования

**Используйте lazy когда**:
- Свойство `val` (неизменяемое)
- Инициализация дорогая и может не понадобиться
- Работа с nullable или примитивными типами
- Нужна потокобезопасность

**Используйте lateinit когда**:
- Свойство `var` (изменяемое)
- Инициализация зависит от внешнего контекста (DI, lifecycle)
- Свойство должно быть не-null и не-примитивным
- Нужно переинициализировать свойство

**Краткое содержание**: lazy для val свойств, потокобезопасный, поддерживает примитивы/nullable, инициализируется при первом доступе. lateinit для var свойств, не потокобезопасный, только не-null не-примитивы, инициализируется вручную. lazy гарантирует однократную инициализацию; lateinit позволяет проверять состояние инициализации и переинициализировать.

---

## Answer (EN)

### lazy()

A function that takes a lambda and returns an instance of `Lazy<T>` for implementing lazy properties. First call executes the lambda and remembers the result. Subsequent calls return the remembered result.

```kotlin
val lazyValue: String by lazy {
    println("computed!")
    "Hello"
}

fun main() {
    println(lazyValue)  // Prints: computed! \n Hello
    println(lazyValue)  // Prints: Hello (cached)
}
```

### Lateinit

A keyword that enables declaration of non-nullable properties without immediate initialization. Must be initialized before access, otherwise throws `UninitializedPropertyAccessException`.

```kotlin
class DemoClass {
    lateinit var userAge: UserAge

    fun init() {
        userAge = UserAge(27)
    }

    fun printAge() {
        if (::userAge.isInitialized) {
            println("Age is : ${userAge.age}")
        } else {
            println("Age not initialized")
        }
    }
}
```

### Key Differences

| Feature | lazy | lateinit |
|---------|------|----------|
| **Property type** | `val` only | `var` only |
| **Primitive types** | - Can use | - Cannot use |
| **Nullable** | - Can use | - Cannot use |
| **Thread safety** | - Thread safe by default | - Not thread safe |
| **Initialization** | Only from initializer lambda | From anywhere |
| **Initialization check** | N/A (always initialized) | `::property.isInitialized` |
| **When initialized** | On first access | Manually before use |

### Thread Safety

```kotlin
// lazy - thread safe by default
val threadSafeValue by lazy {
    // Guaranteed to execute only once
    expensiveComputation()
}

// lateinit - manual synchronization needed
lateinit var threadUnsafeValue: String

fun initialize() {
    synchronized(this) {
        threadUnsafeValue = computeValue()
    }
}
```

### Use Cases

**Use lazy when**:
- Property is `val` (immutable)
- Initialization is expensive and might not be needed
- Working with nullable or primitive types
- Need thread safety

**Use lateinit when**:
- Property is `var` (mutable)
- Initialization depends on external context (DI, lifecycle)
- Property must be non-null and non-primitive
- Need to reinitialize the property

**English Summary**: lazy is for val properties, thread-safe, supports primitives/nullables, initialized on first access. lateinit is for var properties, not thread-safe, non-null non-primitives only, manually initialized. lazy guarantees one-time initialization; lateinit allows checking initialization state and reinitializing.

## References
- [Delegated Properties - Kotlin](https://kotlinlang.org/docs/delegated-properties.html)
- [Kotlin: lateinit vs lazy](https://rommansabbir.com/kotlin-lateinit-vs-lazy)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions
- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-property-delegates--kotlin--medium]]
