---
tags:
  - any
  - kotlin
  - nothing
  - programming-languages
  - type-system
  - types
  - unit
difficulty: medium
---

# Что известно про типы any, unit, nothing в Kotlin ?

**English**: What do you know about Any, Unit, Nothing types in Kotlin?

## Answer

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

## Ответ

Существуют специальные типы Any, Unit и Nothing, которые имеют уникальные цели и применения в языке программирования...

