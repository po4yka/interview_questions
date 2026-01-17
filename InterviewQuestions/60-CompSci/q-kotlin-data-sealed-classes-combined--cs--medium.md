---id: lang-210
title: "Kotlin Data Sealed Classes Combined / Kotlin Data и Sealed классы вместе"
aliases: []
topic: cs
subtopics: [types]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, c-kotlin, q-channels-basics-types--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium]
anki_cards:
- slug: lang-210-0-en
  front: |
    How do data classes and sealed classes work together in Kotlin?
  back: |
    **Data classes**: Auto-generate `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`.
    
    **Sealed classes**: Restricted class hierarchies - all subclasses known at compile time.
    
    **Combined**: Type-safe state hierarchies with exhaustive `when` expressions.
    
    ```kotlin
    sealed class Result<T> {
      data class Success<T>(val data: T): Result<T>()
      data class Error(val msg: String): Result<Nothing>()
    }
    ```
  language: en
  difficulty: 0.5
  tags: [cs_types, difficulty::medium]
- slug: lang-210-0-ru
  front: |
    Как data-классы и sealed-классы работают вместе в Kotlin?
  back: |
    **Data-классы**: Автогенерация `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`.
    
    **Sealed-классы**: Ограниченные иерархии - все подклассы известны компилятору.
    
    **Вместе**: Типобезопасные иерархии состояний с исчерпывающим `when`.
    
    ```kotlin
    sealed class Result<T> {
      data class Success<T>(val data: T): Result<T>()
      data class Error(val msg: String): Result<Nothing>()
    }
    ```
  language: ru
  difficulty: 0.5
  tags: [cs_types, difficulty::medium]

---
# Вопрос (RU)
> Расскажи про data классы и sealed классы и как их сочетать

# Question (EN)
> Tell me about data classes and sealed classes and how to combine them

---

## Ответ (RU)

### Data Классы

Data классы предназначены для "хранения данных" и автоматически генерируют полезные методы на основе свойств, объявленных в первичном конструкторе:
- `equals()` — сравнение по значению (для свойств из первичного конструктора)
- `hashCode()` — согласованное хеширование (по свойствам из первичного конструктора)
- `toString()` — читаемое строковое представление
- `copy()` — создание модифицированных копий
- `componentN()` — поддержка деструктуризации

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = user1.copy(age = 31)
```

По умолчанию в `equals`, `hashCode`, `toString`, `copy` и `componentN` участвуют только свойства из первичного конструктора.

### Sealed Классы

Sealed классы представляют "ограниченные иерархии наследования", где все разрешённые подклассы известны компилятору (они должны находиться в том же пакете и модуле в современных версиях Kotlin):

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val error: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

### Комбинация Обоих

Вместе они создают "типобезопасные и легко управляемые структуры данных", особенно для `when`-выражений:

```kotlin
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.error}")
    Result.Loading -> println("Loading...")
}  // Исчерпывающе для ненулевого Result: компилятор проверяет все случаи
```

Преимущества комбинации:
- Типобезопасность во время компиляции
- Исчерпывающие `when`-выражения для ненулевых sealed-типов
- Чистый, поддерживаемый код
- Отлично подходит для представления иерархий UI/состояний/результатов

См. также:

---

## Answer (EN)

### Data Classes

Data classes are designed for "storing data" and automatically generate useful methods based on the properties declared in the primary constructor:
- `equals()` - value-based equality (for primary-constructor properties)
- `hashCode()` - consistent hashing (for primary-constructor properties)
- `toString()` - readable string representation
- `copy()` - create modified copies
- `componentN()` - support for destructuring declarations

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("John", 30)
val user2 = user1.copy(age = 31)
```

Only properties from the primary constructor participate in `equals`, `hashCode`, `toString`, `copy`, and `componentN` by default.

### Sealed Classes

Sealed classes represent "restricted inheritance hierarchies" where all permitted subclasses are known to the compiler (they must be in the same package and module in modern Kotlin):

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val error: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

### Combining Both

Together, they create "type-safe and easily manageable data structures", especially for `when` expressions:

```kotlin
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println("Data: ${result.data}")
    is Result.Error -> println("Error: ${result.error}")
    Result.Loading -> println("Loading...")
}  // Exhaustive for non-nullable Result: compiler checks all cases
```

Benefits of combination:
- Type safety at compile time
- Exhaustive `when` expressions for non-nullable sealed types
- Clean, maintainable code
- Great for representing UI/state/result hierarchies

---

## Дополнительные Вопросы (RU)

- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-channels-basics-types--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]

## Related Questions

- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-channels-basics-types--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]

## Ссылки (RU)

- [[c-computer-science]]
## References

- [[c-computer-science]]
