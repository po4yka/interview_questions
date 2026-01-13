---
anki_cards:
- slug: q-kotlin-any-unit-nothing--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-any-unit-nothing--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-203
title: "Kotlin Any Unit Nothing / Any Unit и Nothing в Kotlin"
aliases: []
topic: kotlin
subtopics: [functions, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-coroutine-supervisorjob-use-cases--kotlin--medium, q-sharedflow-stateflow--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium]
---
# Вопрос (RU)
> Что известно про типы `Any`, `Unit`, `Nothing` в Kotlin?

# Question (EN)
> What do you know about `Any`, `Unit`, `Nothing` types in Kotlin?

---

## Ответ (RU)

В Kotlin существуют специальные типы с уникальными целями:

### Any
- Корневой тип для всех ненулевых типов в Kotlin; полная иерархия, включая `null`, коренится в `Any?` (аналог `Object` в Java и `Object?` для nullable)
- Любое ненулевое значение в Kotlin имеет тип, являющийся подтипом `Any`
- Используется там, где требуется представление любого возможного ненулевого значения
- Определяет базовые методы: `equals()`, `hashCode()`, `toString()`

### Unit
- Аналог `void` в Java, но в отличие от `void`, `Unit` — это реальный тип
- Функции, которые не возвращают значимый результат, концептуально возвращают единственное значение `Unit`
- Используется для обозначения того, что функция выполняет действие, но не возвращает полезного значения
- Хотя тип возврата `Unit` обычно опускается, его можно указать явно

### Nothing
- Тип, который не имеет значений (нижний тип), является подтипом всех типов
- Используется для обозначения "невозможности" — ситуаций, когда функция никогда не завершает выполнение нормально
- Такая функция может зацикливаться навсегда или всегда выбрасывать исключение
- Указывает, что данная точка кода недостижима; полезен для анализа потока выполнения и в обобщённых API (например, `Result<Nothing>`)

**Пример:**
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

## Answer (EN)

There are special types in Kotlin with unique purposes:

### Any
- Root type for all non-nullable types in Kotlin; the full hierarchy including `null` is rooted at `Any?` (analogous to `Object` in Java and `Object?` for nullable)
- Any non-null value in Kotlin has a type that is a subtype of `Any`
- Used where representation of any possible non-null value is required
- Defines basic methods: `equals()`, `hashCode()`, `toString()`

### Unit
- Analogous to `void` in Java, but unlike `void`, `Unit` is a real type
- Functions that don't return a meaningful result conceptually return the single `Unit` value
- Used to indicate that a function performs an action but doesn't return a useful value
- Although the `Unit` return type is usually omitted, it can be specified explicitly

### Nothing
- Type that has no values (bottom type), a subtype of all types
- Used to denote "impossibility" - situations when a function never completes normally
- Such a function may loop forever or always throw an exception
- Indicates that this code point is unreachable; useful in control-flow analysis and generic APIs (e.g. `Result<Nothing>`)

**Example:**
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

## Follow-ups

- How are `Any`, `Unit`, and `Nothing` used in designing type-safe APIs in Kotlin?
- How does `Nothing` improve control-flow analysis for functions like `error()` or `TODO()`?
- In what scenarios would you explicitly specify `Unit` or `Any` in function signatures instead of relying on type inference?

## Related Questions

- [[q-kotlin-java-primitives--kotlin--medium]]
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]
- [[q-sharedflow-stateflow--kotlin--medium]]
