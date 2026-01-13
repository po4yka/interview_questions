---
anki_cards:
- slug: q-kotlin-access-modifiers--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-access-modifiers--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-213
title: "Kotlin Access Modifiers / Модификаторы доступа Kotlin"
aliases: []
topic: kotlin
subtopics: [functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-semaphore-rate-limiting--kotlin--medium, q-suspend-functions-deep-dive--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium, kotlin/functions]
---
# Вопрос (RU)
> Что известно про модификаторы доступа в Kotlin?

# Question (EN)
> What is known about access modifiers in Kotlin?

---

## Ответ (RU)

Модификаторы доступа в Kotlin управляют видимостью классов, интерфейсов, функций, свойств, конструкторов и других объявлений. Это ключевой механизм инкапсуляции: он позволяет скрывать детали реализации и открывать только необходимый внешний API.

В Kotlin есть четыре модификатора видимости: `public`, `private`, `protected`, `internal` (см. также ).

**1. `public` (по умолчанию в большинстве случаев)**
- Виден отовсюду.
- Используется по умолчанию, если явно не указан другой модификатор, для:
  - верхнеуровневых объявлений;
  - членов класса (если не указано иное).

```kotlin
class PublicClass  // Виден отовсюду
public fun publicFunction() {}  // Явно public
```

**2. `private`**
- Верхнеуровневые объявления: видны только в том же файле.
- Члены класса: видны только внутри этого класса.
- Конструктор: можно ограничить создание экземпляров снаружи.

```kotlin
// Файл: Example.kt
private class PrivateClass  // Видна только в этом файле

class Outer {
    private val privateField = 42  // Видна только внутри Outer

    private constructor()  // Нельзя вызвать снаружи Outer

    fun access() {
        println(privateField)  // OK
    }
}

fun test() {
    val outer = Outer()
    // outer.privateField  // Ошибка: private
}
```

**3. `protected`**
- Применим только к членам классов и конструкторам `open`/`abstract` классов.
- Виден внутри класса и его подклассов.
- Нельзя использовать для верхнеуровневых объявлений.

```kotlin
open class Base {
    protected val protectedField = 42
}

class Derived : Base() {
    fun access() {
        println(protectedField)  // OK в подклассе
    }
}

fun test() {
    val base = Base()
    // base.protectedField  // Ошибка: protected
}
```

**4. `internal`**
- Виден внутри одного модуля.
- Модуль — это набор файлов, компилируемых вместе (например, модуль Gradle, модуль IntelliJ, артефакт Maven).

```kotlin
internal class InternalClass  // Видна в рамках модуля
internal fun internalFunction() {}  // Видна в рамках модуля
```

**Сравнение Kotlin и Java (основные отличия)**

- `public`:
  - Kotlin: по умолчанию для верхнеуровневых объявлений и (если не указано иное) для членов; виден везде.
  - Java: должен быть явно указан; виден везде.
- `private`:
  - Kotlin: применим к членам и верхнеуровневым объявлениям (файловая видимость).
  - Java: только внутри класса; нет `private` для верхнеуровневых типов на уровне файла.
- `protected`:
  - Kotlin: видимость внутри класса и подклассов.
  - Java: внутри класса, подклассов и того же пакета.
- `internal`:
  - Kotlin: видимость в пределах модуля.
  - Java: прямого аналога нет (ближайшее — package-private, но семантика отличается).
- Без модификатора:
  - Kotlin: трактуется как `public` (если не наложены другие ограничения контекстом).
  - Java: package-private (видимость в рамках пакета).

**Рекомендации:**
- Использовать максимально строгий модификатор, который позволяет требуемое использование.
- Отдавать предпочтение `private` для деталей реализации.
- Применять `internal` для API, используемых только внутри модуля.
- Делать `public` только стабильные внешние API.
- Осторожно использовать `protected`, предпочитая композицию наследованию.

## Answer (EN)

Access modifiers in Kotlin control the visibility of classes, interfaces, functions, properties, constructors, and other declarations. They are essential for encapsulation: you hide implementation details and expose only what is needed.

Kotlin provides four visibility modifiers: `public`, `private`, `protected`, and `internal` (see also ).

**1. `public` (default in most cases)**
- Visible everywhere.
- Default if no modifier is specified for:
  - top-level declarations
  - class members (unless another modifier is specified)

```kotlin
class PublicClass  // Visible everywhere
public fun publicFunction() {}  // Explicitly public
```

**2. `private`**
- Top-level: visible only inside the same file.
- Class member: visible only inside that class.
- Constructor: can restrict instantiation from outside.

```kotlin
// File: Example.kt
private class PrivateClass  // Visible only in this file

class Outer {
    private val privateField = 42  // Visible only inside Outer

    private constructor()  // Cannot be called from outside Outer

    fun access() {
        println(privateField)  // OK
    }
}

fun test() {
    val outer = Outer()
    // outer.privateField  // Error: 'privateField' is private in 'Outer'
}
```

**3. `protected`**
- Applicable only to class members and constructors of `open`/`abstract` classes.
- Visible in the class and its subclasses.
- Not allowed for top-level declarations.

```kotlin
open class Base {
    protected val protectedField = 42
}

class Derived : Base() {
    fun access() {
        println(protectedField)  // OK in subclass
    }
}

fun test() {
    val base = Base()
    // base.protectedField  // Error: 'protectedField' is protected in 'Base'
}
```

**4. `internal`**
- Visible within the same module.
- A module is a set of Kotlin files compiled together (e.g., a Gradle module, an IntelliJ module, or a Maven module).

```kotlin
internal class InternalClass  // Visible in the same module
internal fun internalFunction() {}  // Visible in the same module
```

**Kotlin vs Java (high-level differences)**

- `public`:
  - Kotlin: default for top-level declarations and (unless specified) for members; visible everywhere.
  - Java: must be specified explicitly to be public; visible everywhere.
- `private`:
  - Kotlin: for members (class/objects) and top-level declarations (file-level visibility).
  - Java: only within the class; no file-level private for top-level types.
- `protected`:
  - Kotlin: visible in the class and its subclasses only.
  - Java: visible in class, subclasses, and within the same package.
- `internal`:
  - Kotlin: visible within the same module.
  - Java: no direct equivalent (closest is package-private, but semantics differ).
- No modifier:
  - Kotlin: treated as `public` for top-level and member declarations (unless otherwise constrained by context).
  - Java: package-private (visible within the same package).

**Best Practices:**
- Use the most restrictive modifier that still allows required usage.
- Prefer `private` for implementation details.
- Use `internal` for APIs that should be shared within a module but not exposed publicly.
- Use `public` only for stable, external APIs.
- Use `protected` sparingly; prefer composition over inheritance when possible.

## Дополнительные Вопросы (RU)

- [[q-suspend-functions-deep-dive--kotlin--medium]]
- [[q-semaphore-rate-limiting--kotlin--medium]]

## Follow-ups

- [[q-suspend-functions-deep-dive--kotlin--medium]]
- [[q-semaphore-rate-limiting--kotlin--medium]]

## Related Questions

- [[q-suspend-functions-deep-dive--kotlin--medium]]
- [[q-semaphore-rate-limiting--kotlin--medium]]