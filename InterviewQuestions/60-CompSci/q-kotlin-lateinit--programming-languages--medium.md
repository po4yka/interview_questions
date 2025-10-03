---
id: 20251003141108
title: lateinit in Kotlin / lateinit в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, properties]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/732
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-properties

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, lateinit, properties, initialization, dependency-injection, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What do you know about lateinit?

# Вопрос (RU)
> Что известно о lateinit?

---

## Answer (EN)

`lateinit` is used for **deferred initialization** of properties in Kotlin.

**Key characteristics:**

1. **Only for `var`**: Cannot be used with `val`
2. **Only reference types**: Cannot be used with primitives (Int, Boolean, etc.)
3. **Must initialize before use**: Throws `UninitializedPropertyAccessException` if accessed before initialization
4. **No null overhead**: Better than nullable types for deferred initialization

**Syntax:**
```kotlin
class MyClass {
    lateinit var name: String
    
    fun initialize() {
        name = "John"  // Initialize later
    }
    
    fun use() {
        println(name)  // Must be initialized by now!
    }
}
```

**Common use cases:**

1. **Dependency Injection**: Properties initialized by DI framework
```kotlin
class MyActivity : Activity() {
    @Inject lateinit var repository: Repository
}
```

2. **Testing**: Properties initialized in setUp methods
```kotlin
class MyTest {
    lateinit var subject: SubjectUnderTest
    
    @Before
    fun setUp() {
        subject = SubjectUnderTest()
    }
}
```

3. **Android**: Views initialized in onCreate/onViewCreated
```kotlin
class MyFragment : Fragment() {
    lateinit var binding: FragmentBinding
    
    override fun onViewCreated(...) {
        binding = FragmentBinding.bind(view)
    }
}
```

**Checking if initialized:**
```kotlin
if (::name.isInitialized) {
    println(name)
}
```

**Constraints:**
- Cannot be used with nullable types
- Cannot be used in primary constructor
- Cannot be used with primitive types

## Ответ (RU)

1. lateinit используется для откладывания инициализации переменных (только для var и только ссылочных типов). 2. Поле помечается как lateinit и должно быть инициализировано до первого использования, иначе выбрасывается UninitializedPropertyAccessException. 3. Это полезно в случаях, когда инициализация зависит от внешних условий (например, DI или тестирование).

---

## Follow-ups
- What's the difference between lateinit and lazy?
- How to check if lateinit property is initialized?
- When should you use lateinit vs nullable types?

## References
- [[c-kotlin-properties]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-lazy-initialization--programming-languages--medium]]
