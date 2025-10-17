---
id: "20251015082237137"
title: "Kotlin Any Unit Nothing / Any Unit и Nothing в Kotlin"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - any
  - kotlin
  - nothing
  - programming-languages
  - type-system
  - types
  - unit
---
# Что известно про типы any, unit, nothing в Kotlin ?

# Question (EN)
> What do you know about Any, Unit, Nothing types in Kotlin?

# Вопрос (RU)
> Что известно про типы any, unit, nothing в Kotlin ?

---

## Answer (EN)

There are special types in Kotlin with unique purposes:

### Any
- Root type for all non-nullable types in Kotlin (analogous to Object in Java)
- Any object except null inherits from Any
- Used where representation of any possible value except null is required
- Defines basic methods: `equals()`, `hashCode()`, `toString()`

### Unit
- Analogous to `void` in Java, but unlike void, it is a full-fledged object
- Functions that don't return a meaningful result actually return Unit
- Used to indicate that function performs an action but doesn't return a value
- Although Unit return type is usually omitted, it can be specified explicitly

### Nothing
- Type that has no values
- Used to denote "impossibility" - situations when function never completes normally
- Function may loop forever or always throw an exception
- Indicates that this code point is unreachable

**Example:**
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

---

## Ответ (RU)

В Kotlin существуют специальные типы с уникальными целями:

### Any
- Корневой тип для всех ненулевых типов в Kotlin (аналог Object в Java)
- Любой объект, кроме null, наследуется от Any
- Используется там, где требуется представление любого возможного значения, кроме null
- Определяет базовые методы: `equals()`, `hashCode()`, `toString()`

### Unit
- Аналог `void` в Java, но в отличие от void, это полноценный объект
- Функции, которые не возвращают значимый результат, на самом деле возвращают Unit
- Используется для обозначения того, что функция выполняет действие, но не возвращает значение
- Хотя тип возврата Unit обычно опускается, его можно указать явно

### Nothing
- Тип, который не имеет значений
- Используется для обозначения "невозможности" - ситуаций, когда функция никогда не завершается нормально
- Функция может зацикливаться навсегда или всегда выбрасывать исключение
- Указывает, что данная точка кода недостижима

**Пример:**
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

