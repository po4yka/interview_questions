---
id: kotlin-029
title: "Kotlin Generics / Обобщения (Generics) в Kotlin"
aliases: ["Kotlin Generics", "Обобщения (Generics) в Kotlin"]

# Classification
topic: kotlin
subtopics: [generics, types]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-hot-cold-flows--kotlin--medium, q-kotlin-native--kotlin--hard]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/hard, generics, kotlin, type-erasure, types, variance]
date created: Thursday, October 16th 2025, 12:35:35 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Что вы знаете об обобщениях (Generics) в Kotlin?

---

# Question (EN)
> What do you know about Generics in Kotlin?

---

## Ответ (RU)

Обобщенное программирование — это способ написания кода более абстрактным и переиспользуемым образом, подобно тому, как мы работали бы в языке с динамической типизацией, но при этом с сохранением строгой статической типизации и предотвращением ошибок времени выполнения (например, ClassCastException) за счет проверок на этапе компиляции.

Использование обобщений в Kotlin позволяет разработчику сосредоточиться на создании переиспользуемых решений или шаблонов для более широкого круга задач с сохранением статической типобезопасности. См. также [[c-kotlin]].

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
val box = Box(1) // 1 имеет тип `Int`, поэтому компилятор понимает, что это Box<Int>
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
sort(listOf(1, 2, 3)) // OK. `Int` является подтипом Comparable<Int>
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

### Вариативность (in / out)

Kotlin поддерживает вариативность на стороне объявления и на стороне использования.

- `out` — ковариантность: вы можете использовать `Producer<Child>` там, где ожидается `Producer<Parent>`, если тип-параметр объявлен как `out T`. Такой тип безопасен только для «чтения»/возврата значения `T`.

```kotlin
interface Producer<out T> {
    fun produce(): T
}
```

- `in` — контравариантность: вы можете использовать `Consumer<Parent>` там, где ожидается `Consumer<Child>`, если тип-параметр объявлен как `in T`. Такой тип безопасен только для «записи»/потребления `T`.

```kotlin
interface Consumer<in T> {
    fun consume(value: T)
}
```

- Без модификаторов (`in`/`out`) параметр типа инвариантен: `List<String>` не является ни подтипом, ни надтипом `List<Any>`.

Для Java-коллекций Kotlin использует проекции типов, чтобы отразить их ковариантность/контравариантность.

### Вариативность На Месте Использования (use-site variance)

Помимо объявления `in`/`out` в определении типа, можно использовать их в месте использования (типовые проекции):

- `List<out T>` — вы обещаете только читать `T`.
- `MutableList<in T>` — вы обещаете только записывать `T`.

Это позволяет выразить ковариантность/контравариантность для типов, которые сами по себе инвариантны.

### Стирание Типов

На JVM-бэкенде Kotlin использует стирание типов, совместимое с реализацией обобщений в Java. Проверки безопасности типов, которые Kotlin выполняет для использования обобщенных объявлений, выполняются во время компиляции. Во время выполнения экземпляры обобщенных типов не содержат информации о своих фактических аргументах типа. Говорят, что информация о типе *стирается*. Например, экземпляры `Foo<Bar>` и `Foo<Baz?>` стираются до просто `Foo<*>`.

(В других таргетах, таких как Kotlin/Native и Kotlin/JS, часть информации о типах может быть доступна на этапе выполнения, но модель всё равно ориентирована на JVM-совместимое поведение и специфику конкретного таргета следует учитывать отдельно.)

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

Приведения типов к обобщенным типам с конкретными аргументами типа, такие как `foo as List<String>`, не могут быть полностью проверены во время выполнения на JVM.

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

Чтобы избежать непроверяемых приведений, вы можете переработать структуру программы. В приведенном выше примере вы могли бы использовать интерфейсы `DictionaryReader<T>` и `DictionaryWriter<T>` с типобезопасными реализациями для разных типов и инкапсулировать небезопасные приведения внутри реализации.

### Реализованные Параметры Типа (reified Type parameters)

Kotlin позволяет частично обходить стирание типов в inline-функциях с помощью `reified` параметров типа:

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T =
    this.fromJson(json, T::class.java)
