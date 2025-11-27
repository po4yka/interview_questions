---
id: kotlin-006
title: "Functional Interfaces vs Type Aliases / Функциональные интерфейсы vs псевдонимы типов"
aliases: ["Functional Interfaces vs Type Aliases", "Функциональные интерфейсы vs псевдонимы типов"]
topic: kotlin
subtopics: [functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2
status: draft
moc: moc-kotlin
related: [c-concepts--kotlin--medium, c-kotlin, q-kotlin-sam-interfaces--kotlin--medium, q-type-aliases--kotlin--medium]
created: 2025-10-05
updated: 2025-11-11
tags: [difficulty/medium, kotlin, type-aliases]

date created: Thursday, October 16th 2025, 4:43:56 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> В чем разница между функциональными интерфейсами и псевдонимами типов в Kotlin?

# Question (EN)
> What is the difference between functional interfaces and type aliases in Kotlin?

## Ответ (RU)

### Функциональный Интерфейс (SAM)

Интерфейс с **только одним абстрактным методом**. Объявляется с модификатором `fun`.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

Может содержать дополнительные не-абстрактные члены (default-методы, свойства с реализацией и т.п.).

### Псевдоним Типа

Альтернативное имя для **существующего типа**. Это чисто компиляторный алиас и **не создает новый тип**.

```kotlin
typealias MyHandler = (Int, String, Any) -> Unit
typealias Predicate<T> = (T) -> Boolean
```

### Ключевые Отличия

| Функция | Функциональный интерфейс | Псевдоним типа |
|---------|--------------------------|----------------|
| **Создает новый тип** | Да | Нет |
| **Члены** | Может содержать несколько не-абстрактных + один абстрактный метод | Не определяет собственных членов, только переименовывает существующий тип |
| **Расширения** | Можно добавить специфичные для интерфейса | Расширения объявляются для базового (развернутого) типа, псевдоним сам по себе не добавляет новый scope |
| **Implements/Extends** | Может реализовать и расширить другие интерфейсы | Просто имя для существующего типа |
| **Типобезопасность** | Сильнее (отдельный тип участвует в перегрузке и проверках) | Слабее (тот же тип, что и базовый; не участвует отдельно в перегрузке) |

### Когда Использовать Каждый

**Функциональный интерфейс**, когда:
- API нужно больше, чем просто функция (контракты, несколько операций)
- Нужны расширения и дополнительные члены, специфичные для типа
- Хотите отдельный тип для лучшей типобезопасности и явного контракта

**Псевдоним типа**, когда:
- API принимает простую функцию с определенной сигнатурой
- Хотите более короткое имя для сложного типа
- Не нужны дополнительные операции или контракт

### Пример Сравнения

```kotlin
// Псевдоним типа — простое переименование
// ClickHandler и (View) -> Unit — один и тот же тип для компилятора

typealias ClickHandler = (View) -> Unit

fun setClickListener(handler: ClickHandler) {
    // handler это просто (View) -> Unit
}

// Функциональный интерфейс — новый тип
fun interface ClickListener {
    fun onClick(view: View)
}

// Можно добавить расширения специфичные для ClickListener
fun ClickListener.withLogging(): ClickListener = ClickListener { view ->
    println("Нажато: $view")
    onClick(view)
}

// Расширение объявлено для базового типа (View) -> Unit.
// Псевдоним ClickHandler не создает отдельного типа, любые такие расширения
// применимы ко всем значениям типа (View) -> Unit, не только использующим алиас имени.
fun ((View) -> Unit).withLogging(): (View) -> Unit = { view ->
    println("Нажато: $view")
    this(view)
}
```

**Резюме на русском**: Функциональные интерфейсы создают новые отдельные типы (с одним абстрактным методом), могут иметь дополнительные не-абстрактные члены и поддерживают специфичные для интерфейса расширения. Псевдонимы типов — это чисто компиляторные алиасы существующих типов для читаемости и повторного использования; они не вводят новый тип и не влияют на перегрузку. Выбирайте функциональные интерфейсы для более сложных контрактов и явных типов, псевдонимы типов — для удобного именования существующих сигнатур.

**Когда что использовать:**
- **Функциональные интерфейсы**: когда нужна типобезопасность, дополнительные методы или возможность реализовывать/расширять интерфейсы.
- **Псевдонимы типов**: когда нужна простая читаемость кода для сложных типов функций или generics без изменения модели типов.

**Примеры использования:**

Функциональные интерфейсы:
```kotlin
fun interface Validator {
    fun validate(input: String): Boolean
}

fun interface Transformer<T, R> {
    fun transform(input: T): R
}
```

Псевдонимы типов:
```kotlin
typealias UserId = String
typealias Callback<T> = (Result<T>) -> Unit
typealias JsonMap = Map<String, Any>
```

См. также: [[c-kotlin]]

## Answer (EN)

### Functional Interface (SAM)

An interface with **only one abstract method**. Declared with the `fun` modifier.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

It can also contain additional non-abstract members (default methods, properties with implementation, etc.).

### Type Alias

An alternative name for an **existing type**. It is a compile-time alias and **does not create a new type**.

```kotlin
typealias MyHandler = (Int, String, Any) -> Unit
typealias Predicate<T> = (T) -> Boolean
```

### Key Differences

| Feature | Functional Interface | Type Alias |
|---------|---------------------|------------|
| **Creates new type** | Yes | No |
| **Members** | May contain multiple non-abstract members + one abstract method | Does not define its own members; only renames an existing type |
| **Extensions** | You can add interface-specific extensions | Extensions are declared for the underlying (expanded) type; alias itself does not create a new scope |
| **Implements/Extends** | Can implement and extend other interfaces | Just a name for an existing type |
| **Type safety** | Stronger (distinct type participates in overloads and checks) | Weaker (same as underlying type; cannot be distinguished in overloads) |

### When to Use Each

Use a **Functional Interface** when:
- The API needs more than just a function (contracts, multiple operations)
- You need type-specific extensions and additional members
- You want a distinct type for better type safety and an explicit contract

Use a **Type Alias** when:
- The API accepts a simple function with a specific signature
- You want a shorter name for a complex type
- You do not need additional operations or a separate contract

### Example Comparison

```kotlin
// Type alias - simple renaming
// For the compiler, ClickHandler and (View) -> Unit are exactly the same type

typealias ClickHandler = (View) -> Unit

fun setClickListener(handler: ClickHandler) {
    // handler is just (View) -> Unit
}

// Functional interface - new distinct type
fun interface ClickListener {
    fun onClick(view: View)
}

// Can add extensions specific to ClickListener
fun ClickListener.withLogging(): ClickListener = ClickListener { view ->
    println("Clicked: $view")
    onClick(view)
}

// Extension declared for the underlying function type (View) -> Unit.
// The alias ClickHandler does not introduce a separate type; such extensions
// apply to all values of type (View) -> Unit, not only those named via the alias.
fun ((View) -> Unit).withLogging(): (View) -> Unit = { view ->
    println("Clicked: $view")
    this(view)
}
```

**English Summary**: Functional interfaces create new distinct types (with one abstract method), can have additional non-abstract members, and support interface-specific extensions. Type aliases are compile-time aliases for existing types; they do not introduce new types or affect overload resolution. Choose functional interfaces for richer, explicit contracts; use type aliases for readable naming of existing function signatures or complex types.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Functional (SAM) Interfaces - Kotlin](https://kotlinlang.org/docs/fun-interfaces.html)
- [Type Aliases - Kotlin](https://kotlinlang.org/docs/type-aliases.html)

## Related Questions
- [[q-kotlin-sam-interfaces--kotlin--medium]]
- [[q-type-aliases--kotlin--medium]]

## Последующие Вопросы (RU)
- В чем ключевые отличия по сравнению с Java?
- В каких практических сценариях вы бы использовали каждый подход?
- Какие типичные ошибки и подводные камни стоит учитывать?
## Ссылки (RU)
- [Функциональные (SAM) интерфейсы — Kotlin](https://kotlinlang.org/docs/fun-interfaces.html)
- [Псевдонимы типов — Kotlin](https://kotlinlang.org/docs/type-aliases.html)
## Связанные Вопросы (RU)
---