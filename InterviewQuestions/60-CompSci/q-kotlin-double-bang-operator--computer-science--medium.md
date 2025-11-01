---
id: 20251012-12271111124
title: "Kotlin Double Bang Operator / Оператор !! в Kotlin"
aliases: []
topic: computer-science
subtopics: [access-modifiers, type-system, null-safety]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inline-value-classes-performance--kotlin--medium, q-kotlin-null-checks-methods--programming-languages--easy, q-dispatchers-main-immediate--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Что известно о double bang (!!)?

# Question (EN)
> What do you know about double bang (!!)?

# Вопрос (RU)
> Что известно о double bang (!!)?

---

## Answer (EN)


The double-bang operator `!!` in Kotlin forcefully converts a nullable type to non-null, throwing `NullPointerException` if the value is null.

### Syntax
```kotlin
val value: String? = getSomeValue()
val nonNull: String = value!!  // Throws NPE if null
```

### When It's Used

**1. Developer Certainty**
```kotlin
val config: Config? = loadConfig()
// Developer is CERTAIN config loaded successfully
val port = config!!.port
```

**2. Platform Types (Java Interop)**
```kotlin
// Java method returns String (platform type)
val javaString = javaObject.getString()
val kotlinString: String = javaString!!
```

**3. Initialization Patterns**
```kotlin
class MyClass {
    private var lateInit: String? = null
    
    fun initialize() {
        lateInit = "initialized"
    }
    
    fun use() {
        // Developer knows initialize() was called
        println(lateInit!!)
    }
}
```

### Why It's Discouraged

**1. Defeats Null Safety**
```kotlin
// Kotlin's main feature is null safety
// !! bypasses it, making code Java-like
val data = repository.getData()!!  // Bad practice
```

**2. Better Alternatives**

Use safe calls:
```kotlin
val length = text?.length ?: 0
```

Use `let`:
```kotlin
value?.let {
    processNonNull(it)
}
```

Use `requireNotNull`:
```kotlin
val nonNull = requireNotNull(value) {
    "Value must not be null"
}
```

Use `checkNotNull`:
```kotlin
val checked = checkNotNull(config) {
    "Config not initialized"
}
```

### When It's Acceptable
- Tests (where NPE is acceptable)
- Impossible null scenarios
- Better than `lateinit` for some cases

---
---

## Ответ (RU)


Оператор double-bang `!!` в Kotlin принудительно преобразует nullable тип в non-null, выбрасывая `NullPointerException` если значение null.

### Синтаксис
```kotlin
val value: String? = getSomeValue()
val nonNull: String = value!!  // Выбрасывает NPE если null
```

### Когда используется

**1. Уверенность разработчика**
```kotlin
val config: Config? = loadConfig()
// Разработчик УВЕРЕН что config загружен успешно
val port = config!!.port
```

**2. Platform Types (Java Interop)**
```kotlin
// Java метод возвращает String (platform type)
val javaString = javaObject.getString()
val kotlinString: String = javaString!!
```

**3. Паттерны инициализации**
```kotlin
class MyClass {
    private var lateInit: String? = null
    
    fun initialize() {
        lateInit = "initialized"
    }
    
    fun use() {
        // Разработчик знает что initialize() был вызван
        println(lateInit!!)
    }
}
```

### Почему не рекомендуется

**1. Разрушает Null безопасность**
```kotlin
// Главная фича Kotlin - null безопасность
// !! обходит ее, делая код Java-подобным
val data = repository.getData()!!  // Плохая практика
```

**2. Лучшие альтернативы**

Используйте safe calls:
```kotlin
val length = text?.length ?: 0
```

Используйте `let`:
```kotlin
value?.let {
    processNonNull(it)
}
```

Используйте `requireNotNull`:
```kotlin
val nonNull = requireNotNull(value) {
    "Value must not be null"
}
```

Используйте `checkNotNull`:
```kotlin
val checked = checkNotNull(config) {
    "Config not initialized"
}
```

### Когда приемлемо
- Тесты (где NPE приемлем)
- Невозможные null сценарии
- Лучше чем `lateinit` в некоторых случаях

---

## Related Questions

- [[q-inline-value-classes-performance--kotlin--medium]]
- [[q-kotlin-null-checks-methods--programming-languages--easy]]
- [[q-dispatchers-main-immediate--kotlin--medium]]

