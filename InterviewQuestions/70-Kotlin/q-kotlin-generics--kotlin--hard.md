---
id: kotlin-029
title: "Kotlin Generics / Обобщения (Generics) в Kotlin"
aliases: ["Kotlin Generics, Обобщения (Generics) в Kotlin"]

# Classification
topic: kotlin
subtopics: [generics, type-erasure, types]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-hot-cold-flows--kotlin--medium, q-kotlin-any-inheritance--programming-languages--easy, q-kotlin-native--kotlin--hard]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [difficulty/hard, generics, kotlin, type-erasure, types, variance]
date created: Thursday, October 16th 2025, 12:35:35 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Вопрос (RU)
> Что вы знаете об обобщениях (Generics) в Kotlin?

---

# Question (EN)
> What do you know about Generics in Kotlin?
## Ответ (RU)

Обобщенное программирование — это способ написания кода гибким образом, как мы бы это делали в языке с динамической типизацией. В то же время обобщения позволяют нам писать код безопасно и с как можно меньшим количеством ошибок времени компиляции.

Использование обобщений в Kotlin позволяет разработчику сосредоточиться на создании переиспользуемых решений или шаблонов для более широкого круга проблем.

### Обобщенный Класс

Классы в Kotlin могут иметь параметры типа, точно так же, как в Java:

```kotlin
class Box<T>(t: T) {
    var value = t
}
```

Чтобы создать экземпляр такого класса, просто укажите аргументы типа:

```kotlin
val box: Box<Int> = Box<Int>(1)
```

Но если параметры могут быть выведены, например, из аргументов конструктора, вы можете опустить аргументы типа:

```kotlin
val box = Box(1) // 1 имеет тип Int, поэтому компилятор понимает, что это Box<Int>
```

### Обобщенные Функции

Классы — не единственные объявления, которые могут иметь параметры типа. Функции тоже могут. Параметры типа размещаются *перед* именем функции:

```kotlin
fun <T> singletonList(item: T): List<T> {
    // ...
}

fun <T> T.basicToString(): String { // функция-расширение
    // ...
}
```

Чтобы вызвать обобщенную функцию, укажите аргументы типа в месте вызова *после* имени функции:

```kotlin
val l = singletonList<Int>(1)
```

Аргументы типа могут быть опущены, если они могут быть выведены из контекста, поэтому следующий пример также работает:

```kotlin
val l = singletonList(1)
```

### Ограничения Обобщений

Набор всех возможных типов, которые могут быть подставлены для данного параметра типа, может быть ограничен *ограничениями обобщений*.

#### Верхние Границы

Наиболее распространенный тип ограничения — это *верхняя граница*, которая соответствует ключевому слову `extends` в Java:

```kotlin
fun <T : Comparable<T>> sort(list: List<T>) {  ... }
```

Тип, указанный после двоеточия, является *верхней границей*, указывающей, что только подтип `Comparable<T>` может быть подставлен для `T`. Например:

```kotlin
sort(listOf(1, 2, 3)) // OK. Int является подтипом Comparable<Int>
sort(listOf(HashMap<Int, String>())) // Ошибка: HashMap<Int, String> не является подтипом Comparable<HashMap<Int, String>>
```

Верхняя граница по умолчанию (если она не указана) — это `Any?`. Только одна верхняя граница может быть указана внутри угловых скобок. Если один и тот же параметр типа нуждается в более чем одной верхней границе, вам нужна отдельная *where-клауза*:

```kotlin
fun <T> copyWhenGreater(list: List<T>, threshold: T): List<String>
    where T : CharSequence,
          T : Comparable<T> {
    return list.filter { it > threshold }.map { it.toString() }
}
```

Переданный тип должен одновременно удовлетворять всем условиям клаузы `where`. В приведенном выше примере тип `T` должен реализовывать *и* `CharSequence`, *и* `Comparable`.

### Стирание Типов

