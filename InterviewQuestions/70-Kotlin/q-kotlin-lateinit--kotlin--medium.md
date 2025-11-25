---
id: kotlin-019
title: "Kotlin lateinit Keyword / Ключевое слово lateinit в Kotlin"
aliases: ["Kotlin lateinit Keyword", "Ключевое слово lateinit в Kotlin"]

# Classification
topic: kotlin
subtopics: [initialization, lateinit, null-safety]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-channel-flow-comparison--kotlin--medium, q-kotlin-sam-conversions--programming-languages--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/medium, initialization, kotlin, lateinit, null-safety, properties]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Что вы знаете о `lateinit` в Kotlin?

---

# Question (EN)
> What do you know about `lateinit` in Kotlin?

## Ответ (RU)

`lateinit` — это ключевое слово, используемое для определения свойства, которое будет инициализировано позже. В отличие от обычных свойств `var` с не-null типом, для которых нужно задать значение при объявлении или в конструкторе, свойства с `lateinit` не инициализируются во время создания объекта. Это делает его особенно полезным, когда начальное значение свойства неизвестно или недоступно на момент объявления, но при этом вы гарантируете (на уровне контракта кода), что оно будет установлено до первого использования. При нарушении этого контракта будет выброшено `UninitializedPropertyAccessException`.

Пример использования `lateinit`:

```kotlin
public class MyTest {
    lateinit var subject: TestSubject

    @SetUp fun setup() {
        subject = TestSubject()
    }

    @Test fun test() {
        subject.method()  // прямое обращение
    }
}
```

### Ключевые Особенности Модификатора `lateinit`

- **Избежание nullable-типов и проверок на `null`**: `lateinit` позволяет объявить изменяемое свойство с не-null типом без начального значения, избегая использования типа с `?` и дополнительных проверок на `null`. При этом ответственность за корректную инициализацию лежит на разработчике; при обращении к неинициализированному свойству будет выброшено `UninitializedPropertyAccessException`;
- **Начальное значение не требуется**: При использовании `lateinit` не нужно предоставлять начальное значение при объявлении свойства. Это особенно полезно для свойств, инициализируемых позднее, например UI-компонентов в Android или зависимостей из DI-контейнера;
- **Удобство для инфраструктурного и lifecycle-кода**: Модификатор `lateinit` упрощает инициализацию свойств в методах настройки (setup), юнит-тестах или других методах жизненного цикла, где свойству присваивается значение внешним фреймворком или кодом.

### Ключевые Ограничения

- Может использоваться только с изменяемыми свойствами (`var`), так как свойства только для чтения (`val`) должны быть инициализированы при объявлении или в конструкторе;
- Может использоваться только для не-null типов (тип не должен быть помечен `?`), так как предназначен для избежания работы с nullable-типами;
- Не может использоваться для локальных переменных (только для свойств класса, top-level свойств и свойств в `object` / `companion object`);
- Поддержка для примитивов зависит от платформы. На Kotlin/JVM `lateinit` допустим для ряда примитивных типов (`Int`, `Long`, `Double`, `Boolean` и т.д.), которые хранятся как ссылочные типы. На Kotlin/Native и Kotlin/JS `lateinit` доступен только для ссылочных типов.

### Проверка Инициализации `lateinit var`

Чтобы проверить, был ли уже инициализирован `lateinit var`, используйте `.isInitialized` на ссылке на это свойство:

```kotlin
if (foo::bar.isInitialized) {
    println(foo.bar)
}
```

Эта проверка:
- доступна только для `lateinit`-свойств;
- возможна только для свойств, которые лексически доступны: объявлены в том же типе, одном из внешних типов или на верхнем уровне в том же файле.

### Использование `lateinit` В Kotlin

- **Внедрение зависимостей**. Во многих DI-фреймворках зависимости устанавливаются фреймворком после создания объекта. С `lateinit` можно объявить свойства для этих зависимостей и инициализировать их, когда они становятся доступны;
- **UI-компоненты**. `lateinit` обычно используется для UI-компонентов, таких как `TextView`, `Button` или `EditText`, которые инициализируются в `onCreate` / `onViewCreated` после раздувания макета;
- **Тестирование**. В тестах `lateinit` позволяет объявить поля, которые инициализируются в методах `@Before` / `@SetUp`;
- **Пользовательская логика инициализации**. Некоторые свойства требуют сложной логики инициализации, которую неудобно выполнять в конструкторе. С `lateinit` вы можете вызывать отдельный метод инициализации перед первым использованием свойства.

Важно: `lateinit` подходит прежде всего для сценариев, где момент инициализации определяется внешним жизненным циклом или фреймворком. Использование `lateinit` для обычной бизнес-логики, когда можно безопасно проинициализировать значение в конструкторе или использовать `by lazy` / nullable-типы, обычно считается антипаттерном.