```

- `reified T` доступен в теле функции, можно использовать `T::class`, проверки `is T`, приведения `as T` без явной передачи `Class`/`KClass`.
- Это работает только для `inline` функций и зависит от таргета (на JVM компилируется с подстановкой конкретных типов в места вызова).

---

## Answer (EN)

Generic programming is a way of writing code in a more abstract and reusable manner, similar to how we might structure code in a dynamically typed language, while still keeping strong static typing and preventing runtime errors (such as ClassCastException) through compile-time checks.

Using generics in Kotlin enables the developer to focus on creating reusable solutions, or templates, for a wider range of problems while preserving static type safety.

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
val box = Box(1) // 1 has type `Int`, so the compiler figures out that it is Box<Int>
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
sort(listOf(1, 2, 3)) // OK. `Int` is a subtype of Comparable<Int>
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

### Variance (in / out)

Kotlin supports variance both at the declaration site and at the use site.

- `out` — covariance: you can use `Producer<Child>` where `Producer<Parent>` is expected if the type parameter is declared as `out T`. Such a type is safe for producing/returning `T` values.

```kotlin
interface Producer<out T> {
    fun produce(): T
}
```

- `in` — contravariance: you can use `Consumer<Parent>` where `Consumer<Child>` is expected if the type parameter is declared as `in T`. Such a type is safe for consuming `T` values.

```kotlin
interface Consumer<in T> {
    fun consume(value: T)
}
```

- Without modifiers (`in`/`out`), the type parameter is invariant: `List<String>` is neither a subtype nor a supertype of `List<Any>`.

For Java collections, Kotlin uses type projections to reflect their covariance/contravariance semantics.

### Use-site Variance (type projections)

In addition to declaration-site `in`/`out`, you can specify variance at the use site:

- `List<out T>` — you only read `T`.
- `MutableList<in T>` — you only write `T`.

This allows you to model covariance/contravariance for invariant generic types.

### Type Erasure

On the JVM backend, Kotlin uses Java-compatible type erasure for generics. The type safety checks that Kotlin performs for generic declaration usages are done at compile time. At runtime, the instances of generic types do not hold information about their actual type arguments. The type information is said to be *erased*. For example, the instances of `Foo<Bar>` and `Foo<Baz?>` are erased to just `Foo<*>`.

(On other targets such as Kotlin/Native and Kotlin/JS, some type information may be available at runtime, but the overall model is still aligned with JVM-style generics, and target-specific behavior should be considered separately.)

#### Generics Type Checks and Casts

Due to type erasure, there is no general way to check whether an instance of a generic type was created with certain type arguments at runtime, and the compiler prohibits such `is` checks such as `ints is List<Int>` or `list is T` (type parameter). However, you can check an instance against a star-projected type:

```kotlin
if (something is List<*>) {
    something.forEach { println(it) } // The items are typed as `Any?`
}
```

Similarly, when you already have the type arguments of an instance checked statically (at compile time), you can make an `is` check or a cast that involves the non-generic part of the type. Note that angle brackets are omitted in this case:

```kotlin
fun handleStrings(list: MutableList<String>) {
    if (list is ArrayList) {
        // `list` is smart-cast to `ArrayList<String>`
    }
}
```

The same syntax but with the type arguments omitted can be used for casts that do not take type arguments into account: `list as ArrayList`.

#### Unchecked Casts

Type casts to generic types with concrete type arguments such as `foo as List<String>` cannot be fully checked at runtime on the JVM.

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

To avoid unchecked casts, you can redesign the program structure. In the example above, you could use the `DictionaryReader<T>` and `DictionaryWriter<T>` interfaces with type-safe implementations for different types and encapsulate unsafe casts inside the implementation.

### Reified Type Parameters

Kotlin allows partially bypassing type erasure in inline functions using `reified` type parameters:

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T =
    this.fromJson(json, T::class.java)
```

- `reified T` is available inside the function body; you can use `T::class`, `is T`, `as T` without passing `Class`/`KClass` explicitly.
- This only works for `inline` functions and is backend-specific (on the JVM, the concrete type is substituted at call sites).

## Дополнительные Вопросы (RU)

- В чем ключевые отличия обобщений в Kotlin и Java?
- Когда вы бы использовали обобщения на практике?
- Какие распространенные подводные камни при работе с обобщениями?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Generics: in, out, where](https://kotlinlang.org/docs/generics.html)
- [Understanding Kotlin generics](https://blog.logrocket.com/understanding-kotlin-generics/)
- [Generics in Kotlin](https://kt.academy/article/kfde-generics)

## References
- [Generics: in, out, where](https://kotlinlang.org/docs/generics.html)
- [Understanding Kotlin generics](https://blog.logrocket.com/understanding-kotlin-generics/)
- [Generics in Kotlin](https://kt.academy/article/kfde-generics)

## Связанные Вопросы (RU)

- [[q-kotlin-collections--kotlin--easy]]
- [[q-kotlin-type-system--kotlin--medium]]

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
- [[q-kotlin-type-system--kotlin--medium]]