Проверки безопасности типов, которые Kotlin выполняет для использования обобщенных объявлений, выполняются во время компиляции. Во время выполнения экземпляры обобщенных типов не содержат никакой информации о своих фактических аргументах типа. Говорят, что информация о типе *стирается*. Например, экземпляры `Foo<Bar>` и `Foo<Baz?>` стираются до просто `Foo<*>`.

#### Проверки И Приведения Обобщенных Типов

Из-за стирания типов нет общего способа проверить, был ли экземпляр обобщенного типа создан с определенными аргументами типа во время выполнения, и компилятор запрещает такие проверки `is`, как `ints is List<Int>` или `list is T` (параметр типа). Однако вы можете проверить экземпляр на star-projected тип:

```kotlin
if (something is List<*>) {
    something.forEach { println(it) } // Элементы типизированы как `Any?`
}
```

Аналогично, когда вы уже проверили аргументы типа экземпляра статически (во время компиляции), вы можете сделать проверку `is` или приведение, которое включает необобщенную часть типа. Обратите внимание, что угловые скобки в этом случае опущены:

```kotlin
fun handleStrings(list: MutableList<String>) {
    if (list is ArrayList) {
        // `list` умно приводится к `ArrayList<String>`
    }
}
```

Тот же синтаксис, но с опущенными аргументами типа, может использоваться для приведений, которые не учитывают аргументы типа: `list as ArrayList`.

#### Непроверяемые Приведения

Приведения типов к обобщенным типам с конкретными аргументами типа, такие как `foo as List<String>`, не могут быть проверены во время выполнения.

Эти непроверяемые приведения могут использоваться, когда безопасность типов подразумевается логикой программы высокого уровня, но не может быть выведена напрямую компилятором. См. пример ниже.

```kotlin
fun readDictionary(file: File): Map<String, *> = file.inputStream().use {
    // Читаем файл и десериализуем в map (реализация упрощена)
    emptyMap<String, Any>()
}

// Мы сохранили map с `Int` в этот файл
val intsFile = File("ints.dictionary")

// Предупреждение: Непроверяемое приведение: `Map<String, *>` к `Map<String, Int>`
val intsDictionary: Map<String, Int> = readDictionary(intsFile) as Map<String, Int>
```

Появляется предупреждение для приведения в последней строке. Компилятор не может полностью проверить его во время выполнения и не дает гарантии, что значения в map являются `Int`.

Чтобы избежать непроверяемых приведений, вы можете переработать структуру программы. В приведенном выше примере вы могли бы использовать интерфейсы `DictionaryReader<T>` и `DictionaryWriter<T>` с типобезопасными реализациями для разных типов. Вы можете ввести разумные абстракции, чтобы переместить непроверяемые приведения из места вызова в детали реализации.

---

## Answer (EN)

Generic programming is a way of writing our code in a flexible manner like we would in a dynamically-typed language. At the same time, generics allow us to write code safely and with as few compile-time errors as possible.

Using generics in Kotlin enables the developer to focus on creating reusable solutions, or templates, for a wider range of problems.

### Generic Class

Classes in Kotlin can have type parameters, just like in Java:

```kotlin
class Box<T>(t: T) {
    var value = t
}
```

To create an instance of such a class, simply provide the type arguments:

```kotlin
val box: Box<Int> = Box<Int>(1)
```

But if the parameters can be inferred, for example, from the constructor arguments, you can omit the type arguments:

```kotlin
val box = Box(1) // 1 has type Int, so the compiler figures out that it is Box<Int>
```

### Generic Functions

Classes aren't the only declarations that can have type parameters. Functions can, too. Type parameters are placed *before* the name of the function:

```kotlin
fun <T> singletonList(item: T): List<T> {
    // ...
}

fun <T> T.basicToString(): String { // extension function
    // ...
}
```

To call a generic function, specify the type arguments at the call site *after* the name of the function:

```kotlin
val l = singletonList<Int>(1)
```

