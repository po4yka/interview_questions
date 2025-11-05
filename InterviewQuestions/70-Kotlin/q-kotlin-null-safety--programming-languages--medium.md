---
id: lang-078
title: "Kotlin Null Safety / Null Safety в Kotlin"
aliases: [Kotlin Null Safety, Null Safety в Kotlin]
topic: programming-languages
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-coroutines-introduction--kotlin--medium, q-kotlin-static-variable--programming-languages--easy, q-testing-viewmodels-coroutines--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, elvis, null-safety, nullable, operators, programming-languages, safe-call]
date created: Friday, October 31st 2025, 6:30:57 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Что Такое Null Safety И Как Это Пишется?

# Вопрос (RU)
> Что такое null safety и как это пишется?

---

# Question (EN)
> What is null safety and how is it written?

## Ответ (RU)

Null safety, или безопасность относительно null, — это концепция, направленная на предотвращение ошибок времени выполнения, которые возникают из-за неожиданного использования null значений (как NullPointerException в Java).

**Возможности null safety в Kotlin:**

1. **Nullable типы**: Типы переменных по умолчанию не допускают null. Используйте `?` чтобы сделать тип nullable:
```kotlin
var name: String = "John"     // Не может быть null
var nullable: String? = null  // Может быть null
```

2. **Оператор безопасного вызова** `?.`: Безопасный доступ к методам/свойствам:
```kotlin
val length = nullable?.length // Возвращает null, если nullable равен null
```

3. **Оператор Элвис** `?:`: Предоставляет значение по умолчанию:
```kotlin
val length = nullable?.length ?: 0 // Возвращает 0, если null
```

4. **Утверждение not-null** `!!`: Принудительно вызывает NPE (не рекомендуется):
```kotlin
val length = nullable!!.length // Выбрасывает NPE, если null
```

5. **Безопасные приведения** `as?`: Безопасное приведение типов без исключения:
```kotlin
val result = value as? String // Возвращает null, если приведение не удалось
```

Null safety в Kotlin предотвращает большинство ошибок, связанных с null, во время компиляции.

## Answer (EN)

Null safety is a concept aimed at preventing runtime errors that occur due to unexpected use of null values (like NullPointerException in Java).

**Kotlin null safety features:**

1. **Nullable types**: Variable types by default don't allow null. Use `?` to make type nullable:
```kotlin
var name: String = "John"     // Cannot be null
var nullable: String? = null  // Can be null
```

2. **Safe call operator** `?.`: Access methods/properties safely:
```kotlin
val length = nullable?.length // Returns null if nullable is null
```

3. **Elvis operator** `?:`: Provide default value:
```kotlin
val length = nullable?.length ?: 0 // Returns 0 if null
```

4. **Not-null assertion** `!!`: Force NPE (not recommended):
```kotlin
val length = nullable!!.length // Throws NPE if null
```

5. **Safe casts** `as?`: Cast safely without exception:
```kotlin
val result = value as? String // Returns null if cast fails
```

Kotlin's null safety prevents most null-related crashes at compile time.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-coroutines-introduction--kotlin--medium]]
- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-kotlin-static-variable--programming-languages--easy]]
