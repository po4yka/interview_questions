---
id: 20251012-12271111143
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
related: [q-kotlin-coroutines-introduction--kotlin--medium, q-testing-viewmodels-coroutines--kotlin--medium, q-kotlin-static-variable--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags:
  - programming-languages
  - elvis
  - null-safety
  - nullable
  - operators
  - safe-call
  - difficulty/medium
---
# Что такое null safety и как это пишется?

# Question (EN)
> What is null safety and how is it written?

# Вопрос (RU)
> Что такое null safety и как это пишется?

---

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

## Related Questions

- [[q-kotlin-coroutines-introduction--kotlin--medium]]
- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-kotlin-static-variable--programming-languages--easy]]