Type arguments can be omitted if they can be inferred from the context, so the following example works as well:

```kotlin
val l = singletonList(1)
```

### Generic Constraints

The set of all possible types that can be substituted for a given type parameter may be restricted by *generic constraints*.

#### Upper Bounds

The most common type of constraint is an *upper bound*, which corresponds to Java's `extends` keyword:

```kotlin
fun <T : Comparable<T>> sort(list: List<T>) {  ... }
```

The type specified after a colon is the *upper bound*, indicating that only a subtype of `Comparable<T>` can be substituted for `T`. For example:

```kotlin
sort(listOf(1, 2, 3)) // OK. Int is a subtype of Comparable<Int>
sort(listOf(HashMap<Int, String>())) // Error: HashMap<Int, String> is not a subtype of Comparable<HashMap<Int, String>>
```

The default upper bound (if there was none specified) is `Any?`. Only one upper bound can be specified inside the angle brackets. If the same type parameter needs more than one upper bound, you need a separate *where-clause*:

```kotlin
fun <T> copyWhenGreater(list: List<T>, threshold: T): List<String>
    where T : CharSequence,
          T : Comparable<T> {
    return list.filter { it > threshold }.map { it.toString() }
}
```

The passed type must satisfy all conditions of the `where` clause simultaneously. In the above example, the `T` type must implement *both* `CharSequence` and `Comparable`.

### Type Erasure

The type safety checks that Kotlin performs for generic declaration usages are done at compile time. At runtime, the instances of generic types do not hold any information about their actual type arguments. The type information is said to be *erased*. For example, the instances of `Foo<Bar>` and `Foo<Baz?>` are erased to just `Foo<*>`.

#### Generics Type Checks and Casts

Due to the type erasure, there is no general way to check whether an instance of a generic type was created with certain type arguments at runtime, and the compiler prohibits such `is` - checks such as `ints is List<Int>` or `list is T` (type parameter). However, you can check an instance against a star-projected type:

```kotlin
if (something is List<*>) {
    something.forEach { println(it) } // The items are typed as `Any?`
}
```

Similarly, when you already have the type arguments of an instance checked statically (at compile time), you can make an `is` - check or a cast that involves the non-generic part of the type. Note that angle brackets are omitted in this case:

```kotlin
fun handleStrings(list: MutableList<String>) {
    if (list is ArrayList) {
        // `list` is smart-cast to `ArrayList<String>`
    }
}
```

The same syntax but with the type arguments omitted can be used for casts that do not take type arguments into account: `list as ArrayList`.

#### Unchecked Casts

Type casts to generic types with concrete type arguments such as `foo as List<String>` cannot be checked at runtime.

These unchecked casts can be used when type safety is implied by the high-level program logic but cannot be inferred directly by the compiler. See the example below.

```kotlin
fun readDictionary(file: File): Map<String, *> = file.inputStream().use {
    // Read file and deserialize to map (implementation simplified)
    emptyMap<String, Any>()
}

// We saved a map with `Int`s into this file
val intsFile = File("ints.dictionary")

// Warning: Unchecked cast: `Map<String, *>` to `Map<String, Int>`
val intsDictionary: Map<String, Int> = readDictionary(intsFile) as Map<String, Int>
```

A warning appears for the cast in the last line. The compiler can't fully check it at runtime and provides no guarantee that the values in the map are `Int`.

To avoid unchecked casts, you can redesign the program structure. In the example above, you could use the `DictionaryReader<T>` and `DictionaryWriter<T>` interfaces with type-safe implementations for different types. You can introduce reasonable abstractions to move unchecked casts from the call site to the implementation details.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Generics: in, out, where](https://kotlinlang.org/docs/generics.html)
- [Understanding Kotlin generics](https://blog.logrocket.com/understanding-kotlin-generics/)
- [Generics in Kotlin](https://kt.academy/article/kfde-generics)

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
- [[q-kotlin-type-system--kotlin--medium]]
