---
id: 20251012-12271111154
title: "Kotlin Sealed Classes Purpose / Назначение sealed классов в Kotlin"
aliases: [Kotlin Sealed Classes Purpose, Назначение sealed классов в Kotlin]
topic: programming-languages
subtopics: [sealed-classes, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-null-checks-methods--programming-languages--easy, q-expect-actual-kotlin--kotlin--medium, q-kotlin-reified-types--kotlin--hard]
created: 2025-10-15
updated: 2025-10-31
tags:
  - programming-languages
  - oop
  - sealed-classes
  - type-hierarchy
  - when-expressions
  - difficulty/medium
---
# Что такое sealed классы и зачем они нужны?

# Question (EN)
> What are sealed classes and why are they needed?

# Вопрос (RU)
> Что такое sealed классы и зачем они нужны?

---

## Answer (EN)

Sealed classes in Kotlin allow **restricting the set of subclasses** that can be created for a class, providing a strict, closed hierarchy.

**Why they're needed:**

1. **Finite set of states**: Perfect for data that can have a limited number of states
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

2. **Exhaustive when expressions**: Compiler checks all cases are covered
```kotlin
when (result) {
    is Result.Success -> showData(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // No 'else' needed - compiler knows all cases!
}
```

3. **Type safety**: All possible types known at compile time

4. **Better than enums**: Can have different properties and methods per subclass

**Benefits:**
- Code is more safe and understandable
- Compiler helps catch missing cases
- Better than using multiple nullable fields
- Perfect for state machines, API responses, navigation

---

## Ответ (RU)

Sealed классы в Kotlin позволяют **ограничить набор подклассов**, которые могут быть созданы для класса, обеспечивая строгую, закрытую иерархию.

**Зачем они нужны:**

1. **Конечный набор состояний**: Идеально подходят для данных, которые могут иметь ограниченное число состояний
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

2. **Исчерпывающие when-выражения**: Компилятор проверяет, что все случаи охвачены
```kotlin
when (result) {
    is Result.Success -> showData(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // 'else' не нужен - компилятор знает все случаи!
}
```

3. **Типобезопасность**: Все возможные типы известны во время компиляции

4. **Лучше, чем enum**: Могут иметь разные свойства и методы для каждого подкласса

**Преимущества:**
- Код более безопасен и понятен
- Компилятор помогает отловить пропущенные случаи
- Лучше, чем использовать несколько nullable полей
- Идеально для конечных автоматов, ответов API, навигации

## Related Questions

- [[q-kotlin-null-checks-methods--programming-languages--easy]]
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]
