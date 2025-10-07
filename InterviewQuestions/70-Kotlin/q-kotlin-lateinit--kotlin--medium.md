---
id: 20251005-222653
title: "Kotlin lateinit Keyword / Ключевое слово lateinit в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [properties, lateinit, initialization, null-safety]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: reviewed
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, lateinit, properties, initialization, null-safety, difficulty/medium]
---
## Question (EN)
> What do you know about `lateinit` in Kotlin?
## Вопрос (RU)
> Что вы знаете о `lateinit` в Kotlin?

---

## Answer (EN)

`lateinit` is a keyword used to define a property that will be initialized later. Unlike other properties declared with `var`, `lateinit` properties are not initialized at the time of object creation. This makes it particularly useful when the initial value of the property is not known at the time of declaration.

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

### Key features of `lateinit` modifier

- **Avoid Null Checks**: `lateinit` allows you to avoid cumbersome null checks when working with nullable types. The `lateinit` keyword tells the compiler that you will ensure the property is initialized before usage;
- **No Initial Value Required**: When using `lateinit`, you don't need to provide an initial value when the property is declared. This is particularly useful for properties that are not immediately initialized, such as UI components in Android;
- **Easily Set Up Late Initialized Properties**: The `lateinit` modifier simplifies initializing properties in setup methods, unit tests, or other methods where the property can be assigned values dynamically.

### Key restrictions

- Can only be used with mutable properties (variables declared with the `var` keyword), cause read-only properties (declared with the `val` keyword) represent immutable values that must be initialized at the time of declaration;
- Can be used only for non-primitive types (`Int`, `Double`, `Float` etc not allowed);
- Cannot be used with nullable types, as it is designed to avoid dealing with `null` values;

### Checking whether a lateinit var is initialized

To check whether a `lateinit var` has already been initialized, use `.isInitialized` on the reference to that property:

```kotlin
if (foo::bar.isInitialized) {
    println(foo.bar)
}
```

This check is only available for properties that are lexically accessible when declared in the same type, in one of the outer types, or at top level in the same file.

### Uses of Lateinit in Kotlin

- **Dependency Injection**. In many dependency injection frameworks, components or services may not be available at the time of object creation. By using `lateinit`, you can declare properties for these dependencies and initialize them when they become available;
- **UI components**. `lateinit` is commonly used for UI components like `TextView`, `Button`, or `EditText`, as they often need to be initialized in the `onCreate` method after the layout is inflated;
- **Testing**. When writing tests, you might want to create an instance of a class for testing but don't have access to all the data necessary for its properties during initialization. `lateinit` allows you to set up the test environment and then initialize the properties as needed;
- **Lazy Initialization**. You can use `lateinit` in conjunction with the `by lazy` delegate to perform lazy initialization of a property. This is useful when the initialization process is costly and should be deferred until the property is first accessed;
- **Data Fetching and Asynchronous Operations**. When working with data that is fetched asynchronously, such as from a network request, you might not have the data available at object creation. `lateinit` can be used to hold the data until it's fetched and then assigned;
- **Custom Initialization Logic**. Some properties may require custom initialization logic that cannot be performed in the constructor. By using `lateinit`, you can define your own initialization methods and call them when the property is ready to be set.

## Ответ (RU)

`lateinit` — это ключевое слово, используемое для определения свойства, которое будет инициализировано позже. В отличие от других свойств, объявленных с `var`, свойства `lateinit` не инициализируются во время создания объекта. Это делает его особенно полезным, когда начальное значение свойства неизвестно во время объявления.

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

### Ключевые особенности модификатора `lateinit`

- **Избегание проверок на null**: `lateinit` позволяет избежать громоздких проверок на null при работе с nullable типами. Ключевое слово `lateinit` сообщает компилятору, что вы обеспечите инициализацию свойства перед использованием;
- **Начальное значение не требуется**: При использовании `lateinit` вам не нужно предоставлять начальное значение при объявлении свойства. Это особенно полезно для свойств, которые не инициализируются сразу, таких как UI компоненты в Android;
- **Легкая настройка поздно инициализируемых свойств**: Модификатор `lateinit` упрощает инициализацию свойств в методах настройки, юнит-тестах или других методах, где свойству можно динамически присвоить значения.

### Ключевые ограничения

- Может использоваться только с изменяемыми свойствами (переменными, объявленными с ключевым словом `var`), поскольку свойства только для чтения (объявленные с ключевым словом `val`) представляют неизменяемые значения, которые должны быть инициализированы во время объявления;
- Может использоваться только для непримитивных типов (`Int`, `Double`, `Float` и т.д. не разрешены);
- Не может использоваться с nullable типами, так как предназначен для избежания работы со значениями `null`;

### Проверка инициализации lateinit var

Чтобы проверить, был ли уже инициализирован `lateinit var`, используйте `.isInitialized` на ссылке на это свойство:

```kotlin
if (foo::bar.isInitialized) {
    println(foo.bar)
}
```

Эта проверка доступна только для свойств, которые лексически доступны при объявлении в том же типе, в одном из внешних типов или на верхнем уровне в том же файле.

### Использование Lateinit в Kotlin

- **Внедрение зависимостей**. Во многих фреймворках внедрения зависимостей компоненты или сервисы могут быть недоступны во время создания объекта. Используя `lateinit`, вы можете объявить свойства для этих зависимостей и инициализировать их, когда они станут доступны;
- **UI компоненты**. `lateinit` обычно используется для UI компонентов, таких как `TextView`, `Button` или `EditText`, поскольку они часто должны быть инициализированы в методе `onCreate` после раздувания макета;
- **Тестирование**. При написании тестов вы можете захотеть создать экземпляр класса для тестирования, но не иметь доступа ко всем данным, необходимым для его свойств во время инициализации. `lateinit` позволяет настроить тестовую среду, а затем инициализировать свойства по мере необходимости;
- **Ленивая инициализация**. Вы можете использовать `lateinit` в сочетании с делегатом `by lazy` для выполнения ленивой инициализации свойства. Это полезно, когда процесс инициализации затратен и должен быть отложен до первого доступа к свойству;
- **Получение данных и асинхронные операции**. При работе с данными, которые получаются асинхронно, такими как из сетевого запроса, у вас может не быть данных, доступных при создании объекта. `lateinit` может использоваться для хранения данных до тех пор, пока они не будут получены и затем назначены;
- **Пользовательская логика инициализации**. Некоторые свойства могут требовать пользовательской логики инициализации, которую нельзя выполнить в конструкторе. Используя `lateinit`, вы можете определить свои собственные методы инициализации и вызвать их, когда свойство готово к установке.

---

## References
- [Late-initialized properties and variables](https://kotlinlang.org/docs/properties.html#late-initialized-properties-and-variables)
- [Kotlin lateinit (Late Initialization): Full Guide With Examples](https://www.tutorialsfreak.com/kotlin-tutorial/kotlin-lateinit)
- [Kotlin Lateinit: A Complete Guide to Mastering Late Initialization in Kotlin](https://www.dhiwise.com/post/kotlin-lateinit-a-complete-guide-to-late-initialization)
- [Lateinit and Lazy Property in Kotlin](https://medium.com/@guruprasadhegde4/lateinit-and-lazy-property-in-kotlin-8776c67878a0)

## Related Questions
- [[q-kotlin-null-safety--kotlin--medium]]
