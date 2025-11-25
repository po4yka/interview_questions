---
id: lang-201
title: "Kotlin Default Access Modifier / Модификатор доступа по умолчанию в Kotlin"
aliases: ["Kotlin Default Access Modifier", "Модификатор доступа по умолчанию в Kotlin"]
topic: kotlin
subtopics: [access-modifiers]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-concepts--kotlin--medium, q-debounce-search-coroutines--kotlin--medium, q-dispatcher-performance--kotlin--hard]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/easy, kotlin, kotlin/access-modifiers]
date created: Saturday, October 18th 2025, 9:34:45 am
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---

# Вопрос (RU)
> Какой модификатор доступа по умолчанию используется в Kotlin?

# Question (EN)
> What is the default access modifier in Kotlin?

---

## Ответ (RU)

Модификатор доступа по умолчанию в Kotlin — это **`public`**. Если модификатор видимости явно не указан, объявление по умолчанию является `public` (как для top-level объявлений, так и для членов классов).

**Модификаторы доступа в Kotlin:**

```kotlin
// Public (по умолчанию) — виден везде
class PublicClass  // То же что: public class PublicClass

// Private — виден только в том же файле (для top-level) или в классе
private class PrivateClass

// Internal — виден в том же модуле
internal class InternalClass

// Protected — виден в классе и подклассах (только для членов класса)
open class Base {
    protected val protectedProperty = 42
}
```

**Сравнение с Java:**

| Модификатор | Kotlin по умолчанию | Java по умолчанию |
|----------|----------------|---------------|
| Top-level объявления (классы, функции, свойства) | `public` | package-private |
| Члены класса | `public` | package-private |

**Пример:**
```kotlin
// Всё public по умолчанию:
class User(val name: String)  // public класс, public primary-конструктор, public свойство

fun greet() = "Hello"  // public функция

val counter = 0  // public свойство
```

**Ключевые отличия от Java:**
- В Kotlin по умолчанию используется `public` для объявлений без явного модификатора
- В Java по умолчанию используется package-private (при отсутствии модификатора)
- В Kotlin есть `internal` (видимость в модуле) вместо package-private

---

## Answer (EN)

The default access modifier in Kotlin is **`public`**. If you don't specify any visibility modifier, the declaration is `public` by default (for both top-level declarations and class members).

**Access Modifiers in Kotlin:**

```kotlin
// Public (default) - visible everywhere
class PublicClass  // Same as: public class PublicClass

// Private - visible only in the same file (for top-level) or class
private class PrivateClass

// Internal - visible in the same module
internal class InternalClass

// Protected - visible in class and subclasses (only for class members)
open class Base {
    protected val protectedProperty = 42
}
```

**Comparison with Java:**

| Modifier | Kotlin Default | Java Default |
|----------|----------------|---------------|
| Top-level declarations (classes, functions, properties) | `public` | package-private |
| Class members | `public` | package-private |

**Example:**
```kotlin
// All public by default:
class User(val name: String)  // public class, public primary constructor, public property

fun greet() = "Hello"  // public function

val counter = 0  // public property
```

**Key differences from Java:**
- Kotlin: `public` by default for declarations without an explicit modifier
- Java: package-private (no modifier) by default
- Kotlin has `internal` (module visibility) instead of package-private

---

## Дополнительные Вопросы (RU)
- Чем `internal` отличается от видимости package-private в Java?
- В каких случаях вы бы явно использовали `private` для top-level объявлений в Kotlin?
- Чем отличается видимость `protected` в Kotlin и Java?
- Как видимость по умолчанию `public` взаимодействует с `internal` в мульти-модульных проектах?
- Почему в некоторых API всё же явно указывают `public`, хотя это значение по умолчанию?

## Follow-ups
- How does `internal` differ from Java's package-private visibility?
- In which cases would you explicitly use `private` for top-level declarations in Kotlin?
- How does `protected` visibility differ between Kotlin and Java?
- How does the default `public` visibility interact with `internal` in multi-module projects?
- Why might you still explicitly write `public` in some APIs despite it being the default?

## Ссылки (RU)
- [[c-concepts--kotlin--medium]]

## References
- [[c-concepts--kotlin--medium]]

## Связанные Вопросы (RU)

- [[q-dispatcher-performance--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]
- [[q-debounce-search-coroutines--kotlin--medium]]

## Related Questions

- [[q-dispatcher-performance--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]
- [[q-debounce-search-coroutines--kotlin--medium]]
