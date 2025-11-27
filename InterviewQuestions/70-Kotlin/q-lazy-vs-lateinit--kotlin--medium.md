---
id: kotlin-024
title: "lazy vs lateinit / lazy против lateinit"
aliases: ["lazy vs lateinit", "lazy против lateinit"]

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
related: [c-kotlin, q-kotlin-lateinit--kotlin--medium, q-property-delegates--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [delegation, difficulty/medium, initialization, kotlin, lateinit, lazy]
date created: Friday, October 17th 2025, 9:48:25 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> В чем разница между `lazy` и `lateinit` в Kotlin?

---

# Question (EN)
> What is the difference between `lazy` and `lateinit` in Kotlin?

## Ответ (RU)

### lazy()

Функция, которая принимает лямбду и возвращает экземпляр `Lazy<T>` для реализации ленивых свойств. Первый вызов выполняет лямбду и запоминает результат. Последующие вызовы возвращают запомненный результат.

```kotlin
val lazyValue: String by lazy {
    println("computed!")
    "Hello"
}

fun main() {
    println(lazyValue)  // Печатает в консоль: computed! затем Hello с новой строки
    println(lazyValue)  // Печатает: Hello (значение уже вычислено и закешировано)
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
| **Примитивные типы** | Можно использовать | Нельзя использовать (компилятор не разрешит) |
| **Nullable** | Можно использовать | Нельзя использовать (тип должен быть non-null) |
| **Потокобезопасность** | По умолчанию потокобезопасен (`LazyThreadSafetyMode.SYNCHRONIZED`), можно изменить режим | Не потокобезопасен, нужна внешняя синхронизация |
| **Инициализация** | Только из лямбды-инициализатора | Из любого места кода до первого чтения |
| **Проверка инициализации** | Доступна через `Lazy<T>.isInitialized()` при явном хранении `Lazy` | `::property.isInitialized` |
| **Когда инициализируется** | При первом доступе | Вручную до использования |

### Потокобезопасность

```kotlin
// lazy - потокобезопасен по умолчанию с LazyThreadSafetyMode.SYNCHRONIZED
val threadSafeValue by lazy {
    // Гарантированно выполнится только один раз даже при доступе из нескольких потоков
    expensiveComputation()
}

// Можно задать иной режим, включая не потокобезопасный
val nonThreadSafeValue by lazy(LazyThreadSafetyMode.NONE) {
    expensiveComputation()
}

// lateinit - нужна ручная синхронизация при доступе из нескольких потоков
lateinit var threadUnsafeValue: String

fun initialize() {
    synchronized(this) {
        threadUnsafeValue = computeValue()
    }
}
```

### Случаи Использования

**Используйте `lazy` когда**:
- Свойство `val` (неизменяемое)
- Инициализация дорогая и может не понадобиться
- Работа с nullable или примитивными типами
- Нужна управляемая ленивость и при необходимости потокобезопасность

**Используйте `lateinit` когда**:
- Свойство `var` (изменяемое)
- Инициализация зависит от внешнего контекста (DI, lifecycle)
- Свойство должно быть non-null и не-примитивным (это требование проверяется компилятором)
- Нужно переинициализировать свойство

**Краткое содержание**: `lazy` для `val`-свойств, по умолчанию потокобезопасный (`SYNCHRONIZED`), поддерживает примитивы и nullable-типы, инициализируется при первом доступе и гарантирует однократное вычисление. `lateinit` для `var`-свойств, не потокобезопасный, только для non-null ссылочных типов, инициализируется вручную до использования, позволяет проверять состояние инициализации и переинициализировать.

См. также: [[c-kotlin]]

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого поведения от Java?
- Когда бы вы использовали это на практике?
- Какие распространенные ошибки стоит избегать?

## Ссылки (RU)

- [Delegated Properties - Kotlin](https://kotlinlang.org/docs/delegated-properties.html)
- [Kotlin: lateinit vs lazy](https://rommansabbir.com/kotlin-lateinit-vs-lazy)

## Связанные Вопросы (RU)

- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-property-delegates--kotlin--medium]]

---

## Answer (EN)

### lazy()

A function that takes a lambda and returns an instance of `Lazy<T>` for implementing lazy properties. The first access executes the lambda and stores the result. Subsequent accesses return the stored result.

```kotlin
val lazyValue: String by lazy {
    println("computed!")
    "Hello"
}

fun main() {
    println(lazyValue)  // Prints to console: computed! then Hello on the next line
    println(lazyValue)  // Prints: Hello (value already computed and cached)
}
```

### Lateinit

A keyword that enables declaration of non-nullable properties without immediate initialization. The property must be initialized before access; otherwise `UninitializedPropertyAccessException` is thrown.

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
| **Primitive types** | Can use | Cannot use (compiler prohibits) |
| **Nullable** | Can use | Cannot use (type must be non-null) |
| **Thread safety** | Thread-safe by default (`LazyThreadSafetyMode.SYNCHRONIZED`), configurable | Not thread-safe, requires external synchronization |
| **Initialization** | Only from initializer lambda | From any code path before first read |
| **Initialization check** | Available via `Lazy<T>.isInitialized()` when holding `Lazy` explicitly | `::property.isInitialized` |
| **When initialized** | On first access | Manually before use |

### Thread Safety

```kotlin
// lazy - thread-safe by default with LazyThreadSafetyMode.SYNCHRONIZED
val threadSafeValue by lazy {
    // Guaranteed to execute only once even under concurrent access
    expensiveComputation()
}

// You can choose a different mode, including non-thread-safe
val nonThreadSafeValue by lazy(LazyThreadSafetyMode.NONE) {
    expensiveComputation()
}

// lateinit - manual synchronization needed for safe concurrent access
lateinit var threadUnsafeValue: String

fun initialize() {
    synchronized(this) {
        threadUnsafeValue = computeValue()
    }
}
```

### Use Cases

**Use `lazy` when**:
- Property is `val` (immutable)
- Initialization is expensive and might not be needed
- Working with nullable or primitive types
- You want controlled lazy initialization and, if needed, thread safety

**Use `lateinit` when**:
- Property is `var` (mutable)
- Initialization depends on external context (DI, lifecycle)
- Property must be non-null and non-primitive (enforced by the compiler)
- You need to reinitialize the property

**English Summary**: `lazy` is for `val` properties, by default thread-safe (`SYNCHRONIZED`), supports primitives and nullables, and initializes on first access with guaranteed one-time computation. `lateinit` is for `var` properties, not thread-safe, only for non-null reference types, manually initialized before use, and allows checking and reinitializing its initialization state.

See also: [[c-kotlin]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Delegated Properties - Kotlin](https://kotlinlang.org/docs/delegated-properties.html)
- [Kotlin: lateinit vs lazy](https://rommansabbir.com/kotlin-lateinit-vs-lazy)

## Related Questions
- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-property-delegates--kotlin--medium]]
