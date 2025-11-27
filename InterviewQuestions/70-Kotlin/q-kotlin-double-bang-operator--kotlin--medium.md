---
id: lang-212
title: "Kotlin Double Bang Operator / Оператор !! в Kotlin"
aliases: ["Kotlin Double Bang Operator", "Оператор !! в Kotlin"]
topic: kotlin
subtopics: ["null-safety", "type-system"]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c--kotlin--medium, q-dispatchers-main-immediate--kotlin--medium, q-inline-value-classes-performance--kotlin--medium, q-kotlin-null-checks-methods--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium, kotlin/null-safety]

date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Что известно о операторе double bang `!!` в Kotlin?

# Question (EN)
> What do you know about double bang `!!` in Kotlin?

---

## Ответ (RU)

Оператор double-bang `!!` в Kotlin принудительно утверждает, что выражение nullable-типа не равно null. Во время выполнения он делает проверку и выбрасывает `NullPointerException`, если значение равно null.

### Синтаксис
```kotlin
val value: String? = getSomeValue()
val nonNull: String = value!!  // Выбрасывает NPE, если value == null
```

### Когда Используется

Во всех сценариях `!!` — это жёсткое утверждение: его стоит применять только тогда, когда null действительно невозможен (или недопустим), и немедленный падёж (NPE) предпочтительнее продолжения выполнения.

**1. Уверенность / Инварианты**
```kotlin
val config: Config? = loadConfig()
// Разработчик утверждает, что config обязан быть успешно загружен к этому месту
val port = config!!.port
```

**2. Platform Types (Java Interop)**
```kotlin
// Java-метод возвращает String, который в Kotlin рассматривается как platform type
val javaString = javaObject.getString()
val kotlinString: String = javaString!!  // Утверждаем non-null, если контракт API это гарантирует
```

**3. Паттерны инициализации (Контролируемый поток)**
```kotlin
class MyClass {
    private var initialized: String? = null
    
    fun initialize() {
        initialized = "initialized"
    }
    
    fun use() {
        // Разработчик полагается на вызов initialize() до use()
        println(initialized!!)
    }
}
```

### Почему Не Рекомендуется

**1. Подрывает Null-безопасность**
```kotlin
// Одна из ключевых особенностей Kotlin — null-безопасность
// !! обходит проверки на этапе компиляции и приводит к Java-подобным NPE
val data = repository.getData()!!  // В общем случае плохая практика без сильного инварианта
```

**2. Лучшие альтернативы**

Используйте safe calls и elvis:
```kotlin
val length = text?.length ?: 0
```

Используйте `let` для работы только с non-null значением:
```kotlin
value?.let { nonNullValue ->
    processNonNull(nonNullValue)
}
```

Используйте `requireNotNull`, когда это контракт вызова (быстрый fail с понятным сообщением):
```kotlin
val nonNull = requireNotNull(value) {
    "Value must not be null"
}
```

Используйте `checkNotNull` для внутренних инвариантов:
```kotlin
val checked = checkNotNull(config) {
    "Config not initialized"
}
```

Эти варианты сохраняют идею null-безопасности, делая ожидания явными и сообщения об ошибках осмысленными.

### Когда Приемлемо
- В тестах (где прямой NPE допустим и код можно оставить компактным).
- Когда есть сильный, задокументированный инвариант или внешний контракт, гарантирующий non-null, и немедленный краш предпочтителен при его нарушении.
- В редких случаях, когда nullable-бэкинг плюс `!!` для read-only `val` лучше моделирует семантику инициализации, чем `lateinit`, при строго контролируемом инварианте.


## Answer (EN)

The double-bang operator `!!` in Kotlin forcefully asserts that an expression of a nullable type is non-null. At runtime it performs a null-check and throws `NullPointerException` if the value is null.

### Syntax
```kotlin
val value: String? = getSomeValue()
val nonNull: String = value!!  // Throws NPE if value is null
```

### When It's Used

In all cases, `!!` is a hard assertion: it should be used only when it is truly impossible (or unacceptable) for the value to be null and an immediate failure (NPE) is preferred over continuing execution.

**1. Developer Certainty / Invariants**
```kotlin
val config: Config? = loadConfig()
// Developer asserts that config must have been loaded successfully here
val port = config!!.port
```

**2. Platform Types (Java Interop)**
```kotlin
// Java method returns String, seen as a platform type in Kotlin
val javaString = javaObject.getString()
val kotlinString: String = javaString!!  // Assert non-null if API contract guarantees it
```

**3. Initialization Patterns (Controlled flow)**
```kotlin
class MyClass {
    private var initialized: String? = null
    
    fun initialize() {
        initialized = "initialized"
    }
    
    fun use() {
        // Developer relies on calling initialize() before use()
        println(initialized!!)
    }
}
```

### Why It's Discouraged

**1. Undermines Null-Safety**
```kotlin
// Kotlin's key feature is null safety
// !! bypasses compile-time checks, making failures look like Java-style NPEs
val data = repository.getData()!!  // Generally bad practice without a strong invariant
```

**2. Better Alternatives**

Use safe calls and elvis:
```kotlin
val length = text?.length ?: 0
```

Use `let` for scoped non-null usage:
```kotlin
value?.let { nonNullValue ->
    processNonNull(nonNullValue)
}
```

Use `requireNotNull` when a value is a caller contract (fail fast with clear message):
```kotlin
val nonNull = requireNotNull(value) {
    "Value must not be null"
}
```

Use `checkNotNull` for internal invariants:
```kotlin
val checked = checkNotNull(config) {
    "Config not initialized"
}
```

These alternatives preserve the spirit of null-safety by making expectations explicit and failures more informative.

### When It's Acceptable
- In tests (where a direct NPE is fine and keeps code concise).
- When you have a strong, well-documented invariant or external contract that guarantees non-null, and an immediate crash is preferable if violated.
- In rare cases where using a nullable backing field plus `!!` for a read-only `val` closely models initialization semantics better than `lateinit`, and the invariant is strictly controlled.


## Дополнительные Вопросы (RU)

- Как соотносятся `!!`, safe calls и оператор `?:` в контексте null-безопасности в Kotlin?
- В каких случаях `requireNotNull` предпочтительнее `!!`?
- Почему чрезмерное использование `!!` считается признаком плохого дизайна?

## Follow-ups

- How do `!!`, safe calls, and the `?:` operator relate in the context of Kotlin null-safety?
- In which cases is `requireNotNull` preferable to `!!`?
- Why is overuse of `!!` considered a sign of poor design?

## Ссылки (RU)

- [[c--kotlin--medium]]

## References

- [[c--kotlin--medium]]

## Related Questions

- [[q-dispatchers-main-immediate--kotlin--medium]]
- [[q-inline-value-classes-performance--kotlin--medium]]
- [[q-kotlin-null-checks-methods--kotlin--easy]]
