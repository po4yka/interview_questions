---
anki_cards:
- slug: q-kotlin-constants--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-constants--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-207
title: "Kotlin Constants / Константы в Kotlin"
aliases: []
topic: kotlin
subtopics: [functions, types]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-inline-function-limitations--kotlin--medium, q-kotlin-native--kotlin--hard]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/easy]

---
# Вопрос (RU)
> Что такое константы и можно ли их изменять?

# Question (EN)
> What are constants and can they be changed?

---

## Ответ (RU)

Константы — это фиксированные значения, которые не могут быть изменены после их определения. Они используются для значений, остающихся неизменными на протяжении выполнения программы.

**В Kotlin:**

- **`val`**: Неизменяемая ссылка (только для чтения), значение присваивается один раз во время выполнения
```kotlin
val name = "John" // Нельзя переназначить ссылку
```
Важно: если `val` хранит изменяемый объект (например, список), его внутреннее состояние может изменяться; неизменяемой является ссылка, а не обязательно объект.

- **`const val`**: Константа времени компиляции (должна быть на верхнем уровне или внутри `object`/`companion object`; тип — примитивный или `String`)
```kotlin
const val MAX_SIZE = 100 // Значение известно во время компиляции
```

**Ключевые различия:**
- `val` может быть инициализирована во время выполнения
- `const val` должна быть известна во время компиляции
- `const val` может использоваться только с примитивными типами и `String`

Константы (включая `const val` и используемые как константы свойства `val`) не могут быть переназначены после инициализации.

## Answer (EN)

Constants are fixed values that cannot be changed after their definition. They are used to define values that remain unchanged throughout program execution.

**In Kotlin:**

- **`val`**: Immutable reference (read-only), value is assigned once at runtime
```kotlin
val name = "John" // Cannot reassign the reference
```
Note: if `val` holds a mutable object (e.g. a list), the object’s internal state can still change; only the reference is immutable.

- **`const val`**: Compile-time constant (must be top-level, or inside an object or companion object; type must be a primitive or `String`)
```kotlin
const val MAX_SIZE = 100 // Known at compile time
```

**Key differences:**
- `val` can be initialized at runtime
- `const val` must be known at compile time
- `const val` can only be used with primitive types and `String`

Constants (including `const val` and `val` properties used as constants) are not reassignable after initialization.

## Дополнительные Вопросы (RU)

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-extensions-overview--kotlin--medium]]

## Follow-ups

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-extensions-overview--kotlin--medium]]

## Связанные Вопросы (RU)

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-extensions-overview--kotlin--medium]]

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-extensions-overview--kotlin--medium]]