(Для ленивой инициализации `val`-свойств предпочтительнее использовать делегат `by lazy`, а не `lateinit`: они решают разные задачи и не комбинируются на одном свойстве.)

---

## Answer (EN)

`lateinit` is a keyword used to define a property that will be initialized later. Unlike regular non-null `var` properties, which must be assigned a value at declaration time or in a constructor, `lateinit` properties are not initialized at the time of object creation. This is useful when the initial value is not known or not available at declaration time, but you guarantee (as a code contract) that it will be assigned before first use. If that contract is violated, an `UninitializedPropertyAccessException` will be thrown.

Example of `lateinit` usage:

```kotlin
public class MyTest {
    lateinit var subject: TestSubject

    @SetUp fun setup() {
        subject = TestSubject()
    }

    @Test fun test() {
        subject.method()  // dereference directly
    }
}
```

### Key Features of `lateinit` Modifier

- **Avoid nullable types and explicit null checks**: `lateinit` lets you declare a mutable non-null property without providing an initial value, avoiding a `?` type and repetitive null checks. The responsibility to initialize before access is on the developer; accessing it too early results in `UninitializedPropertyAccessException`;
- **No Initial Value Required**: With `lateinit`, you don't need to provide an initial value at the point of declaration. This is particularly useful for properties that are initialized later, such as Android UI components or DI-provided dependencies;
- **Convenient for infrastructure/lifecycle code**: The `lateinit` modifier simplifies initializing properties in setup methods, tests, or other lifecycle callbacks where values are supplied by an external framework or later in the lifecycle.

### Key Restrictions

- Can only be used with mutable properties (`var`), because read-only properties (`val`) must be initialized at declaration or in a constructor;
- Can only be used with non-null types (the type must not be marked with `?`), as it is designed to avoid nullable types;
- Cannot be used for local variables; it's allowed only for class properties, top-level properties, and properties in `object` / `companion object`;
- Primitive support is platform-dependent. On Kotlin/JVM, `lateinit` is allowed for several primitive types (`Int`, `Long`, `Double`, `Boolean`, etc.), which are backed by reference fields. On Kotlin/Native and Kotlin/JS, `lateinit` is limited to reference types.

### Checking whether a `lateinit var` is Initialized

To check whether a `lateinit var` has already been initialized, use `.isInitialized` on the reference to that property:

```kotlin
if (foo::bar.isInitialized) {
    println(foo.bar)
}
```

This check:
- is only available for `lateinit` properties;
- works only for properties that are lexically accessible: declared in the same type, in one of the outer types, or at top level in the same file.

### Uses of `lateinit` in Kotlin

- **Dependency Injection**. In many DI frameworks, components or services are injected after the object is created. Using `lateinit`, you can declare properties for these dependencies and initialize them when they become available;
- **UI components**. `lateinit` is commonly used for UI components like `TextView`, `Button`, or `EditText`, which are initialized in `onCreate` / `onViewCreated` after the layout is inflated;
- **Testing**. When writing tests, `lateinit` is handy for properties initialized in `@Before` / `@SetUp` methods;
- **Custom Initialization Logic**. Some properties require complex initialization that doesn't fit well in the constructor. With `lateinit`, you can perform that initialization in separate methods before the property is used.

Important: `lateinit` is primarily suited for scenarios where the initialization moment is controlled by an external lifecycle or framework. Using `lateinit` for regular business logic fields that could be initialized in a constructor or expressed via `by lazy` / nullable types is generally considered a code smell.

(For lazy initialization of `val` properties, prefer the `by lazy` delegate instead of `lateinit`; they target different scenarios and are not combined on the same property.)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Late-initialized properties and variables](https://kotlinlang.org/docs/properties.html#late-initialized-properties-and-variables)
- [Kotlin lateinit (Late Initialization): Full Guide With Examples](https://www.tutorialsfreak.com/kotlin-tutorial/kotlin-lateinit)
- [Kotlin Lateinit: A Complete Guide to Mastering Late Initialization in Kotlin](https://www.dhiwise.com/post/kotlin-lateinit-a-complete-guide-to-late-initialization)
- [Lateinit and Lazy Property in Kotlin](https://medium.com/@guruprasadhegde4/lateinit-and-lazy-property-in-kotlin-8776c67878a0)

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-properties--kotlin--easy]] - Properties
- [[q-kotlin-init-block--kotlin--easy]] - Init Block
- [[q-kotlin-constructors--kotlin--easy]] - Constructors

### Related (Medium)
- [[q-lazy-vs-lateinit--kotlin--medium]] - Lazy
- [[q-kotlin-null-safety--kotlin--medium]] - Null Safety
- [[q-app-startup-library--android--medium]] - App Startup
